
from flask import Flask
from routes.endpoints import routes
import json


app = Flask(__name__)

# Register the blueprint from routes/endpoints.py
app.register_blueprint(routes)

if __name__ == '__main__':
    # Run the app, accessible on all interfaces (0.0.0.0)
    app.run(host='127.0.0.1', port=8080, debug=True)



