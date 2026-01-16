import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import os

# 0. 페이지 설정
st.set_page_config(page_title="무역 결제 리스크 분석기", layout="wide")

# --- 폰트 설정 (가장 확실한 경로 지정 방식) ---
font_path = "NanumGothic-Regular.ttf"
font_prop = None

if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
    plt.rcParams['axes.unicode_minus'] = False
else:
    # 로컬 윈도우 환경 대응
    plt.rc('font', family='Malgun Gothic')

# 1. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    filepath = "한국무역보험공사_국가별 신용장방식 결제비중_20211231.csv"
    try:
        # 인코딩 자동 대응
        try: data = pd.read_csv(filepath, encoding='cp949')
        except: data = pd.read_csv(filepath, encoding='utf-8')
        
        years = ['2017', '2018', '2019', '2020', '2021']
        for year in years:
            data[year] = data[year].astype(str).str.replace('%', '').str.strip().astype(float)
        
        # 트렌드 계산: $변화량 = 2021년 - 2017년$
        data['변화량'] = data['2021'] - data['2017']
        return data, years
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None, None

df, year_cols = load_data()

if df is not None:
    st.title("🚢 글로벌 신용장(L/C) 결제 트렌드 분석")
    st.markdown("본 도구는 국가별 결제 방식의 변화를 시각화하여 수출 대금 회수 리스크 관리를 지원합니다.")

    tab1, tab2, tab3 = st.tabs(["📊 전체 데이터", "📈 트렌드 분석", "⚔️ 국가별 비교"])

    # --- TAB 1: 전체 데이터 ---
    with tab1:
        st.subheader("전체 국가별 데이터 시트")
        st.dataframe(df, use_container_width=True)

    # --- TAB 2: 트렌드 분석 ---
    with tab2:
        st.subheader("신용장 결제 비중 변화 추이 (2017 vs 2021)")
        col1, col2 = st.columns(2)
        
        inc_df = df[df['변화량'] > 0].sort_values('변화량', ascending=False).head(10)
        dec_df = df[df['변화량'] < 0].sort_values('변화량', ascending=True).head(10)

        with col1:
            st.success("⬆️ L/C 비중 상승 TOP 10 (위험군 관리 필요)")
            fig, ax = plt.subplots(figsize=(8, 6))
            melted = inc_df.melt(id_vars='국가명', value_vars=year_cols)
            sns.lineplot(data=melted, x='variable', y='value', hue='국가명', marker='o', ax=ax)
            
            # [강사 팁] 개별 요소에 폰트 속성 직접 적용
            title_text = "L/C 비중 상승 국가"
            if font_prop:
                ax.set_title(title_text, fontproperties=font_prop, fontsize=14)
                ax.set_ylabel("비중 (%)", fontproperties=font_prop)
                ax.set_xlabel("연도", fontproperties=font_prop)
                plt.legend(prop=font_prop)
            else:
                ax.set_title(title_text)
            st.pyplot(fig)

        with col2:
            st.info("⬇️ L/C 비중 하락 TOP 10 (송금 방식 확산)")
            fig, ax = plt.subplots(figsize=(8, 6))
            melted = dec_df.melt(id_vars='국가명', value_vars=year_cols)
            sns.lineplot(data=melted, x='variable', y='value', hue='국가명', marker='o', ax=ax)
            
            if font_prop:
                ax.set_title("L/C 비중 하락 국가", fontproperties=font_prop, fontsize=14)
                ax.set_ylabel("비중 (%)", fontproperties=font_prop)
                ax.set_xlabel("연도", fontproperties=font_prop)
                plt.legend(prop=font_prop)
            st.pyplot(fig)

    # --- TAB 3: 국가별 비교 ---
    with tab3:
        st.subheader("맞춤형 국가 비교 분석")
        selected_countries = st.multiselect(
            "비교 국가 선택", options=df['국가명'].unique(),
            default=["중국", "베트남"] if "베트남" in df['국가명'].values else [df['국가명'].iloc[0]]
        )

        if selected_countries:
            compare_melt = df[df['국가명'].isin(selected_countries)].melt(id_vars='국가명', value_vars=year_cols)
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.lineplot(data=compare_melt, x='variable', y='value', hue='국가명', marker='s', linewidth=2.5, ax=ax)
            
            if font_prop:
                ax.set_title("선택 국가 간 결제 비중 비교", fontproperties=font_prop, fontsize=16)
                ax.set_ylabel("신용장(L/C) 비중 (%)", fontproperties=font_prop)
                ax.set_xlabel("연도", fontproperties=font_prop)
                plt.legend(prop=font_prop)
            
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            
            # 분석 요약 텍스트
            summary = [f"{c}({df[df['국가명']==c]['2021'].values[0]}%)" for c in selected_countries]
            st.write(f"💡 **2021년 기준 결제 비중:** {', '.join(summary)}")