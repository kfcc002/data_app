# STREAMLING_CHUNK: 라이브러리 임포트 및 페이지 설정
import streamlit as st
import streamlit.components.v1 as components
import os

# 스트림릿 페이지 기본 설정 (전체 화면 사용, 타이틀 설정)
st.set_page_config(
    page_title="팀 예산 관리 대시보드",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# STREAMLING_CHUNK: HTML 파일 읽기 및 예외 처리
# 렌더링할 HTML 파일 경로 지정 (app.py와 같은 폴더에 있어야 합니다)
html_file_path = "team_budget_dashboard.html"

try:
    # HTML 파일을 읽어옵니다. (한글 깨짐 방지를 위해 utf-8 인코딩 지정)
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # STREAMLING_CHUNK: HTML 컴포넌트 렌더링
    # 읽어온 HTML 내용을 스트림릿 화면에 렌더링합니다.
    # height를 1000 이상으로 넉넉하게 주어 내부 스크롤바가 생기는 것을 방지합니다.
    components.html(html_content, height=1200, scrolling=True)

except FileNotFoundError:
    # 파일을 찾지 못했을 때의 에러 메시지
    st.error(f"🚨 '{html_file_path}' 파일을 찾을 수 없습니다. GitHub 레포지토리에 해당 HTML 파일이 함께 업로드되었는지 확인해주세요.")
except Exception as e:
    # 기타 에러 발생 시
    st.error(f"🚨 오류가 발생했습니다: {e}")
