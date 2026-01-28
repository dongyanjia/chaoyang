"""
RAG (Retrieval-Augmented Generation) 服务
基于文档知识库的智能问答
"""
import os
from typing import List, Dict, Optional
from document_service import get_document_service

# 尝试导入 OpenAI（如果可用）
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print('[WARN] OpenAI 未安装，将使用简单的文本匹配')

# 配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')


class RAGService:
    """RAG 问答服务"""
    
    def __init__(self, document_service=None):
        self.document_service = document_service or get_document_service()
        self.use_openai = OPENAI_AVAILABLE and OPENAI_API_KEY
    
    def ask_question(self, question: str, area: str = None, max_sources: int = 3) -> Dict:
        """回答问题"""
        # 1. 检索相关文档
        sources = self.document_service.search_documents(question, area, limit=max_sources)
        
        # 2. 构建上下文
        context = self._build_context(sources)
        
        # 3. 生成回答
        if self.use_openai:
            answer = self._generate_with_openai(question, context)
        else:
            answer = self._generate_simple_answer(question, sources)
        
        return {
            "answer": answer,
            "sources": sources
        }
    
    def _build_context(self, sources: List[Dict]) -> str:
        """构建上下文"""
        if not sources:
            return "没有找到相关的文档内容。"
        
        context_parts = []
        for i, source in enumerate(sources, 1):
            context_parts.append(
                f"文档 {i}: {source['name']}\n"
                f"内容: {source['content'][:500]}..."  # 限制长度
            )
        
        return "\n\n".join(context_parts)
    
    def _generate_with_openai(self, question: str, context: str) -> str:
        """使用 OpenAI 生成回答"""
        try:
            openai.api_key = OPENAI_API_KEY
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个智能助手，基于提供的文档内容回答问题。如果文档中没有相关信息，请诚实地说不知道。"
                },
                {
                    "role": "user",
                    "content": f"基于以下文档内容回答问题：\n\n{context}\n\n问题：{question}"
                }
            ]
            
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f'[ERROR] OpenAI 生成回答失败: {e}')
            return self._generate_simple_answer(question, [])
    
    def _generate_simple_answer(self, question: str, sources: List[Dict]) -> str:
        """简单的文本匹配回答（备用方案）"""
        if not sources:
            return "抱歉，我在知识库中没有找到与您的问题相关的信息。请尝试上传相关文档或重新表述您的问题。"
        
        # 找到最相关的文档片段
        best_source = sources[0] if sources else None
        
        if best_source:
            answer = f"根据文档《{best_source['name']}》中的内容：\n\n{best_source['content'][:300]}..."
            
            if len(sources) > 1:
                answer += f"\n\n此外，还有 {len(sources) - 1} 个相关文档可以参考。"
            
            return answer
        
        return "抱歉，无法生成回答。"


# 全局 RAG 服务实例
_rag_service = None

def get_rag_service(document_service=None):
    """获取 RAG 服务实例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService(document_service)
    return _rag_service
