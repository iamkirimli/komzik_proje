import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime

class TelemetryGenerator:
    def __init__(self, duration=20, sampling_rate=100):
        self.duration = duration
        self.fs = sampling_rate
        self.t = np.linspace(0, duration, int(duration * sampling_rate))
        self.clean_signal = None
        self.noisy_signal = None

    def generate_baseline(self):
        """1. ADIM: İdeal (Baseline) Sinyal"""
        base = 3000 + 500 * np.sin(2 * np.pi * 0.5 * self.t) 
        trend = 15 * self.t**1.4 
        self.clean_signal = base + trend
        self.noisy_signal = self.clean_signal.copy()
        return self.clean_signal

    def add_gaussian_noise(self, sigma=15.0):
        """2. ADIM: Normal Sensör Gürültüsü"""
        noise = np.random.normal(0, sigma, size=self.t.shape)
        self.noisy_signal += noise
        return self.noisy_signal

    def add_spikes(self, intensity=600, probability=0.01):
        """3. ADIM: Kozmik Sıçramalar (Spikes)"""
        # DİKKAT: Buradaki tüm satırlar def'e göre içeride olmalı!
        spike_mask = np.random.choice([0, 1, -1], size=self.t.shape, 
                                      p=[1-probability, probability/2, probability/2])
        
        random_spikes = spike_mask * np.random.uniform(intensity * 0.5, intensity * 1.5, size=self.t.shape)
        
        self.noisy_signal += random_spikes
        return self.noisy_signal

    def save_to_csv(self, filename="telemetri_verisi.csv"):
        """4. ADIM: CSV Kayıt (Sınıfın içinde olmalı)"""
        sim_start_time = datetime.datetime.now()
        
        data = {
            'sensor_id': "ENG_RPM_001",
            'timestamp': [sim_start_time + datetime.timedelta(seconds=x) for x in self.t],
            'ideal_signal': self.clean_signal,
            'raw_value': self.noisy_signal
        }
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"✅ {filename} dosyası başarıyla kaydedildi!")

# --- ÇALIŞTIRMA VE GÖRSELLEŞTİRME ---
if __name__ == "__main__":
    sim = TelemetryGenerator(duration=15, sampling_rate=100)

    # Verileri üret
    sim.generate_baseline()
    sim.add_gaussian_noise(sigma=12.0)
    sim.add_spikes(intensity=700, probability=0.008)

    # CSV Kaydet
    sim.save_to_csv("data/kozmik_telemetri_v1.csv")

    # Grafik Çiz
    plt.figure(figsize=(14, 7))
    plt.plot(sim.t, sim.clean_signal, label='İdeal Sinyal', color='royalblue', linestyle='--', alpha=0.8)
    plt.plot(sim.t, sim.noisy_signal, label='Bozuk Telemetri', color='crimson', linewidth=1)
    
    plt.title("Profesyonel Telemetri Veri Simülasyonu", fontsize=14)
    plt.xlabel("Zaman (saniye)")
    plt.ylabel("Ölçülen Değer")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    print("Simülasyon tamamlandı. Grafik oluşturuluyor...")
    plt.show()