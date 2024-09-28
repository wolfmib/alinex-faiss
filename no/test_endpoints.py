import unittest
from flask import Flask
from routes.endpoints import routes

class TestEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the Flask app and test client"""
        app = Flask(__name__)
        app.register_blueprint(routes)
        self.client = app.test_client()
        self.client.testing = True

    def test_create_vector_store(self):
        """Test creating a new vector store"""
        response = self.client.post('/create/test_store', json={"dimension": 1536})
        self.assertEqual(response.status_code, 201)
        self.assertIn(b"Vector store 'test_store' created", response.data)

    def test_add_vectors(self):
        """Test adding vectors to a vector store"""
        self.client.post('/create/test_store', json={"dimension": 3})
        vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        metadata = [{"label": "vec_1"}, {"label": "vec_2"}]
        response = self.client.post('/vector-token/index', json={
            "name": "test_store", 
            "vectors": vectors,
            "metadata": metadata
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Vectors added successfully", response.data)

    def test_search_vectors(self):
        """Test searching vectors in a vector store"""
        self.client.post('/create/test_store', json={"dimension": 1536})
        vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        metadata = [{"label": "vec_1"}, {"label": "vec_2"}]
        self.client.post('/vector-token/index', json={
            "name": "test_store", 
            "vectors": vectors,
            "metadata": metadata
        })
        query_vector = [0.1, 0.2, 0.3]
        response = self.client.post('/vector_token/search/1', json={
            "name": "test_store",
            "query_vector": query_vector
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"label", response.data)

if __name__ == '__main__':
    unittest.main()
