from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT
from PIL import Image, ImageDraw
import time

def scroll(device, prefix, scrolltext, font=None):
    """
    Display a fixed inverted prefix on the left and scrolling text on the right.
    The prefix stays fixed on the left side, inverted (black on white).
    The scrolltext scrolls from right to left, but only in the area after the prefix.
    
    Args:
        device: The luma.led_matrix device
        prefix: Fixed text to show on the left (inverted)
        scrolltext: Text to scroll from right to left
        font: Font to use (defaults to CP437_FONT if None)
    """
    if font is None:
        font = proportional(CP437_FONT)
    
    # Create a virtual image to measure the prefix width
    img = Image.new('1', (device.width, 8), 0)
    draw = ImageDraw.Draw(img)
    text(draw, (0, 0), prefix, font=font, fill="white")
    
    # Find the actual width of the prefix text
    pixels = list(img.getdata())
    prefix_width = 0
    for x in range(device.width):
        column_has_pixel = False
        for y in range(8):
            if pixels[y * device.width + x] > 0:
                column_has_pixel = True
                break
        if column_has_pixel:
            prefix_width = max(prefix_width, x + 1)
    
    # Add a small gap
    prefix_width += 2
    
    # Ensure prefix isn't too large (max 1/3 of display)
    max_prefix_width = device.width // 3
    if prefix_width > max_prefix_width:
        prefix_width = max_prefix_width
    
    # Create a virtual image for measuring scrolltext width
    scroll_img = Image.new('1', (device.width * 3, 8), 0)
    scroll_draw = ImageDraw.Draw(scroll_img)
    text(scroll_draw, (0, 0), scrolltext, font=font, fill="white")
    
    # Find the actual width of the scrolling text
    scroll_pixels = list(scroll_img.getdata())
    scroll_width = 0
    for x in range(device.width * 3):
        column_has_pixel = False
        for y in range(8):
            if scroll_pixels[y * (device.width * 3) + x] > 0:
                column_has_pixel = True
                break
        if column_has_pixel:
            scroll_width = max(scroll_width, x + 1)
    
    # Main scrolling loop - start with the text completely off-screen to the right
    virtual_width = device.width - prefix_width
    pos = -1 * virtual_width
    
    # Continue until the entire text has scrolled off to the left
    while pos < scroll_width + virtual_width:
        with canvas(device) as draw:
            # First, clear the entire canvas
            draw.rectangle((0, 0, device.width - 1, 7), fill="black")
            
            # Draw the inverted prefix area (white background)
            draw.rectangle((0, 0, prefix_width - 1, 7), fill="white")
            
            # Draw the prefix text (black on white)
            text(draw, (1, 0), prefix, font=font, fill="black")
            
            # Draw the scrolling text in the right section
            for x in range(prefix_width, device.width):
                # Calculate the position in the scroll image
                # This maps the display position to the correct part of the scroll image
                scroll_x = pos + (x - prefix_width)
                if 0 <= scroll_x < scroll_width:
                    # Copy pixels from the scroll virtual image to the display
                    for y in range(8):
                        pixel_index = y * (device.width * 3) + scroll_x
                        if pixel_index < len(scroll_pixels) and scroll_pixels[pixel_index] > 0:
                            draw.point((x, y), fill="white")
        
        pos += 1
        time.sleep(0.003)  # Adjust scroll speed

# Example usage
def main():
    # Create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(
        serial,
        cascaded=8,
        block_orientation=-90,
        blocks_arranged_in_reverse_order=False,
    )
    device.contrast(0)   
    
    # Example calls with different fonts
    scroll(device, "HI", "Welcome to my LED display!", proportional(CP437_FONT))
    time.sleep(1)
    scroll(device, "ABC", "This is scrolling text with tiny font", proportional(TINY_FONT))
    time.sleep(1)
    scroll(device, "ABC", "THIS IS THE SCROLLING TEXT ALL UPPER WITH TINY FONT", proportional(TINY_FONT))

if __name__ == "__main__":
    main()