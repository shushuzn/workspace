import sqlite3

conn = sqlite3.connect('D:/scripts/medium_seen_rss.db')
c = conn.cursor()

c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [r[0] for r in c.fetchall()]
print('Tables:', tables)

if 'seen_articles' in tables:
    c.execute('SELECT COUNT(*) FROM seen_articles')
    print('Total articles:', c.fetchone()[0])
    
    c.execute('SELECT title FROM seen_articles ORDER BY rowid DESC LIMIT 5')
    print('Latest 5:')
    for row in c.fetchall():
        print(f'  - {row[0][:60]}')

conn.close()
