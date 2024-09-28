# alinex-faiss
linex-FAISS is a scalable, cloud-agnostic FAISS vector search server built using Flask and Python. This server can be deployed on any cloud platform and is optimized for managing vector databases for AI applications.



## Why Use Alinex-FAISS?

While managed services like Pinecone offer convenience, their costs can quickly escalate, especially for high-frequency operations. Alinex-FAISS provides a cost-effective alternative by enabling you to self-host your vector search services (e.g., on AWS). By running your own FAISS server, you retain full control over the infrastructure and can significantly reduce your operating expenses.

### Cost Comparison: Pinecone vs. Self-Hosted FAISS (AWS)

- **Pinecone**: Managed service, easy to set up but can be expensive. For example, frequent upserts and retrievals can lead to monthly costs of $50 or more, depending on your usage.
- **Self-Hosted FAISS (AWS)**: Hosting your own FAISS server on an AWS t3.medium instance (for 8 hours a day, 22 working days per month) can cost as low as $7.32 per month. Bandwidth costs are minimal if your data usage stays under 1 GB per month.

By choosing self-hosting with Alinex-FAISS, you can balance performance and cost, especially if you require high-frequency vector search operations.

---

## Features

- Fast and efficient vector search powered by FAISS
- Flask-based server for easy integration with cloud platforms
- Cloud-agnostic, deployable on AWS, GCP, Azure, or any cloud provider
- Configurable for various use cases (recommendation systems, semantic search, etc.)

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- FAISS
- (Optional) Docker for containerized deployment

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/alinex-faiss.git
   cd alinex-faiss

2. Install the dependencies:
    ```bash    
    pip install -r requirements.txt

3. Start the server:
    ```bash 
    python app.py


### Usage
The server provides RESTful endpoints to interact with the FAISS database. You can use the following endpoints:

- POST /index: Add vectors to the FAISS index
- GET /search: Search for similar vectors

### Contributing
If you find this project useful, kindly acknowledge or link back to this repository in your project. Your appreciation is highly valued!

### License
This project is licensed under the MIT License - see the LICENSE file for details.