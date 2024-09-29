#vector_store_manager.py

import faiss
import numpy as np
import os
import random
import string
import openai
from datetime import datetime
import pytz
from dotenv import load_dotenv
import json
from logger import log  # Import the logger


# Load environment variables from .env file
load_dotenv()
# Set the API key from .env
openai.api_key = os.getenv('OPENAI_API_KEY')


class VectorStoreManager:
    def __init__(self, token_file="token_list.txt", vector_store_dir="vector_stores"):
        self.token_file = token_file
        self.stores = {}  # To hold active FAISS stores in memory
        self.metadata = {}  # Metadata associated with tokens
        self.vector_store_dir = vector_store_dir

        # Ensure directory for saving vector stores exists
        if not os.path.exists(self.vector_store_dir):
            os.makedirs(self.vector_store_dir)

        # Ensure the token list file exists
        if not os.path.exists(self.token_file):
            open(self.token_file, "w").close()

    def _generate_unique_token(self):
        """Generates a unique token and ensures it doesn't exist in token_list.txt."""
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        log.debug(f"Token created:  {token}")
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                existing_tokens = f.read().splitlines()
            while token in existing_tokens:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return token

    def _save_token(self, token):
        """Saves a token to the token list."""
        log.debug(f"Saving token to file: {token}")  # Add this line for debugging
        with open(self.token_file, "a") as f:
            f.write(f"{token}\n")


    def _check_token_exists(self, auth_token):
        """Checks if the token exists in token_list.txt."""
        log.debug(f"_check_token {auth_token}")
        with open(self.token_file, "r") as f:
            tokens = f.read().splitlines()
        if auth_token not in tokens:
            raise ValueError("Invalid token, no vector store found in token_list.txt.")

    def create_by_name(self, name):
        """Creates a new vector store, associates it with a unique token, and saves the token."""
        token = self._generate_unique_token()
        dimension = 1536  # Since we're using OpenAI embeddings

        # Create a new FAISS store and add a dummy vector
        self.stores[token] = faiss.IndexFlatL2(dimension)
        dummy_vector = np.zeros((1, dimension)).astype('float32')  # Add a dummy vector (all zeros)
        self.stores[token].add(dummy_vector)

        # Save metadata
        self.metadata[token] = {"name": name, 
        "created_on": datetime.now(pytz.UTC).strftime("%Y-%m-%d-%H-%M"),
        "vectors": [{"input_text": "dummy_vector", "added_on": datetime.now(pytz.UTC).strftime("%Y-%m-%d-%H-%M"), "vector_id": 0}]}

        # Save the token to the token_list.txt
        self._save_token(token)

        # Save the initial vector store
        self.save_vector_store(token)

        # Release the store from memory
        #self.close_vector_store(auth_token)
        #print(f"Vector store for token {auth_token} released from memory.")


        return token  # Return token to the client

    def _get_openai_embedding(self, text):
        """Get the OpenAI embedding for a given text using the new API."""
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        embedding = response.data[0].embedding

        return embedding

    def add_vector_by_token_and_text(self, auth_token, input_text):
        """Adds a vector to the store identified by auth_token, along with metadata."""
        try:
            # Ensure the token is valid and exists
            log.debug(f"Received auth_token: {auth_token}")
            
            self._check_token_exists(auth_token)
            
            log.debug(f"Token {auth_token} is valid.")
            
            # Load the store from disk
            self.load_vector_store(auth_token)
            
            log.debug(f"Vector store for token {auth_token} loaded.")
            
            # Generate embedding using OpenAI
            embedding = self._get_openai_embedding(input_text)
            log.debug(f"Generated embedding for text: {input_text}")
            
            embedding = np.array([embedding])  # Make it a 2D array for FAISS

            # Add embedding to the correct store
            self.stores[auth_token].add(embedding)
            
            log.debug(f"Added embedding to store for token: {auth_token}")
            
            # Automatically add metadata with date
              # Ensure "vectors" exists in metadata
            if "vectors" not in self.metadata[auth_token]:
                self.metadata[auth_token]["vectors"] = []  # Initialize as an empty list
        
            now = datetime.now(pytz.UTC).strftime("%Y-%m-%d-%H-%M")
            self.metadata[auth_token]["vectors"].append({
                "input_text": input_text,
                "added_on": now,
                "vector_id": self.stores[auth_token].ntotal - 1
            })
   
            # Validate metadata length matches FAISS store
            if len(self.metadata[auth_token]["vectors"]) != self.stores[auth_token].ntotal:
                log.debug(f"Warning: Metadata and FAISS index out of sync! Metadata length: {len(self.metadata[auth_token]['vectors'])}, FAISS index total: {self.stores[auth_token].ntotal}")
            

            # Save the updated vector store to disk
            self.save_vector_store(auth_token)
            
            log.debug(f"Vector store for token {auth_token} saved successfully.")
            
            # Release the store from memory
            self.close_vector_store(auth_token)
            log.debug(f"Vector store for token {auth_token} released from memory.")

        except Exception as e:
            # Release the store from memory after search
            
            self.close_vector_store(auth_token)
        
            log.error(f"Error: Close the vectore_store {str(e)}")
            raise


    def save_vector_store(self, auth_token):
        """Saves the FAISS index for a particular auth_token to disk."""
        if auth_token not in self.stores:
            raise ValueError(f"No store found for token '{auth_token}' to save.")
        
        # Save the FAISS index to disk
        faiss_store_path = os.path.join(self.vector_store_dir, f"{auth_token}.index")
        faiss.write_index(self.stores[auth_token], faiss_store_path)

        # 🙂 Save metadata to disk as a JSON file
        metadata_store_path = os.path.join(self.vector_store_dir, f"{auth_token}_metadata.json")
        with open(metadata_store_path, "w") as f:
            json.dump(self.metadata[auth_token], f)
        
    def load_vector_store(self, auth_token):
        """Loads a FAISS vector store and metadata associated with the given auth_token from disk."""
        # Check if the token exists in token_list.txt
        log.debug(f"Loading vector store for token: {auth_token}")
        self._check_token_exists(auth_token)

        # Check if the store is already loaded in memory
        if auth_token in self.stores:
            log.debug(f"Vector store for token {auth_token} is already loaded in memory.")
            return self.stores[auth_token]

        # Load the FAISS index from disk
        faiss_store_path = os.path.join(self.vector_store_dir, f"{auth_token}.index")
        if os.path.exists(faiss_store_path):
            log.debug(f"Loading FAISS index from {faiss_store_path}")
            index = faiss.read_index(faiss_store_path)
            self.stores[auth_token] = index

            # Load the metadata from disk
            metadata_store_path = os.path.join(self.vector_store_dir, f"{auth_token}_metadata.json")
            if os.path.exists(metadata_store_path):
                with open(metadata_store_path, "r") as f:
                    self.metadata[auth_token] = json.load(f)
                log.debug(f"Metadata for token {auth_token} loaded from {metadata_store_path}")
            else:
                log.warning(f"No metadata found for token {auth_token}, creating empty metadata.")
                self.metadata[auth_token] = {"vectors": []}

            return index
        else:
            raise ValueError(f"FAISS store for token '{auth_token}' not found on disk.")

    def close_vector_store(self, auth_token):
        """Closes a vector store and removes it from memory (but keeps it on disk)."""
        if auth_token in self.stores:
            del self.stores[auth_token]
        else:
            raise ValueError(f"No store found in memory for token '{auth_token}' to close.")

    def search_vector_by_token_and_k(self, auth_token, search_context, k=10):
        """Searches for the top k vectors in the store associated with auth_token."""
        log.debug(f"Searching vector store for token: {auth_token}")
        
        self._check_token_exists(auth_token)
        
        # Load the store from disk
        self.load_vector_store(auth_token)
        log.debug(f"Vector store for token {auth_token} loaded for searching.")
        
        # Generate the embedding for the search context
        query_vector = self._get_openai_embedding(search_context)
        log.debug(f"Generated query vector for search context: {search_context}")
        query_vector = np.array([query_vector])  # Make it a 2D array for FAISS

        # Perform search
        D, I = self.stores[auth_token].search(query_vector, k)
        log.debug(f"Search completed. Distances: {D}, Indices: {I}")
        
        #  metadata before filtering
        log.debug(f"Metadata for token {auth_token}: {self.metadata[auth_token]['vectors']}")
        log.debug(f"FAISS index total vectors: {self.stores[auth_token].ntotal}")
        
        # Filter invalid results (e.g., distances too large or indices == -1)
        results = []
        """
        for idx, distance in zip(I[0], D[0]):
            try:
                # Debugging: Print index and length of metadata
                print(f"Checking index {idx}, metadata length: {len(self.metadata[auth_token]['vectors'])}")
                
                if idx != -1 and distance < 1e10:  # Filter out invalid indices and large distances
                    vector_metadata = self.metadata[auth_token]["vectors"][idx]
                    results.append({
                        "vector_id": idx,
                        "distance": distance,  # Include the distance in the result
                        "metadata": vector_metadata
                    })
            except IndexError as e:
                print(f"IndexError: {e}, idx: {idx}")
                # You can handle or log this error if necessary

        if not results:
            return {"message": "No valid results found."}, 404  # Return 404 if no valid results found
        """
        results = []
        for idx, distance in zip(I[0], D[0]):
            if idx != -1 and distance < 1e10:  # Filter out invalid indices and large distances
                # Ensure metadata exists for this index
                if idx < len(self.metadata[auth_token]["vectors"]):
                    vector_metadata = self.metadata[auth_token]["vectors"][idx]
                    results.append({
                        "vector_id": int(idx),
                        "distance": int(distance * 1000000),  # Convert distance to int and scale
                        "metadata": vector_metadata
                    })
                else:
                    log.debug(f"Warning: No metadata found for vector_id {idx}, skipping this result.")
            else:
                log.debug(f"Dropping invalid index {idx} with distance {distance}")

        if not results:
            return {"message": "No valid results found."}, 404  # Return 404 if no valid results found




        # Release the store from memory after search
        self.close_vector_store(auth_token)
        log.debug(f"Vector store for token {auth_token} released from memory after searching.")
        log.debug(f"results: {results}")
        return results



    def close_vector_store(self, auth_token):
        """Closes a vector store and removes it from memory (but keeps it on disk)."""
        if auth_token in self.stores:
            del self.stores[auth_token]
            log.debug(f"Vector store for token {auth_token} has been removed from memory.")
        else:
            log.error("No store found in memory for token")
            raise ValueError(f"No store found in memory for token '{auth_token}' to close.")