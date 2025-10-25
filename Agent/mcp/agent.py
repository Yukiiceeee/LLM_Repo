"""
AI Agent - 使用OpenAI + MCP实现智能工具调用
"""
import json
from typing import List, Dict, Any
from openai import OpenAI
from mcp_client.client import MCPClient
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL


class MCPAgent:
    """
    基于MCP的AI Agent
    整合了OpenAI的Function Calling能力和MCP的工具调用能力
    """
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        
        # 初始化OpenAI客户端
        if OPENAI_BASE_URL:
            self.openai_client = OpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL
            )
        else:
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        self.model = OPENAI_MODEL
        self.conversation_history: List[Dict[str, Any]] = []
    
    def chat(self, user_message: str, max_iterations: int = 5) -> str:
        """
        与Agent对话
        支持多轮工具调用
        """
        print(f"\n💬 [User] {user_message}")
        
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # 获取MCP工具并转换为OpenAI格式
        tools = self.mcp_client.get_tools_for_openai()
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 [Agent] 第 {iteration} 轮思考...")
            
            # 调用OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=tools if tools else None,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            # 检查是否需要调用工具
            if assistant_message.tool_calls:
                # 添加助手消息到历史（包含工具调用）
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                
                # 执行所有工具调用
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"\n🤖 [Agent] 决定调用工具: {function_name}")
                    
                    # 通过MCP客户端调用工具
                    tool_result = self.mcp_client.call_tool(
                        function_name,
                        function_args
                    )
                    
                    # 添加工具结果到历史
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result.get("result", str(tool_result))
                    })
                
                # 继续下一轮（让模型看到工具结果后再回答）
                continue
            else:
                # 没有工具调用，返回最终回答
                final_response = assistant_message.content
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_response
                })
                
                print(f"\n🤖 [Agent] {final_response}")
                return final_response
        
        return "抱歉，达到最大迭代次数，无法完成任务。"
    
    def reset(self):
        """重置对话历史"""
        self.conversation_history = []
        print("\n🔄 对话历史已重置")