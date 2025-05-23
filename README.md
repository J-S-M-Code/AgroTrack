# AgroTrack  
## Animal geolocation system  
This is intended to control the livestock on the farms in order to avoid road accidents and keep the livestock under control.  
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