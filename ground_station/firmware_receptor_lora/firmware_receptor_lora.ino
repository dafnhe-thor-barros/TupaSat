/**
 * =============================================================================
 * PROJETO TUPÃSAT — ESTAÇÃO DE SOLO (GROUND STATION)
 * Firmware Receptor de Telemetria LoRa 915 MHz
 * 
 * Recebe os pacotes do satélite, extrai métricas de sinal de RF (RSSI e SNR)
 * e formata em JSON pela porta USB para consumo do Dashboard de Telemetria.
 * =============================================================================
 */

#include <SPI.h>
#include <LoRa.h>

// Mapeamento de pinos do receptor (compatível com Arduino UNO ou ESP32)
#if defined(ESP32)
  #define PIN_NSS   5
  #define PIN_RST   14
  #define PIN_DIO0  2
#else
  #define PIN_NSS   10
  #define PIN_RST   9
  #define PIN_DIO0  2
#endif

#define LORA_FREQ 915E6

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000);

    Serial.println(F("\n=============================================="));
    Serial.println(F("     TUPASAT GROUND STATION RECEIVER 915MHz   "));
    Serial.println(F("=============================================="));

    LoRa.setPins(PIN_NSS, PIN_RST, PIN_DIO0);

    if (!LoRa.begin(LORA_FREQ)) {
        Serial.println(F("{\"error\": \"Falha ao inicializar o receptor LoRa\"}"));
        while (1);
    }

    LoRa.setSpreadingFactor(7);
    LoRa.setSignalBandwidth(125E3);
    LoRa.setCodingRate4(5);
    LoRa.setSyncWord(0x12);
    LoRa.enableCrc();

    Serial.println(F("{\"status\": \"Aguardando telemetria do TupaSat...\"}"));
}

void loop() {
    int packetSize = LoRa.parsePacket();
    if (packetSize) {
        String incoming = "";
        while (LoRa.available()) {
            incoming += (char)LoRa.read();
        }

        int rssi = LoRa.packetRssi();
        float snr = LoRa.packetSnr();

        // Envia linha formatada em JSON estruturado para o computador
        Serial.print(F("{\"raw\":\""));
        Serial.print(incoming);
        Serial.print(F("\",\"rssi\":"));
        Serial.print(rssi);
        Serial.print(F(",\"snr\":"));
        Serial.print(snr, 1);
        Serial.print(F(",\"bytes\":"));
        Serial.print(packetSize);
        Serial.println(F("}"));
    }
}
