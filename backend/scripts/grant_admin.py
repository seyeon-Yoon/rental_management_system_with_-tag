#!/usr/bin/env python3
"""
사용자에게 관리자 권한 부여
"""

import requests
import sqlite3
import os

def grant_admin_via_db(student_id: str):
    """SQLite DB를 직접 수정해서 관리자 권한 부여"""
    db_path = "/home/seyeon/rental_management_system_with_-tag/backend/rental_system.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 현재 사용자 정보 확인
        cursor.execute("SELECT id, student_id, name, role FROM users WHERE student_id = ?", (student_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ 사용자를 찾을 수 없습니다: {student_id}")
            return False
        
        print(f"현재 사용자 정보: ID={user[0]}, 학번={user[1]}, 이름={user[2]}, 권한={user[3]}")
        
        # 관리자 권한으로 변경
        cursor.execute("UPDATE users SET role = 'ADMIN' WHERE student_id = ?", (student_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ {student_id} 사용자에게 관리자 권한을 부여했습니다")
            
            # 확인
            cursor.execute("SELECT role FROM users WHERE student_id = ?", (student_id,))
            new_role = cursor.fetchone()[0]
            print(f"✅ 현재 권한: {new_role}")
            
            return True
        else:
            print(f"❌ 권한 변경 실패")
            return False
            
    except Exception as e:
        print(f"❌ 데이터베이스 오류: {e}")
        return False
    finally:
        conn.close()

def main():
    """메인 실행 함수"""
    print("🔑 관리자 권한 부여 스크립트")
    print("=" * 40)
    
    student_id = "202210950"
    
    success = grant_admin_via_db(student_id)
    
    if success:
        print("\n🎉 권한 부여 완료!")
        print("이제 다시 시드 스크립트를 실행할 수 있습니다.")
    else:
        print("\n❌ 권한 부여 실패")

if __name__ == "__main__":
    main()