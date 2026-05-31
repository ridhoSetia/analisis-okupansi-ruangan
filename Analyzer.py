from Models import SensorReading
from typing import List
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseIoTAnalyzer(ABC):
    def __init__(self, data: List[SensorReading]):
        self._data = data

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """
        Method abstrak yang WAJIB diimplementasikan oleh semua subclass turunan.
        Jika subclass tidak mengimplementasikan method ini, Python akan error.
        """
        pass

    def get_summary(self) -> Dict[str, Any]:
        """
        Concrete Method (Method biasa). 
        Fungsi ini tidak abstrak, artinya bisa langsung di-reuse (digunakan bersama) 
        oleh semua subclass tanpa harus menulis ulang kodenya.
        """
        total = len(self._data)

        # kalau itu occupied, nanti outputnya true/1
        occupied = sum(row.is_occupied() for row in self._data)
        return {
            "total_records": total,
            "occupied_count": occupied,
            "occupancy_rate": (occupied / total) if total > 0 else 0.0
        }

class CO2Analyzer(BaseIoTAnalyzer):
    """
    Fokus menganalisis korelasi lonjakan CO2 dengan kehadiran manusia di dalam ruangan.
    """
    def analyze(self) -> Dict[str, Any]:
        base_summary = self.get_summary()

        occupied_data = [row for row in self._data if row.is_occupied()]
        avg_co2_occupied = (sum(row.co_2 for row in occupied_data) / len(occupied_data) if occupied_data else 0.0)

        return {
            "overall_occupancy": base_summary,
            "average_co2_when_occupied": avg_co2_occupied,
            "status": "Ventilasi Buruk" if avg_co2_occupied > 1000 else "Ventilasi Baik"
        }

class ThermodynamicAnalyzer(BaseIoTAnalyzer):
    """
    Menganalisis seberapa besar pengaruh suhu badan manusia terhadap temperature dan humidity ruangan.
    """
    def analyze(self) -> Dict[str, Any]:
        if not self._data:
            return {}
            
        max_temp = max(r.temperature for r in self._data)
        min_temp = min(r.temperature for r in self._data)
        avg_humidity = sum(r.humidity for r in self._data) / len(self._data)
        
        return {
            "temperature_range": {"max": max_temp, "min": min_temp},
            "average_humidity": avg_humidity
        }

class EnergyEfficiencyAnalyzer(BaseIoTAnalyzer):
    """
    Menganalisis seberapa sering lampu (sensor light) menyala ketika ruangan sebenarnya kosong (pemborosan energi).
    """