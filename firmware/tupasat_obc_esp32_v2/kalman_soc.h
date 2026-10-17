#ifndef KALMAN_SOC_H
#define KALMAN_SOC_H

#include <Arduino.h>

/**
 * Estimador de Estado de Carga (SoC) com Filtro de Kalman Adaptativo (AEKF)
 * Implementação embarcada baseada em circuito equivalente de 1ª ordem Thevenin
 * para baterias de Íon de Lítio (Li-Ion 3S, 5000 mAh).
 */
class BatteryKalmanSoC {
public:
    BatteryKalmanSoC();

    /**
     * Inicializa o estimador com parâmetros da bateria
     * @param capacity_mah Capacidade nominal da bateria em mAh (ex.: 5000)
     * @param initial_voltage Tensão de circuito aberto no boot para estimativa inicial
     */
    void begin(float capacity_mah, float initial_voltage);

    /**
     * Executa um ciclo de predição e atualização do Filtro de Kalman
     * @param v_meas_volts Tensão medida no barramento (V)
     * @param i_meas_ma Corrente medida (mA), positiva = descarga, negativa = recarga solar
     * @param dt_seconds Intervalo de amostragem em segundos
     * @return Estado de Carga estimado em porcentagem (0.0% a 100.0%)
     */
    float update(float v_meas_volts, float i_meas_ma, float dt_seconds);

    float getSoC() const { return soc * 100.0f; }
    float getVariance() const { return P; }

private:
    float Q_total_as;   // Capacidade total em Ampere-segundos (Coulombs)
    float soc;          // Estado de Carga normalizado [0.0, 1.0]
    float P;            // Covariância do erro de estimação
    float Q_proc;       // Ruído de processo (incerteza do modelo)
    float R_meas;       // Ruído de medição do sensor de tensão
    float R0_ohm;       // Resistência interna ôhmica da bateria (~0.08 Ohm para 3S)

    float ocvFromSoC(float s);
    float dOcv_dSoC(float s);
};

#endif // KALMAN_SOC_H
