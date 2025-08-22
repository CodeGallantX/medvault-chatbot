# Medvault-Copy Deployment Guide

This guide provides a step-by-step process for deploying the Medvault-Copy Django application to a production environment. We will use Gunicorn as the WSGI application server and Nginx as the reverse proxy web server.

## Prerequisites

Before you begin, you should have the following on your server:

- A server running a Linux distribution (e.g., Ubuntu, CentOS).
- Python 3 and `pip` installed.
- `virtualenv` installed (`pip install virtualenv`).
- Nginx installed (`sudo apt-get install nginx` on Ubuntu).
- A user with `sudo` privileges.

## Deployment Steps

### 1. Clone the Project

First, clone the project repository to your server.

```bash
git clone <repository-url>
cd medvault-copy
```

### 2. Set Up the Environment

Create a virtual environment and install the project dependencies.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Also install gunicorn
pip install gunicorn
```

### 3. Configure Django for Production

Next, you need to make a few changes to your Django `settings.py` file for production.

**File:** `medvault_project/settings.py`

-   **`DEBUG`**: Set `DEBUG` to `False`.
    ```python
    DEBUG = False
    ```

-   **`ALLOWED_HOSTS`**: Add your server's IP address or domain name to the `ALLOWED_HOSTS` list.
    ```python
    ALLOWED_HOSTS = ['your_server_ip_or_domain']
    ```

-   **`STATIC_ROOT`**: Add the following to the end of the file to specify where to collect static files.
    ```python
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    ```

Now, run the `collectstatic` command to gather all static files into the `STATIC_ROOT` directory.

```bash
python3 manage.py collectstatic
```

### 4. Set Up Gunicorn

We will use Gunicorn to run the Django application.

**Test Gunicorn:**

First, test that Gunicorn can serve the application correctly.

```bash
gunicorn --bind 0.0.0.0:8000 medvault_project.wsgi:application
```

You should be able to access the application at `http://your_server_ip_or_domain:8000`. Press `Ctrl+C` to stop the Gunicorn server.

**Create a Gunicorn Systemd Service:**

To manage the Gunicorn process, we will create a systemd service file.

Create a new file at `/etc/systemd/system/medvault.service`:

```bash
sudo nano /etc/systemd/system/medvault.service
```

Add the following content to the file. **Make sure to replace `<your_user>` and `<path_to_medvault-copy>` with your actual username and project path.**

```ini
[Unit]
Description=gunicorn daemon for medvault-copy
After=network.target

[Service]
User=<your_user>
Group=www-data
WorkingDirectory=<path_to_medvault-copy>
ExecStart=<path_to_medvault-copy>/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/medvault.sock \
          medvault_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

Now, start and enable the Gunicorn service:

```bash
sudo systemctl start medvault
sudo systemctl enable medvault
```

### 5. Set Up Nginx

Nginx will act as a reverse proxy, passing requests to the Gunicorn process.

**Create an Nginx Server Block:**

Create a new Nginx configuration file at `/etc/nginx/sites-available/medvault`:

```bash
sudo nano /etc/nginx/sites-available/medvault
```

Add the following content to the file. **Make sure to replace `your_server_ip_or_domain` with your actual IP address or domain name.**

```nginx
server {
    listen 80;
    server_name your_server_ip_or_domain;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root <path_to_medvault-copy>;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/medvault.sock;
    }
}
```

**Enable the Nginx Configuration:**

Create a symbolic link from the `sites-available` directory to the `sites-enabled` directory.

```bash
sudo ln -s /etc/nginx/sites-available/medvault /etc/nginx/sites-enabled
```

**Test and Restart Nginx:**

Test your Nginx configuration for syntax errors and then restart Nginx.

```bash
sudo nginx -t
sudo systemctl restart nginx
```

## Firewall Configuration

If you have a firewall enabled (e.g., `ufw`), you will need to allow traffic to Nginx.

```bash
sudo ufw allow 'Nginx Full'
```

## Next Steps

Your Medvault-Copy application should now be deployed and accessible at your server's IP address or domain name.

Here are some recommended next steps:

-   **Set up a domain name:** Point a domain name to your server's IP address.
-   **Secure with HTTPS:** Use Let's Encrypt to get a free SSL/TLS certificate and configure Nginx to use HTTPS.
