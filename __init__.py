#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from luma.core.interface.serial import spi, noop
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, LCD_FONT
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219

import config
from messageprovider import MessageProvider
from timestamp import Timestamp, now

LONG_MSG_LEN = 11

class ClockDigit:

    def __init__(self, position, transition_delay =0, height=10):
        self.position = position
        self.transitions_delay = transition_delay
        self.height = height

    def transition(self, painter, digit, digit_next, offset = 0):
        if digit == digit_next:
            painter(self.position, digit)
        else:    
            delayed_offset = min(self.height, max(0, offset - self.transitions_delay)) 
            painter((self.position[0], self.position[1] - delayed_offset), digit)
            painter((self.position[0], self.position[1] - delayed_offset + self.height), digit_next)

class Clock:
    def __init__(self):
        self.digits = [ 
            ClockDigit(position=(0,1),transition_delay=12),
            ClockDigit(position=(8,1),transition_delay=8),
            ClockDigit(position=(17,1),transition_delay=4),
            ClockDigit(position=(25,1),transition_delay=0)]

    def max_tick(self): return 16

    def transition(self, painter, ts0, ts1, tick ):
        self.digits[0].transition(
            painter=painter,
            digit=ts0.hours[0], 
            digit_next=ts1.hours[0], 
            offset=tick)
        self.digits[1].transition(
            painter=painter,
            digit=ts0.hours[1], 
            digit_next=ts1.hours[1], 
            offset=tick)
        self.digits[2].transition(
            painter=painter,
            digit=ts0.minutes[0], 
            digit_next=ts1.minutes[0], 
            offset=tick)
        self.digits[3].transition(
            painter=painter,
            digit=ts0.minutes[1], 
            digit_next=ts1.minutes[1], 
            offset=tick)


def draw_time(draw, ts, x_offset=0, y_offset=0, minute_y_offset=0, toggle=True):
    def txt(x,y, value, font=CP437_FONT):
        text(draw, (x + x_offset, 1 + y + y_offset), value, fill="white", font=font)    

    txt(0, 0, ts.hours)
    txt(15, 0,":" if toggle else " ", font=proportional(TINY_FONT))
    txt(17, minute_y_offset, ts.minutes)
    txt(48, 0, ts.day_of_week, font=proportional(CP437_FONT))


def minute_change(device):
    """When we reach a minute change, animate it."""
    timestamp = now()

    def helper(current_y):
        with canvas(device) as draw:
            draw_time(draw=draw, ts=timestamp, minute_y_offset=current_y, toggle=False)
        time.sleep(0.08)

    for current_y in range(0, 9):
        helper(current_y)
    timestamp = timestamp.next()
    for current_y in range(9, 0, -1):
        helper(current_y)


def minute_change_v2(device):
    """When we reach a minute change, animate it."""
    ts = now()
    ts_next = ts.next()
    
    clock = Clock()
    for tick in range(clock.max_tick()):
        with canvas(device) as draw:

            text(draw, (48,1), ts.day_of_week, fill="white", font=proportional(CP437_FONT))    

            def painter(position,digit):
                text(draw, position, digit, fill="white", font=CP437_FONT)  

            clock.transition(painter,ts, ts_next,tick)
            time.sleep(0.025)




def animation(device, from_y, to_y):
    """Animate the whole thing, moving it into/out of the abyss."""
    timestamp = now()
    current_y = from_y
    while current_y != to_y:
        with canvas(device) as draw:
            draw_time(draw=draw, ts=timestamp, y_offset=current_y, toggle=False)
        time.sleep(0.065)
        current_y += 1 if to_y > from_y else -1


def vertical_scroll(device, words):
    timestamp = now()
    messages = [" "] + words + [" "]
    virtual = viewport(device, width=device.width, height=len(messages) * 12)

    first_y_index = 0
    last_y_index = (len(messages) - 1) * 12

    with canvas(virtual) as draw:
        for i, word in enumerate(messages):
            text(draw, (0, i * 12), word, fill="white", font=proportional(LCD_FONT))
        draw_time(draw=draw, ts=timestamp, y_offset=first_y_index)
        draw_time(draw=draw, ts=timestamp, y_offset=last_y_index)

    for i in range(virtual.height - 12):
        virtual.set_position((0, i))
        if i > 0 and i % 12 == 0:
            time.sleep(1.5)
        time.sleep(0.022)


def horizontal_scroll(device, messages):
    def cp437_encode(str):
        return [c.encode("cp437") for c in str]

    animation(device, 1, 8)
    for msg in messages:
        show_message(
            device,
            cp437_encode(msg),
            fill="white",
            font=proportional(CP437_FONT),
            scroll_delay=0.024,
        )
    animation(device, 8, 1)


def main():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(
        serial,
        cascaded=8,
        block_orientation=-90,
        blocks_arranged_in_reverse_order=False,
    )
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
            timestamp = now()
            sec = timestamp.ts.second
            if sec == 59:
                # When we change minutes, animate the minute change
                minute_change_v2(device)
            elif sec == 10:
                messages = [timestamp.date] + msg_provider.short_messages(LONG_MSG_LEN)
                vertical_scroll(device, messages)
            elif sec == 40:
                long_messages = msg_provider.long_messages(LONG_MSG_LEN)
                if len(long_messages) > 0:
                    horizontal_scroll(device, long_messages)
                else:
                    messages = [timestamp.date] + msg_provider.short_messages(LONG_MSG_LEN)
                    vertical_scroll(device, messages)
            else:
                with canvas(device) as draw:
                    draw_time(draw=draw, ts=timestamp, toggle=toggle)
                time.sleep(0.5)
        except KeyboardInterrupt:
            msg_provider.loop_stop()
            break


if __name__ == "__main__":
    main()
