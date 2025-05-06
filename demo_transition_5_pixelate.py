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
    pixels = set()
    with canvas(device) as draw:
        text(draw, (0, 0), message, fill="white", font=proportional(font))
        # Get all white pixels from the canvas
        image = draw.im
        for y in range(8):
            for x in range(device.width):
                if image.getpixel((x, y)) > 0:  # If pixel is on
                    pixels.add((x, y))
    return pixels

def pixelate_effect(old_text, new_text, dissolve_steps=10, form_steps=10, 
                   noise_ratio_max=0.6, pause_between=0.5):
    """
    Create a pixelate effect where text dissolves into random pixels then forms new text
    
    Parameters:
    - old_text: The text currently displayed
    - new_text: The text to transition to
    - dissolve_steps: Number of frames for the dissolve animation
    - form_steps: Number of frames for the formation animation
    - noise_ratio_max: Maximum ratio of noise pixels to add (0.0-1.0)
    - pause_between: Pause time between dissolve and formation phases
    """
    # Get pixel positions for both texts
    old_pixels = get_text_pixels(old_text)
    new_pixels = get_text_pixels(new_text)
    
    # Get total display dimensions
    width, height = device.width, device.height
    total_pixels = width * height
    
    # Create a list of all possible pixel positions
    all_positions = [(x, y) for y in range(height) for x in range(width)]
    
    # Phase 1: Dissolve the old text
    current_pixels = old_pixels.copy()
    pixels_to_remove = list(old_pixels)  # Convert to list for random.sample
    random.shuffle(pixels_to_remove)  # Randomize removal order
    
    # Calculate how many pixels to remove in each step
    pixels_per_step = max(1, len(pixels_to_remove) // dissolve_steps)
    
    # Calculate maximum number of noise pixels to add
    max_noise_pixels = int(total_pixels * noise_ratio_max)
    
    for step in range(dissolve_steps):
        # Calculate noise ratio that increases with each step
        noise_ratio = step / dissolve_steps * noise_ratio_max
        num_noise_pixels = int(total_pixels * noise_ratio)
        
        # Remove some pixels from the old text
        start_idx = step * pixels_per_step
        end_idx = min(start_idx + pixels_per_step, len(pixels_to_remove))
        for pixel in pixels_to_remove[start_idx:end_idx]:
            if pixel in current_pixels:
                current_pixels.remove(pixel)
        
        # Add random noise pixels
        noise_pixels = random.sample(all_positions, min(num_noise_pixels, len(all_positions)))
        for pixel in noise_pixels:
            if random.random() < 0.5:  # 50% chance to add each noise pixel
                current_pixels.add(pixel)
        
        # Draw the current state
        with canvas(device) as draw:
            for x, y in current_pixels:
                draw.point((x, y), fill="white")
        
        time.sleep(0.05)  # Animation speed
    
    # Pause between phases
    time.sleep(pause_between)
    
    # Phase 2: Form the new text
    current_pixels = set()  # Start with a blank canvas
    pixels_to_add = list(new_pixels)
    random.shuffle(pixels_to_add)  # Randomize addition order
    
    # Calculate how many pixels to add in each step
    pixels_per_step = max(1, len(pixels_to_add) // form_steps)
    
    for step in range(form_steps + 1):
        # Calculate decreasing noise ratio
        noise_ratio = (1 - step / form_steps) * noise_ratio_max
        num_noise_pixels = int(total_pixels * noise_ratio)
        
        # Add some pixels from the new text
        if step < form_steps:  # In the last step, we'll add all remaining pixels
            start_idx = step * pixels_per_step
            end_idx = min(start_idx + pixels_per_step, len(pixels_to_add))
            pixels_to_add_now = pixels_to_add[start_idx:end_idx]
        else:
            # In the final step, make sure all new text pixels are added
            pixels_to_add_now = pixels_to_add
        
        for pixel in pixels_to_add_now:
            current_pixels.add(pixel)
        
        # Add random noise pixels (decreasing with each step)
        current_pixels = set(p for p in current_pixels if p in new_pixels)  # Remove old noise
        noise_pixels = random.sample(all_positions, min(num_noise_pixels, len(all_positions)))
        for pixel in noise_pixels:
            if random.random() < 0.5 and pixel not in new_pixels:  # Don't add noise where text should be
                current_pixels.add(pixel)
        
        # Draw the current state
        with canvas(device) as draw:
            for x, y in current_pixels:
                draw.point((x, y), fill="white")
        
        time.sleep(0.05)  # Animation speed
    
    # Final frame with clean new text (no noise)
    with canvas(device) as draw:
        for x, y in new_pixels:
            draw.point((x, y), fill="white")

# Example usage
if __name__ == "__main__":
    # Display initial text
    show_message(device, "HELLO", fill="white", font=proportional(CP437_FONT), scroll_delay=0)
    time.sleep(1)
    
    # Transition with pixelate effect
    pixelate_effect("HELLO", "WORLD")
    
    # Display final text longer
    time.sleep(2)