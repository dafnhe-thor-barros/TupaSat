# Especificação Técnica de Requisitos de Engenharia — TupãSat 1U

**Projeto:** TupãSat — Kit de CubeSat Modular para Fins Acadêmicos, Ensino e Pesquisa  
**Documento Base:** *Desenvolvimento de um kit de CubeSat para fins acadêmicos: projeto, construção e aplicações* (Barros, 2025 - Caderno Pedagógico, DOI: 10.54033/cadpedv22n10-248)  
**Autor do Projeto:** Dafnhê Thor Castro de Martins Barros  

---

## 1. Introdução e Propósito

O **TupãSat** é uma plataforma de nanossatélite no padrão CubeSat 1U desenvolvida para integrar o ensino de ciências, tecnologia, engenharia e matemática (STEM) através de metodologias ativas como a Aprendizagem Baseada em Problemas (*Problem-Based Learning* - PBL). 

Este documento estabelece os requisitos formais de engenharia de sistemas nos moldes dos padrões aeroespaciais (ECSS / CubeSat Design Specification), balanceados para viabilidade econômica, facilidade de replicação e alta confiabilidade operacional em solo e voos estratosféricos.

---

## 2. Requisitos de Missão e Restrições de Sistema

| Código | Descrição do Requisito | Valor / Meta | Verificação |
| :--- | :--- | :--- | :--- |
| **REQ-GEN-01** | O satélite deve cumprir o padrão dimensional CubeSat 1U. | $100 \times 100 \times 100 \text{ mm} \pm 0.5 \text{ mm}$ | Medição dimensional direta |
| **REQ-GEN-02** | A massa total do satélite integrada não deve exceder o limite de 1U. | $\le 1000 \text{ g}$ (Meta: ~822 g) | Pesagem em balança de precisão |
| **REQ-GEN-03** | O custo total dos materiais deve ser compatível com orçamentos acadêmicos. | $\le \text{R\$} 1.000,00$ (Base: R$ 810,00) | Análise de BOM |
| **REQ-GEN-04** | A estrutura deve permitir montagem e desmontagem didática rápida. | Fixação modular por parafusos M3 | Teste de montagem por estudantes |

---

## 3. Requisitos dos Subsistemas

### 3.1. Estrutura e Controle Térmico (STR & TCS)
* **REQ-STR-01:** O chassi primário deve ser fabricado por manufatura aditiva (impressão 3D) em polímero resistente (PLA-HT, PETG ou ABS), garantindo baixo custo e prototipagem acessível.
* **REQ-STR-02:** A estrutura deve possuir nervuras de reforço capazes de suportar vibrações de transporte e testes de lançamento sem fratura.
* **REQ-STR-03:** A estrutura deve acomodar 6 painéis solares externos (um por face) sem interferir nos trilhos de deslizamento (*rails*).
* **REQ-TCS-01:** A disposição dos componentes internos deve priorizar o isolamento térmico da bateria e a dissipação do calor do regulador de tensão e amplificador de potência do rádio.

### 3.2. Computador de Bordo e Tratamento de Dados (OBC / OBDH)
* **REQ-OBC-01:** O processador principal na versão básica deve ser compatível com a plataforma Arduino (ATmega328P / Arduino UNO) para facilitar o aprendizado em níveis introdutórios.
* **REQ-OBC-02:** A arquitetura do código deve permitir expansão futura para microcontroladores avançados (ex.: ESP32 dual core ou RP2040) sem alteração na pinagem dos sensores.
* **REQ-OBC-03:** O software embarcado deve implementar um mecanismo de temporização (*watchdog timer* e rotina de reinicialização automática) contra travamentos causados por ruído elétrico ou oscilação de alimentação.
* **REQ-OBC-04:** A OBC deve coletar periodicamente dados de saúde do satélite (*Housekeeping*) e da carga útil a cada 5 segundos (configurável de 1s a 60s).

### 3.3. Sistema de Gerenciamento de Energia Elétrica (EPS / SGE)
* **REQ-EPS-01:** O satélite deve dispor de geração fotovoltaica autônoma utilizando 6 faces solares de 6V, com capacidade total combinada de geração de até 2160 mW pico sob iluminação plena (1 Sol).
* **REQ-EPS-02:** O armazenamento deve ser provido por bateria recarregável Li-Ion de alta capacidade (12V nominal, 5000 mAh), assegurando autonomia superior a 15 horas sem incidência solar.
* **REQ-EPS-03:** O sistema deve contar com controlador de carga inteligente com algoritmo MPPT (*Maximum Power Point Tracking*) para maximizar o rendimento energético das células solares.
* **REQ-EPS-04:** O barramento de tensão regulado de 5.0V e 3.3V deve possuir proteção contra sobrecorrente e inversão de polaridade.
* **REQ-EPS-05:** A telemetria deve monitorar continuamente a tensão do banco de baterias via canal analógico dedicado.

### 3.4. Comunicação e Telecomando (TTC / COMMS)
* **REQ-COM-01:** A comunicação deve operar na frequência de 915 MHz (faixa ISM - UHF), dispensando licenciamentos onerosos para testes acadêmicos no Brasil.
* **REQ-COM-02:** A modulação deve utilizar a tecnologia LoRa (*Long Range*, chip Semtech SX1276), assegurando sensibilidade de até -148 dBm e alcance de linha de visada de até 4 km a 15 km com antena adequada.
* **REQ-COM-03:** Todos os pacotes transmitidos devem conter código de redundância cíclica (CRC16) e identificador único de satélite (`TUPASAT-1U`) para garantir integridade e rejeitar ruídos de canal.
* **REQ-COM-04:** A potência de transmissão deve ser configurável (padrão de +17 dBm a +20 dBm).

### 3.5. Carga Útil e Sensores (PAYLOAD)
* **REQ-PAY-01:** O subsistema de sensoriamento deve incluir medição de temperatura ambiente e umidade relativa de alta precisão via sensor AHT10.
* **REQ-PAY-02:** O subsistema deve incluir sensor barométrico BMP180 para cálculo de pressão atmosférica e estimativa de altitude barométrica.
* **REQ-PAY-03:** O satélite deve incorporar receptor GNSS/GPS capaz de fornecer latitude, longitude, altitude geodésica, velocidade de deslocamento e timestamp UTC sincronizado.
* **REQ-PAY-04:** O sistema deve manter canal I2C livre para conexão de sensores adicionais projetados pelos alunos (ex.: magnetômetro, sensor de radiação ou espectrômetro UV).

### 3.6. Estação de Solo (GROUND SEGMENT)
* **REQ-GS-01:** A estação terrena deve ser composta por um rádio receptor LoRa 915 MHz com saída serial USB.
* **REQ-GS-02:** A estação deve disponibilizar software de recepção (script Python com dashboard de tempo real) capaz de decodificar a telemetria, validar o CRC e exportar os dados em arquivo CSV estruturado para análise pedagógica.
