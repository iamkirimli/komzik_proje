import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from processing import TelemetryProcessor 
import requests
import time
from datetime import datetime
from modules import snr_module # Ekip arkadaşının modülü

# Sayfa Yapılandırması
st.set_page_config(page_title="Kozmik Pipeline Pro", layout="wide")

# --- 1. BELLEK YÖNETİMİ (Session State) ---
if 'buffer' not in st.session_state:
    st.session_state.buffer = pd.DataFrame()
if 'son_veri_saati' not in st.session_state:
    st.session_state.son_veri_saati = None

# --- 2. SIDEBAR (KONTROL MERKEZİ) ---
with st.sidebar:
    st.title("🛰️ Kontrol Merkezi")
    esik_degeri = st.slider("Hata Hassasiyeti (Threshold)", 1.0, 10.0, 3.0, step=0.1)
    
    st.divider()
    # MODÜLER ÖZELLİKLER
    st.subheader("🛠️ Ek Özellikler")
    show_snr = st.checkbox("📡 SNR Analizini Göster", value=True)
    
    st.divider()
    canli_mod = st.toggle("📡 UYDUDAN CANLI YAYINA BAĞLAN", value=False)
    
    if canli_mod:
        st.success("API Bağlantısı Aktif (Gerçek Zamanlı Takip)")
        if st.button("🗑️ Canlı Belleği Sıfırla"):
            st.session_state.buffer = pd.DataFrame()
            st.session_state.son_veri_saati = None
            st.rerun()

# --- 3. İŞLEMCİYİ BAŞLAT ---
processor = TelemetryProcessor(threshold=esik_degeri)

# --- 4. CANLI AKIŞ MODU (LIVE STREAM) ---
if canli_mod:
    st.title("📡 NOAA Canlı Telemetri Yayını")
    durum_cubugu = st.empty()
    
    try:
        # NOAA Canlı Veri Kaynağı
        url = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
        raw_data = requests.get(url).json()
        df_raw = pd.DataFrame(raw_data[1:], columns=raw_data[0])
        
        # Veri Dönüştürme
        sutunlar = ['speed', 'density', 'temperature']
        for col in sutunlar:
            df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')
        df_raw['time_tag'] = pd.to_datetime(df_raw['time_tag'])
        df_raw = df_raw.dropna(subset=sutunlar).reset_index(drop=True)
        
        # Yeni Veri Kontrolü ve Kayan Pencere
        en_yeni_saat = df_raw['time_tag'].iloc[-1]
        if st.session_state.son_veri_saati != en_yeni_saat:
            st.session_state.son_veri_saati = en_yeni_saat
            st.session_state.buffer = df_raw.tail(60).reset_index(drop=True)
            durum_cubugu.success(f"🛰️ Yeni Veri Paketi İşlendi: {en_yeni_saat}")
        else:
            durum_cubugu.info(f"⏳ Uydu Bekleniyor... (Son Veri: {en_yeni_saat})")

        df_live = st.session_state.buffer

        # Üst Metrikler
        m1, m2, m3 = st.columns(3)
        m1.metric("Anlık Güneş Rüzgarı", f"{df_live['speed'].iloc[-1]:.0f} km/s")
        m2.metric("Yoğunluk", f"{df_live['density'].iloc[-1]:.2f} n/cc")
        m3.metric("Sıcaklık", f"{df_live['temperature'].iloc[-1]:.0f} K")

        # Tablo Döngüsü
        for col in sutunlar:
            # Algoritma Uygulama
            df_p = processor.clean_telemetry(df_live, column=col)
            df_p['kalman_value'] = processor.apply_kalman_filter(df_p['cleaned_value'])
            
            # --- MODÜL ENTEGRASYONU (SNR) ---
            if show_snr:
                snr_module.render_snr_ui(df_p, col)
            
            # Grafik Çizimi
            fig = px.line(df_p, x='time_tag', y=[col, 'cleaned_value', 'kalman_value'],
                         color_discrete_map={col: '#DC143C', 'cleaned_value': '#00FF7F', 'kalman_value': '#00BFFF'},
                         template="plotly_dark", title=f"🔴 CANLI {col.upper()} ANALİZİ")
            
            fig.update_layout(height=400, margin=dict(t=30, b=10), dragmode='pan')
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True}, key=f"live_{col}")

        # Otomatik Yenileme
        time.sleep(5)
        st.rerun()
            
    except Exception as e:
        st.error(f"📡 Bağlantı Kesildi: {e}")
        time.sleep(5)
        st.rerun()

# --- 5. STATİK DOSYA MODU ---
else:
    st.title("🚀 Kozmik Veri İşleme Hattı")
    yuklenen_dosya = st.file_uploader("Veri Dosyasını Seçin (CSV veya JSON)", type=["csv", "json"])

    if yuklenen_dosya is not None:
        try:
            # Veri Okuma Mantığı
            if yuklenen_dosya.name.endswith('.csv'):
                df = pd.read_csv(yuklenen_dosya)
            else:
                import json
                yuklenen_dosya.seek(0)
                data = json.load(yuklenen_dosya)
                df = pd.DataFrame(data[1:], columns=data[0]) if isinstance(data, list) and isinstance(data[0], list) else pd.read_json(yuklenen_dosya)

            # Tip Düzenlemeleri
            for col in df.columns:
                if any(k in col.lower() for k in ['time', 'date']):
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                else:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            sayisal_sutunlar = df.select_dtypes(include=[np.number]).columns.tolist()
            st.subheader(f"📊 {len(sayisal_sutunlar)} Telemetri Grubu İnceleniyor")
            
            for index, sutun in enumerate(sayisal_sutunlar):
                with st.expander(f"📉 {sutun.upper()} ANALİZ PANELİ", expanded=True):
                    # Veri Hazırlama
                    df_islem = df.copy()
                    df_islem[sutun] = df_islem[sutun].replace(0, np.nan)
                    df_islem = df_islem.dropna(subset=[sutun]).reset_index(drop=True)
                    
                    if len(df_islem) > 1:
                        # Filtreleri Uygula
                        df_processed = processor.clean_telemetry(df_islem, column=sutun)
                        df_processed['kalman_value'] = processor.apply_kalman_filter(df_processed['cleaned_value'])
                        
                        # 🔥 İSTEDİĞİN YAN YANA METRİKLER BURADA
                        st.divider()
                        m1, m2, m3 = st.columns(3) # 3 sütuna böldük
                        
                        m1.metric("📊 Toplam Veri", f"{len(df_processed)} Satır")
                        
                        hata_sayisi = df_processed['is_outlier'].sum()
                        hata_orani = (hata_sayisi / len(df_processed)) * 100
                        m2.metric("⚠️ Tespit Edilen Hata", f"{hata_sayisi} Adet", f"%{hata_orani:.1f} Yoğunluk", delta_color="inverse")
                        
                        # SNR Modülünü 3. sütuna yerleştiriyoruz
                        with m3:
                            if show_snr:
                                snr_module.render_snr_ui(df_processed, sutun)
                            else:
                                st.metric("📡 SNR Analizi", "Kapalı")
                        
                        # Grafik Çizimi
                        fig = px.line(df_processed, y=[sutun, 'cleaned_value', 'kalman_value'],
                                     color_discrete_map={sutun: '#DC143C', 'cleaned_value': '#00FF7F', 'kalman_value': '#00BFFF'},
                                     template="plotly_dark")
                        
                        fig.update_layout(height=450, dragmode='pan', margin=dict(t=20, b=20))
                        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True}, key=f"statik_{index}")
        
        except Exception as e:
            st.error(f"⚠️ Dosya İşleme Hatası: {e}")