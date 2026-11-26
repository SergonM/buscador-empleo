# Buscador de empleo

Busca cada día ofertas junior (0-2 años) para Sergio y las publica, ordenadas por encaje, en
**https://sergonm.github.io/buscador-empleo/**

- **Fuentes (todas gratis, sin clave), en paralelo:**
  - Portales Workday de multinacionales en Colombia (J&J, Medtronic, Pfizer, Mastercard, Salesforce, P&G, Kyndryl…).
  - Portales públicos de empresas en Greenhouse, Lever, Ashby, SmartRecruiters y Workable (Nubank, Addi, Sezzle, Clara, Cobre, Platzi, Truelogic, Endava…). Lista en `perfil.json` → `empresas` y `workday`.
  - GetOnBoard (API pública).
  - LinkedIn e Indeed Colombia vía [JobSpy](https://github.com/speedyapply/JobSpy) (también LinkedIn remoto LATAM): pocas búsquedas, solo últimas 24 h.
  - Remotos: Remotive, Himalayas, Jobicy (LATAM) y Remote OK.
  - Las ofertas de días anteriores se conservan hasta 30 días. Se pueden apagar fuentes en `perfil.json` → `fuentes`.
- **Filtros:** descarta senior (título, nivel, años pedidos, "III"), ubicación fuera de Bogotá/Colombia/LATAM remoto (incluido "Remote - US") y ofertas fuera de las áreas: Datos / ML, Negocio / Producto, Ciberseguridad / GRC. Sin duplicados (gana el portal de la empresa).
- **Ranking:** puntaje 0-100 por área, habilidades, nivel junior, frases como "recién egresado", modalidad, afinidad con Compliance/salud y frescura; además un puntaje de calidad de la oferta.
- **Página (app instalable):** pestañas Nuevas / Todas / Mi lista; filtros por área, modalidad, fuente, junior e idioma; seguimiento (guardada, postulé, entrevista, oferta, descartada) con notas y respaldo; por oferta: palabras clave para la hoja de vida, carta breve editable y mensaje para reclutador; panel con el estado de cada fuente.
- **Tus habilidades:** edita `perfil.json` → `mis_habilidades` para que las palabras clave y la carta reflejen lo que sí sabes.
- **Horario:** GitHub Actions todos los días a las 7:00 a. m. (Bogotá). También se puede correr a mano en *Actions → Búsqueda diaria → Run workflow*.
- **Aviso diario (opcional):** WhatsApp con los secretos `CALLMEBOT_PHONE` y `CALLMEBOT_APIKEY`, o Telegram con `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID`.

Todo corre con cuotas gratuitas de GitHub.
