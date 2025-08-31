#!/usr/bin/env python3
"""
기존 생활용품 카테고리에 남은 품목들 추가
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

def get_categories(token):
    """카테고리 조회"""
    headers = get_headers(token)
    response = requests.get(f"{BASE_URL}/categories", headers=headers)
    if response.status_code == 200:
        data = response.json()
        return {cat["name"]: cat for cat in data["categories"]}
    return {}

def add_living_items(token, living_category_id):
    """생활용품 카테고리에 남은 품목들 추가"""
    headers = get_headers(token)
    
    # 우산과 실험복, 인공눈물 추가
    living_items = [
        ("우산", 30, "일반 우산"),
        ("실험복", 3, "실험실용 가운"),
        ("인공눈물", 10, "일회용 인공눈물"),
    ]
    
    total_created = 0
    
    print("📦 생활용품 카테고리에 품목 추가:")
    
    for item_name, quantity, description in living_items:
        for i in range(quantity):
            # 일련번호 생성 (기존과 겹치지 않도록 수정)
            if quantity > 1:
                if item_name == "우산":
                    serial_number = f"UMB{i+1:03d}"  # 우산용 특별 번호
                elif item_name == "실험복":
                    sizes = ["S", "M", "L"]
                    size_name = sizes[i % 3] if i < 3 else f"L{i-2}"
                    serial_number = f"LAB{size_name}"
                    display_name = f"{item_name} ({size_name})"
                else:
                    serial_number = f"{item_name[:2].upper()}{i+1:04d}"  # 4자리로 변경
                    display_name = f"{item_name} #{i+1}"
            else:
                serial_number = f"{item_name[:3].upper()}999"  # 고유한 번호
                display_name = item_name
                
            if 'display_name' not in locals():
                display_name = f"{item_name} #{i+1}" if quantity > 1 else item_name
            
            item_data = {
                "name": display_name,
                "category_id": living_category_id,
                "description": description,
                "serial_number": serial_number,
                "location": "학생회실"
            }
            
            response = requests.post(f"{BASE_URL}/items", json=item_data, headers=headers)
            if response.status_code == 201:
                total_created += 1
            else:
                print(f"❌ 품목 생성 실패: {display_name} - {response.text}")
                
            time.sleep(0.1)
            
            # display_name 초기화
            del display_name
        
        print(f"  ✅ {item_name}: {quantity}개")
    
    return total_created

def main():
    """메인 실행 함수"""
    print("🚀 남은 품목들 추가 시작")
    print("=" * 40)
    
    # 1. 로그인
    token = login_admin()
    if not token:
        return
    
    # 2. 카테고리 조회
    categories = get_categories(token)
    
    if "생활용품" not in categories:
        print("❌ 생활용품 카테고리를 찾을 수 없습니다")
        return
    
    living_category_id = categories["생활용품"]["id"]
    print(f"✅ 생활용품 카테고리 ID: {living_category_id}")
    
    # 3. 남은 품목들 추가
    total_added = add_living_items(token, living_category_id)
    
    print(f"\n🎉 총 {total_added}개 품목 추가 완료!")

if __name__ == "__main__":
    main()