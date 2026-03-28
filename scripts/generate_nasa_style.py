import pandas as pd
import numpy as np

# NASA MSL (Curiosity) Batarya Voltajı Simülasyonu
np.random.seed(42)
rows = 1000
time = np.linspace(0, 100, rows)
# Ana sinyal (hafif dalgalı voltaj)
signal = 30 + 2 * np.sin(time * 0.2) + np.random.normal(0, 0.2, rows)

# Gerçekçi NASA anomalileri (Anlık düşüşler ve kozmik gürültü)
signal[200:205] -= 8  # Sensör hatası
signal[500:520] += 5  # Kozmik radyasyon sıçraması
signal[800:810] = 0   # Kısa devre/Bağlantı kopması

df_nasa = pd.DataFrame({'timestamp': range(rows), 'battery_voltage': signal})
df_nasa.to_csv('data/nasa_test_battery.csv', index=False)
print("✅ NASA tarzı test verisi 'data/' klasörüne kaydedildi!")