import faiss
from datetime import datetime
import pytz
import openai
import numpy as np


class VectorStore:
    def __init__(self, dimension=1536, timezone_str='UTC'):
        """Initialize the FAISS index with a given dimension and timezone."""
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = {}
        self.timezone = pytz.timezone(timezone_str)  # Set the timezone for storing dates

    def add_texts(self, texts, metadata):
        """Generate embeddings from text using OpenAI API and add them to the index."""
        if len(texts) != len(metadata):
            raise ValueError("Each text must have corresponding metadata.")

        # Generate embeddings from texts using OpenAI API
        vectors = []
        for text in texts:
            embedding = self._get_openai_embedding(text)
            vectors.append(embedding)

        vectors = np.array(vectors)  # Convert to NumPy array
        print("[vectore_store-add-texts]:\nEmbedding Vector Shape:", np.array(vectors).shape)

        assert len(vectors[0]) == 1536, "Embedding dimensions must be 1536!"

        self.index.add(vectors)

        # Get the current date and time with timezone
        now = datetime.now(self.timezone)
        timestamp = now.strftime("%Y-%m-%d-%H-%M")  # Format as YYYY-MM-DD-HH-MM

        # Store metadata with timestamp
        for i, meta in enumerate(metadata):
            vector_id = self.index.ntotal - len(vectors) + i  # FAISS indexes start at 0
            # Add date and timezone info to metadata
            extended_meta = {
                **meta,  # Copy existing metadata
                "added_on": timestamp,
                "timezone": self.timezone.zone
            }
            self.metadata[vector_id] = extended_meta

    def search_vectors(self, query_vector, k=10):
        """Search for the top k vectors closest to the query vector."""
        D, I = self.index.search(query_vector, k)
        results = []
        for i in I[0]:
            results.append({
                "vector_id": i,
                "metadata": self.metadata.get(i, {})
            })
        return results

    def _get_openai_embedding(self, text):
        """Get the OpenAI embedding for a given text."""
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"  # Use the appropriate embedding model
        )
        return response['data'][0]['embedding']
