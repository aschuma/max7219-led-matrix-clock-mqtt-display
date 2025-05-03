# MAX7219 LED Matrix MQTT Display

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![MQTT](https://img.shields.io/badge/MQTT-enabled-brightgreen.svg)](https://mqtt.org/)

A Raspberry Pi project that shows the current time and visualizes MQTT events on an 8x MAX7219 LED matrix display. 

## 📺 Demo

Click on the image below to watch a demo video:

[![Demo](https://github.com/aschuma/max7219-led-matrix-clock-mqtt-display/blob/main/img/max-display.jpg)](https://youtu.be/OGFmESPtSfg)

## ✨ Features

- Displays current date and time
- Visualizes MQTT events twice per minute
- Uses vertical scrolling when MQTT event text fits on the display
- Uses horizontal scrolling when MQTT message text is too long for the display
- Caches event text for a dedicated amount of time
- Automatic event processing with standardized message structure

## 🔧 Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- MAX7219 8x8 LED Matrix (x8 chained modules)
- Logic level converter (3.3V to 5V)
- Power supply
- Jumper wires

## 📋 Software Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/aschuma/max7219-led-matrix-clock-mqtt-display.git
   cd max7219-led-matrix-clock-mqtt-display
   ```

2. Create and activate a Python virtual environment. (I'm still using Python 3.7, but newer versions should work as well.):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your settings:
   ```bash
   cp config.py.template config.py
   # Edit config.py with your preferred settings
   ```

5. Run the application:
   ```bash
   python __init__.py
   ```

## 🔌 Hardware Setup

This project uses the [luma.led_matrix](https://github.com/rm-hull/luma.led_matrix) driver by Richard Hull. For detailed wiring instructions, please refer to the [official documentation](https://luma-led-matrix.readthedocs.io/en/latest/install.html#pre-requisites), particularly the section on GPIO pin-outs for MAX7219 Devices (SPI).

### 💡 Important Note

As mentioned in the [luma.led_matrix documentation](https://luma-led-matrix.readthedocs.io/en/latest/notes.html), it's recommended to use a logic level converter to bridge the 3.3V (Raspberry Pi) and 5V (MAX7219) gap. We recommend using a bidirectional logic level converter such as [this one](https://www.amazon.com/Level-Conversion-Module-Sensor-Raspberry/dp/B07QC929R4/).

## 📡 MQTT Integration

Submit MQTT events using `display/` as the base path. The payload should be formatted as JSON:

```json
{
  "name": "Temperature",
  "description": "Living room temperature sensor",
  "weight": 1,
  "value": "22.5",
  "unit": "°C",
  "timestamp": "2023-05-03T14:30:00Z"
}
```

### Payload Fields

| Field | Description |
|-------|-------------|
| `name` | Label for the displayed value |
| `description` | Description of the value (currently unused) |
| `weight` | Integer used for sorting multiple values |
| `value` | The value to display |
| `unit` | Unit of the displayed value |
| `timestamp` | ISO timestamp (for debugging purposes) |

## 🙏 Credits

- [Richard Hull](https://github.com/rm-hull) for the excellent [luma.led_matrix](https://github.com/rm-hull/luma.led_matrix) driver
- All contributors to this project

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

