import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Function to parse G-code file and extract coordinates
def parse_gcode(file_path):
    x_coords = []
    y_coords = []
    
    current_x = None
    current_y = None 
    
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(('G0', 'G1')):
                parts = line.split()
                for part in parts:
                    if part.startswith('X'):
                        current_x = float(part[1:])
                    elif part.startswith('Y'):
                        current_y = float(part[1:])
                
                if current_x is not None and current_y is not None:
                    x_coords.append(current_x)
                    y_coords.append(current_y)
    
    return x_coords, y_coords

# Path to your G-code file
gcode_file_path = 'C:\\Users\\a6260\\Downloads\\galvo\\venv\\assets\\texttogcode_line.gcode'

# Parse the G-code file
x_coords, y_coords = parse_gcode(gcode_file_path)

# Set Z-coordinate to 0.0 for all points
z_coords = [0.0] * len(x_coords)

# Plot the tool path in 3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

ax.plot(x_coords, y_coords, z_coords, label='Tool Path', marker='o')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Tool Path (Z = 0.0 mm)')
ax.legend()

plt.tight_layout()
plt.show()
