# Procedimentos de Teste e Validação em Solo — TupãSat 1U

Para assegurar a confiabilidade do **TupãSat** antes de qualquer operação em campo, lançamento em balão estratosférico ou apresentação acadêmica, devem ser executados os seguintes ensaios de verificação e validação (V&V).

---

## 1. Teste de Continuidade e Curto-Circuito (AIT-01)
* **Objetivo:** Garantir a ausência de curto-circuitos entre os barramentos de alimentação (+12V, +5V, +3.3V) e a referência de terra (GND) antes de conectar as baterias.
* **Procedimento:**
  1. Com a bateria desconectada e chave geral aberta, utilize o multímetro na escala de continuidade sonora (*bip*).
  2. Meça a resistência entre o polo positivo da entrada e o GND. A resistência deve ser superior a 10 kΩ.
  3. Repita o teste nos trilhos de 5V e 3.3V.

---

## 2. Teste Funcional dos Sensores de Carga Útil (AIT-02)
* **Objetivo:** Verificar a leitura e a precisão das grandezas físicas dos sensores AHT10, BMP180 e GPS.
* **Procedimento:**
  1. Carregue o firmware de teste na OBC e abra o Monitor Serial a 115200 bps.
  2. Verifique se o scanner I2C detecta os endereços `0x38` (AHT10) e `0x77` (BMP180).
  3. Sopre levemente sobre o sensor de umidade para constatar o aumento dinâmico da leitura de UR.
  4. Compare a pressão e altitude inicial medida com a altitude local conhecida da bancada (tolerância aceitável: $\pm 10 \text{ metros}$).
  5. Posicione o módulo GPS próximo a uma janela aberta e cronometre o tempo até a obtenção de fixação válida (*Time-To-First-Fix - TTFF*). Registre latitude, longitude e número de satélites visíveis.

---

## 3. Teste de Enlace de Rádio LoRa e Sensibilidade (AIT-03)
* **Objetivo:** Medir a estabilidade do enlace RF (915 MHz), taxa de perda de pacotes (*Packet Loss Rate - PLR*) e parâmetros de RSSI/SNR.
* **Procedimento:**
  1. Ligue o TupãSat em modo nominal de transmissão periódica (pacotes a cada 5 segundos).
  2. Conecte a Estação Terrena a um computador executando o script `dashboard.py`.
  3. Em bancada (distância de 5 a 10 metros com atenuador ou baixa potência), confirme a recepção de 100 pacotes consecutivos com $0\%$ de perda e CRC válido.
  4. Realize teste de campo com visada direta (distâncias de 100 m, 500 m, 1 km e 2 km). Anote os valores de RSSI (deve ser superior a $-120\text{ dBm}$) e SNR (positivo ou até $-10\text{ dB}$).

---

## 4. Teste de Balanço Energético e Autonomia da Bateria (AIT-04)
* **Objetivo:** Medir o consumo instantâneo de corrente nos modos de transmissão e standby, comprovando a autonomia estimada.
* **Procedimento:**
  1. Insira o multímetro em série com o polo positivo da bateria na escala de corrente DC (mA).
  2. Registre a corrente média durante o período de espera entre pacotes ($I_{\text{idle}} \approx 35 \text{ a } 50\text{ mA}$).
  3. Registre a corrente de pico durante o pulso de transmissão LoRa ($I_{\text{tx}} \approx 120 \text{ a } 150\text{ mA}$ durante ~80 ms).
  4. Calcule o consumo médio ponderado pelo ciclo de trabalho:
     $$I_{\text{medio}} = \frac{I_{\text{tx}} \cdot t_{\text{tx}} + I_{\text{idle}} \cdot t_{\text{idle}}}{t_{\text{periodo}}}$$
  5. Confirme a autonomia teórica: para uma bateria de 5000 mAh e corrente média de ~55 mA, a autonomia teórica contínua excede 80 horas.

---

## 5. Teste de Desempenho Térmico Preliminar (AIT-05)
* **Objetivo:** Avaliar o comportamento do chassi em PLA e dos componentes sob calor.
* **Procedimento:**
  1. Submeta o conjunto a operação contínua por 4 horas em ambiente controlado a $45^\circ\text{C}$ (estufa ou câmara térmica).
  2. Monitore a temperatura interna reportada pela telemetria do AHT10/BMP180.
  3. Verifique se a estrutura mecânica mantém o alinhamento e se não houve deformação plástica (*creep*) no chassi ou descolamento de fixadores.
