#!/bin/bash
cat <<EOF > mongo-setup.js
use agroTrack
db.createCollection("dueños")
db.createCollection("animales")
db.createCollection("alertas")
db.createCollection("campos")
db.createCollection("usuarios")
EOF

docker exec -i agroTrack mongosh < mongo-setup.js

rm mongo-setup.js
echo "¡Colecciones creadas en la base de datos agroTrack!"