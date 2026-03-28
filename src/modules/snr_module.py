import streamlit as st
import numpy as np

def calculate_snr(signal, noise):
    # Sıfıra bölmeyi engelle
    if np.mean(noise**2) == 0: return 99.9 # Çok temiz sinyal
    return 10 * np.log10(np.mean(signal**2) / np.mean(noise**2))

def render_snr_ui(df, column_name):
    """
    Bu fonksiyon app.py içinden çağrılır.
    Kritik Not: app.py'da hizalamanın bozulmaması için 
    SUBHEADER, WRITE, veya Markdown KULLANMA! Sadece st.metric kalsın.
    """
    try:
        # Sinyal: cleaned_value, Gürültü: cleaned_value - kalman_value
        signal = df['cleaned_value']
        noise = df['cleaned_value'] - df['kalman_value']
        
        # Hesaplamayı yap
        snr_value = calculate_snr(signal, noise)
        
        # 🔥 SADECE BU SATIR KALACAK!
        st.metric(f"📡 {column_name.upper()} SNR", f"{snr_value:.1f} dB")
        
    except Exception as e:
        # Hata durumunda bile hizalamayı bozmayacak sade bir mesaj
        st.metric(f"📡 {column_name.upper()} SNR", "Hata")