#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识卡片生成器 - Android 版
基于 Kivy 的移动端应用
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.core.window import Window
from pathlib import Path
import sys

# 添加核心代码路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入知识卡片生成器
try:
    from knowledge_card_generator import KnowledgeCardGenerator
    GENERATOR_AVAILABLE = True
except ImportError:
    GENERATOR_AVAILABLE = False
    print("警告：知识卡片生成器未找到")


class KnowledgeCardApp(App):
    """知识卡片生成器 App"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.generator = KnowledgeCardGenerator() if GENERATOR_AVAILABLE else None
        self.selected_file = None

    def build(self):
        """构建 UI"""
        # 设置窗口大小 (移动端)
        Window.size = (400, 700)
        Window.clearcolor = (0.95, 0.95, 0.95, 1)

        # 主布局
        layout = FloatLayout()

        # 标题
        title = Label(
            text='知识卡片生成器',
            size_hint=(1, 0.1),
            pos_hint={'top': 1},
            font_size='24sp',
            bold=True
        )
        layout.add_widget(title)

        # 文件选择器
        self.file_chooser = FileChooserListView(
            path=str(Path.home()),
            filters=['*.pdf'],
            size_hint=(1, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        layout.add_widget(self.file_chooser)

        # 处理按钮
        self.process_btn = Button(
            text='生成知识卡片',
            size_hint=(0.8, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.2},
            font_size='18sp'
        )
        self.process_btn.bind(on_press=self.process_pdf)
        layout.add_widget(self.process_btn)

        # 进度条
        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint=(0.8, 0.05),
            pos_hint={'center_x': 0.5, 'y': 0.12}
        )
        layout.add_widget(self.progress)

        # 状态标签
        self.status_label = Label(
            text='请选择 PDF 文件',
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            color=(0.3, 0.3, 0.3, 1)
        )
        layout.add_widget(self.status_label)

        return layout

    def process_pdf(self, instance):
        """处理 PDF 文件"""
        # 获取选中的文件
        selection = self.file_chooser.selection
        if not selection:
            self.show_error('请先选择 PDF 文件')
            return

        self.selected_file = selection[0]
        self.status_label.text = f'正在处理：{Path(self.selected_file).name}'
        self.progress.value = 10

        try:
            if self.generator:
                # 调用生成器
                output_dir = Path(self.selected_file).parent / 'output'
                output_dir.mkdir(exist_ok=True)

                self.progress.value = 50
                self.status_label.text = '提取元数据...'

                # 处理 PDF
                result = self.generator.process(self.selected_file, str(output_dir))

                self.progress.value = 100
                self.status_label.text = f'完成！已保存到：{output_dir}'

                self.show_success(f'知识卡片已生成！\n{output_dir}')
            else:
                self.show_error('生成器未初始化')

        except Exception as e:
            self.progress.value = 0
            self.status_label.text = '处理失败'
            self.show_error(f'处理失败：{str(e)}')

    def show_error(self, message):
        """显示错误弹窗"""
        popup = Popup(
            title='错误',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def show_success(self, message):
        """显示成功弹窗"""
        popup = Popup(
            title='成功',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()


if __name__ == '__main__':
    KnowledgeCardApp().run()
