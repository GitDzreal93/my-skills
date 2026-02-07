# 脚本使用指南

本文档介绍技术书籍写作系统中所有辅助脚本的详细使用方法。

## 脚本清单

| 脚本名 | 功能 | 依赖库 |
|--------|------|--------|
| generate_xmind.py | Markdown转XMind | xmind |
| generate_echart.py | 生成Echart图表HTML | 无 |
| html_to_image.py | HTML转图片 | selenium, pillow |
| generate_ai_image.py | 调用即梦AI生成图片 | requests |
| proofreading.py | 全书质量校对 | 无 |
| validate_code.py | 验证代码示例 | ast, subprocess |
| translate_book.py | 全书翻译 | 需API配置 |

---

## 1. generate_xmind.py - 思维导图生成

### 功能
将Markdown大纲转换为XMind思维导图文件。

### 安装依赖
```bash
pip install xmind
```

### 使用方法
```bash
python scripts/generate_xmind.py \
  --input "书籍大纲.md" \
  --output "知识体系.xmind" \
  --theme "classic|modern"
```

### 参数说明
- `--input`: 输入的Markdown文件路径
- `--output`: 输出的XMind文件路径
- `--theme`: 主题风格（可选，默认classic）

### 输入格式示例
```markdown
# 机器学习入门
## 第一部分：基础准备
### 第1章：机器学习是什么
- 监督学习
- 无监督学习
- 强化学习
### 第2章：环境搭建
## 第二部分：核心算法
```

---

## 2. generate_echart.py - Echart图表生成

### 功能
生成Echart可视化图表的HTML文件。

### 使用方法
```bash
python scripts/generate_echart.py \
  --type "bar" \
  --data "data.json" \
  --title "性能对比" \
  --output "chart.html"
```

### 支持的图表类型
- `bar`: 柱状图
- `line`: 折线图
- `pie`: 饼图
- `scatter`: 散点图
- `radar`: 雷达图

### 数据格式示例（data.json）

**柱状图**:
```json
{
  "xAxis": ["算法A", "算法B", "算法C"],
  "series": [
    {
      "name": "准确率",
      "data": [0.85, 0.90, 0.88]
    },
    {
      "name": "速度(ms)",
      "data": [120, 80, 100]
    }
  ]
}
```

**饼图**:
```json
{
  "data": [
    {"name": "监督学习", "value": 45},
    {"name": "无监督学习", "value": 30},
    {"name": "强化学习", "value": 25}
  ]
}
```

---

## 3. html_to_image.py - HTML转图片

### 功能
将HTML文件转换为JPG或PNG图片。

### 安装依赖
```bash
pip install selenium pillow
# 还需要安装Chrome浏览器和ChromeDriver
```

### 使用方法
```bash
python scripts/html_to_image.py \
  --input "chart.html" \
  --output "chart.jpg" \
  --width 1200 \
  --height 800 \
  --format "jpg"
```

### 参数说明
- `--input`: 输入HTML文件
- `--output`: 输出图片路径
- `--width`: 图片宽度（默认1200）
- `--height`: 图片高度（默认800）
- `--format`: 图片格式，jpg或png（默认jpg）

---

## 4. generate_ai_image.py - AI插图生成

### 功能
调用火山引擎即梦AI生成插图。

### 前提条件
用户必须提供：
- ACCESS_KEY
- SECRET_KEY

### 使用方法
```bash
python scripts/generate_ai_image.py \
  --prompt "一个现代化的数据中心，蓝色科技光线" \
  --ak "YOUR_ACCESS_KEY" \
  --sk "YOUR_SECRET_KEY" \
  --output "data_center.jpg" \
  --style "realistic"
```

### 参数说明
- `--prompt`: 图片描述（中文或英文）
- `--ak`: 火山引擎ACCESS_KEY
- `--sk`: 火山引擎SECRET_KEY
- `--output`: 输出图片路径
- `--style`: 风格（realistic/anime/oil_painting等）
- `--width`: 图片宽度（默认1024）
- `--height`: 图片高度（默认1024）

### 提示词建议

**技术概念插图**:
```
"机器学习流程示意图，数据输入、模型训练、预测输出，简洁扁平化风格"
```

**场景插图**:
```
"现代化的服务器机房，整齐的服务器机架，蓝色LED灯光，科技感"
```

**抽象概念**:
```
"神经网络结构，节点和连接，发光效果，深色背景，科技风格"
```

---

## 5. proofreading.py - 质量校对

### 功能
全书内容质量自动化检查。

### 使用方法
```bash
python scripts/proofreading.py \
  --input "chapters/" \
  --output "校对报告.md" \
  --checks "all"
```

### 检查项目
- `structure`: 章节结构完整性
- `code`: 代码语法检查
- `images`: 插图引用检查
- `language`: 语言风格检查
- `all`: 全部检查（默认）

### 指定特定检查
```bash
python scripts/proofreading.py \
  --input "chapters/" \
  --checks "structure,code"
```

### 输出报告格式
```markdown
# 校对报告

生成时间: 2026-02-06 15:30:00

## 整体统计
- 总章节数: 16
- 检查通过: 14
- 需要修改: 2
- 严重问题: 0

## 问题详情

### 第3章: 数据预处理
❌ 缺少本章导读部分
⚠️ 代码示例缺少import pandas
✅ 插图引用正确

### 第7章: 集成学习
⚠️ 建议添加对比表格
⚠️ 测试题数量不足（仅8题）

## 修改建议
1. 补充第3章的本章导读
2. 在第3章代码开头添加 import pandas as pd
3. 第7章增加算法对比表
4. 第7章补充2道测试题
```

---

## 6. validate_code.py - 代码验证

### 功能
验证书中所有代码示例的可运行性。

### 支持语言
- Python
- JavaScript/TypeScript
- Go
- Java

### 使用方法
```bash
python scripts/validate_code.py \
  --chapters "chapters/" \
  --language "python" \
  --fix-imports
```

### 参数说明
- `--chapters`: 章节目录路径
- `--language`: 编程语言
- `--fix-imports`: 自动修复缺失的import（可选）
- `--extract`: 提取代码到独立文件（可选）

### 工作原理
1. 扫描所有章节的代码块
2. 提取代码并保存为临时文件
3. 使用对应语言的解释器/编译器检查语法
4. 报告错误和警告

### 输出示例
```
✅ 第1章: 5个代码块全部通过
✅ 第2章: 3个代码块全部通过
❌ 第3章: 发现2个问题
   - example_01.py:15 - NameError: 'pd' is not defined
   - example_02.py:8 - SyntaxError: invalid syntax
⚠️  第4章: 1个警告
   - example_03.py:20 - 未使用的变量 'result'
```

---

## 7. translate_book.py - 全书翻译

### 功能
将整本书翻译为目标语言，保持格式和代码不变。

### 使用方法
```bash
python scripts/translate_book.py \
  --input "chapters/" \
  --output "translations/en/" \
  --target-lang "en" \
  --keep-terms "术语表.json" \
  --translate-comments
```

### 参数说明
- `--input`: 原文章节目录
- `--output`: 翻译输出目录
- `--target-lang`: 目标语言代码（en/ja/ko等）
- `--keep-terms`: 术语表文件（JSON格式）
- `--translate-comments`: 是否翻译代码注释

### 术语表格式（glossary.json）
```json
{
  "机器学习": "Machine Learning",
  "深度学习": "Deep Learning",
  "神经网络": "Neural Network",
  "监督学习": "Supervised Learning"
}
```

### 翻译规则
- ✅ 翻译正文内容
- ✅ 翻译代码注释（如果指定）
- ✅ 翻译表格内容
- ❌ 不翻译代码本身
- ❌ 不翻译变量名和函数名
- ❌ 不翻译URL和文件路径

---

## 常见问题

### Q: 脚本运行报错找不到模块？
A: 安装对应的依赖库：
```bash
pip install xmind selenium pillow requests
```

### Q: html_to_image.py 报错找不到ChromeDriver？
A: 安装ChromeDriver：
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver

# 或手动下载并添加到PATH
```

### Q: 即梦AI生成图片失败？
A: 检查：
1. AK/SK是否正确
2. 是否有网络连接
3. 账户是否有余额
4. 提示词是否符合规范

### Q: 校对报告的问题如何批量修复？
A: 某些问题支持自动修复：
```bash
python scripts/proofreading.py \
  --input "chapters/" \
  --auto-fix
```

---

## 高级用法

### 批量处理章节
```bash
# 批量生成所有章节的插图
for chapter in chapters/chapter*.md; do
  python scripts/generate_echart.py \
    --data "data/$(basename $chapter .md).json" \
    --output "images/$(basename $chapter .md)_chart.html"
done
```

### 自定义校对规则
创建 `custom_rules.py`:
```python
def check_custom_rule(chapter_content):
    # 自定义检查逻辑
    if "TODO" in chapter_content:
        return "发现未完成的TODO标记"
    return None
```

然后在校对时加载：
```bash
python scripts/proofreading.py \
  --input "chapters/" \
  --custom-rules "custom_rules.py"
```

---

## 更新日志

- v1.0 (2026-02-06): 初始版本，包含所有基础脚本
