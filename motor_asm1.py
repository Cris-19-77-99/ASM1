import numpy as np
from scipy.integrate import solve_ivp


COMPONENTES = [
  "X_BH", "X_BA", "S_S", "X_S", "X_P", "X_ND",
  "S_ND", "S_NH", "S_NO", "S_O", "S_ALK"
]


def q(A, B):
  denominador = A+B
  if abs(denominador) < 1e-12:
    return 0.0
  return A/denominador


def modelo_asm1(t, Y, parametros, influente, planta):
  Y_H = parametros["Y_H"]
  Y_A = parametros["Y_A"]
  f_p = parametros["f_p"]
  i_XB = parametros["i_XB"]
  i_XP = parametros["i_XP"]
  mu_H = parametros["mu_H"]
  K_S = parametros["K_S"]
  K_OH = parametros["K_OH"]
  K_NO = parametros["K_NO"]
  b_H = parametros["b_H"]
  mu_A = parametros["mu_A"]
  K_NH = parametros["K_NH"]
  K_OA = parametros["K_OA"]
  b_A = parametros["b_A"]
  eta_g = parametros["eta_g"]
  k_a = parametros["k_a"]
  k_h = parametros["k_h"]
  K_X = parametros["K_X"]
  eta_h = parametros["eta_h"]

  X_BHin = influente["X_BHin"]
  X_BAin = influente["X_BAin"]
  S_Sin = influente["S_Sin"]
  X_Sin = influente["X_Sin"]
  X_Pin = influente["X_Pin"]
  X_NDin = influente["X_NDin"]
  S_NDin = influente["S_NDin"]
  S_NHin = influente["S_NHin"]
  S_NOin = influente["S_NOin"]
  S_Oin = influente["S_Oin"]
  S_ALKin = influente["S_ALKin"]
  KLa = influente["KLa"]
  SO_sat = influente["SO_sat"]

  Q = planta["Q"]
  V = planta["V"]
  r = planta["r"]
  B_XBH = planta["B_XBH"]
  B_XBA = planta["B_XBA"]
  B_SS = planta["B_SS"]
  B_XS = planta["B_XS"]
  B_XP = planta["B_XP"]
  B_XND = planta["B_XND"]
  B_SND = planta["B_SND"]
  B_SNH = planta["B_SNH"]
  B_SNO = planta["B_SNO"]
  B_SO = planta["B_SO"]

  X_BH = max(Y[0], 0.0)
  X_BA = max(Y[1], 0.0)
  S_S = max(Y[2], 0.0)
  X_S = max(Y[3], 0.0)
  X_P = max(Y[4], 0.0)
  X_ND = max(Y[5], 0.0)
  S_ND = max(Y[6], 0.0)
  S_NH = max(Y[7], 0.0)
  S_NO = max(Y[8], 0.0)
  S_O = max(Y[9], 0.0)
  S_ALK = Y[10]

  D_h = Q/V

  ro_1 = mu_H*q(S_S, K_S)*q(S_O, K_OH)*X_BH
  ro_2 = eta_g*mu_H*q(S_S, K_S)*q(K_OH, S_O)*q(S_NO, K_NO)*X_BH
  ro_3 = mu_A*q(S_NH, K_NH)*q(S_O, K_OA)*X_BA
  ro_4 = b_H*X_BH
  ro_5 = b_A*X_BA
  ro_6 = k_a*S_ND*X_BH

  razon_hidrolisis = X_S/max(X_BH, 1e-12)
  ro_7 = k_h*q(razon_hidrolisis, K_X)*(q(S_O, K_OH)+eta_h*q(K_OH, S_O)*q(S_NO, K_NO))*X_BH
  ro_8 = ro_7*X_ND/max(X_S, 1e-12)

  dF = np.array([
    D_h*(X_BHin-X_BH)+r*D_h*(B_XBH-1)*X_BH+ro_1+ro_2-ro_4,
    D_h*(X_BAin-X_BA)+r*D_h*(B_XBA-1)*X_BA+ro_3-ro_5,
    D_h*(S_Sin-S_S)+r*D_h*(B_SS-1)*S_S-(ro_1+ro_2)/Y_H+ro_7,
    D_h*(X_Sin-X_S)+r*D_h*(B_XS-1)*X_S+(1-f_p)*(ro_4+ro_5)-ro_7,
    D_h*(X_Pin-X_P)+r*D_h*(B_XP-1)*X_P+f_p*(ro_4+ro_5),
    D_h*(X_NDin-X_ND)+r*D_h*(B_XND-1)*X_ND+(i_XB-f_p*i_XP)*(ro_4+ro_5)-ro_8,
    D_h*(S_NDin-S_ND)+r*D_h*(B_SND-1)*S_ND-ro_6+ro_8,
    D_h*(S_NHin-S_NH)+r*D_h*(B_SNH-1)*S_NH-i_XB*(ro_1+ro_2)-(i_XB+1/Y_A)*ro_3+ro_6,
    D_h*(S_NOin-S_NO)+r*D_h*(B_SNO-1)*S_NO-(1-Y_H)/(2.86*Y_H)*ro_2+ro_3/Y_A,
    D_h*(S_Oin-S_O)+r*D_h*(B_SO-1)*S_O-(1-Y_H)/Y_H*ro_1-(4.57-Y_A)/Y_A*ro_3+KLa*(SO_sat-S_O),
    D_h*(S_ALKin-S_ALK)-i_XB*ro_1/14+((1-Y_H)/(14*2.86*Y_H)-i_XB/14)*ro_2+(i_XB/14-1/(7*Y_A))*ro_3+ro_6/14
  ])

  return dF


def simular_asm1(t_inicio, t_final, dt, Y0, parametros, influente, planta):
  if t_final <= t_inicio:
    raise ValueError("El tiempo final debe ser mayor que el tiempo inicial")

  if dt <= 0:
    raise ValueError("El paso de tiempo debe ser positivo")

  if planta["V"] <= 0:
    raise ValueError("El volumen del reactor debe ser positivo")

  if planta["Q"] < 0:
    raise ValueError("El caudal no puede ser negativo")

  Y0 = np.asarray(Y0, dtype=float)

  if Y0.size != len(COMPONENTES):
    raise ValueError("La condición inicial debe contener 11 componentes")

  if np.any(Y0 < 0):
    raise ValueError("Las concentraciones iniciales no pueden ser negativas")

  t = np.arange(t_inicio, t_final+0.5*dt, dt)

  if t[-1] < t_final:
    t = np.append(t, t_final)
  else:
    t[-1] = t_final

  sol = solve_ivp(
    modelo_asm1,
    (t_inicio, t_final),
    Y0,
    t_eval=t,
    args=(parametros, influente, planta),
    method="BDF",
    rtol=1e-6,
    atol=1e-8
  )

  if not sol.success:
    raise RuntimeError("No fue posible completar la simulación: "+sol.message)

  resultados = sol.y.T
  resultados[:, 0:10] = np.maximum(resultados[:, 0:10], 0)

  return sol.t, resultados
