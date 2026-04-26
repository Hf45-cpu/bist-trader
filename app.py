"""
BIST PRO — Profesyonel Swing Trading Sistemi v2.0
Tüm analistlerin kullandığı 25+ indikatör dahil
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="BIST PRO Trader",page_icon="📊",layout="wide",initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp{background-color:#04111e;color:#c8e4f8}
    .main{background-color:#04111e}
    h1,h2,h3,h4{color:#c8e4f8!important}
    .stTabs [data-baseweb="tab"]{color:#5588aa;font-weight:600}
    .stTabs [aria-selected="true"]{color:#00c8ff!important;border-bottom-color:#00c8ff!important}
    .stSelectbox label,.stSlider label,.stNumberInput label{color:#5588aa!important}
    div[data-testid="stMetricValue"]{font-family:monospace;font-size:1.4rem!important}
    .ind-table{width:100%;border-collapse:collapse}
    .ind-table th{background:#0b2035;color:#00c8ff;padding:10px;text-align:left;font-size:12px}
    .ind-table td{padding:9px;border-bottom:1px solid #143350;font-size:11px;color:#c8e4f8}
    .ind-table tr:hover{background:#0f2540}
    .info-box{background:#0b2035;border:1px solid #143350;border-radius:10px;padding:14px;margin-bottom:10px}
    .warn-box{background:#ffc84010;border:1px solid #ffc84044;border-radius:10px;padding:10px;margin-bottom:8px}
</style>
""",unsafe_allow_html=True)

HISSELER={
    "GARAN":{"isim":"Garanti BBVA","sektor":"Bankacılık"},
    "AKBNK":{"isim":"Akbank","sektor":"Bankacılık"},
    "YKBNK":{"isim":"Yapı Kredi","sektor":"Bankacılık"},
    "ISCTR":{"isim":"İş Bankası C","sektor":"Bankacılık"},
    "VAKBN":{"isim":"Vakıfbank","sektor":"Bankacılık"},
    "HALKB":{"isim":"Halkbank","sektor":"Bankacılık"},
    "ASELS":{"isim":"Aselsan","sektor":"Savunma"},
    "TUPRS":{"isim":"Tüpraş","sektor":"Enerji"},
    "AKSEN":{"isim":"Aksa Enerji","sektor":"Enerji"},
    "THYAO":{"isim":"Türk Hava Yolları","sektor":"Ulaşım"},
    "PGSUS":{"isim":"Pegasus","sektor":"Ulaşım"},
    "KCHOL":{"isim":"Koç Holding","sektor":"Holding"},
    "SAHOL":{"isim":"Sabancı Holding","sektor":"Holding"},
    "EREGL":{"isim":"Ereğli Demir","sektor":"Metal"},
    "FROTO":{"isim":"Ford Otosan","sektor":"Otomotiv"},
    "TOASO":{"isim":"Tofaş Oto","sektor":"Otomotiv"},
    "LOGO":{"isim":"Logo Yazılım","sektor":"Teknoloji"},
    "INDES":{"isim":"İndeks Bilgisayar","sektor":"Teknoloji"},
    "TCELL":{"isim":"Turkcell","sektor":"Telekom"},
    "SISE":{"isim":"Şişe Cam","sektor":"Sanayi"},
    "EKGYO":{"isim":"Emlak Konut GYO","sektor":"GYO"},
    "BIMAS":{"isim":"BİM Mağazalar","sektor":"Perakende"},
    "MGROS":{"isim":"Migros","sektor":"Perakende"},
    "PETKM":{"isim":"Petkim","sektor":"Kimya"},
    "KOZAL":{"isim":"Koza Altın","sektor":"Madencilik"},
}

@st.cache_data(ttl=900)
def veri_cek(kod,period="1y"):
    try:
        df=yf.Ticker(f"{kod}.IS").history(period=period)
        if df.empty:return None
        df.index=pd.to_datetime(df.index).tz_localize(None)
        df.columns=[c.lower() for c in df.columns]
        return df
    except:return None

@st.cache_data(ttl=900)
def endeks_cek():
    semboller={"BIST 100":"XU100.IS","BIST 30":"XU030.IS","USD/TRY":"USDTRY=X","EUR/TRY":"EURTRY=X","Altın":"GC=F","Brent":"BZ=F","VIX":"^VIX"}
    sonuc={}
    for isim,sembol in semboller.items():
        try:
            h=yf.Ticker(sembol).history(period="5d")
            if not h.empty:
                s=h["Close"].iloc[-1];o=h["Close"].iloc[-2] if len(h)>1 else s
                sonuc[isim]={"deger":s,"degisim":(s-o)/o*100}
        except:pass
    return sonuc

def indikatör_hesapla(df):
    df=df.copy();c=df["close"]
    df["ema9"]=ta.trend.EMAIndicator(c,9).ema_indicator()
    df["ema21"]=ta.trend.EMAIndicator(c,21).ema_indicator()
    df["ema50"]=ta.trend.EMAIndicator(c,50).ema_indicator()
    df["ema200"]=ta.trend.EMAIndicator(c,200).ema_indicator()
    df["sma20"]=ta.trend.SMAIndicator(c,20).sma_indicator()
    df["sma50"]=ta.trend.SMAIndicator(c,50).sma_indicator()
    df["rsi"]=ta.momentum.RSIIndicator(c,14).rsi()
    df["rsi9"]=ta.momentum.RSIIndicator(c,9).rsi()
    stoch=ta.momentum.StochasticOscillator(df["high"],df["low"],c)
    df["stoch_k"]=stoch.stoch();df["stoch_d"]=stoch.stoch_signal()
    df["cci"]=ta.trend.CCIIndicator(df["high"],df["low"],c).cci()
    df["williams_r"]=ta.momentum.WilliamsRIndicator(df["high"],df["low"],c).williams_r()
    df["roc"]=ta.momentum.ROCIndicator(c).roc()
    macd=ta.trend.MACD(c)
    df["macd"]=macd.macd();df["macd_signal"]=macd.macd_signal();df["macd_hist"]=macd.macd_diff()
    bb=ta.volatility.BollingerBands(c,20,2)
    df["bb_ust"]=bb.bollinger_hband();df["bb_orta"]=bb.bollinger_mavg()
    df["bb_alt"]=bb.bollinger_lband();df["bb_width"]=(df["bb_ust"]-df["bb_alt"])/df["bb_orta"]*100
    df["atr"]=ta.volatility.AverageTrueRange(df["high"],df["low"],c).average_true_range()
    df["obv"]=ta.volume.OnBalanceVolumeIndicator(c,df["volume"]).on_balance_volume()
    df["vwap"]=(df["volume"]*(df["high"]+df["low"]+c)/3).cumsum()/df["volume"].cumsum()
    df["mfi"]=ta.volume.MFIIndicator(df["high"],df["low"],c,df["volume"]).money_flow_index()
    df["cmf"]=ta.volume.ChaikinMoneyFlowIndicator(df["high"],df["low"],c,df["volume"]).chaikin_money_flow()
    df["hacim_ema"]=df["volume"].ewm(span=20).mean()
    df["hacim_oran"]=df["volume"]/df["hacim_ema"]
    adx_ind=ta.trend.ADXIndicator(df["high"],df["low"],c)
    df["adx"]=adx_ind.adx();df["adx_pos"]=adx_ind.adx_pos();df["adx_neg"]=adx_ind.adx_neg()
    df["psar"]=ta.trend.PSARIndicator(df["high"],df["low"],c).psar()
    aroon=ta.trend.AroonIndicator(df["high"],df["low"])
    df["aroon_up"]=aroon.aroon_up();df["aroon_dn"]=aroon.aroon_down()
    df["pivot"]=(df["high"]+df["low"]+c)/3
    df["r1"]=2*df["pivot"]-df["low"];df["s1"]=2*df["pivot"]-df["high"]
    df["r2"]=df["pivot"]+(df["high"]-df["low"]);df["s2"]=df["pivot"]-(df["high"]-df["low"])
    return df

def sinyal_uret(df):
    if df is None or len(df)<60:return{"sinyal":"VERİ YOK","puan":0,"sebepler":[]}
    son=df.iloc[-1];onc=df.iloc[-2];puan=0;sebepler=[]
    if pd.notna(son["rsi"]):
        if son["rsi"]<30:sebepler.append(f"🟢 RSI AŞIRI SATILMIŞ ({son['rsi']:.0f}) — Güçlü al");puan+=3
        elif son["rsi"]<40:sebepler.append(f"🟢 RSI alım bölgesi ({son['rsi']:.0f})");puan+=2
        elif son["rsi"]<50:sebepler.append(f"🟡 RSI nötr-pozitif ({son['rsi']:.0f})");puan+=1
        elif son["rsi"]>80:sebepler.append(f"🔴 RSI AŞIRI ALINMIŞ ({son['rsi']:.0f})");puan-=3
        elif son["rsi"]>70:sebepler.append(f"🔴 RSI yüksek ({son['rsi']:.0f})");puan-=2
        elif son["rsi"]>60:sebepler.append(f"🟡 RSI yükseliyor ({son['rsi']:.0f})");puan-=1
    if pd.notna(son["macd_hist"]) and pd.notna(onc["macd_hist"]):
        if onc["macd_hist"]<=0 and son["macd_hist"]>0:sebepler.append("🟢 MACD YUKARI KESİŞ — En güçlü al sinyali");puan+=3
        elif son["macd_hist"]>0:sebepler.append("🟡 MACD pozitif bölge");puan+=1
        elif onc["macd_hist"]>=0 and son["macd_hist"]<0:sebepler.append("🔴 MACD AŞAĞI KESİŞ — Güçlü sat");puan-=3
        elif son["macd_hist"]<0:sebepler.append("🟡 MACD negatif");puan-=1
    if pd.notna(son["ema21"]) and pd.notna(son["ema50"]) and pd.notna(son["ema200"]):
        if son["close"]>son["ema200"]:sebepler.append("🟢 EMA200 üstünde (uzun vade pozitif)");puan+=1
        else:sebepler.append("🔴 EMA200 altında (uzun vade negatif)");puan-=1
        if onc["ema21"]<=onc["ema50"] and son["ema21"]>son["ema50"]:sebepler.append("🟢 ALTIN KESİŞ!");puan+=3
        elif onc["ema21"]>=onc["ema50"] and son["ema21"]<son["ema50"]:sebepler.append("🔴 ÖLÜM KESİŞ!");puan-=3
        elif son["ema21"]>son["ema50"]:sebepler.append("🟡 EMA21>EMA50 trend yukarı");puan+=1
        else:sebepler.append("🟡 EMA21<EMA50 trend aşağı");puan-=1
    if pd.notna(son["bb_alt"]) and pd.notna(son["bb_ust"]):
        if son["close"]<son["bb_alt"]:sebepler.append("🟢 Alt Bollinger — dip bölgesi");puan+=2
        elif son["close"]>son["bb_ust"]:sebepler.append("🔴 Üst Bollinger — tepe bölgesi");puan-=2
        if pd.notna(son["bb_width"]) and son["bb_width"]<5:sebepler.append("⚡ BOLLİNGER SIKIŞMA — Büyük hareket yaklaşıyor")
    if pd.notna(son["stoch_k"]):
        if son["stoch_k"]<20 and son["stoch_k"]>son["stoch_d"]:sebepler.append("🟢 Stochastic aşırı satılmış + yukarı");puan+=2
        elif son["stoch_k"]>80 and son["stoch_k"]<son["stoch_d"]:sebepler.append("🔴 Stochastic aşırı alınmış + aşağı");puan-=2
    if pd.notna(son["adx"]):
        if son["adx"]>25:
            if son["adx_pos"]>son["adx_neg"]:sebepler.append(f"🟢 ADX güçlü yukarı trend ({son['adx']:.0f})");puan+=1
            else:sebepler.append(f"🔴 ADX güçlü aşağı trend ({son['adx']:.0f})");puan-=1
        else:sebepler.append(f"⚠️ ADX zayıf trend ({son['adx']:.0f}) — yatay piyasa")
    if pd.notna(son["vwap"]):
        if son["close"]>son["vwap"]:sebepler.append("🟢 VWAP üstünde (kurumsal alım bölgesi)");puan+=1
        else:sebepler.append("🔴 VWAP altında");puan-=1
    if pd.notna(son["mfi"]):
        if son["mfi"]<20:sebepler.append("🟢 MFI aşırı satılmış");puan+=2
        elif son["mfi"]>80:sebepler.append("🔴 MFI aşırı alınmış");puan-=2
    if pd.notna(son["psar"]):
        if son["close"]>son["psar"]:sebepler.append("🟢 Parabolic SAR altında — trend yukarı");puan+=1
        else:sebepler.append("🔴 Parabolic SAR üstünde — trend aşağı");puan-=1
    if pd.notna(son["hacim_oran"]):
        if son["hacim_oran"]>2 and puan>0:sebepler.append(f"🟢 HACİM {son['hacim_oran']:.1f}x — Güçlü teyit!");puan+=2
        elif son["hacim_oran"]>1.5 and puan>0:sebepler.append(f"🟡 Hacim {son['hacim_oran']:.1f}x ortalamanın üstünde");puan+=1
        elif son["hacim_oran"]<0.5:sebepler.append("⚠️ Düşük hacim — sinyal zayıf")
    if puan>=8:sinyal="🚀 GÜÇLÜ AL"
    elif puan>=4:sinyal="🟢 AL"
    elif puan>=1:sinyal="🟡 ZAYIF AL"
    elif puan<=-8:sinyal="🔴 GÜÇLÜ SAT"
    elif puan<=-4:sinyal="🔴 SAT"
    elif puan<=-1:sinyal="🟡 ZAYIF SAT"
    else:sinyal="⚪ BEKLE"
    return{"sinyal":sinyal,"puan":puan,"sebepler":sebepler,
        "rsi":son["rsi"],"ema21":son["ema21"],"ema50":son["ema50"],"ema200":son["ema200"],
        "macd_hist":son["macd_hist"],"adx":son["adx"],"atr":son["atr"],"vwap":son["vwap"],
        "bb_alt":son["bb_alt"],"bb_ust":son["bb_ust"],"stoch_k":son["stoch_k"],
        "mfi":son["mfi"],"psar":son["psar"],"pivot":son["pivot"],
        "r1":son["r1"],"s1":son["s1"],"r2":son["r2"],"s2":son["s2"]}

def backtest_calistir(df,strateji,sermaye,komisyon,stop_loss,take_profit):
    df=df.copy().reset_index();c=df["close"].values
    rsi_s=ta.momentum.RSIIndicator(pd.Series(c),14).rsi().values
    ema21_s=ta.trend.EMAIndicator(pd.Series(c),21).ema_indicator().values
    ema50_s=ta.trend.EMAIndicator(pd.Series(c),50).ema_indicator().values
    macd_h=ta.trend.MACD(pd.Series(c)).macd_diff().values
    bb_alt=ta.volatility.BollingerBands(pd.Series(c)).bollinger_lband().values
    bb_ust=ta.volatility.BollingerBands(pd.Series(c)).bollinger_hband().values
    stoch_k=ta.momentum.StochasticOscillator(df["high"],df["low"],pd.Series(c)).stoch().values
    adx_s=ta.trend.ADXIndicator(df["high"],df["low"],pd.Series(c)).adx().values
    sinyaller=[]
    for i in range(len(df)):
        s=None
        if strateji=="RSI Swing":
            if not np.isnan(rsi_s[i]):
                if rsi_s[i]<35:s="AL"
                elif rsi_s[i]>65:s="SAT"
        elif strateji=="EMA Kesişim":
            if i>0 and not np.isnan(ema21_s[i]) and not np.isnan(ema50_s[i]):
                if ema21_s[i-1]<=ema50_s[i-1] and ema21_s[i]>ema50_s[i]:s="AL"
                elif ema21_s[i-1]>=ema50_s[i-1] and ema21_s[i]<ema50_s[i]:s="SAT"
        elif strateji=="Bollinger Bandı":
            if not np.isnan(bb_alt[i]):
                if c[i]<=bb_alt[i]:s="AL"
                elif c[i]>=bb_ust[i]:s="SAT"
        elif strateji=="MACD + RSI":
            if i>0 and not np.isnan(macd_h[i]) and not np.isnan(rsi_s[i]):
                if macd_h[i-1]<=0 and macd_h[i]>0 and rsi_s[i]<55:s="AL"
                elif macd_h[i-1]>=0 and macd_h[i]<0:s="SAT"
        elif strateji=="Stochastic + RSI":
            if not np.isnan(stoch_k[i]) and not np.isnan(rsi_s[i]):
                if stoch_k[i]<25 and rsi_s[i]<45:s="AL"
                elif stoch_k[i]>75 and rsi_s[i]>55:s="SAT"
        elif strateji=="ADX Trend":
            if i>0 and not np.isnan(adx_s[i]) and not np.isnan(ema21_s[i]) and not np.isnan(ema50_s[i]):
                if adx_s[i]>25 and ema21_s[i]>ema50_s[i] and c[i]>ema21_s[i]:s="AL"
                elif adx_s[i]>25 and ema21_s[i]<ema50_s[i]:s="SAT"
        elif strateji=="Kombine (Tüm)":
            if not np.isnan(rsi_s[i]) and not np.isnan(macd_h[i]) and not np.isnan(ema50_s[i]):
                al_p=int(rsi_s[i]<45)+int(c[i]>ema50_s[i])+int(macd_h[i]>0)+int(not np.isnan(bb_alt[i]) and c[i]<bb_alt[i]*1.02)
                sat_p=int(rsi_s[i]>60)+int(c[i]<ema50_s[i])+int(macd_h[i]<0)+int(not np.isnan(bb_ust[i]) and c[i]>bb_ust[i]*0.98)
                if al_p>=3:s="AL"
                elif sat_p>=3:s="SAT"
        sinyaller.append(s)
    nakit=sermaye;poz=None;islemler=[];egri=[sermaye]
    for i in range(1,len(df)):
        row=df.iloc[i]
        if poz:
            stop_t=row["low"]<=poz["alis"]*(1-stop_loss/100)
            hedef_t=row["high"]>=poz["alis"]*(1+take_profit/100)
            cf=None;neden=None
            if stop_t:cf=poz["alis"]*(1-stop_loss/100);neden="Stop-Loss"
            elif hedef_t:cf=poz["alis"]*(1+take_profit/100);neden="Take-Profit"
            elif sinyaller[i]=="SAT":cf=row["close"];neden="Sinyal"
            if cf:
                gelir=poz["adet"]*cf*(1-komisyon/100);pnl=gelir-poz["maliyet"];nakit+=gelir
                islemler.append({"Giriş":str(poz["tarih"])[:10],"Çıkış":str(row.get("Date",row.name))[:10],
                    "Alış ₺":round(poz["alis"],2),"Satış ₺":round(cf,2),
                    "Kâr/Zarar ₺":round(pnl,2),"% Getiri":round(pnl/poz["maliyet"]*100,2),
                    "Neden":neden,"Gün":i-poz["gun"]});poz=None
        if not poz and sinyaller[i]=="AL" and nakit>100:
            kullan=nakit*0.95;adet=int(kullan/(row["close"]*(1+komisyon/100)))
            if adet>0:
                mal=adet*row["close"]*(1+komisyon/100);nakit-=mal
                tarih=row.get("Date",row.name)
                poz={"alis":row["close"],"adet":adet,"maliyet":mal,"tarih":tarih,"gun":i}
        portfoy=nakit+(poz["adet"]*row["close"] if poz else 0);egri.append(portfoy)
    if poz:
        son=df.iloc[-1];gelir=poz["adet"]*son["close"]*(1-komisyon/100);pnl=gelir-poz["maliyet"];nakit+=gelir
        islemler.append({"Giriş":str(poz["tarih"])[:10],"Çıkış":str(son.get("Date",son.name))[:10],
            "Alış ₺":round(poz["alis"],2),"Satış ₺":round(son["close"],2),
            "Kâr/Zarar ₺":round(pnl,2),"% Getiri":round(pnl/poz["maliyet"]*100,2),
            "Neden":"Dönem Sonu","Gün":len(df)-1-poz["gun"]})
    idf=pd.DataFrame(islemler) if islemler else pd.DataFrame()
    son_d=egri[-1];getiri=(son_d-sermaye)/sermaye*100
    kaz=idf[idf["Kâr/Zarar ₺"]>0] if len(idf) else pd.DataFrame()
    kay=idf[idf["Kâr/Zarar ₺"]<=0] if len(idf) else pd.DataFrame()
    egri_s=pd.Series(egri);tepe=egri_s.cummax();dd=(egri_s-tepe)/tepe*100;max_dd=dd.min()
    gr=pd.Series(egri).pct_change().dropna()
    sharpe=(gr.mean()/gr.std()*np.sqrt(252)) if gr.std()>0 else 0
    al_tut=(c[-1]-c[0])/c[0]*100
    return{"islemler":idf,"egri":egri,"sinyaller":sinyaller,"df":df,
        "ist":{"toplam":len(idf),"kazanan":len(kaz),"kaybeden":len(kay),
            "kazanma_orani":round(len(kaz)/max(len(idf),1)*100,1),
            "getiri":round(getiri,2),"al_tut":round(al_tut,2),
            "max_dd":round(float(max_dd),2),"sharpe":round(float(sharpe),2),
            "son_deger":round(son_d,2),
            "toplam_pnl":round(idf["Kâr/Zarar ₺"].sum(),2) if len(idf) else 0,
            "ort_kazanc":round(kaz["Kâr/Zarar ₺"].mean(),2) if len(kaz) else 0,
            "ort_kayip":round(kay["Kâr/Zarar ₺"].mean(),2) if len(kay) else 0,
            "ort_tutma":round(idf["Gün"].mean(),1) if len(idf) else 0}}

def mumlu_grafik(df,sinyaller=None,goster=None):
    if goster is None:goster=["EMA21","EMA50","Bollinger"]
    fig=make_subplots(rows=4,cols=1,shared_xaxes=True,row_heights=[0.5,0.15,0.2,0.15],vertical_spacing=0.02)
    fig.add_trace(go.Candlestick(x=df.index,open=df["open"],high=df["high"],low=df["low"],close=df["close"],
        increasing_line_color="#00e59a",decreasing_line_color="#ff3e5e",name="Fiyat"),row=1,col=1)
    if "EMA21" in goster and "ema21" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["ema21"],line=dict(color="#00c8ff",width=1.5),name="EMA21"),row=1,col=1)
    if "EMA50" in goster and "ema50" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["ema50"],line=dict(color="#ffc840",width=1.5),name="EMA50"),row=1,col=1)
    if "EMA200" in goster and "ema200" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["ema200"],line=dict(color="#a855f7",width=2),name="EMA200"),row=1,col=1)
    if "Bollinger" in goster and "bb_ust" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["bb_ust"],line=dict(color="#5588aa",width=1,dash="dot"),name="BB Üst"),row=1,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df["bb_alt"],line=dict(color="#5588aa",width=1,dash="dot"),
            fill="tonexty",fillcolor="rgba(85,136,170,0.05)",name="BB Alt"),row=1,col=1)
    if "VWAP" in goster and "vwap" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["vwap"],line=dict(color="#ff8844",width=1.5,dash="dash"),name="VWAP"),row=1,col=1)
    if "PSAR" in goster and "psar" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["psar"],mode="markers",marker=dict(size=3,color="#ff3e5e"),name="PSAR"),row=1,col=1)
    if sinyaller is not None:
        al_x=[df.index[i] for i,s in enumerate(sinyaller) if s=="AL" and i<len(df)]
        al_y=[df["low"].iloc[i]*0.97 for i,s in enumerate(sinyaller) if s=="AL" and i<len(df)]
        sat_x=[df.index[i] for i,s in enumerate(sinyaller) if s=="SAT" and i<len(df)]
        sat_y=[df["high"].iloc[i]*1.03 for i,s in enumerate(sinyaller) if s=="SAT" and i<len(df)]
        if al_x:fig.add_trace(go.Scatter(x=al_x,y=al_y,mode="markers",marker=dict(symbol="triangle-up",size=12,color="#00e59a"),name="AL"),row=1,col=1)
        if sat_x:fig.add_trace(go.Scatter(x=sat_x,y=sat_y,mode="markers",marker=dict(symbol="triangle-down",size=12,color="#ff3e5e"),name="SAT"),row=1,col=1)
    renkler=["#00e59a" if c>=o else "#ff3e5e" for c,o in zip(df["close"],df["open"])]
    fig.add_trace(go.Bar(x=df.index,y=df["volume"],marker_color=renkler,name="Hacim",opacity=0.7),row=2,col=1)
    if "macd" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["macd"],line=dict(color="#00c8ff",width=1.5),name="MACD"),row=3,col=1)
        fig.add_trace(go.Scatter(x=df.index,y=df["macd_signal"],line=dict(color="#ff8844",width=1.5),name="Sinyal"),row=3,col=1)
        colors=["#00e59a" if v>=0 else "#ff3e5e" for v in df["macd_hist"].fillna(0)]
        fig.add_trace(go.Bar(x=df.index,y=df["macd_hist"],marker_color=colors,name="Hist"),row=3,col=1)
    if "rsi" in df.columns:
        fig.add_trace(go.Scatter(x=df.index,y=df["rsi"],line=dict(color="#a855f7",width=2),name="RSI"),row=4,col=1)
        fig.add_hline(y=70,line_color="#ff3e5e",line_dash="dot",line_width=1,row=4,col=1)
        fig.add_hline(y=30,line_color="#00e59a",line_dash="dot",line_width=1,row=4,col=1)
        fig.add_hline(y=50,line_color="#5588aa",line_dash="dot",line_width=0.5,row=4,col=1)
    fig.update_layout(paper_bgcolor="#04111e",plot_bgcolor="#071828",font=dict(color="#5588aa"),
        xaxis_rangeslider_visible=False,height=700,showlegend=True,
        legend=dict(bgcolor="#0b2035",bordercolor="#143350",font=dict(color="#c8e4f8",size=11)),
        margin=dict(l=10,r=10,t=20,b=10))
    fig.update_xaxes(gridcolor="#143350",showgrid=True)
    fig.update_yaxes(gridcolor="#143350",showgrid=True)
    return fig

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 BIST PRO")
    secilenKod=st.selectbox("Hisse",list(HISSELER.keys()),format_func=lambda k:f"{k} — {HISSELER[k]['isim']}")
    period=st.selectbox("Periyot",["1mo","3mo","6mo","1y","2y"],index=3,
        format_func=lambda x:{"1mo":"1 Ay","3mo":"3 Ay","6mo":"6 Ay","1y":"1 Yıl","2y":"2 Yıl"}[x])
    st.markdown("---")
    st.markdown("### ⚗️ Backtest")
    strateji=st.selectbox("Strateji",["RSI Swing","EMA Kesişim","Bollinger Bandı","MACD + RSI","Stochastic + RSI","ADX Trend","Kombine (Tüm)"])
    sermaye=st.number_input("Sermaye (₺)",10000,10000000,100000,10000)
    komisyon=st.slider("Komisyon (%)",0.01,0.50,0.10,0.01)
    stop_loss=st.slider("Stop-Loss (%)",2.0,20.0,8.0,0.5)
    take_profit=st.slider("Take-Profit (%)",5.0,50.0,20.0,1.0)
    st.markdown("---")
    if st.button("🔄 Yenile",use_container_width=True):st.cache_data.clear();st.rerun()
    st.warning("⏱ 15dk gecikmeli")
    st.info(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

# ─── VERİ ────────────────────────────────────────────────────────────────────
st.markdown(f"# 📊 {secilenKod} — {HISSELER[secilenKod]['isim']}")
with st.spinner("Veri çekiliyor..."):
    df=veri_cek(secilenKod,period);endeks=endeks_cek()
if df is None:st.error("Veri alınamadı.");st.stop()
df=indikatör_hesapla(df);sig=sinyal_uret(df)
son=df.iloc[-1];onc=df.iloc[-2];degisim=(son["close"]-onc["close"])/onc["close"]*100

# ─── SEKMELER ────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5=st.tabs(["📈 Analiz","🎯 Sinyaller","⚗️ Backtest","🔍 Tarama","📚 İndikatör Rehberi"])

with tab1:
    cols=st.columns(7)
    for i,(isim,v) in enumerate(endeks.items()):
        with cols[i%7]:st.metric(isim,f"{v['deger']:,.2f}",f"{v['degisim']:+.2f}%",delta_color="normal" if v["degisim"]>=0 else "inverse")
    st.markdown("---")
    col1,col2,col3=st.columns([1.5,1,1])
    with col1:
        st.markdown(f"""<div style='margin-bottom:12px'>
        <span style='font-size:38px;font-weight:900;color:#c8e4f8'>{son['close']:.2f} ₺</span>
        <span style='font-size:20px;font-weight:700;color:{"#00e59a" if degisim>=0 else "#ff3e5e"};margin-left:12px'>{degisim:+.2f}%</span>
        </div><div style='color:#5588aa;font-size:12px'>A:{son['open']:.2f} Y:{son['high']:.2f} D:{son['low']:.2f} H:{int(son['volume']):,}</div>""",unsafe_allow_html=True)
    with col2:
        renk={"AL":"#00e59a","SAT":"#ff3e5e"};r=next((v for k,v in renk.items() if k in sig["sinyal"]),"#ffc840")
        st.markdown(f"""<div style='text-align:center;padding:16px;background:#0b2035;border-radius:12px;border:2px solid {r}'>
        <div style='font-size:10px;color:#5588aa;margin-bottom:6px'>GÜNCEL SİNYAL</div>
        <div style='font-size:20px;font-weight:900;color:{r}'>{sig["sinyal"]}</div>
        <div style='font-size:12px;color:#5588aa;margin-top:6px'>Puan: {sig["puan"]:+d}/20</div></div>""",unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div style='padding:16px;background:#0b2035;border-radius:12px'>
        <div style='font-size:10px;color:#5588aa;margin-bottom:8px'>DESTEK / DİRENÇ</div>
        <div style='display:flex;justify-content:space-between'><span style='color:#ff3e5e;font-size:12px'>R2</span><span style='color:#c8e4f8;font-size:12px;font-family:monospace'>{sig["r2"]:.2f} ₺</span></div>
        <div style='display:flex;justify-content:space-between'><span style='color:#ff8844;font-size:12px'>R1</span><span style='color:#c8e4f8;font-size:12px;font-family:monospace'>{sig["r1"]:.2f} ₺</span></div>
        <div style='display:flex;justify-content:space-between;border-top:1px solid #143350;padding-top:4px'><span style='color:#00c8ff;font-size:12px'>PİVOT</span><span style='color:#00c8ff;font-size:12px;font-family:monospace'>{sig["pivot"]:.2f} ₺</span></div>
        <div style='display:flex;justify-content:space-between'><span style='color:#ffc840;font-size:12px'>S1</span><span style='color:#c8e4f8;font-size:12px;font-family:monospace'>{sig["s1"]:.2f} ₺</span></div>
        <div style='display:flex;justify-content:space-between'><span style='color:#00e59a;font-size:12px'>S2</span><span style='color:#c8e4f8;font-size:12px;font-family:monospace'>{sig["s2"]:.2f} ₺</span></div>
        </div>""",unsafe_allow_html=True)
    st.markdown("### 📊 İndikatör Özeti")
    c1,c2,c3,c4,c5,c6=st.columns(6)
    with c1:st.metric("RSI(14)",f"{sig['rsi']:.1f}" if sig['rsi'] else "—","Aşırı satılmış" if sig['rsi'] and sig['rsi']<30 else "Aşırı alınmış" if sig['rsi'] and sig['rsi']>70 else "Normal")
    with c2:st.metric("MACD Hist",f"{sig['macd_hist']:.4f}" if sig['macd_hist'] else "—","Pozitif ↑" if sig['macd_hist'] and sig['macd_hist']>0 else "Negatif ↓")
    with c3:st.metric("ADX",f"{sig['adx']:.1f}" if sig['adx'] else "—","Güçlü trend" if sig['adx'] and sig['adx']>25 else "Zayıf trend")
    with c4:st.metric("ATR",f"{sig['atr']:.2f}" if sig['atr'] else "—","Volatilite")
    with c5:st.metric("Stoch K",f"{sig['stoch_k']:.1f}" if sig['stoch_k'] else "—","Aşırı satılmış" if sig['stoch_k'] and sig['stoch_k']<20 else "Aşırı alınmış" if sig['stoch_k'] and sig['stoch_k']>80 else "Normal")
    with c6:st.metric("MFI",f"{sig['mfi']:.1f}" if sig['mfi'] else "—","Para girişi" if sig['mfi'] and sig['mfi']<20 else "Para çıkışı" if sig['mfi'] and sig['mfi']>80 else "Normal")
    goster=st.multiselect("Göstergeler",["EMA21","EMA50","EMA200","Bollinger","VWAP","PSAR"],default=["EMA21","EMA50","Bollinger"])
    st.plotly_chart(mumlu_grafik(df.tail(120),goster=goster),use_container_width=True)
    st.markdown("### 🎯 Risk Seviyeleri")
    c1,c2,c3,c4=st.columns(4)
    with c1:st.metric("Stop-Loss (%8)",f"{son['close']*0.92:.2f} ₺",f"-{son['close']*0.08:.2f} ₺",delta_color="inverse")
    with c2:st.metric("Güncel",f"{son['close']:.2f} ₺",f"{degisim:+.2f}%")
    with c3:st.metric("Hedef 1 (%15)",f"{son['close']*1.15:.2f} ₺",f"+{son['close']*0.15:.2f} ₺")
    with c4:st.metric("Hedef 2 (%25)",f"{son['close']*1.25:.2f} ₺",f"+{son['close']*0.25:.2f} ₺")

with tab2:
    st.markdown("### 🎯 Sinyal Analizi")
    col1,col2=st.columns(2)
    with col1:
        st.markdown("#### 🟢 Pozitif Sinyaller")
        poz=[s for s in sig["sebepler"] if "🟢" in s]
        for s in poz:st.markdown(f"<div class='info-box'>{s}</div>",unsafe_allow_html=True)
        if not poz:st.info("Pozitif sinyal yok")
    with col2:
        st.markdown("#### 🔴 Negatif Sinyaller")
        neg=[s for s in sig["sebepler"] if "🔴" in s]
        for s in neg:st.markdown(f"<div class='info-box'>{s}</div>",unsafe_allow_html=True)
        if not neg:st.info("Negatif sinyal yok")
    st.markdown("#### ⚡ Uyarılar")
    for u in [s for s in sig["sebepler"] if "🟡" in s or "⚠️" in s or "⚡" in s]:
        st.markdown(f"<div class='warn-box'>{u}</div>",unsafe_allow_html=True)
    st.markdown("### 📋 Tüm İndikatör Değerleri")
    ind_tablo={"RSI (14)":f"{son['rsi']:.2f}" if pd.notna(son['rsi']) else "—",
        "RSI (9)":f"{son['rsi9']:.2f}" if pd.notna(son['rsi9']) else "—",
        "MACD":f"{son['macd']:.4f}" if pd.notna(son['macd']) else "—",
        "MACD Sinyal":f"{son['macd_signal']:.4f}" if pd.notna(son['macd_signal']) else "—",
        "MACD Histogram":f"{son['macd_hist']:.4f}" if pd.notna(son['macd_hist']) else "—",
        "Stochastic %K":f"{son['stoch_k']:.2f}" if pd.notna(son['stoch_k']) else "—",
        "Stochastic %D":f"{son['stoch_d']:.2f}" if pd.notna(son['stoch_d']) else "—",
        "CCI":f"{son['cci']:.2f}" if pd.notna(son['cci']) else "—",
        "Williams %R":f"{son['williams_r']:.2f}" if pd.notna(son['williams_r']) else "—",
        "ROC":f"{son['roc']:.4f}" if pd.notna(son['roc']) else "—",
        "MFI":f"{son['mfi']:.2f}" if pd.notna(son['mfi']) else "—",
        "CMF":f"{son['cmf']:.4f}" if pd.notna(son['cmf']) else "—",
        "ADX":f"{son['adx']:.2f}" if pd.notna(son['adx']) else "—",
        "ADX+":f"{son['adx_pos']:.2f}" if pd.notna(son['adx_pos']) else "—",
        "ADX-":f"{son['adx_neg']:.2f}" if pd.notna(son['adx_neg']) else "—",
        "ATR":f"{son['atr']:.4f}" if pd.notna(son['atr']) else "—",
        "BB Üst":f"{son['bb_ust']:.2f}" if pd.notna(son['bb_ust']) else "—",
        "BB Orta":f"{son['bb_orta']:.2f}" if pd.notna(son['bb_orta']) else "—",
        "BB Alt":f"{son['bb_alt']:.2f}" if pd.notna(son['bb_alt']) else "—",
        "BB Width":f"{son['bb_width']:.2f}%" if pd.notna(son['bb_width']) else "—",
        "EMA 9":f"{son['ema9']:.2f}" if pd.notna(son['ema9']) else "—",
        "EMA 21":f"{son['ema21']:.2f}" if pd.notna(son['ema21']) else "—",
        "EMA 50":f"{son['ema50']:.2f}" if pd.notna(son['ema50']) else "—",
        "EMA 200":f"{son['ema200']:.2f}" if pd.notna(son['ema200']) else "—",
        "SMA 20":f"{son['sma20']:.2f}" if pd.notna(son['sma20']) else "—",
        "SMA 50":f"{son['sma50']:.2f}" if pd.notna(son['sma50']) else "—",
        "VWAP":f"{son['vwap']:.2f}" if pd.notna(son['vwap']) else "—",
        "Parabolic SAR":f"{son['psar']:.2f}" if pd.notna(son['psar']) else "—",
        "Aroon Up":f"{son['aroon_up']:.2f}" if pd.notna(son['aroon_up']) else "—",
        "Aroon Down":f"{son['aroon_dn']:.2f}" if pd.notna(son['aroon_dn']) else "—",
        "Pivot":f"{son['pivot']:.2f}" if pd.notna(son['pivot']) else "—",
        "R1":f"{son['r1']:.2f}" if pd.notna(son['r1']) else "—",
        "R2":f"{son['r2']:.2f}" if pd.notna(son['r2']) else "—",
        "S1":f"{son['s1']:.2f}" if pd.notna(son['s1']) else "—",
        "S2":f"{son['s2']:.2f}" if pd.notna(son['s2']) else "—"}
    st.dataframe(pd.DataFrame(list(ind_tablo.items()),columns=["İndikatör","Değer"]),use_container_width=True,height=600,hide_index=True)

with tab3:
    st.markdown(f"### ⚗️ {strateji} — {secilenKod}")
    if st.button("▶ Backtest Çalıştır",type="primary",use_container_width=True):
        with st.spinner("Hesaplanıyor..."):
            bt=backtest_calistir(df,strateji,sermaye,komisyon,stop_loss,take_profit)
            st.session_state["bt"]=bt
    if "bt" in st.session_state:
        bt=st.session_state["bt"];ist=bt["ist"]
        c1,c2,c3,c4,c5=st.columns(5)
        with c1:st.metric("Toplam Getiri",f"{ist['getiri']:+.1f}%",f"Al-tut:{ist['al_tut']:+.1f}%",delta_color="normal" if ist['getiri']>=ist['al_tut'] else "inverse")
        with c2:st.metric("Kazanma Oranı",f"%{ist['kazanma_orani']}",f"{ist['kazanan']}K/{ist['kaybeden']}Z")
        with c3:st.metric("Max Drawdown",f"{ist['max_dd']:.1f}%",delta_color="inverse")
        with c4:st.metric("Sharpe",f"{ist['sharpe']:.2f}","İyi ✓" if ist['sharpe']>=1 else "Zayıf")
        with c5:st.metric("Son Değer",f"{ist['son_deger']:,.0f} ₺",f"{ist['toplam_pnl']:+,.0f} ₺")
        fig2=go.Figure()
        al_tut_e=[sermaye*(1+ist["al_tut"]/100*i/len(bt["egri"])) for i in range(len(bt["egri"]))]
        fig2.add_trace(go.Scatter(y=bt["egri"],mode="lines",line=dict(color="#00e59a" if ist["getiri"]>=0 else "#ff3e5e",width=2.5),fill="tozeroy",fillcolor="rgba(0,229,154,0.06)",name="Strateji"))
        fig2.add_trace(go.Scatter(y=al_tut_e,mode="lines",line=dict(color="#ffc840",width=1.5,dash="dot"),name="Al-Tut"))
        fig2.update_layout(paper_bgcolor="#04111e",plot_bgcolor="#071828",font=dict(color="#5588aa"),height=250,margin=dict(l=10,r=10,t=10,b=10),legend=dict(bgcolor="#0b2035"))
        fig2.update_xaxes(gridcolor="#143350");fig2.update_yaxes(gridcolor="#143350")
        st.plotly_chart(fig2,use_container_width=True)
        col1,col2=st.columns(2)
        with col1:
            for k,v in [("Ort. Kazanç",f"{ist['ort_kazanc']:+,.0f} ₺"),("Ort. Kayıp",f"{ist['ort_kayip']:+,.0f} ₺"),("Ort. Tutma",f"{ist['ort_tutma']:.1f} gün"),("Toplam İşlem",ist['toplam'])]:
                ca,cb=st.columns([2,1]);ca.write(f"**{k}**");cb.write(f"`{v}`")
        with col2:
            fark=ist['getiri']-ist['al_tut']
            st.markdown(f"""<div style='text-align:center;padding:20px;background:#0b2035;border-radius:12px;border:1px solid {"#00e59a" if fark>=0 else "#ff3e5e"}44'>
            <div style='font-size:11px;color:#5588aa'>STRATEJİ vs AL-TUT</div>
            <div style='font-size:32px;font-weight:900;color:{"#00e59a" if fark>=0 else "#ff3e5e"};margin:8px 0'>{fark:+.1f}%</div>
            <div style='font-size:12px;color:#5588aa'>{"Strateji kazandı ✓" if fark>=0 else "Al-Tut daha iyi"}</div></div>""",unsafe_allow_html=True)
        if len(bt["islemler"])>0:
            st.markdown("#### 📋 İşlem Geçmişi")
            st.dataframe(bt["islemler"],use_container_width=True,height=300,hide_index=True)

with tab4:
    st.markdown("### 🔍 BIST Hisse Tarayıcı")
    col1,col2=st.columns(2)
    with col1:secili_sektor=st.selectbox("Sektör",["TÜMÜ"]+sorted(set(v["sektor"] for v in HISSELER.values())))
    with col2:min_rsi,max_rsi=st.slider("RSI Aralığı",0,100,(20,60))
    taranacak={k:v for k,v in HISSELER.items() if secili_sektor=="TÜMÜ" or v["sektor"]==secili_sektor}
    if st.button("🔍 Tara",type="primary",use_container_width=True):
        sonuclar=[];prog=st.progress(0);durum=st.empty()
        for i,(kod,bilgi) in enumerate(taranacak.items()):
            durum.text(f"{kod} taranıyor... ({i+1}/{len(taranacak)})")
            prog.progress((i+1)/len(taranacak))
            df_t=veri_cek(kod,"3mo")
            if df_t is not None and len(df_t)>50:
                df_t=indikatör_hesapla(df_t);sig_t=sinyal_uret(df_t)
                s=df_t.iloc[-1];o=df_t.iloc[-2];dg=(s["close"]-o["close"])/o["close"]*100
                rv=sig_t["rsi"]
                if rv and min_rsi<=rv<=max_rsi:
                    sonuclar.append({"Hisse":kod,"İsim":bilgi["isim"],"Sektör":bilgi["sektor"],
                        "Fiyat":round(s["close"],2),"Değişim%":round(dg,2),"RSI":round(rv,1),
                        "ADX":round(sig_t["adx"],1) if sig_t["adx"] else None,
                        "MACD":round(sig_t["macd_hist"],4) if sig_t["macd_hist"] else None,
                        "Sinyal":sig_t["sinyal"],"Puan":sig_t["puan"]})
        prog.empty();durum.empty()
        if sonuclar:st.session_state["tarama"]=pd.DataFrame(sonuclar).sort_values("Puan",ascending=False)
        else:st.warning("RSI aralığında hisse bulunamadı.")
    if "tarama" in st.session_state:
        df_t=st.session_state["tarama"]
        c1,c2,c3,c4=st.columns(4)
        with c1:st.metric("Bulunan",len(df_t))
        with c2:st.metric("AL Sinyali",len(df_t[df_t["Sinyal"].str.contains("AL",na=False)]))
        with c3:st.metric("SAT Sinyali",len(df_t[df_t["Sinyal"].str.contains("SAT",na=False)]))
        with c4:st.metric("Bekle",len(df_t[df_t["Sinyal"].str.contains("BEKLE",na=False)]))
        def renk(val):
            if "AL" in str(val):return "background-color:#00e59a22;color:#00e59a"
            if "SAT" in str(val):return "background-color:#ff3e5e22;color:#ff3e5e"
            return "color:#ffc840"
        styled=df_t.style.map(renk,subset=["Sinyal"]).format({"Değişim%":"{:+.2f}%","Fiyat":"{:.2f} ₺"})
        st.dataframe(styled,use_container_width=True,height=500,hide_index=True)

with tab5:
    st.markdown("### 📚 Profesyonel Analistlerin Kullandığı İndikatörler")
    st.markdown("""
<table class='ind-table'>
<tr><th>Kategori</th><th>İndikatör</th><th>Ne İşe Yarar</th><th>Nasıl Yorumlanır</th><th>Kim Kullanır</th></tr>
<tr><td rowspan='5'><b>🔵 TREND</b></td><td><b>EMA (9/21/50/200)</b></td><td>Üstel hareketli ortalama — fiyat yönü</td><td>Fiyat EMA üstünde = trend yukarı. EMA21 > EMA50 = güçlü yükseliş</td><td>Tüm profesyoneller</td></tr>
<tr><td><b>SMA (20/50/200)</b></td><td>Basit hareketli ortalama</td><td>SMA200 uzun vadeli trend için kullanılır</td><td>Kurumsal yatırımcılar</td></tr>
<tr><td><b>Altın Kesim</b></td><td>EMA50, EMA200'ü yukarı kesiyor</td><td>Güçlü yükseliş sinyali — nadir ama çok değerli</td><td>Profesyonel analistler</td></tr>
<tr><td><b>ADX (14)</b></td><td>Trend gücünü ölçer (yön değil)</td><td>ADX > 25 = güçlü trend. ADX < 20 = yatay piyasa</td><td>Swing ve pozisyon trader</td></tr>
<tr><td><b>Parabolic SAR</b></td><td>Trend dönüş noktaları</td><td>Fiyat SAR üstünde = yukarı trend. Altında = aşağı</td><td>Kısa vadeli traderlar</td></tr>
<tr><td rowspan='6'><b>🟣 MOMENTUM</b></td><td><b>RSI (14)</b></td><td>Aşırı alım/satım tespiti</td><td>30 altı = aşırı satılmış (al fırsatı). 70 üstü = aşırı alınmış (sat)</td><td>Tüm profesyoneller</td></tr>
<tr><td><b>MACD (12,26,9)</b></td><td>Trend momentum ve dönüş sinyali</td><td>Histogram sıfırı yukarı keserse AL. Aşağı keserse SAT</td><td>Tüm profesyoneller</td></tr>
<tr><td><b>Stochastic (14,3,3)</b></td><td>RSI'ya benzer, daha hassas</td><td>%K < 20 ve %D'yi yukarı keserse AL sinyali</td><td>Kısa vadeli traderlar</td></tr>
<tr><td><b>CCI (20)</b></td><td>Fiyatın ortalamadan sapması</td><td>-100 altı = aşırı satılmış. +100 üstü = aşırı alınmış</td><td>Emtia ve hisse analistleri</td></tr>
<tr><td><b>Williams %R</b></td><td>Momentum osilatörü</td><td>-80 altı = aşırı satılmış. -20 üstü = aşırı alınmış</td><td>Kısa vadeli traderlar</td></tr>
<tr><td><b>ROC</b></td><td>Fiyat değişim hızı</td><td>Pozitif ve artıyorsa momentum güçlü</td><td>Nicel analistler</td></tr>
<tr><td rowspan='3'><b>🟡 VOLATİLİTE</b></td><td><b>Bollinger Bantları</b></td><td>Fiyat kanalı — genişlik = volatilite</td><td>Alt banda değme = alım fırsatı. Sıkışma = büyük hareket öncesi</td><td>Tüm profesyoneller</td></tr>
<tr><td><b>ATR (14)</b></td><td>Ortalama gerçek aralık</td><td>Stop-loss için kullanılır (1-2x ATR mesafe)</td><td>Risk yöneticileri</td></tr>
<tr><td><b>BB Sıkışması</b></td><td>BB bantları daraldığında büyük hareket</td><td>BB width < 5 = sıkışma. Kırılma yönünde pozisyon al</td><td>Deneyimli traderlar</td></tr>
<tr><td rowspan='5'><b>🟢 HACİM</b></td><td><b>OBV</b></td><td>Hacim akışını takip eder</td><td>OBV yükselirken fiyat düşüyorsa = yakında yükseliş</td><td>Kurumsal analistler</td></tr>
<tr><td><b>VWAP</b></td><td>Hacim ağırlıklı ortalama fiyat</td><td>Kurumsal alım/satım seviyeleri. Fiyat üstündeyse alım baskısı</td><td>Kurumsal ve günlük traderlar</td></tr>
<tr><td><b>MFI (Money Flow Index)</b></td><td>Hacimli RSI</td><td>20 altı = aşırı satılmış. 80 üstü = aşırı alınmış</td><td>Kurumsal analistler</td></tr>
<tr><td><b>CMF (Chaikin Money Flow)</b></td><td>Para akışının gücü</td><td>Pozitif = alım baskısı. Negatif = satış baskısı</td><td>Kurumsal analistler</td></tr>
<tr><td><b>Hacim/Ort. Oranı</b></td><td>Anlık hacim / 20 günlük ortalama</td><td>2x üstü + fiyat yükseliyor = güçlü teyit</td><td>Tüm traderlar</td></tr>
<tr><td rowspan='3'><b>🔴 DESTEK/DİRENÇ</b></td><td><b>Pivot Noktaları</b></td><td>Önceki günden hesaplanan kritik seviyeler</td><td>R1/R2 = direnç. S1/S2 = destek. Pivot = ana seviye</td><td>Günlük traderlar</td></tr>
<tr><td><b>Fibonacci Retracement</b></td><td>Büyük hareketlerde geri çekilme seviyeleri</td><td>%38.2, %50, %61.8 kritik seviyeleri</td><td>Teknik analistler</td></tr>
<tr><td><b>Aroon (25)</b></td><td>Trend dönüş zamanlaması</td><td>Aroon Up > 70, Down < 30 = güçlü yükseliş trendi</td><td>Orta vadeli traderlar</td></tr>
</table>
    """,unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
### 🎯 Önerilen Kombinasyonlar

| Kombinasyon | İndikatörler | Ne Zaman |
|-------------|-------------|----------|
| **Temel Swing** | RSI + EMA21/50 + Hacim | Başlangıç için |
| **Momentum** | MACD + RSI + Stochastic | Trend dönemlerinde |
| **Volatilite** | Bollinger + ATR + ADX | Sıkışma kırılmalarında |
| **Kurumsal** | VWAP + OBV + MFI | Büyük hisse takibinde |
| **Tam Sistem** | RSI + MACD + EMA + ADX + Hacim | Deneyimli trader |

### ⚠️ Altın Kurallar
- **Hiçbir indikatör tek başına yeterli değil** — en az 2-3 teyit al
- **Hacim her zaman doğrulamalı** — hacim yoksa sinyal zayıftır  
- **ADX > 25 olmadan trend stratejisi kullanma** — yatay piyasada kayıp artar
- **Stop-loss her zaman 1-2x ATR** — sezgiyle değil, matematikle belirle
- **Backtest geçmişi garanti etmez** — sadece strateji mantığını test eder
    """)

st.markdown("---")
st.markdown(f"<div style='text-align:center;color:#244060;font-size:11px'>📊 BIST PRO Trader v2.0 · Yahoo Finance 15dk gecikmeli · Yatırım tavsiyesi değildir · {datetime.now().strftime('%H:%M:%S')}</div>",unsafe_allow_html=True)
