"""Support for the TopMediai TTS service."""
import logging
import voluptuous as vol

from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA,
    Provider,
    TextToSpeechEntity,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import aiohttp_client, config_validation as cv

from .const import CONF_SPEAKER, DEFAULT_LANG, DEFAULT_SPEAKER

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
    """Set up TopMediai TTS component."""
    return TopMediAITTSProvider(
        hass,
        config[CONF_API_KEY],
        config.get(CONF_LANG, DEFAULT_LANG),
        config.get(CONF_SPEAKER, DEFAULT_SPEAKER),
    )


class TopMediAITTSProvider(Provider):
    """The TopMediai TTS API provider."""

    def __init__(self, hass, api_key, lang, speaker):
        """Init TopMediai TTS service."""
        self.hass = hass
        self._api_key = api_key
        self._language = lang
        self._speaker = speaker
        self.name = "TopMediai"

    @property
    def default_language(self):
        """Return the default language."""
        return self._language

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return [self._language]

    async def async_get_tts_audio(self, message, language, options=None):
        """Load TTS from TopMediai."""
        websession = aiohttp_client.async_get_clientsession(self.hass)
        options = options or {}

        headers = {
            "x-api-key": self._api_key,
            "Content-Type": "application/json",
        }
        data = {
            "text": message,
            "speaker": self._speaker,
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
