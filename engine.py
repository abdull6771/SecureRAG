import guardrails as gd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from config import config
from schemas import RAGResponse

class SecureRAGEngine:
    def __init__(self, vectorstore):
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": config.K_RETRIEVAL})
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME, 
            temperature=config.TEMPERATURE,
            api_key=config.OPENAI_API_KEY
        )
        # Initialize Guardrails with Pydantic Schema
        self.guard = gd.Guard.from_pydantic(output_class=RAGResponse)
        self.chain = self._build_chain()

    def _format_docs(self, docs):
        context = ""
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            context += f"Source: {source}\nContent: {doc.page_content}\n\n"
        return context

    def _build_chain(self):
        system_prompt = """
        You are a secure AI assistant. 
        Answer the user question based ONLY on the following Context.
        
        Context:
        {context}
        
        Rules:
        1. If the answer is present, extract it and cite sources. Set confidence to "high".
        2. If the answer is missing, return exactly: "I do not have enough information in the provided documents." and set confidence to "low".
        3. OUTPUT FORMAT: You must return a valid JSON object matching the requested schema.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{question}"),
        ])

        # LCEL Pipeline: Retrieve -> Format -> Prompt -> LLM -> String
        return (
            {
                "context": self.retriever | self._format_docs, 
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def query(self, user_query: str) -> dict:
        """Executes the guarded pipeline."""
        
        # 1. Input Guard (Basic Example)
        if len(user_query) < 3:
            return RAGResponse(
                answer="Query too short.", 
                confidence="low", 
                sources=[]
            ).model_dump()

        try:
            # 2. LLM Generation
            print("🤖 Generating response...")
            raw_response = self.chain.invoke(user_query)
            
            # 3. Guardrails Validation & Repair
            # This ensures the output is valid JSON conforming to RAGResponse
            validated_response = self.guard.parse(raw_response)
            
            return validated_response.validated_output
            
        except Exception as e:
            # Fallback for system errors
            return {
                "answer": f"System Error: {str(e)}",
                "confidence": "low",
                "sources": []
            }