"""Support for the TopMediai TTS service."""
import logging
import voluptuous as vol

from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA,
    TextToSpeechEntity,
    Voice,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import aiohttp_client, config_validation as cv

from .const import CONF_SPEAKER, DEFAULT_LANG, DEFAULT_SPEAKER, DOMAIN

_LOGGER = logging.getLogger(__name__)

TOPMEDIAI_TTS_URL = "https://api.topmediai.com/v1/text2speech"
TOPMEDIAI_VOICES_URL = "https://api.topmediai.com/v1/voices_list"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_LANG, default=DEFAULT_LANG): cv.string,
        vol.Optional(CONF_SPEAKER, default=DEFAULT_SPEAKER): cv.string,
    }
)


async def async_get_engine(hass, config, discovery_info=None):
    """Set up TopMediai TTS component (Legacy YAML)."""
    # Legacy support skipped as per plan
    pass

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up TopMediai TTS from a config entry."""
    async_add_entities([TopMediAITTS(
        hass,
        config_entry.data[CONF_API_KEY],
        DEFAULT_LANG, 
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
        self._voices = {} # Cache for voices: {voice_id: Voice(...)}
        self._voices_data = {} # Cache for raw API data: {voice_name: api_data_dict}

    @property
    def default_language(self):
        """Return the default language."""
        return self._language

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        if self._voices:
             # Extract unique languages from loaded voices
             return list({v.language for v in self._voices.values()})
        return [self._language]
        
    @property
    def supported_options(self):
        """Return list of supported options."""
        return [CONF_SPEAKER]

    async def async_get_tts_audio(self, message, language, options=None):
        """Load TTS from TopMediai."""
        websession = aiohttp_client.async_get_clientsession(self.hass)
        options = options or {}
        
        # Determine speaker:
        # 1. Check 'voice' option (from HA Voice Assistant or tts.speak voice)
        # 2. Check 'speaker' option (custom option for this integration)
        # 3. Fallback to default configured speaker
        
        speaker_uuid = self._speaker

        # If a specific voice ID (name in our case) is requested via HA
        voice_name = options.get("voice")
        if voice_name:
             # Find the UUID for this voice name in our cache
             if voice_name in self._voices_data:
                 speaker_uuid = self._voices_data[voice_name].get("speaker")
             else:
                 _LOGGER.warning("Requested voice '%s' not found in cache.", voice_name)
        
        # Allow raw speaker UUID override via options
        if CONF_SPEAKER in options:
            speaker_uuid = options[CONF_SPEAKER]
        
        # Config entry options override (lowest priority usually, but let's check config flow)
        if self._config_entry and self._config_entry.options:
             config_speaker = self._config_entry.options.get(CONF_SPEAKER)
             if config_speaker and not voice_name and not options.get(CONF_SPEAKER):
                 speaker_uuid = config_speaker

        headers = {
            "x-api-key": self._api_key,
            "Content-Type": "application/json",
        }
        data = {
            "text": message,
            "speaker": speaker_uuid,
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

    async def async_get_tts_voices(self, language):
        """Fetch TTS voices from TopMediai."""
        if not self._voices:
            await self._fetch_voices()
        
        if language is None:
            return list(self._voices.values())
            
        return [v for v in self._voices.values() if v.language == language]

    async def _fetch_voices(self):
        """Fetch voices from API and populate cache."""
        websession = aiohttp_client.async_get_clientsession(self.hass)
        try:
            # Assuming GET request as per docs found earlier (though curl snippet had no headers, usually key is needed?)
            # Re-checking documentation snippet: it didn't explicitly shout headers for GET, but let's try with key.
            headers = {"x-api-key": self._api_key}
            async with websession.get(TOPMEDIAI_VOICES_URL, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # Response format: { "Voice": [ { "name": ..., "speaker": ..., "Languagename": ... } ] }
                    voice_list = data.get("Voice", [])
                    self._voices = {}
                    self._voices_data = {}
                    
                    for v_data in voice_list:
                        name = v_data.get("name")
                        speaker_id = v_data.get("speaker")
                        lang = v_data.get("Languagename", "en-US") # Default if missing
                        
                        if name and speaker_id:
                            # Use name as the ID for HA 
                            self._voices[name] = Voice(
                                voice_id=name,
                                name=name,
                                language=lang
                            )
                            # Store raw data for UUID lookup
                            self._voices_data[name] = v_data
                    
                    _LOGGER.debug("Fetched %d voices from TopMediaAI", len(self._voices))
                else:
                    _LOGGER.error("Failed to fetch voices: %s", response.status)
        except Exception as err:
            _LOGGER.error("Error fetching voices: %s", err)
