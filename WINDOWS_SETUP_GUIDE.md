# Windows에서 렌탈 관리 시스템 설치하기


**복사-붙여넣기로 진행하세요!** 각 명령어를 하나씩 실행하고 오류가 없는지 확인한 후 다음 단계로 넘어가세요.

---

## 📋 준비 단계

### 1. 필수 프로그램 설치 (수동 설치 필요)

다음 프로그램들을 미리 설치해주세요:

1. **Python 3.8 이상** 
   - 다운로드: https://www.python.org/downloads/
   - ⚠️ **중요**: 설치시 "Add Python to PATH" 체크박스를 반드시 선택하세요!

2. **Node.js LTS 버전**
   - 다운로드: https://nodejs.org/
   - LTS (Long Term Support) 버전을 선택하세요

3. **Git**
   - 다운로드: https://git-scm.com/download/win
   - 기본 설정으로 설치하면 됩니다

---

## 🚀 설치 시작

### 2. 프로젝트 복제

Windows 터미널(cmd) 또는 PowerShell을 열고 다음 명령어를 하나씩 실행하세요:

```bash
# 프로젝트를 복제할 폴더로 이동 (예: Desktop)
cd Desktop

# 프로젝트 복제
git clone https://github.com/your-username/rental_management_system_with_tag.git

# 프로젝트 폴더로 이동
cd rental_management_system_with_tag
```

### 3. 설치 확인

```bash
# Python 설치 확인
python --version

# Node.js 설치 확인  
node --version

# npm 설치 확인
npm --version
```

**결과 예시:**
```
Python 3.11.5
v18.17.0  
9.6.7
```

---

## 🐍 백엔드 설정

### 4. Python 가상환경 생성

```bash
# backend 폴더로 이동
cd backend

# 가상환경 생성
python -m venv venv
```

### 5. 가상환경 활성화

```bash
# Windows의 경우
venv\Scripts\activate
```

**성공시**: 터미널 맨 앞에 `(venv)`가 표시됩니다.

### 6. Python 패키지 설치

```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 필요한 패키지들 설치
pip install -r requirements.txt
```

### 7. 데이터베이스 및 샘플 데이터 생성

```bash
# 샘플 데이터 생성 (SQLite 데이터베이스 자동 생성)
python scripts/seed_sample_data.py
```

**성공시**: "샘플 데이터 생성이 완료되었습니다" 메시지가 표시됩니다.

---

## ⚛️ 프론트엔드 설정

### 8. 새 터미널 열기

- 기존 터미널은 그대로 두고 **새 터미널을 하나 더 열어주세요**
- 프로젝트 루트 폴더로 이동:

```bash
# 프로젝트 루트로 이동 (경로는 본인 환경에 맞게 수정)
cd Desktop/rental_management_system_with_tag
```

### 9. pnpm 설치

```bash
# pnpm 글로벌 설치
npm install -g pnpm
```

### 10. 프론트엔드 의존성 설치

```bash
# frontend 폴더로 이동
cd frontend

# 패키지 설치
pnpm install
```

---

## 🏃‍♂️ 서버 실행

### 11. 백엔드 서버 실행 (첫 번째 터미널)

백엔드가 설정된 터미널에서:

```bash
# backend 폴더에서 (가상환경이 활성화된 상태에서)
python main.py
```

**성공시**: 다음과 같은 메시지가 표시됩니다:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 12. 프론트엔드 서버 실행 (두 번째 터미널)

프론트엔드가 설정된 터미널에서:

```bash
# frontend 폴더에서
pnpm dev
```

**성공시**: 다음과 같은 메시지가 표시됩니다:
```
  Local:   http://localhost:3000/
```

---

## 🎉 완료! 접속하기

브라우저에서 다음 주소들에 접속해보세요:

- **프론트엔드**: http://localhost:3000
- **백엔드 API 문서**: http://localhost:8000/docs

---

## 🔧 다음번 실행하기

이미 설치가 완료되었다면, 다음번에는 이렇게 간단히 실행할 수 있습니다:

### 터미널 1 (백엔드):
```bash
cd Desktop/rental_management_system_with_tag/backend
venv\Scripts\activate
python main.py
```

### 터미널 2 (프론트엔드):
```bash
cd Desktop/rental_management_system_with_tag/frontend
pnpm dev
```

---

## ❌ 문제 해결

### Python을 찾을 수 없다는 오류
```
'python'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

**해결방법:**
1. Python이 제대로 설치되었는지 확인
2. 설치시 "Add Python to PATH" 옵션을 선택했는지 확인
3. 컴퓨터 재시작 후 다시 시도

### Node.js/npm을 찾을 수 없다는 오류

**해결방법:**
1. Node.js가 제대로 설치되었는지 확인
2. 컴퓨터 재시작 후 다시 시도

### 포트가 이미 사용중이라는 오류

**해결방법:**
```bash
# 포트를 사용중인 프로세스 종료 후 다시 시도
# 또는 다른 포트 사용:
# 백엔드: python main.py --port 8001
# 프론트엔드: pnpm dev --port 3001
```

### 권한 오류 (permission denied)

**해결방법:**
- 터미널을 "관리자 권한으로 실행"으로 열어보세요

---

## 💡 추가 정보

- **샘플 사용자**: 관리자 계정과 일반 사용자 계정이 자동으로 생성됩니다
- **데이터베이스**: SQLite를 사용하므로 별도 DB 서버 설치 불필요
- **개발 모드**: 코드 수정시 자동으로 서버가 재시작됩니다
