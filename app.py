import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import os

# 0. 페이지 설정 및 폰트
st.set_page_config(page_title="무역 결제 리스크 분석기", layout="wide")

# 한글 폰트 설정 (GitHub 배포 및 로컬 공용)
font_path = "NanumGothic-Regular.ttf"
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
    plt.rcParams['axes.unicode_minus'] = False
else:
    plt.rc('font', family='Malgun Gothic')

# 1. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    filepath = "한국무역보험공사_국가별 신용장방식 결제비중_20211231.csv"
    try:
        # 인코딩 자동 대응
        try: data = pd.read_csv(filepath, encoding='cp949')
        except: data = pd.read_csv(filepath, encoding='utf-8')
        
        # 데이터 클리닝: % 제거 및 숫자 변환
        years = ['2017', '2018', '2019', '2020', '2021']
        for year in years:
            data[year] = data[year].astype(str).str.replace('%', '').str.strip().astype(float)
        
        # 트렌드 계산 (2017년 대비 2021년 변화량)
        data['변화량'] = data['2021'] - data['2017']
        return data, years
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류 발생: {e}")
        return None, None

df, year_cols = load_data()

if df is not None:
    st.title("🚢 글로벌 신용장(L/C) 결제 트렌드 분석")
    st.markdown("무역보험공사의 데이터를 기반으로 국가별 대금 결제 방식의 변화를 분석합니다.")

    # 탭 메뉴 구성
    tab1, tab2, tab3 = st.tabs(["📊 전체 데이터", "📈 트렌드 분석", "⚔️ 국가별 비교"])

    # --- TAB 1: 전체 데이터 표 ---
    with tab1:
        st.subheader("전체 국가별 데이터 시트")
        st.write("모든 국가의 연도별 L/C 결제 비중(%) 데이터입니다.")
        st.dataframe(df, use_container_width=True)

    # --- TAB 2: 트렌드 분석 (상승 vs 하락) ---
    with tab2:
        st.subheader("신용장 결제 비중 변화 추이")
        
        col1, col2 = st.columns(2)
        
        # 2017년 대비 2021년 비중이 높아진 국가 (상위 10개)
        inc_df = df[df['변화량'] > 0].sort_values('변화량', ascending=False).head(10)
        # 비중이 낮아진 국가 (하위 10개)
        dec_df = df[df['변화량'] < 0].sort_values('변화량', ascending=True).head(10)

        with col1:
            st.success("⬆️ 비중이 가장 많이 높아진 TOP 10")
            fig_inc, ax_inc = plt.subplots(figsize=(8, 6))
            # 가독성을 위해 긴 데이터를 피벗
            inc_melt = inc_df.melt(id_vars='국가명', value_vars=year_cols)
            sns.lineplot(data=inc_melt, x='variable', y='value', hue='국가명', marker='o', ax=ax_inc)
            ax_inc.set_title("L/C 비중 상승 국가 (위험군)")
            ax_inc.set_ylabel("비중 (%)")
            st.pyplot(fig_inc)

        with col2:
            st.info("⬇️ 비중이 가장 많이 낮아진 TOP 10")
            fig_dec, ax_dec = plt.subplots(figsize=(8, 6))
            dec_melt = dec_df.melt(id_vars='국가명', value_vars=year_cols)
            sns.lineplot(data=dec_melt, x='variable', y='value', hue='국가명', marker='o', ax=ax_dec)
            ax_dec.set_title("L/C 비중 하락 국가 (송금 우세)")
            ax_dec.set_ylabel("비중 (%)")
            st.pyplot(fig_dec)

    # --- TAB 3: 국가별 비교 ---
    with tab3:
        st.subheader("맞춤형 국가 비교 분석")
        selected_countries = st.multiselect(
            "비교하고 싶은 국가들을 선택하세요 (여러 개 선택 가능)", 
            options=df['국가명'].unique(),
            default=["중국", "베트남"] if "베트남" in df['국가명'].values else [df['국가명'].iloc[0]]
        )

        if selected_countries:
            compare_df = df[df['국가명'].isin(selected_countries)]
            compare_melt = compare_df.melt(id_vars='국가명', value_vars=year_cols)
            
            fig_comp, ax_comp = plt.subplots(figsize=(12, 6))
            sns.lineplot(data=compare_melt, x='variable', y='value', hue='국가명', marker='s', linewidth=2, ax=ax_comp)
            ax_comp.set_title(f"선택 국가 간 결제 비중 비교", fontsize=15)
            ax_comp.set_ylabel("신용장(L/C) 비중 (%)")
            ax_comp.grid(True, alpha=0.3)
            st.pyplot(fig_comp)
            
            # 비교 요약 정보
            st.write("💡 **분석 결과:** " + ", ".join([f"{c}는 2021년 기준 {df[df['국가명']==c]['2021'].values[0]}%" for c in selected_countries]))
        else:
            st.warning("국가를 하나 이상 선택해 주세요.")