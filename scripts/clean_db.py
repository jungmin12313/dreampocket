import sqlite3

def clean_database():
    db_path = "d:/bot/data/antigravity_bot.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    irrelevant_keywords = [
        '결과', '커뮤니티', '발표', '합격자', '수기', '후기', '게시판', '기자단', 
        '서포터즈', '명단', '수여식', '꿀팁', 'MOU', '드림스폰', '지급요청서', 
        '사전교육', '반환', '포기', '모니터링', '영상안내', '교육영상', '설명회', 
        '사용내역', '보고서', '간담회', '발대식', '수혜자', '수정공고', '지급 안내', '변경 안내'
    ]
    
    # Check both title and source URL logic or just title for spam keywords
    deleted_count = 0
    cursor.execute('SELECT id, title FROM scholarships')
    rows = cursor.fetchall()
    
    for row in rows:
        sch_id, title = row
        if any(kw in title for kw in irrelevant_keywords):
            cursor.execute('DELETE FROM scholarships WHERE id = ?', (sch_id,))
            deleted_count += 1
            print(f"Deleted spam entry: {title}")

    conn.commit()
    conn.close()
    print(f"\nDB Cleansing Complete. Total {deleted_count} spam entries removed.")

if __name__ == "__main__":
    clean_database()
