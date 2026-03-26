import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Kozmik Pipeline", layout="wide")
st.title("🚀 Kozmik Veri Ayıklama ve İşleme Hattı")

yuklenen_dosya = st.file_uploader("Lütfen temizlenecek CSV dosyasını seçin", type="csv")

if yuklenen_dosya is not None:
    df = pd.read_csv(yuklenen_dosya)
    
    # --- İŞLEME (ALGORİTMA) KATMANI ---
    # 1. Z-Score Hesapla: (Veri - Ortalama) / Standart Sapma
    esik_degeri = 3.0 # Bu değerden büyükse "bozuk" kabul ediyoruz
    ortalama = df['raw_value'].mean()
    sapma = df['raw_value'].std()
    
    df['z_score'] = (df['raw_value'] - ortalama) / sapma
    
    # 2. Bozuk Verileri Tespit Et ve İşaretle
    df['is_outlier'] = df['z_score'].abs() > esik_degeri
    
    # 3. DÜZELTME: Bozuk olanların yerine medyan değeri yaz
    df['cleaned_value'] = df['raw_value'].copy()
    medyan_deger = df['raw_value'].median()
    df.loc[df['is_outlier'], 'cleaned_value'] = medyan_deger
    
    # --- GÖRSELLEŞTİRME KATMANI ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Ham Veri (Bozuk)")
        st.line_chart(df['raw_value'])
        
    with col2:
        st.subheader("🟢 Temizlenmiş Veri (Düzenlenmiş)")
        st.line_chart(df['cleaned_value'])

    # 4. RAPORLAMA VE İNDİRME
    st.divider()
    toplam_hata = df['is_outlier'].sum()
    st.warning(f"Sistem toplam {toplam_hata} adet kozmik radyasyon hatası tespit etti ve düzeltti!")
    
    # Temizlenmiş dosyayı indirilebilir yap
    csv = df[['timestamp', 'cleaned_value']].to_csv(index=False).encode('utf-8')
    st.download_button("✅ Temizlenmiş CSV Dosyasını İndir", data=csv, file_name="temiz_veri.csv")