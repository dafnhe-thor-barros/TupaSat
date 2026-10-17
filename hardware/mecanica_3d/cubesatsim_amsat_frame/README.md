# Estrutura Mecânica CubeSatSim 1U (AMSAT / Alan Johnston)

Esta pasta contém os arquivos de fabricação aditiva (STLs) da estrutura oficial **CubeSatSim 1U**, adotada como o **chassi padrão do projeto TupãSat**.

---

## 🏛️ Atribuição, Créditos e Citação Formal

Este modelo é uma adaptação e remix de alta engenharia desenvolvido pela comunidade aeroespacial de código aberto:

* **Projeto Original:** *Universal 1U CubeSat for CubeSatSim* (Thingiverse [Thing:4333605](https://www.thingiverse.com/thing:4333605)).
* **Autor Principal:** Alan Johnston (`@alanbjohnston`) — [CubeSatSim.org](https://cubesatsim.org) / [GitHub alanbjohnston/CubeSatSim](https://github.com/alanbjohnston/CubeSatSim).
* **Organização Patrocinadora:** **AMSAT®** (*Radio Amateur Satellite Corporation* — corporação sem fins lucrativos de radioamadorismo por satélite).
* **Projeto CAD e Modificações:** Lindsay White (`KI6LZN`).
* **Design Base de Origem:** Remix do modelo *Universal 1U Cubesat* por Juliano85 ([Thingiverse 4096437](https://www.thingiverse.com/thing:4096437)).
* **Licenciamento:** Licença Aberta Creative Commons Attribution - ShareAlike (CC BY-SA).

### Citação Recomendada:
```bibtex
@misc{johnston2020cubesatsim,
  author       = {Johnston, Alan and White, Lindsay},
  title        = {Universal 1U CubeSat for CubeSatSim},
  howpublished = {Thingiverse Thing 4333605 / AMSAT (Radio Amateur Satellite Corporation)},
  year         = {2020},
  url          = {https://www.thingiverse.com/thing:4333605}
}
```

---

## 📁 Arquivos STL Incluídos

| Arquivo STL | Quantidade a Imprimir | Função no TupãSat |
| :--- | :---: | :--- |
| **`cubesatsim_frame_top_bottom.v2.0.stl`** | **2 peças** | Faces Superior e Inferior (tampas Z+ e Z-) com furação para montagem dos tirantes M3 e passagem para antena LoRa / SMA. |
| **`cubesatsim_frame_side.v2.0.stl`** | **1 peça** | Lateral estrutural padrão com trilhos deslizantes internos (*slide-in rails*). |
| **`cubesatsim_frame_side_camera.v2.0.stl`** | **1 peça** | Lateral especial com berço e janela para módulo de Câmera (ESP32-CAM / PiCam) e furo para LED de telemetria. |
| **`plug_circle_24.stl`** | **1 peça (Opcional)** | Plugue de proteção para a chave mecânica de corte *Remove Before Flight* (RBF). |

---

## 🛠️ Parâmetros de Impressão 3D Recomendados

* **Material:** PLA, PLA-HT (Alta Temperatura) ou PETG.
* **Altura de Camada (*Layer Height*):** $0.20\text{ mm}$ (ou $0.16\text{ mm}$ para encaixes mais suaves nos trilhos).
* **Paredes Externas (*Perimeters*):** 4 perímetros (mínimo de $1.6\text{ mm}$ de espessura sólida).
* **Camadas Topo / Fundo:** 5 camadas sólidas.
* **Preenchimento (*Infill*):** $20\%$ a $40\%$ com padrão **Giroide (*Gyroid*)**.
* **Suportes:** Não são necessários se as peças forem fatiadas deitadas na mesa de impressão.
* **Fixadores Mecânicos:** 4 parafusos de cabeça cilíndrica M3 × 10 mm e 4 porcas autotravantes com anel de nylon (*Nyloc*).

---

## 🌐 Fontes Paramétricas em CAD (OnShape)

Para modificações dimensionais ou customizações paramétricas, os modelos CAD originais estão disponíveis publicamente no OnShape:
* [Top/Bottom Frame - OnShape](https://cad.onshape.com/documents/ba47819ff100597297d1d967/w/f19409ec7cd5459afb429cb9/e/a0e0cc37dee6fb879c4bcc2b)
* [Side Frame - OnShape](https://cad.onshape.com/documents/1515e31c7fa5f6258ef39ae7/w/36f6069826ee0c0263f8d85e/e/2b7801717a8e1af3df455057)
* [Side Camera Frame - OnShape](https://cad.onshape.com/documents/188300bd4469521b14597507/w/546e1730182c1520c46b050d/e/ceef7084a00eb9b26c486bb6)
