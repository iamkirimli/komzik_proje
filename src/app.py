import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from processing import TelemetryProcessor 

st.set_page_config(page_title="Kozmik Pipeline", layout="wide")

# --- 1. SIDEBAR (SADE VE ÖZ) ---
with st.sidebar:
    st.title("🛰️ Kontrol Paneli")
    # Sadece çalışan ve etkili olan slider'ı bıraktık
    esik_degeri = st.slider("Hata Yakalama Hassasiyeti", 1.0, 10.0, 3.5, step=0.1)
    
    st.divider()
    st.subheader("🛠️ Gelişmiş Filtreleme")
    use_kalman = st.checkbox("Kalman Filtresi", value=True)

# --- 2. ANA SAYFA VE DOSYA YÜKLEME ---
st.title("🚀 Kozmik Veri İşleme Hattı")
yuklenen_dosya = st.file_uploader("Temizlenecek CSV dosyasını seçin", type="csv")

# ... (importlar aynı) ...

# ... (importlar aynı) ...

if yuklenen_dosya is not None:
    df = pd.read_csv(yuklenen_dosya)
    
    # --- BURASI KRİTİK ---
    # Her slider hareketinde bu sınıf yeni threshold değeriyle tekrar kurulur
    processor = TelemetryProcessor(threshold=esik_degeri)
    
    # Veriyi işle
    df_processed = processor.clean_telemetry(df)
    
    if use_kalman:
        df_processed['kalman_value'] = processor.apply_kalman_filter(
            df_processed['cleaned_value'], 
            process_variance=0.01
        )

    # 3. ADIM: Metrikler
    hata_sayisi = df_processed['is_outlier'].sum()
    hata_orani = (hata_sayisi / len(df_processed)) * 100
    
    # 4. ADIM: Üst Bilgi Paneli
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📊 Toplam Veri", f"{len(df_processed)} Satır")
    m2.metric("⚠️ Tespit Edilen Hata", f"{hata_sayisi} Adet", 
              delta=f"%{hata_orani:.1f} Oran", delta_color="inverse")
    m3.metric("📉 Sinyal Durumu", "Filtrelendi", delta="Aktif")
    
    if use_kalman:
        m4.metric("🛰️ Kalman Filtresi", "✅ AKTİF", delta="Gürültü Yok Edici")
    else:
        m4.metric("🛰️ Kalman Filtresi", "❌ PASİF", delta="Sadece Z-Score")

    # --- 5. GÖRSELLEŞTİRME ---
    tab1, tab2 = st.tabs(["📊 Karşılaştırmalı Grafik", "📋 Ham Veri Tablosu"])
    
    with tab1:
        st.subheader("📊 İnteraktif 2D Analiz")
        y_ekseni = ['raw_value', 'cleaned_value']
        if use_kalman:
            y_ekseni.append('kalman_value')
            
        fig_2d = px.line(df_processed, x=df_processed.index, y=y_ekseni,
                         color_discrete_map={
                             'raw_value': '#DC143C',
                             'cleaned_value': '#00FF7F',
                             'kalman_value': '#00BFFF'
                         },
                         render_mode='webgl') 
        
        fig_2d.update_layout(
            height=600, hovermode="x unified", dragmode='pan',
            xaxis=dict(rangeslider=dict(visible=True), fixedrange=False),
            yaxis=dict(fixedrange=False)
        )
        st.plotly_chart(fig_2d, use_container_width=True, config={'scrollZoom': True})

    with tab2:
        st.subheader("📋 İşlenmiş Telemetri Kayıtları")
        st.dataframe(df_processed, use_container_width=True)
        csv = df_processed.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Temizlenmiş Veriyi İndir", data=csv, file_name="kozmik_analiz.csv")