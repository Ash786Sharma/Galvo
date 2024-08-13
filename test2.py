import numpy as np
import matplotlib.pyplot as plt
import cv2


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
    
    for y in range(height):
        row = binary_img[y]
        for x in range(width):
            if row[x] == 255:  # Laser on (adjust this based on your binary image)
                gcode.append(f"G1 X{x} Y{y} M3 S255")  # Move to position with laser on
            else:
                gcode.append(f"G1 X{x} Y{y} M5")  # Move to position with laser off
        gcode.append(f"G1 X{x} Y{y + 1} M5")  # Move to the next line
    return gcode, width, height



image_path = 'C:\\Users\\a6260\\Downloads\\galvo\\assets\\test.png'
gcode, img_width, img_height = convert_image_to_gcode_raster(image_path)
print(f"Generated {len(gcode)} G-code commands")


def visualize_gcode_raster(gcode, img_width, img_height, scale=1.0):
    fig, ax = plt.subplots()
    ax.set_xlim(0, img_width * scale)
    ax.set_ylim(0, img_height * scale)
    ax.set_aspect('equal')

    x, y = 0, 0
    laser_on = False
    x_coords = []
    y_coords = []

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
            x, y = new_x, new_y
        elif line.startswith("M3"):
            laser_on = True
        elif line.startswith("M5"):
            laser_on = False

    print(f"Collected {len(x_coords)} laser on points")
    
    #if x_coords and y_coords:
    #    ax.plot(x_coords, y_coords, 'r.', markersize=1)
    #else:
    #    print("No laser on points found")
    for x_coord, y_coord in zip(x_coords, y_coords):
        if x_coord and y_coord:
            ax.plot(x_coord, y_coord, 'r.', markersize=1)
        else:
            print("No laser on points found")
        
    ax.invert_yaxis()  # Invert y-axis to match image coordinates
    plt.title("Laser Engraving Visualization")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.show()

# Example usage
scale_factor = 0.1  # Adjust the scale factor as needed
visualize_gcode_raster(gcode, img_width, img_height, scale=scale_factor)
