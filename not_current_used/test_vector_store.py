import unittest
from unittest.mock import patch
import numpy as np
from vectors.vector_store import VectorStore

class TestVectorStore(unittest.TestCase):

    def setUp(self):
        """Set up the vector store with a small dimension for testing."""
        self.store = VectorStore(dimension=1536, timezone_str='UTC')  # Initialize with 3-dimensional space
        self.texts = ["hello world", "foo bar"]
        self.metadata = [{"label": "text_1"}, {"label": "text_2"}]

    @patch('openai.Embedding.create')
    def test_add_texts(self, mock_openai_embedding):
        """Test adding texts with OpenAI embeddings."""
        # Mock OpenAI embedding response (1536 dimensions)
        mock_openai_embedding.return_value = {
            'data': [{'embedding': [0.1] * 1536}, {'embedding': [0.2] * 1536}]  # 1536-dimensional vectors
        }

        # Call the method to add texts (and generate embeddings)
        self.store.add_texts(self.texts, self.metadata)

        # Check that 2 vectors were added to the FAISS index
        self.assertEqual(self.store.index.ntotal, 2)

        # Check that metadata was added correctly
        self.assertIn("added_on", self.store.metadata[0])  # Check if "added_on" timestamp is present
        self.assertEqual(self.store.metadata[0]["label"], "text_1")  # Ensure the label is correct

    def test_search_vectors(self):
        """Test searching vectors in the vector store."""
        # Add embeddings directly without OpenAI (1536 dimensions)
        vectors = np.array([[0.1] * 1536, [0.2] * 1536])  # Two 1536-dimensional vectors
        self.store.index.add(vectors)  # Directly add vectors to the FAISS index

        # Add metadata for the vectors
        self.store.metadata[0] = {"label": "vector_1"}
        self.store.metadata[1] = {"label": "vector_2"}

        # Query vector similar to the first vector added
        query_vector = np.array([[0.1] * 1536])  # 1536-dimensional query vector

        # Search for the nearest vector (k=1)
        results = self.store.search_vectors(query_vector, k=1)

        # Check the search result
        self.assertEqual(len(results), 1)  # Ensure one result is returned
        self.assertEqual(results[0]["metadata"]["label"], "vector_1")  # Ensure the correct label is returned

if __name__ == '__main__':
    unittest.main()
