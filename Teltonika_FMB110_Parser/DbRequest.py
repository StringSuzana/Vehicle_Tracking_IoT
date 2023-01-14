import psycopg2
import os

from datetime import datetime


class DbRequest:
    def __init__(self):
        self.post_url = ""
        self.connection = psycopg2.connect(
            host=os.environ.get("SMARTINO_DB_HOST"),
            port=os.environ.get("SMARTINO_DB_PORT"),
            user=os.environ.get("SMARTINO_DB_USER"),
            password=os.environ.get("SMARTINO_DB_PWD"),
            database=os.environ.get("SMARTINO_DB_NAME")
        )

        self.cursor = self.connection.cursor()

    def save(self, data):
        print("data:", data)
        self.avlDataToDbFormat(data)

    def avlDataToDbFormat(self, avl):
        time = datetime.now()
        time_formatted = time.strftime("%Y-%m-%d %H:%M:%S")
        coordinate_precision = 10000000

        db_vehicleType_table = {
            "id": 10,
            "name": "CAR"
        }
        db_vehicle_table = {
            "imei": avl['imei'],
            "label": avl['imei'],
            "vehicle_type": 10,
            "registration": "ZG 000 ZG"
        }
        db_conditions_table = {
            "lat": str(avl['lat'] / coordinate_precision),
            "long": str(avl['lon'] / coordinate_precision),
            "speed": int(avl['speed']),
            "dallas_temperature_1": (avl['io_data'].get('Dallas Temperature 1') or 0),
            "gsm_signal": int(avl['io_data'].get('GSM Signal') or 0),
            "trip_odometer": avl['io_data'].get('Trip Odometer'),
            "total_odometer": avl['io_data'].get('Total Odometer'),
            "time": avl['d_time_local'],  # avl['received_time'],
            "vehicle_id": avl['imei'],
            # "external_voltage": (avl['io_data'].get('External Voltage') or 0) / 1000,
        }

        print(db_conditions_table)

        # self.cursor.execute("INSERT INTO vehicleType (id, name) VALUES (%(id)s, %(name)s)", db_vehicleType_table)
        # Insert data into the vehicle table
        # self.cursor.execute(
        #    "INSERT INTO vehicle (imei, label, vehicle_type, registration) VALUES (%(imei)s, %(label)s, %(vehicle_type)s,
        #    %(registration)s)", db_vehicle_table)

        self.cursor.execute(
            "INSERT INTO conditions (lat, long, speed, dallas_temperature_1, gsm_signal, trip_odometer, total_odometer, time, vehicle_id)"
            " VALUES "
            "(%(lat)s, %(long)s, %(speed)s, %(dallas_temperature_1)s, %(gsm_signal)s, %(trip_odometer)s, %(total_odometer)s,"
            " %(time)s, %(vehicle_id)s)",
            db_conditions_table)

        self.connection.commit()

    def closeConnection(self):
        self.cursor.close()
        self.connection.close()


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

    db = DbRequest()
    db.save(data)
