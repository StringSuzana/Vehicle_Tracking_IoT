import psycopg2

# TIMESCALE
CONNECTION = "postgres://username:password@host:port/dbname"


class DbRequest:
    def __init__(self):
        self.post_url = ""

    def save(self, data) -> str:
        print("io", data)
        self.avlDataToDbFormat(data)
        return "Database Response"

    def avlDataToDbFormat(self, avl):
        coordinate_precision = 10000000
        db_format = {
            "imei": avl['imei'],
            "label": avl['imei'],
            "conditions": {
                "lat": str(avl['lat'] / coordinate_precision),
                "long": str(avl['lon'] / coordinate_precision),
                "speed": int(avl['speed']),
                "dallas_temperature_1": (avl['io_data'].get('Dallas Temperature 1') or 0),
                "gsp_signal": int(avl['io_data'].get('GSM Signal') or 0),
                "trip_odometer": avl['io_data'].get('Trip Odometer'),
                "total_odometer": avl['io_data'].get('Total Odometer'),
                "time": avl['received_time'],
                "imei": avl['imei'],
                # "external_voltage": (avl['io_data'].get('External Voltage') or 0) / 1000,
            }
        }
        print(db_format)
        return db_format


if __name__ == "__main__":
    data = {"received_time": "26/11/2022 19:32:31", "data_field_len": 1904, "codecId": 8, "number_of_data_1": 13,
            "number_of_data_2": 13, "crc-16": 29091, "d_time_local": "1970-01-01 01:00:00",
            "d_time_unix": 1668872834000, "priority": 1, "lon": 129413500, "lat": 418042183, "alt": 119, "angle": 255,
            "satellites": 8, "speed": 0,
            "io_data": {"triggered_event": "Dallas Temperature 1", "GSM Signal": 5, "GNSS Status": 1,
                        "Digital Input 1": 1, "Trip": 1, "External Voltage": 16162, "Speed": 0,
                        "Active GSM Operator": 21902, "Trip Odometer": 0, "Total Odometer": 2795575,
                        "Dallas Temperature 1": 90, "Dallas Temperature ID 1": 17871152627483934504},
            "imei": "352093084336436"}

    a = DbRequest()
    ready = a.save(data)
    print(ready)
