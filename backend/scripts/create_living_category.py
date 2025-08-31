#!/usr/bin/env python3
"""
새로운 생활용품 카테고리 생성 및 품목 추가
"""

import requests
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

def create_living_category(token):
    """생활용품 카테고리 새로 생성"""
    headers = get_headers(token)
    
    category_data = {
        "name": "일상생활용품",
        "description": "우산, 실험복, 인공눈물 등 일상생활에 필요한 용품들"
    }
    
    response = requests.post(f"{BASE_URL}/categories", json=category_data, headers=headers)
    if response.status_code == 201:
        category = response.json()
        print(f"✅ 카테고리 생성: {category_data['name']} (ID: {category['id']})")
        return category
    else:
        print(f"❌ 카테고리 생성 실패: {response.text}")
        return None

def add_living_items(token, category_id):
    """일상생활용품 카테고리에 품목들 추가"""
    headers = get_headers(token)
    
    # 품목 정보 (이름, 수량, 설명)
    items_info = [
        ("우산", 30, "일반 우산"),
        ("실험복", 3, "실험실용 가운"),
        ("인공눈물", 10, "일회용 인공눈물"),
    ]
    
    total_created = 0
    
    print("📦 일상생활용품 카테고리에 품목 추가:")
    
    for item_name, quantity, description in items_info:
        for i in range(quantity):
            # 고유한 일련번호 생성
            if item_name == "우산":
                serial_number = f"UMBRELLA{i+1:03d}"
                display_name = f"우산 #{i+1}"
            elif item_name == "실험복":
                sizes = ["S", "M", "L"]
                size = sizes[i % 3] if i < 3 else "XL"
                serial_number = f"LABCOAT_{size}_{(i//3)+1:02d}"
                display_name = f"실험복 ({size})"
            elif item_name == "인공눈물":
                serial_number = f"EYEDROP{i+1:03d}"
                display_name = f"인공눈물 #{i+1}"
            else:
                serial_number = f"ITEM{i+1:04d}"
                display_name = f"{item_name} #{i+1}"
            
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
                
            time.sleep(0.05)  # API 요청 간격
        
        print(f"  ✅ {item_name}: {quantity}개")
    
    return total_created

def main():
    """메인 실행 함수"""
    print("🚀 일상생활용품 카테고리 및 품목 생성")
    print("=" * 50)
    
    # 1. 로그인
    token = login_admin()
    if not token:
        return
    
    # 2. 새 카테고리 생성
    category = create_living_category(token)
    if not category:
        return
    
    # 3. 품목 추가
    total_added = add_living_items(token, category["id"])
    
    print(f"\n🎉 일상생활용품 카테고리에 총 {total_added}개 품목 추가 완료!")
    print("- 우산: 30개")
    print("- 실험복: 3개 (S, M, L)")
    print("- 인공눈물: 10개")

if __name__ == "__main__":
    main()