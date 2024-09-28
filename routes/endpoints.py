from flask import Blueprint, request, jsonify
from vectors.vector_store_manager import VectorStoreManager

# Initialize Flask Blueprint
routes = Blueprint('routes', __name__)

# Initialize VectorStoreManager
vector_manager = VectorStoreManager()

# 1. Create Vector Store
@routes.route('/create/<name>', methods=['POST'])
def create_vector_store(name):
    """Creates a vector store associated with a unique token."""
    try:
        token = vector_manager.create_by_name(name)
        return jsonify({"auth_token": token, "message": f"Vector store '{name}' created."}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500



# 2. Add Vectors by Token
@routes.route('/vector-token/index', methods=['POST'])
def add_vectors():
    """Adds vectors to the FAISS store associated with the given auth_token."""
    auth_token = request.json.get('auth_token')
    texts = request.json.get('texts')
    subject = request.json.get('subject')  # Ensure subject is required
    metadata = request.json.get('metadata', {})  # Optional metadata

    # Ensure required fields are provided
    if not auth_token or not texts or not subject:
        return jsonify({"message": "auth_token, subject, and texts are required fields."}), 400

    try:
        # Add the vector and include the metadata (and automatically add date)
        vector_manager.add_vector_by_token_and_text(auth_token, texts)
        return jsonify({"message": "Vector added successfully.", "subject": subject}), 200
    except ValueError as e:
        print(f"Error: {str(e)}")  # Log the error
        return jsonify({"message": str(e)}), 404  # Token not found, invalid token
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error
        return jsonify({"message": "Error adding vector."}), 500


# 3. Search Vectors by Token
@routes.route('/vector_token/search/<int:k>', methods=['POST'])
def search_vectors(k):
    """Searches for the top k vectors in the FAISS store associated with the given auth_token."""
    auth_token = request.json.get('auth_token')
    input_query_context = request.json.get('input_query_context')

    if not auth_token or not input_query_context:
        return jsonify({"message": "auth_token and input_query_context are required fields."}), 400

    try:
        # Perform the search using the vector manager
        results = vector_manager.search_vector_by_token_and_k(auth_token, input_query_context, k)

        return jsonify({"results": results}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404  # Token not found
    except Exception as e:
        print(f"Error in search_vectors: {str(e)}")
        return jsonify({"message": "Error performing search."}), 500
