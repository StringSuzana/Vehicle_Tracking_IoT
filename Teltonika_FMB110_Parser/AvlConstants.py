from dataclasses import dataclass


@dataclass
class Avl:
    device_imei_length = "\x0f"  # 15

    preamble = 4 * 2
    data_field = 4 * 2
    codec_id = 1 * 2
    number_of_data_1 = 1 * 2
    timestamp = 8 * 2
    priority = 1 * 2
    gps_element = 15 * 2
    number_of_data_2 = 1 * 2
    crc16 = 4 * 2

    data_field_len_start = preamble
    data_field_len_end = preamble + data_field

    codec_id_start = preamble + data_field
    codec_id_end = preamble + data_field + codec_id

    number_of_data_1_start = preamble + data_field + codec_id
    number_of_data_1_end = preamble + data_field + codec_id + number_of_data_1

    data_start = preamble + data_field + codec_id + number_of_data_1
    data_end = number_of_data_2 + crc16

    number_of_data_2_start = -crc16 - number_of_data_2
    number_of_data_2_end = -crc16

    crc_16_start = -crc16
