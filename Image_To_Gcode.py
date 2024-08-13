import cv2
import numpy as np
from tqdm import tqdm  # Import tqdm for progress bar

class ImageToGcode:
    def __init__(self, image_file_path, output_file_path, downsample_factor, raster_direction, mode="vector", scale=1.0, threshold=128, invert=0, scale_mode="default"):
        self.image_file = image_file_path
        self.output_file = output_file_path
        self.downsample_factor = downsample_factor
        self.raster_direction = raster_direction.lower().strip()
        self.mode = mode.lower().strip()
        self.scale = scale
        self.threshold = threshold
        self.invert = invert
        self.scale_mode = scale_mode.lower().strip()

        if mode == "vector":
            self.imageToVector()
        elif mode == "raster":
            self.imageToRaster()
        else:
            raise ValueError("Unsupported mode. Use 'raster' or 'vector'.")

    def _image_Threshold(self):
        img = cv2.imread(self.image_file, cv2.IMREAD_GRAYSCALE)
        ret, binary_img = cv2.threshold(img, self.threshold, 255, cv2.THRESH_BINARY)
        if self.invert == 1:
            binary_img = cv2.bitwise_not(binary_img)
        return binary_img

    def imageToVector(self):
        binary_img = self._image_Threshold()
        height, width = binary_img.shape

        # Optionally downsample the image to reduce vector points
        new_height, new_width = height // self.downsample_factor, width // self.downsample_factor
        downsampled_img = cv2.resize(binary_img, (new_width, new_height), interpolation=cv2.INTER_AREA)

        contours, _ = cv2.findContours(downsampled_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        gcode = []

        with open(self.output_file, 'w') as f:
            f.write("vector\n")
            for contour in tqdm(contours, desc="Processing contours", unit="contour"):
                for point in contour:
                    x, y = point[0]

                    # Scale coordinates based on original image dimensions
                    if self.scale_mode == "default":
                        x = float(x * self.downsample_factor) * self.scale
                        y = float(y * self.downsample_factor) * self.scale
                    elif self.scale_mode == "scale":
                        x = float(x * self.downsample_factor / width) * self.scale
                        y = float(y * self.downsample_factor / height) * self.scale

                    gcode.append(f"G01 X{x:.6f} Y{y:.6f}")
                    f.write(f"G01 X{x:.6f} Y{y:.6f}\n")

        return gcode

    def imageToRaster(self):
        binary_img = self._image_Threshold()

        # Downsample the image to reduce the number of points
        height, width = binary_img.shape
        new_height, new_width = height // self.downsample_factor, width // self.downsample_factor
        downsampled_img = cv2.resize(binary_img, (new_width, new_height), interpolation=cv2.INTER_AREA)

        gcode = []

        def uni_dir_raster():
            with open(self.output_file, 'w') as f:
                f.write("raster\n")
                for y in tqdm(range(new_height), desc="Processing rows", unit="row"):
                    row = downsampled_img[y]
                    for x in range(new_width):

                        # Store the original x and y for indexing
                        original_x = x
                        original_y = y

                        # Calculate the scaled x and y for G-code
                        if self.scale_mode == "default":
                            scaled_x = float(original_x * self.downsample_factor) * self.scale
                            scaled_y = float(original_y * self.downsample_factor) * self.scale
                        elif self.scale_mode == "scale":
                            scaled_x = float(original_x * self.downsample_factor / width) * self.scale
                            scaled_y = float(original_y * self.downsample_factor / height) * self.scale

                        # Use original x for indexing the row
                        if row[original_x] == 255:
                            f.write(f"G01 X{scaled_x:.6f} Y{scaled_y:.6f} M3 S255\n")
                        else:
                            f.write(f"G01 X{scaled_x:.6f} Y{scaled_y:.6f} M5 S00\n")

                    # Move to the start of the next line (in Y axis) with the laser off
                    if y + 1 < new_height:
                        scaled_y_next = float(y + 1) * self.downsample_factor * self.scale
                        next_line_move = f"G1 X{scaled_x:.6f} Y{scaled_y_next:.6f} M5 S00\n"
                        f.write(next_line_move)

        def bi_dir_raster():
            with open(self.output_file, 'w') as f:
                f.write("raster\n")
                for y in tqdm(range(new_height), desc="Processing rows", unit="row"):
                    row = downsampled_img[y]

                    # Alternate the direction of the X-axis depending on the Y-axis line number
                    x_range = range(new_width) if y % 2 == 0 else range(new_width - 1, -1, -1)

                    for x in x_range:

                        # Store the original x and y for indexing
                        original_x = x
                        original_y = y

                        # Calculate the scaled x and y for G-code
                        if self.scale_mode == "default":
                            scaled_x = float(original_x * self.downsample_factor) * self.scale
                            scaled_y = float(original_y * self.downsample_factor) * self.scale
                        elif self.scale_mode == "scale":
                            scaled_x = float(original_x * self.downsample_factor / width) * self.scale
                            scaled_y = float(original_y * self.downsample_factor / height) * self.scale

                        # Use original x for indexing the row
                        if row[original_x] == 255:
                            f.write(f"G01 X{scaled_x:.6f} Y{scaled_y:.6f} M3 S255\n")
                        else:
                            f.write(f"G01 X{scaled_x:.6f} Y{scaled_y:.6f} M5 S00\n")

        if self.raster_direction == 'uni':
            uni_dir_raster()
        elif self.raster_direction == 'bi':
            bi_dir_raster()

        return gcode, new_width, new_height
