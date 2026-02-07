#!/usr/bin/env python3
"""
调用火山引擎即梦AI生成插图（Visual Service API）

API文档: https://www.volcengine.com/docs/85128/1526761

配置方式（按优先级排序）:
1. 命令行参数 --ak --sk
2. 环境变量 VOLCENGINE_AK / VOLCENGINE_SK
3. 配置文件 ~/.tech-book-writer/config.json
"""

import argparse
import json
import os
import sys
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
    print("火山引擎即梦AI AK/SK 配置")
    print("=" * 60)
    print()
    print("请访问以下地址获取您的 AK/SK:")
    print("https://console.volcengine.com/iam/keymanage")
    print()
    print("说明: 即梦AI使用火山引擎Visual Service，需要AK/SK认证")
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


class JimengAIClient:
    """即梦AI客户端（使用Visual Service API）"""

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
        self.req_key = "high_aes_general_v30l_zt2i"  # 通用3.0文生图

    def generate_image(self, prompt, use_pre_llm=True, seed=-1, scale=2.5):
        """
        生成图片

        Args:
            prompt: 图片描述（中英文均可）
            use_pre_llm: 是否开启文本扩写（短prompt建议开启）
            seed: 随机种子，-1表示随机
            scale: 影响文本描述的程度 (1-10)

        Returns:
            dict: API响应，包含base64编码的图片数据
        """
        form = {
            "req_key": self.req_key,
            "prompt": prompt,
            "use_pre_llm": use_pre_llm,
            "seed": seed,
            "scale": scale,
        }

        try:
            print(f"🎨 正在生成图片...")
            print(f"   算法: {self.req_key}")
            print(f"   提示词: {prompt}")
            print(f"   文本扩写: {'开启' if use_pre_llm else '关闭'}")
            print(f"   随机种子: {seed}")
            print(f"   文本权重: {scale}")

            resp = self.client.cv_process(form)

            if resp.get('code') == 10000:
                print(f"✅ 图片生成成功")
                return resp
            else:
                print(f"❌ API返回错误: {resp.get('message', 'Unknown error')}")
                print(f"   响应详情: {resp}")
                return None

        except Exception as e:
            print(f"❌ 发生异常: {e}")
            import traceback
            traceback.print_exc()
            return None

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
            if 'binary_data_base64' not in data or not data['binary_data_base64']:
                print("❌ 响应中没有base64图片数据")
                return False

            # 解码base64图片
            img_base64 = data['binary_data_base64'][0]
            img_data = base64.b64decode(img_base64)

            # 保存图片
            with open(output_path, 'wb') as f:
                f.write(img_data)

            print(f"✅ 图片已保存: {output_path}")
            print(f"   文件大小: {len(img_data)} 字节")

            # 如果有扩展后的prompt，显示出来
            if 'llm_result' in data and data['llm_result']:
                print(f"\n📝 扩展后的提示词:")
                print(f"   {data['llm_result']}")

            return True

        except Exception as e:
            print(f"❌ 保存图片失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(
        description='使用火山引擎即梦AI生成插图',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
配置方式（按优先级）:
  1. 命令行参数 --ak --sk
  2. 环境变量 VOLCENGINE_AK / VOLCENGINE_SK
  3. 配置文件 ~/.tech-book-writer/config.json

获取AK/SK: https://console.volcengine.com/iam/keymanage

首次使用请运行: python generate_ai_image.py --setup

示例:
  # 交互式配置
  python generate_ai_image.py --setup

  # 使用环境变量中的AK/SK生成图片
  python generate_ai_image.py --prompt "一只可爱的猫" --output cat.png

  # 使用命令行参数指定AK/SK
  python generate_ai_image.py --ak YOUR_AK --sk YOUR_SK --prompt "山水画" --output landscape.png

  # 关闭文本扩写（适合长prompt）
  python generate_ai_image.py --prompt "详细的图片描述..." --output result.png --no-pre-llm
        '''
    )
    parser.add_argument('--prompt', help='图片描述（中文或英文）')
    parser.add_argument('--ak', help='火山引擎Access Key')
    parser.add_argument('--sk', help='火山引擎Secret Key')
    parser.add_argument('--output', help='输出图片路径')
    parser.add_argument('--no-pre-llm', action='store_true',
                        help='关闭文本扩写（适合长prompt）')
    parser.add_argument('--seed', type=int, default=-1,
                        help='随机种子（-1表示随机，相同种子生成相似图片）')
    parser.add_argument('--scale', type=float, default=2.5,
                        help='文本描述权重 (1.0-10.0，默认: 2.5)')
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

    # 创建客户端
    client = JimengAIClient(ak, sk)

    # 生成图片
    resp = client.generate_image(
        prompt=args.prompt,
        use_pre_llm=not args.no_pre_llm,
        seed=args.seed,
        scale=args.scale
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
