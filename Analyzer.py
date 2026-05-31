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
    Menganalisis seberapa sering lampu (sensor light) menyala ketika ruangan 
    sebenarnya kosong (pemborosan energi).
    """
    def analyze(self) -> Dict[str, Any]:
        if not self._data:
            return {}
        
        # Data ketika lampu menyala (light > 0)
        light_on_data = [row for row in self._data if row.light > 0]
        light_on_occupied = [row for row in light_on_data if row.is_occupied()]
        light_on_vacant = [row for row in light_on_data if not row.is_occupied()]
        
        # Data ketika ruangan kosong
        vacant_data = [row for row in self._data if not row.is_occupied()]
        light_on_when_vacant = [row for row in vacant_data if row.light > 0]
        
        # Perhitungan metrik
        total_light_on = len(light_on_data)
        wasted_energy_count = len(light_on_when_vacant)
        
        # Estimasi pemborosan energi (asumsi setiap 100 lux setara 10 Watt)
        avg_light_when_vacant = sum(row.light for row in light_on_when_vacant) / len(light_on_when_vacant) if light_on_when_vacant else 0
        estimated_wattage_wasted = (avg_light_when_vacant / 100) * 10 if avg_light_when_vacant > 0 else 0
        
        return {
            "total_light_on_events": total_light_on,
            "light_on_when_occupied": len(light_on_occupied),
            "light_on_when_vacant": wasted_energy_count,
            "waste_percentage": (wasted_energy_count / total_light_on * 100) if total_light_on > 0 else 0,
            "avg_light_intensity_when_vacant_lux": round(avg_light_when_vacant, 2),
            "estimated_wattage_wasted_per_event": round(estimated_wattage_wasted, 2),
            "recommendation": "PERINGATAN! Matikan lampu otomatis saat ruangan kosong." if wasted_energy_count > total_light_on * 0.3 else "Efisiensi energi cukup baik.",
            "status": "BOROS" if wasted_energy_count > total_light_on * 0.3 else "EFISIEN"
        }