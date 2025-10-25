"""
MCP Email Server - 提供邮件发送工具
这是一个简化的MCP服务器实现，用于教学目的
"""
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class Tool(BaseModel):
    """工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class ToolCallRequest(BaseModel):
    """工具调用请求"""
    name: str
    arguments: Dict[str, Any]


class ToolCallResponse(BaseModel):
    """工具调用响应"""
    content: List[Dict[str, str]]
    isError: bool = False


class MCPEmailServer:
    """
    MCP邮件服务器
    在真实的MCP实现中，这会通过JSON-RPC与客户端通信
    这里我们简化为Python类，便于理解核心概念
    """
    
    def __init__(self):
        self.name = "email-server"
        self.version = "1.0.0"
        self._tools = self._register_tools()
    
    def _register_tools(self) -> List[Tool]:
        """注册可用的工具"""
        return [
            Tool(
                name="send_email",
                description="发送电子邮件给指定收件人",
                input_schema={
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "收件人邮箱地址"
                        },
                        "subject": {
                            "type": "string",
                            "description": "邮件主题"
                        },
                        "body": {
                            "type": "string",
                            "description": "邮件正文内容"
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            ),
            Tool(
                name="check_email_status",
                description="检查邮件发送状态",
                input_schema={
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": "邮件ID"
                        }
                    },
                    "required": ["email_id"]
                }
            ),
            Tool(
                name="get_inbox_count",
                description="获取收件箱中未读邮件数量",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
    
    def list_tools(self) -> List[Tool]:
        """列出所有可用工具（MCP Resources发现）"""
        return self._tools
    
    def call_tool(self, request: ToolCallRequest) -> ToolCallResponse:
        """执行工具调用"""
        tool_name = request.name
        arguments = request.arguments
        
        # 路由到对应的工具处理函数
        if tool_name == "send_email":
            return self._send_email(arguments)
        elif tool_name == "check_email_status":
            return self._check_email_status(arguments)
        elif tool_name == "get_inbox_count":
            return self._get_inbox_count(arguments)
        else:
            return ToolCallResponse(
                content=[{
                    "type": "text",
                    "text": f"未知工具: {tool_name}"
                }],
                isError=True
            )
    
    def _send_email(self, args: Dict[str, Any]) -> ToolCallResponse:
        """发送邮件工具实现"""
        to = args.get("to")
        subject = args.get("subject")
        body = args.get("body")
        
        # 模拟邮件发送（实际应用中这里会调用SMTP等真实邮件服务）
        print(f"\n📧 [邮件服务器] 正在发送邮件...")
        print(f"   收件人: {to}")
        print(f"   主题: {subject}")
        print(f"   内容: {body[:50]}..." if len(body) > 50 else f"   内容: {body}")
        
        # 模拟成功响应
        email_id = f"email_{hash(to + subject)}"
        result = {
            "status": "success",
            "message": f"邮件已成功发送到 {to}",
            "email_id": email_id,
            "timestamp": "2025-10-24T10:30:00Z"
        }
        
        return ToolCallResponse(
            content=[{
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False, indent=2)
            }]
        )
    
    def _check_email_status(self, args: Dict[str, Any]) -> ToolCallResponse:
        """检查邮件状态工具实现"""
        email_id = args.get("email_id")
        
        # 模拟状态查询
        result = {
            "email_id": email_id,
            "status": "delivered",
            "delivered_at": "2025-10-24T10:31:00Z"
        }
        
        return ToolCallResponse(
            content=[{
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False, indent=2)
            }]
        )
    
    def _get_inbox_count(self, args: Dict[str, Any]) -> ToolCallResponse:
        """获取收件箱未读数工具实现"""
        # 模拟收件箱查询
        result = {
            "unread_count": 5,
            "total_count": 23
        }
        
        return ToolCallResponse(
            content=[{
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False, indent=2)
            }]
        )


# 创建全局服务器实例
email_server = MCPEmailServer()