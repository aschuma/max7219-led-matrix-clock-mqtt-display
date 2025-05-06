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

def blinds_effect(old_text, new_text, steps=8, num_blinds=4, vertical=False, reverse=False):
    """
    Create a venetian blinds effect where text transitions with horizontal/vertical slats
    
    Parameters:
    - old_text: The text currently displayed
    - new_text: The text to transition to
    - steps: Number of animation steps for each blind
    - num_blinds: Number of blinds to use (should divide evenly into height/width)
    - vertical: If True, uses vertical blinds instead of horizontal
    - reverse: If True, reverses the order of blind transitions
    """
    # Get image data for both texts
    old_image = get_text_image(old_text)
    new_image = get_text_image(new_text)
    
    # Get dimensions
    width, height = device.width, device.height
    
    # Calculate blind size (round to ensure integer division)
    blind_size = height // num_blinds if not vertical else width // num_blinds
    
    # Ensure at least 1 pixel per blind
    blind_size = max(1, blind_size)
    num_blinds = height // blind_size if not vertical else width // blind_size
    
    # Create a list of blind indices
    blind_indices = list(range(num_blinds))
    if reverse:
        blind_indices.reverse()
    
    # Transition one blind at a time
    for blind_idx in blind_indices:
        # Calculate the position of this blind
        blind_start = blind_idx * blind_size
        blind_end = min(blind_start + blind_size, height if not vertical else width)
        
        # Animate the blind closing
        for step in range(steps + 1):
            # Calculate how far the blind has closed (0.0 to 1.0)
            close_ratio = step / steps
            
            with canvas(device) as draw:
                # Draw the current state of all blinds
                for y in range(height):
                    for x in range(width):
                        # Determine if this pixel is in the current animating blind
                        in_current_blind = False
                        if vertical:
                            in_current_blind = blind_start <= x < blind_end
                        else:
                            in_current_blind = blind_start <= y < blind_end
                        
                        # For pixels in the current blind, determine if they've transitioned
                        is_new_text = False
                        if in_current_blind:
                            # Calculate position within the blind (0.0 to 1.0)
                            if vertical:
                                pos_in_blind = (x - blind_start) / blind_size
                            else:
                                pos_in_blind = (y - blind_start) / blind_size
                            
                            # The pixel has transitioned if its position is less than close_ratio
                            is_new_text = pos_in_blind <= close_ratio
                        else:
                            # For blinds that have already transitioned, show new text
                            if vertical:
                                is_new_text = x < blind_start
                            else:
                                is_new_text = y < blind_start
                        
                        # Draw the appropriate pixel
                        image_to_use = new_image if is_new_text else old_image
                        try:
                            pixel = image_to_use.getpixel((x, y))
                            if pixel > 0:  # If pixel is on
                                draw.point((x, y), fill="white")
                        except IndexError:
                            # Skip pixels that might be out of bounds
                            pass
            
            time.sleep(0.02)  # Animation speed
    
    # Make sure the final image is displayed cleanly
    with canvas(device) as draw:
        for y in range(height):
            for x in range(width):
                pixel = new_image.getpixel((x, y))
                if pixel > 0:  # If pixel is on
                    draw.point((x, y), fill="white")

def horizontal_blinds(old_text, new_text, num_blinds=4, reverse=False):
    """Horizontal blinds effect (helper function)"""
    blinds_effect(old_text, new_text, num_blinds=num_blinds, vertical=False, reverse=reverse)

def vertical_blinds(old_text, new_text, num_blinds=8, reverse=False):
    """Vertical blinds effect (helper function)"""
    blinds_effect(old_text, new_text, num_blinds=num_blinds, vertical=True, reverse=reverse)

# Example usage
if __name__ == "__main__":
    # Display initial text
    show_message(device, "HELLO", fill="white", font=proportional(CP437_FONT), scroll_delay=0)
    time.sleep(1)
    
    # Transition with blinds effects
    print("Horizontal blinds (top to bottom)")
    horizontal_blinds("HELLO", "WORLD", num_blinds=4)
    time.sleep(1)
    
    print("Horizontal blinds (bottom to top)")
    horizontal_blinds("WORLD", "HELLO", num_blinds=4, reverse=True)
    time.sleep(1)
    
    print("Vertical blinds (left to right)")
    vertical_blinds("HELLO", "WORLD", num_blinds=8)
    time.sleep(1)
    
    print("Vertical blinds (right to left)")
    vertical_blinds("WORLD", "HELLO", num_blinds=8, reverse=True)
    
    # Display final text longer
    time.sleep(2)