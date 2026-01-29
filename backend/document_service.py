"""
文档服务模块
处理文档上传、解析、向量化和存储
"""
import os
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional
import pymysql

# 可选依赖
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    print('[WARN] PyPDF2 未安装，PDF 解析功能不可用')

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print('[WARN] python-docx 未安装，Word 文档解析功能不可用')

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print('[WARN] pandas 未安装，Excel 解析功能不可用')

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print('[WARN] chromadb 未安装，向量存储功能不可用')

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print('[WARN] sentence-transformers 未安装，向量化功能不可用')

# 初始化向量数据库
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), 'chroma_db')
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

# 初始化 ChromaDB 客户端
chroma_client = None
if CHROMADB_AVAILABLE:
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        print('[OK] ChromaDB 客户端初始化成功')
    except Exception as e:
        print(f'[WARN] ChromaDB 客户端初始化失败: {e}')
        chroma_client = None
else:
    print('[WARN] ChromaDB 未安装，向量存储功能不可用')

# 初始化嵌入模型（使用轻量级的中文模型）
embedding_model = None
if SENTENCE_TRANSFORMERS_AVAILABLE:
    try:
        embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print('[OK] 嵌入模型加载成功')
    except Exception as e:
        print(f'[WARN] 嵌入模型加载失败: {e}，将使用备用方案')
        embedding_model = None
else:
    print('[WARN] sentence-transformers 未安装，向量化功能不可用')

# 文档存储目录
DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), 'documents')
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(os.path.join(DOCUMENTS_DIR, 'public'), exist_ok=True)
os.makedirs(os.path.join(DOCUMENTS_DIR, 'personal'), exist_ok=True)


class DocumentService:
    """文档服务类"""
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.collection = None
        self._init_collection()
        self._init_database()
    
    def _init_collection(self):
        """初始化 ChromaDB 集合"""
        if not chroma_client:
            self.collection = None
            return
        
        try:
            # 获取或创建集合
            self.collection = chroma_client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            print('[OK] ChromaDB 集合初始化成功')
        except Exception as e:
            print(f'[ERROR] ChromaDB 集合初始化失败: {e}')
            self.collection = None
    
    def _init_database(self):
        """初始化数据库表"""
        if not self.db_connection:
            return
        
        try:
            # 如果传入的是 Database 对象，获取其 connection
            if hasattr(self.db_connection, 'connection'):
                conn = self.db_connection.connection
            else:
                conn = self.db_connection
            
            if not conn:
                return
            
            cursor = conn.cursor()
            # 使用 Doris 语法创建表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    file_type VARCHAR(50) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_size BIGINT NOT NULL,
                    area VARCHAR(20) NOT NULL,
                    upload_user VARCHAR(100),
                    upload_time VARCHAR(50),
                    vector_id VARCHAR(255),
                    metadata TEXT
                )
                UNIQUE KEY(id)
                DISTRIBUTED BY HASH(id) BUCKETS 10
                PROPERTIES (
                    "replication_num" = "1"
                )
            ''')
            if hasattr(self.db_connection, 'connection'):
                self.db_connection.connection.commit()
            else:
                self.db_connection.commit()
            print('[OK] 文档表初始化成功')
        except Exception as e:
            print(f'[ERROR] 文档表初始化失败: {e}')
            import traceback
            traceback.print_exc()
    
    def save_document(self, file, area: str, user: str = None) -> Dict:
        """保存文档并解析内容"""
        try:
            # 生成文件哈希作为唯一ID
            file_content = file.read()
            file.seek(0)  # 重置文件指针
            file_hash = hashlib.md5(file_content).hexdigest()
        except Exception as e:
            print(f'[ERROR] 读取文件失败: {e}')
            raise Exception(f'读取文件失败: {str(e)}')
        
        # 获取文件信息
        file_name = file.filename
        file_ext = os.path.splitext(file_name)[1].lower()
        file_type = file_ext[1:] if file_ext.startswith('.') else file_ext
        
        # 保存文件
        area_dir = os.path.join(DOCUMENTS_DIR, area)
        os.makedirs(area_dir, exist_ok=True)
        file_path = os.path.join(area_dir, f"{file_hash}_{file_name}")
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # 解析文档内容
        text_content = self._parse_document(file_path, file_type)
        
        # 向量化并存储
        vector_id = None
        chunks_count = 0
        if text_content and self.collection and embedding_model:
            try:
                # 分块处理（每块500字符）
                chunks = self._chunk_text(text_content, chunk_size=500)
                chunks_count = len(chunks)
                
                # 生成向量
                embeddings = embedding_model.encode(chunks)
                
                # 存储到 ChromaDB
                ids = [f"{file_hash}_{i}" for i in range(len(chunks))]
                metadatas = [
                    {
                        "document_id": file_hash,
                        "document_name": file_name,
                        "area": area,
                        "chunk_index": i,
                        "file_type": file_type
                    }
                    for i in range(len(chunks))
                ]
                
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings.tolist(),
                    documents=chunks,
                    metadatas=metadatas
                )
                
                vector_id = file_hash
                print(f'[OK] 文档向量化成功: {len(chunks)} 个块')
            except Exception as e:
                print(f'[ERROR] 文档向量化失败: {e}')
                import traceback
                traceback.print_exc()
        
        # 保存到数据库
        doc_id = None
        if self.db_connection:
            try:
                # 如果传入的是 Database 对象，获取其 connection
                if hasattr(self.db_connection, 'connection'):
                    conn = self.db_connection.connection
                else:
                    conn = self.db_connection
                
                if conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO documents 
                        (name, file_type, file_path, file_size, area, upload_user, upload_time, vector_id, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        file_name,
                        file_type,
                        file_path,
                        len(file_content),
                        area,
                        user,
                        datetime.now().isoformat(),
                        vector_id,
                        json.dumps({"chunks": chunks_count})
                    ))
                    if hasattr(self.db_connection, 'connection'):
                        self.db_connection.connection.commit()
                    else:
                        self.db_connection.commit()
                    doc_id = cursor.lastrowid
            except Exception as e:
                print(f'[ERROR] 保存文档到数据库失败: {e}')
                import traceback
                traceback.print_exc()
        
        # 确保至少文件已保存
        if not os.path.exists(file_path):
            raise Exception('文件保存失败')
        
        result = {
            "id": doc_id or 0,
            "name": file_name,
            "file_type": file_type,
            "size": len(file_content),
            "area": area,
            "upload_time": datetime.now().isoformat(),
            "vector_id": vector_id
        }
        
        # 如果数据库保存失败，至少返回文件已保存的信息
        if doc_id is None:
            print('[WARN] 文档已保存到文件系统，但数据库保存失败')
            # 仍然返回结果，但 id 为 0 表示未保存到数据库
        
        return result
    
    def _parse_document(self, file_path: str, file_type: str) -> str:
        """解析文档内容"""
        try:
            if file_type == 'pdf':
                return self._parse_pdf(file_path)
            elif file_type in ['doc', 'docx']:
                return self._parse_docx(file_path)
            elif file_type in ['xls', 'xlsx']:
                return self._parse_excel(file_path)
            elif file_type == 'txt':
                return self._parse_txt(file_path)
            else:
                return ""
        except Exception as e:
            print(f'[ERROR] 解析文档失败: {e}')
            return ""
    
    def _parse_pdf(self, file_path: str) -> str:
        """解析 PDF 文件"""
        if not PYPDF2_AVAILABLE:
            print('[WARN] PyPDF2 未安装，无法解析 PDF 文件')
            return ""
        
        text = ""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f'[ERROR] PDF 解析失败: {e}')
        return text
    
    def _parse_docx(self, file_path: str) -> str:
        """解析 Word 文档"""
        if not DOCX_AVAILABLE:
            print('[WARN] python-docx 未安装，无法解析 Word 文档')
            return ""
        
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f'[ERROR] Word 文档解析失败: {e}')
        return text
    
    def _parse_excel(self, file_path: str) -> str:
        """解析 Excel 文件"""
        if not PANDAS_AVAILABLE:
            print('[WARN] pandas 未安装，无法解析 Excel 文件')
            return ""
        
        text = ""
        try:
            df = pd.read_excel(file_path)
            # 将 DataFrame 转换为文本
            text = df.to_string(index=False)
        except Exception as e:
            print(f'[ERROR] Excel 解析失败: {e}')
        return text
    
    def _parse_txt(self, file_path: str) -> str:
        """解析文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f'[ERROR] 文本文件解析失败: {e}')
            return ""
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """将文本分块"""
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def get_documents(self, area: str, user: str = None) -> List[Dict]:
        """获取文档列表"""
        if not self.db_connection:
            return []
        
        try:
            # 如果传入的是 Database 对象，获取其 connection
            if hasattr(self.db_connection, 'connection'):
                conn = self.db_connection.connection
            else:
                conn = self.db_connection
            
            if not conn:
                return []
            
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            if area == 'personal' and user:
                cursor.execute('''
                    SELECT id, name, file_type, file_size as size, area, upload_time
                    FROM documents
                    WHERE area = %s AND upload_user = %s
                    ORDER BY upload_time DESC
                ''', (area, user))
            else:
                cursor.execute('''
                    SELECT id, name, file_type, file_size as size, area, upload_time
                    FROM documents
                    WHERE area = %s
                    ORDER BY upload_time DESC
                ''', (area,))
            
            return cursor.fetchall()
        except Exception as e:
            print(f'[ERROR] 获取文档列表失败: {e}')
            import traceback
            traceback.print_exc()
            return []
    
    def delete_document(self, doc_id: int) -> bool:
        """删除文档"""
        if not self.db_connection:
            return False
        
        try:
            # 如果传入的是 Database 对象，获取其 connection
            if hasattr(self.db_connection, 'connection'):
                conn = self.db_connection.connection
            else:
                conn = self.db_connection
            
            if not conn:
                return False
            
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            # 获取文档信息
            cursor.execute('SELECT vector_id, file_path FROM documents WHERE id = %s', (doc_id,))
            doc = cursor.fetchone()
            
            if doc:
                # 删除向量数据
                if doc['vector_id'] and self.collection:
                    try:
                        # 获取所有相关的向量ID
                        results = self.collection.get(
                            where={"document_id": doc['vector_id']}
                        )
                        if results['ids']:
                            self.collection.delete(ids=results['ids'])
                    except Exception as e:
                        print(f'[WARN] 删除向量数据失败: {e}')
                
                # 删除文件
                if os.path.exists(doc['file_path']):
                    os.remove(doc['file_path'])
                
                # 删除数据库记录
                cursor.execute('DELETE FROM documents WHERE id = %s', (doc_id,))
                if hasattr(self.db_connection, 'connection'):
                    self.db_connection.connection.commit()
                else:
                    self.db_connection.commit()
                return True
        except Exception as e:
            print(f'[ERROR] 删除文档失败: {e}')
            import traceback
            traceback.print_exc()
            if self.db_connection:
                if hasattr(self.db_connection, 'connection'):
                    try:
                        self.db_connection.connection.rollback()
                    except:
                        pass
                elif hasattr(self.db_connection, 'rollback'):
                    try:
                        self.db_connection.rollback()
                    except:
                        pass
        
        return False
    
    def search_documents(self, query: str, area: str = None, limit: int = 5) -> List[Dict]:
        """搜索相关文档"""
        if not self.collection or not embedding_model:
            return []
        
        try:
            # 生成查询向量
            query_embedding = embedding_model.encode([query])[0]
            
            # 构建查询条件
            where = {}
            if area:
                where["area"] = area
            
            # 搜索
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=limit,
                where=where if where else None
            )
            
            # 格式化结果
            sources = []
            if results and 'ids' in results and results['ids'] and len(results['ids'][0]) > 0:
                for i, doc_id in enumerate(results['ids'][0]):
                    sources.append({
                        "document_id": results['metadatas'][0][i].get('document_id') if 'metadatas' in results and results['metadatas'] else None,
                        "name": results['metadatas'][0][i].get('document_name', '未知') if 'metadatas' in results and results['metadatas'] else '未知',
                        "content": results['documents'][0][i] if 'documents' in results and results['documents'] else '',
                        "score": 1 - results['distances'][0][i] if 'distances' in results and results['distances'] and len(results['distances'][0]) > i else 0.8
                    })
            
            return sources
        except Exception as e:
            print(f'[ERROR] 搜索文档失败: {e}')
            import traceback
            traceback.print_exc()
            return []


# 全局文档服务实例
_document_service = None

def get_document_service(db_connection=None):
    """获取文档服务实例"""
    global _document_service
    # 每次都创建新实例，确保使用正确的数据库连接
    # 因为每个请求可能有不同的数据库连接
    if db_connection:
        return DocumentService(db_connection)
    # 如果没有传入连接，使用全局实例（如果存在）
    if _document_service is None:
        _document_service = DocumentService(db_connection)
    return _document_service
