import numpy as np
from scipy.interpolate import interp1d
from tqdm import tqdm  # Import tqdm for progress bar

class LaserPathPlanning:
    
    def __init__(self, x_coords, y_coords, laser_distance, intrp_mode='linear', min_angle=-12.5, max_angle=12.5, voltage_min=-15, voltage_max=15, dac_res=4096, galvo_kpps=20000):
        self.X_Coords = x_coords
        self.Y_Coords = y_coords
        self.Laser_Distance = laser_distance
        self.intrp_mode = intrp_mode
        # Constants based on your specifications
        self.phi_min_deg = min_angle   # Minimum angle in degrees
        self.phi_max_deg = max_angle   # Maximum angle in degrees
        self.voltage_min = voltage_min  # Minimum voltage in volts
        self.voltage_max = voltage_max   # Maximum voltage in volts
        self.dac_resolution = dac_res  # DAC resolution (12-bit)
        self.galvo_kpps = galvo_kpps    # Galvo points per second
        self.dac_values_x = []
        self.dac_values_y = []
        self.smooth_dac_value_x = []
        self.smooth_dac_value_y = []
        
    def _cartesian_to_theta(self, x, y):
        theta_x = np.arctan2(x, self.Laser_Distance)  # X-axis
        theta_y = np.arctan2(y, self.Laser_Distance)  # Y-axis
        return theta_x, theta_y
        
    # Function to convert theta (radians) to DAC value
    def _theta_to_dac(self, theta_rad):
        # Convert theta to degrees
        theta_deg = np.rad2deg(theta_rad)
        
        # Map theta_deg to the range of your galvo (-12.5° to +12.5°)
        mapped_theta_deg = np.interp(theta_deg, [-180, 180], [self.phi_min_deg, self.phi_max_deg])
        
        # Map mapped_theta_deg to DAC range (0 to 4096)
        dac_value = np.interp(mapped_theta_deg, [self.phi_min_deg, self.phi_max_deg], [0, self.dac_resolution])
        
        # Round DAC value to nearest integer
        #dac_value = int(round(dac_value))
        
        return dac_value
    
    # Interpolation function
    def _interpolate_points(self, x, y, num_points):
        t = np.linspace(0, 1, len(x))
        t_new = np.linspace(0, 1, num_points)
        interp_x = interp1d(t, x, kind=self.intrp_mode)
        interp_y = interp1d(t, y, kind=self.intrp_mode)
        x_new = interp_x(t_new)
        y_new = interp_y(t_new)
        return x_new, y_new
    
    def coords_to_dac(self):
        
        # Use tqdm to show progress in the terminal
        for x_coord, y_coord in tqdm(zip(self.X_Coords, self.Y_Coords), total=len(self.X_Coords), desc="Converting coordinates to DAC values"):
            
            theta_x, theta_y = self._cartesian_to_theta(x_coord, y_coord)
        
            # Print theta values for debugging
            #print(f"Point: ({x_coord}, {y_coord}) -> Theta: ({theta_x}, {theta_y})")
            
            dac_value_x = self._theta_to_dac(theta_x)
            dac_value_y = self._theta_to_dac(theta_y)
            
            # Print DAC values for debugging
            #print(f"Theta: ({theta_x}, {theta_y}) -> DAC: ({dac_value_x}, {dac_value_y})")
            
            self.dac_values_x.append(dac_value_x)
            self.dac_values_y.append(dac_value_y)
            
        # Ensure DAC values are not empty
        if not self.dac_values_x or not self.dac_values_y:
            raise ValueError("DAC values are empty. Check the G-code parsing and conversion functions.")
        
        # Interpolate the DAC values to get a smoother curve
        num_interpolated_points = 1 * len(self.dac_values_x)  # Adjust the factor as needed
        self.smooth_dac_values_x, self.smooth_dac_values_y = self._interpolate_points(self.dac_values_x, self.dac_values_y, num_interpolated_points)

    def get_dac_values(self):
        self.coords_to_dac()
        dac_x = np.round(self.dac_values_x).astype(int)
        dac_y = np.round(self.dac_values_y).astype(int)
        return dac_x, dac_y
    
    def get_Smooth_dac_values(self):
        self.coords_to_dac()
        smooth_x = np.round(self.smooth_dac_values_x).astype(int)
        smooth_y = np.round(self.smooth_dac_values_y).astype(int)
        return smooth_x, smooth_y
