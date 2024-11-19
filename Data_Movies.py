import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
import seaborn as sns

data = pd.read_csv("Data/Data_Movies_clear.csv")

st.title("Phân Tích Dữ Liệu Phim")

st.header("1. Phân Phối Điểm Đánh Giá (vote_average)")
fig, ax = plt.subplots()
sns.histplot(data['vote_average'], kde=True, bins=20, ax=ax, color="skyblue")
ax.set_title("Phân Phối Điểm Đánh Giá")
ax.set_xlabel("Điểm đánh giá")
ax.set_ylabel("Tần suất")
st.pyplot(fig)

st.header("2. Tương Quan Ngân Sách vs Doanh Thu")
fig, ax = plt.subplots()
sns.scatterplot(x=data['budget'], y=data['revenue'], alpha=0.5, ax=ax)
ax.set_title("Tương Quan Giữa Ngân Sách và Doanh Thu")
ax.set_xlabel("Ngân sách")
ax.set_ylabel("Doanh thu")
st.pyplot(fig)

st.header("3. Doanh Thu Trung Bình Theo Năm")
revenue_by_year = data.groupby('year')['revenue'].mean().dropna()
fig, ax = plt.subplots()
revenue_by_year.plot(kind='line', ax=ax, color="green")
ax.set_title("Doanh Thu Trung Bình Theo Năm")
ax.set_xlabel("Năm")
ax.set_ylabel("Doanh thu trung bình")
st.pyplot(fig)
