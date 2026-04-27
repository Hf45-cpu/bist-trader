"""
BIST PRO v5.0 — Profesyonel Swing Trading Sistemi
Soft Tema | Robust Hata Yönetimi | Gelişmiş Algoritmalar
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="BIST PRO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── SOFT TEMA ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #e8eef5 50%, #f0f4f8 100%);
        color: #1a2332;
    }
    .main { background: transparent; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e2d42 0%, #243447 100%) !important;
        border-right: 1px solid #2d3f57;
    }
    section[data-testid="stSidebar"] * { color: #c8d8e8 !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label { color: #7a9ab8 !important; font-size: 11px !important; }

    /* Header */
    h1, h2, h3, h4 { color: #1a2332 !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #fff;
        border-radius: 12px;
        padding: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        color: #6b7f96;
        font-weight: 600;
        font-size: 13px;
        border-radius: 8px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: #1e2d42 !important;
        color: #fff !important;
        border-radius: 8px;
    }

    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.3rem !important;
        color: #1a2332 !important;
    }
    div[data-testid="stMetricLabel"] { color: #6b7f96 !important; font-size: 11px !important; }

    /* Cards */
    .pro-card {
        background: #fff;
        border: 1px solid #e2eaf3;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 12px rgba(30,45,66,0.06);
    }
    .pro-card-dark {
        background: linear-gradient(135deg, #1e2d42 0%, #243447 100%);
        border: 1px solid #2d3f57;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(30,45,66,0.15);
    }

    /* Badges */
    .badge-al    { background:#e8f8f1;color:#0d7a4e;border:1px solid #a3d9bf;padding:4px 12px;border-radius:20px;font-weight:700;font-size:12px;font-family:'JetBrains Mono',monospace; }
    .badge-guclu-al { background:#d4f5e7;color:#0a6040;border:1px solid #7dcba5;padding:4px 12px;border-radius:20px;font-weight:800;font-size:12px;font-family:'JetBrains Mono',monospace; }
    .badge-sat   { background:#fde8ec;color:#b02030;border:1px solid #f0a0aa;padding:4px 12px;border-radius:20px;font-weight:700;font-size:12px;font-family:'JetBrains Mono',monospace; }
    .badge-bekle { background:#fff8e6;color:#8a6000;border:1px solid #f0d080;padding:4px 12px;border-radius:20px;font-weight:700;font-size:12px;font-family:'JetBrains Mono',monospace; }

    /* Tablo */
    .styled-table { width:100%;border-collapse:collapse;font-size:12px; }
    .styled-table th { background:#f0f4f8;color:#6b7f96;padding:10px;text-align:left;font-weight:600;border-bottom:2px solid #e2eaf3; }
    .styled-table td { padding:10px;border-bottom:1px solid #f0f4f8;color:#1a2332; }
    .styled-table tr:hover { background:#f8fafc; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #f0f4f8; }
    ::-webkit-scrollbar-thumb { background: #b8c8d8; border-radius: 3px; }

    /* Input */
    .stTextInput input, .stNumberInput input {
        background: #fff !important;
        border: 1px solid #e2eaf3 !important;
        border-radius: 10px !important;
        color: #1a2332 !important;
    }

    /* Progress bar */
    .stProgress .st-bo { background: #4a90c4; }

    div[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

# ─── HİSSE LİSTESİ ────────────────────────────────────────────────────────────
HISSELER = {
    "GARAN": {"isim":"Garanti BBVA","sektor":"Bankacılık"},
    "AKBNK": {"isim":"Akbank","sektor":"Bankacılık"},
    "YKBNK": {"isim":"Yapı Kredi","sektor":"Bankacılık"},
    "ISCTR": {"isim":"İş Bankası C","sektor":"Bankacılık"},
    "VAKBN": {"isim":"Vakıfbank","sektor":"Bankacılık"},
    "HALKB": {"isim":"Halkbank","sektor":"Bankacılık"},
    "ASELS": {"isim":"Aselsan","sektor":"Savunma"},
    "TUPRS": {"isim":"Tüpraş","sektor":"Enerji"},
    "AKSEN": {"isim":"Aksa Enerji","sektor":"Enerji"},
    "THYAO": {"isim":"Türk Hava Yolları","sektor":"Ulaşım"},
    "PGSUS": {"isim":"Pegasus","sektor":"Ulaşım"},
    "KCHOL": {"isim":"Koç Holding","sektor":"Holding"},
    "SAHOL": {"isim":"Sabancı Holding","sektor":"Holding"},
    "EREGL": {"isim":"Ereğli Demir","sektor":"Metal"},
    "FROTO": {"isim":"Ford Otosan","sektor":"Otomotiv"},
    "TOASO": {"isim":"Tofaş Oto","sektor":"Otomotiv"},
    "LOGO":  {"isim":"Logo Yazılım","sektor":"Teknoloji"},
    "INDES": {"isim":"İndeks Bilgisayar","sektor":"Teknoloji"},
    "TCELL": {"isim":"Turkcell","sektor":"Telekom"},
    "SISE":  {"isim":"Şişe Cam","sektor":"Sanayi"},
    "EKGYO": {"isim":"Emlak Konut GYO","sektor":"GYO"},
    "BIMAS": {"isim":"BİM Mağazalar","sektor":"Perakende"},
    "MGROS": {"isim":"Migros","sektor":"Perakende"},
    "PETKM": {"isim":"Petkim","sektor":"Kimya"},
    "KOZAL": {"isim":"Koza Altın","sektor":"Madencilik"},
    "ISGLK": {"isim":"İş Portföy Altın BYF","sektor":"Altın Fonu"},
    "GMSTR": {"isim":"QNB Finans Gümüş BYF","sektor":"Gümüş Fonu"},
    "GLDTR": {"isim":"İstanbul Altın BYF","sektor":"Altın Fonu"},
}

# ─── RENK PALETİ (Soft Tema) ─────────────────────────────────────────────────
C = {
    "bg":     "#f0f4f8",
    "card":   "#ffffff",
    "dark":   "#1e2d42",
    "border": "#e2eaf3",
    "text":   "#1a2332",
    "muted":  "#6b7f96",
    "green":  "#0d7a4e",
    "green2": "#e8f8f1",
    "red":    "#b02030",
    "red2":   "#fde8ec",
    "blue":   "#1a6fa8",
    "blue2":  "#e8f0f8",
    "yel":    "#8a6000",
    "yel2":   "#fff8e6",
    "chart_bg": "#ffffff",
    "grid":   "#f0f4f8",
}

# ─── GÜVENLI İNDİKATÖR HESAPLAMA ─────────────────────────────────────────────
def safe_rsi(series, period=14):
    """Güvenli RSI hesaplama - yeterli veri yoksa None döner"""
    try:
        s = series.dropna()
        if len(s) < period + 2:
            return pd.Series(index=series.index, dtype=float)
        delta = s.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        result = pd.Series(index=series.index, dtype=float)
        result[s.index] = rsi.values
        return result
    except:
        return pd.Series(index=series.index, dtype=float)

def safe_ema(series, period):
    """Güvenli EMA hesaplama"""
    try:
        s = series.dropna()
        if len(s) < period:
            return pd.Series(index=series.index, dtype=float)
        ema = s.ewm(span=period, min_periods=period).mean()
        result = pd.Series(index=series.index, dtype=float)
        result[s.index] = ema.values
        return result
    except:
        return pd.Series(index=series.index, dtype=float)

def safe_sma(series, period):
    """Güvenli SMA hesaplama"""
    try:
        return series.rolling(window=period, min_periods=period).mean()
    except:
        return pd.Series(index=series.index, dtype=float)

def safe_atr(high, low, close, period=14):
    """Güvenli ATR hesaplama - IndexError düzeltildi"""
    try:
        h = high.dropna(); l = low.dropna(); c = close.dropna()
        common = h.index.intersection(l.index).intersection(c.index)
        if len(common) < period + 2:
            return pd.Series(index=close.index, dtype=float)
        h, l, c = h[common], l[common], c[common]
        prev_c = c.shift(1)
        tr = pd.concat([
            h - l,
            (h - prev_c).abs(),
            (l - prev_c).abs()
        ], axis=1).max(axis=1)
        atr = tr.ewm(com=period - 1, min_periods=period).mean()
        result = pd.Series(index=close.index, dtype=float)
        result[common] = atr.values
        return result
    except:
        return pd.Series(index=close.index, dtype=float)

def safe_bollinger(series, period=20, std=2):
    """Güvenli Bollinger hesaplama"""
    try:
        sma = series.rolling(window=period, min_periods=period).mean()
        std_dev = series.rolling(window=period, min_periods=period).std()
        return sma + std * std_dev, sma, sma - std * std_dev
    except:
        nan_s = pd.Series(index=series.index, dtype=float)
        return nan_s, nan_s, nan_s

def safe_macd(series, fast=12, slow=26, signal=9):
    """Güvenli MACD hesaplama"""
    try:
        if len(series.dropna()) < slow + signal:
            nan_s = pd.Series(index=series.index, dtype=float)
            return nan_s, nan_s, nan_s
        ema_fast = series.ewm(span=fast, min_periods=fast).mean()
        ema_slow = series.ewm(span=slow, min_periods=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, min_periods=signal).mean()
        hist = macd_line - signal_line
        return macd_line, signal_line, hist
    except:
        nan_s = pd.Series(index=series.index, dtype=float)
        return nan_s, nan_s, nan_s

def safe_stoch(high, low, close, k=14, d=3):
    """Güvenli Stochastic hesaplama"""
    try:
        if len(close.dropna()) < k + d:
            nan_s = pd.Series(index=close.index, dtype=float)
            return nan_s, nan_s
        lowest = low.rolling(k, min_periods=k).min()
        highest = high.rolling(k, min_periods=k).max()
        k_pct = 100 * (close - lowest) / (highest - lowest).replace(0, np.nan)
        d_pct = k_pct.rolling(d, min_periods=d).mean()
        return k_pct, d_pct
    except:
        nan_s = pd.Series(index=close.index, dtype=float)
        return nan_s, nan_s

def safe_adx(high, low, close, period=14):
    """Güvenli ADX hesaplama"""
    try:
        if len(close.dropna()) < period * 2:
            nan_s = pd.Series(index=close.index, dtype=float)
            return nan_s, nan_s, nan_s
        up = high.diff()
        down = -low.diff()
        plus_dm = up.where((up > down) & (up > 0), 0)
        minus_dm = down.where((down > up) & (down > 0), 0)
        atr = safe_atr(high, low, close, period)
        atr_r = atr.replace(0, np.nan)
        plus_di = 100 * (plus_dm.ewm(com=period-1, min_periods=period).mean() / atr_r)
        minus_di = 100 * (minus_dm.ewm(com=period-1, min_periods=period).mean() / atr_r)
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
        adx = dx.ewm(com=period-1, min_periods=period).mean()
        return adx, plus_di, minus_di
    except:
        nan_s = pd.Series(index=close.index, dtype=float)
        return nan_s, nan_s, nan_s

def safe_vwap(high, low, close, volume):
    """Güvenli VWAP hesaplama"""
    try:
        typical = (high + low + close) / 3
        vol = volume.replace(0, np.nan)
        return (typical * vol).cumsum() / vol.cumsum()
    except:
        return pd.Series(index=close.index, dtype=float)

def safe_mfi(high, low, close, volume, period=14):
    """Güvenli Money Flow Index"""
    try:
        if len(close.dropna()) < period + 2:
            return pd.Series(index=close.index, dtype=float)
        typical = (high + low + close) / 3
        raw_mf = typical * volume
        diff = typical.diff()
        pos_mf = raw_mf.where(diff > 0, 0).rolling(period, min_periods=period).sum()
        neg_mf = raw_mf.where(diff < 0, 0).rolling(period, min_periods=period).sum()
        mfr = pos_mf / neg_mf.replace(0, np.nan)
        return 100 - (100 / (1 + mfr))
    except:
        return pd.Series(index=close.index, dtype=float)

def safe_psar(high, low, close, af=0.02, max_af=0.2):
    """Güvenli Parabolic SAR"""
    try:
        n = len(close)
        if n < 10:
            return pd.Series(index=close.index, dtype=float)
        psar = close.copy().astype(float)
        bull = True
        iaf = af
        ep = low.iloc[0]
        hp = high.iloc[0]
        lp = low.iloc[0]
        for i in range(2, n):
            if bull:
                psar.iloc[i] = psar.iloc[i-1] + iaf * (hp - psar.iloc[i-1])
            else:
                psar.iloc[i] = psar.iloc[i-1] + iaf * (lp - psar.iloc[i-1])
            reverse = False
            if bull:
                if low.iloc[i] < psar.iloc[i]:
                    bull = False; reverse = True
                    psar.iloc[i] = hp
                    lp = low.iloc[i]; iaf = af
            else:
                if high.iloc[i] > psar.iloc[i]:
                    bull = True; reverse = True
                    psar.iloc[i] = lp
                    hp = high.iloc[i]; iaf = af
            if not reverse:
                if bull:
                    if high.iloc[i] > hp: hp = high.iloc[i]; iaf = min(iaf+af, max_af)
                    if low.iloc[i-1] < psar.iloc[i]: psar.iloc[i] = low.iloc[i-1]
                    if low.iloc[i-2] < psar.iloc[i]: psar.iloc[i] = low.iloc[i-2]
                else:
                    if low.iloc[i] < lp: lp = low.iloc[i]; iaf = min(iaf+af, max_af)
                    if high.iloc[i-1] > psar.iloc[i]: psar.iloc[i] = high.iloc[i-1]
                    if high.iloc[i-2] > psar.iloc[i]: psar.iloc[i] = high.iloc[i-2]
        return psar
    except:
        return pd.Series(index=close.index, dtype=float)

def safe_williams_r(high, low, close, period=14):
    """Güvenli Williams %R"""
    try:
        hh = high.rolling(period, min_periods=period).max()
        ll = low.rolling(period, min_periods=period).min()
        return -100 * (hh - close) / (hh - ll).replace(0, np.nan)
    except:
        return pd.Series(index=close.index, dtype=float)

def safe_cci(high, low, close, period=20):
    """Güvenli CCI"""
    try:
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(period, min_periods=period).mean()
        mad = tp.rolling(period, min_periods=period).apply(
            lambda x: np.abs(x - x.mean()).mean(), raw=True)
        return (tp - sma_tp) / (0.015 * mad.replace(0, np.nan))
    except:
        return pd.Series(index=close.index, dtype=float)

# ─── TEMEL ANALİZ HESAPLAMALARı ─────────────────────────────────────────────
def momentum_skoru(closes):
    """Fiyat momentum skoru — 20/60/120 günlük getiri ağırlıklı"""
    try:
        c = closes.dropna()
        if len(c) < 20: return 0
        m20 = (c.iloc[-1]/c.iloc[-20]-1)*100 if len(c)>=20 else 0
        m60 = (c.iloc[-1]/c.iloc[-60]-1)*100 if len(c)>=60 else 0
        m120 = (c.iloc[-1]/c.iloc[-120]-1)*100 if len(c)>=120 else 0
        return m20*0.5 + m60*0.3 + m120*0.2
    except: return 0

def volatilite_yuzde(closes, period=20):
    """Yıllıklaştırılmış volatilite"""
    try:
        c = closes.dropna()
        if len(c) < period: return None
        gunluk = c.pct_change().dropna()
        return gunluk.tail(period).std() * np.sqrt(252) * 100
    except: return None

def sharpe_benzeri(closes, period=60):
    """Basit Sharpe benzeri oran (risksiz faiz ~%40 varsayımı)"""
    try:
        c = closes.dropna()
        if len(c) < period: return None
        gunluk = c.pct_change().dropna().tail(period)
        yillik_getiri = gunluk.mean() * 252
        yillik_vol = gunluk.std() * np.sqrt(252)
        risksiz = 0.40
        return round((yillik_getiri - risksiz) / yillik_vol, 2) if yillik_vol > 0 else None
    except: return None

def max_drawdown(closes, period=90):
    """Maksimum çekilme hesabı"""
    try:
        c = closes.dropna().tail(period)
        tepe = c.cummax()
        dd = (c - tepe) / tepe * 100
        return round(dd.min(), 2)
    except: return None

def fibonacci_seviyeleri(closes, period=60):
    """Fibonacci geri çekilme seviyeleri"""
    try:
        c = closes.dropna().tail(period)
        yuksek = c.max(); dusuk = c.min()
        aralik = yuksek - dusuk
        return {
            "yuksek": round(yuksek, 2),
            "r_0618": round(yuksek - 0.236 * aralik, 2),
            "r_050":  round(yuksek - 0.382 * aralik, 2),
            "r_0382": round(yuksek - 0.500 * aralik, 2),
            "r_0236": round(yuksek - 0.618 * aralik, 2),
            "dusuk":  round(dusuk, 2),
        }
    except: return {}

# ─── TÜM İNDİKATÖRLERİ HESAPLA ───────────────────────────────────────────────
def indikatör_hesapla(df):
    """Tüm indikatörler — güvenli hesaplama ile"""
    df = df.copy()
    c = df["close"]; h = df["high"]; l = df["low"]; v = df["volume"]

    # Trend
    for p in [9,21,50,200]:
        df[f"ema{p}"] = safe_ema(c, p)
    for p in [20,50]:
        df[f"sma{p}"] = safe_sma(c, p)

    # Momentum
    df["rsi"] = safe_rsi(c, 14)
    df["rsi9"] = safe_rsi(c, 9)
    df["stoch_k"], df["stoch_d"] = safe_stoch(h, l, c)
    df["williams_r"] = safe_williams_r(h, l, c)
    df["cci"] = safe_cci(h, l, c)
    df["roc"] = c.pct_change(10) * 100

    # MACD
    df["macd"], df["macd_signal"], df["macd_hist"] = safe_macd(c)

    # Volatilite
    df["bb_ust"], df["bb_orta"], df["bb_alt"] = safe_bollinger(c)
    df["bb_width"] = ((df["bb_ust"] - df["bb_alt"]) / df["bb_orta"].replace(0,np.nan) * 100)
    df["atr"] = safe_atr(h, l, c)
    df["atr_pct"] = df["atr"] / c * 100  # ATR yüzdesi

    # Hacim
    df["vwap"] = safe_vwap(h, l, c, v)
    df["mfi"] = safe_mfi(h, l, c, v)
    df["obv"] = (v * np.sign(c.diff())).fillna(0).cumsum()
    df["hacim_ema"] = v.ewm(span=20, min_periods=5).mean()
    df["hacim_oran"] = v / df["hacim_ema"].replace(0, np.nan)

    # Trend gücü
    df["adx"], df["adx_pos"], df["adx_neg"] = safe_adx(h, l, c)

    # Parabolic SAR
    df["psar"] = safe_psar(h, l, c)

    # Diğer
    df["williams_r"] = safe_williams_r(h, l, c)
    df["pivot"] = (h + l + c) / 3
    df["r1"] = 2*df["pivot"] - l
    df["s1"] = 2*df["pivot"] - h
    df["r2"] = df["pivot"] + (h - l)
    df["s2"] = df["pivot"] - (h - l)

    return df

# ─── GELİŞMİŞ SİNYAL ALGORİTMASI ────────────────────────────────────────────
def sinyal_hesapla(df):
    """
    Çok faktörlü sinyal algoritması:
    - Trend skoru (0-30 puan)
    - Momentum skoru (0-25 puan)
    - Volatilite skoru (0-15 puan)
    - Hacim skoru (0-20 puan)
    - Genel momentum (0-10 puan)
    """
    if df is None or len(df) < 30:
        return {"sinyal":"VERİ YOK","puan":0,"sebepler":[],"trend_yon":"—"}

    son = df.iloc[-1]
    onc = df.iloc[-2] if len(df)>1 else son
    puan = 0
    sebepler = []
    trend_yon = "YATAY"

    # ── TREND FAKTÖRÜ (max 30 puan) ──────────────────────
    # EMA200 kontrolü (uzun vade)
    if pd.notna(son["ema200"]):
        if son["close"] > son["ema200"]:
            sebepler.append("✅ Fiyat EMA200 üstünde — uzun vade pozitif"); puan+=4
        else:
            sebepler.append("❌ Fiyat EMA200 altında — uzun vade negatif"); puan-=4

    # EMA21/50 kesişim
    if pd.notna(son["ema21"]) and pd.notna(son["ema50"]):
        if pd.notna(onc["ema21"]) and pd.notna(onc["ema50"]):
            if onc["ema21"]<=onc["ema50"] and son["ema21"]>son["ema50"]:
                sebepler.append("🚀 ALTIN KESİŞ — EMA21, EMA50'yi yukarı kesti!"); puan+=8
                trend_yon = "YUKARI"
            elif onc["ema21"]>=onc["ema50"] and son["ema21"]<son["ema50"]:
                sebepler.append("💀 ÖLÜM KESİŞ — EMA21, EMA50'yi aşağı kesti!"); puan-=8
                trend_yon = "ASAGI"
            elif son["ema21"]>son["ema50"]:
                sebepler.append("✅ EMA21 > EMA50 — kısa vade trend yukarı"); puan+=4
                trend_yon = "YUKARI"
            else:
                sebepler.append("❌ EMA21 < EMA50 — kısa vade trend aşağı"); puan-=4
                trend_yon = "ASAGI"

    # Parabolic SAR
    if pd.notna(son["psar"]):
        if son["close"] > son["psar"]:
            sebepler.append("✅ Parabolic SAR altında — trend yukarı"); puan+=3
        else:
            sebepler.append("❌ Parabolic SAR üstünde — trend aşağı"); puan-=3

    # ADX
    if pd.notna(son["adx"]):
        if son["adx"] > 30:
            if pd.notna(son["adx_pos"]) and son["adx_pos"] > son["adx_neg"]:
                sebepler.append(f"✅ ADX güçlü yukarı trend ({son['adx']:.0f})"); puan+=5
            elif pd.notna(son["adx_neg"]) and son["adx_neg"] > son["adx_pos"]:
                sebepler.append(f"❌ ADX güçlü aşağı trend ({son['adx']:.0f})"); puan-=5
        elif son["adx"] > 20:
            sebepler.append(f"⚠️ ADX orta trend ({son['adx']:.0f})")
        else:
            sebepler.append(f"⚪ ADX zayıf — yatay piyasa ({son['adx']:.0f})")

    # ── MOMENTUM FAKTÖRÜ (max 25 puan) ───────────────────
    # RSI
    if pd.notna(son["rsi"]):
        r = son["rsi"]
        if r < 25: sebepler.append(f"🟢 RSI EKSTrem satılmış ({r:.0f}) — Güçlü al"); puan+=8
        elif r < 35: sebepler.append(f"✅ RSI aşırı satılmış ({r:.0f})"); puan+=5
        elif r < 45: sebepler.append(f"✅ RSI alım bölgesi ({r:.0f})"); puan+=3
        elif r < 55: sebepler.append(f"⚪ RSI nötr ({r:.0f})"); puan+=1
        elif r < 65: sebepler.append(f"⚠️ RSI yükseliyor ({r:.0f})"); puan-=2
        elif r < 75: sebepler.append(f"❌ RSI aşırı alınmış ({r:.0f})"); puan-=5
        else: sebepler.append(f"🔴 RSI EKSTrem alınmış ({r:.0f}) — Güçlü sat"); puan-=8

    # MACD
    if pd.notna(son["macd_hist"]) and pd.notna(onc["macd_hist"]):
        mh = son["macd_hist"]; pmh = onc["macd_hist"]
        if pmh<=0 and mh>0: sebepler.append("✅ MACD yukarı kesiş — Momentum dönüyor"); puan+=6
        elif mh>0 and mh>pmh: sebepler.append("✅ MACD pozitif ve artıyor"); puan+=3
        elif mh>0: sebepler.append("⚪ MACD pozitif bölge"); puan+=1
        elif pmh>=0 and mh<0: sebepler.append("❌ MACD aşağı kesiş"); puan-=6
        elif mh<0: sebepler.append("❌ MACD negatif"); puan-=3

    # Stochastic
    if pd.notna(son["stoch_k"]) and pd.notna(son["stoch_d"]):
        sk = son["stoch_k"]; sd = son["stoch_d"]
        if sk<20 and sk>sd: sebepler.append("✅ Stochastic aşırı satılmış + yukarı"); puan+=4
        elif sk>80 and sk<sd: sebepler.append("❌ Stochastic aşırı alınmış + aşağı"); puan-=4
        elif sk<30: sebepler.append("✅ Stochastic düşük bölge"); puan+=2
        elif sk>70: sebepler.append("❌ Stochastic yüksek bölge"); puan-=2

    # ── VOLATİLİTE FAKTÖRÜ (max 15 puan) ─────────────────
    # Bollinger
    if pd.notna(son["bb_alt"]) and pd.notna(son["bb_ust"]):
        if son["close"] < son["bb_alt"]:
            sebepler.append("✅ Alt Bollinger altında — dip bölgesi"); puan+=5
        elif son["close"] > son["bb_ust"]:
            sebepler.append("❌ Üst Bollinger üstünde — tepe bölgesi"); puan-=5

    # BB Sıkışma
    if pd.notna(son["bb_width"]):
        if son["bb_width"] < 4:
            sebepler.append("⚡ BOLLİNGER SIKIŞMA — Büyük hareket yaklaşıyor!")

    # ── HACİM FAKTÖRÜ (max 20 puan) ──────────────────────
    # VWAP
    if pd.notna(son["vwap"]):
        if son["close"] > son["vwap"]:
            sebepler.append("✅ Fiyat VWAP üstünde — kurumsal alım bölgesi"); puan+=3
        else:
            sebepler.append("❌ Fiyat VWAP altında"); puan-=3

    # MFI
    if pd.notna(son["mfi"]):
        mf = son["mfi"]
        if mf<20: sebepler.append("✅ MFI aşırı satılmış — para girişi bekleniyor"); puan+=5
        elif mf<35: sebepler.append("✅ MFI düşük bölge"); puan+=2
        elif mf>80: sebepler.append("❌ MFI aşırı alınmış — para çıkışı riski"); puan-=5
        elif mf>65: sebepler.append("❌ MFI yüksek bölge"); puan-=2

    # Hacim teyidi
    if pd.notna(son["hacim_oran"]):
        ho = son["hacim_oran"]
        if ho>2.5 and puan>0: sebepler.append(f"🚀 HACİM {ho:.1f}x — Çok güçlü teyit!"); puan+=7
        elif ho>1.8 and puan>0: sebepler.append(f"✅ Hacim {ho:.1f}x — Güçlü teyit"); puan+=4
        elif ho>1.3 and puan>0: sebepler.append(f"✅ Hacim {ho:.1f}x — Teyit"); puan+=2
        elif ho<0.5: sebepler.append("⚠️ Düşük hacim — sinyal zayıf olabilir")

    # ── GENEL MOMENTUM (max 10 puan) ─────────────────────
    mom = momentum_skoru(df["close"])
    if mom > 20: sebepler.append(f"✅ Güçlü fiyat momentumu (+{mom:.1f}%)"); puan+=4
    elif mom > 10: sebepler.append(f"✅ Pozitif momentum (+{mom:.1f}%)"); puan+=2
    elif mom < -20: sebepler.append(f"❌ Güçlü negatif momentum ({mom:.1f}%)"); puan-=4
    elif mom < -10: sebepler.append(f"❌ Negatif momentum ({mom:.1f}%)"); puan-=2

    # ── KARAR ────────────────────────────────────────────
    if puan>=15:    sinyal="🚀 GÜÇLÜ AL"
    elif puan>=8:   sinyal="🟢 AL"
    elif puan>=3:   sinyal="🔵 ZAYIF AL"
    elif puan<=-15: sinyal="🔴 GÜÇLÜ SAT"
    elif puan<=-8:  sinyal="🔴 SAT"
    elif puan<=-3:  sinyal="🟠 ZAYIF SAT"
    else:           sinyal="⚪ BEKLE"

    return {
        "sinyal":sinyal,"puan":puan,"sebepler":sebepler,
        "trend_yon":trend_yon,
        "rsi":son.get("rsi"),"ema21":son.get("ema21"),"ema50":son.get("ema50"),
        "ema200":son.get("ema200"),"macd_hist":son.get("macd_hist"),
        "adx":son.get("adx"),"atr":son.get("atr"),"atr_pct":son.get("atr_pct"),
        "vwap":son.get("vwap"),"bb_alt":son.get("bb_alt"),"bb_ust":son.get("bb_ust"),
        "stoch_k":son.get("stoch_k"),"mfi":son.get("mfi"),"psar":son.get("psar"),
        "pivot":son.get("pivot"),"r1":son.get("r1"),"s1":son.get("s1"),
        "r2":son.get("r2"),"s2":son.get("s2"),
        "bb_width":son.get("bb_width"),
        "momentum_skoru": round(mom,1),
    }

# ─── VERİ ÇEKME ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=900)
def veri_cek(kod, period="1y"):
    """Yahoo Finance'den veri çek — 1 aylık yeterli veri garantisi ile"""
    try:
        # 1 ay için de yeterli veri çekmek adına min 3mo kullan
        gercek_period = "3mo" if period == "1mo" else period
        df = yf.Ticker(f"{kod}.IS").history(period=gercek_period)
        if df.empty:
            # BYF için sembol farklı olabilir
            df = yf.Ticker(f"{kod}.BIST").history(period=gercek_period)
        if df.empty: return None, "Veri bulunamadı"
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df.columns = [c.lower() for c in df.columns]
        # 1 aylık gösterim isteniyorsa filtrele ama hesaplama için tümü kullan
        return df, None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=900)
def endeks_cek():
    semboller = {
        "BIST 100":"XU100.IS","BIST 30":"XU030.IS",
        "USD/TRY":"USDTRY=X","EUR/TRY":"EURTRY=X",
        "Altın":"GC=F","Brent":"BZ=F","VIX":"^VIX"
    }
    sonuc = {}
    for isim, sembol in semboller.items():
        try:
            h = yf.Ticker(sembol).history(period="5d")
            if not h.empty:
                s=h["Close"].iloc[-1]; o=h["Close"].iloc[-2] if len(h)>1 else s
                sonuc[isim]={"deger":s,"degisim":(s-o)/o*100}
        except: pass
    return sonuc

# ─── BACKTEST ─────────────────────────────────────────────────────────────────
def backtest_calistir(df, strateji, sermaye, komisyon, stop_loss, take_profit):
    """Profesyonel backtest motoru — slipaj dahil"""
    df = df.copy().reset_index()
    c = df["close"].values
    h_arr = df["high"].values
    l_arr = df["low"].values

    # İndikatörler
    c_s = pd.Series(c)
    h_s = pd.Series(h_arr)
    l_s = pd.Series(l_arr)

    rsi_s   = safe_rsi(c_s).values
    ema21_s = safe_ema(c_s, 21).values
    ema50_s = safe_ema(c_s, 50).values
    macd_h  = safe_macd(c_s)[2].values
    bb_alt  = safe_bollinger(c_s)[2].values
    bb_ust  = safe_bollinger(c_s)[0].values
    stoch_k = safe_stoch(h_s, l_s, c_s)[0].values
    adx_s   = safe_adx(h_s, l_s, c_s)[0].values
    mfi_s   = safe_mfi(h_s, l_s, c_s, pd.Series(df["volume"].values)).values

    SLIPAJ = 0.001  # %0.1 slipaj varsayımı

    sinyaller = []
    for i in range(len(df)):
        s = None
        try:
            if strateji == "RSI Swing":
                if not np.isnan(rsi_s[i]):
                    if rsi_s[i]<35: s="AL"
                    elif rsi_s[i]>65: s="SAT"

            elif strateji == "EMA Kesişim":
                if i>0 and not np.isnan(ema21_s[i]) and not np.isnan(ema50_s[i]):
                    if ema21_s[i-1]<=ema50_s[i-1] and ema21_s[i]>ema50_s[i]: s="AL"
                    elif ema21_s[i-1]>=ema50_s[i-1] and ema21_s[i]<ema50_s[i]: s="SAT"

            elif strateji == "Bollinger Bandı":
                if not np.isnan(bb_alt[i]):
                    if c[i]<=bb_alt[i]: s="AL"
                    elif c[i]>=bb_ust[i]: s="SAT"

            elif strateji == "MACD + RSI":
                if i>0 and not np.isnan(macd_h[i]) and not np.isnan(rsi_s[i]):
                    if macd_h[i-1]<=0 and macd_h[i]>0 and rsi_s[i]<55: s="AL"
                    elif macd_h[i-1]>=0 and macd_h[i]<0: s="SAT"

            elif strateji == "Stochastic + RSI":
                if not np.isnan(stoch_k[i]) and not np.isnan(rsi_s[i]):
                    if stoch_k[i]<25 and rsi_s[i]<45: s="AL"
                    elif stoch_k[i]>75 and rsi_s[i]>55: s="SAT"

            elif strateji == "ADX Trend":
                if i>0 and not np.isnan(adx_s[i]) and not np.isnan(ema21_s[i]) and not np.isnan(ema50_s[i]):
                    if adx_s[i]>25 and ema21_s[i]>ema50_s[i] and c[i]>ema21_s[i]: s="AL"
                    elif adx_s[i]>25 and ema21_s[i]<ema50_s[i]: s="SAT"

            elif strateji == "MFI + EMA":
                if not np.isnan(mfi_s[i]) and not np.isnan(ema50_s[i]):
                    if mfi_s[i]<25 and c[i]>ema50_s[i]: s="AL"
                    elif mfi_s[i]>75 and c[i]<ema50_s[i]: s="SAT"

            elif strateji == "Kombine (Tüm)":
                if not np.isnan(rsi_s[i]) and not np.isnan(macd_h[i]) and not np.isnan(ema50_s[i]):
                    al_p  = (int(rsi_s[i]<45) + int(c[i]>ema50_s[i]) + int(macd_h[i]>0) +
                             int(not np.isnan(bb_alt[i]) and c[i]<bb_alt[i]*1.02) +
                             int(not np.isnan(stoch_k[i]) and stoch_k[i]<30))
                    sat_p = (int(rsi_s[i]>60) + int(c[i]<ema50_s[i]) + int(macd_h[i]<0) +
                             int(not np.isnan(bb_ust[i]) and c[i]>bb_ust[i]*0.98) +
                             int(not np.isnan(stoch_k[i]) and stoch_k[i]>70))
                    if al_p>=3: s="AL"
                    elif sat_p>=3: s="SAT"
        except: pass
        sinyaller.append(s)

    # Simülasyon
    nakit=sermaye; poz=None; islemler=[]; egri=[sermaye]
    for i in range(1,len(df)):
        row=df.iloc[i]
        if poz:
            gercek_stop  = row["low"]<=poz["alis"]*(1-stop_loss/100)
            gercek_hedef = row["high"]>=poz["alis"]*(1+take_profit/100)
            cf=None; neden=None
            if gercek_stop:
                cf=poz["alis"]*(1-stop_loss/100)*(1-SLIPAJ); neden="Stop-Loss"
            elif gercek_hedef:
                cf=poz["alis"]*(1+take_profit/100)*(1-SLIPAJ); neden="Take-Profit"
            elif sinyaller[i]=="SAT":
                cf=row["close"]*(1-SLIPAJ); neden="Sinyal"
            if cf:
                gelir=poz["adet"]*cf*(1-komisyon/100)
                pnl=gelir-poz["maliyet"]; nakit+=gelir
                islemler.append({
                    "Giriş": str(poz["tarih"])[:10],
                    "Çıkış": str(row.get("Date",row.name))[:10],
                    "Alış ₺": round(poz["alis"],2),
                    "Satış ₺": round(cf,2),
                    "Kâr/Zarar ₺": round(pnl,2),
                    "% Getiri": round(pnl/poz["maliyet"]*100,2),
                    "Neden": neden,
                    "Gün": i-poz["gun"]
                }); poz=None

        if not poz and sinyaller[i]=="AL" and nakit>100:
            giris_f=row["close"]*(1+SLIPAJ)
            kullan=nakit*0.95
            adet=int(kullan/(giris_f*(1+komisyon/100)))
            if adet>0:
                mal=adet*giris_f*(1+komisyon/100); nakit-=mal
                tarih=row.get("Date",row.name)
                poz={"alis":giris_f,"adet":adet,"maliyet":mal,"tarih":tarih,"gun":i}

        portfoy=nakit+(poz["adet"]*row["close"] if poz else 0)
        egri.append(portfoy)

    if poz:
        son=df.iloc[-1]; cf=son["close"]*(1-SLIPAJ)
        gelir=poz["adet"]*cf*(1-komisyon/100); pnl=gelir-poz["maliyet"]; nakit+=gelir
        islemler.append({
            "Giriş":str(poz["tarih"])[:10],"Çıkış":str(son.get("Date",son.name))[:10],
            "Alış ₺":round(poz["alis"],2),"Satış ₺":round(cf,2),
            "Kâr/Zarar ₺":round(pnl,2),"% Getiri":round(pnl/poz["maliyet"]*100,2),
            "Neden":"Dönem Sonu","Gün":len(df)-1-poz["gun"]
        })

    idf=pd.DataFrame(islemler) if islemler else pd.DataFrame()
    son_d=egri[-1]; getiri=(son_d-sermaye)/sermaye*100
    kaz=idf[idf["Kâr/Zarar ₺"]>0] if len(idf) else pd.DataFrame()
    kay=idf[idf["Kâr/Zarar ₺"]<=0] if len(idf) else pd.DataFrame()
    egri_s=pd.Series(egri); dd=(egri_s-egri_s.cummax())/egri_s.cummax()*100; max_dd=dd.min()
    gr=egri_s.pct_change().dropna()
    sharpe=(gr.mean()/gr.std()*np.sqrt(252)) if gr.std()>0 else 0
    al_tut=(c[-1]-c[0])/c[0]*100
    kazanma=len(kaz)/max(len(idf),1)*100

    # Beklenen değer = kazanma_oranı * ort_kazanç + kaybetme_oranı * ort_kayıp
    ort_kaz = kaz["Kâr/Zarar ₺"].mean() if len(kaz) else 0
    ort_kay = kay["Kâr/Zarar ₺"].mean() if len(kay) else 0
    beklenen_deger = (kazanma/100)*ort_kaz + (1-kazanma/100)*ort_kay

    return {
        "islemler":idf,"egri":egri,"sinyaller":sinyaller,
        "ist":{
            "toplam":len(idf),"kazanan":len(kaz),"kaybeden":len(kay),
            "kazanma":round(kazanma,1),"getiri":round(getiri,2),
            "al_tut":round(al_tut,2),"max_dd":round(float(max_dd),2),
            "sharpe":round(float(sharpe),2),"son_deger":round(son_d,2),
            "toplam_pnl":round(idf["Kâr/Zarar ₺"].sum(),2) if len(idf) else 0,
            "ort_kazanc":round(ort_kaz,2),"ort_kayip":round(ort_kay,2),
            "ort_tutma":round(idf["Gün"].mean(),1) if len(idf) else 0,
            "beklenen_deger":round(beklenen_deger,2),
            "profit_factor": round(abs(kaz["Kâr/Zarar ₺"].sum()/kay["Kâr/Zarar ₺"].sum()),2) if len(kay) and kay["Kâr/Zarar ₺"].sum()!=0 else 0,
        }
    }

# ─── SOFT TEMA GRAFİK ─────────────────────────────────────────────────────────
def mumlu_grafik(df, sinyaller=None, goster=None, n=120):
    if goster is None: goster=["EMA21","EMA50","Bollinger"]
    df_g = df.tail(n)
    fig = make_subplots(rows=4,cols=1,shared_xaxes=True,
        row_heights=[0.5,0.15,0.2,0.15],vertical_spacing=0.02)

    # Mum
    fig.add_trace(go.Candlestick(
        x=df_g.index, open=df_g["open"], high=df_g["high"],
        low=df_g["low"], close=df_g["close"],
        increasing_line_color="#0d7a4e", decreasing_line_color="#b02030",
        increasing_fillcolor="#e8f8f1", decreasing_fillcolor="#fde8ec",
        name="Fiyat"), row=1,col=1)

    if "EMA21" in goster and "ema21" in df_g.columns:
        fig.add_trace(go.Scatter(x=df_g.index,y=df_g["ema21"],
            line=dict(color="#1a6fa8",width=1.5),name="EMA21"),row=1,col=1)
    if "EMA50" in goster and "ema50" in df_g.columns:
        fig.add_trace(go.Scatter(x=df_g.index,y=df_g["ema50"],
            line=dict(color="#e67e22",width=1.8),name="EMA50"),row=1,col=1)
    if "EMA200" in goster and "ema200" in df_g.columns:
        fig.add_trace(go.Scatter(x=df_g.index,y=df_g["ema200"],
            line=dict(color="#8e44ad",width=2),name="EMA200"),row=1,col=1)
    if "Bollinger" in goster and "bb_ust" in df_g.columns:
        fig.add_trace(go.Scatter(x=df_g.index,y=df_g["bb_ust"],
            line=dict(color="#7f8c8d",width=1,dash="dot"),name="BB Üst"),row=1,col=1)
        fig.add_trace(go.Scatter(x=df_g.index,y=df_g["bb_alt"],
            line=dict(color="#7f8c8d",width=1,dash="dot"),
            fill="tonexty",fillcolor="rgba(127,140,141,0.05)",name="BB Alt"),row=1,col=1)
    if "VWAP" in goster and "vwap" in df_g.columns:
        fig.add_trace(go.Scatter(x=df_g.index,y=df_g["vwap"],
            line=dict(color="#c0392b",width=1.5,dash="dash"),name="VWAP"),row=1,col=1)
    if "PSAR" in goster and "psar" in df_g.columns:
        fig.add_trace(go.Scatter(x=df_g.index,y=df_g["psar"],
            mode="markers",marker=dict(size=3,color="#e74c3c"),name="PSAR"),row=1,col=1)

    # Sinyaller
    if sinyaller is not None:
        n_siny = len(df_g)
        siny_slice = sinyaller[-n_siny:] if len(sinyaller)>=n_siny else sinyaller
        al_x=[df_g.index[i] for i,s in enumerate(siny_slice) if s=="AL" and i<len(df_g)]
        al_y=[df_g["low"].iloc[i]*0.97 for i,s in enumerate(siny_slice) if s=="AL" and i<len(df_g)]
        sat_x=[df_g.index[i] for i,s in enumerate(siny_slice) if s=="SAT" and i<len(df_g)]
        sat_y=[df_g["high"].iloc[i]*1.03 for i,s in enumerate(siny_slice) if s=="SAT" and i<len(df_g)]
        if al_x: fig.add_trace(go.Scatter(x=al_x,y=al_y,mode="markers",
            marker=dict(symbol="triangle-up",size=12,color="#0d7a4e"),name="AL"),row=1,col=1)
        if sat_x: fig.add_trace(go.Scatter(x=sat_x,y=sat_y,mode="markers",
            marker=dict(symbol="triangle-down",size=12,color="#b02030"),name="SAT"),row=1,col=1)

    # Hacim
    renkler=["#e8f8f1" if c>=o else "#fde8ec"
             for c,o in zip(df_g["close"],df_g["open"])]
    borderkler=["#0d7a4e" if c>=o else "#b02030"
                for c,o in zip(df_g["close"],df_g["open"])]
    fig.add_trace(go.Bar(x=df_g.index,y=df_g["volume"],
        marker_color=renkler,marker_line_color=borderkler,
        marker_line_width=0.5,name="Hacim",opacity=0.8),row=2,col=1)

    # MACD
    if "macd" in df_g.columns:
        fig.add_trace(go.Scatter(x=df_g.index,y=df_g["macd"],
            line=dict(color="#1a6fa8",width=1.5),name="MACD"),row=3,col=1)
        fig.add_trace(go.Scatter(x=df_g.index,y=df_g["macd_signal"],
            line=dict(color="#e67e22",width=1.5),name="Sinyal"),row=3,col=1)
        colors2=["#e8f8f1" if v>=0 else "#fde8ec" for v in df_g["macd_hist"].fillna(0)]
        fig.add_trace(go.Bar(x=df_g.index,y=df_g["macd_hist"],
            marker_color=colors2,name="Hist"),row=3,col=1)

    # RSI
    if "rsi" in df_g.columns:
        fig.add_trace(go.Scatter(x=df_g.index,y=df_g["rsi"],
            line=dict(color="#8e44ad",width=2),name="RSI"),row=4,col=1)
        for level,color in [(70,"#b02030"),(30,"#0d7a4e"),(50,"#aab8c8")]:
            fig.add_hline(y=level,line_color=color,line_dash="dot",
                line_width=1,row=4,col=1)

    fig.update_layout(
        paper_bgcolor="#ffffff",plot_bgcolor="#fafbfc",
        font=dict(color="#6b7f96",family="Plus Jakarta Sans"),
        xaxis_rangeslider_visible=False,height=680,
        showlegend=True,
        legend=dict(bgcolor="#f8fafc",bordercolor="#e2eaf3",
            font=dict(color="#1a2332",size=11),
            orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        margin=dict(l=10,r=10,t=10,b=10))
    fig.update_xaxes(gridcolor="#f0f4f8",showgrid=True,
        linecolor="#e2eaf3",tickfont=dict(size=10))
    fig.update_yaxes(gridcolor="#f0f4f8",showgrid=True,
        linecolor="#e2eaf3",tickfont=dict(size=10))
    return fig

def egri_grafik(egri, al_tut_getiri, sermaye):
    fig = go.Figure()
    al_tut_egri = [sermaye*(1+al_tut_getiri/100*i/max(len(egri)-1,1)) for i in range(len(egri))]
    son = egri[-1]; renk="#0d7a4e" if son>=sermaye else "#b02030"
    fig.add_trace(go.Scatter(y=egri,mode="lines",
        line=dict(color=renk,width=2.5),
        fill="tozeroy",fillcolor=f"rgba({'13,122,78' if son>=sermaye else '176,32,48'},0.08)",
        name="Strateji"))
    fig.add_trace(go.Scatter(y=al_tut_egri,mode="lines",
        line=dict(color="#e67e22",width=1.5,dash="dot"),name="Al-Tut"))
    fig.add_hline(y=sermaye,line_color="#aab8c8",line_dash="dash",line_width=1)
    fig.update_layout(paper_bgcolor="#ffffff",plot_bgcolor="#fafbfc",
        font=dict(color="#6b7f96"),height=220,
        margin=dict(l=10,r=10,t=10,b=10),
        legend=dict(bgcolor="#f8fafc",font=dict(size=11)))
    fig.update_xaxes(gridcolor="#f0f4f8"); fig.update_yaxes(gridcolor="#f0f4f8")
    return fig

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px'>
        <div style='font-size:28px'>📊</div>
        <div style='font-size:20px;font-weight:800;color:#fff;letter-spacing:-0.5px'>BIST PRO</div>
        <div style='font-size:10px;color:#7a9ab8;margin-top:2px'>v5.0 · Profesyonel Analiz</div>
    </div>
    """,unsafe_allow_html=True)

    secilenKod = st.selectbox("Hisse Seç", list(HISSELER.keys()),
        format_func=lambda k:f"{k} — {HISSELER[k]['isim']}")
    period = st.selectbox("Periyot",["3mo","6mo","1y","2y"],index=2,
        format_func=lambda x:{"3mo":"3 Ay","6mo":"6 Ay","1y":"1 Yıl","2y":"2 Yıl"}[x])

    st.markdown("---")
    st.markdown("<div style='color:#7a9ab8;font-size:11px;font-weight:600;margin-bottom:8px'>BACKTEST AYARLARI</div>",unsafe_allow_html=True)
    strateji = st.selectbox("Strateji",[
        "RSI Swing","EMA Kesişim","Bollinger Bandı",
        "MACD + RSI","Stochastic + RSI","ADX Trend","MFI + EMA","Kombine (Tüm)"])
    sermaye = st.number_input("Sermaye (₺)",10000,10000000,100000,10000)
    komisyon = st.slider("Komisyon (%)",0.01,0.50,0.10,0.01)
    stop_loss = st.slider("Stop-Loss (%)",2.0,20.0,8.0,0.5)
    take_profit = st.slider("Take-Profit (%)",5.0,50.0,20.0,1.0)

    st.markdown("---")
    col1,col2 = st.columns(2)
    with col1:
        if st.button("🔄 Yenile",use_container_width=True):
            st.cache_data.clear(); st.rerun()
    with col2:
        import pytz
        TR = pytz.timezone("Europe/Istanbul")
        saat = datetime.now(TR).strftime("%H:%M")
        st.markdown(f"<div style='text-align:center;color:#7a9ab8;font-size:12px;padding:8px'>🕐 {saat}</div>",unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:#152030;border-radius:8px;padding:10px;margin-top:8px'>
        <div style='color:#f39c12;font-size:10px;font-weight:600'>⏱ VERİ GECİKMESİ</div>
        <div style='color:#7a9ab8;font-size:11px;margin-top:3px'>Yahoo Finance · 15 dakika</div>
    </div>
    """,unsafe_allow_html=True)

# ─── ANA SAYFA ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='display:flex;align-items:center;gap:12px;margin-bottom:20px'>
    <div style='background:linear-gradient(135deg,#1e2d42,#2d4060);border-radius:12px;padding:10px 16px;'>
        <span style='font-size:22px;font-weight:800;color:#fff'>{secilenKod}</span>
    </div>
    <div>
        <div style='font-size:18px;font-weight:700;color:#1a2332'>{HISSELER[secilenKod]['isim']}</div>
        <div style='font-size:12px;color:#6b7f96'>{HISSELER[secilenKod]['sektor']} · Yahoo Finance · 15dk gecikmeli</div>
    </div>
</div>
""",unsafe_allow_html=True)

# Veri yükle
with st.spinner(f"📡 {secilenKod} verisi çekiliyor..."):
    df, hata = veri_cek(secilenKod, period)
    endeks = endeks_cek()

if hata or df is None:
    st.error(f"⚠️ Veri alınamadı: {hata or 'Bilinmeyen hata'}")
    st.info("💡 Sembol Yahoo Finance'de desteklenmeyebilir. BYF sembolleri için doğrudan aracı kurum platformunu kullanın.")
    st.stop()

df = indikatör_hesapla(df)
sig = sinyal_hesapla(df)

# Gösterim için filtreleme (hesaplama için tümü kullanıldı)
son = df.iloc[-1]; onc = df.iloc[-2]
degisim = (son["close"]-onc["close"])/onc["close"]*100

# ─── SEKMELER ────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "📈 Analiz","🎯 Sinyaller","⚗️ Backtest","🔍 Tarama","📚 Rehber","📊 İstatistik"])

# ═══ TAB 1: ANALİZ ═══════════════════════════════════════════════════════════
with tab1:
    # Endeks
    if endeks:
        cols = st.columns(len(endeks))
        for i,(isim,v) in enumerate(endeks.items()):
            with cols[i]:
                st.metric(isim,f"{v['deger']:,.2f}",f"{v['degisim']:+.2f}%",
                    delta_color="normal" if v["degisim"]>=0 else "inverse")

    st.markdown("---")

    # Fiyat + Sinyal + Destek/Direnç
    col1,col2,col3 = st.columns([1.5,1,1])
    with col1:
        sinyal_renk = "#0d7a4e" if "AL" in sig["sinyal"] else "#b02030" if "SAT" in sig["sinyal"] else "#8a6000"
        st.markdown(f"""
        <div class='pro-card'>
            <div style='font-size:11px;color:#6b7f96;margin-bottom:6px;font-weight:600'>GÜNCEL FİYAT</div>
            <div style='display:flex;align-items:baseline;gap:12px;margin-bottom:8px'>
                <span style='font-size:42px;font-weight:800;color:#1a2332;font-family:JetBrains Mono,monospace;letter-spacing:-1px'>{son['close']:.2f} ₺</span>
                <span style='font-size:20px;font-weight:700;color:{sinyal_renk}'>{degisim:+.2f}%</span>
            </div>
            <div style='color:#6b7f96;font-size:12px;font-family:JetBrains Mono,monospace'>
                A: {son['open']:.2f} &nbsp; Y: {son['high']:.2f} &nbsp; D: {son['low']:.2f} &nbsp; H: {int(son['volume']):,}
            </div>
        </div>
        """,unsafe_allow_html=True)

    with col2:
        puan_renk = "#0d7a4e" if sig["puan"]>0 else "#b02030" if sig["puan"]<0 else "#8a6000"
        st.markdown(f"""
        <div class='pro-card' style='text-align:center;border-left:4px solid {sinyal_renk}'>
            <div style='font-size:10px;color:#6b7f96;margin-bottom:8px;font-weight:600'>GÜNCEL SİNYAL</div>
            <div style='font-size:22px;font-weight:800;color:{sinyal_renk};margin-bottom:6px'>{sig["sinyal"]}</div>
            <div style='font-size:13px;color:{puan_renk};font-family:JetBrains Mono,monospace;font-weight:700'>Puan: {sig["puan"]:+d} / 30</div>
            <div style='margin-top:8px'>
                <div style='height:6px;background:#f0f4f8;border-radius:3px;overflow:hidden'>
                    <div style='width:{min(100,abs(sig["puan"])/30*100):.0f}%;height:100%;background:{sinyal_renk};border-radius:3px'></div>
                </div>
            </div>
        </div>
        """,unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='pro-card'>
            <div style='font-size:10px;color:#6b7f96;margin-bottom:10px;font-weight:600'>DESTEK / DİRENÇ (Pivot)</div>
            {''.join([
                f"<div style='display:flex;justify-content:space-between;margin-bottom:5px'><span style='color:#b02030;font-size:11px;font-weight:600'>{lbl}</span><span style='color:#1a2332;font-size:11px;font-family:JetBrains Mono,monospace'>{val:.2f} ₺</span></div>"
                if "R" in lbl else
                f"<div style='display:flex;justify-content:space-between;margin-bottom:5px;padding:4px 0;border-top:1px solid #e2eaf3;border-bottom:1px solid #e2eaf3'><span style='color:#1a6fa8;font-size:11px;font-weight:700'>{lbl}</span><span style='color:#1a6fa8;font-size:11px;font-family:JetBrains Mono,monospace;font-weight:700'>{val:.2f} ₺</span></div>"
                if "PİVOT" in lbl else
                f"<div style='display:flex;justify-content:space-between;margin-bottom:5px'><span style='color:#0d7a4e;font-size:11px;font-weight:600'>{lbl}</span><span style='color:#1a2332;font-size:11px;font-family:JetBrains Mono,monospace'>{val:.2f} ₺</span></div>"
                for lbl, val in [
                    ("R2", sig.get("r2",0) or 0),
                    ("R1", sig.get("r1",0) or 0),
                    ("PİVOT", sig.get("pivot",0) or 0),
                    ("S1", sig.get("s1",0) or 0),
                    ("S2", sig.get("s2",0) or 0),
                ] if val
            ])}
        </div>
        """,unsafe_allow_html=True)

    # İndikatör özeti
    st.markdown("### 📊 İndikatör Özeti")
    ci1,ci2,ci3,ci4,ci5,ci6 = st.columns(6)
    def ind_renk(val,dusuk,yuksek,ters=False):
        if val is None or pd.isna(val): return "normal"
        if ters: dusuk,yuksek = yuksek,dusuk
        if val<=dusuk: return "normal"
        if val>=yuksek: return "inverse"
        return "off"

    with ci1:
        rsi_v = sig.get("rsi")
        st.metric("RSI (14)",f"{rsi_v:.1f}" if rsi_v and not pd.isna(rsi_v) else "—",
            "Aşırı satılmış ✓" if rsi_v and rsi_v<30 else "Aşırı alınmış ✗" if rsi_v and rsi_v>70 else "Normal")
    with ci2:
        macd_v = sig.get("macd_hist")
        st.metric("MACD Hist",f"{macd_v:.4f}" if macd_v and not pd.isna(macd_v) else "—",
            "Pozitif ↑" if macd_v and macd_v>0 else "Negatif ↓")
    with ci3:
        adx_v = sig.get("adx")
        st.metric("ADX",f"{adx_v:.1f}" if adx_v and not pd.isna(adx_v) else "—",
            "Güçlü trend" if adx_v and adx_v>25 else "Zayıf")
    with ci4:
        atr_v = sig.get("atr_pct")
        st.metric("ATR %",f"%{atr_v:.2f}" if atr_v and not pd.isna(atr_v) else "—","Günlük volatilite")
    with ci5:
        sk_v = sig.get("stoch_k")
        st.metric("Stoch %K",f"{sk_v:.1f}" if sk_v and not pd.isna(sk_v) else "—",
            "Aşırı sat ✓" if sk_v and sk_v<20 else "Aşırı alın ✗" if sk_v and sk_v>80 else "Normal")
    with ci6:
        mfi_v = sig.get("mfi")
        st.metric("MFI",f"{mfi_v:.1f}" if mfi_v and not pd.isna(mfi_v) else "—",
            "Para girişi ✓" if mfi_v and mfi_v<20 else "Para çıkışı ✗" if mfi_v and mfi_v>80 else "Normal")

    # Grafik
    goster = st.multiselect("Grafik Göstergeleri",
        ["EMA21","EMA50","EMA200","Bollinger","VWAP","PSAR"],
        default=["EMA21","EMA50","Bollinger"])
    st.plotly_chart(mumlu_grafik(df,goster=goster),use_container_width=True)

    # Risk seviyeleri
    st.markdown("### 🎯 Risk / Hedef Seviyeleri")
    atr_val = sig.get("atr") or (son["close"]*0.02)
    rck1,rck2,rck3,rck4,rck5 = st.columns(5)
    with rck1: st.metric("Stop -%8",f"{son['close']*0.92:.2f} ₺",f"-{son['close']*0.08:.2f} ₺",delta_color="inverse")
    with rck2: st.metric("ATR Stop",f"{son['close']-1.5*atr_val:.2f} ₺",f"1.5x ATR",delta_color="inverse")
    with rck3: st.metric("Güncel",f"{son['close']:.2f} ₺",f"{degisim:+.2f}%")
    with rck4: st.metric("Hedef 1 +%15",f"{son['close']*1.15:.2f} ₺",f"+{son['close']*0.15:.2f} ₺")
    with rck5: st.metric("Hedef 2 +%25",f"{son['close']*1.25:.2f} ₺",f"+{son['close']*0.25:.2f} ₺")

    # Fibonacci
    fib = fibonacci_seviyeleri(df["close"])
    if fib:
        st.markdown("#### 📐 Fibonacci Seviyeleri (Son 60 Gün)")
        fib_cols = st.columns(6)
        for i,(k,v) in enumerate(fib.items()):
            labels = {"yuksek":"Yüksek","r_0618":"%23.6","r_050":"%38.2",
                     "r_0382":"%50.0","r_0236":"%61.8","dusuk":"Düşük"}
            with fib_cols[i]:
                renk = "#b02030" if i<2 else "#0d7a4e" if i>3 else "#1a6fa8"
                st.markdown(f"""
                <div style='text-align:center;background:#f8fafc;border-radius:8px;padding:8px;border:1px solid #e2eaf3'>
                    <div style='font-size:9px;color:#6b7f96;font-weight:600'>{labels.get(k,k)}</div>
                    <div style='font-size:13px;font-weight:700;color:{renk};font-family:JetBrains Mono,monospace'>{v} ₺</div>
                </div>
                """,unsafe_allow_html=True)

# ═══ TAB 2: SİNYALLER ════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🎯 Çok Faktörlü Sinyal Analizi")

    col1,col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ Pozitif Sinyaller")
        pozitif = [s for s in sig["sebepler"] if "✅" in s or "🚀" in s or "🟢" in s]
        if pozitif:
            for s in pozitif:
                st.markdown(f"""<div class='pro-card' style='margin-bottom:8px;border-left:3px solid #0d7a4e;padding:10px 14px'>
                    <span style='font-size:13px;color:#1a2332'>{s}</span></div>""",unsafe_allow_html=True)
        else: st.info("Pozitif sinyal yok")

    with col2:
        st.markdown("#### ❌ Negatif Sinyaller")
        negatif = [s for s in sig["sebepler"] if "❌" in s or "🔴" in s or "💀" in s]
        if negatif:
            for s in negatif:
                st.markdown(f"""<div class='pro-card' style='margin-bottom:8px;border-left:3px solid #b02030;padding:10px 14px'>
                    <span style='font-size:13px;color:#1a2332'>{s}</span></div>""",unsafe_allow_html=True)
        else: st.info("Negatif sinyal yok")

    st.markdown("#### ⚠️ Uyarılar / Dikkat")
    for u in [s for s in sig["sebepler"] if "⚠️" in s or "⚡" in s or "⚪" in s]:
        st.markdown(f"""<div class='pro-card' style='margin-bottom:6px;border-left:3px solid #e67e22;padding:8px 14px;background:#fffdf5'>
            <span style='font-size:12px;color:#5d4e00'>{u}</span></div>""",unsafe_allow_html=True)

    # Tüm değerler
    st.markdown("### 📋 Tüm İndikatör Değerleri")
    son = df.iloc[-1]
    def fv(col): 
        try:
            v = son.get(col)
            return f"{v:.4f}" if v is not None and not pd.isna(v) else "—"
        except: return "—"

    ind_data = [
        ["RSI (14)", fv("rsi"), "0-100", "30↓ al, 70↑ sat"],
        ["RSI (9)", fv("rsi9"), "0-100", "Kısa vadeli momentum"],
        ["MACD", fv("macd"), "+ / -", "Trend momentum"],
        ["MACD Sinyal", fv("macd_signal"), "+ / -", "Kesiş sinyali"],
        ["MACD Histogram", fv("macd_hist"), "+ / -", "Momentum gücü"],
        ["Stochastic %K", fv("stoch_k"), "0-100", "20↓ aşırı sat, 80↑ aşırı al"],
        ["Stochastic %D", fv("stoch_d"), "0-100", "Sinyal çizgisi"],
        ["Williams %R", fv("williams_r"), "-100/0", "-80↓ al, -20↑ sat"],
        ["CCI (20)", fv("cci"), "serbest", "-100↓ al, +100↑ sat"],
        ["ROC (10)", fv("roc"), "% oran", "Fiyat değişim hızı"],
        ["MFI (14)", fv("mfi"), "0-100", "20↓ para girişi, 80↑ para çıkışı"],
        ["ADX", fv("adx"), "0-100", "25↑ güçlü trend"],
        ["ADX (+DI)", fv("adx_pos"), "0-100", "Alıcı gücü"],
        ["ADX (-DI)", fv("adx_neg"), "0-100", "Satıcı gücü"],
        ["ATR (14)", fv("atr"), "TL", "Stop-loss için kullan"],
        ["ATR %", fv("atr_pct"), "%", "Günlük volatilite oranı"],
        ["BB Üst", fv("bb_ust"), "TL", "Üst direnç seviyesi"],
        ["BB Orta", fv("bb_orta"), "TL", "SMA20 = orta bant"],
        ["BB Alt", fv("bb_alt"), "TL", "Alt destek seviyesi"],
        ["BB Width", fv("bb_width"), "%", "<4 = sıkışma, büyük hareket yaklaşıyor"],
        ["EMA 9", fv("ema9"), "TL", "Çok kısa vade trend"],
        ["EMA 21", fv("ema21"), "TL", "Kısa vade trend"],
        ["EMA 50", fv("ema50"), "TL", "Orta vade trend"],
        ["EMA 200", fv("ema200"), "TL", "Uzun vade trend"],
        ["SMA 20", fv("sma20"), "TL", "Bollinger orta bant"],
        ["VWAP", fv("vwap"), "TL", "Kurumsal alım/satım seviyesi"],
        ["Parabolic SAR", fv("psar"), "TL", "Fiyat üstünde = sat, altında = al"],
        ["OBV", fv("obv"), "kumulatif", "Hacim eğilimi"],
        ["Pivot", fv("pivot"), "TL", "Ana seviye"],
        ["R1 / R2", f"{fv('r1')} / {fv('r2')}", "TL", "Direnç seviyeleri"],
        ["S1 / S2", f"{fv('s1')} / {fv('s2')}", "TL", "Destek seviyeleri"],
    ]
    st.dataframe(
        pd.DataFrame(ind_data, columns=["İndikatör","Değer","Aralık","Yorum"]),
        use_container_width=True, height=550, hide_index=True)

# ═══ TAB 3: BACKTEST ═════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"### ⚗️ {strateji} Backtest — {secilenKod}")
    st.markdown("""<div class='pro-card' style='background:#f8fafc;padding:12px 16px;margin-bottom:12px'>
        <span style='font-size:12px;color:#6b7f96'>⚡ Slipaj (%0.1) ve komisyon dahil · Açık pozisyon dönem sonunda kapatılıyor · Sermayenin %95'i kullanılıyor</span>
    </div>""",unsafe_allow_html=True)

    if st.button("▶ Backtest Çalıştır",type="primary",use_container_width=True):
        with st.spinner("Hesaplanıyor..."):
            bt = backtest_calistir(df,strateji,sermaye,komisyon,stop_loss,take_profit)
            st.session_state["bt"]=bt

    if "bt" in st.session_state:
        bt=st.session_state["bt"]; ist=bt["ist"]

        # Ana metrikler
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: st.metric("Toplam Getiri",f"{ist['getiri']:+.1f}%",
            f"Al-tut: {ist['al_tut']:+.1f}%",
            delta_color="normal" if ist['getiri']>=ist['al_tut'] else "inverse")
        with c2: st.metric("Kazanma Oranı",f"%{ist['kazanma']}",
            f"{ist['kazanan']}K / {ist['kaybeden']}Z")
        with c3: st.metric("Max Drawdown",f"{ist['max_dd']:.1f}%",delta_color="inverse")
        with c4: st.metric("Sharpe Oranı",f"{ist['sharpe']:.2f}",
            "Mükemmel ✓" if ist['sharpe']>=2 else "İyi ✓" if ist['sharpe']>=1 else "Zayıf")
        with c5: st.metric("Profit Factor",f"{ist['profit_factor']:.2f}x",
            "İyi ✓" if ist['profit_factor']>=1.5 else "Zayıf")

        # Sermaye eğrisi
        st.plotly_chart(egri_grafik(bt["egri"],ist["al_tut"],sermaye),use_container_width=True)

        # Detay
        col1,col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 Detaylı İstatistikler")
            for k,v in [
                ("Son Portföy Değeri",f"{ist['son_deger']:,.0f} ₺"),
                ("Toplam Kâr/Zarar",f"{ist['toplam_pnl']:+,.0f} ₺"),
                ("Beklenen Değer/İşlem",f"{ist['beklenen_deger']:+,.0f} ₺"),
                ("Ortalama Kazanç",f"{ist['ort_kazanc']:+,.0f} ₺"),
                ("Ortalama Kayıp",f"{ist['ort_kayip']:+,.0f} ₺"),
                ("Ortalama Tutma",f"{ist['ort_tutma']:.1f} gün"),
                ("Toplam İşlem",str(ist['toplam'])),
            ]:
                ca,cb=st.columns([2,1])
                ca.markdown(f"<span style='color:#6b7f96;font-size:13px'>{k}</span>",unsafe_allow_html=True)
                cb.markdown(f"<span style='color:#1a2332;font-weight:700;font-family:monospace'>{v}</span>",unsafe_allow_html=True)

        with col2:
            fark=ist['getiri']-ist['al_tut']
            renk="#0d7a4e" if fark>=0 else "#b02030"
            st.markdown(f"""
            <div class='pro-card' style='text-align:center;border-top:4px solid {renk}'>
                <div style='font-size:11px;color:#6b7f96;margin-bottom:8px;font-weight:600'>STRATEJİ vs AL-TUT</div>
                <div style='font-size:40px;font-weight:800;color:{renk};font-family:JetBrains Mono,monospace'>{fark:+.1f}%</div>
                <div style='font-size:12px;color:#6b7f96;margin-top:6px'>{"Strateji kazandı ✓" if fark>=0 else "Al-Tut daha iyi"}</div>
                <div style='margin-top:12px;font-size:11px;color:#6b7f96'>
                    Strateji: <b style='color:#1a2332'>{ist['getiri']:+.1f}%</b> &nbsp;|&nbsp; Al-Tut: <b style='color:#1a2332'>{ist['al_tut']:+.1f}%</b>
                </div>
            </div>""",unsafe_allow_html=True)

        if len(bt["islemler"])>0:
            st.markdown("#### 📋 İşlem Geçmişi")
            st.dataframe(bt["islemler"],use_container_width=True,height=280,hide_index=True)

# ═══ TAB 4: TARAMA ═══════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🔍 BIST Hisse Tarayıcı")
    col1,col2,col3 = st.columns(3)
    with col1: secili_s=st.selectbox("Sektör",["TÜMÜ"]+sorted(set(v["sektor"] for v in HISSELER.values())))
    with col2: min_rsi,max_rsi=st.slider("RSI Aralığı",0,100,(20,65))
    with col3: min_puan=st.slider("Min Puan",0,20,3)

    taranacak={k:v for k,v in HISSELER.items() if secili_s=="TÜMÜ" or v["sektor"]==secili_s}

    if st.button("🔍 Tara",type="primary",use_container_width=True):
        sonuclar=[]; prog=st.progress(0); durum=st.empty()
        for i,(kod,bilgi) in enumerate(taranacak.items()):
            durum.text(f"📡 {kod} taranıyor... ({i+1}/{len(taranacak)})")
            prog.progress((i+1)/len(taranacak))
            df_t, err = veri_cek(kod,"6mo")
            if df_t is not None and len(df_t)>30:
                try:
                    df_t=indikatör_hesapla(df_t)
                    sig_t=sinyal_hesapla(df_t)
                    s=df_t.iloc[-1]; o=df_t.iloc[-2]
                    dg=(s["close"]-o["close"])/o["close"]*100
                    rv=sig_t.get("rsi")
                    if rv is not None and not pd.isna(rv) and min_rsi<=rv<=max_rsi and sig_t["puan"]>=min_puan:
                        vol=volatilite_yuzde(df_t["close"])
                        sonuclar.append({
                            "Hisse":kod,"İsim":bilgi["isim"],"Sektör":bilgi["sektor"],
                            "Fiyat":round(s["close"],2),"Değişim%":round(dg,2),
                            "RSI":round(rv,1),
                            "ADX":round(sig_t["adx"],1) if sig_t.get("adx") and not pd.isna(sig_t["adx"]) else None,
                            "MACD":round(sig_t["macd_hist"],4) if sig_t.get("macd_hist") and not pd.isna(sig_t["macd_hist"]) else None,
                            "Volatilite%":round(vol,1) if vol else None,
                            "Sinyal":sig_t["sinyal"],"Puan":sig_t["puan"],
                        })
                except: pass
        prog.empty(); durum.empty()
        if sonuclar:
            st.session_state["tarama"]=pd.DataFrame(sonuclar).sort_values("Puan",ascending=False)
        else:
            st.warning("Kriterlere uyan hisse bulunamadı. RSI aralığını veya min puanı genişlet.")

    if "tarama" in st.session_state:
        df_t=st.session_state["tarama"]
        c1,c2,c3,c4=st.columns(4)
        with c1: st.metric("Bulunan",len(df_t))
        with c2: st.metric("AL Sinyali",len(df_t[df_t["Sinyal"].str.contains("AL",na=False)]))
        with c3: st.metric("SAT Sinyali",len(df_t[df_t["Sinyal"].str.contains("SAT",na=False)]))
        with c4: st.metric("Bekle",len(df_t[df_t["Sinyal"].str.contains("BEKLE",na=False)]))

        def renk_sinyal(val):
            if "AL" in str(val): return "background-color:#e8f8f1;color:#0d7a4e"
            if "SAT" in str(val): return "background-color:#fde8ec;color:#b02030"
            return "background-color:#fff8e6;color:#8a6000"

        styled=df_t.style.map(renk_sinyal,subset=["Sinyal"]).format({
            "Değişim%":"{:+.2f}%","Fiyat":"{:.2f} ₺",
            "Volatilite%":"{:.1f}%","Puan":"{:+d}"})
        st.dataframe(styled,use_container_width=True,height=450,hide_index=True)

# ═══ TAB 5: REHBER ═══════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 📚 Profesyonel Analistlerin Kullandığı İndikatörler")

    kategoriler = [
        ("🔵 TREND İNDİKATÖRLERİ","#1a6fa8",[
            ("EMA 9/21/50/200","Üstel hareketli ortalama","Fiyat EMA üstünde = trend yukarı. EMA21>EMA50 = güçlü yükseliş. Altın kesim en güçlü al sinyali.","Tüm profesyoneller"),
            ("ADX (14)","Trend gücü ölçer (yön değil)","25+ = güçlü trend. 20- = yatay piyasa. ADX olmadan trend stratejisi kullanma!","Swing ve pozisyon trader"),
            ("Parabolic SAR","Trend dönüş noktaları","Fiyat SAR altında = yukarı trend. SAR üstünde = aşağı trend. Trailing stop için idealdir.","Kısa-orta vade"),
        ]),
        ("🟣 MOMENTUM İNDİKATÖRLERİ","#8e44ad",[
            ("RSI (14)","Aşırı alım/satım tespiti","30↓ = aşırı satılmış (al fırsatı). 70↑ = aşırı alınmış (dikkat). 50 seviyesi trend sinyali.","Tüm profesyoneller"),
            ("MACD (12,26,9)","Trend momentum ve dönüş","Histogram sıfırı yukarı keserse AL. Aşağı keserse SAT. En güvenilir momentum sinyali.","Tüm profesyoneller"),
            ("Stochastic (14,3,3)","RSI'ya benzer, daha hassas","K<20 ve D'yi yukarı keserse AL. K>80 ve D'yi aşağı keserse SAT.","Kısa vadeli traderlar"),
            ("CCI (20)","Ortalamadan sapma","±100 normal aralık. -100↓ aşırı satılmış, +100↑ aşırı alınmış.","Emtia analistleri"),
            ("Williams %R","Tersten Stochastic","-80↓ aşırı satılmış. -20↑ aşırı alınmış.","Kısa vadeli traderlar"),
        ]),
        ("🟡 VOLATİLİTE İNDİKATÖRLERİ","#e67e22",[
            ("Bollinger Bantları","Dinamik fiyat kanalı","Alt banda değme = alım fırsatı. Sıkışma (<4%) = büyük hareket öncesi uyarısı.","Tüm profesyoneller"),
            ("ATR (14)","Gerçek aralık ortalaması","Stop-loss = Alış - 1.5xATR. Pozisyon büyüklüğü = Risk / ATR.","Risk yöneticileri"),
        ]),
        ("🟢 HACİM İNDİKATÖRLERİ","#0d7a4e",[
            ("OBV","Hacim eğilimi","OBV yükselirken fiyat düşüyorsa = yakında fiyat yükselir (diverjans).","Kurumsal analistler"),
            ("VWAP","Hacim ağırlıklı ortalama","Kurumsal alım/satım referans fiyatı. Fiyat üstünde = alım baskısı.","Günlük traderlar"),
            ("MFI (14)","Hacimli RSI","20↓ = para girişi bekleniyor. 80↑ = para çıkışı riski.","Kurumsal analistler"),
        ]),
    ]

    for kat_isim, kat_renk, indikatorler in kategoriler:
        st.markdown(f"<h4 style='color:#1a2332;margin-top:20px'>{kat_isim}</h4>",unsafe_allow_html=True)
        for ind, ne, nasil, kim in indikatorler:
            st.markdown(f"""
            <div class='pro-card' style='border-left:4px solid {kat_renk};margin-bottom:8px;padding:12px 16px'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                    <div style='flex:1'>
                        <span style='font-size:14px;font-weight:700;color:#1a2332'>{ind}</span>
                        <span style='font-size:11px;color:#6b7f96;margin-left:8px'>{ne}</span>
                        <div style='font-size:12px;color:#4a5568;margin-top:5px;line-height:1.5'>{nasil}</div>
                    </div>
                    <span style='font-size:10px;color:{kat_renk};background:{kat_renk}18;padding:3px 8px;border-radius:12px;white-space:nowrap;margin-left:12px;font-weight:600'>{kim}</span>
                </div>
            </div>
            """,unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
### 🎯 Önerilen Kombinasyonlar

| Kombinasyon | İndikatörler | Ne Zaman |
|-------------|-------------|----------|
| **Temel Swing** | RSI(14) + EMA21/50 + Hacim | Başlangıç için ideal |
| **Momentum** | MACD + RSI + Stochastic | Güçlü trend dönemlerinde |
| **Volatilite** | Bollinger + ATR + ADX | Sıkışma kırılmalarında |
| **Kurumsal** | VWAP + OBV + MFI | Büyük hisse takibinde |
| **Tam Sistem** | RSI + MACD + EMA + ADX + Hacim | Deneyimli trader |

### ⚠️ Altın Kurallar
- **Hiçbir indikatör tek başına yeterli değil** — en az 2-3 teyit al
- **Hacim her zaman doğrulamalı** — hacim yoksa sinyal zayıftır
- **ADX > 25 olmadan trend stratejisi kullanma** — yatay piyasada kayıp artar
- **Stop-loss = 1.5x ATR** — sezgiyle değil, matematikle belirle
- **Backtest geçmişi garanti etmez** — sadece strateji mantığını test eder
""")

# ═══ TAB 6: İSTATİSTİK ═══════════════════════════════════════════════════════
with tab6:
    st.markdown("### 📊 Hisse İstatistikleri")

    col1,col2 = st.columns(2)

    with col1:
        vol = volatilite_yuzde(df["close"])
        sharpe_b = sharpe_benzeri(df["close"])
        max_dd_v = max_drawdown(df["close"])
        mom_s = momentum_skoru(df["close"])

        st.markdown("#### 📈 Risk Metrikleri")
        for k,v,acik in [
            ("Yıllıklaştırılmış Volatilite",f"%{vol:.1f}" if vol else "—","Getiri standart sapması × √252"),
            ("Sharpe Benzeri Oran",f"{sharpe_b:.2f}" if sharpe_b else "—","(Getiri - %40) / Volatilite"),
            ("Max Drawdown (90 gün)",f"%{max_dd_v:.1f}" if max_dd_v else "—","Tepe'den en derin düşüş"),
            ("Momentum Skoru",f"{mom_s:+.1f}%","20/60/120 günlük ağırlıklı getiri"),
        ]:
            st.markdown(f"""
            <div class='pro-card' style='padding:12px 16px;margin-bottom:8px'>
                <div style='display:flex;justify-content:space-between'>
                    <div>
                        <div style='font-size:13px;font-weight:600;color:#1a2332'>{k}</div>
                        <div style='font-size:10px;color:#6b7f96;margin-top:2px'>{acik}</div>
                    </div>
                    <div style='font-size:20px;font-weight:800;color:#1a6fa8;font-family:JetBrains Mono,monospace'>{v}</div>
                </div>
            </div>
            """,unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📉 Fiyat İstatistikleri")
        c_clean = df["close"].dropna()
        if len(c_clean) > 10:
            for k,v in [
                ("52 Hafta Yüksek",f"{c_clean.max():.2f} ₺"),
                ("52 Hafta Düşük",f"{c_clean.min():.2f} ₺"),
                ("Güncel / 52H Max",f"%{(son['close']/c_clean.max()*100):.1f}"),
                ("Güncel / 52H Min",f"%{(son['close']/c_clean.min()*100):.1f}"),
                ("Ortalama Fiyat",f"{c_clean.mean():.2f} ₺"),
                ("Medyan Fiyat",f"{c_clean.median():.2f} ₺"),
                ("Toplam Veri Noktası",f"{len(c_clean)} gün"),
            ]:
                st.markdown(f"""
                <div class='pro-card' style='padding:10px 16px;margin-bottom:8px'>
                    <div style='display:flex;justify-content:space-between;align-items:center'>
                        <span style='font-size:13px;color:#6b7f96'>{k}</span>
                        <span style='font-size:15px;font-weight:700;color:#1a2332;font-family:JetBrains Mono,monospace'>{v}</span>
                    </div>
                </div>
                """,unsafe_allow_html=True)

    # Getiri dağılımı grafiği
    st.markdown("#### 📊 Günlük Getiri Dağılımı")
    gunluk_getiri = df["close"].pct_change().dropna() * 100
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=gunluk_getiri, nbinsx=50,
        marker_color="#e8f0f8", marker_line_color="#1a6fa8",
        marker_line_width=0.5, name="Getiri Dağılımı"))
    fig_hist.add_vline(x=0,line_color="#1a2332",line_dash="dash",line_width=1)
    fig_hist.add_vline(x=gunluk_getiri.mean(),line_color="#0d7a4e",line_dash="dot",line_width=1.5)
    fig_hist.update_layout(
        paper_bgcolor="#ffffff",plot_bgcolor="#fafbfc",
        font=dict(color="#6b7f96"),height=250,
        xaxis_title="Günlük Getiri (%)",
        margin=dict(l=10,r=10,t=10,b=30),showlegend=False)
    fig_hist.update_xaxes(gridcolor="#f0f4f8")
    fig_hist.update_yaxes(gridcolor="#f0f4f8")
    st.plotly_chart(fig_hist,use_container_width=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("---")
import pytz
TR2 = pytz.timezone("Europe/Istanbul")
saat_tr = datetime.now(TR2).strftime("%d.%m.%Y %H:%M:%S")
st.markdown(f"""
<div style='text-align:center;color:#aab8c8;font-size:11px;padding:8px'>
    📊 BIST PRO v5.0 &nbsp;·&nbsp; Yahoo Finance 15dk gecikmeli &nbsp;·&nbsp; 
    Yatırım tavsiyesi değildir &nbsp;·&nbsp; {saat_tr} (TR)
</div>
""",unsafe_allow_html=True)
