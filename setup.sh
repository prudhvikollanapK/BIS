#!/bin/bash

echo "Checking if virtualenv is installed..."
if ! pip show virtualenv > /dev/null 2>&1; then
    echo "Installing virtualenv..."
    pip install virtualenv
else
    echo "virtualenv is already installed."
fi

echo "Setting up virtual environment..."
virtualenv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py makemigrations bis_app
python manage.py migrate

echo "Creating superuser..."
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@example.com \
DJANGO_SUPERUSER_PASSWORD=admin123 \
python manage.py createsuperuser --noinput || echo "Superuser already exists."

echo "Starting the development server..."
python manage.py runserver &

echo "Opening the admin page in the browser..."
sleep 3
xdg-open http://127.0.0.1:8000/admin &

echo "Checking Docker status..."
if sudo systemctl status docker > /dev/null 2>&1; then
    echo "Docker is running."
else
    echo "Starting Docker..."
    sudo systemctl start docker
fi

if groups $USER | grep &>/dev/null '\bdocker\b'; then
    echo "User $USER is already in the docker group."
else
    echo "Adding user $USER to the docker group..."
    sudo usermod -aG docker $USER
    echo "You will need to log out and log back in for this to take effect."
fi

echo "Testing Docker without sudo..."
docker ps

echo "Setup is complete!"
