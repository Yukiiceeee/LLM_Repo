"""配置文件"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# 如果使用其他兼容OpenAI API的服务（如DeepSeek等）
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)

