# AgroTrack  
## Animal geolocation system  
This is intended to control the livestock on the farms in order to avoid road accidents and keep the livestock under control.  
## 📁 Project Structure Overview  
### main.py  
This class configures and launches an application, starting by setting up the logging system to suppress non-critical messages from the Werkzeug server (commonly used in Flask), setting its level to ERROR only to keep output clean. Then, in the main block (if __name__ == "__main__":), it imports and instantiates the AppRunner class (in charge of the core application logic) and runs its run() method to start the program.
### location_emulator.py  
This class simulates the periodic updating of locations for animals and users in the AgroTrack database, using GPS coordinates to track movement at 15-second intervals. It connects to a local MongoDB instance (mongodb://localhost:543/) and updates the animales and usuarios collections with new latitudes and longitudes in five stages ("Ubicación 0" to "Ubicación 4"), simulating real movements (e.g., the animal with ID "gps001" moves among nearby coordinates, while the user "user001" gradually moves away). 
### GeoUtils.py  
The GeoUtils class provides utilities for geographic calculations, including two static methods: animal_dentro_del_campo() checks if an animal’s coordinates (in the format {"lat": value, "lon": value}) are inside a polygon defined by a list of coordinates, using the shapely library to create a Polygon object and evaluate the point's containment; while distancia_km() calculates the distance in kilometers between two GPS coordinates using the geodetic formula from geopy.distance.geodesic, which is useful for determining proximity between animals, users, or field boundaries. Both methods operate with dictionary-formatted coordinates using lat and lon keys, integrable with agricultural monitoring systems.  
### DatabaseManager.py  
The DatabaseManager class manages the connection and operations with the AgroTrack database, automatically initializing the connection to the specified server (by default mongodb://localhost:543/) and accessing the AgroTrack database along with its main collections (animales, dueños, campos, usuarios, and alertas). If successful, it confirms the connection with a (💾) message; if it fails, it shows the error (❌) and terminates execution.    
### AppRunner.py  
The AppRunner class coordinates the start and execution of all main components of the AgroTrack application. Upon initialization, it creates instances of essential classes (DatabaseManager, GeoUtils, AlertManager, AnimalVerifier, and ApiServer) with their respective dependencies injected. When run() is executed, it starts four key processes:
1. Automatically opens the web interface in the browser (using webbrowser).   
2. Launches the location emulator in a secondary thread (via subprocess).
3. Starts the animal verifier in another thread for continuous monitoring.
4. Launches the API server on the main thread (using Flask).  

Threads are set as daemons to allow clean termination, while centralized error handling provides clear feedback during startup.  
### ApiServer.py
The ApiServer class implements a full REST API for the AgroTrack system using Flask, with all four main HTTP methods (GET, POST, PUT, DELETE) to manage owners, animals, fields, and users. It includes CORS to allow cross-origin requests and connects to MongoDB via the injected DatabaseManager. Each method follows the CRUD pattern: GET endpoints retrieve data (full listings or individual entries), POST creates new records with required field validation, PUT updates existing records (except the ID), and DELETE removes records. It handles errors with appropriate HTTP codes (404 for not found, 400 for invalid data, etc.) and returns standardized JSON responses.  
### AnimalVerifier.py
The AnimalVerifier class is the core of the animal monitoring system in AgroTrack, designed to periodically check animals' locations and generate alerts when they leave their designated zones. Its operation starts with injected dependencies: db_manager to access the MongoDB database, geo_utils for geographic calculations such as geofence verification, and alert_manager for managing notifications.
The main method verificar_animales() iterates over all registered animals, checking for each one if it has a valid assigned field; if the field doesn’t exist, it logs a warning and skips verification, while if it does, it uses geo_utils.animal_dentro_del_campo() to determine if the animal’s coordinates are within the field polygon. If the animal is inside, a confirmation is logged (✅), but if it is outside (❌), alerts are triggered: first it checks if an alert should be sent to the owner via debe_enviar_alerta() to avoid redundant notifications, then notifies nearby users with alertar_usuarios_cercanos(), which also considers geographic proximity and time since the last alert.
The method iniciar_verificador() runs this process in an infinite loop every 5 seconds (simulating 5 minutes in production), logging execution times and separating cycles with lines for clarity in the logs.  
### AlertManager.py  
The AlertManager class is the core of the smart notification system in AgroTrack, designed to efficiently manage the complete alert cycle from detection to logging. Upon initialization, it receives db_manager (for interacting with MongoDB) and geo_utils (for accurate geographic calculations) as dependencies.
Its operation starts when the system detects anomalies, beginning with the alertar_dueño() method, which looks up the owner associated with the animal that triggered the alert (using the idDueño field), generates a clear message like "🔔 Alert sent to owner Carlos Méndez - Animal toro123 is outside the field", and logs the incident in the alertas collection with all relevant metadata, including exact coordinates and a local timezone timestamp for temporal consistency.
For notifications to nearby users, the alertar_usuarios_cercanos() method implements a two-level severity system: it calculates accurate distances with geo_utils.distancia_km() and classifies alerts as "🚨 CRITICAL ALERT" (≤0.5 km) or "⚠️ Alert" (≤1 km), avoiding redundant notifications by checking the last similar alert with debe_enviar_alerta_usuario(), which only allows new alerts if more than 5 minutes have passed (configurable).
### collections
#### createCollections.bat  
This script automatically creates and runs an initial setup for the AgroTrack MongoDB database inside a Docker container for Windows systems. It first generates a temporary file called mongo-setup.js containing MongoDB commands: selects/creates a database called agroTrack (use agroTrack) and then creates five collections (equivalent to tables in relational databases) called dueños, animales, alertas, campos, and usuarios. Then, the script uses the docker exec command to run these commands inside the Docker container named agroTrack through the MongoDB shell (mongosh), passing the JavaScript file as input. Finally, it deletes the temporary setup file (mongo-setup.js) and pauses execution (pause) to allow viewing the results before the window closes.  
#### createCollections.sh
It has the same functionality as its Windows counterpart, the difference is that this is for GNU/Linux distributions.
## Dependencies  
Python 3  
Docker  
MongoDB
## System installation  
Copy repository
### For Windows 
1.  [Download Docker][def1]  
    [Download Python][def2]  
    [Download Repository][def3]
2. Unzip the .zip file
3. Press win+r
4. type cmd and press enter
5. Run the following commands
```cmd 
docker pull mongo
```
```cmd
docker run -d -p 543:543 --name agroTrack mongo
```
&nbsp;We see if the database is running
```cmd
docker ps
```
6. We create the db collections. Run the createCollections.bat file.  
7. Run the main.py file.  
### For Linux
1. Run terminal
2. Run the following commands
```bash
sudo apt update
```
```bash
sudo apt install -y python3 python3-pip
```
2. Create the virtual environment
```bash
python -m venv ./venv
```
3. Activate the virtual environment
```bash
source ./venv/bin/activate
```
4. Install docker
```bash
sudo apt install docker.io
```
5. Install MongoDB with docker
```bash
sudo docker run -d -p 543:543 --name agroTrack mongo
```
6. Run the db
```bash
sudo docker start
```
&nbsp;We see if the database is running
```bash
sudo docker ps
```
7. We create the db collections. Run the createCollections.sh file.  
8. Run the main.py file.  


[def1]: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe?utm_source=docker&utm_medium=webreferral&utm_campaign=dd-smartbutton&utm_location=module
[def2]: https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe
[def3]: https://codeload.github.com/J-S-M-Code/AgroTrack/zip/refs/heads/main