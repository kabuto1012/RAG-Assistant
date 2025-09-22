"""
Knowledge base implementation for the RDR2 Agent system.
Implements the Single Responsibility Principle by handling only knowledge storage and retrieval.
"""

import os
from typing import Tuple, List
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from models.base_models import IKnowledgeBase


class ChromaKnowledgeBase(IKnowledgeBase):
    """
    Handles knowledge operations.
    """
    
    def __init__(self, db_path: str, embedding_model: str = "all-mpnet-base-v2", collection_name: str = "rdr2_knowledge"):
        """
        Initialize the ChromaDB knowledge base.
        
        Args:
            db_path: Path to the ChromaDB database
            embedding_model: Name of the embedding model to use
            collection_name: Name of the collection in ChromaDB
        """
        self._db_path = db_path
        self._embedding_model = embedding_model
        self._collection_name = collection_name
        
        # Initialize ChromaDB client
        self._client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding function
        self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Get or create collection
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._embedding_function
        )
    
    def load_knowledge(self, source_path: str) -> bool:
        """
        Load knowledge from text files in the specified path.
        
        Args:
            source_path: Path to the directory containing knowledge files
            
        Returns:
            bool: True if knowledge loaded successfully, False otherwise
        """
        try:
            # Check if collection already has documents
            if self._collection.count() > 0:
                print(f"Knowledge base already has {self._collection.count()} documents.")
                return True
            
            # Load knowledge from files
            knowledge_blocks = self._load_text_files(source_path)
            
            if not knowledge_blocks:
                print(f"No knowledge found in {source_path}")
                return False
            
            # Filter out very short blocks
            filtered_blocks = [block.strip() for block in knowledge_blocks if len(block.strip()) >= 20]
            
            if not filtered_blocks:
                print("No substantial knowledge blocks found after filtering")
                return False
            
            # Create document IDs
            ids = [f"doc_{i}" for i in range(len(filtered_blocks))]
            
            # Add documents to collection
            self._collection.add(
                documents=filtered_blocks,
                ids=ids
            )
            
            print(f"Successfully loaded {len(filtered_blocks)} knowledge blocks into ChromaDB.")
            return True
            
        except Exception as e:
            print(f"Error loading knowledge: {e}")
            return False
    
    def _load_text_files(self, folder_path: str) -> List[str]:
        """
        Load text content from all .txt files in the specified folder.
        
        Args:
            folder_path: Path to the folder containing text files
            
        Returns:
            List[str]: List of text blocks from all files
        """
        all_text_blocks = []
        
        try:
            print(f"Loading knowledge from: {os.path.abspath(folder_path)}")
            
            for filename in os.listdir(folder_path):
                if filename.endswith(".txt"):
                    file_path = os.path.join(folder_path, filename)
                    print(f"Processing file: {filename}")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Split by '---' delimiter and add to blocks
                        blocks = content.split('---')
                        all_text_blocks.extend(blocks)
            
            print(f"Loaded {len(all_text_blocks)} text blocks from {len([f for f in os.listdir(folder_path) if f.endswith('.txt')])} files.")
            return all_text_blocks
            
        except FileNotFoundError:
            print(f"ERROR: The folder '{folder_path}' was not found.")
            return []
        except Exception as e:
            print(f"Error reading files: {e}")
            return []
    
    def find_relevant_content(self, query: str, top_n: int = 5) -> Tuple[str, float]:
        """
        Find the most relevant content for a query.
        
        Args:
            query: Search query string
            top_n: Number of top results to retrieve
            
        Returns:
            Tuple[str, float]: Combined relevant content and best similarity score
        """
        try:
            # Query the collection
            results = self._collection.query(
                query_texts=[query],
                n_results=top_n
            )
            
            # Check if we have results
            if not results['documents'] or not results['documents'][0]:
                return "", float('inf')
            
            # Get the top documents and scores
            top_blocks = results['documents'][0]
            distances = results['distances'][0] if results['distances'] else [float('inf')]
            
            # Combine the top blocks
            combined_content = "\n---\n".join(top_blocks)
            best_score = min(distances) if distances else float('inf')
            
            print(f"Retrieved {len(top_blocks)} blocks (best distance={round(best_score, 3)})")
            
            return combined_content, best_score
            
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return "", float('inf')
    
    def get_document_count(self) -> int:
        """
        Get the total number of documents in the knowledge base.
        
        Returns:
            int: Number of documents
        """
        try:
            return self._collection.count()
        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0
    
    def add_document(self, content: str, doc_id: str = None) -> bool:
        """
        Add a single document to the knowledge base.
        
        Args:
            content: Document content
            doc_id: Optional document ID (auto-generated if not provided)
            
        Returns:
            bool: True if document added successfully
        """
        try:
            if doc_id is None:
                # Generate auto ID based on current count
                doc_id = f"doc_{self._collection.count()}"
            
            self._collection.add(
                documents=[content],
                ids=[doc_id]
            )
            
            print(f"Added document with ID: {doc_id}")
            return True
            
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def search_by_metadata(self, metadata_filter: dict, top_n: int = 5) -> List[str]:
        """
        Search documents by metadata (if metadata was stored).
        
        Args:
            metadata_filter: Dictionary of metadata filters
            top_n: Number of results to return
            
        Returns:
            List[str]: List of matching documents
        """
        try:
            results = self._collection.get(
                where=metadata_filter,
                limit=top_n
            )
            
            return results.get('documents', [])
            
        except Exception as e:
            print(f"Error searching by metadata: {e}")
            return []
    
    def get_collection_info(self) -> dict:
        """
        Get information about the collection.
        
        Returns:
            dict: Collection information
        """
        try:
            return {
                "name": self._collection_name,
                "count": self._collection.count(),
                "embedding_model": self._embedding_model,
                "db_path": self._db_path
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {}
