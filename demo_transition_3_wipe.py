import time
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT

# Configuration for 8 cascaded MAX7219 devices
num_devices = 8
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=num_devices, block_orientation=-90, rotate=0)
device.contrast(15)  # Adjust brightness (0-15)

# Virtual viewport for scrolling
virtual = viewport(device, width=device.width, height=device.height)

def get_text_image(message, font=CP437_FONT):
    """Capture image data for a given text message"""
    with canvas(device) as draw:
        text(draw, (0, 0), message, fill="white", font=proportional(font))
        # Return a copy of the image
        return draw.im.copy()

def wipe_effect(old_text, new_text, direction="left-to-right", steps=30):
    """
    Create a wipe effect where new text replaces old text with a directional wipe
    
    Parameters:
    - old_text: The text currently displayed
    - new_text: The text to transition to
    - direction: One of "left-to-right", "right-to-left", "top-to-bottom", "bottom-to-top"
    - steps: Number of frames for the animation
    """
    # Get image data for both texts
    old_image = get_text_image(old_text)
    new_image = get_text_image(new_text)
    
    # Determine dimensions
    width, height = device.width, device.height
    
    # Set direction parameters
    is_horizontal = direction in ["left-to-right", "right-to-left"]
    is_reversed = direction in ["right-to-left", "bottom-to-top"]
    
    # Determine the total range to animate over
    total_range = width if is_horizontal else height
    
    # Calculate step size
    step_size = max(1, total_range // steps)
    
    # Animation loop
    for step in range(steps + 1):
        # Calculate current position of the wipe edge
        progress = step / steps
        position = int(total_range * progress)
        
        # Reverse position if needed
        if is_reversed:
            position = total_range - position
        
        with canvas(device) as draw:
            # Draw combined image based on wipe position
            for y in range(height):
                for x in range(width):
                    # Determine which image to sample from based on wipe position
                    use_new_image = False
                    
                    if is_horizontal:
                        # For horizontal wipes
                        if (not is_reversed and x < position) or (is_reversed and x >= position):
                            use_new_image = True
                    else:
                        # For vertical wipes
                        if (not is_reversed and y < position) or (is_reversed and y >= position):
                            use_new_image = True
                    
                    # Get pixel value from appropriate image
                    try:
                        # Check if the point is inside the bounds
                        if 0 <= x < width and 0 <= y < height:
                            pixel = new_image.getpixel((x, y)) if use_new_image else old_image.getpixel((x, y))
                            if pixel > 0:  # If pixel is on
                                draw.point((x, y), fill="white")
                    except IndexError:
                        # Skip pixels that might be out of bounds
                        pass
        
        # Control animation speed
        time.sleep(0.02)

def horizontal_wipe(old_text, new_text, right_to_left=False):
    """Horizontal wipe effect (helper function)"""
    direction = "right-to-left" if right_to_left else "left-to-right"
    wipe_effect(old_text, new_text, direction=direction)

def vertical_wipe(old_text, new_text, bottom_to_top=False):
    """Vertical wipe effect (helper function)"""
    direction = "bottom-to-top" if bottom_to_top else "top-to-bottom"
    wipe_effect(old_text, new_text, direction=direction)

# Example usage
if __name__ == "__main__":
    # Display initial text
    show_message(device, "HELLO", fill="white", font=proportional(CP437_FONT), scroll_delay=0)
    time.sleep(1)
    
    # Transition with wipe effects
    print("Left to right wipe")
    horizontal_wipe("HELLO", "WORLD")
    time.sleep(1)
    
    print("Right to left wipe")
    horizontal_wipe("WORLD", "HELLO", right_to_left=True)
    time.sleep(1)
    
    print("Top to bottom wipe")
    vertical_wipe("HELLO", "WORLD")
    time.sleep(1)
    
    print("Bottom to top wipe")
    vertical_wipe("WORLD", "HELLO", bottom_to_top=True)
    
    # Display final text longer
    time.sleep(2)