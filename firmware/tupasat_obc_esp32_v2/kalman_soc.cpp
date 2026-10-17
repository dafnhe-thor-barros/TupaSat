#include "kalman_soc.h"
#include <math.h>

BatteryKalmanSoC::BatteryKalmanSoC()
    : Q_total_as(18000.0f),
      soc(0.80f),
      P(0.01f),
      Q_proc(1e-6f),
      R_meas(0.04f),
      R0_ohm(0.08f) {}

void BatteryKalmanSoC::begin(float capacity_mah, float initial_voltage) {
    Q_total_as = (capacity_mah / 1000.0f) * 3600.0f; // Converte mAh para A.s (Coulombs)

    // Estimativa inicial grosseira de SoC via curva inversa OCV estática
    if (initial_voltage >= 12.50f) soc = 0.98f;
    else if (initial_voltage <= 9.60f) soc = 0.05f;
    else soc = (initial_voltage - 9.60f) / (12.60f - 9.60f);

    // Limites de saturação
    if (soc > 1.0f) soc = 1.0f;
    if (soc < 0.0f) soc = 0.0f;

    P = 0.05f; // Incerteza inicial moderada
}

float BatteryKalmanSoC::ocvFromSoC(float s) {
    // Modelo polinomial da curva OCV para bateria Li-Ion 3S (9.0V a 12.6V)
    // V_ocv(s) = a0 + a1*s + a2*s^2 + a3*s^3
    if (s <= 0.0f) return 9.00f;
    if (s >= 1.0f) return 12.60f;
    return 9.60f + 2.40f * s + 0.60f * (s * s);
}

float BatteryKalmanSoC::dOcv_dSoC(float s) {
    // Derivada d(V_ocv)/d(SoC) para cálculo da matriz C do Jacobiano
    return 2.40f + 1.20f * s;
}

float BatteryKalmanSoC::update(float v_meas_volts, float i_meas_ma, float dt_seconds) {
    float i_meas_a = i_meas_ma / 1000.0f;

    // -------------------------------------------------------------------------
    // ETAPA 1: PREDICÃO NO TEMPO (Coulomb Counting integrado)
    // x_hat_k^- = x_hat_{k-1} - (dt / Q_total) * I_meas
    // -------------------------------------------------------------------------
    float delta_soc = -(dt_seconds / Q_total_as) * i_meas_a;
    soc += delta_soc;

    // Saturação física
    if (soc > 1.0f) soc = 1.0f;
    if (soc < 0.0f) soc = 0.0f;

    // Propagação da covariância do erro de predição
    P = P + Q_proc;

    // -------------------------------------------------------------------------
    // ETAPA 2: ADAPTABILIDADE DO RUÍDO DE MEDIÇÃO
    // Se a corrente for muito alta ou sofrer transientes bruscos, aumenta R_meas
    // -------------------------------------------------------------------------
    float current_abs = fabsf(i_meas_a);
    float R_k = R_meas + (current_abs * 0.05f);

    // -------------------------------------------------------------------------
    // ETAPA 3: ATUALIZAÇÃO DA MEDIÇÃO (Inovação e Ganho de Kalman)
    // -------------------------------------------------------------------------
    float v_pred = ocvFromSoC(soc) - (i_meas_a * R0_ohm);
    float y_tilde = v_meas_volts - v_pred; // Resíduo da medição

    float C = dOcv_dSoC(soc); // Jacobiano da medição
    float S = (C * P * C) + R_k;
    float K = (P * C) / S; // Ganho ótimo de Kalman

    // Atualização do estado e da covariância
    soc = soc + K * y_tilde;
    P = (1.0f - K * C) * P;

    // Saturação final [0.0, 1.0]
    if (soc > 1.0f) soc = 1.0f;
    if (soc < 0.0f) soc = 0.0f;

    return soc * 100.0f; // Retorna em porcentagem
}
