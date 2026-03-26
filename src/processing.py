import numpy as np
import pandas as pd

class TelemetryProcessor:
    def __init__(self, threshold=3.5):
        self.threshold = threshold

    def apply_modified_zscore(self, data, window_size=50):
        """YEREL (ROLLING) MODIFIED Z-SCORE: Sinyalin o anki akışına göre hata bulur."""
        series = pd.Series(data)
        
        # 1. Yerel Medyanı ve Yerel Sapmayı (MAD) hesapla
        rolling_median = series.rolling(window=window_size, center=True).median()
        rolling_ad = np.abs(series - rolling_median)
        rolling_mad = rolling_ad.rolling(window=window_size, center=True).median()
        
        # 2. Modified Z-Score hesapla
        modified_z_score = 0.6745 * rolling_ad / (rolling_mad + 1e-6)
        
        # 3. Eşik değerini aşanları bul (NaN değerleri False kabul et)
        outliers_mask = (modified_z_score > self.threshold).fillna(False)
        return outliers_mask

    def apply_median_filter(self, data, window_size=5):
        """2. ADIM: Tekil noktaları çevresine göre onar"""
        return pd.Series(data).rolling(window=window_size, center=True).median().fillna(method='bfill').fillna(method='ffill').values

    def clean_telemetry(self, df, column='raw_value'):
        """Tüm filtreleri sırayla uygula (Main Pipeline)"""
        df_cleaned = df.copy()
        
        # Sıçramaları bul
        outliers = self.apply_modified_zscore(df_cleaned[column])
        df_cleaned['is_outlier'] = outliers
        
        # Düzeltme: Önce sıçramaları Medyan Filtresi ile onar
        df_cleaned['cleaned_value'] = self.apply_median_filter(df_cleaned[column])
        
        # Alternatif: Sadece outlier olan yerleri medyanla değiştir, diğerlerini bırak
        # df_cleaned.loc[outliers, 'cleaned_value'] = df_cleaned['raw_value'].median()
        
        return df_cleaned