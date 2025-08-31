#!/usr/bin/env python3
"""
API를 통한 실제 대여물품 목록 업데이트
2025-08-31
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def login_admin():
    """관리자 로그인"""
    login_data = {
        "student_id": "202210950",
        "password": "seyeon0303!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"로그인 실패: {response.text}")
        return None

def get_headers(token):
    """인증 헤더 생성"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def clear_existing_data(token):
    """기존 데이터 조회 및 삭제"""
    headers = get_headers(token)
    
    # 기존 카테고리 조회
    response = requests.get(f"{BASE_URL}/categories", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"API 응답: {data}")  # 디버그용
        
        # API 응답이 배열인지 객체인지 확인
        if isinstance(data, dict) and "categories" in data:
            categories = data["categories"]
        elif isinstance(data, list):
            categories = data
        else:
            categories = []
            
        print(f"기존 카테고리 {len(categories)}개 발견")
        
        # 각 카테고리의 품목들 삭제
        for category in categories:
            cat_id = category["id"]
            # 해당 카테고리의 품목들 조회
            items_response = requests.get(f"{BASE_URL}/items?category_id={cat_id}", headers=headers)
            if items_response.status_code == 200:
                items_data = items_response.json()
                if isinstance(items_data, dict) and "items" in items_data:
                    items = items_data["items"]
                elif isinstance(items_data, list):
                    items = items_data
                else:
                    items = []
                    
                print(f"카테고리 '{category['name']}'의 품목 {len(items)}개 삭제 중...")
                
                for item in items:
                    delete_response = requests.delete(f"{BASE_URL}/items/{item['id']}", headers=headers)
                    if delete_response.status_code != 200:
                        print(f"품목 삭제 실패: {item['name']}")
            
            # 카테고리 삭제
            delete_cat_response = requests.delete(f"{BASE_URL}/categories/{cat_id}", headers=headers)
            if delete_cat_response.status_code != 200:
                print(f"카테고리 삭제 실패: {category['name']}")
    
    print("✅ 기존 데이터 정리 완료")

def create_categories(token):
    """새 카테고리 생성"""
    headers = get_headers(token)
    
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
    
    created_categories = {}
    
    for cat_data in categories_data:
        response = requests.post(f"{BASE_URL}/categories", json=cat_data, headers=headers)
        if response.status_code == 201:
            category = response.json()
            created_categories[cat_data["name"]] = category
            print(f"✅ 카테고리 생성: {cat_data['name']} (ID: {category['id']})")
        else:
            print(f"❌ 카테고리 생성 실패: {cat_data['name']} - {response.text}")
    
    return created_categories

def create_items(token, categories):
    """실제 대여물품 생성"""
    headers = get_headers(token)
    
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
        ("인공눈물", 10, "일회용 인공눈물"),
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
    
    total_created = 0
    
    for items_data, category_name in item_groups:
        if category_name not in categories:
            print(f"❌ 카테고리를 찾을 수 없습니다: {category_name}")
            continue
            
        category_id = categories[category_name]["id"]
        print(f"\n📦 {category_name} 카테고리:")
        
        for item_name, quantity, description in items_data:
            for i in range(quantity):
                # 일련번호 생성
                if quantity > 1:
                    serial_number = f"{item_name[:3].upper()}{i+1:03d}"
                    display_name = f"{item_name} #{i+1}"
                else:
                    serial_number = f"{item_name[:3].upper()}001"
                    display_name = item_name
                
                item_data = {
                    "name": display_name,
                    "category_id": category_id,
                    "description": description,
                    "serial_number": serial_number,
                    "location": "학생회실"
                }
                
                response = requests.post(f"{BASE_URL}/items", json=item_data, headers=headers)
                if response.status_code == 201:
                    total_created += 1
                else:
                    print(f"❌ 품목 생성 실패: {display_name} - {response.text}")
                    
                time.sleep(0.1)  # API 요청 간격
            
            print(f"  ✅ {item_name}: {quantity}개")
    
    return total_created

def main():
    """메인 실행 함수"""
    print("🚀 API를 통한 실제 대여물품 목록 업데이트 시작")
    print("=" * 60)
    
    # 1. 관리자 로그인
    print("1️⃣ 관리자 로그인...")
    token = login_admin()
    if not token:
        print("❌ 로그인 실패")
        return
    print("✅ 로그인 성공")
    
    # 2. 기존 데이터 정리
    print("\n2️⃣ 기존 데이터 정리...")
    clear_existing_data(token)
    
    # 3. 새 카테고리 생성
    print("\n3️⃣ 새 카테고리 생성...")
    categories = create_categories(token)
    
    # 4. 새 품목들 생성
    print("\n4️⃣ 실제 대여물품 생성...")
    total_items = create_items(token, categories)
    
    print("\n" + "=" * 60)
    print("🎉 실제 대여물품 목록 업데이트 완료!")
    print(f"📊 총 4개 카테고리, {total_items}개 품목 생성")
    print("\n예상 카테고리별 품목 수:")
    print("- 스포츠용품: 33개")
    print("- 문구/사무: 12개") 
    print("- 생활용품: 43개")
    print("- 보드게임: 30개")
    print(f"\n💡 예상 총합: 118개 품목")

if __name__ == "__main__":
    main()