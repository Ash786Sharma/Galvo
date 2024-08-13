import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from scipy.interpolate import interp1d
import cv2  # OpenCV library for image processing

# Function to load image and apply thresholding
def process_image(image_path, threshold=127):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresholded = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return image, thresholded

# Function to find and fill contours
def get_filled_contours(thresholded_image):
    contours, _ = cv2.findContours(thresholded_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(thresholded_image)
    cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)
    points = np.column_stack(np.where(mask == 255))
    return points, contours

# Interactive thresholding function with contour preview
def interactive_thresholding(image_path):
    def on_trackbar(val):
        threshold = cv2.getTrackbarPos('Threshold', 'Thresholded Image')
        _, thresholded = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
        
        # Get filled contours
        filled_contour_points, contours = get_filled_contours(thresholded)
        
        # Draw contours on original image
        contour_image = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR)
        cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 1)
        
        # Display thresholded image with contours
        cv2.imshow('Thresholded Image', contour_image)

    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Create a window to display the thresholded image
    cv2.namedWindow('Thresholded Image', cv2.WINDOW_NORMAL)

    # Create a trackbar for adjusting the threshold value
    cv2.createTrackbar('Threshold', 'Thresholded Image', 127, 255, on_trackbar)

    # Display the initial thresholded image
    _, initial_thresholded = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    cv2.imshow('Thresholded Image', cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2BGR))

    # Wait until user presses the escape key
    cv2.waitKey(0)
    final_threshold = cv2.getTrackbarPos('Threshold', 'Thresholded Image')
    cv2.destroyAllWindows()

    # Return the final thresholded image and contours
    _, final_thresholded = cv2.threshold(image, final_threshold, 255, cv2.THRESH_BINARY)
    filled_contour_points, contours = get_filled_contours(final_thresholded)
    return image, final_thresholded, filled_contour_points, contours

# Example usage:
image_path = 'C:\\Users\\a6260\\Downloads\\galvo\\assets\\test.png'

# Process the image with interactive thresholding and contour preview
original_image, thresholded_image, filled_contour_points, contours = interactive_thresholding(image_path)

# Print the filled contour points for debugging
print("Filled Contour Points:", filled_contour_points)

# Display the original and thresholded images using matplotlib
fig, axs = plt.subplots(1, 2, figsize=(8, 6))
axs[0].imshow(original_image, cmap='gray')
axs[0].set_title('Original Image')
axs[0].axis('off')

# Draw contours on the original image for visualization
contour_image = cv2.cvtColor(original_image.copy(), cv2.COLOR_GRAY2BGR)
cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 1)
axs[1].imshow(contour_image)
axs[1].set_title('Thresholded Image with Contours')
axs[1].axis('off')

plt.show()

# Proceed with the filled contour points to path conversion and plotting
# Constants based on your specifications
phi_min_deg = -12.5  # Minimum angle in degrees
phi_max_deg = 12.5   # Maximum angle in degrees
voltage_min = -15.0  # Minimum voltage in volts
voltage_max = 15.0   # Maximum voltage in volts
dac_resolution = 4096  # DAC resolution (12-bit)
distance_mm = 225.64  # Distance in mm
galvo_kpps = 20000    # Galvo points per second

# Function to convert Cartesian coordinate to theta in radians
def cartesian_to_theta(x, y):
    theta_x = np.arctan2(x, distance_mm)  # X-axis
    theta_y = np.arctan2(y, distance_mm)  # Y-axis
    return theta_x, theta_y

# Function to convert theta (radians) to DAC value
def theta_to_dac(theta_rad):
    # Convert theta to degrees
    theta_deg = np.rad2deg(theta_rad)
    
    # Map theta_deg to the range of your galvo (-12.5° to +12.5°)
    mapped_theta_deg = np.interp(theta_deg, [-180, 180], [phi_min_deg, phi_max_deg])
    
    # Map mapped_theta_deg to DAC range (0 to 4096)
    dac_value = np.interp(mapped_theta_deg, [phi_min_deg, phi_max_deg], [0, dac_resolution])
    
    # Round DAC value to nearest integer
    dac_value = int(round(dac_value))
    
    return dac_value

# Convert filled contour points to DAC values for each axis
dac_values_x = []
dac_values_y = []
for point in filled_contour_points:
    x, y = point
    theta_x, theta_y = cartesian_to_theta(x, y)
    
    # Print theta values for debugging
    print(f"Point: ({x}, {y}) -> Theta: ({theta_x}, {theta_y})")
    
    dac_value_x = theta_to_dac(theta_x)
    dac_value_y = theta_to_dac(theta_y)
    
    # Print DAC values for debugging
    print(f"Theta: ({theta_x}, {theta_y}) -> DAC: ({dac_value_x}, {dac_value_y})")
    
    dac_values_x.append(dac_value_x)
    dac_values_y.append(dac_value_y)

# Ensure DAC values are not empty
if not dac_values_x or not dac_values_y:
    raise ValueError("DAC values are empty. Check the image processing and conversion functions.")

# Interpolation function
def interpolate_points(x, y, num_points):
    t = np.linspace(0, 1, len(x))
    t_new = np.linspace(0, 1, num_points)
    interp_x = interp1d(t, x, kind='linear')
    interp_y = interp1d(t, y, kind='linear')
    x_new = interp_x(t_new)
    y_new = interp_y(t_new)
    return x_new, y_new

# Interpolate the DAC values to get a smoother curve
num_interpolated_points = 5 * len(dac_values_x)  # Adjust the factor as needed (reduced from 10 to 5)
smooth_dac_values_x, smooth_dac_values_y = interpolate_points(dac_values_x, dac_values_y, num_interpolated_points)

# Create 3D plot
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# Plot initial points
path_line, = ax.plot([], [], [], label='Image Path', color='blue')
laser_point, = ax.plot([], [], [], 'ro')  # Red point representing the laser
origin_point, = ax.plot(min(dac_values_x), min(dac_values_y), [0], 'ro')  # Red point representing the laser
source_point, = ax.plot(min(dac_values_x), min(dac_values_y), [distance_mm], 'go')  # Green point representing the laser source
connection_line, = ax.plot([], [], [], 'r-')  # Red line connecting laser source to moving point

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Visualization of Image Path and Galvo Outputs')
ax.legend()

# Set the view angle for a top-down perspective
ax.view_init(elev=90, azim=-90)  # Top view

# Set up the limits of the plot
ax.set_xlim(min(dac_values_x)-50, max(dac_values_x)+50)
ax.set_ylim(min(dac_values_y)-50, max(dac_values_y)+50)
ax.set_zlim(0, distance_mm + 50)

# Animation function
def animate(i):
    # Update path line
    path_line.set_data(smooth_dac_values_x[:i+1], smooth_dac_values_y[:i+1])
    path_line.set_3d_properties([0] * (i+1)) 
    
    # Update laser point
    if i < len(smooth_dac_values_x):
        laser_point.set_data([smooth_dac_values_x[i]], [smooth_dac_values_y[i]])
        laser_point.set_3d_properties([0])
    
    # Update connection line
    if i < len(smooth_dac_values_x):
        connection_line.set_data([min(dac_values_x), smooth_dac_values_x[i]], [min(dac_values_y), smooth_dac_values_y[i]])
        connection_line.set_3d_properties([distance_mm, 0])
    
    return path_line, laser_point, connection_line

# Calculate number of frames and interval
total_points = len(smooth_dac_values_x)
duration_seconds = total_points / galvo_kpps
frames_per_second = 120  # Increase FPS for faster animation
num_frames = num_interpolated_points
if num_frames == 0:
    num_frames = frames_per_second

interval = duration_seconds / frames_per_second  # Reduced interval for faster animation
print("total_points:", total_points, "duration_seconds:", duration_seconds, "frames_per_second:", frames_per_second, "num_frame:", num_frames, "interval:", interval)

# Create animation
ani = FuncAnimation(fig, animate, frames=num_frames, interval=interval, blit=True)

plt.show()
