#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import date
from datetime import datetime
from datetime import timedelta

from luma.core.interface.serial import spi, noop
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, LCD_FONT
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219

import config
from messageprovider import MessageProvider

CLOCK_FONT = CP437_FONT
MSG_FONT = proportional(LCD_FONT)
LONG_MSG_LEN = 11

class HoursMinutes:
    def __init__(self):
        self.ts = datetime.now()
        self._set_hm()

    def next(self):
        self.ts = self.ts + timedelta(seconds=1)
        self._set_hm()
    
    def _set_hm(self):
        self.hours = self.ts.strftime('%H')
        self.minutes = self.ts.strftime('%M')


def now():
    return HoursMinutes()


def day_of_week():
    return ["MO", "DI", "MI", "DO", "FR", "SA", "SO"][datetime.today().weekday()]

def cp437_encode(str):
   return [c.encode('cp437') for c in str]

def minute_change(device):
    """When we reach a minute change, animate it."""
    ts = now()
    
    def helper(current_y):
        with canvas(device) as draw:
            text(draw, (0, 1), ts.hours, fill="white", font=CLOCK_FONT)
            text(draw, (15, 1), ":", fill="white", font=proportional(TINY_FONT))
            text(draw, (17, current_y), ts.minutes, fill="white", font=CLOCK_FONT)
            text(draw, (device.width - 2 * 8, 1), day_of_week(), fill="white", font=proportional(CLOCK_FONT))
            
        time.sleep(0.08)
    
    for current_y in range(1, 9):
        helper(current_y)
    ts.next()
    for current_y in range(9, 1, -1):
        helper(current_y)


def animation(device, from_y, to_y):
    """Animate the whole thing, moving it into/out of the abyss."""
    ts = now()
    current_y = from_y
    while current_y != to_y:
        with canvas(device) as draw:
            text(draw, (0, current_y), ts.hours, fill="white", font=CLOCK_FONT)
            text(draw, (15, current_y), ":", fill="white", font=proportional(TINY_FONT))
            text(draw, (17, current_y), ts.minutes, fill="white", font=CLOCK_FONT)
            text(draw, (device.width - 2 * 8, current_y + 1), day_of_week(), fill="white", font=proportional(CLOCK_FONT))
        time.sleep(0.065)
        current_y += 1 if to_y > from_y else -1


def vertical_scroll(device, words):
    ts = now()
    messages = [" "] + words + [" "]
    virtual = viewport(device, width=device.width, height=len(messages) * 12)
    
    first_y_index = 0
    last_y_index = (len(messages) - 1) * 12
    
    with canvas(virtual) as draw:
        for i, word in enumerate(messages):
            text(draw, (0, i * 12), word, fill="white", font=MSG_FONT)
        text(draw, (0, first_y_index), ts.hours, fill="white", font=CLOCK_FONT)
        text(draw, (15, first_y_index), ":", fill="white", font=proportional(TINY_FONT))
        text(draw, (17, first_y_index), ts.minutes, fill="white", font=CLOCK_FONT)
        text(draw, (device.width - 2 * 8, first_y_index + 1), day_of_week(), fill="white", font=proportional(CLOCK_FONT))
        text(draw, (0, last_y_index), ts.hours, fill="white", font=CLOCK_FONT)
        text(draw, (15, last_y_index), ":", fill="white", font=proportional(TINY_FONT))
        text(draw, (17, last_y_index), ts.minutes, fill="white", font=CLOCK_FONT)
        text(draw, (device.width - 2 * 8, last_y_index), day_of_week(), fill="white", font=proportional(CLOCK_FONT))
    
    for i in range(virtual.height - 12):
        virtual.set_position((0, i))
        if i > 0 and i % 12 == 0:
            time.sleep(1.5)
        time.sleep(0.022)


def main():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=8, block_orientation=-90, blocks_arranged_in_reverse_order=False)
    device.contrast(0)
    
    msg = str(chr(177) * 8)
    show_message(device, msg, fill="white", font=CP437_FONT)
    
    # Start mqtt message subscription
    msg_provider = MessageProvider(config)
    msg_provider.loop_start()
    
    # The time ascends from the abyss...
    animation(device, 8, 1)
    
    toggle = False  # Toggle the second indicator every second
    while True:
        try:
            toggle = not toggle
            sec = datetime.now().second
            if sec == 59:
                # When we change minutes, animate the minute change
                minute_change(device)
            elif sec == 20:
                today = date.today()
                messages = [today.strftime("%2d.%2m.%4Y")] + [m for m in msg_provider.messages() if len(m) <= LONG_MSG_LEN]
                vertical_scroll(device, messages)
            elif sec == 40:
                today = date.today()
                long_messages = [ m for m in msg_provider.messages() if len(m) > LONG_MSG_LEN ]
                if len(long_messages) > 0:
                    messages = long_messages
                    animation(device, 1, 8)
                    for full_msg in messages:
                       show_message(device, cp437_encode(full_msg), fill="white", font=proportional(CLOCK_FONT), scroll_delay=0.024)
                    animation(device, 8, 1)
                else:
                    messages = [today.strftime("%2d.%2m.%4Y")] + [m for m in msg_provider.messages() if len(m) <= LONG_MSG_LEN]
                    vertical_scroll(device, messages)
            else:
                ts = now()
                with canvas(device) as draw:
                    text(draw, (0, 1), ts.hours, fill="white", font=CLOCK_FONT)
                    text(draw, (15, 1), ":" if toggle else " ", fill="white", font=proportional(TINY_FONT))
                    text(draw, (17, 1), ts.minutes, fill="white", font=CLOCK_FONT)
                    text(draw, (device.width - 2 * 8, 1), day_of_week(), fill="white", font=proportional(CLOCK_FONT))
                time.sleep(0.5)
        except KeyboardInterrupt:
            msg_provider.loop_stop()
            break


if __name__ == "__main__":
    main()
