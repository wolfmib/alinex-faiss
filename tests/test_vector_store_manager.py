import unittest
import os
import numpy as np
from vectors.vector_store_manager import VectorStoreManager
from unittest.mock import patch

class TestVectorStoreManager(unittest.TestCase):

    def setUp(self):
        """Set up for testing, remove token file if exists."""
        self.manager = VectorStoreManager(token_file="test_token_list.txt")
        if os.path.exists("test_token_list.txt"):
            os.remove("test_token_list.txt")  # Ensure the token file is fresh for every test

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists("test_token_list.txt"):
            os.remove("test_token_list.txt")  # Clean up after each test

    def test_create_by_name(self):
        """Test creating a vector store with a unique token."""
        token = self.manager.create_by_name("test_store")
        self.assertTrue(token)  # Ensure a token is returned
        self.assertIn(token, self.manager.stores)  # Ensure the store is created
        self.assertIn(token, self.manager.metadata)  # Ensure metadata is created

    @patch('openai.Embedding.create')
    def test_add_vector_by_token_and_text(self, mock_openai_embedding):
        """Test adding a vector to a specific store."""
        # Mock OpenAI embedding response (1536 dimensions)
        mock_openai_embedding.return_value = {
            'data': [{'embedding': [0.1] * 1536}]
        }

        # Create a store and get its token
        token = self.manager.create_by_name("test_store")

        # Add vector
        self.manager.add_vector_by_token_and_text(token, "test text")

        # Check if the vector is added
        self.assertEqual(self.manager.stores[token].ntotal, 1)  # Ensure vector is added to FAISS
        self.assertEqual(len(self.manager.metadata[token]["vectors"]), 1)  # Ensure metadata is added

    def test_load_vector_store(self):
        """Test loading a vector store by token."""
        # Create a store and get its token
        token = self.manager.create_by_name("test_store")

        # Load the store
        store = self.manager.load_vector_store(token)

        self.assertEqual(store.ntotal, 0)  # Ensure the store is empty initially

    @patch('openai.Embedding.create')
    def test_search_vector_by_token_and_k(self, mock_openai_embedding):
        """Test searching vectors in the vector store."""
        # Mock OpenAI embedding response (1536 dimensions)
        mock_openai_embedding.return_value = {
            'data': [{'embedding': [0.1] * 1536}, {'embedding': [0.2] * 1536}]
        }

        # Create a store and get its token
        token = self.manager.create_by_name("test_store")

        # Add two vectors
        self.manager.add_vector_by_token_and_text(token, "test text 1")
        self.manager.add_vector_by_token_and_text(token, "test text 2")

        # Mock search context (1536 dimensions) similar to the first vector
        mock_openai_embedding.return_value = {
            'data': [{'embedding': [0.1] * 1536}]
        }
        results = self.manager.search_vector_by_token_and_k(token, "search text", k=1)

        # Ensure one result is returned and it's the correct vector
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["metadata"]["input_text"], "test text 1")

if __name__ == '__main__':
    unittest.main()
