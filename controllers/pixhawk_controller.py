# controllers/pixhawk_controller.py
import serial
import asyncio
from serial.tools import list_ports
import traceback
import random
import math
from threading import Thread
import json

from mavsdk import System


class UAVState:
    def __init__(self):
        self.battery_voltage = 0
        self.battery_min = 6.4
        self.battery_max = 8.4
        self.battery_percent = 0
        self.lat = 0
        self.lon = 0
        self.alt = 0
        self.prev_lat = 0
        self.prev_lon = 0
        self.prev_alt = 0
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.waypoints = None
        self.current_waypoint = None
        self.ground_speed = 0
        self.prev_ground_speed = 0
        self.health = False


class PixhawkController:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connected = False
            cls._instance.uav = None
            cls._instance.client_socket_id = None
            cls._instance.uavpass = random.randint(10**9, 10**10 - 1)
            cls._instance.uav_state = UAVState()
            # cls._instance.update_task_500ms = asyncio.create_task(
            #    cls._instance.update_task_500ms()
            # )
            # cls._instance.update_task_5000ms = asyncio.create_task(
            #    cls._instance.update_task_5000ms()
            # )
        return cls._instance

# INITIALIZATION | CONNECTION --------------------------------------------------
    def _get_uav_port(self):
        ports = list_ports.comports()
        for port in ports:
            # if 'fmuv3' in port.description:
            if 'PX4 FMU v2.x' in port.description:
                try:
                    ser = serial.Serial(port.device)
                    ser.close()
                    return port.device
                except (OSError, serial.SerialException):
                    pass
        return None

    async def connect(self):
        if not self.connected:
            try:
                pix_port = self._get_uav_port()
                if pix_port:
                    print('--> UAV connecting')
                    print('--> UAV in port ' + pix_port)
                    uav = System()
                    await uav.connect(system_address=f"serial://{pix_port}")
                    print("--> Waiting for UAV to connect...")
                    async for state in uav.core.connection_state():
                        if state.is_connected:
                            print(f"--> Connected to UAV!")
                            self.connected = True
                            self.uav = uav
                            # await self.start()
                            break
                else:
                    print(" No Pixhawk found!")
                    self.connected = False
            except Exception as e:
                print(f"Error connecting to UAV: {e}")
                traceback.print_exc()
                self.connected = False

    async def disconnect(self):
        if self.connected:
            await self.uav.close()
            self.connected = False
            print('Pixhawk disconnected')

# COMMANDS -----------------------------------------------------------------

    def get_status(self):
        status_dict = {
            "type": "status",
            "battery_voltage": self.uav_state.battery_voltage,
            "battery_percent": self.uav_state.battery_percent,
            "latitude": self.uav_state.lat,
            "longitude": self.uav_state.lon,
            "altitude": self.uav_state.alt,
            "pitch": self.uav_state.pitch,
            "roll": self.uav_state.roll,
            "yaw": self.uav_state.yaw,
            "ground_speed": self.uav_state.ground_speed,
            "health": self.uav_state.health
        }
        return json.dumps(status_dict)

    async def arm(self):
        try:
            await self.uav.action.arm()
            print("UAV armed")
        except Exception as e:
            print(f"Errorarming UAV: {e}")

    async def take_off(self):
        try:
            await self.uav.action.takeoff()
            print("UAV taking off")
        except Exception as e:
            print(f"Error taking off UAV: {e}")

# disarm
# land
# goto

# STATE ACTUALIZATIONS ------------------------------------------------------

    async def health_check(self):
        try:
            async for health in self.uav.telemetry.health():
                if health.is_global_position_ok and health.is_home_position_ok:
                    self.uav_state.health = True
                return
        except Exception as e:
            print(f"Error checking health: {e}")

    async def battery_check(self):
        try:
            async for battery in self.uav.telemetry.battery():
                self.uav_state.battery_voltage = battery.voltage_v
                self.uav_state.battery_percent = (self.uav_state.battery_voltage - self.uav_state.battery_min) / (
                    self.uav_state.battery_max - self.uav_state.battery_min) * 100
                return
        except Exception as e:
            print(f"Error checking battery: {e}")

    async def attitude_check(self):
        try:
            async for attitude_euler in self.uav.telemetry.attitude_euler():
                self.uav_state.pitch = attitude_euler.pitch_deg
                self.uav_state.roll = attitude_euler.roll_deg
                if attitude_euler.yaw_deg < 0:
                    self.uav_state.yaw = 360 + attitude_euler.yaw_deg
                else:
                    self.uav_state.yaw = attitude_euler.yaw_deg
                return
        except Exception as e:
            print(f"Error checking attitude: {e}")

    async def position_check(self):
        try:
            if self.uav_state.health:
                self.uav_state.prev_lat = self.uav_state.lat
                self.uav_state.prev_lon = self.uav_state.lon
                self.uav_state.prev_alt = self.uav_state.alt
                async for position in self.uav.telemetry.position():
                    self.uav_state.lat = position.latitude_deg
                    self.uav_state.lon = position.longitude_deg
                    self.uav_state.alt = position.relative_altitude_m
                    return
        except Exception as e:
            print(f"Error checking position: {e}")

    async def ground_speed_calc(self, time):
        try:
            self.uav_state.prev_ground_speed = self.uav_state.ground_speed
            diff_lat = (self.uav_state.lat -
                        self.uav_state.prev_lat) * math.pi / 180
            diff_lon = (self.uav_state.lon -
                        self.uav_state.prev_lon) * math.pi / 180
            a = math.sin(diff_lat / 2)**2 + math.cos(self.uav_state.lat * math.pi / 180) * \
                math.cos(self.uav_state.prev_lat * math.pi / 180) * \
                math.sin(diff_lon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = math.sqrt(
                (6371000 * c)**2 + (self.uav_state.alt - self.uav_state.prev_alt)**2)
            speed_ms = distance / time
            self.uav_state.ground_speed = 0.9 * speed_ms * \
                3.6 + 0.1 * self.uav_state.prev_ground_speed
        except Exception as e:
            print(f"Error calculating ground speed: {e}")

# UPDATE LOOP ---------------------------------------------------------------

    async def update_task_500ms(self):
        try:
            if self.connected:
                await self.attitude_check()
        except Exception as e:
            print(f"Error updating state: {e}")

    async def update_task_5000ms(self):
        try:
            if self.connected:
                await self.health_check()
                await self.battery_check()
                await self.position_check()
                await self.ground_speed_calc(5)
        except Exception as e:
            print(f"Error updating state: {e}")

    async def start(self):
        task_500ms = asyncio.create_task(self.update_task_500ms())
        task_5000ms = asyncio.create_task(self.update_task_5000ms())
        asyncio.gather(task_500ms, task_5000ms)

    '''
    async def get_attitude_bak(self):
        try: 
            async for heading in self.uav.telemetry.heading():
                print("Pitch: {} Roll:  Yaw: ".format(heading.heading_deg))
                return heading.heading_deg
        except Exception as e:
            print(f"Error getting UAV health: {e}")
    '''

    # Get the list of parameters
    # all_params = await uav.param.get_all_params()

    # Iterate through all int parameters
    # for param in all_params.int_params:
    #    print(f"{param.name}: {param.value}")

    # for param in all_params.float_params:
    #    print(f"{param.name}: {param.value}")

    # print("Fetching amsl altitude at home location....")
    # async for terrain_info in uav.telemetry.home():
    #    absolute_altitude = terrain_info.absolute_altitude_m
    #    break

    # Comprueba si el dron está en el aire
    # in_air = await uav.telemetry.in_air()
    # print(f"In air: {in_air}")

    # Comprueba el estado de salud del sistema
    # health = await uav.telemetry.health()
    # print(f"Health: {health}")

    # print("-- Starting magnetometer calibration")
    # async for progress_data in uav.calibration.calibrate_magnetometer():
    #    print(progress_data)
    # print("-- Magnetometer calibration finished")


    # return master
"""
class mavsdk.telemetry.FixedwingMetrics(airspeed_m_s, throttle_percentage, climb_rate_m_s)¶
Bases: object

FixedwingMetrics message type.

Parameters:
airspeed_m_s (float) – Current indicated airspeed (IAS) in metres per second

throttle_percentage (float) – Current throttle setting (0 to 100)

climb_rate_m_s (float) – Current climb rate in metres per second
"""

# async def main():
#    await connect_to_uav()

# asyncio.run(main())
