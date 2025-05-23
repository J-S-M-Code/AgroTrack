// Constante para la URL base de la API
const API_BASE_URL = "http://localhost:5000/api";

// Inicialización del mapa
const map = L.map("map").setView([-30.0, -66.0], 5); // Vista un poco más alejada inicialmente
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

let animalMarkers = [];
let userMarker = null;
let campoPolygon = null;
let userIcon; // Variable para el icono de usuario
let initialCampoLoad = true; // Bandera para controlar el primer centrado del campo

/**
 * Crea un icono personalizado para el usuario.
 * Considera usar un SVG inline o un placeholder si la URL falla.
 */
function createUserIcon() {
    // Icono de usuario (ejemplo, puedes personalizarlo)
    // Documentación de Leaflet para iconos: https://leafletjs.com/reference.html#icon
    return L.icon({
        iconUrl: 'https://placehold.co/40x40/3498db/ffffff?text=U', // Placeholder azul con 'U'
        iconSize: [30, 30], // Tamaño del icono
        iconAnchor: [15, 30], // Punto del icono que corresponderá a la ubicación del marcador
        popupAnchor: [0, -30], // Punto desde donde se abrirá el popup, relativo al iconAnchor
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png', // Sombra opcional
        shadowSize: [41, 41],
        shadowAnchor: [12, 41]
    });
}
userIcon = createUserIcon();

/**
 * Carga y muestra los datos de animales, usuarios y campos en el mapa.
 */
async function cargarDatosDelMapa() {
    try {
        const [animalesRes, usuariosRes, camposRes] = await Promise.all([
            fetch(`${API_BASE_URL}/animales`).catch(e => ({ ok: false, error: e, source: 'animales' })),
            fetch(`${API_BASE_URL}/usuarios`).catch(e => ({ ok: false, error: e, source: 'usuarios' })),
            fetch(`${API_BASE_URL}/campos`).catch(e => ({ ok: false, error: e, source: 'campos' })),
        ]);

        // Función auxiliar para procesar respuestas y manejar errores de red/fetch
        const processResponse = async (res, sourceName) => {
            if (!res.ok) {
                // Si res.error existe, es un error de red/fetch capturado por .catch()
                // Si no, es una respuesta HTTP no exitosa (ej. 404, 500)
                const errorMsg = res.error ? res.error.message : `HTTP ${res.status}: ${res.statusText}`;
                console.error(`Error al obtener datos de ${sourceName}: ${errorMsg}`);
                // Mostrar un mensaje en la UI podría ser útil aquí
                document.getElementById('noti-lista').innerHTML += `<div class="notificacion error">Error cargando ${sourceName}</div>`;
                return []; // Devuelve un array vacío para evitar más errores
            }
            try {
                return await res.json(); // Intenta parsear el JSON
            } catch (jsonError) {
                console.error(`Error al parsear JSON de ${sourceName}: ${jsonError.message}`);
                return []; // Devuelve un array vacío si el JSON es inválido
            }
        };

        const animales = await processResponse(animalesRes, 'animales');
        const usuarios = await processResponse(usuariosRes, 'usuarios');
        const campos = await processResponse(camposRes, 'campos');

        // --- Renderizar Animales ---
        animalMarkers.forEach(m => map.removeLayer(m));
        animalMarkers = [];

        if (animales && animales.length > 0) {
            animales.forEach(animal => {
                if (animal.coordenadas && typeof animal.coordenadas.lat === 'number' && typeof animal.coordenadas.lon === 'number') {
                    const animalCoord = [animal.coordenadas.lat, animal.coordenadas.lon];
                    // Icono de animal (ejemplo, puedes personalizarlo)
                    const animalIcon = L.icon({
                        iconUrl: 'https://placehold.co/40x40/2ecc71/ffffff?text=A', // Placeholder verde con 'A'
                        iconSize: [25, 25],
                        iconAnchor: [12, 25],
                        popupAnchor: [0, -25]
                    });
                    const marker = L.marker(animalCoord, {
                        title: `Animal ${animal._id}`,
                        icon: animalIcon
                    })
                        .addTo(map)
                        .bindPopup(`🐄 <strong>ID:</strong> ${animal._id}<br><strong>Desc:</strong> ${animal.descripcion || "N/A"}`);
                    animalMarkers.push(marker);
                }
            });
        }

        // --- Renderizar Usuario ---
        if (userMarker) map.removeLayer(userMarker);
        if (usuarios && usuarios.length > 0) {
            const usuario = usuarios[0]; // Tomamos el primer usuario para el ejemplo
            if (usuario.coordenadas && typeof usuario.coordenadas.lat === 'number' && typeof usuario.coordenadas.lon === 'number') {
                const userCoord = [usuario.coordenadas.lat, usuario.coordenadas.lon];
                userMarker = L.marker(userCoord, {
                    title: `Usuario ${usuario._id}`,
                    icon: userIcon // Usar el icono de usuario definido
                })
                    .addTo(map)
                    .bindPopup(`🧑 <strong>Usuario ID:</strong> ${usuario._id}`);
            }
        }

        // --- Renderizar Campo ---
        if (campoPolygon) map.removeLayer(campoPolygon);
        if (campos && campos.length > 0) {
            const campo = campos[0]; // Tomamos el primer campo para el ejemplo
            if (campo.poligono && Array.isArray(campo.poligono) && campo.poligono.length > 0) {
                // Filtrar coordenadas inválidas o mal formadas
                const campoCoords = campo.poligono
                    .filter(p => p && typeof p.lat === 'number' && typeof p.lon === 'number')
                    .map(p => [p.lat, p.lon]);

                if (campoCoords.length > 2) { // Un polígono necesita al menos 3 puntos válidos
                    campoPolygon = L.polygon(campoCoords, {
                        color: "#28a745", // Un verde más estándar
                        weight: 2,
                        fillColor: "#2ecc71",
                        fillOpacity: 0.3,
                    }).addTo(map).bindPopup(`🌾 <strong>Campo ID:</strong> ${campo._id}`);

                    // Centrar el mapa en el polígono del campo solo en la carga inicial
                    if (initialCampoLoad) {
                        map.fitBounds(campoPolygon.getBounds());
                        initialCampoLoad = false; // Desactivar la bandera
                    }
                } else if (campoCoords.length > 0) {
                    // Si hay pocos puntos, quizás mostrar marcadores individuales o una línea
                    console.warn(`Campo ${campo._id} tiene menos de 3 puntos válidos para formar un polígono.`);
                }
            } else if (initialCampoLoad && animalMarkers.length > 0) {
                // Si no hay campo pero hay animales en la carga inicial, centrar en los animales
                const group = new L.featureGroup(animalMarkers);
                map.fitBounds(group.getBounds().pad(0.5));
                initialCampoLoad = false;
            } else if (initialCampoLoad && userMarker) {
                // Si solo hay usuario en la carga inicial
                map.setView(userMarker.getLatLng(), 13);
                initialCampoLoad = false;
            } else if (initialCampoLoad) {
                initialCampoLoad = false; // Desactivar la bandera aunque no se ajuste la vista
            }
            // Si ya se cargó el campo una vez, no se vuelve a centrar.
        } else if (initialCampoLoad && animalMarkers.length > 0) {
            // Si no hay campo pero hay animales en la carga inicial
            const group = new L.featureGroup(animalMarkers);
            map.fitBounds(group.getBounds().pad(0.5));
            initialCampoLoad = false;
        } else if (initialCampoLoad && userMarker) {
            // Si solo hay usuario en la carga inicial
            map.setView(userMarker.getLatLng(), 13);
            initialCampoLoad = false;
        } else if (initialCampoLoad) {
            initialCampoLoad = false; // Asegurar que la bandera se desactive
        }
        // Si no hay campo en las actualizaciones posteriores, no se hace nada con la vista.

    } catch (error) {
        console.error("Error general en cargarDatosDelMapa:", error);
        // Mostrar un mensaje de error al usuario en la UI si es necesario
        const notiLista = document.getElementById("noti-lista");
        if (notiLista) {
            const errorDiv = document.createElement("div");
            errorDiv.className = "notificacion"; // Reutilizar clase de notificación para errores
            errorDiv.style.borderLeftColor = "#dc3545"; // Rojo para errores
            errorDiv.innerHTML = `<p>⚠️ Error al cargar datos del mapa: ${error.message}. Intente recargar.</p>`;
            notiLista.prepend(errorDiv); // Añadir al principio
        }
    }
}

/**
 * Carga y muestra las notificaciones.
 */
async function cargarNotificaciones() {
    const contenedor = document.getElementById("noti-lista");
    if (!contenedor) return;

    try {
        const res = await fetch(`${API_BASE_URL}/notificaciones`);
        if (!res.ok) {
            console.error("Error al obtener notificaciones:", res.status, res.statusText);
            // No limpiar el contenedor si falla, para no borrar notificaciones previas o mensajes de error
            contenedor.innerHTML = '<p>Error al cargar notificaciones.</p>'; // O añadir un mensaje de error
            return;
        }
        const notificaciones = await res.json();

        contenedor.innerHTML = ""; // Limpiar notificaciones anteriores solo si la petición fue exitosa

        if (notificaciones && notificaciones.length > 0) {
            notificaciones.forEach(n => {
                const div = document.createElement("div");
                div.className = "notificacion";
                // Asegurarse de que el mensaje y timestamp existen
                const mensaje = n.mensaje || "Mensaje no disponible";
                const fecha = n.timestamp ? new Date(n.timestamp).toLocaleTimeString() : "Hora no disponible";
                div.innerHTML = `<p>🚨 ${mensaje} (${fecha})</p>`;
                contenedor.appendChild(div);
            });
        } else {
            contenedor.innerHTML = "<p>No hay notificaciones nuevas.</p>";
        }
    } catch (error) {
        console.error("Error en cargarNotificaciones:", error);
        contenedor.innerHTML = "<p>Error al conectar con el servicio de notificaciones.</p>";
    }
}

// Cargar datos y notificaciones al inicio y luego periódicamente
window.addEventListener('load', () => {
    if (typeof L === 'undefined') {
        console.error("Leaflet no se ha cargado. El mapa no funcionará.");
        // Podrías mostrar un mensaje al usuario aquí.
        document.getElementById('map').innerHTML =
            '<div style="padding: 20px; text-align: center; background-color: #ffdddd; border: 1px solid red;">Error: La librería de mapas (Leaflet) no pudo cargarse. Verifique su conexión a internet o contacte al administrador.</div>';
        return;
    }

    cargarDatosDelMapa();
    cargarNotificaciones();

    setInterval(cargarDatosDelMapa, 5000); // Actualizar datos del mapa cada 5 segundos
    setInterval(cargarNotificaciones, 5000); // Actualizar notificaciones cada 5 segundos
});