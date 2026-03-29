import pandas as pd
import numpy as np
from scipy import stats

class TelemetryProcessor:
    """
    Kozmik Radyasyon Telemetri İşleme Motoru
    ==========================================
    Güneş rüzgarı ve uzay radyasyonunun sebep olduğu
    bit-flip, spike ve veri bozulmalarını tespit eder ve temizler.
    """

    def _init_(self, threshold=3.5):
        self.threshold = threshold
        self.window_size = 15
        self.q_val = 0.02
        self.r_val = 0.5

        # Radyasyon bozulma türü sayaçları
        self.radiation_stats = {
            "bit_flip": 0,
            "spike": 0,
            "dropout": 0,
            "drift": 0
        }

    # =========================================================
    # KATMAN 1: RADYASYON BOZULMA TİPİ TESPİTİ
    # =========================================================

    def classify_radiation_damage(self, series):
        """
        Her anomalinin radyasyon bozulma türünü belirler.
        
        Türler:
        - BIT_FLIP  : Anlık aşırı değer (kozmik ışın çarpması)
        - SPIKE     : Kısa süreli gürültü patlaması
        - DROPOUT   : Sinyal kaybı / sıfır değeri
        - DRIFT     : Yavaş kayma (sensör yaşlanması/radyasyon hasarı)
        """
        damage_types = pd.Series(["NORMAL"] * len(series), index=series.index)
        values = series.values.astype(float)

        rolling_med = pd.Series(values).rolling(self.window_size, center=True, min_periods=1).median()
        rolling_std = pd.Series(values).rolling(self.window_size, center=True, min_periods=1).std().fillna(1e-6)

        for i in range(1, len(values) - 1):
            deviation = abs(values[i] - rolling_med.iloc[i])
            sigma = rolling_std.iloc[i]

            # DROPOUT: sıfır veya NaN
            if values[i] == 0 or np.isnan(values[i]):
                damage_types.iloc[i] = "DROPOUT"

            # BIT_FLIP: tek nokta, komşulardan çok farklı (kozmik ışın)
            elif (deviation > self.threshold * sigma * 2 and
                  abs(values[i] - values[i-1]) > self.threshold * sigma and
                  abs(values[i] - values[i+1]) > self.threshold * sigma):
                damage_types.iloc[i] = "BIT_FLIP"

            # SPIKE: kısa süreli bozulma (1-3 nokta)
            elif deviation > self.threshold * sigma:
                damage_types.iloc[i] = "SPIKE"

        # DRIFT: uzun pencerede istatistiksel kayma (Mann-Kendall benzeri)
        segment_size = max(20, len(values) // 10)
        for start in range(0, len(values) - segment_size, segment_size // 2):
            segment = values[start:start + segment_size]
            if len(segment) < 10:
                continue
            slope, _, r, p, _ = stats.linregress(range(len(segment)), segment)
            normalized_slope = abs(slope) / (np.std(segment) + 1e-9)
            if normalized_slope > 0.15 and p < 0.05:
                for j in range(start, min(start + segment_size, len(values))):
                    if damage_types.iloc[j] == "NORMAL":
                        damage_types.iloc[j] = "DRIFT"

        return damage_types

    # =========================================================
    # KATMAN 2: HAMPEL FİLTRESİ (Spike Avcısı)
    # =========================================================

    def clean_telemetry(self, df, column):
        """Hampel filtresi ile spike ve outlier temizleme."""
        df_cleaned = df.copy()

        rolling_median = df_cleaned[column].rolling(
            window=self.window_size, center=True, min_periods=1).median()
        rolling_mad = df_cleaned[column].rolling(
            window=self.window_size, center=True, min_periods=1).apply(
            lambda x: np.median(np.abs(x - np.median(x))))

        outlier_mask = np.abs(df_cleaned[column] - rolling_median) > (
            self.threshold * (rolling_mad * 1.4826) + 1e-6)

        df_cleaned['is_outlier'] = outlier_mask
        df_cleaned['cleaned_value'] = df_cleaned[column].copy()
        df_cleaned.loc[outlier_mask, 'cleaned_value'] = rolling_median[outlier_mask]

        df_cleaned['cleaned_value'] = (
            df_cleaned['cleaned_value']
            .interpolate(method='linear')
            .ffill()
            .bfill()
        )

        # Radyasyon bozulma tiplerini ekle
        df_cleaned['damage_type'] = self.classify_radiation_damage(df_cleaned[column])

        # Sayaçları güncelle
        for dmg_type in ["BIT_FLIP", "SPIKE", "DROPOUT", "DRIFT"]:
            key = dmg_type.lower()
            self.radiation_stats[key] = int(
                (df_cleaned['damage_type'] == dmg_type).sum())

        return df_cleaned

    # =========================================================
    # KATMAN 3: ADAPTİF KALMAN FİLTRESİ
    # =========================================================

    def apply_kalman_filter(self, data):
        """
        Adaptif Kalman Filtresi.
        Verinin yerel varyansına göre Q ve R değerlerini otomatik ayarlar.
        Radyasyon spike'larına karşı standart Kalman'dan çok daha dayanıklı.
        """
        data = np.array(data, dtype=float)
        n = len(data)
        xhat = np.zeros(n)
        P = np.zeros(n)
        xhat[0] = data[0]
        P[0] = 1.0

        # Başlangıç gürültüsünden adaptif Q/R tahmini
        init_window = data[:min(30, n)]
        base_var = np.var(init_window) if np.var(init_window) > 0 else 1.0
        adaptive_q = base_var * 0.01
        adaptive_r = base_var * 0.5

        for k in range(1, n):
            # Tahmin adımı
            xhatminus = xhat[k-1]
            Pminus = P[k-1] + adaptive_q

            # Yerel varyansa göre R'yi dinamik güncelle
            local_start = max(0, k - 5)
            local_var = np.var(data[local_start:k]) if k > local_start else base_var
            dynamic_r = max(adaptive_r, local_var * 0.3)

            # Güncelleme adımı
            K = Pminus / (Pminus + dynamic_r)
            xhat[k] = xhatminus + K * (data[k] - xhatminus)
            P[k] = (1 - K) * Pminus

        return xhat

    # =========================================================
    # KATMAN 4: ANOMALİ SKORU
    # =========================================================

    def anomaly_score(self, df, column):
        """
        Her veri noktası için 0-100 arası radyasyon hasar skoru.
        Yüksek skor = yüksek bozulma şüphesi.
        """
        rolling_median = df[column].rolling(
            window=self.window_size, center=True, min_periods=1).median()
        rolling_mad = df[column].rolling(
            window=self.window_size, center=True, min_periods=1).apply(
            lambda x: np.median(np.abs(x - np.median(x)))).fillna(1e-6)

        raw_score = np.abs(df[column] - rolling_median) / (rolling_mad * 1.4826 + 1e-6)
        normalized = np.clip((raw_score / (self.threshold * 3)) * 100, 0, 100)
        return normalized

    # =========================================================
    # KATMAN 5: ÖZET RAPOR
    # =========================================================

    def summary_report(self, df, column):
        """
        Temizleme işleminin etkisini özetleyen rapor.
        app.py'de st.json() veya st.metric() ile gösterilebilir.
        """
        if 'cleaned_value' not in df.columns:
            df = self.clean_telemetry(df, column)

        original_std = df[column].std()
        cleaned_std = df['cleaned_value'].std()
        noise_reduction = (1 - cleaned_std / (original_std + 1e-9)) * 100

        total = len(df)
        outliers = int(df['is_outlier'].sum())

        damage_counts = {}
        if 'damage_type' in df.columns:
            damage_counts = df['damage_type'].value_counts().to_dict()

        return {
            "total_points": total,
            "outliers_found": outliers,
            "outlier_ratio": f"{(outliers/total)*100:.2f}%",
            "noise_reduction": f"{noise_reduction:.1f}%",
            "original_std": round(original_std, 4),
            "cleaned_std": round(cleaned_std, 4),
            "damage_breakdown": damage_counts
        }