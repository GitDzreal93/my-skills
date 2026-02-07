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


def main():
    parser = argparse.ArgumentParser(description='生成Echart可视化图表')
    parser.add_argument('--type', required=True, choices=['bar', 'line', 'pie', 'scatter', 'radar'],
                        help='图表类型')
    parser.add_argument('--data', required=True, help='数据JSON文件路径')
    parser.add_argument('--title', default='图表', help='图表标题')
    parser.add_argument('--output', required=True, help='输出HTML文件路径')
    
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
    else:
        print(f"⚠️ 暂未实现 {args.type} 类型图表")


if __name__ == '__main__':
    main()
