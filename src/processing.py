import numpy as np
import pandas as pd

class TelemetryProcessor:
    def __init__(self, threshold=3.5):
        self.threshold = threshold

    def apply_modified_zscore(self, data, window_size=50):
        """Kenar etkisini (min_periods) hesaba katan hata tespiti"""
        series = pd.Series(data)
        
        # min_periods=1 ekleyerek en baştaki ve en sondaki noktaları da kurtarıyoruz
        rolling_median = series.rolling(window=window_size, center=True, min_periods=1).median()
        rolling_ad = np.abs(series - rolling_median)
        rolling_mad = rolling_ad.rolling(window=window_size, center=True, min_periods=1).median()
        
        modified_z_score = 0.6745 * rolling_ad / (rolling_mad + 1e-6)
        return (modified_z_score > self.threshold).fillna(False)

    def clean_telemetry(self, df, column='raw_value'):
        """DİNAMİK ONARIM: Sadece tespit edilen yerleri düzeltir."""
        df_cleaned = df.copy()
        
        # 1. Hataları işaretle (Threshold burada devreye girer)
        outliers = self.apply_modified_zscore(df_cleaned[column])
        df_cleaned['is_outlier'] = outliers
        
        # Onarım yaparken de kenarları boş geçmemek için min_periods ekle
        rolling_median = df_cleaned[column].rolling(window=21, center=True, min_periods=1).median()
        
        # 3. CERRAHİ MÜDAHALE
        df_cleaned['cleaned_value'] = df_cleaned[column].copy()
        # Sadece hata olan satırlara medyanı yapıştır, diğerleri orijinal kalsın
        df_cleaned.loc[outliers, 'cleaned_value'] = rolling_median[outliers]
        
        # Kenarları doldur
        df_cleaned['cleaned_value'] = df_cleaned['cleaned_value'].ffill().bfill()
        
        return df_cleaned

    def apply_kalman_filter(self, data, process_variance=0.01):
        """Kalman filtresini uygular"""
        # (Önceki yazdığımız kalman kodu aynen kalabilir)
        # Sadece temizlenmiş veri üzerinden geçtiği için artık slider'a dolaylı tepki verir.
        n_iter = len(data)
        xhat = np.zeros(n_iter)
        P = np.zeros(n_iter)
        xhatminus = np.zeros(n_iter)
        Pminus = np.zeros(n_iter)
        K = np.zeros(n_iter)
        xhat[0] = data[0]
        P[0] = 1.0
        for k in range(1, n_iter):
            xhatminus[k] = xhat[k-1]
            Pminus[k] = P[k-1] + process_variance
            K[k] = Pminus[k] / (Pminus[k] + 0.1) # measurement_variance sabitlendi
            xhat[k] = xhatminus[k] + K[k] * (data[k] - xhatminus[k])
            P[k] = (1 - K[k]) * Pminus[k]
        return xhat