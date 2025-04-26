import pyfirmata
import time

# Arduino board setup
board = pyfirmata.Arduino('COM3')  # Change this to your Arduino's serial port

# Pin setup
in1 = board.get_pin('d:4:o')  # Motor 1 control pin 1
in2 = board.get_pin('d:5:o')  # Motor 1 control pin 2
ConA = board.get_pin('d:9:p')  # Motor 1 speed control pin
# in3 = board.get_pin('d:6:o')  # Motor 2 control pin 1
# in4 = board.get_pin('d:7:o')  # Motor 2 control pin 2
# ConB = board.get_pin('d:8:p')  # Motor 2 speed control pin
ir_pin = board.get_pin('d:2:i')  # IR sensor digital input pin
servo_pin = board.get_pin('d:10:p')  # Servo motor pin
pot_pin = board.get_pin('a:0:i')  # Potentiometer pin

# Servo angles
servo_angles = {
    'right': 0,
    'left': 180,
    'back': 270,
    'center': 90
}


def read_ir():
    """Reads IR sensor output."""
    return ir_pin.read()


def look_direction(angle):
    """Looks in a specific direction using servo and IR sensor."""
    servo_pin.write(angle / 180)  # PyFirmata uses 0 to 1 for servo angles
    time.sleep(0.5)
    obstacle_detected = read_ir()
    time.sleep(0.1)
    servo_pin.write(90 / 180)  # Reset servo to center
    return obstacle_detected


def move_stop():
    """Stops the motor."""
    in1.write(0)
    in2.write(0)


def turn_motor_forward():
    """Turns the motor forward."""
    in1.write(0)
    in2.write(1)
    speed = pot_pin.read()
    if speed is not None:
        speed = speed * 0.2492668622
        ConA.write(speed)
    else:
        ConA.write(0.5)  # Default speed if potentiometer value is None


def turn_motor_backward():
    """Turns the motor backward."""
    in1.write(1)
    in2.write(0)
    speed = pot_pin.read()
    if speed is not None:
        speed = speed * 0.2492668622
        ConA.write(speed)
    else:
        ConA.write(0.5)  # Default speed if potentiometer value is None


def main():
    servo_pin.write(180 / 180)  # Initialize servo to right
    time.sleep(2)

    it = pyfirmata.util.Iterator(board)
    it.start()

    while True:
        obstacle_detected = read_ir()
        time.sleep(0.05)

        if obstacle_detected is not None and obstacle_detected == 0:
            print("Obstacle detected!")
            move_stop()
            time.sleep(0.3)
            turn_motor_backward()
            time.sleep(0.4)
            move_stop()
            time.sleep(0.3)

            obstacle_right = look_direction(servo_angles['right'])
            time.sleep(0.3)
            obstacle_left = look_direction(servo_angles['left'])
            time.sleep(0.3)
            obstacle_back = look_direction(servo_angles['back'])
            time.sleep(0.3)
            turn_motor_backward()

            if obstacle_right == 1 and obstacle_left == 0 and obstacle_back == 0:
                print("Moving right.")
                turn_motor_forward()
            elif obstacle_left == 1 and obstacle_right == 0 and obstacle_back == 0:
                print("Moving left.")
                # You need to adjust the motor direction for left turn
                # This might involve changing in1 and in2 states or using another motor
                pass
            else:
                print("No clear path, moving backward.")
                turn_motor_backward()
        else:
            print("No obstacle detected.")
            turn_motor_forward()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        move_stop()
        board.exit()
