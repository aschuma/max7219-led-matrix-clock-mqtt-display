import time
import random
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

def get_text_pixels(message, font=CP437_FONT):
    """Capture all pixel positions for a given text message"""
    pixels = []
    with canvas(device) as draw:
        text(draw, (0, 0), message, fill="white", font=proportional(font))
        # Get all white pixels from the canvas
        image = draw.im
        for y in range(8):
            for x in range(device.width):
                if image.getpixel((x, y)) > 0:  # If pixel is on
                    pixels.append((x, y))
    return pixels

def explode_effect(old_text, new_text, explosion_steps=15, implosion_steps=15, 
                   min_speed=1, max_speed=3, pause_between=0.5):
    """
    Create an explosion effect where text pixels fly outwards, then new text forms
    
    Parameters:
    - old_text: The text currently displayed
    - new_text: The text to transition to
    - explosion_steps: Number of frames for the explosion animation
    - implosion_steps: Number of frames for the implosion animation
    - min_speed, max_speed: Range of pixel movement speeds
    - pause_between: Pause time between explosion and implosion phases
    """
    # Get pixel positions for both texts
    old_pixels = get_text_pixels(old_text)
    new_pixels = get_text_pixels(new_text)
    
    # Calculate center of the display
    center_x = device.width // 2
    center_y = device.height // 2
    
    # Assign random speeds and directions to each pixel for explosion
    explosion_vectors = []
    for x, y in old_pixels:
        # Calculate direction vector from center
        dx = x - center_x
        dy = y - center_y
        
        # Normalize and apply random speed
        length = max(0.1, (dx**2 + dy**2)**0.5)  # Avoid division by zero
        speed = random.uniform(min_speed, max_speed)
        
        # Normalize direction vector and apply speed
        dx = (dx / length) * speed
        dy = (dy / length) * speed
        
        explosion_vectors.append(((x, y), (dx, dy)))
    
    # Assign vectors for implosion (new text)
    implosion_pixels = []
    for x, y in new_pixels:
        # Calculate random starting position outside the visible area
        angle = random.uniform(0, 2 * 3.14159)
        distance = random.uniform(10, 30)
        start_x = center_x + distance * math.cos(angle)
        start_y = center_y + distance * math.sin(angle)
        
        # Vector will point toward the final position
        dx = (x - start_x) / implosion_steps
        dy = (y - start_y) / implosion_steps
        
        implosion_pixels.append(((start_x, start_y), (dx, dy), (x, y)))
    
    # Phase 1: Explosion animation
    pixel_positions = {pos: pos for pos in old_pixels}
    for step in range(explosion_steps):
        with canvas(device) as draw:
            # Update and draw each pixel's new position
            for original_pos, (dx, dy) in explosion_vectors:
                if original_pos in pixel_positions:
                    x, y = pixel_positions[original_pos]
                    new_x = x + dx
                    new_y = y + dy
                    
                    # Check if pixel is still on screen
                    if (0 <= new_x < device.width and 0 <= new_y < device.height):
                        draw.point((int(new_x), int(new_y)), fill="white")
                        pixel_positions[original_pos] = (new_x, new_y)
                    else:
                        # Pixel moves off screen
                        del pixel_positions[original_pos]
        
        time.sleep(0.05)  # Animation speed
    
    # Pause between explosion and implosion
    time.sleep(pause_between)
    
    # Phase 2: Implosion animation (new text forms)
    current_positions = {}
    for i, ((start_x, start_y), (dx, dy), dest) in enumerate(implosion_pixels):
        current_positions[i] = (start_x, start_y)
    
    for step in range(implosion_steps):
        with canvas(device) as draw:
            # Update and draw each pixel's new position
            for i, ((start_x, start_y), (dx, dy), (dest_x, dest_y)) in enumerate(implosion_pixels):
                if i in current_positions:
                    x, y = current_positions[i]
                    
                    # Move pixel toward its destination
                    new_x = x + dx
                    new_y = y + dy
                    
                    # If we're on the last step, snap to exact destination
                    if step == implosion_steps - 1:
                        new_x, new_y = dest_x, dest_y
                    
                    # Check if pixel is on screen
                    if (0 <= new_x < device.width and 0 <= new_y < device.height):
                        draw.point((int(new_x), int(new_y)), fill="white")
                        current_positions[i] = (new_x, new_y)
        
        time.sleep(0.05)  # Animation speed

# Import needed for the random angle calculation
import math

# Example usage
if __name__ == "__main__":
    # Display initial text
    show_message(device, "HELLO", fill="white", font=proportional(CP437_FONT))
    time.sleep(1)
    
    # Transition with explode effect
    explode_effect("HELLO", "WORLD")
    
    # Display final text longer
    time.sleep(2)