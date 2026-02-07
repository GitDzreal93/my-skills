#!/usr/bin/env python3
"""
质量校对脚本 - 检查技术书籍内容质量

检查项目:
1. 结构完整性
2. 代码语法
3. 插图引用
4. 语言风格
5. 技术准确性
"""

import re
import argparse
from pathlib import Path
from datetime import datetime
import ast


class BookProofreader:
    def __init__(self, chapters_dir):
        self.chapters_dir = Path(chapters_dir)
        self.issues = []
        self.warnings = []
        self.passed = []
        
    def check_structure(self, chapter_file):
        """检查章节结构完整性"""
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chapter_name = chapter_file.stem
        required_sections = [
            '## 本章导读',
            '## 核心概念',
            '## 实战案例',
            '## 本章小结',
            '## 章节测试',
            '## 参考答案'
        ]
        
        for section in required_sections:
            if section not in content:
                self.issues.append({
                    'chapter': chapter_name,
                    'type': '结构',
                    'level': 'error',
                    'message': f'缺少必需章节: {section}'
                })
        
        # 检查测试题数量
        choice_questions = len(re.findall(r'^\d+\.\s+', content, re.MULTILINE))
        if choice_questions < 5:
            self.warnings.append({
                'chapter': chapter_name,
                'type': '结构',
                'level': 'warning',
                'message': f'选择题数量不足: {choice_questions}/5'
            })
    
    def check_code_blocks(self, chapter_file):
        """检查代码块"""
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chapter_name = chapter_file.stem
        
        # 提取所有Python代码块
        python_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
        
        for idx, code in enumerate(python_blocks, 1):
            # 检查是否有注释
            if '#' not in code and '"""' not in code:
                self.warnings.append({
                    'chapter': chapter_name,
                    'type': '代码',
                    'level': 'warning',
                    'message': f'代码块 {idx} 缺少注释'
                })
            
            # 检查代码行数
            lines = code.strip().split('\n')
            if len(lines) > 50:
                self.warnings.append({
                    'chapter': chapter_name,
                    'type': '代码',
                    'level': 'warning',
                    'message': f'代码块 {idx} 超过50行 ({len(lines)}行)'
                })
            
            # 检查常用库的import
            if 'import' not in code and 'from' not in code:
                if any(lib in code for lib in ['np.', 'pd.', 'plt.', 'torch.']):
                    self.issues.append({
                        'chapter': chapter_name,
                        'type': '代码',
                        'level': 'error',
                        'message': f'代码块 {idx} 使用了库但缺少import语句'
                    })
            
            # 尝试解析Python语法
            try:
                ast.parse(code)
            except SyntaxError as e:
                self.issues.append({
                    'chapter': chapter_name,
                    'type': '代码',
                    'level': 'error',
                    'message': f'代码块 {idx} 语法错误: {e.msg} (行{e.lineno})'
                })
    
    def check_images(self, chapter_file):
        """检查插图引用"""
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chapter_name = chapter_file.stem
        
        # 检查图片引用
        image_refs = re.findall(r'!\[.*?\]\((.*?)\)', content)
        for img_path in image_refs:
            if img_path.startswith('http'):
                continue  # 跳过外部链接
            
            full_path = self.chapters_dir.parent / img_path
            if not full_path.exists():
                self.issues.append({
                    'chapter': chapter_name,
                    'type': '插图',
                    'level': 'error',
                    'message': f'图片文件不存在: {img_path}'
                })
        
        # 检查Mermaid图表语法
        mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)
        for idx, mermaid in enumerate(mermaid_blocks, 1):
            if not any(keyword in mermaid for keyword in ['flowchart', 'sequenceDiagram', 'graph']):
                self.warnings.append({
                    'chapter': chapter_name,
                    'type': '插图',
                    'level': 'warning',
                    'message': f'Mermaid图表 {idx} 可能缺少类型声明'
                })
    
    def check_language_style(self, chapter_file):
        """检查语言风格"""
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chapter_name = chapter_file.stem
        
        # 检查段落长度
        paragraphs = content.split('\n\n')
        for idx, para in enumerate(paragraphs):
            lines = para.strip().split('\n')
            # 跳过代码块和列表
            if para.startswith('```') or para.startswith('-') or para.startswith('|'):
                continue
            if len(lines) > 5:
                self.warnings.append({
                    'chapter': chapter_name,
                    'type': '风格',
                    'level': 'warning',
                    'message': f'段落 {idx} 过长 ({len(lines)}行)，建议拆分'
                })
        
        # 检查学术术语
        academic_terms = ['基于', '进行', '实现了', '具有较高的']
        for term in academic_terms:
            if term in content:
                self.warnings.append({
                    'chapter': chapter_name,
                    'type': '风格',
                    'level': 'warning',
                    'message': f'发现学术术语 "{term}"，建议使用日常语言'
                })
    
    def check_chapter(self, chapter_file, checks):
        """检查单个章节"""
        print(f"📖 检查章节: {chapter_file.name}")
        
        if 'structure' in checks:
            self.check_structure(chapter_file)
        
        if 'code' in checks:
            self.check_code_blocks(chapter_file)
        
        if 'images' in checks:
            self.check_images(chapter_file)
        
        if 'language' in checks:
            self.check_language_style(chapter_file)
    
    def run_checks(self, checks='all'):
        """运行所有检查"""
        if checks == 'all':
            check_list = ['structure', 'code', 'images', 'language']
        else:
            check_list = checks.split(',')
        
        chapter_files = sorted(self.chapters_dir.glob('*.md'))
        
        for chapter_file in chapter_files:
            self.check_chapter(chapter_file, check_list)
        
        return self.generate_report()
    
    def generate_report(self):
        """生成校对报告"""
        total_chapters = len(list(self.chapters_dir.glob('*.md')))
        
        report = f"""# 校对报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 整体统计
- 总章节数: {total_chapters}
- ❌ 严重问题: {len(self.issues)}
- ⚠️  警告: {len(self.warnings)}

---

"""
        
        # 按章节分组问题
        issues_by_chapter = {}
        for issue in self.issues:
            chapter = issue['chapter']
            if chapter not in issues_by_chapter:
                issues_by_chapter[chapter] = {'errors': [], 'warnings': []}
            issues_by_chapter[chapter]['errors'].append(issue)
        
        for warning in self.warnings:
            chapter = warning['chapter']
            if chapter not in issues_by_chapter:
                issues_by_chapter[chapter] = {'errors': [], 'warnings': []}
            issues_by_chapter[chapter]['warnings'].append(warning)
        
        # 输出问题详情
        if issues_by_chapter:
            report += "## 问题详情\n\n"
            for chapter in sorted(issues_by_chapter.keys()):
                report += f"### {chapter}\n\n"
                
                for error in issues_by_chapter[chapter]['errors']:
                    report += f"❌ **{error['type']}**: {error['message']}\n"
                
                for warning in issues_by_chapter[chapter]['warnings']:
                    report += f"⚠️  **{warning['type']}**: {warning['message']}\n"
                
                report += "\n"
        else:
            report += "## ✅ 所有检查通过\n\n"
        
        # 修改建议
        if self.issues or self.warnings:
            report += "## 修改建议\n\n"
            report += "1. 优先修复所有 ❌ 标记的严重问题\n"
            report += "2. 根据实际情况处理 ⚠️ 标记的警告\n"
            report += "3. 修改完成后重新运行校对\n\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description='技术书籍质量校对')
    parser.add_argument('--input', required=True, help='章节目录路径')
    parser.add_argument('--output', default='校对报告.md', help='输出报告路径')
    parser.add_argument('--checks', default='all', 
                        help='检查项目: all, structure, code, images, language')
    
    args = parser.parse_args()
    
    print("🔍 开始质量校对...")
    print(f"📂 检查目录: {args.input}")
    print(f"📋 检查项目: {args.checks}\n")
    
    proofreader = BookProofreader(args.input)
    report = proofreader.run_checks(args.checks)
    
    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 校对完成!")
    print(f"📄 报告已保存: {args.output}")
    print(f"\n统计:")
    print(f"  - 严重问题: {len(proofreader.issues)}")
    print(f"  - 警告: {len(proofreader.warnings)}")


if __name__ == '__main__':
    main()
