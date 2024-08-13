import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class GCodeParser:
    def __init__(self, gcode_file):
        self.gcode_file = gcode_file
        self.commands = []

    def parse(self):
        with open(self.gcode_file, 'r') as file:
            for line in file:
                command = self._parse_line(line)
                if command:
                    self.commands.append(command)

    def _parse_line(self, line):
        line = line.strip()
        if line and not line.startswith(';'):  # Ignore empty lines and comments
            parts = line.split(' ')
            cmd = parts[0]
            params = {part[0]: float(part[1:]) for part in parts[1:] if len(part) > 1}
            return (cmd, params)
        return None


class PathPlanner:
    def __init__(self, commands):
        self.commands = commands
        self.lookahead_buffer = []
        self.planned_paths = []
        self.laser_state = False

    def plan(self):
        for command in self.commands:
            
            cmd, params = command
            if cmd in ('G0', 'G1','G00', 'G01', 'G2', 'G3', 'G02', 'G03'):  # Linear and circular movements
                self.lookahead_buffer.append(command)
                print(command)
                if len(self.lookahead_buffer) > 1:
                    self._plan_lookahead()
            elif cmd in ('M3', 'M5'):  # Laser control
                self._handle_laser_control(cmd)

    def _plan_lookahead(self):
        prev_cmd = self.lookahead_buffer[-2]
        curr_cmd = self.lookahead_buffer[-1]

        if prev_cmd[0] in ('G0', 'G1', 'G00', 'G01') and curr_cmd[0] in ('G0', 'G1', 'G00', 'G01'):
            self._plan_linear_movement(prev_cmd, curr_cmd)
        elif prev_cmd[0] in ('G0', 'G1', 'G00', 'G01') and curr_cmd[0] in ('G2', 'G3', 'G02', 'G03'):
            self._plan_circular_movement(prev_cmd, curr_cmd)

    def _plan_linear_movement(self, prev_cmd, curr_cmd):
        prev_pos = np.array([prev_cmd[1].get(axis, 0) for axis in 'XYZ'])
        curr_pos = np.array([curr_cmd[1].get(axis, 0) for axis in 'XYZ'])
        distance = np.linalg.norm(curr_pos - prev_pos)
        speed = curr_cmd[1].get('F', 1500)  # Default speed
        time = distance / speed
        self.planned_paths.append((prev_pos, curr_pos, time, self.laser_state))

    def _plan_circular_movement(self, prev_cmd, curr_cmd):
        start_pos = np.array([prev_cmd[1].get(axis, 0) for axis in 'XYZ'])
        end_pos = np.array([curr_cmd[1].get(axis, 0) for axis in 'XYZ'])
        center = np.array([curr_cmd[1].get('I', 0), curr_cmd[1].get('J', 0)])
        radius = np.linalg.norm(center)
        speed = curr_cmd[1].get('F', 1500)  # Default speed
        angle = np.arctan2(end_pos[1] - center[1], end_pos[0] - center[0])
        time = (angle * radius) / speed
        self.planned_paths.append((start_pos, end_pos, time, self.laser_state))

    def _handle_laser_control(self, cmd):
        if cmd == 'M3':
            self.laser_state = True
        elif cmd == 'M5':
            self.laser_state = False


class MotionPlanner:
    def __init__(self, planned_paths):
        self.planned_paths = planned_paths

    def execute(self):
        for path in self.planned_paths:
            self._move_to_position(path)

    def _move_to_position(self, path):
        start_pos, end_pos, time, laser_state = path
        print(f"Moving from {start_pos} to {end_pos} in {time:.2f} seconds with laser {'ON' if laser_state else 'OFF'}")


def visualize_motion(planned_paths):
    fig, ax = plt.subplots()
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)

    xdata, ydata = [], []
    ln, = plt.plot([], [], 'b', animated=True)
    points, = plt.plot([], [], 'ro')

    def init():
        ax.set_xlim(-100, 100)
        ax.set_ylim(-100, 100)
        ln.set_data([], [])
        points.set_data([], [])
        return ln, points

    def update(frame):
        start_pos, end_pos, _, laser_state = planned_paths[frame]
        xdata.append(end_pos[0])
        ydata.append(end_pos[1])
        ln.set_data(xdata, ydata)
        points.set_data(xdata, ydata)
        return ln, points

    ani = FuncAnimation(fig, update, frames=range(len(planned_paths)), init_func=init, blit=True)
    plt.show()


def main():
    gcode_file = 'C:\\Users\\a6260\\Downloads\\galvo\\assets\\texttogcode_line.gcode'
    
    # Step 1: Parse G-code
    parser = GCodeParser(gcode_file)
    parser.parse()
    
    # Step 2: Path Planning
    planner = PathPlanner(parser.commands)
    planner.plan()
    
    # Step 3: Motion Planning
    motion_planner = MotionPlanner(planner.planned_paths)
    motion_planner.execute()
    
    # Visualize the motion
    visualize_motion(planner.planned_paths)

if __name__ == "__main__":
    main()
