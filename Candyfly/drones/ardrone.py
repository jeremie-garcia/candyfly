from pyparrot.Bebop import Bebop

from drones.drone import Drone


class ARDrone(Drone):

    def __init__(self):
        super().__init__()

        self.bebop = Bebop()

        print("connecting to bebop drone")
        self.connection.emit("progress")
        self.success = self.bebop.connect(5)
        if self.success:
            self.connection.emit("on")
            self.bebop.set_max_altitude(20)
            self.bebop.set_max_distance(20)
            self.bebop.set_max_rotation_speed(180)
            self.bebop.set_max_vertical_speed(2)
            self.bebop.enable_geofence(1)
            self.bebop.set_hull_protection(1)

            # todo: battery signal to emit (look in sensors)
            #TODO test this piece of code
            self.bebop.set_user_sensor_callback(print, self.bebop.sensors.battery)
        else:
            print("refresh....")
            self.connection.emit("off")



    def take_off(self):
        self.bebop.safe_takeoff(5)

    def land(self):
        self.bebop.safe_land(5)

    def stop(self):
        self.bebop.disconnect()

    def fly_direct(self, roll, pitch, yaw, vertical_movement):
        my_roll = self.bebop._ensure_fly_command_in_range(roll)
        my_pitch = self.bebop_ensure_fly_command_in_range(pitch)
        my_yaw = self.bebop_ensure_fly_command_in_range(yaw)
        my_vertical = self.bebop_ensure_fly_command_in_range(vertical_movement)
        command_tuple = self.bebop.command_parser.get_command_tuple("ardrone3", "Piloting", "PCMD")
        self.bebop.drone_connection.send_single_pcmd_command(command_tuple, my_roll, my_pitch, my_yaw, my_vertical)

    def process_motion(self, _up, _rotate, _front, _right):
        velocity_up = _up * self.max_vert_speed
        velocity_yaw = _rotate * self.max_rotation_speed
        velocity_pitch = _front * self.max_horiz_speed
        velocity_roll = _right * self.max_horiz_speed
        #print("PRE", velocity_roll, velocity_pitch, velocity_up, velocity_yaw)
        self.fly_direct(velocity_roll, velocity_pitch, velocity_yaw, velocity_up)
