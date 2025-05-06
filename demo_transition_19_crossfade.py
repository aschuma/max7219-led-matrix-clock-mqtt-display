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

def get_character_positions(message, font=CP437_FONT):
    """
    Map each character in the message to its pixel positions and determine character boundaries
    Returns a list of (start_x, end_x, pixels) for each character
    """
    # First get all text pixels
    all_pixels = {}
    with canvas(device) as draw:
        text(draw, (0, 0), message, fill="white", font=proportional(font))
        # Get all white pixels from the canvas
        image = draw.im
        for y in range(8):
            for x in range(device.width):
                if image.getpixel((x, y)) > 0:  # If pixel is on
                    all_pixels[(x, y)] = 1
    
    # If no text was rendered (empty message), return empty list
    if not all_pixels:
        return []
    
    # Get the x-coordinates of all pixels
    x_coords = [x for x, y in all_pixels.keys()]
    
    # Estimate character width based on font (typical 8x8 font is ~4-6 pixels wide)
    avg_char_width = 6  # Default assumption
    
    # Try to detect character boundaries by looking for gaps in x coordinates
    x_coords_sorted = sorted(list(set(x_coords)))
    gaps = []
    for i in range(len(x_coords_sorted) - 1):
        if x_coords_sorted[i+1] - x_coords_sorted[i] > 1:  # Gap detected
            gaps.append((x_coords_sorted[i], x_coords_sorted[i+1]))
    
    # Use gaps to determine character boundaries
    char_boundaries = []
    if gaps:
        # Start with the first pixel
        start_x = min(x_coords)
        for gap_end, gap_start in gaps:
            char_boundaries.append((start_x, gap_end + 1))
            start_x = gap_start
        # Add the last character
        char_boundaries.append((start_x, max(x_coords) + 1))
    else:
        # If no gaps detected, estimate based on the width of all pixels
        total_width = max(x_coords) - min(x_coords) + 1
        num_chars = max(1, len(message))  # Avoid division by zero
        avg_char_width = total_width / num_chars
        
        # Create evenly spaced boundaries
        start_x = min(x_coords)
        for i in range(len(message)):
            end_x = start_x + avg_char_width
            char_boundaries.append((int(start_x), int(end_x)))
            start_x = end_x
    
    # Map pixels to each character based on boundaries
    char_pixels = []
    for start_x, end_x in char_boundaries:
        pixels = [(x, y) for (x, y) in all_pixels if start_x <= x < end_x]
        char_pixels.append((start_x, end_x, pixels))
    
    return char_pixels

def crossfade_effect(old_text, new_text, fade_steps=8, char_delay=2):
    """
    Create a character-by-character crossfade effect
    
    Parameters:
    - old_text: The text currently displayed
    - new_text: The text to transition to
    - fade_steps: Number of frames for each character's fade animation
    - char_delay: Delay between starting fade of consecutive characters (in frames)
    """
    # Get character pixel information for both texts
    old_chars = get_character_positions(old_text)
    new_chars = get_character_positions(new_text)
    
    # Handle case where either text is empty
    if not old_chars:
        show_message(device, new_text, fill="white", font=proportional(CP437_FONT), scroll_delay=0)
        return
    if not new_chars:
        with canvas(device) as draw:
            # Clear the display
            pass
        return
    
    # Get the maximum number of characters to process
    num_chars = max(len(old_chars), len(new_chars))
    
    # Get all old text pixels for initial display
    old_pixels = {}
    for _, _, pixels in old_chars:
        for pixel in pixels:
            old_pixels[pixel] = 1
    
    # Initialize crossfade progress for each character (0.0 = old text, 1.0 = new text)
    fade_progress = [0.0] * num_chars
    
    # Animation loop
    animation_finished = False
    frame = 0
    
    while not animation_finished:
        current_pixels = {}
        
        # Update fade progress for characters that have started fading
        for char_idx in range(num_chars):
            # Check if this character should start fading based on delay
            if frame >= char_idx * char_delay:
                # Update fade progress
                fade_progress[char_idx] = min(1.0, fade_progress[char_idx] + (1.0 / fade_steps))
        
        # Draw the current state based on fade progress
        for char_idx in range(num_chars):
            progress = fade_progress[char_idx]
            
            # Get old and new character pixels
            old_char_pixels = old_chars[char_idx][2] if char_idx < len(old_chars) else []
            new_char_pixels = new_chars[char_idx][2] if char_idx < len(new_chars) else []
            
            # Apply dithering to simulate fade
            # For each potential pixel position, decide whether to draw it based on fade progress
            char_start_x = min(old_chars[char_idx][0] if char_idx < len(old_chars) else float('inf'),
                              new_chars[char_idx][0] if char_idx < len(new_chars) else float('inf'))
            char_end_x = max(old_chars[char_idx][1] if char_idx < len(old_chars) else 0,
                            new_chars[char_idx][1] if char_idx < len(new_chars) else 0)
            char_width = char_end_x - char_start_x
            
            # Create a set of all potential pixel positions in this character area
            all_char_positions = set()
            for x in range(int(char_start_x), int(char_end_x)):
                for y in range(8):  # 8 pixels height for MAX7219
                    all_char_positions.add((x, y))
            
            # Convert pixel lists to sets for faster lookup
            old_set = set(old_char_pixels)
            new_set = set(new_char_pixels)
            
            # Determine which pixels to draw based on fade progress
            for pixel in all_char_positions:
                in_old = pixel in old_set
                in_new = pixel in new_set
                
                if in_old and in_new:
                    # Pixel is in both - always show
                    current_pixels[pixel] = 1
                elif in_old and not in_new:
                    # Pixel is fading out - decrease probability
                    if random.random() > progress:
                        current_pixels[pixel] = 1
                elif not in_old and in_new:
                    # Pixel is fading in - increase probability
                    if random.random() < progress:
                        current_pixels[pixel] = 1
                # If pixel is in neither, don't show it
        
        # Draw the current frame
        with canvas(device) as draw:
            for (x, y) in current_pixels:
                draw.point((x, y), fill="white")
        
        # Increment frame counter
        frame += 1
        
        # Check if animation is finished
        animation_finished = all(p >= 1.0 for p in fade_progress)
        
        # Control animation speed
        time.sleep(0.05)
    
    # Ensure final text is displayed cleanly
    show_message(device, new_text, fill="white", font=proportional(CP437_FONT), scroll_delay=0)

# Example usage
if __name__ == "__main__":
    # Display initial text
    show_message(device, "HELLO", fill="white", font=proportional(CP437_FONT), scroll_delay=0)
    time.sleep(1)
    
    # Transition with character crossfade effect
    crossfade_effect("HELLO", "WORLD")
    
    time.sleep(1)
    
    # Try with different lengths
    crossfade_effect("WORLD", "HI")
    
    time.sleep(1)
    
    crossfade_effect("HI", "WELCOME")
    
    # Display final text longer
    time.sleep(2)