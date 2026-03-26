import streamlit as st
import pandas as pd
import numpy as np
# 1. KENDİ DOSYAMIZI İÇERİ ALIYORUZ
from processing import TelemetryProcessor 

st.set_page_config(page_title="Kozmik Pipeline", layout="wide")

# --- SIDEBAR (YAN MENÜ) ---
with st.sidebar:
    st.title("🛰️ Kontrol Paneli")
    st.info("Algoritma hassasiyetini buradan ayarlayabilirsiniz.")
    
    # Kullanıcıya seçim şansı verelim
    esik_degeri = st.slider("Z-Score Eşik Değeri (Hassasiyet)", 1.0, 10.0, 3.5, step=0.1)
    pencere_boyutu = st.slider("Medyan Filtre Penceresi", 3, 15, 5, step=2)

st.title("🚀 Kozmik Veri Ayıklama ve İşleme Hattı")

yuklenen_dosya = st.file_uploader("Temizlenecek CSV dosyasını seçin", type="csv")

if yuklenen_dosya is not None:
    df = pd.read_csv(yuklenen_dosya)
    
    # --- İŞLEME KATMANI (BEYİN BURASI) ---
    # 2. Sınıfımızı sidebar'dan gelen değerle oluşturuyoruz
    processor = TelemetryProcessor(threshold=esik_degeri)
    
    # 3. Temizleme işlemini başlatıyoruz
    df_processed = processor.clean_telemetry(df)
    
    # --- UI/UX METRİKLER ---
    hata_sayisi = df_processed['is_outlier'].sum()
    hata_orani = (hata_sayisi / len(df_processed)) * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("Toplam Veri", len(df_processed))
    m2.metric("Tespit Edilen Hata", hata_sayisi, delta=f"%{hata_orani:.2f}", delta_color="inverse")
    m3.metric("Durum", "Filtrelendi", delta="Aktif")

    # --- GÖRSELLEŞTİRME ---
    st.divider()
    
    tab1, tab2 = st.tabs(["📊 Karşılaştırmalı Grafik", "📋 Ham Veri Tablosu"])
    
    with tab1:
        # Profesyonel Karşılaştırma Grafiği
        # Streamlit line_chart birden fazla sütunu aynı anda çizebilir
        grafik_data = df_processed[['raw_value', 'cleaned_value']]
        st.line_chart(grafik_data)
        st.caption("Mavi: Ham Veri | Turuncu: Temizlenmiş Veri")

    with tab2:
        st.dataframe(df_processed, use_container_width=True)

    # 4. İNDİRME BUTONU
    st.divider()
    csv = df_processed.to_csv(index=False).encode('utf-8')
    st.download_button("✅ Temizlenmiş Veriyi İndir", data=csv, file_name="kozmik_sonuc.csv")