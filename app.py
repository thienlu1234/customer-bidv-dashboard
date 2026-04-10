import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Dashboard Trạng Thái Khách Hàng")

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
    dates = pd.to_datetime("1899-12-30") + pd.to_timedelta(numeric_series, unit="D")
    return dates


if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is None:
        st.error("❌ Không đọc được file")
        st.stop()

    # Chuẩn hóa tên cột
    df.columns = [str(c).strip().upper() for c in df.columns]

    # Tìm các cột quan trọng
    col_status = find_column(df, ["TRANGTHAI", "STATUS"])
    col_customer = find_column(df, ["MA_KHACHHANG", "CIF", "CUSTOMER"])
    col_manager = find_column(df, ["CANBO_QUANLY", "CANBO", "CBQL"])
    col_open_date = find_column(df, ["NGAYMOCIF", "NGAY_MO_CIF"])
    col_open_year = find_column(df, ["NAMMOCIF", "NAM_MO_CIF", "YEAR_MOCIF", "YEAR"])

    if col_status is None:
        st.error("❌ Không tìm thấy cột trạng thái khách hàng")
        st.stop()

    # Chuẩn hóa trạng thái
    df[col_status] = df[col_status].astype("string").str.strip()

    # Tính KPI trạng thái
    total = len(df)
    active = (df[col_status] == "Active").sum()
    new = (df[col_status] == "New").sum()
    frozen = (df[col_status] == "Frozen").sum()
    dormant = (df[col_status] == "Dormant").sum()
    null_count = df[col_status].isna().sum() + (df[col_status].astype(str).str.upper() == "NAN").sum()

    st.subheader("📌 Tổng quan khách hàng")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Tổng KH", f"{total:,}")
    c2.metric("Active", f"{active:,}")
    c3.metric("New", f"{new:,}")
    c4.metric("Frozen", f"{frozen:,}")
    c5.metric("Dormant", f"{dormant:,}")
    c6.metric("NaN", f"{null_count:,}")

    # Lọc dữ liệu
    st.subheader("🎯 Lọc dữ liệu")
    option = st.selectbox("Chọn loại khách", ["All", "Active", "New"])

    df_filtered = df.copy()
    if option != "All":
        df_filtered = df_filtered[df_filtered[col_status] == option]

    # Bản để hiển thị
    df_display = df_filtered.copy()

    # 1) Cột mã khách hàng: bỏ dấu phẩy, giữ dạng mã
    if col_customer is not None:
        customer_numeric = pd.to_numeric(df_display[col_customer], errors="coerce")
        df_display[col_customer] = customer_numeric.apply(
            lambda x: str(int(x)) if pd.notnull(x) else ""
        )

    # 2) Cột cán bộ quản lý: bỏ dấu phẩy, giữ dạng mã
    if col_manager is not None:
        manager_numeric = pd.to_numeric(df_display[col_manager], errors="coerce")
        df_display[col_manager] = manager_numeric.apply(
            lambda x: str(int(x)) if pd.notnull(x) else ""
        )

    # 3) Cột ngày mở CIF: đổi serial date Excel thành ngày thật
    if col_open_date is not None:
        converted_dates = convert_excel_serial_to_date(df_display[col_open_date])
        df_display[col_open_date] = converted_dates.dt.strftime("%Y-%m-%d")
        df_display[col_open_date] = df_display[col_open_date].fillna("")

    # 4) Cột năm mở CIF: giữ nguyên dạng năm, không dấu phẩy
    if col_open_year is not None:
        year_numeric = pd.to_numeric(df_display[col_open_year], errors="coerce")
        df_display[col_open_year] = year_numeric.apply(
            lambda x: str(int(x)) if pd.notnull(x) else ""
        )

    # 5) Format các cột số còn lại
    excluded_cols = {
        col_customer,
        col_manager,
        col_open_date,
        col_open_year
    }

    numeric_cols = df_filtered.select_dtypes(include=["number"]).columns

    for col in numeric_cols:
        if col not in excluded_cols:
            df_display[col] = pd.to_numeric(df_filtered[col], errors="coerce").apply(
                lambda x: f"{x:,.0f}" if pd.notnull(x) else ""
            )

    st.subheader("📋 Danh sách khách hàng (FULL DATA)")
    st.dataframe(
    df_display,
    use_container_width=True,
    height=650,
    hide_index=True
    )

else:
    st.info("👉 Upload file để bắt đầu")
