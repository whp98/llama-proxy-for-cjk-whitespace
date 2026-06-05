#贡献指南

感谢你对本项目的贡献！🎉

## 📋 代码规范

### Python 风格指南

本项目遵循[PEP 8](https://pep8.org/)编码规范：

```bash
#格式化代码
black llama_proxy/

#检查导入顺序
isort llama_proxy/

#类型检查（可选）
mypy llama_proxy/
```

###提交信息规范

我们使用[Conventional Commits](https://www.conventionalcommits.org/)：

```bash
feat:添加新功能
fix:修复bug
docs:文档更新
style:代码格式调整
refactor:重构代码
test:测试相关
chore:构建/工具链变更
```

## 🚀 开发流程

###1. Fork 并克隆仓库

```bash
git clone https://github.com/<your-username>/llama-proxy-for-qwen3.5-9b.git
cd llama-proxy-for-qwen3.5-9b
```

###2.创建分支

```bash
git checkout -b feature/你的功能名
#或
git checkout -b fix/你的bug 修复
```

###3.开发并提交

```bash
#开发代码
# ...

#提交更改
git add .
git commit -m "feat:添加CJK 空格智能检测优化"
```

###4.Push 并创建Pull Request

```bash
git push origin feature/你的功能名
```

然后在GitHub 上创建Pull Request。

## 📝 如何贡献

###欢迎贡献以下类型：

1. **Bug 修复** -报告或修复已知问题
2. **新功能** -增强代理功能（如更多语言支持）
3. **性能优化** -提升处理速度和内存效率
4. **文档改进** -完善README、注释等
5. **测试覆盖** -添加单元测试和集成测试

###提交PR 前请：

- ✅ 确保代码通过所有现有测试
- ✅ 更新相关文档（如有需要）
- ✅ 保持提交信息清晰
- ✅ 不要修改未使用的依赖项
- ✅ 在PR 描述中说明变更原因

## 🧪 测试你的更改

###运行单元测试

```bash
pytest tests/ -v
```

###手动测试

1.启动服务：`./start.sh`
2.访问`http://localhost:58080/v1/models`
3.使用curl 或客户端工具测试API

## 📦 添加新功能

###示例：添加新的字符集支持

如果要在正则中添加更多CJK 字符范围，请确保：

1. **兼容性** -不影响现有功能
2. **性能** -避免过度复杂的正则表达式
3. **测试** -覆盖新字符集的边界情况

```python
# llama_proxy.py
#示例：扩展CJK 支持
CJK = r"[一-鿿㐀-䶿豈-﫿0-⩭f⾀0-⿿E]"
```

## 📄 License

通过贡献代码，你同意你的贡献将遵循MIT 许可证。

## 💬 需要帮助？

在创建PR 之前，欢迎：

-打开[Issue](https://github.com/<org>/llama-proxy-for-qwen3.5-9b/issues)讨论
-查看现有的Issues 和Discussions
-查阅项目文档

## 🙏 感谢所有贡献者！

[![Contributors](https://contrib.rocks/image?repo=<your-org>/llama-proxy-for-qwen3.5-9b)](https://github.com/<your-org>/llama-proxy-for-qwen3.5-9b/graph/contributors)

---

**Together we build better! 🚀**
