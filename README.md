# TopMediai TTS Integration for Home Assistant

This custom component integrates TopMediai's Text-to-Speech (TTS) service with Home Assistant, allowing you to use TopMediai's TTS capabilities within your smart home setup.

## Installation

### HACS Installation

1. Open Home Assistant and navigate to HACS (Home Assistant Community Store).
2. In HACS, go to "Integrations" and click on the "+ Explore & Add Integrations" button in the bottom right corner.
3. Search for "TopMediai TTS" and select it from the list.
4. Click "Install this Repository in HACS".
5. Restart Home Assistant.

### Manual Installation

1. Download the latest release from the [GitHub repository](https://github.com/HrMarcussen/topmediai_tts).
2. Copy the `topmediai_tts` folder from the downloaded zip file to your `custom_components` directory in your Home Assistant configuration directory.
3. Restart Home Assistant.

## Configuration

After installation, you need to configure the integration:

1. In Home Assistant, go to "Settings" > "Devices & Services".
2. Click on the "+ Add Integration" button.
3. Search for "TopMediai TTS" and select it.
4. Enter your TopMediai API key and preferred speaker ID in the configuration dialog.
5. Click "Submit" to complete the setup.

## Usage

Once configured, you can use TopMediai TTS as any other TTS platform in Home Assistant. You can call the `tts.topmediai_tts_say` service to convert text to speech.

Example service data:

```yaml
entity_id: media_player.your_media_player
message: "Hello, this is a test message from TopMediai TTS."
