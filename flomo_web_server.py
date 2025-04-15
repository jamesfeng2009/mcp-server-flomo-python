import os
import json
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("flomo-web-server")

# 创建 Flask 应用
app = Flask(__name__)

# 加载环境变量
load_dotenv()

# 获取 API URL
FLOMO_API_URL = os.getenv("FLOMO_API_URL")
if not FLOMO_API_URL:
    logger.error("FLOMO_API_URL 环境变量未设置")
    raise ValueError("FLOMO_API_URL 环境变量必须设置")

# 验证 API URL
try:
    url = urlparse(FLOMO_API_URL)
    if not all([url.scheme, url.netloc]):
        raise ValueError("无效的 API URL 格式")
    logger.info(f"Flomo API URL 有效，协议: {url.scheme}, 主机: {url.netloc}, 路径: {url.path}")
except Exception as e:
    logger.error(f"无效的 API URL: {str(e)}")
    raise ValueError(f"无效的 API URL: {str(e)}")

@app.route('/')
def index():
    """首页，显示简单的使用说明"""
    return """
    <html>
        <head>
            <title>Flomo Web 服务器</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                pre { background: #f6f8fa; padding: 15px; border-radius: 5px; }
                h1 { color: #333; }
                .endpoint { font-weight: bold; color: #0366d6; }
            </style>
        </head>
        <body>
            <h1>Flomo Web 服务器</h1>
            <p>这是一个与 Flomo API 交互的简单 Web 服务器。</p>
            
            <h2>可用端点：</h2>
            <p><span class="endpoint">GET /test</span> - 测试服务器是否工作正常</p>
            <p><span class="endpoint">POST /write_note</span> - 发送笔记到 Flomo</p>
            
            <h2>写入笔记示例：</h2>
            <pre>
curl -X POST http://localhost:12345/write_note \\
    -H "Content-Type: application/json" \\
    -d '{"content": "这是一条通过 API 发送的测试笔记！\\n\\n支持 **Markdown** 格式\\n- 列表1\\n- 列表2\\n\\n> 引用文本"}'
            </pre>
        </body>
    </html>
    """

@app.route('/test')
def test():
    """测试端点，检查服务器是否正常工作"""
    logger.info("测试端点被调用")
    return jsonify({
        "status": "success",
        "message": "服务器工作正常",
        "flomo_api_url": FLOMO_API_URL[:30] + "..." if len(FLOMO_API_URL) > 30 else FLOMO_API_URL
    })

@app.route('/write_note', methods=['POST'])
def write_note():
    """发送笔记到 Flomo"""
    try:
        data = request.json
        if not data or 'content' not in data:
            return jsonify({"error": "必须提供 content 字段"}), 400
        
        content = data['content']
        if not content:
            return jsonify({"error": "content 不能为空"}), 400
        
        logger.info(f"发送笔记到 Flomo: {content[:50]}{'...' if len(content) > 50 else ''}")
        
        # 发送请求到 Flomo API
        req = {"content": content}
        response = requests.post(
            FLOMO_API_URL.strip(),
            json=req,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Flomo-Web-Server/1.0"
            }
        )
        
        if not response.ok:
            logger.error(f"请求失败，状态码: {response.status_code} {response.reason}")
            try:
                error_json = response.json()
                return jsonify(error_json), response.status_code
            except:
                return jsonify({
                    "error": f"请求失败，状态码 {response.status_code} {response.reason}",
                    "raw": response.text
                }), response.status_code
        
        result = response.json()
        
        # 添加笔记 URL
        if result.get("memo", {}).get("slug"):
            memo_url = f"https://v.flomoapp.com/mine/?memo_id={result['memo']['slug']}"
            result["memo"]["url"] = memo_url
            logger.info(f"已添加笔记 URL: {memo_url}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 12345))
    logger.info(f"启动 Flomo Web 服务器，端口: {port}")
    app.run(host="0.0.0.0", port=port, debug=True) 