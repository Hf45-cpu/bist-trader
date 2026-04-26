"""
BIST Swing Trading & Backtest Uygulaması
Streamlit + yfinance + pandas + ta
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─── SAYFA AYARI ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BIST Swing Trader",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .main { background-color: #04111e; }
    .stApp { background-color: #04111e; color: #c8e4f8; }
    
    .metric-card {
        background: #0b2035;
        border: 1px solid #143350;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-label { font-size: 11px; color: #5588aa; letter-spacing: 1px; margin-bottom: 4px; }
    .metric-value { font-size: 24px; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
    .green { color: #00e59a; }
    .red   { color: #ff3e5e; }
    .blue  { color: #00c8ff; }
    .yellow{ color: #ffc840; }
    
    .sinyal-al  { background: #00e59a22; color: #00e59a; border: 1px solid #00e59a44;
                  padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 13px; }
    .sinyal-sat { background: #ff3e5e22; color: #ff3e5e; border: 1px solid #ff3e5e44;
                  padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 13px; }
    .sinyal-bekle { background: #ffc84022; color: #ffc840; border: 1px solid #ffc84044;
                    padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 13px; }
    
    div[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; }
    .stSelectbox label, .stSlider label { color: #5588aa !important; font-size: 12px !important; }
    
    h1, h2, h3 { color: #c8e4f8 !important; }
    .stTabs [data-baseweb="tab"] { color: #5588aa; }
    .stTabs [aria-selected="true"] { color: #00c8ff !important; border-bottom-color: #00c8ff !important; }
</style>
""", unsafe_allow_html=True)

# ─── HİSSE LİSTESİ ───────────────────────────────────────────────────────────
HISSELER = {
    "GARAN": {"isim": "Garanti BBVA",       "sektor": "Bankacılık"},
    "AKBNK": {"isim": "Akbank",             "sektor": "Bankacılık"},
    "YKBNK": {"isim": "Yapı Kredi",         "sektor": "Bankacılık"},
    "ISCTR": {"isim": "İş Bankası C",       "sektor": "Bankacılık"},
    "VAKBN": {"isim": "Vakıfbank",          "sektor": "Bankacılık"},
    "ASELS": {"isim": "Aselsan",            "sektor": "Savunma"},
    "TUPRS": {"isim": "Tüpraş",             "sektor": "Enerji"},
    "THYAO": {"isim": "Türk Hava Yolları",  "sektor": "Ulaşım"},
    "KCHOL": {"isim": "Koç Holding",        "sektor": "Holding"},
    "SAHOL": {"isim": "Sabancı Holding",    "sektor": "Holding"},
    "EREGL": {"isim": "Ereğli Demir",       "sektor": "Metal"},
    "FROTO": {"isim": "Ford Otosan",        "sektor": "Otomotiv"},
    "TOASO": {"isim": "Tofaş Oto",          "sektor": "Otomotiv"},
    "LOGO":  {"isim": "Logo Yazılım",       "sektor": "Teknoloji"},
    "TCELL": {"isim": "Turkcell",           "sektor": "Telekom"},
    "SISE":  {"isim": "Şişe Cam",           "sektor": "Sanayi"},
    "EKGYO": {"isim": "Emlak Konut GYO",    "sektor": "GYO"},
    "PGSUS": {"isim": "Pegasus",            "sektor": "Ulaşım"},
    "BIMAS": {"isim": "BİM Mağazalar",      "sektor": "Perakende"},
    "MGROS": {"isim": "Migros",             "sektor": "Perakende"},
}

# ─── VERİ ÇEKME ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=900)  # 15 dk cache
def veri_cek(kod: str, period: str = "1y") -> pd.DataFrame:
    """Yahoo Finance'den BIST hisse verisi çek (15 dk gecikmeli)"""
    try:
        ticker = yf.Ticker(f"{kod}.IS")
        df = ticker.history(period=period)
        if df.empty:
            return None
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df.columns = [c.lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Veri çekilemedi: {e}")
        return None

@st.cache_data(ttl=900)
def endeks_cek() -> dict:
    """BIST100 ve döviz verilerini çek"""
    sonuc = {}
    semboller = {
        "BIST100": "XU100.IS",
        "USDTRY": "USDTRY=X",
        "EURTRY": "EURTRY=X",
        "ALTIN": "GC=F",
        "BRENT": "BZ=F",
    }
    for isim, sembol in semboller.items():
        try:
            t = yf.Ticker(sembol)
            h = t.history(period="2d")
            if not h.empty:
                son = h["Close"].iloc[-1]
                onceki = h["Close"].iloc[-2] if len(h) > 1 else son
                degisim = (son - onceki) / onceki * 100
                sonuc[isim] = {"deger": son, "degisim": degisim}
        except:
            pass
    return sonuc

# ─── TEKNİK İNDİKATÖRLER ─────────────────────────────────────────────────────
def indikatör_hesapla(df: pd.DataFrame) -> pd.DataFrame:
    """Tüm teknik indikatörleri hesapla"""
    df = df.copy()
    
    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
    
    # EMA
    df["ema21"] = ta.trend.EMAIndicator(df["close"], window=21).ema_indicator()
    df["ema50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()
    df["ema200"] = ta.trend.EMAIndicator(df["close"], window=200).ema_indicator()
    
    # MACD
    macd = ta.trend.MACD(df["close"])
    df["macd"]        = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_hist"]   = macd.macd_diff()
    
    # Bollinger Bantları
    bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
    df["bb_ust"]  = bb.bollinger_hband()
    df["bb_orta"] = bb.bollinger_mavg()
    df["bb_alt"]  = bb.bollinger_lband()
    df["bb_width"] = (df["bb_ust"] - df["bb_alt"]) / df["bb_orta"] * 100
    
    # Stochastic
    stoch = ta.momentum.StochasticOscillator(df["high"], df["low"], df["close"])
    df["stoch_k"] = stoch.stoch()
    df["stoch_d"] = stoch.stoch_signal()
    
    # ATR (Volatilite)
    df["atr"] = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"]).average_true_range()
    
    # Hacim EMA
    df["hacim_ema"] = df["volume"].ewm(span=20).mean()
    df["hacim_oran"] = df["volume"] / df["hacim_ema"]
    
    # Destek / Direnç (Pivot Points)
    df["pivot"] = (df["high"] + df["low"] + df["close"]) / 3
    df["r1"] = 2 * df["pivot"] - df["low"]
    df["s1"] = 2 * df["pivot"] - df["high"]
    
    return df

# ─── SİNYAL MOTORU ───────────────────────────────────────────────────────────
def sinyal_uret(df: pd.DataFrame) -> dict:
    """Son günün sinyalini üret"""
    if df is None or len(df) < 50:
        return {"sinyal": "VERİ YOK", "guc": 0, "sebepler": []}
    
    son = df.iloc[-1]
    sebepler = []
    puan = 0
    
    # RSI
    if pd.notna(son["rsi"]):
        if son["rsi"] < 35:
            sebepler.append(f"✅ RSI aşırı satılmış ({son['rsi']:.0f})")
            puan += 2
        elif son["rsi"] < 50:
            sebepler.append(f"✅ RSI alım bölgesi ({son['rsi']:.0f})")
            puan += 1
        elif son["rsi"] > 70:
            sebepler.append(f"❌ RSI aşırı alınmış ({son['rsi']:.0f})")
            puan -= 2
        elif son["rsi"] > 60:
            sebepler.append(f"⚠️ RSI yüksek bölge ({son['rsi']:.0f})")
            puan -= 1

    # EMA Trend
    if pd.notna(son["ema21"]) and pd.notna(son["ema50"]):
        if son["close"] > son["ema21"] > son["ema50"]:
            sebepler.append("✅ Fiyat EMA21 > EMA50 üzerinde (trend yukarı)")
            puan += 2
        elif son["close"] < son["ema21"] < son["ema50"]:
            sebepler.append("❌ Fiyat EMA21 < EMA50 altında (trend aşağı)")
            puan -= 2
        elif son["close"] > son["ema50"]:
            sebepler.append("✅ Fiyat EMA50 üzerinde")
            puan += 1

    # MACD
    if pd.notna(son["macd_hist"]):
        onceki = df.iloc[-2]
        if son["macd_hist"] > 0 and onceki["macd_hist"] <= 0:
            sebepler.append("✅ MACD yukarı kesiş (güçlü sinyal)")
            puan += 2
        elif son["macd_hist"] > 0:
            sebepler.append("✅ MACD pozitif bölge")
            puan += 1
        elif son["macd_hist"] < 0 and onceki["macd_hist"] >= 0:
            sebepler.append("❌ MACD aşağı kesiş")
            puan -= 2
        elif son["macd_hist"] < 0:
            sebepler.append("⚠️ MACD negatif bölge")
            puan -= 1

    # Bollinger
    if pd.notna(son["bb_alt"]) and pd.notna(son["bb_ust"]):
        if son["close"] <= son["bb_alt"]:
            sebepler.append("✅ Alt Bollinger bandına değdi (dip olabilir)")
            puan += 1
        elif son["close"] >= son["bb_ust"]:
            sebepler.append("❌ Üst Bollinger bandına değdi (tepe olabilir)")
            puan -= 1

    # Hacim teyidi
    if pd.notna(son["hacim_oran"]):
        if son["hacim_oran"] > 1.5 and puan > 0:
            sebepler.append(f"✅ Hacim ortalamanın {son['hacim_oran']:.1f}x üzerinde (teyit)")
            puan += 1
        elif son["hacim_oran"] < 0.5:
            sebepler.append("⚠️ Düşük hacim (sinyal zayıf olabilir)")

    # Karar
    if puan >= 4:
        sinyal = "GÜÇLÜ AL"
    elif puan >= 2:
        sinyal = "AL"
    elif puan <= -4:
        sinyal = "GÜÇLÜ SAT"
    elif puan <= -2:
        sinyal = "SAT"
    else:
        sinyal = "BEKLE"

    return {
        "sinyal": sinyal,
        "puan": puan,
        "sebepler": sebepler,
        "rsi": son["rsi"],
        "ema21": son["ema21"],
        "ema50": son["ema50"],
        "macd_hist": son["macd_hist"],
        "bb_alt": son["bb_alt"],
        "bb_ust": son["bb_ust"],
        "atr": son["atr"],
    }

# ─── BACKTEST MOTORU ─────────────────────────────────────────────────────────
def backtest_calistir(df, strateji, sermaye, komisyon, stop_loss, take_profit):
    """Gerçek OHLCV verisi üzerinde backtest çalıştır"""
    df = df.copy().reset_index()
    kapanislar = df["close"].values
    
    # İndikatörler
    rsi_ser   = ta.momentum.RSIIndicator(pd.Series(kapanislar), window=14).rsi().values
    ema21_ser = ta.trend.EMAIndicator(pd.Series(kapanislar), window=21).ema_indicator().values
    ema50_ser = ta.trend.EMAIndicator(pd.Series(kapanislar), window=50).ema_indicator().values
    macd_obj  = ta.trend.MACD(pd.Series(kapanislar))
    macd_hist = macd_obj.macd_diff().values
    bb_obj    = ta.volatility.BollingerBands(pd.Series(kapanislar))
    bb_alt    = bb_obj.bollinger_lband().values
    bb_ust    = bb_obj.bollinger_hband().values

    # Sinyal üret
    sinyaller = []
    for i in range(len(df)):
        s = None
        if strateji == "RSI Swing":
            if rsi_ser[i] < 35: s = "AL"
            elif rsi_ser[i] > 65: s = "SAT"
        elif strateji == "EMA Kesişim":
            if i > 0 and not np.isnan(ema21_ser[i]) and not np.isnan(ema50_ser[i]):
                if ema21_ser[i-1] <= ema50_ser[i-1] and ema21_ser[i] > ema50_ser[i]: s = "AL"
                elif ema21_ser[i-1] >= ema50_ser[i-1] and ema21_ser[i] < ema50_ser[i]: s = "SAT"
        elif strateji == "Bollinger Bandı":
            if not np.isnan(bb_alt[i]):
                if kapanislar[i] <= bb_alt[i]: s = "AL"
                elif kapanislar[i] >= bb_ust[i]: s = "SAT"
        elif strateji == "MACD + RSI":
            if i > 0 and not np.isnan(macd_hist[i]) and not np.isnan(rsi_ser[i]):
                if macd_hist[i-1] <= 0 and macd_hist[i] > 0 and rsi_ser[i] < 55: s = "AL"
                elif macd_hist[i-1] >= 0 and macd_hist[i] < 0: s = "SAT"
        elif strateji == "Kombine (RSI+EMA+MACD)":
            if not np.isnan(rsi_ser[i]) and not np.isnan(ema50_ser[i]) and not np.isnan(macd_hist[i]):
                al_puan  = (rsi_ser[i] < 45) + (kapanislar[i] > ema50_ser[i]) + (macd_hist[i] > 0)
                sat_puan = (rsi_ser[i] > 60) + (kapanislar[i] < ema50_ser[i]) + (macd_hist[i] < 0)
                if al_puan >= 2: s = "AL"
                elif sat_puan >= 2: s = "SAT"
        sinyaller.append(s)

    # İşlem simülasyonu
    nakit = sermaye
    pozisyon = None
    islemler = []
    sermaye_egrisi = [sermaye]

    for i in range(1, len(df)):
        row = df.iloc[i]
        
        # Açık pozisyon kontrolü
        if pozisyon:
            degisim = (row["close"] - pozisyon["alis"]) / pozisyon["alis"] * 100
            stop_tetik   = row["low"]  <= pozisyon["alis"] * (1 - stop_loss / 100)
            target_tetik = row["high"] >= pozisyon["alis"] * (1 + take_profit / 100)
            
            cikis_fiyat = None
            neden = None
            if stop_tetik:
                cikis_fiyat = pozisyon["alis"] * (1 - stop_loss / 100)
                neden = "Stop-Loss"
            elif target_tetik:
                cikis_fiyat = pozisyon["alis"] * (1 + take_profit / 100)
                neden = "Take-Profit"
            elif sinyaller[i] == "SAT":
                cikis_fiyat = row["close"]
                neden = "Sinyal"

            if cikis_fiyat:
                gelir = pozisyon["adet"] * cikis_fiyat * (1 - komisyon / 100)
                pnl   = gelir - pozisyon["maliyet"]
                nakit += gelir
                islemler.append({
                    "giris_tarih": pozisyon["tarih"],
                    "cikis_tarih": row["Date"] if "Date" in row else row.name,
                    "giris_fiyat": round(pozisyon["alis"], 2),
                    "cikis_fiyat": round(cikis_fiyat, 2),
                    "pnl": round(pnl, 2),
                    "pnl_pct": round(pnl / pozisyon["maliyet"] * 100, 2),
                    "neden": neden,
                    "tutma_gun": (i - pozisyon["gun"]),
                })
                pozisyon = None

        # Yeni AL
        if not pozisyon and sinyaller[i] == "AL" and nakit > 100:
            kullan = nakit * 0.95
            adet   = int(kullan / (row["close"] * (1 + komisyon / 100)))
            if adet > 0:
                maliyet = adet * row["close"] * (1 + komisyon / 100)
                nakit  -= maliyet
                pozisyon = {
                    "alis": row["close"], "adet": adet, "maliyet": maliyet,
                    "tarih": row["Date"] if "Date" in row else row.name,
                    "gun": i,
                }

        # Portföy değeri
        portfoy = nakit + (pozisyon["adet"] * row["close"] if pozisyon else 0)
        sermaye_egrisi.append(portfoy)

    # Açık pozisyonu kapat
    if pozisyon:
        son = df.iloc[-1]
        gelir = pozisyon["adet"] * son["close"] * (1 - komisyon / 100)
        pnl   = gelir - pozisyon["maliyet"]
        nakit += gelir
        islemler.append({
            "giris_tarih": pozisyon["tarih"],
            "cikis_tarih": son.get("Date", son.name),
            "giris_fiyat": round(pozisyon["alis"], 2),
            "cikis_fiyat": round(son["close"], 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl / pozisyon["maliyet"] * 100, 2),
            "neden": "Dönem Sonu",
            "tutma_gun": len(df) - 1 - pozisyon["gun"],
        })

    # İstatistikler
    islemler_df = pd.DataFrame(islemler) if islemler else pd.DataFrame()
    son_deger = sermaye_egrisi[-1]
    toplam_getiri = (son_deger - sermaye) / sermaye * 100

    kazananlar = islemler_df[islemler_df["pnl"] > 0] if len(islemler_df) else pd.DataFrame()
    kayiplar   = islemler_df[islemler_df["pnl"] <= 0] if len(islemler_df) else pd.DataFrame()

    # Max drawdown
    egri = pd.Series(sermaye_egrisi)
    tepe = egri.cummax()
    drawdown = (egri - tepe) / tepe * 100
    max_dd = drawdown.min()

    # Sharpe
    gunluk_getiri = pd.Series(sermaye_egrisi).pct_change().dropna()
    sharpe = (gunluk_getiri.mean() / gunluk_getiri.std() * np.sqrt(252)) if gunluk_getiri.std() > 0 else 0

    # Al-tut
    al_tut = (kapanislar[-1] - kapanislar[0]) / kapanislar[0] * 100

    return {
        "islemler": islemler_df,
        "sermaye_egrisi": sermaye_egrisi,
        "tarihler": df.index.tolist() if hasattr(df.index, "tolist") else list(range(len(df))),
        "istatistik": {
            "toplam_islem": len(islemler_df),
            "kazanan": len(kazananlar),
            "kaybeden": len(kayiplar),
            "kazanma_orani": round(len(kazananlar) / max(len(islemler_df), 1) * 100, 1),
            "toplam_getiri": round(toplam_getiri, 2),
            "al_tut": round(al_tut, 2),
            "max_drawdown": round(max_dd, 2),
            "sharpe": round(sharpe, 2),
            "son_deger": round(son_deger, 2),
            "toplam_pnl": round(islemler_df["pnl"].sum(), 2) if len(islemler_df) else 0,
            "ort_pnl": round(islemler_df["pnl"].mean(), 2) if len(islemler_df) else 0,
            "ort_kazanc": round(kazananlar["pnl"].mean(), 2) if len(kazananlar) else 0,
            "ort_kayip":  round(kayiplar["pnl"].mean(), 2)   if len(kayiplar)   else 0,
            "ort_tutma":  round(islemler_df["tutma_gun"].mean(), 1) if len(islemler_df) else 0,
        },
        "sinyaller": sinyaller,
        "df": df,
    }

# ─── GRAFİKLER ───────────────────────────────────────────────────────────────
def mumlu_grafik(df, sinyaller=None, baslik=""):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2],
        vertical_spacing=0.03,
    )

    # Mum grafik
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        increasing_line_color="#00e59a", decreasing_line_color="#ff3e5e",
        name="Fiyat"
    ), row=1, col=1)

    # EMA'lar
    if "ema21" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["ema21"], line=dict(color="#00c8ff", width=1.5), name="EMA21"), row=1, col=1)
    if "ema50" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["ema50"], line=dict(color="#ffc840", width=1.5), name="EMA50"), row=1, col=1)

    # Bollinger
    if "bb_ust" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["bb_ust"], line=dict(color="#a855f7", width=1, dash="dot"), name="BB Üst"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["bb_alt"], line=dict(color="#a855f7", width=1, dash="dot"),
                                 fill="tonexty", fillcolor="rgba(168,85,247,0.05)", name="BB Alt"), row=1, col=1)

    # Sinyaller
    if sinyaller is not None:
        al_idx  = [i for i, s in enumerate(sinyaller) if s == "AL"]
        sat_idx = [i for i, s in enumerate(sinyaller) if s == "SAT"]
        if al_idx:
            fig.add_trace(go.Scatter(
                x=df.index[al_idx], y=df["low"].iloc[al_idx] * 0.98,
                mode="markers", marker=dict(symbol="triangle-up", size=10, color="#00e59a"),
                name="AL Sinyali"
            ), row=1, col=1)
        if sat_idx:
            fig.add_trace(go.Scatter(
                x=df.index[sat_idx], y=df["high"].iloc[sat_idx] * 1.02,
                mode="markers", marker=dict(symbol="triangle-down", size=10, color="#ff3e5e"),
                name="SAT Sinyali"
            ), row=1, col=1)

    # Hacim
    renkler = ["#00e59a" if c >= o else "#ff3e5e" for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(x=df.index, y=df["volume"], marker_color=renkler, name="Hacim", opacity=0.7), row=2, col=1)
    if "hacim_ema" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["hacim_ema"], line=dict(color="#ffc840", width=1.5), name="Hacim EMA"), row=2, col=1)

    # RSI
    if "rsi" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], line=dict(color="#00c8ff", width=2), name="RSI"), row=3, col=1)
        fig.add_hline(y=70, line_color="#ff3e5e", line_dash="dot", line_width=1, row=3, col=1)
        fig.add_hline(y=30, line_color="#00e59a", line_dash="dot", line_width=1, row=3, col=1)
        fig.add_hrect(y0=30, y1=70, fillcolor="rgba(255,255,255,0.02)", row=3, col=1)

    fig.update_layout(
        title=dict(text=baslik, font=dict(color="#c8e4f8", size=16)),
        paper_bgcolor="#04111e",
        plot_bgcolor="#071828",
        font=dict(color="#5588aa"),
        xaxis_rangeslider_visible=False,
        height=600,
        showlegend=True,
        legend=dict(bgcolor="#0b2035", bordercolor="#143350", font=dict(color="#c8e4f8")),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    fig.update_xaxes(gridcolor="#143350", showgrid=True)
    fig.update_yaxes(gridcolor="#143350", showgrid=True)
    return fig

def sermaye_grafigi(egrisi, al_tut_sermaye, al_tut_son):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=egrisi, mode="lines",
        line=dict(color="#00e59a" if egrisi[-1] >= egrisi[0] else "#ff3e5e", width=2.5),
        fill="tozeroy", fillcolor="rgba(0,229,154,0.08)",
        name="Strateji"
    ))
    fig.add_hline(y=al_tut_sermaye, line_color="#ffc840", line_dash="dot", line_width=1.5)
    fig.add_annotation(x=len(egrisi)-1, y=al_tut_son, text=f"Al-Tut", showarrow=False,
                       font=dict(color="#ffc840", size=11), xanchor="right")
    fig.update_layout(
        paper_bgcolor="#04111e", plot_bgcolor="#071828",
        font=dict(color="#5588aa"), height=250,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
    )
    fig.update_xaxes(gridcolor="#143350")
    fig.update_yaxes(gridcolor="#143350")
    return fig

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    
    secilenKod = st.selectbox(
        "Hisse Seç",
        list(HISSELER.keys()),
        format_func=lambda k: f"{k} — {HISSELER[k]['isim']}"
    )
    
    period = st.selectbox("Veri Periyodu", ["3mo", "6mo", "1y", "2y"], index=2,
                          format_func=lambda x: {"3mo":"3 Ay","6mo":"6 Ay","1y":"1 Yıl","2y":"2 Yıl"}[x])
    
    st.markdown("---")
    st.markdown("### 📋 Backtest Ayarları")
    
    strateji = st.selectbox("Strateji", [
        "RSI Swing", "EMA Kesişim", "Bollinger Bandı",
        "MACD + RSI", "Kombine (RSI+EMA+MACD)"
    ])
    
    sermaye   = st.number_input("Başlangıç Sermayesi (₺)", 10000, 10000000, 100000, 10000)
    komisyon  = st.slider("Komisyon (%)", 0.01, 0.5, 0.1, 0.01)
    stop_loss = st.slider("Stop-Loss (%)", 2, 20, 8, 0.5)
    take_profit = st.slider("Take-Profit (%)", 5, 50, 20, 1)
    
    st.markdown("---")
    st.markdown("### ⏱ Veri Gecikmesi")
    st.warning("Yahoo Finance: **15 dk gecikmeli**")
    st.info(f"Son güncelleme: {datetime.now().strftime('%H:%M:%S')}")
    
    if st.button("🔄 Veriyi Yenile", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ─── ANA SAYFA ───────────────────────────────────────────────────────────────
st.markdown(f"# 📊 BIST Swing Trader — {secilenKod}")
st.markdown(f"**{HISSELER[secilenKod]['isim']}** · {HISSELER[secilenKod]['sektor']} · 15dk gecikmeli")

# Veri yükle
with st.spinner(f"{secilenKod} verisi çekiliyor..."):
    df = veri_cek(secilenKod, period)
    endeks = endeks_cek()

if df is None:
    st.error("Veri alınamadı. İnternet bağlantınızı kontrol edin.")
    st.stop()

df = indikatör_hesapla(df)
sinyal_sonuc = sinyal_uret(df)

# ─── SEKMELER ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Analiz", "⚗️ Backtest", "🔍 Tarama", "📖 Rehber"])

# ═══ TAB 1: ANALİZ ═══════════════════════════════════════════════════════════
with tab1:
    # Endeks özeti
    st.markdown("### 🌍 Piyasa Özeti")
    cols = st.columns(5)
    for i, (isim, veri) in enumerate(endeks.items()):
        with cols[i % 5]:
            delta_renk = "normal" if veri["degisim"] >= 0 else "inverse"
            st.metric(isim, f"{veri['deger']:,.2f}", f"{veri['degisim']:+.2f}%", delta_color=delta_renk)

    st.markdown("---")

    # Fiyat ve sinyal
    col1, col2 = st.columns([2, 1])
    with col1:
        son_fiyat = df["close"].iloc[-1]
        onceki_fiyat = df["close"].iloc[-2]
        degisim = (son_fiyat - onceki_fiyat) / onceki_fiyat * 100

        st.markdown(f"""
        <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:16px">
            <span style="font-size:42px;font-weight:900;color:#c8e4f8;font-family:'JetBrains Mono'">{son_fiyat:.2f} ₺</span>
            <span style="font-size:20px;font-weight:700;color:{'#00e59a' if degisim>=0 else '#ff3e5e'};font-family:'JetBrains Mono'">{degisim:+.2f}%</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        sinyal = sinyal_sonuc["sinyal"]
        renk = {"GÜÇLÜ AL": "green", "AL": "green", "BEKLE": "yellow", "SAT": "red", "GÜÇLÜ SAT": "red"}.get(sinyal, "yellow")
        st.markdown(f"""
        <div style="text-align:center;padding:20px;background:#0b2035;border-radius:12px;border:2px solid {'#00e59a' if 'AL' in sinyal else '#ff3e5e' if 'SAT' in sinyal else '#ffc840'}">
            <div style="font-size:11px;color:#5588aa;margin-bottom:8px">GÜNCEL SİNYAL</div>
            <div class="sinyal-{'al' if 'AL' in sinyal else 'sat' if 'SAT' in sinyal else 'bekle'}" style="font-size:18px;padding:8px 20px">{sinyal}</div>
            <div style="font-size:12px;color:#5588aa;margin-top:8px">Güç: {sinyal_sonuc['puan']:+d} / 8</div>
        </div>
        """, unsafe_allow_html=True)

    # 4'lü metrik
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("RSI (14)", f"{sinyal_sonuc['rsi']:.1f}" if sinyal_sonuc['rsi'] else "—",
                         "Aşırı satılmış" if sinyal_sonuc['rsi'] and sinyal_sonuc['rsi'] < 35 else "Aşırı alınmış" if sinyal_sonuc['rsi'] and sinyal_sonuc['rsi'] > 70 else "Normal")
    with col2: st.metric("EMA 21", f"{sinyal_sonuc['ema21']:.2f}" if sinyal_sonuc['ema21'] else "—",
                         "Üstünde ✓" if sinyal_sonuc['ema21'] and son_fiyat > sinyal_sonuc['ema21'] else "Altında ✗")
    with col3: st.metric("EMA 50", f"{sinyal_sonuc['ema50']:.2f}" if sinyal_sonuc['ema50'] else "—",
                         "Üstünde ✓" if sinyal_sonuc['ema50'] and son_fiyat > sinyal_sonuc['ema50'] else "Altında ✗")
    with col4:
        son = df.iloc[-1]
        st.metric("52H Bant", f"%{((son_fiyat - df['low'].min()) / (df['high'].max() - df['low'].min()) * 100):.0f}",
                  f"{df['low'].min():.0f} – {df['high'].max():.0f}")

    # Sinyal gerekçeleri
    st.markdown("#### 📋 Sinyal Gerekçeleri")
    for sebep in sinyal_sonuc["sebepler"]:
        st.markdown(f"- {sebep}")

    # Mum grafik
    st.plotly_chart(
        mumlu_grafik(df.tail(120), baslik=f"{secilenKod} — Son 120 Gün"),
        use_container_width=True
    )

    # Stop & Hedef seviyeleri
    st.markdown("#### 🎯 Swing Seviyeleri")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Stop-Loss (%8)", f"{son_fiyat * 0.92:.2f} ₺", f"-{son_fiyat * 0.08:.2f} ₺", delta_color="inverse")
    with col2: st.metric("Güncel", f"{son_fiyat:.2f} ₺", f"{degisim:+.2f}%")
    with col3: st.metric("Hedef (%20)", f"{son_fiyat * 1.20:.2f} ₺", f"+{son_fiyat * 0.20:.2f} ₺")

# ═══ TAB 2: BACKTEST ═════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"### ⚗️ {strateji} — {secilenKod} Backtesti")

    if st.button("▶ Backtest Çalıştır", type="primary", use_container_width=True):
        with st.spinner("Backtest çalışıyor..."):
            bt = backtest_calistir(df, strateji, sermaye, komisyon, stop_loss, take_profit)
            st.session_state["bt"] = bt

    if "bt" in st.session_state:
        bt = st.session_state["bt"]
        ist = bt["istatistik"]
        
        # Ana metrikler
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Toplam Getiri", f"{ist['toplam_getiri']:+.1f}%",
                             f"Al-tut: {ist['al_tut']:+.1f}%",
                             delta_color="normal" if ist['toplam_getiri'] >= ist['al_tut'] else "inverse")
        with col2: st.metric("Kazanma Oranı", f"%{ist['kazanma_orani']}",
                             f"{ist['kazanan']}K / {ist['kaybeden']}Z")
        with col3: st.metric("Max Drawdown", f"{ist['max_drawdown']:.1f}%",
                             delta_color="inverse")
        with col4: st.metric("Sharpe Oranı", f"{ist['sharpe']:.2f}",
                             "İyi ✓" if ist['sharpe'] >= 1 else "Zayıf")

        # Sermaye eğrisi
        al_tut_son = sermaye * (1 + ist["al_tut"] / 100)
        st.plotly_chart(sermaye_grafigi(bt["sermaye_egrisi"], sermaye, al_tut_son), use_container_width=True)

        # Detaylı istatistikler
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 Detaylı İstatistikler")
            detay = {
                "Son Portföy Değeri":  f"{ist['son_deger']:,.0f} ₺",
                "Toplam Kâr/Zarar":    f"{ist['toplam_pnl']:+,.0f} ₺",
                "Ortalama İşlem P&L":  f"{ist['ort_pnl']:+,.0f} ₺",
                "Ortalama Kazanç":     f"{ist['ort_kazanc']:+,.0f} ₺",
                "Ortalama Kayıp":      f"{ist['ort_kayip']:+,.0f} ₺",
                "Ortalama Tutma":      f"{ist['ort_tutma']:.1f} gün",
                "Toplam İşlem Sayısı": str(ist['toplam_islem']),
            }
            for k, v in detay.items():
                col_a, col_b = st.columns([2, 1])
                col_a.markdown(f"<span style='color:#5588aa;font-size:13px'>{k}</span>", unsafe_allow_html=True)
                col_b.markdown(f"<span style='color:#c8e4f8;font-weight:700;font-family:monospace'>{v}</span>", unsafe_allow_html=True)

        with col2:
            st.markdown("#### ⚡ Strateji vs Al-Tut")
            fark = ist['toplam_getiri'] - ist['al_tut']
            st.markdown(f"""
            <div style="background:#0b2035;border-radius:12px;padding:20px;text-align:center">
                <div style="font-size:11px;color:#5588aa;margin-bottom:8px">STRATEJİ FARK</div>
                <div style="font-size:36px;font-weight:900;color:{'#00e59a' if fark>=0 else '#ff3e5e'};font-family:'JetBrains Mono'">{fark:+.1f}%</div>
                <div style="font-size:13px;color:#5588aa;margin-top:8px">Al-Tut: {ist['al_tut']:+.1f}% | Strateji: {ist['toplam_getiri']:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        # İşlem geçmişi
        if len(bt["islemler"]) > 0:
            st.markdown("#### 📋 İşlem Geçmişi")
            islemler_goster = bt["islemler"].copy()
            islemler_goster["pnl_renkli"] = islemler_goster["pnl"].apply(
                lambda x: f"{'🟢' if x>0 else '🔴'} {x:+,.0f} ₺"
            )
            st.dataframe(
                islemler_goster[["giris_tarih","cikis_tarih","giris_fiyat","cikis_fiyat","pnl_renkli","pnl_pct","neden","tutma_gun"]].rename(columns={
                    "giris_tarih":"Giriş", "cikis_tarih":"Çıkış",
                    "giris_fiyat":"Alış ₺", "cikis_fiyat":"Satış ₺",
                    "pnl_renkli":"P&L", "pnl_pct":"% Getiri",
                    "neden":"Neden", "tutma_gun":"Gün"
                }),
                use_container_width=True, height=300
            )

# ═══ TAB 3: TARAMA ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🔍 BIST Hisse Tarayıcı")
    st.info("Tüm hisseler için sinyal taraması — bu biraz zaman alabilir")

    secili_sektor = st.selectbox("Sektör Filtresi", ["TÜMÜ"] + sorted(set(v["sektor"] for v in HISSELER.values())))
    taranacak = {k: v for k, v in HISSELER.items() if secili_sektor == "TÜMÜ" or v["sektor"] == secili_sektor}

    if st.button("🔍 Tara", type="primary"):
        sonuclar = []
        progress = st.progress(0)
        durum = st.empty()

        for i, (kod, bilgi) in enumerate(taranacak.items()):
            durum.text(f"{kod} taranıyor... ({i+1}/{len(taranacak)})")
            progress.progress((i + 1) / len(taranacak))
            
            df_t = veri_cek(kod, "3mo")
            if df_t is not None and len(df_t) > 50:
                df_t = indikatör_hesapla(df_t)
                sig = sinyal_uret(df_t)
                son_t = df_t.iloc[-1]
                onceki_t = df_t.iloc[-2]
                degisim_t = (son_t["close"] - onceki_t["close"]) / onceki_t["close"] * 100
                
                sonuclar.append({
                    "Hisse": kod,
                    "İsim": bilgi["isim"],
                    "Sektör": bilgi["sektor"],
                    "Fiyat": round(son_t["close"], 2),
                    "Değişim%": round(degisim_t, 2),
                    "RSI": round(sig["rsi"], 1) if sig["rsi"] else None,
                    "Sinyal": sig["sinyal"],
                    "Puan": sig["puan"],
                })

        progress.empty(); durum.empty()

        if sonuclar:
            sonuc_df = pd.DataFrame(sonuclar).sort_values("Puan", ascending=False)
            st.session_state["tarama"] = sonuc_df

    if "tarama" in st.session_state:
        df_t = st.session_state["tarama"]
        
        # Özet
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Tarama Yapılan", len(df_t))
        with col2: st.metric("AL Sinyali", len(df_t[df_t["Sinyal"].str.contains("AL", na=False)]))
        with col3: st.metric("SAT Sinyali", len(df_t[df_t["Sinyal"].str.contains("SAT", na=False)]))
        with col4: st.metric("BEKLE", len(df_t[df_t["Sinyal"] == "BEKLE"]))

        # Tablo
        def sinyal_renk(val):
            if "AL" in str(val): return "background-color: #00e59a22; color: #00e59a"
            if "SAT" in str(val): return "background-color: #ff3e5e22; color: #ff3e5e"
            return "color: #ffc840"

        styled = df_t.style.applymap(sinyal_renk, subset=["Sinyal"]) \
                          .format({"Değişim%": "{:+.2f}%", "Fiyat": "{:.2f} ₺"})
        st.dataframe(styled, use_container_width=True, height=500)

# ═══ TAB 4: REHBER ═══════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    ## 📖 Nasıl Kullanılır?

    ### ⚗️ Backtest Nedir?
    Geçmiş veriye dayanarak bir stratejinin ne kadar iyi çalıştığını test etmektir.
    Gerçek para riske atmadan stratejiyi anlayabilirsin.

    ### 📊 Stratejiler
    | Strateji | Nasıl Çalışır | Ne Zaman İyi |
    |----------|---------------|--------------|
    | RSI Swing | RSI<35 AL, RSI>65 SAT | Yatay piyasada |
    | EMA Kesişim | EMA21>EMA50 AL | Trend piyasada |
    | Bollinger | Alt banda değince AL | Volatil piyasada |
    | MACD+RSI | İkisi aynı anda onaylarsa | Her koşulda |
    | Kombine | 3 indikatör çoğunluğu | Genel kullanım |

    ### 🎯 Swing Trading Kuralları
    1. **RSI 35-55 bölgesinde giriş** — aşırı alınmış/satılmış değil
    2. **EMA21 üzerinde kapanış** — trend sende
    3. **Stop-loss: -%8** — asla bozma
    4. **Hedef: +%15-25** — trailing stop ile koru
    5. **2-6 hafta tut** — sabır
    6. **KAP'ı kontrol et** — her girişten önce

    ### ⚠️ Önemli Uyarılar
    - Bu uygulama **yatırım tavsiyesi değildir**
    - Backtest geçmiş performansı gösterir, **gelecek garanti değildir**
    - Gerçek işlemde slipaj ve likidite faktörlerini hesaba kat
    - Küçük pozisyonlarla başla, sistemi öğren

    ### 📈 Sharpe Oranı Yorumu
    - **< 0**: Strateji çalışmıyor
    - **0-1**: Kabul edilebilir
    - **1-2**: İyi
    - **> 2**: Mükemmel
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#244060;font-size:11px'>"
    "📊 BIST Swing Trader · Yahoo Finance 15dk gecikmeli veri · Yatırım tavsiyesi değildir"
    "</div>",
    unsafe_allow_html=True
)
