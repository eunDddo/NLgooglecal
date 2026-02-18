# 🗓️ NLgooglecal - NL Google Calendar Manager
자연어(Natural Language)로 Google Calendar에 일정을 추가하는 AI 기반 애플리케이션입니다. OpenAI의 GPT를 사용해 사용자의 자연스러운 한국어 입력을 분석하여 Google Calendar에 자동으로 일정을 등록합니다.

## ✨ 주요 기능
- **자연어 처리**: "내일 오후 2시에 카페에서 친구 만나기" 같은 자연스러운 문장으로 일정 추가
- **GPT 기반 분석**: OpenAI GPT-3.5-turbo를 사용한 고정확도 이벤트 파싱
- **Google Calendar 자동 동기화**: 인식된 일정이 자동으로 Google Calendar에 저장됨
- **한글 완벽 지원**: 장소, 설명 등 모든 필드에서 한글 사용 가능
- **Streamlit 기반 UI**: 직관적이고 사용하기 쉬운 웹 인터페이스
- **상세 로깅**: 모든 쿼리와 처리 결과를 로그 파일에 기록

## 🎯 사용 예시

```
사용자 입력: "2월 20일 오후 3시에 코엑스에서 미팅"
    ↓
GPT 분석
    ↓
자동 추출: 
- 제목: 미팅
- 날짜: 2025-02-20
- 시간: 15:00 (3시)
- 위치: 코엑스
    ↓
Google Calendar에 자동 저장 ✅
```

## 📋 요구사항
- Python 3.13+
- Google Cloud Project & Service Account
- OpenAI API Key
- macOS / Linux / Windows

## 🚀 빠른 시작
### 1️⃣ 저장소 클론

```bash
git clone https://github.com/eunDddo/NLgooglecal.git
cd NLgooglecal
```

### 2️⃣ 가상환경 설정 (macOS)
```bash
# 가상환경 생성
python3 -m venv .venv

# 가상환경 활성화
source .venv/bin/activate

# pip 업그레이드
python -m pip install --upgrade pip

# 패키지 설치
python -m pip install -r requirements.txt
```

### 3️⃣ 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 수정 (텍스트 에디터로 열기)
# 다음 값들을 입력:
# - OPENAI_API_KEY: OpenAI API 키
# - GOOGLE_CALENDAR_ID: 구글 캘린더 ID
# - GOOGLE_CREDENTIALS_PATH: service_account.json 경로
```

### 4️⃣ Google Cloud 설정

[GOOGLE_CALENDAR_SETUP.md](./GOOGLE_CALENDAR_SETUP.md)를 참고하여:
1. Google Cloud Project 생성
2. Google Calendar API 활성화
3. Service Account 생성 및 JSON 키 다운로드
4. Google Calendar에 서비스 계정 공유

### 5️⃣ 앱 실행

```bash
streamlit run calendar_chatgpt_google_integration.py
```

브라우저가 자동으로 열리며, `http://localhost:8501`에서 애플리케이션에 접속할 수 있습니다.

## 📁 프로젝트 구조

```
NLgooglecal/
├── calendar_chatgpt_google_integration.py    # 메인 Streamlit 앱
├── calendar_chatgpt_google_integration_DEBUG.py  # 디버깅 버전
├── requirements.txt                          # 파이썬 의존성
├── .env.example                             # 환경 변수 예시
├── .gitignore                               # Git 제외 파일
├── GOOGLE_CALENDAR_SETUP.md                 # Google Cloud 상세 가이드
└── README.md                                # 이 파일
```

## 🔧 설정 파일 상세

### requirements.txt

```
streamlit>=1.28.0          # 웹 UI 프레임워크
openai>=1.3.0              # OpenAI API
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.80.0
python-dotenv>=1.0.0       # 환경 변수 관리
prettytable>=3.10.0        # 테이블 포맷팅
```

### .env 예시

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxx
GOOGLE_CALENDAR_ID=your-email@gmail.com
GOOGLE_CREDENTIALS_PATH=service_account.json
```

## 💡 사용법

### 기본 사용

1. **Streamlit 앱 실행**
2. **Google Calendar 탭** 선택
3. **자연어로 일정 입력**
   - 예: "내일 오전 10시에 강남역 카페에서 면접"
   - 예: "3월 15일 저녁 7시, 친구 생일 축하"
4. **이벤트 정보 확인** - GPT가 자동으로 파싱한 결과 표시
5. **"Google 캘린더에 추가" 버튼 클릭** - 자동으로 Google Calendar에 저장됨

### 지원하는 자연어 형식

```
날짜 표현:
- "내일", "모레", "이번 주 화요일"
- "2월 20일", "다음달 15일"
- "YYYY-MM-DD" 형식

시간 표현:
- "오전 10시", "오후 3시"
- "14:00", "2시 30분"
- "아침", "저녁"

위치 표현:
- "강남역 카페", "회사", "집"
- "서울 강남구", "코엑스"

설명/내용:
- "팀 미팅", "친구 생일", "병원 예약"
```

## 📊 디버깅 버전

문제가 발생했을 때는 디버깅 버전을 사용하세요:

```bash
streamlit run calendar_chatgpt_google_integration_DEBUG.py
```

**디버깅 버전의 장점:**
- 터미널에 상세한 로그 출력
- 각 단계의 처리 과정 추적
- 에러 메시지 상세 분석
- Google Calendar 초기화 상태 확인

## 🐛 문제 해결

### "Google Calendar이 초기화되지 않았습니다"

**해결책:**
1. `service_account.json` 파일이 프로젝트 폴더에 있는지 확인
2. `.env` 파일에서 경로가 올바른지 확인
3. Google Cloud Console에서 Google Calendar API가 활성화되었는지 확인

```bash
# 파일 확인
ls -la service_account.json
```

### "Permission denied" 오류

**해결책:**
1. Google Calendar 설정으로 이동
2. "공유" 섹션에서 서비스 계정 이메일 추가
3. 권한을 "일정 변경"으로 설정
4. 변경사항 저장

### "아무것도 표시 안 됨" (버튼 클릭 후)

**해결책:**
1. Streamlit 캐시 삭제:
   ```bash
   streamlit cache clear
   ```
2. 앱 재실행:
   ```bash
   streamlit run calendar_chatgpt_google_integration.py
   ```
3. 디버깅 버전 실행하여 터미널 로그 확인

### "날짜/시간 형식 오류"

**확인사항:**
- 날짜 형식: `YYYYMMDD` (예: 20250220)
- 시간 형식: 24시간 형식 HHMM (예: 1430 = 14:30)
- GPT가 올바르게 파싱했는지 "추출된 이벤트 정보"에서 확인

## 🔐 보안 주의사항

### ⚠️ 절대 하지 마세요!

```bash
# ❌ Git에 민감한 파일 올리기
git add service_account.json
git add .env

# ❌ 다른 사람에게 JSON 파일 공유
cat service_account.json | slack

# ❌ 코드에 직접 API 키 입력
OPENAI_API_KEY = "sk-proj-xxxx"  # 하지 마세요!
```

### ✅ 올바른 방법

```bash
# .gitignore에 자동 추가됨
cat .gitignore | grep service_account.json

# 환경 변수로 관리
echo "OPENAI_API_KEY=your-key" >> .env
```

## 📝 로깅

모든 작업은 `gpt_queries.log` 파일에 기록됩니다:

```
[2025-02-18 10:30:45]
Status: Google Calendar Added
User Input: 2월 20일 오후 3시에 카페에서 친구 만나기
Generated Data: {"title": "친구 만나기", ...}
--------------------------------------------------
```

## 🛠️ 개발

### 코드 수정 후 테스트

```bash
# 1. 가상환경 활성화
source .venv/bin/activate

# 2. 앱 실행
streamlit run calendar_chatgpt_google_integration.py

# 3. 변경사항 확인
# 파일이 저장되면 자동으로 앱이 재로드됩니다
```

### 로그 확인

```bash
# 실시간 로그 확인
tail -f gpt_queries.log

# 마지막 20줄 확인
tail -20 gpt_queries.log
```

## 📚 관련 문서

- [Google Calendar 설정 가이드](./GOOGLE_CALENDAR_SETUP.md) - 상세한 Google Cloud 설정 방법
- [Python 3.13 설치 가이드](https://www.python.org/downloads/) - Python 최신 버전 설치
- [Streamlit 공식 문서](https://docs.streamlit.io) - Streamlit 사용법

## 🎓 학습 포인트

이 프로젝트에서 배울 수 있는 것:

- **자연어 처리 (NLP)**: GPT를 사용한 구조화되지 않은 텍스트 처리
- **API 통합**: OpenAI API와 Google Calendar API 연동
- **인증 시스템**: Service Account를 통한 안전한 인증
- **웹 애플리케이션**: Streamlit을 사용한 빠른 웹앱 개발
- **Python 베스트 프랙티스**: 환경 변수, 로깅, 에러 처리 등

## 🚀 향후 개선 사항
- [ ] 반복 일정 지원 ("매주 월요일 미팅")
- [ ] 알림 설정 ("30분 전 알림")
- [ ] 캘린더 조회/수정/삭제 기능
- [ ] 모바일 앱 개발 (Flutter/React Native)
- [ ] 여러 언어 지원

**만든이**: Team BDAI  
**최종 업데이트**: 2025년 2월 18일

**Happy Scheduling! 🗓️✨**
