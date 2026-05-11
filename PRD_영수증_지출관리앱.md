# PRD: 영수증 지출 관리 앱 (Receipt Expense Tracker)
### Product Requirements Document | Ver 1.4 | 2026-04-23

---

## 1. 문서 개요

| 항목 | 내용 |
|------|------|
| 문서 버전 | v1.4 |
| 작성일 | 2026-04-23 |
| 기반 문서 | 프로그램개요서_영수증_지출관리앱 v2.0 |
| 개발 기간 | 1일 단기 스프린트 |
| 배포 목표 | Vercel (프론트엔드 + 백엔드 서버리스) |

---

## 2. 제품 목적 및 배경

### 2.1 문제 정의

| 문제 | 설명 |
|------|------|
| 수동 입력 번거로움 | 사용자가 영수증을 보고 가계부에 직접 입력해야 하는 반복 작업 |
| 관리 불연속성 | 영수증을 분실하거나 입력을 미루면 지출 내역 파악이 어려움 |
| 진입 장벽 | 기존 가계부 앱은 기능이 많아 단순 지출 추적에 과도한 학습 비용 발생 |

### 2.2 솔루션

영수증(이미지/PDF)을 업로드하면 **Upstage information-extract API**가 자동으로 내용을 파싱·구조화하여 지출 데이터를 생성하는 경량 웹 애플리케이션을 제공한다.

### 2.3 목표 지표 (Success Metrics)

| 지표 | 목표값 |
|------|--------|
| 영수증 파싱 성공률 | 한국어·영어 영수증 기준 80% 이상 |
| 업로드 → 파싱 완료 응답 시간 | 10초 이내 |
| E2E 흐름 동작 (업로드 → 목록 조회) | 1일 스프린트 내 완료 |

---

## 3. 타겟 사용자 (User Personas)

### Persona A — 직장인 지출 관리자
- **특성**: 영수증이 많지만 입력이 귀찮은 30대 직장인
- **목표**: 최소한의 노력으로 월별 소비 패턴 파악
- **Pain Point**: 복잡한 앱 설치 없이 빠르게 영수증 기록을 남기고 싶음

### Persona B — 사이드 프로젝트 개발자
- **특성**: AI/OCR 기술을 실제 서비스에 적용해 보고 싶은 개발자
- **목표**: Upstage information-extract API 연동 실습 및 포트폴리오 구성
- **Pain Point**: 빠르게 동작하는 MVP를 만들고 싶음

---

## 4. 범위 정의 (Scope)

### 4.1 In Scope (1일 스프린트 내 포함)

| ID | 기능 | 우선순위 |
|----|------|----------|
| M-01 | 영수증 이미지 업로드 (JPG, PNG, PDF) | Must Have |
| M-02 | Upstage information-extract API 기반 OCR 자동 파싱 | Must Have |
| M-03 | 구조화 JSON 추출 (가게명, 날짜, 품목, 금액) | Must Have |
| M-04 | 지출 내역 카드형 목록 조회 | Must Have |
| M-05 | expenses.json 파일 누적 저장 | Must Have |
| S-01 | 총 지출 합계 대시보드 | Should Have |
| S-02 | 날짜 범위 필터링 | Should Have |
| S-03 | 지출 항목 삭제 | Should Have |
| S-04 | OCR 파싱 결과 수정 후 저장 | Should Have |

### 4.2 Out of Scope (1차 제외)

- 사용자 인증/로그인
- 다국어 영수증 지원 (한국어·영어 외)
- 데이터베이스 연동 (Supabase, PostgreSQL 등)
- 다중 사용자 동시 접속 지원
- 모바일 네이티브 앱
- 카테고리 자동 분류 학습 (ML 학습 루프)

---

## 5. 기능 요구사항 (Functional Requirements)

### FR-01: 영수증 파일 업로드

**설명**: 사용자가 영수증 이미지 또는 PDF를 웹 UI에서 업로드할 수 있다.

| 항목 | 내용 |
|------|------|
| 지원 형식 | JPG, PNG, PDF |
| 최대 파일 크기 | 10MB |
| 입력 방식 | 드래그 앤 드롭 또는 파일 선택 버튼 |
| 업로드 중 피드백 | 진행률 표시바(ProgressBar) 노출 |

**수락 기준 (Acceptance Criteria)**:
- [ ] JPG, PNG, PDF 파일이 정상 업로드된다.
- [ ] 10MB 초과 파일은 오류 메시지를 표시하고 업로드를 차단한다.
- [ ] 지원하지 않는 형식(예: .gif, .docx) 업로드 시 오류 메시지를 표시한다.
- [ ] 업로드 진행 중 로딩 상태가 UI에 표시된다.

---

### FR-02: OCR 자동 파싱

**설명**: 업로드된 파일을 Upstage information-extract API로 분석하여 영수증 내용을 구조화된 JSON으로 반환한다.

| 항목 | 내용 |
|------|------|
| API | Upstage information-extract |
| 입력 | Base64 인코딩된 이미지/PDF |
| 출력 | 구조화 JSON (response_format: json_schema) |
| SDK | OpenAI SDK (Upstage 호환 base_url) |

**추출 필드**:

| 필드 | 필수 여부 | 설명 |
|------|-----------|------|
| store_name | 필수 | 가게(상호) 이름 |
| receipt_date | 필수 | 영수증 날짜 (YYYY-MM-DD) |
| receipt_time | 선택 | 영수증 시각 (HH:MM) |
| category | 선택 | 지출 카테고리 (예: 식료품, 외식) |
| items[] | 필수 | 품목 목록 (name, quantity, unit_price, total_price) |
| total_amount | 필수 | 최종 결제 금액 |
| payment_method | 선택 | 결제 수단 (예: 신용카드, 현금) |

**수락 기준**:
- [ ] 한국어 영수증에서 가게명, 날짜, 합계 금액이 정확히 추출된다.
- [ ] 영어 영수증에서도 동일하게 동작한다.
- [ ] OCR 파싱 실패 시 사용자에게 오류 메시지를 표시하고 재시도를 안내한다.
- [ ] 응답은 10초 이내에 반환된다.

---

### FR-03: 파싱 결과 미리보기 및 저장

**설명**: OCR 파싱 결과를 사용자가 확인하고, 필요 시 수정 후 저장할 수 있다.

**수락 기준**:
- [ ] 파싱 결과가 업로드 페이지 하단에 즉시 표시된다.
- [ ] 사용자가 각 필드를 직접 수정할 수 있다.
- [ ] "저장" 버튼 클릭 시 expenses.json에 append 저장된다.
- [ ] 저장 완료 후 성공 Toast 알림이 표시된다.

---

### FR-04: 지출 내역 목록 조회

**설명**: 저장된 지출 내역을 카드 형태로 목록 조회한다.

**수락 기준**:
- [ ] 메인 대시보드에 저장된 모든 지출 내역이 카드 형태로 표시된다.
- [ ] 각 카드에는 가게명, 날짜, 총 금액, 카테고리 뱃지가 표시된다.
- [ ] 날짜 범위 필터 적용 시 해당 기간의 내역만 필터링된다.
- [ ] 내역이 없을 경우 빈 상태(empty state) 안내 문구가 표시된다.

---

### FR-05: 지출 합계 대시보드

**설명**: 조회된 지출 내역의 합산 통계를 요약하여 표시한다.

**수락 기준**:
- [ ] 총 지출 금액이 대시보드 상단에 표시된다.
- [ ] 이번 달 지출 금액이 별도로 표시된다.
- [ ] 카테고리별 합계가 요약 표시된다.

---

### FR-06: 지출 항목 삭제

**설명**: 잘못 등록된 지출 항목을 삭제할 수 있다.

**수락 기준**:
- [ ] 각 지출 카드 또는 상세 화면에서 삭제 버튼이 제공된다.
- [ ] 삭제 전 확인 다이얼로그(Modal)가 표시된다.
- [ ] 삭제 확인 시 expenses.json에서 해당 항목이 제거되고 목록이 즉시 갱신된다.
- [ ] 삭제 완료 후 Toast 알림이 표시된다.

---

## 6. 비기능 요구사항 (Non-Functional Requirements)

### 6.1 성능

| 항목 | 요구사항 |
|------|----------|
| OCR 파싱 응답 시간 | 10초 이내 (Upstage API 응답 포함) |
| 목록 조회 응답 시간 | 1초 이내 (JSON 파일 읽기) |
| 동시 사용자 | 1인 기준 (개인 프로젝트 MVP) |

### 6.2 보안

| 항목 | 요구사항 |
|------|----------|
| API Key 관리 | Vercel 환경변수에만 저장, 소스코드 노출 금지 |
| API 엔드포인트 | URL 비공개로 최소 보안 유지 |
| 파일 업로드 검증 | 파일 형식 및 크기 서버 측 재검증 필수 |
| 인증 | 1차 범위 제외 (API URL 비공개로 대체) |

### 6.3 가용성 및 데이터 영속성

| 방안 | 설명 | 난이도 | 권장 |
|------|------|--------|------|
| localStorage 병행 저장 | 클라이언트에서 데이터 영속성 유지 | ⭐ 쉬움 | MVP 1순위 |
| Railway / Render 배포 | 일반 서버에서 파일 시스템 유지 | ⭐⭐ 보통 | 안정성 필요 시 |
| Vercel KV (Redis) | Vercel 내장 키-값 저장소 | ⭐⭐ 보통 | Vercel 유지 시 |
| Supabase 무료 플랜 | PostgreSQL DB로 영구 전환 | ⭐⭐⭐ 어려움 | 장기 운영 시 |

> **MVP 기본 채택**: localStorage 병행 저장 (Vercel 서버리스 파일 시스템 비지속 문제 대응)

### 6.4 공통 오류 처리 기준

| 오류 유형 | 처리 방식 | UI 표현 |
|----------|----------|---------|
| 네트워크 단절 | 요청 중단 + 재시도 버튼 제공 | 빨간 Toast + 재시도 버튼 |
| API 4xx 오류 | 사용자 친화적 메시지 표시 | 노란 Toast |
| API 5xx 오류 | 재시도 안내 메시지 표시 | 빨간 Toast + 재시도 버튼 |
| 로딩 중 중복 요청 | 버튼 비활성화로 중복 방지 | `disabled` + `opacity-50 cursor-not-allowed` |
| 파일 형식/크기 오류 | 업로드 즉시 차단 + 안내 메시지 | 빨간 인라인 메시지 |

**Toast 공통 규칙**:
- 자동 소멸: 3초
- 위치: `fixed bottom-4 right-4`
- 중복 Toast 발생 시 최신 메시지만 표시

---

### 6.5 유지보수성

- 백엔드와 프론트엔드를 독립 디렉토리(`backend/`, `frontend/`)로 분리
- 환경변수는 `.env` 파일 또는 Vercel 환경변수로 중앙 관리
- OCR 서비스는 `services/` 레이어로 분리하여 교체 용이하게 구성

---

## 7. 데이터 구조 (Data Schema)

### 7.1 지출 항목 JSON 스키마

```json
{
  "id": "uuid-v4-string",
  "created_at": "2025-07-15T14:30:00Z",
  "store_name": "이마트 강남점",
  "receipt_date": "2025-07-15",
  "receipt_time": "13:25",
  "category": "식료품",
  "items": [
    {"name": "신라면 멀티팩", "quantity": 2, "unit_price": 4500, "total_price": 9000},
    {"name": "바나나우유", "quantity": 1, "unit_price": 1800, "total_price": 1800}
  ],
  "subtotal": 10800,
  "discount": 500,
  "tax": 0,
  "total_amount": 10300,
  "payment_method": "신용카드",
  "raw_image_path": "uploads/receipt_20250715_001.jpg"
}
```

### 7.2 저장 구조

- **파일 위치**: `backend/data/expenses.json`
- **저장 방식**: JSON 배열에 append (누적 저장)
- **ID 생성**: UUID v4 (서버 측 생성)
- **타임스탬프**: ISO 8601 형식 (UTC 기준)

---

## 8. API 명세 (API Specification)

### GET /health
| 항목 | 내용 |
|------|------|
| 설명 | 서버 상태 확인 |
| 성공 응답 (200) | `{"status":"ok","version":"1.0.0"}` |

### POST /api/upload
| 항목 | 내용 |
|------|------|
| 설명 | 영수증 파일 업로드 및 OCR 파싱 |
| 요청 형식 | `multipart/form-data` |
| 요청 파라미터 | `file`: 업로드 파일 |
| 성공 응답 (200) | 파싱된 지출 JSON 객체 |
| 실패 응답 (400) | 파일 형식/크기 오류 메시지 |
| 실패 응답 (500) | OCR 파싱 실패 메시지 |

### GET /api/expenses
| 항목 | 내용 |
|------|------|
| 설명 | 전체 지출 내역 조회 |
| 쿼리 파라미터 | `from`: 시작일 (YYYY-MM-DD), `to`: 종료일 (YYYY-MM-DD) |
| 성공 응답 (200) | 지출 항목 배열 `[]` |

### DELETE /api/expenses/{id}
| 항목 | 내용 |
|------|------|
| 설명 | 특정 지출 항목 삭제 |
| Path 파라미터 | `id`: UUID |
| 성공 응답 (200) | 삭제 성공 메시지 |
| 실패 응답 (404) | 항목 없음 메시지 |

### PUT /api/expenses/{id}
| 항목 | 내용 |
|------|------|
| 설명 | 특정 지출 항목 수정 |
| Path 파라미터 | `id`: UUID |
| 요청 Body | 수정할 JSON 필드 |
| 성공 응답 (200) | 수정된 지출 객체 |

### GET /api/summary
| 항목 | 내용 |
|------|------|
| 설명 | 지출 합계 통계 조회 |
| 쿼리 파라미터 | `month`: YYYY-MM (선택) |
| 성공 응답 (200) | 총합계, 이번달 합계, 카테고리별 통계 |

---

## 9. 화면 설계 (UI Specification)

### 9.1 페이지 목록

| 페이지 | 경로 | 핵심 컴포넌트 |
|--------|------|---------------|
| 메인 대시보드 | `/` | SummaryCard, FilterBar, ExpenseList, ExpenseCard |
| 업로드 | `/upload` | DropZone, ProgressBar, ParsePreview |
| 지출 상세/수정 | `/expense/:id` | ReceiptImage, EditForm, 삭제 버튼 |

### 9.2 주요 컴포넌트 명세

#### DropZone
- 드래그 앤 드롭 및 클릭 업로드 지원
- 지원 형식 안내 텍스트 표시 (JPG, PNG, PDF / 최대 10MB)
- 파일 선택 후 즉시 업로드 API 호출

#### ParsePreview
- OCR 파싱 결과를 인라인 편집 가능한 폼으로 표시
- 각 필드: 가게명, 날짜, 카테고리, 품목 목록, 합계
- "저장" / "취소" 버튼 제공

#### ExpenseCard
- 표시 항목: 가게명, 날짜, 총 금액, 카테고리 뱃지
- 카드 클릭 시 상세 페이지(`/expense/:id`)로 이동

#### SummaryCard
- 총 지출 금액 (전체 기간)
- 이번 달 지출 금액
- 카테고리별 지출 요약

#### FilterBar
- 시작일 / 종료일 날짜 입력
- "조회" 버튼으로 필터 적용
- "초기화" 버튼으로 전체 목록 복원

### 9.3 공통 컴포넌트

| 컴포넌트 | 역할 |
|----------|------|
| Badge | 카테고리 뱃지 (색상 코딩) |
| Modal | 삭제 확인 다이얼로그 |
| Toast | 저장/삭제/오류 알림 (3초 자동 소멸) |
| ProgressBar | OCR 처리 진행 상태 표시 |

---

## 10. 화면 디자인 & 스타일 가이드 (Design & Style Guide)

### 10.1 디자인 원칙

| 원칙 | 설명 |
|------|------|
| **간결함 (Simplicity)** | 불필요한 요소 없이 핵심 정보만 표시 |
| **신뢰감 (Trust)** | 숫자·금액·날짜가 명확히 구분되어 데이터를 신뢰할 수 있는 느낌 |
| **빠른 피드백 (Responsiveness)** | 업로드·저장·삭제 모든 동작에 즉각적인 시각적 피드백 제공 |
| **모바일 우선 (Mobile-First)** | 스마트폰에서 영수증을 촬영 후 바로 업로드하는 시나리오 고려 |

---

### 10.2 컬러 팔레트

| 토큰 | Tailwind 클래스 | HEX | 용도 |
|------|-----------------|-----|------|
| Primary | `indigo-600` | `#4F46E5` | CTA 버튼, 링크, 포커스 링 |
| Primary Hover | `indigo-700` | `#4338CA` | 버튼 hover 상태 |
| Background | `gray-50` | `#F9FAFB` | 페이지 배경 |
| Surface | `white` | `#FFFFFF` | 카드, 모달 배경 |
| Success | `green-500` | `#22C55E` | 저장 완료 Toast |
| Error | `red-500` | `#EF4444` | 오류 메시지, 삭제 버튼 |

#### 카테고리 뱃지 색상

| 카테고리 | 뱃지 배경 | 텍스트 색 |
|----------|-----------|----------|
| 식료품 | `green-100` | `green-700` |
| 외식 | `orange-100` | `orange-700` |
| 교통 | `blue-100` | `blue-700` |
| 쇼핑 | `purple-100` | `purple-700` |
| 의료 | `red-100` | `red-700` |
| 기타 | `gray-100` | `gray-700` |

---

### 10.3 타이포그래피

```css
font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
```

---

## 11. 기술 스택 및 의존성 (Tech Stack)

| 구분 | 기술 | 버전 |
|------|------|------|
| 프론트엔드 | ReactJS | v18+ |
| 빌드 도구 | Vite | v5+ |
| 스타일링 | TailwindCSS | v3+ |
| HTTP 클라이언트 | Axios | v1+ |
| 백엔드 | Python FastAPI | v0.136+ |
| OCR API | Upstage information-extract (OpenAI SDK 호환) | openai v2+ |
| 이미지 처리 | Pillow / pdf2image | pillow v12+, pdf2image v1.17 |
| 데이터 저장 | JSON 파일 | DB 미사용 |
| 배포 | Vercel | - |
| 버전 관리 | GitHub | main 브랜치 |

---

## 12. 환경변수 명세

| 변수명 | 설명 | 적용 위치 |
|--------|------|----------|
| `UPSTAGE_API_KEY` | Upstage API 인증 키 | Vercel 환경변수 (백엔드) |
| `VITE_API_BASE_URL` | 백엔드 API 기본 URL | Vercel 환경변수 (프론트 빌드 시 주입) |
| `DATA_FILE_PATH` | expenses.json 저장 경로 | Vercel 환경변수 (백엔드) |

---

## 13. 프로젝트 디렉토리 구조

```
receipt-tracker/
├── frontend/
│     ├── src/
│     │     ├── pages/
│     │     │     ├── Dashboard.jsx
│     │     │     ├── UploadPage.jsx
│     │     │     └── ExpenseDetail.jsx
│     │     ├── components/
│     │     │     ├── DropZone.jsx
│     │     │     ├── ParsePreview.jsx
│     │     │     ├── ExpenseCard.jsx
│     │     │     ├── SummaryCard.jsx
│     │     │     ├── FilterBar.jsx
│     │     │     ├── Badge.jsx
│     │     │     ├── Modal.jsx
│     │     │     └── Toast.jsx
│     │     └── api/
│     │           └── axios.js
│     ├── package.json
│     └── vite.config.js
├── backend/
│     ├── main.py
│     ├── routers/
│     │     ├── upload.py
│     │     ├── expenses.py
│     │     └── summary.py
│     ├── services/
│     │     ├── ocr_service.py
│     │     └── storage_service.py
│     ├── data/
│     │     └── expenses.json
│     └── requirements.txt
├── vercel.json
└── .env.example
```

---

## 14. 바이브 코딩 3원칙 적용

### 원칙 1 — "뭘 만들면 완료인지" 체크리스트를 미리 적어라

#### 전체 스프린트 완료 체크리스트 (Master Checklist)

**Must Have — 이것만 되면 배포 가능**
- [ ] JPG/PNG/PDF 영수증 업로드 → OCR 파싱 → JSON 반환 정상 동작
- [ ] 파싱 결과가 ParsePreview에 표시되고 수정 후 저장 가능
- [ ] 대시보드에서 저장된 지출 내역 카드 목록 조회 가능
- [ ] 10MB 초과 / 미지원 형식 업로드 시 오류 메시지 표시
- [ ] Vercel 배포 URL에서 E2E 전체 흐름 동작 확인

**Should Have — 완성도를 높이는 기능**
- [ ] 날짜 범위 필터링 동작
- [ ] 지출 항목 삭제 (Modal 확인 포함)
- [ ] 총 지출 / 이번달 지출 SummaryCard 표시
- [ ] 상세 페이지에서 수정 저장 동작

---

### 원칙 3 — 버그가 나면 "분석 먼저, 수정 나중"

| 버그 유형 | 분석 시 확인할 것 |
|-----------|------------------|
| OCR 파싱 실패 (500) | API 응답 형식 / JSON 스키마 일치 여부 / API Key 유효성 |
| CORS 오류 | FastAPI `allow_origins` 설정 / Vercel 라우팅 경로 일치 여부 |
| 데이터 손실 (Vercel) | 서버리스 컨테이너 재시작 여부 / localStorage 병행 저장 동작 여부 |
| 환경변수 미적용 | `VITE_` 접두사 확인 / Vercel 환경변수 등록 여부 / 재배포 여부 |

---

## 15. 개발 일정 및 완료 기준

> **전체 개발 타임라인 (1일 스프린트 기준)**
>
> ```
> [Phase 0] 사전 기술 검증        ── 0.5h  ✅ 완료
> [Phase 1] 환경 설정             ── 0.5h  ✅ 완료
> [Phase 2] 백엔드 핵심 API       ── 2.5h
> [Phase 3] 백엔드 부가 API       ── 1.0h
> [Phase 4] 프론트 환경 설정      ── 0.5h
> [Phase 5] 업로드 화면           ── 1.5h
> [Phase 6] 대시보드 화면         ── 1.5h
> [Phase 7] 상세/수정 화면        ── 1.0h  (Should Have)
> [Phase 8] 배포 & E2E 검증      ── 1.0h
>                                 ────────
>                                 총 10.0h
> ```

---

### Phase 0 — 사전 기술 검증 ✅ 완료

#### 완료 기준
- [x] Upstage API Key로 테스트 호출 시 200 응답을 받는다
- [x] `pdf2image`로 샘플 PDF 변환이 로컬에서 성공한다 (Poppler 25.07.0 설치)
- [x] Vercel 서버리스에서 `/tmp` 경로 사용 가능 여부를 확인한다
- [x] OCR API 예제 코드를 확보한다 (`information-extract` API 직접 사용)

> **Phase 0 발견 사항 (2026-05-11)**
> - OCR 방식 변경: `ChatUpstage Vision LLM` → **Upstage `information-extract` API** (OpenAI SDK 호환)
> - PDF도 base64로 직접 처리 가능 → Vercel 배포 시 Poppler 불필요
> - 패키지 버전 대폭 변경: LangChain 미사용으로 제외, openai SDK 채택

---

### Phase 1 — 프로젝트 환경 설정 ✅ 완료

#### requirements.txt

```txt
# Phase 0 검증 기준 최신 버전 (2026-05-11)
fastapi==0.136.1
uvicorn[standard]==0.46.0
python-multipart==0.0.28
openai==2.36.0
pillow==12.2.0
pdf2image==1.17.0
python-dotenv==1.2.2
mangum==0.19.0
```

#### 완료 기준
- [x] `receipt-tracker` Remote Repository 생성 및 Push 완료 (https://github.com/popillon/receipt-tracker)
- [x] 가상환경 폴더 venv가 생성되어 있고, 패키지가 설치되어 있다
- [x] `uvicorn backend.main:app --reload` 실행 시 FastAPI 서버가 정상 기동된다
- [x] Health Check 엔드포인트 구현 (`GET /health` → `{"status":"ok","version":"1.0.0"}`)
- [x] `http://localhost:8000/docs` Swagger UI가 열린다
- [x] `.env` 파일이 `.gitignore`에 포함되어 있다

---

### Phase 2 — 백엔드 핵심 API: OCR 업로드 (예상 2.5h)

#### 2-2. 스토리지 서비스 (`backend/services/storage_service.py`)

| # | 작업 | 내용 |
|---|------|------|
| 2-2-1 | `load_expenses()` 함수 | `expenses.json` 읽기 → 리스트 반환 |
| 2-2-2 | `save_expenses(data)` 함수 | 리스트 → `expenses.json` 쓰기 |
| 2-2-3 | `append_expense(item)` 함수 | UUID 생성 후 리스트에 추가 저장 |

#### 2-3. OCR 서비스 (`backend/services/ocr_service.py`)

| # | 작업 | 내용 |
|---|------|------|
| 2-3-1 | 파일 전처리 함수 | JPG/PNG/PDF → Base64 인코딩 |
| 2-3-2 | `information-extract` API 호출 | OpenAI SDK + response_format json_schema |
| 2-3-3 | `parse_receipt(file_bytes, content_type)` 함수 | 전처리 → API 호출 → JSON 반환 |

#### 2-4. 업로드 라우터 (`backend/routers/upload.py`)

| # | 작업 | 내용 |
|---|------|------|
| 2-4-1 | `POST /api/upload` 엔드포인트 | `UploadFile` 수신, 형식/크기 검증 |
| 2-4-2 | 파일 검증 로직 | 허용 MIME 타입 체크, 10MB 초과 차단 |
| 2-4-3 | OCR 서비스 호출 및 응답 | `parse_receipt()` → UUID 부여 → JSON 반환 |
| 2-4-4 | 오류 처리 | 400 (파일 오류), 500 (OCR 실패) HTTPException |

#### 완료 기준
- [ ] `curl -X POST /api/upload -F "file=@receipt.jpg"` 실행 시 구조화 JSON이 반환된다
- [ ] 10MB 초과 파일 업로드 시 400 오류가 반환된다
- [ ] PDF 파일 업로드 시 정상적으로 파싱된다

---

### Phase 3 — 백엔드 부가 API (예상 1.0h)

#### 3-1. 지출 CRUD 라우터 (`backend/routers/expenses.py`)

| # | 작업 | 엔드포인트 | 내용 |
|---|------|-----------|------|
| 3-1-1 | 전체 조회 | `GET /api/expenses` | `from`, `to` 쿼리로 날짜 필터링 |
| 3-1-2 | 항목 삭제 | `DELETE /api/expenses/{id}` | UUID로 항목 찾아 제거, 없으면 404 |
| 3-1-3 | 항목 수정 | `PUT /api/expenses/{id}` | 요청 Body로 필드 부분 업데이트 |

#### 3-2. 통계 라우터 (`backend/routers/summary.py`)

| # | 작업 | 엔드포인트 | 내용 |
|---|------|-----------|------|
| 3-2-1 | 합계 조회 | `GET /api/summary` | `month` 쿼리로 월별 필터, 총합·카테고리별 합계 반환 |

#### 완료 기준
- [ ] 5개 엔드포인트 전체 정상 응답 확인
- [ ] `GET /api/expenses?from=2025-07-01&to=2025-07-31` 날짜 필터가 동작한다
- [ ] 존재하지 않는 ID로 DELETE 시 404가 반환된다

---

### Phase 4 — 프론트엔드 환경 설정 (예상 0.5h)

#### 완료 기준
- [ ] `npm run dev` 실행 시 `http://localhost:5173` 에서 React 앱이 열린다
- [ ] TailwindCSS 클래스가 정상 적용된다
- [ ] `/`, `/upload`, `/expense/:id` 3개 경로가 라우팅된다

---

### Phase 5 — 업로드 화면 구현 (예상 1.5h)

#### 완료 기준
- [ ] 이미지를 드래그 앤 드롭하면 OCR 파싱이 실행된다
- [ ] ProgressBar가 처리 중 표시되고 완료 후 숨겨진다
- [ ] ParsePreview에서 필드를 수정하고 저장 시 대시보드로 이동한다
- [ ] Toast 알림이 저장 성공 시 표시된다

---

### Phase 6 — 대시보드 화면 구현 (예상 1.5h)

#### 완료 기준
- [ ] 대시보드 진입 시 저장된 지출 내역이 카드 목록으로 표시된다
- [ ] SummaryCard에 총 지출 / 이번달 지출 금액이 표시된다
- [ ] 날짜 필터 적용 시 해당 기간 내역만 표시된다
- [ ] 내역이 없을 때 Empty State가 표시된다

---

### Phase 7 — 지출 상세/수정 화면 구현 (예상 1.0h) `Should Have`

#### 완료 기준
- [ ] ExpenseCard 클릭 시 상세 페이지로 이동한다
- [ ] 필드 수정 후 "수정 저장" 클릭 시 PUT API가 호출되고 Toast가 표시된다
- [ ] "삭제" 클릭 시 Modal이 열리고, 확인 시 항목이 삭제되어 대시보드로 이동한다

---

### Phase 8 — 배포 및 E2E 검증 (예상 1.0h)

#### Vercel 등록 필수 환경변수

| 키 | 값 | 비고 |
|----|-----|------|
| `UPSTAGE_API_KEY` | `up_xxx...` | Upstage 콘솔에서 복사 |
| `VERCEL` | `1` | 자동 주입 (별도 설정 불필요) |

#### E2E 시나리오 검증 체크리스트

| # | 시나리오 | 기대 결과 | 우선도 |
|---|----------|----------|---------|
| E2E-01 | JPG 영수증 업로드 → OCR 파싱 | 구조화 JSON이 ParsePreview에 표시됨 | Must |
| E2E-02 | ParsePreview 필드 수정 → 저장 | 대시보드에 수정된 내용으로 카드 추가됨 | Must |
| E2E-03 | 대시보드 날짜 필터 적용 | 해당 기간 내역만 필터링됨 | Must |
| E2E-04 | ExpenseCard 클릭 → 상세 진입 | 상세 정보 및 원본 이미지 표시됨 | Should |
| E2E-05 | 항목 삭제 → 목록 갱신 확인 | 삭제된 카드가 목록에서 제거됨 | Should |
| E2E-06 | PDF 파일 업로드 | 정상 파싱 및 저장됨 | Should |
| E2E-07 | 10MB 초과 파일 업로드 | 오류 메시지 표시, 업로드 차단됨 | Must |
| E2E-08 | 지원하지 않는 파일 형식 업로드 | 오류 메시지 표시됨 | Must |

#### 완료 기준
- [ ] Vercel 배포 URL에서 E2E-01 ~ E2E-03 시나리오가 모두 통과한다
- [ ] 브라우저 콘솔에 CORS 오류가 없다
- [ ] 환경변수가 정상 주입되어 Upstage API 호출이 성공한다

---

## 16. 리스크 및 대응 방안

| 리스크 | 영향 | 대응 방안 |
|--------|------|----------|
| Vercel 서버리스 파일 시스템 비지속 | 데이터 손실 | localStorage 병행 저장 또는 Railway 배포로 전환 |
| Upstage API 응답 시간 초과 | OCR 파싱 실패 | 타임아웃 설정 (15초), 재시도 안내 메시지 표시 |
| OCR 파싱 정확도 낮음 | 잘못된 데이터 저장 | ParsePreview에서 사용자 직접 수정 후 저장 가능하도록 처리 |
| 1일 스프린트 일정 초과 | 기능 미완성 | Should Have 기능 후순위 처리, Must Have 우선 완료 |

---

## 17. 용어 정의

| 용어 | 설명 |
|------|------|
| OCR | 광학 문자 인식 (Optical Character Recognition) |
| information-extract | Upstage의 문서 정보 추출 API 모델 |
| LLM | 대형 언어 모델 (Large Language Model) |
| E2E | End-to-End, 전체 흐름 테스트 |
| MVP | Minimum Viable Product, 최소 기능 제품 |
| UUID | Universally Unique Identifier, 전역 고유 식별자 |

---

*Receipt Expense Tracker | PRD v1.5 | Phase 0/1 완료 반영*
*v1.5: Phase 0 검증 결과 반영 (OCR 방식 변경, 패키지 버전 업데이트), Phase 1 완료 체크리스트 반영*
