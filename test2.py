import numpy as np
import matplotlib.pyplot as plt

# Constants
d = 225.64  # Distance from laser source to drawing surface in mm
max_angle = 12.5  # Maximum angle in degrees for galvos

# G-code points (in mm)
points = [
    (-50, -50),
    (-50, 50),
    (50, 50),
    (50, -50),
    (-50, -50)
]

# Function to calculate angles in degrees
def calculate_angles(x, y, d):
    theta_x = np.degrees(np.arctan2(x , d))
    theta_y = np.degrees(np.arctan2(y , d))
    print("theta : x ",theta_x, ", y ", theta_y)
    return theta_x, theta_y

# Function to convert angles to DAC values
def angles_to_dac(theta, max_angle, max_dac=4095):
    return np.clip((theta + max_angle) / (2 * max_angle) * max_dac, 0, max_dac)

# Calculate angles for each point
angles = [calculate_angles(x, y, d) for x, y in points]

# Convert angles to DAC values
dac_values = [(angles_to_dac(theta_x, max_angle), angles_to_dac(theta_y, max_angle)) for theta_x, theta_y in angles]
print(dac_values)
# Extract X and Y DAC values for plotting
x_dac = [x for x, y in dac_values]
y_dac = [y for x, y in dac_values]

# Plotting the path
plt.figure(figsize=(6, 6))
plt.plot(x_dac, y_dac, )
plt.scatter([x_dac[0]], [y_dac[0]], color='red', label='Origin')  # Marking the origin
#plt.plot(0, 0, marker='o',color='green')
plt.title('Laser Path for Drawing 100mm x 100mm Square')
plt.xlabel('X DAC Value')
plt.ylabel('Y DAC Value')
plt.legend()
plt.grid(True)
plt.show()
