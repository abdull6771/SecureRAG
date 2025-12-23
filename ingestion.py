import os
from typing import List, Optional, Dict
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from config import config, logger

class KnowledgeBase:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)
        self.vectorstore = None
        logger.info("Knowledge base initialized")

    def load_documents(self, filter_metadata: Optional[Dict] = None) -> List[Document]:
        """Loads documents from the configured directory with optional metadata filtering."""
        if not os.path.exists(config.DOCS_PATH):
            os.makedirs(config.DOCS_PATH)
            logger.info("Created documents directory", path=config.DOCS_PATH)
            # Create dummy file for testing
            with open(f"{config.DOCS_PATH}/sample.txt", "w") as f:
                f.write("Guardrails AI ensures LLMs follow strict validation rules. LangChain orchestrates the logic.")
            logger.info("Created sample document")
            
        docs = []
        loaders = {".txt": TextLoader, ".pdf": PyPDFLoader}
        
        logger.info("Scanning documents directory", path=config.DOCS_PATH)
        for root, _, files in os.walk(config.DOCS_PATH):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in loaders:
                    try:
                        file_path = os.path.join(root, file)
                        loader = loaders[ext](file_path)
                        loaded_docs = loader.load()
                        
                        # Add enhanced metadata
                        for doc in loaded_docs:
                            doc.metadata.update({
                                "filename": file,
                                "extension": ext,
                                "upload_date": datetime.now().isoformat(),
                                "file_size": os.path.getsize(file_path)
                            })
                        
                        # Apply metadata filtering if provided
                        if filter_metadata:
                            loaded_docs = [
                                doc for doc in loaded_docs
                                if all(doc.metadata.get(k) == v for k, v in filter_metadata.items())
                            ]
                        
                        docs.extend(loaded_docs)
                        logger.info("Loaded document", filename=file, doc_count=len(loaded_docs))
                    except Exception as e:
                        logger.error("Failed to load document", filename=file, error=str(e))
        
        logger.info("Document loading complete", total_docs=len(docs))
        return docs

    def get_vector_store(self, force_rebuild: bool = False):
        """Builds or loads the FAISS vector store."""
        if os.path.exists(config.VECTOR_STORE_PATH) and not force_rebuild:
            logger.info("Loading existing vector store", path=config.VECTOR_STORE_PATH)
            self.vectorstore = FAISS.load_local(
                config.VECTOR_STORE_PATH, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            return self.vectorstore

        logger.info("Building new vector store")
        docs = self.load_documents()
        
        if not docs:
            logger.error("No documents found for vector store creation")
            raise ValueError("No documents found. Add .txt or .pdf files to 'documents/'")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        splits = text_splitter.split_documents(docs)
        logger.info("Document splitting complete", chunk_count=len(splits))
        
        self.vectorstore = FAISS.from_documents(splits, self.embeddings)
        self.vectorstore.save_local(config.VECTOR_STORE_PATH)
        logger.info("Vector store saved", path=config.VECTOR_STORE_PATH)
        return self.vectorstore