#!/usr/bin/env python3
"""
调用火山引擎即梦AI生成插图

API文档: https://www.volcengine.com/docs/85621/1537648?lang=zh

配置方式（按优先级排序）:
1. 命令行参数 --ak 和 --sk
2. 环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY
3. 配置文件 ~/.tech-book-writer/config.json
"""

import argparse
import requests
import json
import time
import hmac
import hashlib
import os
import sys
from datetime import datetime
from urllib.parse import urlencode
from pathlib import Path


def get_credentials_from_env():
    """从环境变量读取凭证"""
    ak = os.environ.get('VOLCENGINE_ACCESS_KEY')
    sk = os.environ.get('VOLCENGINE_SECRET_KEY')
    return ak, sk


def get_credentials_from_config():
    """从配置文件读取凭证"""
    config_path = Path.home() / '.tech-book-writer' / 'config.json'
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('volcengine_access_key'), config.get('volcengine_secret_key')
        except Exception as e:
            print(f"⚠️  读取配置文件失败: {e}")
    return None, None


def get_credentials():
    """
    获取凭证（按优先级：环境变量 > 配置文件）

    Returns:
        (access_key, secret_key) 或 (None, None)
    """
    # 优先从环境变量读取
    ak, sk = get_credentials_from_env()
    if ak and sk:
        return ak, sk

    # 其次从配置文件读取
    ak, sk = get_credentials_from_config()
    if ak and sk:
        return ak, sk

    return None, None


def setup_credentials():
    """交互式配置凭证"""
    print("=" * 60)
    print("即梦AI 凭证配置")
    print("=" * 60)
    print()
    print("请访问以下地址获取您的 ACCESS_KEY 和 SECRET_KEY:")
    print("https://console.volcengine.com/iam/keymanage/")
    print()

    ak = input("请输入 ACCESS_KEY: ").strip()
    if not ak:
        print("❌ ACCESS_KEY 不能为空")
        return False

    sk = input("请输入 SECRET_KEY: ").strip()
    if not sk:
        print("❌ SECRET_KEY 不能为空")
        return False

    # 创建配置目录
    config_dir = Path.home() / '.tech-book-writer'
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / 'config.json'

    # 保存配置
    config = {
        'volcengine_access_key': ak,
        'volcengine_secret_key': sk
    }

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print()
    print(f"✅ 配置已保存到: {config_path}")
    print()
    print("📝 后续使用时，脚本会自动读取此配置文件。")
    print("💡 提示: 配置文件仅保存在本地，请勿泄露或提交到版本控制系统。")
    print()
    return True


class JimengAIClient:
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = "https://visual.volcengineapi.com"
        
    def _sign_request(self, params):
        """生成签名"""
        # 按字典序排序参数
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)
        
        # 生成签名
        string_to_sign = query_string
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def generate_image(self, prompt, style='realistic', width=1024, height=1024):
        """
        生成图片
        
        Args:
            prompt: 图片描述
            style: 风格（realistic/anime/oil_painting等）
            width: 宽度
            height: 高度
        
        Returns:
            图片URL或None
        """
        endpoint = "/api/v1/visual/generate"
        
        params = {
            'Action': 'GenerateImage',
            'Version': '2023-01-01',
            'AccessKeyId': self.access_key,
            'SignatureMethod': 'HMAC-SHA256',
            'SignatureVersion': '1.0',
            'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        # 请求体
        body = {
            'prompt': prompt,
            'style': style,
            'width': width,
            'height': height,
            'num': 1
        }
        
        # 生成签名
        signature = self._sign_request(params)
        params['Signature'] = signature
        
        # 发送请求
        url = f"{self.base_url}{endpoint}"
        
        try:
            print(f"🎨 正在生成图片...")
            print(f"   提示词: {prompt}")
            print(f"   风格: {style}")
            print(f"   尺寸: {width}x{height}")
            
            response = requests.post(
                url,
                params=params,
                json=body,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    image_url = result['data']['images'][0]['url']
                    print(f"✅ 图片生成成功")
                    return image_url
                else:
                    print(f"❌ API返回错误: {result.get('message')}")
                    return None
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"   响应: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 发生异常: {e}")
            return None
    
    def download_image(self, image_url, output_path):
        """下载图片"""
        try:
            print(f"⬇️  正在下载图片...")
            response = requests.get(image_url, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ 图片已保存: {output_path}")
                return True
            else:
                print(f"❌ 下载失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 下载异常: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='使用即梦AI生成插图',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
配置方式（按优先级）:
  1. 命令行参数 --ak 和 --sk
  2. 环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY
  3. 配置文件 ~/.tech-book-writer/config.json

首次使用请运行: python generate_ai_image.py --setup
        '''
    )
    parser.add_argument('--prompt', help='图片描述（中文或英文）')
    parser.add_argument('--ak', help='火山引擎ACCESS_KEY（覆盖环境变量和配置文件）')
    parser.add_argument('--sk', help='火山引擎SECRET_KEY（覆盖环境变量和配置文件）')
    parser.add_argument('--output', help='输出图片路径')
    parser.add_argument('--style', default='realistic',
                        help='风格: realistic/anime/oil_painting/sketch/cartoon (默认: realistic)')
    parser.add_argument('--width', type=int, default=1024, help='图片宽度 (默认: 1024)')
    parser.add_argument('--height', type=int, default=1024, help='图片高度 (默认: 1024)')
    parser.add_argument('--setup', action='store_true', help='交互式配置凭证')

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
        print("💡 首次使用请先配置凭证:")
        print("   python generate_ai_image.py --setup")
        print()
        print("   或设置环境变量:")
        print("   export VOLCENGINE_ACCESS_KEY='your_ak'")
        print("   export VOLCENGINE_SECRET_KEY='your_sk'")
        sys.exit(1)

    # 获取凭证（命令行参数 > 环境变量 > 配置文件）
    ak = args.ak
    sk = args.sk

    if not ak or not sk:
        ak, sk = get_credentials()

    if not ak or not sk:
        print("❌ 错误: 未找到 ACCESS_KEY 和 SECRET_KEY")
        print()
        print("💡 请通过以下方式配置（任选一种）:")
        print()
        print("   方式1: 交互式配置（推荐）")
        print("   python generate_ai_image.py --setup")
        print()
        print("   方式2: 设置环境变量")
        print("   export VOLCENGINE_ACCESS_KEY='your_ak'")
        print("   export VOLCENGINE_SECRET_KEY='your_sk'")
        print()
        print("   方式3: 使用命令行参数")
        print("   python generate_ai_image.py --ak YOUR_AK --sk YOUR_SK ...")
        print()
        print("📖 获取凭证: https://console.volcengine.com/iam/keymanage/")
        sys.exit(1)

    # 创建客户端
    client = JimengAIClient(ak, sk)
    
    # 生成图片
    image_url = client.generate_image(
        prompt=args.prompt,
        style=args.style,
        width=args.width,
        height=args.height
    )
    
    if image_url:
        # 下载图片
        success = client.download_image(image_url, args.output)
        if success:
            print(f"\n🎉 完成! 图片已保存到: {args.output}")
        else:
            print(f"\n⚠️  图片生成成功但下载失败")
            print(f"   图片URL: {image_url}")
            print(f"   请手动下载")
    else:
        print(f"\n❌ 图片生成失败")


if __name__ == '__main__':
    main()
