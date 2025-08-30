#!/usr/bin/env python3
"""
샘플 데이터 생성 스크립트
프론트엔드 개발 및 테스트를 위한 더미 데이터를 데이터베이스에 추가합니다.
"""

import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

# 프로젝트 루트를 Python path에 추가
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.item import Item, ItemStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.rental import Rental, RentalStatus
from app.core.security import get_password_hash


def create_sample_users(db: Session):
    """샘플 사용자 생성"""
    print("🔑 샘플 사용자 생성 중...")
    
    users_data = [
        # 관리자 계정
        {
            "student_id": "2024001",
            "name": "김관리",
            "department": "융합공과대학",
            "email": "admin@convergence.ac.kr",
            "role": UserRole.ADMIN,
            "is_active": True,
        },
        {
            "student_id": "2024002", 
            "name": "이운영",
            "department": "융합공과대학",
            "email": "admin2@convergence.ac.kr",
            "role": UserRole.ADMIN,
            "is_active": True,
        },
        # 학생 계정
        {
            "student_id": "2024101",
            "name": "박학생",
            "department": "컴퓨터과학전공",
            "email": "student1@convergence.ac.kr",
            "role": UserRole.STUDENT,
            "is_active": True,
        },
        {
            "student_id": "2024102",
            "name": "최융공",
            "department": "전자공학과",
            "email": "student2@convergence.ac.kr", 
            "role": UserRole.STUDENT,
            "is_active": True,
        },
        {
            "student_id": "2024103",
            "name": "윤대여",
            "department": "기계공학과",
            "email": "student3@convergence.ac.kr",
            "role": UserRole.STUDENT,
            "is_active": True,
        },
        {
            "student_id": "2024104",
            "name": "정예약",
            "department": "화학공학과", 
            "email": "student4@convergence.ac.kr",
            "role": UserRole.STUDENT,
            "is_active": True,
        },
        {
            "student_id": "2024105",
            "name": "강반납",
            "department": "건설환경공학과",
            "email": "student5@convergence.ac.kr",
            "role": UserRole.STUDENT,
            "is_active": True,
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # 중복 체크
        existing_user = db.query(User).filter(User.student_id == user_data["student_id"]).first()
        if existing_user:
            print(f"  ⚠️  사용자 {user_data['student_id']} 이미 존재")
            created_users.append(existing_user)
            continue
            
        user = User(**user_data)
        db.add(user)
        created_users.append(user)
        print(f"  ✅ 사용자 생성: {user_data['name']} ({user_data['student_id']})")
    
    db.commit()
    return created_users


def create_sample_categories(db: Session):
    """샘플 카테고리 생성"""
    print("📂 샘플 카테고리 생성 중...")
    
    categories_data = [
        {
            "name": "운동용품",
            "description": "스포츠 및 운동 관련 용품들",
            "is_active": True
        },
        {
            "name": "전자기기", 
            "description": "보조배터리, 계산기 등 전자제품",
            "is_active": True
        },
        {
            "name": "생활용품",
            "description": "우산, 인공눈물, 상비약 등 일상용품", 
            "is_active": True
        },
        {
            "name": "엔터테인먼트",
            "description": "보드게임, 놀이용품",
            "is_active": True
        },
        {
            "name": "학업용품",
            "description": "실험복, 학습 도구 등",
            "is_active": True
        },
        {
            "name": "IT장비",
            "description": "노트북, 태블릿, 액세서리",
            "is_active": True
        },
        {
            "name": "캠핑용품", 
            "description": "텐트, 침낭, 캠핑 장비",
            "is_active": True
        },
        {
            "name": "취미용품",
            "description": "카메라, 악기, 미술용품",
            "is_active": False  # 하나는 비활성 상태로
        }
    ]
    
    created_categories = []
    for cat_data in categories_data:
        # 중복 체크
        existing_category = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if existing_category:
            print(f"  ⚠️  카테고리 '{cat_data['name']}' 이미 존재")
            created_categories.append(existing_category)
            continue
            
        category = Category(**cat_data)
        db.add(category)
        created_categories.append(category)
        print(f"  ✅ 카테고리 생성: {cat_data['name']}")
    
    db.commit()
    return created_categories


def create_sample_items(db: Session, categories: list[Category]):
    """샘플 품목 생성"""
    print("📦 샘플 품목 생성 중...")
    
    items_data = [
        # 운동용품
        {"name": "축구공", "serial": "SPORT-001", "category": "운동용품", "status": ItemStatus.AVAILABLE, "metadata": {"브랜드": "나이키", "크기": "5호"}},
        {"name": "농구공", "serial": "SPORT-002", "category": "운동용품", "status": ItemStatus.AVAILABLE, "metadata": {"브랜드": "스팰딩", "크기": "7호"}},
        {"name": "배드민턴 라켓", "serial": "SPORT-003", "category": "운동용품", "status": ItemStatus.RENTED, "metadata": {"브랜드": "요넥스", "무게": "85g"}},
        {"name": "탁구 라켓 세트", "serial": "SPORT-004", "category": "운동용품", "status": ItemStatus.AVAILABLE, "metadata": {"구성": "라켓2개+공3개"}},
        
        # 전자기기  
        {"name": "보조배터리", "serial": "ELEC-001", "category": "전자기기", "status": ItemStatus.RESERVED, "metadata": {"용량": "20000mAh", "브랜드": "삼성"}},
        {"name": "보조배터리", "serial": "ELEC-002", "category": "전자기기", "status": ItemStatus.AVAILABLE, "metadata": {"용량": "10000mAh", "브랜드": "LG"}},
        {"name": "공학용 계산기", "serial": "ELEC-003", "category": "전자기기", "status": ItemStatus.AVAILABLE, "metadata": {"모델": "TI-84 Plus CE", "기능": "그래프 계산기"}},
        {"name": "무선 마우스", "serial": "ELEC-004", "category": "전자기기", "status": ItemStatus.RENTED, "metadata": {"브랜드": "로지텍", "연결": "USB 무선"}},
        
        # 생활용품
        {"name": "우산", "serial": "LIFE-001", "category": "생활용품", "status": ItemStatus.AVAILABLE, "metadata": {"색상": "검정", "크기": "장우산"}},
        {"name": "우산", "serial": "LIFE-002", "category": "생활용품", "status": ItemStatus.AVAILABLE, "metadata": {"색상": "파랑", "크기": "접이식"}},
        {"name": "인공눈물", "serial": "LIFE-003", "category": "생활용품", "status": ItemStatus.AVAILABLE, "metadata": {"브랜드": "히알리안", "용량": "10ml"}},
        {"name": "두통약", "serial": "LIFE-004", "category": "생활용품", "status": ItemStatus.AVAILABLE, "metadata": {"브랜드": "타이레놀", "개수": "20정"}},
        
        # 엔터테인먼트
        {"name": "할리갈리", "serial": "GAME-001", "category": "엔터테인먼트", "status": ItemStatus.AVAILABLE, "metadata": {"인원": "2-6명", "시간": "15분"}},
        {"name": "카탄", "serial": "GAME-002", "category": "엔터테인먼트", "status": ItemStatus.RENTED, "metadata": {"인원": "3-4명", "시간": "60-90분"}},
        {"name": "루미큐브", "serial": "GAME-003", "category": "엔터테인먼트", "status": ItemStatus.AVAILABLE, "metadata": {"인원": "2-4명", "시간": "30분"}},
        
        # 학업용품
        {"name": "실험복", "serial": "STUDY-001", "category": "학업용품", "status": ItemStatus.AVAILABLE, "metadata": {"크기": "M", "색상": "흰색"}},
        {"name": "실험복", "serial": "STUDY-002", "category": "학업용품", "status": ItemStatus.AVAILABLE, "metadata": {"크기": "L", "색상": "흰색"}},
        {"name": "안전고글", "serial": "STUDY-003", "category": "학업용품", "status": ItemStatus.AVAILABLE, "metadata": {"종류": "화학실험용"}},
        
        # IT장비
        {"name": "노트북 거치대", "serial": "IT-001", "category": "IT장비", "status": ItemStatus.AVAILABLE, "metadata": {"재질": "알루미늄", "각도조절": "가능"}},
        {"name": "USB 허브", "serial": "IT-002", "category": "IT장비", "status": ItemStatus.AVAILABLE, "metadata": {"포트": "USB 3.0 x4", "전원": "어댑터"}},
        
        # 캠핑용품
        {"name": "1인용 텐트", "serial": "CAMP-001", "category": "캠핑용품", "status": ItemStatus.AVAILABLE, "metadata": {"브랜드": "코베아", "무게": "2.1kg"}},
        {"name": "침낭", "serial": "CAMP-002", "category": "캠핑용품", "status": ItemStatus.AVAILABLE, "metadata": {"온도": "0도", "크기": "성인용"}},
        {"name": "캠핑 의자", "serial": "CAMP-003", "category": "캠핑용품", "status": ItemStatus.RENTED, "metadata": {"접이식": "O", "무게": "1.2kg"}},
    ]
    
    # 카테고리 매핑
    category_map = {cat.name: cat for cat in categories}
    
    created_items = []
    for item_data in items_data:
        # 중복 체크
        existing_item = db.query(Item).filter(Item.serial_number == item_data["serial"]).first()
        if existing_item:
            print(f"  ⚠️  품목 '{item_data['serial']}' 이미 존재")
            created_items.append(existing_item)
            continue
            
        category = category_map.get(item_data["category"])
        if not category:
            print(f"  ❌ 카테고리 '{item_data['category']}' 찾을 수 없음")
            continue
            
        item = Item(
            name=item_data["name"],
            serial_number=item_data["serial"],
            category_id=category.id,
            status=item_data["status"],
            description=f"{item_data['name']} - {item_data['category']}",
            item_metadata=item_data.get("metadata"),
            is_active=True
        )
        
        db.add(item)
        created_items.append(item)
        print(f"  ✅ 품목 생성: {item_data['name']} ({item_data['serial']}) - {item_data['status']}")
    
    db.commit()
    return created_items


def create_sample_reservations(db: Session, users: list[User], items: list[Item]):
    """샘플 예약 생성"""
    print("🔖 샘플 예약 생성 중...")
    
    # 학생 사용자들만 필터링
    students = [user for user in users if user.role == UserRole.STUDENT]
    
    # RESERVED 상태인 품목들
    reserved_items = [item for item in items if item.status == ItemStatus.RESERVED]
    
    reservations_data = []
    for i, item in enumerate(reserved_items[:3]):  # 최대 3개의 예약 생성
        if i < len(students):
            # 일부는 만료 임박, 일부는 여유시간 있게
            if i == 0:
                # 5분 후 만료 (긴급)
                expires_at = datetime.now() + timedelta(minutes=5)
            elif i == 1:
                # 30분 후 만료 (주의)  
                expires_at = datetime.now() + timedelta(minutes=30)
            else:
                # 50분 후 만료 (여유)
                expires_at = datetime.now() + timedelta(minutes=50)
                
            reservations_data.append({
                "user": students[i],
                "item": item,
                "expires_at": expires_at,
                "status": ReservationStatus.PENDING
            })
    
    created_reservations = []
    for res_data in reservations_data:
        reservation = Reservation(
            user_id=res_data["user"].id,
            item_id=res_data["item"].id,
            reserved_at=datetime.now(),
            expires_at=res_data["expires_at"],
            status=res_data["status"]
        )
        
        db.add(reservation)
        created_reservations.append(reservation)
        minutes_left = int((res_data["expires_at"] - datetime.now()).total_seconds() / 60)
        print(f"  ✅ 예약 생성: {res_data['user'].name} - {res_data['item'].name} ({minutes_left}분 남음)")
    
    db.commit()
    return created_reservations


def create_sample_rentals(db: Session, users: list[User], items: list[Item]):
    """샘플 대여 생성"""
    print("📅 샘플 대여 생성 중...")
    
    # 학생 사용자들만 필터링
    students = [user for user in users if user.role == UserRole.STUDENT]
    
    # RENTED 상태인 품목들
    rented_items = [item for item in items if item.status == ItemStatus.RENTED]
    
    rentals_data = []
    for i, item in enumerate(rented_items):
        if i < len(students):
            # 다양한 대여 상황 생성
            if i == 0:
                # 오늘 시작해서 내일 반납 예정 (정상)
                rental_date = datetime.now().date()
                due_date = rental_date + timedelta(days=1)
                status = RentalStatus.ACTIVE
            elif i == 1:
                # 3일 전에 시작해서 4일 후 반납 예정 (정상, 중간)
                rental_date = datetime.now().date() - timedelta(days=3)
                due_date = rental_date + timedelta(days=7)
                status = RentalStatus.ACTIVE
            elif i == 2:
                # 일주일 전에 시작해서 이미 연체 상태
                rental_date = datetime.now().date() - timedelta(days=8)
                due_date = rental_date + timedelta(days=7)
                status = RentalStatus.OVERDUE
            else:
                # 기본 대여 (5일 전 시작, 2일 후 반납)
                rental_date = datetime.now().date() - timedelta(days=5)
                due_date = rental_date + timedelta(days=7)
                status = RentalStatus.ACTIVE
                
            rentals_data.append({
                "user": students[i % len(students)],
                "item": item,
                "rental_date": rental_date,
                "due_date": due_date,
                "status": status
            })
    
    created_rentals = []
    for rent_data in rentals_data:
        rental = Rental(
            user_id=rent_data["user"].id,
            item_id=rent_data["item"].id,
            rental_date=rent_data["rental_date"],
            due_date=rent_data["due_date"],
            status=rent_data["status"]
        )
        
        db.add(rental)
        created_rentals.append(rental)
        
        days_left = (rent_data["due_date"] - datetime.now().date()).days
        status_emoji = "⚠️" if rent_data["status"] == RentalStatus.OVERDUE else "✅"
        print(f"  {status_emoji} 대여 생성: {rent_data['user'].name} - {rent_data['item'].name} ({days_left}일 {'연체' if days_left < 0 else '남음'})")
    
    db.commit()
    return created_rentals


def create_audit_logs(db: Session):
    """샘플 감사 로그 생성"""
    print("📝 샘플 감사 로그 생성 중...")
    
    # 기본적인 시스템 활동 로그들이 자동으로 생성되므로
    # 추가적인 샘플 데이터는 생성하지 않음
    print("  ℹ️  감사 로그는 시스템 활동에 따라 자동 생성됩니다")


def reset_database(db: Session):
    """데이터베이스 초기화 (개발용)"""
    print("🗑️  기존 데이터 삭제 중...")
    
    # 외래 키 제약조건 순서에 맞춰 삭제
    db.execute(text("DELETE FROM audit_logs"))
    db.execute(text("DELETE FROM rentals"))
    db.execute(text("DELETE FROM reservations"))
    db.execute(text("DELETE FROM items"))
    db.execute(text("DELETE FROM categories"))
    db.execute(text("DELETE FROM users"))
    
    # SQLite의 경우 시퀀스 초기화
    if "sqlite" in str(db.bind.url):
        db.execute(text("DELETE FROM sqlite_sequence"))
    
    db.commit()
    print("  ✅ 기존 데이터 삭제 완료")


def main():
    """메인 실행 함수"""
    print("🌱 샘플 데이터 생성 스크립트 시작")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 옵션: 기존 데이터 삭제 (주의!)
        # 비대화형 모드에서는 자동으로 추가만 진행 (중복 데이터는 스킵)
        print("기존 데이터는 유지하고 누락된 데이터만 추가합니다 (중복 시 스킵)")
        print("전체 초기화가 필요한 경우 스크립트를 수정하여 reset_database(db) 호출")
        
        # 1. 사용자 생성
        users = create_sample_users(db)
        
        # 2. 카테고리 생성
        categories = create_sample_categories(db)
        
        # 3. 품목 생성
        items = create_sample_items(db, categories)
        
        # 4. 예약 생성
        reservations = create_sample_reservations(db, users, items)
        
        # 5. 대여 생성
        rentals = create_sample_rentals(db, users, items)
        
        # 6. 감사 로그 (자동 생성)
        create_audit_logs(db)
        
        print("\n" + "=" * 50)
        print("✅ 샘플 데이터 생성 완료!")
        print(f"📊 생성된 데이터:")
        print(f"   👥 사용자: {len(users)}명 (관리자 2명, 학생 5명)")
        print(f"   📂 카테고리: {len(categories)}개")
        print(f"   📦 품목: {len(items)}개")
        print(f"   🔖 예약: {len(reservations)}개")
        print(f"   📅 대여: {len(rentals)}개")
        
        print(f"\n🔗 테스트 계정 정보:")
        print(f"   관리자: 2024001 (김관리), 2024002 (이운영)")
        print(f"   학생: 2024101 (박학생), 2024102 (최융공), 2024103 (윤대여)")
        print(f"   ※ 비밀번호는 백엔드 API 연동 시 대학교 시스템을 통해 설정")
        
        print(f"\n🌐 API 테스트:")
        print(f"   Swagger UI: http://localhost:8000/docs")
        print(f"   Health Check: http://localhost:8000/health")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()