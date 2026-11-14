import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_style("whitegrid")

# Fungsi memuat dan membersihkan data
@st.cache_data
def load_data():
    day_df = pd.read_csv("day.csv")
    hour_df = pd.read_csv("hour.csv")
    
    # Ubah format tanggal
    day_df["dteday"] = pd.to_datetime(day_df["dteday"])
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
    
    # Mapping label
    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    weather_map = {
        1: "Clear/Partly Cloudy",
        2: "Mist/Cloudy",
        3: "Light Snow/Rain",
        4: "Heavy Rain/Snow"
    }
    
    for df in [day_df, hour_df]:
        df["season"] = df["season"].map(season_map)
        df["weathersit"] = df["weathersit"].map(weather_map)
        
    # Klaster waktu untuk hour_df
    def categorize_time(hr):
        if 0 <= hr <= 5:
            return "Dini Hari (00:00 - 05:00)"
        elif 6 <= hr <= 11:
            return "Pagi (06:00 - 11:00)"
        elif 12 <= hr <= 16:
            return "Siang (12:00 - 16:00)"
        elif 17 <= hr <= 20:
            return "Sore (17:00 - 20:00)"
        else:
            return "Malam (21:00 - 23:00)"
            
    hour_df["time_category"] = hour_df["hr"].apply(categorize_time)
    return day_df, hour_df

day_df, hour_df = load_data()

# --- SIDEBAR (FILTER INTERAKTIF) ---
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    st.title("🚲 Bike Sharing Analytics")
    st.markdown("Gunakan filter di bawah ini untuk menyesuaikan rentang waktu analisis:")
    
    start_date, end_date = st.date_input(
        label="Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter DataFrame berdasarkan input tanggal
main_day_df = day_df[(day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))]
main_hour_df = hour_df[(hour_df["dteday"] >= str(start_date)) & (hour_df["dteday"] <= str(end_date))]

# --- HEADER & METRIK UTAMA ---
st.header("Dashboard Analisis Penyewaan Sepeda (2011–2012) 🚴‍♂️")
st.markdown(f"Menampilkan data dari **{start_date}** hingga **{end_date}**")

col1, col2, col3 = st.columns(3)
with col1:
    total_rentals = main_day_df["cnt"].sum()
    st.metric("Total Penyewaan Sepeda", value=f"{total_rentals:,}")
with col2:
    total_registered = main_day_df["registered"].sum()
    st.metric("Pengguna Registered", value=f"{total_registered:,}")
with col3:
    total_casual = main_day_df["casual"].sum()
    st.metric("Pengguna Casual", value=f"{total_casual:,}")

st.divider()

# --- VISUALISASI 1: PENGARUH MUSIM & CUACA ---
st.subheader("1. Pengaruh Musim dan Kondisi Cuaca terhadap Penyewaan Harian")
fig1, ax1 = plt.subplots(nrows=1, ncols=2, figsize=(16, 5))

# Musim
season_avg = main_day_df.groupby("season")["cnt"].mean().sort_values(ascending=False).reset_index()
sns.barplot(x="cnt", y="season", data=season_avg, palette="Blues_r", ax=ax1[0], hue="season", legend=False)
ax1[0].set_title("Rata-rata Penyewaan per Musim", fontsize=13, fontweight="bold")
ax1[0].set_xlabel("Rata-rata Penyewaan Harian")
ax1[0].set_ylabel(None)

# Cuaca
weather_avg = main_day_df.groupby("weathersit")["cnt"].mean().sort_values(ascending=False).reset_index()
sns.barplot(x="cnt", y="weathersit", data=weather_avg, palette="Blues_r", ax=ax1[1], hue="weathersit", legend=False)
ax1[1].set_title("Rata-rata Penyewaan per Kondisi Cuaca", fontsize=13, fontweight="bold")
ax1[1].set_xlabel("Rata-rata Penyewaan Harian")
ax1[1].set_ylabel(None)

plt.tight_layout()
st.pyplot(fig1)

st.divider()

# --- VISUALISASI 2: POLA JAM SIBUK (REGISTERED VS CASUAL) ---
st.subheader("2. Pola Jam Sibuk: Pengguna Registered vs Casual")
fig2, ax2 = plt.subplots(nrows=1, ncols=2, figsize=(16, 5), sharey=True)

working_df = main_hour_df[main_hour_df["workingday"] == 1].groupby("hr")[["registered", "casual"]].mean().reset_index()
holiday_df = main_hour_df[main_hour_df["workingday"] == 0].groupby("hr")[["registered", "casual"]].mean().reset_index()

# Hari Kerja
ax2[0].plot(working_df["hr"], working_df["registered"], marker="o", linewidth=2, color="#1f77b4", label="Registered")
ax2[0].plot(working_df["hr"], working_df["casual"], marker="s", linewidth=2, color="#ff7f0e", label="Casual")
ax2[0].set_title("Hari Kerja (Workingday)", fontsize=13, fontweight="bold")
ax2[0].set_xlabel("Jam (00:00 - 23:00)")
ax2[0].set_ylabel("Rata-rata Penyewaan per Jam")
ax2[0].set_xticks(range(0, 24))
ax2[0].legend()

# Hari Libur
ax2[1].plot(holiday_df["hr"], holiday_df["registered"], marker="o", linewidth=2, color="#1f77b4", label="Registered")
ax2[1].plot(holiday_df["hr"], holiday_df["casual"], marker="s", linewidth=2, color="#ff7f0e", label="Casual")
ax2[1].set_title("Akhir Pekan & Hari Libur", fontsize=13, fontweight="bold")
ax2[1].set_xlabel("Jam (00:00 - 23:00)")
ax2[1].set_xticks(range(0, 24))
ax2[1].legend()

plt.tight_layout()
st.pyplot(fig2)

st.divider()

# --- VISUALISASI 3: KLASTER WAKTU (ANALISIS LANJUTAN) ---
st.subheader("3. Distribusi Total Penyewaan Berdasarkan Klaster Waktu")
time_cluster = main_hour_df.groupby("time_category")["cnt"].sum().sort_values(ascending=False).reset_index()

fig3, ax3 = plt.subplots(figsize=(12, 4))
sns.barplot(x="cnt", y="time_category", data=time_cluster, palette="Blues_r", ax=ax3, hue="time_category", legend=False)
ax3.set_title("Total Penyewaan Sepeda per Kategori Waktu", fontsize=13, fontweight="bold")
ax3.set_xlabel("Total Penyewaan")
ax3.set_ylabel(None)

plt.tight_layout()
st.pyplot(fig3)