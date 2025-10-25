"""
MCP Client - 连接MCP服务器并管理工具调用
"""
from typing import List, Dict, Any
from mcp_server.email_server import MCPEmailServer, ToolCallRequest


class MCPClient:
    """
    MCP客户端
    在真实的MCP实现中，这会通过JSON-RPC 2.0与远程服务器通信
    这里我们简化为直接调用本地服务器，便于理解
    """
    
    def __init__(self):
        self.servers: Dict[str, MCPEmailServer] = {}
        self.connected = False
    
    def connect_server(self, server_name: str, server: MCPEmailServer):
        """连接到MCP服务器"""
        print(f"🔌 [MCP Client] 正在连接到服务器: {server_name}")
        self.servers[server_name] = server
        self.connected = True
        print(f"✅ [MCP Client] 已成功连接到 {server_name}")
    
    def list_all_tools(self) -> List[Dict[str, Any]]:
        """
        列出所有已连接服务器的工具
        这是MCP的能力发现（Capability Discovery）机制
        """
        all_tools = []
        for server_name, server in self.servers.items():
            tools = server.list_tools()
            for tool in tools:
                all_tools.append({
                    "server": server_name,
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema
                })
        return all_tools
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用工具
        这是MCP的工具执行机制
        """
        print(f"\n🔧 [MCP Client] 正在调用工具: {tool_name}")
        print(f"   参数: {arguments}")
        
        # 在所有服务器中查找工具
        for server_name, server in self.servers.items():
            tools = server.list_tools()
            tool_names = [t.name for t in tools]
            
            if tool_name in tool_names:
                # 创建工具调用请求
                request = ToolCallRequest(name=tool_name, arguments=arguments)
                # 执行调用
                response = server.call_tool(request)
                
                if response.isError:
                    print(f"❌ [MCP Client] 工具调用失败")
                    return {
                        "error": True,
                        "message": response.content[0]["text"]
                    }
                else:
                    print(f"✅ [MCP Client] 工具调用成功")
                    return {
                        "error": False,
                        "result": response.content[0]["text"]
                    }
        
        # 工具未找到
        return {
            "error": True,
            "message": f"未找到工具: {tool_name}"
        }
    
    def get_tools_for_openai(self) -> List[Dict[str, Any]]:
        """
        将MCP工具转换为OpenAI Function Calling格式
        这是连接MCP和OpenAI的关键转换层
        """
        all_tools = self.list_all_tools()
        openai_tools = []
        
        for tool in all_tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            })
        
        return openai_tools