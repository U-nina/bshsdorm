import streamlit as st
import datetime
import calendar
import pandas as pd
import requests
import re

# 페이지 기본 설정
st.set_page_config(page_title="부산고 기숙사 통합 시스템", page_icon="🏫", layout="wide")

# --- 단어 잘림 방지를 위한 전역 CSS 주입 (요구사항 7 반영) ---
st.markdown("""
    <style>
    div, p, span, h1, h2, h3, h4, h5, h6, label, button, .stButton {
        word-break: keep-all !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. 초기 세션 상태 설정 및 데이터 로드 ---
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.user_id = None

    st.session_state.passwords = {}
    st.session_state.outings = []
    st.session_state.demerits = {}
    st.session_state.demerit_history = []

    st.session_state.qa_posts = [
        {"idx": 0, "author": "1102", "title": "기숙사 온수 사용 시간 문의", "content": "겨울철에 온수가 몇 시부터 몇 시까지 나오나요?",
         "is_private": False, "password": "", "reply": "사감실입니다. 온수는 아침 6시~8시, 저녁 7시~11시까지 공급됩니다."},
        {"idx": 1, "author": "1201", "title": "개인 자습용 스탠드 반입 가능한가요?", "content": "방에서 쓸 스탠드 가져가도 되는지 궁금합니다.",
         "is_private": True, "password": "1234", "reply": ""}
    ]

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

academic_calendar = {
    "2026-03-02": "시업식 및 입학식", "2026-03-24": "학평 (1,2,3학년)",
    "2026-03-26": "맞춤형 학업성취도 자율평가 / 학부모총회", "2026-04-06": "영어듣기평가 (1학년)",
    "2026-04-08": "영어듣기평가 (2학년)", "2026-04-09": "영어듣기평가 (3학년)",
    "2026-04-27": "1학기 중간고사 시작", "2026-04-30": "1학기 중간고사 종료",
    "2026-05-04": "재량휴업일", "2026-05-05": "어린이날", "2026-05-07": "학평 (3학년)",
    "2026-05-15": "체육한마당", "2026-06-03": "지방선거일", "2026-06-04": "학평(1,2) / 모평(3)",
    "2026-06-19": "개교기념식", "2026-06-29": "1학기 기말고사 시작", "2026-07-03": "1학기 기말고사 종료",
    "2026-07-06": "학교자율교육과정 시작", "2026-07-08": "학평 (3학년)", "2026-07-16": "방학식",
    "2026-08-18": "2학기 개학식", "2026-11-19": "대학수학능력시험일", "2026-11-20": "재량휴업일", "2026-12-31": "방학식",
    "2027-01-05": "2학기 기말고사(1,2학년)", "2027-01-08": "기말고사 종료",
    "2027-01-15": "겨울방학식(기숙사 전체 일시 귀사)", "2027-02-05": "부산고 졸업식 및 종업식"
}


# --- 나이스 API 호출 함수 (🛠️ KeyError 해결을 위한 예외처리 보완) ---
def fetch_neis_diet(target_date_str):
    """
    나이스 API를 이용하여 부산고등학교의 특정 날짜 식단을 실시간으로 가져옵니다.
    """
    # ⚠️ 아래 따옴표 안에 발급받으신 나이스 공식 인증키 32자리를 꼭 넣어주세요!
    api_key = "YOUR_API_KEY"
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"

    params = {
        "KEY": api_key,
        "Type": "json",
        "pIndex": 1,
        "pSize": 10,
        "ATPT_OFCDC_SC_CODE": "C10",  # 부산광역시교육청
        "SD_SCHUL_CODE": "7150073",  # 부산고등학교
        "MLSV_YMD": target_date_str.replace("-", "")
    }

    diet_result = {"조식": "등록된 식단이 없습니다.", "중식": "등록된 식단이 없습니다.", "석식": "등록된 식단이 없습니다."}

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        # 🛠️ [핵심 교정] 데이터 수신 차단 또는 인증키 대기 상태 시 KeyError 방어
        if "mealServiceDietInfo" in data:
            row_data = data["mealServiceDietInfo"][1]["row"]
            for row in row_data:
                meal_type = row["MMEAL_SC_NM"]
                menu_text = row["DDISH_NM"]

                # HTML 태그 및 알레르기 유발 물질 번호 정제
                menu_clean = menu_text.replace("<br/>", ", ")
                menu_clean = re.sub(r'[0-9]+\.', '', menu_clean)

                if "조식" in meal_type:
                    diet_result["조식"] = menu_clean
                elif "중식" in meal_type:
                    diet_result["중식"] = menu_clean
                elif "석식" in meal_type:
                    diet_result["석식"] = menu_clean
        else:
            # 나이스 서버에서 정상 데이터를 받지 못했을 때 안내 문구 처리
            error_msg = "인증키 승인 대기 중이거나 식단이 없는 날입니다."
            if "RESULT" in data and "MESSAGE" in data["RESULT"]:
                error_msg = f"안내: {data['RESULT']['MESSAGE']}"
            return {"조식": error_msg, "중식": error_msg, "석식": error_msg}

        return diet_result
    except Exception as e:
        return {"조식": "데이터 로드 실패", "중식": "네트워크 연결 확인 필요", "석식": "사감실 문의"}


# --- 2. 내비게이션 메뉴 구성 ---
st.sidebar.markdown("## 🧭 내비게이션 메뉴")
menu_options = ["📢 공지사항", "📝 외박 신청", "📊 벌점 관리", "🍱 오늘의 식단", "📅 학사일정 캘린더", "❓ Q&A 게시판", "🏠 실시간 외박 현황"]
selected_menu = st.sidebar.radio("이동할 메뉴를 선택하세요", menu_options)
st.sidebar.markdown("---")

# --- 3. 사용자 인증 및 패스워드 마이페이지 ---
st.sidebar.markdown("## 🔑 사용자 로그인")

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
else:
    if st.session_state.user_type == "student":
        student_info = df_students[df_students['id'] == st.session_state.user_id].iloc[0]
        st.sidebar.success(
            f"👤 {student_info['name']} 학생 환영합니다.  \n(학번: {student_info['id']} / {student_info['room']}호)")

        current_demerit = st.session_state.demerits.get(st.session_state.user_id, 0)
        if current_demerit >= 10:
            penalty_days = "7일" if current_demerit < 15 else "30일"
            st.sidebar.warning(f"🚨 경고: 벌점 {current_demerit}점으로 [{penalty_days} 퇴사] 대상입니다.")
    else:
        st.sidebar.success("👨‍🏫 관리자(교사) 계정 로그인 중")

    if st.session_state.user_type == "student":
        with st.sidebar.expander("🔑 비밀번호 변경하기"):
            new_pw = st.text_input("새 비밀번호 입력", type="password")
            if st.button("비밀번호 변경 적용", use_container_width=True):
                if new_pw.strip():
                    st.session_state.passwords[st.session_state.user_id] = new_pw
                    st.success("✅ 비밀번호가 변경되었습니다.")
                else:
                    st.error("❌ 올바른 비밀번호를 입력해 주세요.")

    if st.sidebar.button("🔒 로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.user_id = None
        st.rerun()


def check_login_permission():
    if not st.session_state.logged_in:
        st.warning("🔒 이 메뉴는 로그인 후 이용하실 수 있는 서비스입니다. 왼쪽 사용자 로그인 메뉴에서 먼저 로그인을 진행해 주세요.")
        return False
    return True


# --- 메인 본문 핵심 렌더링 영역 ---

# 1. 공지사항
if selected_menu == "📢 공지사항":
    st.header("📢 기숙사 공지사항 게시판")
    if st.session_state.user_type == "teacher" and st.session_state.logged_in:
        with st.expander("✏️ 교사 공지사항 신규 작성"):
            notice_title = st.text_input("공지 제목")
            notice_content = st.text_area("공지 내용")
            if st.button("공지사항 등록"):
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
                if st.session_state.user_type == "teacher" and st.session_state.logged_in:
                    if st.button("❌ 삭제", key=f"del_{n['idx']}", use_container_width=True):
                        st.session_state.notices.remove(n)
                        st.rerun()
            st.markdown(n['content'])

# 2. 외박 신청
elif selected_menu == "📝 외박 신청":
    st.header("📝 외박 신청 및 결재 시스템")
    if check_login_permission():
        if st.session_state.user_type == "student":
            student_id = st.session_state.user_id
            my_outings = [o for o in st.session_state.outings if o['id'] == student_id and o['status'] != '거절']

            if len(my_outings) >= 2:
                st.warning("⚠️ 알림: 외박 신청은 주 2회까지만 허용됩니다.")

            with st.form("outing_form"):
                st.markdown("#### 📋 외박 신청서 작성")
                out_date = st.date_input("외박 날짜 선택", min_value=datetime.date.today())
                c1, c2 = st.columns(2)
                start_time = c1.time_input("외박 시작 시간", datetime.time(18, 0))
                end_time = c2.time_input("복귀 예정 시간", datetime.time(21, 0))
                reason_cat = st.selectbox("사유 선택", ["학원 수업", "병원", "학교 행사", "개인 사정"])
                detail_reason = st.text_input("상세 구체적 사유 기록 (학교 행사, 개인 사정 선택 시 필수입력)")

                if st.form_submit_button("외박 신청"):
                    if reason_cat in ["학교 행사", "개인 사정"] and not detail_reason.strip():
                        st.error("❌ 신청 실패: '학교 행사' 또는 '개인 사정'은 구체적인 상세 사유를 반드시 적어주셔야 신청이 가능합니다.")
                    elif start_time >= end_time:
                        st.error("❌ 시간 오류: 시작 시간이 복귀 시간보다 늦거나 같을 수 없습니다.")
                    elif len(my_outings) >= 2:
                        st.error("❌ 신청 차단: '외박 신청은 주 2회까지 가능합니다.'")
                    else:
                        st.session_state.outings.append({
                            "id": student_id, "name": student_info['name'], "room": student_info['room'],
                            "floor": student_info['floor'],
                            "date": out_date, "start": start_time, "end": end_time,
                            "reason": f"[{reason_cat}] {detail_reason}".strip(), "status": "승인대기"
                        })
                        st.success("✅ 외박 신청서가 정상적으로 접수되었습니다.")
                        st.rerun()

            st.markdown("---")
            st.subheader("외박 신청 내역 및 결과")
            for idx, o in enumerate([o for o in st.session_state.outings if o['id'] == student_id]):
                with st.container(border=True):
                    st.markdown(
                        f"🗓️ **날짜**: {o['date']} | ⏰ **시간**: {o['start']} ~ {o['end']} | 사유: {o['reason']} | 상태: **{o['status']}**")
                    if o['status'] == "승인대기" and st.button("신청 취소", key=f"can_{idx}"):
                        st.session_state.outings.remove(o)
                        st.rerun()

        elif st.session_state.user_type == "teacher":
            st.subheader("👨‍🏫 학생 외박 신청 결재 승인/거절 권한 관리")
            pending = [o for o in st.session_state.outings if o['status'] == "승인대기"]
            if pending:
                for idx, o in enumerate(pending):
                    with st.container(border=True):
                        st.markdown(f"📌 **[{o['floor']} {o['room']}호] {o['id']} {o['name']}** | 사유: {o['reason']}")
                        col1, col2 = st.columns(2)
                        if col1.button("🟢 교사 승인", key=f"app_{idx}", use_container_width=True):
                            o['status'] = "승인"
                            st.rerun()
                        if col2.button("🔴 교사 거절", key=f"rej_{idx}", use_container_width=True):
                            o['status'] = "거절"
                            st.rerun()
            else:
                st.info("결재 처리를 기다리는 외박 대기 신청 건이 없습니다.")

# 3. 벌점 관리
elif selected_menu == "📊 벌점 관리":
    st.header("📊 기숙사 생활 규정 벌점 관리")
    if check_login_permission():
        if st.session_state.user_type == "teacher":
            st.subheader("교사 벌점 부여 통제")
            selected_student_str = st.selectbox("학생 선택",
                                                [f"{s['id']} {s['name']} ({s['room']}호)" for s in students_data])
            selected_student_id = selected_student_str.split()[0]
            chosen_rule = st.selectbox("기숙사 벌점 부과 기준 선택", list(demerit_rules.keys()))
            score = demerit_rules[chosen_rule]

            col1, col2 = st.columns(2)
            if col1.button("🚨 벌점 부과", use_container_width=True):
                st.session_state.demerits[selected_student_id] += score
                st.session_state.demerit_history.append(
                    {"id": selected_student_id, "rule": chosen_rule, "score": score, "date": datetime.date.today()})
                st.success("벌점이 성공적으로 부과되었습니다.")
                st.rerun()
            if col2.button("취소 버튼", use_container_width=True):
                st.info("벌점 배정 입력이 취소 처리되었습니다.")

            st.markdown("---")
            st.dataframe(pd.DataFrame(
                [{"학번": s['id'], "이름": s['name'], "호실": s['room'], "누적 벌점": st.session_state.demerits.get(s['id'], 0)}
                 for s in students_data]), use_container_width=True)

        elif st.session_state.user_type == "student":
            my_score = st.session_state.demerits.get(st.session_state.user_id, 0)
            st.metric(label="📊 이번 달 나의 누적 벌점 현황", value=f"{my_score} 점")

            if my_score >= 10:
                p_days = "7일" if my_score < 15 else "30일"
                st.error(f"🚨 안내 알림: 월 단위 벌점 10점 초과로 인하여 귀하는 [{p_days} 간 퇴사] 지도대상입니다. 사감실로 방문하세요.")

            st.markdown("#### 상세 벌점 부과 내역")
            for h in [h for h in st.session_state.demerit_history if h['id'] == st.session_state.user_id]:
                st.warning(f"• {h['date']} | {h['rule']} (+{h['score']}점)")

# 4. 오늘의 식단
elif selected_menu == "🍱 오늘의 식단":
    st.header("🍱 주간 기숙사 식단표 조회 시스템")
    st.caption("🔗 교육부 나이스(NEIS) 오픈 API를 활용하여 부산고등학교 급식 정보를 정확하게 출력합니다.")

    week_select = st.selectbox("📅 조회할 급식 주차를 선택하세요", ["2026년 6월 3주차 식단", "2026년 6월 4주차 식단"])

    if "3주차" in week_select:
        monday = datetime.date(2026, 6, 15)
    else:
        monday = datetime.date(2026, 6, 22)

    day_names = ["월요일", "화요일", "수요일", "목요일", "금요일"]
    cols = st.columns(5)

    for i in range(5):
        target_date = monday + datetime.timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")

        with st.spinner(f"{date_str} 조회 중..."):
            diet_info = fetch_neis_diet(date_str)

        with cols[i]:
            with st.container(border=True):
                st.markdown(f"### {date_str} ({day_names[i]})")
                st.markdown(f"🌅 **조식**\n{diet_info['조식']}")
                st.markdown("---")
                st.markdown(f"☀️ **중식**\n{diet_info['중식']}")
                st.markdown("---")
                st.markdown(f"🌌 **석식**\n{diet_info['석식']}")

# 5. 학사일정 캘린더
elif selected_menu == "📅 학사일정 캘린더":
    st.header("📅 학사일정 월별 스마트 캘린더")

    year_choice = st.selectbox("📆 조회 연도 선택", [2026, 2027])
    if year_choice == 2026:
        months_list = ["3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"]
    else:
        months_list = ["1월", "2월"]

    selected_month_name = st.selectbox("조회 대상 월 선택", months_list)
    target_month = int(selected_month_name.replace("월", ""))

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year_choice, target_month)

    cols_header = st.columns(7)
    days_headers = [
        "<span style='color:red; font-weight:bold;'>일</span>",
        "<span style='font-weight:bold;'>월</span>",
        "<span style='font-weight:bold;'>화</span>",
        "<span style='font-weight:bold;'>수</span>",
        "<span style='font-weight:bold;'>목</span>",
        "<span style='font-weight:bold;'>금</span>",
        "<span style='color:blue; font-weight:bold;'>토</span>"
    ]
    for idx, header_html in enumerate(days_headers):
        cols_header[idx].markdown(f"<p style='text-align:center;'>{header_html}</p>", unsafe_allow_html=True)

    for week in month_days:
        cols = st.columns(7)
        for idx, day in enumerate(week):
            if day == 0:
                cols[idx].write("")
            else:
                current_date_str = f"{year_choice}-{target_month:02d}-{day:02d}"
                with cols[idx]:
                    if idx == 0:
                        st.markdown(f"<span style='color:red; font-weight:bold;'>{day}</span>", unsafe_allow_html=True)
                    elif idx == 6:
                        st.markdown(f"<span style='color:blue; font-weight:bold;'>{day}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{day}**")

                    if current_date_str in academic_calendar:
                        st.markdown(
                            f"<div style='background-color:#E8F0FE; padding:5px; border-radius:5px; font-size:11px; color:#1A73E8; font-weight:bold;'>{academic_calendar[current_date_str]}</div>",
                            unsafe_allow_html=True)
        st.markdown("<div style='padding:5px;'></div>", unsafe_allow_html=True)

# 6. Q&A 게시판
elif selected_menu == "❓ Q&A 게시판":
    st.header("❓ 기숙사 소통 Q&A 게시판")

    if "qa_view" not in st.session_state:
        st.session_state.qa_view = "list"

    c1, c2 = st.columns(2)
    if c1.button("📋 질문 목록 보기", use_container_width=True):
        st.session_state.qa_view = "list"
    if c2.button("📝 새 질문 글 올리기", use_container_width=True):
        if check_login_permission():
            st.session_state.qa_view = "write"

    st.markdown("---")

    if st.session_state.qa_view == "write" and st.session_state.logged_in:
        with st.container(border=True):
            st.subheader("📝 기숙사 건의 및 질문 글 쓰기")
            title = st.text_input("질문 글 제목")
            content = st.text_area("질문 상세 내용")
            is_private = st.checkbox("🔒 비밀글로 작성하기")
            secret_pw = ""
            if is_private:
                secret_pw = st.text_input("비밀글 확인용 암호 설정", type="password")

            if st.button("질문 등록 완료"):
                if title and content:
                    st.session_state.qa_posts.insert(0, {
                        "idx": len(st.session_state.qa_posts), "author": st.session_state.user_id,
                        "title": title, "content": content, "is_private": is_private, "password": secret_pw, "reply": ""
                    })
                    st.success("✅ 질문이 정상 등록되었습니다.")
                    st.session_state.qa_view = "list"
                    st.rerun()
                else:
                    st.error("❌ 제목과 내용을 채워주세요.")

    elif st.session_state.qa_view == "list":
        st.subheader("📋 기숙사 질의응답 피드 목록")
        if st.session_state.qa_posts:
            for post in st.session_state.qa_posts:
                with st.container(border=True):
                    st.markdown(f"#### 📌 [{post['idx']}] {post['title']}")
                    st.caption(f"작성유저 ID: {post['author']} | 비밀글 여부: {'예' if post['is_private'] else '아니오'}")

                    can_view = True
                    if post['is_private']:
                        if st.session_state.logged_in and (
                                st.session_state.user_type == "teacher" or post['author'] == st.session_state.user_id):
                            can_view = True
                        else:
                            can_view = False
                            input_key_pw = st.text_input(f"🔒 비밀글 암호를 입력하세요 (글번호: {post['idx']})", type="password",
                                                         key=f"pw_{post['idx']}")
                            if input_key_pw == post['password']:
                                can_view = True

                    if can_view:
                        st.markdown(f"📄 **본문**: {post['content']}")
                        if post['reply']:
                            st.info(f"↳ 👨‍🏫 **교사 답글**: {post['reply']}")
                        else:
                            st.warning("↳ 선생님이 답변을 건의 검토 중입니다.")

                        if st.session_state.logged_in and post['author'] == st.session_state.user_id:
                            with st.expander("✏️ 내 글 수정하기"):
                                edit_content = st.text_area("내용 수정란", post['content'], key=f"edit_{post['idx']}")
                                if st.button("수정 완료", key=f"edit_btn_{post['idx']}"):
                                    post['content'] = edit_content
                                    st.success("수정 완료!")
                                    st.rerun()

                        if st.session_state.logged_in and st.session_state.user_type == "teacher":
                            with st.expander("💬 교사용 답글 달기 및 수정"):
                                r_text = st.text_area("답변 작성", post['reply'], key=f"r_{post['idx']}")
                                if st.button("답글 저장 완료", key=f"rb_{post['idx']}"):
                                    post['reply'] = r_text
                                    st.rerun()
                    else:
                        st.error("🔒 본인 혹은 선생님만 열람할 수 있도록 설정된 비밀글입니다.")
        else:
            st.caption("등록된 소통 질문 게시글이 비어 있습니다.")

# 7. 실시간 외박 현황
elif selected_menu == "🏠 실시간 외박 현황":
    st.header("🏠 생활실별 외박 현황 실시간 모니터링")

    search_date = st.date_input("조회 대상을 지정할 해당일자 선택", datetime.date.today())
    st.caption(f"📅 현재 화면 데이터 기준일자: **{search_date}**")

    active_outings = [o for o in st.session_state.outings if o['status'] == "승인" and str(o['date']) == str(search_date)]

    for floor in ["1층", "2층", "3층"]:
        st.subheader(f"🏢 {floor} 생활관")
        rooms = sorted(df_students[df_students['floor'] == floor]['room'].unique())
        cols = st.columns(len(rooms))

        for i, room in enumerate(rooms):
            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"##### 🚪 {room}호")
                    room_outings = [o for o in active_outings if o['room'] == room]
                    if room_outings:
                        for ro in room_outings:
                            st.error(f"🔴 **{ro['name']}** \n⏱️ {ro['start'].strftime('%H:%M')}~\n💬 {ro['reason']}")
                    else:
                        st.success("🟢 전원 잔류")