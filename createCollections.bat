@echo off
echo use agroTrack > mongo-setup.js
echo db.createCollection("dueños") >> mongo-setup.js
echo db.createCollection("animales") >> mongo-setup.js
echo db.createCollection("alertas") >> mongo-setup.js
echo db.createCollection("campos") >> mongo-setup.js
echo db.createCollection("usuarios") >> mongo-setup.js

docker exec -i agroTrack mongosh < mongo-setup.js

del mongo-setup.js
pause