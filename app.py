"""
🎰 TU QUINIELA ASISTENTE - Versión Web Mejorada
Ejecutar: python app_quiniela.py
Abrir: http://127.0.0.1:5000
"""

from flask import Flask, render_template_string, request, jsonify
import random
from collections import Counter
from datetime import datetime, timedelta

app = Flask(__name__)

# ==========================================
# DATOS SIMULADOS: 30 sorteos con fechas
# ==========================================
random.seed(42)
fecha_base = datetime(2026, 5, 24)
sorteos = []

for i in range(30):
    fecha = fecha_base - timedelta(days=i)
    # Simular 4 sorteos por día (mañana, tarde, noche, extra)
    for horario in ['Mañana', 'Tarde', 'Noche', 'Extra']:
        numeros = random.sample(range(0, 100), 20)
        sorteos.append({
            'numero_sorteo': 4000 + (i * 4) + len(sorteos) - (i * 4),
            'fecha': fecha.strftime('%Y-%m-%d'),
            'horario': horario,
            'numeros': numeros
        })

# Ordenar por fecha y número
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
    """Filtra sorteos por cantidad de días hacia atrás."""
    if dias >= 30:  # "Todos" los sorteos
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
# HTML + CSS + JS (Todo integrado)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 15px;
        }
        .container { max-width: 750px; margin: 0 auto; }
        
        /* Header */
        .header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 2px solid var(--border);
            margin-bottom: 20px;
        }
        .header h1 { font-size: 2em; color: var(--gold); }
        .header .emoji { font-size: 1.5em; }
        .header p { color: #8b949e; margin-top: 5px; font-size: 0.9em; }

        /* Selector de período */
        .periodo-selector {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        .periodo-selector label {
            font-weight: bold;
            color: var(--gold);
            display: block;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        .periodo-opciones {
            display: flex;
            gap: 8px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .periodo-btn {
            padding: 10px 20px;
            border: 2px solid var(--border);
            background: transparent;
            color: var(--text);
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            font-size: 0.95em;
        }
        .periodo-btn:hover { border-color: var(--gold); color: var(--gold); }
        .periodo-btn.activo {
            background: var(--gold);
            color: var(--bg);
            border-color: var(--gold);
        }

        /* Cards */
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .card h2 {
            color: var(--gold);
            margin-bottom: 15px;
            font-size: 1.2em;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .card h2 .icono { font-size: 1.3em; }

        /* Grid de botones */
        .botones-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 10px;
        }
        .btn {
            padding: 14px 18px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 700;
            font-size: 0.9em;
            transition: all 0.25s;
            color: white;
            text-align: center;
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.4); filter: brightness(1.15); }
        .btn:active { transform: translateY(0); }

        .btn-atrasados { background: linear-gradient(135deg, #ff4757, #c0392b); }
        .btn-frecuentes { background: linear-gradient(135deg, #2ed573, #27ae60); }
        .btn-frec5 { background: linear-gradient(135deg, #ffa502, #e67e22); }
        .btn-infrec5 { background: linear-gradient(135deg, #1e90ff, #2980b9); }
        .btn-suenio { background: linear-gradient(135deg, #a55eea, #8e44ad); }
        .btn-numero { background: linear-gradient(135deg, #1abc9c, #16a085); }
        .btn-jugada {
            background: linear-gradient(135deg, #ff4757, #ffa502, #2ed573);
            font-size: 1.1em;
            grid-column: 1 / -1;
            animation: brillo 2s infinite;
        }
        @keyframes brillo {
            0%, 100% { box-shadow: 0 0 10px rgba(255,215,0,0.5); }
            50% { box-shadow: 0 0 30px rgba(255,215,0,0.8); }
        }
        .btn-ultimos { background: linear-gradient(135deg, #34495e, #2c3e50); }

        /* Inputs dinámicos */
        .input-grupo {
            display: flex;
            gap: 10px;
            margin-top: 12px;
            flex-wrap: wrap;
        }
        .input-grupo input {
            padding: 12px 16px;
            border-radius: 25px;
            border: 2px solid var(--border);
            background: var(--bg);
            color: white;
            font-size: 1em;
            flex: 1;
            min-width: 150px;
            transition: border 0.3s;
        }
        .input-grupo input:focus {
            border-color: var(--gold);
            outline: none;
        }
        .input-grupo button {
            padding: 12px 24px;
            border-radius: 25px;
            border: none;
            cursor: pointer;
            font-weight: bold;
            color: white;
        }

        /* Resultados */
        #resultados { margin-top: 20px; }
        .resultado-card {
            background: var(--card);
            border: 2px solid var(--gold);
            border-radius: 16px;
            padding: 20px;
            margin-top: 15px;
            animation: aparecer 0.4s ease-out;
        }
        @keyframes aparecer {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .resultado-card h3 {
            color: var(--gold);
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        .resultado-card .info-periodo {
            color: #8b949e;
            font-size: 0.85em;
            margin-bottom: 15px;
            padding: 8px 12px;
            background: rgba(255,215,0,0.08);
            border-radius: 8px;
            display: inline-block;
        }
        .numeros-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin: 15px 0;
        }
        .bola {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 1.1em;
            position: relative;
            transition: transform 0.3s;
        }
        .bola:hover { transform: scale(1.15); }
        .bola-normal {
            background: radial-gradient(circle at 35% 30%, #fff8dc, var(--gold), #b8860b);
            color: #1a1a2e;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
        .bola-sugerida {
            background: radial-gradient(circle at 35% 30%, #ff6b6b, #c0392b, #8b0000);
            color: white;
            box-shadow: 0 0 20px rgba(255,71,87,0.6);
            animation: latido 1.5s infinite;
        }
        @keyframes latido {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.12); }
        }
        .bola .frecuencia {
            position: absolute;
            bottom: -8px;
            right: -8px;
            background: var(--bg);
            color: var(--text);
            font-size: 0.6em;
            padding: 2px 6px;
            border-radius: 10px;
            border: 1px solid var(--border);
            font-weight: normal;
        }
        .sorteo-mini {
            background: rgba(0,0,0,0.3);
            padding: 12px;
            border-radius: 10px;
            margin: 8px 0;
            border-left: 3px solid var(--gold);
        }
        .sorteo-mini strong { color: var(--gold); }
        .sorteo-mini .bolas-chicas {
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
            margin-top: 5px;
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
        }
        .criterio-box {
            background: rgba(255,215,0,0.1);
            padding: 12px;
            border-radius: 10px;
            margin-top: 12px;
            font-size: 0.9em;
            color: #ccc;
        }
        .loading-text {
            text-align: center;
            padding: 30px;
            color: var(--gold);
            font-size: 1.1em;
        }
        .aviso-legal {
            text-align: center;
            color: #484f58;
            font-size: 0.75em;
            padding: 20px;
            margin-top: 20px;
            border-top: 1px solid var(--border);
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }
        .badge-atrasado { background: rgba(255,71,87,0.2); color: #ff4757; }
        .badge-frecuente { background: rgba(46,213,115,0.2); color: #2ed573; }
        .badge-top5 { background: rgba(255,165,2,0.2); color: #ffa502; }
        .badge-infrec5 { background: rgba(30,144,255,0.2); color: #1e90ff; }
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <h1><span class="emoji">🎰</span> Tu Quiniela Asistente</h1>
            <p>Análisis inteligente para la Quiniela de Tucumán</p>
            <p style="font-size:0.75em; color:#484f58;">⚠️ Demo educativo · Datos simulados · +18</p>
        </div>

        <!-- SELECTOR DE PERÍODO -->
        <div class="periodo-selector">
            <label>📅 ¿Desde cuándo querés analizar?</label>
            <div class="periodo-opciones">
                <button class="periodo-btn" onclick="cambiarPeriodo(7)" id="btn-7">Últimos 7 días</button>
                <button class="periodo-btn activo" onclick="cambiarPeriodo(15)" id="btn-15">Últimos 15 días</button>
                <button class="periodo-btn" onclick="cambiarPeriodo(30)" id="btn-30">Últimos 30 días</button>
                <button class="periodo-btn" onclick="cambiarPeriodo(99)" id="btn-99">📊 Todos</button>
            </div>
            <p style="font-size:0.8em; color:#8b949e; margin-top:8px;" id="info-periodo-actual">
                ⏳ Mostrando estadísticas de los <strong>últimos 15 días</strong>
            </p>
        </div>

        <!-- CONSULTAS -->
        <div class="card">
            <h2><span class="icono">🔮</span> ¿Qué querés consultar?</h2>
            <div class="botones-grid">
                <button class="btn btn-atrasados" onclick="mostrarInput('atrasados')">
                    🔴 Números atrasados
                    <br><small style="font-weight:normal;">(No salieron en X días)</small>
                </button>
                <button class="btn btn-frecuentes" onclick="consultar('frecuentes')">
                    🟢 Más frecuentes
                    <br><small style="font-weight:normal;">(Los que más salen)</small>
                </button>
                <button class="btn btn-frec5" onclick="consultar('frecuentes_top5')">
                    🟡 Frecuentes 1° a 5°
                    <br><small style="font-weight:normal;">(Primeras posiciones)</small>
                </button>
                <button class="btn btn-infrec5" onclick="consultar('infrecuentes_top5')">
                    🔵 Infrecuentes 1° a 5°
                    <br><small style="font-weight:normal;">(Menos salen 1ros)</small>
                </button>
                <button class="btn btn-suenio" onclick="mostrarInput('suenio')">
                    💤 Soñé con...
                    <br><small style="font-weight:normal;">(Buscar por sueño)</small>
                </button>
                <button class="btn btn-numero" onclick="mostrarInput('numero')">
                    🔍 Investigar número
                    <br><small style="font-weight:normal;">(Significado y stats)</small>
                </button>
                <button class="btn btn-ultimos" onclick="consultar('ultimos')">
                    📋 Últimos sorteos
                </button>
                <button class="btn btn-jugada" onclick="consultar('combinacion')">
                    🍀 ¡QUIERO MI JUGADA! 🍀
                </button>
            </div>
            <div id="input-dinamico"></div>
        </div>

        <!-- RESULTADOS -->
        <div id="resultados"></div>
    </div>

    <script>
        // Período global
        let periodoActual = 15;

        function cambiarPeriodo(dias) {
            periodoActual = dias;
            // Actualizar botones
            document.querySelectorAll('.periodo-btn').forEach(b => b.classList.remove('activo'));
            document.getElementById(`btn-${dias}`).classList.add('activo');
            // Actualizar texto
            const texto = dias >= 99 ? 'todos los sorteos' : `los últimos ${dias} días`;
            document.getElementById('info-periodo-actual').innerHTML = 
                `⏳ Mostrando estadísticas de <strong>${texto}</strong>`;
            // Limpiar resultados
            document.getElementById('resultados').innerHTML = '';
            document.getElementById('input-dinamico').innerHTML = '';
        }

        function mostrarInput(tipo) {
            const div = document.getElementById('input-dinamico');
            if (tipo === 'atrasados') {
                div.innerHTML = `
                    <div class="input-grupo" style="margin-top:15px;">
                        <input type="number" id="dias-atraso" placeholder="Días sin salir (ej: 5)" min="1" max="30" value="5">
                        <button class="btn-atrasados" onclick="consultarAtrasados()" style="border-radius:25px;">
                            🔍 Buscar atrasados
                        </button>
                    </div>`;
            } else if (tipo === 'suenio') {
                div.innerHTML = `
                    <div class="input-grupo" style="margin-top:15px;">
                        <input type="text" id="suenio-input" placeholder="Ej: agua, muerte, caballo, mujer...">
                        <button class="btn-suenio" onclick="consultarSuenio()" style="border-radius:25px; background:#a55eea;">
                            💤 Buscar números
                        </button>
                    </div>`;
            } else if (tipo === 'numero') {
                div.innerHTML = `
                    <div class="input-grupo" style="margin-top:15px;">
                        <input type="number" id="numero-input" placeholder="Número (00-99)" min="0" max="99">
                        <button class="btn-numero" onclick="consultarNumero()" style="border-radius:25px; background:#1abc9c;">
                            🔍 Investigar
                        </button>
                    </div>`;
            }
        }

        function consultarAtrasados() {
            const dias = document.getElementById('dias-atraso').value || 5;
            fetch(`/api/ausentes?periodo=${periodoActual}&dias=${dias}`)
                .then(r => r.json())
                .then(mostrarResultado);
        }

        function consultarSuenio() {
            const palabra = document.getElementById('suenio-input').value.trim();
            if (!palabra) return alert('✍️ Escribí una palabra clave de tu sueño');
            fetch(`/api/suenio?palabra=${encodeURIComponent(palabra)}&periodo=${periodoActual}`)
                .then(r => r.json())
                .then(mostrarResultado);
        }

        function consultarNumero() {
            const num = document.getElementById('numero-input').value;
            if (num === '') return alert('🔢 Ingresá un número del 00 al 99');
            fetch(`/api/numero?num=${num}&periodo=${periodoActual}`)
                .then(r => r.json())
                .then(mostrarResultado);
        }

        function consultar(tipo) {
            document.getElementById('resultados').innerHTML = 
                '<div class="loading-text">🔮 Analizando datos...</div>';
            document.getElementById('input-dinamico').innerHTML = '';
            
            fetch(`/api/${tipo}?periodo=${periodoActual}`)
                .then(r => r.json())
                .then(mostrarResultado);
        }

        function mostrarResultado(data) {
            const div = document.getElementById('resultados');
            if (data.error) {
                div.innerHTML = `
                    <div class="resultado-card" style="border-color:#ff4757;">
                        <h3>❌ ${data.error}</h3>
                        <p style="color:#8b949e;">Probá con otra palabra o parámetro.</p>
                    </div>`;
                return;
            }

            let html = `<div class="resultado-card">`;

            // Info del período
            const textoPeriodo = data.periodo_texto || '';
            if (textoPeriodo) {
                html += `<span class="info-periodo">📅 ${textoPeriodo}</span>`;
            }

            // Render según tipo
            if (data.tipo === 'ausentes') {
                html += `<h3>🔴 Números ATRASADOS</h3>`;
                html += `<p style="color:#8b949e;">No salieron en los <strong>últimos ${data.dias_atraso} días</strong></p>`;
                html += `<p style="color:#8b949e;font-size:0.85em;">📊 Analizando ${data.sorteos_analizados} sorteos</p>`;
                html += '<div class="numeros-grid">';
                data.numeros.forEach(n => {
                    html += `<div class="bola bola-normal"><span class="badge badge-atrasado" style="position:absolute;top:-8px;font-size:0.55em;">atrasado</span>${n}</div>`;
                });
                html += '</div>';
            }
            
            else if (data.tipo === 'frecuentes') {
                html += `<h3>🟢 Números MÁS FRECUENTES (General)</h3>`;
                html += `<p style="color:#8b949e;font-size:0.85em;">📊 ${data.sorteos_analizados} sorteos analizados</p>`;
                html += '<div class="numeros-grid">';
                data.numeros.forEach(item => {
                    html += `<div class="bola bola-normal" title="Salió ${item[1]} veces">${item[0]}<span class="frecuencia">${item[1]}x</span></div>`;
                });
                html += '</div>';
            }
            
            else if (data.tipo === 'frecuentes_top5') {
                html += `<h3>🟡 Más FRECUENTES entre los PRIMEROS 5</h3>`;
                html += `<p style="color:#8b949e;font-size:0.85em;">📊 ${data.sorteos_analizados} sorteos · Posiciones 1° a 5°</p>`;
                html += '<div class="numeros-grid">';
                data.numeros.forEach(item => {
                    html += `<div class="bola bola-normal" title="Salió ${item[1]} veces en 1ros 5">${item[0]}<span class="frecuencia">${item[1]}x</span></div>`;
                });
                html += '</div>';
            }
            
            else if (data.tipo === 'infrecuentes_top5') {
                html += `<h3>🔵 Menos FRECUENTES entre los PRIMEROS 5</h3>`;
                html += `<p style="color:#8b949e;font-size:0.85em;">📊 ${data.sorteos_analizados} sorteos · Posiciones 1° a 5°</p>`;
                html += '<div class="numeros-grid">';
                data.numeros.forEach(item => {
                    html += `<div class="bola bola-normal" title="Salió ${item[1]} veces en 1ros 5">${item[0]}<span class="frecuencia">${item[1]}x</span></div>`;
                });
                html += '</div>';
            }
            
            else if (data.tipo === 'suenio') {
                html += `<h3>💤 Soñaste con: "${data.palabra_buscada}"</h3>`;
                if (data.resultados.length === 1) {
                    const r = data.resultados[0];
                    html += `<p>📖 Significado: <strong style="color:var(--gold);">"${r.significado}"</strong></p>`;
                    html += '<div class="numeros-grid">';
                    r.numeros.forEach(n => html += `<div class="bola bola-normal">${n}</div>`);
                    html += '</div>';
                } else {
                    html += `<p style="color:#8b949e;">Se encontraron ${data.resultados.length} coincidencias:</p>`;
                    data.resultados.forEach(r => {
                        html += `<div style="margin:10px 0; padding:10px; background:rgba(0,0,0,0.2); border-radius:8px;">`;
                        html += `<strong>📖 "${r.significado}"</strong> → `;
                        r.numeros.forEach(n => html += `<span class="bola-chica">${n}</span> `);
                        html += `</div>`;
                    });
                }
            }
            
            else if (data.tipo === 'numero') {
                html += `<h3>🔍 Número ${data.numero}</h3>`;
                html += `<p>📖 Significado: <strong style="color:var(--gold);">${data.significado || 'No está en la tabla tradicional'}</strong></p>`;
                html += `<p>📊 Frecuencia general: <strong>${data.frecuencia} veces</strong> en ${data.sorteos_analizados} sorteos</p>`;
                html += `<p>📊 En primeros 5: <strong>${data.frecuencia_top5} veces</strong></p>`;
            }
            
            else if (data.tipo === 'combinacion') {
                html += `<h3>🍀 TU JUGADA SUGERIDA</h3>`;
                html += `<p style="color:#8b949e;font-size:0.85em;">📊 Basado en ${data.sorteos_analizados} sorteos</p>`;
                html += '<div class="numeros-grid" style="gap:15px;">';
                const criterios = [
                    '🔴 Atrasado', '🟢 Frecuente general', 
                    '🟡 Frecuente 1°-5°', '🔵 Sorpresa (infrecuente 1°-5°)'
                ];
                data.numeros.forEach((n, i) => {
                    html += `<div style="text-align:center;">
                        <div class="bola bola-sugerida">${n}</div>
                        <small style="color:#8b949e;display:block;margin-top:5px;">${criterios[i]}</small>
                    </div>`;
                });
                html += '</div>';
                html += `<div class="criterio-box">${data.criterio}</div>`;
            }
            
            else if (data.tipo === 'ultimos') {
                html += `<h3>📋 Últimos sorteos</h3>`;
                html += `<p style="color:#8b949e;font-size:0.85em;">📊 ${data.total_sorteos_disponibles} sorteos en total · Mostrando últimos ${data.sorteos.length}</p>`;
                data.sorteos.forEach(s => {
                    html += `<div class="sorteo-mini">`;
                    html += `<strong>#${s.numero}</strong> · ${s.fecha} · ${s.horario}<br>`;
                    html += `<span style="color:var(--gold);font-size:0.8em;">1ros 5:</span> `;
                    html += `<span class="bolas-chicas">`;
                    s.primeros5.forEach(n => html += `<span class="bola-chica">${n}</span>`);
                    html += `</span><br>`;
                    html += `<span style="color:#8b949e;font-size:0.75em;">10 primeros: ${s.primeros10.join(' ')}</span>`;
                    html += `</div>`;
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
# RUTAS DE LA API (actualizadas con período)
# ==========================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ausentes')
def api_ausentes():
    periodo = int(request.args.get('periodo', 15))
    dias = int(request.args.get('dias', 5))
    sorteos_periodo = filtrar_por_dias(sorteos, periodo)
    sorteos_atraso = sorteos_periodo[:min(dias*4, len(sorteos_periodo))]  # ~4 sorteos/día
    nums = numeros_ausentes(sorteos_atraso)
    texto = 'todos los sorteos' if periodo >= 30 else f'últimos {periodo} días'
    return jsonify({
        'tipo': 'ausentes',
        'periodo_texto': f'Período: {texto} ({len(sorteos_periodo)} sorteos)',
        'dias_atraso': min(dias, len(sorteos_periodo)//4),
        'sorteos_analizados': len(sorteos_atraso),
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
        'periodo_texto': f'Período: {texto} ({len(sorteos_periodo)} sorteos)',
        'sorteos_analizados': len(sorteos_periodo),
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
        'periodo_texto': f'Período: {texto} ({len(sorteos_periodo)} sorteos) · Solo 1° a 5° posición',
        'sorteos_analizados': len(sorteos_periodo),
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
        'periodo_texto': f'Período: {texto} ({len(sorteos_periodo)} sorteos) · Solo 1° a 5° posición',
        'sorteos_analizados': len(sorteos_periodo),
        'numeros': [[f"{n:02d}", c] for n, c in freq]
    })

@app.route('/api/suenio')
def api_suenio():
    palabra = request.args.get('palabra', '')
    resultados = buscar_suenio(palabra)
    periodo = int(request.args.get('periodo', 15))
    texto = 'todos los sorteos' if periodo >= 30 else f'últimos {periodo} días'
    if not resultados:
        return jsonify({'error': f'No encontré "{palabra}". Probá con: agua, muerte, caballo, mujer, dinero...'})
    return jsonify({
        'tipo': 'suenio',
        'palabra_buscada': palabra,
        'periodo_texto': f'📅 {texto}',
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
        return jsonify({'error': 'Número no válido. Ingresá un número del 00 al 99.'})
    return jsonify({
        'tipo': 'numero',
        'numero': nf,
        'significado': sig,
        'frecuencia': freq,
        'frecuencia_top5': freq5,
        'sorteos_analizados': len(sorteos_periodo),
        'periodo_texto': f'📅 {texto} ({len(sorteos_periodo)} sorteos)'
    })

@app.route('/api/combinacion')
def api_combinacion():
    periodo = int(request.args.get('periodo', 15))
    sorteos_periodo = filtrar_por_dias(sorteos, periodo)
    nums = generar_combinacion(sorteos_periodo)
    texto = 'todos los sorteos' if periodo >= 30 else f'últimos {periodo} días'
    return jsonify({
        'tipo': 'combinacion',
        'periodo_texto': f'📅 {texto} ({len(sorteos_periodo)} sorteos)',
        'sorteos_analizados': len(sorteos_periodo),
        'numeros': nums,
        'criterio': '💡 <strong>Estrategia balanceada:</strong><br>'
                    '🔴 1 número atrasado (no salió en varios días)<br>'
                    '🟢 1 número frecuente general (zona media-alta)<br>'
                    '🟡 1 número frecuente en primeras 5 posiciones<br>'
                    '🔵 1 número sorpresa (poco frecuente en 1ros 5)'
    })

@app.route('/api/ultimos')
def api_ultimos():
    periodo = int(request.args.get('periodo', 15))
    return jsonify({
        'tipo': 'ultimos',
        'total_sorteos_disponibles': len(sorteos),
        'periodo_texto': f'Últimos sorteos',
        'sorteos': obtener_ultimos_sorteos(5)
    })

# ==========================================
# INICIO
# ==========================================
if __name__ == '__main__':
    print("\n" + "="*55)
    print("🎰  TU QUINIELA ASISTENTE - Versión Web 2.0")
    print("="*55)
    print("\n✅ Servidor iniciado!")
    print("🌐 Abrí: http://127.0.0.1:5000")
    print("\n📊 Datos simulados: 120 sorteos (30 días × 4 horarios)")
    print("🎯 Seleccioná el período arriba para ver estadísticas")
    print("\nPresioná Ctrl+C para salir\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
