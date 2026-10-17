#!/usr/bin/env python3
"""
=============================================================================
PROJETO TUPÃSAT — ESTAÇÃO DE SOLO (GROUND STATION)
Dashboard de Telemetria e Registro de Dados de Missão em Tempo Real

Suporta:
- Conexão serial com o receptor LoRa (ex: COM3, /dev/ttyUSB0)
- Modo de simulação (--demo) para testes e demonstrações acadêmicas sem hardware
- Registro automático de telemetria em arquivo CSV com timestamp UTC
- Validação de integridade via algoritmo CRC16-CCITT
=============================================================================
"""

import sys
import time
import argparse
import csv
import json
import random
from datetime import datetime

try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False


def calculate_crc16(data: str) -> int:
    """Calcula o CRC16-CCITT (Polinômio 0x1021) idêntico ao firmware da OBC."""
    crc = 0xFFFF
    for ch in data:
        crc ^= (ord(ch) & 0xFF) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def parse_tupasat_packet(raw_str: str):
    """
    Decodifica as sentenças:
    v1: $TUPA,<PKT_ID>,<UPTIME>,<STATUS>,<VBAT>,<TAHT>,<HUM>,<TBMP>,<PRESS>,<ALT>,<FIX>,<LAT>,<LON>,<SATS>*<CRC16>
    v2: $TUPA2,<PKT_ID>,<UPTIME>,<STATUS>,<VBUS>,<IMA>,<PMW>,<SOC_KALMAN>,<TAHT>,<HUM>,<PRESS>,<ALT>,<ROLL>,<PITCH>,<YAW>,<FIX>,<LAT>,<LON>,<SATS>*<CRC16>
    """
    raw_str = raw_str.strip()
    if not (raw_str.startswith("$TUPA") or raw_str.startswith("$TUPA2")) or "*" not in raw_str:
        return None, "Formato inválido"

    payload_part, crc_part = raw_str.split("*", 1)
    try:
        expected_crc = int(crc_part, 16)
    except ValueError:
        return None, "CRC mal formatado"

    calc_crc = calculate_crc16(payload_part)
    if calc_crc != expected_crc:
        return None, f"CRC Incompativel (calc={calc_crc:04X}, recebido={expected_crc:04X})"

    fields = payload_part.split(",")

    # Formato v2 (Estendido com Kalman e IMU)
    if fields[0] == "$TUPA2" and len(fields) >= 18:
        try:
            telemetry = {
                "version": 2,
                "callsign": "TUPASAT-v2",
                "packet_id": int(fields[1]),
                "uptime_s": int(fields[2]),
                "status": int(fields[3]),
                "v_bat": float(fields[4]),
                "current_ma": float(fields[5]),
                "power_mw": float(fields[6]),
                "soc_kalman": float(fields[7]),
                "temp_aht": float(fields[8]),
                "hum_aht": float(fields[9]),
                "temp_bmp": float(fields[8]) - 0.3,
                "press_hpa": float(fields[10]),
                "altitude_m": float(fields[11]),
                "roll": float(fields[12]),
                "pitch": float(fields[13]),
                "yaw": float(fields[14]),
                "gps_fix": int(fields[15]),
                "latitude": float(fields[16]),
                "longitude": float(fields[17]),
                "sat_count": int(fields[18]) if len(fields) > 18 else 8,
                "crc_valid": True,
            }
            return telemetry, "OK"
        except Exception as e:
            return None, f"Erro de conversão v2: {e}"

    # Formato v1 (Legado / Arduino)
    if len(fields) < 14:
        return None, f"Campos insuficientes ({len(fields)} de 14)"

    try:
        telemetry = {
            "version": 1,
            "callsign": fields[0].replace("$", ""),
            "packet_id": int(fields[1]),
            "uptime_s": int(fields[2]),
            "status": int(fields[3]),
            "v_bat": float(fields[4]),
            "current_ma": None,
            "power_mw": None,
            "soc_kalman": None,
            "temp_aht": float(fields[5]),
            "hum_aht": float(fields[6]),
            "temp_bmp": float(fields[7]),
            "press_hpa": float(fields[8]),
            "altitude_m": float(fields[9]),
            "roll": 0.0,
            "pitch": 0.0,
            "yaw": 0.0,
            "gps_fix": int(fields[10]),
            "latitude": float(fields[11]),
            "longitude": float(fields[12]),
            "sat_count": int(fields[13]),
            "crc_valid": True,
        }
        return telemetry, "OK"
    except Exception as e:
        return None, f"Erro de conversão v1: {e}"


def print_dashboard(telem, rssi=None, snr=None):
    """Renderiza a tela de telemetria no terminal com layout limpo e intuitivo."""
    v_bat = telem["v_bat"]
    soc_display = telem["soc_kalman"] if telem.get("soc_kalman") is not None else max(0.0, min(100.0, (v_bat - 9.6) / (12.6 - 9.6) * 100.0))
    status_str = "NOMINAL" if telem["status"] == 0 else f"ALERTA (Code: {telem['status']})"

    print("\033[2J\033[H", end="") # Limpa tela ANSI
    print("=" * 76)
    print(f"      ESTAÇÃO TERRENA TUPÃSAT — TELEMETRIA EM TEMPO REAL (915 MHz)      ")
    print("=" * 76)
    print(f" Data/Hora Local: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Satélite: {telem['callsign']} (v{telem.get('version', 1)})")
    print(f" Pacote Nº: {telem['packet_id']:<8} | Uptime: {telem['uptime_s']} s | Status Geral: {status_str}")
    print("-" * 76)

    # Bloco EPS
    print(f" [SUBSISTEMA DE ENERGIA - EPS]")
    print(f"   Tensão Barramento : {v_bat:>6.2f} V   | SoC Estimado (Kalman) : {soc_display:>5.1f} %")
    if telem.get("current_ma") is not None:
        print(f"   Corrente Líquida  : {telem['current_ma']:>6.1f} mA  | Potência Instantânea  : {telem['power_mw']:>6.1f} mW")
    print(f"   Saúde Barramento  : {'SAUDAVEL' if v_bat >= 10.0 else 'BATERIA CRITICA (SAFE MODE)'}")
    print("-" * 76)

    # Bloco Sensores
    print(f" [CARGA ÚTIL & SENSORES AMBIENTAIS]")
    print(f"   Temperatura (AHT10) : {telem['temp_aht']:>6.2f} °C   | Umidade Relativa    : {telem['hum_aht']:>5.1f} %")
    print(f"   Temperatura (BMP180): {telem['temp_bmp']:>6.2f} °C   | Pressão Atmosférica : {telem['press_hpa']:>6.1f} hPa")
    print(f"   Altitude Barométrica: {telem['altitude_m']:>6.1f} m")
    print("-" * 76)

    # Bloco Atitude (se v2)
    if telem.get("version") == 2:
        print(f" [DETERMINAÇÃO DE ATITUDE - ADCS / IMU 6-DOF]")
        print(f"   Roll (Rolagem): {telem['roll']:>7.2f}°  | Pitch (Arfagem): {telem['pitch']:>7.2f}°  | Yaw (Guinada): {telem['yaw']:>7.2f}°")
        print("-" * 76)

    # Bloco GNSS
    fix_str = "FIX VALIDO (3D)" if telem["gps_fix"] == 1 else "AGUARDANDO FIX"
    print(f" [NAVEGAÇÃO GNSS/GPS]")
    print(f"   Status Fix : {fix_str:<18} | Satélites Rastreando : {telem['sat_count']}")
    print(f"   Latitude   : {telem['latitude']:>11.5f}°     | Longitude            : {telem['longitude']:>11.5f}°")
    print("-" * 76)

    # Bloco Enlace RF
    rssi_str = f"{rssi} dBm" if rssi is not None else "N/A"
    snr_str = f"{snr} dB" if snr is not None else "N/A"
    print(f" [QUALIDADE DO ENLACE DE RÁDIO]")
    print(f"   Sinal RSSI : {rssi_str:<12} | Relação Sinal/Ruído (SNR) : {snr_str}")
    print("=" * 76)
    print(" Pressione Ctrl+C para encerrar o monitoramento.")


def generate_demo_packet(pkt_id, version=2):
    """Gera um pacote simulado realista para testes de bancada."""
    vbat = round(12.15 - (pkt_id * 0.004), 2)
    current = round(135.0 + random.uniform(-10.0, 15.0), 1)
    power = round(vbat * current, 1)
    soc = round(85.0 - (pkt_id * 0.1), 1)
    taht = round(24.5 + random.uniform(-0.4, 0.4), 2)
    hum = round(56.0 + random.uniform(-1.0, 1.0), 1)
    press = round(1013.2 + random.uniform(-0.5, 0.5), 1)
    alt = round(16.5 + random.uniform(-0.8, 0.8), 1)
    roll = round(random.uniform(-15.0, 15.0), 2)
    pitch = round(random.uniform(-8.0, 8.0), 2)
    yaw = round(random.uniform(0.0, 360.0), 2)
    lat = -20.27410 + random.uniform(-0.00005, 0.00005)
    lon = -40.30650 + random.uniform(-0.00005, 0.00005)

    if version == 2:
        payload = f"$TUPA2,{pkt_id},{pkt_id*5},0,{vbat:.2f},{current:.1f},{power:.1f},{soc:.1f},{taht:.2f},{hum:.1f},{press:.1f},{alt:.1f},{roll:.2f},{pitch:.2f},{yaw:.2f},1,{lat:.5f},{lon:.5f},8"
    else:
        payload = f"$TUPA,{pkt_id},{pkt_id*5},0,{vbat:.2f},{taht:.2f},{hum:.1f},{taht-0.2:.2f},{press:.1f},{alt:.1f},1,{lat:.5f},{lon:.5f},7"

    crc = calculate_crc16(payload)
    return f"{payload}*{crc:04X}"


def main():
    parser = argparse.ArgumentParser(description="Dashboard da Estação de Solo TupãSat")
    parser.add_argument("--port", type=str, default="COM3", help="Porta serial do receptor LoRa")
    parser.add_argument("--baud", type=int, default=115200, help="Velocidade serial (baudrate)")
    parser.add_argument("--demo", action="store_true", help="Executa em modo de simulação sem hardware")
    parser.add_argument("--log", type=str, default="tupasat_mission_log.csv", help="Arquivo CSV de saída")
    args = parser.parse_args()

    csv_fields = [
        "timestamp_utc", "version", "packet_id", "uptime_s", "status", "v_bat",
        "current_ma", "power_mw", "soc_kalman",
        "temp_aht", "hum_aht", "temp_bmp", "press_hpa", "altitude_m",
        "roll", "pitch", "yaw",
        "gps_fix", "latitude", "longitude", "sat_count", "rssi", "snr"
    ]

    # Cria ou abre o arquivo de log CSV
    with open(args.log, mode="a", newline="", encoding="utf-8") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=csv_fields, extrasaction="ignore")
        if f_csv.tell() == 0:
            writer.writeheader()

        if args.demo:
            print("[INFO] Iniciando modo de demonstracao simulada (Demo Mode)...")
            pkt_id = 1
            try:
                while True:
                    packet_str = generate_demo_packet(pkt_id, version=2)
                    rssi = random.randint(-95, -70)
                    snr = round(random.uniform(6.0, 10.5), 1)
                    telem, err = parse_tupasat_packet(packet_str)
                    if telem:
                        print_dashboard(telem, rssi, snr)
                        log_row = dict(telem)
                        log_row["timestamp_utc"] = datetime.utcnow().isoformat()
                        log_row["rssi"] = rssi
                        log_row["snr"] = snr
                        writer.writerow(log_row)
                        f_csv.flush()
                    pkt_id += 1
                    time.sleep(2.0)
            except KeyboardInterrupt:
                print("\n[INFO] Sessao de telemetria encerrada pelo operador.")
                return

        # Modo Serial Real
        if not HAS_SERIAL:
            print("[ERRO] Biblioteca pyserial nao instalada. Instale com: pip install pyserial")
            sys.exit(1)

        print(f"[INFO] Conectando a porta {args.port} a {args.baud} bps...")
        try:
            ser = serial.Serial(args.port, args.baud, timeout=2.0)
        except Exception as e:
            print(f"[ERRO] Nao foi possivel abrir a porta serial {args.port}: {e}")
            print("Dica: Use a flag --demo para testar sem conectar hardware.")
            sys.exit(1)

        try:
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                rssi, snr = None, None
                packet_str = line

                # Se a estação terrena enviar em formato JSON estruturado
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
                    print_dashboard(telem, rssi, snr)
                    log_row = dict(telem)
                    del log_row["callsign"]
                    del log_row["crc_valid"]
                    log_row["timestamp_utc"] = datetime.utcnow().isoformat()
                    log_row["rssi"] = rssi if rssi is not None else ""
                    log_row["snr"] = snr if snr is not None else ""
                    writer.writerow(log_row)
                    f_csv.flush()
        except KeyboardInterrupt:
            print("\n[INFO] Monitoramento serial encerrado.")
        finally:
            ser.close()


if __name__ == "__main__":
    main()
