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

    # fix NaN
    df = df.fillna("NaN")

    # chuẩn hóa tên cột
    df.columns = [str(c).strip().upper() for c in df.columns]

    # =========================
    # TÌM CỘT TRẠNG THÁI
    # =========================
    col_status = next((c for c in df.columns if "TRANGTHAI" in c or "STATUS" in c), None)
    col_manager = next((c for c in df.columns if "CANBO" in c), None)
    col_phong = next((c for c in df.columns if "PHONG" in c), None)

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
    null = len(df[df[col_status] == "NaN"])

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
    st.subheader("🎯 Lọc dữ liệu")

    option = st.selectbox("Chọn loại khách", ["All", "Active", "New"])

    df_filtered = df.copy()

    if option != "All":
        df_filtered = df_filtered[df_filtered[col_status] == option]

    # =========================
    # FORMAT SỐ
    # =========================
    df_display = df_filtered.copy()

    numeric_cols = df_display.select_dtypes(include=["float64", "int64"]).columns

    for col in numeric_cols:
        df_display[col] = df_display[col].apply(
            lambda x: f"{x:,.0f}" if pd.notnull(x) else ""
        )

    # =========================
    # CHỌN CỘT QUAN TRỌNG
    # =========================
    important_cols = [
        col_status,
        "TNT",
        "HDVBQ",
        "TOTAL_SPDV",
        col_manager,
        col_phong
    ]

    important_cols = [c for c in important_cols if c in df_display.columns]

    # =========================
    # HIGHLIGHT MÀU
    # =========================
    def highlight_status(val):
        if val == "Active":
            return "background-color: lightgreen"
        elif val == "New":
            return "background-color: lightblue"
        return ""

    st.subheader("📋 Danh sách khách hàng")

    st.dataframe(
        df_display[important_cols].style.applymap(
            highlight_status, subset=[col_status]
        ),
        use_container_width=True,
        height=600
    )

else:
    st.info("👉 Upload file để bắt đầu")
