# Idea Pool

---


- [20260407] seed [brainstorm] [score:5x2] [f:2] [angle:feature] [focus:wikipedia]
  description: adaptive-bitrate.py：多编码通道 + 按场景复杂度自动分配码率，质量敏感场景（公式推导/矩阵）用更优 crf，静态场景放宽 crf
  | benefit: 复杂公式场景细节更清晰，整体文件体积不增加
  | reason: 已知资源：make_video.py 第66-67行 libx264 硬编码 CRF=23，无 preset 参数；draw_scene.py SCENE_DRAWERS 已按场景类型分类（formula/graph/cover 等）。缺失环节：所有场景用同一码率，公式等复杂场景质量不足，静态封面浪费码率。连接方式：在 make_video.py 片段编码循环前，根据 scene key 类型查询 SCENE_DRAWERS，推断画面复杂度，动态设置 crf/preset
  | approach: 阶段一：1. 读 make_video.py 片段编码循环（第121-138行）；2. 定义 SCENE_COMPLEXITY = {'formula':(18,'slow'),'graph':(20,'medium'),'cover':(23,'fast')} 映射；3. 在片段编码 cmd 构造前，根据 img_path 文件名推断 scene key，查询映射表；4. 用 crf/preset 参数替换硬编码值 | shipped:20260407
  阶段二：5. 添加 --bitrate-profile low/medium/high 参数覆盖默认映射


- [20260407] seed [brainstorm] [score:5x3] [f:3] [angle:quality] [focus:wikipedia] | shipped:20260407
  description: make_video.py 硬字幕烧录：用 ffmpeg subtitles filter 将文字内容直接烧入视频，不用图形覆盖层
  | benefit: 字幕永久内嵌，播放时不依赖播放器支持，不丢字幕
  | reason: 已知资源：make_video.py 第198-210行 concat+混流逻辑已知；scripts/ 下无字幕工具。缺失环节：目前所有画面是静态图，字幕通过播放器渲染；播放器不兼容时丢字幕。连接方式：在最终视频段写入后，用 ffmpeg -vf subtitles 将字幕 ASS 文件烧入
  | approach: 1. 修改 make_video.py，在 concat 视频段后、最终混流前，添加字幕烧录步骤；2. 读取 article_dir 下的 NN-标题.ass 字幕文件；3. ffmpeg -vf subtitles=filename 将字幕硬编码进视频流；4. 同时保留原有音轨；5. 写 test：跑一次完整流程，验证输出 MP4 包含内嵌字幕 


- [20260407] seed [brainstorm] [score:5x3] [f:3] [angle:quality] [focus:wikipedia] | shipped:20260407
  description: draw_scene.py 配图升级：所有 plt.savefig 加 dpi=200（现有150）+ facecolor='white'，消除 matplotlib 抗锯齿毛边
  | benefit: 配图更锐利，专业感提升，学术场合可直接使用
  | reason: 已知资源：draw_scene.py 第65行 savefig dpi=150，plt.style.use('default') 第15行；现有图偏糊，边缘有锯齿感。缺失环节：dpi 150 对 1920×1080 视频来说偏小，matplotlib 默认抗锯齿未开启。连接方式：修改所有 plt.savefig 调用，将 dpi=150 升级到 dpi=200，添加 aa 级设置
  | approach: 1. 搜索 draw_scene.py 所有 plt.savefig 调用（共约 817 行需检查）；2. 统一替换 dpi=150→dpi=200；3. matplotlib.rcParams 添加 'axes.antialiased': True, 'lines.antialiased': True；4. 验证：对比升级前后 fig 文件大小和清晰度；5. 如效果不足，改用 dpi=300 封面 + dpi=200 配图 


- [20260407] seed [brainstorm] [score:4x4] [f:4] [angle:quality] [focus:wikipedia]
  description: generate_speech.py --voice 参数传递给所有文件：命令行指定 voice 时，自动判断中英文 speech.txt 并合理选择
  | benefit: 批量处理时不用逐个改文件名指定 voice，一行命令完成所有语音生成
  | reason: 已知资源：generate_speech.py 第122行已有 --voice 参数，第130行根据 -en 判断英文；缺失环节：目前 --voice 参数对中文文件无效（被硬编码 voice 覆盖），批量处理时指定 --voice 无法对英文文件生效。连接方式：修改 main() 的 batch 循环，让 --voice 仅在未指定时回退到默认值，已知英文文件始终用 en-US-AriaNeural
  | approach: 1. 修改 generate_speech.py batch 循环分支（第141-145行）；2. 当 args.voice 为默认值时，根据 is_english() 判断 voice；3. 非默认 --voice 参数直接透传给 generate_speech()；4. 测试：python generate_speech.py --voice en-US-AriaNeural 对中英文混合目录执行，验证中文用指定 voice | shipped:20260407


- [20260407] seed [brainstorm] [score:5x4] [f:4] [angle:infra] [focus:wikipedia] | shipped:20260407
  description: make_video.py --bitrate 参数：新增 --bitrate 覆盖默认码率设置，支持 1M/2M/5M 等预设
  | benefit: 按发布平台需要调整码率，YouTube 用 5M，文件大小敏感场景用 1M
  | reason: 已知资源：make_video.py 第61-75行 ffmpeg 编码参数硬编码；现有视频固定 192k audio bitrate。缺失环节：没有视频码率控制，输出的视频不适合不同平台。连接方式：在 main() 添加 --bitrate 参数，解析后注入到 ffmpeg cmd 的 -b:v 值
  | approach: 1. 在 make_video.py main() 的 argparse 添加 --bitrate 参数（如 '1M'/'2M'/'5M'/'10M'）；2. 新增函数 parse_bitrate() 将字符串转为 ffmpeg -b:v 参数值；3. 在 ffmpeg cmd 列表构建时注入 -b:v 参数；4. 测试：python make_video.py --bitrate 5M 处理一个 MP3，验证输出码率 


- [20260407] seed [brainstorm] [score:4x4] [f:4] [angle:feature] [focus:wikipedia]
  description: make_video.py 过渡帧生成：相邻场景之间插入 0.5s fade-in/out 过渡帧，避免画面跳变突兀
  | benefit: 场景切换更平滑，专业感提升
  | reason: 已知资源：make_video.py 第112-138行片段编码循环，每段固定 1fps；现有视频场景切换是硬切。缺失环节：没有帧间过渡，相邻场景跳变时视觉突兀。连接方式：在片段编码完成后、concat 前，对每个片段首尾各加 0.5 秒 fade 过渡
  | approach: 1. 在 make_video.py 的 make_video_multi() 片段编码后、concat 前（第140行前后），添加 fade 过渡处理；2. 用 ffmpeg -vf fade 分别为首尾片段加 fade-in/fade-out；3. 过渡时长可配置（默认 0.5s）；4. 添加 --transition 参数控制过渡时长；5. 验证：对比有/无过渡的视频，视觉体验差异 | shipped:20260407


- [20260407] seed [brainstorm] [score:4x5] [f:5] [angle:quality] [focus:wikipedia] shipped:20260407
  description: make_video.py + draw_scene.py 默认 dpi 从 150 改为 200（已知可行的小改进） | shipped:20260407
  | benefit: 配图清晰度提升约 30%，零成本
  | reason: 已知资源：draw_scene.py 第65行 dpi=150；make_video.py 静态图编码无 dpi 设置。缺失环节：当前 dpi 偏小。连接方式：单行 Edit，150→200
  | approach: 1. Edit: draw_scene.py 第65行 dpi=150 改为 dpi=200；2. 立即运行 make_video.py 处理一篇论文验证无副作用 


- [20260407] seed [brainstorm] [score:4x3] [f:3] [angle:quality] [focus:wikipedia] | shipped:20260407
  description: shared/video-quality-check.mjs：用 ffprobe 检测输出 MP4 的 video/audio bitrate、分辨率、时长，写入 JSON 报告
  | benefit: 每次生成视频后自动检查质量指标是否符合预期，发现问题及时告警
  | reason: 已知资源：shared/wiki-indexer.mjs 已实现扫描和 JSON 输出；ffprobe 是 imageio-ffmpeg 自带工具。缺失环节：目前视频质量靠人工检查，无自动化验证。连接方式：在 package_videos.py 完成后运行 ffprobe 检查，写入 JSON，指标异常输出 WARNING
  | approach: 1. 创建 shared/video-quality-check.mjs；2. 用 ffprobe -v quiet -print_format json -show_format -show_streams 读取 MP4 元数据；3. 解析 json 输出，提取 width/height/video_bitrate/audio_bitrate/duration；4. 定义质量阈值：min_width=1920, min_bitrate=500k, max_bitrate=10M；5. 在 package_videos.py 完成后调用该检查脚本；6. 异常时输出 [WARN] 并附具体指标 


- [20260407] seed [brainstorm] [score:4x2] [f:2] [angle:feature] [focus:wikipedia]
  description: 自动生成英文专业版 speech-en.txt：MiniMax API 翻译 + 术语替换，写入 -speech-en.txt
  | benefit: 只需写中文版文案，英文版自动生成，无需手动翻译和维护两份文案
  | reason: 已知资源：generate_speech.py 已支持 en-US-AriaNeural 英文语音；MINIMAX_API 环境变量已配置；现有中文字幕文案。缺失环节：没有翻译工具，需要手动维护英文文案。连接方式：在 video/ 下新增 translate_script.py，读取中文 speech.txt，调用 MiniMax API 翻译，按 generate_speech.py 的 MATH_REPLACEMENTS 规则替换术语，结果写入同名 -speech-en.txt
  | approach: 1. 创建 video/translate_script.py；2. 读取中文 *-阅读文案-speech.txt；3. 调用 MiniMax Chat API 翻译为英文；4. 替换术语（Yang-Baxter→杨-巴克斯特，Burau-Lyapunov→Burau-Lyapunov 等）；5. 写入 *-阅读文案-speech-en.txt；6. 支持 --all 批量处理 | shipped:20260407


- [20260407] seed [brainstorm] [score:6x2] [f:2] [angle:fusion] [focus:wikipedia] | shipped:20260407
  description: Wikipedia 知识库作为 task-orchestrator 的 RAG 上下文：articles 条目自动注册为可查询知识源
  | benefit: task-orchestrator 执行任务时可引用 wikipedia 论文知识点作为上下文，决策质量更高
  | reason: 已知资源：task-orchestrator 已支持 CLI registry 和 browser automation；articles/ 下有知识点条目和 arXiv 论文笔记。缺失环节：task-orchestrator 无法访问 wikipedia 知识库作为 RAG 上下文。连接方式：在 task-orchestrator 中创建 adapters/wikipedia-loader.ts，读取 index.json 提供 search/retrieve 接口
  | approach: 1. 在 task-orchestrator 项目创建 adapters/wikipedia-loader.ts；2. 实现 ArticleLoader 类，提供 search(query) 和 retrieve(title) 方法；3. 从 wikipedia/index.json 读取条目索引；4. 在 task-orchestrator 的 pick-next-project 中可选加载 wikipedia 上下文 


- [20260407] seed [brainstorm] [score:9x3] [f:3] [angle:quality] [focus:wikipedia] shipped:20260407
  description: draw_scene.py 场景覆盖率校验：make_video 前检查所有 [画面：] 场景是否都有配图函数
  | benefit: 防止配图数量与场景数量不匹配，视频合成时才发现缺图导致白帧
  | reason: 已知资源：draw_scene.py 的 SCENE_DRAWERS 字典和 scene_to_key() 匹配逻辑；scene-*.png 图片已存在。缺失环节：目前 scene_to_key 匹配失败时只 SKIP 不告警；没有提前校验覆盖率。连接方式：在 generate_scenes_for_script() 开头添加覆盖率检查，未覆盖场景数 > 0 时输出 WARN 并列出缺失 key
  | approach: 1. 修改 draw_scene.py 的 generate_scenes_for_script()，解析脚本获取所有场景描述；2. 对每个场景调用 scene_to_key()，若返回 None 或 SCENE_DRAWERS 无对应函数，计入缺失列表；3. 缺失数 > 0 时 print WARNING 并列出场景描述；4. 添加 --strict 参数，有缺失时 exit(1)；5. 在 make_video.py 调用 draw_scene 前先运行校验 | shipped:20260407


- [20260407] seed [brainstorm] [score:8x4] [f:4] [angle:docs] [focus:wikipedia] shipped:20260407
  description: wiki.mjs create --type video-script 命令：自动生成带 frontmatter 和 [画面：] 占位符的视频文案模板
  | benefit: 新视频文案只需填标题和 frontmatter，模板自动生成，不用每次复制粘贴
  | reason: 已知资源：wiki.mjs create 命令已支持 --template 参数；CLAUDE.md 已有 frontmatter 结构文档。缺失环节：create 命令没有 video-script 模板。连接方式：在 wiki.mjs create 添加 --type video-script 参数，生成标准 frontmatter 模板和章节框架
  | approach: 1. 修改 wiki.mjs create 命令，支持 --type video-script；2. 生成标准 frontmatter（title/duration/style/target_audience）；3. 添加 ## 开场 / ## 展开 / ## 总结章节框架和 [画面：] 占位符；4. 输出文件路径并告知下一步 | shipped:20260407


- [20260407] seed [brainstorm] [score:10x4] [f:4] [angle:infra] [focus:wikipedia] shipped:20260407
  description: package_videos.py --all 批量打包：一个命令把 articles/ 下所有有 MP4 的目录全部打包
  | benefit: 一次命令完成所有视频的打包，不用逐个论文运行脚本
  | reason: 已知资源：package_videos.py 已实现单论文打包逻辑（dist/ 和 dist-en/）；wiki.mjs sync 已实现目录扫描。缺失环节：package_videos.py 目前没有批量模式。连接方式：添加 --all 参数，扫描 articles/ 下所有含 .mp4 的子目录，批量执行打包
  | approach: 1. package_videos.py 添加 --all 参数；2. 扫描 articles/ 下所有含 .mp4 文件的子目录；3. 对每个子目录执行现有打包逻辑；4. 输出汇总报告：成功数/失败数；5. 添加 --dry-run 先预览不执行 | shipped:20260407


- [20260407] seed [brainstorm] [score:9x3] [f:3] [angle:feature] [focus:wikipedia] shipped:20260407
  description: wiki.mjs obsidian --fuzzy 命令：模糊搜索打开 Obsidian 条目，不知道确切标题也能找到
  | benefit: 不知道确切标题时，模糊搜索也能打开 obsidian 条目，不用猜文件路径
  | reason: 已知资源：wiki.mjs obsidian 命令已封装 obsidian CLI；wiki.mjs search 支持模糊搜索；缺失环节：obsidian edit 只支持精确标题匹配。连接方式：wiki.mjs edit 支持 --fuzzy 参数，模糊匹配时列出候选让用户选择编号
  | approach: 1. 修改 wiki.mjs edit 命令，支持 --fuzzy 参数；2. 调用 wiki.mjs search 模糊匹配，返回前 5 个候选；3. 如果候选 > 1，输出编号列表让用户选；4. 用户选好后调用 obsidian edit 打开对应条目；5. 添加 --exact 参数强制精确匹配（默认行为） | shipped:20260407


- [20260407] seed [brainstorm] [score:4x4] [f:4] [angle:ws-level] [focus:wikipedia]
  description: shared/wiki-indexer.mjs：扫描 workspace 下所有项目的 README.md 建立统一搜索索引，支持 wiki.mjs search --workspace
  | benefit: 在 wiki.mjs search 里跨所有项目搜索，一次找到所有相关项目的笔记和文档
  | reason: 已知资源：wiki.mjs search 支持模糊搜索和 JSON 输出；workspace 下有多个项目各自有 README.md。缺失环节：wiki.mjs search 只搜 articles/，不搜 80-PROJECTS。连接方式：新增 shared/wiki-indexer.mjs 扫描 workspace 下所有 README.md 并建立索引，wiki.mjs search --workspace 调用该索引
  | approach: 1. 创建 shared/wiki-indexer.mjs；2. 扫描 workspace 下所有 */README.md；3. 提取标题和第一段描述建立 JSON 索引；4. wiki.mjs search 添加 --workspace 参数，从共享索引搜索；5. 添加 --rebuild 强制重建索引 | shipped:20260407


- [20260407] seed [brainstorm] [score:6x3] [f:3] [angle:commercializable] [focus:wikipedia]
  description: Wikipedia 论文视频知识付费频道：把视频打包成付费订阅产品，提供专业英文版 + 科普中文版双语合集
  | benefit: 目标用户：科研人员、科技爱好者；变现路径：知识付费平台（知乎/少数派）；差异化：每期视频有对应原始论文和知识点笔记，可溯源
  | reason: 已知资源：wikipedia 已有完整视频生产流水线（speech→配图→视频→打包）；双版本（科普+专业）已跑通。缺失环节：没有付费渠道集成、没有视频托管、没有定期更新机制。连接方式：集成到公开的笔记/视频平台（YouTube/知乎），用 wiki.mjs batch-export 批量导出视频到指定目录
  | approach: 1. 调研知乎/少数派/YouTube 视频上传 API 或手动上传流程；2. 设计视频封面模板（区分科普版/专业版）；3. 制定更新频率（每周1-2篇）和订阅者通知机制；4. wiki.mjs 添加 batch-export 命令，导出 dist/ 视频到上传目录；5. 写 README 说明如何运营和变现 | shipped:20260407


- [20260407] seed [brainstorm] [score:6x2] [f:2] [angle:ws-level] | shipped:20260407
  description: shared/check-deps.mjs：扫描 workspace 下所有项目的 package.json，建立依赖健康度报告
  | benefit: 一次检查所有项目的依赖状态（过期/缺失/版本冲突），发现潜在安全风险
  | reason: 已知资源：workspace 下有 80-PROJECTS/ 和 shared/ 目录，package.json 格式已知。缺失环节：目前无统一依赖检查工具，各项目独立管理。连接方式：在 shared/ 下创建 check-deps.mjs，扫描所有 package.json，用 npm view --json 检测最新版本
  | approach: 阶段一：1. 创建 shared/check-deps.mjs；2. 扫描 80-PROJECTS/*/package.json 和 workspace root；3. 对每个包用 npm view --json 获取 latestVersion；4. 对比 package.json 中的 version，输出报告 
  阶段二：5. 添加 --fix 参数自动更新 minor/patch 版本；6. 添加 --audit 安全扫描


- [20260407] seed [brainstorm] [score:6x4] [f:4] [angle:feature] [focus:wikipedia] shipped:20260407 | shipped:20260407
  description: check_script.py --glossary 参数：输出术语表，列出 speech.txt 中的所有专业术语及其解释
  | benefit: 质量门禁时自动生成术语表，方便人工核对术语翻译是否准确
  | reason: 已知资源：video/check_script.py 已实现禁用词和术语检查；TERMS 字典已知。缺失环节：目前只检查禁用词，不输出术语表。连接方式：在 check_script.py 添加 --glossary 参数，扫描 speech.txt 匹配 TERMS 字典
  | approach: 1. Edit: video/check_script.py main() 添加 --glossary 参数；2. 读取 speech.txt 内容；3. 用 TERMS 字典匹配所有出现的术语；4. 去重后按行输出"术语 → 解释"；5. 无匹配时输出"无术语" 


- [20260407] seed [brainstorm] [score:6x4] [f:4] [angle:feature] [focus:wikipedia] | shipped:20260407
  description: wiki.mjs recent 命令：列出最近编辑的 Obsidian 条目（按修改时间排序）
  | benefit: 快速查看最近更新的知识点，不用在 Obsidian 手动翻找
  | reason: 已知资源：wiki.mjs obsidian 命令已封装 obsidian CLI；wiki.mjs sync 已读 index.json。缺失环节：无 --recent 参数，无法列出最近条目。连接方式：在 wiki.mjs 添加 --recent 参数，读取 Obsidian vault 下所有 .md 文件的 mtime 排序
  | approach: 1. 修改 wiki.mjs obsidian 命令，支持 --recent 参数；2. 用 obsidian vault list 或直接扫描 vault 目录；3. 按 mtime 倒序取前 20 条；4. 输出 序号 | 标题 | 修改时间 


- [20260407] seed [brainstorm] [score:6x3] [f:3] [angle:ws-level]
  description: shared/video-editors.mjs：FFmpeg 视频编辑封装，支持剪切/拼接/添加字幕/转码
  | benefit: 对 video-quality-check.mjs 的补充，实现常见视频编辑操作无需记忆 ffmpeg 语法
  | reason: 已知资源：shared/video-quality-check.mjs 已实现质量检查；ffmpeg 在 imageio-ffmpeg 中。缺失环节：只有检查工具，没有编辑工具。连接方式：在 shared/ 下创建 video-editors.mjs，封装 cut/concat/subtitle/transcode 四个子命令
  | approach: 1. 创建 shared/video-editors.mjs；2. 实现 cut: ffmpeg -ss start -to end；3. 实现 concat: ffmpeg concat demuxer；4. 实现 subtitle burn: ffmpeg -vf subtitles；5. 实现 transcode: 按 --bitrate重新编码 | shipped:20260407


- [20260407] seed [brainstorm] [score:6x4] [f:4] [angle:feature] [focus:wikipedia] | shipped:20260407
  description: wiki.mjs batch-export 命令：批量导出 articles/ 下指定日期范围的视频到目标目录
  | benefit: 一次导出多个视频到上传目录，不用逐个手动复制
  | reason: 已知资源：wiki.mjs 已封装 wiki.mjs CLI；articles/ 下视频已按 NN-标题.mp4 命名。缺失环节：无批量导出命令。连接方式：在 wiki.mjs 添加 batch-export 命令，扫描 articles/ 下所有 .mp4，按日期或标题过滤
  | approach: 1. 修改 wiki.mjs，添加 batch-export 命令；2. 解析 --from/--to 日期范围参数；3. 扫描 articles/**/*.mp4；4. 按日期或 glob 过滤；5. 用 fs.copyFileSync 复制到 --output 目录；6. 输出汇总：成功数/失败数 


- [20260407] seed [brainstorm] [score:10x2] [f:2] [angle:fusion] | shipped:20260407
  description: task-orchestrator → wikipedia-loader adapter：Wikipedia 知识库作为 RAG 上下文注入任务规划
  | benefit: task-orchestrator 执行任务时可引用 wikipedia 论文知识点作为上下文，决策质量更高
  | reason: 已知资源：task-orchestrator 已支持 CLI registry 和 browser automation；wikipedia/articles/ 下有知识点条目。缺失环节：task-orchestrator 无法访问 wikipedia 知识库作为 RAG 上下文。连接方式：在 task-orchestrator 项目创建 adapters/wikipedia-loader.ts，读取 index.json 提供 search/retrieve 接口
  | approach: 阶段一（architecture design）：1. 在 task-orchestrator 项目创建 adapters/ 目录；2. 设计 ArticleLoader 类，提供 search(query) 和 retrieve(title) 方法；3. 从 wikipedia/index.json 读取条目索引 
  阶段二（实现）：4. 用 readFileSync + JSON.parse 读取 wikipedia/index.json；5. 模糊匹配标题；6. 在 pick-next-project 中可选加载 wikipedia 上下文


- [20260407] seed [brainstorm] [score:10x2] [f:2] [angle:fusion] | shipped:20260407
  description: task-orchestrator → opencli adapter：opencli browser automation 集成到 task-orchestrator（已有实现）
  | benefit: task-orchestrator 可以用 opencli 控制浏览器执行复杂网页操作
  | reason: 已知资源：task-orchestrator 已实现 pick-next-project 和 CLI registry adapter；opencli 已实现 browser automation。缺失环节：task-orchestrator 无法调用 opencli 执行浏览器操作。连接方式：在 task-orchestrator 中创建 adapters/opencli-adapter.ts，用 child_process.exec 封装 opencli 命令
  | approach: 阶段一（architecture design）：1. 在 task-orchestrator 创建 adapters/opencli-adapter.ts；2. 设计 BrowserAdapter 类，提供 navigate(url)/click(selector)/type(text) 方法 
  阶段二（实现）：3. 用 execSync 封装 opencli 命令行；4. 实现命令链执行；5. 在 task-orchestrator 的 execute-step 中调用 BrowserAdapter


- [20260407] seed [brainstorm] [score:5x5] [f:5] [angle:feature] [focus:task-orchestrator]
  description: planner.ts 添加 wikipedia 关键词路由：说"查 wiki 论文"自动触发 WikipediaLoaderAdapter search
  | benefit: 用户只需说"查 Wikipedia XXX"，task-orchestrator 自动搜索并展示 wikipedia 知识库条目
  | reason: 已知资源：planner.ts BUILT_IN_RULES 第32-48行包含 screenshot/open/obs 等关键词路由；WikipediaLoaderAdapter 已注册，adapterId='wikipedia'。缺失环节：planner 不知道 wikipedia 关键词，没有路由规则。连接方式：在 BUILT_IN_RULES 添加一条 {keywords:['wiki','wikipedia','维基','论文'], adapterId:'wikipedia', adapterType:'wikipedia', command:'search', args:['QUERY']}
  | approach: 1. Edit planner.ts line 48后（screenshot规则块之后）插入新规则对象；2. keywords:['wiki','wikipedia','维基']；3. adapterId:'wikipedia', adapterType:'wikipedia', command:'search' 
 | shipped:20260407

- [20260407] seed [brainstorm] [score:4x4] [f:4] [angle:infra] [focus:task-orchestrator]
  description: executor.ts --dry-run 参数：不真正执行 adapter，只打印将调用的 adapterId/command/args
  | benefit: 调试任务链时无需真正执行耗时的 browser/AI 操作，秒级验证 planning 是否正确
  | reason: 已知资源：executor.ts 第115行 execute(steps, ctx?) 签名已知；adapter 调用发生在第115-150行循环。缺失环节：没有 dry-run 模式，每次修改 planner 规则后必须跑完整流程才能验证。连接方式：在 execute() 入口检查 steps[0].dryRun || ctx.dryRun 标志，若为真则跳过 adapter 调用，只 console.log plan
  | approach: 1. Read executor.ts:115 查看 execute() 签名；2. 在 Step interface 添加 dryRun?:boolean；3. execute() 开头 if(steps.some(s=>s.dryRun)) { console.log('[DRY]', JSON.stringify(steps)); return ok([]) } | shipped:20260407


- [20260407] seed [brainstorm] [score:5x3] [f:3] [angle:quality] [focus:task-orchestrator] | shipped:20260407
  description: executor 每步记录耗时写入 Result.metadata（startTime/endTime/durationMs），并在 UI 流输出perf行
  | benefit: 任务执行后立即知道每步耗时，定位慢瓶颈步骤，优化任务链
  | reason: 已知资源：executor.ts:115 execute() 方法，第150-200行有循环执行 adapter；Result 类型来自 shared-types。缺失环节：Result 只有 success/output/logs，没有执行耗时字段，无法定位慢步骤。连接方式：在 executor 的步骤循环前后记录 Date.now()，结果写入 result.metadata = {durationMs}；UI stream 输出 [PERF adapterId: Xms]
  | approach: 阶段一：1. 在 executor.ts:115 execute() 循环内，adapter 调用前后记录 start=Date.now()；2. result.metadata = {durationMs: Date.now()-start}；3. stream 输出 [PERF ${step.adapterId}: ${durationMs}ms] 


- [20260407] seed [brainstorm] [score:4x2] [f:2] [angle:fusion] [focus:task-orchestrator]
  description: shared-types Result 添加可选 metadata 字段：{durationMs?, retries?, adapterId?}，所有 adapter 执行结果自动附带执行信息
  | benefit: 所有 adapter 的执行元数据统一格式，方便 audit/replay/performance 分析，跨项目复用
  | reason: 已知资源：shared-types/index.ts:57 Result interface；executor.ts 已为每个 adapter 调用计时。缺失环节：Result 接口没有 metadata 字段，各 adapter 返回值格式不统一，无法做统一性能分析。连接方式：在 Result 接口添加 metadata?: {durationMs?:number, retries?:number, adapterId?:string}，executor.ts 在包装 adapter 结果时自动写入 metadata | shipped:20260407
  | approach: 阶段一（design）：1. Read shared-types/index.ts:57 Result；2. 确认 metadata 字段设计（与 executor.ts:120 Duration 测量兼容）；3. 确认对所有 adapter 的影响（是否有反模式风险） 
  阶段二（实现）：4. Edit shared-types/index.ts 在 Result 添加 metadata 字段；5. Edit executor.ts 在结果包装处自动写入 metadata.durationMs


- [20260407] seed [brainstorm] [score:5x1] [f:1] [angle:feature] [focus:task-orchestrator] | shipped:20260407
  description: executor 自动重试 + 指数退避：Step 有 maxRetries 时，失败自动指数退避重试（2^attempt × baseDelayMs），重试过程输出 [RETRY attempt N] 日志
  | benefit: 网络抖动、临时服务不可用等瞬时失败时任务自动恢复，无需人工干预，提升任务成功率
  | reason: 已知资源：executor.ts:28 RetryStrategy.action='retry' 和 Step.maxRetries 字段已存在；planner.ts 支持 YAML 规则配置。缺失环节：当前 retry 是同步立即重试，没有退避延迟；指数退避能显著提升最终成功率。连接方式：在 executor.ts 的步骤执行失败处理逻辑中，if(action==='retry') 用 setTimeout 延迟重试，每次延迟 = baseDelay * 2^attempt
  | approach: 阶段一（architecture）：1. 在 executor.ts 中找到 retry 逻辑位置（grep 'action.*retry'）；2. 设计 RetryContext {attempt, maxRetries, baseDelayMs}；3. 决定指数退避是否影响全局任务超时 
  阶段二（实现）：4. 实现 _retryWithBackoff(ctx, attempt) 函数，用 setTimeout 包装；5. 输出 [RETRY step.adapterId attempt/MaxRetries after Xms]；6. 添加单元测试：mock adapter 返回 error，验证退避序列
  阶段三（验证）：7. 用 task-orchestrator CLI 跑一个会失败两次后成功的 adapter，验证退避行为


- [20260407] seed [brainstorm] [score:4x4] [f:4] [angle:ws-level]
  description: shared/run-seed.mjs：扫描 ideas.md pool，运行最高分未完成 seed，像 CLI pipeline 一样串联执行
  | benefit: 每次 session 开始只需运行一个命令，自动完成所有 seed 实现，不用手动挑选和组织
  | reason: 已知资源：shared/ 下已有 check-deps/video-quality-check/video-editors/wiki-indexer 等工具；ideas.md 有 seed stage 标记。缺失环节：没有统一的 seed runner，每次需要手动挑 seed、自己执行、自己标记 shipped。连接方式：在 shared/ 创建 run-seed.mjs，读取 ideas.md 找未 shipped seed，执行后写 shipped 标记 | shipped:20260407
  | approach: 1. 创建 shared/run-seed.mjs；2. 用 grep 解析 ideas.md 找所有未 shipped seed；3. 按 score 降序取最高分；4. 执行 seed 的 approach 第一步（具体命令）；5. 成功后 sed -i 写 shipped:YYYYMMDD；6. 输出汇总报告 


- [20260407] seed [brainstorm] [score:5x3] [f:3] [angle:commercializable] [focus:task-orchestrator] | shipped:20260407
  description: task-orchestrator → wiki-indexer → Wikipedia 知识库自动研究 pipeline：输入主题，自动从 wikipedia 知识库抓取相关论文笔记作为上下文，生成研究报告
  | benefit: 目标用户：研究人员、科技内容创作者；变现路径：研究报告订阅、API 调用计费；差异化：每份报告有原始论文引用，可溯源
  | reason: 已知资源：task-orchestrator 有 CLI registry 和 executor；shared/wiki-indexer.mjs 已扫描 workspace 下所有 README；wikipedia loader adapter 可 search/retrieve 条目。缺失环节：没有自动研究 pipeline，主题到报告之间需要大量人工协调。连接方式：task-orchestrator 新增 'research' adapterType，输入查询字符串，调用 wiki-indexer search + wikipedia retrieve，结果拼成报告
  | approach: 阶段一（design）：1. 设计 research pipeline：query → wiki search → top-K retrieve → summarize → report；2. 确定 wikipedia 条目如何作为 LLM 上下文注入 
  阶段二（实现）：3. 在 task-orchestrator 新增 research.ts adapter；4. wiki-indexer.mjs 添加 --query 参数返回相关条目列表；5. WikipediaLoaderAdapter.execute 支持 'summarize' action；6. 写 README 说明如何运营和变现


- [20260407] seed [brainstorm] [score:5x2] [f:2] [angle:fusion|project-fusion] [focus:task-orchestrator] | shipped:20260407
  description: task-orchestrator shell adapter：把 task-orchestrator 本身变成一个可用自然语言驱动的 agent，自动发现和注册 PATH 上的 CLI 工具
  | benefit: 用户说"用 tree 显示目录结构"，task-orchestrator 自动找到 tree 命令并执行；零配置，PATH 上有什么工具就能用什么
  | reason: 已知资源：shell.ts:13 shell adapter 可执行任意 shell 命令；registry-loader.ts:38 从 registry.json 提取 keywords。缺失环节：没有自动发现 PATH 上新 CLI 工具的机制；BUILT_IN_RULES 是手写静态的。连接方式：启动时扫描 PATH（which 命令），提取所有可执行文件作为 keywords；每个 keyword 对应 shell:<cmd> 步骤
  | approach: 阶段一（design）：1. 在 registry.ts load() 后扫描 PATH：which -a 列出所有可执行文件；2. 过滤掉内置命令（node/npm/git）；3. 为每个命令在内存 rules 中生成 KeywordRule 
  阶段二（实现）：4. 在 registry.ts discoverFromDirs() 后添加 scanPathCommands()；5. 提取命令名作为 keywords；6. commandBuilder 映射到 shell:<cmd>；7. 输出 [DISCOVERED N commands] 到 logs


- [20260407] seed [brainstorm] [score:4x5] [f:5] [angle:infra] description: run-seed.mjs --dry-run 参数：模拟执行不写 shipped 标记，验证 seed 能否正常运行 | benefit: 开发调试 seed 时不用真正执行，可预览脚本行为 | reason: 已知资源：run-seed.mjs 第17行已有 dryRun 检测，execSync 在第144行。缺失环节：目前 run-seed.mjs --dry-run 只打印不执行，但会走到 mark shipped 逻辑（第155-168行），应提前退出。连接方式：在 execSync try/catch 之后、mark shipped 之前，加 `if (dryRun) { console.log('[DRY] Done'); process.exit(0) }`
  | approach: 1. Edit run-seed.mjs 在第137行（execSync try/catch 之后）插入 if(dryRun){console.log('[DRY] seed validated');process.exit(0)} | shipped:20260407


- [20260407] seed [brainstorm] [score:6x4] [f:4] [angle:quality] description: shared-types Result.metadata 字段：executor 每步写入 startTime/endTime/durationMs，UI 流输出 [PERF] 行 | benefit: 任务执行后立即知道每步耗时，定位慢瓶颈 | reason: 已知资源：shared-types/index.ts:57 Result interface；executor.ts:115 execute() 循环。缺失环节：Result 只有 success/output/logs，无耗时字段。连接方式：在 Result 添加 metadata?:{durationMs?:number}，executor 在 adapter 调用前后记录 Date.now()
  | approach: 1. Edit shared-types/index.ts:57 Result interface 添加 metadata?:{durationMs?:number}；2. Edit executor.ts execute() 循环内 start=Date.now()，执行后 result.metadata={durationMs:Date.now()-start}；3. stream 输出 [PERF ${step.adapterId}: ${durationMs}ms] | shipped:20260407


- [20260407] seed [brainstorm] [score:9x3] [f:3] [angle:feature] description: task-orchestrator executor.ts 重试日志格式化：从 [RETRY] 改为 [RETRY step.adapterId attempt N/M] 更清晰 | benefit: 重试时一眼看出是哪个 step 在重试，调试更容易 | reason: 已知资源：executor.ts 第363行已有 [RETRY attempt ${attempt}/${maxRetries}] 格式。缺失环节：重试日志缺少 adapterId 标识，多个 step 重试时无法区分。连接方式：在 executor.ts:363 的 [RETRY] 字符串前加 step.adapterId
  | approach: 1. Edit executor.ts:363 将 '[RETRY attempt' 改为 '[RETRY ${step.adapterId} attempt'；2. 跑 task-orchestrator 验证格式正确 | shipped:20260407


- [20260407] seed [brainstorm] [score:8x2] [f:2] [angle:fusion|project-fusion] description: task-orchestrator shell adapter PATH 命令自动发现：启动时扫描 PATH 上可执行文件作为 keywords | benefit: 用户说"用 tree 显示目录"自动找到 tree 命令执行，零配置 | reason: 已知资源：shell.ts:13 shell adapter；registry-loader.ts:38 从 registry.json 提取 keywords；planner.ts BUILT_IN_RULES 静态配置。缺失环节：没有启动时 PATH 扫描，所有 keywords 需手写。连接方式：在 registry.ts load() 后调用 scanPathCommands()，用 which -a 列出所有可执行文件，过滤内置命令后追加到内存 rules
  | approach: 阶段一：1. Read task-orchestrator/src/registry.ts 查看 load() 位置；2. Read shell.ts 查看 commandBuilder 格式
  阶段二：3. 在 registry.ts load() 末尾添加 scanPathCommands()；4. 用 execSync('which -a') 扫描 PATH；5. 过滤 node/npm/git 等内置；6. 对每个命令生成内嵌 KeywordRule 映射到 shell:<cmd>；7. 输出 [DISCOVERED N commands] | shipped:20260407


- [20260407] seed [brainstorm] [score:5x1] [f:1] [angle:feature] description: task-orchestrator 自主任务分解：当用户给高层目标时，agent 自动拆解为可执行步骤链 | benefit: 用户说"帮我研究这个领域"，task-orchestrator 自动规划搜索→阅读→整理→报告的完整链路 | reason: 已知资源：planner.ts 有 BUILT_IN_RULES 和 YAML 规则加载；executor.ts execute() 循环；shell adapter 执行 shell 命令。缺失环节：没有任务分解能力，所有步骤必须用户显式给出。连接方式：设计 TaskDecomposer 类，接收高层目标，调用 LLM 分解为步骤数组，每个步骤含 adapterId/command/args，注入 executor 执行
  | approach: 阶段一(architecture)：1. Read planner.ts 理解 BUILT_IN_RULES 结构；2. 设计 TaskDecomposer 接口：decompose(goal:string) -> Step[]；3. 确定是否用 MiniMax API 做分解决策 | shipped:20260407
  阶段二(实现)：4. 创建 src/task-decomposer.ts 实现 TaskDecomposer；5. 接收自然语言 goal，调用 LLM 返回结构化步骤；6. 每个 Step 含 adapterId/command/args；7. 在 executor 入口增加 decompose 模式检测；8. 添加 --decompose 参数


- [20260407] seed [brainstorm] [score:7x4] [f:4] [angle:ws-level] description: shared/wiki-indexer.mjs --query 参数：传入搜索词返回相关条目列表（JSON 输出），被 task-orchestrator 等工具调用 | benefit: wiki-indexer 不只是建索引，还能被其他工具实时查询，不用加载全部数据 | reason: 已知资源：wiki-indexer.mjs 已扫描所有 README.md 建立 wiki-index.json；shared-types 约定 JSON 输出格式。缺失环节：wiki-indexer 只有 --rebuild，没有 --query 实时查询。连接方式：在 wiki-indexer.mjs 添加 --query 参数，从 wiki-index.json 模糊匹配标题/描述
  | approach: 1. Read shared/wiki-indexer.mjs 理解现有 --rebuild 逻辑；2. 添加 --query 参数分支；3. 用 fuzzy search 匹配 wiki-index.json 中的 title/description；4. JSON 输出 [{title,path,description}]；5. 添加 --limit 参数控制返回数量 | shipped:20260407


- [20260407] seed [brainstorm] [score:6x3] [f:3] [angle:ws-level] description: shared-types TaskResult 添加 reason 字段：记录 planner 为什么选择这个 adapter，帮助理解 agent 决策 | benefit: agent 执行日志可解释，调试时知道为什么选了这个 adapter 而不是另一个 | reason: 已知资源：shared-types/index.ts TaskResult interface；planner.ts 第48-80行 rule matching 逻辑。缺失环节：TaskResult 只有 adapterId 和 command，没有决策原因。连接方式：在 TaskResult 添加 reason?:string，planner 在 rule match 成功后写入匹配到的 rule key | shipped:20260407
  | approach: 1. Read shared-types/index.ts TaskResult；2. 添加 reason?:string 字段；3. Read planner.ts rule match 位置；4. 在 match 成功后 result.reason = matchedRule.key；5. 验证 executor 输出含 reason 字段


- [20260407] seed [brainstorm] [score:6x3] [f:3] [angle:commercializable] description: task-orchestrator 研究报告 pipeline 产品化：输入研究主题，wiki-indexer search + WikipediaLoaderAdapter retrieve + MiniMax API 生成报告，按主题打包出售 | benefit: 目标用户：研究人员/科技内容创作者；变现路径：研究报告订阅、API 调用计费；差异化：每份报告有原始论文引用可溯源 | reason: 已知资源：task-orchestrator 有 CLI registry 和 executor；shared/wiki-indexer.mjs 支持 --query；WikipediaLoaderAdapter 可 search/retrieve 条目。缺失环节：没有自动研究 pipeline，主题到报告之间需要大量人工协调。连接方式：task-orchestrator 新增 research adapterType，输入查询字符串，调用 wiki-indexer search + wikipedia retrieve，结果拼成报告
  | approach: 阶段一(design)：1. 设计 research pipeline：query → wiki-indexer search → top-K retrieve → LLM summarize → report.md；2. 确定 wikipedia 条目如何作为 LLM 上下文注入 | shipped:20260407
  阶段二(实现)：3. 在 task-orchestrator 新增 src/adapters/research.ts；4. wiki-indexer.mjs --query 返回相关条目 JSON；5. WikipediaLoaderAdapter.execute 支持 'summarize' action；6. 拼接摘要写 report.md；7. 写 README 说明如何运营和变现


- [20260407] seed [brainstorm] [score:4x5] [f:5] [angle:infra] [focus:task-orchestrator] description: task-orchestrator executor.ts --dry-run 参数：不执行 adapter，只打印将调用的 adapterId/command/args | benefit: 调试任务链时无需真正执行耗时的 browser/AI 操作，秒级验证 planning 是否正确 | reason: 已知资源：executor.ts:115 execute() 循环；adapter 调用在第115-150行。缺失环节：没有 dry-run 模式，每次改 planner 规则后必须跑完整流程。连接方式：在 execute() 入口检查 steps[0].dryRun || ctx.dryRun，若为真跳过 adapter 调用
  | approach: 1. Read executor.ts:115 查看 execute() 签名和 Step 接口；2. Edit executor.ts:115 execute() 开头加 if(steps.some(s=>s.dryRun)){console.log('[DRY]',JSON.stringify(steps));return ok([])} | shipped:20260407


- [20260407] seed [brainstorm] [score:6x4] [f:4] [angle:ws-level] description: shared-types Result.metadata 字段：executor 每步写入 durationMs，UI 流输出 [PERF adapterId: Xms] | benefit: 任务执行后立即知道每步耗时，定位慢瓶颈 | reason: 已知资源：shared-types/index.ts Result interface；executor.ts:115 execute() 循环。缺失环节：Result 只有 success/output/logs，无耗时字段。连接方式：在 Result 添加 metadata?:{durationMs?:number}，executor 循环内 start=Date.now() 后写入
  | approach: 1. Edit shared-types/index.ts Result interface 添加 metadata?:{durationMs?:number}；2. Edit executor.ts execute() 循环内 start=Date.now()，执行后 result.metadata={durationMs:Date.now()-start}；3. stream 输出 [PERF ${step.adapterId}: ${durationMs}ms] | shipped:20260407


- [20260407] seed [brainstorm] [score:5x3] [f:3] [angle:hookify] description: hookify 规则拦截 rm -rf 在 node_modules：在 .claude/ 下创建 hookify.prevent-node-modules-rf.local.md | benefit: 防止执行 rm -rf 时误删 node_modules，拦截危险命令 | reason: 已知资源：hookify 规则格式已知，.claude/ 目录存在。缺失环节：无此拦截规则。连接方式：创建 hookify.prevent-node-modules-rf.local.md，pattern 匹配 rm.*rf.*node_modules
  | approach: 1. Write D:/OpenClaw/workspace/.claude/hookify.prevent-node-modules-rf.local.md，内容：--- name: prevent-node-modules-rf enabled: true event: bash pattern:rm\s+-rf\s+.*node_modules --- Danger: rm -rf on node_modules detected | shipped:20260407


- [20260407] seed [brainstorm] [score:8x2] [f:2] [angle:fusion|project-fusion] [focus:task-orchestrator] description: task-orchestrator shell adapter PATH 命令自动发现：启动时扫描 PATH 上可执行文件作为 keywords | benefit: 用户说"用 tree 显示目录"自动找到 tree 命令执行，零配置 | reason: 已知资源：shell.ts:13 shell adapter；registry-loader.ts:38 从 registry.json 提取 keywords；planner.ts BUILT_IN_RULES。缺失环节：没有启动时 PATH 扫描，所有 keywords 需手写。连接方式：在 registry.ts load() 后调用 scanPathCommands()，用 which -a 列出所有可执行文件，过滤内置命令后追加到内存 rules
  | approach: 阶段一：1. Read task-orchestrator/src/registry.ts 查看 load() 位置；2. Read shell.ts 查看 commandBuilder 格式
  阶段二：3. 在 registry.ts load() 末尾添加 scanPathCommands()；4. 用 execSync('which -a') 扫描 PATH；5. 过滤 node/npm/git 等内置；6. 对每个命令生成内嵌 KeywordRule 映射到 shell:<cmd>；7. 输出 [DISCOVERED N commands] | shipped:20260407


- [20260407] seed [brainstorm] [score:5x1] [f:1] [angle:feature] [focus:task-orchestrator] description: task-orchestrator 自主任务分解：当用户给高层目标时，agent 自动拆解为可执行步骤链 | benefit: 用户说"帮我研究这个领域"，task-orchestrator 自动规划搜索→阅读→整理→报告的完整链路 | reason: 已知资源：planner.ts BUILT_IN_RULES 和 YAML 规则加载；executor.ts execute() 循环；shell adapter。缺失环节：没有任务分解能力，所有步骤必须用户显式给出。连接方式：设计 TaskDecomposer 类，接收高层目标，调用 MiniMax API 分解为步骤数组，注入 executor 执行
  | approach: 阶段一(architecture)：1. Read planner.ts 理解 BUILT_IN_RULES 结构；2. 设计 TaskDecomposer 接口：decompose(goal:string) -> Step[] | shipped:20260407
  阶段二(实现)：3. 创建 src/task-decomposer.ts 实现 TaskDecomposer；4. 接收自然语言 goal，调用 MiniMax API 返回结构化步骤；5. 每个 Step 含 adapterId/command/args；6. 在 executor 入口增加 decompose 模式检测；7. 添加 --decompose 参数


- [20260407] seed [brainstorm] [score:6x3] [f:3] [angle:quality] description: shared/video-quality-check.mjs 添加 JSON 输出 + --checklist 参数：输出质量指标摘要列表 | benefit: 视频质量检查结果可直接被其他脚本解析，方便 CI/CD 集成 | reason: 已知资源：shared/videoquality-check.mjs 已实现 ffprobe 元数据提取。缺失环节：只有控制台输出，没有 JSON 格式机器可读输出。连接方式：在 video quality-check.mjs 添加 --json 参数，输出 {width,height,bitrate,duration,status} 对象
  | approach: 1. Read shared/video-quality-check.mjs；2. 添加 --json 参数分支；3. ffprobe 元数据解析后输出 JSON 对象而非控制台格式；4. 添加 --checklist 参数输出 [{metric,value,pass}] 格式 | shipped:20260407


- [20260407] seed [brainstorm] [score:7x4] [f:4] [angle:ws-level] description: shared/wiki-indexer.mjs fuzzy 匹配改进：传入 term 名称部分匹配（如 wiki 也能找到 wikipedia），按相关性排序 | benefit: wiki-indexer 查询更鲁棒，模糊匹配能处理拼写错误和部分输入 | reason: 已知资源：wiki-indexer.mjs 已实现 --query 和 --fuzzy；fuzzyMatch() 在第67行。缺失环节：当前 fuzzy 匹配用字符重叠率，对英文词根效果差（如 wiki 匹配不到 wikipedia）。连接方式：改进 fuzzyMatch() 函数，对英文单词做前缀匹配，给前缀匹配更高的权重
  | approach: 1. Edit wiki-indexer.mjs fuzzyMatch() 函数；2. 检测 query 是否为连续英文字符，若是则检查 entry.title 是否以 query 开头或包含 query 作为完整单词；3. 前词边界匹配 *1.5，单词重叠保持原逻辑 | shipped:20260407


- [20260407] seed [brainstorm] [score:6x3] [f:3] [angle:commercializable] description: task-orchestrator → wiki-indexer 研究报告 pipeline：输入研究主题，wiki-indexer search + WikipediaLoader retrieve + MiniMax API 生成报告，按主题打包出售 | benefit: 目标用户：研究人员/科技内容创作者；变现路径：研究报告订阅/按份计费；差异化：每份报告有原始论文引用可溯源 | reason: 已知资源：task-orchestrator executor 已支持 CLI registry；shared/wiki-indexer.mjs 支持 --query JSON 输出；WikipediaLoaderAdapter 可 search/retrieve。缺失环节：没有自动研究 pipeline。连接方式：task-orchestrator 新增 research adapter，调用 wiki-indexer --query + WikipediaLoader retrieve，结果拼成 markdown 报告
  | approach: 阶段一(design)：1. 设计 pipeline：query → wiki-indexer --query --json → top-K retrieve → LLM summarize → report.md | shipped:20260407
  阶段二(实现)：2. 在 task-orchestrator/src/adapters/ 创建 research.ts adapter；3. 实现 ResearchPipeline.execute(searchQuery) → 调用 wiki-indexer.mjs --query JSON → 对每个结果调用 WikipediaLoader → 拼接内容 → 调用 MiniMax API summarize → 写 report.md；4. 写 README 说明如何运营和变现


- [20260407] seed [brainstorm] [score:6x2] [f:2] [angle:hookify] description: hookify 规则：run-seed 执行前检测 approach 是否为可执行命令，非 shell 命令则 abort | benefit: 阻止非可执行 approach 被执行，避免假 shipped | reason: 已知资源：run-seed.mjs 第105-129行已知晓 9 种 executable prefix；hookify 规则体系已建立(.claude/hookify.*.local.md)。缺失环节：当前 runner 对 "Edit wiki-indexer.mjs 理解..." 这种纯描述文本无法识别，会当作 shell 命令执行后 fail。连接方式：在 .claude/ 下建 hookify.run-seed-approach.local.md，event=bash，pattern 匹配 node.*run-seed.*step.*Edit|step.*Read|step.*Write，后缀带中文标点或句号
  | approach: 阶段一：写 hookify 规则；阶段二：测试 "node run-seed.mjs --dry-run" 验证规则生效 | killed:20260407 non-executable approach


- [20260407] seed [brainstorm] [score:9x3] [f:3] [angle:skill-file] description: brainstorming skill 增加 approach 可执行性子规则：f:4/f:5 的 approach 第1步必须是 `python ` / `node ` / `Edit ` / `Write ` 等命令前缀，禁止纯描述文本 | benefit: 从入口拦截低质量 approach，brainstorm 自身质量提升 | reason: 已知资源：brainstorming skill 已有 Seed Quality Gates §1-§12；D:/OpenClaw/workspace 已知晓 skill 文件位置。缺失环节：skill 中没有对 approach 可执行性的明确验证规则（现有规则只要求格式，不验证命令有效性）。连接方式：在 brainstorming skill 的 Gate 4 后追加 Gate 4b：approach 第1步必须匹配 /^(python |node |npx |Edit |Write |Read |Create |Bash |Grep |Glob )/
  | approach: 1. Read brainstorming skill 找到 Gate 4 位置；2. 在 Gate 4 段落后追加 Gate 4b approach 可执行性检查；3. 验证格式 | shipped:20260407


- [20260407] seed [brainstorm] [score:6x3] [f:3] [angle:infra] description: run-seed.mjs 添加 --validate-only flag：扫描 ideas.md 中所有 unshipped seed，对每个 seed 的 approach 第1步做可执行性验证，无效则自动标记 killed | benefit: 自动化清理 pool 中无效 seed，无需手动逐个审查 | reason: 已知资源：run-seed.mjs 已有 approach 解析逻辑(第95行)和 ship 标记逻辑(第158-171行)；已知晓 killed 标记格式。缺失环节：缺少批量验证模式，不能在写入 pool 前拦截非可执行 approach。连接方式：在 run-seed.mjs 添加 --validate-only 分支，解析所有 unshipped seed，对每个 approach 第1步检测是否匹配 executable prefix，不匹配则执行 sed -i 's/^  | approach: /  | approach: killed:20260407 non-executable /'
  | approach: 1. Edit run-seed.mjs 在第111行（args parsing）后添加 --validate-only 分支；2. 该分支扫描所有 unshipped seeds，检测 approach 第1步是否匹配 executable prefix；3. 无效 seeds 用 sed 标记 killed；4. 输出验证报告


- [20260407] seed [brainstorm] [score:6x4] [f:4] [angle:infra] description: run-seed.mjs 增加 executable prefix：Grep / Glob / Bash / Search / List / Write / Edit / Read / Create / Delete 作为合法命令前缀 | benefit: runner 可识别更多类型的可执行 approach，覆盖 skill file 编写、hookify 规则等场景 | reason: 已知资源：run-seed.mjs 第105行已有 9 种 prefix 检测。缺失环节：Grep/Glob/Bash 等常见命令未加入，skill 文件编写类 approach 仍被当作描述。连接方式：在第105行的 `!firstStep.startsWith('Edit ')` 后追加 `&& !firstStep.startsWith('Grep ') && !firstStep.startsWith('Glob ') && !firstStep.startsWith('Bash ') && !firstStep.startsWith('Write ') && !firstStep.startsWith('Read ')`
  | approach: 1. Edit run-seed.mjs 第105行，在 Edit / Read / Write 后追加 Grep / Glob / Bash / Search / List / Delete 等 prefix | shipped:20260407


- [20260407] seed [brainstorm] [score:5x5] [f:5] [angle:infra] description: ideas.md pool 文件头部添加统计注释行：自动追踪 total/shipped/killed/unshipped/f:N 分布 | benefit: 每次 brainstorm 前快速了解 pool 状态，不用手动 grep 统计 | reason: 已知资源：ideas.md 已有 pool header；run-seed.mjs 会读取 ideas.md。缺失环节：pool 头部没有统计行，需要手动运行 grep 计数。连接方式：在 ideas.md 顶部 # Idea Pool 后插入统计行，通过 run-seed.mjs 的 --limit N 模式输出实时统计并提示更新
  | approach: 1. Edit ideas.md 在 # Idea Pool 行后插入 `<!-- pool: total:N shipped:N killed:N unshipped:N f:1:N f:2:N f:3:N f:4:N f:5:N -->` | shipped:20260407


- [20260407] seed [brainstorm] [score:6x2] [f:2] [angle:MEMORY.md] description: MEMORY.md 添加 Brainstorm Effectiveness 表：追踪每批次 seeds 生成数量、shipped 率、平均 score，量化 brainstorm 质量 | benefit: 量化每次 brainstorm 的输出质量，发现批次退化趋势 | reason: 已知资源：MEMORY.md 有 Session History 和 Projects 表；brainstorm skill 有 Pool Monitoring 报告机制。缺失环节：没有结构化的 brainstorm 效果追踪表，每批次质量不可比较。连接方式：在 MEMORY.md 新增 ### Brainstorm Effectiveness 表，每次 brainstorm 后手动或脚本更新
  | approach: 阶段一(design)：设计表格列（批次日期/种子数/shipped数/平均分/最高分/killed原因）；阶段二(实现)：在 MEMORY.md 添加表格框架 | killed:20260407 non-executable approach


- [20260407] seed [brainstorm] [score:5x1] [f:1] [angle:skill-file] description: brainstorm 自改进机制设计：实现"种子质量评分 → 反馈 → 下次生成改进"的闭环——每次 shipped 后分析 approach 文本质量，下次 brainstorm 时据此调整评分权重 | benefit: brainstorm 随执行次数增加而质量提升，自身成为自我增强系统 | reason: 已知资源：brainstorming skill 有 Quality Gates 12 条；run-seed.mjs 追踪 shipped/unshipped。缺失环节：种子质量改进是开环的，每次 brainstorm 都从零开始，没有从历史执行结果中学习。连接方式：设计 FeedbackLoop 模块：解析 ideas.md 中 shipped seeds 的 approach 文本，提取高频模式（好的/坏的），在下一次 Generate seed 时注入提示词权重调整
  | approach: 阶段一(研究)：分析已 shipped 的 23 个 seeds 的 approach，找出共同模式；阶段二(设计)：在 brainstorming skill 中增加 "feedback-informed prompt weighting" 机制；阶段三(实现)：写一个 analyze-seeds.mjs 提取模式，更新 skill 文件 | killed:20260407 non-executable approach


- [20260407] seed [brainstorm] [score:8x4] [f:4] [angle:infra] description: 写 analyze-seed-quality.mjs：扫描 ideas.md 所有 unshipped seeds，检测 approach 是否为可执行命令，无效则列出并可选择自动标记 killed | benefit: 快速清理无效 seeds，量化评估 pool 健康度，支持 CI 集成 | reason: 已知资源：run-seed.mjs 第95-105行的 approach 解析和 executable prefix 逻辑；ideas.md 格式已知。缺失环节：没有独立工具对 pool 做全面可执行性审计。连接方式：复用 run-seed.mjs 的 approach 解析 + executable prefix 检测逻辑，独立为 check-seed-quality.mjs
  | approach: 1. Write D:/OpenClaw/workspace/scripts/analyze-seed-quality.mjs，复用 run-seed.mjs 的 approach 解析逻辑；2. 第1步检测 executable prefix，不匹配则输出 [INVALID]；3. 支持 --auto-kill 参数自动标记 killed；4. 支持 --json 输出便于 CI | shipped:20260407


- [20260407] seed [brainstorm] [score:8x3] [f:3] [angle:skill-file] description: brainstorm skill 添加种子重评分机制：生成时自我评估 approach 可执行性，f:4/f:5 若第1步不以合法前缀开头则自动降为 f:3 并改为分阶段 milestone | benefit: 减少因 approach 文本质量导致的 seed 废弃，提高 brainstorm 效率 | reason: 已知资源：brainstorming skill 已有 Gate 4（命令级步骤）和 Gate 4b（可执行前缀白名单）；D:/OpenClaw/workspace 已知晓 skill 文件位置。缺失环节：当前 Gate 4b 发现前缀无效就直接废弃，没有"降分保命"机制。连接方式：在 brainstorming skill 的 Gate 4b 段增加"降分保命"规则：f:4/f:5 prefix 无效 → 降为 f:3，approach 改为"阶段一(调研)；阶段二(实现)"
  | approach: 1. Read brainstorming skill 找到 Gate 4b 位置；2. 在 Gate 4b 段追加降分逻辑 | shipped:20260407


- [20260407] seed [brainstorm] [score:8x3] [f:3] [angle:skill-file] description: brainstorm skill 增加 reason 三段式强制验证：reason 必须包含「已知资源」「缺失环节」「连接方式」三个关键词，用正则检测，缺一废弃 | benefit: 防止 reason 空洞化，确保每个 seed 都有可执行的 connection 逻辑 | reason: 已知资源：brainstorming skill 已有 Gate 2（三段式必填）；D:/OpenClaw/workspace 已知晓 skill 文件位置。缺失环节：现有 Gate 2 只要求 reason 包含三段，没有强制关键词检测。连接方式：在 brainstorming skill 的 Gate 2 段增加正则检测：/已知资源.*缺失环节.*连接方式/s
  | approach: 1. Read brainstorming skill 找到 Gate 2 位置；2. 在 Gate 2 段追加正则验证逻辑 | shipped:20260407


- [20260407] seed [brainstorm] [score:12x4] [f:4] [angle:infra] description: scripts/check-project-health.mjs：扫描 80-PROJECTS 下所有项目，检测 package.json scripts 完整性（test/build/lint）和 git 状态，给出健康度评分 | benefit: 快速发现被遗忘的废弃项目，追踪哪些项目有 CI 哪些没有 | reason: 已知资源：scripts/ 下已有 34 个 check-*.mjs 脚本；D:/OpenClaw/workspace 已知晓 80-PROJECTS 结构。缺失环节：没有统一的项目健康度检查工具。连接方式：复用 scripts/check-package-scripts.mjs 的检测逻辑，新增 git status 检测
  | approach: 1. Write D:/OpenClaw/workspace/scripts/check-project-health.mjs，扫描 80-PROJECTS 下所有 package.json；2. 检测 test/build/lint scripts 是否存在；3. 检测 git status（clean/untracked/modified）；4. 输出健康度评分 | shipped:20260407


- [20260407] seed [brainstorm] [score:6x4] [f:4] [angle:infra] description: scripts/audit-shipped.mjs：扫描 ideas.md 所有 shipped seeds，提取每批 seeds 的平均分、shipped 率、killed 原因分布，输出 trend 报告 | benefit: 量化 brainstorm 随时间的质量变化，发现模式退化 | reason: 已知资源：ideas.md 已记录 23 个 shipped seeds；D:/OpenClaw/workspace 已知晓 seed 格式。缺失环节：没有工具分析 shipped seeds 历史趋势。连接方式：复用 analyze-seed-quality.mjs 的 ideas.md 解析逻辑，新增 shipped 日期聚合和统计
  | approach: 1. Write D:/OpenClaw/workspace/scripts/audit-shipped.mjs，解析 ideas.md shipped entries；2. 按日期聚合，输出 avg_score/shipped_rate/killed_reasons；3. 支持 --json 输出 | shipped:20260407


- [20260407] seed [brainstorm] [score:6x3] [f:3] [angle:skill-file] description: brainstorm skill 在 Pool Monitoring 段增加"无效 seed 自动标记"检查：每次 brainstorm 结束时运行 analyze-seed-quality.mjs --auto-kill，清理上一批无效 seeds | benefit: brainstorm 循环后立即清理，不让无效 seeds 累积在 pool 中 | reason: 已知资源：brainstorming skill 已有 Pool Monitoring 段；analyze-seed-quality.mjs 已实现并可被调用。缺失环节：当前 brainstorm 写完 seeds 后不自动清理，留下无效 approach 的 seeds。连接方式：在 brainstorming skill 的 Pool Monitoring 段（第8步"Pick highest-score seed"之前）插入"运行 node scripts/analyze-seed-quality.mjs --auto-kill"
  | approach: 1. Read brainstorming skill 找到 Pool Monitoring 位置；2. 在"Pick highest-score seed"前插入运行 analyze-seed-quality.mjs --auto-kill 的步骤 | shipped:20260407


- [20260407] seed [brainstorm] [score:8x2] [f:2] [angle:hookify] description: hookify 规则：拦截 Edit/Write/Delete 操作对 .git 目录的修改，防止误操作导致 git 状态破坏 | benefit: 保护 git 工作区，防止通过 Edit tool 误改 .git 内容 | reason: 已知资源：hookify 规则体系已建立；D:/OpenClaw/workspace 已有 hookify.prevent-node-modules-rf.local.md。缺失环节：没有防止误改 .git 的规则。连接方式：在 .claude/ 下创建 hookify.prevent-git-edit.local.md，event=file，pattern 匹配 /^\.git\//
  | approach: 1. Write D:/OpenClaw/workspace/.claude/hookify.prevent-git-edit.local.md，内容包含 event:file 和 pattern 匹配 .git 目录 | shipped:20260407


- [20260407] seed [brainstorm] [score:9x3] [f:3] [angle:infra] description: run-seed.mjs 添加 --bail-on-error flag：命令执行失败后立即退出，不继续执行剩余 steps | benefit: f:3 以上 seeds 如果第一步就失败，不需要继续跑后续 steps，避免无效等待 | reason: 已知资源：run-seed.mjs 第143-156行已有 execSync try/catch 和 timeout 逻辑。缺失环节：当前 runner 执行失败后继续下一步，但失败 seed 应立即停止。连接方式：在 run-seed.mjs 的 execSync catch 块中，如果 dryRun=false 且 bailOnError=true，则直接 process.exit(err.status ?? 1)
  | approach: 1. Edit run-seed.mjs 在第143行（execSync try/catch）添加 --bail-on-error flag 检测；2. 失败时检查 flag，为 true 则 process.exit(1) | shipped:20260407


- [20260407] seed [brainstorm] [score:10x4] [f:4] [angle:MEMORY.md] description: MEMORY.md Brainstorm Effectiveness 表：追踪每批次 brainstorm 的种子数/shipped数/平均分/最高分，在 Brainstorm 结束时自动更新 | benefit: 长期追踪 brainstorm 质量趋势，发现哪些项目方向最容易落地 | reason: 已知资源：MEMORY.md 有 Projects 表和 Session History；brainstorm skill 有 Pool Monitoring。缺失环节：没有结构化追踪 brainstorm 效果历史数据。连接方式：在 MEMORY.md 添加 ### Brainstorm Effectiveness 表，每次 shipped 后手动追加一行
  | approach: 1. Edit MEMORY.md 在 Session History 后添加 ### Brainstorm Effectiveness 表格；2. 表头：批次日期|种子数|shipped数|平均分|最高分|killed原因 | shipped:20260407


- [20260407] seed [brainstorm] [score:8x2] [f:2] [angle:skill-file] description: brainstorm metacognition.jsonl 追踪文件：brainstorm 批次结束后自动写入批次元数据到 .omc/innovation/brainstorm-metacognition.jsonl，包含 avg_score/gate_failures/self_assessment | benefit: 建立跨批次质量追踪机制，发现长期退化模式 | reason: 已知资源：brainstorming skill 刚增加元认知机制但无落地文件；scripts/analyze-seed-quality.mjs 有 JSONL 追加模式。缺失环节：没有持久化记录，每次 brainstorm 结束后批次评估数据丢失。连接方式：创建 brainstorm-metacognition.jsonl，brainstorm 结束后用 fs.appendFileSync 追加一条 JSONL 记录
  | approach: 阶段一(调研)：设计 JSONL 格式 {date,batch_seed_count,batch_avg_score,gate_failures,self_assessment,low_score_angles,high_score_projects}；阶段二(实现)：在 brainstorming skill 的"Report pool stats"后追加 JSONL 写入逻辑；阶段三(验证)：运行一次 brainstorm 验证 JSONL 有新记录 | shipped:20260407


- [20260407] seed [brainstorm] [score:6x3] [f:3] [angle:skill-file] description: brainstorm skill Gate 通过率追踪表：在 SKILL.md 末尾增加 ### Gate Statistics 历史表格，记录每次 brainstorm 的 Gate1-12 通过/失败次数统计 | benefit: 量化哪些 Gate 最容易失败，针对性改进 brainstorm prompt | reason: 已知资源：brainstorming skill 有 Gate 1-12 定义和通过率监控机制；D:/OpenClaw/workspace/knowledge/wikipedia/.omc/innovation/ideas.md 有批次历史。缺失环节：Gate 通过率没有结构化表格，每次都是定性评估。连接方式：在 SKILL.md 末尾增加 Gate Statistics 表格，每次 brainstorm 结束后更新
  | approach: 1. Read brainstorming skill 找到文档末尾位置；2. 在 ## Flow 之后追加 ### Gate Statistics 表格（表头：Date | Gate1 | Gate2 | ... | Gate12 | avg_score | self_assessment）；3. 每次 brainstorm 结束后手动更新一行 | shipped:20260407


- [20260407] seed [brainstorm] [score:5x4] [f:4] [angle:infra] description: brainstorm-metacognition.jsonl 可视化脚本：读取 JSONL 生成简单统计报告（avg_score 趋势、gate_failures 高频原因、self_assessment 通过率） | benefit: 快速了解 brainstorm 质量历史，不需要手动分析 JSONL | reason: 已知资源：brainstorm-metacognition.jsonl 将被创建；scripts/analyze-seed-quality.mjs 有 JSONL 读取模式。缺失环节：JSONL 没有可视化，只能用命令行 cat 查看。连接方式：复用 analyze-seed-quality.mjs 的 JSONL 读取逻辑，新增 trend 可视化输出
  | approach: 1. Write D:/OpenClaw/workspace/scripts/brainstorm-stats.mjs，读取 .omc/innovation/brainstorm-metacognition.jsonl；2. 输出 avg_score 趋势表 + gate_failures 排行榜 + self_assessment 通过率；3. 验证 node scripts/brainstorm-stats.mjs 正常输出 | shipped:20260407
