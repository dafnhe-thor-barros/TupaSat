#ifndef TUPASAT_CONFIG_H
#define TUPASAT_CONFIG_H

#include <Arduino.h>

// =============================================================================
// IDENTIFICAÇÃO DO SATÉLITE E MISSÃO
// =============================================================================
#define SAT_CALLSIGN        "TUPASAT"
#define SAT_ID              1
#define FIRMWARE_VERSION    "1.0.0"

// =============================================================================
// MAPEAMENTO DE PINOS (Arduino UNO + Sensor Shield V5)
// =============================================================================

// Módulo LoRa SX1276 (Interface SPI + Controle)
#define PIN_LORA_NSS        10      // Chip Select do transceptor SPI
#define PIN_LORA_RST        9       // Reset do rádio
#define PIN_LORA_DIO0       2       // Interrupção externa (INT0)

// Módulo GPS GNSS (SoftwareSerial)
#define PIN_GPS_RX          4       // Arduino RX conectado ao TX do GPS
#define PIN_GPS_TX          3       // Arduino TX conectado ao RX do GPS
#define GPS_BAUDRATE        9600

// Subsistema de Energia (EPS) - Sensor Analógico de Tensão
#define PIN_VBAT_ADC        A0      // Divisor resistivo (R1=100k, R2=22k)

// LED indicador de status da OBC
#define PIN_STATUS_LED      13      // LED embarcado do Arduino

// =============================================================================
// PARÂMETROS DE RÁDIO FREQUÊNCIA (LoRa 915 MHz)
// =============================================================================
#define LORA_FREQUENCY      915E6   // 915.0 MHz (Faixa ISM UHF)
#define LORA_SPREAD_FACTOR  7       // SF7 (7 a 12)
#define LORA_BANDWIDTH      125E3   // 125 kHz
#define LORA_CODING_RATE    5       // 4/5 (5 a 8)
#define LORA_SYNC_WORD      0x12    // Palavra de sincronismo da rede
#define LORA_TX_POWER       17      // Potência em dBm (+2 a +20)

// =============================================================================
// PARÂMETROS TEMPORAIS E LIMITES OPERACIONAIS
// =============================================================================
#define TELEMETRY_INTERVAL_NOMINAL_MS  5000   // Envio a cada 5 segundos em modo nominal
#define TELEMETRY_INTERVAL_SAFE_MS     60000  // Envio a cada 60 segundos em safe mode

#define BATTERY_SAFE_THRESHOLD_V       9.8f   // Tensão de entrada em Safe Mode (3S)
#define BATTERY_RECOVERY_THRESHOLD_V   11.1f  // Tensão para retorno ao modo Nominal

// Fator do divisor resistivo para leitura de bateria:
// V_in = ADC * (5.0 / 1023.0) * ((R1 + R2) / R2)
// Com R1=100k e R2=22k: ((100 + 22) / 22) = 5.5454
#define ADC_REF_VOLTAGE     5.0f
#define ADC_RESOLUTION      1023.0f
#define DIVIDER_RATIO       5.5454f

#endif // TUPASAT_CONFIG_H
