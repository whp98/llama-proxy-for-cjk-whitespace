#测试说明

##运行测试

###方式一：pytest（推荐）

```bash
pip install pytest pytest-asyncio requests

pytest tests/test_proxy.py -v
```

###方式二：直接执行

```bash
pip install requests

python tests/test_proxy.py
```

##预期输出

测试会验证以下功能：

1. ✅ **服务健康检查** -确认代理服务正常运行
2. ✅ **OpenAI Chat API** -非流式请求的CJK 空格修复
3. ✅ **流式响应** - SSE 格式的逐块处理
4. ✅ **Anthropic API** - Anthropic 格式的支持
5. ✅ **多种模式** -中英文、数字、符号的组合测试

##注意事项

-确保代理服务已在`http://localhost:58080` 运行
- llama.cpp upstream 服务必须正常响应
-首次运行可能需要等待模型加载完成

---

**Happy Testing! 🧪**
