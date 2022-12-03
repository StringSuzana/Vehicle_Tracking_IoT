import socket
import threading
import binascii
import time
import traceback

from AvlDecoder import AvlDecoder
from DbRequest import DbRequest
from TimeUtils import readTime

avl_decoder = AvlDecoder()
post_requester = DbRequest()


class TCPServer:
    def __init__(self, port):
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
                    received = self.rawToHex(data)
                    with open('data/raw_hex.txt', 'a+') as w:
                        w.writelines(received.decode('utf-8') + '\n')
                    with open('data/raw_bytes.txt', 'a') as w:
                        for b in data:
                            w.write(bin(b)[2:].zfill(8))
                        w.writelines('\n')
                    avl_data_packet = avl_decoder.decodeAVL(received.decode('utf-8'))
                    print(f"| TIME | Received packet {readTime()}")
                    for packet in avl_data_packet:
                        packet['imei'] = imei  # IMEI_len(2 bytes) | IMEI_val(X bytes)
                        print("avl_data_packet", packet)
                        self.number_of_data_resp = packet['number_of_data_1']
                    resp = self.mResponse(self.number_of_data_resp)
                    conn.send(resp)
                    time.sleep(10)
                else:
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

    def rawToHex(self, raw):
        decoded = binascii.hexlify(raw)
        return decoded

    def mResponse(self, data):
        return data.to_bytes(4, byteorder='big')


if __name__ == '__main__':
    port = 5555
    data = TCPServer(port)
    data.tcpServer()
