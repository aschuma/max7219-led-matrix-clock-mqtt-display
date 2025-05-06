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

def curtain_effect(old_text, new_text, steps=15, pause_middle=0.5):
    """
    Create a curtain effect where text splits in the middle and opens to reveal new text
    
    Parameters:
    - old_text: The text currently displayed
    - new_text: The text to transition to
    - steps: Number of frames for the animation
    - pause_middle: Pause time when curtain is fully open
    """
    # Get pixel positions for both texts
    old_pixels = get_text_pixels(old_text)
    new_pixels = get_text_pixels(new_text)
    
    # Find center of the display
    center_x = device.width // 2
    
    # Split old pixels into left and right sides
    left_pixels = [(x, y) for x, y in old_pixels if x < center_x]
    right_pixels = [(x, y) for x, y in old_pixels if x >= center_x]
    
    # Create movement vectors for each pixel
    max_distance = max(device.width // 2, 1)  # Maximum distance pixels will move
    
    # Phase 1: Opening the curtain
    for step in range(steps + 1):
        # Calculate current offset for this step (accelerating outward)
        progress = step / steps
        offset = int(max_distance * (progress ** 2))  # Quadratic easing for acceleration
        
        with canvas(device) as draw:
            # Draw left side pixels (moving left)
            for x, y in left_pixels:
                new_x = max(0, x - offset)  # Move left
                draw.point((new_x, y), fill="white")
            
            # Draw right side pixels (moving right)
            for x, y in right_pixels:
                new_x = min(device.width - 1, x + offset)  # Move right
                draw.point((new_x, y), fill="white")
            
            # If this is the last step, also show the new text faintly
            # This creates a "reveal" effect as curtain opens
            if step == steps:
                # Draw the new text at lower intensity
                # Since MAX7219 is 1-bit, we'll use a dithering effect
                for i, (x, y) in enumerate(new_pixels):
                    if i % 2 == 0:  # Only draw every other pixel for dithering effect
                        draw.point((x, y), fill="white")
        
        time.sleep(0.05)  # Animation speed
    
    # Pause when curtain is fully open
    time.sleep(pause_middle)
    
    # Phase 2: Reveal the new text fully
    for step in range(5):  # 5 "fade in" steps for new text
        with canvas(device) as draw:
            # Draw partially revealed new text with increasing density
            for i, (x, y) in enumerate(new_pixels):
                if step == 0 and i % 2 == 0:
                    draw.point((x, y), fill="white")
                elif step == 1 and i % 3 == 0:
                    draw.point((x, y), fill="white")
                elif step == 2 and i % 2 != 0:
                    draw.point((x, y), fill="white")
                elif step >= 3:  # Full reveal in last steps
                    draw.point((x, y), fill="white")
        
        time.sleep(0.1)  # Animation speed
    
    # Phase 3: Hold the new text
    with canvas(device) as draw:
        for x, y in new_pixels:
            draw.point((x, y), fill="white")
    
    # Optional: Display the new text using standard method to ensure it's perfect
    show_message(device, new_text, fill="white", font=proportional(CP437_FONT), scroll_delay=0)

# Example usage
if __name__ == "__main__":
    # Display initial text
    show_message(device, "HELLO", fill="white", font=proportional(CP437_FONT), scroll_delay=0)
    time.sleep(1)
    
    # Transition with curtain effect
    curtain_effect("HELLO", "WORLD")
    
    # Display final text longer
    time.sleep(2)