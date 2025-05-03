from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT
import time
import random
import math

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

# Basic scrolling text
def scroll_text(device, message, delay=0.05):
    show_message(device, message, fill="white", 
                 font=proportional(CP437_FONT), scroll_delay=delay)

# Bouncing ball effect
def bouncing_ball(device, cycles=5, delay=0.05):
    for _ in range(cycles):
        # Define our "ball"
        x = 0
        y = 0
        x_speed = 1
        y_speed = 1
        
        # Bounce for a while
        for _ in range(150):
            with canvas(device) as draw:
                # Draw the ball
                draw.point((x, y), fill="white")
                
            # Move the ball
            x += x_speed
            y += y_speed
            
            # Bounce off the edges
            if x == 0 or x == 63:  # For 8 matrices: 8*8 - 1 = 63
                x_speed = -x_speed
            if y == 0 or y == 7:   # Matrix height is 8 pixels
                y_speed = -y_speed
                
            time.sleep(delay)

# Rain effect
def rain(device, drops=20, cycles=100, delay=0.05):
    # Initialize raindrops
    raindrops = []
    for _ in range(drops):
        x = random.randint(0, 63)  # For 8 matrices: 8*8 - 1 = 63
        y = random.randint(0, 7)   # Matrix height is 8 pixels
        speed = random.uniform(0.2, 1.0)  # Different speed for each drop
        raindrops.append([x, y, speed])

    for _ in range(cycles):
        with canvas(device) as draw:
            for i, drop in enumerate(raindrops):
                # Draw the raindrop
                draw.point((int(drop[0]), int(drop[1])), fill="white")
                
                # Move the raindrop
                drop[1] += drop[2]
                
                # If raindrop moves out of screen, reset it
                if drop[1] > 7:
                    raindrops[i][0] = random.randint(0, 63)
                    raindrops[i][1] = 0
                    
        time.sleep(delay)

# Wave effect
def wave(device, cycles=100, delay=0.05):
    offset = 0
    for _ in range(cycles):
        with canvas(device) as draw:
            for x in range(64):  # For 8 matrices: 8*8 = 64
                # Calculate y position using a sine wave
                y = int(3.5 + 3.5 * math.sin((x + offset) * 0.1))
                draw.point((x, y), fill="white")
        offset += 1
        time.sleep(delay)

# Snake game effect
def snake_effect(device, cycles=200, delay=0.1):
    # Initialize the snake
    snake = [(32, 4)]  # Start in the middle
    direction = (1, 0)  # Initially moving right
    
    # Directions: right, up, left, down
    directions = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    current_dir = 0
    
    # Food position
    food = (random.randint(0, 63), random.randint(0, 7))
    
    for _ in range(cycles):
        # Change direction randomly sometimes
        if random.random() < 0.1:
            current_dir = (current_dir + random.choice([-1, 1])) % 4
            direction = directions[current_dir]
        
        # Calculate new head position
        head_x, head_y = snake[0]
        new_head = ((head_x + direction[0]) % 64, (head_y + direction[1]) % 8)
        
        # If snake hits food, grow it
        if new_head == food:
            snake.insert(0, new_head)
            food = (random.randint(0, 63), random.randint(0, 7))
        else:
            # Move snake
            snake.insert(0, new_head)
            snake.pop()
        
        # Draw everything
        with canvas(device) as draw:
            # Draw snake
            for segment in snake:
                draw.point(segment, fill="white")
            
            # Draw food
            draw.point(food, fill="white")
        
        time.sleep(delay)

# Starfield effect
def starfield(device, cycles=200, delay=0.05):
    # Initialize stars with random positions and speeds
    stars = []
    for _ in range(30):
        x = random.randint(0, 63)
        y = random.randint(0, 7)
        speed = random.uniform(0.1, 0.8)
        stars.append([x, y, speed])
    
    for _ in range(cycles):
        with canvas(device) as draw:
            for i, star in enumerate(stars):
                # Draw the star
                draw.point((int(star[0]), int(star[1])), fill="white")
                
                # Move the star
                star[0] -= star[2]  # Move toward left
                
                # If star moves out of screen, reset it
                if star[0] < 0:
                    stars[i][0] = 63
                    stars[i][1] = random.randint(0, 7)
                    
        time.sleep(delay)

# Pulsing heart
def pulsing_heart(device, cycles=30, delay=0.1):
    # Heart coordinates
    heart = [
        (30, 1), (32, 1), (29, 2), (33, 2), (28, 3), (34, 3),
        (28, 4), (34, 4), (29, 5), (33, 5), (30, 6), (32, 6), (31, 7)
    ]
    
    for _ in range(cycles):
        for size in range(5):  # Pulse in
            with canvas(device) as draw:
                for x, y in heart:
                    for dx in range(-size, size+1):
                        for dy in range(-size, size+1):
                            if 0 <= x+dx < 64 and 0 <= y+dy < 8:
                                draw.point((x+dx, y+dy), fill="white")
            time.sleep(delay)
            
        for size in range(5, -1, -1):  # Pulse out
            with canvas(device) as draw:
                for x, y in heart:
                    for dx in range(-size, size+1):
                        for dy in range(-size, size+1):
                            if 0 <= x+dx < 64 and 0 <= y+dy < 8:
                                draw.point((x+dx, y+dy), fill="white")
            time.sleep(delay)

# Spectrum analyzer effect
def spectrum_analyzer(device, cycles=100, delay=0.05):
    for _ in range(cycles):
        with canvas(device) as draw:
            for x in range(8):  # 8 frequency bands (one per matrix)
                # Generate random height for this band
                height = random.randint(1, 8)
                for y in range(8 - height, 8):
                    # Draw line from bottom to height
                    draw.point((x * 8 + 4, y), fill="white")
        time.sleep(delay)

# Fire effect
def fire_effect(device, cycles=200, delay=0.05):
    # Create a buffer for the fire simulation
    buffer = [[0 for _ in range(8)] for _ in range(64)]
    
    for _ in range(cycles):
        # Randomly seed the bottom row with "heat"
        for x in range(64):
            buffer[x][7] = random.randint(0, 1)
        
        # Calculate the fire propagation
        for y in range(6, -1, -1):
            for x in range(64):
                if x > 0 and x < 63:
                    buffer[x][y] = (buffer[x-1][y+1] + buffer[x][y+1] + buffer[x+1][y+1]) / 3
                else:
                    buffer[x][y] = buffer[x][y+1] / 2
        
        # Render the fire
        with canvas(device) as draw:
            for y in range(8):
                for x in range(64):
                    if buffer[x][y] > 0.3:  # Threshold for visibility
                        draw.point((x, y), fill="white")
        
        time.sleep(delay)

# Running lights effect
def running_lights(device, cycles=5, delay=0.05):
    for _ in range(cycles):
        # Run lights from left to right
        for x in range(64):
            with canvas(device) as draw:
                draw.line((x, 0, x, 7), fill="white")
            time.sleep(delay)
        
        # Run lights from right to left
        for x in range(63, -1, -1):
            with canvas(device) as draw:
                draw.line((x, 0, x, 7), fill="white")
            time.sleep(delay)

# Random pixels effect
def random_pixels(device, cycles=200, delay=0.05):
    for _ in range(cycles):
        with canvas(device) as draw:
            for _ in range(20):  # Draw 20 random pixels
                x = random.randint(0, 63)
                y = random.randint(0, 7)
                draw.point((x, y), fill="white")
        time.sleep(delay)

# Game of Life
def game_of_life(device, cycles=200, delay=0.1):
    # Initialize random state
    grid = [[random.choice([0, 1]) for _ in range(8)] for _ in range(64)]
    
    for _ in range(cycles):
        # Draw current state
        with canvas(device) as draw:
            for x in range(64):
                for y in range(8):
                    if grid[x][y] == 1:
                        draw.point((x, y), fill="white")
        
        # Calculate next generation
        new_grid = [[0 for _ in range(8)] for _ in range(64)]
        for x in range(64):
            for y in range(8):
                # Count neighbors (including wrap-around)
                neighbors = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx = (x + dx) % 64
                        ny = (y + dy) % 8
                        neighbors += grid[nx][ny]
                
                # Apply Conway's rules
                if grid[x][y] == 1:
                    new_grid[x][y] = 1 if neighbors in [2, 3] else 0
                else:
                    new_grid[x][y] = 1 if neighbors == 3 else 0
        
        grid = new_grid
        time.sleep(delay)

# Main function to run effects
def main():
    device = initialize_device(cascaded=8, brightness=5)
    
    try:
        print("Starting LED effects demo")
        
        # Start with a greeting
        scroll_text(device, "LED Demo", delay=0.03)
        
        # Run various effects
        starfield(device, cycles=100)
        bouncing_ball(device, cycles=2)
        rain(device, cycles=100)
        wave(device, cycles=100)
        #snake_effect(device, cycles=150)
        #pulsing_heart(device, cycles=5)
        #spectrum_analyzer(device, cycles=100)
        #running_lights(device, cycles=3)
        #fire_effect(device, cycles=100)
        random_pixels(device, cycles=100)
        game_of_life(device, cycles=100)
        
        # End with a goodbye
        scroll_text(device, "Thank you! Goodbye!", delay=0.03)
        
    except KeyboardInterrupt:
        pass
    finally:
        # Clear the display
        device.clear()
        device.contrast(0)

if __name__ == "__main__":
    main()
    
