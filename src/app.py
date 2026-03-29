import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from processing import TelemetryProcessor
import requests
import time
import json
from datetime import datetime
from modules import snr_module
from modules import log_module

st.set_page_config(page_title="ST∞RK — Kozmik Veri", layout="wide", page_icon="🛰️")

# ═══════════════════════════════════════
#  CSS — Full Theme
# ═══════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;500;600;700;800;900&family=Nunito+Sans:wght@300;400;600;700;800&family=Space+Mono:wght@400;700&display=swap');

/* ══ ANA ARKA PLAN — derin uzay ══ */
.stApp {
    background: #020608;
    color: #ccdae8;
}
/* Yıldız katmanı */
.stApp::before {
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background:
        radial-gradient(1.3px 1.3px at 2% 6%, rgba(255,255,255,.6), transparent),
        radial-gradient(.8px .8px at 6% 48%, rgba(190,215,255,.4), transparent),
        radial-gradient(1.5px 1.5px at 11% 82%, rgba(0,255,220,.28), transparent),
        radial-gradient(1px 1px at 18% 20%, rgba(255,255,255,.35), transparent),
        radial-gradient(.6px .6px at 25% 65%, rgba(170,195,255,.25), transparent),
        radial-gradient(1.1px 1.1px at 33% 10%, rgba(255,255,255,.42), transparent),
        radial-gradient(.7px .7px at 40% 42%, rgba(0,190,255,.22), transparent),
        radial-gradient(1px 1px at 48% 76%, rgba(255,255,255,.3), transparent),
        radial-gradient(1.4px 1.4px at 56% 4%, rgba(200,230,255,.48), transparent),
        radial-gradient(.5px .5px at 62% 36%, rgba(255,255,255,.2), transparent),
        radial-gradient(1px 1px at 68% 60%, rgba(0,255,195,.18), transparent),
        radial-gradient(.8px .8px at 76% 16%, rgba(255,255,255,.32), transparent),
        radial-gradient(1.2px 1.2px at 83% 72%, rgba(175,215,255,.28), transparent),
        radial-gradient(.5px .5px at 89% 28%, rgba(255,255,255,.22), transparent),
        radial-gradient(.7px .7px at 94% 86%, rgba(195,195,255,.2), transparent),
        radial-gradient(.4px .4px at 14% 38%, rgba(255,255,255,.16), transparent),
        radial-gradient(.5px .5px at 44% 54%, rgba(255,255,255,.14), transparent),
        radial-gradient(.6px .6px at 71% 40%, rgba(255,255,255,.16), transparent),
        radial-gradient(.3px .3px at 52% 90%, rgba(255,255,255,.12), transparent),
        radial-gradient(.4px .4px at 86% 50%, rgba(200,215,255,.14), transparent),
        radial-gradient(.35px .35px at 22% 55%, rgba(255,255,255,.1), transparent),
        radial-gradient(.45px .45px at 37% 28%, rgba(255,255,255,.12), transparent),
        radial-gradient(.3px .3px at 78% 45%, rgba(255,255,255,.1), transparent),
        radial-gradient(.55px .55px at 58% 68%, rgba(180,210,255,.12), transparent),
        radial-gradient(.3px .3px at 92% 12%, rgba(255,255,255,.1), transparent);
}
/* Nebula glow */
.stApp::after {
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background:
        radial-gradient(ellipse 700px 450px at 10% 78%, rgba(6,30,80,.14), transparent),
        radial-gradient(ellipse 500px 320px at 85% 15%, rgba(0,45,100,.1), transparent),
        radial-gradient(ellipse 900px 500px at 50% 50%, rgba(2,10,30,.1), transparent);
}

/* ══ GİRİŞ EKRANI ══ */
.intro-wrap {
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    min-height:70vh; text-align:center; position:relative; z-index:1;
}
.intro-title {
    font-family:'Exo 2',sans-serif; font-weight:900; font-size:6rem;
    letter-spacing:28px; color:#eaf2ff;
    text-shadow: 0 0 80px rgba(0,180,255,.3), 0 0 160px rgba(0,160,255,.1), 0 2px 4px rgba(0,0,0,.4);
    margin-bottom:24px;
}
.intro-box {
    background:rgba(4,12,24,.45); backdrop-filter:blur(18px);
    border:1px solid rgba(0,255,255,.08); border-radius:20px;
    padding:36px 56px; max-width:580px; margin-bottom:0;
}
.intro-subtitle {
    font-family:'Exo 2',sans-serif; font-weight:600; font-size:1.15rem;
    color:#9cb4cc; letter-spacing:3.5px; text-transform:uppercase;
    line-height:1.8; margin:0;
}

/* ══ SIDEBAR — %60+ transparan ══ */
section[data-testid="stSidebar"] {
    background: rgba(2,5,12,.55) !important;
    border-right: 1px solid rgba(0,255,255,.05) !important;
    backdrop-filter: blur(28px) !important;
    -webkit-backdrop-filter: blur(28px) !important;
}
/* Sidebar butonlar — küçük, zarif */
section[data-testid="stSidebar"] .stButton>button {
    width:100% !important;
    background: rgba(0,255,255,.02) !important;
    border: 1px solid rgba(0,255,255,.07) !important;
    border-radius: 7px !important;
    padding: 7px 10px !important;
    color: #7a98b0 !important;
    font-family: 'Exo 2',sans-serif !important;
    font-weight: 500 !important;
    font-size: .78rem !important;
    letter-spacing: .8px !important;
    text-transform: uppercase !important;
    text-align: center !important;
    transition: all .2s ease !important;
    cursor: pointer !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}
section[data-testid="stSidebar"] .stButton>button:hover {
    background: rgba(0,255,255,.06) !important;
    border-color: rgba(0,255,255,.22) !important;
    color: #00e5cc !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 12px rgba(0,255,255,.05) !important;
}
section[data-testid="stSidebar"] .stButton>button:active,
section[data-testid="stSidebar"] .stButton>button:focus {
    background: rgba(0,255,255,.06) !important;
    border-color: rgba(0,255,255,.2) !important;
    color: #00e5cc !important;
}
/* Aktif sayfa butonu */
section[data-testid="stSidebar"] .active-btn button {
    background: rgba(0,255,255,.08) !important;
    border-color: rgba(0,255,255,.32) !important;
    color: #00ffcc !important;
    font-weight: 600 !important;
    box-shadow: 0 0 14px rgba(0,255,255,.05), inset 0 0 10px rgba(0,255,255,.02) !important;
}
.sidebar-divider {
    border:none; border-top:1px solid rgba(0,255,255,.04);
    margin:14px 6px;
}
.stark-logo {
    font-family:'Exo 2',sans-serif; font-weight:900; font-size:1.4rem;
    text-align:center; padding:14px 0 6px 0; letter-spacing:6px;
    background:linear-gradient(90deg,#00e5ff,#00ffcc,#00e5ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}

/* ══ HEADER ══ */
.page-header-sub {
    font-family:'Space Mono',monospace; color:#00e5cc;
    font-size:.74rem; letter-spacing:3px; text-transform:uppercase;
    margin-bottom:2px; opacity:.8;
}
.page-header {
    font-family:'Exo 2',sans-serif !important;
    font-weight:800 !important; font-size:2rem !important;
    color:#e4eeff !important; letter-spacing:2px;
    margin-top:0 !important; text-transform:uppercase;
}

/* ══ KARTLAR — %60+ transparan ══ */
.stark-card {
    background: rgba(3,8,18,.3);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(0,255,255,.06);
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}
.stark-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,255,255,.2),transparent);
}
.stark-card-title {
    font-family:'Exo 2',sans-serif; font-weight:700; font-size:.95rem;
    color:#00e5cc; letter-spacing:1.5px;
    text-transform:uppercase; margin-bottom:10px;
}
.stark-card p, .stark-card li {
    font-family:'Nunito Sans',sans-serif;
    font-size:.95rem; color:#a0b8ce; line-height:1.8;
}

/* ══ CODE ══ */
.stark-code {
    background:rgba(0,0,0,.3); backdrop-filter:blur(6px);
    border:1px solid rgba(0,255,255,.04);
    border-radius:10px; padding:16px;
    font-family:'Space Mono',monospace;
    font-size:.82rem; color:#82a0b8; line-height:1.9; overflow-x:auto;
}
.stark-code .cmd{color:#00e5cc;font-weight:bold}
.stark-code .comment{color:#445c72}

/* ══ TEAM ══ */
.team-member {
    display:flex; align-items:center; gap:12px; padding:7px 0;
    font-family:'Nunito Sans',sans-serif; font-size:.95rem; color:#b8cede;
}
.team-emoji{font-size:1.2rem}

/* ══ PROCESS ══ */
.process-flow {display:flex;justify-content:center;align-items:center;gap:6px;flex-wrap:wrap;margin:16px 0}
.process-step {
    background:rgba(0,255,255,.025);backdrop-filter:blur(6px);
    border:1px solid rgba(0,255,255,.08);border-radius:10px;padding:14px 18px;
    text-align:center;min-width:120px;transition:all .3s;
}
.process-step:last-child{border-color:rgba(0,255,200,.25);background:rgba(0,255,200,.03)}
.process-step:hover{border-color:rgba(0,255,255,.22);background:rgba(0,255,255,.05);transform:translateY(-2px)}
.process-step .emoji{font-size:1.6rem;margin-bottom:4px}
.process-step .step-title{font-family:'Exo 2',sans-serif;font-weight:700;font-size:.75rem;color:#00e5cc;letter-spacing:.8px}
.process-step .step-desc{font-family:'Nunito Sans',sans-serif;font-size:.72rem;color:#6080a0;margin-top:2px}
.process-arrow{color:rgba(0,255,255,.18);font-size:1.1rem}

/* ══ RESP CARDS ══ */
.resp-cards{display:flex;gap:12px;flex-wrap:wrap}
.resp-card{flex:1;min-width:180px;background:rgba(0,255,255,.02);backdrop-filter:blur(6px);border:1px solid rgba(0,255,255,.07);border-radius:12px;padding:20px;text-align:center;transition:all .3s}
.resp-card:hover{border-color:rgba(0,255,255,.2);background:rgba(0,255,255,.04)}
.resp-card .rc-emoji{font-size:1.6rem;margin-bottom:6px}
.resp-card .rc-title{font-family:'Exo 2',sans-serif;font-weight:700;font-size:.78rem;color:#00e5cc;letter-spacing:.8px;margin-bottom:5px}
.resp-card .rc-desc{font-family:'Nunito Sans',sans-serif;font-size:.82rem;color:#6890aa}

/* ══ CONFIG ══ */
.config-params{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.config-tag{background:rgba(0,255,255,.03);border:1px solid rgba(0,255,255,.08);border-radius:5px;padding:4px 10px;font-family:'Space Mono',monospace;font-size:.78rem}
.config-tag .tag-name{color:#00e5cc}
.config-tag .tag-val{color:#607892}

/* ══ FOLDER ══ */
.folder-item{display:flex;align-items:center;gap:10px;padding:5px 0;font-family:'Space Mono',monospace;font-size:.85rem}
.folder-item .fi-icon{font-size:1rem}
.folder-item .fi-name{color:#00e5cc;font-weight:bold}
.folder-item .fi-desc{color:#6890aa}

/* ══ STREAMLIT OVERRIDES — transparan ══ */
.stMetric {
    background:rgba(3,8,18,.3) !important;
    backdrop-filter:blur(10px) !important;
    border:1px solid rgba(0,255,255,.05) !important;
    border-radius:10px !important; padding:10px !important;
}
.stMetric label{color:#6890aa !important;font-family:'Nunito Sans',sans-serif !important}
.stMetric [data-testid="stMetricValue"]{color:#00e5ff !important;font-family:'Exo 2',sans-serif !important;font-size:1.15rem !important;font-weight:700 !important}
.stExpander {
    border:1px solid rgba(0,255,255,.05) !important;
    background:rgba(3,8,18,.25) !important;
    backdrop-filter:blur(10px) !important;
    border-radius:12px !important;
}
h1,h2,h3{color:#00e5cc !important;font-family:'Exo 2',sans-serif !important}
div[data-testid="stFileUploader"] {
    background:rgba(0,255,255,.015);
    border:1px dashed rgba(0,255,255,.1);
    border-radius:12px; padding:8px;
}

/* ══ GİRİŞ BUTONU (Streamlit button override for intro) ══ */
div[data-testid="stVerticalBlock"] > div:has(> div > button[kind="secondary"]) {
    margin-top: -10px;
}

/* ══ Giriş sayfası ana buton stili ══ */
[data-testid="stButton"] > button[kind="secondary"] {
    font-family: 'Exo 2', sans-serif !important;
}

/* ══ Genel block container margin düzeltmesi ══ */
.block-container { padding-top: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
#  SABİTLER
# ═══════════════════════════════════════
COLORS = {"raw":"#ff4444","cleaned":"#00ff88","kalman":"#00cfff","BIT_FLIP":"#ff00ff","SPIKE":"#ffaa00","DROPOUT":"#ff4444","DRIFT":"#aa44ff"}
DAMAGE_EMOJI = {"BIT_FLIP":"⚡","SPIKE":"📈","DROPOUT":"📉","DRIFT":"🌀","NORMAL":"✅"}

# ═══════════════════════════════════════
#  FONKSİYONLAR
# ═══════════════════════════════════════
def plot_telemetry(df, column, title_prefix="", x_col=None):
    x = df[x_col] if x_col and x_col in df.columns else df.index
    fig = make_subplots(rows=2,cols=1,shared_xaxes=True,row_heights=[.72,.28],vertical_spacing=.06,
        subplot_titles=(f"📡 {title_prefix}{column.upper()} — Ham / Temizlenmiş / Kalman","☢️ Radyasyon Hasar Haritası"))
    fig.add_trace(go.Scatter(x=x,y=df[column],name="🔴 Ham Veri",mode="lines",line=dict(color=COLORS["raw"],width=1.2,dash="dot"),opacity=.6),row=1,col=1)
    fig.add_trace(go.Scatter(x=x,y=df["cleaned_value"],name="🟢 Hampel Temizlenmiş",mode="lines",line=dict(color=COLORS["cleaned"],width=1.8)),row=1,col=1)
    if "kalman_value" in df.columns:
        fig.add_trace(go.Scatter(x=x,y=df["kalman_value"],name="🔵 Kalman Filtreli",mode="lines",line=dict(color=COLORS["kalman"],width=2.2)),row=1,col=1)
    if "damage_type" in df.columns:
        for dt in ["BIT_FLIP","SPIKE","DROPOUT","DRIFT"]:
            m=df["damage_type"]==dt
            if m.sum()==0:continue
            fig.add_trace(go.Scatter(x=x[m],y=df.loc[m,column],name=f"{DAMAGE_EMOJI[dt]} {dt}",mode="markers",
                marker=dict(color=COLORS[dt],size=10,symbol="x",line=dict(color="white",width=1))),row=1,col=1)
        fig.add_trace(go.Bar(x=x,y=[1]*len(df),marker=dict(color=df["damage_type"].map(COLORS).fillna("#333"),line=dict(width=0)),
            showlegend=False,hovertext=df["damage_type"],hoverinfo="text"),row=2,col=1)
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(4,10,22,.35)",
        font=dict(color="#b0c4d8",family="Exo 2, sans-serif"),
        legend=dict(bgcolor="rgba(4,10,22,.6)",bordercolor="rgba(0,255,255,.06)",borderwidth=1,font=dict(size=10)),
        height=560,margin=dict(t=50,b=20,l=10,r=10),dragmode="pan",hovermode="x unified")
    fig.update_xaxes(gridcolor="rgba(0,255,255,.03)",zerolinecolor="rgba(0,255,255,.05)")
    fig.update_yaxes(gridcolor="rgba(0,255,255,.03)",zerolinecolor="rgba(0,255,255,.05)")
    fig.update_yaxes(showticklabels=False,row=2,col=1)
    return fig

def render_damage_metrics(report):
    bd=report.get("damage_breakdown") or {}
    if not bd:return
    cols=st.columns(max(len(bd),1))
    for i,(dt,c) in enumerate(bd.items()):
        cols[i].metric(f"{DAMAGE_EMOJI.get(dt,'🔹')} {dt}",c)

def page_header(sub,title):
    st.markdown(f'<p class="page-header-sub">// {sub}</p><h1 class="page-header">{title}</h1>',unsafe_allow_html=True)

# ═══════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════
if "sayfa" not in st.session_state:
    st.session_state.sayfa = "GIRIS"
if "buffer" not in st.session_state:
    st.session_state.buffer = pd.DataFrame()
if "son_veri_saati" not in st.session_state:
    st.session_state.son_veri_saati = None

def navigate(p):
    st.session_state.sayfa = p

# ═══════════════════════════════════════
#  GİRİŞ EKRANI
# ═══════════════════════════════════════
if st.session_state.sayfa == "GIRIS":
    # Spacer to center vertically
    st.markdown("<div style='height:12vh'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align:center; position:relative; z-index:1;">
        <div class="intro-title">S T A R K</div>
        <div style="display:flex; justify-content:center;">
            <div class="intro-box">
                <p class="intro-subtitle">
                    KOZMİK VERİ AYIKLAMA<br>VE İŞLEME HATTI (PİPELİNE)
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    _, c2, _ = st.columns([1.3, 1, 1.3])
    with c2:
        if st.button("✦  ANASAYFA  ✦", use_container_width=True, key="intro_btn"):
            st.session_state.sayfa = "HAKKINDA"
            st.rerun()
    st.stop()

# ═══════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="stark-logo">ST∞RK</div>', unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)

    for label, key in [("🛸  HAKKINDA","HAKKINDA"),("📋  DÖKÜMANTASYON","DÖKÜMANTASYON"),("🚀  PİPELİNE","PİPELİNE")]:
        if st.session_state.sayfa == key:
            st.markdown('<div class="active-btn">', unsafe_allow_html=True)
        st.button(label, key=f"btn_{key}", on_click=navigate, args=(key,), use_container_width=True)
        if st.session_state.sayfa == key:
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    for label, key in [("⚙️  VERİ İŞLEME & FİLTRELEME","VERİ İŞLEME"),("🟢  NOAA","NOAA")]:
        if st.session_state.sayfa == key:
            st.markdown('<div class="active-btn">', unsafe_allow_html=True)
        st.button(label, key=f"btn_{key}", on_click=navigate, args=(key,), use_container_width=True)
        if st.session_state.sayfa == key:
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← GİRİŞ EKRANI", key="btn_giris", use_container_width=True):
        st.session_state.sayfa = "GIRIS"
        st.rerun()

sayfa = st.session_state.sayfa

# ═══════════════════════════════════════
#  HAKKINDA
# ═══════════════════════════════════════
if sayfa == "HAKKINDA":
    page_header("PROJE HAKKINDA", "HAKKIMIZDA")
    st.markdown("""
    <div class="stark-card">
        <div class="stark-card-title">🛸 HAKKIMIZDA</div>
        <p>STARK ekibi olarak, evrenin derinliklerinden gelen karmaşık telemetri verilerini anlamlı içgörülere dönüştürmek amacıyla yola çıktık. "Kozmik Veri" projemizle; güneş patlamalarından derin uzay sinyallerine kadar geniş bir yelpazedeki ham veriyi modern algoritmalarla işliyor; gerçek zamanlı görselleştirme ve ileri düzey anomali tespit yöntemleriyle geleceğin uzay teknolojilerine ışık tutuyoruz. Bizim için her veri noktası, keşfedilmeyi bekleyen bir yıldızdır.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="stark-card">
        <div class="stark-card-title">🚀 STARK EKİBİ</div>
        <p>Projemizin mutfağında; veriyi kodla, analizi tutkuyla birleştiren beş kişilik dinamik bir kadro yer alıyor:</p>
        <div class="team-member"><span class="team-emoji">🌙</span> Hayat Ay</div>
        <div class="team-member"><span class="team-emoji">🌶️</span> Beray Akar</div>
        <div class="team-member"><span class="team-emoji">🍕</span> Mehmet Ali Kırımlı</div>
        <div class="team-member"><span class="team-emoji">🌟</span> Nihal Eylül İl</div>
        <div class="team-member"><span class="team-emoji">🍊</span> Mert Külekci</div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════
#  DÖKÜMANTASYON
# ═══════════════════════════════════════
elif sayfa == "DÖKÜMANTASYON":
    page_header("PROFESYONEL ÇALIŞMA DİSİPLİNİ", "DÖKÜMANTASYON")
    st.markdown("""<div class="stark-card"><div class="stark-card-title">📋 PROJE DÖKÜMANTASYONU</div><p>STARK olarak sadece kod yazmıyor, bu kodun sürdürülebilir ve geliştirilebilir olması için profesyonel standartlarda bir dökümantasyon yapısı kuruyoruz.</p></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="stark-card"><div class="stark-card-title">NEDEN GEREKLİDİR?</div><p>Projenin iskeletini ekip ruhuna uygun, birbirimizin kodunu bozmadan çalışabileceğimiz bir sistem üzerine inşa ettik.</p></div>""", unsafe_allow_html=True)
    st.markdown("""
    <div class="stark-card">
        <div class="stark-card-title">SİSTEM KURULUMU</div>
        <p>VS Code üzerinden projenin klonlanmasından, gerekli kütüphanelerin tek komutla kurulmasına kadar her adımı standardize ettik.</p>
        <div class="stark-code"><span class="comment"># Projeyi klonla</span><br><span class="cmd">git</span> clone https://github.com/stark-team/kozmik-veri.git<br><span class="cmd">cd</span> kozmik-veri<br><br><span class="comment"># Gerekli kütüphaneleri kur</span><br><span class="cmd">pip</span> install -r requirements.txt<br><br><span class="comment"># requirements.txt içeriği:</span><br><span class="comment"># streamlit, pandas, numpy, plotly, requests</span><br><br><span class="comment"># Uygulamayı başlat</span><br><span class="cmd">streamlit</span> run app.py</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="stark-card">
        <div class="stark-card-title">MODÜLER MİMARİ</div>
        <p>Projemiz tam bir düzen içinde çalışır:</p>
        <div class="folder-item"><span class="fi-icon">📁</span> <span class="fi-name">src/</span> <span class="fi-desc">— Hampel filtresi, Kalman filtresi, SNR modülü</span></div>
        <div class="folder-item"><span class="fi-icon">📁</span> <span class="fi-name">scripts/</span> <span class="fi-desc">— Veri üretimi ve simülasyon scriptleri</span></div>
        <div class="folder-item"><span class="fi-icon">📁</span> <span class="fi-name">data/</span> <span class="fi-desc">— Telemetri kayıtları ve işlenmiş veri setleri</span></div>
        <div class="folder-item"><span class="fi-icon">📄</span> <span class="fi-name">app.py</span> <span class="fi-desc">— Streamlit ana uygulama dosyası</span></div>
        <div class="folder-item"><span class="fi-icon">📄</span> <span class="fi-name">requirements.txt</span> <span class="fi-desc">— Bağımlılık listesi</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="stark-card">
        <div class="stark-card-title">SORUMLULUK PAYLAŞIMI</div>
        <div class="resp-cards">
            <div class="resp-card"><div class="rc-emoji">⚙️</div><div class="rc-title">ALGORİTMA GELİŞTİRME</div><div class="rc-desc">Hampel, Kalman ve SNR algoritmalarının geliştirilmesi ve optimizasyonu</div></div>
            <div class="resp-card"><div class="rc-emoji">📊</div><div class="rc-title">VERİ ANALİZİ</div><div class="rc-desc">NOAA veri akışı, telemetri işleme ve anomali tespiti</div></div>
            <div class="resp-card"><div class="rc-emoji">🎨</div><div class="rc-title">ARAYÜZ TASARIMI</div><div class="rc-desc">Streamlit dashboard, görselleştirme ve kullanıcı deneyimi</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""<div class="stark-card"><div class="stark-card-title">API REFERANSI</div><p>STARK pipeline sınıfı <code style="color:#00e5cc;background:rgba(0,255,255,.05);padding:2px 5px;border-radius:3px">CosmicDataPipeline</code> olarak sunulmaktadır. <code style="color:#00e5cc;background:rgba(0,255,255,.05);padding:2px 5px;border-radius:3px">process(rawSignal)</code> metodu ham sinyali alır; temizlenmiş sinyal, spike bayrakları ve istatistik nesnesini döndürür.</p></div>""", unsafe_allow_html=True)
    st.markdown("""
    <div class="stark-card">
        <div class="stark-card-title">KONFİGÜRASYON PARAMETRELERİ</div>
        <div class="config-params">
            <div class="config-tag"><span class="tag-name">hampelWindow</span> <span class="tag-val">(5)</span></div>
            <div class="config-tag"><span class="tag-name">hampelThresh</span> <span class="tag-val">(3.0)</span></div>
            <div class="config-tag"><span class="tag-name">sgWindow</span> <span class="tag-val">(7)</span></div>
            <div class="config-tag"><span class="tag-name">sgOrder</span> <span class="tag-val">(2)</span></div>
        </div>
        <p style="margin-top:10px">Tüm parametreler çalışma zamanında güncellenebilir.</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════
#  VERİ İŞLEME & FİLTRELEME
# ═══════════════════════════════════════
elif sayfa == "VERİ İŞLEME":
    page_header("VERİ ANALİZ PLATFORMU", "VERİ İŞLEME & FİLTRELEME")
    st.markdown("""<div class="stark-card"><div class="stark-card-title">📂 VERİ YÜKLEME</div><p>CSV veya JSON formatında telemetri verilerinizi yükleyin. Sistem otomatik olarak sayısal sütunları tespit edecek ve Hampel + Kalman filtreleme hattından geçirecektir.</p></div>""", unsafe_allow_html=True)

    yuklenen = st.file_uploader("Veri Dosyasını Seçin (CSV veya JSON)", type=["csv","json"])

    if yuklenen is not None:
        with st.expander("⚙️ Analiz Ayarları", expanded=True):
            ca,cb = st.columns([2,1])
            with ca: esik = st.slider("🎯 Hata Hassasiyeti (Threshold)",1.0,10.0,3.0,step=0.1,key="vi_t")
            with cb: snr_on = st.checkbox("📡 SNR Analizini Göster",value=True,key="vi_s")
        proc = TelemetryProcessor(threshold=esik)
        try:
            if yuklenen.name.endswith(".csv"): df=pd.read_csv(yuklenen)
            else:
                yuklenen.seek(0); data=json.load(yuklenen)
                df=(pd.DataFrame(data[1:],columns=data[0]) if isinstance(data,list) and isinstance(data[0],list) else pd.read_json(yuklenen))
            for c in df.columns:
                if any(k in c.lower() for k in ["time","date"]): df[c]=pd.to_datetime(df[c],errors="coerce")
                else: df[c]=pd.to_numeric(df[c],errors="coerce")
            nums=df.select_dtypes(include=[np.number]).columns.tolist()
            st.markdown(f'<div class="stark-card"><div class="stark-card-title">📊 ANALİZ</div><p><strong style="color:#00e5cc">{len(nums)}</strong> telemetri kanalı tespit edildi.</p></div>',unsafe_allow_html=True)
            for i,s in enumerate(nums):
                with st.expander(f"📉 {s.upper()} ANALİZ PANELİ",expanded=True):
                    d=df.copy(); d[s]=d[s].replace(0,np.nan); d=d.dropna(subset=[s]).reset_index(drop=True)
                    if len(d)>1:
                        dp=proc.clean_telemetry(d,column=s); dp["kalman_value"]=proc.apply_kalman_filter(dp["cleaned_value"])
                        st.divider()
                        m1,m2,m3=st.columns(3); m1.metric("📊 Toplam",f"{len(dp)} Satır")
                        hs=int(dp["is_outlier"].sum()); ho=(hs/len(dp))*100
                        m2.metric("⚠️ Hata",f"{hs}",f"%{ho:.1f}",delta_color="inverse")
                        with m3:
                            if snr_on: snr_module.render_snr_ui(dp,s)
                            else: st.metric("📡 SNR","Kapalı")
                        st.divider(); rp=proc.summary_report(dp,s)
                        r1,r2,r3=st.columns(3)
                        r1.metric("🔇 Gürültü ↓",rp["noise_reduction"]); r2.metric("📊 Anomali",rp["outlier_ratio"]); r3.metric("⚠️ Sayı",rp["outliers_found"])
                        render_damage_metrics(rp); st.divider()
                        zc=None
                        for c in dp.columns:
                            if any(k in c.lower() for k in ["time","date"]): zc=c; break
                        st.plotly_chart(plot_telemetry(dp,s,x_col=zc),use_container_width=True,config={"scrollZoom":True},key=f"s_{i}")
                        log_module.render_anomaly_log(dp,s)
        except Exception as e: st.error(f"⚠️ Hata: {e}")
    else:
        st.markdown('<div class="stark-card" style="text-align:center;padding:40px"><div style="font-size:2.5rem;margin-bottom:8px">📂</div><p style="color:#607892;font-size:1rem">Analiz başlatmak için bir CSV veya JSON dosyası yükleyin.</p></div>',unsafe_allow_html=True)

# ═══════════════════════════════════════
#  NOAA — OTOMATİK BAĞLANTI
# ═══════════════════════════════════════
elif sayfa == "NOAA":
    page_header("UYDU BAĞLANTI MERKEZİ", "NOAA CANLI VERİ")
    with st.expander("⚙️ Analiz Ayarları",expanded=True):
        ca,cb=st.columns([2,1])
        with ca: esik_n=st.slider("🎯 Hata Hassasiyeti",1.0,10.0,3.0,step=0.1,key="n_t")
        with cb: snr_n=st.checkbox("📡 SNR Analizi",value=True,key="n_s")
    proc=TelemetryProcessor(threshold=esik_n)
    _,cr,_=st.columns([1,1,1])
    with cr:
        if st.button("🗑️ Belleği Sıfırla",use_container_width=True):
            st.session_state.buffer=pd.DataFrame(); st.session_state.son_veri_saati=None; st.rerun()
    dur=st.empty()
    try:
        raw=requests.get("https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json",timeout=10).json()
        dfr=pd.DataFrame(raw[1:],columns=raw[0])
        sut=["speed","density","temperature"]
        for c in sut: dfr[c]=pd.to_numeric(dfr[c],errors="coerce")
        dfr["time_tag"]=pd.to_datetime(dfr["time_tag"]); dfr=dfr.dropna(subset=sut).reset_index(drop=True)
        son=dfr["time_tag"].iloc[-1]
        if st.session_state.son_veri_saati!=son:
            st.session_state.son_veri_saati=son; st.session_state.buffer=dfr.tail(60).reset_index(drop=True)
            dur.success(f"🛰️ Yeni Veri: {son}")
        else: dur.info(f"⏳ Bekleniyor… (Son: {son})")
        dl=st.session_state.buffer
        m1,m2,m3=st.columns(3)
        m1.metric("🌬️ Rüzgar",f"{dl['speed'].iloc[-1]:.0f} km/s")
        m2.metric("💧 Yoğunluk",f"{dl['density'].iloc[-1]:.2f} n/cc")
        m3.metric("🌡️ Sıcaklık",f"{dl['temperature'].iloc[-1]:.0f} K")
        for c in sut:
            dp=proc.clean_telemetry(dl,column=c); dp["kalman_value"]=proc.apply_kalman_filter(dp["cleaned_value"])
            if snr_n: snr_module.render_snr_ui(dp,c)
            rp=proc.summary_report(dp,c)
            with st.expander(f"🔬 {c.upper()} Rapor",expanded=False):
                r1,r2,r3=st.columns(3)
                r1.metric("🔇 Gürültü ↓",rp["noise_reduction"]); r2.metric("⚠️ Anomali",rp["outlier_ratio"]); r3.metric("🔢 Sayı",rp["outliers_found"])
                render_damage_metrics(rp)
            st.plotly_chart(plot_telemetry(dp,c,title_prefix="CANLI — ",x_col="time_tag"),use_container_width=True,config={"scrollZoom":True},key=f"l_{c}")
            log_module.render_anomaly_log(dp,c); st.divider()
        time.sleep(5); st.rerun()
    except Exception as e:
        st.error(f"📡 Bağlantı Kesildi: {e}"); time.sleep(5); st.rerun()

# ═══════════════════════════════════════
#  PİPELİNE
# ═══════════════════════════════════════
elif sayfa == "PİPELİNE":
    page_header("ÇOK KATMANLI FİLTRELEME HATTI", "PİPELİNE")
    st.markdown("""<div class="stark-card"><div class="stark-card-title">🚀 KOZMİK VERİ İŞLEME HATTI</div><p>Ham telemetri verisi, işlenmediği sürece sadece gürültüden ibarettir. STARK veri hattı, bu gürültüyü bilimsel birer çıktıya dönüştürür.</p></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="stark-card"><div class="stark-card-title">NEDEN KULLANDIK?</div><p>Kozmik ışınlar ve sensör hataları veride ani sıçramalara yol açar. Bu hataları ayıklamak için çok katmanlı bir "filtreleme hattı" kurduk.</p></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="stark-card"><div class="stark-card-title">⚡ HAMPEL FİLTRESİ</div><p>Verideki ani parazitleri (spike) tespit eden ilk savunma hattımızdır. Medyan Mutlak Sapma (MAD) tabanlı bu algoritma, pencere içindeki her noktayı komşularıyla karşılaştırarak aykırı değerleri işaretler.</p></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="stark-card"><div class="stark-card-title">🔵 ADAPTİF KALMAN FİLTRESİ</div><p>Standart filtrelerin aksine, verinin o anki değişkenliğine (varyansına) göre kendini güncelleyen akıllı bir tahminleme motorudur; gürültüyü minimize ederek "ideal sinyali" üretir.</p></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="stark-card"><div class="stark-card-title">🚨 ANOMALİ SKORLAMA</div><p>Her veri noktasına 0–100 arası bir hasar skoru atayarak, bozulma şüphesini matematiksel olarak kanıtlarız.</p></div>""", unsafe_allow_html=True)
    st.markdown("""
    <div class="stark-card">
        <div class="stark-card-title">5 AŞAMALI İŞLEME HATTI</div>
        <div class="process-flow">
            <div class="process-step"><div class="emoji">🛸</div><div class="step-title">GİRİŞ</div><div class="step-desc">Ham telemetri alım</div></div>
            <div class="process-arrow">→</div>
            <div class="process-step"><div class="emoji">⚡</div><div class="step-title">HAMPEL</div><div class="step-desc">Spike tespiti</div></div>
            <div class="process-arrow">→</div>
            <div class="process-step"><div class="emoji">🔶</div><div class="step-title">İNTERPOL</div><div class="step-desc">Veri kurtarma</div></div>
            <div class="process-arrow">→</div>
            <div class="process-step"><div class="emoji">🔵</div><div class="step-title">KALMAN</div><div class="step-desc">Gürültü azaltma</div></div>
            <div class="process-arrow">→</div>
            <div class="process-step"><div class="emoji">✅</div><div class="step-title">ÇIKIŞ</div><div class="step-desc">Temiz sinyal</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""<div class="stark-card"><div class="stark-card-title">1. AŞAMA — VERİ GİRİŞİ</div><p>Ham telemetri verisi sensörden alınır, zaman damgası eklenir ve sistem tamponuna yazılır. Maksimum giriş hızı: <strong style="color:#00e5cc">10.000 örnek/saniye</strong>.</p></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="stark-card"><div class="stark-card-title">2-3. AŞAMA — SPİKE TESPİTİ VE TEMİZLEME</div><p>Hampel filtresi anomali noktaları işaretler. İnterpolasyon modülü bozuk değerleri komşulardan türetilen tahminlerle doldurur.</p></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="stark-card"><div class="stark-card-title">4-5. AŞAMA — DÜZLEŞTİRME VE ÇIKIŞ</div><p>Savitzky-Golay filtresi artık yüksek frekanslı gürültüyü azaltır. Doğrulama katmanı SNR ve RMSE metriklerini hesaplayarak temiz sinyali çıkış tamponuna yazar.</p></div>""", unsafe_allow_html=True)
