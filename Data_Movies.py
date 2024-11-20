import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
import seaborn as sns

# Đọc dữ liệu
data = pd.read_csv('Data/Data_Movies_clear.csv')

# Tiêu đề ứng dụng
st.title("Phân Tích Dữ Liệu Phim - Ứng Dụng Nâng Cao")

# 1. Bộ lọc dữ liệu
st.sidebar.header("Bộ Lọc Dữ Liệu")
year_range = st.sidebar.slider("Chọn khoảng năm phát hành", int(data['year'].min()), int(data['year'].max()), (2000, 2015))
min_revenue, max_revenue = st.sidebar.slider("Doanh thu (triệu $)", 0, int(data['revenue'].max()), (0, 100000000))

# Xử lý cột genres_list
data['genres_list'] = data['genres_list'].apply(lambda x: eval(x) if isinstance(x, str) else x)
# Tạo danh sách các thể loại duy nhất từ cột 'genres_list'
all_genres = sorted(set([genre for sublist in data['genres_list'].dropna() for genre in sublist]))

st.sidebar.header("Chọn Thể Loại Phim")
selected_genre = st.sidebar.selectbox("Chọn thể loại", all_genres)

# Lọc dữ liệu theo thể loại được chọn
filtered_by_genre = data[data['genres_list'].apply(lambda x: selected_genre in x)]
st.write(f"Dữ liệu cho thể loại: **{selected_genre}** (Số lượng: {len(filtered_by_genre)})")
st.dataframe(filtered_by_genre)

# Biểu đồ số lượng phim theo năm cho thể loại được chọn
st.header(f"Số Lượng Phim Theo Năm - {selected_genre}")
movies_by_year = filtered_by_genre.groupby('year').size()
fig, ax = plt.subplots()
movies_by_year.plot(kind='bar', ax=ax, color='purple', alpha=0.7)
ax.set_title(f"Số Lượng Phim Theo Năm - {selected_genre}")
ax.set_xlabel("Năm")
ax.set_ylabel("Số lượng phim")
st.pyplot(fig)

# Lọc dữ liệu chung theo năm và doanh thu
filtered_data = data[
    (data['year'] >= year_range[0]) & 
    (data['year'] <= year_range[1]) & 
    (data['revenue'] >= min_revenue) & 
    (data['revenue'] <= max_revenue)
]

st.write(f"Dữ liệu sau khi lọc: {filtered_data.shape[0]} dòng")
st.dataframe(filtered_data)

# 2. Tìm kiếm phim
st.sidebar.header("Tìm Kiếm Phim")
search_title = st.sidebar.text_input("Nhập tên phim")
if search_title:
    searched_movie = data[data['title'].str.contains(search_title, case=False, na=False)]
    st.write(f"Tìm thấy {searched_movie.shape[0]} phim phù hợp")
    st.dataframe(searched_movie)

# 3. Tải xuống dữ liệu
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

csv_data = convert_to_csv(filtered_data)
st.download_button(
    label="Tải xuống dữ liệu CSV",
    data=csv_data,
    file_name="Filtered_Movies.csv",
    mime="text/csv"
)

# 4. So sánh theo năm: Doanh thu trung bình và tỷ lệ lợi nhuận
st.header("So Sánh Theo Năm: Doanh Thu Trung Bình và Tỷ Lệ Lợi Nhuận")

# Tính doanh thu trung bình và tỷ lệ lợi nhuận trung bình theo năm
revenue_by_year = data.groupby('year')['revenue'].mean()
profit_margin_by_year = data.groupby('year')['profit_margin'].mean()

# Tạo biểu đồ so sánh
fig, ax = plt.subplots(figsize=(12, 6))

# Biểu đồ doanh thu trung bình
ax.bar(revenue_by_year.index, revenue_by_year.values / 1e6, color='blue', alpha=0.6, label='Doanh thu trung bình (triệu $)')

# Biểu đồ tỷ lệ lợi nhuận trung bình
ax2 = ax.twinx()
ax2.plot(profit_margin_by_year.index, profit_margin_by_year.values * 100, color='red', label='Tỷ lệ lợi nhuận (%)')

# Giao diện biểu đồ
ax.set_xlabel("Năm")
ax.set_ylabel("Doanh thu trung bình (triệu $)", color='blue')
ax2.set_ylabel("Tỷ lệ lợi nhuận (%)", color='red')
ax.set_title("So Sánh Doanh Thu Trung Bình và Tỷ Lệ Lợi Nhuận Theo Năm")
ax.legend(loc='upper left')
ax2.legend(loc='upper right')

st.pyplot(fig)
