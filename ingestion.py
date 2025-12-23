import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from config import config

class KnowledgeBase:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)
        self.vectorstore = None

    def load_documents(self) -> List[Document]:
        """Loads documents from the configured directory."""
        if not os.path.exists(config.DOCS_PATH):
            os.makedirs(config.DOCS_PATH)
            # Create dummy file for testing
            with open(f"{config.DOCS_PATH}/sample.txt", "w") as f:
                f.write("Guardrails AI ensures LLMs follow strict validation rules. LangChain orchestrates the logic.")
            
        docs = []
        loaders = {".txt": TextLoader, ".pdf": PyPDFLoader}
        
        print(f"📂 Scanning {config.DOCS_PATH}...")
        for root, _, files in os.walk(config.DOCS_PATH):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in loaders:
                    try:
                        loader = loaders[ext](os.path.join(root, file))
                        docs.extend(loader.load())
                    except Exception as e:
                        print(f"❌ Error loading {file}: {e}")
        return docs

    def get_vector_store(self, force_rebuild: bool = False):
        """Builds or loads the FAISS vector store."""
        if os.path.exists(config.VECTOR_STORE_PATH) and not force_rebuild:
            print("💾 Loading existing Vector Store...")
            self.vectorstore = FAISS.load_local(
                config.VECTOR_STORE_PATH, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            return self.vectorstore

        print("⚡ Building new Vector Store...")
        docs = self.load_documents()
        
        if not docs:
            raise ValueError("No documents found. Add .txt or .pdf files to 'documents/'")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        splits = text_splitter.split_documents(docs)
        
        self.vectorstore = FAISS.from_documents(splits, self.embeddings)
        self.vectorstore.save_local(config.VECTOR_STORE_PATH)
        return self.vectorstore