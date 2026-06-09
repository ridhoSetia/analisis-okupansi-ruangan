"""
Unit Testing - Smart Building Sensor Analytics
Dataset: UCI Occupancy Detection

Menguji: Models, Repository, dan Analyzer (CO2, Thermodinamic, EnergyEfficiency)
Jalankan dengan: pytest test_smart_building.py -v
"""

import pytest
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO
import csv


# ─────────────────────────────────────────────
# FIXTURES - Data sampel untuk semua test
# ─────────────────────────────────────────────

def make_reading(
    timestamp="2015-02-04 17:51:00",
    temperature=23.18,
    humidity=27.27,
    light=426.0,
    co_2=721.25,
    humidity_ratio=0.00479,
    occupancy=1
):
    """Helper factory untuk membuat SensorReading dengan nilai default."""
    from Models import SensorReading
    return SensorReading(
        timestamp=timestamp,
        temperature=temperature,
        humidity=humidity,
        light=light,
        co_2=co_2,
        humidity_ratio=humidity_ratio,
        occupancy=occupancy
    )


@pytest.fixture
def sample_occupied():
    """SensorReading saat ruangan terisi."""
    return make_reading(occupancy=1, co_2=900.0, light=500, temperature=24.0, humidity=30.0)


@pytest.fixture
def sample_vacant():
    """SensorReading saat ruangan kosong."""
    return make_reading(occupancy=0, co_2=450.0, light=0, temperature=20.0, humidity=25.0)


@pytest.fixture
def mixed_data():
    """List campuran data terisi dan kosong untuk test analyzer."""
    return [
        make_reading(occupancy=1, co_2=1100.0, light=500, temperature=25.0, humidity=55.0),
        make_reading(occupancy=1, co_2=900.0,  light=400, temperature=23.0, humidity=45.0),
        make_reading(occupancy=0, co_2=450.0,  light=300, temperature=20.0, humidity=30.0),
        make_reading(occupancy=0, co_2=420.0,  light=0,   temperature=19.0, humidity=28.0),
        make_reading(occupancy=1, co_2=800.0,  light=600, temperature=22.0, humidity=40.0),
    ]


# ═══════════════════════════════════════════════════════════
# TEST SUITE 1: Models.py — SensorReading
# ═══════════════════════════════════════════════════════════

class TestSensorReading:
    """Menguji encapsulation dan validasi data pada Models.SensorReading."""

    def test_create_valid_reading(self, sample_occupied):
        """SensorReading berhasil dibuat dengan nilai valid."""
        assert sample_occupied.temperature == 24.0
        assert sample_occupied.co_2 == 900.0
        assert sample_occupied.occupancy == 1

    def test_is_occupied_returns_true(self, sample_occupied):
        """is_occupied() harus True saat occupancy == 1."""
        assert sample_occupied.is_occupied() is True

    def test_is_occupied_returns_false(self, sample_vacant):
        """is_occupied() harus False saat occupancy == 0."""
        assert sample_vacant.is_occupied() is False

    def test_is_abnormal_co2_high(self):
        """is_abnormal_co2() harus True jika CO2 > 1000 ppm."""
        reading = make_reading(co_2=1200.0)
        assert reading.is_abnormal_co2() is True

    def test_is_abnormal_co2_normal(self, sample_occupied):
        """is_abnormal_co2() harus False jika CO2 <= 1000 ppm."""
        assert sample_occupied.is_abnormal_co2() is False

    def test_invalid_humidity_raises_error(self):
        """Kelembaban di luar 0–100 harus raise ValueError."""
        with pytest.raises(ValueError, match="Kelembapan"):
            make_reading(humidity=150.0)

    def test_invalid_co2_raises_error(self):
        """CO2 di bawah 400 ppm dianggap tidak valid."""
        with pytest.raises(ValueError, match="CO2"):
            make_reading(co_2=100.0)

    def test_boundary_humidity_zero(self):
        """Kelembaban 0% seharusnya valid (batas bawah)."""
        r = make_reading(humidity=0.0)
        assert r.humidity == 0.0

    def test_boundary_humidity_hundred(self):
        """Kelembaban 100% seharusnya valid (batas atas)."""
        r = make_reading(humidity=100.0)
        assert r.humidity == 100.0


# ═══════════════════════════════════════════════════════════
# TEST SUITE 2: Repository.py — SensorRepository
# ═══════════════════════════════════════════════════════════

class TestSensorRepository:
    """Menguji SensorRepository: load CSV dan pengambilan data."""

    CSV_CONTENT = (
        "Date,Temperature,Humidity,Light,CO2,HumidityRatio,Occupancy\n"
        "2015-02-04 17:51:00,23.18,27.27,426.0,721.25,0.00479,1\n"
        "2015-02-04 17:52:00,23.15,27.29,429.0,714.0,0.00480,0\n"
        "2015-02-04 17:53:00,23.20,27.30,431.0,730.0,0.00481,1\n"
    )

    def test_load_csv_returns_correct_count(self):
        """load_csv() harus mengembalikan jumlah baris yang benar."""
        from Repository import SensorRepository
        repo = SensorRepository()
        with patch("builtins.open", mock_open(read_data=self.CSV_CONTENT)):
            count = repo.load_csv("dummy_path.csv")
        assert count == 3

    def test_get_all_returns_list(self):
        """get_all() harus mengembalikan list SensorReading."""
        from Repository import SensorRepository
        repo = SensorRepository()
        with patch("builtins.open", mock_open(read_data=self.CSV_CONTENT)):
            repo.load_csv("dummy_path.csv")
        result = repo.get_all()
        assert isinstance(result, list)
        assert len(result) == 3

    def test_get_all_parses_temperature(self):
        """Nilai temperature dari CSV harus diparsing dengan benar."""
        from Repository import SensorRepository
        repo = SensorRepository()
        with patch("builtins.open", mock_open(read_data=self.CSV_CONTENT)):
            repo.load_csv("dummy_path.csv")
        first = repo.get_all()[0]
        assert first.temperature == pytest.approx(23.18)

    def test_get_occupied_filters_correctly(self):
        """get_occupied() hanya boleh mengembalikan data occupancy == 1."""
        from Repository import SensorRepository
        repo = SensorRepository()
        with patch("builtins.open", mock_open(read_data=self.CSV_CONTENT)):
            repo.load_csv("dummy_path.csv")
        occupied = repo.get_occupied()
        assert all(r.occupancy == 1 for r in occupied)

    def test_initial_data_is_empty(self):
        """Sebelum load_csv dipanggil, get_all() harus mengembalikan list kosong."""
        from Repository import SensorRepository
        repo = SensorRepository()
        assert repo.get_all() == []


# ═══════════════════════════════════════════════════════════
# TEST SUITE 3: Analyzer.py — BaseIoTAnalyzer & Subclass
# ═══════════════════════════════════════════════════════════

class TestBaseAnalyzer:
    """Menguji abstraksi dan concrete method pada BaseIoTAnalyzer."""

    def test_base_analyzer_is_abstract(self):
        """BaseIoTAnalyzer tidak boleh diinstansiasi langsung (ABC)."""
        from Analyzer import BaseIoTAnalyzer
        with pytest.raises(TypeError):
            BaseIoTAnalyzer([])

    def test_get_summary_total_records(self, mixed_data):
        """get_summary() harus mengembalikan total_records yang benar."""
        from Analyzer import CO2Analyzer
        analyzer = CO2Analyzer(mixed_data)
        summary = analyzer.get_summary()
        assert summary["total_records"] == 5

    def test_get_summary_occupied_count(self, mixed_data):
        """get_summary() harus menghitung occupied_count dengan benar."""
        from Analyzer import CO2Analyzer
        analyzer = CO2Analyzer(mixed_data)
        summary = analyzer.get_summary()
        assert summary["occupied_count"] == 3

    def test_get_summary_occupancy_rate(self, mixed_data):
        """occupancy_rate harus 3/5 = 0.6 dari data campuran."""
        from Analyzer import CO2Analyzer
        analyzer = CO2Analyzer(mixed_data)
        summary = analyzer.get_summary()
        assert summary["occupancy_rate"] == pytest.approx(0.6)

    def test_get_summary_empty_data(self):
        """get_summary() dengan data kosong tidak boleh raise error, rate = 0."""
        from Analyzer import CO2Analyzer
        analyzer = CO2Analyzer([])
        summary = analyzer.get_summary()
        assert summary["occupancy_rate"] == 0.0


# ═══════════════════════════════════════════════════════════
# TEST SUITE 4: CO2Analyzer
# ═══════════════════════════════════════════════════════════

class TestCO2Analyzer:
    """Menguji CO2Analyzer: analisis korelasi CO2 dengan occupancy."""

    def test_analyze_returns_required_keys(self, mixed_data):
        """analyze() harus mengembalikan dict dengan key yang diharapkan."""
        from Analyzer import CO2Analyzer
        result = CO2Analyzer(mixed_data).analyze()
        assert "overall_occupancy" in result
        assert "average_co2_when_occupied" in result
        assert "status" in result

    def test_average_co2_when_occupied(self, mixed_data):
        """Rata-rata CO2 saat occupied harus dihitung dari data occupied saja."""
        from Analyzer import CO2Analyzer
        result = CO2Analyzer(mixed_data).analyze()
        # occupied: 1100, 900, 800 → rata-rata = 933.33
        expected = (1100.0 + 900.0 + 800.0) / 3
        assert result["average_co2_when_occupied"] == pytest.approx(expected)

    def test_status_ventilasi_buruk(self):
        """Status 'Ventilasi Buruk' jika rata-rata CO2 > 1000 ppm."""
        from Analyzer import CO2Analyzer
        data = [make_reading(occupancy=1, co_2=1500.0)]
        result = CO2Analyzer(data).analyze()
        assert result["status"] == "Ventilasi Buruk"

    def test_status_ventilasi_baik(self, sample_occupied):
        """Status 'Ventilasi Baik' jika rata-rata CO2 <= 1000 ppm."""
        from Analyzer import CO2Analyzer
        result = CO2Analyzer([sample_occupied]).analyze()
        assert result["status"] == "Ventilasi Baik"

    def test_no_occupied_data_returns_zero_co2(self, sample_vacant):
        """Jika tidak ada data occupied, avg CO2 harus 0."""
        from Analyzer import CO2Analyzer
        result = CO2Analyzer([sample_vacant]).analyze()
        assert result["average_co2_when_occupied"] == 0.0


# ═══════════════════════════════════════════════════════════
# TEST SUITE 5: ThermodynamicAnalyzer
# ═══════════════════════════════════════════════════════════

class TestThermodynamicAnalyzer:
    """Menguji ThermodynamicAnalyzer: rentang suhu dan kelembaban rata-rata."""

    def test_temperature_range(self, mixed_data):
        """Rentang suhu min-max harus tepat."""
        from Analyzer import ThermodynamicAnalyzer
        result = ThermodynamicAnalyzer(mixed_data).analyze()
        assert result["temperature_range"]["min"] == pytest.approx(19.0)
        assert result["temperature_range"]["max"] == pytest.approx(25.0)

    def test_average_humidity(self, mixed_data):
        """Rata-rata kelembaban harus dihitung dari semua data."""
        from Analyzer import ThermodynamicAnalyzer
        result = ThermodynamicAnalyzer(mixed_data).analyze()
        expected = (55.0 + 45.0 + 30.0 + 28.0 + 40.0) / 5
        assert result["average_humidity"] == pytest.approx(expected)

    def test_empty_data_returns_empty_dict(self):
        """analyze() dengan data kosong harus mengembalikan dict kosong."""
        from Analyzer import ThermodynamicAnalyzer
        result = ThermodynamicAnalyzer([]).analyze()
        assert result == {}

    def test_single_record(self):
        """Dengan satu rekaman, min == max == nilai suhu itu sendiri."""
        from Analyzer import ThermodynamicAnalyzer
        data = [make_reading(temperature=22.5)]
        result = ThermodynamicAnalyzer(data).analyze()
        assert result["temperature_range"]["min"] == pytest.approx(22.5)
        assert result["temperature_range"]["max"] == pytest.approx(22.5)


# ═══════════════════════════════════════════════════════════
# TEST SUITE 6: EnergyEfficiencyAnalyzer
# ═══════════════════════════════════════════════════════════

class TestEnergyEfficiencyAnalyzer:
    """Menguji EnergyEfficiencyAnalyzer: deteksi pemborosan lampu."""

    def test_analyze_returns_required_keys(self, mixed_data):
        """analyze() harus mengembalikan semua key yang diharapkan."""
        from Analyzer import EnergyEfficiencyAnalyzer
        result = EnergyEfficiencyAnalyzer(mixed_data).analyze()
        for key in ["total_light_on_events", "light_on_when_occupied",
                    "light_on_when_vacant", "waste_percentage",
                    "status", "recommendation"]:
            assert key in result

    def test_status_boros(self):
        """Status 'BOROS' jika >30% lampu menyala saat ruangan kosong."""
        from Analyzer import EnergyEfficiencyAnalyzer
        data = [
            make_reading(occupancy=1, light=500),
            make_reading(occupancy=0, light=500),  # boros
            make_reading(occupancy=0, light=500),  # boros
            make_reading(occupancy=0, light=500),  # boros
        ]
        result = EnergyEfficiencyAnalyzer(data).analyze()
        assert result["status"] == "BOROS"

    def test_status_efisien(self):
        """Status 'EFISIEN' jika pemborosan lampu <= 30%."""
        from Analyzer import EnergyEfficiencyAnalyzer
        data = [
            make_reading(occupancy=1, light=500),
            make_reading(occupancy=1, light=400),
            make_reading(occupancy=1, light=300),
            make_reading(occupancy=0, light=0),    # lampu mati — tidak boros
        ]
        result = EnergyEfficiencyAnalyzer(data).analyze()
        assert result["status"] == "EFISIEN"

    def test_waste_percentage_calculation(self):
        """Persentase pemborosan: 1 boros dari 2 lampu menyala = 50%."""
        from Analyzer import EnergyEfficiencyAnalyzer
        data = [
            make_reading(occupancy=1, light=500),
            make_reading(occupancy=0, light=500),
        ]
        result = EnergyEfficiencyAnalyzer(data).analyze()
        assert result["waste_percentage"] == pytest.approx(50.0)

    def test_no_light_on_events(self):
        """Jika semua lampu mati, waste_percentage harus 0."""
        from Analyzer import EnergyEfficiencyAnalyzer
        data = [
            make_reading(occupancy=0, light=0),
            make_reading(occupancy=1, light=0),
        ]
        result = EnergyEfficiencyAnalyzer(data).analyze()
        assert result["waste_percentage"] == 0.0

    def test_empty_data_returns_empty_dict(self):
        """analyze() dengan data kosong harus mengembalikan dict kosong."""
        from Analyzer import EnergyEfficiencyAnalyzer
        result = EnergyEfficiencyAnalyzer([]).analyze()
        assert result == {}