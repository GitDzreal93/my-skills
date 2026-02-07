#!/usr/bin/env python3
"""
生成 Echart 可视化图表的 HTML 文件

支持的图表类型:
- bar: 柱状图
- line: 折线图
- pie: 饼图
- scatter: 散点图
- radar: 雷达图
"""

import json
import argparse
import subprocess
import tempfile
from pathlib import Path


def generate_bar_chart(data, title, output_path):
    """生成柱状图"""
    x_axis = data.get('xAxis', [])
    series = data.get('series', [])
    
    series_data = []
    for s in series:
        series_data.append({
            'name': s.get('name', ''),
            'type': 'bar',
            'data': s.get('data', [])
        })
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; background: #fff; }}
        #main {{ width: 100%; height: 600px; }}
    </style>
</head>
<body>
    <div id="main"></div>
    <script type="text/javascript">
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option = {{
            title: {{
                text: '{title}',
                left: 'center',
                textStyle: {{
                    fontSize: 20,
                    fontWeight: 'bold'
                }}
            }},
            tooltip: {{
                trigger: 'axis',
                axisPointer: {{
                    type: 'shadow'
                }}
            }},
            legend: {{
                top: '10%',
                data: {json.dumps([s['name'] for s in series_data])}
            }},
            grid: {{
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            }},
            xAxis: {{
                type: 'category',
                data: {json.dumps(x_axis)}
            }},
            yAxis: {{
                type: 'value'
            }},
            series: {json.dumps(series_data)}
        }};
        
        myChart.setOption(option);
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ 柱状图已生成: {output_path}")


def generate_line_chart(data, title, output_path):
    """生成折线图"""
    x_axis = data.get('xAxis', [])
    series = data.get('series', [])
    
    series_data = []
    for s in series:
        series_data.append({
            'name': s.get('name', ''),
            'type': 'line',
            'data': s.get('data', []),
            'smooth': True
        })
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; background: #fff; }}
        #main {{ width: 100%; height: 600px; }}
    </style>
</head>
<body>
    <div id="main"></div>
    <script type="text/javascript">
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option = {{
            title: {{
                text: '{title}',
                left: 'center'
            }},
            tooltip: {{
                trigger: 'axis'
            }},
            legend: {{
                top: '10%',
                data: {json.dumps([s['name'] for s in series_data])}
            }},
            grid: {{
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            }},
            xAxis: {{
                type: 'category',
                data: {json.dumps(x_axis)}
            }},
            yAxis: {{
                type: 'value'
            }},
            series: {json.dumps(series_data)}
        }};
        
        myChart.setOption(option);
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ 折线图已生成: {output_path}")


def generate_pie_chart(data, title, output_path):
    """生成饼图"""
    pie_data = data.get('data', [])

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; background: #fff; }}
        #main {{ width: 100%; height: 600px; }}
    </style>
</head>
<body>
    <div id="main"></div>
    <script type="text/javascript">
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option = {{
            title: {{
                text: '{title}',
                left: 'center'
            }},
            tooltip: {{
                trigger: 'item',
                formatter: '{{a}} <br/>{{b}}: {{c}} ({{d}}%)'
            }},
            legend: {{
                orient: 'vertical',
                left: 'left'
            }},
            series: [
                {{
                    name: '{title}',
                    type: 'pie',
                    radius: '55%',
                    center: ['50%', '60%'],
                    data: {json.dumps(pie_data)},
                    emphasis: {{
                        itemStyle: {{
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }}
                    }}
                }}
            ]
        }};

        myChart.setOption(option);
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ 饼图已生成: {output_path}")


def generate_scatter_chart(data, title, output_path):
    """生成散点图"""
    series = data.get('series', [])

    series_data = []
    for s in series:
        series_data.append({
            'name': s.get('name', ''),
            'type': 'scatter',
            'data': s.get('data', []),
            'symbolSize': 10
        })

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; background: #fff; }}
        #main {{ width: 100%; height: 600px; }}
    </style>
</head>
<body>
    <div id="main"></div>
    <script type="text/javascript">
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option = {{
            title: {{
                text: '{title}',
                left: 'center'
            }},
            tooltip: {{
                trigger: 'item',
                formatter: function (params) {{
                    return params.seriesName + '<br/>' +
                           'X: ' + params.value[0] + '<br/>' +
                           'Y: ' + params.value[1];
                }}
            }},
            legend: {{
                top: '10%',
                data: {json.dumps([s['name'] for s in series_data])}
            }},
            grid: {{
                left: '3%',
                right: '7%',
                bottom: '3%',
                containLabel: true
            }},
            xAxis: {{
                type: 'value',
                scale: true,
                name: 'X轴'
            }},
            yAxis: {{
                type: 'value',
                scale: true,
                name: 'Y轴'
            }},
            series: {json.dumps(series_data)}
        }};

        myChart.setOption(option);
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ 散点图已生成: {output_path}")


def generate_radar_chart(data, title, output_path):
    """生成雷达图"""
    indicators = data.get('indicators', [])
    series = data.get('series', [])

    series_data = []
    for s in series:
        series_data.append({
            'name': s.get('name', ''),
            'value': s.get('data', []),
            'type': 'radar'
        })

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; background: #fff; }}
        #main {{ width: 100%; height: 600px; }}
    </style>
</head>
<body>
    <div id="main"></div>
    <script type="text/javascript">
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option = {{
            title: {{
                text: '{title}',
                left: 'center'
            }},
            tooltip: {{
                trigger: 'item'
            }},
            legend: {{
                top: '10%',
                data: {json.dumps([s['name'] for s in series_data])}
            }},
            radar: {{
                indicator: {json.dumps(indicators)}
            }},
            series: [{{
                name: '{title}',
                type: 'radar',
                data: {json.dumps(series_data)}
            }}]
        }};

        myChart.setOption(option);
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ 雷达图已生成: {output_path}")


def export_html_to_image(html_path, output_path):
    """使用Playwright将HTML导出为JPG图片"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("⚠️  未安装 playwright，跳过图片导出")
        print("💡 安装方法: pip install playwright && playwright install chromium")
        return False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1200, 'height': 700})
            page.goto(f'file://{html_path}')

            # 等待图表加载完成
            page.wait_for_selector('#main', timeout=5000)

            # 额外等待确保图表渲染完成
            import time
            time.sleep(1)

            # 截图
            page.screenshot(path=output_path, full_page=False)

            browser.close()

        print(f"✅ 图片已导出: {output_path}")
        return True

    except Exception as e:
        print(f"⚠️  导出图片失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='生成Echart可视化图表')
    parser.add_argument('--type', required=True, choices=['bar', 'line', 'pie', 'scatter', 'radar'],
                        help='图表类型')
    parser.add_argument('--data', required=True, help='数据JSON文件路径')
    parser.add_argument('--title', default='图表', help='图表标题')
    parser.add_argument('--output', required=True, help='输出HTML文件路径')
    parser.add_argument('--export-jpg', action='store_true', help='同时导出为JPG图片（需要Playwright）')

    args = parser.parse_args()

    # 读取数据
    with open(args.data, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 根据类型生成图表
    if args.type == 'bar':
        generate_bar_chart(data, args.title, args.output)
    elif args.type == 'line':
        generate_line_chart(data, args.title, args.output)
    elif args.type == 'pie':
        generate_pie_chart(data, args.title, args.output)
    elif args.type == 'scatter':
        generate_scatter_chart(data, args.title, args.output)
    elif args.type == 'radar':
        generate_radar_chart(data, args.title, args.output)
    else:
        print(f"⚠️ 暂未实现 {args.type} 类型图表")
        return

    # 如果需要，导出为JPG
    if args.export_jpg:
        jpg_path = str(Path(args.output)).replace('.html', '.jpg')
        export_html_to_image(args.output, jpg_path)


if __name__ == '__main__':
    main()
