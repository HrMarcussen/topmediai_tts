"""Custom integration for TopMediai TTS."""

DOMAIN = "topmediai_tts"

def setup(hass, config):
    """Set up the TopMediAI TTS component."""
    # Import the TTS platform
    hass.helpers.discovery.load_platform("tts", DOMAIN, {}, config)
    return True
