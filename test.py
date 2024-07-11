import numpy as np
import matplotlib.pyplot as plt

# Constants
h = 225.64  # Height in mm
angle_limit = 12.5  # Degree limit for laser

# Function to convert Cartesian coordinates to angles
def cartesian_to_angles(x, y, h):
    theta_x = np.degrees(np.arctan(x / h))
    theta_y = np.degrees(np.arctan(y / h))
    return theta_x, theta_y

# Define the work area range (from -50 to +50 mm)
x_range = np.linspace(-50, 50, 100)
y_range = np.linspace(-50, 50, 100)

# Create a grid of coordinates
X, Y = np.meshgrid(x_range, y_range)

# Flatten the grid for easier processing
x_flat = X.flatten()
y_flat = Y.flatten()

# Convert each coordinate to angles
angles_x = []
angles_y = []
for x, y in zip(x_flat, y_flat):
    theta_x, theta_y = cartesian_to_angles(x, y, h)
    angles_x.append(theta_x)
    angles_y.append(theta_y)

# Plot the results to verify the path is centered at the origin
plt.figure(figsize=(8, 8))
plt.scatter(angles_x, angles_y, s=1)
plt.title('Laser Angles for 100 mm x 100 mm Work Area')
plt.xlabel('Theta X (degrees)')
plt.ylabel('Theta Y (degrees)')
plt.axhline(0, color='r', linestyle='--')
plt.axvline(0, color='r', linestyle='--')
plt.grid(True)
plt.show()
