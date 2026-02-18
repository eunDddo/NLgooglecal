import streamlit as st
from openai import OpenAI
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import datetime
import json
import traceback
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "service_account.json")


class CalendarChatGPT:
    def __init__(self, openai_api_key, google_credentials_path, calendar_id):
        self.client = OpenAI(api_key=openai_api_key)
        self.calendar_id = calendar_id

        # 기본값 먼저 세팅 (안전)
        self.use_google = False
        self.google_service = None

        try:
            self.google_service = self._init_google_calendar(google_credentials_path)
            self.use_google = True
            print("✅ Google Calendar API 연결 성공")
            print(f"📅 Calendar ID: {self.calendar_id}")
        except Exception as e:
            print(f"❌ Google Calendar 초기화 실패: {e}")
            print(traceback.format_exc())

    def _init_google_calendar(self, credentials_path):
        print(f"🔐 Credentials 파일 로드: {credentials_path}")

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"service_account.json 파일을 찾을 수 없습니다: {credentials_path}")

        credentials = Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/calendar"],
        )

        service = build("calendar", "v3", credentials=credentials)
        print("✓ Google Calendar API 빌드 성공")
        return service

    def get_response_from_gpt(self, system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()

    def parse_event_details(self, user_input):
        extraction_prompt = """Extract event details from the user's request and return as JSON.
Required fields: title, date (YYYYMMDD or YYMMDD), time (HHMM in 24h format), location (optional), description (optional)

Return ONLY valid JSON, no other text."""
        user_prompt = f"User request: {user_input}"

        try:
            response = self.get_response_from_gpt(extraction_prompt, user_prompt)
            parsed = json.loads(response)
            return parsed
        except json.JSONDecodeError:
            print("❌ JSON 파싱 실패")
            print(f"📋 응답 내용: {response}")
            return None

    def _normalize_date(self, date_str: str) -> str:
        if len(date_str) == 6:  # YYMMDD
            return "20" + date_str
        return date_str

    def _add_one_hour(self, time_str):
        time_obj = datetime.datetime.strptime(time_str, "%H:%M:%S")
        return (time_obj + datetime.timedelta(hours=1)).strftime("%H:%M:%S")

    def add_to_google_calendar(self, event_details):
        if not self.use_google or not self.google_service:
            return False, "❌ Google Calendar이 초기화되지 않았습니다."

        try:
            date_str = self._normalize_date(event_details.get("date", ""))
            time_str = event_details.get("time", "0900")

            if len(date_str) != 8:
                return False, f"잘못된 날짜 형식입니다 (받은 값: {date_str})"

            year, month, day = date_str[:4], date_str[4:6], date_str[6:8]
            date_formatted = f"{year}-{month}-{day}"

            if len(time_str) == 4:
                time_formatted = f"{time_str[:2]}:{time_str[2:4]}:00"
            else:
                time_formatted = "09:00:00"

            event = {
                "summary": event_details.get("title", "No Title"),
                "description": event_details.get("description", ""),
                "location": event_details.get("location", ""),
                "start": {"dateTime": f"{date_formatted}T{time_formatted}", "timeZone": "Asia/Seoul"},
                "end": {"dateTime": f"{date_formatted}T{self._add_one_hour(time_formatted)}", "timeZone": "Asia/Seoul"},
            }

            event_result = (
                self.google_service.events()
                .insert(calendarId=self.calendar_id, body=event)
                .execute()
            )

            return True, f"✅ 추가됨\n🆔 ID: {event_result.get('id')}\n🔗 링크: {event_result.get('htmlLink')}"

        except Exception as e:
            print(traceback.format_exc())
            return False, f"❌ 구글 캘린더 추가 실패: {str(e)}"


def run(calendar_chatgpt):
    st.set_page_config(page_title="CalendarDB", page_icon="🗓️")
    st.title("🗓️ CalendarDB with Google Calendar Integration")
    st.text("Team BDAI")

    st.header("Add Event to Google Calendar")

    if not calendar_chatgpt.use_google:
        st.warning("⚠️ Google Calendar가 초기화되지 않았습니다.")
        return

    with st.form("google_event_form"):
        google_text = st.text_input(
            "자연어로 일정을 설명해주세요",
            placeholder="예: 2월 19일 오후 2시에 카페에서 지우 만나기",
        )
        submitted = st.form_submit_button("이벤트 분석하기")

    if submitted and google_text:
        event_details = calendar_chatgpt.parse_event_details(google_text)
        st.session_state.event_details = event_details
        st.session_state.google_text = google_text

    if st.session_state.get("event_details"):
        st.write("**추출된 이벤트 정보:**")
        st.json(st.session_state.event_details)

        if st.button("Google 캘린더에 추가", key="add_google"):
            success, message = calendar_chatgpt.add_to_google_calendar(st.session_state.event_details)
            (st.success if success else st.error)(message)


# Streamlit에서는 여기만 있으면 됨 (중복 생성 제거)
if "calendar_chatgpt" not in st.session_state:
    st.session_state.calendar_chatgpt = CalendarChatGPT(
        openai_api_key=OPENAI_API_KEY,
        google_credentials_path=GOOGLE_CREDENTIALS_PATH,
        calendar_id=GOOGLE_CALENDAR_ID,
    )

run(st.session_state.calendar_chatgpt)
