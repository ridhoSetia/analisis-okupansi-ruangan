# 🏢 Analisis Data Sensor Smart Building (Deteksi Okupansi Ruangan)

Aplikasi berbasis *Command Line Interface* (CLI) menggunakan Python untuk menganalisis dan memvisualisasikan data sensor lingkungan dari sebuah *Smart Building*. Fokus utama dari aplikasi ini adalah untuk mendeteksi tingkat okupansi (kehadiran manusia) di dalam ruangan serta memberikan berbagai *insight* terkait kualitas udara, termodinamika, dan efisiensi energi. 

Proyek ini dibangun secara modular menggunakan prinsip **Pemrograman Berorientasi Objek (OOP)** serta menerapkan prinsip desain **SOLID**.

## ✨ Fitur Utama

1. **Analisis Kualitas Udara (CO2)**: Menganalisis korelasi lonjakan tingkat CO2 terhadap kehadiran manusia dan mengevaluasi status ventilasi ruangan.
2. **Analisis Termodinamika**: Mengukur rentang suhu dan rata-rata kelembapan untuk mendeteksi anomali lingkungan (mis. butuh *humidifier/dehumidifier*).
3. **Analisis Efisiensi Energi**: Mendeteksi pemborosan energi dengan melacak seberapa sering lampu dibiarkan menyala saat ruangan kosong.
4. **Visualisasi Data Beragam**:
   - Time-series CO2 vs Occupancy
   - Scatter plot korelasi Suhu vs Cahaya
   - Bar chart pola okupansi per jam
   - Heatmap matriks korelasi antar-sensor
5. **Filter Data Fleksibel**: Kemampuan menyaring dataset berdasarkan jam tertentu, hari, maupun rentang tanggal tertentu.
6. **Ekspor Laporan**: Secara otomatis membuat rangkuman dan rekomendasi (laporan analisis lengkap) ke dalam format file `.txt`.

## 📁 Struktur Direktori

Proyek ini dipisah menjadi beberapa modul terpisah (arsitektur modular) untuk kemudahan *maintenance* dan keterbacaan:

```text
├── dataset/
│   ├── data_.csv           # File dataset utama berisi rekaman data sensor
│   ├── datatraining.txt    # Dataset training untuk pengujian
│   ├── datatest.txt        # Dataset testing 1
│   └── datatest2.txt       # Dataset testing 2
├── Analyzer.py             # Kelas analisis data (Abstraksi & Pewarisan)
├── Main.py                 # File utama / Entry point untuk menjalankan aplikasi CLI
├── Models.py               # Representasi data menggunakan Dataclass (SensorReading)
├── Repository.py           # Menangani ekstraksi file dan pemrosesan awal dataset
└── Visualization.py        # Kelas visualizer untuk memproses grafik dan plot data

```

## 🛠️ Persyaratan Sistem (Prerequisites)

Pastikan Anda telah menginstal Python (disarankan versi 3.8 ke atas). Program ini membutuhkan beberapa *library* eksternal untuk manipulasi data dan visualisasi. Instal dependensi melalui `pip`:

```bash
pip install pandas matplotlib numpy

```

## 🚀 Cara Instalasi dan Penggunaan

1. **Clone Repositori**
```bash
git clone [https://github.com/ridhosetia/analisis-okupansi-ruangan.git](https://github.com/ridhosetia/analisis-okupansi-ruangan.git)
cd analisis-okupansi-ruangan

```


2. **Siapkan Dataset**
Pastikan file dataset berada di dalam folder `dataset/`. Program secara default akan membaca `dataset/data_.csv`. Dataset harus memiliki kolom (header) berikut:
`Date, Temperature, Humidity, Light, CO2, HumidityRatio, Occupancy`
3. **Jalankan Aplikasi**
Jalankan file `Main.py` menggunakan Python:
```bash
python Main.py

```


4. **Navigasi Menu Utama**
Ikuti instruksi di layar terminal untuk memilih menu analisis atau visualisasi yang Anda inginkan (Ketik angka 0-7).

## 🧠 Konsep OOP & SOLID yang Diimplementasikan

### 1. SOLID Principle: Single Responsibility Principle (SRP)

Proyek ini mengadopsi **SRP** secara ketat, di mana **setiap kelas dan modul hanya memiliki satu alasan untuk berubah** (satu tanggung jawab spesifik):

* **`Repository.py` (`DataRepository`)**: Hanya bertanggung jawab untuk urusan I/O data, seperti membaca file CSV/TXT, melakukan parsing, dan menyediakan data mentah ke aplikasi. Kelas ini tidak tahu-menahu tentang cara menganalisis atau menggambar grafik.
* **`Models.py` (`SensorReading`)**: Hanya bertanggung jawab untuk merepresentasikan struktur data satu baris log sensor dan melakukan validasi tipe data dasar.
* **`Analyzer.py` (`BaseIoTAnalyzer` dan turunannya)**: Hanya bertanggung jawab untuk melakukan kalkulasi matematis/analitik dan mengekstrak statistik dari data. Mereka tidak bertanggung jawab menampilkan grafik atau membaca file.
* **`Visualization.py` (`DataVisualizer`)**: Hanya bertanggung jawab untuk merender visualisasi grafik (Matplotlib). Kelas ini menerima data yang sudah siap plot tanpa perlu tahu logika bisnis di balik analisisnya.
* **`Main.py`**: Hanya bertanggung jawab sebagai *orchestrator* atau pengatur alur jalannya program (CLI Menu) dan menjembatani interaksi pengguna dengan sistem.

### 2. Konsep OOP Lainnya

* **Encapsulation**: Pembungkusan atribut log sensor ke dalam objek `SensorReading`.
* **Abstraction**: Menggunakan modul `abc` (Abstract Base Class) pada `BaseIoTAnalyzer` di `Analyzer.py` untuk mendefinisikan *interface* metode `analyze()` yang wajib diimplementasikan oleh setiap jenis analisis.
* **Inheritance & Polymorphism**: Kelas `CO2Analyzer`, `ThermodynamicAnalyzer`, dan `EnergyEfficiencyAnalyzer` mewarisi properti dari `BaseIoTAnalyzer`, namun masing-masing menerapkan perilaku (*behavior*) yang berbeda pada metode `analyze()`.

## 📊 Format Dataset

Isi dataset diharapkan mengikuti format berikut:

```csv
Date,Temperature,Humidity,Light,CO2,HumidityRatio,Occupancy
2015-02-04 17:51:00,23.18,27.272,426.0,721.25,0.004792988,1
2015-02-04 17:51:59,23.15,27.2675,429.5,714.0,0.004783441,1

```

*(Catatan: Nilai `Occupancy` 1 menandakan ruangan terisi, sedangkan 0 menandakan ruangan kosong).*

## 📄 Lisensi

Silakan menggunakan, mendistribusikan, atau memodifikasi *codebase* ini untuk keperluan pembelajaran maupun riset.

```

<Elicitations message="Apakah ada bagian lain yang ingin Anda tambahkan atau sesuaikan?">
  <Elicitation label="Tambahkan Open/Closed Principle" query="Tambahkan penjelasan konsep Open/Closed Principle (OCP) dari SOLID ke dalam README.md tersebut" />
  <Elicitation label="Tambahkan petunjuk Jupyter Notebook" query="Tambahkan bagian penjelasan mengenai file test_okupansi.ipynb ke dalam README.md" />
</Elicitations>

```