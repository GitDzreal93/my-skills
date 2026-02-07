#!/usr/bin/env python3
"""
调用火山引擎即梦AI 4.0生成插图

API文档: https://www.volcengine.com/docs/85621/1817045

新版即梦AI 4.0特性：
- 支持自定义图片尺寸（包括16:9横版）
- 异步任务模式（提交任务 → 查询结果）
- req_key: jimeng_t2i_v40

配置方式（按优先级排序）:
1. 命令行参数 --ak --sk
2. 环境变量 VOLCENGINE_AK / VOLCENGINE_SK
3. 配置文件 ~/.tech-book-writer/config.json
"""

import argparse
import json
import os
import sys
import time
import base64
from pathlib import Path


def get_credentials_from_env():
    """从环境变量读取AK/SK"""
    ak = os.environ.get('VOLCENGINE_AK')
    sk = os.environ.get('VOLCENGINE_SK')
    if ak and sk:
        return ak, sk
    return None, None


def get_credentials_from_config():
    """从配置文件读取AK/SK"""
    config_path = Path.home() / '.tech-book-writer' / 'config.json'
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('volcengine_ak'), config.get('volcengine_sk')
        except Exception as e:
            print(f"⚠️  读取配置文件失败: {e}")
    return None, None


def get_shell_config_path():
    """获取用户的shell配置文件路径"""
    # 检测用户使用的shell
    shell = os.environ.get('SHELL', '')
    if 'zsh' in shell:
        return Path.home() / '.zshrc'
    elif 'bash' in shell:
        return Path.home() / '.bashrc'
    else:
        # 默认使用 .zshrc (macOS默认)
        return Path.home() / '.zshrc'


def save_to_shell_config(ak, sk):
    """保存AK/SK到shell配置文件"""
    config_path = get_shell_config_path()
    export_lines = f'''
# 火山引擎即梦AI AK/SK
export VOLCENGINE_AK="{ak}"
export VOLCENGINE_SK="{sk}"
'''

    try:
        # 读取现有内容
        existing_content = ""
        if config_path.exists():
            with open(config_path, 'r') as f:
                existing_content = f.read()

        # 检查是否已经配置过
        if 'VOLCENGINE_AK' in existing_content:
            print(f"⚠️  {config_path} 中已存在 VOLCENGINE_AK 配置")
            return False

        # 追加配置
        with open(config_path, 'a') as f:
            f.write(export_lines)

        return True
    except Exception as e:
        print(f"❌ 写入shell配置文件失败: {e}")
        return False


def setup_credentials():
    """交互式配置AK/SK"""
    print("=" * 60)
    print("火山引擎即梦AI 4.0 AK/SK 配置")
    print("=" * 60)
    print()
    print("请访问以下地址获取您的 AK/SK:")
    print("https://console.volcengine.com/iam/keymanage")
    print()
    print("说明: 即梦AI 4.0 支持自定义图片尺寸（包括16:9横版）")
    print()

    ak = input("请输入 Access Key (AK): ").strip()
    if not ak:
        print("❌ AK 不能为空")
        return False

    sk = input("请输入 Secret Key (SK): ").strip()
    if not sk:
        print("❌ SK 不能为空")
        return False

    # 创建配置目录
    config_dir = Path.home() / '.tech-book-writer'
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / 'config.json'

    # 保存配置到文件（作为备份）
    config = {
        'volcengine_ak': ak,
        'volcengine_sk': sk
    }

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print()
    print(f"✅ 配置已保存到: {config_path}")

    # 询问是否保存到shell配置文件
    print()
    save_to_shell = input("是否将AK/SK保存到shell配置文件(~/.zshrc或~/.bashrc)? [y/N]: ").strip().lower()
    if save_to_shell == 'y' or save_to_shell == 'yes':
        shell_config_path = get_shell_config_path()
        if save_to_shell_config(ak, sk):
            print(f"✅ 已添加到shell配置文件: {shell_config_path}")
            print()
            print("📝 请运行以下命令使配置生效:")
            print(f"   source {shell_config_path}")
        else:
            print(f"⚠️  保存到shell配置文件失败，仅使用配置文件方式")

    print()
    print("📝 后续使用时，脚本会自动读取配置。")
    print("💡 提示: 配置文件仅保存在本地，请勿泄露或提交到版本控制系统。")
    print()
    return True


class JimengAI40Client:
    """即梦AI 4.0客户端（异步API）"""

    def __init__(self, ak, sk):
        """
        初始化客户端

        Args:
            ak: 火山引擎 Access Key
            sk: 火山引擎 Secret Key
        """
        from volcengine.visual.VisualService import VisualService

        self.client = VisualService()
        self.client.set_ak(ak)
        self.client.set_sk(sk)
        self.req_key = "jimeng_t2i_v40"  # 即梦AI 4.0

    def submit_task(self, prompt, width=None, height=None, scale=0.5, force_single=True):
        """
        提交图片生成任务

        Args:
            prompt: 图片描述（中英文均可，最长800字符）
            width: 图片宽度（与height同时传入才生效）
            height: 图片高度（与width同时传入才生效）
            scale: 文本描述权重 (0-1，默认0.5)
            force_single: 是否强制生成单图（默认True）

        Returns:
            str: 任务ID，失败返回None
        """
        form = {
            "req_key": self.req_key,
            "prompt": prompt,
            "scale": scale,
            "force_single": force_single,
        }

        # 添加尺寸参数（必须同时传入width和height）
        if width and height:
            form["width"] = width
            form["height"] = height
            print(f"   尺寸: {width}x{height} ({width/height:.2f}:1)")

        try:
            print(f"🎨 正在提交任务...")
            print(f"   算法: {self.req_key}")
            print(f"   提示词: {prompt}")
            print(f"   文本权重: {scale}")
            print(f"   强制单图: {force_single}")

            # 使用异步提交接口
            resp = self.client.cv_sync2async_submit_task(form)

            if resp.get('code') == 10000 and 'data' in resp:
                task_id = resp['data'].get('task_id')
                print(f"✅ 任务已提交: {task_id}")
                return task_id
            else:
                print(f"❌ 提交任务失败: {resp.get('message', 'Unknown error')}")
                print(f"   响应详情: {resp}")
                return None

        except Exception as e:
            print(f"❌ 发生异常: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_result(self, task_id, retry_interval=3, max_wait=120):
        """
        查询任务结果

        Args:
            task_id: 任务ID
            retry_interval: 重试间隔（秒）
            max_wait: 最大等待时间（秒）

        Returns:
            dict: API响应，包含base64编码的图片数据
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                form = {
                    "req_key": self.req_key,
                    "task_id": task_id,
                }

                resp = self.client.cv_sync2async_get_result(form)

                if resp.get('code') == 10000 and 'data' in resp:
                    data = resp['data']
                    status = data.get('status')

                    if status == 'done':
                        print(f"✅ 任务完成")
                        return resp
                    elif status in ['in_queue', 'generating']:
                        elapsed = int(time.time() - start_time)
                        print(f"⏳ 任务处理中... ({elapsed}s)", end='\r')
                        time.sleep(retry_interval)
                    else:
                        print(f"\n❌ 任务状态异常: {status}")
                        return None
                else:
                    print(f"\n❌ 查询失败: {resp.get('message', 'Unknown error')}")
                    return None

            except Exception as e:
                print(f"\n❌ 查询异常: {e}")
                import traceback
                traceback.print_exc()
                return None

        print(f"\n❌ 超时: 任务未在 {max_wait} 秒内完成")
        return None

    def generate_image(self, prompt, width=None, height=None, scale=0.5, force_single=True, retry_interval=3, max_wait=120):
        """
        生成图片（提交任务 + 查询结果）

        Args:
            prompt: 图片描述
            width: 图片宽度
            height: 图片高度
            scale: 文本权重
            force_single: 强制单图
            retry_interval: 查询重试间隔
            max_wait: 最大等待时间

        Returns:
            dict: API响应
        """
        # 提交任务
        task_id = self.submit_task(prompt, width, height, scale, force_single)
        if not task_id:
            return None

        # 查询结果
        resp = self.get_result(task_id, retry_interval, max_wait)
        return resp

    def save_image(self, resp, output_path):
        """
        从API响应中保存图片

        Args:
            resp: API响应
            output_path: 输出路径

        Returns:
            bool: 是否成功
        """
        try:
            if not resp or 'data' not in resp:
                print("❌ 响应中没有图片数据")
                return False

            data = resp['data']

            # 优先使用image_urls（如果配置了return_url）
            if 'image_urls' in data and data['image_urls']:
                import requests
                img_url = data['image_urls'][0]
                print(f"📥 下载图片: {img_url}")

                response = requests.get(img_url, timeout=30)
                if response.status_code == 200:
                    img_data = response.content
                else:
                    print(f"⚠️  下载失败，尝试使用base64数据")
                    raise Exception("Download failed")

            # 使用base64数据
            elif 'binary_data_base64' in data and data['binary_data_base64']:
                img_base64 = data['binary_data_base64'][0]
                img_data = base64.b64decode(img_base64)
            else:
                print("❌ 响应中没有图片数据")
                return False

            # 保存图片
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(img_data)

            print(f"✅ 图片已保存: {output_path}")
            print(f"   文件大小: {len(img_data)} 字节")

            return True

        except Exception as e:
            print(f"❌ 保存图片失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    # 预设尺寸
    PRESET_SIZES = {
        '1:1': [
            (1024, 1024, '1K正方形'),
            (2048, 2048, '2K正方形'),
            (4096, 4096, '4K正方形'),
        ],
        '4:3': [
            (2304, 1728, '2K 4:3'),
            (4694, 3520, '4K 4:3'),
        ],
        '3:2': [
            (2496, 1664, '2K 3:2'),
            (4992, 3328, '4K 3:2'),
        ],
        '16:9': [
            (2560, 1440, '2K 16:9'),
            (5404, 3040, '4K 16:9'),
        ],
        '21:9': [
            (3024, 1296, '2K 21:9'),
            (6198, 2656, '4K 21:9'),
        ],
    }

    parser = argparse.ArgumentParser(
        description='使用火山引擎即梦AI 4.0生成插图（支持自定义尺寸）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
配置方式（按优先级）:
  1. 命令行参数 --ak --sk
  2. 环境变量 VOLCENGINE_AK / VOLCENGINE_SK
  3. 配置文件 ~/.tech-book-writer/config.json

获取AK/SK: https://console.volcengine.com/iam/keymanage

API文档: https://www.volcengine.com/docs/85621/1817045

预设尺寸:
  1:1   - 1024x1024, 2048x2048, 4096x4096 (正方形)
  4:3   - 2304x1728, 4694x3520
  3:2   - 2496x1664, 4992x3328
  16:9  - 2560x1440, 5404x3040 (推荐横版)
  21:9  - 3024x1296, 6198x2656

示例:
  # 交互式配置
  python generate_ai_image.py --setup

  # 生成16:9横版图片（推荐）
  python generate_ai_image.py --prompt "山水画" --output landscape.jpg --preset "16:9"

  # 生成2K 16:9图片
  python generate_ai_image.py --prompt "山水画" --output landscape.jpg --width 2560 --height 1440

  # 生成4K 16:9图片
  python generate_ai_image.py --prompt "山水画" --output landscape.jpg --width 5404 --height 3040

  # 使用预设尺寸
  python generate_ai_image.py --prompt "机器学习" --output ml.jpg --preset "16:9" --size 2k

  # 自定义尺寸
  python generate_ai_image.py --prompt "代码" --output code.jpg --width 1920 --height 1080
        '''
    )
    parser.add_argument('--prompt', help='图片描述（中文或英文，最长800字符）')
    parser.add_argument('--ak', help='火山引擎Access Key')
    parser.add_argument('--sk', help='火山引擎Secret Key')
    parser.add_argument('--output', help='输出图片路径')
    parser.add_argument('--width', type=int, help='图片宽度（与height同时使用）')
    parser.add_argument('--height', type=int, help='图片高度（与width同时使用）')
    parser.add_argument('--preset', choices=['1:1', '4:3', '3:2', '16:9', '21:9'],
                        help='预设宽高比（推荐16:9）')
    parser.add_argument('--size', choices=['1k', '2k', '4k'], default='2k',
                        help='预设尺寸（与--preset配合使用，默认2k）')
    parser.add_argument('--scale', type=float, default=0.5,
                        help='文本描述权重 (0.0-1.0，默认: 0.5)')
    parser.add_argument('--timeout', type=int, default=120,
                        help='最大等待时间（秒，默认120）')
    parser.add_argument('--setup', action='store_true', help='交互式配置AK/SK')

    args = parser.parse_args()

    # 处理 setup 命令
    if args.setup:
        setup_credentials()
        return

    # 验证必需参数
    if not args.prompt or not args.output:
        parser.print_help()
        print()
        print("❌ 错误: --prompt 和 --output 是必需参数")
        print()
        print("💡 首次使用请先配置AK/SK:")
        print("   python generate_ai_image.py --setup")
        print()
        print("   或设置环境变量:")
        print("   export VOLCENGINE_AK='your_ak'")
        print("   export VOLCENGINE_SK='your_sk'")
        sys.exit(1)

    # 获取AK/SK（命令行参数 > 环境变量 > 配置文件）
    ak, sk = args.ak, args.sk

    if not ak or not sk:
        ak, sk = get_credentials_from_env()

    if not ak or not sk:
        ak, sk = get_credentials_from_config()

    if not ak or not sk:
        print("❌ 错误: 未找到 AK/SK")
        print()
        print("💡 请通过以下方式配置（任选一种）:")
        print()
        print("   方式1: 交互式配置（推荐）")
        print("   python generate_ai_image.py --setup")
        print()
        print("   方式2: 设置环境变量")
        print("   export VOLCENGINE_AK='your_ak'")
        print("   export VOLCENGINE_SK='your_sk'")
        print()
        print("   方式3: 使用命令行参数")
        print("   python generate_ai_image.py --ak YOUR_AK --sk YOUR_SK ...")
        print()
        print("📖 获取AK/SK: https://console.volcengine.com/iam/keymanage")
        sys.exit(1)

    # 确定图片尺寸
    width, height = args.width, args.height

    if args.preset:
        # 使用预设尺寸
        size_key = args.size.lower()
        for w, h, desc in PRESET_SIZES[args.preset]:
            if size_key in desc.lower():
                width, height = w, h
                print(f"📐 使用预设: {desc} ({w}x{h})")
                break

    # 创建客户端
    client = JimengAI40Client(ak, sk)

    # 生成图片
    resp = client.generate_image(
        prompt=args.prompt,
        width=width,
        height=height,
        scale=args.scale,
        force_single=True,
        max_wait=args.timeout
    )

    if resp:
        # 保存图片
        success = client.save_image(resp, args.output)
        if success:
            print(f"\n🎉 完成! 图片已保存到: {args.output}")
        else:
            print(f"\n❌ 图片保存失败")
    else:
        print(f"\n❌ 图片生成失败")


if __name__ == '__main__':
    main()
