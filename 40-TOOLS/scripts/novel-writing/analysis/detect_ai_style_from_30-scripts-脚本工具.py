#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Writing Style Detector (Optimized Version)
Detect AI writing patterns in chapters
Fixed false positives for "他/她" patterns
"""

import os
import re
from datetime import datetime

# Config
DRAFTS_FOLDER = r"D:\OpenClaw\workspace\50-novels\drafts"
AI_THRESHOLD = 0.2

def detect_ai_patterns(text):
    """
    Detect AI writing patterns
    Returns AI rate (0-1) and detected patterns
    """
    patterns = {
        '排比句过多': 0,
        '情感太直白': 0,
        '缺少感官细节': 0,
        '说教味重': 0,
        '对话太完整': 0,
        '过渡词过多': 0,
        '总结式结尾': 0,
        '抽象词过多': 0,
        '重复句式': 0,
        '缺少具体细节': 0,
    }
    
    word_count = len(text)
    
    # 1. 排比句检测 (排除"他/她"误判)
    parallel_patterns = [
        r'(一样)[\u4e00-\u9fa5]{0,20}\1[\u4e00-\u9fa5]{0,20}\1',  # "一样...一样...一样"
        r'(不是[\u4e00-\u9fa5]+是[\u4e00-\u9fa5]+).*\1',  # "不是...是...不是...是"
        r'(可以[\u4e00-\u9fa5]+).*\1.*\1',  # "可以...可以...可以"
        r'(这.*?这.*?这.*?这)',  # 连续 4 个"这"
        r'(那.*?那.*?那.*?那)',  # 连续 4 个"那"
    ]
    parallel_count = 0
    for pattern in parallel_patterns:
        parallel_count += len(re.findall(pattern, text, re.DOTALL))
    
    # 检测真正的排比句 (3 句以上相同结构)
    sentences = re.split(r'[。！？]', text)
    sentence_starts = [s[:5] for s in sentences if len(s) > 10]
    from collections import Counter
    start_counts = Counter(sentence_starts)
    repeated_starts = sum(1 for count in start_counts.values() if count >= 3)
    parallel_count += repeated_starts
    
    if parallel_count >= 2:
        patterns['排比句过多'] = min(parallel_count * 0.15, 0.4)
    
    # 2. 情感直白检测
    emotion_words = [
        '很伤心', '很难过', '很愤怒', '很激动', '很兴奋', '很失落', '很绝望',
        '非常', '特别', '十分', '极其', '无比',
    ]
    emotion_count = sum(text.count(word) for word in emotion_words)
    if emotion_count >= 3:
        patterns['情感太直白'] = min(emotion_count * 0.08, 0.3)
    
    # 3. 感官细节检测
    sensory_words = ['看见', '听到', '闻到', '感觉', '触感', '味道', '声音', '颜色', '光影', '气味', '响', '亮', '暗']
    sensory_count = sum(text.count(word) for word in sensory_words)
    if word_count > 1000 and sensory_count < 8:
        patterns['缺少感官细节'] = 0.25
    elif word_count > 2000 and sensory_count < 15:
        patterns['缺少感官细节'] = 0.2
    
    # 4. 说教检测
    preach_words = ['应该', '必须', '一定要', '要知道', '记住', '明白了吗', '这就是', '所以说', '由此可见']
    preach_count = sum(text.count(word) for word in preach_words)
    if preach_count >= 4:
        patterns['说教味重'] = min(preach_count * 0.06, 0.3)
    
    # 5. 对话完整性检测
    dialogue_patterns = re.findall(r'"([^"]+)"', text)
    if len(dialogue_patterns) > 5:
        complete_dialogue = sum(1 for d in dialogue_patterns if len(d) > 15 and '...' not in d and '……' not in d)
        if complete_dialogue / len(dialogue_patterns) > 0.7:
            patterns['对话太完整'] = 0.2
    
    # 6. 过渡词过多
    transition_words = ['然后', '接着', '于是', '因此', '所以', '然而', '但是', '可是', '不过']
    transition_count = sum(text.count(word) for word in transition_words)
    if transition_count >= 8:
        patterns['过渡词过多'] = min(transition_count * 0.03, 0.25)
    
    # 7. 总结式结尾检测
    summary_endings = [
        r'这就是[\u4e00-\u9fa5]+',
        r'他终于明白了[\u4e00-\u9fa5]+',
        r'他知道了[\u4e00-\u9fa5]+',
        r'这就是[\u4e00-\u9fa5]+的意义',
        r'他下定决心[\u4e00-\u9fa5]+',
    ]
    summary_count = sum(len(re.findall(pattern, text)) for pattern in summary_endings)
    if summary_count >= 2:
        patterns['总结式结尾'] = min(summary_count * 0.1, 0.3)
    
    # 8. 抽象词过多检测
    abstract_words = ['意义', '价值', '目标', '梦想', '希望', '未来', '人生', '世界', '生活', '命运']
    abstract_count = sum(text.count(word) for word in abstract_words)
    if word_count > 1000 and abstract_count >= 10:
        patterns['抽象词过多'] = min(abstract_count * 0.03, 0.25)
    
    # 9. 重复句式检测 (排除正常代词)
    sentence_patterns = re.findall(r'([\u4e00-\u9fa5]{8,20})[\u3002\uff01]', text)
    pattern_counts = Counter(sentence_patterns)
    repeated = sum(1 for count in pattern_counts.values() if count >= 3)
    if repeated >= 3:
        patterns['重复句式'] = min(repeated * 0.1, 0.3)
    
    # 10. 缺少具体细节检测
    number_count = len(re.findall(r'\d+', text))
    object_patterns = ['书包', '卷子', '笔', '手机', '桌子', '椅子', '门', '窗', '书', '衣服']
    object_count = sum(text.count(obj) for obj in object_patterns)
    if word_count > 2000 and number_count < 3 and object_count < 5:
        patterns['缺少具体细节'] = 0.2
    
    # Calculate total AI rate
    ai_rate = sum(patterns.values())
    ai_rate = min(ai_rate, 1.0)
    
    # Filter patterns with score > 0
    detected_patterns = {k: v for k, v in patterns.items() if v > 0}
    
    return ai_rate, detected_patterns

def check_chapter_ai_rate(file_path):
    """Check single chapter AI rate"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ai_rate, patterns = detect_ai_patterns(content)
        
        # Determine risk level
        if ai_rate > 0.5:
            status = 'HIGH_RISK'
        elif ai_rate > 0.3:
            status = 'MEDIUM_RISK'
        elif ai_rate > 0.15:
            status = 'LOW_RISK'
        else:
            status = 'VERY_LOW_RISK'
        
        return {
            'file': file_path,
            'name': os.path.basename(file_path),
            'ai_rate': ai_rate,
            'status': status,
            'patterns': patterns
        }
    except Exception as e:
        return {
            'file': file_path,
            'name': os.path.basename(file_path),
            'ai_rate': 0,
            'status': 'ERROR',
            'patterns': {},
            'error': str(e)
        }

def scan_drafts_folder():
    """Scan drafts folder"""
    print("=" * 60)
    print("AI Writing Style Detection Report (Optimized)")
    print("=" * 60)
    print(f"Folder: {DRAFTS_FOLDER}")
    print(f"Threshold: {AI_THRESHOLD}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    draft_files = []
    for file in os.listdir(DRAFTS_FOLDER):
        if file.endswith('.md') and file.startswith('第'):
            draft_files.append(os.path.join(DRAFTS_FOLDER, file))
    
    draft_files.sort(key=lambda x: int(re.search(r'第 (\d+) 章', x).group(1)) if re.search(r'第 (\d+) 章', x) else 0)
    
    results = []
    for file_path in draft_files:
        result = check_chapter_ai_rate(file_path)
        results.append(result)
    
    print("Chapter AI Rate:")
    print("-" * 60)
    print(f"{'Chapter':<40} {'AI Rate':<10} {'Risk':<15}")
    print("-" * 60)
    
    high_risk = 0
    medium_risk = 0
    low_risk = 0
    very_low_risk = 0
    
    for result in results:
        chapter_name = result['name'][:38].ljust(40)
        ai_rate = f"{result['ai_rate']:.2f}".ljust(10)
        status = result['status']
        
        print(f"{chapter_name} {ai_rate} {status}")
        
        if 'HIGH_RISK' in status:
            high_risk += 1
        elif 'MEDIUM_RISK' in status:
            medium_risk += 1
        elif 'LOW_RISK' in status:
            low_risk += 1
        else:
            very_low_risk += 1
    
    print("-" * 60)
    print()
    
    print("Summary:")
    print(f"  Total chapters: {len(results)}")
    print(f"  High risk: {high_risk}")
    print(f"  Medium risk: {medium_risk}")
    print(f"  Low risk: {low_risk}")
    print(f"  Very low risk: {very_low_risk}")
    print()
    
    if high_risk > 0 or medium_risk > 0:
        print("Detected Patterns:")
        print("-" * 60)
        for result in results:
            if result['patterns']:
                print(f"  {result['name']}:")
                for pattern, score in result['patterns'].items():
                    print(f"    - {pattern}: {score:.2f}")
        print("-" * 60)
        print()
    
    print("Suggestions:")
    if high_risk > 0 or medium_risk > 0:
        print("  Please revise high/medium risk chapters:")
        print("    1. Reduce parallel sentences (排比句)")
        print("    2. Show emotions through actions, not direct statements")
        print("    3. Add sensory details (visual, auditory, olfactory)")
        print("    4. Reduce preaching and moral lessons")
        print("    5. Make dialogues more natural (interruptions, ellipsis)")
        print("    6. Reduce transition words (然后，接着，于是...)")
        print("    7. Avoid summary endings")
        print("    8. Use more concrete details (numbers, objects)")
        print("    9. Vary sentence structures")
        print("   10. Add specific item names and actions")
    elif low_risk > 0:
        print("  Some chapters have low AI risk, but can be improved:")
        print("    - Add more sensory details")
        print("    - Make dialogues more natural")
        print("    - Reduce abstract words")
    else:
        print("  All chapters have very low AI risk, keep it up!")
    
    print()
    print("=" * 60)
    
    return results

def main():
    """Main function"""
    if not os.path.exists(DRAFTS_FOLDER):
        print(f"Error: Folder not found - {DRAFTS_FOLDER}")
        return
    
    results = scan_drafts_folder()
    
    report_file = os.path.join(DRAFTS_FOLDER, "ai_detection_report_optimized.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("AI Writing Style Detection Report (Optimized)\n")
        f.write("=" * 60 + "\n")
        f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Threshold: {AI_THRESHOLD}\n")
        f.write("=" * 60 + "\n\n")
        
        for result in results:
            f.write(f"{result['name']}: AI Rate {result['ai_rate']:.2f} [{result['status']}]\n")
            if result['patterns']:
                for pattern, score in result['patterns'].items():
                    f.write(f"  - {pattern}: {score:.2f}\n")
        
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"Report saved to: {report_file}")

if __name__ == "__main__":
    main()
