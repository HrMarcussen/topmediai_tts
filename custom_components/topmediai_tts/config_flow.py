"""Config flow for TopMediai TTS integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN, CONF_SPEAKER

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_SPEAKER): str,
    }
)


async def validate_input(hass, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    websession = aiohttp_client.async_get_clientsession(hass)
    api_key = data[CONF_API_KEY]
    
    # We can try to hit the user info endpoint to validate the key
    # Based on docs: https://docs.topmediai.com/api-reference/x-api-key-info/get-api-key-info
    url = "https://api.topmediai.com/v1/get_api_key_info"
    headers = {"x-api-key": api_key}

    try:
        async with websession.get(url, headers=headers) as response:
            if response.status == 401 or response.status == 403:
                raise InvalidAuth
            if response.status != 200:
                # If the endpoint doesn't return 200, we might still proceed but warn?
                # Or stricly fail. Let's fail on auth errors only strictly.
                # Actually, if the key is invalid, we expect 4xx.
                # If 200, we are good.
                pass
            response.raise_for_status()
    except Exception as err:
        _LOGGER.error("Failed to validate API key: %s", err)
        # If we can't connect, we might raise CannotConnect
        # But for now let's assume if it throws, it's invalid or connection error
        raise CannotConnect from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TopMediai TTS."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
                return self.async_create_entry(title="TopMediai TTS", data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_KEY,
                        default=self.config_entry.options.get(
                            CONF_API_KEY, self.config_entry.data.get(CONF_API_KEY)
                        ),
                    ): str,
                    vol.Required(
                        CONF_SPEAKER,
                        default=self.config_entry.options.get(
                            CONF_SPEAKER, self.config_entry.data.get(CONF_SPEAKER)
                        ),
                    ): str,
                }
            ),
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
