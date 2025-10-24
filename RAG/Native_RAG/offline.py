from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# load document
loader = TextLoader("./knowledge.txt")
documents = loader.load()

# split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 20,
)
splits = text_splitter.split_documents(documents)

# embed chunks
embeddings = OpenAIEmbeddings(
    base_url="https://api.siliconflow.cn/v1",
    model="Qwen/Qwen3-Embedding-0.6B",
)

# store chunks
vector_store = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./vector_store",
)
print("successfully stored chunks")



