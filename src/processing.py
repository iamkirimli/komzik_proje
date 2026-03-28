import pandas as pd
import numpy as np

class TelemetryProcessor:
    def __init__(self, threshold=3.5):
        self.threshold = threshold
        # Optimal mühendislik değerleri (Sabitlendi)
        self.window_size = 15
        self.q_val = 0.02
        self.r_val = 0.5

    def clean_telemetry(self, df, column):
        df_cleaned = df.copy()
        
        # Hampel Filtresi: Yerel pencerelerde 'spike' avcı
        rolling_median = df_cleaned[column].rolling(window=self.window_size, center=True, min_periods=1).median()
        rolling_mad = df_cleaned[column].rolling(window=self.window_size, center=True, min_periods=1).apply(
            lambda x: np.median(np.abs(x - np.median(x)))
        )
        
        # Hata tespiti (1.4826 MAD ölçekleme katsayısıdır)
        outlier_mask = np.abs(df_cleaned[column] - rolling_median) > (self.threshold * (rolling_mad * 1.4826) + 1e-6)
        
        df_cleaned['is_outlier'] = outlier_mask
        df_cleaned['cleaned_value'] = df_cleaned[column].copy()
        df_cleaned.loc[outlier_mask, 'cleaned_value'] = rolling_median
        
        # Boşlukları akıllıca doldur
        df_cleaned['cleaned_value'] = df_cleaned['cleaned_value'].interpolate(method='linear').ffill().bfill()
        
        return df_cleaned

    def apply_kalman_filter(self, data):
        """Hızlı ve gecikmesiz Kalman filtresi"""
        n_iter = len(data)
        xhat = np.zeros(n_iter)
        P = np.zeros(n_iter)
        xhat[0] = data[0]
        P[0] = 1.0
        
        for k in range(1, n_iter):
            xhatminus = xhat[k-1]
            Pminus = P[k-1] + self.q_val
            K = Pminus / (Pminus + self.r_val)
            xhat[k] = xhatminus + K * (data[k] - xhatminus)
            P[k] = (1 - K) * Pminus
            
        return xhat