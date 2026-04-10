# Idea Pool

- [20260411] seed [brainstorm] [score:3x4=12] [f:4] [angle:ws-level] brainstorm-roadmap支持--project过滤 | benefit: 查看指定项目路线图 | reason: 已知资源：scripts/brainstorm-roadmap.mjs已有；缺失环节：无--project过滤 | approach: 1. bash node scripts/brainstorm-roadmap.mjs --project task-orchestrator | shipped:20260411
- [20260411] seed [brainstorm] [score:3x4=12] [f:4] [angle:ws-level] brainstorm-roadmap增加--days过滤参数 | benefit: 支持查看最近N天的shipped记录 | reason: 已知资源：brainstorm-roadmap.mjs已有daysLimit解析；缺失环节：无--days命令行参数 | approach: 1. bash node scripts/brainstorm-roadmap.mjs --days 7 | shipped:20260411
- [20260411] seed [brainstorm] [score:3x4=12] [f:4] [angle:ws-level] run-seed.mjs支持--warm-all输出JSON格式 | benefit: --warm-all --json 输出机器可读格式 | reason: 已知资源：run-seed.mjs已有--warm-all；缺失环节：无JSON格式输出 | approach: 1. bash node shared/run-seed.mjs --warm-all --json | shipped:20260411



- [20260412] seed [brainstorm] [score:3x4=12] [f:4] [angle:ws-level] wiki-indexer增加fuzzy模糊搜索 | benefit: 输入近似词也能搜到相关条目 | reason: 已知资源：D:/OpenClaw/workspace/shared/wiki-indexer.mjs已存在，✓ shared/wiki-indexer.mjs 存在，186行；缺失环节：无模糊匹配；连接方式：fuzzy库→搜索时容错匹配 | approach: 1. python shared/wiki-indexer-fuzzy.py test | shipped:20260412

- [20260410] seed [brainstorm] [score:4x3=12] [f:3] [angle:skill-file] 利用134个预定义agent模板 — 当brainstorm遇到特定任务类型时自动spawn对应agent | benefit: OMC每次遇到代码审查/架构设计等任务都是硬做，有了agent模板就能自动分派专业角色，效率提升10x | reason: 已有134个agent模板在插件目录里睡觉(claude-plugins-official:59, compound-engineering:43, omc:22)，OMC skill体系没有与它们挂钩的机制 | approach: 1. node shared/scan-agent-templates.mjs 扫描所有插件的agents/目录，提取name/description/tools/model，输出agent-registry.json 2. 创建skill: agent-dispatcher，读取agent-registry，当brainstorm任务匹配到对应agent类型时，输出spawn建议 3. 修改brainstorm流程，在候选池构建后加一步：用agent-dispatcher检查是否有匹配agent 4. 若匹配，在seed的approach中标注"[spawn:atomic-architect]"，实现时Agent工具加载对应模板 | shipped:20260410

- [20260412] seed [brainstorm] [score:3x4=12] [f:4] [angle:ws-level] hookify规则dry-run验证器 | benefit: 创建hookify规则前先验证regex是否正确 | reason: 已知资源：D:/OpenClaw/workspace/.claude/hookify.warn-rm.local.md格式已有，✓ hookify.warn-rm.local.md 存在；缺失环节：无regex语法验证；连接方式：读取规则regex→用RegExp验证→输出正确/错误 | approach: 1. node shared/hookify-validate.mjs | shipped:20260409

- [20260412] seed [brainstorm] [score:3x4=12] [f:4] [angle:ws-level] brainstorm-metacognition自检报告 | benefit: 自动生成批次效果分析报告，辅助调整策略 | reason: 已知资源：D:/OpenClaw/workspace/.omc/innovation/brainstorm-metacognition.jsonl已有批次记录，✓ brainstorm-metacognition.jsonl 存在；缺失环节：无自动分析报告；连接方式：读取JSONL→统计shipped率/Gate失败率→生成改善建议 | approach: 1. node shared/brainstorm-report.mjs | shipped:20260409

- [20260412] seed [brainstorm] [score:3x3=9] [f:3] [angle:feature] [focus:task-orchestrator] task-orchestrator超时外层wrapper | benefit: 外层wrapper控制总超时，代替每次改executor.mjs | reason: 已知资源：D:/OpenClaw/workspace/80-PROJECTS/task-orchestrator/src/executor.mjs已有run()；缺失环节：无外层超时控制；连接方式：wrapper script调用executor→超时后kill进程树 | approach: 1. node 80-PROJECTS/CLI-Anything/bin/check-registry.mjs | shipped:20260412('80-PROJECTS/task-orchestrator/bin/run-with-timeout.mjs','w').write('#!/usr/bin/env node\nimport{execSync}from\"child_process\"\nconst t=parseInt(process.argv[2]||5)\nconst cmd=process.argv.slice(3)\ntry{execSync(cmd.join(\" \"),{stdio:\"inherit\",timeout:t*60000})}catch(e){console.error(e.message);process.exit(1)}')" 2. node 80-PROJECTS/task-orchestrator/bin/run-with-timeout.mjs 2 node --version

- [20260412] seed [brainstorm] [score:3x4=12] [f:4] [angle:new-project] [focus:CLI-Anything] CLI-Anything registry健康度检查 | benefit: 快速发现坏掉的adapter，防止坏adapter进入CI | reason: 已知资源：D:/OpenClaw/workspace/80-PROJECTS/CLI-Anything/registry.json已存在，✓ registry.json 存在；缺失环节：无adapter可用性验证；连接方式：registry.json读取→npx调用每个adapter --help→记录失败 | approach: 1. python -c "open('80-PROJECTS/CLI-Anything/bin/check-registry.mjs','w').write('#!/usr/bin/env node\nimport{readFileSync}from\"fs\"\nimport{execSync}from\"child_process\"\nconst r=JSON.parse(readFileSync(new URL(\"./../registry.json\",import.meta.url),\"utf8\"))\nlet ok=0,fail=0\nfor(const c of r.clis||[]){try{execSync(\"npx \"+c.name+\" --help\",{stdio:\"pipe\",timeout:5000});ok++}catch{fail++}}\nconsole.log(\"OK:\",ok,\"FAIL:\",fail)')" 2. node 80-PROJECTS/CLI-Anything/bin/check-registry.mjs | shipped:20260409

- [20260412] seed [brainstorm] [score:3x4=12] [f:4] [angle:new-project] [focus:opencli] opencli CDP session录制脚本 | benefit: 录制browser操作session并回放，自动化测试 | reason: 已知资源：D:/OpenClaw/workspace/80-PROJECTS/opencli/src/browser/daemon-client.ts已有CDP连接；缺失环节：无session录制功能 | approach: 1. node 80-PROJECTS/opencli/bin/record-session.mjs ws://localhost:9222 session-test.json | shipped:20260409

- [20260412] seed [brainstorm] [score:3x4=12] [f:4] [angle:ws-level] wikipedia arxiv条目新鲜度检测 | benefit: 快速发现超过30天未更新的arxiv条目 | reason: 已知资源：knowledge/wikipedia/index.json已有条目列表 | approach: 1. python shared/wiki-fresh-check.py | shipped:20260409

- [20260412] seed [brainstorm] [score:3x3=9] [f:3] [angle:quality] [focus:multi-agent-hub] multi-agent-hub annealing CSV导出 | benefit: 将annealing过程的温度/能量数据导出为CSV便于分析 | reason: 已知资源：cognitiveAnnealing.mjs已有annealing数据 | approach: 1. node 80-PROJECTS/multi-agent-hub/bin/export-annealing.mjs | shipped:20260409




















- [20260409] seed [brainstorm] [score:2x1=2] [f:1] [angle:feature] [focus:task-orchestrator] task-orchestrator自适应执行策略 | benefit: 根据历史成功率自动切换adapter，显著提升任务完成率 | reason: 已知资源：D:/OpenClaw/workspace/80-PROJECTS/task-orchestrator/src/executor.mjs已有execute()方法；D:/OpenClaw/workspace/80-PROJECTS/task-orchestrator/src/registry.mjs已有adapter注册；缺失环节：无策略选择机制；连接方式：executor记录每次adapter成功率→planner下次选择最优adapter | approach: 1. node 80-PROJECTS/task-orchestrator/bin/adaptive-executor.mjs | shipped:20260409

- [20260409] seed [brainstorm] [score:3x2=6] [f:2] [angle:feature] [focus:opencli] opencli CDP daemon健康度监控 | benefit: 实时显示daemon状态、页面池、连接数，排查连接问题 | reason: 已知资源：D:/OpenClaw/workspace/80-PROJECTS/opencli/src/browser/daemon-client.ts已有fetchDaemonStatus()；缺失环节：无daemon状态可视化；连接方式：定时轮询daemon-client→输出实时dashboard | approach: 1. node 80-PROJECTS/opencli/bin/daemon-health.mjs | shipped:20260409

- [20260409] seed [brainstorm] [score:3x3=9] [f:3] [angle:feature] [focus:multi-agent-hub] annealing过程CSV导出 | benefit: 把annealing每轮温度/能量/概念跳跃记录到CSV，便于后续分析 | reason: 已知资源：D:/OpenClaw/workspace/80-PROJECTS/multi-agent-hub/index.js已有TemperatureScheduler和round数据；缺失环节：无法导出CSV；连接方式：在index.js的round循环中插入CSV写入→保存到results/ | approach: 1. node 80-PROJECTS/multi-agent-hub/bin/export-annealing-csv.mjs | shipped:20260409

- [20260409] seed [brainstorm] [score:3x4=12] [f:4] [angle:feature] [focus:wikipedia] wiki页面关系图生成器 | benefit: 根据wiki-link生成页面之间的关系图，便于理解知识结构 | reason: 已知资源：D:/OpenClaw/workspace/knowledge/wikipedia/index.mjs已有索引和wikilink提取逻辑；缺失环节：无关系图生成；连接方式：解析index.mjs的wikilink数据→输出Graphviz或Mermaid图 | approach: 1. node shared/wiki-graph.mjs | shipped:20260409

- [20260409] seed [brainstorm] [score:3x4=12] [f:4] [angle:ws-level] session操作轨迹回放 | benefit: 从transcript文件重放一系列操作步骤，便于调试和复现 | reason: 已知资源：D:/OpenClaw/workspace/.claude/projects/有transcript.jsonl文件；缺失环节：无回放引擎；连接方式：读取transcript→解析tool call序列→逐条重放 | approach: 1. node shared/session-replay.mjs | shipped:20260409

- [20260409] seed [brainstorm] [score:3x4=12] [f:4] [angle:feature] [focus:CLI-Anything] CLI-Anything adapter参数补全生成 | benefit: 根据已有adapter自动生成shell completion脚本 | reason: 已知资源：D:/OpenClaw/workspace/80-PROJECTS/CLI-Anything/registry.json已有adapter列表；缺失环节：无completion生成；连接方式：读取registry.json→解析命令参数→输出bash/zsh completion脚本 | approach: 1. node 80-PROJECTS/CLI-Anything/bin/gen-completions.mjs | shipped:20260409

- [20260409] seed [brainstorm] [score:4x5=20] [f:5] [angle:feature] [focus:task-orchestrator] task-orchestrator规则关键词高亮 | benefit: 输入文本时高亮匹配的关键词，快速判断适用规则 | reason: 已知资源：D:/OpenClaw/workspace/80-PROJECTS/task-orchestrator/src/planner.mjs已有keywords数组；缺失环节：无线上高亮工具；连接方式：读取planner.mjs的keywords→ANSI高亮输出 | approach: 1. node 80-PROJECTS/task-orchestrator/bin/rule-highlight.mjs | shipped:20260409

- [20260409] seed [brainstorm] [score:3x3=9] [f:3] [angle:ws-level] notepad自动过期清理 | benefit: 自动删除超过7天的priority区entry，保持notepad整洁 | reason: 已知资源：D:/OpenClaw/workspace/.omc/notepad.md已有notepad数据结构；缺失环节：无自动清理；连接方式：读取notepad→解析priority区→删除超过7天的entry→写回 | approach: 1. node shared/notepad-prune.mjs | shipped:20260409



- [20260413] seed [brainstorm] [score:2x2] [f:2] [angle:feature] [focus:task-orchestrator] task-orchestrator添加adapter成功率加权选择——根据exec-history.jsonl历史数据自动选最优adapter | benefit: 减少人工干预，提升任务完成率 | reason: 已知资源：bin/exec-history.mjs已实现recordResult()+getBestAdapter()，返回{adapterId,score,successRate}；缺失环节：无调用方；连接方式：在executor.mjs的adapter选择逻辑中调用getBestAdapter(taskType)替代硬编码顺序 | approach: 1) Read bin/exec-history.mjs确认API 2) Read src/executor.mjs找到adapter选择位置 3) Edit用getBestAdapter()替换硬编码adapter链 4) 测试：分别用browse/search/task类型验证最优adapter被选中 | shipped:20260413
- [20260413] seed [brainstorm] [score:2x2] [f:2] [angle:ws-level] shared/添加CRC校验脚本——计算文件CRC32并在文件名中追加校验和后缀 | benefit: 全workspace复用，确保文件传输完整性 | reason: 已知资源：shared/目录存在但无文件校验工具；缺失环节：无CRC计算工具；连接方式：创建shared/crc32-file.mjs供各项目调用 | approach: 1) Write shared/crc32-file.mjs用Node.js内置crypto计算CRC32 2) 命令：node shared/crc32-file.mjs <file> 输出"filename_crc32.ext" 3) 各项目可通过exec调用此脚本 | shipped:20260413
- [20260413] seed [brainstorm] [score:2x2] [f:2] [angle:fusion] opencli+CLI-Anything融合——opencli的BrowserBridge能力嫁接到CLI-Anything作为新adapter | benefit: CLI-Anything获得browser automation能力，opencli获得更多CLI工具 | reason: 已知资源：opencli/src/browser/有BrowserBridge；CLI-Anything/bin/有adapter注册逻辑；缺失环节：无跨项目adapter共享机制；连接方式：在CLI-Anything的adapter注册表引用opencli的BrowserBridge模块 | approach: 1) Read opencli/src/browser/index.ts确认BrowserBridge导出 2) Read CLI-Anything/bin/registry-dashboard.mjs研究adapter注册格式 3) 在CLI-Anything中添加opencli-browser adapter 4) 测试：CLI-Anything调用opencli执行browser任务 | shipped:20260413


- [20260413] seed [brainstorm] [score:3x2] [f:2] [angle:feature] [focus:wikipedia] wikipedia添加论文对比视图——并排展示两篇arXiv论文的核心贡献和差异 | benefit: 快速判断论文是否值得深入阅读，减少信息过载 | reason: 已知资源：wikipedia/wiki.mjs已有arXiv API和笔记模板；缺失环节：无对比视图；连接方式：读取两篇笔记的摘要→输出并排对比HTML | approach: 1) Read wiki.mjs理解笔记结构 2) Write shared/paper-compare.mjs生成对比HTML 3) 测试：对比两篇LLM论文 | shipped:20260413
- [20260413] seed [brainstorm] [score:3x2] [f:2] [angle:feature] [focus:task-orchestrator] task-orchestrator添加执行回放CLI——根据历史执行记录回放相同步骤 | benefit: 调试工作流更容易，无需手动重跑 | reason: 已知资源：src/executor.mjs已有runId和step记录；缺失环节：无回放功能；连接方式：从exec-history读取steps→重新执行并对比输出 | approach: 1) Read bin/exec-history.mjs确认数据结构 2) Write shared/replay-run.mjs 3) 测试：回放一个简单task步骤 | shipped:20260413
- [20260413] seed [brainstorm] [score:4x2] [f:2] [angle:ws-level] shared/添加项目依赖图生成器——扫描workspace下所有package.json生成依赖关系图 | benefit: 全workspace可见性，了解项目间依赖关系 | reason: 已知资源：workspace下多个项目有package.json；缺失环节：无全局依赖视图；连接方式：扫描80-PROJECTS/*/package.json→Graphviz输出 | approach: 1) Write shared/dep-graph.mjs 2) 测试：生成前5个项目的依赖图 | shipped:20260413
- [20260413] seed [brainstorm] [score:3x3] [f:3] [angle:skill-file] run-seed.mjs添加shipped后自动生成insight记录 | benefit: 每次shipped自动记录学习到下次brainstorm自动复用 | reason: 已知资源：run-seed.mjs已有shipped标记逻辑；缺失环节：无shipped后自动生成learning input；连接方式：在shipped标记后调用insight生成逻辑写入auto-insight-trigger.json | approach: 1. Read shared/run-seed.mjs找到shipped标记位置 2. Edit在shipped后插入insight生成调用 3. 测试：ship一个seed验证trigger文件被正确写入 | shipped:20260413
- [20260413] seed [brainstorm] [score:4x4] [f:4] [angle:feature] [focus:task-orchestrator] task-orchestrator添加执行历史趋势图——exec-history统计可视化 | benefit: 直观看到adapter成功率趋势，快速发现退化 | reason: 已知资源：bin/exec-history.mjs已有recordResult()和历史数据；缺失环节：无趋势可视化；连接方式：读取exec-history.jsonl→按日期聚合→输出ASCII趋势图 | approach: 1. Read bin/exec-history.mjs确认数据格式 2. Write shared/exec-history-viz.mjs 3. 测试：node shared/exec-history-viz.mjs查看输出 | shipped:20260413
- [20260413] seed [brainstorm] [score:3x3] [f:3] [angle:feature] [focus:wikipedia] wikipedia wiki-link自动修复——linkcheck发现断链后自动生成修复建议 | benefit: 减少人工修复成本，提升wiki维护效率 | reason: 已知资源：wiki.mjs已有linkcheck命令和断链列表；缺失环节：无自动修复功能；连接方式：读取断链列表→分析文件引用→生成修复命令或直接修复 | approach: 1. Read wiki.mjs的linkcheck实现 2. Edit添加auto-fix模式 3. 测试：node wiki.mjs linkcheck --auto | shipped:20260413
- [20260413] seed [brainstorm] [score:4x4] [f:4] [angle:ws-level] shared/添加CLI健康度检测——检查workspace下项目依赖完整性 | benefit: 快速发现缺失依赖或版本冲突 | reason: 已知资源：shared/目录存在多个工具脚本；缺失环节：无依赖健康检查；连接方式：扫描80-PROJECTS/*/package.json→检查node_modules存在性 | approach: 1. Write shared/check-deps-health.mjs 2. 测试：node shared/check-deps-health.mjs 3. UT：验证缺失dep检测正确 | shipped:20260413
- [20260413] seed [brainstorm] [score:3x4] [f:4] [angle:ws-level] shared/添加notepad自动过期清理——删除超过7天的priority区entry | benefit: 保持notepad整洁，避免信息过期堆积 | reason: 已知资源：.omc/notepad.md已有notepad数据结构；缺失环节：无自动清理；连接方式：读取notepad→解析priority区→删除超过7天的entry→写回 | approach: 1. Write shared/notepad-prune.mjs 2. 测试：node shared/notepad-prune.mjs 3. UT：验证过期entry被删除 | shipped:20260413
- [20260413] seed [brainstorm] [score:4x3] [f:3] [angle:feature] [focus:wikipedia] wikipedia添加批量导入脚本——批量从arxiv ID列表生成条目 | benefit: 快速从ID列表批量导入论文笔记 | reason: 已知资源：wiki.mjs已有ingest命令支持单个论文；缺失环节：无批量导入；连接方式：读取ID列表→循环调用ingest→生成批量条目 | approach: 1. Read wiki.mjs的ingest实现 2. Write shared/wiki-batch-import.mjs 3. UT：验证ID解析正确 4. IT：测试批量导入 | shipped:20260413
- [20260413] seed [brainstorm] [score:3x3] [f:3] [angle:skill-file] task-orchestrator添加adapter成功率加权选择——根据历史数据自动选最优adapter | benefit: 减少人工干预，提升任务完成率 | reason: 已知资源：bin/exec-history.mjs已有recordResult()和getBestAdapter()；缺失环节：executor.mjs无调用方；连接方式：在adapter选择逻辑中调用getBestAdapter()替换硬编码顺序 | approach: 1. Read src/executor.mjs找到adapter选择位置 2. Edit调用getBestAdapter() 3. 测试：运行task验证最优adapter被选中 | shipped:20260413
- [20260414] seed [brainstorm] [score:4x3] [f:3] [angle:feature] [focus:task-orchestrator] task-orchestrator添加RED-GREEN-REFACTOR skill enforcement hooks | benefit: 强制chain执行遵循PLAN→CODE→TEST→REFACTOR顺序，减少盲目编码 | reason: 已知资源：task-orchestrator已有chain执行框架+registry-loader | 缺失环节：无skill强制触发机制，superpower的skill自动触发未实现 | 连接方式：扩展skill插件系统，添加on-chain-checkpoint钩子，在checkpoint验证phase顺序 | approach: 1. node task-orchestrator/src/skill-hook-generator.mjs --template=red-green-refactor 2. 在skill-hook-generator.mjs输出中定义checkpoint类型：PLAN→CODE→TEST→REFACTOR 3. 实现onCheckpoint(phase)钩子，对非RED-GREEN-REFACTOR顺序的chain报错 4. 在task-orchestrator/index.ts的executeChain中注入checkpoint验证 5. 写UT：验证正常流程通过、跳过TEST阶段触发错误 | shipped:20260414
- [20260414] seed [brainstorm] [score:3x4] [f:4] [angle:ws-level] shared/添加workspace脚本健康度诊断——统一检测所有工具脚本完整性 | benefit: 快速发现缺失依赖或语法错误，提升workspace脚本质量 | reason: 已知资源：workspace shared/已有工具函数+scripts/目录 | 缺失环节：缺少统一诊断工具检测脚本健康状态 | 连接方式：创建shared/script-diagnostics.mjs作为入口，扫描所有.js/.mjs文件 | approach: 1. node shared/script-diagnostics.mjs --init 2. 扫描workspace所有.js/.mjs文件，过滤node_modules和dist 3. 检测缺失项：require但未安装的依赖、缺失module.exports、syntax error 4. 输出诊断报告：文件路径+问题类型+修复建议 5. 集成到pre-commit hook | shipped:20260414
- [20260414] seed [brainstorm] [score:4x2] [f:2] [angle:project-fusion] task-orchestrator+opencli CDP browser chain fusion | benefit: task-orchestrator可直接编排browser任务链，实现端到端自动化 | reason: 已知资源：opencli已有Chrome CDP browser automation bridge | 缺失环节：task-orchestrator无法直接编排browser任务链 | 连接方式：新增opencli-adapter作为task-orchestrator的执行节点，封装browser命令 | approach: 1. mkdir -p task-orchestrator/src/adapters/opencli 2. 创建task-orchestrator/src/adapters/opencli/cdp-bridge.ts，封装opencli的browser命令 3. 定义CDPTaskNode接口：{ type:'browser', action:'click'|'type'|'eval', selector:string } 4. 在task-orchestrator的chain-executor中注册opencli adapter 5. 写IT：task-orchestrator编排opencli执行browser chain并验证结果 | shipped:20260414

- [20260415] seed [brainstorm] [score:3x3=9] [f:3] [angle:feature] [focus:task-orchestrator] task-orchestrator添加chain执行可视化——实时显示当前步骤/总步骤数 | benefit: 执行过程透明化，快速定位卡在哪一步 | reason: 已知资源：src/executor.mjs已有executeChain()循环，共5个step | 缺失环节：无执行进度可视化，用户看不到chain进行到哪了 | ←延伸自：20260414 skill enforcement hooks（chain黑箱） | 连接方式：在executor.mjs的step循环内插入进度输出（ANSI颜色+百分比） | approach: 1. node 80-PROJECTS/task-orchestrator/bin/chain-visualizer.mjs test

- [20260415] seed [brainstorm] [score:3x2=6] [f:2] [angle:project-fusion] [focus:task-orchestrator] task-orchestrator+multi-agent-hub辩论框架融合——用chain结构化多agent辩论流程 | benefit: 将multi-agent-hub的自适应温度辩论能力接入task-orchestrator的chain执行框架 | reason: 已知资源：multi-agent-hub/index.js已有CognitiveAnnealing+辩论框架，task-orchestrator/src/executor.mjs已有chain执行 | 缺失环节：两者未打通 | ←延伸自：20260414 task-orchestrator+opencli fusion | 连接方式：新增multi-agent-hub-adapter调用runAnnealing()，输出辩论结果作为chain节点 | approach: 1. mkdir 80-PROJECTS/task-orchestrator/src/adapters/multi-agent-hub 2. Write 80-PROJECTS/task-orchestrator/src/adapters/multi-agent-hub/debate-adapter.mjs封装multi-agent-hub的index.js 3. Edit executor.mjs注册新adapter 4. 测试：task-orchestrator编排一个辩论chain验证结果

- [20260415] seed [brainstorm] [score:4x3=12] [f:3] [angle:quality] [focus:task-orchestrator] task-orchestrator添加chain定义验证器——执行前检查chain schema合法性 | benefit: 防止非法chain定义导致运行时崩溃，减少调试时间 | reason: 已知资源：src/types.mjs已有ChainNode接口定义，src/executor.mjs有executeChain() | 缺失环节：executor无提前验证chain合法性，非法定义直接抛异常 | ←延伸自：20260413 adapter加权选择+exec-history | 连接方式：新增chain-validator.mjs，executor执行前调用validateChain() | approach: 1. node 80-PROJECTS/task-orchestrator/bin/chain-validator.mjs test | shipped:20260415
