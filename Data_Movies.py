import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('Data/Data_Movies_clear.csv')
data['year'] = data['year'].astype(int)

st.title("Trực Quan Hóa Dữ Liệu Phim với Streamlit")

st.sidebar.header("Bộ Lọc Dữ Liệu")
year_range = st.sidebar.slider("Chọn khoảng năm phát hành", int(data['year'].min()), int(data['year'].max()), (2000, 2015))
min_revenue, max_revenue = st.sidebar.slider("Doanh thu (triệu $)", 0, int(data['revenue'].max()), (0, 100000000))
data['genres_list'] = data['genres_list'].apply(lambda x: [genre.strip() for genre in x.split(',')] if isinstance(x, str) else [])

# Tạo danh sách các thể loại duy nhất từ cột 'genres_list'
all_genres = sorted(set(genre for sublist in data['genres_list'].dropna() for genre in sublist))
st.sidebar.header("Chọn Thể Loại Phim")
selected_genres = st.sidebar.multiselect("Chọn thể loại (nhiều thể loại có thể chọn)", all_genres)
if selected_genres:
    filtered_by_genre = data[data['genres_list'].apply(lambda x: any(genre in x for genre in selected_genres))]
    st.write(f"Dữ liệu cho các thể loại: **{', '.join(selected_genres)}** (Số lượng: {len(filtered_by_genre)})")
    st.dataframe(filtered_by_genre)
else:
    st.write("Chưa chọn thể loại nào.")

# Lọc dữ liệu chung theo năm và doanh thu
filtered_data = data[
    (data['year'] >= year_range[0]) & 
    (data['year'] <= year_range[1]) & 
    (data['revenue'] >= min_revenue) & 
    (data['revenue'] <= max_revenue)
]

st.write(f"Dữ liệu sau khi lọc: {filtered_data.shape[0]} dòng")
st.dataframe(filtered_data)

# Tìm kiếm phim
st.sidebar.header("Tìm Kiếm Phim")
search_title = st.sidebar.text_input("Nhập tên phim")
if search_title:
    searched_movie = data[data['title'].str.contains(search_title, case=False, na=False)]
    st.write(f"Tìm thấy {searched_movie.shape[0]} phim phù hợp")
    st.dataframe(searched_movie)

# Tải xuống dữ liệu
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

st.header("So sánh Ngân sách và Doanh thu theo Năm")
data_per_year = filtered_data.groupby('year').agg({
    'budget': 'sum',
    'revenue': 'sum',
}).reset_index()

# Vẽ biểu đồ
fig, ax1 = plt.subplots(figsize=(12, 6))
bar_width = 0.3
x = data_per_year['year']
ax1.bar(x - bar_width / 2, data_per_year['budget'], width=bar_width, label='Ngân sách (USD)', color='skyblue')
ax1.bar(x + bar_width / 2, data_per_year['revenue'], width=bar_width, label='Doanh thu (USD)', color='orange')
ax1.set_title('Biểu đồ so sánh doanh thu và ngân sách theo năm', fontsize=16)
ax1.set_xlabel('Năm', fontsize=12)
ax1.set_ylabel('Ngân sách / Doanh thu (USD)', fontsize=12)
ax1.set_xticks(x)
ax1.set_xticklabels(x, rotation=45)
ax1.legend(loc='upper left')
st.pyplot(fig)

st.header(" Độ Phổ Biến và Đánh Giá Phim")
movies_by_year = filtered_data.groupby('year').agg({
    'vote_count': 'sum',
    'vote_average': 'mean'
}).reset_index()

fig, ax1 = plt.subplots(figsize=(12, 6))

# Vẽ biểu đồ cột cho số lượt bình chọn
ax1.bar(movies_by_year['year'], movies_by_year['vote_count'], color='orange', alpha=0.7, label='Số lượt bình chọn')
ax1.set_xlabel('Năm')
ax1.set_ylabel('Số lượt bình chọn', color='orange')
ax1.tick_params(axis='y', labelcolor='orange')

# Thêm biểu đồ đường cho điểm đánh giá trung bình
ax2 = ax1.twinx()
ax2.plot(movies_by_year['year'], movies_by_year['vote_average'], color='blue', marker='o', label='Điểm đánh giá trung bình', linestyle='-', linewidth=2)
ax2.set_ylabel('Điểm đánh giá trung bình', color='blue')
ax2.tick_params(axis='y', labelcolor='blue')
fig.suptitle('Biểu đồ thể hiện sự tương quan giữa điểm đánh giá trung bình và số lượt bình chọn theo năm', fontsize=16)
st.pyplot(fig)

# Top 10 bộ phim có độ nổi tiếng cao nhất
top_10_movies = data[['title', 'popularity']].sort_values(by='popularity', ascending=False).head(10)

# Hiển thị bảng top 10 bộ phim
st.header("Top 10 Bộ Phim Có Độ Nổi Tiếng Cao Nhất")

# Vẽ biểu đồ cột cho độ nổi tiếng của top 10 bộ phim
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(top_10_movies['title'], top_10_movies['popularity'], color='skyblue')
ax.set_xlabel("Độ Nổi Tiếng")
ax.set_ylabel("Bộ Phim")
ax.set_title("Biểu đồ thể hiện top 10 bộ phim có độ nổi tiếng cao nhất")
st.pyplot(fig)


# Phân tích doanh thu và ngân sách
st.header("Phân Tích Doanh Thu và Ngân Sách Phim")
col1, col2 = st.columns(2)

with col1:
    st.write("Phân phối Ngân sách của Phim")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=data, x='budget', bins=50, kde=False, color='skyblue', ax=ax)
    plt.xticks(rotation=45)
    ax.set_title('Biểu đồ thể hiện phân phối ngân sách (USD)', fontsize=16)
    ax.set_xlabel('Ngân sách (USD)', fontsize=12)
    ax.set_ylabel('Số lượng phim', fontsize=12)
    st.pyplot(fig)

with col2:
    st.write("Phân phối Doanh Thu của Phim")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=data, x='revenue', bins=50, kde=False, color='green', ax=ax)
    ax.set_title('Biểu đồ thể hiện phân phối doanh thu (USD)', fontsize=16)
    ax.set_xlabel('Doanh thu (USD)', fontsize=12)
    ax.set_ylabel('Số lượng phim', fontsize=12)
    st.pyplot(fig)

# Top 10 hang san xuat va the loai phim
st.header("Top 10 Hãng Sản Xuất và Thể Loại Phim Phổ Biến Nhất")

# Phân tích Top 10 Hãng Sản Xuất Phim
production_companies_exploded = data['production_companies_list'].str.split(',').explode()
top_10_companies = production_companies_exploded.value_counts().head(10)

col1, col2 = st.columns(2)

with col1:
    st.write("Top 10 Hãng Sản Xuất Phim Phổ Biến Nhất")
    plt.figure(figsize=(12, 6))
    plt.bar(top_10_companies.index, top_10_companies.values, color='coral')
    plt.title('Biểu đồ thể hiện top 10 hãng sản xuất phim phổ biến nhất', fontsize=16)
    plt.xlabel('Hãng sản xuất', fontsize=12)
    plt.ylabel('Số lượng phim', fontsize=12)
    plt.xticks(ticks=range(len(top_10_companies.index)), labels=top_10_companies.index, rotation=45, fontsize=10)
    plt.tight_layout()
    st.pyplot(plt)

# Phân tích Top 10 Thể Loại Phim
genres_exploded = pd.Series(all_genres)
top_10_genres = genres_exploded.value_counts().head(10)

with col2:
    st.write("Top 10 Thể Loại Phim Phổ Biến Nhất")
    plt.figure(figsize=(12, 6))
    top_10_genres.plot(kind='bar', color='teal')
    plt.title('Biểu đồ thể hiện top 10 thể loại phim phổ biến nhất', fontsize=16)
    plt.xlabel('Thể loại phim', fontsize=12)
    plt.ylabel('Số lượng phim', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)
    

st.header("Tương Quan Giữa Các Biến")
col1, col2 = st.columns(2)
with col1:
    st.write('Tương Quan Giữa Số Lượt Bình Chọn và Đánh Giá Trung Bình')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=data, x='vote_count', y='vote_average', alpha=0.6, color='purple', ax=ax)
    ax.set_title('Biểu đồ phân tán thể hiện tương quan giữa số lượt bình chọn và đánh giá trung bình', fontsize=16)
    ax.set_xlabel('Số lượt bình chọn', fontsize=12)
    ax.set_ylabel('Điểm đánh giá trung bình', fontsize=12)
    st.pyplot(fig)

with col2:
    st.write('Tương Quan Giữa Ngân Sách và Doanh Thu')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=data, x='budget', y='revenue', alpha=0.5, color='blue', ax=ax)
    ax.set_title('Biểu đồ phân tán thể hiện tương quan giữa ngân sách và doanh thu', fontsize=16)
    ax.set_xlabel('Ngân sách (USD)', fontsize=12)
    ax.set_ylabel('Doanh thu (USD)', fontsize=12)
    st.pyplot(fig)

# Phân phối đánh giá trung bình của phim 
st.header("Phân Phối Đánh Giá Trung Bình Của Phim")
fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(data=data, x='vote_average', bins=20, kde=True, color='orange', ax=ax)
ax.set_title('Phân phối đánh giá trung bình', fontsize=16)
ax.set_xlabel('Điểm đánh giá trung bình', fontsize=12)
ax.set_ylabel('Số lượng phim', fontsize=12)
st.pyplot(fig)

# Đếm số lượng phim theo từng năm
st.header("Xu Hướng Số Lượng Phim Qua Các Năm")
movies_per_year = data['year'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(movies_per_year.index, movies_per_year.values, marker='o', linestyle='-', color='b')
ax.set_title('Biểu đồ thể hiện xu hướng số lượng phim qua các năm', fontsize=16)
ax.set_xlabel('Năm', fontsize=12)
ax.set_ylabel('Số lượng phim', fontsize=12)
ax.grid(visible=True, linestyle='--', alpha=0.7)
st.pyplot(fig)

# LƯU HOÀNG
#1. Biểu đồ số lượng phim theo năm cho thể loại được chọn
if selected_genres:
    st.header(f"Số Lượng Phim Theo Năm - {', '.join(selected_genres)}")
    movies_by_year = filtered_by_genre.groupby('year').size()
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.xticks(rotation=45)
    movies_by_year.plot(kind='bar', ax=ax, color='purple', alpha=0.7)
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    xytext=(0, 9), 
                    textcoords='offset points', 
                    ha='center', va='bottom', 
                    fontsize=10, color='black')
    ax.set_title(f"Biểu đồ thể hiện số Lượng Phim Theo Năm - {', '.join(selected_genres)}")
    ax.set_xlabel("Năm")
    ax.set_ylabel("Số lượng phim")
    st.pyplot(fig)
# 2. Biểu đồ Tròn Tỷ Lệ Ngôn Ngữ Phim
st.header("Tỷ Lệ Ngôn Ngữ Phim")
top_10_languages = data['original_language'].value_counts().head(10)
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(top_10_languages, labels=top_10_languages.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set2", len(top_10_languages)))
ax.set_title('Top 10 Ngôn Ngữ Phim Phổ Biến Nhất', fontsize=16)
ax.legend(top_10_languages.index, title="Ngôn Ngữ", loc='upper left', bbox_to_anchor=(1, 1))
st.pyplot(fig)

# 3. Biểu đồ Cột Top 10 Quốc Gia Sản Xuất Phim Nhiều Nhất
st.header("Top 10 Quốc Gia Sản Xuất Phim Nhiều Nhất")
production_countries_exploded = filtered_data['production_countries_list'].str.split(',').explode().str.strip()
country_counts = production_countries_exploded.value_counts()

# Top 10 quốc gia sản xuất phim nhiều nhất
top_10_countries = country_counts.head(10)
fig, ax = plt.subplots( figsize=(16, 6))

# Biểu đồ Cột cho Top 10 Quốc Gia Sản Xuất Phim Nhiều Nhất
ax.bar(top_10_countries.index, top_10_countries.values, color='teal')
ax.set_title('Biểu  đồ thể hiện top 10 quốc gia sản xuất phim nhiều nhất', fontsize=16)
ax.set_xlabel('Quốc Gia', fontsize=12)
ax.set_ylabel('Số Lượng Phim', fontsize=12)
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# CSS cho trang web
st.markdown(
    """
    <style>
    .block-container {
        max-width: 960px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
    }
    </style>
    """, 
    unsafe_allow_html=True
)
