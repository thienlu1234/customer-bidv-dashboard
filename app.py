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

    # giữ nguyên NaN (KHÔNG replace nữa)
    # df = df.fillna("NaN")

    # chuẩn hóa tên cột
    df.columns = [str(c).strip().upper() for c in df.columns]

    # =========================
    # TÌM CỘT TRẠNG THÁI
    # =========================
    col_status = next((c for c in df.columns if "TRANGTHAI" in c or "STATUS" in c), None)

    if col_status is None:
        st.error("❌ Không tìm thấy cột trạng thái")
        st.stop()

    df[col_status] = df[col_status].astype(str).str.strip()

    # =========================
    # KPI
    # =========================
    total = len(df)
    active = len(df[df[col_status] == "Active"])
    new = len(df[df[col_status] == "New"])
    frozen = len(df[df[col_status] == "Frozen"])
    dormant = len(df[df[col_status] == "Dormant"])
    null = df[col_status].isna().sum()

    st.subheader("📌 Tổng quan khách hàng")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Tổng KH", f"{total:,}")
    c2.metric("Active", f"{active:,}")
    c3.metric("New", f"{new:,}")
    c4.metric("Frozen", f"{frozen:,}")
    c5.metric("Dormant", f"{dormant:,}")
    c6.metric("NaN", f"{null:,}")

    # =========================
    # FILTER
    # =========================
    option = st.selectbox("Chọn loại khách", ["All", "Active", "New"])

    df_filtered = df.copy()

    if option != "All":
        df_filtered = df_filtered[df_filtered[col_status] == option]

    # =========================
    # FORMAT SỐ (GIỮ NGUYÊN CỘT)
    # =========================
    df_display = df_filtered.copy()

    numeric_cols = df_display.select_dtypes(include=["float64", "int64"]).columns

    for col in numeric_cols:
        df_display[col] = df_display[col].apply(
            lambda x: f"{x:,.0f}" if pd.notnull(x) else ""
        )

    # =========================
    # HIỂN THỊ FULL DATA
    # =========================
    st.subheader("📋 Danh sách khách hàng (FULL DATA)")

    st.dataframe(
        df_display,
        use_container_width=True,
        height=600
    )

else:
    st.info("👉 Upload file để bắt đầu")
