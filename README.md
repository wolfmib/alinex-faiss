
##  Use FAISS for Self-Development?

🚀 FAISS to the rescue! If you're tired of high costs from services like Pinecone, especially for large-scale vector storage, using FAISS on your own AWS instance can save your budget. For example, hosting your own FAISS on a t3.medium EC2 instance can drastically cut down costs compared to the recurring fees for retrieval and upserts on Pinecone. With FAISS, you get scalable, high-performance vector searching at a fraction of the price—no subscription costs or hidden fees! Why pay more when you can build smarter? 😎


# FAISS Vector Store API

This project provides a Flask-based API for managing FAISS vector stores with OpenAI embeddings. You can create vector stores, add vectors to them, and perform similarity searches.

## Features

- **Create FAISS vector stores**: Easily initialize new FAISS vector stores with a unique token.
- **Add vectors**: Use OpenAI embeddings to generate vectors and add them to the store.
- **Similarity search**: Perform top-K searches to find the most similar vectors based on input text.
- **JSON serializable responses**: Ensure clean and valid JSON responses for all API endpoints.
- **Memory management**: Vector stores are loaded and released from memory efficiently.


## Run
python3 main.py


## API Endpoints

### 1. Create a Vector Store

- **Endpoint**: `/create/<name>`
- **Method**: `POST`
- **Description**: Creates a new FAISS vector store and returns a unique token.

Example request:
```bash
curl -X POST http://localhost:5000/create/my_store
```

Response:
```json
{
  "token": "unique_token"
}
```

### 2. Add Vectors to a Store

- **Endpoint**: `/vector-token/index`
- **Method**: `POST`
- **Description**: Adds vectors to the store using an auth token, with automatic metadata handling.

Example request:
```bash
curl -X POST http://localhost:5000/vector-token/index \
     -H "Content-Type: application/json" \
     -d '{"auth_token":"your_token", "texts": "your input text", "subject": "Test Subject"}'
```

Response:
```json
{
  "message": "Vector added successfully"
}
```

### 3. Search for Vectors

- **Endpoint**: `/vector_token/search/<k>`
- **Method**: `POST`
- **Description**: Performs a top-K similarity search based on input query context.

Example request:
```bash
curl -X POST http://localhost:5000/vector_token/search/5 \
     -H "Content-Type: application/json" \
     -d '{"auth_token":"your_token", "input_query_context": "search text"}'
```

Response:
```json
{
  "results": [
    {
      "vector_id": 1,
      "distance": 290884,
      "metadata": {
        "input_text": "I wana sleep 4",
        "added_on": "2024-09-28-22-17",
        "vector_id": 1
      }
    },
    {
      "vector_id": 0,
      "distance": 999999,
      "metadata": {
        "input_text": "dummy_vector",
        "added_on": "2024-09-28-22-17",
        "vector_id": 0
      }
    }
  ]
}
```

## Key Implementation Details

- **OpenAI Embeddings**: The API uses OpenAI's embedding model (`text-embedding-ada-002`) to generate embeddings from text.
- **Vector Store Management**: Each vector store is associated with a unique token. Stores are saved to disk and can be loaded or released from memory when needed.
- **Indexing and Searching**: FAISS is used for efficient vector storage and similarity searching.

## Improvements

- **Optimize Memory Handling**: Automatically release vector stores from memory after every operation.
- **Distance Scaling**: Convert distances to integers by multiplying by `1,000,000` to avoid floating-point precision issues in JSON responses.
- **Error Handling**: Added error handling for invalid tokens and indices.

## How to Contribute

- **Clone the repository**:
  ```bash
  git clone https://github.com/your-repo/alinex-faiss.git
  ```
- **Set up the environment**:
  - Install Python dependencies: `pip install -r requirements.txt`
  - Create a `.env` file and add your OpenAI API key.
  
- **Run Tests**:
  ```bash
  python -m unittest discover -s tests
  ```

## License

This project is licensed under the MIT License. Please remember to attribute contributions where applicable.
```

### How to Use It:
- Replace the placeholders like `your_token` and `your-repo` with actual values.
- The Markdown is structured to be readable and organized with clear sections for features, API endpoints, and usage examples.

Let me know if you need any further adjustments!