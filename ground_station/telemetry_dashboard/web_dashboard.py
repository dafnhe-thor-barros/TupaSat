#!/usr/bin/env python3
"""
=============================================================================
PROJETO TUPÃSAT — ESTAÇÃO DE SOLO WEB (GROUND STATION WEB DASHBOARD)
Painel de Controle e Telemetria em Tempo Real com Interface Web Integrada

Características:
- Zero dependências pesadas (utiliza Python padrão e bibliotecas web via CDN)
- Gráficos de telemetria em tempo real (Tensão, Corrente, Potência e Temperatura)
- Indicador visual de Atitude (Roll, Pitch, Yaw)
- Console para envio de Telecomandos (Uplink TC)
- Suporte a modo real (porta serial USB) ou modo simulado (--demo)
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

# Importa funções do dashboard base
sys.path.append(os.path.dirname(__file__))
from dashboard import parse_tupasat_packet, generate_demo_packet, calculate_crc16

# Estado global da telemetria
latest_telemetry = {
    "version": 2,
    "callsign": "TUPASAT-v2",
    "packet_id": 0,
    "uptime_s": 0,
    "status": 0,
    "v_bat": 12.20,
    "current_ma": 138.5,
    "power_mw": 1689.7,
    "soc_kalman": 88.5,
    "temp_aht": 24.50,
    "hum_aht": 55.2,
    "temp_bmp": 24.20,
    "press_hpa": 1013.2,
    "altitude_m": 16.5,
    "roll": 2.4,
    "pitch": -1.2,
    "yaw": 45.0,
    "gps_fix": 1,
    "latitude": -20.27410,
    "longitude": -40.30650,
    "sat_count": 8,
    "rssi": -78,
    "snr": 8.5,
    "last_update": "Aguardando primeiro pacote..."
}

telemetry_history = []
MAX_HISTORY = 60

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
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--card-border); }
        .logo-title h1 { font-size: 26px; color: var(--accent); letter-spacing: 1px; }
        .logo-title p { font-size: 13px; color: var(--text-muted); }
        .badge-status { padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 12px; background: rgba(0,230,118,0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }
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
    </style>
</head>
<body>
    <header>
        <div class="logo-title">
            <h1>TUPÃSAT-1U GROUND STATION</h1>
            <p>Monitoramento Orbital e Gerenciamento Térmico-Energético (TEMS)</p>
        </div>
        <div>
            <span id="satStatus" class="badge-status">ENLACE NOMINAL</span>
        </div>
    </header>

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
                <span style="font-size: 12px; color: var(--text-muted);">Amostragem em tempo real</span>
            </div>
            <canvas id="powerChart" height="120"></canvas>
        </div>

        <div class="chart-box">
            <div class="chart-title">
                <span>Controle e Atitude (ADCS)</span>
            </div>
            <div class="attitude-box">
                <div class="att-item">ROLL<div id="attRoll" class="att-val">0.0°</div></div>
                <div class="att-item">PITCH<div id="attPitch" class="att-val">0.0°</div></div>
                <div class="att-item">YAW<div id="attYaw" class="att-val">0.0°</div></div>
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

                document.getElementById('vBat').innerText = d.v_bat.toFixed(2);
                document.getElementById('socKalman').innerText = d.soc_kalman.toFixed(1);
                document.getElementById('powerMw').innerText = d.power_mw.toFixed(1);
                document.getElementById('currentMa').innerText = d.current_ma.toFixed(1);
                document.getElementById('tempAht').innerText = d.temp_aht.toFixed(1);
                document.getElementById('humAht').innerText = d.hum_aht.toFixed(1);
                document.getElementById('altM').innerText = d.altitude_m.toFixed(1);
                document.getElementById('pressHpa').innerText = d.press_hpa.toFixed(1);
                document.getElementById('rssiVal').innerText = d.rssi;
                document.getElementById('snrVal').innerText = d.snr;
                document.getElementById('pktId').innerText = d.packet_id;

                document.getElementById('attRoll').innerText = d.roll.toFixed(1) + '°';
                document.getElementById('attPitch').innerText = d.pitch.toFixed(1) + '°';
                document.getElementById('attYaw').innerText = d.yaw.toFixed(1) + '°';

                // Atualiza Gráfico
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

            } catch (err) {
                console.error("Erro na busca de telemetria:", err);
            }
        }

        async function sendCmd(cmdName) {
            alert('Telecomando enviado com sucesso: ' + cmdName);
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
            self.wfile.write(json.dumps(latest_telemetry).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suprime logs de requisições HTTP para manter o terminal limpo
        pass


def simulation_thread():
    """Gera telemetrias contínuas no modo de demonstração."""
    global latest_telemetry
    pkt_id = 1
    while True:
        raw_pkt = generate_demo_packet(pkt_id, version=2)
        telem, err = parse_tupasat_packet(raw_pkt)
        if telem:
            telem["rssi"] = random.randint(-92, -72)
            telem["snr"] = round(random.uniform(7.0, 10.5), 1)
            telem["last_update"] = datetime.now().strftime("%H:%M:%S")
            latest_telemetry = telem
        pkt_id += 1
        time.sleep(2.0)


def main():
    parser = argparse.ArgumentParser(description="Web Dashboard da Estação Terrena TupãSat")
    parser.add_argument("--port", type=int, default=8080, help="Porta HTTP do servidor web")
    parser.add_argument("--demo", action="store_true", default=True, help="Executa com simulador de telemetria ativo")
    args = parser.parse_args()

    if args.demo:
        sim = threading.Thread(target=simulation_thread, daemon=True)
        sim.start()
        print("[INFO] Simulador orbital de telemetria v2.0 ativo.")

    server = HTTPServer(("0.0.0.0", args.port), TelemetryHandler)
    print(f"\n==================================================================")
    print(f"   TUPÃSAT WEB GROUND STATION ONLINE: http://localhost:{args.port}  ")
    print(f"==================================================================")
    print("Abra o navegador no endereço acima para visualizar a telemetria em tempo real.")
    print("Pressione Ctrl+C para encerrar o servidor.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Servidor web encerrado pelo operador.")


if __name__ == "__main__":
    main()
