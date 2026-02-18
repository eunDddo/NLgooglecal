# Google Calendar 연동 설정 가이드

## 개요
자연어 입력으로 구글 캘린더에 직접 일정을 추가하고, 로컬 SQLite 데이터베이스와 동기화할 수 있습니다.

## 아키텍처

```
User Input (자연어)
    ↓
GPT (자연어 처리)
    ↓
Event Details (구조화된 데이터)
    ↓
┌───────────────────────┬─────────────────┐
↓                       ↓
SQLite DB         Google Calendar API
(Local Storage)   (Cloud Storage)
```

## 설정 단계

### 1단계: Google Cloud Project 생성

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성 (프로젝트명: "CalendarDB" 추천)
3. 프로젝트 선택

### 2단계: Google Calendar API 활성화

1. 좌측 메뉴에서 **"API 및 서비스"** → **"라이브러리"** 클릭
2. **"Google Calendar API"** 검색
3. **"사용"** 버튼 클릭

### 3단계: 서비스 계정 생성

1. **"API 및 서비스"** → **"사용자 인증정보"** 클릭
2. **"사용자 인증정보 만들기"** → **"서비스 계정"** 선택
3. 서비스 계정 세부정보 입력:
   - 서비스 계정명: `calendardb-service`
   - 설명: `Calendar DB Service Account`
   - **"만들기"** 클릭

### 4단계: 서비스 계정 키 생성

1. 생성된 서비스 계정 클릭
2. **"키"** 탭 클릭
3. **"키 추가"** → **"새 키 만들기"**
4. **"JSON"** 형식 선택 후 **"만들기"**
5. JSON 파일이 다운로드됨 → **이를 `service_account.json`으로 저장**

### 5단계: Google Calendar 공유

1. [Google Calendar](https://calendar.google.com) 접속
2. 사용할 캘린더 선택 (또는 새로 생성)
3. 캘린더 설정 → **"공유"**
4. 4단계에서 받은 JSON 파일의 `client_email` 추가
   ```json
   "client_email": "calendardb-service@innate-legacy-487808-b3.iam.gserviceaccount.com"
   ```
5. **편집 권한** 부여

### 6단계: Calendar ID 확인

1. Google Calendar 설정 → **"캘린더 설정"**
2. **"캘린더 ID"** 복사
   - 형식: `your-email@gmail.com` 또는 `your-email@googlemail.com`

### 7단계: 코드 설정

```python
OPENAI_API_KEY = "your-openai-api-key"
GOOGLE_CALENDAR_ID = "your-calendar-id@gmail.com"  # 6단계에서 복사한 ID
GOOGLE_CREDENTIALS_PATH = "service_account.json"    # 5단계에서 저장한 파일
```

### 8단계: 패키지 설치

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

또는 requirements.txt 업데이트:

```bash
streamlit>=1.28.0
openai>=1.3.0
prettytable>=3.10.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.80.0
```

## 사용 방법

### Local Database 탭
기존과 동일하게 SQLite 데이터베이스에 쿼리 실행

```
사용자: "2월 17일 오후 3시에 카페에서 친구 만나기 추가해줘"
→ SQL: INSERT INTO calendar (day, clock, location, passage) VALUES (250217, 1500, 'cafe', 'meet friend')
```

### Google Calendar 탭
자연어로 입력하면 Google Calendar에 자동으로 추가

```
사용자: "내일 오후 2시에 카페에서 친구 만나기"
↓
GPT가 이벤트 정보 추출
↓
사용자 확인 후 Google Calendar에 추가
```

## 로그 파일

모든 작업은 `gpt_queries.log`에 기록됩니다:

```
[2025-02-18 10:30:45]
Status: Google Calendar Added
User Input: 2월 17일 오후 3시에 카페에서 친구 만나기
Generated SQL: {"title": "친구 만나기", "date": "250217", "time": "1500", "location": "카페"}
--------------------------------------------------
```

## 트러블슈팅

### "Google Calendar이 초기화되지 않았습니다"
- `service_account.json` 파일 경로 확인
- JSON 파일 형식 확인
- Google Calendar API 활성화 확인

### "권한 부족" 오류
- 서비스 계정 이메일이 Google Calendar에 공유되었는지 확인
- 편집 권한이 있는지 확인

### "캘린더 ID를 찾을 수 없음"
- Google Calendar 설정에서 정확한 Calendar ID 복사
- `@gmail.com` 또는 `@googlemail.com` 확인

### 이벤트가 추가되지 않음
- `gpt_queries.log` 확인하여 오류 메시지 확인
- 날짜/시간 형식 확인 (YYYYMMDD, HHMM)

## 고급 기능 (추가 가능)

1. **Naver Calendar 연동**
   - Naver OAuth 인증
   - Naver Calendar API 사용

2. **Outlook/Microsoft 365 연동**
   - Microsoft Graph API 사용

3. **캘린더 동기화**
   - Google Calendar ↔ SQLite 양방향 동기화
   - 스케줄러를 통한 주기적 동기화

4. **알림 및 리마인더**
   - 30분/1시간 전 알림 설정
   - Slack/이메일 통지

## 보안 주의사항

1. **service_account.json 보안**
   - `.gitignore`에 추가하여 절대 커밋하지 않기
   ```bash
   echo "service_account.json" >> .gitignore
   ```

2. **API 키 관리**
   - 환경 변수로 관리 (`.env` 파일 사용)
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
   GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
   ```

3. **권한 최소화**
   - 서비스 계정에 Calendar API만 권한 부여

## 다음 단계

1. Naver Calendar 연동 추가
2. 캘린더 간 동기화 기능
3. 자동 리마인더 시스템
4. 모바일 앱 개발 (Flutter/React Native)
