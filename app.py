import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📊 Dashboard Khách Hàng")

# =========================
# UPLOAD FILE
# =========================
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


# =========================
# MAIN
# =========================
if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is None:
        st.error("❌ Không đọc được file")
        st.stop()

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
    # MENU
    # =========================
    menu = st.sidebar.radio(
        "📂 Chọn chức năng",
        ["📊 Tổng quan", "🎯 Chăm sóc khách hàng", "💰 HDVCKH_CK"]
    )

    # =========================
    # 1. TỔNG QUAN
    # =========================
    if menu == "📊 Tổng quan":

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
    # 2. CHĂM SÓC KHÁCH HÀNG
    # =========================
    elif menu == "🎯 Chăm sóc khách hàng":

        st.subheader("🎯 Phân loại chăm sóc theo HDVKKH_BQ")

        df_cs = df[df[col_status].isin(["Active", "New"])].copy()

        col_hdv = "HDVKKH_BQ"

        if col_hdv not in df_cs.columns:
            st.error("❌ Không tìm thấy cột HDVKKH_BQ")
            st.stop()

        df_cs[col_hdv] = pd.to_numeric(df_cs[col_hdv], errors="coerce")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Dưới 5TR", f"{(df_cs[col_hdv] <= 5_000_000).sum():,}")
        c2.metric("5TR - 20TR", f"{((df_cs[col_hdv] > 5_000_000) & (df_cs[col_hdv] <= 20_000_000)).sum():,}")
        c3.metric("20TR - 50TR", f"{((df_cs[col_hdv] > 20_000_000) & (df_cs[col_hdv] <= 50_000_000)).sum():,}")
        c4.metric("> 50TR", f"{(df_cs[col_hdv] > 50_000_000).sum():,}")

        option = st.selectbox(
            "📌 Chọn nhóm",
            ["Dưới 5TR", "5TR - 20TR", "20TR - 50TR", "> 50TR"]
        )

        # FIX LỖI df_show
        df_show = df_cs.copy()

        if option == "Dưới 5TR":
            df_show = df_cs[df_cs[col_hdv] <= 5_000_000]
        elif option == "5TR - 20TR":
            df_show = df_cs[(df_cs[col_hdv] > 5_000_000) & (df_cs[col_hdv] <= 20_000_000)]
        elif option == "20TR - 50TR":
            df_show = df_cs[(df_cs[col_hdv] > 20_000_000) & (df_cs[col_hdv] <= 50_000_000)]
        else:
            df_show = df_cs[df_cs[col_hdv] > 50_000_000]

        st.metric("Số khách", f"{len(df_show):,}")

        st.dataframe(df_show, use_container_width=True, height=600, hide_index=True)

    # =========================
    # 3. HDVCKH_CK
    # =========================
    elif menu == "💰 HDVCKH_CK":

        st.subheader("💰 Khách hàng cần chăm sóc (HDVCKH_CK)")

        col_ck = "HDVCKH_CK"

        if col_ck not in df.columns:
            st.error("❌ Không tìm thấy cột HDVCKH_CK")
            st.stop()

        df_ck = df[df[col_status].isin(["Active", "New"])].copy()

        df_ck[col_ck] = pd.to_numeric(df_ck[col_ck], errors="coerce")

        df_ck = df_ck[df_ck[col_ck].notna() & (df_ck[col_ck] > 0)]

        st.metric("Số khách cần chăm", f"{len(df_ck):,}")

        st.dataframe(df_ck, use_container_width=True, height=600, hide_index=True)

else:
    st.info("👉 Upload file để bắt đầu")
