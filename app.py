import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Dashboard Khách Hàng (Active + New)")

uploaded_file = st.file_uploader(
    "Upload file dữ liệu",
    type=["xlsx", "csv", "xlsb"]
)

@st.cache_data
def load_data(file):
    name = file.name.lower()

    if name.endswith(".csv"):
        return pd.read_csv(file)
    elif name.endswith(".xlsx"):
        return pd.read_excel(file)
    elif name.endswith(".xlsb"):
        return pd.read_excel(file, engine="pyxlsb")
    return None


def find_column(df, keywords):
    for col in df.columns:
        col_upper = str(col).upper()
        for kw in keywords:
            if kw in col_upper:
                return col
    return None


def convert_excel_serial_to_date(series):
    numeric_series = pd.to_numeric(series, errors="coerce")
    return pd.to_datetime("1899-12-30") + pd.to_timedelta(numeric_series, unit="D")


if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is None:
        st.error("❌ Không đọc được file")
        st.stop()

    # =========================
    # CHUẨN HÓA CỘT
    # =========================
    df.columns = [str(c).strip().upper() for c in df.columns]

    col_status = find_column(df, ["TRANGTHAI", "STATUS"])
    col_customer = find_column(df, ["MA_KHACHHANG", "CIF"])
    col_manager = find_column(df, ["CANBO_QUANLY", "CBQL"])
    col_open_date = find_column(df, ["NGAYMOCIF"])
    col_open_year = find_column(df, ["NAMMOCIF"])

    if col_status is None:
        st.error("❌ Không tìm thấy cột trạng thái")
        st.stop()

    df[col_status] = df[col_status].astype("string").str.strip()

    # =========================
    # KPI
    # =========================
    st.subheader("📌 Tổng quan khách hàng")

    total = len(df)
    active = (df[col_status] == "Active").sum()
    new = (df[col_status] == "New").sum()
    frozen = (df[col_status] == "Frozen").sum()
    dormant = (df[col_status] == "Dormant").sum()
    nan_count = df[col_status].isna().sum()
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    c1.metric("Tổng KH", f"{total:,}")
    c2.metric("Active", f"{active:,}")
    c3.metric("New", f"{new:,}")
    c4.metric("Frozen", f"{frozen:,}")
    c5.metric("Dormant", f"{dormant:,}")
    c6.metric("NaN", f"{nan_count:,}")

    # =========================
    # CHỈ LẤY ACTIVE + NEW
    # =========================
    df_filtered = df[df[col_status].isin(["Active", "New"])].copy()

    # =========================
    # CHĂM SÓC KHÁCH HÀNG
    # =========================
    col_hdv = "HDVKKH_BQ"

    if col_hdv in df_filtered.columns:
        df_filtered[col_hdv] = pd.to_numeric(df_filtered[col_hdv], errors="coerce")

        def classify_care(x):
            if pd.isna(x):
                return "Không xác định"
            elif x <= 5_000_000:
                return "Không cần chăm"
            elif x <= 20_000_000:
                return "Chăm sóc cấp 1"
            elif x <= 50_000_000:
                return "Chăm sóc cấp 2"
            else:
                return "Chăm sóc cấp 3"

        df_filtered["CHAM_SOC"] = df_filtered[col_hdv].apply(classify_care)

        # KPI chăm sóc
        st.subheader("🎯 Phân loại chăm sóc theo HDVKKH_BQ")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Dưới 5TR", f"{(df_filtered['CHAM_SOC']=='Không cần chăm').sum():,}")
        c2.metric("Từ 5TR đến 20TR", f"{(df_filtered['CHAM_SOC']=='Chăm sóc cấp 1').sum():,}")
        c3.metric("Từ 20TR đến 50TR", f"{(df_filtered['CHAM_SOC']=='Chăm sóc cấp 2').sum():,}")
        c4.metric("Trên 50TR", f"{(df_filtered['CHAM_SOC']=='Chăm sóc cấp 3').sum():,}")

    # =========================
    # FORMAT HIỂN THỊ
    # =========================
    df_display = df_filtered.copy()

    # mã KH
    if col_customer:
        df_display[col_customer] = pd.to_numeric(df_display[col_customer], errors="coerce")\
            .apply(lambda x: str(int(x)) if pd.notnull(x) else "")

    # cán bộ
    if col_manager:
        df_display[col_manager] = pd.to_numeric(df_display[col_manager], errors="coerce")\
            .apply(lambda x: str(int(x)) if pd.notnull(x) else "")

    # ngày
    if col_open_date:
        df_display[col_open_date] = convert_excel_serial_to_date(df_display[col_open_date])\
            .dt.strftime("%Y-%m-%d")

    # năm
    if col_open_year:
        df_display[col_open_year] = pd.to_numeric(df_display[col_open_year], errors="coerce")\
            .apply(lambda x: str(int(x)) if pd.notnull(x) else "")

    # format số
    exclude = {col_customer, col_manager, col_open_date, col_open_year}
    num_cols = df_filtered.select_dtypes(include=["number"]).columns

    for col in num_cols:
        if col not in exclude:
            df_display[col] = pd.to_numeric(df_filtered[col], errors="coerce")\
                .apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")

    # =========================
    # HIỂN THỊ
    # =========================
    st.subheader("📋 Khách hàng Active & New")

    col1, col2 = st.columns(2)

    with col1:
        st.write("🟢 Active")
        st.dataframe(
            df_display[df_display[col_status] == "Active"],
            hide_index=True,
            use_container_width=True,
            height=500
        )

    with col2:
        st.write("🆕 New")
        st.dataframe(
            df_display[df_display[col_status] == "New"],
            hide_index=True,
            use_container_width=True,
            height=500
        )

else:
    st.info("👉 Upload file để bắt đầu")
