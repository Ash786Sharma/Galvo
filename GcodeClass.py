from tqdm import tqdm  # Import tqdm library

class GcodeParser:
    def __init__(self, gcode_file_path, scale=1.0):
        self.gcode_file_path = gcode_file_path
        self.scale = scale
        self.frames = []
        self.x_coords = []
        self.y_coords = []
        # self.laser_state = []
        self.img_width = 0
        self.img_height = 0
        self.mode = None
        
        self._determine_mode()
        
        if self.mode == "raster":
            self.parse_raster_gcode()
        elif self.mode == "vector":
            self.parse_vector_gcode()
        else:
            raise ValueError("Unsupported mode. Use 'raster' or 'vector'.")
        
    def _determine_mode(self):
        with open(self.gcode_file_path, 'r') as file:
            for line in file:
                parts = line.split()
                if not parts:
                    continue  # skip empty lines
                mode = parts[0].lower()
                if mode == 'raster':
                    self.mode = 'raster'
                    break
                elif mode == 'vector':
                    self.mode = 'vector'
                    break

    def parse_raster_gcode(self):
        with open(self.gcode_file_path, 'r') as file:
            lines = file.readlines()
            for line in tqdm(lines, desc="Parsing Raster G-code"):
                parts = line.split()
                if not parts:
                    continue  # skip empty lines
                command = parts[0]
                if command in {'G00', 'G0', 'G01', 'G1'}:
                    new_x, new_y = None, None
                    laser_on = False
                    for part in parts[1:]:
                        if part.startswith('X'):
                            try:
                                new_x = float(part[1:]) * self.scale
                            except ValueError:
                                print(f"Skipping line with invalid X coordinate: {line}")
                                continue
                        elif part.startswith('Y'):
                            try:
                                new_y = float(part[1:]) * self.scale
                            except ValueError:
                                print(f"Skipping line with invalid Y coordinate: {line}")
                                continue
                        elif part.startswith('M3'):
                            laser_on = True
                        elif part.startswith('M5'):
                            laser_on = False
    
                    if new_x is not None and new_y is not None and laser_on:
                        self.x_coords.append(new_x)
                        self.y_coords.append(new_y)
    
            if self.x_coords:
                self.img_width = max(self.x_coords) / self.scale
            if self.y_coords:
                self.img_height = max(self.y_coords) / self.scale

    def parse_vector_gcode(self):
        with open(self.gcode_file_path, 'r') as file:
            lines = file.readlines()
            for line in tqdm(lines, desc="Parsing Vector G-code"):
                parts = line.split()
                if not parts:
                    continue  # skip empty lines
                command = parts[0]
                if command in {'G00', 'G0', 'G01', 'G1'}:
                    new_x, new_y = None, None
                    for part in parts[1:]:
                        if part.startswith('X'):
                            try:
                                new_x = float(part[1:]) * self.scale
                            except ValueError:
                                print(f"Skipping line with invalid X coordinate: {line}")
                                continue
                        elif part.startswith('Y'):
                            try:
                                new_y = float(part[1:]) * self.scale
                            except ValueError:
                                print(f"Skipping line with invalid Y coordinate: {line}")
                                continue
                    
                    if new_x is not None and new_y is not None:
                        self.x_coords.append(new_x)
                        self.y_coords.append(new_y)
                        
            if self.x_coords:
                self.img_width = max(self.x_coords) / self.scale
            if self.y_coords:
                self.img_height = max(self.y_coords) / self.scale

    def get_frames(self):
        return self.frames
    
    def get_x_coords(self):
        return self.x_coords
    
    def get_y_coords(self):
        return self.y_coords
    
    # def get_laser_state(self):
    #     return self.laser_state

    def get_image_dimensions(self):
        return self.img_width, self.img_height
