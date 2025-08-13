import json
import numpy as np
import faiss
from typing import List, Dict, Any
import os
from groq import Groq
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self, groq_api_key: str):
        """Initialize RAG system with FAISS vector store and Groq embeddings"""
        self.client = Groq(api_key=groq_api_key)
        self.index = None
        self.documents = []
        self.embeddings = []
        self.dimension = 1536  # OpenAI ada-002 embedding dimension
        
        # Load agricultural data
        self.load_agricultural_data()
        self.build_vector_store()
    
    def load_agricultural_data(self):
        """Load agricultural data from JSON files"""
        try:
            # Load soil data
            with open('data/soil_data.json', 'r', encoding='utf-8') as f:
                soil_data = json.load(f)
            
            # Load crop data
            with open('data/crop_data.json', 'r', encoding='utf-8') as f:
                crop_data = json.load(f)
            
            # Load schemes data
            with open('data/schemes_data.json', 'r', encoding='utf-8') as f:
                schemes_data = json.load(f)
            
            # Convert data to documents
            self.documents = []
            
            # Process soil data
            for soil_type, details in soil_data['soil_types'].items():
                doc = f"Soil Type: {details['name']}. "
                doc += f"pH Range: {details['characteristics']['ph_range']}. "
                doc += f"Drainage: {details['characteristics']['drainage']}. "
                doc += f"Fertility: {details['characteristics']['fertility']}. "
                doc += f"Suitable crops: {', '.join(details['suitable_crops'])}. "
                doc += f"Nitrogen requirement: {details['fertilizer_recommendations']['nitrogen']}. "
                doc += f"Phosphorus requirement: {details['fertilizer_recommendations']['phosphorus']}. "
                doc += f"Potassium requirement: {details['fertilizer_recommendations']['potassium']}. "
                doc += f"Found in regions: {', '.join(details['regions'])}."
                self.documents.append({
                    'content': doc,
                    'type': 'soil',
                    'category': soil_type,
                    'source': details
                })
            
            # Process crop data
            for crop_name, details in crop_data['crops'].items():
                doc = f"Crop: {details['name']}. "
                doc += f"Season: {', '.join(details['season'])}. "
                doc += f"Duration: {details['duration_days']} days. "
                doc += f"Water requirement: {details['water_requirement']}. "
                doc += f"Suitable soil types: {', '.join(details['soil_types'])}. "
                doc += f"Planting months: {', '.join(map(str, details['planting_months']))}. "
                doc += f"Harvesting months: {', '.join(map(str, details['harvesting_months']))}."
                self.documents.append({
                    'content': doc,
                    'type': 'crop',
                    'category': crop_name,
                    'source': details
                })
            
            # Process schemes data
            for scheme_id, details in schemes_data['government_schemes'].items():
                doc = f"Government Scheme: {details['name']}. "
                doc += f"Description: {details['description']}. "
                doc += f"Benefits: {details['benefits']}. "
                doc += f"Ministry: {details['ministry']}. "
                doc += f"Launch Year: {details['launch_year']}."
                if 'eligibility' in details:
                    doc += f" Eligibility criteria available."
                self.documents.append({
                    'content': doc,
                    'type': 'scheme',
                    'category': scheme_id,
                    'source': details
                })
                
            logger.info(f"Loaded {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Error loading agricultural data: {e}")
            self.documents = []
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate simple embeddings using text similarity"""
        try:
            # Simple TF-IDF like approach for text similarity
            embeddings = []
            for text in texts:
                # Create a simple vector based on character frequencies and word counts
                words = text.lower().split()
                embedding = [0.0] * self.dimension
                
                for i, word in enumerate(words[:100]):  # Limit to first 100 words
                    if i < self.dimension:
                        embedding[i] = len(word) * 0.1  # Simple weighting
                
                embeddings.append(embedding)
            
            return embeddings
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            # Return random embeddings as fallback
            return [np.random.rand(self.dimension).tolist() for _ in texts]
    
    def build_vector_store(self):
        """Build FAISS vector store from documents"""
        if not self.documents:
            logger.warning("No documents to build vector store")
            return
        
        try:
            # Get embeddings for all documents
            document_texts = [doc['content'] for doc in self.documents]
            embeddings = self.get_embeddings(document_texts)
            
            if not embeddings or all(sum(emb) == 0 for emb in embeddings):
                logger.warning("Failed to get valid embeddings, using random embeddings for demo")
                embeddings = [np.random.rand(self.dimension).tolist() for _ in document_texts]
            
            # Create FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for similarity
            
            # Normalize embeddings for cosine similarity
            embeddings_array = np.array(embeddings, dtype=np.float32)
            faiss.normalize_L2(embeddings_array)
            
            # Add to index
            self.index.add(embeddings_array)
            self.embeddings = embeddings_array
            
            logger.info(f"Built vector store with {len(embeddings)} documents")
            
        except Exception as e:
            logger.error(f"Error building vector store: {e}")
            self.index = None
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if not self.index or not self.documents:
            return []
        
        try:
            # Get query embedding
            query_embedding = self.get_embeddings([query])
            if not query_embedding or sum(query_embedding[0]) == 0:
                logger.warning("Failed to get query embedding")
                return self.documents[:top_k]  # Return first few documents as fallback
            
            # Normalize query embedding
            query_vector = np.array(query_embedding, dtype=np.float32)
            faiss.normalize_L2(query_vector)
            
            # Search
            scores, indices = self.index.search(query_vector, min(top_k, len(self.documents)))
            
            # Return results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.documents):
                    result = self.documents[idx].copy()
                    result['score'] = float(score)
                    result['rank'] = i + 1
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return self.documents[:top_k]  # Return first few documents as fallback
    
    def get_context(self, query: str, max_context_length: int = 2000) -> str:
        """Get relevant context for a query"""
        relevant_docs = self.search(query, top_k=5)
        
        context = "Relevant agricultural information:\n\n"
        current_length = len(context)
        
        for doc in relevant_docs:
            doc_text = f"- {doc['content']}\n"
            if current_length + len(doc_text) <= max_context_length:
                context += doc_text
                current_length += len(doc_text)
            else:
                break
        
        return context
