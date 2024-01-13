from homeassistant.const import CONF_API_KEY
from .const import DOMAIN, CONF_SPEAKER

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    # Set up TopMediai TTS from a config entry
    hass.data[DOMAIN] = {
        CONF_API_KEY: entry.data[CONF_API_KEY],
        CONF_SPEAKER: entry.data[CONF_SPEAKER]
    }
    return True
