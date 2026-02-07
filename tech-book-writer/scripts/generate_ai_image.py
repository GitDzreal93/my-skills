#!/usr/bin/env python3
"""
调用火山引擎即梦AI生成插图

API文档: https://www.volcengine.com/docs/85621/1537648?lang=zh
"""

import argparse
import requests
import json
import time
import hmac
import hashlib
from datetime import datetime
from urllib.parse import urlencode


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
    parser = argparse.ArgumentParser(description='使用即梦AI生成插图')
    parser.add_argument('--prompt', required=True, help='图片描述（中文或英文）')
    parser.add_argument('--ak', required=True, help='火山引擎ACCESS_KEY')
    parser.add_argument('--sk', required=True, help='火山引擎SECRET_KEY')
    parser.add_argument('--output', required=True, help='输出图片路径')
    parser.add_argument('--style', default='realistic', 
                        help='风格: realistic/anime/oil_painting/sketch/cartoon')
    parser.add_argument('--width', type=int, default=1024, help='图片宽度')
    parser.add_argument('--height', type=int, default=1024, help='图片高度')
    
    args = parser.parse_args()
    
    # 检查AK/SK
    if not args.ak or not args.sk:
        print("❌ 错误: 必须提供ACCESS_KEY和SECRET_KEY")
        print("   获取方式: https://console.volcengine.com/iam/keymanage/")
        return
    
    # 创建客户端
    client = JimengAIClient(args.ak, args.sk)
    
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
