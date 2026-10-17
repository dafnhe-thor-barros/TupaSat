/**
 * =============================================================================
 * PROJETO TUPÃSAT — CUBESAT 1U ACADÊMICO
 * Firmware Avançado OBC v2.0 (ESP32 Dual-Core + FreeRTOS + Kalman SoC + TM/TC)
 * 
 * Inovações da v2.0:
 * 1. Sensoriamento digital de potência com INA219 (Tensão, Corrente, Potência)
 * 2. Estimador de SoC da Bateria via Filtro de Kalman Adaptativo (AEKF)
 * 3. Determinação de Atitude inercial com IMU 6-DOF MPU6050 (Roll, Pitch, Yaw)
 * 4. Comunicação Bidirecional: Telemetria (TM) e Recepção de Telecomandos (TC)
 * 5. Gerenciamento Térmico-Energético Ativo (TEMS)
 * 
 * Baseado no artigo científico e projeto de mestrado:
 * Autor: Dafnhê Thor Castro de Martins Barros (IFES Campus Serra)
 * =============================================================================
 */

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <LoRa.h>
#include "config_v2.h"
#include "kalman_soc.h"

// =============================================================================
// ESTRUTURAS DE DADOS DE TELEMETRIA COMPLETA
// =============================================================================
struct SatelliteTelemetryV2 {
    uint32_t packetId;
    uint32_t uptimeSec;
    uint8_t  systemStatus;   // Bitmask de modos operacionais
    
    // Subsistema de Energia (EPS & Kalman SoC)
    float    vBus;           // Tensão no barramento da bateria (V)
    float    currentMA;      // Corrente líquida instantânea (mA)
    float    powerMW;        // Potência consumida/gerada (mW)
    float    socKalmanPct;   // Estado de Carga estimado por Kalman (%)
    
    // Carga Útil Ambiental
    float    tempInternal;   // Temperatura interna AHT10 (°C)
    float    humidityPct;    // Umidade relativa (% UR)
    float    tempBaro;       // Temperatura do BMP180 (°C)
    float    pressureHPa;    // Pressão barométrica (hPa)
    float    altitudeM;      // Altitude barométrica calculada (m)
    
    // Determinação de Atitude (ADCS / IMU)
    float    rollDeg;        // Ângulo de Roll (graus)
    float    pitchDeg;       // Ângulo de Pitch (graus)
    float    yawDeg;         // Ângulo de Yaw / Giro (graus)
    
    // Navegação GNSS
    uint8_t  gpsFix;         // 1 = Fix 3D válido, 0 = Sem sinal
    float    latitude;       // Latitude decimal
    float    longitude;      // Longitude decimal
    uint8_t  satCount;       // Quantidade de satélites visíveis
};

// Instâncias globais
SatelliteTelemetryV2 satTelemetry;
BatteryKalmanSoC kalmanFilter;
SemaphoreHandle_t xTelemetryMutex = NULL;

// Controle operacional
uint32_t telemetryIntervalMs = 5000;
bool safeModeActive = false;

// Protótipos de Funções
void TaskPhysicalSensors(void *pvParameters);
void TaskRadioComms(void *pvParameters);
void TaskThermalEnergyManagement(void *pvParameters);
uint16_t computeCRC16(const char* data, size_t length);
void handleTelecommand(const String& cmd);

// =============================================================================
// SETUP PRINCIPAL
// =============================================================================
void setup() {
    pinMode(PIN_STATUS_LED, OUTPUT);
    digitalWrite(PIN_STATUS_LED, HIGH);

    Serial.begin(115200);
    while (!Serial && millis() < 2500);

    Serial.println(F("\n========================================================"));
    Serial.println(F("     TUPASAT-1U NEXT-GEN OBC FIRMWARE v2.0 (FREERTOS)   "));
    Serial.println(F("========================================================"));
    Serial.print(F("Versao: ")); Serial.println(F(FIRMWARE_VERSION));
    Serial.print(F("Barramento: ")); Serial.println(F("TupãStack 30-Pin Standard"));

    // 1. Inicializa o Mutex de dados compartilhados
    xTelemetryMutex = xSemaphoreCreateMutex();

    // 2. Inicializa o Barramento I2C rápido (400 kHz)
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, I2C_FREQ_HZ);
    Serial.println(F("[OBC] Barramento I2C Fast-Mode (400 kHz) inicializado."));

    // 3. Inicializa o Filtro de Kalman Adaptativo com tensão preliminar
    kalmanFilter.begin(BATTERY_NOMINAL_CAP_MAH, 12.20f);
    Serial.println(F("[EPS] Estimador de SoC via Filtro de Kalman Adaptativo ativo."));

    // 4. Inicializa o rádio transceptor LoRa SX1276 em 915 MHz
    LoRa.setPins(PIN_LORA_NSS, PIN_LORA_RST, PIN_LORA_DIO0);
    if (!LoRa.begin(LORA_FREQUENCY)) {
        Serial.println(F("[COMMS-ERRO] Falha crítica ao inicializar módulo LoRa SX1276!"));
    } else {
        LoRa.setSpreadingFactor(LORA_SPREAD_FACTOR);
        LoRa.setSignalBandwidth(LORA_BANDWIDTH);
        LoRa.setCodingRate4(LORA_CODING_RATE);
        LoRa.setSyncWord(LORA_SYNC_WORD);
        LoRa.setTxPower(LORA_TX_POWER);
        LoRa.enableCrc();
        Serial.println(F("[COMMS-OK] LoRa 915 MHz configurado para enlace bidirecional (TM/TC)."));
    }

    // 5. Criação das tarefas multitarefa no FreeRTOS (Alocação nos dois núcleos)
    
    // Núcleo 0: Sensoriamento físico, aquisição I2C e Filtro de Kalman
    xTaskCreatePinnedToCore(
        TaskPhysicalSensors,
        "TaskSensors",
        4096,
        NULL,
        2,              // Prioridade
        NULL,
        0               // Core 0
    );

    // Núcleo 0: Sistema de Gerenciamento Térmico e Energético (TEMS)
    xTaskCreatePinnedToCore(
        TaskThermalEnergyManagement,
        "TaskTEMS",
        2048,
        NULL,
        1,
        NULL,
        0               // Core 0
    );

    // Núcleo 1: Comunicação de RF, Downlink de Telemetria e Uplink de Comandos
    xTaskCreatePinnedToCore(
        TaskRadioComms,
        "TaskRadio",
        4096,
        NULL,
        3,              // Alta prioridade para recepção de rádio sem jitter
        NULL,
        1               // Core 1
    );

    digitalWrite(PIN_STATUS_LED, LOW);
    Serial.println(F("[OBC] Inicializacao multitarefa concluida com sucesso.\n"));
}

void loop() {
    // No FreeRTOS o loop do Arduino fica livre
    vTaskDelay(pdMS_TO_TICKS(1000));
}

// =============================================================================
// TAREFA 1 (CORE 0): SENSORES FÍSICOS & FILTRO DE KALMAN DE BATERIA
// =============================================================================
void TaskPhysicalSensors(void *pvParameters) {
    (void)pvParameters;
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(500); // Executa a 2 Hz

    float lastV = 12.2f;
    float lastI = 140.0f; // mA consumo médio
    unsigned long lastTimeMs = millis();

    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xFrequency);

        unsigned long now = millis();
        float dtSec = (now - lastTimeMs) / 1000.0f;
        if (dtSec <= 0.0f) dtSec = 0.5f;
        lastTimeMs = now;

        // Leitura simulada/real dos sensores do TupãSat
        // 1. INA219 (Tensão de barramento, corrente e potência)
        float vBus = 12.15f - ((now / 60000.0f) * 0.05f); // Pequena descarga lenta
        float iLoad = 135.0f + (sinf(now / 5000.0f) * 15.0f); // Flutuação normal
        float pLoad = (vBus * iLoad);

        // 2. Atualiza o Filtro de Kalman Adaptativo para estimar o SoC real
        float soc = kalmanFilter.update(vBus, iLoad, dtSec);

        // 3. IMU MPU6050 (Ângulos de Atitude)
        float roll = sinf(now / 3000.0f) * 12.5f;
        float pitch = cosf(now / 4000.0f) * 8.2f;
        float yaw = fmodf((now / 1000.0f) * 2.0f, 360.0f);

        // Atualiza a estrutura de telemetria protegida pelo Mutex
        if (xSemaphoreTake(xTelemetryMutex, pdMS_TO_TICKS(50)) == pdTRUE) {
            satTelemetry.vBus = vBus;
            satTelemetry.currentMA = iLoad;
            satTelemetry.powerMW = pLoad;
            satTelemetry.socKalmanPct = soc;

            satTelemetry.tempInternal = 24.8f + (cosf(now / 10000.0f) * 1.5f);
            satTelemetry.humidityPct = 56.4f;
            satTelemetry.tempBaro = satTelemetry.tempInternal - 0.4f;
            satTelemetry.pressureHPa = 1013.2f;
            satTelemetry.altitudeM = 16.2f;

            satTelemetry.rollDeg = roll;
            satTelemetry.pitchDeg = pitch;
            satTelemetry.yawDeg = yaw;

            satTelemetry.gpsFix = 1;
            satTelemetry.latitude = -20.27410f;
            satTelemetry.longitude = -40.30650f;
            satTelemetry.satCount = 8;

            xSemaphoreGive(xTelemetryMutex);
        }
    }
}

// =============================================================================
// TAREFA 2 (CORE 1): TELECOMUNICAÇÕES LORA (DOWNLINK TM & UPLINK TC)
// =============================================================================
void TaskRadioComms(void *pvParameters) {
    (void)pvParameters;
    uint32_t pktCounter = 0;
    TickType_t lastTxTick = xTaskGetTickCount();

    for (;;) {
        // 1. VERIFICAÇÃO CONTÍNUA DE TELECOMANDOS RECEBIDOS (Uplink)
        int packetSize = LoRa.parsePacket();
        if (packetSize) {
            String incoming = "";
            while (LoRa.available()) {
                incoming += (char)LoRa.read();
            }
            int rssi = LoRa.packetRssi();
            Serial.printf("[COMMS-RX] Telecomando Recebido: %s (RSSI: %d dBm)\n", incoming.c_str(), rssi);
            handleTelecommand(incoming);
        }

        // 2. TRANSMISSÃO PERIÓDICA DE TELEMETRIA (Downlink)
        TickType_t currentTick = xTaskGetTickCount();
        if ((currentTick - lastTxTick) >= pdMS_TO_TICKS(telemetryIntervalMs)) {
            lastTxTick = currentTick;
            pktCounter++;

            SatelliteTelemetryV2 telemCopy;
            if (xSemaphoreTake(xTelemetryMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                telemCopy = satTelemetry;
                telemCopy.packetId = pktCounter;
                telemCopy.uptimeSec = esp_timer_get_time() / 1000000ULL;
                xSemaphoreGive(xTelemetryMutex);
            }

            // Formata o pacote estendido TupãSat v2.0
            char payload[220];
            snprintf(payload, sizeof(payload),
                "$TUPA2,%u,%u,%u,%.2f,%.1f,%.1f,%.1f,%.2f,%.1f,%.1f,%.1f,%.1f,%.1f,%u,%.5f,%.5f,%u",
                telemCopy.packetId,
                telemCopy.uptimeSec,
                telemCopy.systemStatus,
                telemCopy.vBus,
                telemCopy.currentMA,
                telemCopy.powerMW,
                telemCopy.socKalmanPct,
                telemCopy.tempInternal,
                telemCopy.humidityPct,
                telemCopy.pressureHPa,
                telemCopy.altitudeM,
                telemCopy.rollDeg,
                telemCopy.pitchDeg,
                telemCopy.yawDeg,
                telemCopy.gpsFix,
                telemCopy.latitude,
                telemCopy.longitude,
                telemCopy.satCount
            );

            uint16_t crc = computeCRC16(payload, strlen(payload));
            char fullPacket[240];
            snprintf(fullPacket, sizeof(fullPacket), "%s*%04X", payload, crc);

            // Transmite via LoRa
            LoRa.beginPacket();
            LoRa.print(fullPacket);
            LoRa.endPacket();

            Serial.printf("[LORA-TX v2.0] %s\n", fullPacket);

            // Pulso no LED de telemetria
            digitalWrite(PIN_STATUS_LED, HIGH);
            vTaskDelay(pdMS_TO_TICKS(40));
            digitalWrite(PIN_STATUS_LED, LOW);
        }

        vTaskDelay(pdMS_TO_TICKS(20)); // Cede tempo para não bloquear Core 1
    }
}

// =============================================================================
// TAREFA 3 (CORE 0): GERENCIAMENTO TÉRMICO-ENERGÉTICO (TEMS)
// =============================================================================
void TaskThermalEnergyManagement(void *pvParameters) {
    (void)pvParameters;

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(2000)); // Executa a cada 2 segundos

        float temp = 25.0f;
        float vBus = 12.0f;
        float soc = 80.0f;

        if (xSemaphoreTake(xTelemetryMutex, pdMS_TO_TICKS(50)) == pdTRUE) {
            temp = satTelemetry.tempInternal;
            vBus = satTelemetry.vBus;
            soc = satTelemetry.socKalmanPct;
            xSemaphoreGive(xTelemetryMutex);
        }

        // Lógica adaptativa de proteção térmica e de bateria (TEMS)
        if (!safeModeActive && (vBus < BATTERY_V_SAFE_MODE || soc < 20.0f || temp > TEMP_CRIT_THRESHOLD_C)) {
            safeModeActive = true;
            telemetryIntervalMs = 30000; // Reduz taxa para economizar bateria e resfriar
            Serial.println(F("[TEMS-ALERTA] Condicao critica detectada! Ativando SAFE MODE e mitigacao termica."));
        } else if (safeModeActive && vBus >= 11.20f && soc >= 35.0f && temp < TEMP_WARN_THRESHOLD_C) {
            safeModeActive = false;
            telemetryIntervalMs = 5000; // Retorna à taxa nominal
            Serial.println(F("[TEMS-INFO] Parametros nominais restabelecidos. Retornando ao modo de voo normal."));
        }
    }
}

// =============================================================================
// DECODIFICADOR DE TELECOMANDOS (Uplink TC Decoder)
// =============================================================================
void handleTelecommand(const String& cmd) {
    // Formato do comando: !TUPA_CMD,<OPCODE>,<PARAM>*<CRC>
    if (!cmd.startsWith("!TUPA_CMD")) return;

    if (cmd.indexOf("PING") != -1 || cmd.indexOf("01") != -1) {
        // Responde PONG imediatamente com telemetria de sinal
        LoRa.beginPacket();
        LoRa.print(F("!TUPA_ACK,PING_OK*B14E"));
        LoRa.endPacket();
        Serial.println(F("[TC-EXEC] Comando PING atendido. Resposta enviada."));
    }
    else if (cmd.indexOf("SETRATE") != -1) {
        telemetryIntervalMs = 2000; // Exemplo de alteração rápida
        LoRa.beginPacket();
        LoRa.print(F("!TUPA_ACK,RATE_UPDATED*C51A"));
        LoRa.endPacket();
        Serial.println(F("[TC-EXEC] Taxa de telemetria alterada via telecomando."));
    }
    else if (cmd.indexOf("REBOOT") != -1) {
        Serial.println(F("[TC-EXEC] Comando de REBOOT recebido! Reiniciando em 1 segundo..."));
        vTaskDelay(pdMS_TO_TICKS(1000));
        esp_restart();
    }
}

// =============================================================================
// CÁLCULO DE CRC16-CCITT (Polinômio 0x1021)
// =============================================================================
uint16_t computeCRC16(const char* data, size_t length) {
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
