# app/services/knowledge_retriever.py

import os
from langchain_community.document_loaders import JSONLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter

class KnowledgeRetriever:
    def __init__(
        self,
        kb_path: str = "psychology-10k-Deepseek-R1-zh.jsonl",
        deepseek_api_key: str = None,
        deepseek_base_url: str = "https://api.deepseek.com",
        index_path: str = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        top_k: int = 3,
    ):
        if not deepseek_api_key:
            raise ValueError("请在构造时传入 deepseek_api_key 参数，不能依赖环境变量")

        self.kb_path = kb_path
        self.index_path = index_path or f"{kb_path}.faiss"
        self.top_k = top_k
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 嵌入模型：使用 DeepSeek OpenAI 兼容接口
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=deepseek_api_key,
            openai_api_base=deepseek_base_url.rstrip("/")
        )

        # 构建或加载 FAISS 向量库
        self._init_vector_store()

    def _init_vector_store(self):
        if os.path.exists(self.index_path):
            # 如果已存在索引，直接加载
            self.vector_store = FAISS.load_local(self.index_path, self.embeddings)
        else:
            # 按行解析 JSONL，并允许 page_content 是 dict
            loader = JSONLoader(
                file_path=self.kb_path,
                jq_schema="""
                  . | {
                    page_content: (.content | tostring),
                    metadata: {
                      input: .input,
                      reasoning: .reasoning_content
                    }
                  }
                """,
                json_lines=True,      # 启用 JSONL 支持
                text_content=False    # 允许非字符串，自动序列化
            )
            docs = loader.load()

            # 切分文档
            splitter = CharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            split_docs = splitter.split_documents(docs)

            # 创建并保存 FAISS 索引
            self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
            self.vector_store.save_local(self.index_path)

        # 创建检索器
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": self.top_k}
        )

    def retrieve(self, query: str) -> list[str]:
        """
        对外接口：输入查询，返回 top_k 条最相关的文档内容
        """
        docs = self.retriever.get_relevant_documents(query)
        return [doc.page_content for doc in docs]


from langchain_core.embeddings import Embeddings
from openai import OpenAI
import json

class DeepSeekChatEmbeddings(Embeddings):
    def __init__(self, api_key: str, base_url: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def embed_query(self, text: str) -> list[float]:
        # 请求模型将文本转为 JSON 向量
        prompt = (
            f"请将下面文本转换成长度 1536 的浮点向量，用 JSON 列表的形式输出：\n'''{text}'''"
        )
        resp = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        content = resp.choices[0].message.content.strip()
        vector = json.loads(content)
        if not isinstance(vector, list):
            raise ValueError("DeepSeek Chat 未返回 JSON 数组")
        return vector

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(t) for t in texts]
