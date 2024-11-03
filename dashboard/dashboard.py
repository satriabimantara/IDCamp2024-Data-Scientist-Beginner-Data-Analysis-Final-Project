import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# load cleaned data
merged_orders_df = pd.read_csv("product_orders.csv")

# ubah kolom yang semestinya datetime
datetime_columns = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date',
]
merged_orders_df['shipping_limit_date'] = pd.to_datetime(
    merged_orders_df['shipping_limit_date'])
merged_orders_df['review_creation_date'] = pd.to_datetime(
    merged_orders_df['review_creation_date'],
    format='%Y-%m-%d', errors='coerce'
)
merged_orders_df['review_answer_timestamp'] = pd.to_datetime(
    merged_orders_df['review_answer_timestamp'],
    format='%Y-%m-%d %H:%M:%S', errors='coerce'
)
for column in datetime_columns:
    merged_orders_df[column] = pd.to_datetime(merged_orders_df[column])


# sort values dan reset index
merged_orders_df.sort_values(by="order_purchase_timestamp", inplace=True)
merged_orders_df.reset_index(inplace=True)

# Filter data tanggal
min_date = merged_orders_df["order_purchase_timestamp"].min()
max_date = merged_orders_df["order_purchase_timestamp"].max()


with st.sidebar:
    st.header('Streamlit Dashboard')
    st.subheader('I Made Satria Bimantara')
    st.caption('Email: satriabimantara.md@gmail.com')
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu (Purchase Timestamps)', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# filter merged_orders sesuai tanggal yang dimasukkan
main_orders_df = merged_orders_df[(merged_orders_df["order_purchase_timestamp"] >= str(start_date)) &
                                  (merged_orders_df["order_purchase_timestamp"] <= str(end_date))]

# siapkan berbagai dataframe untuk dashboard


# dashboard display
st.header('E-Commerce Analysis Dashboard :sparkles:')


# Quest
def create_total_penjualan_category_product_df(main_orders_df):
    df = main_orders_df['product_category_name'].value_counts()

    # filter kategori produk dengan nilai >2000 untuk ditampilkan selain itu beri simbol "Others"
    filtered_categories = df[df >= 2000].index
    main_orders_df['updated_product_category'] = main_orders_df['product_category_name'].where(
        main_orders_df['product_category_name'].isin(filtered_categories), 'Other')

    # hitung total penjualan per produk kategori
    df = main_orders_df.groupby('updated_product_category')['price'].sum(
    ).reset_index().sort_values(by='price', ascending=False)
    return df


total_penjualan_category_product_df = create_total_penjualan_category_product_df(
    main_orders_df)
st.subheader('Total Penjualan Setiap Product Category')

fig, ax = plt.subplots(figsize=(10, 16))
colors = ["#D3D3D3", "#90CAF9", "#90CAF9", "#90CAF9"] + \
    ["#D3D3D3" for _ in range(total_penjualan_category_product_df.shape[0]-5)]
sns.barplot(
    y="updated_product_category",
    x="price",
    data=total_penjualan_category_product_df,
    palette=colors,
    ax=ax
)
ax.set_title("Total Penjualan per Kategori Produk", loc="center", fontsize=25)
ax.set_ylabel(None, fontdict={'size': 20})
ax.set_xlabel(None, fontdict={'size': 20})
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
# Add annotations on top of each bar
for p in ax.patches:
    ax.annotate(f'{p.get_width()}',
                (p.get_width(), p.get_y() + p.get_height() / 2),
                ha='left', va='center', size=20)
st.pyplot(fig)
st.divider()

# Tren Penjualan
data_penjualan_harian = main_orders_df.groupby(
    main_orders_df['order_purchase_timestamp'].dt.weekday
).agg({'price': 'sum'})

st.subheader('Tren Penjualan (order) Setiap Bulan dan Tahun')

fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(
    data_penjualan_harian.index.astype(str),
    data_penjualan_harian['price'],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.set_title("Tren Penjualan Harian", loc="center", fontsize=25)
ax.set_ylabel(None, fontdict={'size': 20})
ax.set_xlabel(None, fontdict={'size': 20})
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xticks(range(0, 7))
ax.set_xticklabels(['Senin', 'Selasa', 'Rabu', 'Kamis',
                   'Jumat', 'Sabtu', 'Minggu'])

st.pyplot(fig)
st.divider()

data_penjualan_tanggal = main_orders_df.groupby(
    main_orders_df['order_purchase_timestamp'].dt.day
).agg({'price': 'sum'})

fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(
    data_penjualan_tanggal.index.astype(str),
    data_penjualan_tanggal['price'],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.set_title("Tren Penjualan Per Tanggal", loc="center", fontsize=25)
ax.set_ylabel(None, fontdict={'size': 20})
ax.set_xlabel(None, fontdict={'size': 20})
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)
st.divider()
data_penjualan_bulanan = main_orders_df.groupby(
    main_orders_df['order_purchase_timestamp'].dt.to_period('M')
).agg({'price': 'sum'})

fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(
    data_penjualan_bulanan.index.astype(str),
    data_penjualan_bulanan['price'],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.set_title("Tren Penjualan Bulanan", loc="center", fontsize=25)
ax.set_ylabel(None, fontdict={'size': 20})
ax.set_xlabel(None, fontdict={'size': 20})
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15, rotation=45)

st.pyplot(fig)
st.divider()
data_penjualan_bulanan = main_orders_df.groupby(
    main_orders_df['order_purchase_timestamp'].dt.month
).agg({'price': 'sum'})

fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(
    data_penjualan_bulanan.index.astype(str),
    data_penjualan_bulanan['price'],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.set_title("Tren Penjualan Bulanan", loc="center", fontsize=25)
ax.set_ylabel(None, fontdict={'size': 20})
ax.set_xlabel(None, fontdict={'size': 20})
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xticks(range(0, 12))
ax.set_xticklabels(['January', 'February', 'March', 'April', 'May',
                   'June', 'July', 'August', 'September', 'October',
                    'November', 'December'])

st.pyplot(fig)
st.divider()
# cari tahu data (price) penjualan per Tahun
data_penjualan_tahunan = main_orders_df.groupby(
    main_orders_df['order_purchase_timestamp'].dt.to_period('Y')
).agg({'price': 'sum'}).reset_index()
data_penjualan_tahunan['order_purchase_timestamp'] = data_penjualan_tahunan['order_purchase_timestamp'].apply(
    lambda x: str(x))
data_penjualan_tahunan['Change'] = data_penjualan_tahunan['price'].diff(
).fillna(0)

fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(
    data_penjualan_tahunan.index.astype(str),
    data_penjualan_tahunan['price'],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.set_title("Tren Penjualan Tahunan", loc="center", fontsize=25)
ax.set_ylabel(None, fontdict={'size': 20})
ax.set_xlabel(None, fontdict={'size': 20})
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xticks(range(0, 3))
ax.set_xticklabels([2016, 2017, 2018])

st.pyplot(fig)
st.divider()

# Waktu Pengantaran per Kategori Produk
st.subheader('Waktu Pengantaran per kategori produk')


def create_waktu_pengantaran_df(main_orders_df):
    main_orders_df['weekday'] = main_orders_df['order_purchase_timestamp'].dt.weekday

    difference_delivery_datetime = (
        main_orders_df['order_delivered_customer_date'] - main_orders_df['order_purchase_timestamp'])
    main_orders_df['delivery_day_times'] = difference_delivery_datetime.dt.days
    main_orders_df['delivery_hours_times'] = difference_delivery_datetime.dt.total_seconds(
    ) // 3600
    main_orders_df['delivery_minutes_times'] = (
        difference_delivery_datetime.dt.total_seconds() % 3600) // 60
    return main_orders_df


df = create_waktu_pengantaran_df(main_orders_df)

fig, ax = plt.subplots(figsize=(12, 8))
colors = ["#26536f",  "#749ca8", "#c78a4d", "#854927", "#3b96b7",  "#b6a98d"]

sns.boxplot(
    y="updated_product_category",
    x="delivery_day_times",
    data=df,
    palette=colors,
    ax=ax
)
ax.set_title("Waktu Pengantaran (Hari) Per Kategori Produk",
             loc="center", fontsize=25, fontweight='bold')
ax.set_ylabel(None, fontdict={'size': 20})
ax.set_xlabel(None, fontdict={'size': 20})
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
st.pyplot(fig)
st.divider()

fig, ax = plt.subplots(figsize=(12, 6))
colors = ["#26536f",  "#749ca8", "#c78a4d", "#854927", "#3b96b7",  "#b6a98d"]

sns.boxplot(
    y="delivery_day_times",
    x="weekday",
    data=df,
    palette=colors,
    ax=ax
)
ax.set_title("Waktu Pengantaran dalam hari per minggu per kategori produk",
             loc="center", fontsize=25, fontweight='bold')
ax.set_ylabel(None, fontdict={'size': 20})
ax.set_xlabel(None, fontdict={'size': 20})
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
st.pyplot(fig)
st.divider()

# RFM Analysis


def create_rfm_df(unique_primary_key, name='customer'):
    # buat variabel untuk menampung hasil perhitungan RFM analysis
    rfm_df = main_orders_df.groupby(unique_primary_key, as_index=False).agg({
        "order_purchase_timestamp": "max",  # mengambil tanggal order terakhir
        "order_id": "nunique",  # menghitung jumlah order unik
        "price": "sum"  # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = [name+"_id",
                      "max_order_timestamp", "frequency", "monetary"]

    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = main_orders_df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(
        lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    # buat mapping customer_id agar ID (ambil 3 kode string terakhir dari setiap id)
    rfm_df[name+'_id_mapping'] = rfm_df[name +
                                        '_id'].apply(lambda x: "ID-"+x[-3:])

    return rfm_df


def visualize_rfm_df(
    rfm_df,
    name='customer',
    name_id='customer_id_mapping',
    n_objects=10,
    recency_ascending=True,
    frequency_ascending=False,
    monetary_ascending=False,
):
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)
    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)
    with col3:
        avg_frequency = format_currency(
            rfm_df.monetary.mean(), "AUD", locale='es_CO')
        st.metric("Average Monetary", value=avg_frequency)

    # identifikasi best customer berdasarkan parameter frequency, monetary, recency
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
    colors = ["#90CAF9" for _ in range(n_objects)]

    sns.barplot(y="recency", x=name_id, data=rfm_df.sort_values(
        by="recency", ascending=recency_ascending).head(n_objects), palette=colors, ax=ax[0])

    ax[0].set_ylabel(None)
    ax[0].set_xlabel(name_id, fontsize=30)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=30)
    ax[0].tick_params(axis='x', labelsize=35, rotation=45)

    sns.barplot(y="frequency", x=name_id, data=rfm_df.sort_values(
        by="frequency", ascending=frequency_ascending).head(n_objects), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(name_id, fontsize=30)
    ax[1].set_title("By Frequency", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=30)
    ax[1].tick_params(axis='x', labelsize=35, rotation=45)

    sns.barplot(y="monetary", x=name_id, data=rfm_df.sort_values(
        by="monetary", ascending=monetary_ascending).head(n_objects), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(name_id, fontsize=30)
    ax[2].set_title("By Monetary", loc="center", fontsize=50)
    ax[2].tick_params(axis='y', labelsize=30)
    ax[2].tick_params(axis='x', labelsize=35, rotation=45)

    fig.suptitle(
        f"Best {name.capitalize()} Based on RFM Parameters ({name_id})", fontsize=40)

    st.pyplot(fig)
    st.caption('Copyright © I Made Satria Bimantara 2024')


# visualize RFM analysis (Customer)
st.subheader("Best Customer Based on RFM Parameters")
customer_rfm_df = create_rfm_df('customer_unique_id')
visualize_rfm_df(customer_rfm_df)

# visualize RFM analysis (Seller)
st.subheader("Best Seller Based on RFM Parameters")
seller_rfm_df = create_rfm_df('seller_id', name='seller')
visualize_rfm_df(seller_rfm_df,
                 name='seller',
                 name_id='seller_id_mapping')
