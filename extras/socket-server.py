#!/usr/bin/env python3

# This is a simple socket server for testing

import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8883         # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()
        with conn:
            print('\nConnected by', addr)

            frame = b''
            tel_sent = 0
            while True:
                buffer = conn.recv(4096)
                if not buffer:
                    print('Disconnected\n')
                    break
                frame += buffer

                if (not tel_sent and frame[-2:] == b'\r\n'):
                    # end of frame
                    print('Received:\n', repr(frame))

                    cmd = frame.decode('ascii').split(',')[0]
                    if cmd == '+HRT':
                        out = b'$TEL,0\r\n'
                        conn.sendall(out)
                        tel_sent = 1
                        print('Sent:\n', repr(out))

                    frame = b''  # reset frame
                elif tel_sent and frame[-1:] == b'\x04':
                    print('Received:\n', repr(frame))
                    frame = b''  # reset frame
                    tel_sent = 0
