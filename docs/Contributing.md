# Git 컨벤션

## 브랜치

```
master
  ├── frontend
  ├── backend
  ├── ai
  └── embedded
```

**기능 브랜치:** `파트/feat/설명` 또는 `파트/fix/설명`

```
frontend/feat/login
backend/fix/token-error
```

## 커밋

```
[파트] type: 설명
```

| 파트 | 설명 |
|------|------|
| FE | Frontend |
| BE | Backend |
| AI | AI |
| EM | Embedded |

| Type | 설명 |
|------|------|
| feat | 새로운 기능 추가 |
| fix | 버그 수정 |
| docs | 문서 수정 (README 등) |
| refactor | 코드 리팩토링 (기능 변경 없이 코드 개선) |
| chore | 설정, 빌드, 패키지 등 기타 작업 |

**예시:**
```
[FE] feat: 로그인 페이지 구현
[BE] fix: 토큰 만료 처리 수정
[AI] feat: 이미지 분류 모델 추가
```

## MR(PR) 규칙

**MR(PR) 제목:** `[파트] type: 작업 내용`

```
[FE] feat: 로그인/회원가입 페이지 구현
[BE] fix: 토큰 갱신 로직 수정
```

- **1명 이상** Approve 후 병합
- Conflict 해결 후 MR 요청
- MR 전 Self-review 필수

## 주의사항

- master, 파트 브랜치에 직접 push 금지
- API Key, Token 등 민감 정보 커밋 금지
