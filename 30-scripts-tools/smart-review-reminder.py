#!/usr/bin/env python3
"""
智能复习提醒 - Smart Review Reminder
功能：基于遗忘曲线的智能复习提醒
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

class SmartReviewReminder:
    """智能复习提醒"""
    
    def __init__(self):
        self.forgetting_curve = {
            1: 0.90,    # 1 天后
            3: 0.70,    # 3 天后
            7: 0.50,    # 7 天后
            14: 0.35,   # 14 天后
            30: 0.25    # 30 天后
        }
        self.reminder_file = Path(__file__).parent / 'review-schedule.json'
    
    def schedule_review(self, lesson_id: str, lesson_title: str, importance: str = 'medium'):
        """安排复习"""
        today = datetime.now()
        
        # 基于重要性调整复习间隔
        importance_multiplier = {
            'high': 0.7,    # 重要内容复习更频繁
            'medium': 1.0,
            'low': 1.3      # 次要内容复习间隔更长
        }
        
        multiplier = importance_multiplier.get(importance, 1.0)
        
        reviews = []
        for days, retention in self.forgetting_curve.items():
            review_date = today + timedelta(days=int(days * multiplier))
            reviews.append({
                'lesson_id': lesson_id,
                'lesson_title': lesson_title,
                'review_date': review_date.strftime('%Y-%m-%d'),
                'days_after': int(days * multiplier),
                'expected_retention': f'{retention:.0%}',
                'importance': importance,
                'status': 'pending',
                'created_at': today.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # 保存到文件
        self._save_reviews(reviews)
        
        return reviews
    
    def _save_reviews(self, reviews: List[Dict]):
        """保存复习计划"""
        existing = self._load_reviews()
        
        # 合并
        existing.extend(reviews)
        
        # 去重
        seen = set()
        unique = []
        for review in existing:
            key = f"{review['lesson_id']}_{review['review_date']}"
            if key not in seen:
                seen.add(key)
                unique.append(review)
        
        # 保存
        with open(self.reminder_file, 'w', encoding='utf-8') as f:
            json.dump(unique, f, ensure_ascii=False, indent=2)
    
    def _load_reviews(self) -> List[Dict]:
        """加载复习计划"""
        if not self.reminder_file.exists():
            return []
        
        with open(self.reminder_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_due_reviews(self, date: str = None) -> List[Dict]:
        """获取今日应复习的内容"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        reviews = self._load_reviews()
        due = [r for r in reviews if r['review_date'] == date and r['status'] == 'pending']
        
        return due
    
    def mark_reviewed(self, lesson_id: str, review_date: str):
        """标记为已复习"""
        reviews = self._load_reviews()
        
        for review in reviews:
            if review['lesson_id'] == lesson_id and review['review_date'] == review_date:
                review['status'] = 'completed'
                review['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                break
        
        with open(self.reminder_file, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
    
    def get_statistics(self) -> Dict:
        """获取统计"""
        reviews = self._load_reviews()
        
        total = len(reviews)
        completed = len([r for r in reviews if r['status'] == 'completed'])
        pending = len([r for r in reviews if r['status'] == 'pending'])
        overdue = len([r for r in reviews if r['status'] == 'pending' and r['review_date'] < datetime.now().strftime('%Y-%m-%d')])
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'overdue': overdue,
            'completion_rate': f'{completed/total:.0%}' if total > 0 else '0%'
        }
    
    def print_due_reviews(self):
        """打印今日应复习内容"""
        due = self.get_due_reviews()
        
        print("=" * 60)
        print("今日复习提醒")
        print("=" * 60)
        
        if not due:
            print("\n[OK] 今日无复习任务")
        else:
            print(f"\n[INFO] 今日应复习 {len(due)} 个教训:")
            for i, review in enumerate(due, 1):
                print(f"\n  {i}. {review['lesson_id']}: {review['lesson_title']}")
                print(f"     复习时间：{review['days_after']}天后")
                print(f"     预期保留：{review['expected_retention']}")
                print(f"     重要性：{review['importance']}")
        
        stats = self.get_statistics()
        print(f"\n【统计】")
        print(f"  总复习数：{stats['total']}")
        print(f"  已完成：{stats['completed']}")
        print(f"  待完成：{stats['pending']}")
        print(f"  已过期：{stats['overdue']}")
        print(f"  完成率：{stats['completion_rate']}")
        
        print("\n" + "=" * 60)


def demo_reminder():
    """演示复习提醒"""
    print("=" * 60)
    print("智能复习提醒")
    print("=" * 60)
    
    reminder = SmartReviewReminder()
    
    # 示例教训
    lessons = [
        ('[SYS-019]', '100% 防护系统', 'high'),
        ('[MULTI-021]', '规划者优化', 'medium'),
        ('[MEM-011]', '记忆系统优化', 'medium')
    ]
    
    print("\n[安排复习计划]")
    for lesson_id, title, importance in lessons:
        reviews = reminder.schedule_review(lesson_id, title, importance)
        print(f"  [OK] {lesson_id}: 安排 {len(reviews)} 次复习")
    
    print()
    
    # 打印今日应复习
    reminder.print_due_reviews()


if __name__ == "__main__":
    demo_reminder()
