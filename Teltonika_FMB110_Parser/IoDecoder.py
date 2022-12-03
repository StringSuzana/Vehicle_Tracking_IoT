from AvlIds import AvlIds
from dataclasses import dataclass
from enum import Enum


class IoResult(Enum):
    END = 0
    CONTINUE = 1


@dataclass
class Element:
    name: str
    value: int = 0
    length: int = 1 * 2  # 1 byte == 2 characters
    length_in_bytes = length / 2


class IoElements:
    def __init__(self):
        self.io_data_hexstring = None
        '''
        event io                    | 1 byte
        num of total io             | 1 byte
        
            num of 1byte io         | 1 byte
                nth 1byte io id     | 1 byte    |---One IO packet---|
                nth 1byte io value  | 1 byte    |-------------------|
                ....
            num of 2byte io         | 1 byte
                nth 2byte io id     | 1 byte   |---One IO packet---|
                nth 2byte io value  | 2 byte   |-------------------|
                ....
            num of 4byte io         | 1 byte
                nth 4byte io id     | 1 byte   |---One IO packet---|
                nth 4byte io value  | 4 byte   |-------------------|
                ....
            num of 8byte io         | 1 byte
                nth 8byte io id     | 1 byte   |---One IO packet---|
                nth 8byte io value  | 8 byte   |-------------------|
                .... 
        '''
        self.event_io = Element(name="event_io_id", length=1 * 2)
        self.num_of_total_io = Element(name="num_of_total_io", length=1 * 2)
        self.nth_io_id = Element(name="io_id", length=1 * 2)

        self.count_of_1_byte_io = Element(name="count_of_1_byte_io", length=1 * 2)
        self._1byte_io_value = Element(name="_1byte_io_value", length=1 * 2)
        self._1byte_io_values = []

        self.count_of_2_byte_io = Element(name="count_of_2_byte_io", length=1 * 2)
        self._2byte_io_value = Element(name="_2byte_io_value_len", length=2 * 2)
        self._2byte_io_values = []

        self.count_of_4_byte_io = Element(name="count_of_4_byte_io", length=1 * 2)
        self._4byte_io_value = Element(name="_2byte_io_value_len", length=4 * 2)
        self._4byte_io_values = []

        self.count_of_8_byte_io = Element(name="count_of_8_byte_io", length=1 * 2)
        self._8byte_io_value = Element(name="_2byte_io_value_len", length=8 * 2)
        self._8byte_io_values = []

        self.io_result = {}

    def decode(self, io_data_hexstring):
        self.io_data_hexstring = io_data_hexstring

        self.read_event_io_id()
        self.read_num_of_total_io()

        if self.read_1byte_elements() == IoResult.END:
            return AvlIds().idToAvl(self.io_result)

        if self.read_2byte_elements() == IoResult.END:
            return AvlIds().idToAvl(self.io_result)

        if self.read_4byte_elements() == IoResult.END:
            return AvlIds().idToAvl(self.io_result)

        if self.read_8byte_elements() == IoResult.END:
            return AvlIds().idToAvl(self.io_result)

    def read_event_io_id(self):
        self.event_io.value = int(self.io_data_hexstring[0:self.event_io.length], 16)
        if self.event_io.value != 0:
            self.io_result[self.event_io.value] = 'triggered_event'

    def read_num_of_total_io(self):
        self.num_of_total_io.value = int(self.io_data_hexstring[2:4], 16)
        print(f" | Number of total IOs {self.num_of_total_io.value}")

    def read_1byte_elements(self) -> IoResult:
        # io_data_hexstring = event_io (2bytes) | num_of_total_io (2bytes) | [ count_of_1_byte_io (2bytes) ] | ...
        num_start = self.event_io.length + self.num_of_total_io.length
        num_end = self.event_io.length + self.num_of_total_io.length + self.count_of_1_byte_io.length

        self.count_of_1_byte_io.value = int(self.io_data_hexstring[num_start:num_end], 16)

        one_1byte_packet_length = self.nth_io_id.length + self._1byte_io_value.length

        self.whole_1byte_io_size = self.count_of_1_byte_io.value * one_1byte_packet_length
        _1byte_ios_start = num_end
        _1byte_ios_end = _1byte_ios_start + self.whole_1byte_io_size

        n1s_data = self.io_data_hexstring[_1byte_ios_start:_1byte_ios_end]

        self._1byte_io_values = self.decode_n_byte_io(io_data=n1s_data,
                                                      one_io_length=one_1byte_packet_length)
        self.io_result['n1'] = self._1byte_io_values

        if self.count_of_1_byte_io.value == self.num_of_total_io.value:
            return IoResult.END
        else:
            return IoResult.CONTINUE

    def read_2byte_elements(self) -> IoResult:
        num_start = (self.event_io.length +
                     self.num_of_total_io.length +
                     self.count_of_1_byte_io.length +
                     self.whole_1byte_io_size)
        num_end = num_start + self.count_of_2_byte_io.length

        self.count_of_2_byte_io.value = int(self.io_data_hexstring[num_start:num_end], 16)

        one_2byte_packet_length = self.nth_io_id.length + self._2byte_io_value.length
        self.whole_2byte_io_size = self.count_of_2_byte_io.value * one_2byte_packet_length
        _2byte_ios_start = num_end
        _2byte_ios_end = _2byte_ios_start + self.whole_2byte_io_size

        n2s_data = self.io_data_hexstring[_2byte_ios_start:_2byte_ios_end]

        self._2byte_io_values = self.decode_n_byte_io(io_data=n2s_data,
                                                      one_io_length=one_2byte_packet_length)
        self.io_result['n2'] = self._2byte_io_values

        if self.count_of_1_byte_io.value + self.count_of_2_byte_io.value == self.num_of_total_io.value:
            return IoResult.END
        else:
            return IoResult.CONTINUE

    def read_4byte_elements(self) -> IoResult:
        num_start = (self.event_io.length +
                     self.num_of_total_io.length +
                     self.count_of_1_byte_io.length +
                     self.whole_1byte_io_size +
                     self.count_of_2_byte_io.length +
                     self.whole_2byte_io_size)
        num_end = num_start + self.count_of_4_byte_io.length
        self.count_of_4_byte_io.value = int(self.io_data_hexstring[num_start:num_end], 16)

        one_4byte_packet_length = self.nth_io_id.length + self._4byte_io_value.length
        self.whole_4byte_io_size = self.count_of_4_byte_io.value * one_4byte_packet_length
        _4byte_ios_start = num_end
        _4byte_ios_end = _4byte_ios_start + self.whole_4byte_io_size

        n4s_data = self.io_data_hexstring[_4byte_ios_start:_4byte_ios_end]

        self._4byte_io_values = self.decode_n_byte_io(io_data=n4s_data,
                                                      one_io_length=one_4byte_packet_length)
        self.io_result['n4'] = self._4byte_io_values

        if (self.count_of_1_byte_io.value +
            self.count_of_2_byte_io.value +
            self.count_of_4_byte_io.value) \
                == self.num_of_total_io.value:
            return IoResult.END
        else:
            return IoResult.CONTINUE

    def read_8byte_elements(self) -> IoResult:
        num_start = (self.event_io.length +
                     self.num_of_total_io.length +
                     self.count_of_1_byte_io.length +
                     self.whole_1byte_io_size +
                     self.count_of_2_byte_io.length +
                     self.whole_2byte_io_size +
                     self.count_of_4_byte_io.length +
                     self.whole_4byte_io_size)
        num_end = num_start + self.count_of_8_byte_io.length
        self.count_of_8_byte_io.value = int(self.io_data_hexstring[num_start:num_end], 16)

        one_8byte_packet_length = self.nth_io_id.length + self._8byte_io_value.length
        self.whole_8byte_io_size = self.count_of_8_byte_io.value * one_8byte_packet_length
        _8byte_ios_start = num_end
        _8byte_ios_end = _8byte_ios_start + self.whole_8byte_io_size

        n8s_data = self.io_data_hexstring[_8byte_ios_start:_8byte_ios_end]

        self._8byte_io_values = self.decode_n_byte_io(io_data=n8s_data,
                                                      one_io_length=one_8byte_packet_length)
        self.io_result['n8'] = self._8byte_io_values

        return IoResult.END

    def decode_n_byte_io(self, io_data, one_io_length) -> dict:
        if io_data == '':
            return {}
        n_bytes_io = {}
        for i in range(0, len(io_data), one_io_length):
            nth_io_id = int(io_data[i:i + self.nth_io_id.length], 16)
            nth_io_val = int(io_data[i + self.nth_io_id.length: i + one_io_length], 16)
            n_bytes_io[int(nth_io_id)] = nth_io_val
        return n_bytes_io


if __name__ == '__main__':
    n_data = b'fa0b04150545010101fa010242328418000204f10000558ec70000000010002aa8374800000076014cf80316a117f7ff28'
    io = IoElements()
    print(io.decode(n_data))
