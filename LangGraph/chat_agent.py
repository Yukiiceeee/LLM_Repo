from dotenv import load_dotenv
import os

load_dotenv(".env")

BASE_URL = "https://api.deepseek.com"
API_KEY = os.environ.get("API_KEY")

deepseek_chat_model = "deepseek-chat"

# 1. langchain: init model,invoke,prompt template
# 2. langgraph memory
# 3. langgraph create_react_agent

from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

llm1 = ChatOpenAI(model=deepseek_chat_model, api_key=API_KEY, base_url=BASE_URL)

result = llm1.invoke([HumanMessage("给我讲个笑话吧")])
print(result.content)

from langchain.chat_models import init_chat_model

llm2 = init_chat_model(
    deepseek_chat_model,
    api_key=API_KEY,
    base_url=BASE_URL
)

result = llm2.invoke([HumanMessage("给我讲个笑话吧")])
print(result.content)

# 构建prompt template
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate(
    [
        ("system", "你是一个笑话大王，请给我讲个笑话"),
        ("user", "帮我写一个主题为{topic}的笑话")
    ]
)

prompt.invoke({"topic": "狗"}).to_messages()
print(prompt.input_variables)

# langchian里chain的体现
# | 连接的两侧必须是可以被invoke的，在调用时会自动调用两侧的invoke方法
# 左边的输出会作为右边的输入
chain = prompt | llm1

ans = chain.invoke(
    {"topic": "狗"}
)

print(ans.content)

from pydantic import BaseModel, Field

# class Joke(BaseModel):
#     "joke to tell user"
#     setup: str = Field(description="The setup of the joke")
#     punchline: str = Field(description="The punchline of the joke")

# joke_chain = prompt | ChatOpenAI(
#     model=deepseek_chat_model,
#     api_key=API_KEY,
#     base_url=BASE_URL
# ).with_structured_output(Joke)

# ans = joke_chain.invoke({"topic": "狗"})
# print(ans.setup)
# print(ans.punchline)

# memory: message & output, 通过维护图结构来保存

# class MessagesState(TypedDict):
#     messages: Annotated[list[AnyMessage], add_messages]
#     {
#         "messages": []
#     }


from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, START, StateGraph, END

workflow = StateGraph(MessagesState)

def call_model(state: MessagesState):
    return {"messages": [llm1.invoke(state["messages"])]}

workflow.add_node("node1", call_model)
workflow.add_edge(START, "node1")

# Add Memory
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# config标识线程id，是通过线程id来存储历史消息的
config = {"configurable": {"thread_id": "1"}}
query = "你好啊，我是Cyan。"

input_messages = {"messages": [HumanMessage(content=query)]}
output_messages = graph.invoke(input_messages, config=config)
print(output_messages["messages"][-1].content) 
# 这里的output包含所有历史消息，langgraph做了一个消息拼接，[-1] 获取最后一条消息（最新的AI回复）

query = "我叫什么名字？"
input_messages = {"messages": [HumanMessage(content=query)]}
output_messages = graph.invoke(input_messages, config=config)
print(output_messages["messages"][-1].content)

from langgraph.prebuilt import create_react_agent

def add(a:int, b:int):
    # docstring是必要的，langchain会根据docstring生成工具的描述
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The sum of a and b
    """
    return a + b

def multiply(a:int, b:int):
    """Multiply two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The product of a and b
    """
    return a * b

agent = create_react_agent(
    model=llm1,
    tools=[add, multiply],
)

input_messages = {"messages": [HumanMessage("计算10+20，然后计算10*20")]}
output_messages = agent.invoke(input_messages)

for message in output_messages["messages"]:
    print(message.content)



