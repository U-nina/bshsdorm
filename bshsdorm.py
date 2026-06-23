import streamlit as st
import datetime
import pandas as pd

# --- 1. 초기 세션 상태 설정 및 데이터 로드 ---
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.logged_in = False
    st.session_state.user_type = None  # 'student' or 'teacher'
    st.session_state.user_id = None

    # 비밀번호 저장소 (초기 비밀번호 0000)
    st.session_state.passwords = {}

    # 외박 신청 데이터 리스트
    st.session_state.outings = []

    # 벌점 데이터 (학생 학번별 누적 벌점 및 히스토리)
    st.session_state.demerits = {}
    st.session_state.demerit_history = []

    # Q&A 게시판 데이터
    st.session_state.qa_posts = []

    # (8) 공지사항 데이터 초기화 (기본 예시 공지 포함)
    st.session_state.notices = [
        {
            "idx": 0,
            "title": "📢 2026학년도 1학기 기숙사 입사 환영 및 준수사항 안내",
            "content": "부산고등학교 기숙사에 입사한 것을 환영합니다. 공동생활의 기본 예절을 지키고, 일과 시간(귀사 및 등교, 자율학습 등)을 철저히 준수해 주시기 바랍니다. 벌점 규정을 반드시 확인하세요.",
            "date": "2026-03-02"
        }
    ]

# --- 학생 배치 데이터 구축 (제공된 CSV 기반) ---
students_data = [
    # 1층 (101~107)
    {"floor": "1층", "room": "101", "bed": "1(위)", "id": "1101", "name": "김민준"},
    {"floor": "1층", "room": "101", "bed": "2(아래)", "id": "1102", "name": "김서준"},
    {"floor": "1층", "room": "102", "bed": "1", "id": "1201", "name": "김도윤"},
    {"floor": "1층", "room": "102", "bed": "2", "id": "1202", "name": "김예준"},
    {"floor": "1층", "room": "103", "bed": "1", "id": "1301", "name": "김시우"},
    {"floor": "1층", "room": "103", "bed": "2", "id": "1302", "name": "김하준"},
    {"floor": "1층", "room": "104", "bed": "1", "id": "1401", "name": "김주원"},
    {"floor": "1층", "room": "104", "bed": "2", "id": "1402", "name": "김지호"},
    {"floor": "1층", "room": "105", "bed": "1", "id": "1501", "name": "김동현"},
    {"floor": "1층", "room": "105", "bed": "2", "id": "1502", "name": "김유준"},
    {"floor": "1층", "room": "106", "bed": "1", "id": "1601", "name": "김은우"},
    {"floor": "1층", "room": "106", "bed": "2", "id": "1602", "name": "김현우"},
    {"floor": "1층", "room": "107", "bed": "1", "id": "1701", "name": "김선우"},
    {"floor": "1층", "room": "107", "bed": "2", "id": "1702", "name": "김우진"},
    # 2층 (201~210)
    {"floor": "2층", "room": "201", "bed": "1", "id": "2101", "name": "이준우"},
    {"floor": "2층", "room": "201", "bed": "2", "id": "2102", "name": "이도윤"},
    {"floor": "2층", "room": "202", "bed": "1", "id": "2103", "name": "이수현"},
    {"floor": "2층", "room": "202", "bed": "2", "id": "2104", "name": "이재현"},
    {"floor": "2층", "room": "203", "bed": "1", "id": "2201", "name": "이정우"},
    {"floor": "2층", "room": "203", "bed": "2", "id": "2202", "name": "이시윤"},
    {"floor": "2층", "room": "204", "bed": "1", "id": "2203", "name": "이준서"},
    {"floor": "2층", "room": "204", "bed": "2", "id": "2204", "name": "이진우"},
    {"floor": "2층", "room": "205", "bed": "1", "id": "2301", "name": "이승우"},
    {"floor": "2층", "room": "205", "bed": "2", "id": "2302", "name": "이민우"},
    {"floor": "2층", "room": "206", "bed": "1", "id": "2303", "name": "이태민"},
    {"floor": "2층", "room": "206", "bed": "2", "id": "2304", "name": "이한결"},
    {"floor": "2층", "room": "207", "bed": "1", "id": "2401", "name": "이로운"},
    {"floor": "2층", "room": "207", "bed": "2", "id": "2402", "name": "이서진"},
    {"floor": "2층", "room": "208", "bed": "1", "id": "2501", "name": "이하민"},
    {"floor": "2층", "room": "208", "bed": "2", "id": "2502", "name": "박지훈"},
    {"floor": "2층", "room": "209", "bed": "1", "id": "2601", "name": "박민재"},
    {"floor": "2층", "room": "209", "bed": "2", "id": "2602", "name": "박도하"},
    {"floor": "2층", "room": "210", "bed": "1", "id": "2701", "name": "박준혁"},
    {"floor": "2층", "room": "210", "bed": "2", "id": "2702", "name": "박시온"},
    # 3층 (301~310)
    {"floor": "3층", "room": "301", "bed": "1", "id": "3101", "name": "최진혁"},
    {"floor": "3층", "room": "301", "bed": "2", "id": "3102", "name": "최민성"},
    {"floor": "3층", "room": "302", "bed": "1", "id": "3103", "name": "최도진"},
    {"floor": "3층", "room": "302", "bed": "2", "id": "3104", "name": "최준영"},
    {"floor": "3층", "room": "303", "bed": "1", "id": "3201", "name": "최유찬"},
    {"floor": "3층", "room": "303", "bed": "2", "id": "3202", "name": "최현서"},
    {"floor": "3층", "room": "304", "bed": "1", "id": "3203", "name": "정연우"},
    {"floor": "3층", "room": "304", "bed": "2", "id": "3204", "name": "정지안"},
    {"floor": "3층", "room": "305", "bed": "1", "id": "3301", "name": "강동우"},
    {"floor": "3층", "room": "305", "bed": "2", "id": "3302", "name": "강민철"},
    {"floor": "3층", "room": "306", "bed": "1", "id": "3303", "name": "조윤성"},
    {"floor": "3층", "room": "306", "bed": "2", "id": "3304", "name": "한성민"},
    {"floor": "3층", "room": "307", "bed": "1", "id": "3401", "name": "한준희"},
    {"floor": "3층", "room": "307", "bed": "2", "id": "3402", "name": "윤지환"},
    {"floor": "3층", "room": "308", "bed": "1", "id": "3501", "name": "임태윤"},
    {"floor": "3층", "room": "308", "bed": "2", "id": "3502", "name": "서유안"},
    {"floor": "3층", "room": "309", "bed": "1", "id": "3601", "name": "배하겸"},
    {"floor": "3층", "room": "309", "bed": "2", "id": "3602", "name": "전하랑"},
    {"floor": "3층", "room": "310", "bed": "1", "id": "3701", "name": "배은찬"},
    {"floor": "3층", "room": "310", "bed": "2", "id": "3702", "name": "신우주"},
]
df_students = pd.DataFrame(students_data)

# 비밀번호 딕셔너리 초기화
for sid in df_students['id']:
    if sid not in st.session_state.passwords:
        st.session_state.passwords[sid] = "0000"
if "busanhs" not in st.session_state.passwords:
    st.session_state.passwords["busanhs"] = "dorm2026"

# 벌점 초기화
for sid in df_students['id']:
    if sid not in st.session_state.demerits:
        st.session_state.demerits[sid] = 0

# 기숙사 벌점 부과 기준 정의
demerit_rules = {
    "자정 이후 기숙사 무단 외출 (10점)": 10,
    "비기숙사생과 기숙사 출입 (10점)": 10,
    "화투, 카드, 보드게임 등을 소지 (5점)": 5,
    "출입문 통제 후 비정상적 방법으로 기숙사 출입 (5점)": 5,
    "기숙사 일과시간 미준수 (5점)": 5,
    "지도불응 및 기만(거짓말) (5점)": 5,
    "고의적인 기물 훼손 (5점)": 5,
    "일과 중 기숙사 무단 출입 (5점)": 5,
    "음식물 쓰레기 무단 투기 (5점)": 5,
    "자정 이후 타호실 출입이나 취침 (2점)": 2,
    "호실 내 취침 방해 (2점)": 2,
    "자율학습 불참 또는 분위기 저해 (2점)": 2, # 🛠️ 끝에 쉼표 추가함
    "퇴실 시 정돈 불량 (2점)": 2
}

# --- 학사 일정 데이터 정의 (제공된 자료 기반 중요 일정 발췌) ---
academic_calendar = {
    "2026-03-02": "시업식 및 입학식",
    "2026-03-24": "학평 (1,2,3학년)",
    "2026-03-26": "맞춤형 학업성취도 자율평가 (1,2학년) / 학부모총회",
    "2026-04-06": "영어듣기평가 (1학년)",
    "2026-04-08": "영어듣기평가 (2학년)",
    "2026-04-09": "영어듣기평가 (3학년)",
    "2026-04-27": "1학기 중간고사 시작",
    "2026-04-30": "1학기 중간고사 종료",
    "2026-05-04": "재량휴업일",
    "2026-05-05": "어린이날",
    "2026-05-07": "학평 (3학년)",
    "2026-05-15": "체육한마당",
    "2026-06-03": "지방선거일",
    "2026-06-04": "학평(1,2학년) / 모평(3학년)",
    "2026-06-19": "개교기념식",
    "2026-06-29": "1학기 기말고사 시작",
    "2026-07-03": "1학기 기말고사 종료",
    "2026-07-06": "학교자율교육과정 시작",
    "2026-07-08": "학평 (3학년)",
    "2026-07-16": "방학식",
    "2026-08-18": "2학기 개학식",
    "2026-11-19": "대학수학능력시험일",
    "2026-11-20": "재량휴업일",
    "2026-12-31": "방학식",
}

# --- 크롤링 대용 데이터: 오늘의 식단 ---
@st.cache_data(ttl=3600)
def fetch_diet_info():
    mock_diet = {
        "월요일": {"조식": "흰밥, 미역국, 불고기, 김치", "중식": "돈까스볶음밥, 팽이장국, 떡볶이", "석식": "잡곡밥, 육개장, 고등어구이"},
        "화요일": {"조식": "계란볶음밥, 콩나물국, 소시지", "중식": "비빔밥, 약고추장, 수제비, 만두", "석식": "쌀밥, 부대찌개, 제육볶음"},
        "수요일": {"조식": "누룽지탕, 닭간장조림, 무생채", "중식": "스파게티, 마늘빵, 샐러드, 피클", "석식": "카레라이스, 맑은우동, 치킨가라아게"},
        "목요일": {"조식": "흰밥, 북어해장국, 감자조림", "중식": "낙지비빔밥, 계란파국, 탕수육", "석식": "오곡밥, 순두부찌개, 오리훈제볶음"},
        "금요일": {"조식": "샌드위치, 우유, 시리얼, 바나나", "중식": "칼국수, 주먹밥, 겉절이, 핫도그", "석식": "기숙사 잔류생 없음 (귀가)"}
    }
    return mock_diet


# --- 메인 타이틀 ---
st.title("🏫 2026 부산고등학교 기숙사 통합 시스템")
st.sidebar.markdown("### 🔒 로그인 관리")

# --- (1) 로그인 메뉴 ---
if not st.session_state.logged_in:
    login_mode = st.sidebar.radio("로그인 유형 선택", ["학생용", "교사용"])
    input_id = st.sidebar.text_input("아이디 (학번 또는 교사 ID)")
    input_pw = st.sidebar.text_input("비밀번호", type="password")

    if st.sidebar.button("로그인"):
        if login_mode == "학생용":
            if input_id in st.session_state.passwords and st.session_state.passwords[input_id] == input_pw:
                st.session_state.logged_in = True
                st.session_state.user_type = "student"
                st.session_state.user_id = input_id
                st.rerun()
            else:
                st.sidebar.error("학번 또는 비밀번호가 올바르지 않습니다.")
        else:
            if input_id == "busanhs" and st.session_state.passwords["busanhs"] == input_pw:
                st.session_state.logged_in = True
                st.session_state.user_type = "teacher"
                st.session_state.user_id = "busanhs"
                st.rerun()
            else:
                st.sidebar.error("교사 ID 또는 비밀번호가 올바르지 않습니다.")
else:
    if st.session_state.user_type == "student":
        student_info = df_students[df_students['id'] == st.session_state.user_id].iloc[0]
        st.sidebar.success(f"👋 {student_info['name']} 학생 ({student_info['id']})")

        with st.sidebar.expander("🔑 비밀번호 변경"):
            new_pw = st.text_input("새 비밀번호", type="password")
            if st.button("변경 적용"):
                if new_pw.strip() != "":
                    st.session_state.passwords[st.session_state.user_id] = new_pw
                    st.success("비밀번호가 변경되었습니다.")
                else:
                    st.error("올바른 비밀번호를 입력하세요.")

        current_demerit = st.session_state.demerits.get(st.session_state.user_id, 0)
        if current_demerit >= 10:
            penalty_days = "7일" if current_demerit < 15 else "30일"
            st.error(f"🚨 알림: 월 누적 벌점 {current_demerit}점 초과로 인해 [{penalty_days} 간 퇴사] 대상입니다. 사감실로 문의하세요.")

    else: # 🛠️ 들여쓰기 교정 완료
        st.sidebar.success("👨‍🏫 관리자(교사) 계정 로그인 중")

    if st.sidebar.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.user_id = None
        st.rerun()

# --- 메인 기능 탭 구성 (공지사항을 0번 탭으로 지정) ---
if st.session_state.logged_in:
    tabs = st.tabs(["📢 공지사항", "📝 외박 신청", "📊 벌점 관리", "🍱 오늘의 식단", "📅 학사일정 캘린더", "❓ Q&A 게시판", "🏠 실시간 외박 현황"])

    # --- (8) 공지사항 탭 ---
    with tabs[0]:
        st.header("📢 기숙사 공지사항 게시판")

        # 교사용 공지사항 작성 기능
        if st.session_state.user_type == "teacher":
            with st.expander("✏️ 사감 교사 공지사항 작성하기"):
                notice_title = st.text_input("공지 제목")
                notice_content = st.text_area("공지 내용")
                if st.button("공지사항 등록"):
                    if notice_title and notice_content:
                        st.session_state.notices.insert(0, {
                            "idx": len(st.session_state.notices),
                            "title": notice_title,
                            "content": notice_content,
                            "date": str(datetime.date.today())
                        })
                        st.success("공지사항이 성공적으로 등록되었습니다.")
                        st.rerun()
                    else:
                        st.error("제목과 내용을 모두 작성해 주세요.")

        # 공지사항 목록 표시
        if st.session_state.notices:
            for n in st.session_state.notices:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.subheader(n['title'])
                        st.caption(f"🗓️ 등록일: {n['date']}")
                    with col2:
                        if st.session_state.user_type == "teacher":
                            if st.button("❌ 삭제", key=f"del_notice_{n['idx']}"):
                                st.session_state.notices.remove(n)
                                st.success("공지가 삭제되었습니다.")
                                st.rerun()
                    st.write(n['content'])
                    st.markdown("---")
        else:
            st.info("등록된 기숙사 공지사항이 없습니다.")

    # --- (2) 외박 신청 탭 ---
    with tabs[1]:
        st.header("📝 기숙사 외박 신청 안내")

        if st.session_state.user_type == "student":
            student_id = st.session_state.user_id
            my_outings = [o for o in st.session_state.outings if o['id'] == student_id and o['status'] != '거절']

            if len(my_outings) >= 2:
                st.warning("⚠️ 외박 신청은 주 2회까지 가능합니다. (현재 주 3회 이상 초과 신청 불가)")

            with st.