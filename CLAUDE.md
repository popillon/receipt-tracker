# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 프로젝트 개요

영수증(이미지/PDF)을 업로드하면 Upstage `information-extract` API가 자동으로 파싱·구조화하는 경량 지출 관리 웹앱. DB 없이 JSON 파일로 운영하며 Vercel에 배포한다.

---

## 개발 환경 실행 명령

### 백엔드 (FastAPI)

```bash
# 가상환경 생성 및 패키지 설치 (최초 1회)
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r backend/requirements.txt

# 서버 실행 (포트 8000)
uvicorn backend.main:app --reload
# Swagger UI: http://localhost:8000/docs
```

### 프론트엔드 (React + Vite)

```bash
cd frontend
npm install
npm run dev       # http://localhost:5173
npm run build     # 프로덕션 빌드
```

### E2E 업로드 테스트

```bash
curl -X POST http://localhost:8000/api/upload -F "file=@images/01_emart.png"
```

---

## 아키텍처

```
[브라우저 React 앱]
     │  multipart/form-data
     ▼
[FastAPI - /api/upload]
     │  Base64 인코딩 (이미지/PDF 모두 동일)
     ▼
[Upstage information-extract API (OpenAI SDK)]
     │  구조화 JSON (response_format: json_schema)
     ▼
[storage_service → expenses.json]
     │
     ▼  (로컬: backend/data/   Vercel: /tmp/)
```

### 디렉토리 구조

```
receipt-tracker/
├── backend/
│   ├── main.py                    # FastAPI 앱 진입점, CORS 설정, 라우터 등록
│   ├── routers/
│   │   ├── upload.py              # POST /api/upload — 파일 검증 + OCR 호출
│   │   ├── expenses.py            # GET · DELETE · PUT /api/expenses
│   │   └── summary.py             # GET /api/summary
│   ├── services/
│   │   ├── ocr_service.py         # Upstage information-extract API 연동
│   │   └── storage_service.py     # expenses.json 읽기/쓰기, UUID 생성
│   ├── data/expenses.json         # 지출 데이터 (JSON 배열)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/                 # Dashboard, UploadPage, ExpenseDetail
│   │   ├── components/            # DropZone, ParsePreview, ExpenseCard, SummaryCard, FilterBar, Badge, Modal, Toast
│   │   └── api/axios.js           # Axios 인스턴스 (baseURL: VITE_API_BASE_URL)
│   ├── package.json
│   └── vite.config.js
├── vercel.json
└── .env                           # UPSTAGE_API_KEY (절대 커밋 금지)
```

---

## API 명세

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 확인 |
| POST | `/api/upload` | 영수증 업로드 + OCR 파싱 → 지출 JSON 반환 |
| GET | `/api/expenses` | 목록 조회 (`?from=YYYY-MM-DD&to=YYYY-MM-DD`) |
| DELETE | `/api/expenses/{id}` | 항목 삭제 |
| PUT | `/api/expenses/{id}` | 항목 수정 |
| GET | `/api/summary` | 총합·이번달·카테고리별 통계 (`?month=YYYY-MM`) |

파일 검증: JPG, PNG, PDF만 허용 / 최대 10MB (클라이언트·서버 양쪽 검증).

---

## 데이터 스키마

```json
{
  "id": "uuid-v4",
  "created_at": "ISO-8601 UTC",
  "store_name": "이마트 강남점",
  "receipt_date": "YYYY-MM-DD",
  "receipt_time": "HH:MM",
  "category": "식료품|외식|교통|쇼핑|의료|기타",
  "items": [{ "name": "", "quantity": 0, "unit_price": 0, "total_price": 0 }],
  "subtotal": 0, "discount": 0, "tax": 0, "total_amount": 0,
  "payment_method": "신용카드",
  "raw_image_path": "uploads/..."
}
```

---

## 환경변수

| 변수 | 위치 | 설명 |
|------|------|------|
| `UPSTAGE_API_KEY` | `.env` / Vercel 환경변수 | Upstage API 인증 키 |
| `VITE_API_BASE_URL` | `.env.production` | 프론트 빌드 시 API URL (Vercel 배포 시 빈값 → 상대경로) |
| `DATA_FILE_PATH` | 자동 | `VERCEL=1` 감지 시 자동으로 `/tmp/expenses.json` 사용 |

---

## Vercel 배포 주의사항

- Vercel 서버리스는 파일 시스템이 **비지속적**이므로, 데이터는 `localStorage`에 병행 저장한다.
- 백엔드에서 `VERCEL=1` 환경변수 감지 시 `/tmp/expenses.json` 경로를 사용한다.
- Python 서버리스는 `@vercel/python` + Mangum을 사용해 FastAPI를 래핑한다.
- PDF 처리 시 `information-extract` API가 PDF를 직접 지원하므로 Vercel에서 Poppler 불필요. 로컬 개발 시에만 pdf2image+Poppler 사용.

---

## OCR 서비스 핵심 구조

`backend/services/ocr_service.py`에서 Upstage `information-extract` API를 직접 호출한다.

```python
# OpenAI SDK + Upstage information-extract API
from openai import OpenAI
client = OpenAI(api_key=UPSTAGE_API_KEY,
                base_url="https://api.upstage.ai/v1/information-extraction")

resp = client.chat.completions.create(
    model="information-extract",
    messages=[{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:application/octet-stream;base64,{b64}"}}
    ]}],
    response_format={"type": "json_schema", "json_schema": {"name": "receipt_schema", "schema": RECEIPT_SCHEMA}}
)
result = json.loads(resp.choices[0].message.content)
```

- 이미지(JPG/PNG)와 PDF 모두 동일한 방식으로 처리 (base64 인코딩)
- `response_format`의 JSON 스키마로 구조화 출력을 보장
- OCR 실패 시 `json.JSONDecodeError` 또는 API 예외를 잡아 HTTP 500으로 변환

---

## UI 가이드라인

- **폰트**: Pretendard (CDN), 폴백 Noto Sans KR
- **주 색상**: `indigo-600` (`#4F46E5`) — 버튼, 링크, 포커스 링
- **배경**: `gray-50`, 카드: `white`, 테두리: `gray-200`
- **Toast**: `fixed bottom-4 right-4`, 3초 자동 소멸, 중복 시 최신 메시지만 유지
- **그리드**: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4`
- **로딩 중 버튼**: `disabled opacity-50 cursor-not-allowed`

카테고리 뱃지 색상: 식료품=green, 외식=orange, 교통=blue, 쇼핑=purple, 의료=red, 기타=gray

---

## 신규 기술 사용 전 참조

Context7 MCP를 통해 최신 공식 문서를 먼저 확인한다.

```
# Upstage information-extract API 최신 사용법
use context7: upstage information-extract API json schema

# Vercel Python 서버리스 배포
use context7: vercel python serverless fastapi
```

### Source Code가 변경되거나 라이브러리 버전이 변경되면 반드시 @PRD_영수증_지출관리앱.md 같이 업데이트 하고, 완료 기준의 Check Box에 완료된 사항들도 모두 체크표시 하세요.
