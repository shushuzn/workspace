import sqlite3
import os

# 数据库路径
db_path = os.path.expanduser("~/.n8n/database.sqlite")
print(f"数据库路径：{db_path}")

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 查询所有工作流
c.execute("SELECT id, name, active FROM workflow_entity")
workflows = c.fetchall()

print(f"\n找到 {len(workflows)} 个工作流:")
activated = 0
for wf in workflows:
    print(f"  ID: {wf[0]}, 名称：{wf[1]}, 激活：{wf[2]}")

    # 激活所有工作流
    if not wf[2]:
        c.execute("UPDATE workflow_entity SET active = 1 WHERE id = ?", (wf[0],))
        print(f"  → 已激活：{wf[1]}")
        activated += 1

conn.commit()
conn.close()

print(f"\n完成！新激活 {activated} 个工作流")
