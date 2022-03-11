import socket
import picar_4wd as car
import time
from gpiozero import CPUTemperature
from enum import Enum

HOST = "192.168.107.241" # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

DISTANCE_PER_SECOND = 28 # cm / s
MOTOR_POWER = -10 # The power needed to go forward at DISTANCE_PER_SECOND
TIME_FOR_TURN_90 = 1.4 # Seconds of turn_right or turn_left

class Movement(Enum):
    STOPPED = 0
    FORWARD = 1
    TURN_LEFT = 2
    TURN_RIGHT = 3
    BACKWARD = 4

def get_angle_delta(now, move, start_move):
    if move == Movement.STOPPED or move == Movement.FORWARD or move == Movement.BACKWARD:
        return 0
    
    delta_time = now - start_move
    deg = 90.0 * delta_time / TIME_FOR_TURN_90
    
    if move == Movement.TURN_LEFT:
        return deg
    elif move == Movement.TURN_RIGHT:
        return -deg

    return 0

def get_distance_delta(now, move, start_move):
    if move != Movement.FORWARD and move != Movement.BACKWARD:
        return 0
    
    delta_time = now - start_move
    delta_dist = delta_time * DISTANCE_PER_SECOND
    return delta_dist

def get_speed(move):
    speed = 0
    if move == Movement.FORWARD:
        speed = DISTANCE_PER_SECOND
    elif move == Movement.BACKWARD:
        speed = -DISTANCE_PER_SECOND
    return speed

def get_temperature():
    pi_temp = CPUTemperature() #create a CPUTemperature object
    temp_celsius = float(pi_temp.temperature)
    #temp_fahr = (temp_celsius * (9/5)) + 32
    return temp_celsius
    

def get_direction_string(direction):
    # Get direction between -180 and 180
    d = direction % 360
    if d > 180:
        d -= 360
    
    angles = {0:'E', 45:'NE', 90:'N', 135:'NW', 180:'W', -180:'W', -135:'SW', -90:'S', -45:'SE'}
    angle = min(angles.keys(), key=lambda x:abs(x-d))
    return "%d deg (%s)" % (d, angles[angle])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    try:
        start_move = 0
        move = Movement.STOPPED
        direction = 0
        distance = 0
        
        while 1:
            client, clientInfo = s.accept()
            print("server recv from: ", clientInfo)
            data = client.recv(1024).decode().strip()      # receive 1024 Bytes of message in binary format
            if data == "":
                continue

            now = time.time()
            
            distance += get_distance_delta(now, move, start_move)
            direction += get_angle_delta(now, move, start_move)
            
            start_move = now
            
            if data == "87":
                car.forward(MOTOR_POWER)
                start_move = now
                move = Movement.FORWARD
            elif data == "83":
                car.backward(MOTOR_POWER)
                start_move = now
                move = Movement.BACKWARD
            elif data == "65":
                car.turn_left(MOTOR_POWER)
                start_move = now
                move = Movement.TURN_LEFT
            elif data == "68":
                car.turn_right(MOTOR_POWER)
                start_move = now
                move = Movement.TURN_RIGHT
            #elif data == "88":
            #    car.stop()
            else:
                car.stop()
                move = Movement.STOPPED
                
            print(data)
            
            speed = get_speed(move)
            temp = get_temperature()
            direction_str = get_direction_string(direction)
            response = "%s,%d cm/s,%.2f cm,%.2f C" % (direction_str, speed, distance, temp)

            client.sendall(response.encode()) # Echo back to client
                
    except Exception as e: 
        print("Closing socket:", e)
        client.close()
        s.close()    