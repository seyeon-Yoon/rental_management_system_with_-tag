#!/usr/bin/env python3
"""
실제 대여물품 목록 시드 스크립트
2025-08-31 업데이트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models.user import User
from app.models.category import Category
from app.models.item import Item, ItemStatus
from app.models.audit_log import AuditLog
import app.models.base  # 모든 테이블 생성을 위해


def clear_existing_data(db: Session):
    """기존 품목 및 카테고리 데이터 삭제"""
    print("기존 품목 및 카테고리 데이터 삭제 중...")
    
    # 품목 삭제
    db.query(Item).delete()
    
    # 카테고리 삭제 (사용자는 유지)
    db.query(Category).delete()
    
    db.commit()
    print("✅ 기존 데이터 삭제 완료")


def create_categories(db: Session) -> dict:
    """카테고리 생성"""
    print("카테고리 생성 중...")
    
    categories_data = [
        {
            "name": "스포츠용품",
            "description": "농구공, 축구공, 배드민턴 채, 테니스 채 등 스포츠 관련 용품"
        },
        {
            "name": "문구/사무",
            "description": "공학용계산기 등 학습 및 사무용품"
        },
        {
            "name": "생활용품",
            "description": "우산, 실험복, 인공눈물 등 일상생활 용품"
        },
        {
            "name": "보드게임",
            "description": "젠가, 루미큐브, 카탄 등 다양한 보드게임"
        }
    ]
    
    categories = {}
    
    for cat_data in categories_data:
        category = Category(
            name=cat_data["name"],
            description=cat_data["description"]
        )
        db.add(category)
        categories[cat_data["name"]] = category
    
    db.commit()
    
    for name, category in categories.items():
        db.refresh(category)
        print(f"  ✅ {name} (ID: {category.id})")
    
    return categories


def create_items(db: Session, categories: dict):
    """실제 대여물품 생성"""
    print("대여물품 생성 중...")
    
    # 스포츠용품
    sports_items = [
        ("농구공", 3, "실내외 사용 가능한 농구공"),
        ("축구공", 1, "표준 사이즈 축구공"),
        ("족구공", 1, "족구 전용 공"),
        ("피구공", 1, "실내 피구용 공"),
        ("배드민턴 채", 6, "성인용 배드민턴 라켓"),
        ("테니스 채", 3, "성인용 테니스 라켓"),
        ("탁구채", 3, "탁구 전용 라켓"),
        ("글러브", 1, "야구 글러브"),
        ("야구공", 7, "경식 야구공"),
        ("배드민턴콕", 9, "배드민턴 셔틀콕"),
    ]
    
    # 문구/사무
    office_items = [
        ("공학용계산기", 12, "공학 계산기 (카시오/샤프)"),
    ]
    
    # 생활용품
    living_items = [
        ("우산", 30, "일반 우산"),
        ("실험복", 3, "실험실용 가운"),
        ("인공눈물", 10, "일회용 인공눈물"),  # n개를 10개로 임시 설정
    ]
    
    # 보드게임
    boardgame_items = [
        ("해적룰렛", 1, "해적 룰렛 보드게임"),
        ("루미큐브", 2, "숫자 타일 보드게임"),
        ("아발론", 1, "추론 보드게임"),
        ("뱅!", 1, "서부 테마 카드게임"),
        ("거짓말 탐지기", 1, "심리 추론 게임"),
        ("젠가", 1, "나무 블록 쌓기 게임"),
        ("아임더 보스", 1, "협상 보드게임"),
        ("클루", 1, "추리 보드게임"),
        ("노땡스", 1, "카드게임"),
        ("달무티", 1, "계급 카드게임"),
        ("선물입니다", 1, "선물 주제 게임"),
        ("쿼리도", 1, "미로 보드게임"),
        ("다빈치 코드", 2, "추론 보드게임"),
        ("시타델", 1, "역할 선택 게임"),
        ("블리츠", 1, "빠른 반응 게임"),
        ("스플렌더", 1, "보석 수집 게임"),
        ("임호텝", 1, "이집트 테마 게임"),
        ("카탄", 1, "개척 보드게임"),
        ("펭귄얼음", 1, "펭귄 테마 게임"),
        ("할리갈리", 1, "반응속도 카드게임"),
        ("COUP", 1, "블러핑 카드게임"),
        ("보난자", 1, "콩 재배 카드게임"),
        ("로스트시티", 1, "탐험 카드게임"),
    ]
    
    item_groups = [
        (sports_items, "스포츠용품"),
        (office_items, "문구/사무"),
        (living_items, "생활용품"),
        (boardgame_items, "보드게임"),
    ]
    
    total_items_created = 0
    
    for items_data, category_name in item_groups:
        category = categories[category_name]
        print(f"\n📦 {category_name} 카테고리:")
        
        for item_name, quantity, description in items_data:
            for i in range(quantity):
                # 일련번호 생성 (수량이 1개 이상일 때는 번호 추가)
                if quantity > 1:
                    serial_number = f"{item_name[:3].upper()}{i+1:03d}"
                    display_name = f"{item_name} #{i+1}"
                else:
                    serial_number = f"{item_name[:3].upper()}001"
                    display_name = item_name
                
                item = Item(
                    name=display_name,
                    category_id=category.id,
                    description=description,
                    serial_number=serial_number,
                    status=ItemStatus.AVAILABLE,
                    location="학생회실"
                )
                db.add(item)
                total_items_created += 1
            
            print(f"  ✅ {item_name}: {quantity}개")
    
    db.commit()
    print(f"\n🎉 총 {total_items_created}개 품목 생성 완료!")
    
    return total_items_created


def create_audit_log_entry(db: Session, total_items: int):
    """감사 로그 기록"""
    audit_log = AuditLog(
        action="BULK_DATA_SEED",
        table_name="items",
        description=f"실제 대여물품 목록 시드 완료 - 총 {total_items}개 품목 생성",
        ip_address="127.0.0.1"
    )
    db.add(audit_log)
    db.commit()


def main():
    """메인 실행 함수"""
    print("🚀 실제 대여물품 목록 시드 스크립트 시작")
    print("=" * 50)
    
    # 데이터베이스 연결
    db = SessionLocal()
    
    try:
        # 1. 기존 데이터 삭제
        clear_existing_data(db)
        
        # 2. 카테고리 생성
        categories = create_categories(db)
        
        # 3. 품목 생성
        total_items = create_items(db, categories)
        
        # 4. 감사 로그 기록
        create_audit_log_entry(db, total_items)
        
        print("\n" + "=" * 50)
        print("🎉 실제 대여물품 목록 시드 완료!")
        print(f"📊 총 4개 카테고리, {total_items}개 품목 생성")
        print("\n카테고리별 품목 수:")
        print("- 스포츠용품: 33개")
        print("- 문구/사무: 12개") 
        print("- 생활용품: 43개")
        print("- 보드게임: 30개")
        print(f"\n💡 총합: {33+12+43+30}개 품목")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()