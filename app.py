import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Dashboard Trạng Thái Khách Hàng")

# =========================
# UPLOAD FILE
# =========================
uploaded_file = st.file_uploader(
    "Upload file dữ liệu",
    type=["xlsx", "csv", "xlsb"]
)

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data(file):
    name = file.name.lower()

    if name.endswith(".csv"):
        return pd.read_csv(file)
    elif name.endswith(".xlsx"):
        return pd.read_excel(file)
    elif name.endswith(".xlsb"):
        return pd.read_excel(file, engine="pyxlsb")

# =========================
# MAIN
# =========================
if uploaded_file is not None:

    df = load_data(uploaded_file)

    # fix dữ liệu trống
    df = df.fillna("NaN")

    # fix tên cột
    df.columns = [str(c).strip().upper() for c in df.columns]

    # =========================
    # TÌM CỘT TRẠNG THÁI
    # =========================
    col_status = next((c for c in df.columns if "TRANGTHAI" in c or "STATUS" in c), None)

    if col_status is None:
        st.error("❌ Không tìm thấy cột trạng thái")
        st.stop()

    # chuẩn hóa
    df[col_status] = df[col_status].astype(str).str.strip()

    # =========================
    # KPI
    # =========================
    total = len(df)
    active = len(df[df[col_status] == "Active"])
    new = len(df[df[col_status] == "New"])
    frozen = len(df[df[col_status] == "Frozen"])
    dormant = len(df[df[col_status] == "Dormant"])
    null = len(df[df[col_status] == "NaN"])

    st.subheader("📌 Tổng quan khách hàng")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Tổng KH", f"{total:,}")
    col2.metric("Active", f"{active:,}")
    col3.metric("New", f"{new:,}")
    col4.metric("Frozen", f"{frozen:,}")
    col5.metric("Dormant", f"{dormant:,}")
    col6.metric("NaN", f"{null:,}")

    # =========================
    # FILTER ACTIVE + NEW
    # =========================
    df_filtered = df[df[col_status].isin(["Active", "New"])]

    st.subheader("🎯 Danh sách khách hàng Active & New")

    # =========================
    # FORMAT SỐ CHO ĐẸP
    # =========================
    df_display = df_filtered.copy()

    numeric_cols = df_display.select_dtypes(include=["int64", "float64"]).columns

    for col in numeric_cols:
        df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}")

    # =========================
    # HIỂN THỊ
    # =========================
    st.dataframe(
        df_display,
        use_container_width=True,
        height=600
    )

else:
    st.info("👉 Upload file để bắt đầu")
