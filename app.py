import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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

#logo
col_logo, col_title = st.columns([1.2, 5.8])

with col_logo:
    st.image("logo_bidv3.png", width=160)

    st.markdown(
        """
        <div style="
            margin-top:-32px;
            margin-left:11px;
            font-size:18px;   /* 🔥 tăng size */
            color:#0E6F66;
            font-weight:600;
            width:160px;      /* 🔥 ép chiều ngang theo logo */
            text-align:justify;
        ">
            Chi nhánh Hà Tĩnh
        </div>
        """,
        unsafe_allow_html=True
    )
with col_title:
    st.markdown(
        '<div style="font-size:32px;font-weight:700;color:#0E6F66;margin-top:10px">'
        'Báo cáo tổng quan nền khách hàng mass tại chi nhánh'
        '</div>',
        unsafe_allow_html=True
    )
def create_pdf_report(total, active, frozen, dormant, chart_bytes):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # ======================
    # 🔥 FONT TIẾNG VIỆT
    # ======================
    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name='Title',
        fontName='DejaVu',
        fontSize=18,
        leading=22,
        alignment=1,  # center
        textColor=colors.HexColor("#0E6F66"),
        spaceAfter=10
    )

    normal_style = ParagraphStyle(
        name='Normal',
        fontName='DejaVu',
        fontSize=11,
        leading=14
    )

    # ======================
    # 🏦 LOGO
    # ======================
    try:
        logo = Image("logo_bidv3.png", width=120, height=40)
        elements.append(logo)
    except:
        pass

    elements.append(Spacer(1, 10))

    # ======================
    # 📌 TITLE
    # ======================
    elements.append(Paragraph(
        "BÁO CÁO TỔNG QUAN KHÁCH HÀNG",
        title_style
    ))

    elements.append(Paragraph(
        "Chi nhánh Hà Tĩnh",
        normal_style
    ))

    elements.append(Spacer(1, 15))

    # ======================
    # 📊 KPI TABLE
    # ======================
    data = [
        ["Tổng KH", f"{total:,}"],
        ["Active", f"{active:,}"],
        ["Frozen", f"{frozen:,}"],
        ["Dormant", f"{dormant:,}"]
    ]

    table = Table(data, colWidths=[120, 120])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0E6F66")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]))

    elements.append(table)

    elements.append(Spacer(1, 20))

    # ======================
    # 📈 CHART
    # ======================
    elements.append(Paragraph("Tỷ lệ khách hàng", title_style))

    img = io.BytesIO(chart_bytes)
    elements.append(Image(img, width=350, height=220))

    elements.append(Spacer(1, 20))

    # ======================
    # 📌 NHẬN XÉT
    # ======================
    elements.append(Paragraph("Nhận xét:", title_style))

    elements.append(Paragraph(
        "Khách hàng Active chiếm tỷ trọng cao, cần tiếp tục duy trì và phát triển.",
        normal_style
    ))

    # ======================
    # BUILD
    # ======================
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf

# ======================
# MENU NGANG
# ======================
menu = option_menu(
    None,
    ["📊  Tổng quan", "🎯  HDVKKH_BQ", "💰  HDVCKH_CK", "🏦  DNCK", "📈  Trung bình DV/người", "👨‍💼  Cán bộ", "🏢  Phòng ban", "👶  Độ tuổi", "💼  Nghề nghiệp", "📌  Đo luong"],
    
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

    # ======================
    # SAVE FILE
    # ======================
    if uploaded_file is not None:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        

with col2:
    st.markdown("<br>", unsafe_allow_html=True)



# ======================
# SAVE + LOAD (PRO MAX)
# ======================
if uploaded_file is not None:

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 🔥 load 1 lần duy nhất
    st.session_state.df = load_data(uploaded_file)

    


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
        df_temp[col_status] = df_temp[col_status].fillna("Dormant")
        df_temp[col_status] = df_temp[col_status].replace("", "Dormant")
        df_temp[col_status] = df_temp[col_status].replace("None", "Dormant")
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

    # ======================
    # CHUẨN HÓA STATUS
    # ======================
    status_series = df[col_status]

    total = len(df)
    active = status_series.isin(["Active", "New"]).sum()
    frozen = (status_series == "Frozen").sum()
    dormant = total - active - frozen

    # ======================
    # KPI CHÍNH
    # ======================
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card("👥 Tổng KH", f"{total:,}")

    with c2:
        kpi_card("🔥 Active", f"{active:,}")

    with c3:
        kpi_card("❄️ Frozen", f"{frozen:,}")

    with c4:
        kpi_card("😴 Dormant", f"{dormant:,}")

    # ======================
    # 🔥 KPI BỔ SUNG (MỚI)
    # ======================
    st.markdown("### 📊 Tổng hợp chỉ tiêu")

    # ====== XỬ LÝ CỘT ======
    col_hdv_bq = "HDVKKH_BQ"
    col_hdv_ck = "HDVCKH_CK"
    col_dnck = "DNCK"
    

    # convert số an toàn
    for col in [col_hdv_bq, col_hdv_ck, col_dnck]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ====== TÍNH TOÁN ======
    tong_hdv_bq = df[col_hdv_bq].fillna(0).sum() if col_hdv_bq in df else 0
    tong_hdv_ck = df[col_hdv_ck].fillna(0).sum() if col_hdv_ck in df else 0
    tong_dnck = df[col_dnck].fillna(0).sum() if col_dnck in df else 0
    

    

    # số phòng ban
    so_phong_ban = df["PHONG BAN"].nunique() if "PHONG BAN" in df.columns else 0

    # ====== HIỂN THỊ ======
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card("🏢 Số phòng ban", f"{so_phong_ban:,}")

    with c2:
        kpi_card("💰 HDVKKH_BQ", f"{tong_hdv_bq:,.0f}")

    with c3:
        kpi_card("💰 HDVCKH_CK", f"{tong_hdv_ck:,.0f}")

    with c4:
        kpi_card("🏦 DNCK", f"{tong_dnck:,.0f}")

    

    # ======================
    # 🎯 BIỂU ĐỒ TRÒN
    # ======================
    st.markdown("### 📊 Tỷ lệ khách hàng")
    
    labels = ["Active", "Frozen", "Dormant"]
    values = [active, frozen, dormant]
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            pull=[0.06, 0, 0],
            marker=dict(
                chart_colors=["#0E6F66", "#5DADE2", "#EC7063"],
                line=dict(color="white", width=3)
            ),
            textinfo="percent",
            texttemplate="%{percent:.2%}",
            textfont=dict(size=18, color="white"),
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
    
    # ======================
    # 🔥 TẠO ẢNH (KHÔNG DÙNG PLOTLY)
    # ======================
    import matplotlib.pyplot as plt
    import io
    
    fig_mpl, ax = plt.subplots()
    
    chart_colors = ["#0E6F66", "#5DADE2", "#EC7063"]
    
    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors)
    ax.set_title("Tỷ lệ khách hàng")
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    
    img_bytes = buf.getvalue()
    
    # ======================
    # 📄 TẠO PDF
    # ======================
    pdf_file = create_pdf_report(
        total=total,
        active=active,
        frozen=frozen,
        dormant=dormant,
        chart_bytes=img_bytes
    )
    
    st.download_button(
        label="📥 Tải báo cáo PDF",
        data=pdf_file,
        file_name="bao_cao.pdf",
        mime="application/pdf"
    )

# =========================
# 2. CHĂM SÓC KHÁCH HÀNG
# =========================
elif menu == "🎯  HDVKKH_BQ":
    
    st.markdown(
        '<div class="section-title">🎯 Tổng quan HDVKKH_BQ</div>',
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
    duoi_5 = ((df_cs[col_hdv] <= 5_000_000) | (df_cs[col_hdv].isna())).sum()
    tu_5_20 = ((df_cs[col_hdv] > 5_000_000) & (df_cs[col_hdv] <= 20_000_000)).sum()
    tu_20_50 = ((df_cs[col_hdv] > 20_000_000) & (df_cs[col_hdv] <= 50_000_000)).sum()
    tren_50 = (df_cs[col_hdv] > 50_000_000).sum()

    # =========================
    # TÍNH TỔNG HDV
    # =========================
    tong_hdv = df_cs[col_hdv].sum()
    
    hdv_duoi_5 = df_cs[
        (df_cs[col_hdv] <= 5_000_000) | (df_cs[col_hdv].isna())
    ][col_hdv].sum()
    hdv_5_20 = df_cs[(df_cs[col_hdv] > 5_000_000) & (df_cs[col_hdv] <= 20_000_000)][col_hdv].sum()
    hdv_20_50 = df_cs[(df_cs[col_hdv] > 20_000_000) & (df_cs[col_hdv] <= 50_000_000)][col_hdv].sum()
    hdv_tren_50 = df_cs[df_cs[col_hdv] > 50_000_000][col_hdv].sum()

    # =========================
    # KPI CARD GỘP (MỚI)
    # =========================
    

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        kpi_card("🏦 Tổng",
            f"{len(df_cs):,}<br><span style='font-size:22px;font-weight:bold;color:#E6A700'>{tong_hdv:,.0f}</span>"
        )

    with c2:
        kpi_card("💚 <5TR",
            f"{duoi_5:,}<br><span style='font-size:22px;font-weight:bold;color:#E6A700'>{hdv_duoi_5:,.0f}</span>"
        )
    
    with c3:
        kpi_card("💰 5-20TR",
            f"{tu_5_20:,}<br><span style='font-size:22px;font-weight:bold;color:#E6A700'>{hdv_5_20:,.0f}</span>"
        )
    
    with c4:
        kpi_card("🏆 20-50TR",
            f"{tu_20_50:,}<br><span style='font-size:22px;font-weight:bold;color:#E6A700'>{hdv_20_50:,.0f}</span>"
        )
    
    with c5:
        kpi_card("🔥 >50TR",
            f"{tren_50:,}<br><span style='font-size:22px;font-weight:bold;color:#E6A700'>{hdv_tren_50:,.0f}</span>"
        )
    
    


    
    st.markdown(
        '<div class="section-title">🎯 Phân loại HDVKKH_BQ theo phòng</div>',
        unsafe_allow_html=True
    )

    df_cs = df[df[col_status].isin(["Active", "New"])].copy()

    col_hdv = "HDVKKH_BQ"

    if col_hdv not in df_cs.columns:
        st.error("❌ Không tìm thấy cột HDVKKH_BQ")
        st.stop()

    df_cs[col_hdv] = pd.to_numeric(df_cs[col_hdv], errors="coerce")

    # =========================
    # 🔥 CHỌN PHÒNG BAN (MỚI)
    # =========================
    if "PHONG BAN" not in df_cs.columns:
        st.error("❌ Không có cột PHONG BAN")
        st.stop()
    
    list_pb = sorted(
        df_cs["PHONG BAN"]
        .dropna()
        .astype(str)
        .loc[lambda x: ~x.str.startswith("0x")]
        .unique()
    )
    
    selected_pb = st.selectbox(
        "🏢 Chọn phòng ban",
        list_pb
    )
    
    # lọc theo phòng ban
    df_pb = df_cs[df_cs["PHONG BAN"] == selected_pb].copy()


    # =========================
    # 🔥 TỔNG TIỀN PHÒNG BAN
    # =========================
    tong_hdv_pb = df_pb[col_hdv].fillna(0).sum()

    
        

    # =========================
    # TÍNH SỐ LIỆU THEO PHÒNG
    # =========================
    duoi_5 = (df_pb[col_hdv] <= 5_000_000).sum()
    tu_5_20 = ((df_pb[col_hdv] > 5_000_000) & (df_pb[col_hdv] <= 20_000_000)).sum()
    tu_20_50 = ((df_pb[col_hdv] > 20_000_000) & (df_pb[col_hdv] <= 50_000_000)).sum()
    tren_50 = (df_pb[col_hdv] > 50_000_000).sum()

    hdv_duoi_5 = df_pb[df_pb[col_hdv] <= 5_000_000][col_hdv].sum()
    hdv_5_20 = df_pb[(df_pb[col_hdv] > 5_000_000) & (df_pb[col_hdv] <= 20_000_000)][col_hdv].sum()
    hdv_20_50 = df_pb[(df_pb[col_hdv] > 20_000_000) & (df_pb[col_hdv] <= 50_000_000)][col_hdv].sum()
    hdv_tren_50 = df_pb[df_pb[col_hdv] > 50_000_000][col_hdv].sum()

    # =========================
    # SELECT BOX NHÓM KH
    # =========================
    

    option = st.selectbox(
        "Chọn nhóm",
        ["Tổng", "<5TR", "5-20TR", "20-50TR", ">50TR"]
    )

    # =========================
    # FILTER DATA
    # =========================
    if option == "Tổng":
        df_show = df_pb.copy()
        tong_tien = tong_hdv_pb

    elif option == "<5TR":
        df_show = df_pb[df_pb[col_hdv] <= 5_000_000]
        tong_tien = hdv_duoi_5
    
    elif option == "5-20TR":
        df_show = df_pb[(df_pb[col_hdv] > 5_000_000) & (df_pb[col_hdv] <= 20_000_000)]
        tong_tien = hdv_5_20
    
    elif option == "20-50TR":
        df_show = df_pb[(df_pb[col_hdv] > 20_000_000) & (df_pb[col_hdv] <= 50_000_000)]
        tong_tien = hdv_20_50
    
    else:
        df_show = df_pb[df_pb[col_hdv] > 50_000_000]
        tong_tien = hdv_tren_50

    # =========================
    # KPI KẾT QUẢ (SỬA ĐẸP)
    # =========================
    st.markdown("### 📊 Kết quả")

    c1, c2 = st.columns(2)

    with c1:
        kpi_card("👥 Số khách", f"{len(df_show):,}")

    with c2:
        kpi_card(
            "💰 Tổng tiền",
            f"<span style='font-size:26px;font-weight:bold;color:#E6A700'>{tong_tien:,.0f}</span>"
        )

    

    
    # =========================
    # DATA TABLE
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

    with c1:
        kpi_card("💳 Tổng DV", f"{int(total_spdv):,}")
    
    with c2:
        kpi_card("👥 Số KH", f"{total_kh:,}")
    
    with c3:
        kpi_card("📊 TB DV / KH", f"{avg_spdv:.2f}")

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

    # =========================
    # CHECK CỘT
    # =========================
    required_cols = [
        "CANBO_QUANLY", 
        "HO VA TEN", 
        "TOTAL_SPDV", 
        "HDVKKH_BQ",
        "HDVCKH_CK",
        "DNCK"
    ]

    for col in required_cols:
        if col not in df.columns:
            st.error(f"❌ Thiếu cột: {col}")
            st.stop()

    # =========================
    # CHUYỂN SỐ
    # =========================
    numeric_cols = ["TOTAL_SPDV", "HDVKKH_BQ", "HDVCKH_CK", "DNCK"]

    for col in numeric_cols:
        df_kh[col] = pd.to_numeric(df_kh[col], errors="coerce").fillna(0)

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
        tong_hdv_bq=("HDVKKH_BQ", "sum"),
        tong_hdv_ck=("HDVCKH_CK", "sum"),
        tong_dnck=("DNCK", "sum")
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
    group_cbql["dv_trung_binh"] = (
        group_cbql["tong_spdv"] / group_cbql["tong_kh_active"].replace(0, 1)
    )

    # =========================
    # FORMAT HIỂN THỊ
    # =========================
    group_cbql["Tổng KH"] = group_cbql["tong_kh_all"].apply(lambda x: f"{int(x):,}")
    group_cbql["KH Active+New"] = group_cbql["tong_kh_active"].apply(lambda x: f"{int(x):,}")
    group_cbql["Tổng DV"] = group_cbql["tong_spdv"].apply(lambda x: f"{int(x):,}")

    group_cbql["HDVKKH_BQ"] = group_cbql["tong_hdv_bq"].apply(lambda x: f"{int(x):,}")
    group_cbql["HDVCKH_CK"] = group_cbql["tong_hdv_ck"].apply(lambda x: f"{int(x):,}")
    group_cbql["DNCK"] = group_cbql["tong_dnck"].apply(lambda x: f"{int(x):,}")

    group_cbql["DV/KH"] = group_cbql["dv_trung_binh"].apply(lambda x: f"{x:.2f}")

    # =========================
    # SORT
    # =========================
    group_cbql = group_cbql.sort_values(by="tong_kh_all", ascending=False)

    # =========================
    # HIỂN THỊ
    # =========================
    st.dataframe(
        group_cbql[[
            "CANBO_QUANLY",
            "HO VA TEN",
            "Tổng KH",
            "KH Active+New",
            "Tổng DV",
            "HDVKKH_BQ",
            "HDVCKH_CK",
            "DNCK",
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

    # =========================
    # 🔥 THÊM KPI THEO CÁN BỘ (MỚI)
    # =========================
    col_hdv_bq = "HDVKKH_BQ"
    col_hdv_ck = "HDVCKH_CK"
    col_dnck = "DNCK"
    col_spdv = "TOTAL_SPDV"

    # convert số
    df_detail[col_hdv_bq] = pd.to_numeric(df_detail[col_hdv_bq], errors="coerce")
    df_detail[col_hdv_ck] = pd.to_numeric(df_detail[col_hdv_ck], errors="coerce")
    df_detail[col_dnck] = pd.to_numeric(df_detail[col_dnck], errors="coerce")
    df_detail[col_spdv] = pd.to_numeric(df_detail[col_spdv], errors="coerce")

    # tính tổng
    tong_hdv_bq = df_detail[col_hdv_bq].fillna(0).sum()
    tong_hdv_ck = df_detail[col_hdv_ck].fillna(0).sum()
    tong_dnck = df_detail[col_dnck].fillna(0).sum()
    tong_spdv = df_detail[col_spdv].fillna(0).sum()

    # =========================
    # KPI ĐẸP BIDV
    # =========================
    st.markdown("### 📊 Tổng hợp theo cán bộ")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        kpi_card("👥 KH Active+New", f"{len(df_detail):,}")

    with c2:
        kpi_card("💰 HDVKKH_BQ", f"{tong_hdv_bq:,.0f}")

    with c3:
        kpi_card("💰 HDVCKH_CK", f"{tong_hdv_ck:,.0f}")

    with c4:
        kpi_card("🏦 DNCK", f"{tong_dnck:,.0f}")

    with c5:
        kpi_card("📊 Tổng DV", f"{tong_spdv:,.0f}")

    # =========================
    # TABLE
    # =========================
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

    # =========================
    # CHECK CỘT
    # =========================
    required_cols = [
        "PHONG BAN",
        "TOTAL_SPDV",
        "HDVKKH_BQ",
        "HDVCKH_CK",
        "DNCK"
    ]

    for col in required_cols:
        if col not in df.columns:
            st.error(f"❌ Thiếu cột: {col}")
            st.stop()

    # =========================
    # CHUYỂN SỐ
    # =========================
    numeric_cols = ["TOTAL_SPDV", "HDVKKH_BQ", "HDVCKH_CK", "DNCK"]

    for col in numeric_cols:
        df_kh[col] = pd.to_numeric(df_kh[col], errors="coerce").fillna(0)

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
        tong_hdv_bq=("HDVKKH_BQ", "sum"),
        tong_hdv_ck=("HDVCKH_CK", "sum"),
        tong_dnck=("DNCK", "sum")
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
    group_pb["dv_trung_binh"] = (
        group_pb["tong_spdv"] / group_pb["tong_kh_active"].replace(0, 1)
    )

    # =========================
    # FORMAT HIỂN THỊ
    # =========================
    group_pb["Tổng KH"] = group_pb["tong_kh_all"].apply(lambda x: f"{int(x):,}")
    group_pb["KH Active+New"] = group_pb["tong_kh_active"].apply(lambda x: f"{int(x):,}")
    group_pb["Tổng DV"] = group_pb["tong_spdv"].apply(lambda x: f"{int(x):,}")

    group_pb["HDVKKH_BQ"] = group_pb["tong_hdv_bq"].apply(lambda x: f"{int(x):,}")
    group_pb["HDVCKH_CK"] = group_pb["tong_hdv_ck"].apply(lambda x: f"{int(x):,}")
    group_pb["DNCK"] = group_pb["tong_dnck"].apply(lambda x: f"{int(x):,}")

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
            "HDVKKH_BQ",
            "HDVCKH_CK",
            "DNCK",
            "DV/KH"
        ]],
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # CHI TIẾT THEO PHÒNG BAN
    # =========================
    st.markdown("---")
    st.markdown(
        '<div class="section-title">🏢 Chi tiết theo phòng ban</div>',
        unsafe_allow_html=True
    )

    # chọn phòng ban
    list_pb = group_pb["PHONG BAN"].dropna().unique()

    selected_pb = st.selectbox(
        "Chọn phòng ban",
        list_pb
    )

    # lọc dữ liệu
    df_pb = df[
        (df["PHONG BAN"] == selected_pb) &
        (df[col_status].isin(["Active", "New"]))
    ].copy()

    # =========================
    # KPI THEO PHÒNG BAN
    # =========================
    col_hdv_bq = "HDVKKH_BQ"
    col_hdv_ck = "HDVCKH_CK"
    col_dnck = "DNCK"
    col_spdv = "TOTAL_SPDV"

    # convert số
    df_pb[col_hdv_bq] = pd.to_numeric(df_pb[col_hdv_bq], errors="coerce")
    df_pb[col_hdv_ck] = pd.to_numeric(df_pb[col_hdv_ck], errors="coerce")
    df_pb[col_dnck] = pd.to_numeric(df_pb[col_dnck], errors="coerce")
    df_pb[col_spdv] = pd.to_numeric(df_pb[col_spdv], errors="coerce")

    # tính tổng
    tong_hdv_bq = df_pb[col_hdv_bq].fillna(0).sum()
    tong_hdv_ck = df_pb[col_hdv_ck].fillna(0).sum()
    tong_dnck = df_pb[col_dnck].fillna(0).sum()
    tong_spdv = df_pb[col_spdv].fillna(0).sum()

    # =========================
    # KPI ĐẸP BIDV
    # =========================
    st.markdown("### 📊 Tổng hợp phòng ban")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        kpi_card("👥 KH Active+New", f"{len(df_pb):,}")

    with c2:
        kpi_card("💰 HDVKKH_BQ", f"{tong_hdv_bq:,.0f}")

    with c3:
        kpi_card("💰 HDVCKH_CK", f"{tong_hdv_ck:,.0f}")

    with c4:
        kpi_card("🏦 DNCK", f"{tong_dnck:,.0f}")

    with c5:
        kpi_card("📊 Tổng DV", f"{tong_spdv:,.0f}")

    # =========================
    # DANH SÁCH CÁN BỘ CỦA PHÒNG
    # =========================
    st.markdown("### 👨‍💼 Cán bộ thuộc phòng")

    list_cb_pb = sorted(df_pb["HO VA TEN"].dropna().astype(str).unique())
    so_cb = len(list_cb_pb)
    
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #ffffff, #f9fafb);
            padding: 18px;
            border-radius: 14px;
            box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
            font-size: 16px;
            line-height: 1.8;
            color: #0E6F66;
            margin-bottom: 16px;
        ">
            <b>👨‍💼 Tổng cán bộ: {so_cb}</b><br><br>
            {", ".join(list_cb_pb) if so_cb > 0 else "Không có cán bộ"}
        </div>
        """,
        unsafe_allow_html=True
    )
    # =========================
    # TABLE CHI TIẾT
    # =========================
    st.dataframe(
        format_dataframe(df_pb, col_customer, col_manager),
        use_container_width=True,
        height=500,
        hide_index=True
    )
    
elif menu == "👶  Độ tuổi":

    st.markdown(
        '<div class="section-title">👶 Chi tiết theo độ tuổi</div>',
        unsafe_allow_html=True
    )

    # =========================
    # DATA
    # =========================
    df_kh = df[df[col_status].isin(["Active", "New"])].copy()

    # =========================
    # 🔥 CHỌN PHÒNG BAN (GỘP VÀO ĐÂY)
    # =========================
    if "PHONG BAN" not in df_kh.columns:
        st.error("❌ Không có cột PHONG BAN")
        st.stop()

    df_kh["PHONG BAN"] = df_kh["PHONG BAN"].astype("string").str.strip()

    list_pb = sorted(
        df_kh["PHONG BAN"]
        .dropna()
        .loc[~df_kh["PHONG BAN"].str.contains("0x", na=False)]
        .unique()
    )

    col_f1, col_f2 = st.columns(2)

    with col_f1:
        selected_pb = st.selectbox(
            "🏢 Chọn phòng ban",
            ["Tất cả"] + list_pb
        )

    # lọc phòng ban
    if selected_pb != "Tất cả":
        df_kh = df_kh[df_kh["PHONG BAN"] == selected_pb]

    # =========================
    # TÌM CỘT TUỔI
    # =========================
    col_age = "NAM SINH"
    for col in df.columns:
        if "TUOI" in col.upper() or "AGE" in col.upper():
            col_age = col
            break

    if col_age is None:
        st.error("❌ Không tìm thấy cột tuổi")
        st.stop()

    df_kh[col_age] = pd.to_numeric(df_kh[col_age], errors="coerce")

    # =========================
    # PHÂN NHÓM TUỔI
    # =========================
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

    # =========================
    # 🔥 CHỌN NHÓM TUỔI (GỘP)
    # =========================
    list_age = df_kh["AGE_GROUP"].dropna().unique()

    with col_f2:
        selected_age = st.selectbox(
            "👶 Chọn nhóm tuổi",
            sorted(list_age)
        )

    # lọc dữ liệu
    df_age_detail = df_kh[df_kh["AGE_GROUP"] == selected_age].copy()

    # =========================
    # KPI
    # =========================
    col_hdv_bq = "HDVKKH_BQ"
    col_hdv_ck = "HDVCKH_CK"
    col_dnck = "DNCK"
    col_spdv = "TOTAL_SPDV"

    # convert số
    df_age_detail[col_hdv_bq] = pd.to_numeric(df_age_detail[col_hdv_bq], errors="coerce")
    df_age_detail[col_hdv_ck] = pd.to_numeric(df_age_detail[col_hdv_ck], errors="coerce")
    df_age_detail[col_dnck] = pd.to_numeric(df_age_detail[col_dnck], errors="coerce")
    df_age_detail[col_spdv] = pd.to_numeric(df_age_detail[col_spdv], errors="coerce")

    # tính tổng
    tong_hdv_bq = df_age_detail[col_hdv_bq].fillna(0).sum()
    tong_hdv_ck = df_age_detail[col_hdv_ck].fillna(0).sum()
    tong_dnck = df_age_detail[col_dnck].fillna(0).sum()
    tong_spdv = df_age_detail[col_spdv].fillna(0).sum()

    # =========================
    # KPI HIỂN THỊ
    # =========================
    st.markdown("### 📊 Tổng hợp")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        kpi_card("👥 KH Active+New", f"{len(df_age_detail):,}")

    with c2:
        kpi_card("💰 HDVKKH_BQ",
            f"<span style='font-size:22px;color:#0E6F66'>{tong_hdv_bq:,.0f}</span>"
        )

    with c3:
        kpi_card("💰 HDVCKH_CK",
            f"<span style='font-size:22px;color:#0E6F66'>{tong_hdv_ck:,.0f}</span>"
        )

    with c4:
        kpi_card("🏦 DNCK",
            f"<span style='font-size:22px;color:#0E6F66'>{tong_dnck:,.0f}</span>"
        )

    with c5:
        kpi_card("📊 Tổng DV", f"{tong_spdv:,.0f}")

    # =========================
    # TABLE CHI TIẾT
    # =========================
    st.dataframe(
        format_dataframe(df_age_detail, col_customer, col_manager),
        use_container_width=True,
        height=500,
        hide_index=True
    )

elif menu == "💼  Nghề nghiệp":

    st.markdown(
        '<div class="section-title">💼 Chi tiết theo nghề nghiệp</div>',
        unsafe_allow_html=True
    )

    # =========================
    # DATA
    # =========================
    df_kh = df[df[col_status].isin(["Active", "New"])].copy()

    # =========================
    # 🔥 CHỌN PHÒNG BAN (GIỐNG ĐỘ TUỔI)
    # =========================
    if "PHONG BAN" not in df_kh.columns:
        st.error("❌ Không có cột PHONG BAN")
        st.stop()

    list_pb = ["Tất cả"] + sorted(
        df_kh["PHONG BAN"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda x: ~x.str.contains("0x", na=False)]  # 🔥 bỏ 0x2a
        .unique()
    )

    selected_pb = st.selectbox(
        "🏢 Chọn phòng ban",
        list_pb
    )

    # lọc theo phòng ban
    if selected_pb != "Tất cả":
        df_kh = df_kh[df_kh["PHONG BAN"] == selected_pb]

    # =========================
    # TÌM CỘT NGHỀ NGHIỆP
    # =========================
    col_job = None
    for col in df.columns:
        if "NGHE" in col.upper() or "JOB" in col.upper():
            col_job = col
            break

    if col_job is None:
        st.error("❌ Không tìm thấy cột nghề nghiệp")
        st.stop()

    # =========================
    # CHỌN NGHỀ NGHIỆP
    # =========================
    list_job = (
        df_kh[col_job]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    selected_job = st.selectbox(
        "Chọn nghề nghiệp",
        sorted(list_job)
    )

    # =========================
    # LỌC DATA
    # =========================
    df_job = df_kh[df_kh[col_job] == selected_job].copy()

    # =========================
    # KPI
    # =========================
    col_hdv_bq = "HDVKKH_BQ"
    col_hdv_ck = "HDVCKH_CK"
    col_dnck = "DNCK"
    col_spdv = "TOTAL_SPDV"

    # convert số
    df_job[col_hdv_bq] = pd.to_numeric(df_job[col_hdv_bq], errors="coerce")
    df_job[col_hdv_ck] = pd.to_numeric(df_job[col_hdv_ck], errors="coerce")
    df_job[col_dnck] = pd.to_numeric(df_job[col_dnck], errors="coerce")
    df_job[col_spdv] = pd.to_numeric(df_job[col_spdv], errors="coerce")

    # tính tổng
    tong_hdv_bq = df_job[col_hdv_bq].fillna(0).sum()
    tong_hdv_ck = df_job[col_hdv_ck].fillna(0).sum()
    tong_dnck = df_job[col_dnck].fillna(0).sum()
    tong_spdv = df_job[col_spdv].fillna(0).sum()

    # =========================
    # KPI ĐẸP
    # =========================
    st.markdown("### 📊 Tổng hợp theo nghề nghiệp")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        kpi_card("👥 KH Active+New", f"{len(df_job):,}")

    with c2:
        kpi_card("💰 HDVKKH_BQ", f"{tong_hdv_bq:,.0f}")

    with c3:
        kpi_card("💰 HDVCKH_CK", f"{tong_hdv_ck:,.0f}")

    with c4:
        kpi_card("🏦 DNCK", f"{tong_dnck:,.0f}")

    with c5:
        kpi_card("📊 Tổng DV", f"{tong_spdv:,.0f}")

    # =========================
    # TABLE CHI TIẾT
    # =========================
    st.dataframe(
        format_dataframe(df_job, col_customer, col_manager),
        use_container_width=True,
        height=500,
        hide_index=True
    
    )

# =========================
# 📌 TRẠNG THÁI ĐO LƯỜNG
# =========================
elif menu == "📌  Đo luong":

    st.markdown(
        '<div class="section-title">📌 Danh sách TRANGTHAI_DOLUONG</div>',
        unsafe_allow_html=True
    )

    col_measure = "TRANG THAI_DOLUONG"

    if col_measure not in df.columns:
        st.error("❌ Không có cột TRANGTHAI_DOLUONG")
        st.stop()

    # =========================
    # 🔥 CHỌN PHÒNG BAN
    # =========================
    if "PHONG BAN" not in df.columns:
        st.error("❌ Không có cột PHONG BAN")
        st.stop()

    df["PHONG BAN"] = df["PHONG BAN"].astype(str).str.strip()

    list_pb = ["Tất cả"] + sorted(
        df["PHONG BAN"]
        .dropna()
        .loc[~df["PHONG BAN"].str.contains("0x", na=False)]  # bỏ rác
        .unique()
    )

    selected_pb = st.selectbox("🏢 Chọn phòng ban", list_pb)

    # lọc theo phòng ban
    if selected_pb != "Tất cả":
        df_filter = df[df["PHONG BAN"] == selected_pb].copy()
    else:
        df_filter = df.copy()

    # =========================
    # FILTER TRẠNG THÁI
    # =========================
    df_filter[col_measure] = pd.to_numeric(df_filter[col_measure], errors="coerce")

    df_need = df_filter[df_filter[col_measure] == 1].copy()

    # =========================
    # KPI
    # =========================
    st.markdown("### 👥 Số khách")

    kpi_card("👥 Số khách THDL", f"{len(df_need):,}")

    # =========================
    # TABLE
    # =========================
    st.markdown("### 📋 Danh sách")

    st.dataframe(
        format_dataframe(df_need, col_customer, col_manager),
        use_container_width=True,
        height=600,
        hide_index=True
    )
else:
    st.info("👉 Upload file để bắt đầu")
