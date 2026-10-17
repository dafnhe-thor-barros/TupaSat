# Protocolo de Telemetria e Telecomando — TupãSat 1U

Para equilibrar **simplicidade pedagógica** para estudantes iniciantes e **eficiência de engenharia aeroespacial** para aplicações avançadas, o **TupãSat** suporta dois formatos de transmissão de telemetria via rádio LoRa (915 MHz):

1. **Protocolo Padrão ASCII (Formato NMEA estendido):** Altamente legível no monitor serial do Arduino, fácil de depurar e analisar em planilhas ou Python.
2. **Protocolo Compacto Binário:** Para redução do tempo no ar (*Time-on-Air - ToA*), economia extrema de energia e maior confiabilidade de longo alcance.

---

## 1. Protocolo Padrão ASCII (Recomendado para Ensino)

Cada linha transmitida termina com `\r\n` e segue a estrutura:

```
$TUPA,<PKT_ID>,<UPTIME_S>,<STATUS>,<V_BAT>,<T_AHT>,<HUM_AHT>,<T_BMP>,<PRESS_HPA>,<ALT_M>,<GPS_FIX>,<LAT>,<LON>,<SATS>*<CRC16>
```

### 1.1. Dicionário de Campos

| Campo | Tipo | Exemplo | Unidade | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **Prefixo** | String | `$TUPA` | - | Identificador de início de sentença do TupãSat |
| **PKT_ID** | Inteiro | `142` | Contagem | Número sequencial do pacote transmitido |
| **UPTIME_S**| Inteiro | `710` | Segundos | Tempo decorrido desde o boot da OBC |
| **STATUS** | Hex/Int | `0` | Bitmask | `0`=Nominal, `1`=SafeMode, `2`=I2C Error, `4`=GPS NoFix |
| **V_BAT** | Float (2 casas) | `11.85` | Volts (V) | Tensão no barramento de baterias |
| **T_AHT** | Float (2 casas) | `24.50` | °C | Temperatura interna medida pelo sensor AHT10 |
| **HUM_AHT** | Float (1 casa) | `58.2` | % UR | Umidade relativa do ar medida pelo AHT10 |
| **T_BMP** | Float (2 casas) | `24.30` | °C | Temperatura medida pelo sensor BMP180 |
| **PRESS_HPA**| Float (1 casa)| `1013.2`| hPa | Pressão atmosférica barométrica |
| **ALT_M** | Float (1 casa) | `15.4` | Metros | Altitude calculada a partir do nível do mar (QNH) |
| **GPS_FIX** | Inteiro | `1` | Booleano | `1`=Fixado (válido), `0`=Sem sinal de satélites |
| **LAT** | Float (5 casas) | `-20.27410`| Graus | Latitude (coordenadas geográficas) |
| **LON** | Float (5 casas) | `-40.30650`| Graus | Longitude (coordenadas geográficas) |
| **SATS** | Inteiro | `7` | Contagem | Quantidade de satélites GNSS rastreados |
| **CRC16** | Hex (4 dígitos)| `A3F8` | - | Checksum CRC-CCITT (polinômio 0x1021) |

### 1.2. Exemplo de Pacote Transmitido
```text
$TUPA,142,710,0,11.85,24.50,58.2,24.30,1013.2,15.4,1,-20.27410,-40.30650,7*8C2F
```

---

## 2. Protocolo Compacto Binário (Avançado)

Para missões que necessitam de transmissões ultrarrápidas, a telemetria é empacotada em uma estrutura C/C++ binária com alinhamento de 1 byte (`#pragma pack(push, 1)`):

```c
#pragma pack(push, 1)
typedef struct {
    uint8_t  sync_word[2];   // 0x54, 0x50 ("TP")
    uint16_t packet_id;      // Contador incremental
    uint32_t uptime_sec;     // Segundos desde a energização
    uint8_t  system_status;  // Status de subsistemas
    uint16_t v_bat_mv;       // Tensão da bateria em milivolts (ex.: 11850 mV)
    int16_t  temp_aht_c;     // Temp AHT em centésimos de grau (2450 = 24.50 °C)
    uint16_t humidity_c;     // Umidade em centésimos (5820 = 58.20 %)
    int16_t  temp_bmp_c;     // Temp BMP em centésimos de grau
    uint32_t pressure_pa;    // Pressão em Pascals (101325 Pa)
    int32_t  altitude_cm;    // Altitude em centímetros
    uint8_t  gps_fix;        // 0 = No Fix, 1 = 2D/3D Fix
    int32_t  latitude_scaled;// Latitude * 10^6
    int32_t  longitude_scaled;// Longitude * 10^6
    uint8_t  satellites;     // Número de satélites visíveis
    uint16_t crc16;          // CRC16 do payload
} TupaSatPacket_t;
#pragma pack(pop)
```
* **Tamanho total:** 36 bytes (vs ~85 bytes do formato ASCII).
* **Tempo no ar (ToA):** Redução de aproximadamente 60%, aumentando a sensibilidade marginal e a probabilidade de recepção sem erros em enlaces com grande atenuação.

---

## 3. Configurações da Camada Física LoRa (RF)

| Parâmetro RF | Valor Padrão | Justificativa |
| :--- | :--- | :--- |
| **Frequência Central** | 915.000 MHz | Faixa ISM liberada pela Anatel no Brasil (UHF) |
| **Largura de Banda (BW)** | 125 kHz | Padrão ótimo para longo alcance e sensibilidade |
| **Spreading Factor (SF)** | SF7 (Nominal) / SF10 (Longo alcance) | SF7 provê menor ToA e alta taxa; SF10 para alcance estendido |
| **Coding Rate (CR)** | 4/5 | Taxa de correção de erro de transmissão com baixo overhead |
| **Potência de Transmissão (TX Power)** | +17 dBm (~50 mW) | Excelente alcance com dissipação térmica moderada |
| **Preâmbulo** | 8 símbolos | Sincronismo rápido do receptor de solo |
| **Polarização de Antena** | Linear vertical | Compatível com antena monopolo vertical de 1/4 de onda (~7.8 cm) |

---

## 4. Cálculo do CRC16

O checksum adotado é o padrão **CRC16-CCITT** (polinômio gerador $0x1021$, valor inicial $0xFFFF$), garantindo que dados corrompidos por ruído eletromagnético ou desvanecimento (*fading*) sejam descartados pela estação terrena.
