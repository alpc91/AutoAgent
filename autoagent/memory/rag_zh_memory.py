import os
import re
import zipfile
import uuid
import math
import chromadb
import numpy as np
from datetime import datetime
from typing import List, Dict, Union
from chromadb.utils import embedding_functions
from chromadb.api.types import QueryResult
import jieba

chromadb.logger.setLevel(chromadb.logging.ERROR)
import torch

class ChineseMarkdownConverter:
    """中文文档增强处理器"""
    def __init__(self, chunk_size=512, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # 初始化jieba分词器
        jieba.initialize()

    def preprocess_text(self, text: str) -> str:
        # 中文文本预处理
        text = text.replace(u'\u3000', u' ')  # 全角空格转半角
        text = re.sub(r'\r\n', '\n', text)    # 统一换行符
        text = re.sub(r'([。！？；])([^"\'])', r'\1\n\2', text)  # 按中文标点分段
        return text.strip()

    def split_text(self, text: str) -> List[str]:
        """使用jieba分词并按照指定大小分块"""
        # 使用jieba分词
        sentences = re.split(r'([。！？；\n])', text)
        sentences = [''.join(i) for i in zip(sentences[0::2], sentences[1::2] + [''])]
        sentences = [s for s in sentences if s.strip()]

        # 按大小分块
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # 如果单个句子超过chunk_size，进一步分割
            if sentence_length > self.chunk_size:
                words = list(jieba.cut(sentence))
                # 小段落按词分块
                for i in range(0, len(words), self.chunk_size // 2):
                    sub_sentence = ''.join(words[i:i + self.chunk_size // 2])
                    if sub_sentence:
                        chunks.append(sub_sentence)
                continue
                
            # 如果添加当前句子会超过chunk_size，先保存当前chunk
            if current_length + sentence_length > self.chunk_size:
                if current_chunk:
                    chunks.append(''.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # 添加最后一个chunk
        if current_chunk:
            chunks.append(''.join(current_chunk))
            
        return chunks

    def convert_file(self, file_path: str) -> List[Dict]:
        # 读取文件并分块
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        processed_text = self.preprocess_text(text)
        chunks = self.split_text(processed_text)
        
        return [{
            "content": chunk,
            "metadata": {
                "source": os.path.basename(file_path),
                "file_type": file_path.split('.')[-1],
                "chunk_index": i
            }
        } for i, chunk in enumerate(chunks)]
    
    def convert_text(self, text: str) -> List[Dict]:
        processed_text = self.preprocess_text(text)
        chunks = self.split_text(processed_text)
        
        return [{
            "content": chunk,
            "metadata": {
                "source": "text_input",
                "chunk_index": i
            }
        } for i, chunk in enumerate(chunks)]

class EnhancedMemory:
    """增强版记忆管理系统"""
    def __init__(self, project_path: str, db_name: str = '.rag_db'):
        self.client = chromadb.PersistentClient(path=os.path.join(project_path, db_name))
        print(f"连接到数据库: {os.path.join(project_path, db_name)}")
        # self.embedder = embedding_functions.DefaultEmbeddingFunction()
        self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-large-zh-v1.5",
            device="cuda" if torch.cuda.is_available() else "cpu",
            normalize_embeddings=True,
            local_files_only=True
        )
    
    def create_collection(self, collection_name: str):
        return self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedder
        )

    def ingest_documents(
        self,
        file_paths: List[str],
        collection_name: str,
        overwrite: bool = False,
        batch_size: int = 200
    ) -> str:
        # 创建或获取集合
        collection = self.create_collection(collection_name)
        if overwrite and collection.count() > 0:
            self.client.delete_collection(name=collection_name)
            collection = self.create_collection(collection_name)

        # 文档处理
        converter = ChineseMarkdownConverter()
        total_chunks = 0
        
        for file_path in file_paths:
            chunks = converter.convert_file(file_path)
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                # 构建元数据
                metadata = chunk['metadata']
                metadata.update({
                    "ingest_time": datetime.now().isoformat(),
                    "document_id": str(uuid.uuid4())
                })
                
                documents.append(chunk['content'])
                metadatas.append(metadata)
                ids.append(f"{metadata['source']}_{metadata['chunk_index']}")

            # 分批插入
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_meta = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                
                collection.add(
                    documents=batch_docs,
                    metadatas=batch_meta,
                    ids=batch_ids
                )
            
            total_chunks += len(documents)
        
        return f"成功存储 {total_chunks} 个文本块到集合 {collection_name}"

    def hybrid_search(
        self,
        query: str,
        collection_name: str,
        n_results: int = 5,
        keyword_filter: str = None
    ) -> Dict:
        collection = self.create_collection(collection_name)
        
        # 构建查询条件
        where = None
        if keyword_filter:
            where = {"$or": [
                {"metadata.source": {"$contains": keyword_filter}},
                {"metadata.keywords": {"$contains": keyword_filter}}
            ]}
        
        # 执行混合检索
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        # 重组结果
        return {
            "documents": results['documents'][0],
            "sources": [m['source'] for m in results['metadatas'][0]],
            "scores": [1 - d for d in results['distances'][0]]  # 转换为相似度分数
        }
    
    def add_text(
        self,
        text: List[Dict[str, str]],
        collection_name: str = None,
        batch_size: int = 200
    ) -> List[str]:
        
        collection = self.create_collection(collection_name)

        converter = ChineseMarkdownConverter()
        total_chunks = 0

        chunks = converter.convert_text(text)
        documents = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            # 构建元数据
            metadata = chunk['metadata']
            metadata.update({
                "ingest_time": datetime.now().isoformat(),
                "document_id": str(uuid.uuid4())
            })
            
            documents.append(chunk['content'])
            metadatas.append(metadata)
            ids.append(f"{metadata['source']}_{metadata['chunk_index']}")

        # 分批插入
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            collection.add(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids
            )
        
        total_chunks += len(documents)
        
        return f"成功存储 {total_chunks} 个文本块到集合 {collection_name}"

        

class RAGPipeline:
    """端到端RAG流水线"""
    def __init__(self, workspace: str = "./workspace"):
        self.workspace = workspace
        self.memory = EnhancedMemory(workspace)
        os.makedirs(os.path.join(workspace, "docs"), exist_ok=True)

    def process_input(
        self,
        input_path: str,
        collection_name: str,
        overwrite: bool = False
    ) -> str:
        # 支持多种输入类型
        if input_path.endswith('.zip'):
            return self._process_zip(input_path, collection_name, overwrite)
        elif os.path.isdir(input_path):
            return self._process_directory(input_path, collection_name, overwrite)
        else:
            return self._process_single_file(input_path, collection_name, overwrite)

    def _process_zip(self, zip_path: str, collection_name: str, overwrite: bool) -> str:
        extract_dir = os.path.splitext(zip_path)[0]
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        return self._process_directory(extract_dir, collection_name, overwrite)

    def _process_directory(self, dir_path: str, collection_name: str, overwrite: bool) -> str:
        file_paths = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.split('.')[-1].lower() in ['txt', 'md', 'pdf', 'docx']:
                    file_paths.append(os.path.join(root, file))
        return self.memory.ingest_documents(file_paths, collection_name, overwrite)

    def _process_single_file(self, file_path: str, collection_name: str, overwrite: bool) -> str:
        return self.memory.ingest_documents([file_path], collection_name, overwrite)

    def query(self, question: str, collection_name: str, top_k: int = 3) -> Dict:
        return self.memory.hybrid_search(question, collection_name, top_k)
    
    
    def add_text(self, text: str, collection_name: str) -> str:
        return self.memory.add_text(text, collection_name)

# 使用示例
if __name__ == "__main__":
    # 初始化流水线
    rag = RAGPipeline("./rag_db")
    
    # 处理文档（示例路径）
    result = rag.process_input(
        input_path="./rag_docs/",
        collection_name="base_info",
        overwrite=True
    )
    print(result)
    
    # 执行查询
    question = "数据库说了啥？"
    results = rag.query(question, "base_info", top_k=3)
    
    print("\n检索结果：")
    for doc, score in zip(results['documents'], results['scores']):
        print(f"[相似度：{score:.2f}] {doc}...")