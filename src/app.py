import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from processing import TelemetryProcessor
import requests
import time
from datetime import datetime
from modules import snr_module
from modules import log_module

st.set_page_config(page_title="Kozmik Pipeline Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0a0a0f; color: #e0e0ff; }
    .stMetric { background: linear-gradient(135deg, #0d1117, #161b22); border: 1px solid #30363d; border-radius: 10px; padding: 10px; }
    .stMetric label { color: #8b949e !important; }
    .stMetric [data-testid="stMetricValue"] { color: #00ffff !important; font-size: 1.4rem !important; }
    .stExpander { border: 1px solid #21262d !important; background: #0d1117 !important; border-radius: 12px !important; }
    .stSidebar { background: #0d1117 !important; border-right: 1px solid #21262d; }
    h1, h2, h3 { color: #00ffcc !important; }
</style>
""", unsafe_allow_html=True)

COLORS = {"raw": "#ff4444", "cleaned": "#00ff88", "kalman": "#00cfff", "BIT_FLIP": "#ff00ff", "SPIKE": "#ffaa00", "DROPOUT": "#ff4444", "DRIFT": "#aa44ff"}
DAMAGE_EMOJI = {"BIT_FLIP": "⚡", "SPIKE": "📈", "DROPOUT": "📉", "DRIFT": "🌀", "NORMAL": "✅"}

def plot_telemetry(df, column, title_prefix="", x_col=None):
    x = df[x_col] if x_col and x_col in df.columns else df.index

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.06,
        subplot_titles=(f"📡 {title_prefix}{column.upper()} — Ham / Temizlenmiş / Kalman", "☢️ Radyasyon Hasar Haritası")
    )

    fig.add_trace(go.Scatter(x=x, y=df[column], name="🔴 Ham Veri", mode="lines", line=dict(color=COLORS["raw"], width=1.2, dash="dot"), opacity=0.6), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["cleaned_value"], name="🟢 Hampel Temizlenmiş", mode="lines", line=dict(color=COLORS["cleaned"], width=1.8)), row=1, col=1)
    
    if "kalman_value" in df.columns:
        fig.add_trace(go.Scatter(x=x, y=df["kalman_value"], name="🔵 Kalman Filtreli", mode="lines", line=dict(color=COLORS["kalman"], width=2.2)), row=1, col=1)

    if "damage_type" in df.columns:
        for dmg_type in ["BIT_FLIP", "SPIKE", "DROPOUT", "DRIFT"]:
            mask = df["damage_type"] == dmg_type
            if mask.sum() == 0: continue
            fig.add_trace(go.Scatter(x=x[mask], y=df.loc[mask, column], name=f"{DAMAGE_EMOJI[dmg_type]} {dmg_type}", mode="markers", marker=dict(color=COLORS[dmg_type], size=10, symbol="x", line=dict(color="white", width=1))), row=1, col=1)
        fig.add_trace(go.Bar(x=x, y=[1] * len(df), marker=dict(color=df["damage_type"].map(COLORS).fillna("#333"), line=dict(width=0)), showlegend=False, hovertext=df["damage_type"], hoverinfo="text"), row=2, col=1)

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0a0a0f", plot_bgcolor="#0d1117", font=dict(color="#c9d1d9", family="monospace"),
        legend=dict(bgcolor="rgba(13,17,23,0.85)", bordercolor="#30363d", borderwidth=1, font=dict(size=11)),
        height=560, margin=dict(t=50, b=20, l=10, r=10), dragmode="pan", hovermode="x unified"
    )
    fig.update_xaxes(gridcolor="#161b22", zerolinecolor="#21262d")
    fig.update_yaxes(gridcolor="#161b22", zerolinecolor="#21262d")
    fig.update_yaxes(showticklabels=False, row=2, col=1)
    return fig

def render_damage_metrics(report):
    # Veri 'None' gelse bile çökmesin diye '{}' (boş küme) olarak yakalıyoruz.
    breakdown = report.get("damage_breakdown") or {}
    
    # Gösterecek hasar yoksa sessizce durdur, hata verme.
    if not breakdown:
        return
        
    cols = st.columns(max(len(breakdown), 1))
    for i, (dmg_type, count) in enumerate(breakdown.items()):
        emoji = DAMAGE_EMOJI.get(dmg_type, "🔹")
        cols[i].metric(f"{emoji} {dmg_type}", count)

if "buffer" not in st.session_state: st.session_state.buffer = pd.DataFrame()
if "son_veri_saati" not in st.session_state: st.session_state.son_veri_saati = None

with st.sidebar:
    st.markdown("## 🛰️ Kontrol Merkezi")
    esik_degeri = st.slider("Hata Hassasiyeti (Threshold)", 1.0, 10.0, 3.0, step=0.1)
    st.divider()
    st.subheader("🛠️ Ek Özellikler")
    show_snr = st.checkbox("📡 SNR Analizini Göster", value=True)
    st.divider()
    canli_mod = st.toggle("📡 UYDUDAN CANLI YAYINA BAĞLAN", value=False)
    if canli_mod:
        st.success("API Bağlantısı Aktif")
        if st.button("🗑️ Canlı Belleği Sıfırla"):
            st.session_state.buffer = pd.DataFrame()
            st.session_state.son_veri_saati = None
            st.rerun()

processor = TelemetryProcessor(threshold=esik_degeri)

if canli_mod:
    st.title("📡 NOAA Canlı Telemetri Yayını")
    durum_cubugu = st.empty()

    try:
        url = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
        raw_data = requests.get(url).json()
        df_raw = pd.DataFrame(raw_data[1:], columns=raw_data[0])

        sutunlar = ["speed", "density", "temperature"]
        for col in sutunlar: df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")
        df_raw["time_tag"] = pd.to_datetime(df_raw["time_tag"])
        df_raw = df_raw.dropna(subset=sutunlar).reset_index(drop=True)

        en_yeni_saat = df_raw["time_tag"].iloc[-1]
        if st.session_state.son_veri_saati != en_yeni_saat:
            st.session_state.son_veri_saati = en_yeni_saat
            st.session_state.buffer = df_raw.tail(60).reset_index(drop=True)
            durum_cubugu.success(f"🛰️ Yeni Veri Paketi: {en_yeni_saat}")
        else:
            durum_cubugu.info(f"⏳ Uydu Bekleniyor... (Son: {en_yeni_saat})")

        df_live = st.session_state.buffer

        m1, m2, m3 = st.columns(3)
        m1.metric("🌬️ Güneş Rüzgarı", f"{df_live['speed'].iloc[-1]:.0f} km/s")
        m2.metric("💧 Yoğunluk", f"{df_live['density'].iloc[-1]:.2f} n/cc")
        m3.metric("🌡️ Sıcaklık", f"{df_live['temperature'].iloc[-1]:.0f} K")

        for col in sutunlar:
            df_p = processor.clean_telemetry(df_live, column=col)
            df_p["kalman_value"] = processor.apply_kalman_filter(df_p["cleaned_value"])

            if show_snr: snr_module.render_snr_ui(df_p, col)

            report = processor.summary_report(df_p, col)
            with st.expander(f"🔬 {col.upper()} Hasar Raporu", expanded=False):
                r1, r2, r3 = st.columns(3)
                r1.metric("🔇 Gürültü Azaltma", report["noise_reduction"])
                r2.metric("⚠️ Anomali Oranı", report["outlier_ratio"])
                r3.metric("🔢 Anomali Sayısı", report["outliers_found"])
                render_damage_metrics(report)

            fig = plot_telemetry(df_p, col, title_prefix="CANLI — ", x_col="time_tag")
            st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True}, key=f"live_{col}")
            
            # LOG TABLOSU BURADA
            log_module.render_anomaly_log(df_p, col)
            st.divider()

        time.sleep(5)
        st.rerun()

    except Exception as e:
        st.error(f"📡 Bağlantı Kesildi: {e}")
        time.sleep(5)
        st.rerun()

else:
    st.title("🚀 Kozmik Veri İşleme Hattı")
    yuklenen_dosya = st.file_uploader("Veri Dosyasını Seçin (CSV veya JSON)", type=["csv", "json"])

    if yuklenen_dosya is not None:
        try:
            if yuklenen_dosya.name.endswith(".csv"):
                df = pd.read_csv(yuklenen_dosya)
            else:
                import json
                yuklenen_dosya.seek(0)
                data = json.load(yuklenen_dosya)
                df = (pd.DataFrame(data[1:], columns=data[0]) if isinstance(data, list) and isinstance(data[0], list) else pd.read_json(yuklenen_dosya))

            for col in df.columns:
                if any(k in col.lower() for k in ["time", "date"]): df[col] = pd.to_datetime(df[col], errors="coerce")
                else: df[col] = pd.to_numeric(df[col], errors="coerce")

            sayisal_sutunlar = df.select_dtypes(include=[np.number]).columns.tolist()
            st.subheader(f"📊 {len(sayisal_sutunlar)} Telemetri Kanalı Analiz Ediliyor")

            for index, sutun in enumerate(sayisal_sutunlar):
                with st.expander(f"📉 {sutun.upper()} ANALİZ PANELİ", expanded=True):
                    df_islem = df.copy()
                    df_islem[sutun] = df_islem[sutun].replace(0, np.nan)
                    df_islem = df_islem.dropna(subset=[sutun]).reset_index(drop=True)

                    if len(df_islem) > 1:
                        df_processed = processor.clean_telemetry(df_islem, column=sutun)
                        df_processed["kalman_value"] = processor.apply_kalman_filter(df_processed["cleaned_value"])

                        st.divider()
                        m1, m2, m3 = st.columns(3)
                        m1.metric("📊 Toplam Veri", f"{len(df_processed)} Satır")
                        hata_sayisi = int(df_processed["is_outlier"].sum())
                        hata_orani = (hata_sayisi / len(df_processed)) * 100
                        m2.metric("⚠️ Tespit Edilen Hata", f"{hata_sayisi} Adet", f"%{hata_orani:.1f} Yoğunluk", delta_color="inverse")

                        with m3:
                            if show_snr: snr_module.render_snr_ui(df_processed, sutun)
                            else: st.metric("📡 SNR Analizi", "Kapalı")

                        st.divider()
                        st.subheader("☢️ Radyasyon Hasar Analizi")
                        report = processor.summary_report(df_processed, sutun)

                        r1, r2, r3 = st.columns(3)
                        r1.metric("🔇 Gürültü Azaltma", report["noise_reduction"])
                        r2.metric("📊 Anomali Oranı", report["outlier_ratio"])
                        r3.metric("⚠️ Anomali Sayısı", report["outliers_found"])

                        render_damage_metrics(report)
                        st.divider()

                        zaman_col = None
                        for c in df_processed.columns:
                            if any(k in c.lower() for k in ["time", "date"]): zaman_col = c; break

                        fig = plot_telemetry(df_processed, sutun, x_col=zaman_col)
                        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True}, key=f"statik_{index}")
                        
                        # LOG TABLOSU BURADA
                        log_module.render_anomaly_log(df_processed, sutun)

        except Exception as e:
            st.error(f"⚠️ Dosya İşleme Hatası: {e}")