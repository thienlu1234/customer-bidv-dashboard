import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import os 
st.set_page_config(layout="wide")

def find_column(df, keywords):
    for col in df.columns:
        col_upper = str(col).upper()
        for kw in keywords:
            if kw in col_upper:
                return col
    return None

# ======================
# CSS GIAO DIỆN BIDV
# ======================
st.markdown("""
<style>

/* ============================= */
/* BACKGROUND */
/* ============================= */
body {
    background-color: #f5f7f9;
}

/* ============================= */
/* SIDEBAR */
/* ============================= */
section[data-testid="stSidebar"] {
    background-color: #0E6F66;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* ============================= */
/* MAIN TITLE */
/* ============================= */
.main-title {
    font-size: 38px;
    font-weight: 700;
    color: #0E6F66;
}

/* ============================= */
/* SECTION TITLE */
/* ============================= */
.section-title {
    color: #0E6F66;
    font-size: 26px;
    font-weight: 700;
    border-left: 6px solid #F5C32C;
    padding-left: 10px;
    margin-top: 25px;
}

/* ============================= */
/* KPI CARD */
/* ============================= */
.kpi-card {
    background: linear-gradient(135deg, #ffffff, #f9fafb);
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
    text-align: center;
    transition: 0.3s;
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0px 10px 24px rgba(0,0,0,0.12);
}

.kpi-title {
    font-size: 14px;
    color: gray;
}

.kpi-value {
    font-size: 28px;
    font-weight: bold;
    color: #0E6F66;
}

/* ============================= */
/* DATAFRAME */
/* ============================= */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stDataFrame"] table {
    border-radius: 12px;
}

/* ============================= */
/* SELECTBOX */
/* ============================= */
div[data-baseweb="select"] {
    border-radius: 10px;
}

/* hover */
div[data-baseweb="select"]:hover {
    border: 2px solid #F5C32C;
}

/* focus */
div[data-baseweb="select"] > div {
    border: 2px solid #0E6F66;
}

/* dropdown hover */
li:hover {
    background-color: #F5C32C !important;
    color: black !important;
}

/* ============================= */
/* METRIC */
/* ============================= */
[data-testid="stMetric"] {
    background-color: white;
    padding: 12px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}

/* ============================= */
/* BUTTON */
/* ============================= */
.stButton>button {
    background-color: #F5C32C;
    color: black;
    border-radius: 8px;
    border: none;
}

.stButton>button:hover {
    background-color: #e0b12c;
}

/* ============================= */
/* DIVIDER */
/* ============================= */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(to right, #0E6F66, #F5C32C);
    margin: 25px 0;
}

</style>
""", unsafe_allow_html=True)

# ======================
# HÀM KPI CARD
# ======================
def kpi_card(title, value):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# ======================
# HEADER (LOGO + TITLE)
# ======================
col_logo, col_title = st.columns([1, 6])

with col_logo:
    st.image("logo_bidv2.png", width=120)

with col_title:
    st.markdown(
        '<div class="main-title">Dashboard Khách Hàng BIDV</div>',
        unsafe_allow_html=True
    )

# ======================
# MENU NGANG
# ======================
menu = option_menu(
    None,
    ["📊  Tổng quan", "🎯  HDVKKH_BQ", "💰  HDVCKH_CK", "🏦  DNCK", "📈  Trung bình DV/người", "👨‍💼  Cán bộ", "🏢  Phòng ban", "👶  Độ tuổi", "💼  Nghề nghiệp"],
    
    orientation="horizontal",
    styles={
        "container": {
            "background-color": "#0E6F66",
            "padding": "8px",
            "border-radius": "12px"
        },
        "nav-link": {
            "color": "white",
            "font-size": "15px",
            "text-align": "center",
            "font-family": "Arial, sans-serif",
            "font-weight": "500",
            "padding": "10px 14px",
            "white-space": "nowrap",
        },
        "nav-link-selected": {
            "background-color": "#F5C32C",
            "color": "black",
            "font-family": "Arial, sans-serif",
            "font-weight": "600",
            "border-radius": "10px",
        },
    }
)
# =========================
# LOAD DATA FUNCTION (PHẢI ĐẶT LÊN TRÊN)
# =========================
@st.cache_data
def load_data(file):

    try:
        df = pd.read_excel(file).copy()
    except:
        try:
            df = pd.read_excel(file, engine="pyxlsb").copy()
        except:
            try:
                df = pd.read_csv(file).copy()
            except:
                return None
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df


# ======================
# LOAD / SHARE DATA (FAST VERSION)
# ======================
file_path = "saved_data.xlsx"

st.markdown("---")

col1, col2 = st.columns([3,1])

with col1:
    uploaded_file = st.file_uploader("📂 Upload file dữ liệu")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if "df" in st.session_state:
        if st.button("🗑️ Tắt dữ liệu"):
            if os.path.exists(file_path):
                os.remove(file_path)

            st.session_state.pop("df", None)
            st.warning("⚠️ Đã tắt dữ liệu")
            st.rerun()



# ======================
# SAVE + LOAD (PRO MAX)
# ======================
if uploaded_file is not None:

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 🔥 load 1 lần duy nhất
    st.session_state.df = load_data(uploaded_file)

    st.success("✅ Đã upload dữ liệu")


# ======================
# GET DATA (KHÔNG LOAD LẠI)
# ======================
if "df" not in st.session_state:

    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.session_state.df = load_data(f)
    else:
        st.info("📌 Chưa có dữ liệu. Vui lòng upload file.")
        st.stop()

df = st.session_state.df

# ======================
# ⚡ TỐI ƯU DATA (SIÊU QUAN TRỌNG)
# ======================
if "df_processed" not in st.session_state:

    df_temp = df.copy()

    # chuẩn hóa status 1 lần
    col_status = find_column(df_temp, ["TRANGTHAI", "STATUS"])
    if col_status:
        df_temp[col_status] = df_temp[col_status].astype("string").str.strip()

    # chuyển numeric 1 lần
    numeric_cols = ["TOTAL_SPDV", "HDVKKH_BQ", "HDVCKH_CK", "DNCK"]

    for col in numeric_cols:
        if col in df_temp.columns:
            df_temp[col] = pd.to_numeric(df_temp[col], errors="coerce")

    st.session_state.df_processed = df_temp

df = st.session_state.df_processed

    





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


    
    

# ======================
# 📊 TỔNG QUAN
# ======================
if menu == "📊  Tổng quan":

    st.markdown(
        '<div class="section-title">📌 Tổng quan khách hàng</div>',
        unsafe_allow_html=True
    )

    total = len(df)
    active = df[col_status].isin(["Active", "New"]).sum()
    
    frozen = (df[col_status] == "Frozen").sum()
    dormant = (df[col_status] == "Dormant").sum()
    nan_count = df[col_status].isna().sum()

    # ======================
    # KPI
    # ======================
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        kpi_card("👥 Tổng KH", f"{total:,}")
    with c2:
        kpi_card("🔥 Active", f"{active:,}")
    with c3:
        kpi_card("❄️ Frozen", f"{frozen:,}")
    with c4:
        kpi_card("😴 Dormant", f"{dormant:,}")
    with c5:
        kpi_card("❓ NaN", f"{nan_count:,}")

    # ======================
    # 🎯 BIỂU ĐỒ TRÒN XỊN
    # ======================
    
    st.markdown("### 📊 Tỷ lệ khách hàng")
    
    # 🔥 KHÔNG còn New
    labels = ["Active", "Frozen", "Dormant"]
    values = [active, frozen, dormant]
    
    # CHIA LAYOUT CHO ĐẸP (center)
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
    
            hole=0.55,
    
            # 🔥 chỉ highlight Active
            pull=[0.06, 0, 0],
    
            marker=dict(
                colors=[
                    "#0E6F66",  # xanh BIDV (Active)
                    "#5DADE2",  # xanh nhạt (Frozen)
                    "#EC7063"   # đỏ (Dormant)
                    
                ],
                line=dict(color="white", width=3)
            ),
    
            textinfo="percent",
            textfont=dict(size=18, color="white"),
    
            hovertemplate="<b>%{label}</b><br>Số KH: %{value:,}<br>Tỷ lệ: %{percent}<extra></extra>"
        )])
    
        fig.update_layout(
            showlegend=True,
    
            legend=dict(
                orientation="h",
                y=-0.1,
                x=0.5,
                xanchor="center"
            ),
    
            margin=dict(t=20, b=40, l=0, r=0),
    
            annotations=[dict(
                text="Tỉ lệ<br>khách hàng",
                x=0.5, y=0.5,
                font_size=14,
                showarrow=False
            )]
        )
    
        st.plotly_chart(fig, use_container_width=True)

# =========================
# 2. CHĂM SÓC KHÁCH HÀNG
# =========================
elif menu == "🎯  HDVKKH_BQ":

    st.markdown(
        '<div class="section-title">🎯 Phân loại theo HDVKKH_BQ</div>',
        unsafe_allow_html=True
    )

    df_cs = df[df[col_status].isin(["Active", "New"])].copy()

    col_hdv = "HDVKKH_BQ"

    if col_hdv not in df_cs.columns:
        st.error("❌ Không tìm thấy cột HDVKKH_BQ")
        st.stop()

    df_cs[col_hdv] = pd.to_numeric(df_cs[col_hdv], errors="coerce")

    # =========================
    # TÍNH SỐ LIỆU
    # =========================
    duoi_5 = (df_cs[col_hdv] <= 5_000_000).sum()
    tu_5_20 = ((df_cs[col_hdv] > 5_000_000) & (df_cs[col_hdv] <= 20_000_000)).sum()
    tu_20_50 = ((df_cs[col_hdv] > 20_000_000) & (df_cs[col_hdv] <= 50_000_000)).sum()
    tren_50 = (df_cs[col_hdv] > 50_000_000).sum()

    # =========================
    # TÍNH TỔNG HDV
    # =========================
    tong_hdv = df_cs[col_hdv].sum()
    
    hdv_duoi_5 = df_cs[df_cs[col_hdv] <= 5_000_000][col_hdv].sum()
    hdv_5_20 = df_cs[(df_cs[col_hdv] > 5_000_000) & (df_cs[col_hdv] <= 20_000_000)][col_hdv].sum()
    hdv_20_50 = df_cs[(df_cs[col_hdv] > 20_000_000) & (df_cs[col_hdv] <= 50_000_000)][col_hdv].sum()
    hdv_tren_50 = df_cs[df_cs[col_hdv] > 50_000_000][col_hdv].sum()

    # =========================
    # KPI CARD ĐẸP
    # =========================
    st.markdown("### 📊 Phân nhóm khách hàng")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card("💚 < 5TR", f"{duoi_5:,}")
    with c2:
        kpi_card("💰 5 - 20TR", f"{tu_5_20:,}")
    with c3:
        kpi_card("🏆 20 - 50TR", f"{tu_20_50:,}")
    with c4:
        kpi_card("🔥 > 50TR", f"{tren_50:,}")

    # =========================
    # KPI TỔNG HDV (MỚI)
    # =========================
    st.markdown("### 💰 Tổng HDVKKH_BQ")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        kpi_card("🏦 Tổng", f"{tong_hdv:,.0f}")
    
    with c2:
        kpi_card("💚 <5TR", f"{hdv_duoi_5:,.0f}")
    
    with c3:
        kpi_card("💰 5-20TR", f"{hdv_5_20:,.0f}")
    
    with c4:
        kpi_card("🏆 20-50TR", f"{hdv_20_50:,.0f}")
    
    with c5:
        kpi_card("🔥 >50TR", f"{hdv_tren_50:,.0f}")

    # =========================
    # SELECT BOX
    # =========================
    option = st.selectbox(
        "📌 Chọn nhóm khách hàng",
        ["<5TR", "5-20TR", "20-50TR", ">50TR"]
    )

    df_show = df_cs.copy()

    if option == "<5TR":
        df_show = df_cs[df_cs[col_hdv] <= 5_000_000]
    elif option == "5-20TR":
        df_show = df_cs[(df_cs[col_hdv] > 5_000_000) & (df_cs[col_hdv] <= 20_000_000)]
    elif option == "20-50TR":
        df_show = df_cs[(df_cs[col_hdv] > 20_000_000) & (df_cs[col_hdv] <= 50_000_000)]
    else:
        df_show = df_cs[df_cs[col_hdv] > 50_000_000]

    # =========================
    # KPI KẾT QUẢ
    # =========================
    st.markdown("### 📊 Kết quả")

    col_kq1, col_kq2 = st.columns([1, 2])

    with col_kq1:
        kpi_card("👥 Số khách", f"{len(df_show):,}")

    with col_kq2:
        st.success(f"👉 Nhóm **{option}** có **{len(df_show):,} khách hàng**")

    # =========================
    # BIỂU ĐỒ MINI (ĐẸP)
    # =========================
    import plotly.express as px

    df_chart = pd.DataFrame({
        "Nhóm": ["<5TR", "5-20TR", "20-50TR", ">50TR"],
        "Số KH": [duoi_5, tu_5_20, tu_20_50, tren_50]
    })

    fig = px.bar(
        df_chart,
        x="Nhóm",
        y="Số KH",
        color="Nhóm",
        text="Số KH"
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(t=30, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # DATA TABLE (GIỮ NGUYÊN)
    # =========================
    st.markdown("### 📋 Danh sách khách hàng")

    st.dataframe(
        format_dataframe(df_show, col_customer, col_manager),
        use_container_width=True,
        height=600,
        hide_index=True
    )
# =========================
# 3. HDVCKH_CK
# =========================
elif menu == "💰  HDVCKH_CK":

    st.markdown(
        '<div class="section-title">💰 Phân loại theo HDVCKH_CK</div>',
        unsafe_allow_html=True
    )

    # 🔥 chỉ lấy Active + New (giống toàn hệ thống của bạn)
    df_ck = df[df[col_status].isin(["Active", "New"])].copy()

    col_ck = "HDVCKH_CK"

    # kiểm tra cột
    if col_ck not in df_ck.columns:
        st.error("❌ Không tìm thấy cột HDVCKH_CK")
        st.stop()

    # chuyển sang số
    df_ck[col_ck] = pd.to_numeric(df_ck[col_ck], errors="coerce")

    # lọc khách có giá trị (khách cần chăm)
    df_ck = df_ck[df_ck[col_ck] > 0]

    # sort tiền lớn lên trên
    df_ck = df_ck.sort_values(by=col_ck, ascending=False)

    # =========================
    # KPI ĐẸP (BIDV)
    # =========================
    tong_hdv_ck = df_ck[col_ck].sum()
    
    c1, c2 = st.columns(2)
    
    with c1:
        kpi_card("👥 Số khách cần chăm", f"{len(df_ck):,}")
    
    with c2:
        kpi_card("💰 Tổng HDVCKH_CK", f"{tong_hdv_ck:,.0f}")

    # hiển thị
    st.dataframe(
        format_dataframe(df_ck, col_customer, col_manager),
        use_container_width=True,
        height=600,
        hide_index=True
    )

# =========================
# 4. DNCK
# =========================
elif menu == "🏦  DNCK":

    st.markdown(
        '<div class="section-title">🏦 Phân loại theo DNCK</div>',
        unsafe_allow_html=True
    )

    col_dnck = "DNCK"

# kiểm tra cột
if col_dnck not in df.columns:
    st.error("❌ Không tìm thấy cột DNCK")
    st.write("Các cột hiện có:", df.columns)
    st.stop()

# 🔥 1. Active + New
df_dnck = df[df[col_status].isin(["Active", "New"])].copy()

# 🔥 2. CONVERT SỐ (QUAN TRỌNG - PHẢI ĐẶT TRƯỚC)
df_dnck[col_dnck] = pd.to_numeric(df_dnck[col_dnck], errors="coerce")

# 🔥 3. GIỮ KHÁCH CÓ DNCK
df_dnck = df_dnck[df_dnck[col_dnck] > 0]

# 🔥 4. SORT
df_dnck = df_dnck.sort_values(by=col_dnck, ascending=False)

# =========================
# KPI ĐẸP (BIDV)
# =========================
tong_dnck = df_dnck[col_dnck].fillna(0).sum()

c1, c2 = st.columns(2)

with c1:
    kpi_card("🏦 Số khách DNCK", f"{len(df_dnck):,}")

with c2:
    kpi_card("💰 Tổng DNCK (VND)", f"{tong_dnck:,.0f}")

# =========================
# DATA TABLE
# =========================
st.dataframe(
    format_dataframe(df_dnck, col_customer, col_manager),
    use_container_width=True,
    height=600,
    hide_index=True
)

# =========================
# 5. TRUNG BÌNH DV / NGƯỜI
# =========================
elif menu == "📈  Trung bình DV/người":

    st.markdown(
        '<div class="section-title">📈 Phân loại theo số dịch vụ / khách hàng</div>',
        unsafe_allow_html=True
    )

    col_spdv = "TOTAL_SPDV"

    if col_spdv not in df.columns:
        st.error("❌ Không tìm thấy cột TOTAL_SPDV")
        st.stop()

    # 🔥 chỉ lấy Active + New
    df_kh = df[df[col_status].isin(["Active", "New"])].copy()

    # chuyển sang số
    df_kh[col_spdv] = pd.to_numeric(df_kh[col_spdv], errors="coerce")

    # =========================
    # KPI
    # =========================
    total_spdv = df_kh[col_spdv].sum()
    total_kh = len(df_kh)
    avg_spdv = total_spdv / total_kh if total_kh > 0 else 0

    c1, c2, c3 = st.columns(3)

    c1.metric("💳 Tổng DV", f"{int(total_spdv):,}")
    c2.metric("👥 Số KH", f"{total_kh:,}")
    c3.metric("📊 TB DV / KH", f"{avg_spdv:.2f}")

    # =========================
    # 🔥 PHÂN BỐ SỐ DỊCH VỤ
    # =========================
    st.markdown(
        '<div class="section-title">📊 Phân bố số dịch vụ</div>',
        unsafe_allow_html=True
    )

    df_dist = df_kh.dropna(subset=[col_spdv])

    dv_dist = (
        df_dist.groupby(col_spdv)
        .size()
        .reset_index(name="Số khách")
        .sort_values(by=col_spdv)
    )

    dv_dist.columns = ["Số dịch vụ", "Số khách"]

    # format đẹp
    dv_dist["Số khách"] = dv_dist["Số khách"].apply(lambda x: f"{x:,}")

    # =========================
    # HIỂN THỊ 2 CỘT (TABLE + CHART)
    # =========================
    col1, col2 = st.columns([1, 2])

    # ===== TABLE =====
    with col1:
        
        st.dataframe(
            dv_dist,
            use_container_width=True,
            hide_index=True
        )

    # ===== CHART =====
    with col2:
        import plotly.express as px

        dv_dist_chart = dv_dist.copy()
        dv_dist_chart["Số khách"] = dv_dist_chart["Số khách"].str.replace(",", "").astype(int)

        fig = px.bar(
            dv_dist_chart,
            x="Số dịch vụ",
            y="Số khách",
            text="Số khách",
            color="Số dịch vụ",
            color_continuous_scale="Teal"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            title="Phân bố số dịch vụ / khách hàng",
            xaxis_title="Số dịch vụ",
            yaxis_title="Số khách",
            showlegend=False,
            height=400,
            margin=dict(l=10, r=10, t=40, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)
# =========================
# THEO CÁN BỘ QUẢN LÝ
# =========================
elif menu == "👨‍💼  Cán bộ":

    st.markdown(
        '<div class="section-title">👨‍💼 Phân loại theo cán bộ quản lý</div>',
        unsafe_allow_html=True
    )

    # =========================
    # DATA
    # =========================
    df_all = df.copy()
    df_kh = df[df[col_status].isin(["Active", "New"])].copy()

    # kiểm tra cột
    required_cols = ["CANBO_QUANLY", "HO VA TEN", "TOTAL_SPDV", "HDVKKH_BQ"]

    for col in required_cols:
        if col not in df.columns:
            st.error(f"❌ Thiếu cột: {col}")
            st.stop()

    # chuyển số
    df_kh["TOTAL_SPDV"] = pd.to_numeric(df_kh["TOTAL_SPDV"], errors="coerce")
    df_kh["HDVKKH_BQ"] = pd.to_numeric(df_kh["HDVKKH_BQ"], errors="coerce")

    # =========================
    # GROUP ALL KH
    # =========================
    group_all = df_all.groupby(["CANBO_QUANLY", "HO VA TEN"]).agg(
        tong_kh_all=("CANBO_QUANLY", "count")
    ).reset_index()

    # =========================
    # GROUP ACTIVE + NEW
    # =========================
    group_active = df_kh.groupby(["CANBO_QUANLY", "HO VA TEN"]).agg(
        tong_kh_active=("CANBO_QUANLY", "count"),
        tong_spdv=("TOTAL_SPDV", "sum"),
        tong_hdv=("HDVKKH_BQ", "sum")
    ).reset_index()

    # =========================
    # MERGE
    # =========================
    group_cbql = pd.merge(
        group_all,
        group_active,
        on=["CANBO_QUANLY", "HO VA TEN"],
        how="left"
    ).fillna(0)

    # =========================
    # KPI
    # =========================
    group_cbql["dv_trung_binh"] = group_cbql["tong_spdv"] / group_cbql["tong_kh_active"].replace(0, 1)

    # =========================
    # FORMAT
    # =========================
    group_cbql["Tổng KH"] = group_cbql["tong_kh_all"].apply(lambda x: f"{int(x):,}")
    group_cbql["KH Active+New"] = group_cbql["tong_kh_active"].apply(lambda x: f"{int(x):,}")
    group_cbql["Tổng DV"] = group_cbql["tong_spdv"].apply(lambda x: f"{int(x):,}")
    group_cbql["Tổng HDV"] = group_cbql["tong_hdv"].apply(lambda x: f"{int(x):,}")
    group_cbql["DV/KH"] = group_cbql["dv_trung_binh"].apply(lambda x: f"{x:.2f}")

    # =========================
    # HIỂN THỊ BẢNG TỔNG
    # =========================
    group_cbql = group_cbql.sort_values(by="tong_kh_all", ascending=False)

    st.dataframe(
        group_cbql[[
            "CANBO_QUANLY",
            "HO VA TEN",
            "Tổng KH",
            "KH Active+New",
            "Tổng DV",
            "Tổng HDV",
            "DV/KH"
        ]],
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # 🔥 CHI TIẾT KHÁCH THEO CÁN BỘ
    # =========================
    st.markdown("---")
    st.markdown(
        '<div class="section-title">🔍 Chi tiết khách hàng theo cán bộ</div>',
        unsafe_allow_html=True
    )

    # danh sách cán bộ
    list_cb = group_cbql["HO VA TEN"].unique()

    selected_cb = st.selectbox(
        "Chọn cán bộ quản lý",
        list_cb
    )

    # lọc khách
    df_detail = df[
        (df["HO VA TEN"] == selected_cb) &
        (df[col_status].isin(["Active", "New"]))
    ].copy()

    # KPI nhỏ
    st.metric("Số khách Active + New", f"{len(df_detail):,}")

    # hiển thị bảng chi tiết
    st.dataframe(
        format_dataframe(df_detail, col_customer, col_manager),
        use_container_width=True,
        height=500,
        hide_index=True
    )
# =========================
# THEO PHÒNG BAN
# =========================
elif menu == "🏢  Phòng ban":

    st.markdown(
        '<div class="section-title">🏢 Phân loại theo phòng ban</div>',
        unsafe_allow_html=True
    )

    # =========================
    # DATA
    # =========================
    df_all = df.copy()
    df_kh = df[df[col_status].isin(["Active", "New"])].copy()

    # kiểm tra cột
    if "PHONG BAN" not in df.columns:
        st.error("❌ Không tìm thấy cột PHONG BAN")
        st.stop()

    # chuyển số
    df_kh["TOTAL_SPDV"] = pd.to_numeric(df_kh["TOTAL_SPDV"], errors="coerce")
    df_kh["HDVKKH_BQ"] = pd.to_numeric(df_kh["HDVKKH_BQ"], errors="coerce")

    # =========================
    # GROUP ALL KH
    # =========================
    group_all = df_all.groupby("PHONG BAN").agg(
        tong_kh_all=("PHONG BAN", "count")
    ).reset_index()

    # =========================
    # GROUP ACTIVE + NEW
    # =========================
    group_active = df_kh.groupby("PHONG BAN").agg(
        tong_kh_active=("PHONG BAN", "count"),
        tong_spdv=("TOTAL_SPDV", "sum"),
        tong_hdv=("HDVKKH_BQ", "sum")
    ).reset_index()

    # =========================
    # MERGE
    # =========================
    group_pb = pd.merge(
        group_all,
        group_active,
        on="PHONG BAN",
        how="left"
    ).fillna(0)

    # =========================
    # KPI
    # =========================
    group_pb["dv_trung_binh"] = group_pb["tong_spdv"] / group_pb["tong_kh_active"].replace(0, 1)

    # =========================
    # FORMAT
    # =========================
    group_pb["Tổng KH"] = group_pb["tong_kh_all"].apply(lambda x: f"{int(x):,}")
    group_pb["KH Active+New"] = group_pb["tong_kh_active"].apply(lambda x: f"{int(x):,}")
    group_pb["Tổng DV"] = group_pb["tong_spdv"].apply(lambda x: f"{int(x):,}")
    group_pb["Tổng HDV"] = group_pb["tong_hdv"].apply(lambda x: f"{int(x):,}")
    group_pb["DV/KH"] = group_pb["dv_trung_binh"].apply(lambda x: f"{x:.2f}")

    # =========================
    # SORT
    # =========================
    group_pb = group_pb.sort_values(by="tong_kh_all", ascending=False)

    # =========================
    # HIỂN THỊ
    # =========================
    st.dataframe(
        group_pb[[
            "PHONG BAN",
            "Tổng KH",
            "KH Active+New",
            "Tổng DV",
            "Tổng HDV",
            "DV/KH"
        ]],
        use_container_width=True,
        hide_index=True
    ) 
elif menu == "👶  Độ tuổi":

    st.markdown(
        '<div class="section-title">👶 Phân loại theo độ tuổi</div>',
        unsafe_allow_html=True
    )

    # chỉ lấy Active + New
    df_kh = df[df[col_status].isin(["Active", "New"])].copy()

    # tìm cột tuổi
    col_age = "NAM SINH"
    for col in df.columns:
        if "TUOI" in col.upper() or "AGE" in col.upper():
            col_age = col
            break

    if col_age is None:
        st.error("❌ Không tìm thấy cột tuổi")
        st.stop()

    df_kh[col_age] = pd.to_numeric(df_kh[col_age], errors="coerce")

    # phân nhóm tuổi
    def age_group(x):
        if pd.isna(x):
            return "Không rõ"
        elif x < 25:
            return "<25"
        elif x < 35:
            return "25-34"
        elif x < 45:
            return "35-44"
        elif x < 60:
            return "45-59"
        else:
            return "60+"

    df_kh["AGE_GROUP"] = df_kh[col_age].apply(age_group)

    result = df_kh["AGE_GROUP"].value_counts().reset_index()
    result.columns = ["Nhóm tuổi", "Số KH"]

    result["Số KH"] = result["Số KH"].apply(lambda x: f"{x:,}")

    st.dataframe(result, use_container_width=True, hide_index=True)

elif menu == "💼  Nghề nghiệp":

    st.markdown(
        '<div class="section-title">💼 Phân loại theo nghề nghiệp</div>',
        unsafe_allow_html=True
    )

    df_kh = df[df[col_status].isin(["Active", "New"])].copy()

    # tìm cột nghề nghiệp
    col_job = None
    for col in df.columns:
        if "NGHE" in col.upper() or "JOB" in col.upper():
            col_job = col
            break

    if col_job is None:
        st.error("❌ Không tìm thấy cột nghề nghiệp")
        st.stop()

    result = df_kh[col_job].value_counts().reset_index()
    result.columns = ["Nghề nghiệp", "Số KH"]

    result["Số KH"] = result["Số KH"].apply(lambda x: f"{x:,}")

    st.dataframe(result, use_container_width=True, hide_index=True)
else:
    st.info("👉 Upload file để bắt đầu")
