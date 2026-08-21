import streamlit as st
import requests
import pandas as pd
import altair as alt
import datetime
import time

st.set_page_config(page_title="팀 예산 관리 대시보드", page_icon="📊", layout="wide")

st.title("📊 팀 예산 관리 시스템")
st.markdown("부장님 보고용 월별 예산 취합 및 대시보드 (Google Sheets + Apps Script 연동)")

with st.sidebar:
    st.header("⚙️ 시스템 설정")
    # Apps Script Web App URL 입력창
    gas_url = st.text_input(
        "Apps Script Web App URL", 
        type="password", 
        help="Google Apps Script를 '웹 앱'으로 배포한 후 발급받은 URL을 입력하세요."
    )
    
    st.markdown("---")
    st.markdown("### 🚀 서비스 설정 가이드")
    st.markdown("1. 새 구글 스프레드시트를 생성하고 첫 번째 시트 이름을 **Sheet1**로 설정합니다.")
    st.markdown("2. 메뉴에서 **[확장 프로그램] > [Apps Script]**를 클릭합니다.")
    st.markdown("3. 제공된 `apps_script.js` 코드를 붙여넣습니다.")
    st.markdown("4. 우측 상단의 **[배포] > [새 배포]**를 클릭합니다.")
    st.markdown("5. 유형을 **웹 앱**으로 선택, 액세스 권한을 **모든 사용자**로 설정 후 배포합니다.")
    st.markdown("6. 생성된 **웹 앱 URL**을 위 입력창에 붙여넣으면 연동이 완료됩니다!")

@st.cache_data(ttl=5) # 5초 동안 데이터 캐싱 (잦은 요청 방지)
def fetch_data(url):
    if not url:
        return pd.DataFrame()
    try:
        # GET 요청을 통해 스프레드시트의 모든 데이터 가져오기
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                return pd.DataFrame(data)
            else:
                return pd.DataFrame(columns=['id', 'member', 'month', 'category', 'amount'])
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

tab1, tab2 = st.tabs(["📝 데이터 입력", "📈 전체 대시보드"])

with tab1:
    st.header("내역 입력")
    
    with st.form("budget_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            member = st.selectbox("팀원 선택", ["부장님", "팀원1", "팀원2", "팀원3", "팀원4"])
            # 이번 달을 기본값으로 하는 연월 텍스트박스
            current_month = datetime.date.today().strftime("%Y-%m")
            month = st.text_input("해당 월 (YYYY-MM)", value=current_month)
            
        with col2:
            category = st.selectbox("예산 항목", ["수선유지비", "비품", "개량공사"])
            amount = st.number_input("사용 금액 (원)", min_value=0, step=1000)
        
        submit = st.form_submit_button("기록 저장하기", use_container_width=True)
        
        if submit:
            if not gas_url:
                st.warning("⚠️ 먼저 좌측 사이드바에 Apps Script URL을 입력해주세요.")
            else:
                payload = {
                    "id": int(datetime.datetime.now().timestamp() * 1000),
                    "member": member,
                    "month": month,
                    "category": category,
                    "amount": amount
                }
                try:
                    with st.spinner('데이터를 스프레드시트에 저장하는 중...'):
                        res = requests.post(gas_url, json=payload)
                    
                    if res.status_code == 200:
                        st.success("✅ 예산 데이터가 정상적으로 기록되었습니다!")
                        time.sleep(1) # 성공 메시지 표시 후 캐시 갱신을 위해 대기
                        fetch_data.clear() # 캐시 지우기
                        st.rerun() # 화면 새로고침
                    else:
                        st.error("❌ 저장에 실패했습니다. (서버 응답 오류)")
                except Exception as e:
                    st.error(f"❌ 네트워크 또는 서버 에러가 발생했습니다: {e}")

    st.subheader("📂 최근 입력 내역")
    df = fetch_data(gas_url)
    if not df.empty:
        # 최신 데이터가 위로 오도록 정렬
        display_df = df[['month', 'member', 'category', 'amount']].copy()
        display_df['amount'] = pd.to_numeric(display_df['amount'])
        st.dataframe(
            display_df.sort_values('month', ascending=False), 
            use_container_width=True,
            column_config={
                "month": "연월",
                "member": "팀원",
                "category": "예산 항목",
                "amount": st.column_config.NumberColumn("사용 금액 (원)", format="%d 원")
            }
        )
    else:
        st.info("입력된 데이터가 없거나 URL이 아직 설정되지 않았습니다.")

with tab2:
    st.header("대시보드")
    df = fetch_data(gas_url)
    
    if df.empty:
        st.warning("분석할 데이터가 없습니다. [데이터 입력] 탭에서 데이터를 먼저 추가해주세요.")
    else:
        df['amount'] = pd.to_numeric(df['amount'])
        
        total_amount = df['amount'].sum()
        count = len(df)
        
        # 카테고리별 누적액 구하기 (최대 사용 항목 추출용)
        category_sums = df.groupby('category')['amount'].sum()
        top_category = category_sums.idxmax() if not category_sums.empty else "-"
        
        col1, col2, col3 = st.columns(3)
        col1.metric("전체 누적 사용액", f"{total_amount:,.0f} 원")
        col2.metric("최대 사용 항목", top_category)
        col3.metric("누적 데이터 건수", f"{count} 건")
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("🏠 항목별 예산 분포")
            cat_df = df.groupby('category', as_index=False)['amount'].sum()
            
            # Donut Chart
            base = alt.Chart(cat_df).encode(
                theta=alt.Theta("amount:Q", stack=True),
                color=alt.Color("category:N", legend=alt.Legend(title="항목")),
                tooltip=['category', 'amount']
            )
            pie = base.mark_arc(innerRadius=60, stroke="#fff")
            st.altair_chart(pie, use_container_width=True)

        with c2:
            st.subheader("👥 팀원별 누적 사용액")
            mem_df = df.groupby('member', as_index=False)['amount'].sum()
            
            # Bar Chart
            bar_chart = alt.Chart(mem_df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                x=alt.X('member:N', title='팀원', sort='-y'),
                y=alt.Y('amount:Q', title='총 사용 금액 (원)'),
                color=alt.Color('member:N', legend=None),
                tooltip=['member', 'amount']
            ).properties(height=350)
            st.altair_chart(bar_chart, use_container_width=True)
            
        st.markdown("---")
        
        st.subheader("📅 월별/항목별 요약 테이블 (취합본)")
        
        # 피벗 테이블 생성
        pivot_df = df.pivot_table(
            index='month', 
            columns='category', 
            values='amount', 
            aggfunc='sum', 
            fill_value=0
        )
        
        # 합계 열 추가
        pivot_df['합계'] = pivot_df.sum(axis=1)
        
        # 최신 월이 위로 오도록 정렬
        pivot_df = pivot_df.sort_index(ascending=False)
        
        # 서식 지정 (숫자에 콤마 추가)
        styled_df = pivot_df.applymap(lambda x: f"{int(x):,} 원" if pd.notnull(x) else "0 원")
        
        st.dataframe(styled_df, use_container_width=True)
