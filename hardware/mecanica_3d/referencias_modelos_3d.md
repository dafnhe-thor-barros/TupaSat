# Catálogo de Modelos 3D e Estruturas Mecânicas — TupãSat 1U

Para facilitar a reprodução da estrutura física do **TupãSat**, este guia cataloga e analisa os principais modelos 3D abertos (STL/STEP) da comunidade global compatíveis com o padrão CubeSat 1U (100×100×100 mm), orientando a escolha conforme o objetivo pedagógico ou operacional.

---

## 1. Modelos 3D Recomendados para Impressão

### 🥇 1. CubeSatSim Universal 1U (Recomendação Principal)
* **Autor:** Alan Johnston (AMSAT - *Radio Amateur Satellite Corporation*)
* **Link de Download:** [Thingiverse 4333605](https://www.thingiverse.com/thing:4333605)
* **Compatibilidade com TupãSat:** **100% compatível** com o barramento empilhável TupãStack (placas de 90×90 mm ou 85×85 mm).
* **Vantagens:**
  * Trilhos laterais internos deslizantes (*slide-in rails*), permitindo encaixar e retirar placas eletrônicas como gavetas sem desmontar o chassi.
  * Furação externa padronizada para os 6 painéis solares fotovoltaicos de 6V.
  * Abertura superior para antena monopolo LoRa e antena patch de GPS.
* **Material Sugerido:** PETG ou PLA-HT (infill 40% giroide).

---

### 🥈 2. HeliosCube-Eleni (CubeSat 1U Open-Source)
* **Autor / Plataforma:** MakerWorld
* **Links de Download:** 
  * Estrutura: [HeliosCube-Eleni 1U no MakerWorld](https://makerworld.com/pt/models/1735798-helioscube-eleni-open-source-1u-cubesat)
  * Berço Eletrônico: [Eletrônicos do HeliosCube-Eleni](https://makerworld.com/pt/models/1735791-electronics-of-the-helioscube-eleni)
* **Vantagens:**
  * Otimizado para impressoras 3D modernas (Bambu Lab, Creality K1, Prusa MK4).
  * Inclui berço modular para fixação de baterias e módulos de rádio.
  * Acabamento estético e cantos arredondados de alta precisão.

---

### 🥉 3. Robinson Aerospace 1U Structure
* **Autor:** Robinson Aerospace
* **Link de Download:** [Thingiverse 6947346](https://www.thingiverse.com/thing:6947346)
* **Vantagens:**
  * Geometria estrita em conformidade com as tolerâncias de lançadores P-POD (*Poly-Picosatellite Orbital Deployer*).
  * Paredes estruturais reforçadas, ideal para ensaios mecânicos rigorosos ou lançamento em balão estratosférico.

---

### 4. Outras Estruturas Disponíveis para Ensino e Demonstração
* **Universal 1U CubeSat por Juliano85:** [Thingiverse 4096437](https://www.thingiverse.com/thing:4096437) — Montagem modular por placas parafusadas, ideal para alunos de ensino fundamental e médio.
* **1U Cubesat model v3 por TJEmsley:** [Thingiverse 2042254](https://www.thingiverse.com/thing:2042254) — Modelo clássico com cubos de canto em latão/M3.
* **CubeSat 1U da ESA:** [MakerWorld 2894831](https://makerworld.com/pt/models/2894831-cubesat-1u-from-esa) — Maquete detalhada para eventos, feiras de ciências e divulgação científica.
* **CubeSat U1:** [MakerWorld 889802](https://makerworld.com/pt/models/889802-cubesat-u1) e [MakerWorld 1027005](https://makerworld.com/pt/models/1027005-cubesat).

---

## 2. Parâmetros de Fatiamento (Slicer Profile) para o Chassi TupãSat

Para qualquer um dos modelos acima, utilize os seguintes parâmetros no seu fatiador (Bambu Studio, Cura, PrusaSlicer ou OrcaSlicer):

```ini
[Configurações de Impressão Recomendadas]
layer_height = 0.20 mm
first_layer_height = 0.24 mm
perimeters = 4 (mínimo de 1.6 mm de parede sólida)
top_solid_layers = 5
bottom_solid_layers = 5
fill_density = 40%
fill_pattern = gyroid (resistência mecânica isotrópica)
support_material = auto (com ângulo de overdrive > 50°)
nozzle_temperature = 210°C (PLA) / 240°C (PETG)
bed_temperature = 60°C (PLA) / 75°C (PETG)
```
