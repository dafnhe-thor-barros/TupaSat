/**
 * =============================================================================
 * PROJETO TUPÃSAT — CUBESAT 1U ACADÊMICO
 * Firmware do Computador de Bordo (OBC) - Plataforma Arduino UNO
 * 
 * Baseado no artigo:
 * "Desenvolvimento de um kit de CubeSat para fins acadêmicos: projeto,
 * construção e aplicações" (Barros, 2025 - Caderno Pedagógico)
 * Autor: Dafnhê Thor Castro de Martins Barros
 * =============================================================================
 */

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SoftwareSerial.h>
#include <LoRa.h>
#include "config.h"

// =============================================================================
// ESTRUTURAS DE DADOS E VARIÁVEIS GLOBAIS
// =============================================================================

// Porta serial emulada para o receptor GPS NEO-6M
SoftwareSerial gpsSerial(PIN_GPS_RX, PIN_GPS_TX);

// Estrutura de dados de telemetria da missão
struct TelemetryData {
    uint32_t packetId;
    uint32_t uptimeSec;
    uint8_t  systemStatus;   // 0=Nominal, 1=SafeMode, 2=SensorWarning, 4=GPSNoFix
    float    vBat;           // Tensão da bateria (V)
    float    tempAHT;        // Temperatura AHT10 (°C)
    float    humAHT;         // Umidade AHT10 (% UR)
    float    tempBMP;        // Temperatura BMP180 (°C)
    float    pressHPa;       // Pressão barométrica (hPa)
    float    altitudeM;      // Altitude estimada (m)
    uint8_t  gpsFix;         // 1=Fixado, 0=Sem sinal
    float    latitude;       // Latitude decimal
    float    longitude;      // Longitude decimal
    uint8_t  satCount;       // Quantidade de satélites visíveis
};

TelemetryData telemetry;

// Controle de temporização não-bloqueante
unsigned long lastTelemetryTime = 0;
unsigned long telemetryInterval = TELEMETRY_INTERVAL_NOMINAL_MS;
bool inSafeMode = false;

// =============================================================================
// PROTÓTIPOS DE FUNÇÕES
// =============================================================================
void initLoRa();
void readEPS();
void readEnvironmentalSensors();
void processGPS();
void checkPowerState();
uint16_t calculateCRC16(const char* data, size_t length);
void transmitTelemetry();

// =============================================================================
// SETUP: INICIALIZAÇÃO DO SISTEMA
// =============================================================================
void setup() {
    pinMode(PIN_STATUS_LED, OUTPUT);
    digitalWrite(PIN_STATUS_LED, HIGH);

    // Inicialização da porta serial para depuração e testes de bancada
    Serial.begin(115200);
    while (!Serial && millis() < 3000); // Aguarda conexão da porta serial em bancada

    Serial.println(F("\n=========================================="));
    Serial.println(F("     TUPASAT-1U EMBEDDED OBC FIRMWARE     "));
    Serial.println(F("=========================================="));
    Serial.print(F("Versao do Firmware: ")); Serial.println(F(FIRMWARE_VERSION));
    Serial.print(F("Satélite ID: ")); Serial.println(F(SAT_CALLSIGN));

    // 1. Inicializa o barramento I2C para sensores
    Wire.begin();
    Serial.println(F("[OBC] Barramento I2C inicializado."));

    // 2. Inicializa a comunicação UART com o GPS
    gpsSerial.begin(GPS_BAUDRATE);
    Serial.println(F("[OBC] Interface GPS inicializada a 9600 bps."));

    // 3. Inicializa o rádio transceptor LoRa SX1276
    initLoRa();

    // 4. Inicializa o contador de pacotes e estado
    telemetry.packetId = 0;
    telemetry.systemStatus = 0;

    digitalWrite(PIN_STATUS_LED, LOW);
    Serial.println(F("[OBC] Boot concluido com sucesso. Iniciando operacao nominal.\n"));
}

// =============================================================================
// LOOP: CICLO OPERACIONAL PERIÓDICO
// =============================================================================
void loop() {
    // 1. Processa bytes de dados NMEA do GPS continuamente em segundo plano
    processGPS();

    // 2. Verifica se atingiu o período de envio de telemetria
    unsigned long currentMillis = millis();
    if (currentMillis - lastTelemetryTime >= telemetryInterval) {
        lastTelemetryTime = currentMillis;

        // Sinaliza atividade no LED
        digitalWrite(PIN_STATUS_LED, HIGH);

        // Atualiza contadores de tempo e pacote
        telemetry.packetId++;
        telemetry.uptimeSec = currentMillis / 1000UL;

        // Executa ciclo de leitura de telemetria
        readEPS();
        readEnvironmentalSensors();
        checkPowerState();

        // Transmite o pacote via rádio e porta serial
        transmitTelemetry();

        digitalWrite(PIN_STATUS_LED, LOW);
    }
}

// =============================================================================
// IMPLEMENTAÇÃO DOS SUBSISTEMAS
// =============================================================================

/**
 * Inicializa e configura o transceptor LoRa SX1276 via barramento SPI
 */
void initLoRa() {
    LoRa.setPins(PIN_LORA_NSS, PIN_LORA_RST, PIN_LORA_DIO0);

    Serial.print(F("[COMMS] Inicializando LoRa em 915 MHz... "));
    if (!LoRa.begin(LORA_FREQUENCY)) {
        Serial.println(F("FALHA!"));
        telemetry.systemStatus |= 0x02; // Alerta de erro de hardware
        return;
    }

    LoRa.setSpreadingFactor(LORA_SPREAD_FACTOR);
    LoRa.setSignalBandwidth(LORA_BANDWIDTH);
    LoRa.setCodingRate4(LORA_CODING_RATE);
    LoRa.setSyncWord(LORA_SYNC_WORD);
    LoRa.setTxPower(LORA_TX_POWER);
    LoRa.enableCrc();

    Serial.println(F("OK. Rádio pronto."));
}

/**
 * Lê o subsistema de energia elétrica (EPS)
 */
void readEPS() {
    int rawADC = analogRead(PIN_VBAT_ADC);
    float pinVoltage = (rawADC * ADC_REF_VOLTAGE) / ADC_RESOLUTION;
    telemetry.vBat = pinVoltage * DIVIDER_RATIO;
}

/**
 * Lê os sensores ambientais AHT10 e BMP180 via I2C
 * (Inclui leituras simuladas / tratamento robusto para sensores desconectados)
 */
void readEnvironmentalSensors() {
    // Teste de presença no I2C para AHT10 (0x38)
    Wire.beginTransmission(0x38);
    byte ahtError = Wire.endTransmission();

    if (ahtError == 0) {
        // Leitura básica simplificada (ou via biblioteca Adafruit/AHTxx instalada)
        telemetry.tempAHT = 24.50f;
        telemetry.humAHT = 55.0f;
    } else {
        // Valor padrão se o sensor não estiver fisicamente conectado na bancada
        telemetry.tempAHT = 25.0f;
        telemetry.humAHT = 50.0f;
    }

    // Teste de presença para BMP180 (0x77)
    Wire.beginTransmission(0x77);
    byte bmpError = Wire.endTransmission();

    if (bmpError == 0) {
        telemetry.tempBMP = 24.30f;
        telemetry.pressHPa = 1013.25f;
        telemetry.altitudeM = 15.0f;
    } else {
        telemetry.tempBMP = 24.8f;
        telemetry.pressHPa = 1012.8f;
        telemetry.altitudeM = 18.0f;
    }
}

/**
 * Lê e processa sentenças NMEA do módulo GPS
 */
void processGPS() {
    while (gpsSerial.available() > 0) {
        char c = (char)gpsSerial.read();
        // Em integração com biblioteca TinyGPSPlus, alimentar: gps.encode(c);
        (void)c;
    }

    // Dados padrão de bancada quando sem fixação em ambiente coberto
    telemetry.gpsFix = 0;
    telemetry.latitude = -20.27410f;  // Referência IFES Serra - ES
    telemetry.longitude = -40.30650f;
    telemetry.satCount = 0;
}

/**
 * Gerenciamento do estado operacional e economia de bateria (FSM / CONOPS)
 */
void checkPowerState() {
    if (!inSafeMode && telemetry.vBat < BATTERY_SAFE_THRESHOLD_V && telemetry.vBat > 3.0f) {
        inSafeMode = true;
        telemetryInterval = TELEMETRY_INTERVAL_SAFE_MS;
        telemetry.systemStatus |= 0x01; // Flag de Safe Mode
        Serial.println(F("[EPS-ALERTA] Bateria Baixa! Entrando em SAFE MODE (60s)."));
    } else if (inSafeMode && telemetry.vBat >= BATTERY_RECOVERY_THRESHOLD_V) {
        inSafeMode = false;
        telemetryInterval = TELEMETRY_INTERVAL_NOMINAL_MS;
        telemetry.systemStatus &= ~0x01; // Limpa flag de Safe Mode
        Serial.println(F("[EPS-INFO] Bateria recuperada. Retornando ao modo NOMINAL (5s)."));
    }
}

/**
 * Cálculo do algoritmo de verificação CRC16-CCITT (Polinômio 0x1021)
 */
uint16_t calculateCRC16(const char* data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint8_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

/**
 * Constrói o pacote formatado em padrão ASCII e transmite via LoRa e Serial
 */
void transmitTelemetry() {
    char payload[160];
    char vBatStr[8], tAhtStr[8], humStr[8], tBmpStr[8], pressStr[10], altStr[8];
    char latStr[12], lonStr[12];

    // Converte floats para string (padrão AVR)
    dtostrf(telemetry.vBat, 4, 2, vBatStr);
    dtostrf(telemetry.tempAHT, 4, 2, tAhtStr);
    dtostrf(telemetry.humAHT, 4, 1, humStr);
    dtostrf(telemetry.tempBMP, 4, 2, tBmpStr);
    dtostrf(telemetry.pressHPa, 6, 1, pressStr);
    dtostrf(telemetry.altitudeM, 5, 1, altStr);
    dtostrf(telemetry.latitude, 8, 5, latStr);
    dtostrf(telemetry.longitude, 8, 5, lonStr);

    // Formata o corpo do pacote de dados
    snprintf(payload, sizeof(payload),
        "$%s,%lu,%lu,%u,%s,%s,%s,%s,%s,%s,%u,%s,%s,%u",
        SAT_CALLSIGN,
        (unsigned long)telemetry.packetId,
        (unsigned long)telemetry.uptimeSec,
        telemetry.systemStatus,
        vBatStr,
        tAhtStr,
        humStr,
        tBmpStr,
        pressStr,
        altStr,
        telemetry.gpsFix,
        latStr,
        lonStr,
        telemetry.satCount
    );

    // Calcula o checksum CRC16
    uint16_t crc = calculateCRC16(payload, strlen(payload));

    // Monta o pacote final completo com o CRC
    char fullPacket[180];
    snprintf(fullPacket, sizeof(fullPacket), "%s*%04X", payload, crc);

    // 1. Exibe na serial de bancada
    Serial.print(F("[TX] "));
    Serial.println(fullPacket);

    // 2. Transmite via rádio LoRa
    LoRa.beginPacket();
    LoRa.print(fullPacket);
    LoRa.endPacket();
}
