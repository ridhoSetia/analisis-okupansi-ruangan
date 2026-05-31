import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List
from Models import SensorReading

class SensorVisualizer:
    """Kelas untuk memvisualisasikan data sensor"""
    
    def __init__(self, data: List[SensorReading]):
        self.data = data
        self.df = self._to_dataframe()
    
    def _to_dataframe(self) -> pd.DataFrame:
        """Konversi list SensorReading ke Pandas DataFrame"""
        records = []
        for reading in self.data:
            records.append({
                'timestamp': pd.to_datetime(reading.timestamp),
                'temperature': reading.temperature,
                'humidity': reading.humidity,
                'light': reading.light,
                'co2': reading.co_2,
                'humidity_ratio': reading.humidity_ratio,
                'occupancy': reading.occupancy
            })
        df = pd.DataFrame(records)
        return df.set_index('timestamp')
    
    def plot_co2_vs_occupancy(self, save_path: str = None):
        """Time-series: CO2 vs Occupancy"""
        fig, ax1 = plt.subplots(figsize=(14, 6))
        
        # Ambil sample (maks 500 titik untuk performa)
        sample_data = self.df.iloc[::max(1, len(self.df)//500)]
        
        # Plot CO2
        ax1.set_xlabel('Timestamp')
        ax1.set_ylabel('CO2 (ppm)', color='tab:red')
        ax1.plot(sample_data.index, sample_data['co2'], color='tab:red', alpha=0.7, linewidth=1, label='CO2')
        ax1.tick_params(axis='y', labelcolor='tab:red')
        
        # Plot Occupancy sebagai area
        ax2 = ax1.twinx()
        ax2.set_ylabel('Occupancy (1=Ada Orang, 0=Kosong)', color='tab:blue')
        ax2.fill_between(sample_data.index, sample_data['occupancy'], 0, 
                         color='tab:blue', alpha=0.3, label='Occupancy')
        ax2.tick_params(axis='y', labelcolor='tab:blue')
        
        # Garis threshold CO2 1000ppm
        ax1.axhline(y=1000, color='orange', linestyle='--', linewidth=1.5, label='Threshold Ventilasi Buruk (1000ppm)')
        
        plt.title('Analisis CO2 vs Occupancy - Deteksi Kehadiran Manusia')
        fig.tight_layout()
        
        # Tambahan legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()
        
    def plot_temperature_vs_light_scatter(self, save_path: str = None):
        """Scatter plot: Temperature vs Light, colored by occupancy"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        occupied = self.df[self.df['occupancy'] == 1]
        vacant = self.df[self.df['occupancy'] == 0]
        
        ax.scatter(vacant['temperature'], vacant['light'], 
                   alpha=0.5, c='blue', label='Ruangan Kosong (0)', s=20)
        ax.scatter(occupied['temperature'], occupied['light'], 
                   alpha=0.5, c='red', label='Ruangan Terisi (1)', s=20)
        
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Light Intensity (Lux)')
        ax.set_title('Korelasi Suhu vs Intensitas Cahaya berdasarkan Occupancy')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()
    
    def plot_hourly_occupancy_pattern(self, save_path: str = None):
        """Pattern okupansi per jam"""
        fig, ax = plt.subplots(figsize=(12, 5))
        
        # Ekstrak jam
        hourly_data = self.df.copy()
        hourly_data['hour'] = hourly_data.index.hour
        
        # Hitung persentase okupansi per jam
        hourly_occupancy = hourly_data.groupby('hour')['occupancy'].mean() * 100
        
        ax.bar(hourly_occupancy.index, hourly_occupancy.values, 
               color='skyblue', edgecolor='navy', alpha=0.7)
        ax.set_xlabel('Jam')
        ax.set_ylabel('Persentase Okupansi (%)')
        ax.set_title('Pola Okupansi Ruangan per Jam')
        ax.set_xticks(range(0, 24))
        ax.set_xticklabels([f'{i}:00' for i in range(24)], rotation=45)
        ax.axhline(y=50, color='red', linestyle='--', label='Tengah hari (50%)')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()
    
    def plot_correlation_matrix(self, save_path: str = None):
        """Heatmap korelasi antar sensor"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Pilih kolom numerik
        corr_cols = ['temperature', 'humidity', 'light', 'co2', 'humidity_ratio', 'occupancy']
        corr_matrix = self.df[corr_cols].corr()
        
        im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr_cols)))
        ax.set_yticks(range(len(corr_cols)))
        ax.set_xticklabels(corr_cols, rotation=45, ha='right')
        ax.set_yticklabels(corr_cols)
        
        # Tambahkan nilai di heatmap
        for i in range(len(corr_cols)):
            for j in range(len(corr_cols)):
                text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                               ha="center", va="center", color="white" if abs(corr_matrix.iloc[i, j]) > 0.5 else "black")
        
        plt.colorbar(im, ax=ax, label='Korelasi')
        plt.title('Matriks Korelasi Antar Sensor')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()
    
    def generate_all_visualizations(self, output_dir: str = "visualizations"):
        """Generate semua visualisasi sekaligus"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n" + "="*60)
        print("MEMBANGKITKAN VISUALISASI...")
        print("="*60)
        
        self.plot_co2_vs_occupancy(save_path=f"{output_dir}/co2_vs_occupancy.png")
        self.plot_temperature_vs_light_scatter(save_path=f"{output_dir}/temp_vs_light.png")
        self.plot_hourly_occupancy_pattern(save_path=f"{output_dir}/hourly_pattern.png")
        self.plot_correlation_matrix(save_path=f"{output_dir}/correlation_matrix.png")
        
        print(f"\nSemua visualisasi disimpan di folder '{output_dir}/'")