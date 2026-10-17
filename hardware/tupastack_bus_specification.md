# Especificação do Barramento Empilhável "TupãStack" (30 Pinos)

O barramento **TupãStack** é uma especificação aberta de interface física e elétrica que padroniza o empilhamento das placas de circuito impresso (PCBs) do TupãSat v2.0. Inspirado no clássico padrão aeroespacial PC/104, o TupãStack utiliza conectores duplos fêmea/macho de passo 2.54 mm (2×15 vias), eliminando cabos avulsos (*jumpers*), prevenindo desconexões em testes vibracionais e garantindo modularidade para inclusão de novas placas de carga útil desenvolvidas por estudantes.

---

## 1. Pinagem do Conector de Empilhamento (2×15 Vias - 30 Pinos)

```text
               CONECTOR TUPÃSTACK (VISTA SUPERIOR)
                     Linha A       Linha B
                 (Ímpares)     (Pares)
        +12V_RAW  [ 1]           [ 2]  +12V_RAW
         +5V_REG  [ 3]           [ 4]  +5V_REG
       +3V3_MAIN  [ 5]           [ 6]  +3V3_MAIN
             GND  [ 7]           [ 8]  GND
             GND  [ 9]           [10]  GND
        I2C1_SDA  [11]           [12]  I2C1_SCL
        SPI_MOSI  [13]           [14]  SPI_MISO
         SPI_SCK  [15]           [16]  SPI_CS_LORA
      SPI_CS_PAY  [17]           [18]  SPI_CS_SD
         UART_TX  [19]           [20]  UART_RX
       GPS_RX_OBC [21]           [22]  GPS_TX_OBC
       INT_LORA_0 [23]           [24]  INT_PAYLOAD
        RST_MAIN  [25]           [26]  RBF_SENSE
         ADC_BAT  [27]           [28]  ADC_CURRENT
        GPIO_AUX  [29]           [30]  GPIO_STATUS_LED
```

---

## 2. Descrição das Funções dos Pinos

| Pino | Sinal | Tipo | Nível | Descrição |
| :---: | :--- | :---: | :---: | :--- |
| **1, 2** | `+12V_RAW` | Alimentação | +11.1V a +12.6V | Barramento direto da bateria / controlador de carga MPPT. |
| **3, 4** | `+5V_REG` | Alimentação | +5.0V DC ($\pm 2\%$) | Barramento regulado para sensores I2C de 5V, GPS e expansões. |
| **5, 6** | `+3V3_MAIN`| Alimentação | +3.3V DC ($\pm 1\%$) | Barramento principal para OBC (ESP32), LoRa e lógica digital. |
| **7-10** | `GND` | Referência | 0V | Plano de terra comum com retorno de baixa impedância. |
| **11** | `I2C1_SDA` | Bidirecional | 3.3V | Linha de dados do barramento I2C compartilhado. |
| **12** | `I2C1_SCL` | Saída (OBC) | 3.3V | Linha de clock do barramento I2C (100 kHz a 400 kHz). |
| **13** | `SPI_MOSI` | Saída (OBC) | 3.3V | Master Out Slave In do barramento SPI de alta velocidade. |
| **14** | `SPI_MISO` | Entrada (OBC)| 3.3V | Master In Slave Out do barramento SPI. |
| **15** | `SPI_SCK` | Saída (OBC) | 3.3V | Linha de clock do barramento SPI (até 10 MHz). |
| **16** | `SPI_CS_LORA`| Saída (OBC) | 3.3V | Chip Select dedicado para o transceptor LoRa SX1276. |
| **17** | `SPI_CS_PAY` | Saída (OBC) | 3.3V | Chip Select reservado para placa de Carga Útil experimental. |
| **18** | `SPI_CS_SD` | Saída (OBC) | 3.3V | Chip Select para leitor de cartão de memória / BlackBox. |
| **19** | `UART_TX` | Saída (OBC) | 3.3V | Linha de transmissão serial (Debug / Telemetria cabeada). |
| **20** | `UART_RX` | Entrada (OBC)| 3.3V | Linha de recepção serial. |
| **21** | `GPS_RX_OBC`| Entrada (OBC)| 3.3V / 5V | Recepção de dados NMEA do receptor GPS. |
| **22** | `GPS_TX_OBC`| Saída (OBC) | 3.3V | Transmissão de comandos e configuração para o GPS. |
| **23** | `INT_LORA_0`| Entrada (OBC)| 3.3V | Interrupção externa (DIO0 do LoRa: RxDone / TxDone). |
| **24** | `INT_PAYLOAD`| Entrada (OBC)| 3.3V | Interrupção gerada pela placa de carga útil (ex.: alarme de evento). |
| **25** | `RST_MAIN` | Entrada/Saída| 3.3V | Linha de Reset mestre do sistema (ativo baixo). |
| **26** | `RBF_SENSE` | Entrada (OBC)| 3.3V | Sensor de estado do pino *Remove Before Flight* (chave geral). |
| **27** | `ADC_BAT` | Entrada analógica| 0 a 3.3V | Amostragem analógica redundante da bateria. |
| **28** | `ADC_CURRENT`| Entrada analógica| 0 a 3.3V | Amostragem analógica de corrente do barramento principal. |
| **29** | `GPIO_AUX` | Bidirecional | 3.3V | Pino de uso geral para controle de atuador ou sensor. |
| **30** | `GPIO_LED` | Saída (OBC) | 3.3V | Linha de controle para LED externo de sinalização de status. |

---

## 3. Diretrizes de Projeto de Placa (PCB Layout)

* **Dimensões das Placas do Stack:** $90.0 \times 90.0 \text{ mm}$ com cantos arredondados ($R = 3.0 \text{ mm}$).
* **Furos de Montagem:** 4 furos de $\varnothing 3.2 \text{ mm}$ localizados nos vértices ($X = 5.0 \text{ mm}, Y = 5.0 \text{ mm}$ a partir das bordas externas), permitindo a passagem de tirantes de aço inoxidável ou espaçadores M3 de latão/nylon.
* **Espessura da Placa:** $1.6 \text{ mm}$, padrão FR-4 de 2 camadas com plano de terra maciço na camada inferior (*Bottom Layer*).
* **Capacidade de Corrente dos Trilhos:**
  * Trilhos de terra (`GND`) e de alimentação (`+12V`, `+5V`, `+3.3V`): trilhas com largura mínima de $1.2 \text{ mm}$ (ou plano de cobre dedicado) para suportar correntes contínuas de até $2.0\text{ A}$ com baixa elevação térmica.
  * Trilhas de sinais de dados e barramentos (I2C, SPI, UART): largura padrão de $0.254 \text{ mm}$ (10 mil).
