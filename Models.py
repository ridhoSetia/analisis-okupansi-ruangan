from dataclasses import dataclass

@dataclass
class SensorReading:
    timestamp: str
    temperature: float
    humidity: float
    light: int
    co_2: float
    humidity_ratio: float
    occupancy: int

    def __post_init__(self):
        if not 0 <= self.humidity <= 100:
            raise ValueError("Kelembapan harus rentang 0 - 100%")
        if self.co_2 < 400:
            raise ValueError("Nilai CO2 tidak valid")
        
    def is_occupied(self) -> bool:
        return self.occupancy == 1
    
    def is_abnormal_co2(self) -> bool:
        return self.co_2 > 1000 # indikasi ventilasi buruk