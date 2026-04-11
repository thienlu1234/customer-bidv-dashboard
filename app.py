import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
st.set_page_config(layout="wide")

# ======================
# CSS GIAO DIỆN BIDV
# ======================
st.markdown("""
<style>

/* Sidebar nền xanh */
section[data-testid="stSidebar"] {
    background-color: #0E6F66;
}

/* Text sidebar */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Title */
.main-title {
    font-size: 38px;
    font-weight: 700;
    color: #0E6F66;
    margin-bottom: 10px;
}

/* KPI CARD */
.kpi-card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    text-align: center;
}

/* KPI text */
.kpi-title {
    font-size: 14px;
    color: gray;
}

.kpi-value {
    font-size: 28px;
    font-weight: bold;
    color: #0E6F66;
}

</style>
""", unsafe_allow_html=True)

# ======================
# HÀM KPI
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
    st.image("logo_bidv.png", width=80)

with col_title:
    st.markdown(
        '<div class="main-title">Dashboard Khách Hàng BIDV</div>',
        unsafe_allow_html=True
    )

def kpi_box(title, value, color):
    st.markdown(f"""
    <div style="
        background-color: {color};
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    ">
        <div style="font-size:14px;">{title}</div>
        <div style="font-size:28px; margin-top:5px;">{value}</div>
    </div>
    """, unsafe_allow_html=True)
# ======================
# MENU NGANG
# ======================
menu = option_menu(
    None,
    ["📊  Tổng quan", "🎯  Chăm sóc KH", "💰  HDVCKH_CK", "🏦  DNCK", "📈  Trung bình DV/người", "👨‍💼  Theo cán bộ", "🏢  Theo phòng ban", "👶  Độ tuổi", "💼  Nghề nghiệp"],
    
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

    

    # ======================
    # 📊 TỔNG QUAN
    # ======================
    if menu == "📊  Tổng quan":
    
        st.subheader("📌 Tổng quan khách hàng")
    
        total = len(df)
        active = (df[col_status] == "Active").sum()
        new = (df[col_status] == "New").sum()
        frozen = (df[col_status] == "Frozen").sum()
        dormant = (df[col_status] == "Dormant").sum()
        nan_count = df[col_status].isna().sum()
    
        # ======================
        # KPI
        # ======================
        c1, c2, c3, c4, c5, c6 = st.columns(6)
    
        with c1:
            kpi_card("👥 Tổng KH", f"{total:,}")
        with c2:
            kpi_card("🔥 Active", f"{active:,}")
        with c3:
            kpi_card("🆕 New", f"{new:,}")
        with c4:
            kpi_card("❄️ Frozen", f"{frozen:,}")
        with c5:
            kpi_card("😴 Dormant", f"{dormant:,}")
        with c6:
            kpi_card("❓ NaN", f"{nan_count:,}")
    
        # ======================
        # 🎯 BIỂU ĐỒ TRÒN XỊN
        # ======================
        
        st.markdown("### 📊 Tỷ lệ khách hàng")
        
        labels = ["Active", "New", "Frozen", "Dormant"]
        values = [active, new, frozen, dormant]
        
        # CHIA LAYOUT CHO ĐẸP (center)
        col_left, col_center, col_right = st.columns([1, 2, 1])
        
        with col_center:
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
        
                hole=0.55,  # donut sâu hơn → sang hơn
        
                # chỉ highlight Active thôi (đỡ rối)
                pull=[0.06, 0, 0, 0],
        
                marker=dict(
                    colors=[
                        "#0E6F66",  # xanh BIDV (Active)
                        "#F5C32C",  # vàng (New)
                        "#5DADE2",  # xanh nhạt (Frozen)
                        "#EC7063"   # đỏ (Dormant)
                    ],
                    line=dict(color="white", width=3)
                ),
        
                textinfo="percent",  # chỉ hiện % cho gọn
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
    elif menu == "🎯  Chăm sóc KH":
    
        st.subheader("🎯 Phân loại theo HDVKKH_BQ")
    
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
    # 3. HDVCKH_CK
    # =========================
    elif menu == "💰  HDVCKH_CK":

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
    elif menu == "🏦  DNCK":

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
    elif menu == "📈  Trung bình DV/người":
    
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
    # =========================
    # THEO CÁN BỘ QUẢN LÝ
    # =========================
    elif menu == "👨‍💼  Theo cán bộ":
    
        st.subheader("👨‍💼 Hiệu suất theo cán bộ quản lý")
    
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
        # HIỂN THỊ
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
    # THEO PHÒNG BAN
    # =========================
    elif menu == "🏢  Theo phòng ban":
    
        st.subheader("🏢 Hiệu suất theo phòng ban")
    
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

        st.subheader("👶 Phân loại khách hàng theo độ tuổi")
    
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

        st.subheader("💼 Phân loại khách hàng theo nghề nghiệp")
    
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
