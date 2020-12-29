# Purpose 
Clock and MQTT data visualisation panel based on an 8 x MAX7219 8x8 led matrix running on a PI 4B

Here is what you get when you deploy the application on your PI / MAX7219 led matrix, please click on the image to see more.

[![Demo](https://github.com/aschuma/max7219-led-matrix-clock-mqtt-display/blob/main/img/max-display.jpg)](https://youtu.be/OGFmESPtSfg)


## Some hints for setting up the software and the hardware

* Please consult https://github.com/rm-hull/luma.led_matrix/blob/master/README.rst for LED Matrix setup/wiring
* Checkout source code `git clone https://github.com/aschuma/max7219-led-matrix-clock-mqtt-display.git`
* Create a python 3 virtual environment
* Install 3rd party libraries defined in `requirements.txt`
* Copy `config.py.template` to `config.py` and adjust the settings
* Run the `__init__.py` script in the base directory   
* Submit MQTT events using `display/` as base path. The payload of the events should be like   
   ```
    {
        name : <label-string-for-the-value>,
        description: <string-describing-the-value--currently-unused>',
        weight : <integer-used-for-sorting-the-values>,
        value : <the-value-to-display-as-string>,
        unit : <unit-of-the-value-to-display-as-string>,
        timestamp: <iso-timestamp-as-string--only-for-debugging-purpose>
    }
   ```

