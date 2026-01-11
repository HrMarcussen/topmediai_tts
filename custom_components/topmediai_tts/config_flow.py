"""Config flow for TopMediai TTS integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN, CONF_SPEAKER, DEFAULT_SPEAKER

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_SPEAKER, default=DEFAULT_SPEAKER): str,
    }
)


async def validate_input(hass, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    websession = aiohttp_client.async_get_clientsession(hass)
    api_key = data[CONF_API_KEY]
    
    url = "https://api.topmediai.com/v1/get_api_key_info"
    headers = {"x-api-key": api_key}

    try:
        async with websession.get(url, headers=headers) as response:
            if response.status == 401 or response.status == 403:
                raise InvalidAuth
            # 200 is success. 
            # Some APIs might return 200 with error body, but usually auth failure is 4xx.
            # If we really want to check payload:
            # json = await response.json()
            # if json.get('code') != 0: ...
            
            # Simple check:
            response.raise_for_status()
    except Exception as err:
        _LOGGER.error("Failed to validate API key: %s", err)
        raise CannotConnect from err


class TopMediaiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
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
        try:
            _LOGGER.warning("TopMediaAI: OptionsFlow async_step_init called.")
            # Safely get default values
            options = self.config_entry.options or {}
            data = self.config_entry.data or {}
            
            _LOGGER.warning("TopMediaAI: Retrieving options. Options: %s, Data: %s", options, data)
            current_api_key = str(options.get(CONF_API_KEY, data.get(CONF_API_KEY, "")))
            current_speaker = str(options.get(CONF_SPEAKER, data.get(CONF_SPEAKER, DEFAULT_SPEAKER)))

            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        # Usually we don't allow changing API key in options, but if we do...
                        # Or maybe just speaker. Let's keep both for flexibility.
                        vol.Required(CONF_API_KEY, default=current_api_key): str,
                        vol.Required(CONF_SPEAKER, default=current_speaker): str,
                    }
                ),
            )
        except Exception as e:
            _LOGGER.error("TopMediaAI: Unexpected error in OptionsFlowHandler: %s", e)
            return self.async_abort(reason="unknown_error")


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
