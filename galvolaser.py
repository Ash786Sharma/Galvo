import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# Constants based on your specifications
phi_min_deg = -12.5  # Minimum angle in degrees
phi_max_deg = 12.5    # Maximum angle in degrees
voltage_min = -15.0   # Minimum voltage in volts
voltage_max = 15.0    # Maximum voltage in volts
dac_resolution = 4096  # DAC resolution (12-bit)
distance_mm = 225.64       # Distance in mm 

# Function to convert Cartesian coordinate to theta in radians
def cartesian_to_theta(x, y):
    theta_x = np.arctan2(x, distance_mm)  # X-axis
    theta_y = np.arctan2(y, distance_mm)  # Y-axis
    print("theta_deg : x", np.rad2deg(theta_x), " y",np.rad2deg(theta_y))
    return theta_x, theta_y

# Function to convert theta (radians) to DAC value
def theta_to_dac(theta_rad):
    # Convert theta to degrees
    theta_deg = np.rad2deg(theta_rad)
    #print("theta_deg :", theta_deg)
    # Map theta_deg to the range of your galvo (-12.5° to +12.5°)
    mapped_theta_deg = np.interp(theta_deg, [-180, 180], [phi_min_deg, phi_max_deg])
    print("map_theta_deg :",mapped_theta_deg)
    # Map mapped_theta_deg to DAC range (0 to 4096)
    dac_value = np.interp(theta_deg, [phi_min_deg, phi_max_deg], [0, dac_resolution])
    print("dac_value :",dac_value)
    # Round DAC value to nearest integer
    dac_value = int(round(dac_value))
    
    return dac_value

# Example G-code parsing function (replace with your actual parsing logic)
def parse_gcode_file(file_path):
    command_queue = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('G01') or line.startswith('G00'):
                parts = line.split()
                x = float(parts[1][1:])  # Example: parse X coordinate
                y = float(parts[2][1:])  # Example: parse Y coordinate
                command_queue.append((x, y))
    return command_queue

# Example usage:
# Path to your G-code file
#gcode_file_path = 'C:\\Users\\a6260\\Downloads\\galvo\\venv\\assets\\rectangle.gcode'
gcode_file_path = 'C:\\Users\\a6260\\Downloads\\galvo\\venv\\assets\\texttogcode_line.gcode'

# Parse G-code file to get command queue
command_queue = parse_gcode_file(gcode_file_path)

# Convert Cartesian coordinates to DAC values for each axis
dac_values_x = []
dac_values_y = []
actual_x = []
actual_y = []
for point in command_queue:
    x, y = point
    actual_x.append(x)
    actual_y.append(y)
    theta_x, theta_y = cartesian_to_theta(x, y)
    
    dac_value_x = theta_to_dac(theta_x)
    dac_value_y = theta_to_dac(theta_y)
    dac_values_x.append(dac_value_x)
    dac_values_y.append(dac_value_y)



# Plot G-code path
plt.figure(figsize=(10, 6))
plt.plot([point for point in dac_values_x], [point for point in dac_values_y], label='G-code Path', color='blue')
plt.plot(0, 0, label='Origin', color='red')
#plt.plot([point for point in actual_x], [point for point in actual_y], label='G-code Path', color='green')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('G-code Path and Galvo Outputs')
plt.grid(True)

# Plot DAC values for Galvo X (X-axis)
#plt.plot(dac_values_x, label='Galvo X (X-axis)', color='red', linestyle='--')

# Plot DAC values for Galvo Y (Y-axis)
#plt.plot(dac_values_y, label='Galvo Y (Y-axis)', color='green', linestyle='--')

plt.legend()
plt.tight_layout()
plt.show()


# Create 3D plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot G-code path in 3D
#z_values = [distance_mm] * len(command_queue)  # Constant distance for Z
z_values = 0
ax.plot([point for point in dac_values_x], [point for point in dac_values_y], z_values, label='G-code Path', color='blue')
#ax.plot([point for point in actual_x], [point for point in actual_y], z_values, label='G-code Path', color='green')
ax.plot(0, 0, z_values, label='Origin', color='red')
# Plot DAC values for Galvo X (X-axis) in 3D
#ax.scatter(dac_values_x, np.zeros_like(dac_values_x), np.zeros_like(dac_values_x), label='Galvo X (X-axis)', color='red')

# Plot DAC values for Galvo Y (Y-axis) in 3D
#ax.scatter(np.zeros_like(dac_values_y), dac_values_y, np.zeros_like(dac_values_y), label='Galvo Y (Y-axis)', color='green')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Visualization of G-code Path and Galvo Outputs')
ax.legend()

# Set the view angle for a top-down perspective
ax.view_init(elev=90, azim=-90)  # Top view

plt.show()


