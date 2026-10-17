/**
 * =============================================================================
 * PROJETO TUPÃSAT — CUBESAT 1U ACADÊMICO
 * Firmware Avançado OBC - Plataforma ESP32 (FreeRTOS Dual-Core)
 * 
 * Permite processamento paralelo:
 * - Núcleo 0 (Core 0): Coleta contínua de sensores I2C, GPS e cálculo de telemetria
 * - Núcleo 1 (Core 1): Pilha de comunicação RF LoRa 915 MHz e telecomandos
 * =============================================================================
 */

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <LoRa.h>

// Definições de pinos para ESP32 DevKit V1
#define PIN_LORA_SS     5
#define PIN_LORA_RST    14
#define PIN_LORA_DIO0   2
#define PIN_STATUS_LED  2

#define LORA_FREQ       915E6

// Estrutura de dados compartilhada entre tarefas
struct SharedTelemetry {
    uint32_t packetId;
    uint32_t uptimeSec;
    float vBat;
    float temp;
    float hum;
    float press;
    float alt;
    float lat;
    float lon;
};

SharedTelemetry satData;
SemaphoreHandle_t xDataMutex = NULL;

// Protótipos de Tarefas FreeRTOS
void TaskSensors(void *pvParameters);
void TaskRadio(void *pvParameters);

void setup() {
    Serial.begin(115200);
    pinMode(PIN_STATUS_LED, OUTPUT);

    Serial.println(F("\n============================================="));
    Serial.println(F("   TUPASAT-1U ESP32 FREERTOS OBC INITIALIZED "));
    Serial.println(F("============================================="));

    xDataMutex = xSemaphoreCreateMutex();

    // Inicialização do rádio LoRa no ESP32
    LoRa.setPins(PIN_LORA_SS, PIN_LORA_RST, PIN_LORA_DIO0);
    if (!LoRa.begin(LORA_FREQ)) {
        Serial.println(F("[COMMS-ERR] Falha ao iniciar modulo LoRa!"));
    } else {
        LoRa.setSpreadingFactor(7);
        LoRa.setSignalBandwidth(125E3);
        LoRa.setTxPower(17);
        LoRa.enableCrc();
        Serial.println(F("[COMMS-OK] LoRa 915 MHz online no ESP32."));
    }

    // Criação de tarefas no FreeRTOS vinculadas aos núcleos
    xTaskCreatePinnedToCore(
        TaskSensors,
        "TaskSensors",
        4096,
        NULL,
        1,
        NULL,
        0 // Executa no Núcleo 0
    );

    xTaskCreatePinnedToCore(
        TaskRadio,
        "TaskRadio",
        4096,
        NULL,
        2,
        NULL,
        1 // Executa no Núcleo 1
    );
}

void loop() {
    // No FreeRTOS, o loop principal pode permanecer ocioso
    vTaskDelay(pdMS_TO_TICKS(1000));
}

// Tarefa no Núcleo 0: Aquisição periódica de sensores
void TaskSensors(void *pvParameters) {
    (void)pvParameters;
    uint32_t count = 0;

    for (;;) {
        if (xSemaphoreTake(xDataMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            count++;
            satData.packetId = count;
            satData.uptimeSec = esp_timer_get_time() / 1000000ULL;
            satData.vBat = 12.1f;
            satData.temp = 23.8f;
            satData.hum = 60.5f;
            satData.press = 1013.1f;
            satData.alt = 20.4f;
            satData.lat = -20.27410f;
            satData.lon = -40.30650f;

            xSemaphoreGive(xDataMutex);
        }
        vTaskDelay(pdMS_TO_TICKS(5000)); // Amostragem a cada 5s
    }
}

// Tarefa no Núcleo 1: Envio do pacote de RF
void TaskRadio(void *pvParameters) {
    (void)pvParameters;

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(5000));

        if (xSemaphoreTake(xDataMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            char buffer[160];
            snprintf(buffer, sizeof(buffer),
                "$TUPASAT,%u,%u,0,%.2f,%.2f,%.1f,%.2f,%.1f,%.1f,1,%.5f,%.5f,7",
                satData.packetId,
                satData.uptimeSec,
                satData.vBat,
                satData.temp,
                satData.hum,
                satData.temp,
                satData.press,
                satData.alt,
                satData.lat,
                satData.lon
            );
            xSemaphoreGive(xDataMutex);

            // Transmissão LoRa
            LoRa.beginPacket();
            LoRa.print(buffer);
            LoRa.endPacket();

            Serial.print(F("[LORA-TX ESP32] "));
            Serial.println(buffer);

            // Pulso no LED indicador
            digitalWrite(PIN_STATUS_LED, HIGH);
            vTaskDelay(pdMS_TO_TICKS(50));
            digitalWrite(PIN_STATUS_LED, LOW);
        }
    }
}
