# TopMediai TTS Integration for Home Assistant

This custom component integrates TopMediai's Text-to-Speech (TTS) service with Home Assistant, allowing you to use TopMediai's TTS capabilities within your smart home setup.

> [!NOTE]
> This integration has been updated to use fully asynchronous communication for better performance and stability in Home Assistant.

## Installation

### HACS Installation

1. Open Home Assistant and navigate to HACS.
2. In HACS, go to "Integrations" and click on the "+ Explore & Add Integrations" button.
3. Search for "TopMediai TTS" and select it.
4. Click "Install this Repository in HACS".
5. Restart Home Assistant.

### Manual Installation

1. Download the latest release from the [GitHub repository](https://github.com/HrMarcussen/topmediai_tts).
2. Copy the `topmediai_tts` folder from the downloaded zip file to your `custom_components` directory in your Home Assistant configuration directory.
3. Restart Home Assistant.

## Configuration

After installation, the integration can be configured via the UI:

1. Go to **Settings** > **Devices & Services**.
2. Click **+ Add Integration**.
3. Search for **TopMediai TTS**.
4. Enter your **API Key** and **Speaker ID**.
   - The integration will verify your API key immediately.

## Usage

You can use the standard `tts.speak` service or the legacy `tts.topmediai_tts_say` service.

```yaml
service: tts.speak
target:
  entity_id: tts.topmediai
data:
  media_player_entity_id: media_player.living_room
  message: "Hello, this is a test message from TopMediai TTS."
```
