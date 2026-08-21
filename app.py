import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="업무 지원 요청 데이터 분석 대시보드",
    page_icon="📋",
    layout="wide"
)

# 타이틀
st.title("📋 업무 지원 요청 데이터 시각화 대시보드")
st.markdown("업로드하신 `업무지원요청_합성자료.csv` 형식의 데이터를 분석하고 시각화합니다.")

# 사이드바 - 파일 업로드 및 필터
st.sidebar.header("📁 데이터 업로드 및 필터")
uploaded_file = st.sidebar.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # 데이터 로드 (한글 인코딩 대응)
    try:
        df = pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='cp949')

    # 날짜 데이터 변환
    if 'request_date' in df.columns:
        df['request_date'] = pd.to_datetime(df['request_date'])

    # 사이드바 카테고리 필터
    st.sidebar.subheader("필터 옵션")
    selected_categories = st.sidebar.multiselect(
        "카테고리 선택",
        options=df['category'].unique() if 'category' in df.columns else [],
        default=df['category'].unique() if 'category' in df.columns else []
    )

    # 필터링 적용
    filtered_df = df[df['category'].isin(selected_categories)] if 'category' in df.columns else df

    # --- 메트릭 요약 ---
    st.subheader("📌 주요 요약 지표 (KPI)")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("총 요청 건수", f"{len(filtered_df)} 건")
    
    completed_count = len(filtered_df[filtered_df['status'] == '완료']) if 'status' in filtered_df.columns else 0
    col2.metric("처리 완료 건수", f"{completed_count} 건")
    
    in_progress_count = len(filtered_df[filtered_df['status'] == '처리중']) if 'status' in filtered_df.columns else 0
    col3.metric("처리중 건수", f"{in_progress_count} 건")
    
    high_urgency_count = len(filtered_df[filtered_df['urgency'] == '상']) if 'urgency' in filtered_df.columns else 0
    col4.metric("긴급('상') 건수", f"{high_urgency_count} 건")

    st.divider()

    # --- 탭 구성 ---
    tab1, tab2, tab3 = st.tabs(["📊 주요 시각화", "🔍 상세 분석", "📄 원본 데이터"])

    # TAB 1: 차트 시각화
    with tab1:
        c1, c2 = st.columns(2)

        # 1. 카테고리별 요청 건수 (막대 그래프)
        with c1:
            st.markdown("##### 1. 카테고리별 지원 요청 건수")
            if 'category' in filtered_df.columns:
                cat_counts = filtered_df['category'].value_counts().reset_index()
                cat_counts.columns = ['category', 'count']
                fig_cat = px.bar(
                    cat_counts, x='category', y='count',
                    text='count', color='category',
                    labels={'category': '카테고리', 'count': '요청 건수'},
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_cat.update_traces(textposition='outside')
                st.plotly_chart(fig_cat, use_container_width=True)

        # 2. 처리 상태별 비중 (파이 차트)
        with c2:
            st.markdown("##### 2. 처리 상태(Status) 비중")
            if 'status' in filtered_df.columns:
                status_counts = filtered_df['status'].value_counts().reset_index()
                status_counts.columns = ['status', 'count']
                fig_status = px.pie(
                    status_counts, names='status', values='count',
                    hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_status, use_container_width=True)

        c3, c4 = st.columns(2)

        # 3. 긴급도별 분포 (도넛 차트 / 막대 차트)
        with c3:
            st.markdown("##### 3. 긴급도(Urgency) 분포")
            if 'urgency' in filtered_df.columns:
                urgency_counts = filtered_df['urgency'].value_counts().reset_index()
                urgency_counts.columns = ['urgency', 'count']
                fig_urgency = px.bar(
                    urgency_counts, x='urgency', y='count',
                    text='count', color='urgency',
                    color_discrete_map={'상': '#ff6b6b', '보통': '#feca57', '하': '#1dd1a1'}
                )
                st.plotly_chart(fig_urgency, use_container_width=True)

        # 4. AI 대응 가능 여부 분포
        with c4:
            st.markdown("##### 4. AI 대응(ai_handling) 분류 현황")
            if 'ai_handling' in filtered_df.columns:
                ai_counts = filtered_df['ai_handling'].value_counts().reset_index()
                ai_counts.columns = ['ai_handling', 'count']
                fig_ai = px.pie(
                    ai_counts, names='ai_handling', values='count',
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                st.plotly_chart(fig_ai, use_container_width=True)

    # TAB 2: 날짜별 추이 및 교차 분석
    with tab2:
        st.markdown("##### 📈 일자별 요청 건수 추이")
        if 'request_date' in filtered_df.columns:
            date_df = filtered_df.groupby('request_date').size().reset_index(name='count')
            fig_date = px.line(
                date_df, x='request_date', y='count',
                markers=True, title="일자별 접수 건수 흐름",
                labels={'request_date': '요청 일자', 'count': '접수 건수'}
            )
            st.plotly_chart(fig_date, use_container_width=True)

        st.markdown("##### 🔄 카테고리 x 긴급도 교차 분석")
        if 'category' in filtered_df.columns and 'urgency' in filtered_df.columns:
            cross_tab = pd.crosstab(filtered_df['category'], filtered_df['urgency'])
            st.dataframe(cross_tab, use_container_width=True)

    # TAB 3: 원본 데이터 출력 및 검색
    with tab3:
        st.markdown("##### 🔍 전체 데이터 목록")
        st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("👈 왼쪽 사이드바에서 `업무지원요청_합성자료.csv` 파일(또는 동일한 형식의 CSV)을 업로드해주세요.")
