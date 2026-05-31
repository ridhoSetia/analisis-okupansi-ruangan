import os
import sys
from datetime import datetime
from typing import List

from Repository import SensorRepository
from Analyzer import CO2Analyzer, ThermodynamicAnalyzer, EnergyEfficiencyAnalyzer, BaseIoTAnalyzer
from Models import SensorReading
from Visualization import SensorVisualizer

class SmartBuildingAnalytics:
    """Kelas utama untuk menjalankan analisis Smart Building"""
    
    def __init__(self, csv_path: str = "dataset/data_.csv"):
        self.csv_path = csv_path
        self.repository = SensorRepository()
        self.data: List[SensorReading] = []
        self.load_status = False
        
    def load_data(self) -> bool:
        """Memuat data dari CSV"""
        print("\n" + "="*60)
        print("MEMUAT DATA SENSOR...")
        print("="*60)
        
        try:
            if not os.path.exists(self.csv_path):
                print(f"File tidak ditemukan: {self.csv_path}")
                print("   Pastikan file data_.csv berada di folder 'dataset/'")
                return False
                
            total = self.repository.load_csv(self.csv_path)
            self.data = self.repository.get_all()
            self.load_status = True
            
            print(f"Berhasil memuat {total} rekaman data sensor")
            print(f"Rentang waktu: {self.data[0].timestamp} s/d {self.data[-1].timestamp}")
            
            # Statistik dasar
            occupied = sum(1 for d in self.data if d.is_occupied())
            vacant = len(self.data) - occupied
            print(f"Ruangan Terisi: {occupied} ({occupied/len(self.data)*100:.1f}%)")
            print(f"Ruangan Kosong: {vacant} ({vacant/len(self.data)*100:.1f}%)")
            
            return True
        except Exception as e:
            print(f"Error saat memuat data: {e}")
            return False
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_menu(self):
        """Tampilkan menu utama"""
        self.clear_screen()
        print("="*60)
        print("   ANALISIS DATA SENSOR SMART BUILDING")
        print("="*60)
        print("   Deteksi Okupansi Ruangan menggunakan OOP")
        print("="*60)
        print("\nMENU UTAMA:\n")
        print("1. Analisis CO2 (Korelasi dengan Kehadiran Manusia)")
        print("2. Analisis Termodinamika (Pengaruh Suhu & Kelembaban)")
        print("3. Analisis Efisiensi Energi (Pemborosan Lampu)")
        print("4. Tampilkan Semua Analisis (Lengkap)")
        print("5. Visualisasi Data (Grafik & Chart)")
        print("6. Statistik Ringkas Dataset")
        print("7. Filter Data berdasarkan Waktu")
        print("0. Keluar Aplikasi")
        print("\n" + "="*60)
    
    def run_analyzer(self, analyzer_class, title: str):
        """Menjalankan analyzer dan menampilkan hasil"""
        if not self.load_status:
            print("\nData belum dimuat! Silakan load data terlebih dahulu.")
            input("\nTekan Enter untuk kembali...")
            return
        
        print("\n" + "="*60)
        print(f"{title}")
        print("="*60)
        
        analyzer = analyzer_class(self.data)
        result = analyzer.analyze()
        
        # Format output berdasarkan jenis analyzer
        if isinstance(analyzer, CO2Analyzer):
            print("\nHASIL ANALISIS CO2:")
            print(f"   ├─ Total Records: {result['overall_occupancy']['total_records']}")
            print(f"   ├─ Jumlah Terisi: {result['overall_occupancy']['occupied_count']}")
            print(f"   ├─ Tingkat Okupansi: {result['overall_occupancy']['occupancy_rate']*100:.1f}%")
            print(f"   ├─ Rata-rata CO2 saat terisi: {result['average_co2_when_occupied']:.1f} ppm")
            print(f"   └─ Status Ventilasi: {result['status']}")
            
            if result['average_co2_when_occupied'] > 1000:
                print("\n    REKOMENDASI: Tingkatkan sirkulasi udara!")
            else:
                print("\n    Ventilasi ruangan dalam kondisi baik.")
                
        elif isinstance(analyzer, ThermodynamicAnalyzer):
            print("\nHASIL ANALISIS TERMODINAMIKA:")
            print(f"   ├─ Rentang Suhu: {result['temperature_range']['min']:.1f}°C - {result['temperature_range']['max']:.1f}°C")
            print(f"   ├─ Rata-rata Kelembaban: {result['average_humidity']:.1f}%")
            print(f"   └─ Stabilitas Lingkungan: {'Baik' if result['temperature_range']['max'] - result['temperature_range']['min'] < 5 else 'Kurang stabil'}")
            
            # Deteksi anomali
            if result['average_humidity'] > 70:
                print("\n    REKOMENDASI: Kelembaban tinggi, gunakan dehumidifier.")
            elif result['average_humidity'] < 30:
                print("\n    REKOMENDASI: Udara terlalu kering, gunakan humidifier.")
                
        elif isinstance(analyzer, EnergyEfficiencyAnalyzer):
            print("\n HASIL ANALISIS EFISIENSI ENERGI:")
            print(f"   ├─ Total Lampu Menyala: {result['total_light_on_events']}x")
            print(f"   ├─ Lampu Menyala (Ruangan Terisi): {result['light_on_when_occupied']}x")
            print(f"   ├─ Lampu Menyala (Ruangan Kosong): {result['light_on_when_vacant']}x")
            print(f"   ├─ Persentase Pemborosan: {result['waste_percentage']:.1f}%")
            print(f"   ├─ Rata-rata Intensitas (Kosong): {result['avg_light_intensity_when_vacant_lux']} lux")
            print(f"   ├─ Estimasi Watt terbuang/event: {result['estimated_wattage_wasted_per_event']} Watt")
            print(f"   └─ Status: {result['status']}")
            
            if result['waste_percentage'] > 30:
                print("\n    REKOMENDASI: Pasang sensor gerak untuk kontrol lampu otomatis!")
                savings = result['waste_percentage'] * 0.7
                print(f"    Potensi hemat energi: ~{savings:.0f}% dari konsumsi lampu.")
        
        # Tampilkan summary juga
        summary = analyzer.get_summary()
        print("\nRINGKASAN DATASET:")
        print(f"   ├─ Total Rekaman: {summary['total_records']}")
        print(f"   ├─ Record Terisi: {summary['occupied_count']}")
        print(f"   └─ Tingkat Okupansi: {summary['occupancy_rate']*100:.1f}%")
        
        input("\nTekan Enter untuk kembali ke menu...")
    
    def show_all_analyses(self):
        """Menampilkan semua analisis sekaligus"""
        if not self.load_status:
            print("\nData belum dimuat!")
            input("\nTekan Enter untuk kembali...")
            return
        
        self.clear_screen()
        print("\n" + "="*60)
        print("LAPORAN LENGKAP ANALISIS SMART BUILDING")
        print("="*60)
        
        analyzers = [
            (CO2Analyzer, "ANALISIS KUALITAS UDARA (CO2)"),
            (ThermodynamicAnalyzer, "ANALISIS TERMODINAMIKA RUANGAN"),
            (EnergyEfficiencyAnalyzer, "ANALISIS EFISIENSI ENERGI")
        ]
        
        for analyzer_class, title in analyzers:
            print("\n" + "="*60)
            print(f"{title}")
            print("="*60)
            analyzer = analyzer_class(self.data)
            result = analyzer.analyze()
            
            if isinstance(analyzer, CO2Analyzer):
                print(f"   Rata-rata CO2 saat terisi: {result['average_co2_when_occupied']:.1f} ppm")
                print(f"   Status Ventilasi: {result['status']}")
            elif isinstance(analyzer, ThermodynamicAnalyzer):
                print(f"   Rentang Suhu: {result['temperature_range']['min']:.1f}°C - {result['temperature_range']['max']:.1f}°C")
                print(f"   Rata-rata Kelembaban: {result['average_humidity']:.1f}%")
            elif isinstance(analyzer, EnergyEfficiencyAnalyzer):
                print(f"   Pemborosan Energi: {result['waste_percentage']:.1f}%")
                print(f"   Status: {result['status']}")
                print(f"   Rekomendasi: {result['recommendation']}")
        
        # Export report ke file
        self.export_report(analyzers)
        
        input("\nTekan Enter untuk kembali...")
    
    def export_report(self, analyzers):
        """Export laporan ke file teks"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"smart_building_report_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("LAPORAN ANALISIS SMART BUILDING\n")
            f.write(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            for analyzer_class, title in analyzers:
                f.write(f"\n{title}\n")
                f.write("-"*40 + "\n")
                analyzer = analyzer_class(self.data)
                result = analyzer.analyze()
                
                for key, value in result.items():
                    if isinstance(value, dict):
                        for subkey, subval in value.items():
                            f.write(f"   {subkey}: {subval}\n")
                    else:
                        f.write(f"   {key}: {value}\n")
                f.write("\n")
        
        print(f"\nLaporan telah disimpan ke: {filename}")
    
    def show_statistics(self):
        """Menampilkan statistik ringkas dataset"""
        if not self.load_status:
            print("\nData belum dimuat!")
            input("\nTekan Enter untuk kembali...")
            return
        
        self.clear_screen()
        print("\n" + "="*60)
        print("STATISTIK RINGKAS DATASET")
        print("="*60)
        
        occupied_data = [d for d in self.data if d.is_occupied()]
        vacant_data = [d for d in self.data if not d.is_occupied()]
        
        print(f"\nOVERVIEW:")
        print(f"   ├─ Total Rekaman: {len(self.data)}")
        print(f"   ├─ Ruangan Terisi: {len(occupied_data)} ({len(occupied_data)/len(self.data)*100:.1f}%)")
        print(f"   └─ Ruangan Kosong: {len(vacant_data)} ({len(vacant_data)/len(self.data)*100:.1f}%)\n")
        
        print("STATISTIK SENSOR (Rata-rata):")
        print(f"   ├─ Suhu: {sum(d.temperature for d in self.data)/len(self.data):.2f}°C")
        print(f"   ├─ Kelembaban: {sum(d.humidity for d in self.data)/len(self.data):.2f}%")
        print(f"   ├─ Cahaya: {sum(d.light for d in self.data)/len(self.data):.2f} lux")
        print(f"   ├─ CO2: {sum(d.co_2 for d in self.data)/len(self.data):.2f} ppm")
        print(f"   └─ Humidity Ratio: {sum(d.humidity_ratio for d in self.data)/len(self.data):.4f}\n")
        
        print("PERBANDINGAN (Terisi vs Kosong):")
        print(f"   ├─ Suhu (Terisi): {sum(d.temperature for d in occupied_data)/len(occupied_data):.2f}°C")
        print(f"   ├─ Suhu (Kosong): {sum(d.temperature for d in vacant_data)/len(vacant_data):.2f}°C")
        print(f"   ├─ CO2 (Terisi): {sum(d.co_2 for d in occupied_data)/len(occupied_data):.2f} ppm")
        print(f"   └─ CO2 (Kosong): {sum(d.co_2 for d in vacant_data)/len(vacant_data):.2f} ppm")
        
        # Deteksi anomali CO2
        high_co2 = [d for d in self.data if d.is_abnormal_co2()]
        if high_co2:
            high_co2_occupied = sum(1 for d in high_co2 if d.is_occupied())
            print(f"\n ANOMALI: {len(high_co2)} rekaman memiliki CO2 > 1000 ppm")
            print(f"   ({high_co2_occupied} di antaranya saat ruangan terisi)")
        
        input("\nTekan Enter untuk kembali...")
    
    def filter_by_time(self):
        """Filter data berdasarkan rentang waktu"""
        if not self.load_status:
            print("\nData belum dimuat!")
            input("\nTekan Enter untuk kembali...")
            return
        
        self.clear_screen()
        print("\n" + "="*60)
        print("FILTER DATA BERDASARKAN WAKTU")
        print("="*60)
        
        # Tampilkan rentang waktu yang tersedia
        print(f"\nRentang waktu tersedia:")
        print(f"   Dari: {self.data[0].timestamp}")
        print(f"   Sampai: {self.data[-1].timestamp}")
        
        print("\nOpsi filter:")
        print("1. Filter berdasarkan jam tertentu")
        print("2. Filter berdasarkan hari")
        print("3. Filter berdasarkan rentang tanggal")
        
        choice = input("\nPilih opsi (1-3): ").strip()
        
        filtered = []
        
        if choice == "1":
            hour = input("Masukkan jam (0-23): ").strip()
            filtered = [d for d in self.data if d.timestamp.split()[1].startswith(f"{int(hour):02d}:")]
            print(f"\nData pada jam {hour}:00 - {len(filtered)} rekaman")
            
        elif choice == "2":
            date = input("Masukkan tanggal (YYYY-MM-DD): ").strip()
            filtered = [d for d in self.data if d.timestamp.startswith(date)]
            print(f"\nData tanggal {date}: {len(filtered)} rekaman")
            
        elif choice == "3":
            start = input("Tanggal mulai (YYYY-MM-DD): ").strip()
            end = input("Tanggal akhir (YYYY-MM-DD): ").strip()
            filtered = [d for d in self.data if start <= d.timestamp[:10] <= end]
            print(f"\nData dari {start} s/d {end}: {len(filtered)} rekaman")
        
        if filtered:
            occupied = sum(1 for d in filtered if d.is_occupied())
            print(f"   ├─ Terisi: {occupied} ({occupied/len(filtered)*100:.1f}%)")
            print(f"   └─ Kosong: {len(filtered)-occupied}")
            
            # Tawarkan analisis pada data yang sudah difilter
            if input("\nApakah Anda ingin menganalisis data yang sudah difilter? (y/n): ").lower() == 'y':
                print("\nANALISIS DATA TERFILTER:")
                co2_analyzer = CO2Analyzer(filtered)
                co2_result = co2_analyzer.analyze()
                print(f"   Rata-rata CO2: {co2_result['average_co2_when_occupied']:.1f} ppm (saat terisi)")
                print(f"   Status Ventilasi: {co2_result['status']}")
        
        input("\nTekan Enter untuk kembali...")
    
    def show_visualizations(self):
        """Menampilkan visualisasi data"""
        if not self.load_status:
            print("\nData belum dimuat!")
            input("\nTekan Enter untuk kembali...")
            return
        
        self.clear_screen()
        print("\n" + "="*60)
        print("VISUALISASI DATA")
        print("="*60)
        
        print("\nOpsi Visualisasi:")
        print("1. CO2 vs Occupancy (Time Series)")
        print("2. Suhu vs Cahaya (Scatter Plot)")
        print("3. Pola Okupansi per Jam (Bar Chart)")
        print("4. Matriks Korelasi (Heatmap)")
        print("5. Generate Semua Visualisasi")
        
        choice = input("\nPilih opsi (1-5): ").strip()
        
        try:
            visualizer = SensorVisualizer(self.data)
            
            if choice == "1":
                visualizer.plot_co2_vs_occupancy()
            elif choice == "2":
                visualizer.plot_temperature_vs_light_scatter()
            elif choice == "3":
                visualizer.plot_hourly_occupancy_pattern()
            elif choice == "4":
                visualizer.plot_correlation_matrix()
            elif choice == "5":
                visualizer.generate_all_visualizations()
            else:
                print("Pilihan tidak valid!")
            
        except Exception as e:
            print(f"\nError saat membuat visualisasi: {e}")
            print("   Pastikan matplotlib, pandas, numpy sudah terinstall.")
        
        input("\nTekan Enter untuk kembali...")
    
    def run(self):
        """Menjalankan aplikasi utama"""
        # Load data otomatis jika file ada
        if os.path.exists(self.csv_path):
            self.load_data()
        else:
            print(f"\n File {self.csv_path} tidak ditemukan!")
            print("   Silakan tempatkan file data_.csv di folder 'dataset/'")
            input("\nTekan Enter untuk melanjutkan dengan menu...")
        
        while True:
            self.display_menu()
            choice = input("Pilih menu (0-7): ").strip()
            
            if choice == "0":
                self.clear_screen()
                print("\nTerima kasih telah menggunakan Smart Building Analytics!")
                print("   Sampai jumpa!\n")
                sys.exit(0)
                
            elif choice == "1":
                self.run_analyzer(CO2Analyzer, "ANALISIS KUALITAS UDARA (CO2)")
                
            elif choice == "2":
                self.run_analyzer(ThermodynamicAnalyzer, "ANALISIS TERMODINAMIKA RUANGAN")
                
            elif choice == "3":
                self.run_analyzer(EnergyEfficiencyAnalyzer, "ANALISIS EFISIENSI ENERGI")
                
            elif choice == "4":
                self.show_all_analyses()
                
            elif choice == "5":
                self.show_visualizations()
                
            elif choice == "6":
                self.show_statistics()
                
            elif choice == "7":
                self.filter_by_time()
                
            else:
                print("\nPilihan tidak valid! Silakan coba lagi.")
                input("\nTekan Enter untuk melanjutkan...")


if __name__ == "__main__":
    app = SmartBuildingAnalytics()
    app.run()