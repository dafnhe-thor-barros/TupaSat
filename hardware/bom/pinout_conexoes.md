# Mapeamento Elétrico e Pinout — TupãSat (Base Arduino UNO / Sensor Shield V5)

Este documento define o mapeamento padronizado de conexões e barramentos elétricos entre o Computador de Bordo (OBC), o módulo de comunicação LoRa, os sensores da carga útil (Payload) e o subsistema de energia (EPS).

---

## 1. Barramentos Principais

| Barramento | Linhas | Tensão Lógica | Dispositivos Conectados | Observações |
| :--- | :--- | :--- | :--- | :--- |
| **I2C** | SDA, SCL | 3.3V / 5.0V | AHT10 (`0x38`), BMP180 (`0x77`) | Barramento compartilhado com resistores de pull-up (4.7 kΩ). |
| **SPI** | SCK, MISO, MOSI, NSS | 3.3V | Transceptor LoRa SX1276 (915 MHz) | Comunicação de alta velocidade para RF. |
| **UART (SoftSerial)** | RX (D4), TX (D3) | 3.3V / 5.0V | Módulo GPS (NEO-6M) | Taxa padrão: 9600 bps, mensagens NMEA. |
| **ADC Analógico** | A0 | 0.0V - 5.0V | Divisor de Tensão do Barramento de Bateria | Medição de telemetria do estado de carga (SoC). |
| **Interrupções** | INT0 (D2) | 3.3V / 5.0V | DIO0 do Módulo LoRa | Notificação por interrupção de recepção/envio de pacote. |

---

## 2. Pinout Detalhado (Arduino UNO + Sensor Shield V5)

### 2.1. Conexão do Transceptor LoRa SX1276 (915 MHz)
> **Atenção:** O chip SX1276 opera nativamente com **3.3V**. Certifique-se de que a linha VCC receba 3.3V estável (mínimo de 150 mA contínuos) com capacitor eletrolítico de desacoplamento de 100 µF em paralelo com 100 nF para suprimir transitórios durante o chaveamento do amplificador de potência (PA).

| Pino SX1276 | Pino Arduino UNO / Shield | Função | Nível Lógico |
| :--- | :--- | :--- | :--- |
| **VCC** | 3V3 (ou regulador 3.3V dedicado) | Alimentação positiva | +3.3V DC |
| **GND** | GND | Referência de terra | 0V |
| **SCK** | D13 | Clock do barramento SPI | 3.3V / 5V tolerante |
| **MISO** | D12 | Master In Slave Out | 3.3V |
| **MOSI** | D11 | Master Out Slave In | 3.3V / 5V tolerante |
| **NSS / CS** | D10 | Chip Select (ativo baixo) | Saída digital D10 |
| **RST / RESET**| D9 | Reset do transceptor | Saída digital D9 |
| **DIO0** | D2 (INT0) | Sinalizador de interrupção (RxDone/TxDone) | Entrada com interrupção externa |

---

### 2.2. Sensores da Carga Útil (Payload) — Barramento I2C

| Sensor | Pino Sensor | Pino Arduino UNO | Função | Endereço I2C |
| :--- | :--- | :--- | :--- | :--- |
| **AHT10** | VCC | 5V / 3V3 | Alimentação | - |
| | GND | GND | Terra | - |
| | SDA | A4 (SDA) | Dados I2C | `0x38` |
| | SCL | A5 (SCL) | Clock I2C | `0x38` |
| **BMP180** | VCC | 3V3 ou 5V (placa com LDO) | Alimentação | - |
| | GND | GND | Terra | - |
| | SDA | A4 (SDA) | Dados I2C | `0x77` |
| | SCL | A5 (SCL) | Clock I2C | `0x77` |

---

### 2.3. Módulo de Navegação GNSS/GPS (UART)

| Pino GPS NEO-6M | Pino Arduino UNO | Função | Observações |
| :--- | :--- | :--- | :--- |
| **VCC** | 5V | Alimentação | Consumo ~50 mA |
| **GND** | GND | Terra | 0V |
| **TX** | D4 | Arduino RX (SoftwareSerial) | Transmissão NMEA para a OBC |
| **RX** | D3 | Arduino TX (SoftwareSerial) | Comandos de configuração da OBC |

---

### 2.4. Telemetria do Subsistema de Energia (EPS) — Sensor de Tensão da Bateria

Para monitorar a bateria de 12V utilizando o conversor A/D de 10 bits do Arduino (0 a 5V com referência interna de 5V):
* **R1 (lado positivo da bateria):** 100 kΩ (1%)
* **R2 (lado GND):** 22 kΩ (1%)
* **Fator de Divisão:** $V_{\text{out}} = V_{\text{bat}} \times \frac{R_2}{R_1 + R_2} = V_{\text{bat}} \times \frac{22}{122} \approx 0.1803 \times V_{\text{bat}}$
* Para $V_{\text{bat}} = 12.6\text{ V}$ (carga máxima 3S Li-Ion), $V_{\text{out}} \approx 2.27\text{ V}$ (seguro para o pino A0 do Arduino).

| Ponto de Medição | Pino Arduino | Componente | Sinal |
| :--- | :--- | :--- | :--- |
| Ponto médio do divisor | A0 | R1 (100k) + R2 (22k) | Tensão analógica proporcional à bateria |

---

## 3. Topologia de Alimentação e Barramentos DC

```
                +-------------------+
                | 6x Painéis 6V     |
                | (Faces CubeSat 1U)|
                +---------+---------+
                          |
                          v
                +-------------------+
                |  Controlador MPPT |
                +---------+---------+
                          |
             +------------+------------+
             |                         |
             v                         v
     +---------------+         +---------------+
     | Bateria 12V   |         | Regulador Buck|
     | Li-Ion 5000mAh|         | 12V -> 5V DC  |
     +---------------+         +-------+-------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
         +-------------------+                   +-------------------+
         | Trilho 5.0V       |                   | LDO 3.3V          |
         | - Arduino UNO     |                   | - Transceptor     |
         | - Sensores I2C    |                   |   LoRa SX1276     |
         | - GPS NEO-6M      |                   +-------------------+
         +-------------------+
```
