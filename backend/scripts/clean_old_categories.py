#!/usr/bin/env python3
"""
기존 샘플 카테고리들 삭제
"""

import requests

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

def clean_old_categories(token):
    """기존 샘플 카테고리들 삭제"""
    headers = get_headers(token)
    
    # 현재 카테고리 조회
    response = requests.get(f"{BASE_URL}/categories", headers=headers)
    if response.status_code != 200:
        print("카테고리 조회 실패")
        return
    
    categories = response.json()["categories"]
    
    # 삭제할 기존 카테고리들 (우리가 새로 만든 것은 유지)
    keep_categories = ["스포츠용품", "문구/사무", "보드게임", "일상생활용품"]
    
    deleted_count = 0
    
    for category in categories:
        if category["name"] not in keep_categories:
            # 해당 카테고리의 품목들 먼저 삭제
            items_response = requests.get(f"{BASE_URL}/items?category_id={category['id']}", headers=headers)
            if items_response.status_code == 200:
                items_data = items_response.json()
                if "items" in items_data:
                    items = items_data["items"]
                    
                    print(f"카테고리 '{category['name']}'의 품목 {len(items)}개 삭제 중...")
                    for item in items:
                        delete_response = requests.delete(f"{BASE_URL}/items/{item['id']}", headers=headers)
                        if delete_response.status_code == 200:
                            print(f"  ✅ 품목 삭제: {item['name']}")
                        else:
                            print(f"  ❌ 품목 삭제 실패: {item['name']}")
            
            # 카테고리 삭제
            delete_response = requests.delete(f"{BASE_URL}/categories/{category['id']}", headers=headers)
            if delete_response.status_code == 200:
                print(f"✅ 카테고리 삭제: {category['name']}")
                deleted_count += 1
            else:
                print(f"❌ 카테고리 삭제 실패: {category['name']} - {delete_response.text}")
        else:
            print(f"⏭️  카테고리 유지: {category['name']}")
    
    return deleted_count

def main():
    """메인 실행 함수"""
    print("🧹 기존 샘플 카테고리 정리 시작")
    print("=" * 40)
    
    # 1. 로그인
    token = login_admin()
    if not token:
        return
    
    # 2. 기존 카테고리 정리
    deleted = clean_old_categories(token)
    
    print(f"\n🎉 기존 샘플 카테고리 {deleted}개 삭제 완료!")
    print("유지된 카테고리:")
    print("- 스포츠용품")
    print("- 문구/사무") 
    print("- 보드게임")
    print("- 일상생활용품")

if __name__ == "__main__":
    main()