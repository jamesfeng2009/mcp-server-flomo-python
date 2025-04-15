# Flomo Web 服务器与命令行工具

这个项目提供了一个简单的 Web 服务器和命令行工具，用于与 Flomo API 交互，以便在不同环境中方便地添加笔记到 Flomo。

## 项目结构

```
.
├── flomo_cli.py         # 命令行工具入口脚本
├── flomo_server.py      # Web服务器入口脚本
├── src                  # 源代码目录
│   ├── cli              # 命令行工具模块
│   │   ├── __init__.py
│   │   ├── __main__.py  # CLI主入口
│   │   └── commands.py  # CLI命令实现
│   ├── server           # Web服务器模块
│   │   ├── __init__.py
│   │   ├── __main__.py  # 服务器主入口
│   │   └── app.py       # Flask应用实现
│   └── utils            # 工具模块
│       ├── __init__.py
│       ├── config.py    # 配置管理
│       └── flomo_client.py  # Flomo API客户端
├── tests                # 测试目录
└── docs                 # 文档目录
```

## 功能

- Web 服务器：提供 REST API 接口与 Flomo 交互
- 命令行工具：提供命令行界面，用于从终端发送笔记

## 安装

确保已安装 Python 3.7+ 和所需依赖：

```bash
pip install flask requests python-dotenv
```

## 配置

1. 在项目根目录创建 `.env` 文件：

```
FLOMO_API_URL=https://flomoapp.com/iwh/你的ID/你的API密钥/
```

> 注意：FLOMO_API_URL 是必需的，你可以从 Flomo 网站的 设置 > API 页面获取。

## Web 服务器使用

启动 Web 服务器：

```bash
python flomo_server.py
```

服务器默认在 http://localhost:12345 上运行，提供以下端点：

- `GET /` - 显示使用说明
- `GET /test` - 测试服务器连接
- `POST /write_note` - 写入笔记到 Flomo

### 示例：写入笔记

```bash
curl -X POST http://localhost:12345/write_note \
    -H "Content-Type: application/json" \
    -d '{"content": "这是一条测试笔记！\n\n支持 **Markdown** 格式\n- 列表1\n- 列表2\n\n> 引用文本"}'
```

## 命令行工具使用

### 测试连接

```bash
python flomo_cli.py test
```

### 发送笔记

直接发送内容：

```bash
python flomo_cli.py write "这是一条通过命令行发送的测试笔记！"
```

从文件读取内容：

```bash
python flomo_cli.py write -f notes.md
```

### 高级选项

指定服务器URL：

```bash
python flomo_cli.py --server http://example.com:8080 write "自定义服务器的笔记"
```

## 在 Cursor 中使用

你可以通过直接调用命令行工具在 Cursor 中使用：

1. 打开终端
2. 运行以下命令：

```bash
cd /Users/fengyu/Downloads/myStudy/project/mcp-server-flomo-python
python flomo_cli.py write "这是从 Cursor 发送的笔记！"
```

你还可以将 Web 服务器设置为在启动时自动运行，然后通过各种方式（例如快捷键、脚本等）调用命令行工具。

## 开发指南

### 运行服务器

使用指定端口：

```bash
python flomo_server.py --port 8080
```

使用指定主机：

```bash
python flomo_server.py --host 127.0.0.1
```

### 扩展功能

如需添加新功能：

1. 对于CLI，在 `src/cli/commands.py` 中添加新命令函数
2. 对于Web服务器，在 `src/server/app.py` 中添加新路由

## 故障排除

1. 如果 Web 服务器无法启动，请检查端口 12345 是否已被占用
2. 如果连接到 Flomo API 失败，请检查 API URL 是否正确
3. 确保 `.env` 文件中的 FLOMO_API_URL 设置正确

## 链接

- [Flomo 官方网站](https://flomoapp.com)
- [Flomo API 文档](https://help.flomoapp.com/advance/api)
