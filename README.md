# BIS (Browser Isolation Service)

## Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone https://github.com/prudhvikollanapK/BIS.git
    cd bis_app
    ```

2. **Set up the virtual environment**:
    ```bash
    python3 -m venv env 
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```
    or
   ```bash
   pip install virtualenv
   virtualenv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

4. **Install dependencies**:
     ```bash
     pip install -r requirements.txt
     ```

5. **Run migrations**:
    ```bash
    python manage.py makemigrations bis_app
    python manage.py migrate
    ```

6. **Create the superuser**:
    ```bash
    python manage.py createsuperuser
    ```

7. **Run the development server**:
    ```bash
    python manage.py runserver
    ```

8. **Open this url in browser for Database adminstration(login with superuser creds)**
    ```bash
    http://127.0.0.1:8000/admin
    ```
 ## Docker setup

1. **Ensure Docker is Running**:

   ***First, check if Docker is running. You can check Docker's status using***
    ```bash
    sudo systemctl status docker
    ```

   ***If Docker is not running, you can start it using***
    ```bash
    sudo systemctl start docker
    ```
2. **Add Your User to the Docker Group**:

   ***By default, Docker commands need to be run as the root user. To allow non-root users to access Docker, you need to add your user to the docker group.***

   ***Add your current user to the Docker group***
    ```bash
    sudo usermod -aG docker $USER
    ```

   ***After running the command, log out and back in again***
    ```bash
    newgrp docker
    ```

     ***Verify that your user has been added to the docker group***
    ```bash
    groups
    ```

     ***Test Docker without sudo***
    ```bash
    docker ps
    ```

***If this works without showing any permission issues, Docker is now properly accessible.***

## Final Steps
1. **After making sure Docker is accessible**
2. **Restart your Django application**
    ```bash
    python manage.py runserver
    ```
3.**Execute any one of this this**
    ```bash
    docker build -t custom-playwright . 
    docker build --no-cache -t custom-playwright .
    ```

4. **Hit the endpoint to start the Chrome container**
    ```bash
    http://localhost:8000/users/3/start-container/
    ```
5. **List Running Containers**
   ***To verify that the container is running, use the following command***
    ```bash
    docker ps
    ```
    ***This will display a list of all the running containers. You should see your container with the image browserless/chrome along with the port it's mapped to.***

6. **Access the Browser in the Container: Since you are running browserless/chrome, it will expose a port (in your case, likely 3000), which you can access in your browser.**
    ```bash
    http://localhost:3000
    ```
  ***This should give you access to the browserless Chrome instance running inside the Docker container. You can control the browser via its API or interface.***
  ![image](https://github.com/user-attachments/assets/32417424-c879-4b39-b497-17a2cec1b3f0)

6. **Searching the normal content**
   ![image](https://github.com/user-attachments/assets/16ccc013-5e67-4a4c-904b-fb15484d98c4)

7. **Searching the blocked content**
   ![image](https://github.com/user-attachments/assets/d196335a-c92f-48d0-a2c4-d3450c4226de)

6. **Stopping the Container**
   ```bash
    docker stop <container_id>
    ```
   or
      ```bash
    http://localhost:8000/containers/<container_id>/stop/
    ```
7. **Accessing the Container logs**
    ```bash
    http://localhost:8000/containers/<container_id>/logs/
    ```





