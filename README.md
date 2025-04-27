# AgroTrack  
## Animal geolocation system  
This is intended to control the livestock on the farms in order to avoid road accidents and keep the livestock under control.  
## Dependencies  
Python 3  
Docker  
MongoDB
## System installation  
### For Windows 
1.  [Download Docker][def1]  
    [Download Python][def2]  
2. Press win+r
3. type cmd and press enter
4. Run the following commands
```cmd 
docker pull mongo
```
```cmd
docker run -d -p 543:543 --name agroTrack mongo
```
```cmd
docker exec -it agroTrack mongosh
```
&nbsp;If it doesn't work, try with
```cmd
docker exec -i agroTrack mongosh
```
```cmd
Agregar un archivo que cree los archivos por primera vez
```


[def1]: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe?utm_source=docker&utm_medium=webreferral&utm_campaign=dd-smartbutton&utm_location=module
[def2]: https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe