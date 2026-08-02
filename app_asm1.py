import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from motor_asm1 import COMPONENTES, simular_asm1


st.set_page_config(
  page_title="Simulador ASM1",
  layout="wide"
)


PARAMETROS_DEFAULT = {
  "Y_H": 0.67,
  "Y_A": 0.24,
  "f_p": 0.08,
  "i_XB": 0.086,
  "i_XP": 0.06,
  "mu_H": 6.0,
  "K_S": 20.0,
  "K_OH": 0.2,
  "K_NO": 0.5,
  "b_H": 0.62,
  "mu_A": 0.8,
  "K_NH": 1.0,
  "K_OA": 0.4,
  "b_A": 0.15,
  "eta_g": 0.8,
  "k_a": 0.08,
  "k_h": 3.0,
  "K_X": 0.03,
  "eta_h": 0.4
}


INICIALES_DEFAULT = {
  "X_BH": 0.5,
  "X_BA": 0.5,
  "S_S": 125.0,
  "X_S": 250.0,
  "X_P": 0.4,
  "X_ND": 10.0,
  "S_ND": 8.0,
  "S_NH": 30.0,
  "S_NO": 0.5,
  "S_O": 0.1,
  "S_ALK": 0.1
}


PLANTA_DEFAULT = {
  "Q": 18500.0,
  "V": 3999.0,
  "r": 0.1,
  "B_XBH": 1.0,
  "B_XBA": 1.0,
  "B_SS": 1.0,
  "B_XS": 1.0,
  "B_XP": 1.0,
  "B_XND": 1.0,
  "B_SND": 1.0,
  "B_SNH": 1.0,
  "B_SNO": 1.0,
  "B_SO": 1.0
}


INFLUENTE_DEFAULT = {
  "X_BHin": 28.17,
  "X_BAin": 0.0,
  "S_Sin": 65.24,
  "X_Sin": 202.32,
  "X_Pin": 0.0,
  "X_NDin": 10.59,
  "S_NDin": 6.95,
  "S_NHin": 30.14,
  "S_NOin": 0.0,
  "S_Oin": 0.0,
  "S_ALKin": 0.0,
  "KLa": 150.0,
  "SO_sat": 8.0
}


SIMULACION_DEFAULT = {
  "t_inicio": 0.0,
  "t_final": 20.0,
  "dt": 0.01
}


ETIQUETAS = {
  "X_BH": "Biomasa heterótrofa X_BH",
  "X_BA": "Biomasa autótrofa X_BA",
  "S_S": "Sustrato fácilmente biodegradable S_S",
  "X_S": "Sustrato lentamente biodegradable X_S",
  "X_P": "Productos particulados X_P",
  "X_ND": "Nitrógeno orgánico particulado X_ND",
  "S_ND": "Nitrógeno orgánico soluble S_ND",
  "S_NH": "Nitrógeno amoniacal S_NH",
  "S_NO": "Nitrato y nitrito S_NO",
  "S_O": "Oxígeno disuelto S_O",
  "S_ALK": "Alcalinidad S_ALK"
}


UNIDADES = {
  "X_BH": "g DQO/m³",
  "X_BA": "g DQO/m³",
  "S_S": "g DQO/m³",
  "X_S": "g DQO/m³",
  "X_P": "g DQO/m³",
  "X_ND": "g N/m³",
  "S_ND": "g N/m³",
  "S_NH": "g N/m³",
  "S_NO": "g N/m³",
  "S_O": "g O₂/m³",
  "S_ALK": "mol/m³"
}


PARAMETROS_INFO = [
  ("Y_H", "Rendimiento heterótrofo"),
  ("Y_A", "Rendimiento autótrofo"),
  ("f_p", "Fracción de biomasa a productos particulados"),
  ("i_XB", "Nitrógeno por DQO en biomasa"),
  ("i_XP", "Nitrógeno por DQO en productos"),
  ("mu_H", "Crecimiento máximo heterótrofo [1/día]"),
  ("K_S", "Semisaturación de sustrato"),
  ("K_OH", "Semisaturación de O₂ heterótrofa"),
  ("K_NO", "Semisaturación de nitrato"),
  ("b_H", "Decaimiento heterótrofo [1/día]"),
  ("mu_A", "Crecimiento máximo autótrofo [1/día]"),
  ("K_NH", "Semisaturación de amonio"),
  ("K_OA", "Semisaturación de O₂ autótrofa"),
  ("b_A", "Decaimiento autótrofo [1/día]"),
  ("eta_g", "Corrección anóxica del crecimiento"),
  ("k_a", "Tasa de amonificación"),
  ("k_h", "Tasa máxima de hidrólisis"),
  ("K_X", "Semisaturación de hidrólisis"),
  ("eta_h", "Corrección anóxica de hidrólisis")
]


def configuracion_default():
  return {
    "parametros": PARAMETROS_DEFAULT.copy(),
    "iniciales": INICIALES_DEFAULT.copy(),
    "planta": PLANTA_DEFAULT.copy(),
    "influente": INFLUENTE_DEFAULT.copy(),
    "simulacion": SIMULACION_DEFAULT.copy()
  }


def guardar_configuracion_en_estado(configuracion):
  for nombre, valor in configuracion["parametros"].items():
    st.session_state["param_"+nombre] = float(valor)

  for nombre, valor in configuracion["iniciales"].items():
    st.session_state["ini_"+nombre] = float(valor)

  for nombre, valor in configuracion["planta"].items():
    st.session_state["planta_"+nombre] = float(valor)

  for nombre, valor in configuracion["influente"].items():
    st.session_state["in_"+nombre] = float(valor)

  for nombre, valor in configuracion["simulacion"].items():
    st.session_state["sim_"+nombre] = float(valor)


def obtener_configuracion():
  parametros = {
    nombre: st.session_state["param_"+nombre]
    for nombre in PARAMETROS_DEFAULT
  }

  iniciales = {
    nombre: st.session_state["ini_"+nombre]
    for nombre in INICIALES_DEFAULT
  }

  planta = {
    nombre: st.session_state["planta_"+nombre]
    for nombre in PLANTA_DEFAULT
  }

  influente = {
    nombre: st.session_state["in_"+nombre]
    for nombre in INFLUENTE_DEFAULT
  }

  simulacion = {
    nombre: st.session_state["sim_"+nombre]
    for nombre in SIMULACION_DEFAULT
  }

  return {
    "parametros": parametros,
    "iniciales": iniciales,
    "planta": planta,
    "influente": influente,
    "simulacion": simulacion
  }


def validar_configuracion(configuracion):
  secciones = ["parametros", "iniciales", "planta", "influente", "simulacion"]

  for seccion in secciones:
    if seccion not in configuracion:
      raise ValueError("Falta la sección '"+seccion+"' en el archivo")

  for nombre in PARAMETROS_DEFAULT:
    if nombre not in configuracion["parametros"]:
      raise ValueError("Falta el parámetro "+nombre)

  for nombre in INICIALES_DEFAULT:
    if nombre not in configuracion["iniciales"]:
      raise ValueError("Falta la condición inicial "+nombre)

  for nombre in PLANTA_DEFAULT:
    if nombre not in configuracion["planta"]:
      raise ValueError("Falta la condición de planta "+nombre)

  for nombre in INFLUENTE_DEFAULT:
    if nombre not in configuracion["influente"]:
      raise ValueError("Falta el dato de entrada "+nombre)

  for nombre in SIMULACION_DEFAULT:
    if nombre not in configuracion["simulacion"]:
      raise ValueError("Falta el dato de simulación "+nombre)


if "configuracion_iniciada" not in st.session_state:
  guardar_configuracion_en_estado(configuracion_default())
  st.session_state["configuracion_iniciada"] = True


with st.sidebar:
  st.title("ASM1")
  selected = st.radio(
    "Menú",
    ["Información", "Parámetros", "Modelo"]
  )

  st.divider()
  st.subheader("Configuración")

  archivo_config = st.file_uploader(
    "Cargar configuración JSON",
    type=["json"]
  )

  if st.button("Cargar archivo", use_container_width=True):
    if archivo_config is None:
      st.warning("Selecciona un archivo JSON")
    else:
      try:
        configuracion = json.load(archivo_config)
        validar_configuracion(configuracion)
        guardar_configuracion_en_estado(configuracion)
        st.session_state.pop("resultado", None)
        st.success("Configuración cargada")
        st.rerun()
      except Exception as error:
        st.error(str(error))

  if st.button("Restablecer valores", use_container_width=True):
    guardar_configuracion_en_estado(configuracion_default())
    st.session_state.pop("resultado", None)
    st.rerun()

  configuracion_actual = obtener_configuracion()

  st.download_button(
    "Descargar configuración",
    data=json.dumps(configuracion_actual, indent=2),
    file_name="configuracion_asm1.json",
    mime="application/json",
    use_container_width=True
  )


if selected == "Información":
  st.title("Simulador de tratamiento de aguas residuales")
  st.subheader("Activated Sludge Model No. 1 (ASM1)")
  st.markdown(
    "Esta aplicación simula los proceso de oxidación, nitrificación y desnitrificación de materia organica en un reactor de lodos activados mediante un sistema "
    "de once ecuaciones diferenciales. Son considerados procesos de crecimiento y decaimiento "
    "de biomasa, nitrificación, desnitrificación, amonificación, hidrólisis y "
    "transferencia de oxígeno."
  )

  st.info(
    "El modelo se integra con un método BDF para ecuaciones diferenciales ordinarias, el cual es adecuado para este sistema de ecuaciones "
    "diferenciales que es potencialmente rígidos."
  )

  datos_componentes = pd.DataFrame({
    "Componente": COMPONENTES,
    "Descripción": [ETIQUETAS[nombre] for nombre in COMPONENTES],
    "Unidad": [UNIDADES[nombre] for nombre in COMPONENTES]
  })

  st.dataframe(datos_componentes, hide_index=True, use_container_width=True)


if selected == "Parámetros":
  st.title("Parámetros cinéticos y estequiométricos")
  st.caption("Valores predeterminados para ASM1 a 20 °C")

  columnas = st.columns(3)

  for i in range(len(PARAMETROS_INFO)):
    nombre = PARAMETROS_INFO[i][0]
    descripcion = PARAMETROS_INFO[i][1]

    columnas[i % 3].number_input(
      descripcion+" ("+nombre+")",
      min_value=0.0,
      format="%.6f",
      key="param_"+nombre
    )

  st.success("Los cambios se conservan automáticamente durante la sesión")


if selected == "Modelo":
  st.title("Simulación del reactor")

  with st.expander("Condiciones iniciales", expanded=True):
    columnas = st.columns(3)

    for i in range(len(COMPONENTES)):
      nombre = COMPONENTES[i]

      columnas[i % 3].number_input(
        ETIQUETAS[nombre]+" ["+UNIDADES[nombre]+"]",
        min_value=0.0,
        format="%.6f",
        key="ini_"+nombre
      )

  with st.expander("Condiciones de planta", expanded=False):
    col1, col2, col3 = st.columns(3)

    col1.number_input("Caudal Q [m³/día]", min_value=0.0, key="planta_Q")
    col2.number_input("Volumen V [m³]", min_value=0.000001, key="planta_V")
    col3.number_input("Recirculación r", min_value=0.0, key="planta_r")

    factores = [
      ("B_XBH", "Factor X_BH"),
      ("B_XBA", "Factor X_BA"),
      ("B_SS", "Factor S_S"),
      ("B_XS", "Factor X_S"),
      ("B_XP", "Factor X_P"),
      ("B_XND", "Factor X_ND"),
      ("B_SND", "Factor S_ND"),
      ("B_SNH", "Factor S_NH"),
      ("B_SNO", "Factor S_NO"),
      ("B_SO", "Factor S_O")
    ]

    columnas = st.columns(3)

    for i in range(len(factores)):
      nombre = factores[i][0]
      descripcion = factores[i][1]

      columnas[i % 3].number_input(
        descripcion,
        min_value=0.0,
        format="%.6f",
        key="planta_"+nombre
      )

  with st.expander("Concentraciones de entrada", expanded=False):
    entradas = [
      ("X_BHin", "Entrada X_BH"),
      ("X_BAin", "Entrada X_BA"),
      ("S_Sin", "Entrada S_S"),
      ("X_Sin", "Entrada X_S"),
      ("X_Pin", "Entrada X_P"),
      ("X_NDin", "Entrada X_ND"),
      ("S_NDin", "Entrada S_ND"),
      ("S_NHin", "Entrada S_NH"),
      ("S_NOin", "Entrada S_NO"),
      ("S_Oin", "Entrada S_O"),
      ("S_ALKin", "Entrada S_ALK"),
      ("KLa", "Coeficiente KLa [1/día]"),
      ("SO_sat", "Saturación de O₂")
    ]

    columnas = st.columns(3)

    for i in range(len(entradas)):
      nombre = entradas[i][0]
      descripcion = entradas[i][1]

      columnas[i % 3].number_input(
        descripcion,
        min_value=0.0,
        format="%.6f",
        key="in_"+nombre
      )

  with st.expander("Tiempo de simulación", expanded=True):
    col1, col2, col3 = st.columns(3)

    col1.number_input("Tiempo inicial [días]", key="sim_t_inicio")
    col2.number_input("Tiempo final [días]", key="sim_t_final")
    col3.number_input("Paso de salida dt [días]", min_value=0.000001, format="%.6f", key="sim_dt")

  variables = st.multiselect(
    "Variables a graficar",
    options=COMPONENTES,
    default=["X_BH", "S_S", "S_NH", "S_O"],
    format_func=lambda nombre: ETIQUETAS[nombre]
  )

  if st.button("Simular", type="primary", use_container_width=True):
    try:
      configuracion = obtener_configuracion()

      Y0 = np.array([
        configuracion["iniciales"][nombre]
        for nombre in COMPONENTES
      ])

      with st.spinner("Resolviendo el sistema de ecuaciones..."):
        t, resultados = simular_asm1(
          configuracion["simulacion"]["t_inicio"],
          configuracion["simulacion"]["t_final"],
          configuracion["simulacion"]["dt"],
          Y0,
          configuracion["parametros"],
          configuracion["influente"],
          configuracion["planta"]
        )

      tabla = pd.DataFrame(resultados, columns=COMPONENTES)
      tabla.insert(0, "Tiempo", t)

      st.session_state["resultado"] = tabla
      st.success("Simulación completada")

    except Exception as error:
      st.error(str(error))

  if "resultado" in st.session_state:
    tabla = st.session_state["resultado"]

    if len(variables) > 0:
      fig, ax = plt.subplots(figsize=(10, 6))

      for nombre in variables:
        ax.plot(tabla["Tiempo"], tabla[nombre], label=nombre)

      ax.set_xlabel("Tiempo [días]")
      ax.set_ylabel("Concentración")
      ax.set_title("Evolución temporal del modelo ASM1")
      ax.grid(True)
      ax.legend()
      fig.tight_layout()

      st.pyplot(fig)
      plt.close(fig)
    else:
      st.warning("Selecciona al menos una variable para graficar")

    st.subheader("Valores finales")

    valores_finales = pd.DataFrame({
      "Componente": COMPONENTES,
      "Valor final": [tabla[nombre].iloc[-1] for nombre in COMPONENTES],
      "Unidad": [UNIDADES[nombre] for nombre in COMPONENTES]
    })

    st.dataframe(valores_finales, hide_index=True, use_container_width=True)

    st.download_button(
      "Descargar resultados CSV",
      data=tabla.to_csv(index=False),
      file_name="resultados_asm1.csv",
      mime="text/csv"
    )
