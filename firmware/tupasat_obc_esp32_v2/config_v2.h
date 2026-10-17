#ifndef TUPASAT_CONFIG_V2_H
#define TUPASAT_CONFIG_V2_H

#include <Arduino.h>

// =============================================================================
// IDENTIFICAÇÃO E VERSÃO
// =============================================================================
#define SAT_CALLSIGN            "TUPASAT"
#define SAT_ID                  2
#define FIRMWARE_VERSION        "2.0.0-PRO"

// =============================================================================
// MAPEAMENTO DE PINOS (ESP32 DevKit V1 - Barramento TupãStack)
// =============================================================================

// Barramento I2C Principal (INA219, AHT10, BMP180, MPU6050)
#define PIN_I2C_SDA             21
#define PIN_I2C_SCL             22
#define I2C_FREQ_HZ             400000  // Fast Mode 400 kHz

// Barramento SPI e Controle do Transceptor LoRa SX1276
#define PIN_LORA_SCK            18
#define PIN_LORA_MISO           19
#define PIN_LORA_MOSI           23
#define PIN_LORA_NSS            5
#define PIN_LORA_RST            14
#define PIN_LORA_DIO0           2       // Interrupção externa

// Interface Serial UART com o Receptor GNSS/GPS
#define PIN_GPS_RX              16      // ESP32 RX2 conectado ao TX do GPS
#define PIN_GPS_TX              17      // ESP32 TX2 conectado ao RX do GPS
#define GPS_BAUDRATE            9600

// LED Indicador de Saúde e Atividade
#define PIN_STATUS_LED          4

// =============================================================================
// PARÂMETROS DE RÁDIO FREQUÊNCIA (LoRa 915 MHz)
// =============================================================================
#define LORA_FREQUENCY          915E6   // 915.0 MHz (Faixa ISM UHF)
#define LORA_SPREAD_FACTOR      7       // SF7 (taxa alta) ou SF10 (longo alcance)
#define LORA_BANDWIDTH          125E3   // 125 kHz
#define LORA_CODING_RATE        5       // 4/5
#define LORA_SYNC_WORD          0x12    // Rede TupãSat
#define LORA_TX_POWER           17      // dBm (+17 dBm nominal)

// =============================================================================
// OPCODES DE TELECOMANDOS (Uplink TC)
// =============================================================================
#define TC_CMD_PING             0x01
#define TC_CMD_SET_RATE         0x02
#define TC_CMD_SAFE_MODE        0x03
#define TC_CMD_BURST            0x04
#define TC_CMD_REBOOT           0xFF
#define TC_REBOOT_SECURITY_KEY  0xA55A

// =============================================================================
// PARÂMETROS DO SUBSISTEMA DE ENERGIA (Bateria Li-Ion 3S 5000 mAh)
// =============================================================================
#define BATTERY_NOMINAL_CAP_MAH 5000.0f
#define BATTERY_V_MAX           12.60f
#define BATTERY_V_NOMINAL       11.10f
#define BATTERY_V_SAFE_MODE     9.80f
#define BATTERY_V_MIN_SHUTDOWN  9.00f

// Limites Térmicos do Sistema (TEMS - Thermal Energy Management System)
#define TEMP_WARN_THRESHOLD_C   50.0f
#define TEMP_CRIT_THRESHOLD_C   65.0f

#endif // TUPASAT_CONFIG_V2_H
