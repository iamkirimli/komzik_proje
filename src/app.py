import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from processing import TelemetryProcessor 
import requests
import time
from datetime import datetime

st.set_page_config(page_title="Kozmik Pipeline Live", layout="wide")

# --- 1. BELLEK YÖNETİMİ (Gerçek Zamanlı Akış İçin) ---
if 'buffer' not in st.session_state:
    st.session_state.buffer = pd.DataFrame()
if 'son_veri_saati' not in st.session_state:
    st.session_state.son_veri_saati = None

with st.sidebar:
    st.title("🛰️ Kontrol Merkezi")
    esik_degeri = st.slider("Hata Hassasiyeti (Threshold)", 1.0, 10.0, 3.0, step=0.1)
    st.divider()
    canli_mod = st.toggle("📡 UYDUDAN CANLI YAYINA BAĞLAN", value=False)
    
    if canli_mod:
        # NOAA 1 dakikada bir veri basar, biz 10 saniyede bir gidip "yeni bir şey var mı?" diyeceğiz
        st.success("API Bağlantısı Aktif (Gerçek Zamanlı Uydu Takibi)")

processor = TelemetryProcessor(threshold=esik_degeri)

if canli_mod:
    st.title("📡 NOAA Canlı Telemetri Yayını")
    
    # Uyarı ve Saat Alanı
    durum_cubugu = st.empty()
    
    try:
        # En güncel veriyi barındıran (ve her dakika güncellenen) ana kaynak
        url = "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json"
        raw_data = requests.get(url).json()
        df_raw = pd.DataFrame(raw_data[1:], columns=raw_data[0])
        
        sutunlar = ['speed', 'density', 'temperature']
        for col in sutunlar:
            df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')
        df_raw['time_tag'] = pd.to_datetime(df_raw['time_tag'])
        
        df_raw = df_raw.dropna(subset=sutunlar).reset_index(drop=True)
        
        # Uydudan gelen EN SON verinin saatini al
        en_yeni_saat = df_raw['time_tag'].iloc[-1]
        
        # Eğer yeni bir veri geldiyse veya sistem ilk kez açıldıysa
        if st.session_state.son_veri_saati != en_yeni_saat:
            st.session_state.son_veri_saati = en_yeni_saat
            # Grafikte akış hissi için son 60 veriyi ekrana alıyoruz
            st.session_state.buffer = df_raw.tail(60).reset_index(drop=True)
            durum_cubugu.success(f"🛰️ Uydudan Yeni Veri Paketi İndi! (Zaman Damgası: {en_yeni_saat})")
        else:
            durum_cubugu.info(f"⏳ Uydu Bekleniyor... Son Paket: {en_yeni_saat} (NOAA veriyi dakikada bir fırlatır)")

        df_live = st.session_state.buffer

        # Metrikler
        m1, m2, m3 = st.columns(3)
        m1.metric("Anlık Güneş Rüzgarı", f"{df_live['speed'].iloc[-1]:.0f} km/s")
        m2.metric("Plazma Yoğunluğu", f"{df_live['density'].iloc[-1]:.2f} n/cc")
        m3.metric("Sıcaklık", f"{df_live['temperature'].iloc[-1]:.0f} K")

        for col in sutunlar:
            df_p = processor.clean_telemetry(df_live, column=col)
            df_p['kalman_value'] = processor.apply_kalman_filter(df_p['cleaned_value'])
            
            # Grafiği Çiz (Range Slider'ı kapatıp sağı sola kilitleyerek akış hissi veriyoruz)
            fig = px.line(df_p, x='time_tag', y=[col, 'cleaned_value', 'kalman_value'],
                         color_discrete_map={col: '#DC143C', 'cleaned_value': '#00FF7F', 'kalman_value': '#00BFFF'},
                         template="plotly_dark", title=f"🔴 CANLI: {col.upper()} YAYINI")
            
            fig.update_layout(height=350, margin=dict(t=30, b=10), showlegend=False, xaxis_title="Gerçek Zaman")
            st.plotly_chart(fig, use_container_width=True, key=f"live_stream_{col}")

        # Her 5 saniyede bir sayfayı yenileyip uydudan yeni veri düşmüş mü diye bakar
        time.sleep(5)
        st.rerun()
            
    except Exception as e:
        durum_cubugu.error(f"📡 Veri Akışı Bekleniyor... {e}")
        time.sleep(5)
        st.rerun()

else:
    st.info("Sol menüden '📡 UYDUDAN CANLI YAYINA BAĞLAN' butonunu açın.")
    # (Eski statik dosya yükleme kodları buraya gelecek)