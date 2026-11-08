import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Setup Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="E-Commerce Data Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Load Data dengan Caching & Handling Nama Kolom
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Standarisasi kolom jika terdapat perbedaan penamaan
    if 'payment_value' in df.columns and 'total_payment_value' not in df.columns:
        df.rename(columns={'payment_value': 'total_payment_value'}, inplace=True)
    if 'product_category_name_english' in df.columns and 'product_category_main' not in df.columns:
        df.rename(columns={'product_category_name_english': 'product_category_main'}, inplace=True)
        
    return df

df = load_data()

# Header Dashboard
st.title("🛒 E-Commerce Public Data Dashboard")
st.markdown("Dashboard interaktif untuk menganalisis kinerja penjualan, kategori produk, dan lokasi pelanggan.")

# Sidebar Filter Tanggal
min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()

with st.sidebar:
    st.header("Filter Data")
    date_range = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Validasi Pilihan Tanggal
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
elif isinstance(date_range, (list, tuple)) and len(date_range) == 1:
    start_date = end_date = date_range[0]
else:
    start_date = end_date = date_range

# Filter Data
main_filtered_df = df[
    (df['order_purchase_timestamp'].dt.date >= start_date) &
    (df['order_purchase_timestamp'].dt.date <= end_date)
]

# Matriks Ringkasan (KPI)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Orders", value=f"{len(main_filtered_df):,}")
with col2:
    st.metric("Total Revenue", value=f"R$ {main_filtered_df['total_payment_value'].sum():,.2f}")
with col3:
    st.metric("Average Review Score", value=f"{main_filtered_df['review_score'].mean():.2f}")

st.divider()

# Grafik 1: Tren Penjualan Bulanan
st.subheader("📈 Tren Pendapatan Penjualan")
monthly_revenue = main_filtered_df.resample(rule='M', on='order_purchase_timestamp')['total_payment_value'].sum().reset_index()
monthly_revenue['order_purchase_timestamp'] = monthly_revenue['order_purchase_timestamp'].dt.strftime('%Y-%m')

fig_trend, ax_trend = plt.subplots(figsize=(12, 4))
sns.lineplot(data=monthly_revenue, x='order_purchase_timestamp', y='total_payment_value', marker='o', color='#1f77b4', ax=ax_trend)
ax_trend.set_xlabel("Bulan")
ax_trend.set_ylabel("Total Pendapatan (R$)")
plt.xticks(rotation=45)
st.pyplot(fig_trend)

st.divider()

# Grafik 2 & 3: Top Kategori & Wilayah Pelanggan
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📦 Top 5 Kategori Produk Terlaris")
    top_cat = main_filtered_df.groupby("product_category_main")["total_payment_value"].sum().sort_values(ascending=False).head(5).reset_index()
    fig_cat, ax_cat = plt.subplots(figsize=(6, 4))
    sns.barplot(data=top_cat, y="product_category_main", x="total_payment_value", hue="product_category_main", palette="Blues_r", legend=False, ax=ax_cat)
    ax_cat.set_xlabel("Total Sales (R$)")
    ax_cat.set_ylabel("Kategori Produk")
    st.pyplot(fig_cat)

with col_right:
    st.subheader("📍 Top 5 Wilayah Pelanggan (State)")
    top_state = main_filtered_df["customer_state"].value_counts().head(5).reset_index()
    top_state.columns = ["customer_state", "count"]
    fig_state, ax_state = plt.subplots(figsize=(6, 4))
    sns.barplot(data=top_state, x="customer_state", y="count", hue="customer_state", palette="Greens_r", legend=False, ax=ax_state)
    ax_state.set_xlabel("Negara Bagian (State)")
    ax_state.set_ylabel("Jumlah Transaksi")
    st.pyplot(fig_state)

st.divider()
st.subheader("📄 Pratinjau Data Transaksi")
st.dataframe(main_filtered_df.head(10))
