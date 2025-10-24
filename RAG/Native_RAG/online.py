from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

embeddings = OpenAIEmbeddings(
    base_url="https://api.siliconflow.cn/v1",
    model="Qwen/Qwen3-Embedding-0.6B",
)
vectorstore = Chroma(persist_directory="./vector_store", embedding_function=embeddings)

query = "什么是RAG？"

documents = vectorstore.similarity_search(query, k=3)

context = "\n".join([doc.page_content for doc in documents])

prompt = PromptTemplate(
    template="""
    你是一个专业的问答助手。请根据以下参考文档回答用户的问题。
    如果参考文档中没有相关信息，请诚实地说不知道，不要编造答案。

    参考文档：{context}

    用户问题：{query}

    回答：
    """,
    input_variables=["context", "query"]
)
chain = prompt | ChatOpenAI(
    model="THUDM/glm-4-9b-chat",
    temperature=0,
    max_retries=3,
    base_url="https://api.siliconflow.cn/v1",
    api_key=API_KEY,
)

result = chain.invoke({"context": context, "query": query})
print(result.content)


