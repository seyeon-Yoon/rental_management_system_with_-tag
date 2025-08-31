# 예약 시스템 notes 필드 관련 트러블슈팅

## 발생한 문제들

### 1차 문제: 예약 생성 실패
**에러**: `'notes' is an invalid keyword argument for Reservation`

```
HomePage.tsx:158 예약 실패: Error: 예약 생성 중 오류 발생: 'notes' is an invalid keyword argument for Reservation
    at api.ts:45:27
    at async Axios.request (axios.js?v=fb5abd3a:2139:14)
    at async Object.post (api.ts:59:22)
    at async handleReservation (HomePage.tsx:149:7)
```

### 2차 문제: 데이터베이스 스키마 불일치
**에러**: `sqlite3.OperationalError: no such column: reservations.notes`

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: reservations.notes
[SQL: SELECT reservations.id AS reservations_id, reservations.user_id AS reservations_user_id, 
reservations.item_id AS reservations_item_id, reservations.reserved_at AS reservations_reserved_at, 
reservations.expires_at AS reservations_expires_at, reservations.status AS reservations_status, 
reservations.notes AS reservations_notes, reservations.created_at AS reservations_created_at, 
reservations.updated_at AS reservations_updated_at 
FROM reservations 
WHERE ? = reservations.item_id]
```

### 3차 문제: 데이터 유실
데이터베이스 재생성 후 모든 카테고리와 아이템 데이터가 삭제됨

## 원인 분석

### 스키마 불일치 원인
1. **Pydantic 스키마**(`backend/app/schemas/reservation.py`)에는 `notes` 필드 존재:
   ```python
   class ReservationBase(BaseModel):
       item_id: int = Field(..., description="품목 ID")
       notes: Optional[str] = Field(None, max_length=500, description="예약 메모")
   ```

2. **SQLAlchemy 모델**(`backend/app/models/reservation.py`)에는 `notes` 필드 누락:
   ```python
   class Reservation(Base):
       __tablename__ = "reservations"
       
       id = Column(Integer, primary_key=True, index=True, comment="예약 ID")
       user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="사용자 ID")
       item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True, comment="품목 ID")
       # notes 필드가 없음!
   ```

3. **서비스 레이어**(`backend/app/services/reservation_service.py:215`)에서 존재하지 않는 필드 사용:
   ```python
   reservation = Reservation(
       user_id=user_id,
       item_id=reservation_data.item_id,
       notes=reservation_data.notes,  # ← 이 부분이 에러 발생
       status=ReservationStatus.PENDING,
       expires_at=expires_at
   )
   ```

### 데이터베이스 파일 혼동
- 삭제한 파일: `rental_management.db` (존재하지 않는 파일)
- 실제 사용 파일: `rental_system.db` (실제 데이터베이스 파일)

## 해결 과정

### 1단계: SQLAlchemy 모델에 notes 필드 추가

**파일**: `backend/app/models/reservation.py`

```python
# Import 추가
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, String

# Reservation 클래스 내부에 notes 필드 추가
class Reservation(Base):
    # 기존 필드들...
    
    # 상태
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False, index=True, comment="예약 상태")
    
    # 예약 메모 (새로 추가)
    notes = Column(String(500), nullable=True, comment="예약 메모")
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 시간")
```

### 2단계: 데이터베이스 재생성

기존 데이터베이스를 완전 삭제하고 새 스키마로 재생성:

```bash
# 올바른 데이터베이스 파일 삭제
cd backend && rm -f rental_system.db

# 백엔드 서버 재시작으로 새 스키마 적용
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3단계: 데이터 복원

1. **관리자 권한 부여**:
   ```bash
   cd backend && python scripts/grant_admin.py
   ```

2. **카테고리 및 아이템 데이터 복원**:
   ```bash
   cd backend && python scripts/api_seed_items.py
   ```

## 최종 결과

### 성공적으로 해결된 문제들
- ✅ `'notes' is an invalid keyword argument for Reservation` 에러 해결
- ✅ `500 Internal Server Error` 해결  
- ✅ `no such column: reservations.notes` 에러 해결
- ✅ 사라진 카테고리와 아이템 데이터 복원 (4개 카테고리, 109개 품목)
- ✅ 관리자 권한 복원

### 새로운 데이터베이스 스키마
```sql
CREATE TABLE reservations (
    id INTEGER NOT NULL, 
    user_id INTEGER NOT NULL, 
    item_id INTEGER NOT NULL, 
    reserved_at DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
    expires_at DATETIME NOT NULL, 
    status VARCHAR(9) NOT NULL, 
    notes VARCHAR(500),  -- 새로 추가된 필드
    created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
    updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id), 
    FOREIGN KEY(item_id) REFERENCES items (id)
);
```

### 복원된 데이터
- **스포츠용품**: 농구공, 축구공, 배드민턴 채, 테니스 채, 탁구채 등
- **문구/사무**: 공학용계산기 12개
- **생활용품**: 우산 30개, 실험복, 인공눈물 등  
- **보드게임**: 해적룰렛, 루미큐브, 젠가, 카탄 등 23종

## 예방책

### 1. 스키마 동기화 확인
Pydantic 스키마와 SQLAlchemy 모델 간의 필드 일치 확인:
```bash
# 스키마 검증 스크립트 실행 권장
python scripts/validate_schemas.py
```

### 2. 마이그레이션 시스템 도입
Alembic을 사용한 데이터베이스 마이그레이션 시스템 구축 권장

### 3. 테스트 강화
- 모델과 스키마 일치성 테스트
- API 엔드포인트 통합 테스트
- 데이터베이스 스키마 검증 테스트

## 참고사항

이번 이슈는 **Pydantic 스키마와 SQLAlchemy 모델 간의 불일치**로 인해 발생한 전형적인 스키마 동기화 문제였습니다. 향후 새로운 필드를 추가할 때는 반드시 다음 요소들을 모두 업데이트해야 합니다:

1. SQLAlchemy 모델 (데이터베이스 스키마)
2. Pydantic 스키마 (API 검증)
3. 서비스 레이어 (비즈니스 로직)
4. 데이터베이스 마이그레이션 (기존 데이터 유지)

---

**문서 작성일**: 2025-08-31  
**작성자**: Claude Code Assistant  
**관련 이슈**: 예약 시스템 notes 필드 추가 및 스키마 동기화