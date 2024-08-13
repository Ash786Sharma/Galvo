from Image_To_Gcode import ImageToGcode
from GcodeClass import GcodeParser
from LaserPathPlanning import LaserPathPlanning
from LaserPathVisual import LaserPathVisual

def main():
    image_path = 'C:\\Users\\a6260\\Downloads\\galvo\\assets\\square.png'
    gcode_path = 'C:\\Users\\a6260\\Downloads\\galvo\\assets\\texttogcode_line.gcode'
    output_gcode_path = 'C:\\Users\\a6260\\Downloads\\galvo\\assets\\testclass.gcode'
    mode = "raster"
    #mode = "vector"
    scale = 20.00
    threshold = 128
    invert = 1
    scale_mode = "scale"
    kpps = 20000
    distance = 255.64
    #raster_dir = 'uni'
    raster_dir = 'bi'
    downsample_factor = 2
    
    print(f"Running ImageToGcode with mode={mode}")
    ImageToGcode(image_path, output_gcode_path, downsample_factor, raster_dir, mode, scale, threshold, invert, scale_mode)
    
    print(f"Parsing G-code from {output_gcode_path}")
    parser = GcodeParser(output_gcode_path)
    frames = parser.get_frames()
    x_coords = parser.get_x_coords()
    y_coords = parser.get_y_coords()
    #laser_state = parser.get_laser_state()
    img_width, img_height = parser.get_image_dimensions()
    
    print(f"Dimensions: {img_width}x{img_height}")
    print(f"Number of frames: {len(frames)}")
    print(f"Number of xcoords: {len(x_coords)}")
    print(f"Number of ycoords: {len(y_coords)}")
    #print(f"Number of xcoords: {(x_coords)}")
    #print(f"Number of laser state: {len(laser_state)}")
    motion = LaserPathPlanning(x_coords,y_coords, distance)
    smooth_dac_values_x, smooth_dac_values_y = motion.get_dac_values()
    
    visual = LaserPathVisual(smooth_dac_values_x, smooth_dac_values_y, distance, mode)
    visual1 = LaserPathVisual(x_coords, y_coords, distance, mode)
    #print(f"Number of frames: {(frames)}")

    #if len(frames) > 0:
    #    for i, frame in enumerate(frames):
    #        print(f"Frame {i}: {frame}")

if __name__ == "__main__":
    main()
