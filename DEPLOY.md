# 🌍 KOICA 소장 시뮬레이터 - 모바일 배포 가이드

이 문서는 KOICA 소장 시뮬레이터를 모바일 환경에서 플레이할 수 있도록 웹으로 배포하는 방법을 안내합니다.

## 📱 모바일 웹 버전

Streamlit을 사용하여 모바일 친화적인 웹 인터페이스를 제공합니다.

### 특징

- ✅ 반응형 디자인 (모바일, 태블릿, 데스크톱 모두 지원)
- ✅ 터치 친화적 버튼 인터페이스
- ✅ 시각적 스탯 표시 (프로그레스 바)
- ✅ 부드러운 게임 플레이
- ✅ 클래식 모드 및 AI 모드 지원

## 🚀 배포 방법

### 방법 1: Streamlit Cloud (추천 - 무료)

가장 쉽고 빠른 방법입니다.

#### 1단계: GitHub에 코드 푸시

```bash
# 이미 git 저장소에 있다면 푸시
git add .
git commit -m "Add Streamlit web interface for mobile"
git push origin main
```

#### 2단계: Streamlit Cloud 배포

1. https://streamlit.io/cloud 방문
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택: `amnotyoung/odagame`
5. 메인 파일 경로: `streamlit_app.py`
6. "Deploy" 클릭

**배포 완료!** 몇 분 안에 앱이 배포되고 모바일에서 접근 가능한 URL을 받게 됩니다.

#### 주의사항

- Streamlit Cloud는 무료 플랜에서 리소스가 제한적입니다
- AI 모드를 사용하려면 Gemini API 키를 앱 내에서 입력해야 합니다
- Secrets 관리를 위해 Streamlit Cloud의 Secrets 기능을 사용할 수 있습니다

### 방법 2: Render (무료)

#### 1단계: Render 계정 생성

https://render.com 에서 계정 생성

#### 2단계: Web Service 생성

1. Dashboard에서 "New +" → "Web Service" 클릭
2. GitHub 저장소 연결
3. 설정:
   - **Name**: koica-simulator
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
   - **Instance Type**: Free

4. "Create Web Service" 클릭

배포 완료!

### 방법 3: Heroku

#### 1단계: Heroku CLI 설치

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Ubuntu/Debian
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2단계: 필요한 파일 생성

이미 포함되어 있습니다:
- `requirements.txt`: Python 패키지 의존성
- `.streamlit/config.toml`: Streamlit 설정

추가로 필요한 파일:

```bash
# Procfile 생성
echo "web: streamlit run streamlit_app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# runtime.txt 생성
echo "python-3.11.6" > runtime.txt
```

#### 3단계: Heroku 배포

```bash
# Heroku 로그인
heroku login

# 앱 생성
heroku create koica-simulator

# 배포
git push heroku main

# 앱 열기
heroku open
```

### 방법 4: 로컬에서 실행 (테스트용)

모바일 기기에서 로컬 서버에 접속하려면:

#### 1단계: 로컬에서 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# Streamlit 앱 실행
streamlit run streamlit_app.py --server.address=0.0.0.0
```

#### 2단계: 모바일에서 접속

1. 컴퓨터의 로컬 IP 주소 확인:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet "

   # Windows
   ipconfig
   ```

2. 모바일 기기에서 브라우저 열기

3. `http://[컴퓨터-IP]:8501` 접속
   예: `http://192.168.0.100:8501`

**주의**: 모바일과 컴퓨터가 같은 Wi-Fi 네트워크에 연결되어 있어야 합니다.

## 🎮 웹 버전 사용 방법

### 기본 플레이

1. 배포된 URL 접속
2. 게임 모드 선택 (클래식 / AI)
3. 초기 생활 설정 (자동차, 주거지, 여가, 식사)
4. 게임 플레이
   - 각 시나리오의 선택지를 터치/클릭
   - 상단의 스탯 바를 확인하며 진행
   - 위험한 선택에는 경고 표시
5. 2년 임기 완수 또는 게임 오버

### AI 모드 사용

AI 모드를 사용하려면:

1. Gemini API 키 필요
   - https://makersuite.google.com/app/apikey 에서 발급
2. 게임 시작 시 API 키 입력
3. 동적 시나리오 및 자유 입력 기능 활성화

## 🔧 문제 해결

### Streamlit Cloud 배포 실패

**문제**: 앱이 시작되지 않음

**해결**:
1. GitHub 저장소가 공개(Public)인지 확인
2. `streamlit_app.py` 파일 경로가 정확한지 확인
3. `requirements.txt`에 모든 의존성이 포함되어 있는지 확인

### 모바일에서 버튼이 작음

이미 CSS로 모바일 최적화가 적용되어 있습니다. 만약 여전히 작다면:

`.streamlit/config.toml` 파일의 폰트 크기 조정:

```toml
[theme]
fontSize = 16
```

### AI 모드가 작동하지 않음

**문제**: AI 모드 버튼이 비활성화됨

**해결**:
1. `google-generativeai` 패키지가 `requirements.txt`에 포함되어 있는지 확인
2. 배포 환경에서 패키지 설치 로그 확인

## 📊 리소스 요구사항

### Streamlit Cloud (무료 플랜)

- ✅ CPU: 1 core
- ✅ RAM: 1GB
- ✅ 저장공간: 무제한
- ⚠️ 사용하지 않으면 자동으로 sleep 모드
- ⚠️ 동시 접속 제한: 약 10-20명

### Render (무료 플랜)

- ✅ CPU: Shared
- ✅ RAM: 512MB
- ✅ 저장공간: 무제한
- ⚠️ 15분간 요청이 없으면 sleep
- ⚠️ 월 750시간 무료 (sleep 시간 제외)

### Heroku (무료 플랜 종료됨)

Heroku의 무료 플랜은 2022년 11월에 종료되었습니다. 유료 플랜 사용 필요.

## 🌐 도메인 연결 (선택사항)

### Streamlit Cloud

1. Streamlit Cloud 대시보드에서 앱 선택
2. Settings → Domain
3. 커스텀 도메인 추가 (CNAME 레코드 설정 필요)

### Render

1. Render 대시보드에서 서비스 선택
2. Settings → Custom Domain
3. 도메인 추가 및 DNS 설정

## 📱 PWA (Progressive Web App) 설정 (선택사항)

모바일 홈 화면에 앱처럼 추가하려면:

### manifest.json 생성

```json
{
  "short_name": "KOICA 시뮬레이터",
  "name": "KOICA 소장 시뮬레이터",
  "icons": [
    {
      "src": "/favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#1f77b4",
  "background_color": "#ffffff"
}
```

현재 Streamlit은 기본적으로 PWA를 완전히 지원하지 않으므로, 이 기능은 제한적입니다.

## 🎯 추천 배포 방법

**초보자**: Streamlit Cloud
- 가장 쉽고 빠름
- 클릭 몇 번으로 배포 완료
- Streamlit에 특화되어 최적화됨

**중급자**: Render
- 더 많은 제어 가능
- 다양한 앱 유형 지원
- 무료 플랜 제공

**고급자**: Docker + Cloud Run / AWS
- 완전한 제어
- 확장성 좋음
- 비용 발생

## 💡 팁

1. **모바일 테스트**: 배포 전에 로컬에서 모바일 반응형을 테스트하세요
2. **Analytics**: Streamlit Cloud는 기본 analytics를 제공합니다
3. **성능**: 대용량 시나리오 파일은 로딩 시간에 영향을 줄 수 있습니다
4. **보안**: API 키 등 민감한 정보는 환경변수나 Secrets로 관리하세요

## 🆘 추가 도움말

- Streamlit 문서: https://docs.streamlit.io
- Streamlit Cloud 가이드: https://docs.streamlit.io/streamlit-community-cloud
- Render 가이드: https://render.com/docs
- 이슈 리포트: GitHub Issues

---

**즐거운 게임 되세요!** 🎮
