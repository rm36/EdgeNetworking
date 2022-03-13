#!/usr/bin/env python3
import bluetooth
import time
import picar_4wd as car

DISTANCE_PER_SECOND = 28 # cm / s
MOTOR_POWER = -10 # The power needed to go forward at DISTANCE_PER_SECOND
TIME_FOR_TURN_90 = 1.4 # Seconds of turn_right or turn_left

def parse_command(strings):
    if len(strings) < 1:
        return 'Not enough params'

    if strings[0] == 'forward':
        if len(strings) < 2:
            return 'Need to specify time to go forward'
        seconds = int(strings[1])
        car.forward(MOTOR_POWER)
        time.sleep(seconds)
        car.stop()
    elif strings[0] == 'backward':
        if len(strings) < 2:
            return 'Need to specify time to go backward'
        seconds = int(strings[1])
        car.backward(MOTOR_POWER)
        time.sleep(seconds)
        car.stop()
    elif strings[0] == 'right':
        car.turn_right(MOTOR_POWER)
        time.sleep(TIME_FOR_TURN_90)
        car.stop()
    elif strings[0] == 'left':
        car.turn_left(MOTOR_POWER)
        time.sleep(TIME_FOR_TURN_90)
        car.stop()
    else:
        return 'Unknown command'

    return 'Done'

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                            service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE],
                            # protocols=[bluetooth.OBEX_UUID]
                            )

print("Waiting for connection on RFCOMM channel", port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from", client_info)

try:
    while True:
        data = client_sock.recv(1024)
        if not data:
            break

        result = parse_command(data.decode().strip().split())
        print(data, ' -> ', result)
        client_sock.send(result)
except OSError:
    pass

print("Disconnected.")

client_sock.close()
server_sock.close()
print("All done.")
