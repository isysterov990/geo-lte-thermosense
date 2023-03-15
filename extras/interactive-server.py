#!/usr/bin/env python3

# This is a simple socket server for testing

import socket

HOST = '159.89.114.72'  # Standard loopback interface address (localhost)
PORT = 8884         # Port to listen on (non-privileged ports are > 1023)
import threading
import queue
import time

def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while (True):
        input_str = input()
        inputQueue.put(input_str)

def main():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)

                frame = b''
                tel_sent = 0
                while True:
                    buffer = conn.recv(4096)
                    if not buffer:
                        break
                    frame += buffer

                    if (not tel_sent and frame[-2:] == b'\r\n'):
                        # end of frame
                        print('Received:\t', repr(frame))

                        cmd = frame.decode('ascii').split(',')[0]
                        out = None
                        if cmd == '+HRT':
                            EXIT_COMMAND = "exit"
                            inputQueue = queue.Queue()

                            inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
                            inputThread.start()
                            while(True):
                                if (inputQueue.qsize() > 0):
                                    input_str = inputQueue.get()
                                    print("input_str = {}".format(input_str))
                                    out = '{}\r\n'.format(input_str)
                                    out = out.encode()
                                    if(out!=None):
                                        conn.sendall(out)
                                        tel_sent = 1
                                        print('-- Sent:\n', repr(out))
                                    if (input_str == EXIT_COMMAND):
                                        print("Exiting serial terminal.")
                                        break

                                    time.sleep(0.01)


                        frame = b''  # reset frame
                    elif tel_sent and frame[-1:] == b'\x04':
                        print('-- Received:\n', repr(frame))
                        frame = b''  # reset frame
                        tel_sent = 0



main()
