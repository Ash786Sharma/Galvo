import numpy as np
import matplotlib.pyplot as plt
import cv2
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

def convert_image_to_gcode_raster(image_path, threshold=128):
    # Load image and convert to grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Apply thresholding to get binary image
    _, binary_img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    
    # Invert the binary image (optional, depends on whether 0 or 255 should be laser on)
    binary_img = cv2.bitwise_not(binary_img)
    
    # Generate G-code for raster scanning
    gcode = []
    height, width = binary_img.shape
    
    #for y in range(height):
    #    row = binary_img[y]
    #    for x in range(width):
    #        if row[x] == 255:  # Laser on (adjust this based on your binary image)
    #            gcode.append(f"G1 X{x} Y{y} M3 S255")  # Move to position with laser on
    #        else:
    #            gcode.append(f"G1 X{x} Y{y} M5")  # Move to position with laser off
    #    gcode.append(f"G1 X{x} Y{y + 1} M5")  # Move to the next line
    #return gcode, width, height
    
    for y in range(height):
        row = binary_img[y]

        # Alternate the direction of the X-axis depending on the Y-axis line number
        if y % 2 == 0:
            # Left to right
            x_range = range(width)
        else:
            # Right to left
            x_range = range(width - 1, -1, -1)

        for x in x_range:
            if row[x] == 255:  # Laser on (adjust this based on your binary image)
                gcode.append(f"G1 X{x} Y{y} M3 S255")  # Move to position with laser on
            else:
                gcode.append(f"G1 X{x} Y{y} M5")  # Move to position with laser off

        # No need to add a movement to the next line since the serpentine pattern naturally moves in the correct direction

    return gcode, width, height

image_path = 'C:\\Users\\a6260\\Downloads\\galvo\\assets\\test.png'
gcode, img_width, img_height = convert_image_to_gcode_raster(image_path)
print(f"Generated {len(gcode)} G-code commands")

def animate_gcode_raster_3d(gcode, img_width, img_height, scale=1.0, interval=50):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(0, img_width * scale)
    ax.set_ylim(0, img_height * scale)
    ax.set_zlim(0, 255)  # Assuming laser intensity goes from 0 to 255

    x, y = 0, 0
    laser_on = False
    x_coords = []
    y_coords = []
    z_coords = []

    for line in gcode:
        parts = line.split()
        
        if line.startswith("G1"):
            new_x = x
            new_y = y
            
            for part in parts:
                if part.startswith('X'):
                    try:
                        new_x = int(part[1:]) * scale
                    except ValueError:
                        print(f"Skipping line with invalid X coordinate: {line}")
                        continue
                elif part.startswith('Y'):
                    try:
                        new_y = int(part[1:]) * scale
                    except ValueError:
                        print(f"Skipping line with invalid Y coordinate: {line}")
                        continue
                elif part == "M3":
                    laser_on = True
                    
                elif part == "M5":
                    laser_on = False
                    

            if laser_on:
                x_coords.append(new_x)
                y_coords.append(new_y)
                z_coords.append(0)
            x, y = new_x, new_y
        elif line.startswith("M3"):
            laser_on = True
        elif line.startswith("M5"):
            laser_on = False

    print(f"Collected {len(x_coords)} laser on points")

    line, = ax.plot([], [], [], 'r.', markersize=0.5)
    point, = ax.plot([], [], [], 'bo', markersize=5)

    def init():
        line.set_data([], [])
        line.set_3d_properties([])
        point.set_data([], [])
        point.set_3d_properties([])
        return line, point

    def update(frame):
        line.set_data(x_coords[:frame], y_coords[:frame])
        line.set_3d_properties(z_coords[:frame])
        if frame < len(x_coords):
            point.set_data([x_coords[frame]], [y_coords[frame]])  # Wrap in a list to make them sequences
            point.set_3d_properties([z_coords[frame]])  # Wrap in a list to make them sequences
        return line, point

    ani = animation.FuncAnimation(fig, update, frames=len(x_coords), init_func=init, blit=True, interval=interval)
    
    ax.invert_yaxis()
    plt.title("Laser Engraving Visualization in 3D")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_zlabel("Laser Intensity")
    plt.show()

# Example usage
scale_factor = 0.1  # Adjust the scale factor as needed
animate_gcode_raster_3d(gcode, img_width, img_height, scale=scale_factor)
