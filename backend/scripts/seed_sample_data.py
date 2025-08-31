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


def create_sample_categories(db: Session):
    """샘플 카테고리 생성"""
    print("📂 샘플 카테고리 생성 중...")
    
    categories_data = [
        {
            "name": "운동용품",
            "description": "다양한 운동용품 및 스포츠 장비",
            "is_active": True,
        },
        {
            "name": "전자기기",
            "description": "전자기기 및 IT 장비",
            "is_active": True,
        },
        {
            "name": "생활용품",
            "description": "일상 생활에 필요한 용품들",
            "is_active": True,
        },
        {
            "name": "엔터테인먼트",
            "description": "보드게임, 오락용품 등",
            "is_active": True,
        },
        {
            "name": "학업용품",
            "description": "학습 및 실험에 필요한 용품들",
            "is_active": True,
        },
        {
            "name": "캠핑용품",
            "description": "야외활동 및 캠핑 장비",
            "is_active": True,
        },
        {
            "name": "의료용품",
            "description": "응급처치 및 건강관리 용품",
            "is_active": True,
        },
        {
            "name": "기타",
            "description": "기타 유용한 물품들",
            "is_active": True,
        }
    ]
    
    for category_data in categories_data:
        category = Category(**category_data)
        db.add(category)
    
    db.commit()
    print(f"✅ {len(categories_data)}개 카테고리 생성 완료")


def create_sample_items(db: Session):
    """샘플 품목 생성"""
    print("📦 샘플 품목 생성 중...")
    
    # 카테고리 조회
    categories = db.query(Category).all()
    category_map = {cat.name: cat.id for cat in categories}
    
    items_data = [
        # 운동용품
        {"name": "축구공", "category_id": category_map["운동용품"], "serial_number": "SPORTS-001", "status": ItemStatus.AVAILABLE},
        {"name": "농구공", "category_id": category_map["운동용품"], "serial_number": "SPORTS-002", "status": ItemStatus.AVAILABLE},
        {"name": "배드민턴 라켓", "category_id": category_map["운동용품"], "serial_number": "SPORTS-003", "status": ItemStatus.AVAILABLE},
        
        # 전자기기
        {"name": "보조배터리 10000mAh", "category_id": category_map["전자기기"], "serial_number": "ELEC-001", "status": ItemStatus.AVAILABLE},
        {"name": "보조배터리 20000mAh", "category_id": category_map["전자기기"], "serial_number": "ELEC-002", "status": ItemStatus.AVAILABLE},
        {"name": "공학용계산기", "category_id": category_map["전자기기"], "serial_number": "ELEC-003", "status": ItemStatus.AVAILABLE},
        
        # 생활용품
        {"name": "우산", "category_id": category_map["생활용품"], "serial_number": "LIFE-001", "status": ItemStatus.AVAILABLE},
        {"name": "우산", "category_id": category_map["생활용품"], "serial_number": "LIFE-002", "status": ItemStatus.AVAILABLE},
        {"name": "인공눈물", "category_id": category_map["생활용품"], "serial_number": "LIFE-003", "status": ItemStatus.AVAILABLE},
        
        # 엔터테인먼트
        {"name": "카탄", "category_id": category_map["엔터테인먼트"], "serial_number": "GAME-001", "status": ItemStatus.AVAILABLE},
        {"name": "스플렌더", "category_id": category_map["엔터테인먼트"], "serial_number": "GAME-002", "status": ItemStatus.AVAILABLE},
        {"name": "윷놀이", "category_id": category_map["엔터테인먼트"], "serial_number": "GAME-003", "status": ItemStatus.AVAILABLE},
        
        # 학업용품
        {"name": "실험복 (L)", "category_id": category_map["학업용품"], "serial_number": "EDU-001", "status": ItemStatus.AVAILABLE},
        {"name": "실험복 (M)", "category_id": category_map["학업용품"], "serial_number": "EDU-002", "status": ItemStatus.AVAILABLE},
        {"name": "실험복 (S)", "category_id": category_map["학업용품"], "serial_number": "EDU-003", "status": ItemStatus.AVAILABLE},
        
        # 캠핑용품
        {"name": "캠핑의자", "category_id": category_map["캠핑용품"], "serial_number": "CAMP-001", "status": ItemStatus.AVAILABLE},
        {"name": "캠핑테이블", "category_id": category_map["캠핑용품"], "serial_number": "CAMP-002", "status": ItemStatus.AVAILABLE},
        {"name": "랜턴", "category_id": category_map["캠핑용품"], "serial_number": "CAMP-003", "status": ItemStatus.AVAILABLE},
        
        # 의료용품
        {"name": "체온계", "category_id": category_map["의료용품"], "serial_number": "MED-001", "status": ItemStatus.AVAILABLE},
        {"name": "응급처치키트", "category_id": category_map["의료용품"], "serial_number": "MED-002", "status": ItemStatus.AVAILABLE},
        
        # 기타
        {"name": "휴대용 선풍기", "category_id": category_map["기타"], "serial_number": "ETC-001", "status": ItemStatus.AVAILABLE},
        {"name": "물티슈", "category_id": category_map["기타"], "serial_number": "ETC-002", "status": ItemStatus.AVAILABLE},
    ]
    
    for item_data in items_data:
        # JSONB 메타데이터 추가
        item_data['metadata'] = {
            "condition": "양호",
            "location": "학생회실",
            "purchase_date": "2024-01-01",
            "notes": "정상 작동"
        }
        item = Item(**item_data)
        db.add(item)
    
    db.commit()
    print(f"✅ {len(items_data)}개 품목 생성 완료")


def initialize_database():
    """데이터베이스 테이블 초기화 및 샘플 데이터 생성"""
    print("🚀 데이터베이스 초기화 및 샘플 데이터 생성 시작")
    
    # 데이터베이스 세션 생성
    db = SessionLocal()
    
    try:
        # 기존 데이터 삭제 (테스트 환경용)
        print("🧹 기존 데이터 정리 중...")
        
        # 외래 키 제약 조건 순서에 맞춰 삭제
        db.execute(text("DELETE FROM audit_logs"))
        db.execute(text("DELETE FROM rentals"))  
        db.execute(text("DELETE FROM reservations"))
        db.execute(text("DELETE FROM items"))
        db.execute(text("DELETE FROM categories"))
        db.execute(text("DELETE FROM users"))
        
        db.commit()
        print("✅ 기존 데이터 정리 완료")
        
        # 샘플 데이터 생성
        create_sample_categories(db)
        create_sample_items(db)
        
        print("🎉 샘플 데이터 생성이 완료되었습니다!")
        print("📊 생성된 데이터:")
        print(f"   - 카테고리: {db.query(Category).count()}개")
        print(f"   - 품목: {db.query(Item).count()}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()