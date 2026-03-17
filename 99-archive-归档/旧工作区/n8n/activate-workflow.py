import sqlite3
import os

# 数据库路径
db_path = os.path.expanduser("~/.n8n/database.sqlite")
print(f"数据库路径：{db_path}")

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 查询 OpenClaw 工作流
c.execute("SELECT id, name, active FROM workflow_entity WHERE name LIKE '%OpenClaw%'")
workflows = c.fetchall()

print("\n找到的工作流:")
for wf in workflows:
    print(f"  ID: {wf[0]}, 名称：{wf[1]}, 激活：{wf[2]}")
    
    # 激活工作流
    if not wf[2]:
        c.execute("UPDATE workflow_entity SET active = 1 WHERE id = ?", (wf[0],))
        print(f"  → 已激活：{wf[1]}")

conn.commit()
conn.close()

print("\n完成！")
