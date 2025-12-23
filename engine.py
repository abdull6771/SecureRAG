import guardrails as gd
import json
from typing import Optional, List, Dict, AsyncIterator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
import redis

from config import config, logger
from schemas import RAGResponse

class ConversationMemory:
    """Manages conversation history with Redis backend."""
    
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                password=config.REDIS_PASSWORD if config.REDIS_PASSWORD else None,
                decode_responses=True
            )
            self.redis_client.ping()
            self.use_redis = True
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning("Redis unavailable, using in-memory storage", error=str(e))
            self.use_redis = False
            self.memory_store = {}
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to conversation history."""
        message = {"role": role, "content": content}
        
        if self.use_redis:
            key = f"conversation:{session_id}"
            self.redis_client.rpush(key, json.dumps(message))
            self.redis_client.expire(key, 3600)  # 1 hour TTL
        else:
            if session_id not in self.memory_store:
                self.memory_store[session_id] = []
            self.memory_store[session_id].append(message)
    
    def get_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve conversation history."""
        if self.use_redis:
            key = f"conversation:{session_id}"
            messages = self.redis_client.lrange(key, -limit, -1)
            return [json.loads(msg) for msg in messages]
        else:
            return self.memory_store.get(session_id, [])[-limit:]
    
    def clear_history(self, session_id: str):
        """Clear conversation history for a session."""
        if self.use_redis:
            self.redis_client.delete(f"conversation:{session_id}")
        else:
            self.memory_store.pop(session_id, None)

class SecureRAGEngine:
    def __init__(self, vectorstore, enable_memory: bool = True):
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": config.K_RETRIEVAL})
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME, 
            temperature=config.TEMPERATURE,
            api_key=config.OPENAI_API_KEY
        )
        # Initialize Guardrails with Pydantic Schema
        self.guard = gd.Guard.from_pydantic(output_class=RAGResponse)
        self.chain = self._build_chain()
        self.memory = ConversationMemory() if enable_memory else None
        logger.info("SecureRAG engine initialized", 
                   model=config.MODEL_NAME, 
                   memory_enabled=enable_memory)

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

    def query(self, user_query: str, session_id: Optional[str] = None) -> dict:
        """Executes the guarded pipeline with optional conversation memory."""
        
        # 1. Input Guard (Basic Example)
        if len(user_query) < 3:
            logger.warning("Query too short", query_length=len(user_query))
            return RAGResponse(
                answer="Query too short.", 
                confidence="low", 
                sources=[]
            ).model_dump()

        try:
            # 2. Add conversation context if memory is enabled
            if self.memory and session_id:
                history = self.memory.get_history(session_id)
                logger.info("Retrieved conversation history", 
                           session_id=session_id, 
                           message_count=len(history))
            
            # 3. LLM Generation
            logger.info("Generating response", query=user_query[:100])
            raw_response = self.chain.invoke(user_query)
            
            # 4. Guardrails Validation & Repair
            validated_response = self.guard.parse(raw_response)
            result = validated_response.validated_output
            
            # 5. Save to conversation memory
            if self.memory and session_id:
                self.memory.add_message(session_id, "user", user_query)
                self.memory.add_message(session_id, "assistant", result["answer"])
                logger.info("Saved to conversation memory", session_id=session_id)
            
            logger.info("Query completed successfully", 
                       confidence=result.get("confidence"),
                       sources_count=len(result.get("sources", [])))
            return result
            
        except Exception as e:
            # Fallback for system errors
            logger.error("Query failed", error=str(e), query=user_query[:100])
            return {
                "answer": f"System Error: {str(e)}",
                "confidence": "low",
                "sources": []
            }
    
    async def query_stream(self, user_query: str, session_id: Optional[str] = None) -> AsyncIterator[str]:
        """Executes the pipeline with streaming response."""
        
        if len(user_query) < 3:
            yield json.dumps({"error": "Query too short"})
            return
        
        try:
            logger.info("Starting streaming query", query=user_query[:100])
            
            # Stream LLM response
            streaming_llm = ChatOpenAI(
                model=config.MODEL_NAME,
                temperature=config.TEMPERATURE,
                api_key=config.OPENAI_API_KEY,
                streaming=True
            )
            
            # Get context
            docs = self.retriever.get_relevant_documents(user_query)
            context = self._format_docs(docs)
            
            system_prompt = f"""
            You are a secure AI assistant. 
            Answer the user question based ONLY on the following Context.
            
            Context:
            {context}
            
            Rules:
            1. If the answer is present, extract it and cite sources.
            2. If the answer is missing, return: "I do not have enough information."
            """
            
            # Stream response
            full_response = ""
            async for chunk in streaming_llm.astream([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]):
                if chunk.content:
                    full_response += chunk.content
                    yield chunk.content
            
            # Save to memory after streaming completes
            if self.memory and session_id:
                self.memory.add_message(session_id, "user", user_query)
                self.memory.add_message(session_id, "assistant", full_response)
            
            logger.info("Streaming query completed")
            
        except Exception as e:
            logger.error("Streaming query failed", error=str(e))
            yield json.dumps({"error": str(e)})