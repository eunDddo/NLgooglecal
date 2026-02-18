import streamlit as st
from openai import OpenAI
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import sqlite3
import datetime
from prettytable import PrettyTable
import json
import re


######## 사용자가 입력 ########
OPENAI_API_KEY = "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"
GOOGLE_CALENDAR_ID = "deu06053@gmail.com"
# 구글 서비스 계정 JSON 파일 경로
GOOGLE_CREDENTIALS_PATH = "service_account.json"
db_path = "calendar.db"
##############################


class CalendarChatGPT:
    def __init__(self, openai_api_key, google_credentials_path, calendar_id, db_path, log_file="gpt_queries.log"):
        """
        CalendarChatGPT 인스턴스를 초기화합니다.
        
        Args:
            openai_api_key: OpenAI API 키
            google_credentials_path: 구글 서비스 계정 JSON 파일 경로
            calendar_id: 구글 캘린더 ID
            db_path: SQLite 데이터베이스 파일 경로
            log_file: 로그 파일의 이름
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.db_path = db_path
        self.log_file = log_file
        self.messages = []
        self.calendar_id = calendar_id
        
        # 구글 캘린더 API 초기화
        try:
            self.google_service = self._init_google_calendar(google_credentials_path)
            self.use_google = True
        except Exception as e:
            print(f"Google Calendar 초기화 실패: {e}")
            self.use_google = False
        
        # SQLite 데이터베이스 초기화
        self._init_database()
    
    def _init_google_calendar(self, credentials_path):
        """구글 캘린더 API를 초기화합니다."""
        credentials = Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        return build('calendar', 'v3', credentials=credentials)
    
    def _init_database(self):
        """SQLite 데이터베이스와 calendar 테이블을 초기화합니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar (
                day INTEGER,
                clock INTEGER,
                location TEXT,
                passage TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def log_query(self, user_input, generated_query, status="Success"):
        """사용자 질의, 생성된 쿼리, 상태를 로그 파일에 기록합니다."""
        with open(self.log_file, "a", encoding="utf-8") as file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"[{timestamp}]\n")
            file.write(f"Status: {status}\n")
            file.write(f"User Input: {user_input}\n")
            file.write(f"Generated SQL: {generated_query}\n")
            file.write("-" * 50 + "\n")
    
    def get_response_from_gpt(self, system_prompt, user_prompt):
        """OpenAI GPT로부터 응답을 받습니다."""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    
    def parse_event_details(self, user_input):
        """
        자연어 입력에서 이벤트 상세 정보를 추출합니다.
        GPT를 사용하여 구조화된 데이터로 변환합니다.
        """
        extraction_prompt = """Extract event details from the user's request and return as JSON.
Required fields: title, date (YYYYMMDD), time (HHMM in 24h format), location (optional), description (optional)

Example:
User: "2월 17일 오후 3시에 카페에서 친구 만나기"
Output: {"title": "친구 만나기", "date": "250217", "time": "1500", "location": "카페", "description": "친구 만나기"}

Return ONLY valid JSON, no other text."""
        
        user_prompt = f"User request: {user_input}"
        
        try:
            response = self.get_response_from_gpt(extraction_prompt, user_prompt)
            return json.loads(response)
        except json.JSONDecodeError:
            return None
    
    def add_to_google_calendar(self, event_details):
        """
        구글 캘린더에 이벤트를 추가합니다.
        
        Args:
            event_details: 이벤트 정보 (title, date, time, location, description)
        
        Returns:
            성공 여부와 메시지
        """
        if not self.use_google:
            return False, "Google Calendar이 초기화되지 않았습니다."
        
        try:
            # 날짜와 시간 형식 변환
            date_str = event_details.get('date', '')
            time_str = event_details.get('time', '0900')
            
            # YYYYMMDD → YYYY-MM-DD
            if len(date_str) == 8:
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                date_formatted = f"{year}-{month}-{day}"
            else:
                return False, "잘못된 날짜 형식입니다."
            
            # HHMM → HH:MM
            if len(time_str) == 4:
                hour = time_str[:2]
                minute = time_str[2:4]
                time_formatted = f"{hour}:{minute}:00"
            else:
                time_formatted = "09:00:00"
            
            # 이벤트 객체 생성
            event = {
                'summary': event_details.get('title', 'No Title'),
                'description': event_details.get('description', ''),
                'location': event_details.get('location', ''),
                'start': {
                    'dateTime': f"{date_formatted}T{time_formatted}",
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'dateTime': f"{date_formatted}T{self._add_one_hour(time_formatted)}",
                    'timeZone': 'Asia/Seoul',
                },
            }
            
            # 구글 캘린더에 추가
            event_result = self.google_service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return True, f"구글 캘린더에 추가되었습니다. (ID: {event_result.get('id')})"
        
        except Exception as e:
            return False, f"구글 캘린더 추가 실패: {str(e)}"
    
    def _add_one_hour(self, time_str):
        """시간에 1시간을 더합니다."""
        time_obj = datetime.datetime.strptime(time_str, "%H:%M:%S")
        end_time = time_obj + datetime.timedelta(hours=1)
        return end_time.strftime("%H:%M:%S")
    
    def prompt(self, user_input):
        """사용자 입력에 대한 SQL 쿼리를 생성합니다."""
        system_prompt = """You are a database manager specializing in calendar scheduling.
Your task is to convert natural language requests into SQL queries.

You have access to a calendar database with the following structure:
CREATE TABLE calendar (
    day INTEGER,
    clock INTEGER,
    location TEXT,
    passage TEXT
);

Important rules:
1. Only output SQL queries - no explanations or additional text
2. For date input, use YYYYMMDD format (e.g., 250217 for February 17, 2025)
3. For time input, use 24-hour format as integer (e.g., 1330 for 1:30 PM)
4. Handle INSERT, SELECT, UPDATE, and DELETE operations
5. Always ensure the SQL query is valid and executable

===== Few-Shot Examples =====

Example 1 (INSERT):
User request: "2월 17일 오후 3시에 카페에서 친구 만나기 일정 추가해줘"
SQL output: INSERT INTO calendar (day, clock, location, passage) VALUES (250217, 1500, 'cafe', 'meet friend');

Example 2 (SELECT):
User request: "2월 17일의 모든 일정을 보여줘"
SQL output: SELECT * FROM calendar WHERE day = 250217;

Example 3 (UPDATE):
User request: "2월 17일 오후 3시 일정을 집으로 옮겨줘"
SQL output: UPDATE calendar SET location = 'home' WHERE day = 250217 AND clock = 1500;

Example 4 (DELETE):
User request: "2월 17일 오후 3시 일정을 삭제해줘"
SQL output: DELETE FROM calendar WHERE day = 250217 AND clock = 1500;

Example 5 (SELECT with condition):
User request: "office에서 있을 모든 일정을 찾아줘"
SQL output: SELECT * FROM calendar WHERE location = 'office';

===== End of Examples ===="""
        
        user_prompt = f"Convert this request to SQL: {user_input}"
        
        self.messages.append({
            "role": "user",
            "content": user_input,
        })
        
        response = self.get_response_from_gpt(system_prompt, user_prompt)
        
        self.messages.append({
            "role": "assistant",
            "content": response
        })
        
        self.log_query(user_input, response)
        return response
    
    def execute_query(self, query):
        """주어진 SQL 쿼리를 데이터베이스에서 실행합니다."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            
            if any(keyword in query.upper() for keyword in ["INSERT", "UPDATE", "DELETE"]):
                conn.commit()
                return "Your request has been processed successfully."
            else:
                result = cursor.fetchall()
                
                if result:
                    table = PrettyTable()
                    fields = [description[0] for description in cursor.description]
                    table.field_names = fields
                    
                    for row in result:
                        table.add_row(row)
                    
                    return table
                else:
                    return "No results found."
        
        except sqlite3.Error as e:
            return f"Database error: {str(e)}"
        finally:
            conn.close()
    
    def clear_table(self):
        """calendar 테이블의 모든 행을 삭제합니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM calendar;")
            conn.commit()
            print('Calendar table cleared')
        finally:
            conn.close()


def run(calendar_chatgpt):
    """Streamlit 애플리케이션의 메인 실행 함수"""
    st.set_page_config(page_title="CalendarDB", page_icon="🗓️")
    st.title("🗓️ CalendarDB with Google Calendar Integration")
    st.text('Team BDAI')
    
    # 탭 생성
    tab1, tab2 = st.tabs(["Local DB", "Google Calendar"])
    
    try:
        # 채팅 메시지 히스토리 초기화
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "I'm your calendar DB manager. You can INSERT, SELECT, UPDATE, or DELETE your schedule by chatting 😃"
                }
            ]
        
        # 탭 1: Local SQLite Database
        with tab1:
            st.header("Local Calendar Database")
            user_input = st.chat_input("Query CalendarDB")
            
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
            
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
            
            if user_input and st.session_state.messages[-1]["role"] == "user":
                with st.chat_message("assistant"):
                    query_made_by_gpt = calendar_chatgpt.prompt(user_input)
                    result = calendar_chatgpt.execute_query(query_made_by_gpt)
                    st.write(result)
                    
                    message_content = str(result) if not isinstance(result, PrettyTable) else result.get_string()
                    st.session_state.messages.append(
                        {"role": "assistant", "content": message_content}
                    )
        
        # 탭 2: Google Calendar
        with tab2:
            st.header("Add Event to Google Calendar")
            
            if calendar_chatgpt.use_google:
                google_input = st.chat_input("자연어로 일정을 설명해주세요 (예: 내일 오후 2시에 카페에서 친구 만나기)")
                
                if google_input:
                    st.write(f"**사용자 입력:** {google_input}")
                    
                    # 이벤트 정보 추출
                    with st.spinner("이벤트 정보를 분석 중입니다..."):
                        event_details = calendar_chatgpt.parse_event_details(google_input)
                    
                    if event_details:
                        st.write("**추출된 이벤트 정보:**")
                        st.json(event_details)
                        
                        # 확인 후 추가
                        if st.button("Google 캘린더에 추가"):
                            with st.spinner("Google 캘린더에 추가 중..."):
                                success, message = calendar_chatgpt.add_to_google_calendar(event_details)
                            
                            if success:
                                st.success(message)
                                calendar_chatgpt.log_query(google_input, str(event_details), "Google Calendar Added")
                            else:
                                st.error(message)
                                calendar_chatgpt.log_query(google_input, str(event_details), f"Failed: {message}")
                    else:
                        st.error("이벤트 정보를 추출할 수 없습니다. 다시 시도해주세요.")
            else:
                st.warning("⚠️ Google Calendar가 초기화되지 않았습니다.")
                st.info("""
                **Google Calendar를 연동하려면:**
                1. Google Cloud Console에서 서비스 계정 생성
                2. 서비스 계정 JSON 키 다운로드
                3. `service_account.json` 파일을 프로젝트 폴더에 저장
                4. Google Calendar ID 설정
                
                [Google Cloud Console](https://console.cloud.google.com)
                """)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        print(f"Error details: {e}")


if __name__ == "__main__":
    calendar_chatgpt = CalendarChatGPT(
        openai_api_key=OPENAI_API_KEY,
        google_credentials_path=GOOGLE_CREDENTIALS_PATH,
        calendar_id=GOOGLE_CALENDAR_ID,
        db_path=db_path
    )
    run(calendar_chatgpt)
