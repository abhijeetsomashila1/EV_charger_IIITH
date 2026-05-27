import threading
import time
import serial
import serial.tools.list_ports
import fnmatch
import send_to_AR
import EV_BLE
import tkinter as tk


# =========================================================
# CHECK ARDUINO
# =========================================================

def is_arduino(port):

    try:

        ser = serial.Serial(port, 9600, timeout=1)

        time.sleep(2)

        ser.reset_input_buffer()

        ser.write(b'CHECK_ARDUINO\n')

        time.sleep(1)

        if ser.in_waiting:

            response = ser.readline().decode().strip()

            print(f"{port} -> {response}")

            if response == "ARDUINO_OK":

                ser.close()

                return True

        ser.close()

    except Exception as e:

        print(f"Error checking {port}: {e}")

    return False


# =========================================================
# FIND PORTS
# =========================================================

def find_ports():

    ports = serial.tools.list_ports.comports()

    arduino_port = None
    wisun_port = None

    print("\nAvailable Ports:\n")

    for port in ports:

        print(port.device)

    for port in ports:

        if fnmatch.fnmatch(port.device, '/dev/ttyACM*'):

            if is_arduino(port.device):

                arduino_port = port.device

            else:

                wisun_port = port.device

    return arduino_port, wisun_port


# =========================================================
# START GUI
# =========================================================

def start_ui():

    root = tk.Tk()

    app = EV_BLE.MainApp(
        root,
        wisun_port,
        arduino_socket_port
    )

    root.mainloop()


# =========================================================
# MAIN
# =========================================================

if __name__ == '__main__':

    time.sleep(3)

    arduino_ser_port, wisun_ser_port = find_ports()

    if arduino_ser_port is None:

        print("\nArduino BLE not detected\n")

        exit(1)

    print(f"\nArduino Port : {arduino_ser_port}")

    if wisun_ser_port:

        print(f"Wi-SUN Port  : {wisun_ser_port}")

    # SOCKET PORTS
    socket_base = 6010

    arduino_socket_port = socket_base + 1

    # START ARDUINO THREAD
    sendAR_thread = threading.Thread(
        target=send_to_AR.sendAR,
        args=(arduino_ser_port, arduino_socket_port,)
    )

    sendAR_thread.daemon = True

    sendAR_thread.start()

    time.sleep(2)

    # START GUI
    start_ui()