import pandas as pd
import streamlit as st
import plotly.express as px
import gdown


# Sayfa ayarları
st.set_page_config(page_title="Üniversite Dashboard", layout="wide")
st.title("🎓 Üniversite Yerleşme Analiz Dashboardu")

# Veri yükleme (cache ile hızlandırma)

import pandas as pd

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/gizemyuksel67/streamlit/main/All_data.parquet"
    df = pd.read_parquet(url)
    
    # Doluluk oranı hesapla
    df["Doluluk Oranı"] = df["Toplam Yerleşen"] / df["Toplam Kontenjan"]
    return df

df = load_data()

st.sidebar.header("🔍 Filtreleme")

# 1) Üniversite Türü
uni_types = df["Üniversite Adı Ref Excel.Üniversite Türü"].dropna().unique()
selected_uni_type = st.sidebar.selectbox("Üniversite Türü Seç", sorted(uni_types))

# 2) Üniversite Adı (seçilen türe göre filtrelenmiş)
uni_list = df[df["Üniversite Adı Ref Excel.Üniversite Türü"] == selected_uni_type]["Üniversite Adı Ref Excel.Üniversite Adı"].dropna().unique()
selected_uni = st.sidebar.selectbox("Üniversite Seç", sorted(uni_list))

# 3) Program Adı (sadece o üniversitedeki programlar)
program_list = df[df["Üniversite Adı Ref Excel.Üniversite Adı"] == selected_uni]["Program Adı Analiz"].dropna().unique()
selected_program = st.sidebar.selectbox("Program Seç", sorted(program_list))

# 4) Yıl Aralığı
year_min, year_max = int(df["Yıl"].min()), int(df["Yıl"].max())
year_range = st.sidebar.slider("Yıl Aralığı Seç", year_min, year_max, (year_min, year_max))

# 5) Eğer vakıf ise burs oranı sorulsun
selected_burs = None
if selected_uni_type.lower() == "vakıf":
    burs_list = df[df["Üniversite Adı Ref Excel.Üniversite Adı"] == selected_uni]["Burs İndirim"].dropna().unique()
    selected_burs = st.sidebar.multiselect("Burs Oranı Seç (opsiyonel)", sorted(burs_list))

# ------------------------------
# Rapor Butonu
# ------------------------------
run_report = st.sidebar.button("📊 Raporu Getir")

# ------------------------------
# Filtreleme ve Raporlama
# ------------------------------
if run_report:
    df_filtered = df.copy()
    df_filtered = df_filtered[df_filtered["Üniversite Adı Ref Excel.Üniversite Türü"] == selected_uni_type]
    df_filtered = df_filtered[df_filtered["Üniversite Adı Ref Excel.Üniversite Adı"] == selected_uni]
    df_filtered = df_filtered[df_filtered["Program Adı Analiz"] == selected_program]
    df_filtered = df_filtered[(df_filtered["Yıl"] >= year_range[0]) & (df_filtered["Yıl"] <= year_range[1])]

    if selected_burs and selected_uni_type.lower() == "vakıf":
        df_filtered = df_filtered[df_filtered["Burs İndirim"].isin(selected_burs)]

    # ---- Özet Kartlar ----
    st.subheader("📌 Özet Bilgiler")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📉 Ortalama Taban Puan", f"{df_filtered['Taban Puan'].mean():.2f}")
    with col2:
        st.metric("🏆 Ortalama Başarı Sırası", f"{df_filtered['Taban Başarı Sırası'].mean():.0f}")
    with col3:
        st.metric("🎯 Ortalama Doluluk", f"{df_filtered['Doluluk Oranı'].mean()*100:.1f}%")
    with col4:
        st.metric("👥 Ortalama Kontenjan", f"{df_filtered['Toplam Kontenjan'].mean():.0f}")

    # ---- Trend Grafikleri ----
    st.subheader("📊 Trend Analizleri")
    tab1, tab2, tab3 = st.tabs(["Taban Puan", "Başarı Sırası", "Kontenjan & Yerleşen"])

    with tab1:
        fig1 = px.line(df_filtered, x="Yıl", y="Taban Puan", markers=True,
                       title="Yıllara Göre Taban Puan Değişimi")
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        fig2 = px.line(df_filtered, x="Yıl", y="Taban Başarı Sırası", markers=True,
                       title="Yıllara Göre Başarı Sırası Değişimi")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        fig3 = px.bar(df_filtered, x="Yıl", y=["Toplam Kontenjan", "Toplam Yerleşen"],
                      barmode="group", title="Kontenjan & Yerleşen Sayısı")
        st.plotly_chart(fig3, use_container_width=True)

    # ---- Detay Tablo ----
    st.subheader("📋 Detaylı Veriler")
    st.dataframe(df_filtered)

    # ---- CSV İndirme ----
    def convert_df(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df(df_filtered)
    st.download_button(
        label="📥 CSV Olarak İndir",
        data=csv,
        file_name="rapor.csv",
        mime="text/csv",
    )

else:
    st.info("📌 Lütfen filtreleri seçip **Raporu Getir** butonuna basın.")
