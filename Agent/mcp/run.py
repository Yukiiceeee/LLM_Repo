"""
MCP Demo - 完整示例
演示如何使用MCP构建AI Agent
"""
from mcp_server.email_server import email_server
from mcp_client.client import MCPClient
from agent import MCPAgent


def main():
    print("=" * 60)
    print("🚀 MCP Demo - AI Agent with Tool Calling")
    print("=" * 60)
    
    # 步骤1: 创建MCP客户端
    print("\n📦 步骤1: 初始化MCP客户端")
    mcp_client = MCPClient()
    
    # 步骤2: 连接MCP服务器
    print("\n📦 步骤2: 连接MCP服务器")
    mcp_client.connect_server("email-server", email_server)
    
    # 步骤3: 查看可用工具
    print("\n📦 步骤3: 发现可用工具")
    tools = mcp_client.list_all_tools()
    print(f"   发现 {len(tools)} 个可用工具:")
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description']}")
    
    # 步骤4: 创建AI Agent
    print("\n📦 步骤4: 创建AI Agent")
    agent = MCPAgent(mcp_client)
    
    # 步骤5: 与Agent交互
    print("\n📦 步骤5: 开始与Agent交互")
    print("=" * 60)
    
    # 示例1: 发送邮件
    agent.chat("请帮我给 zhangsan@example.com 发送一封邮件，主题是'项目进度更新'，内容是'本周项目进展顺利，已完成75%的开发任务。'")
    
    print("\n" + "=" * 60)
    
    # 示例2: 查询收件箱
    agent.chat("查看一下我的收件箱有多少未读邮件")
    
    print("\n" + "=" * 60)
    
    # 示例3: 复杂任务（多步骤）
    agent.reset()  # 重置对话历史
    agent.chat("先查一下收件箱情况，然后给 lisi@example.com 发一封邮件告诉他我会在周五回复他")
    
    print("\n" + "=" * 60)
    print("✅ Demo完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()