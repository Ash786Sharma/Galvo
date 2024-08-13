import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

class LaserPathVisual:
    
    def __init__(self, x_coords, y_coords, laser_distance, mode, scale=1.0, galvo_kpps=20000):
        #self.visual_mode = visual_mode
        self.scale = scale
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.z_coords = [0] * len(self.x_coords)
        self.laser_distance = laser_distance
        self.mode = mode
        #self.laser_state = laser_state
        self.galvo_kpps = galvo_kpps
        
        if self.mode == "raster":
            self._raster_visual()
        elif self.mode == "vector":
            self._vector_visual()
        else:
            raise ValueError("Unsupported mode. Use 'raster' or 'vector'.")
        
        
    def _vector_visual(self):
        
        # Create 3D plot
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot initial points
        path_line, = ax.plot([], [], [], label='G-code Path', color='blue')
        laser_point, = ax.plot([], [], [], 'ro')  # Red point representing the laser
        origin_point, = ax.plot(min(self.x_coords), min(self.y_coords), [0], 'ro')  # Red point representing the laser
        source_point, = ax.plot(min(self.x_coords), min(self.y_coords), [self.laser_distance], 'go')  # Green point representing the laser source
        connection_line, = ax.plot([], [], [], 'r-')  # Red line connecting laser source to moving point
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('3D Visualization of G-code Path and Galvo Outputs')
        ax.legend()
        
        # Set the view angle for a top-down perspective
        ax.view_init(elev=90, azim=-90)  # Top view
        
        # Set up the limits of the plot
        ax.set_xlim(min(self.x_coords)-50, max(self.x_coords)+50)
        ax.set_ylim(min(self.y_coords)-50, max(self.y_coords)+50)
        ax.set_zlim(0, self.laser_distance + 50)
        
        # Animation function
        def animate(i):
            #if not self.laser_state[i]:
            #    return path_line, laser_point, connection_line  # Skip if laser is off
            
            # Update path line
            path_line.set_data(self.x_coords[:i+1], self.y_coords[:i+1])
            path_line.set_3d_properties([0] * (i+1)) 
            
            # Update laser point
            if i < len(self.x_coords):
                laser_point.set_data([self.x_coords[i]], [self.y_coords[i]])
                laser_point.set_3d_properties([0])
            
            # Update connection line
            if i < len(self.x_coords):
                connection_line.set_data([min(self.x_coords), self.x_coords[i]], [min(self.x_coords), self.y_coords[i]])
                connection_line.set_3d_properties([self.laser_distance, 0])
            
            return path_line, laser_point, connection_line
        
        # Calculate number of frames and interval
        total_points = len(self.x_coords)
        interval = 1000 / self.galvo_kpps
        
        # Create animation
        ani = FuncAnimation(fig, animate, frames=total_points, interval=interval, blit=True)
        
        plt.show()
    
    def _raster_visual(self):
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim(min(self.x_coords)-10, max(self.x_coords)+10 )
        ax.set_ylim(min(self.y_coords)-10, max(self.y_coords)+10 )
        ax.set_zlim(0, 255)  # Assuming laser intensity goes from 0 to 255
        
        print(f"Collected {len(self.x_coords)} laser on points")
        
        line, = ax.plot([], [], [], 'r.', markersize=0.5)
        point, = ax.plot([], [], [], 'bo', markersize=5)
        
        def init():
            line.set_data([], [])
            line.set_3d_properties([])
            point.set_data([], [])
            point.set_3d_properties([])
            return line, point
        
        def update(frame):
            line.set_data(self.x_coords[:frame], self.y_coords[:frame])
            line.set_3d_properties(self.z_coords[:frame])
            if frame < len(self.x_coords):
                point.set_data([self.x_coords[frame]], [self.y_coords[frame]])  # Wrap in a list to make them sequences
                point.set_3d_properties([self.z_coords[frame]])  # Wrap in a list to make them sequences
            return line, point
        
        # Calculate number of frames and interval
        total_points = len(self.x_coords)
        
        num_frames = 1 * len(self.x_coords)  # Adjust the factor as needed
        
        interval = 1000 / self.galvo_kpps
        print("total_points:", total_points, "num_frame:", num_frames, "interval:", interval)
        
        
        ani = FuncAnimation(fig, update, frames=total_points, init_func=init, blit=True, interval=interval)
        
        ax.invert_yaxis()
        plt.title("Laser Engraving Visualization in 3D")
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        ax.set_zlabel("Laser Intensity")
        plt.show()
        
        