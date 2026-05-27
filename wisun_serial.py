import socket
import serial
import time
import select


def sendAR(AR_ser_port, port=6011):

    print("\nAR Script Started\n")

    try:

        ser = serial.Serial(
            AR_ser_port,
            9600,
            timeout=1
        )

        server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server.bind(
            (socket.gethostname(), port)
        )

        server.listen(1)

        print(f"Listening on port {port}")

        while True:

            client, addr = server.accept()

            print(f"\nClient Connected : {addr}\n")

            while True:

                try:

                    readable, _, _ = select.select(
                        [ser, client],
                        [],
                        [],
                        1
                    )

                    for source in readable:

                        # SERIAL -> SOCKET
                        if source == ser:

                            data = ser.readline().decode().strip()

                            if data:

                                print(f"Arduino : {data}")

                                client.send(
                                    (data + '\n').encode()
                                )

                        # SOCKET -> SERIAL
                        elif source == client:

                            data = client.recv(
                                1024
                            ).decode().strip()

                            if data:

                                print(f"App : {data}")

                                ser.write(
                                    (data + '\n').encode()
                                )

                except Exception as e:

                    print(f"Connection Error : {e}")

                    client.close()

                    break

    except Exception as e:

        print(f"AR Script Error : {e}")