import os
import json
import logging
import sys
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import requests
from dotenv import load_dotenv
from mcp.server import FastMCP

# 配置日志 - 使用更详细的日志级别
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("flomo-server")

# 打印出所有环境变量，帮助调试
logger.debug("Environment variables:")
for key, value in os.environ.items():
    if "API" in key or "MCP" in key or "PORT" in key:
        logger.debug(f"  {key}: {value}")

class FlomoClient:
    """Flomo client used to interact with the Flomo API."""
    
    def __init__(self, api_url: str):
        """
        Create a new Flomo client.
        Args:
            api_url: The API URL of the Flomo API.
        """
        self.api_url = api_url
        logger.info(f"[FlomoClient] Initialized with API URL: {self.api_url}")
        
        # 验证API URL
        try:
            url = urlparse(api_url)
            if not all([url.scheme, url.netloc]):
                raise ValueError("Invalid API URL format")
            logger.info(f"[FlomoClient] API URL is valid, protocol: {url.scheme}, host: {url.netloc}, path: {url.path}")
        except Exception as e:
            logger.error(f"[FlomoClient] Invalid API URL: {str(e)}")
            raise ValueError(f"Invalid API URL: {str(e)}")

    async def write_note(self, content: str) -> Dict[str, Any]:
        """
        Write a note to Flomo.
        Args:
            content: The content of the note.
        Returns:
            The response from the Flomo API.
        """
        logger.info(f"[FlomoClient] Starting writeNote with content: {content[:50]}{'...' if len(content) > 50 else ''}")
        
        try:
            if not content:
                logger.error("[FlomoClient] Content is empty")
                raise ValueError("invalid content")

            req = {"content": content}
            logger.info(f"[FlomoClient] Sending request to: {self.api_url}")
            logger.info(f"[FlomoClient] Request payload: {json.dumps(req, indent=2)}")

            try:
                response = requests.post(
                    self.api_url.strip(),
                    json=req,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "User-Agent": "MCP-Server-Flomo-Python/1.0"
                    }
                )
                
                logger.info(f"[FlomoClient] Response status: {response.status_code} {response.reason}")
                logger.info(f"[FlomoClient] Response headers: {json.dumps(dict(response.headers), indent=2)}")

                if not response.ok:
                    logger.error(f"[FlomoClient] Request failed with status: {response.status_code} {response.reason}")
                    error_text = response.text
                    logger.error(f"[FlomoClient] Error response: {error_text}")
                    try:
                        return response.json()
                    except:
                        return {
                            "error": f"request failed with status {response.status_code} {response.reason}",
                            "raw": error_text
                        }

                response_text = response.text
                logger.info(f"[FlomoClient] Raw response text: {response_text}")
                
                try:
                    result = response.json()
                    logger.info(f"[FlomoClient] Parsed result: {json.dumps(result, indent=2)}")
                except Exception as e:
                    logger.error(f"[FlomoClient] Failed to parse response as JSON: {str(e)}")
                    return {
                        "error": "Failed to parse JSON response",
                        "raw": response_text
                    }

                if result.get("memo", {}).get("slug"):
                    memo_url = f"https://v.flomoapp.com/mine/?memo_id={result['memo']['slug']}"
                    result["memo"]["url"] = memo_url
                    logger.info(f"[FlomoClient] Added memo URL: {memo_url}")
                else:
                    logger.info("[FlomoClient] No memo slug found in response")

                return result

            except requests.RequestException as e:
                logger.error(f"[FlomoClient] Network error: {str(e)}")
                return {"error": f"Network error: {str(e)}"}

        except Exception as e:
            logger.error(f"[FlomoClient] Error in writeNote: {str(e)}")
            return {"error": str(e) if isinstance(e, Exception) else "Unknown error"}

# 创建 Flomo 客户端实例
flomo_client = None

# 在创建服务器实例之前加载环境变量
load_dotenv()

# 明确设置端口
port = int(os.getenv("MCP_PORT", "8822"))  # 改为默认8822
host = os.getenv("MCP_HOST", "127.0.0.1")

logger.debug(f"Using host={host}, port={port}")

# 创建 MCP 服务器实例
try:
    mcp = FastMCP("Flomo MCP Server", host=host, port=port)
    logger.info(f"[FlomoServer] Created FastMCP server instance on {host}:{port}")
except Exception as e:
    logger.error(f"[FlomoServer] Failed to create FastMCP server: {str(e)}")
    sys.exit(1)

@mcp.tool()
def test(message: str) -> str:
    """A simple test method"""
    logger.info(f"[FlomoServer] Test called with message: {message}")
    return f"Test successful! {message}"

@mcp.tool()
async def write_note(content: str) -> dict:
    """
    Write a note to Flomo
    Args:
        content: The content of the note (supports markdown)
    Returns:
        dict: Response from Flomo API
    """
    global flomo_client
    
    logger.info("[FlomoServer] Write note called")
    if not content:
        raise ValueError("Content is required")
    
    if flomo_client is None:
        # 获取API URL
        api_url = os.getenv("FLOMO_API_URL")
        if not api_url:
            logger.error("[FlomoServer] FLOMO_API_URL environment variable is not set")
            raise ValueError("FLOMO_API_URL environment variable is required")
        
        logger.info(f"[FlomoServer] Initializing with API URL: {api_url}")
        flomo_client = FlomoClient(api_url)
        
    result = await flomo_client.write_note(content)
    
    if result.get("error"):
        logger.error(f"[FlomoServer] Failed to write note: {result['error']}")
        raise ValueError(f"Failed to write note: {result['error']}")
        
    logger.info("[FlomoServer] Successfully wrote note to Flomo")
    return result

def main():
    try:
        logger.info("[FlomoServer] Starting server")
        logger.info(f"[FlomoServer] Using {host}:{port}")
        logger.info("[FlomoServer] Available tools: test, write_note")
        logger.info("[FlomoServer] Running...")
        mcp.run()
    except Exception as e:
        logger.error(f"[FlomoServer] Error while running server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
