import csv
from Models import SensorReading
from typing import List

class SensorRepository:
    def __init__(self):
        self._data: List[SensorReading] = []

    def load_csv(self, file_path: str) -> str:
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Setiap baris di CSV di mapping (diubah) menjadi objek Model
                reading = SensorReading(
                    timestamp=row["Date"],
                    temperature=float(row["Temperature"]),
                    humidity=float(row["Humidity"]),
                    light=float(row["Light"]),
                    co_2=float(row["CO2"]),
                    humidity_ratio=float(row["HumidityRatio"]),
                    occupancy=int(row["Occupancy"])
                )
                
                # Objek tersebut ditambahkan ke dalam self._data
                self._data.append(reading)
                
        # Mengembalikan jumlah total data yang berhasil dimuat
        return len(self._data)

    def get_all(self) -> List[SensorReading]:
        return self._data
    
    def get_occupied(self) -> bool:
        return [row for row in self._data if row.is_occupied()]