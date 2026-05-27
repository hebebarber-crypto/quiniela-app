"""
🎰 TU QUINIELA ASISTENTE - PWA (App Móvil)
Lista para Railway y para instalar en celular
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import random
from collections import Counter
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__, static_folder='static')

# ==========================================
# DATOS SIMULADOS (30 sorteos con fechas)
# ==========================================
random.seed(42)
fecha_base = datetime(2026, 5, 24)
sorteos = []

for i in range(30):
    fecha = fecha_base - timedelta(days=i)
    for horario in ['Mañana', 'Tarde', 'Noche', 'Extra']:
        numeros = random.sample(range(0, 100), 20)
        sorteos.append({
            'numero_sorteo': 4000 + (i * 4) + len(sorteos) - (i * 4),
            'fecha': fecha.strftime('%Y-%m-%d'),
            'horario': horario,
            'numeros': numeros
        })

sorteos.sort(key=lambda x: (x['fecha'], x['numero_sorteo']), reverse=True)

# ==========================================
# TABLA DE SUEÑOS
# ==========================================
tabla_suenios = {
    "huevos": ["00", "15"], "agua": ["01", "16"], "niño": ["02", "17"],
    "san cono": ["03", "18"], "la cama": ["04", "19"], "gato": ["05", "20"],
    "perro": ["06", "21"], "loco": ["07", "22"], "fuego": ["08", "23"],
    "cárcel": ["09", "24"], "leche": ["10", "25"], "palacio": ["11", "26"],
    "yeta": ["12", "27"], "muerte": ["13", "28"], "enamorado": ["14", "29"],
    "niña bonita": ["15", "30"], "misa": ["16", "31"], "desgracia": ["17", "32"],
    "sangre": ["18", "33"], "comida": ["19", "34"], "iglesia": ["20", "35"],
    "mujer": ["21", "36"], "loco grande": ["22", "37"], "cirujano": ["23", "38"],
    "caballo": ["24", "39"], "monja": ["25", "40"], "mierda": ["26", "41"],
    "cuchillo": ["27", "42"], "cerro": ["28", "43"], "san pedro": ["29", "44"],
    "santa rosa": ["30", "45"], "luz": ["31", "46"], "dinero": ["32", "47"],
    "cristo": ["33", "48"], "cabeza": ["34", "49"], "pajarito": ["35", "50"],
    "fuego grande": ["36", "51"], "dentista": ["37", "52"], "piedras": ["38", "53"],
    "lluvia": ["39", "54"], "cura": ["40", "55"], "cuchillo grande": ["41", "56"],
    "zapatillas": ["42", "57"], "balcón": ["43", "58"], "cárcel vieja": ["44", "59"],
    "vino": ["45", "60"], "tomates": ["46", "61"], "muerto": ["47", "62"],
    "muerto que habla": ["48", "63"], "borracho": ["49", "64"], "pan": ["50", "65"],
    "serrucho": ["51", "66"], "madre": ["52", "67"], "hospital": ["53", "68"],
    "vaca": ["54", "69"], "música": ["55", "70"], "caída": ["56", "71"],
    "jorobado": ["57", "72"], "ahorcado": ["58", "73"], "gente": ["59", "74"],
    "tormenta": ["60", "75"], "escopeta": ["61", "76"], "inundación": ["62", "77"],
    "casamiento": ["63", "78"], "llanto": ["64", "79"], "cazador": ["65", "80"],
    "lombrices": ["66", "81"], "mordida": ["67", "82"], "hermanos": ["68", "83"],
    "pescado": ["69", "84"], "limosna": ["70", "85"], "excremento": ["71", "86"],
    "sorpresa": ["72", "87"], "hospital viejo": ["73", "88"], "gente negra": ["74", "89"],
    "beso": ["75", "90"], "humo": ["76", "91"], "pierna": ["77", "92"],
    "ramera": ["78", "93"], "ladrón": ["79", "94"], "policía": ["80", "95"],
    "flores": ["81", "96"], "pelea": ["82", "97"], "trabajo": ["83", "98"],
    "velorio": ["84", "99"],
}

# ==========================================
# FUNCIONES DE ANÁLISIS
# ==========================================
def filtrar_por_dias(sorteos, dias):
    if dias >= 30:
        return sorteos
    fecha_limite = fecha_base - timedelta(days=dias)
    return [s for s in sorteos if datetime.strptime(s['fecha'], '%Y-%m-%d') >= fecha_limite]

def calcular_frecuencias(sorteos_filtrados):
    todos = []
    primeros_5 = []
    for sorteo in sorteos_filtrados:
        todos.extend(sorteo['numeros'])
        primeros_5.extend(sorteo['numeros'][:5])
    return Counter(todos), Counter(primeros_5)

def numeros_ausentes(sorteos_filtrados):
    salidos = set()
    for s in sorteos_filtrados:
        salidos.update(s['numeros'])
    return sorted([f"{n:02d}" for n in set(range(100)) - salidos])

def numeros_frecuentes(sorteos_filtrados, top=10):
    freq, _ = calcular_frecuencias(sorteos_filtrados)
    return freq.most_common(top)

def numeros_frecuentes_top5(sorteos_filtrados, top=10):
    _, freq5 = calcular_frecuencias(sorteos_filtrados)
    return freq5.most_common(top)

def numeros_infrecuentes_top5(sorteos_filtrados, top=10):
    _, freq5 = calcular_frecuencias(sorteos_filtrados)
    return freq5.most_common()[:-top-1:-1]

def buscar_suenio(palabra):
    palabra = palabra.lower().strip()
    resultados = []
    for clave, nums in tabla_suenios.items():
        if palabra in clave:
            resultados.append((clave, nums))
    return resultados if resultados else None

def buscar_numero(num_str, sorteos_filtrados):
    try:
        n = int(num_str)
        nf = f"{n:02d}"
    except:
        return None, None, None, None
    significado = next((k for k, v in tabla_suenios.items() if nf in v), None)
    freq, freq5 = calcular_frecuencias(sorteos_filtrados)
    return significado, freq.get(n, 0), freq5.get(n, 0), nf

def generar_combinacion(sorteos_filtrados):
    ausentes = numeros_ausentes(sorteos_filtrados)
    freq = numeros_frecuentes(sorteos_filtrados, 30)
    freq5 = numeros_frecuentes_top5(sorteos_filtrados, 30)
    infreq5 = numeros_infrecuentes_top5(sorteos_filtrados, 30)
    
    if not ausentes: ausentes = ["00"]
    if not freq: freq = [("00", 0)]
    if not freq5: freq5 = [("00", 0)]
    if not infreq5: infreq5 = [("99", 0)]
    
    n1 = ausentes[0]
    n2 = f"{freq[len(freq)//3][0]:02d}" if len(freq) > 3 else f"{freq[0][0]:02d}"
    n3 = f"{freq5[len(freq5)//2][0]:02d}" if len(freq5) > 2 else f"{freq5[0][0]:02d}"
    n4 = f"{infreq5[0][0]:02d}"
    
    return [n1, n2, n3, n4]

def obtener_ultimos_sorteos(n=3):
    resultado = []
    for s in sorteos[:n]:
        nums = [f"{x:02d}" for x in s['numeros']]
        resultado.append({
            'numero': s['numero_sorteo'],
            'fecha': s['fecha'],
            'horario': s['horario'],
            'primeros5': nums[:5],
            'primeros10': nums[:10],
            'completos': nums
        })
    return resultado

# ==========================================
# HTML + CSS + JS (PWA optimizado)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#0d1117">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="/icon-192.png">
    <title>🎰 Tu Quiniela Asistente</title>
    <style>
        :root {
            --bg: #0d1117;
            --card: #161b22;
            --border: #30363d;
            --text: #e6edf3;
            --gold: #ffd700;
            --red: #ff4757;
            --green: #2ed573;
            --orange: #ffa502;
            --blue: #1e90ff;
            --purple: #a55eea;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 12px;
            padding-bottom: 80px;
        }
        .container { max-width: 600px; margin: 0 auto; }
        
        .header {
            text-align: center;
            padding: 15px 0;
            border-bottom: 2px solid var(--border);
            margin-bottom: 15px;
        }
        .header h1 { font-size: 1.6em; color: var(--gold); }
        .header p { color: #8b949e; margin-top: 5px; font-size: 0.8em; }

        .periodo-selector {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 12px;
            margin-bottom: 15px;
            text-align: center;
        }
        .periodo-opciones {
            display: flex;
            gap: 6px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .periodo-btn {
            padding: 8px 14px;
            border: 2px solid var(--border);
            background: transparent;
            color: var(--text);
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.8em;
        }
        .periodo-btn.activo {
            background: var(--gold);
            color: var(--bg);
            border-color: var(--gold);
        }

        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 16px;
            margin-bottom: 15px;
        }
        .card h2 {
            color: var(--gold);
            margin-bottom: 12px;
            font-size: 1.1em;
        }

        .botones-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 8px;
        }
        .btn {
            padding: 12px;
            border: none;
            border-radius: 14px;
            cursor: pointer;
            font-weight: 700;
            font-size: 0.85em;
            color: white;
            text-align: center;
        }
        .btn:active { transform: scale(0.97); }
        .btn-atrasados { background: linear-gradient(135deg, #ff4757, #c0392b); }
        .btn-frecuentes { background: linear-gradient(135deg, #2ed573, #27ae60); }
        .btn-frec5 { background: linear-gradient(135deg, #ffa502, #e67e22); }
        .btn-infrec5 { background: linear-gradient(135deg, #1e90ff, #2980b9); }
        .btn-suenio { background: linear-gradient(135deg, #a55eea, #8e44ad); }
        .btn-numero { background: linear-gradient(135deg, #1abc9c, #16a085); }
        .btn-jugada {
            background: linear-gradient(135deg, #ff4757, #ffa502, #2ed573);
            font-size: 1em;
            grid-column: 1 / -1;
            animation: brillo 2s infinite;
        }
        @keyframes brillo {
            0%, 100% { box-shadow: 0 0 10px rgba(255,215,0,0.5); }
            50% { box-shadow: 0 0 25px rgba(255,215,0,0.8); }
        }
        .btn-ultimos { background: linear-gradient(135deg, #34495e, #2c3e50); }

        .input-grupo {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }
        .input-grupo input {
            padding: 12px 14px;
            border-radius: 25px;
            border: 2px solid var(--border);
            background: var(--bg);
            color: white;
            font-size: 0.9em;
            flex: 1;
        }
        .input-grupo input:focus {
            border-color: var(--gold);
            outline: none;
        }
        .input-grupo button {
            padding: 12px 20px;
            border-radius: 25px;
            border: none;
            cursor: pointer;
            font-weight: bold;
            color: white;
        }

        #resultados { margin-top: 15px; }
        .resultado-card {
            background: var(--card);
            border: 2px solid var(--gold);
            border-radius: 20px;
            padding: 16px;
            margin-top: 12px;
            animation: aparecer 0.3s ease-out;
        }
        @keyframes aparecer {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .resultado-card h3 { color: var(--gold); margin-bottom: 8px; }
        .info-periodo {
            color: #8b949e;
            font-size: 0.75em;
            margin-bottom: 12px;
            padding: 6px 10px;
            background: rgba(255,215,0,0.08);
            border-radius: 10px;
            display: inline-block;
        }
        .numeros-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
            margin: 12px 0;
        }
        .bola {
            width: 55px;
            height: 55px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 1.1em;
            position: relative;
        }
        .bola-normal {
            background: radial-gradient(circle at 35% 30%, #fff8dc, var(--gold), #b8860b);
            color: #1a1a2e;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .bola-sugerida {
            background: radial-gradient(circle at 35% 30%, #ff6b6b, #c0392b, #8b0000);
            color: white;
            box-shadow: 0 0 15px rgba(255,71,87,0.6);
            animation: latido 1.5s infinite;
        }
        @keyframes latido {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.08); }
        }
        .bola .frecuencia {
            position: absolute;
            bottom: -6px;
            right: -6px;
            background: var(--bg);
            color: var(--text);
            font-size: 0.55em;
            padding: 2px 5px;
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        .sorteo-mini {
            background: rgba(0,0,0,0.3);
            padding: 10px;
            border-radius: 12px;
            margin: 8px 0;
            border-left: 3px solid var(--gold);
        }
        .bola-chica {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: radial-gradient(circle at 35% 30%, #fff8dc, var(--gold), #b8860b);
            color: #1a1a2e;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7em;
            font-weight: 800;
            margin: 2px;
        }
        .criterio-box {
            background: rgba(255,215,0,0.1);
            padding: 10px;
            border-radius: 12px;
            margin-top: 12px;
            font-size: 0.8em;
        }
        .loading-text {
            text-align: center;
            padding: 30px;
            color: var(--gold);
        }
        .aviso-legal {
            text-align: center;
            color: #484f58;
            font-size: 0.65em;
            padding: 15px;
            margin-top: 15px;
            border-top: 1px solid var(--border);
        }
        .install-banner {
            background: linear-gradient(135deg, #2ed573, #27ae60);
            color: white;
            padding: 12px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 15px;
            cursor: pointer;
            display: none;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="install-banner" id="installBanner">
            📱 Instalar esta app en tu celular
        </div>
        
        <div class="header">
            <h1>🎰 Tu Quiniela Asistente</h1>
            <p>Análisis para la Quiniela de Tucumán</p>
            <p style="font-size:0.65em;">⚠️ Uso educativo · +18</p>
        </div>

        <div class="periodo-selector">
            <label>📅 Período de análisis</label>
            <div class="periodo-opciones">
                <button class="periodo-btn" onclick="cambiarPeriodo(7)">7 días</button>
                <button class="periodo-btn activo" onclick="cambiarPeriodo(15)">15 días</button>
                <button class="periodo-btn" onclick="cambiarPeriodo(30)">30 días</button>
                <button class="periodo-btn" onclick="cambiarPeriodo(99)">Todos</button>
            </div>
            <p style="font-size:0.7em; margin-top:6px;" id="info-periodo-actual">📊 Últimos 15 días</p>
        </div>

        <div class="card">
            <h2>🔮 Consultas rápidas</h2>
            <div class="botones-grid">
                <button class="btn btn-atrasados" onclick="mostrarInput('atrasados')">🔴 Atrasados</button>
                <button class="btn btn-frecuentes" onclick="consultar('frecuentes')">🟢 + Frecuentes</button>
                <button class="btn btn-frec5" onclick="consultar('frecuentes_top5')">🟡 Frecuentes 1°-5°</button>
                <button class="btn btn-infrec5" onclick="consultar('infrecuentes_top5')">🔵 Infrecuentes 1°-5°</button>
                <button class="btn btn-suenio" onclick="mostrarInput('suenio')">💤 Soñé con...</button>
                <button class="btn btn-numero" onclick="mostrarInput('numero')">🔍 Investigar número</button>
                <button class="btn btn-ultimos" onclick="consultar('ultimos')">📋 Últimos sorteos</button>
                <button class="btn btn-jugada" onclick="consultar('combinacion')">🍀 ¡MI JUGADA!</button>
            </div>
            <div id="input-dinamico"></div>
        </div>

        <div id="resultados"></div>
        <div class="aviso-legal">🎯 Los números son sugerencias estadísticas · No garantizan aciertos</div>
    </div>

    <script>
        let periodoActual = 15;
        let deferredPrompt;

        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('installBanner').style.display = 'block';
        });

        document.getElementById('installBanner').addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                deferredPrompt = null;
                document.getElementById('installBanner').style.display = 'none';
            }
        });

        function cambiarPeriodo(dias) {
            periodoActual = dias;
            document.querySelectorAll('.periodo-btn').forEach(b => b.classList.remove('activo'));
            document.querySelector(`.periodo-btn[onclick="cambiarPeriodo(${dias})"]`).classList.add('activo');
            const texto = dias >= 99 ? 'todos los sorteos' : `últimos ${dias} días`;
            document.getElementById('info-periodo-actual').innerHTML = `📊 ${texto}`;
            document.getElementById('resultados').innerHTML = '';
            document.getElementById('input-dinamico').innerHTML = '';
        }

        function mostrarInput(tipo) {
            const div = document.getElementById('input-dinamico');
            if (tipo === 'atrasados') {
                div.innerHTML = `<div class="input-grupo"><input type="number" id="dias-atraso" placeholder="Días sin salir" value="5"><button class="btn-atrasados" onclick="consultarAtrasados()">Buscar</button></div>`;
            } else if (tipo === 'suenio') {
                div.innerHTML = `<div class="input-grupo"><input type="text" id="suenio-input" placeholder="Ej: agua, muerte, caballo"><button class="btn-suenio" onclick="consultarSuenio()">Buscar</button></div>`;
            } else if (tipo === 'numero') {
                div.innerHTML = `<div class="input-grupo"><input type="number" id="numero-input" placeholder="Número (00-99)"><button class="btn-numero" onclick="consultarNumero()">Investigar</button></div>`;
            }
        }

        function consultarAtrasados() {
            const dias = document.getElementById('dias-atraso').value || 5;
            fetch(`/api/ausentes?periodo=${periodoActual}&dias=${dias}`).then(r => r.json()).then(mostrarResultado);
        }

        function consultarSuenio() {
            const palabra = document.getElementById('suenio-input').value.trim();
            if (!palabra) return alert('Escribí una palabra clave');
            fetch(`/api/suenio?palabra=${encodeURIComponent(palabra)}&periodo=${periodoActual}`).then(r => r.json()).then(mostrarResultado);
        }

        function consultarNumero() {
            const num = document.getElementById('numero-input').value;
            if (num === '') return alert('Ingresá un número');
            fetch(`/api/numero?num=${num}&periodo=${periodoActual}`).then(r => r.json()).then(mostrarResultado);
        }

        function consultar(tipo) {
            document.getElementById('resultados').innerHTML = '<div class="loading-text">🔮 Analizando...</div>';
            document.getElementById('input-dinamico').innerHTML = '';
            fetch(`/api/${tipo}?periodo=${periodoActual}`).then(r => r.json()).then(mostrarResultado);
        }

        function mostrarResultado(data) {
            const div = document.getElementById('resultados');
            if (data.error) {
                div.innerHTML = `<div class="resultado-card"><h3>❌ ${data.error}</h3></div>`;
                return;
            }

            let html = `<div class="resultado-card">`;
            if (data.periodo_texto) html += `<span class="info-periodo">📅 ${data.periodo_texto}</span>`;

            if (data.tipo === 'ausentes') {
                html += `<h3>🔴 ATRASADOS</h3><p>No salieron en ${data.dias_atraso} días</p><div class="numeros-grid">`;
                data.numeros.forEach(n => { html += `<div class="bola bola-normal">${n}</div>`; });
                html += '</div>';
            }
            else if (data.tipo === 'frecuentes') {
                html += `<h3>🟢 MÁS FRECUENTES</h3><div class="numeros-grid">`;
                data.numeros.forEach(item => { html += `<div class="bola bola-normal">${item[0]}<span class="frecuencia">${item[1]}</span></div>`; });
                html += '</div>';
            }
            else if (data.tipo === 'frecuentes_top5') {
                html += `<h3>🟡 FRECUENTES en 1°-5°</h3><div class="numeros-grid">`;
                data.numeros.forEach(item => { html += `<div class="bola bola-normal">${item[0]}<span class="frecuencia">${item[1]}</span></div>`; });
                html += '</div>';
            }
            else if (data.tipo === 'infrecuentes_top5') {
                html += `<h3>🔵 MENOS FRECUENTES en 1°-5°</h3><div class="numeros-grid">`;
                data.numeros.forEach(item => { html += `<div class="bola bola-normal">${item[0]}<span class="frecuencia">${item[1]}</span></div>`; });
                html += '</div>';
            }
            else if (data.tipo === 'suenio') {
                html += `<h3>💤 Soñaste con: "${data.palabra_buscada}"</h3>`;
                data.resultados.forEach(r => {
                    html += `<p><strong>📖 ${r.significado}</strong></p><div class="numeros-grid">`;
                    r.numeros.forEach(n => html += `<div class="bola bola-normal">${n}</div>`);
                    html += `</div>`;
                });
            }
            else if (data.tipo === 'numero') {
                html += `<h3>🔍 Número ${data.numero}</h3>`;
                html += `<p>📖 ${data.significado || 'No está en la tabla'}</p>`;
                html += `<p>📊 Frecuencia: ${data.frecuencia} veces</p>`;
            }
            else if (data.tipo === 'combinacion') {
                html += `<h3>🍀 TU JUGADA</h3><div class="numeros-grid">`;
                data.numeros.forEach(n => { html += `<div class="bola bola-sugerida">${n}</div>`; });
                html += `</div><div class="criterio-box">${data.criterio}</div>`;
            }
            else if (data.tipo === 'ultimos') {
                html += `<h3>📋 ÚLTIMOS SORTEOS</h3>`;
                data.sorteos.forEach(s => {
                    html += `<div class="sorteo-mini"><strong>#${s.numero}</strong> ${s.fecha} ${s.horario}<br><span style="font-size:0.7em;">1ros 5: ${s.primeros5.join(' ')}</span></div>`;
                });
            }

            html += '</div>';
            div.innerHTML = html;
            div.scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""

# ==========================================
# RUTAS DE LA API
# ==========================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/manifest.json')
def manifest():
    return {
        "name": "Tu Quiniela Asistente",
        "short_name": "Quiniela",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0d1117",
        "theme_color": "#0d1117",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    }

@app.route('/icon-192.png')
def icon_192():
    from flask import send_file
    import io
    from PIL import Image, ImageDraw
    
    img = Image.new('RGB', (192, 192), color='#ffd700')
    draw = ImageDraw.Draw(img)
    draw.ellipse([46, 46, 146, 146], fill='#0d1117')
    
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/icon-512.png')
def icon_512():
    from flask import send_file
    import io
    from PIL import Image, ImageDraw
    
    img = Image.new('RGB', (512, 512), color='#ffd700')
    draw = ImageDraw.Draw(img)
    draw.ellipse([126, 126, 386, 386], fill='#0d1117')
    
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/api/ausentes')
def api_ausentes():
    periodo = int(request.args.get('periodo', 15))
    dias = int(request.args.get('dias', 5))
    sorteos_periodo = filtrar_por_dias(sorteos, periodo)
    sorteos_atraso = sorteos_periodo[:min(dias*4, len(sorteos_periodo))]
    nums = numeros_ausentes(sorteos_atraso)
    texto = 'todos los sorteos' if periodo >= 30 else f'últimos {periodo} días'
    return jsonify({
        'tipo': 'ausentes',
        'periodo_texto': f'{texto} ({len(sorteos_periodo)} sorteos)',
        'dias_atraso': min(dias, len(sorteos_periodo)//4),
        'numeros': nums[:20]
    })

@app.route('/api/frecuentes')
def api_frecuentes():
    periodo = int(request.args.get('periodo', 15))
    sorteos_periodo = filtrar_por_dias(sorteos, periodo)
    freq = numeros_frecuentes(sorteos_periodo, 10)
    texto = 'todos los sorteos' if periodo >= 30 else f'últimos {periodo} días'
    return jsonify({
        'tipo': 'frecuentes',
        'periodo_texto': f'{texto} ({len(sorteos_periodo)} sorteos)',
        'numeros': [[f"{n:02d}", c] for n, c in freq]
    })

@app.route('/api/frecuentes_top5')
def api_frecuentes_top5():
    periodo = int(request.args.get('periodo', 15))
    sorteos_periodo = filtrar_por_dias(sorteos, periodo)
    freq = numeros_frecuentes_top5(sorteos_periodo, 10)
    texto = 'todos los sorteos' if periodo >= 30 else f'últimos {periodo} días'
    return jsonify({
        'tipo': 'frecuentes_top5',
        'periodo_texto': f'{texto} ({len(sorteos_periodo)} sorteos)',
        'numeros': [[f"{n:02d}", c] for n, c in freq]
    })

@app.route('/api/infrecuentes_top5')
def api_infrecuentes_top5():
    periodo = int(request.args.get('periodo', 15))
    sorteos_periodo = filtrar_por_dias(sorteos, periodo)
    freq = numeros_infrecuentes_top5(sorteos_periodo, 10)
    texto = 'todos los sorteos' if periodo >= 30 else f'últimos {periodo} días'
    return jsonify({
        'tipo': 'infrecuentes_top5',
        'periodo_texto': f'{texto} ({len(sorteos_periodo)} sorteos)',
        'numeros': [[f"{n:02d}", c] for n, c in freq]
    })

@app.route('/api/suenio')
def api_suenio():
    palabra = request.args.get('palabra', '')
    resultados = buscar_suenio(palabra)
    periodo = int(request.args.get('periodo', 15))
    texto = 'todos los sorteos' if periodo >= 30 else f'últimos {periodo} días'
    if not resultados:
        return jsonify({'error': f'No encontré "{palabra}"'})
    return jsonify({
        'tipo': 'suenio',
        'palabra_buscada': palabra,
        'periodo_texto': texto,
        'resultados': [{'significado': s, 'numeros': n} for s, n in resultados]
    })

@app.route('/api/numero')
def api_numero():
    num = request.args.get('num', '')
    periodo = int(request.args.get('periodo', 15))
    sorteos_periodo = filtrar_por_dias(sorteos, periodo)
    sig, freq, freq5, nf = buscar_numero(num, sorteos_periodo)
    texto = 'todos los sorteos' if periodo >= 30 else f'últimos {periodo} días'
    if nf is None:
        return jsonify({'error': 'Número inválido'})
    return jsonify({
        'tipo': 'numero',
        'numero': nf,
        'significado': sig,
        'frecuencia': freq,
        'periodo_texto': f'{texto} ({len(sorteos_periodo)} sorteos)'
    })

@app.route('/api/combinacion')
def api_combinacion():
    periodo = int(request.args.get('periodo', 15))
    sorteos_periodo = filtrar_por_dias(sorteos, periodo)
    nums = generar_combinacion(sorteos_periodo)
    texto = 'todos los sorteos' if periodo >= 30 else f'últimos {periodo} días'
    return jsonify({
        'tipo': 'combinacion',
        'periodo_texto': f'{texto} ({len(sorteos_periodo)} sorteos)',
        'numeros': nums,
        'criterio': '🎯 1 atrasado + 1 frecuente + 1 frecuente en 1ros 5 + 1 sorpresa'
    })

@app.route('/api/ultimos')
def api_ultimos():
    return jsonify({
        'tipo': 'ultimos',
        'sorteos': obtener_ultimos_sorteos(5)
    })

# ==========================================
# INICIO
# ==========================================
if __name__ == '__main__':
    print("\n" + "="*55)
    print("🎰  TU QUINIELA ASISTENTE - PWA (App Móvil)")
    print("="*55)
    print("\n✅ Servidor iniciado!")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)