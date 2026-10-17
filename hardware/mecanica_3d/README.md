# Diretrizes Mecânicas e Impressão 3D — Chassi TupãSat 1U

Este diretório contém as especificações geométricas, de materiais e de montagem da estrutura física (STR) do **TupãSat**, compatível com o padrão CubeSat 1U (100 mm × 100 mm × 100 mm).

---

## 1. Requisitos Mecânicos Gerais

* **Dimensões Externas:** $100.0 \pm 0.5 \text{ mm} \times 100.0 \pm 0.5 \text{ mm} \times 100.0 \pm 0.5 \text{ mm}$.
* **Trilhos de Ejeção (*Rails*):** 4 arestas externas com largura mínima de $8.5 \text{ mm}$ e chanfro/raio nos cantos para compatibilidade com o padrão P-POD (*Poly-Picosatellite Orbital Deployer*).
* **Massa Máxima da Estrutura:** $\le 200 \text{ g}$.
* **Material Recomendado:**
  * **Prototipagem Educacional / Solo:** PLA ou PLA-HT (Alta Temperatura).
  * **Testes em Balão Estratosférico / Ambientes Térmicos Severos:** PETG ou ABS (temperatura de transição vítrea superior, resistente a deformação em ciclos térmicos).

---

## 2. Parâmetros de Impressão 3D (FDM)

Para garantir resistência mecânica e evitar descolamento de camadas (*delaminação*):

| Parâmetro | Valor Recomendado | Justificativa |
| :--- | :--- | :--- |
| **Altura de Camada** | 0.20 mm | Bom equilíbrio entre acabamento superficial e adesão de camada |
| **Paredes Externas (*Perimeters*)** | 4 a 5 perímetros | Resistência a esforço de aperto dos parafusos M3 |
| **Camadas Superior / Inferior** | 5 camadas sólidas | Rigidez torsional |
| **Densidade de Preenchimento (*Infill*)** | 35% a 50% | Redução de massa sem comprometer estabilidade |
| **Padrão de Preenchimento** | Giroide (*Gyroid*) | Resistência isotrópica contra vibração multidirecional |
| **Tolerância Dimensional nos Furos** | +0.2 mm | Facilita a passagem livre dos parafusos M3 |

---

## 3. Arquitetura de Montagem Interna

A estrutura adota o conceito de **bandejas empilháveis (*stack modular*)**:

1. **Base Inferior:** Alojamento da bateria (12V 5000 mAh) e do controlador de carga MPPT, mantendo o centro de massa o mais próximo possível do centro geométrico do satélite.
2. **Nível Intermediário:** Placa do Computador de Bordo (Arduino UNO + Sensor Shield V5.0) e reguladores DC-DC.
3. **Nível Superior:** Módulo transceptor LoRa SX1276, antena e módulo GPS com visada limpa para o zênite.
4. **Faces Laterais (X+, X-, Y+, Y-):** Painéis solares de 6V montados externamente com parafusos de nylon ou adesivo térmico estrutural.
5. **Face Superior (Z+):** Painel solar superior + passagem da antena monopolo/dipolo LoRa e antena patch do GPS.
6. **Face Inferior (Z-):** Painel solar inferior + chave geral mecânica (*Remove Before Flight* / RBF) e porta de programação/carga externa.

---

## 4. Lista de Fixadores Recomendados

* Parafusos tipo Allen de cabeça cilíndrica M3 × 12 mm e M3 × 25 mm (Aço Inox ou latão).
* Espaçadores hexagonais M3 de nylon (15 mm e 20 mm) para separação das placas eletrônicas.
* Porcas M3 autotravantes com anel de nylon (*Nyloc*).
* Arruelas M3 de fibra ou latão.
