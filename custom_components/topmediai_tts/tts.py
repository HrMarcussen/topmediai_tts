"""Support for the TopMediai TTS service."""
import logging
import voluptuous as vol

from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA,
    TextToSpeechEntity,
    Voice,
    ATTR_VOICE,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import aiohttp_client, config_validation as cv

from .const import CONF_SPEAKER, DEFAULT_LANG, DEFAULT_SPEAKER, DOMAIN
from .languages import get_iso_code

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
        self._attr_supported_options = [ATTR_VOICE]
        self._voices = {} # Cache for voices: {voice_id: Voice(...)}
        self._voices_data = {} # Cache for raw API data: {voice_name: api_data_dict}

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        await self._fetch_voices()
        self.async_write_ha_state()

    @property
    def default_language(self):
        """Return the default language."""
        return self._language

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        if self._voices_data:
             # Extract unique languages from loaded voices data
             languages = set()
             for v in self._voices_data.values():
                 langs = v.get("mapped_languages")
                 if langs:
                     languages.update(langs)
             return list(languages)
        
        # DEBUG FALLBACK: Return common languages if voices failed to load
        return ["en-US", "da-DK", "de-DE", "es-ES", "fr-FR", "it-IT", "nl-NL", "pl-PL", "pt-PT", "ru-RU", "sv-SE"]

    async def async_get_tts_audio(self, message, language, options=None):
        """Load TTS from TopMediai."""
        websession = aiohttp_client.async_get_clientsession(self.hass)
        options = options or {}
        
        # Determine speaker:
        speaker_uuid = self._speaker

        # If a specific voice ID (name in our case) is requested via HA
        voice_name = options.get("voice")
        if voice_name:
             # Find the UUID for this voice name in our cache
             if voice_name in self._voices_data:
                 speaker_uuid = self._voices_data[voice_name].get("speaker")
             else:
                 _LOGGER.warning("TopMediaAI: Requested voice '%s' not found in cache. Using default.", voice_name)
        
        # Allow raw speaker UUID override via options
        if CONF_SPEAKER in options:
            speaker_uuid = options[CONF_SPEAKER]
        
        # Config entry options override
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

                if "data" in response_data and "oss_url" in response_data["data"]:
                    audio_url = response_data["data"]["oss_url"]
                    async with websession.get(audio_url) as audio_response:
                        audio_response.raise_for_status()
                        audio_content = await audio_response.read()
                        return "mp3", audio_content
                else:
                    _LOGGER.error(
                        "TopMediaAI: oss_url not found in response: %s", response_data
                    )
                    return None, None

        except Exception as err:
            _LOGGER.error("TopMediaAI: Error during TTS request: %s", err)
            return None, None

    async def async_get_tts_voices(self, language):
        """Fetch TTS voices from TopMediai."""
        if not self._voices:
            await self._fetch_voices()
        
        if language is None:
            return list(self._voices.values())
            
        # Filter voices by language using the data cache
        found_voices = []
        for name, data in self._voices_data.items():
            mapped_langs = data.get("mapped_languages", [])
            if language in mapped_langs:
                voice = self._voices.get(name)
                if voice:
                    found_voices.append(voice)
        return found_voices

    async def _fetch_voices(self):
        """Fetch voices from API and populate cache."""
        _LOGGER.debug("TopMediaAI: Starting voice fetch...")
        websession = aiohttp_client.async_get_clientsession(self.hass)
        try:
            headers = {"x-api-key": self._api_key}
            async with websession.get(TOPMEDIAI_VOICES_URL, headers=headers) as response:
                _LOGGER.debug("TopMediaAI: Voice fetch status: %s", response.status)
                if response.status == 200:
                    data = await response.json()
                    voice_list = data.get("Voice", [])
                    _LOGGER.debug("TopMediaAI: Found %d voices in API response.", len(voice_list))
                    
                    self._voices = {}
                    self._voices_data = {}
                    
                    for v_data in voice_list:
                        name = v_data.get("name")
                        speaker_id = v_data.get("speaker")
                        if not name or not speaker_id:
                            continue

                        raw_lang_str = v_data.get("Languagename", "English")
                        # Split multiple languages by comma
                        raw_langs = [l.strip() for l in raw_lang_str.split(",")]
                        mapped_langs = set()
                        for raw_lang in raw_langs:
                            lang_code = get_iso_code(raw_lang)
                            mapped_langs.add(lang_code)
                        
                        self._voices[name] = Voice(
                            voice_id=name,
                            name=name,
                        )
                        # Store mapped languages list in data for easy access
                        v_data["mapped_languages"] = list(mapped_langs)
                        # Also keep single mapped_language for backward compat or primary sorting? 
                        # Just grab the first one if we need a single one, but filter logic uses list.
                        if mapped_langs:
                            v_data["mapped_language"] = list(mapped_langs)[0]
                            
                        self._voices_data[name] = v_data
                    
                    _LOGGER.debug("TopMediaAI: Successfully cached %d voices.", len(self._voices))
                else:
                    _LOGGER.error("TopMediaAI: Failed to fetch voices. Status: %s. Body: %s", response.status, await response.text())
        except Exception as err:
            _LOGGER.error("TopMediaAI: Exception fetching voices: %s", err)
