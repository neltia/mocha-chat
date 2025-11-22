import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings
from app.utils.prompt_loader import get_prompt


class BlogRAGService:
    def __init__(self, data_dir: str = "backend/data/blog_posts", persist_directory: str = "backend/data/chroma_db"):
        self.data_dir = data_dir
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = None
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.1-8b-instant",
            api_key=settings.GROQ_API_KEY
        )

    def load_and_index(self):
        """
        마크다운 파일을 로드하고 ChromaDB에 인덱싱합니다.

        프로세스:
        1. 디렉터리에서 .md 파일 로드
        2. 청크로 분할 (1000자씩, 200자 겹침)
        3. 각 청크를 벡터로 변환하여 ChromaDB에 저장
        """
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            # Create a dummy file if empty to avoid errors
            with open(os.path.join(self.data_dir, "welcome.md"), "w", encoding="utf-8") as f:
                f.write("# Welcome to the Blog\n\nThis is a sample blog post to initialize the RAG system.")

        loader = DirectoryLoader(self.data_dir, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
        docs = loader.load()

        if not docs:
            print("No documents found to index.")
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        self.vector_store = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )

    def get_retriever(self):
        if not self.vector_store:
            # Try to load existing DB
            if os.path.exists(self.persist_directory):
                self.vector_store = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
            else:
                self.load_and_index()

        return self.vector_store.as_retriever()

    def format_docs(self, docs):
        return "\n\n".join(d.page_content for d in docs)

    def query_test(self, user_query: str) -> str:
        retriever = self.get_retriever()

        # Create a proper ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an assistant for question-answering tasks. "
             "Use the following pieces of retrieved context to answer "
             "the question. If you don't know the answer, say that you "
             "don't know. Use three sentences maximum and keep the "
             "answer concise.\n\n"
             "Context: {context}"),
            ("human", "{question}")
        ])

        # Wrap the static method in RunnableLambda
        rag_chain = (
            {
                "context": retriever | RunnableLambda(self.format_docs),
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        result = rag_chain.invoke(user_query)
        return result

    def query(self, user_query: str, prompt_section: str = "blog_search") -> str:
        """
        RAG 기반 질문 응답

        Args:
            user_query: 사용자 질문
            prompt_section: YAML에서 사용할 프롬프트 섹션

        Returns:
            LLM 생성 답변
        """
        retriever = self.get_retriever()

        # YAML에서 프롬프트 로드
        prompt_data = get_prompt("blog_rag_prompts.yaml", prompt_section)
        system_prompt = prompt_data.get("system", "")
        user_template = prompt_data.get("user", "")

        # ChatPromptTemplate 생성
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_template)
        ])

        # RAG 체인 구성
        rag_chain = (
            {
                "context": retriever | RunnableLambda(self.format_docs),
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        result = rag_chain.invoke(user_query)
        return result


    def query_with_sources(self, user_query: str) -> dict:
        """
        출처 포함 응답 (어떤 문서에서 정보를 가져왔는지 표시)

        Returns:
            {"answer": str, "sources": [{"content": str, "metadata": dict}]}
        """
        retriever = self.get_retriever()

        # 관련 문서 검색
        docs = retriever.invoke(user_query)

        if not docs:
            return {
                "answer": "검색된 관련 문서가 없습니다. 질문을 다시 확인해주세요.",
                "sources": [],
                "context_used": ""
            }

        # 프롬프트 로드
        prompt_data = get_prompt("blog_rag_prompts.yaml", "blog_search")
        system_prompt = prompt_data.get("system", "")
        user_template = prompt_data.get("user", "")

        # 문맥 생성
        context = self.format_docs(docs)

        # ChatPromptTemplate - LangChain이 자동으로 변수를 치환하므로 수동 렌더링 불필요
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_template)
        ])

        # LLM 체인 실행
        chain = prompt | self.llm | StrOutputParser()

        # invoke에 dict 형태로 변수 전달
        answer = chain.invoke({
            "context": context,
            "question": user_query
        })

        # 출처 정보 추출
        sources = []
        for doc in docs:
            source_info = {
                "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                "metadata": doc.metadata,
                "source_file": doc.metadata.get("source", "Unknown")
            }
            sources.append(source_info)

        return {
            "answer": answer,
            "sources": sources,
            "context_used": context[:500] + "..." if len(context) > 500 else context
        }


# Singleton instance or dependency injection could be used
rag_service = BlogRAGService()
