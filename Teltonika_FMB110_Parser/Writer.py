import json
from dataclasses import dataclass


@dataclass
class Write:
    @staticmethod
    def dataAsBytes(data):
        with open('data/raw_bytes.txt', 'a') as w:
            for b in data:
                w.write(bin(b)[2:].zfill(8))
            w.writelines('\n')

    @staticmethod
    def dataAsHex(data):
        with open('data/raw_hex.txt', 'a+') as w:
            w.writelines(data.decode('utf-8') + '\n')

    @staticmethod
    def newPacketDivider():
        with open('data/decoded_avl.txt', 'a') as a:
            a.write('\n=========NEW AVL_DATA_PACKET=========\n')

    @staticmethod
    def newDataLineInPacket(dataLine):
        with open('data/decoded_avl.txt', 'a') as a:
            a.write(json.dumps(dataLine))
            a.write('\n')
