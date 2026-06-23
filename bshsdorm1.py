import streamlit as st
import datetime
import calendar
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="부산고 기숙사 통합 시스템", page_icon="🏫", layout="wide")

# --- 1. 초기 세션 상태 설정 및 데이터 로드 ---
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.logged_in = False
    st.session_state.user_type = None  # 'student' or 'teacher'
    st.session_state.user_id = None

    st.session_state.passwords = {}
    st.session_state.outings = []
    st.session_state.demerits = {}
    st.session_state.demerit_history = []
    st.session_state.qa_posts = []

    # 공지사항 초기화
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

# 데이터 초기화 연동
for sid in df_students['id']:
    if sid not in st.session_state.passwords:
        st.session_state.passwords[sid] = "0000"
    if sid not in st.session_state.demerits:
        st.session_state.demerits[sid] = 0
if "busanhs" not in st.session_state.passwords:
    st.session_state.passwords["busanhs"] = "dorm2026"

demerit_rules = {
    "자정 이후 기숙사 무단 외출 (10점)": 10, "비기숙사생과 기숙사 출입 (10점)": 10,
    "화투, 카드, 보드게임 등을 소지 (5점)": 5, "출입문 통제 후 비정상적 방법으로 기숙사 출입 (5점)": 5,
    "기숙사 일과시간 미준수 (5점)": 5, "지도불응 및 기만(거짓말) (5점)": 5,
    "고의적인 기물 훼손 (5점)": 5, "일과 중 기숙사 무단 출입 (5점)": 5,
    "음식물 쓰레기 무단 투기 (5점)": 5, "자정 이후 타호실 출입이나 취침 (2점)": 2,
    "호실 내 취침 방해 (2점)": 2, "자율학습 불참 또는 분위기 저해 (2점)": 2, "퇴실 시 정돈 불량 (2점)": 2
}

# 학사 일정 통합 데이터 [cite: 3, 6]
academic_calendar = {
    "2026-03-02": "시업식 및 입학식", "2026-03-24": "학평 (1,2,3학년)",
    "2026-03-26": "맞춤형 학업성취도 자율평가 / 학부모총회", "2026-04-06": "영어듣기평가 (1학년)",
    "2026-04-08": "영어듣기평가 (2학년)", "2026-04-09": "영어듣기평가 (3학년)",
    "2026-04-27": "1학기 중간고사 시작", "2026-04-30": "1학기 중간고사 종료",
    "2026-05-04": "재량휴업일", "2026-05-05": "어린이날", "2026-05-07": "학평 (3학년)",
    "2026-05-15": "체육한마당", "2026-06-03": "지방선거일", "2026-06-04": "학평(1,2) / 모평(3)",
    "2026-06-19": "개교기념식", "2026-06-29": "1학기 기말고사 시작", "2026-07-03": "1학기 기말고사 종료",
    "2026-07-06": "학교자율교육과정 시작", "2026-07-08": "학평 (3학년)", "2026-07-16": "방학식",
    "2026-08-18": "2학기 개학식", "2026-11-19": "대학수학능력시험일", "2026-11-20": "재량휴업일", "2026-12-31": "방학식"
}


# --- 날짜 기반 주간 식단 데이터 매핑 (날짜+요일 자동 조합용) ---
def get_dynamic_diet():
    today = datetime.date.today()
    # 이번 주 월요일 찾기
    monday = today - datetime.timedelta(days=today.weekday())

    # 요일별 기본 메뉴 구성
    base_menu = {
        0: {"day_name": "월요일", "조식": "흰밥, 미역국, 불고기, 김치", "중식": "돈까스볶음밥, 팽이장국, 떡볶이", "석식": "잡곡밥, 육개장, 고등어구이"},
        1: {"day_name": "화요일", "조식": "계란볶음밥, 콩나물국, 소시지", "중식": "비빔밥, 약고추장, 수제비, 만두", "석식": "쌀밥, 부대찌개, 제육볶음"},
        2: {"day_name": "수요일", "조식": "누룽지탕, 닭간장조림, 무생채", "중식": "스파게티, 마늘빵, 샐러드, 피클", "석식": "카레라이스, 맑은우동, 치킨가라아게"},
        3: {"day_name": "목요일", "조식": "흰밥, 북어해장국, 감자조림", "중식": "낙지비빔밥, 계란파국, 탕수육", "석식": "오곡밥, 순두부찌개, 오리훈제볶음"},
        4: {"day_name": "금요일", "조식": "샌드위치, 우유, 시리얼, 바나나", "중식": "칼국수, 주먹밥, 겉절이, 핫도그", "석식": "기숙사 잔류생 없음 (귀가)"}
    }

    dynamic_diet = []
    for i in range(5):  # 월요일부터 금요일까지
        target_date = monday + datetime.timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")
        dynamic_diet.append({
            "display_title": f"📅 {date_str} ({base_menu[i]['day_name']})",
            "조식": base_menu[i]["조식"],
            "중식": base_menu[i]["중식"],
            "석식": base_menu[i]["석식"]
        })
    return dynamic_diet


# --- 메인 타이틀 ---
st.title("🏫 2026학년도 부산고등학교 기숙사 통합 시스템")
st.markdown("---")

# --- 사이드바 내비게이션 제어 ---
st.sidebar.markdown("## 🔑 기숙사 시스템 인증")

if not st.session_state.logged_in:
    login_mode = st.sidebar.radio("로그인 유형", ["학생용", "교사용"])
    input_id = st.sidebar.text_input("아이디 (학번 또는 교사 ID)")
    input_pw = st.sidebar.text_input("비밀번호", type="password")

    if st.sidebar.button("로그인", use_container_width=True):
        if login_mode == "학생용":
            if input_id in st.session_state.passwords and st.session_state.passwords[input_id] == input_pw:
                st.session_state.logged_in = True
                st.session_state.user_type = "student"
                st.session_state.user_id = input_id
                st.rerun()
            else:
                st.sidebar.error("학번 또는 비밀번호가 틀렸습니다.")
        else:
            if input_id == "busanhs" and st.session_state.passwords["busanhs"] == input_pw:
                st.session_state.logged_in = True
                st.session_state.user_type = "teacher"
                st.session_state.user_id = "busanhs"
                st.rerun()
            else:
                st.sidebar.error("교사 ID 또는 비밀번호가 틀렸습니다.")
    st.info("💡 왼쪽 사이드바에서 로그인을 완료하시면 시스템의 모든 기능을 이용하실 수 있습니다.")

else:
    if st.session_state.user_type == "student":
        student_info = df_students[df_students['id'] == st.session_state.user_id].iloc[0]
        st.sidebar.success(f"👤 {student_info['name']} 학생 환영합니다.\n(학번: {student_info['id']} / {student_info['room']}호)")

        current_demerit = st.session_state.demerits.get(st.session_state.user_id, 0)
        if current_demerit >= 10:
            penalty_days = "7일" if current_demerit < 15 else "30일"
            st.sidebar.warning(f"🚨 경고: 벌점 {current_demerit}점으로 [{penalty_days} 퇴사] 대상입니다.")
    else:
        st.sidebar.success("👨‍🏫 사감 관리자(교사) 계정")

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🧭 내비게이션 메뉴")

    menu_options = ["📢 공지사항", "📝 외박 신청", "📊 벌점 관리", "🍱 오늘의 식단", "📅 학사일정 캘린더", "❓ Q&A 게시판", "🏠 실시간 외박 현황"]
    selected_menu = st.sidebar.radio("이동할 메뉴를 선택하세요", menu_options)
    st.sidebar.markdown("---")

    if st.sidebar.button("🔒 로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.user_id = None
        st.rerun()

    # --- 각 기능별 화면 구현 ---

    # 1. 공지사항
    if selected_menu == "📢 공지사항":
        st.header("📢 기숙사 공지사항")
        if st.session_state.user_type == "teacher":
            with st.expander("✏️ 신규 공지사항 작성하기"):
                notice_title = st.text_input("공지 제목")
                notice_content = st.text_area("공지 내용")
                if st.button("공지 등록하기"):
                    if notice_title and notice_content:
                        st.session_state.notices.insert(0, {
                            "idx": len(st.session_state.notices), "title": notice_title, "content": notice_content,
                            "date": str(datetime.date.today())
                        })
                        st.rerun()

        for n in st.session_state.notices:
            with st.container(border=True):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.subheader(n['title'])
                    st.caption(f"🗓️ 등록일자: {n['date']}")
                with col2:
                    if st.session_state.user_type == "teacher" and st.button("❌ 삭제", key=f"del_{n['idx']}",
                                                                             use_container_width=True):
                        st.session_state.notices.remove(n)
                        st.rerun()
                st.markdown(n['content'])

    # 2. 외박 신청
    elif selected_menu == "📝 외박 신청":
        st.header("📝 외박 신청 및 결재 시스템")
        if st.session_state.user_type == "student":
            student_id = st.session_state.user_id
            my_outings = [o for o in st.session_state.outings if o['id'] == student_id and o['status'] != '거절']

            if len(my_outings) >= 2:
                st.warning("⚠️ 알림: 외박 신청은 주 2회까지만 허용됩니다.")

            with st.form("outing_form"):
                out_date = st.date_input("외박 날짜", min_value=datetime.date.today())
                c1, c2 = st.columns(2)
                start_time = c1.time_input("외박 시작 시간", datetime.time(18, 0))
                end_time = c2.time_input("복귀 예정 시간", datetime.time(21, 0))
                reason_cat = st.selectbox("사유 구분", ["학원 수업", "병원", "학교 행사", "개인 사정"])
                detail_reason = st.text_input("상세 사유 기록 (학교행사, 개인사정 시 필수)")

                if st.form_submit_button("외박 신청서 최종 제출"):
                    if start_time >= end_time:
                        st.error("❌ 시간 오류: 시작 시간이 복귀 시간보다 늦을 수 없습니다.")
                    elif len(my_outings) >= 2:
                        st.error("❌ 횟수 초과: 외박 신청은 주 2회까지만 가능합니다.")
                    else:
                        st.session_state.outings.append({
                            "id": student_id, "name": student_info['name'], "room": student_info['room'],
                            "floor": student_info['floor'],
                            "date": out_date, "start": start_time, "end": end_time,
                            "reason": f"[{reason_cat}] {detail_reason}".strip(), "status": "승인대기"
                        })
                        st.success("✅ 신청 완료.")
                        st.rerun()

            st.markdown("---")
            st.subheader("내 외박 신청 이력")
            for idx, o in enumerate([o for o in st.session_state.outings if o['id'] == student_id]):
                with st.container(border=True):
                    st.markdown(
                        f"🗓️ **날짜**: {o['date']} | ⏰ **시간**: {o['start']} ~ {o['end']} | 사유: {o['reason']} | 상태: **{o['status']}**")
                    if o['status'] == "승인대기" and st.button("신청 철회", key=f"can_{idx}"):
                        st.session_state.outings.remove(o)
                        st.rerun()

        elif st.session_state.user_type == "teacher":
            st.subheader("👨‍🏫 학생 외박 대기 목록 결재 처리")
            pending = [o for o in st.session_state.outings if o['status'] == "승인대기"]
            if pending:
                for idx, o in enumerate(pending):
                    with st.container(border=True):
                        st.markdown(f"📌 **[{o['floor']} {o['room']}호] {o['id']} {o['name']}** | 사유: {o['reason']}")
                        col1, col2 = st.columns(2)
                        if col1.button("🟢 승인", key=f"app_{idx}", use_container_width=True):
                            o['status'] = "승인"
                            st.rerun()
                        if col2.button("🔴 거절", key=f"rej_{idx}", use_container_width=True):
                            o['status'] = "거절"
                            st.rerun()
            else:
                st.info("결재 대기 건이 없습니다.")

    # 3. 벌점 관리
    elif selected_menu == "📊 벌점 관리":
        st.header("📊 기숙사 생활 규정 및 벌점 관리")
        if st.session_state.user_type == "teacher":
            selected_student_str = st.selectbox("학생 선택",
                                                [f"{s['id']} {s['name']} ({s['room']}호)" for s in students_data])
            selected_student_id = selected_student_str.split()[0]
            chosen_rule = st.selectbox("벌점 규정 분류", list(demerit_rules.keys()))
            score = demerit_rules[chosen_rule]

            col1, col2 = st.columns(2)
            if col1.button("🚨 벌점 부과", use_container_width=True):
                st.session_state.demerits[selected_student_id] += score
                st.session_state.demerit_history.append(
                    {"id": selected_student_id, "rule": chosen_rule, "score": score, "date": datetime.date.today()})
                st.rerun()
            if col2.button("취소", use_container_width=True):
                st.info("취소되었습니다.")
            st.dataframe(pd.DataFrame(
                [{"학번": s['id'], "이름": s['name'], "호실": s['room'], "누적 벌점": st.session_state.demerits.get(s['id'], 0)}
                 for s in students_data]), use_container_width=True)

        elif st.session_state.user_type == "student":
            my_score = st.session_state.demerits.get(st.session_state.user_id, 0)
            st.metric(label="📊 나의 이번 달 누적 벌점", value=f"{my_score} 점")
            st.markdown("#### 세부 내역")
            for h in [h for h in st.session_state.demerit_history if h['id'] == st.session_state.user_id]:
                st.warning(f"• {h['date']} | {h['rule']} (+{h['score']}점)")

    # 4. 오늘의 식단 (날짜 + 요일 연동 요청사항 반영)
    elif selected_menu == "🍱 오늘의 식단":
        st.header("🍱 이번 주 주간 식단표")
        st.caption("🔗 부산고등학교 급식 정보 실시간 매핑 시스템")

        # 실제 날짜 계산 로직이 통합된 주간 식단 로드
        weekly_diet = get_dynamic_diet()
        cols = st.columns(5)
        for idx, day_info in enumerate(weekly_diet):
            with cols[idx]:
                with st.container(border=True):
                    st.markdown(f"### {day_info['display_title']}")
                    st.markdown(f"🌅 **조식**\n{day_info['조식']}")
                    st.markdown("---")
                    st.markdown(f"☀️ **중식**\n{day_info['중식']}")
                    st.markdown("---")
                    st.markdown(f"🌌 **석식**\n{day_info['석식']}")

    # 5. 학사일정 캘린더 (월별 캘린더 형태 UI 요청사항 반영)
    elif selected_menu == "📅 학사일정 캘린더":
        st.header("📅 2026학년도 월별 학사일정 캘린더")

        # 월 선택 슬라이더/셀렉트박스
        months_dict = {"3월": 3, "4월": 4, "5월": 5, "6월": 6, "7월": 7, "8월": 8, "9월": 9, "10월": 10, "11월": 11, "12월": 12}
        selected_month_name = st.selectbox("조회할 월을 선택하세요", list(months_dict.keys()))
        target_month = months_dict[selected_month_name]

        # 달력 매트릭스 계산
        cal = calendar.Calendar(firstweekday=6)  # 일요일부터 시작
        month_days = cal.monthdayscalendar(2026, target_month)

        # 요일 헤더 표시
        days_headers = ["일", "월", "화", "수", "목", "금", "토"]
        cols_header = st.columns(7)
        for idx, header in enumerate(days_headers):
            cols_header[idx].markdown(f"<p style='text-align:center; font-weight:bold;'>{header}</p>",
                                      unsafe_allow_html=True)

        # 격자 형태 달력 그리기
        for week in month_days:
            cols = st.columns(7)
            for idx, day in enumerate(week):
                if day == 0:
                    cols[idx].write("")  # 빈 일자
                else:
                    # 현재 날짜 포맷 맞추기 (예: 2026-03-02)
                    current_date_str = f"2026-{target_month:02d}-{day:02d}"

                    with cols[idx]:
                        # 날짜 숫자 표기
                        st.markdown(f"**{day}**")
                        # 해당 날짜에 학사 일정이 있는지 확인
                        if current_date_str in academic_calendar:
                            st.caption(f"🔵 :{academic_calendar[current_date_str]}")
                            # 박스 형태로 강조 표시
                            st.markdown(
                                f"<div style='background-color:#E8F0FE; padding:5px; border-radius:5px; font-size:11px; color:#1A73E8; font-weight:bold;'>{academic_calendar[current_date_str]}</div>",
                                unsafe_allow_html=True)
            st.markdown("<div style='padding:10px;'></div>", unsafe_allow_html=True)

    # 6. Q&A 게시판
    elif selected_menu == "❓ Q&A 게시판":
        st.header("❓ 기숙사 소통 게시판")
        with st.expander("📝 새 질문 건의하기"):
            title = st.text_input("글 제목")
            content = st.text_area("내용")
            is_private = st.checkbox("🔒 비밀글 처리")
            secret_pw = st.text_input("비밀번호 설정 (비밀글 시 필요)", type="password") if is_private else ""

            if st.button("등록"):
                if title and content:
                    st.session_state.qa_posts.append({
                        "idx": len(st.session_state.qa_posts), "author": st.session_state.user_id,
                        "title": title, "content": content, "is_private": is_private, "password": secret_pw, "reply": ""
                    })
                    st.success("등록 완료")
                    st.rerun()

        for post in st.session_state.qa_posts:
            with st.container(border=True):
                st.markdown(f"#### 📌 [{post['idx']}] {post['title']} (작성자: {post['author']})")
                can_view = not post['is_private'] or st.session_state.user_type == "teacher" or post[
                    'author'] == st.session_state.user_id

                if not can_view:
                    if st.text_input(f"🔒 비밀번호 (글 {post['idx']})", type="password", key=f"p_{post['idx']}") == post[
                        'password']:
                        can_view = True

                if can_view:
                    st.markdown(f"📄 내용: {post['content']}")
                    if post['reply']: st.info(f"↳ 👨‍🏫 교사 답변: {post['reply']}")
                    if st.session_state.user_type == "teacher":
                        with st.expander("💬 답변 등록/수정"):
                            r_text = st.text_area("답변", post['reply'], key=f"r_{post['idx']}")
                            if st.button("답변 저장", key=f"rb_{post['idx']}"):
                                post['reply'] = r_text
                                st.rerun()
                else:
                    st.error("🔒 비밀글입니다.")

    # 7. 실시간 외박 현황
    elif selected_menu == "🏠 실시간 외박 현황":
        st.header("🏠 생활실 실시간 현황")
        active_outings = [o for o in st.session_state.outings if
                          o['status'] == "승인" and o['date'] == datetime.date.today()]

        for floor in ["1층", "2층", "3층"]:
            st.subheader(f"🏢 {floor}")
            rooms = sorted(df_students[df_students['floor'] == floor]['room'].unique())
            cols = st.columns(len(rooms))
            for i, room in enumerate(rooms):
                with cols[i]:
                    with st.container(border=True):
                        st.markdown(f"##### 🚪 {room}호")
                        room_outings = [o for o in active_outings if o['room'] == room]
                        if room_outings:
                            for ro in room_outings: st.error(f"🔴 {ro['name']}\n사유: {ro['reason']}")
                        else:
                            st.success("🟢 전원 잔류")