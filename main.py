import streamlit as st
import json

# MBTI별 데이터: 직업, 환경 점수, 학습 리소스, 동기부여 메시지
mbti_data = {
    "INTJ": {
        "jobs": ["🔬 연구원", "📊 데이터 분석가", "🛠️ 전략 컨설턴트"],
        "environment": [80, 90, 85, 90, 60],  # [팀워크, 독립성, 창의성, 구조화, 압박감]
        "resources": [
            {"title": "Coursera: Data Science", "url": "https://www.coursera.org"},
            {"title": "책: Thinking, Fast and Slow", "url": "https://example.com"},
        ],
        "motivation": "당신의 전략적 사고는 세상을 바꿀 수 있습니다! 🚀"
    },
    "INTP": {
        "jobs": ["💻 소프트웨어 엔지니어", "🔍 UX 리서처", "📚 교수/강사"],
        "environment": [60, 95, 90, 70, 50],
        "resources": [
            {"title": "Udemy: Python Programming", "url": "https://www.udemy.com"},
            {"title": "YouTube: CS50 Lectures", "url": "https://www.youtube.com"},
        ],
        "motivation": "호기심이 당신을 혁신의 길로 이끌어요! 💡"
    },
    "ENTJ": {
        "jobs": ["🚀 스타트업 창업가", "📈 경영 컨설턴트", "🏢 CEO/임원"],
        "environment": [90, 60, 80, 85, 70],
        "resources": [
            {"title": "Udemy: Business Strategy", "url": "https://www.udemy.com"},
            {"title": "책: Lean Startup", "url": "https://example.com"},
        ],
        "motivation": "당신의 리더십은 팀을 성공으로 이끌어요! 🌟"
    },
    "ENTP": {
        "jobs": ["🧠 혁신 디자이너", "🎤 테크 연사", "🛠️ 제품 매니저"],
        "environment": [70, 80, 95, 60, 65],
        "resources": [
            {"title": "Coursera: Design Thinking", "url": "https://www.coursera.org"},
            {"title": "책: The Innovator's Dilemma", "url": "https://example.com"},
        ],
        "motivation": "당신의 창의력은 한계를 모릅니다! 🌈"
    },
    "INFJ": {
        "jobs": ["💖 상담사", "✍️ 작가", "🌎 사회 혁신가"],
        "environment": [85, 80, 90, 65, 40],
        "resources": [
            {"title": "Coursera: Psychology", "url": "https://www.coursera.org"},
            {"title": "책: The Alchemist", "url": "https://example.com"},
        ],
        "motivation": "당신의 공감은 세상을 더 따뜻하게 만듭니다! 💞"
    },
    "INFP": {
        "jobs": ["🎨 아티스트", "📖 편집자", "🌱 비영리 기획자"],
        "environment": [70, 90, 95, 50, 30],
        "resources": [
            {"title": "Skillshare: Digital Art", "url": "https://www.skillshare.com"},
            {"title": "책: Big Magic", "url": "https://example.com"},
        ],
        "motivation": "당신의 꿈은 세상에 색을 더해요! 🎨"
    },
    "ENFJ": {
        "jobs": ["🤝 HR 매니저", "🎤 동기부여 강연자", "🏫 교사"],
        "environment": [95, 60, 85, 70, 50],
        "resources": [
            {"title": "Coursera: Leadership", "url": "https://www.coursera.org"},
            {"title": "책: Daring Greatly", "url": "https://example.com"},
        ],
        "motivation": "당신의 열정은 모두를 하나로 묶어요! 🌍"
    },
    "ENFP": {
        "jobs": ["🌟 이벤트 플래너", "🌀 마케팅 크리에이터", "🧭 여행 작가"],
        "environment": [80, 70, 95, 55, 45],
        "resources": [
            {"title": "Udemy: Digital Marketing", "url": "https://www.udemy.com"},
            {"title": "책: Eat Pray Love", "url": "https://example.com"},
        ],
        "motivation": "당신의 에너지는 세상을 밝게 비춰요! ✨"
    },
    "ISTJ": {
        "jobs": ["🛡️ 감사 전문가", "📑 프로젝트 매니저", "📋 품질 관리자"],
        "environment": [80, 85, 60, 95, 65],
        "resources": [
            {"title": "Coursera: Project Management", "url": "https://www.coursera.org"},
            {"title": "책: Getting Things Done", "url": "https://example.com"},
        ],
        "motivation": "당신의 꼼꼼함은 성공의 열쇠예요! 🗂️"
    },
    "ISFJ": {
        "jobs": ["🩺 간호사", "🏛️ 기록 보관 관리자", "🏥 복지 상담사"],
        "environment": [90, 75, 70, 80, 40],
        "resources": [
            {"title": "Coursera: Healthcare", "url": "https://www.coursera.org"},
            {"title": "책: The Gifts of Imperfection", "url": "https://example.com"},
        ],
        "motivation": "당신의 따뜻함은 모두에게 위로가 됩니다! 🫶"
    },
    "ESTJ": {
        "jobs": ["🏭 운영 관리자", "👮 법 집행관", "💼 금융 관리자"],
        "environment": [90, 70, 65, 90, 70],
        "resources": [
            {"title": "Udemy: Operations Management", "url": "https://www.udemy.com"},
            {"title": "책: The 7 Habits", "url": "https://example.com"},
        ],
        "motivation": "당신의 리더십은 질서를 만듭니다! 🏛️"
    },
    "ESFJ": {
        "jobs": ["🍽️ 이벤트 코디네이터", "🛒 소매 관리자", "🏥 간호 관리자"],
        "environment": [95, 60, 75, 80, 50],
        "resources": [
            {"title": "Coursera: Event Planning", "url": "https://www.coursera.org"},
            {"title": "책: How to Win Friends", "url": "https://example.com"},
        ],
        "motivation": "당신의 친화력은 모두를 행복하게 해요! 😊"
    },
    "ISTP": {
        "jobs": ["🔧 기계 엔지니어", "🕵️‍♂️ 범죄 현장 조사관", "🚗 자동차 기술자"],
        "environment": [60, 95, 80, 65, 55],
        "resources": [
            {"title": "Udemy: Mechanical Engineering", "url": "https://www.udemy.com"},
            {"title": "YouTube: Engineering Explained", "url": "https://www.youtube.com"},
        ],
        "motivation": "당신의 실용성은 문제를 해결해요! 🛠️"
    },
    "ISFP": {
        "jobs": ["🎸 뮤지션", "📷 사진 작가", "🛋️ 인테리어 디자이너"],
        "environment": [65, 90, 95, 50, 35],
        "resources": [
            {"title": "Skillshare: Photography", "url": "https://www.skillshare.com"},
            {"title": "책: Steal Like an Artist", "url": "https://example.com"},
        ],
        "motivation": "당신의 감성은 세상을 아름답게 해요! 🌸"
    },
    "ESTP": {
        "jobs": ["🏎️ 스포츠 코치", "💼 판매 대표", "🎬 스턴트 배우"],
        "environment": [85, 70, 80, 60, 65],
        "resources": [
            {"title": "Udemy: Sales Techniques", "url": "https://www.udemy.com"},
            {"title": "책: Influence", "url": "https://example.com"},
        ],
        "motivation": "당신의 에너지는 무대를 장악해요! 🔥"
    },
    "ESFP": {
        "jobs": ["🎭 배우", "🎤 가수", "🕺 댄서"],
        "environment": [90, 65, 95, 55, 50],
        "resources": [
            {"title": "Skillshare: Acting", "url": "https://www.skillshare.com"},
            {"title": "책: The Artist's Way", "url": "https://example.com"},
        ],
        "motivation": "당신의 열정은 모두를 사로잡아요! 🎤"
    },
}

st.set_page_config(page_title="MBTI 직업 추천", layout="centered", page_icon="✨")

st.title("✨ MBTI 기반 직업 추천 앱 ✨")
st.write("당신의 MBTI 유형을 선택하면 맞춤형 직업, 학습 리소스, 그리고 동기를 드립니다! 🚀")

# 세션 상태로 MBTI 선택 유지
if "mbti" not in st.session_state:
    st.session_state.mbti = ""

# MBTI 선택
mbti = st.selectbox(
    "당신의 MBTI를 선택하세요:",
    [""] + list(mbti_data.keys()),
    index=0 if not st.session_state.mbti else list(mbti_data.keys()).index(st.session_state.mbti) + 1,
)
st.session_state.mbti = mbti

# 결과 보기 버튼
if st.button("결과 보기", use_container_width=True):
    if mbti:
        data = mbti_data[mbti]

        # 추천 직업
        st.subheader(f"📌 '{mbti}' 유형에 어울리는 직업")
        for job in data["jobs"]:
            st.write(f"- {job}")

        # 직업 환경 분석 차트 (Plotly 사용으로 변경)
        st.subheader("📊 직업 환경 분석")
        import plotly.graph_objects as go
        fig = go.Figure(
            data=[
                go.Scatterpolar(
                    r=data["environment"],
                    theta=["팀워크", "독립성", "창의성", "구조화", "압박감"],
                    fill="toself",
                    name=f"{mbti} 직업 환경 적합도",
                )
            ],
            layout=go.Layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

        # 학습 리소스
        st.subheader("📚 추천 학습 리소스")
        for resource in data["resources"]:
            st.markdown(f"- [{resource['title']}]({resource['url']})")

        # 동기부여 메시지
        st.subheader("💪 당신에게 보내는 메시지")
        st.success(data["motivation"])

    else:
        st.warning("MBTI 유형을 선택해주세요! 😊")

# 앱 정보
st.markdown("---")
st.caption("Made with 💖 by Streamlit | 데이터는 예시이며, 실제 진로 선택 시 전문가와 상담하세요.")
