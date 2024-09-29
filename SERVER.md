

# Deploying Nginx Combined with Python (Flask) Running on Local Port 8080

## 1. Handling the Port Issue for Non-Root User

By default, ports below 1024 (e.g., port 80 or 443 for HTTP/HTTPS) require root or elevated privileges. Since we want to run the Flask app as the `ec2-user` without using `sudo` to start the app, we will configure **Nginx** as a reverse proxy to handle requests on port 80/443 and forward them to the Flask app running on port 8080.

### Steps:

1. Run your Flask app on **port 8080**.
   ```bash
   python3 /home/ec2-user/alinex-faiss/main.py --port 8080
   ```

2. Configure Nginx as a reverse proxy.
   
   Create a new Nginx config file for your app (e.g., `/etc/nginx/conf.d/faiss.jagroupai.com.conf`):
   ```bash
   sudo vi /etc/nginx/conf.d/faiss.jagroupai.com.conf
   ```

   Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name faiss.jagroupai.com;

       location / {
           proxy_pass http://127.0.0.1:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   This config listens on port 80 and forwards all traffic to your local Flask app on port 8080.

## 2. Using Let's Encrypt for SSL/TLS

To enable HTTPS for your domain using Let's Encrypt, follow these steps:

1. Install **Certbot**:
   ```bash
   sudo amazon-linux-extras install epel
   sudo yum install certbot python3-certbot-nginx
   ```

2. Generate the SSL certificate for your subdomain:
   ```bash
   sudo certbot --nginx -d faiss.jagroupai.com
   ```

   This will automatically edit your Nginx config to handle HTTPS and set up SSL certificates.

3. Verify the certificate generation and automatic Nginx update:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

Now, your app will be served securely over HTTPS using Let's Encrypt.

## 3. DNS Configuration

We use **GoDaddy** to manage the DNS for our main domain. Here's the basic setup:

- **Main Domain** (`jagroupai.com`):
   - A record pointing to the **EC2 Elastic IP**.

- **Subdomain** (`faiss.jagroupai.com`):
   - Another A record pointing to the same **Elastic IP** where your API is hosted.

This setup ensures that the main domain can handle web traffic, while the subdomain points specifically to the FAISS vector server.

## 4. Systemctl Commands Overview

We use **systemctl** to manage the Nginx server and Flask app service. Below are some useful commands:

- **Start Nginx**:
   ```bash
   sudo systemctl start nginx
   ```

- **Restart Nginx**:
   ```bash
   sudo systemctl restart nginx
   ```

- **Check Nginx status**:
   ```bash
   sudo systemctl status nginx
   ```

- **Enable Flask app service on boot**:
   ```bash
   sudo systemctl enable flask-app.service
   ```

- **Restart Flask app service**:
   ```bash
   sudo systemctl restart flask-app.service
   ```

## 5. Testing the Flask API with HTTPS

After deploying the Flask app behind Nginx with HTTPS enabled, you can test the API as follows:

- **Create a new vector store**:
   ```bash
   curl -X POST https://faiss.jagroupai.com/create/test_store \
       -H "Content-Type: application/json" \
       -d '{"name": "test_store"}'
   ```

- **Add a vector to the store**:
   ```bash
   curl -X POST https://faiss.jagroupai.com/vector-token/index \
       -H "Content-Type: application/json" \
       -d '{"auth_token":"your_token_here","texts":"test text","subject":"Test Subject"}'
   ```

- **Search for vectors**:
   ```bash
   curl -X POST https://faiss.jagroupai.com/vector_token/search/5 \
       -H "Content-Type: application/json" \
       -d '{"auth_token": "your_token_here", "input_query_context": "test search"}'
   ```

## Recap

1. **Nginx** forwards requests from port 80/443 to the local Flask app running on port 8080.
2. **Let's Encrypt** is used to generate SSL certificates for secure HTTPS communication.
3. **GoDaddy** is used to manage DNS for both the main domain and subdomain.
4. Basic **systemctl** commands help manage Nginx and the Flask app service.
5. You can test the vector store API using simple `curl` commands with HTTPS.



