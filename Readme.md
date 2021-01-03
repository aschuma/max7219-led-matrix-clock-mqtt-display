# Visualizes MQTT events on an 8 x MAX7219 8x8 led matrix / raspberry pi w

Here is what you get when you deploy the application on a PI / MAX7219 led matrix, please click on the image to see more.

[![Demo](https://github.com/aschuma/max7219-led-matrix-clock-mqtt-display/blob/main/img/max-display.jpg)](https://youtu.be/OGFmESPtSfg)


## Some hints for setting up the software and the hardware

* This project uses the luma led matrix driver coded by Richard Hull https://github.com/rm-hull/luma.led_matrix/blob/master/README.rst (Credits to Richard for his excellent work).
* For LED matrix setup/wiring, please consult https://luma-led-matrix.readthedocs.io/en/latest/install.html#pre-requisites, especially the section GPIO pin-outs MAX7219 Devices (SPI) 
* As Richard Hull mentiones in https://luma-led-matrix.readthedocs.io/en/latest/notes.html, you should consider to use a logic level converter to bridge the 3.3V (PI) <-> 5V (MAX7219) gap. I'am using https://www.amazon.com/Level-Conversion-Module-Sensor-Raspberry/dp/B07QC929R4/ref=sr_1_16?dchild=1&keywords=5V+3.3V+8-Kanal+Logic+Level+Converter+f%C3%BCr+Arduino+Raspberry+Pi&qid=1609707511&sr=8-16, but other bidirectional converter should work fine too.
* Checkout source code `git clone https://github.com/aschuma/max7219-led-matrix-clock-mqtt-display.git`
* Create a python 3 virtual environment
* Install 3rd party libraries defined in `requirements.txt`
* Copy `config.py.template` to `config.py` and adjust the settings
* Run the `__init__.py` script in the base directory   
* Submit MQTT events using `display/` as base path. The payload of the events should be like   
   ```
    {
        name : <label-string-for-the-value>,
        description: <string-describing-the-value--currently-unused>,
        weight : <integer-used-for-sorting-the-values>,
        value : <the-value-to-display-as-string>,
        unit : <unit-of-the-value-to-display-as-string>,
        timestamp: <iso-timestamp-as-string--only-for-debugging-purpose>
    }
   ```

