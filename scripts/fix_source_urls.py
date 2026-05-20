import sqlite3

conn = sqlite3.connect('data/antigravity_bot.db')
cursor = conn.cursor()

updates = [
    # (new_url, old_url)
    ('https://www.hissf.or.kr/info/notice', 'https://www.hissf.or.kr'),
    ('https://www.kosaf.go.kr/ko/notice.do?ctgrId1=0000000002', 'https://www.kosaf.go.kr'),
    ('http://www.bitgoeul.gwangju.go.kr/notice', 'http://www.bitgoeul.gwangju.go.kr'),
    ('https://www.cmkfoundation-scholarship.org/apply', 'https://www.cmkfoundation-scholarship.org'),
    ('https://scholarship.ktng.com/apply', 'https://scholarship.ktng.com'),
    ('http://www.daeguedu.or.kr/contents/contents.do?contentsNo=156', 'http://www.daeguedu.or.kr'),
    ('https://www.daejeon.go.kr/scholarship', 'https://www.daejeon.go.kr'),
]

for new_url, old_url in updates:
    cursor.execute('UPDATE scholarships SET source=? WHERE source=?', (new_url, old_url))
    print(f'Updated {cursor.rowcount} rows: {old_url[:50]} -> {new_url[:50]}')

conn.commit()
conn.close()
print('All DB source URLs updated successfully.')
