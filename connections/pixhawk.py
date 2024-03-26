import serial
import asyncio
from serial.tools import list_ports
import traceback

from mavsdk import System


class PixhawkController:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connected = False
            cls._instance.uav = None
        return cls._instance

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
                    print('UAV in port ' + pix_port)
                    uav = System()
                    await uav.connect(system_address=f"serial://{pix_port}")
                    print("Waiting for UAV to connect...")
                    async for state in uav.core.connection_state():
                        if state.is_connected:
                            print(f"-- Connected to UAV!")
                            self.connected = True
                            self.uav = uav
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

    async def battery_check(self):
        try:
            for battery in self.uav.telemetry.battery():
                print(f"Battery: {battery.remaining_percent * 100}%")
                return battery.remaining_percent
        except Exception as e:
            print(f"Error checking battery: {e}")

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

            # Get the list of parameters
            # all_params = await uav.param.get_all_params()

            # Iterate through all int parameters
            # for param in all_params.int_params:
            #    print(f"{param.name}: {param.value}")

            # for param in all_params.float_params:
            #    print(f"{param.name}: {param.value}")

            # print("Waiting for drone to have a global position estimate...")
            # async for health in uav.telemetry.health():
            #    if health.is_global_position_ok and health.is_home_position_ok:
            #        print("-- Global position state is good enough for flying.")
            #        break

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


# async def main():
#    await connect_to_uav()

# asyncio.run(main())
