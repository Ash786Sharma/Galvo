import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# File paths
image_path = 'C:\\Users\\a6260\\Downloads\\galvo\\assets\\test.png'
output_gcode_path = 'C:\\Users\\a6260\\Downloads\\galvo\\assets\\test.gcode'

def image_to_gcode(image_path, output_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    ret, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    # Find contours which represent the paths to be engraved
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    with open(output_path, 'w') as f:
        for contour in contours:
            for point in contour:
                x, y = point[0]
                # Convert image coordinates to engraving area coordinates
                x = (x / image.shape[1]) * 20  # scale to 20mm
                y = (y / image.shape[0]) * 20  # scale to 20mm
                f.write(f"G01 X{x:.2f} Y{y:.2f}\n")

def image_to_raster_gcode(image_path, output_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    ret, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)  # Inverted threshold

    height, width = image.shape
    raster_img = np.zeros_like(image)

    with open(output_path, 'w') as f:
        for y in range(height):
            laser_on = False
            for x in range(width):
                if thresh[y, x] == 0:  # Black pixel (inverted)
                    if not laser_on:
                        laser_on = True
                        # Convert image coordinates to engraving area coordinates
                        x_mm = (x / width) * 20  # scale to 100mm
                        y_mm = (y / height) * 20  # scale to 100mm
                        f.write(f"G01 X{x_mm:.2f} Y{y_mm:.2f} S1\n")  # S1 to turn on the laser
                    raster_img[y, x] = 255  # White pixel in raster image
                else:
                    if laser_on:
                        laser_on = False
                        x_mm = (x / width) * 20  # scale to 100mm
                        y_mm = (y / height) * 20  # scale to 100mm
                        f.write(f"G01 X{x_mm:.2f} Y{y_mm:.2f} S0\n")  # S0 to turn off the laser

            if laser_on:  # Ensure the laser is turned off at the end of the row
                x_mm = (width / width) * 20  # scale to 100mm
                y_mm = (y / height) * 20  # scale to 100mm
                f.write(f"G01 X{x_mm:.2f} Y{y_mm:.2f} S0\n")  # S0 to turn off the laser at the end of the row

    return image, thresh, raster_img

def gcode_to_image(gcode_path, width, height):
    gcode_image = np.zeros((height, width), dtype=np.uint8)
    gcode_path_points = []
    laser_on = False
    current_x = 0
    current_y = 0
    with open(gcode_path, 'r') as f:
        for line in f:
            if line.startswith('G01'):
                parts = line.split()
                x_mm = float(parts[1][1:])
                y_mm = float(parts[2][1:])
                x = int((x_mm / 20) * width)
                y = int((y_mm / 20) * height)
                if 'S1' in line:
                    laser_on = True
                elif 'S0' in line:
                    laser_on = False
                if laser_on:
                    cv2.line(gcode_image, (current_x, current_y), (x, y), 255, 1)
                current_x = x
                current_y = y
                gcode_path_points.append((x_mm, y_mm, 0 if laser_on else 1))
    return gcode_image, gcode_path_points

# Generate G-code from image
original_image, threshold_image, raster_image = image_to_raster_gcode(image_path, output_gcode_path)
gcode_image, gcode_path_points = gcode_to_image(output_gcode_path, original_image.shape[1], original_image.shape[0])


# Plot images side by side
fig, axes = plt.subplots(2, 2, figsize=(6, 5))
axes[0][0].imshow(original_image, cmap='gray')
axes[0][0].set_title('Original Image')
axes[0][0].axis('off')

axes[0][1].imshow(threshold_image, cmap='gray')
axes[0][1].set_title('Threshold Image')
axes[0][1].axis('off')

axes[1][0].imshow(raster_image, cmap='gray')
axes[1][0].set_title('Raster Image')
axes[1][0].axis('off')

axes[1][1].imshow(gcode_image, cmap='gray')
axes[1][1].set_title('G-code Image')
axes[1][1].axis('off')

plt.tight_layout()

# Create a 3D plot for the G-code path
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# Convert the G-code path points to arrays for plotting
x_points = [point[0] for point in gcode_path_points]
y_points = [point[1] for point in gcode_path_points]
z_points = [0] * len(gcode_path_points)  # z=0 for 2D path

# Plot the G-code path points
for i in range(len(gcode_path_points) - 1):
    x = [gcode_path_points[i][0], gcode_path_points[i+1][0]]
    y = [gcode_path_points[i][1], gcode_path_points[i+1][1]]
    z = [gcode_path_points[i][2], gcode_path_points[i+1][2]]
    color = 'blue' if gcode_path_points[i][2] == 0 else 'red'
    ax.plot(x, y, z, color=color)

ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Laser On/Off')
ax.set_title('3D Visualization of G-code Path')

# Set the view angle for a top-down perspective
ax.view_init(elev=90, azim=-90)  # Top view

plt.show()