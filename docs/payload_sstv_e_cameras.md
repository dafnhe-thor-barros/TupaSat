# Carga Útil Opcional: Câmera e Transmissão de Imagens (SSTV / ESP32-CAM)

Este documento descreve uma proposta de **Carga Útil Avançada (Payload Experimental)** para o TupãSat, inspirada em projetos abertos da comunidade espacial de radioamadorismo como o *Launch-Ready SSTV CubeSat* (Instructables) e o *Stellarons MIT CubeSat*.

---

## 1. O Que é SSTV (*Slow-Scan Television*)?

O **SSTV** é um método tradicionalmente utilizado em satélites e estações orbitais (incluindo a Estação Espacial Internacional - ISS) para transmitir imagens estáticas através de canais de rádio de baixa largura de banda (banda vocal de rádio de 3 kHz). 

As linhas da imagem são convertidas em tons de áudio audíveis (frequências proporcionais ao brilho e cores de cada pixel), que são modulados em rádio (UHF/FM) e podem ser decodificados no solo por:
* Qualquer rádio receptor (walkie-talkie analógico ou SDR);
* Aplicativos gratuitos de smartphone (ex.: *Robot36* no Android ou *BlackCat SSTV* no iOS);
* Computador conectado a uma interface de áudio / fone de ouvido.

---

## 2. Proposta de Arquitetura da Câmera para o TupãSat

```
   +-----------------------+
   |   Sensor OV2640       |
   | (Lente Grande Angular)|
   +-----------+-----------+
               |
               v
   +-----------------------+
   |  Módulo ESP32-CAM     |  (Custo: ~R$ 35,00)
   | - Buffer de Frame     |
   | - Codificador SSTV    |
   +-----------+-----------+
               |
        +------+------+
        |             |
        v (Áudio)     v (Dados LoRa)
   +---------+   +---------+
   | Rádio   |   | LoRa    |
   | UHF FM  |   | SX1276  | (Transmissão em pacotes de bytes)
   +---------+   +---------+
```

---

## 3. Modo 1: Transmissão por LoRa (Pacotes de Imagem JPEG)
1. A câmera tira uma foto de baixa resolução ($160 \times 120$ ou $320 \times 240$ pixels em escala de cinza ou JPEG comprimido).
2. O arquivo de ~3 kB a 8 kB é fatiado em pacotes LoRa de 200 bytes.
3. A estação de solo recebe os fragmentos, monta a imagem e exibe no Dashboard em tempo real.

## 4. Modo 2: Transmissão por SSTV Analógico (Modo Robot36)
1. A imagem é convertida em um stream de áudio no padrão **Robot36** (tempo de transmissão: ~36 segundos por imagem colorida).
2. O transmissor emite o sinal de áudio na frequência VHF/UHF.
3. Alunos na escola apontam o celular próximo ao alto-falante do receptor de solo e assistem à imagem sendo desenhada linha por linha na tela do smartphone!

---

## 5. Referências e Inspirações
* **Instructables Launch-Ready SSTV CubeSat:** [Tutorial Completo](https://www.instructables.com/Launch-Ready-SSTV-CubeSat)
* **HyperDuino CubeSat Project:** [Tutorial Completo](https://www.instructables.com/HyperDuino-based-CubeSat)
* **MIT Stellarons CubeSat Project:** [Tutorial Completo](https://www.instructables.com/Stellarons-MIT-Cubesat-Project)
