#!/usr/bin/env python3
"""
=============================================================================
PROJETO TUPÃSAT — ESTAÇÃO DE SOLO WEB (GROUND STATION WEB DASHBOARD)
Painel de Controle e Telemetria em Tempo Real com Suporte a Rádio Real e Simulação

Características:
- Modo Real: Conecta à porta serial USB do receptor LoRa 915 MHz e aguarda
  pacotes reais do TupãSat (exibe '--' e 'Aguardando Satélite' até o primeiro sinal).
- Modo Simulado (--demo): Gera pacotes sintéticos para testes e aulas sem hardware.
- Botão na interface para alternar entre Modo Real e Modo Simulado em tempo de execução.
=============================================================================
"""

import sys
import os
import json
import time
import random
import threading
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

# Importa funções do dashboard base
sys.path.append(os.path.dirname(__file__))
from dashboard import parse_tupasat_packet, generate_demo_packet, calculate_crc16

# Estado global da telemetria
lock = threading.Lock()
is_simulation_active = False
serial_connected = False
active_serial_port = None
serial_instance = None

# Estrutura vazia padrão (quando nenhum satélite transmitiu ainda)
empty_telemetry = {
    "has_data": False,
    "mode": "REAL",
    "callsign": "TUPASAT",
    "packet_id": None,
    "uptime_s": None,
    "status": None,
    "v_bat": None,
    "current_ma": None,
    "power_mw": None,
    "soc_kalman": None,
    "temp_aht": None,
    "hum_aht": None,
    "temp_bmp": None,
    "press_hpa": None,
    "altitude_m": None,
    "roll": None,
    "pitch": None,
    "yaw": None,
    "gps_fix": None,
    "latitude": None,
    "longitude": None,
    "sat_count": None,
    "rssi": None,
    "snr": None,
    "last_update": "Aguardando primeiro pacote LoRa...",
    "status_text": "AGUARDANDO SATÉLITE (NENHUM SINAL RF DETECTADO)"
}

latest_telemetry = dict(empty_telemetry)

HTML_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TupãSat — Estação Terrena em Tempo Real</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg: #0b0f19;
            --card-bg: #141b2d;
            --card-border: #232d4b;
            --accent: #00d2ff;
            --accent-green: #00e676;
            --accent-orange: #ff9100;
            --accent-red: #ff1744;
            --text-main: #f0f4f8;
            --text-muted: #8a99ad;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg); color: var(--text-main); padding: 20px; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--card-border); flex-wrap: wrap; gap: 12px; }
        .logo-title h1 { font-size: 26px; color: var(--accent); letter-spacing: 1px; }
        .logo-title p { font-size: 13px; color: var(--text-muted); }
        .header-actions { display: flex; align-items: center; gap: 12px; }
        .badge-status { padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 12px; }
        .badge-waiting { background: rgba(255,145,0,0.15); color: var(--accent-orange); border: 1px solid var(--accent-orange); animation: pulse 2s infinite; }
        .badge-nominal { background: rgba(0,230,118,0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }
        .badge-demo { background: rgba(0,210,255,0.15); color: var(--accent); border: 1px solid var(--accent); }
        
        .mode-banner { background: #1c273c; border-left: 4px solid var(--accent); padding: 12px 16px; border-radius: 6px; margin-bottom: 20px; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }
        .mode-banner.demo-active { border-left-color: var(--accent-orange); background: #2a2016; }
        .btn-toggle-mode { background: #1e293b; border: 1px solid var(--card-border); color: #fff; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; }
        .btn-toggle-mode:hover { border-color: var(--accent); color: var(--accent); }

        .grid-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        .card-label { font-size: 12px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px; letter-spacing: 0.5px; }
        .card-value { font-size: 28px; font-weight: 700; color: #fff; }
        .card-unit { font-size: 14px; font-weight: normal; color: var(--text-muted); margin-left: 4px; }
        .card-sub { font-size: 12px; color: var(--accent); margin-top: 6px; }

        .grid-charts { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 24px; }
        @media(max-width: 900px) { .grid-charts { grid-template-columns: 1fr; } }
        .chart-box { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 20px; }
        .chart-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: var(--text-main); display: flex; justify-content: space-between; }
        .tc-console { display: flex; flex-direction: column; gap: 10px; }
        .tc-btn { background: #1e293b; border: 1px solid var(--accent); color: var(--accent); padding: 10px 14px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.2s; text-align: left; }
        .tc-btn:hover { background: var(--accent); color: #000; }
        .tc-btn.danger { border-color: var(--accent-red); color: var(--accent-red); }
        .tc-btn.danger:hover { background: var(--accent-red); color: #fff; }
        .attitude-box { display: flex; justify-content: space-around; text-align: center; padding: 12px 0; }
        .att-item { font-size: 13px; color: var(--text-muted); }
        .att-val { font-size: 20px; font-weight: bold; color: var(--accent); margin-top: 4px; }

        @keyframes pulse {
            0% { opacity: 0.7; }
            50% { opacity: 1; }
            100% { opacity: 0.7; }
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-title">
            <h1>TUPÃSAT-1U GROUND STATION</h1>
            <p>Monitoramento Orbital e Gerenciamento Térmico-Energético (TEMS)</p>
        </div>
        <div class="header-actions">
            <span id="satStatus" class="badge-status badge-waiting">AGUARDANDO SATÉLITE</span>
        </div>
    </header>

    <div id="modeBanner" class="mode-banner">
        <div>
            <strong id="modeTitle">MODO DE OPERAÇÃO: HARDWARE REAL</strong> — 
            <span id="modeDesc">Aguardando telemetria real via receptor LoRa 915 MHz plugado na USB.</span>
        </div>
        <button class="btn-toggle-mode" onclick="toggleMode()">Alternar para Modo Simulado (Demo)</button>
    </div>

    <div class="grid-cards">
        <div class="card">
            <div class="card-label">Tensão Barramento (EPS)</div>
            <div class="card-value"><span id="vBat">--</span><span class="card-unit">V</span></div>
            <div class="card-sub">SoC Kalman: <strong id="socKalman">--</strong>%</div>
        </div>
        <div class="card">
            <div class="card-label">Potência Instantânea</div>
            <div class="card-value"><span id="powerMw">--</span><span class="card-unit">mW</span></div>
            <div class="card-sub">Corrente: <span id="currentMa">--</span> mA</div>
        </div>
        <div class="card">
            <div class="card-label">Temperatura Interna</div>
            <div class="card-value"><span id="tempAht">--</span><span class="card-unit">°C</span></div>
            <div class="card-sub">Umidade: <span id="humAht">--</span>% UR</div>
        </div>
        <div class="card">
            <div class="card-label">Altitude Barométrica</div>
            <div class="card-value"><span id="altM">--</span><span class="card-unit">m</span></div>
            <div class="card-sub">Pressão: <span id="pressHpa">--</span> hPa</div>
        </div>
        <div class="card">
            <div class="card-label">Enlace RF LoRa 915 MHz</div>
            <div class="card-value"><span id="rssiVal">--</span><span class="card-unit">dBm</span></div>
            <div class="card-sub">SNR: <span id="snrVal">--</span> dB | Pkt: #<span id="pktId">--</span></div>
        </div>
    </div>

    <div class="grid-charts">
        <div class="chart-box">
            <div class="chart-title">
                <span>Histórico de Potência e Tensão (EPS)</span>
                <span id="chartSub" style="font-size: 12px; color: var(--text-muted);">Aguardando pacotes...</span>
            </div>
            <canvas id="powerChart" height="120"></canvas>
        </div>

        <div class="chart-box">
            <div class="chart-title">
                <span>Controle e Atitude (ADCS)</span>
            </div>
            <div class="attitude-box">
                <div class="att-item">ROLL<div id="attRoll" class="att-val">--°</div></div>
                <div class="att-item">PITCH<div id="attPitch" class="att-val">--°</div></div>
                <div class="att-item">YAW<div id="attYaw" class="att-val">--°</div></div>
            </div>
            <hr style="border: 0; border-top: 1px solid var(--card-border); margin: 16px 0;">
            <div class="chart-title" style="font-size: 14px;">Telecomandos de Solo (Uplink)</div>
            <div class="tc-console">
                <button class="tc-btn" onclick="sendCmd('PING')">📡 Enviar PING (Verificar Enlace)</button>
                <button class="tc-btn" onclick="sendCmd('SETRATE_1S')">⚡ Alta Taxa de Dados (Burst 1s)</button>
                <button class="tc-btn" onclick="sendCmd('SETRATE_5S')">⏱️ Taxa Nominal (5s)</button>
                <button class="tc-btn danger" onclick="sendCmd('REBOOT')">⚠️ Telecomando: Reiniciar OBC</button>
            </div>
        </div>
    </div>

    <script>
        let powerChart;
        const maxPoints = 25;
        const labels = [];
        const dataPower = [];
        const dataVoltage = [];

        function initChart() {
            const ctx = document.getElementById('powerChart').getContext('2d');
            powerChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Potência (mW)',
                            data: dataPower,
                            borderColor: '#00d2ff',
                            backgroundColor: 'rgba(0,210,255,0.1)',
                            borderWidth: 2,
                            tension: 0.3,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Tensão (V)',
                            data: dataVoltage,
                            borderColor: '#ff9100',
                            borderWidth: 2,
                            borderDash: [4, 4],
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8a99ad' } },
                        y: { position: 'left', grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#00d2ff' } },
                        y1: { position: 'right', grid: { drawOnChartArea: false }, ticks: { color: '#ff9100' } }
                    }
                }
            });
        }

        async function updateData() {
            try {
                const res = await fetch('/api/telemetry');
                const d = await res.json();

                const banner = document.getElementById('modeBanner');
                const modeTitle = document.getElementById('modeTitle');
                const modeDesc = document.getElementById('modeDesc');
                const btnToggle = document.querySelector('.btn-toggle-mode');
                const badge = document.getElementById('satStatus');

                if (d.mode === "DEMO") {
                    banner.className = "mode-banner demo-active";
                    modeTitle.innerText = "MODO DE OPERAÇÃO: SIMULAÇÃO DE BANCADA (DEMO)";
                    modeDesc.innerText = "Exibindo dados orbitais sintéticos para validação visual e didática da interface.";
                    btnToggle.innerText = "Alternar para Modo Hardware Real";
                    badge.className = "badge-status badge-demo";
                    badge.innerText = "SIMULAÇÃO ATIVA";
                } else {
                    banner.className = "mode-banner";
                    modeTitle.innerText = "MODO DE OPERAÇÃO: HARDWARE REAL";
                    modeDesc.innerText = d.has_data ? "Recepção ativa via rádio LoRa na porta USB." : "Aguardando primeiro pacote LoRa da porta USB serial...";
                    btnToggle.innerText = "Alternar para Modo Simulado (Demo)";
                    if (d.has_data) {
                        badge.className = "badge-status badge-nominal";
                        badge.innerText = "ENLACE ATIVO (RF OK)";
                    } else {
                        badge.className = "badge-status badge-waiting";
                        badge.innerText = "AGUARDANDO SATÉLITE";
                    }
                }

                if (!d.has_data) {
                    document.getElementById('vBat').innerText = "--";
                    document.getElementById('socKalman').innerText = "--";
                    document.getElementById('powerMw').innerText = "--";
                    document.getElementById('currentMa').innerText = "--";
                    document.getElementById('tempAht').innerText = "--";
                    document.getElementById('humAht').innerText = "--";
                    document.getElementById('altM').innerText = "--";
                    document.getElementById('pressHpa').innerText = "--";
                    document.getElementById('rssiVal').innerText = "--";
                    document.getElementById('snrVal').innerText = "--";
                    document.getElementById('pktId').innerText = "--";
                    document.getElementById('attRoll').innerText = "--°";
                    document.getElementById('attPitch').innerText = "--°";
                    document.getElementById('attYaw').innerText = "--°";
                    document.getElementById('chartSub').innerText = "Aguardando pacotes do satélite...";
                    return;
                }

                document.getElementById('vBat').innerText = d.v_bat !== null ? d.v_bat.toFixed(2) : "--";
                document.getElementById('socKalman').innerText = d.soc_kalman !== null ? d.soc_kalman.toFixed(1) : "--";
                document.getElementById('powerMw').innerText = d.power_mw !== null ? d.power_mw.toFixed(1) : "--";
                document.getElementById('currentMa').innerText = d.current_ma !== null ? d.current_ma.toFixed(1) : "--";
                document.getElementById('tempAht').innerText = d.temp_aht !== null ? d.temp_aht.toFixed(1) : "--";
                document.getElementById('humAht').innerText = d.hum_aht !== null ? d.hum_aht.toFixed(1) : "--";
                document.getElementById('altM').innerText = d.altitude_m !== null ? d.altitude_m.toFixed(1) : "--";
                document.getElementById('pressHpa').innerText = d.press_hpa !== null ? d.press_hpa.toFixed(1) : "--";
                document.getElementById('rssiVal').innerText = d.rssi !== null ? d.rssi : "--";
                document.getElementById('snrVal').innerText = d.snr !== null ? d.snr : "--";
                document.getElementById('pktId').innerText = d.packet_id !== null ? d.packet_id : "--";

                document.getElementById('attRoll').innerText = d.roll !== null ? d.roll.toFixed(1) + '°' : "--°";
                document.getElementById('attPitch').innerText = d.pitch !== null ? d.pitch.toFixed(1) + '°' : "--°";
                document.getElementById('attYaw').innerText = d.yaw !== null ? d.yaw.toFixed(1) + '°' : "--°";
                document.getElementById('chartSub').innerText = "Última atualização: " + d.last_update;

                // Atualiza Gráfico
                if (d.power_mw !== null && d.v_bat !== null) {
                    const nowLabel = new Date().toLocaleTimeString();
                    if (labels.length > maxPoints) {
                        labels.shift();
                        dataPower.shift();
                        dataVoltage.shift();
                    }
                    labels.push(nowLabel);
                    dataPower.push(d.power_mw);
                    dataVoltage.push(d.v_bat);
                    powerChart.update();
                }

            } catch (err) {
                console.error("Erro na busca de telemetria:", err);
            }
        }

        async function toggleMode() {
            try {
                const res = await fetch('/api/toggle_mode', { method: 'POST' });
                const d = await res.json();
                updateData();
            } catch (e) {
                alert("Erro ao alternar modo: " + e);
            }
        }

        async function sendCmd(cmdName) {
            try {
                const res = await fetch('/api/telecommand?cmd=' + encodeURIComponent(cmdName), { method: 'POST' });
                const d = await res.json();
                alert(d.message);
            } catch (e) {
                alert("Falha ao enviar comando: " + e);
            }
        }

        window.onload = () => {
            initChart();
            setInterval(updateData, 2000);
            updateData();
        };
    </script>
</body>
</html>
"""

class TelemetryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/api/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            with lock:
                payload = json.dumps(latest_telemetry)
            self.wfile.write(payload.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global is_simulation_active, latest_telemetry
        if self.path == "/api/toggle_mode":
            with lock:
                is_simulation_active = not is_simulation_active
                if not is_simulation_active:
                    latest_telemetry = dict(empty_telemetry)
                    latest_telemetry["mode"] = "REAL"
                else:
                    latest_telemetry["mode"] = "DEMO"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"is_simulation": is_simulation_active}).encode("utf-8"))
        elif self.path.startswith("/api/telecommand"):
            cmd = self.path.split("cmd=")[-1] if "cmd=" in self.path else "UNKNOWN"
            msg = f"Telecomando '{cmd}' enfileirado para transmissão via rádio LoRa."
            if serial_instance and serial_instance.is_open:
                try:
                    serial_instance.write(f"!TUPA_CMD,{cmd}*FFFF\n".encode("utf-8"))
                    msg += " (Enviado com sucesso pela porta serial)"
                except Exception as e:
                    msg += f" (Erro serial: {e})"
            else:
                msg += " (Aviso: Estação terrena física offline)"

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "OK", "message": msg}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def simulation_thread_worker():
    """Gera telemetrias contínuas apenas quando o modo de simulação estiver ativo."""
    global latest_telemetry
    pkt_id = 1
    while True:
        if is_simulation_active:
            raw_pkt = generate_demo_packet(pkt_id, version=2)
            telem, err = parse_tupasat_packet(raw_pkt)
            if telem:
                telem["has_data"] = True
                telem["mode"] = "DEMO"
                telem["rssi"] = random.randint(-92, -72)
                telem["snr"] = round(random.uniform(7.0, 10.5), 1)
                telem["last_update"] = datetime.now().strftime("%H:%M:%S")
                telem["status_text"] = "SIMULAÇÃO ORBITAL ATIVA (DADOS SINTÉTICOS)"
                with lock:
                    latest_telemetry = telem
            pkt_id += 1
        time.sleep(2.0)


def serial_reader_worker(port, baud):
    """Lê a porta serial real do receptor LoRa."""
    global latest_telemetry, serial_instance, serial_connected
    if not HAS_SERIAL:
        return

    print(f"[SERIAL] Iniciando monitoramento da porta {port} a {baud} bps...")
    while True:
        try:
            ser = serial.Serial(port, baud, timeout=2.0)
            serial_instance = ser
            serial_connected = True
            print(f"[SERIAL-OK] Conectado ao receptor LoRa na porta {port}.")
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line and not is_simulation_active:
                    rssi, snr = None, None
                    packet_str = line
                    if line.startswith("{") and line.endswith("}"):
                        try:
                            j = json.loads(line)
                            packet_str = j.get("raw", "")
                            rssi = j.get("rssi")
                            snr = j.get("snr")
                        except Exception:
                            pass

                    telem, err = parse_tupasat_packet(packet_str)
                    if telem:
                        telem["has_data"] = True
                        telem["mode"] = "REAL"
                        telem["rssi"] = rssi if rssi is not None else -80
                        telem["snr"] = snr if snr is not None else 8.0
                        telem["last_update"] = datetime.now().strftime("%H:%M:%S")
                        telem["status_text"] = "ENLACE ATIVO (PACOTE REAL RECEBIDO)"
                        with lock:
                            latest_telemetry = telem
        except Exception as e:
            serial_connected = False
            time.sleep(3.0) # Tenta reconectar se a porta desconectar


def main():
    global is_simulation_active
    parser = argparse.ArgumentParser(description="Web Dashboard da Estação Terrena TupãSat")
    parser.add_argument("--port", type=int, default=8080, help="Porta HTTP do servidor web (padrão: 8080)")
    parser.add_argument("--serial-port", type=str, default=None, help="Porta serial do receptor LoRa (ex: COM3, /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=115200, help="Baudrate serial (padrão: 115200)")
    parser.add_argument("--demo", action="store_true", help="Inicia no modo de simulação com dados sintéticos")
    args = parser.parse_args()

    # Define o modo inicial
    is_simulation_active = args.demo
    latest_telemetry["mode"] = "DEMO" if is_simulation_active else "REAL"

    # Inicia a thread de simulação
    sim_t = threading.Thread(target=simulation_thread_worker, daemon=True)
    sim_t.start()

    # Inicia a thread serial se uma porta for informada ou detectada
    if args.serial_port:
        ser_t = threading.Thread(target=serial_reader_worker, args=(args.serial_port, args.baud), daemon=True)
        ser_t.start()
    elif HAS_SERIAL:
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if ports:
            print(f"[INFO] Portas seriais detectadas: {ports}. Conectando automaticamente em {ports[0]}...")
            ser_t = threading.Thread(target=serial_reader_worker, args=(ports[0], args.baud), daemon=True)
            ser_t.start()
        else:
            print("[INFO] Nenhuma porta serial USB conectada no momento. Aguardando conexão de hardware...")

    server = HTTPServer(("0.0.0.0", args.port), TelemetryHandler)
    print(f"\n==================================================================")
    print(f"   TUPÃSAT WEB GROUND STATION ONLINE: http://localhost:{args.port}  ")
    print(f"==================================================================")
    if is_simulation_active:
        print(" [STATUS]: Iniciado em MODO SIMULADO (Demo Educacional com dados sintéticos).")
    else:
        print(" [STATUS]: Iniciado em MODO HARDWARE REAL.")
        print("           Exibindo '--' e 'Aguardando Satélite' até receber sinal do rádio LoRa.")
    print(" Pressione Ctrl+C para encerrar o servidor.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Servidor web encerrado pelo operador.")


if __name__ == "__main__":
    main()
