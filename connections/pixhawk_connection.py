import serial
import asyncio
from serial.tools import list_ports
import traceback

from mavsdk import System


def getUavPort():
    ports = list_ports.comports()
    for port in ports:
        if 'PX4 FMU v2.x' in port.description:
            try:
                ser = serial.Serial(port.device)
                ser.close()
                return port.device
            except (OSError, serial.SerialException):
                pass
    return None


uav_connected = False

async def connect_to_uav():
    global uav_connected
    if not uav_connected:
        try:
            pix_port = getUavPort() 
            print('--> UAV connecting')
            print('UAV in port '+ pix_port)
     
            uav = System()
            await uav.connect(system_address=f"serial://{pix_port}")
            print("Waiting for UAV to connect...")
            async for state in uav.core.connection_state():
                if state.is_connected:
                    print(f"-- Connected to UAV!")
                    break
                    
            # Get the list of parameters
            #all_params = await uav.param.get_all_params()

            # Iterate through all int parameters
            #for param in all_params.int_params:
            #    print(f"{param.name}: {param.value}")

            #for param in all_params.float_params:
            #    print(f"{param.name}: {param.value}")
            
            #print("Waiting for drone to have a global position estimate...")
            #async for health in uav.telemetry.health():
            #    if health.is_global_position_ok and health.is_home_position_ok:
            #        print("-- Global position state is good enough for flying.")
            #        break
                    
            #print("Fetching amsl altitude at home location....")
            #async for terrain_info in uav.telemetry.home():
            #    absolute_altitude = terrain_info.absolute_altitude_m
            #    break
            
            # Comprueba el estado de la batería
            async for battery in uav.telemetry.battery():
                print(f"Battery: {battery.remaining_percent * 100}%")
                break

            # Comprueba si el dron está en el aire
            #in_air = await uav.telemetry.in_air()
            #print(f"In air: {in_air}")

            # Comprueba el estado de salud del sistema
            #health = await uav.telemetry.health()
            #print(f"Health: {health}")
                
            print("-- Starting magnetometer calibration")
            async for progress_data in uav.calibration.calibrate_magnetometer():
                print(progress_data)
            print("-- Magnetometer calibration finished")
                
            #print("-- Arming")
            #await uav.action.arm()
            
            #print("-- Takeoff")
            #await uav.action.takeoff()
            
            #return master
            return #uav
        except Exception as e:
            print(f'Error al conectar con UAV: {e}')
            traceback.print_exc()
            return None


async def main():
    await connect_to_uav()

asyncio.run(main())