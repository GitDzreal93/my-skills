#!/usr/bin/env python3
"""
生成技术文章总结卡片

功能：
- 分析文章内容，提取关键信息
- 生成精美的总结卡片HTML组件
- 生成独立的HTML预览文件
- 支持导出为图片（使用Playwright）
- 响应式设计，适配PC和移动端

使用：
python scripts/generate_share_card.py --input chapter.md --share-url "https://..."
python scripts/generate_share_card.py --input chapter.md --html-output preview.html
python scripts/generate_share_card.py --input chapter.md --export-image card.png
"""

import argparse
import re
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime


# 卡片配色方案（清新技术风）
CARD_COLORS = {
    'primary': '#2563EB',       # 科技蓝
    'secondary': '#7C3AED',     # 紫色
    'accent': '#10B981',        # 绿色
    'bg_gradient': 'linear-gradient(135deg, #F0F9FF 0%, #FFFFFF 50%, #F5F3FF 100%)',
    'card_shadow': '0 8px 30px rgba(37, 99, 235, 0.12)',
}


def extract_title(content):
    """提取文章标题（第一个 # 标题）"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "技术分享"


def extract_summary(content):
    """提取文章摘要（第一段或前100字）"""
    # 找第一个段落
    paragraphs = re.split(r'\n\n+', content)
    for para in paragraphs:
        para = para.strip()
        # 跳过标题
        if para.startswith('#'):
            continue
        # 跳过代码块
        if para.startswith('```'):
            continue
        # 清理 Markdown 格式
        para = re.sub(r'[*_#`]', '', para)
        if 20 <= len(para) <= 200:
            return para
    return "本文介绍了相关技术概念和实践方法。"


def extract_key_points(content, num_points=5):
    """
    提取文章核心要点
    优先提取：加粗文本、列表项、独立段落
    """
    points = []

    # 提取加粗的重点内容
    bold_items = re.findall(r'\*\*(.+?)\*\*', content)
    for item in bold_items:
        item = item.strip()
        if 4 <= len(item) <= 50 and not item.endswith(('：', ':')):
            points.append(item)

    # 提取列表项
    if len(points) < num_points:
        list_items = re.findall(r'^[\-\*]\s+(.+)$', content, re.MULTILINE)
        for item in list_items:
            item = item.strip()
            if 4 <= len(item) <= 80 and item not in points:
                points.append(item)

    # 提取独立段落（短句子）
    if len(points) < num_points:
        paragraphs = re.findall(r'^(?!#|[\-\*]|\|).{20,100}$', content, re.MULTILINE)
        for para in paragraphs:
            para = para.strip()
            if para and para not in points:
                points.append(para)

    return points[:num_points]


def extract_tags(content):
    """提取文章关键词/标签"""
    tags = []

    # 常见技术关键词
    tech_keywords = [
        '机器学习', '深度学习', 'Python', 'JavaScript', 'Go', 'Java',
        'React', 'Vue', 'Docker', 'Kubernetes', '微服务', '前端', '后端',
        '算法', '数据结构', '数据库', '编程', '教程', '实战', '入门',
        '进阶', '架构', '设计模式', '性能优化', '最佳实践'
    ]

    content_lower = content.lower()
    for keyword in tech_keywords:
        if keyword.lower() in content_lower or keyword in content:
            tags.append(keyword)

    # 如果标签太少，从标题中提取
    if len(tags) < 3:
        title = extract_title(content)
        for keyword in tech_keywords:
            if keyword in title and keyword not in tags:
                tags.append(keyword)

    return tags[:8]


def generate_full_html_page(title, summary, key_points, tags, share_url, article_content=""):
    """生成完整的HTML页面（用于独立预览）"""

    card_html = generate_share_card_html(title, summary, key_points, tags, share_url)

    full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 总结卡片</title>
    <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
</head>
<body style="margin: 0; padding: 20px; background: #f5f5f5; min-height: 100vh;">
    <div style="max-width: 1200px; margin: 0 auto;">
        <!-- 文章内容预览（可选） -->
        {f'<div style="background: white; padding: 40px; border-radius: 16px; margin-bottom: 40px; box-shadow: 0 2px 12px rgba(0,0,0,0.08);"><article style="line-height: 1.8; color: #333;">{article_content}</article></div>' if article_content else ''}

        <!-- 分享卡片 -->
        {card_html}

        <!-- 使用说明 -->
        <div style="margin-top: 40px; padding: 20px; background: white; border-radius: 12px; border-left: 4px solid #2563EB;">
            <h3 style="margin: 0 0 10px 0; color: #2563EB;">📖 使用说明</h3>
            <ul style="margin: 0; padding-left: 20px; color: #666; line-height: 1.8;">
                <li>点击"复制链接"按钮可复制文章链接</li>
                <li>点击"导出图片"按钮可将卡片保存为PNG图片</li>
                <li>也可以使用系统截图工具：<strong>Mac: Cmd+Shift+4</strong>，<strong>Windows: Win+Shift+S</strong></li>
            </ul>
        </div>
    </div>

    <script>
        // 重写导出图片功能，使用html2canvas
        function exportCardImage() {{
            const card = document.getElementById('summaryCard');
            const button = event.target.closest('.action-btn');

            // 禁用按钮，显示加载状态
            button.disabled = true;
            button.innerHTML = '<svg class="spinner" width="18" height="18" viewBox="0 0 18 18" fill="none" style="animation: spin 1s linear infinite;"><circle cx="9" cy="9" r="7" stroke="currentColor" stroke-width="2" stroke-dasharray="14" stroke-dashoffset="7"></circle></svg><span>生成中...</span>';

            html2canvas(card, {{
                backgroundColor: '#ffffff',
                scale: 2,
                useCORS: true,
                logging: false,
                allowTaint: true,
                onclone: function(clonedDoc) {{
                    // 确保克隆的文档样式正确
                    const clonedCard = clonedDoc.getElementById('summaryCard');
                    if (clonedCard) {{
                        clonedCard.style.transform = 'none';
                        clonedCard.style.boxShadow = '0 8px 30px rgba(37, 99, 235, 0.12)';
                    }}
                }}
            }}).then(canvas => {{
                // 创建下载链接
                const link = document.createElement('a');
                link.download = '技术分享卡片.png';
                link.href = canvas.toDataURL('image/png', 1.0);
                link.click();

                // 恢复按钮
                button.disabled = false;
                button.innerHTML = '<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M3.75 14.25V3.75C3.75 3.33757 4.08757 3 4.5 3H13.5C13.9124 3 14.25 3.33757 14.25 3.75V14.25" stroke="currentColor" stroke-width="1.5"/><path d="M6 11.25L9 8.25L12 11.25" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 8.25V15.75" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg><span>导出图片</span>';

                showToast('导出成功！');
            }}).catch(err => {{
                console.error('导出失败:', err);
                button.disabled = false;
                button.innerHTML = '<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M3.75 14.25V3.75C3.75 3.33757 4.08757 3 4.5 3H13.5C13.9124 3 14.25 3.33757 14.25 3.75V14.25" stroke="currentColor" stroke-width="1.5"/><path d="M6 11.25L9 8.25L12 11.25" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 8.25V15.75" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg><span>导出图片</span>';
                showFallbackGuide();
            }});
        }}

        // 旋转动画
        const style = document.createElement('style');
        style.textContent = '@keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }} .spinner {{ animation: spin 1s linear infinite; }}';
        document.head.appendChild(style);
    </script>
</body>
</html>'''
    return full_html


def convert_markdown_to_html(markdown_content):
    """简单的Markdown转HTML（用于预览）"""
    import re

    html = markdown_content

    # 标题
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # 加粗
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # 列表
    html = re.sub(r'^[\-\*] (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.+</li>\n?)+', r'<ul>\0</ul>', html)

    # 段落
    html = re.sub(r'\n\n+', '</p><p>', html)
    html = '<p>' + html + '</p>'

    # 清理空标签
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'<p>(<h[1-6]>)', r'\1', html)
    html = re.sub(r'(</h[1-6]>)</p>', r'\1', html)

    return html


def export_card_to_image(file_path, output_path, share_url=None):
    """使用Playwright将卡片导出为图片"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 未安装 playwright，正在安装...")
        subprocess.run(['pip', 'install', 'playwright'], check=True)
        subprocess.run(['playwright', 'install', 'chromium'], check=True)
        from playwright.sync_api import sync_playwright

    file_path = Path(file_path)

    # 读取文章内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取信息
    title = extract_title(content)
    summary = extract_summary(content)
    key_points = extract_key_points(content)
    tags = extract_tags(content)

    if not share_url:
        share_url = "https://your-book-url.com"

    # 生成完整HTML页面
    html_content = generate_full_html_page(title, summary, key_points, tags, share_url)

    # 创建临时HTML文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_html_path = f.name

    try:
        # 使用Playwright截图
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1400, 'height': 1200})
            page.goto(f'file://{temp_html_path}')

            # 等待卡片加载
            page.wait_for_selector('#summaryCard')

            # 隐藏操作按钮和提示（用于截图）
            page.evaluate('''
                () => {
                    // 隐藏操作按钮区域
                    const actions = document.querySelector('.card-actions');
                    if (actions) actions.style.display = 'none';

                    // 隐藏分享提示
                    const prompt = document.querySelector('.card-prompt');
                    if (prompt) prompt.style.display = 'none';

                    // 隐藏toast提示
                    const toast = document.querySelector('.success-toast');
                    if (toast) toast.style.display = 'none';
                }
            ''')

            # 只截取卡片部分
            card = page.locator('#summaryCard')
            card.screenshot(path=output_path)

            browser.close()

        print(f"✅ 卡片已导出为图片: {output_path}")
        return True

    except Exception as e:
        print(f"❌ 导出图片失败: {e}")
        print(f"💡 提示: 请使用浏览器打开生成的HTML文件，然后点击'导出图片'按钮")
        return False

    finally:
        # 删除临时文件
        Path(temp_html_path).unlink(missing_ok=True)


def generate_html_preview(file_path, output_path, share_url=None, include_article=False):
    """生成独立的HTML预览文件"""
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return False

    # 读取文章内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取信息
    title = extract_title(content)
    summary = extract_summary(content)
    key_points = extract_key_points(content)
    tags = extract_tags(content)

    if not share_url:
        share_url = "https://your-book-url.com"

    # 转换文章内容为HTML（可选）
    article_html = ""
    if include_article:
        article_html = convert_markdown_to_html(content)

    # 生成完整HTML页面
    html_content = generate_full_html_page(title, summary, key_points, tags, share_url, article_html)

    # 写入文件
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML预览文件已生成: {output_path}")
    print()
    print(f"📌 标题: {title}")
    print(f"📝 摘要: {summary[:50]}...")
    print(f"💡 核心要点: {len(key_points)} 条")
    print(f"🏷️  标签: {', '.join(tags)}")
    print()
    print(f"💡 请在浏览器中打开该文件查看效果并导出图片")
    print(f"   open {output_path}")
    print()

    return True


def generate_share_card_html(title, summary, key_points, tags, share_url):
    """生成技术文章总结卡片的HTML"""

    # 生成当前日期
    current_date = datetime.now().strftime('%Y年%m月%d日')

    # 标签HTML
    tags_html = ' '.join([f'<span class="card-tag">#{tag}</span>' for tag in tags])

    # 要点HTML
    points_html = '\n'.join([
        f'''<div class="card-point">
            <div class="point-number">{i+1}</div>
            <div class="point-text">{point}</div>
        </div>''' for i, point in enumerate(key_points)
    ])

    html = f'''
<!-- 技术文章总结卡片 -->
<div class="article-summary-card" id="summaryCard">
    <!-- 卡片头部 -->
    <div class="card-header">
        <div class="card-badge">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 0C3.58 0 0 3.58 0 8s3.58 8 8 8 8-3.58 8-8-3.58-8-8-8zm1 11H7v-1h2v1zm0-2H7V4h2v5z"/>
            </svg>
            <span>技术干货</span>
        </div>
        <div class="card-date">{current_date}</div>
    </div>

    <!-- 标题区域 -->
    <div class="card-title-area">
        <h2 class="card-title">{title}</h2>
        <p class="card-summary">{summary}</p>
    </div>

    <!-- 核心要点 -->
    <div class="card-content">
        <div class="content-title">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M9 16.5C13.125 16.5 16.5 13.125 16.5 9C16.5 4.875 13.125 1.5 9 1.5C4.875 1.5 1.5 4.875 1.5 9C1.5 13.125 4.875 16.5 9 16.5Z" stroke="currentColor" stroke-width="1.5"/>
                <path d="M9 12V9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M9 6H9.0075" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <span>核心要点</span>
        </div>
        <div class="points-list">
            {points_html}
        </div>
    </div>

    <!-- 标签区域 -->
    <div class="card-tags">
        {tags_html}
    </div>

    <!-- 分享提示 -->
    <div class="card-prompt">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 18.333C14.583 18.333 18.333 14.583 18.333 9.99967C18.333 5.41634 14.583 1.66634 10 1.66634C5.41667 1.66634 1.66667 5.41634 1.66667 9.99967C1.66667 14.583 5.41667 18.333 10 18.333Z" stroke="#F59E0B" stroke-width="1.5"/>
            <path d="M10 14.1663V9.16634" stroke="#F59E0B" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M10 6.66699H10.0083" stroke="#F59E0B" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span>如果这篇文章对你有帮助，欢迎分享给更多小伙伴！</span>
    </div>

    <!-- 操作按钮 -->
    <div class="card-actions">
        <button class="action-btn action-btn-primary" onclick="copyArticleLink('{share_url}')">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M6.75 3H11.25C12.4926 3 13.5 4.00736 13.5 5.25V12.75C13.5 13.9926 12.4926 15 11.25 15H6.75C5.50736 15 4.5 13.9926 4.5 12.75V5.25C4.5 4.00736 5.50736 3 6.75 3Z" stroke="currentColor" stroke-width="1.5"/>
                <path d="M9.75 3H11.25C12.4926 3 13.5 3.75736 13.5 5V12.75" stroke="currentColor" stroke-width="1.5"/>
                <path d="M9 7.5H11.25" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M9 10.5H11.25" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <span>复制链接</span>
        </button>
        <button class="action-btn action-btn-secondary" onclick="exportCardImage()">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M3.75 14.25V3.75C3.75 3.33757 4.08757 3 4.5 3H13.5C13.9124 3 14.25 3.33757 14.25 3.75V14.25" stroke="currentColor" stroke-width="1.5"/>
                <path d="M6 11.25L9 8.25L12 11.25" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 8.25V15.75" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>导出图片</span>
        </button>
    </div>

    <!-- 成功提示 -->
    <div class="success-toast" id="toast">复制成功！</div>
</div>

<style>
/* 容器 */
.article-summary-card {{
    max-width: 680px;
    margin: 40px auto;
    padding: 32px;
    background: {CARD_COLORS['bg_gradient']};
    border-radius: 16px;
    box-shadow: {CARD_COLORS['card_shadow']};
    border: 1px solid rgba(37, 99, 235, 0.1);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    position: relative;
}}

/* 头部 */
.card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}}

.card-badge {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    background: linear-gradient(135deg, {CARD_COLORS['primary']}, {CARD_COLORS['secondary']});
    color: white;
    font-size: 13px;
    font-weight: 600;
    border-radius: 20px;
}}

.card-date {{
    font-size: 13px;
    color: #9CA3AF;
}}

/* 标题区 */
.card-title-area {{
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 2px solid rgba(37, 99, 235, 0.1);
}}

.card-title {{
    margin: 0 0 12px 0;
    font-size: 24px;
    font-weight: 700;
    color: #1F2937;
    line-height: 1.4;
}}

.card-summary {{
    margin: 0;
    font-size: 15px;
    color: #6B7280;
    line-height: 1.7;
}}

/* 内容区 */
.card-content {{
    margin-bottom: 20px;
}}

.content-title {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 600;
    color: {CARD_COLORS['primary']};
    margin-bottom: 16px;
}}

.points-list {{
    display: flex;
    flex-direction: column;
    gap: 12px;
}}

.card-point {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 14px 16px;
    background: white;
    border-radius: 10px;
    border-left: 3px solid {CARD_COLORS['primary']};
    transition: all 0.3s ease;
}}

.card-point:hover {{
    transform: translateX(4px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
}}

.point-number {{
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, {CARD_COLORS['primary']}, {CARD_COLORS['secondary']});
    color: white;
    font-size: 12px;
    font-weight: 700;
    border-radius: 50%;
}}

.point-text {{
    flex: 1;
    font-size: 14px;
    color: #4B5563;
    line-height: 1.6;
}}

/* 标签 */
.card-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 20px;
}}

.card-tag {{
    display: inline-block;
    padding: 6px 12px;
    background: rgba(37, 99, 235, 0.08);
    color: {CARD_COLORS['primary']};
    font-size: 12px;
    font-weight: 500;
    border-radius: 6px;
    border: 1px solid rgba(37, 99, 235, 0.15);
}}

/* 提示 */
.card-prompt {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 16px;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.1));
    border-radius: 10px;
    margin-bottom: 20px;
    border: 1px dashed rgba(245, 158, 11, 0.3);
}}

.card-prompt span {{
    flex: 1;
    font-size: 14px;
    color: #92400E;
    font-weight: 500;
}}

/* 按钮区 */
.card-actions {{
    display: flex;
    gap: 12px;
}}

.action-btn {{
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    border: none;
}}

.action-btn-primary {{
    background: linear-gradient(135deg, {CARD_COLORS['primary']}, {CARD_COLORS['secondary']});
    color: white;
}}

.action-btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}}

.action-btn-secondary {{
    background: white;
    color: {CARD_COLORS['primary']};
    border: 2px solid {CARD_COLORS['primary']};
}}

.action-btn-secondary:hover {{
    background: rgba(37, 99, 235, 0.05);
    transform: translateY(-2px);
}}

/* Toast提示 */
.success-toast {{
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%) translateY(-100px);
    padding: 12px 24px;
    background: #10B981;
    color: white;
    font-size: 14px;
    font-weight: 600;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    opacity: 0;
    transition: all 0.3s ease;
    z-index: 1000;
}}

.success-toast.show {{
    transform: translateX(-50%) translateY(0);
    opacity: 1;
}}

/* 响应式设计 */
@media (max-width: 768px) {{
    .article-summary-card {{
        margin: 20px 0;
        padding: 20px;
        border-radius: 12px;
    }}

    .card-title {{
        font-size: 20px;
    }}

    .card-summary {{
        font-size: 14px;
    }}

    .card-point {{
        padding: 12px;
    }}

    .card-actions {{
        flex-direction: column;
    }}

    .action-btn {{
        width: 100%;
    }}
}}

@media (max-width: 480px) {{
    .article-summary-card {{
        padding: 16px;
    }}

    .card-header {{
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }}

    .card-title {{
        font-size: 18px;
    }}

    .point-text {{
        font-size: 13px;
    }}
}}
</style>

<script>
// 复制链接功能
function copyArticleLink(url) {{
    navigator.clipboard.writeText(url).then(() => {{
        showToast('复制成功！');
    }}).catch(() => {{
        // 降级方案
        const input = document.createElement('input');
        input.value = url;
        document.body.appendChild(input);
        input.select();
        document.execCommand('copy');
        document.body.removeChild(input);
        showToast('复制成功！');
    }});
}}

// 显示提示
function showToast(message) {{
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {{
        toast.classList.remove('show');
    }}, 2000);
}}

// 导出图片功能
function exportCardImage() {{
    const card = document.getElementById('summaryCard');

    // 方案1: 使用 html2canvas（需要引入库）
    if (typeof html2canvas !== 'undefined') {{
        html2canvas(card, {{
            backgroundColor: '#ffffff',
            scale: 2, // 提高清晰度
            useCORS: true,
            logging: false
        }}).then(canvas => {{
            const link = document.createElement('a');
            link.download = '文章总结.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
            showToast('导出成功！');
        }}).catch(err => {{
            console.error('导出失败:', err);
            showFallbackGuide();
        }});
    }} else {{
        // 方案2: 提供截图指导
        showFallbackGuide();
    }}
}}

// 降级方案：显示截图指导
function showFallbackGuide() {{
    alert('📸 导出图片功能说明：\\n\\n' +
          '方式1（推荐）：\\n' +
          '使用系统截图工具（Mac: Cmd+Shift+4，Windows: Win+Shift+S）截取卡片区域\\n\\n' +
          '方式2：\\n' +
          '安装 html2canvas 库后可一键导出\\n' +
          'npm install html2canvas');
}}
</script>
'''
    return html


def insert_share_card(file_path, share_url=None, preview=False):
    """
    在文章末尾插入分享卡片

    Args:
        file_path: 文章文件路径
        share_url: 分享链接（可选，默认使用当前页面URL）
        preview: 是否只预览不写入
    """
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return False

    # 读取文章内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已有分享卡片
    if '<!-- 技术文章总结卡片 -->' in content or 'article-summary-card' in content:
        print(f"⚠️  文章已包含总结卡片，跳过插入")
        return False

    # 提取信息
    title = extract_title(content)
    summary = extract_summary(content)
    key_points = extract_key_points(content)
    tags = extract_tags(content)

    # 默认分享链接（提示用户修改）
    if not share_url:
        share_url = "https://your-book-url.com"

    # 生成HTML
    html = generate_share_card_html(title, summary, key_points, tags, share_url)

    # 插入到文章末尾
    new_content = content.rstrip() + '\n\n' + html + '\n'

    if preview:
        print("=" * 60)
        print("📝 总结卡片预览")
        print("=" * 60)
        print()
        print(html)
        print()
        print("=" * 60)
        print(f"💡 提示: 实际插入时请修改分享链接")
        print("=" * 60)
        return True

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ 总结卡片已插入到: {file_path}")
    print()
    print(f"📌 标题: {title}")
    print(f"📝 摘要: {summary[:50]}...")
    print(f"💡 核心要点: {len(key_points)} 条")
    print(f"🏷️  标签: {', '.join(tags)}")
    print()
    print("💡 功能说明:")
    print("   1. 复制链接：点击按钮复制文章链接")
    print("   2. 导出图片：可截图或安装 html2canvas 一键导出")
    print()
    print("⚙️  更新分享链接:")
    print(f"   python scripts/generate_share_card.py --input {file_path.name} --share-url 'YOUR_URL' --update")
    print()

    return True


def update_share_url(file_path, new_url):
    """更新已有卡片的分享链接"""
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换分享链接（在JavaScript函数中）
    import re
    pattern = r"copyArticleLink\('([^']*)'\)"
    new_pattern = f"copyArticleLink('{new_url}')"

    if re.search(pattern, content):
        content = re.sub(pattern, new_pattern, content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 分享链接已更新: {new_url}")
        return True
    else:
        print(f"⚠️  未找到可更新的分享链接")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='生成技术文章总结卡片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 在文章末尾插入总结卡片
  python generate_share_card.py --input chapter01.md

  # 指定分享链接
  python generate_share_card.py --input chapter01.md --share-url "https://example.com"

  # 预览卡片内容（不写入文件）
  python generate_share_card.py --input chapter01.md --preview

  # 生成独立的HTML预览文件（推荐）
  python generate_share_card.py --input chapter01.md --html-output card.html

  # 生成包含文章内容的HTML预览
  python generate_share_card.py --input chapter01.md --html-output card.html --include-article

  # 导出卡片为PNG图片（需要Playwright）
  python generate_share_card.py --input chapter01.md --export-image card.png

  # 更新已有卡片的分享链接
  python generate_share_card.py --input chapter01.md --share-url "https://example.com" --update

功能说明:
  - 复制链接：点击按钮复制文章链接到剪贴板
  - 导出图片：在浏览器中点击按钮导出，或使用--export-image直接生成图片
        '''
    )

    parser.add_argument('--input', required=True, help='文章文件路径')
    parser.add_argument('--share-url', help='分享链接（可选，默认使用占位符）')
    parser.add_argument('--preview', action='store_true', help='预览卡片内容（不写入文件）')
    parser.add_argument('--html-output', help='生成独立的HTML预览文件')
    parser.add_argument('--include-article', action='store_true', help='HTML预览中包含文章内容')
    parser.add_argument('--export-image', help='将卡片导出为PNG图片（需要Playwright）')
    parser.add_argument('--update', action='store_true', help='更新已有卡片的分享链接')

    args = parser.parse_args()

    # 导出图片模式
    if args.export_image:
        export_card_to_image(args.input, args.export_image, args.share_url)
        return

    # 生成HTML预览模式
    if args.html_output:
        generate_html_preview(args.input, args.html_output, args.share_url, args.include_article)
        return

    # 更新模式
    if args.update:
        if not args.share_url:
            print("❌ 错误: --update 模式需要提供 --share-url")
            return
        update_share_url(args.input, args.share_url)
        return

    # 默认：插入到文章末尾
    insert_share_card(args.input, args.share_url, args.preview)


if __name__ == '__main__':
    main()
