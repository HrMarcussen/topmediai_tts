"""Support for the TopMediai TTS service."""
import logging
import voluptuous as vol

from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA,
    TextToSpeechEntity,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import aiohttp_client, config_validation as cv

from .const import CONF_SPEAKER, DEFAULT_LANG, DEFAULT_SPEAKER, DOMAIN

_LOGGER = logging.getLogger(__name__)

TOPMEDIAI_TTS_URL = "https://api.topmediai.com/v1/text2speech"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_LANG, default=DEFAULT_LANG): cv.string,
        vol.Optional(CONF_SPEAKER, default=DEFAULT_SPEAKER): cv.string,
    }
)


async def async_get_engine(hass, config, discovery_info=None):
    """Set up TopMediai TTS component (Legacy YAML)."""
    # This is for legacy YAML setup. For config entries, async_setup_entry is used.
    # To support legacy yaml with the new Entity model, we can't easily return a Provider
    # if we switched to TextToSpeechEntity totally.
    # However, HA supports returning a Provider that inherits form Provider.
    # But strictly speaking, TextToSpeechEntity is for Config Entries (mostly).
    # Since we want Config Entry support, we should prioritize `async_setup_entry`.
    # For YAML support, we can still use Provider or map it.
    # For simplicity and modern support, we'll return None here or deprecate YAML if strictly config flow.
    # BUT, to keep backwards compatibility, we can return a Provider wrapper?
    # Actually, simpler: Use `async_setup_platform` to load the entity from YAML.
    pass

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the TopMediai TTS platform via YAML."""
    async_add_entities([TopMediAITTS(
        hass,
        config[CONF_API_KEY],
        config.get(CONF_LANG, DEFAULT_LANG),
        config.get(CONF_SPEAKER, DEFAULT_SPEAKER),
    )])

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up TopMediai TTS from a config entry."""
    async_add_entities([TopMediAITTS(
        hass,
        config_entry.data[CONF_API_KEY],
        DEFAULT_LANG, # Language is often dynamic or per-call, but user can set default
        config_entry.data[CONF_SPEAKER],
        config_entry
    )])


class TopMediAITTS(TextToSpeechEntity):
    """The TopMediai TTS API Entity."""

    def __init__(self, hass, api_key, lang, speaker, config_entry=None):
        """Init TopMediai TTS service."""
        self.hass = hass
        self._api_key = api_key
        self._language = lang
        self._speaker = speaker
        self._config_entry = config_entry
        self._attr_name = "TopMediai"
        self._attr_unique_id = config_entry.entry_id if config_entry else None

    @property
    def default_language(self):
        """Return the default language."""
        return self._language

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return [self._language]
        
    @property
    def supported_options(self):
        """Return list of supported options."""
        return [CONF_SPEAKER]

    async def async_get_tts_audio(self, message, language, options=None):
        """Load TTS from TopMediai."""
        websession = aiohttp_client.async_get_clientsession(self.hass)
        options = options or {}
        
        # Allow overriding speaker from options, falling back to init speaker
        speaker = options.get(CONF_SPEAKER, self._speaker)
        
        # Check if we have updated options in config entry (if used)
        if self._config_entry and self._config_entry.options:
             speaker = self._config_entry.options.get(CONF_SPEAKER, speaker)
             # Also update API key if changed in options? Usually sensitive data isn't in options.
             # API Key should be in data.

        headers = {
            "x-api-key": self._api_key,
            "Content-Type": "application/json",
        }
        data = {
            "text": message,
            "speaker": speaker,
            "emotion": "Neutral",
        }

        try:
            async with websession.post(
                TOPMEDIAI_TTS_URL, headers=headers, json=data
            ) as response:
                response.raise_for_status()
                response_data = await response.json()

                _LOGGER.debug("TopMediAI API response data: %s", response_data)

                if "data" in response_data and "oss_url" in response_data["data"]:
                    audio_url = response_data["data"]["oss_url"]
                    async with websession.get(audio_url) as audio_response:
                        audio_response.raise_for_status()
                        audio_content = await audio_response.read()
                        return "mp3", audio_content
                else:
                    _LOGGER.error(
                        "oss_url not found in the response: %s", response_data
                    )
                    return None, None

        except Exception as err:
            _LOGGER.error("Error during TopMediai TTS request: %s", err)
            return None, None
