import streamlit as st
import pandas as pd

def render_anomaly_log(df_processed, column_name):
    if 'is_outlier' not in df_processed.columns:
        return

    hatalar = df_processed[df_processed['is_outlier'] == True].copy()
    
    st.markdown(f"""
        <div style='border-left: 4px solid #ff4444; padding-left: 10px; margin-top: 15px; margin-bottom: 5px;'>
            <p style='color: #00ffcc; font-weight: bold; margin-bottom: 0px; font-family: monospace; font-size: 1.1rem;'>
                🚀 {column_name.upper()} ANOMALİ KAYITLARI
            </p>
        </div>
    """, unsafe_allow_html=True)

    # TABLO HER ZAMAN ÇİZİLECEK
    html = """
    <style>
        .log-container { 
            max-height: 230px; 
            overflow-y: auto; 
            border: 1px solid #30363d; border-radius: 8px; background: #0d1117; 
        }
        .log-container::-webkit-scrollbar { width: 6px; }
        .log-container::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
        .log-table { width: 100%; border-collapse: collapse; font-family: monospace; }
        .log-table th { background: #161b22; color: #8b949e; padding: 10px; text-align: left; font-size: 1rem; border-bottom: 2px solid #30363d; position: sticky; top: 0; }
        .log-table td { padding: 10px; border-bottom: 1px solid #21262d; font-size: 1.1rem; font-weight: bold; }
        .tc-time { color: #00ffcc; }       
        .tc-raw { color: #d32f2f; }        
        .tc-clean { color: #2e7d32; }      
        .tc-empty { color: #00ff88; text-align: center; }
    </style>
    <div class="log-container">
    <table class="log-table">
        <thead><tr><th>ZAMAN</th><th>HAM VERİ</th><th>DÜZELTİLEN</th></tr></thead>
        <tbody>
    """
    
    if not hatalar.empty:
        if 'time_tag' in hatalar.columns:
            hatalar['show_time'] = hatalar['time_tag'].dt.strftime('%H:%M:%S')
        else:
            hatalar['show_time'] = hatalar.index.astype(str)
            
        hatalar = hatalar.sort_values(by='show_time', ascending=False)
        
        for _, row in hatalar.iterrows():
            ham = round(float(row[column_name]), 2)
            duz = round(float(row['cleaned_value']), 2)
            html += f"<tr><td class='tc-time'>{row['show_time']}</td><td class='tc-raw'>{ham}</td><td class='tc-clean'>{duz}</td></tr>"
    else:
        # EĞER HATA YOKSA TABLO BOŞ KALMASIN DİYE BU YAZACAK
        html += "<tr><td colspan='3' class='tc-empty'>✅ Anomali Tespit Edilmedi - Veri Akışı Stabil</td></tr>"
        
    html += "</tbody></table></div><br>"
    st.markdown(html, unsafe_allow_html=True)