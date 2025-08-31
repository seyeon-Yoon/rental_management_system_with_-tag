#!/usr/bin/env python3
"""
보조배터리 품목 추가
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

def create_power_bank_category(token):
    """보조배터리 카테고리 생성"""
    headers = get_headers(token)
    
    category_data = {
        "name": "보조배터리",
        "description": "각종 보조배터리 및 충전 관련 용품"
    }
    
    response = requests.post(f"{BASE_URL}/categories", json=category_data, headers=headers)
    if response.status_code == 201:
        category = response.json()
        print(f"✅ 카테고리 생성: {category_data['name']} (ID: {category['id']})")
        return category
    else:
        print(f"❌ 카테고리 생성 실패: {response.text}")
        return None

def add_power_banks(token, category_id):
    """보조배터리 품목들 추가"""
    headers = get_headers(token)
    
    # 보조배터리 품목 정보 (이름, 수량, 설명)
    power_bank_items = [
        ("보조배터리 8핀 일체형", 6, "8핀 연결선 일체형 보조배터리"),
        ("보조배터리 C타입 일체형", 9, "USB-C 연결선 일체형 보조배터리"),
        ("보조배터리 통합형", 6, "다중 포트 통합형 보조배터리"),
        ("보조배터리 연결선", 3, "보조배터리용 별도 연결선"),
    ]
    
    total_created = 0
    
    print("📦 보조배터리 카테고리에 품목 추가:")
    
    for item_name, quantity, description in power_bank_items:
        for i in range(quantity):
            # 고유한 일련번호 생성
            if "8핀" in item_name:
                serial_number = f"PB8PIN{i+1:03d}"
                display_name = f"보조배터리 8핀 일체형 #{i+1}"
            elif "C타입" in item_name:
                serial_number = f"PBCTYPE{i+1:03d}"
                display_name = f"보조배터리 C타입 일체형 #{i+1}"
            elif "통합형" in item_name:
                serial_number = f"PBMULTI{i+1:03d}"
                display_name = f"보조배터리 통합형 #{i+1}"
            elif "연결선" in item_name:
                serial_number = f"PBCABLE{i+1:03d}"
                display_name = f"보조배터리 연결선 #{i+1}"
            else:
                serial_number = f"POWERBANK{i+1:03d}"
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
    print("🔋 보조배터리 품목 추가")
    print("=" * 40)
    
    # 1. 로그인
    token = login_admin()
    if not token:
        return
    
    # 2. 보조배터리 카테고리 생성
    category = create_power_bank_category(token)
    if not category:
        return
    
    # 3. 보조배터리 품목 추가
    total_added = add_power_banks(token, category["id"])
    
    print(f"\n🎉 전자기기 카테고리에 총 {total_added}개 보조배터리 추가 완료!")
    print("추가된 품목:")
    print("- 보조배터리 8핀 일체형: 6개")
    print("- 보조배터리 C타입 일체형: 9개")
    print("- 보조배터리 통합형: 6개")
    print("- 보조배터리 연결선: 3개")
    print(f"📊 총 {6+9+6+3}개 품목")

if __name__ == "__main__":
    main()