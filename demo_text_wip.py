from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT
import time
import datetime

# Initialize the MAX7219 device
def initialize_device(cascaded=8, brightness=10):
        
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(
        serial,
        cascaded=8,
        block_orientation=-90,
        blocks_arranged_in_reverse_order=False,
    )
    device.contrast(0)
    
    return device

def get_string_pixels(device, string_to_display, font=TINY_FONT):
    """
    Returns a dict of pixel positions that would be lit for the given string
    Keys are x-positions, values are lists of y-positions
    """
    pixel_map = {}
    
    # Create a temporary PIL Image of the same size as the device
    from PIL import Image, ImageDraw
    img = Image.new('1', (device.width, device.height))
    draw = ImageDraw.Draw(img)
    
    # Draw the text
    text(draw, (0, 0), string_to_display, fill="white", font=font)
    
    # Get the pixel data
    width, height = img.size
    pixels = img.load()
    
    # Capture all lit pixels
    for x in range(width):
        for y in range(height):
            # In a 1-bit image, pixel values are 0 for black and 255 for white
            if pixels[x, y] > 0:  # If pixel is lit
                if x not in pixel_map:
                    pixel_map[x] = []
                pixel_map[x].append(y)
    
    return pixel_map

# Function to display a string using its pixel map
def display_string_from_pixels(device, pixel_map, x_offset=0):
    with canvas(device) as draw:
        # Draw pixels according to pixel_map
        for x in pixel_map:
            for y in pixel_map[x]:
                draw.point((x + x_offset, y), fill="white")

# Function for the stripe transition effect between two strings
def stripe_transition(device, old_pixels, new_pixels, stripe_width=4, delay=0.01, x_offset=0):
    """
    Transition from old_pixels to new_pixels with a stripe effect
    
    Parameters:
    - device: The LED matrix device
    - old_pixels: Dict of pixel positions for the old string
    - new_pixels: Dict of pixel positions for the new string
    - stripe_width: Width of the transition stripe in pixels
    - delay: Delay between frames for smooth animation
    - x_offset: Horizontal offset for displaying the strings
    """
    # Get device dimensions
    max_x = device.width
    
    # Find the leftmost and rightmost pixels across both strings
    all_x_positions = set(old_pixels.keys()).union(set(new_pixels.keys()))
    if not all_x_positions:
        return  # No pixels to transition
        
    min_x = min(all_x_positions)
    max_x = max(all_x_positions) + 1
    
    # Add margins to ensure stripe fully enters and exits
    start_x = min_x - stripe_width
    end_x = max_x + stripe_width
    
    # Move stripe from left to right
    for stripe_left in range(start_x, end_x):
        # Calculate the right edge of the stripe
        stripe_right = stripe_left + stripe_width
        
        with canvas(device) as draw:
            # For each column in our display area
            for x in range(min_x - 1, max_x + 1):
                # Apply the offset for displaying on the device
                display_x = x + x_offset
                
                # If stripe has passed this column, use new string
                if stripe_right <= x:
                    if x in new_pixels:
                        for y in new_pixels[x]:
                            draw.point((display_x, y), fill="white")
                            
                # If stripe hasn't reached this column yet, use old string
                elif stripe_left > x:
                    if x in old_pixels:
                        for y in old_pixels[x]:
                            draw.point((display_x, y), fill="white")
                            
                # If column is under the stripe, invert the old string
                else:
                    # Get all possible y positions (0-7)
                    all_y_positions = set(range(8))
                    
                    # Get the old lit positions for this column
                    old_lit = set(old_pixels.get(x, []))
                    
                    # Invert: light up positions that weren't lit in old string
                    for y in all_y_positions - old_lit:
                        draw.point((display_x, y), fill="white")
        
        # Delay for smooth animation
        time.sleep(delay)

# Function to demonstrate string transition
def demo_string_transition(device, string1, string2, font=TINY_FONT):
    """
    Demonstrate transition between two strings
    
    Parameters:
    - device: The LED matrix device
    - string1: First string to display
    - string2: Second string to display
    - font: Font to use for display
    """
    # Calculate the center position for better display
    x_offset = (device.width - len(string1) * 6) // 2  # Rough estimation of string width
    
    # Get pixel maps for both strings
    string1_pixels = get_string_pixels(device, string1, font)
    string2_pixels = get_string_pixels(device, string2, font)
    
    # Display the first string
    display_string_from_pixels(device, string1_pixels, x_offset)
    time.sleep(2)  # Show the first string for 2 seconds
    
    # Perform the transition
    stripe_transition(device, string1_pixels, string2_pixels, stripe_width=4, delay=0.02, x_offset=x_offset)
    
    # Keep the second string displayed
    time.sleep(2)

# Function to display time with transition when minute changes
def run_time_display(device, font=TINY_FONT, duration_minutes=60):
    """
    Display time with transitions when minute changes
    
    Parameters:
    - device: The LED matrix device
    - font: Font to use for display
    - duration_minutes: How long to run the display in minutes
    """
    # Calculate end time
    end_time = datetime.datetime.now() + datetime.timedelta(minutes=duration_minutes)
    
    # Start with current time
    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%H:%M")
    current_time_pixels = get_string_pixels(device, current_time_str, font)
    
    # Center position for the time
    x_offset = (device.width - len(current_time_str) * 6) // 2
    
    # Initial display
    display_string_from_pixels(device, current_time_pixels, x_offset)
    
    # Track last minute for change detection
    last_minute = current_time.minute
    
    # Main loop
    while datetime.datetime.now() < end_time:
        # Check current time
        now = datetime.datetime.now()
        
        # If minute changed
        if now.minute != last_minute:
            # Update last minute
            last_minute = now.minute
            
            # Format new time
            new_time_str = now.strftime("%H:%M")
            new_time_pixels = get_string_pixels(device, new_time_str, font)
            
            # Perform transition
            stripe_transition(device, current_time_pixels, new_time_pixels, 
                              stripe_width=4, delay=0.02, x_offset=x_offset)
            
            # Update current time data
            current_time_str = new_time_str
            current_time_pixels = new_time_pixels
        
        # Small delay to reduce CPU usage
        time.sleep(0.1)

# Main function with examples
def main():
    device = initialize_device(cascaded=8, brightness=10)
    
    try:
        print("Starting string transition demo")
        
        # Example 1: Simple string transition
        demo_string_transition(device, "HELLO", "WORLD")
        
        # Example 2: Different length strings
        demo_string_transition(device, "SHORT", "LONG TEXT")
        
        # Example 3: Numbers
        demo_string_transition(device, "12345", "67890")
        
        # Example 4: Run the time display with transitions
        print("Running time display with transitions")
        run_time_display(device, duration_minutes=10)
        
    except KeyboardInterrupt:
        pass
    finally:
        # Clear the display
        device.clear()

# Function to transition between any two strings
def string_transition(device, string1, string2, font=TINY_FONT, stripe_width=4, delay=0.02):
    """
    Public function to transition between any two strings
    
    Parameters:
    - device: The LED matrix device
    - string1: First string to display
    - string2: Second string to display
    - font: Font to use for display
    - stripe_width: Width of the transition stripe in pixels
    - delay: Delay between frames for smooth animation
    """
    # Calculate the center position for better display
    x_offset = (device.width - len(string1) * 6) // 2  # Rough estimation
    
    # Get pixel maps for both strings
    string1_pixels = get_string_pixels(device, string1, font)
    string2_pixels = get_string_pixels(device, string2, font)
    
    # Display the first string
    display_string_from_pixels(device, string1_pixels, x_offset)
    
    # Perform the transition
    stripe_transition(device, string1_pixels, string2_pixels, 
                     stripe_width=stripe_width, delay=delay, x_offset=x_offset)
    
    return string2_pixels  # Return the pixels of the second string for further use

if __name__ == "__main__":
    main()