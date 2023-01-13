import socket
import threading
import binascii
import time
import traceback

from AvlDecoder import AvlDecoder, ERROR_VALUE
from DbRequest import DbRequest
from TimeUtils import readTime
from Writer import Write


post_requester = DbRequest()


class TCPServer:
    def __init__(self, port):
        self.number_of_data_resp = None

        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.bind(('', self.port))

    def tcpServer(self):
        self.sock.listen()
        while True:
            conn, addr = self.sock.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

    def Communicator(self, conn, imei):
        accept_con_mes = '\x01'
        conn.send(accept_con_mes.encode('utf-8'))
        print("Sent 0x01 response to Teltonika device. It means server agrees to receive the data from this device.")
        while True:
            try:
                data = conn.recv(1024)
                if (data):
                    avl_decoder = AvlDecoder()

                    received = TCPServer.rawToHex(data)
                    Write.dataAsHex(received)
                    res = avl_decoder.decodeAVL(received.decode('utf-8'))
                    valid_res_generator = [p for p in res if p != ERROR_VALUE]
                    print(f"| TIME | Received packet {readTime()}")
                    anything = 0
                    for packet in valid_res_generator:
                        packet['imei'] = imei  # IMEI_len(2 bytes) | IMEI_val(X bytes)
                        print("avl_data_packet", packet)
                        post_requester.save(packet)

                    self.number_of_data_resp = avl_decoder.number_of_data_1
                    resp = TCPServer.mResponse(self.number_of_data_resp)
                    conn.send(resp)
                    time.sleep(2)
                else:
                    print("break")
                    break
            except Exception as e:
                print(traceback.format_exc())
                print(e)
                break
        print('|EXIT Communicator|')

    def handle_client(self, conn, addr):
        print(f"[Connection from device] {addr} ")
        connected = True
        while connected:
            print("waiting for device")
            try:
                imei_data = conn.recv(1024)
                if imei_data:
                    imei = imei_data[2:].decode('utf-8')
                    print(f"Device IMEI: {imei}")
                    self.Communicator(conn, imei)
                else:
                    break
            except Exception as e:
                print('|CLOSED connection|')
                conn.close()
                break

    @staticmethod
    def rawToHex(raw):
        decoded = binascii.hexlify(raw)
        return decoded

    @staticmethod
    def mResponse(response):
        return response.to_bytes(4, byteorder='big')


if __name__ == '__main__':
    port = 5560
    data = TCPServer(port)
    data.tcpServer()
