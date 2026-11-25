# Buscador de empleo

Busca cada día ofertas junior (0-2 años) para Sergio y las publica, ordenadas por encaje, en
**https://sergonm.github.io/buscador-empleo/**

- **Fuentes:** GetOnBoard (API pública, sin clave). Más fuentes vendrán después.
- **Filtros:** descarta senior (por título, nivel o años pedidos), ubicación fuera de Bogotá/Colombia/LATAM remoto y ofertas fuera de las áreas: Datos / ML, Negocio / Producto, Ciberseguridad / GRC. Sin duplicados.
- **Ranking:** puntaje 0-100 por área en el cargo, habilidades pedidas, nivel junior, modalidad, afinidad con Compliance/salud y frescura.
- **Horario:** GitHub Actions todos los días a las 7:00 a. m. (Bogotá). También se puede correr a mano en *Actions → Búsqueda diaria → Run workflow*.
- **Ajustes:** edita `perfil.json` (palabras de búsqueda, áreas, exclusiones).
- **WhatsApp (opcional):** agrega los secretos `CALLMEBOT_PHONE` y `CALLMEBOT_APIKEY`.

Todo corre con cuotas gratuitas de GitHub.
