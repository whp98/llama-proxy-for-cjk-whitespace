"""
测试脚本- Test Script for llama-proxy
验证CJK 空格修复功能是否正常工作
"""

import requests
import json


def test_openai_chat():
    """测试OpenAI Chat API"""
    print("\n" + "="*50)
    print("测试1: OpenAI Chat API (非流式)")
    print("="*50)

    url = "http://localhost:58080/v1/chat/completions"
    payload = {
        "model": "qwen3.5-9b",
        "messages": [
            {"role": "user", "content": "我使用Python 代码计算"}
        ],
        "max_tokens": 100,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        print(f"状态码：{response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"响应内容：{content[:100]}...")

            #检查是否有多余空格
            if "Python code" in content or "Python代码" in content:
                print("✅ 空格修复成功！")
            else:
                print("⚠️ 未检测到明显的CJK-ASCII 边界问题")
        else:
            print(f"❌ 请求失败：{response.text[:200]}")
    except Exception as e:
        print(f"❌ 测试错误：{e}")


def test_streaming():
    """测试流式响应"""
    print("\n" + "="*50)
    print("测试2: OpenAI Chat API (流式)")
    print("="*50)

    url = "http://localhost:58080/v1/chat/completions"
    payload = {
        "model": "qwen3.5-9b",
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 50,
        "stream": True
    }

    try:
        with requests.post(url, json=payload, stream=True) as response:
            count = 0
            for line in response.iter_lines():
                if line:
                    count += 1
                    print(f"Chunk {count}: {line[:80]}...")
                    if count >= 5:  #只显示前5 个chunk
                        break
        print("✅ 流式响应正常")
    except Exception as e:
        print(f"❌ 测试错误：{e}")


def test_anthropic_api():
    """测试Anthropic API"""
    print("\n" + "="*50)
    print("测试3: Anthropic Messages API")
    print("="*50)

    url = "http://localhost:58080/v1/messages"
    payload = {
        "model": "qwen3.5-9b",
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "我使用JavaScript 编写"}
        ]
    }

    try:
        response = requests.post(url, json=payload)
        print(f"状态码：{response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result["content"][0]["text"]
            print(f"响应内容：{content[:100]}...")

            #检查是否有多余空格
            if "JavaScript 编写" in content or "JavaScript编写" in content:
                print("✅ 空格修复成功！")
        else:
            print(f"❌ 请求失败")
    except Exception as e:
        print(f"❌ 测试错误：{e}")


def test_health_check():
    """健康检查"""
    print("\n" + "="*50)
    print("测试4:服务健康检查")
    print("="*50)

    try:
        response = requests.get("http://localhost:58080/v1/models", timeout=5)
        print(f"状态码：{response.status_code}")

        if response.status_code == 200:
            models = response.json().get("data", [])
            print(f"可用模型数：{len(models)}")
            for model in models[:3]:
                print(f"  - {model.get('id', 'unknown')}")
            print("✅ 服务运行正常")
        else:
            print("⚠️ 无法获取模型列表（可能是代理未启动）")
    except Exception as e:
        print(f"❌ 健康检查失败：{e}")


def test_whitespace_patterns():
    """测试各种空格模式"""
    print("\n" + "="*50)
    print("测试5:多种空格模式检测")
    print("="*50)

    patterns = [
        ("我使用Python", "中文+英文"),
        ("English中文", "英文+中文"),
        ("数字123 中文", "数字+中文"),
        ("中文456 符号!", "中文+数字+符号"),
    ]

    for text, desc in patterns:
        payload = {
            "model": "qwen3.5-9b",
            "messages": [{"role": "user", "content": f"测试：{text}"}],
            "max_tokens": 50,
            "stream": False
        }

        try:
            response = requests.post("http://localhost:58080/v1/chat/completions", json=payload)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                print(f"✅ {desc}: {text} → {content[:30]}")
        except Exception as e:
            print(f"❌ {desc}: {e}")


if __name__ == "__main__":
    import sys

    print("\n" + "🧪 llama-proxy 测试套件")
    print("="*50)

    #运行所有测试
    test_health_check()
    test_openai_chat()
    test_streaming()
    test_anthropic_api()
    test_whitespace_patterns()

    print("\n" + "="*50)
    print("✅ 测试完成！")
    print("="*50)
