import logging
import requests
from homeassistant.components.tts import CONF_LANG, PLATFORM_SCHEMA, Provider
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

CONF_API_KEY = 'api_key'
CONF_SPEAKER = 'speaker'
DEFAULT_LANG = 'en-US'
DEFAULT_SPEAKER = '00157290-3826-11ee-a861-00163e2ac61b'
TOPMEDIAI_TTS_URL = "https://api.topmediai.com/v1/text2speech"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_LANG, default=DEFAULT_LANG): cv.string,
    vol.Optional(CONF_SPEAKER, default=DEFAULT_SPEAKER): cv.string,
})

def get_engine(hass, config, discovery_info=None):
    api_key = config[CONF_API_KEY]
    language = config.get(CONF_LANG, DEFAULT_LANG)
    speaker = config.get(CONF_SPEAKER, DEFAULT_SPEAKER)
    return TopMediAITTSProvider(hass, api_key, language, speaker)

class TopMediAITTSProvider(Provider):
    def __init__(self, hass, api_key, lang, speaker):
        self.hass = hass
        self._api_key = api_key
        self._language = lang
        self._speaker = speaker

    @property
    def default_language(self):
        return self._language

    @property
    def supported_languages(self):
        return [self._language]

    def get_tts_audio(self, message, language, options=None):
        headers = {
            'x-api-key': self._api_key,
            'Content-Type': 'application/json'
        }
        data = {
            'text': message,
            'speaker': self._speaker,
            'emotion': 'Neutral'
        }

        try:
            response = requests.post(TOPMEDIAI_TTS_URL, json=data, headers=headers)
            response.raise_for_status()
            response_data = response.json()

            _LOGGER.debug("TopMediAI API response data: %s", response_data)

            if 'data' in response_data and 'oss_url' in response_data['data']:
                audio_url = response_data['data']['oss_url']
                audio_content = requests.get(audio_url).content
                return "mp3", audio_content
            else:
                _LOGGER.error("oss_url not found in the response: %s", response_data)
                return None, None

        except requests.exceptions.HTTPError as http_err:
            _LOGGER.error("HTTP error from TopMediAI: %s", http_err)
        except requests.exceptions.RequestException as req_err:
            _LOGGER.error("Request exception from TopMediAI: %s", req_err)
        except KeyError as key_err:
            _LOGGER.error("Key error in processing response: %s", key_err)

        return None, None
