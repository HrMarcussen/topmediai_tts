"""The TopMediai TTS integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_SPEAKER
from homeassistant.const import CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["tts"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the TopMediai TTS component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up TopMediai TTS from a config entry."""
    # Store settings in hass.data if needed, but for TTS platform it's often passed via config.
    # However, since we are using config_flow, the entity will likely get config from the entry or options.
    hass.data.setdefault(DOMAIN, {})
    
    # We don't strictly need to store anything here if the platform setup handles it,
    # but it's good practice to have the key available.
    hass.data[DOMAIN][entry.entry_id] = {
        CONF_API_KEY: entry.data[CONF_API_KEY],
        CONF_SPEAKER: entry.data[CONF_SPEAKER],
    }

    # Forward the setup to the tts platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
