import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(layout="wide")

st.title("📊 Dashboard Phân Tích Khách Hàng")

file = st.file_uploader("Upload file Excel", type=["xlsx"])

@st.cache_data
def load_data(file):
    return pd.read_excel(file)

if file is not None:
    df = load_data(file)
    df = df.fillna(0)

    # =========================
    # MENU
    # =========================
    menu = st.sidebar.radio("Chọn phân tích", [
        "1. Top khách hàng giá trị",
        "2. Phân nhóm VIP",
        "3. Theo cán bộ quản lý",
        "4. Theo phòng ban",
        "5. Khách ngủ đông",
        "6. Biểu đồ tiền & doanh thu",
        "7. Clustering AI",
        "8. Customer Scoring",
        "9. Dự đoán rời bỏ"
    ])

    # =========================
    # 1. TOP KHÁCH HÀNG
    # =========================
    if menu.startswith("1"):
        df["TOTAL_VALUE"] = df["TNT"] + df["HDVBQ"]
        top = df.nlargest(20, "TOTAL_VALUE")

        st.subheader("🏆 Top khách hàng giá trị cao")
        st.dataframe(top)

    # =========================
    # 2. VIP / THƯỜNG
    # =========================
    elif menu.startswith("2"):
        threshold = df["TOTAL_VALUE"].quantile(0.8)
        df["SEGMENT"] = df["TOTAL_VALUE"].apply(
            lambda x: "VIP" if x >= threshold else "Thường"
        )

        st.subheader("🎯 Phân nhóm khách hàng")
        st.bar_chart(df["SEGMENT"].value_counts())

    # =========================
    # 3. THEO CÁN BỘ
    # =========================
    elif menu.startswith("3"):
        result = df.groupby("CANBO_QUANLY")["TOTAL_VALUE"].sum().reset_index()

        st.subheader("👨‍💼 Hiệu quả theo cán bộ")
        fig = px.bar(result.sort_values(by="TOTAL_VALUE", ascending=False),
                     x="CANBO_QUANLY", y="TOTAL_VALUE")
        st.plotly_chart(fig)

    # =========================
    # 4. THEO PHÒNG BAN
    # =========================
    elif menu.startswith("4"):
        result = df.groupby("PHONG BAN")["TOTAL_VALUE"].sum().reset_index()

        st.subheader("🏢 Hiệu quả theo phòng ban")
        fig = px.pie(result, names="PHONG BAN", values="TOTAL_VALUE")
        st.plotly_chart(fig)

    # =========================
    # 5. KHÁCH NGỦ ĐÔNG
    # =========================
    elif menu.startswith("5"):
        dormant = df[df["TOTAL_SPDV"] <= 1]

        st.subheader(f"😴 Khách ngủ đông: {len(dormant)}")
        st.dataframe(dormant.head(100))

    # =========================
    # 6. BIỂU ĐỒ TIỀN + DOANH THU
    # =========================
    elif menu.startswith("6"):
        st.subheader("📊 Phân bố tiền gửi & doanh thu")

        fig1 = px.histogram(df, x="HDVBQ", title="Tiền gửi")
        fig2 = px.histogram(df, x="TNT", title="Doanh thu")

        st.plotly_chart(fig1)
        st.plotly_chart(fig2)

    # =========================
    # 7. CLUSTERING AI
    # =========================
    elif menu.startswith("7"):
        X = df[["TNT", "HDVBQ", "TOTAL_SPDV"]]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=3, n_init=10)
        df["CLUSTER"] = kmeans.fit_predict(X_scaled)

        st.subheader("🤖 Phân cụm khách hàng")
        fig = px.scatter(df, x="TNT", y="HDVBQ", color="CLUSTER")
        st.plotly_chart(fig)

    # =========================
    # 8. SCORING
    # =========================
    elif menu.startswith("8"):
        df["SCORE"] = df["TNT"]*0.5 + df["HDVBQ"]*0.3 + df["TOTAL_SPDV"]*0.2

        st.subheader("📊 Điểm khách hàng")
        st.dataframe(df.nlargest(50, "SCORE"))

    # =========================
    # 9. CHURN
    # =========================
    elif menu.startswith("9"):
        df["CHURN"] = df["TOTAL_SPDV"].apply(lambda x: 1 if x <= 1 else 0)
        churn = df[df["CHURN"] == 1]

        st.subheader(f"⚠️ Khách có nguy cơ rời: {len(churn)}")
        st.dataframe(churn.head(100))
