import numpy as np
import trimesh
import matplotlib.pyplot as plt

def load_stl(file_path):
    return trimesh.load(file_path)

def generate_slices(mesh, num_slices=100):
    slices = []
    z_values = np.linspace(mesh.bounds[0][2], mesh.bounds[1][2], num_slices)
    
    for z in z_values:
        slice = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if slice is not None:
            slice_2D, _ = slice.to_planar()
            slices.append(slice_2D)
    
    return slices

def plot_slices(slices):
    plt.figure(figsize=(10, 10))
    for slice in slices:
        for path in slice.entities:
            if isinstance(path, trimesh.path.entities.Line):
                vertices = path.points
                print(f"Vertices shape: {vertices.shape}, vertices: {vertices}")
                if len(vertices) % 2 != 0:
                    continue  # Skip invalid shapes
                vertices = vertices.reshape(-1, 2)
                plt.plot(vertices[:, 0], vertices[:, 1], color='black')
    plt.gca().set_aspect('equal')
    plt.show()

def generate_gcode(slices):
    gcode = []
    gcode.append("G21 ; Set units to millimeters")
    gcode.append("G90 ; Use absolute coordinates")
    gcode.append("G1 F1000 ; Set feedrate")
    
    for slice in slices:
        for path in slice.entities:
            if isinstance(path, trimesh.path.entities.Line):
                vertices = path.points
                if len(vertices) % 2 != 0:
                    continue  # Skip invalid shapes
                vertices = vertices.reshape(-1, 2)
                gcode.append(f"G0 X{vertices[0, 0]} Y{vertices[0, 1]} ; Move to start point")
                for x, y in vertices:
                    gcode.append(f"G1 X{x} Y{y} ; Engrave")
    
    return gcode

def save_gcode(gcode, file_path):
    with open(file_path, 'w') as f:
        for line in gcode:
            f.write(line + '\n')

# Load the STL file
stl_file_path = 'C:\\Users\\a6260\\Downloads\\galvo\\venv\\assets\\qrcode.stl'
mesh = load_stl(stl_file_path)

# Generate slices
slices = generate_slices(mesh, num_slices=20)

# Plot the slices
plot_slices(slices)

# Generate G-code
gcode = generate_gcode(slices)

# Save the G-code to a file
gcode_file_path = 'C:\\Users\\a6260\\Downloads\\galvo\\venv\\assets\\stl2gcode.gcode'
save_gcode(gcode, gcode_file_path)
