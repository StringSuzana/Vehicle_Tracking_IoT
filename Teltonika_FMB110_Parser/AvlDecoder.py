import math
import json

from TimeUtils import readTime
from TimeUtils import unixToLocal
from IoDecoder import IoElements
from crc16 import Crc16Ibm
from AvlConstants import Avl

io_elements = IoElements()

ERROR_VALUE = -1


class AvlDecoder:
    def __init__(self):
        self.first_io_end = None
        self.first_io_start = None
        self.avl_end_index = None
        self.total_avl_data_size = None
        self.data_field_len = None
        self.raw_data = ""
        self.codecId = 0
        self.number_of_data_1 = 0
        self.number_of_data_2 = 0
        self.crc_16 = 0
        self.avl_entries = []
        self.avl_latest = ""
        self.d_time_unix = 0
        self.d_time_local = ""
        self.avl_io_raw = ""
        self.priority = 0

        self.lon = 0
        self.lat = 0
        self.alt = 0
        self.angle = 0
        self.satellites = 0
        self.speed = 0
        self.decoded_io = {}

    def decodeAVL(self, data):
        data = data.rstrip()
        if data == '':
            return ERROR_VALUE
        if Crc16Ibm.isCorrect(data) is not True:
            return ERROR_VALUE

        self.raw_data = data
        # data_field is from Codec ID to number_of_data_2
        self.data_field_len = int(data[Avl.data_field_len_start:Avl.data_field_len_end], 16) * 2
        self.avl_end_index = len(data[0:len(data) - Avl.data_end])
        self.total_avl_data_size = len(data[Avl.data_start:self.avl_end_index])

        self.codecId = int(data[Avl.codec_id_start:Avl.codec_id_end], 16)  # codec ID = 0x08 (Codec 8)
        self.number_of_data_1 = int(data[Avl.number_of_data_1_start:Avl.number_of_data_1_end], 16)

        self.number_of_data_2 = int(data[Avl.number_of_data_2_start:Avl.number_of_data_2_end], 16)
        self.crc_16 = int(data[Avl.crc_16_start:], 16)  # crc-16 check

        if self.codecId == 8 and (self.number_of_data_1 == self.number_of_data_2):
            self.first_io_start = 20  # first io starting pos
            self.first_io_end = int(self.total_avl_data_size / self.number_of_data_1)  # end pos for first io entry

            avl_data_entries = data[self.first_io_start: self.avl_end_index]  # entry data

            total_entries_size = len(avl_data_entries)  # total no of entries
            division_size = total_entries_size / self.number_of_data_1  # division size
            if math.floor(division_size) != math.ceil(division_size):
                print("[ERROR] division_size IS NOT AN INTEGER !!! ")
                division_size = int(math.ceil(division_size))

            else:
                division_size = int(math.ceil(division_size))

            print(
                f"Number of IO entries: {self.number_of_data_1} | "
                f"Each IO entry size: {self.total_avl_data_size / self.number_of_data_1} | "
                f"Total IO size: {self.total_avl_data_size}")

            for i in range(0, total_entries_size, division_size):
                self.avl_entries.append(avl_data_entries[i:i + division_size])  # splitting into chunks

            self.d_time_local = unixToLocal(self.d_time_unix)  # device time local

            for entry in self.avl_entries:
                try:
                    self.readAvlDataEntry(entry)
                    is_gps_data_valid = self.isGpsDataValid()
                    is_temperature_valid = self.isTemperatureValid()
                    if is_temperature_valid & is_gps_data_valid:
                        yield self.getAvlData()
                    else:
                        yield ERROR_VALUE
                except:
                    print("[ERROR] | Somethings went wrong in looping through avl entries")
                    yield ERROR_VALUE

        else:
            yield ERROR_VALUE

    def readAvlDataEntry(self, entry):
        """
        AVL DATA entry
                without preamble, data_field, codec_id, number_of_data_1 at the beginning 
                and without number_of_data_2 and crc at the end
        """
        self.d_time_unix = int(entry[0:16], 16)  # timestamp from device
        self.priority = int(entry[16:18], 16)  # device data priority

        # GPS element
        self.lon = int(entry[18:26], 16)  # longitude
        self.lat = int(entry[26:34], 16)  # latitude
        lon_minus = int.from_bytes(bytes.fromhex(entry[18:20]), byteorder="big", signed=False) & 0x80
        lat_minus = int.from_bytes(bytes.fromhex(entry[26:28]), byteorder="big", signed=False) & 0x80
        if lon_minus == 1:
            self.lon = - self.lon
        if lat_minus == 1:
            self.lat = -self.lat
        self.alt = int(entry[34:38], 16)  # altitude
        self.angle = int(entry[38:42], 16)  # angle
        self.satellites = int(entry[42:44], 16)  # no of satellites
        self.speed = int(entry[44:48], 16)  # speed

        # IO element
        io_start = Avl.timestamp + Avl.priority + Avl.gps_element
        self.avl_io_raw = entry[io_start:]
        self.decoded_io = io_elements.decode(self.avl_io_raw)  # decoded avl data
        self.convert_dallas_temperature()

    def getAvlData(self):
        data = {
            "received_time": readTime(),
            "data_field_len": self.data_field_len,
            "codecId": self.codecId,
            "number_of_data_1": self.number_of_data_1,
            "number_of_data_2": self.number_of_data_2,
            "crc-16": self.crc_16,
            "d_time_local": self.d_time_local,
            "d_time_unix": self.d_time_unix,
            "priority": self.priority,
            "lon": self.lon,
            "lat": self.lat,
            "alt": self.alt,
            "angle": self.angle,
            "satellites": self.satellites,
            "speed": self.speed,
            "io_data": self.decoded_io
        }
        return data

    def getRawData(self):
        return self.raw_data

    def convert_dallas_temperature(self):
        try:
            # negative values? two's complement.
            self.decoded_io['Dallas Temperature 1'] = self.decoded_io['Dallas Temperature 1'] / 10

        except:
            print("[ERROR] | Dallas Temperature 1 convert fail.")

    def isGpsDataValid(self):
        """
        Speed will be 0x0000 if GPS data is invalid.
        """
        if self.speed == 0:
            self.lat = ERROR_VALUE  # 458041616
            self.lon = ERROR_VALUE  # 159412116
            self.angle = ERROR_VALUE  # 122
            self.satellites = ERROR_VALUE  # 9
            return False
        else:
            return True

    def isTemperatureValid(self):
        """
        Degrees ( °C ), -55 - +115,
           if 850 – Sensor not ready
           if 2000 – Value read error
           if 3000 – Not connected
           if 4000 – ID failed
           if 5000 – same as 850
       """
        temperature = self.decoded_io['Dallas Temperature 1']
        if (temperature < -55) | (temperature > 115):
            return False
        else:
            return True


if __name__ == "__main__":

    with open('data/raw_hex.txt', 'r') as r:
        lines = r.readlines()

    for packet in lines:
        avl = AvlDecoder()
        results = avl.decodeAVL(packet)
        valid_res_generator = [p for p in results if p != ERROR_VALUE]
        for res in valid_res_generator:
            res['imei'] = '352093084336436'
            with open('data/decoded_avl.txt', 'a') as a:
                a.write(json.dumps(res))
                a.write('\n')
        with open('data/decoded_avl.txt', 'a') as a:
            a.write('\n=========NEW AVL_DATA_PACKET=========\n')
