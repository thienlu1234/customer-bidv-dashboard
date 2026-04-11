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
        df = pd.read_csv(file)
    elif name.endswith(".xlsx"):
        df = pd.read_excel(file)
    elif name.endswith(".xlsb"):
        df = pd.read_excel(file, engine="pyxlsb")
    else:
        return None

    # =========================
    # FIX NGÀY EXCEL
    # =========================
    for col in df.columns:
        if "NGAY" in str(col).upper():
            try:
                num = pd.to_numeric(df[col], errors="coerce")
                if num.notna().sum() > 0:
                    df[col] = pd.to_datetime("1899-12-30") + pd.to_timedelta(num, unit="D")
            except:
                pass

    return df


def find_column(df, keywords):
    for col in df.columns:
        col_upper = str(col).upper()
        for kw in keywords:
            if kw in col_upper:
                return col
    return None


# =========================
# FORMAT HIỂN THỊ
# =========================
def format_dataframe(df, col_customer=None, col_manager=None):
    df_display = df.copy()

    for col in df_display.columns:

        # format ngày
        if pd.api.types.is_datetime64_any_dtype(df_display[col]):
            df_display[col] = df_display[col].dt.strftime("%d/%m/%Y")

        # format số
        elif df_display[col].dtype in ["float64", "int64"]:

            # ❌ KHÔNG format các cột mã + năm
            if col in [col_customer, col_manager] or "NAM" in col:
                df_display[col] = df_display[col].apply(
                    lambda x: str(int(x)) if pd.notnull(x) else ""
                )
        
            # ✅ format số tiền
            else:
                df_display[col] = df_display[col].apply(
                    lambda x: f"{x:,.0f}" if pd.notnull(x) else ""
                )

    return df_display


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

    if col_status is None:
        st.error("❌ Không tìm thấy cột trạng thái")
        st.stop()

    df[col_status] = df[col_status].astype("string").str.strip()

    # =========================
    # MENU
    # =========================
    menu = st.sidebar.radio(
        "📂 Chọn chức năng",
        ["📊 Tổng quan", "🎯 Chăm sóc khách hàng", "💰 HDVCKH_CK", "🏦 DNCK", "📈 Trung bình DV/ người"]]
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

        st.subheader("🎯 Phân loại theo HDVKKH_BQ")

        df_cs = df[df[col_status].isin(["Active", "New"])].copy()

        col_hdv = "HDVKKH_BQ"

        if col_hdv not in df_cs.columns:
            st.error("❌ Không tìm thấy cột HDVKKH_BQ")
            st.stop()

        df_cs[col_hdv] = pd.to_numeric(df_cs[col_hdv], errors="coerce")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Dưới 5TR", f"{(df_cs[col_hdv] <= 5_000_000).sum():,}")
        c2.metric("5-20TR", f"{((df_cs[col_hdv] > 5_000_000) & (df_cs[col_hdv] <= 20_000_000)).sum():,}")
        c3.metric("20-50TR", f"{((df_cs[col_hdv] > 20_000_000) & (df_cs[col_hdv] <= 50_000_000)).sum():,}")
        c4.metric(">50TR", f"{(df_cs[col_hdv] > 50_000_000).sum():,}")

        option = st.selectbox("Chọn nhóm", ["<5TR", "5-20TR", "20-50TR", ">50TR"])

        df_show = df_cs.copy()

        if option == "<5TR":
            df_show = df_cs[df_cs[col_hdv] <= 5_000_000]
        elif option == "5-20TR":
            df_show = df_cs[(df_cs[col_hdv] > 5_000_000) & (df_cs[col_hdv] <= 20_000_000)]
        elif option == "20-50TR":
            df_show = df_cs[(df_cs[col_hdv] > 20_000_000) & (df_cs[col_hdv] <= 50_000_000)]
        else:
            df_show = df_cs[df_cs[col_hdv] > 50_000_000]

        st.metric("Số khách", f"{len(df_show):,}")

        st.dataframe(
            format_dataframe(df_show, col_customer, col_manager),
            use_container_width=True,
            height=600,
            hide_index=True
        )

    # =========================
    # 3. HDVCKH_CK
    # =========================
    elif menu == "💰 HDVCKH_CK":

        st.subheader("💰 Khách hàng cần chăm (HDVCKH_CK)")

        col_ck = "HDVCKH_CK"

        df_ck = df[df[col_status].isin(["Active", "New"])].copy()
        df_ck[col_ck] = pd.to_numeric(df_ck[col_ck], errors="coerce")

        df_ck = df_ck[df_ck[col_ck] > 0]

        st.metric("Số khách", f"{len(df_ck):,}")

        st.dataframe(
            format_dataframe(df_ck, col_customer, col_manager),
            use_container_width=True,
            height=600,
            hide_index=True
        )

    # =========================
    # 4. DNCK
    # =========================
    elif menu == "🏦 DNCK":

        st.subheader("🏦 Khách hàng cần chăm (DNCK)")

        col_dnck = "DNCK"

        df_dnck = df[df[col_status].isin(["Active", "New"])].copy()
        df_dnck[col_dnck] = pd.to_numeric(df_dnck[col_dnck], errors="coerce")

        df_dnck = df_dnck[df_dnck[col_dnck] > 0]

        st.metric("Số khách", f"{len(df_dnck):,}")

        st.dataframe(
            format_dataframe(df_dnck, col_customer, col_manager),
            use_container_width=True,
            height=600,
            hide_index=True
        )

    # =========================
    # 5. TRUNG BÌNH DV / NGƯỜI
    # =========================
    elif menu == "📈 Trung bình DV/ người":
    
        st.subheader("📈 Trung bình số dịch vụ / khách hàng")
    
        col_spdv = "TOTAL_SPDV"
    
        if col_spdv not in df.columns:
            st.error("❌ Không tìm thấy cột TOTAL_SPDV")
            st.stop()
    
        # 🔥 chỉ lấy Active + New
        df_kh = df[df[col_status].isin(["Active", "New"])].copy()
    
        # chuyển sang số
        df_kh[col_spdv] = pd.to_numeric(df_kh[col_spdv], errors="coerce")
    
        # tổng dịch vụ
        total_spdv = df_kh[col_spdv].sum()
    
        # số khách
        total_kh = len(df_kh)
    
        # trung bình
        avg_spdv = total_spdv / total_kh if total_kh > 0 else 0
    
        # =========================
        # HIỂN THỊ KPI
        # =========================
        c1, c2, c3 = st.columns(3)
    
        c1.metric("Tổng DV", f"{int(total_spdv):,}")
        c2.metric("Số KH", f"{total_kh:,}")
        c3.metric("Trung bình DV / KH", f"{avg_spdv:.2f}")
    
        # =========================
        # HIỂN THỊ DATA
        # =========================
        st.subheader("📋 Danh sách khách hàng")
    
        st.dataframe(
            format_dataframe(df_kh, col_customer, col_manager),
            use_container_width=True,
            height=600,
            hide_index=True
        )
else:
    st.info("👉 Upload file để bắt đầu")
