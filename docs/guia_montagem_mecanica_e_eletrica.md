# Guia de Montagem Mecânica e Integração Elétrica — TupãSat 1U

Este roteiro foi elaborado sob a ótica de **Aprendizagem Baseada em Problemas (PBL)**, servindo como manual de oficina prática para professores, alunos de graduação, cursos técnicos e entusiastas espaciais.

---

## 1. Ferramental Necessário
* Ferro de solda com temperatura ajustável (30W a 60W) e solda estanho/chumbo (ou lead-free).
* Chave Allen M3 e chave Philips fina.
* Multímetro digital (medição de continuidade, tensão DC e corrente).
* Alicate de corte rente e alicate de bico.
* Fita isolante de Kapton (alta rigidez dielétrica e resistência térmica).
* Tubo termo retrátil de 2 mm a 5 mm.

---

## 2. Passo 1: Preparação da Estrutura 3D (Chassi)
1. Inspecione as 4 peças angulares do chassi impresso em 3D, conferindo as dimensões externas de $100 \times 100 \times 100 \text{ mm}$.
2. Remova rebarbas e suportes de impressão com lixa fina d'água (grão 400).
3. Passe um macho manual M3 nos furos de fixação para garantir que os parafusos entrem retos sem esmagar o plástico.
4. Reserve as faces laterais com guias de passagem para os cabos dos painéis solares.

---

## 3. Passo 2: Montagem do Subsistema de Energia (EPS)
1. **Inspeção da Bateria:** Meça a tensão em vazio da bateria de 12V com o multímetro. O valor deve estar entre 11.1V e 12.6V.
2. **Montagem do Divisor Resistivo:**
   * Solde o resistor R1 (100 kΩ) em série com R2 (22 kΩ).
   * O terminal livre de R1 vai para o barramento positivo da bateria (+12V).
   * O terminal livre de R2 vai para a referência comum (GND).
   * O ponto central de junção vai para o cabo de medição do pino analógico A0 da OBC.
3. **Controlador MPPT:**
   * Conecte a entrada fotovoltaica do MPPT aos barramentos de junção dos 6 painéis solares (em configuração paralela com diodos Schottky de proteção antireverso tipo 1N5819).
   * Conecte a saída de carga do MPPT aos polos da bateria.
4. **Regulador Buck (12V para 5V):**
   * Ajuste o trimpot do conversor DC-DC para cravar exatamente $5.00 \pm 0.05 \text{ V}$ antes de ligar em qualquer placa controladora!

---

## 4. Passo 3: Integração do Computador de Bordo (OBC) e Sensores
1. Encaixe com firmeza o **Sensor Shield V5.0** sobre a placa **Arduino UNO**, verificando se nenhum pino entortou durante o acoplamento.
2. **Barramento I2C:**
   * Conecte os pinos SDA dos sensores AHT10 e BMP180 ao barramento SDA (A4) do shield.
   * Conecte os pinos SCL ao barramento SCL (A5) do shield.
   * Alimente ambos os sensores com o barramento de 5V ou 3.3V conforme o modelo da plaquinha regulada.
3. **Módulo GPS:**
   * Conecte o pino TX do GPS no pino digital D4 do Arduino.
   * Conecte o pino RX do GPS no pino digital D3 do Arduino.
   * Conecte o VCC no barramento de 5V e o GND na referência.
4. **Módulo LoRa SX1276:**
   * Conecte as linhas SPI (D13=SCK, D12=MISO, D11=MOSI, D10=NSS, D9=RST, D2=DIO0).
   * **Imprescindível:** O módulo LoRa deve ser alimentado na linha de 3.3V com capacitor de desacoplamento de 100 µF soldado junto aos seus pinos VCC/GND. **Nunca transmita sem a antena rosqueada**, sob risco de queimar o amplificador de potência (PA) por onda estacionária refletida (SWR elevado).

---

## 5. Passo 4: Integração Final no Chassi
1. Posicione a bateria no fundo do satélite (base Z-) utilizando fita adesiva dupla-face automotiva de espuma e braçadeiras de nylon.
2. Fixe o conjunto Arduino + Shield nos espaçadores de nylon centrais.
3. Fixe a antena do GPS e do LoRa na face superior (Z+).
4. Feche a estrutura com os 8 parafusos M3 estruturais e porcas com trava de nylon.
5. Pese a estrutura completa para verificar a conformidade com o limite de 1000g.
