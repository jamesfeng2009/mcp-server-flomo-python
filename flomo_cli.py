#!/usr/bin/env python
"""
Flomo CLI - 命令行工具，用于与 Flomo Web 服务器交互
"""

import argparse
import requests
import sys
import json
import os
from pathlib import Path

# Web 服务器地址
SERVER_URL = os.getenv("FLOMO_SERVER_URL", "http://localhost:12345")

def test_server():
    """测试服务器是否正常工作"""
    try:
        response = requests.get(f"{SERVER_URL}/test")
        if response.ok:
            result = response.json()
            print("✅ 服务器状态:", result["message"])
            print("🔗 Flomo API URL:", result["flomo_api_url"])
            return True
        else:
            print("❌ 服务器错误:", response.status_code, response.reason)
            try:
                print(response.json())
            except:
                print(response.text)
            return False
    except requests.RequestException as e:
        print(f"❌ 无法连接到服务器: {str(e)}")
        return False

def write_note(content, file=None):
    """写入笔记到 Flomo"""
    try:
        # 如果指定了文件，则从文件读取内容
        if file:
            filepath = Path(file)
            if not filepath.exists():
                print(f"❌ 文件不存在: {file}")
                return False
            
            content = filepath.read_text(encoding="utf-8")
            print(f"📄 已读取文件: {file} ({len(content)} 字符)")
        
        # 确保内容不为空
        if not content:
            print("❌ 内容不能为空")
            return False
        
        # 发送请求
        response = requests.post(
            f"{SERVER_URL}/write_note",
            json={"content": content},
            headers={"Content-Type": "application/json"}
        )
        
        if response.ok:
            result = response.json()
            print("✅ 笔记已成功发送！")
            
            if result.get("memo", {}).get("url"):
                print("🔗 笔记链接:", result["memo"]["url"])
            
            return True
        else:
            print("❌ 发送笔记失败:", response.status_code, response.reason)
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except:
                print(response.text)
            return False
    
    except requests.RequestException as e:
        print(f"❌ 请求错误: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Flomo CLI - 与 Flomo Web 服务器交互的命令行工具")
    
    # 创建子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # test 命令
    test_parser = subparsers.add_parser("test", help="测试服务器连接")
    
    # write 命令
    write_parser = subparsers.add_parser("write", help="写入笔记到 Flomo")
    write_parser.add_argument("content", nargs="?", help="笔记内容")
    write_parser.add_argument("-f", "--file", help="从文件读取笔记内容")
    
    # 解析参数
    args = parser.parse_args()
    
    # 处理命令
    if args.command == "test":
        test_server()
    elif args.command == "write":
        if args.file:
            write_note(None, args.file)
        elif args.content:
            write_note(args.content)
        else:
            print("❌ 请提供笔记内容或指定文件")
            write_parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 