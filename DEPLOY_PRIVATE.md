# 🔒 Private Repository 배포 가이드

Private repository에서 모바일 배포를 위한 해결 방법들입니다.

## 방법 1: Repository를 Public으로 변경 (가장 쉬움)

### GitHub에서 설정 변경:

1. GitHub에서 repository 페이지로 이동
2. `Settings` 탭 클릭
3. 맨 아래 `Danger Zone` 섹션으로 스크롤
4. `Change visibility` → `Change to public` 클릭
5. 확인 후 변경

이후 Streamlit Cloud에서 정상적으로 선택 가능합니다.

**장점:**
- 무료
- 가장 쉬운 방법
- Streamlit Cloud에서 자동 배포

**단점:**
- 코드가 공개됨

---

## 방법 2: Render.com 사용 (무료, Private repo 지원)

Render는 무료 플랜에서도 private repository를 지원합니다!

### 배포 단계:

#### 1. Render 계정 생성
https://render.com 에서 GitHub 계정으로 가입

#### 2. Web Service 생성

1. Dashboard → `New +` → `Web Service` 클릭
2. GitHub 연결 및 `odagame` repository 선택 (private 가능!)
3. 설정:
   ```
   Name: koica-simulator
   Environment: Python 3
   Branch: claude/mobile-environment-fix-011CUbYo8Wv6qE7eiUUFNGqF
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
   ```
4. Instance Type: `Free` 선택
5. `Create Web Service` 클릭

약 5-10분 후 배포 완료! URL을 받게 됩니다.

**장점:**
- ✅ Private repo 지원 (무료)
- ✅ 자동 배포
- ✅ HTTPS 제공

**단점:**
- 15분간 요청이 없으면 sleep (첫 접속 시 느림)

---

## 방법 3: Fly.io (무료, Private repo 지원)

### 배포 단계:

#### 1. Fly.io CLI 설치

```bash
# macOS/Linux
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

#### 2. 로그인

```bash
fly auth login
```

#### 3. Dockerfile 생성

프로젝트에 Dockerfile을 추가해드리겠습니다.

#### 4. 배포

```bash
fly launch
fly deploy
```

---

## 방법 4: Railway (무료, Private repo 지원)

### 배포 단계:

1. https://railway.app 접속
2. GitHub 계정으로 가입
3. `New Project` → `Deploy from GitHub repo`
4. `odagame` repository 선택
5. 자동으로 감지 및 배포

Railway가 자동으로 Streamlit을 감지하고 배포합니다.

**무료 플랜:** 월 $5 크레딧 제공

---

## 방법 5: 로컬 + ngrok (임시 공개)

로컬에서 실행하고 ngrok으로 임시 공개 URL 생성:

### 설치:

```bash
# macOS
brew install ngrok

# Windows/Linux
# https://ngrok.com/download 에서 다운로드
```

### 실행:

```bash
# 터미널 1: Streamlit 실행
streamlit run streamlit_app.py

# 터미널 2: ngrok 터널 생성
ngrok http 8501
```

ngrok이 제공하는 URL을 모바일에서 접속!

**장점:**
- 빠른 테스트 가능
- Private 유지

**단점:**
- 임시 URL (세션 종료시 사라짐)
- 컴퓨터를 계속 켜두어야 함
- 무료 플랜은 URL이 매번 변경됨

---

## 방법 6: Replit (무료, 가장 빠름)

코드를 복사하여 Replit에서 실행:

1. https://replit.com 접속
2. `Create Repl` → `Python` 선택
3. 파일들을 업로드:
   - `streamlit_app.py`
   - `koica_game.py`
   - `scenarios.json`
   - `requirements.txt`
4. Shell에서 실행:
   ```bash
   pip install -r requirements.txt
   streamlit run streamlit_app.py --server.headless=true
   ```
5. Replit이 자동으로 공개 URL 제공

**장점:**
- 매우 빠름
- 브라우저에서 모든 작업 가능
- 무료

**단점:**
- Git 연동이 직접적이지 않음
- 파일 수동 업로드 필요

---

## 🎯 추천 방법

### 상황별 최적 선택:

1. **오픈소스로 공개해도 괜찮다면**
   → Repository를 Public으로 변경 + Streamlit Cloud

2. **Private 유지 + 무료 배포**
   → **Render.com** (가장 추천!)

3. **빠른 테스트만 필요**
   → ngrok 또는 Replit

4. **장기 프로덕션**
   → Railway 또는 Fly.io

---

## 🔧 다음 단계

원하는 방법을 선택하셨으면 알려주세요.
해당 방법에 필요한 추가 파일(Dockerfile 등)을 생성해드리겠습니다!
