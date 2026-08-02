# Simulador ASM1 para tratamiento de aguas residuales

Aplicación interactiva en Python para explorar la evolución temporal de distintas concentraciones en un reactor de lodos activados, mediante una implementación simplificada inspirada en el **Activated Sludge Model No. 1 (ASM1)**.

> **Demo en Streamlit:** [Abrir la aplicación](https://tu-app.streamlit.app)  
> Reemplaza este enlace por la dirección pública de la aplicación una vez desplegada.

> [!IMPORTANT]
> Este repositorio corresponde a un **prototipo académico** desarrollado originalmente durante una práctica profesional en 2023 y reorganizado posteriormente para facilitar su ejecución. No es una implementación oficial de la IWA ni una herramienta validada para diseñar u operar plantas reales.

## Descripción del problema

Los sistemas de lodos activados utilizan comunidades microbianas para remover materia orgánica y compuestos nitrogenados presentes en aguas residuales. Su comportamiento depende de procesos acoplados como:

- crecimiento y decaimiento de biomasa heterótrofa;
- crecimiento y decaimiento de biomasa autótrofa;
- consumo de sustrato orgánico;
- nitrificación y desnitrificación;
- amonificación;
- hidrólisis de materia particulada;
- transferencia de oxígeno al reactor.

El objetivo de esta aplicación es resolver numéricamente un sistema dinámico que representa estos procesos en un **reactor de mezcla completa**. El usuario puede modificar parámetros cinéticos y estequiométricos, condiciones iniciales, concentraciones del afluente, condiciones operacionales y el intervalo de simulación.

La aplicación permite:

- cargar y descargar configuraciones en formato JSON;
- ejecutar la simulación desde una interfaz Streamlit;
- seleccionar las variables que se desean visualizar;
- explorar los resultados mediante gráficos interactivos;
- descargar las trayectorias simuladas en formato CSV.

## Variables de estado

La implementación utiliza once variables dinámicas:

| Variable | Descripción | Unidad usada en la aplicación |
|---|---|---:|
| `X_BH` | Biomasa heterótrofa | g DQO/m³ |
| `X_BA` | Biomasa autótrofa | g DQO/m³ |
| `S_S` | Sustrato fácilmente biodegradable | g DQO/m³ |
| `X_S` | Sustrato lentamente biodegradable | g DQO/m³ |
| `X_P` | Productos particulados del decaimiento | g DQO/m³ |
| `X_ND` | Nitrógeno orgánico particulado biodegradable | g N/m³ |
| `S_ND` | Nitrógeno orgánico soluble biodegradable | g N/m³ |
| `S_NH` | Nitrógeno amoniacal soluble | g N/m³ |
| `S_NO` | Nitrato y nitrito soluble | g N/m³ |
| `S_O` | Oxígeno disuelto | g O₂/m³ |
| `S_ALK` | Alcalinidad | unidad molar empleada por la interfaz |

El ASM1 original también considera componentes inertes como `S_I` y `X_I`. Esta versión no los incorpora como estados dinámicos porque no participan en las reacciones implementadas.

## Estructura general del modelo

Sea

$$
Y(t)=
\begin{pmatrix}
X_{BH} & X_{BA} & S_S & X_S & X_P & X_{ND} & S_{ND} & S_{NH} & S_{NO} & S_O & S_{ALK}
\end{pmatrix}^{\!T}.
$$

Para la mayoría de las componentes, el balance implementado tiene la estructura

$$
\frac{dY_i}{dt}
=
D\left(Y_{i,\mathrm{in}}-Y_i\right)
+rD\left(B_i-1\right)Y_i
+\sum_{j=1}^{8}\nu_{ij}\rho_j
+a_i(Y),
$$

con

$$
D=\frac{Q}{V},
$$

siendo:

- $Q$ el caudal de entrada;
- $V$ el volumen del reactor;
- $r$ un factor de recirculación;
- $B_i$ un factor de concentración asociado a la recirculación;
- $\nu_{ij}$ los coeficientes estequiométricos;
- $\rho_j$ las tasas de los procesos biológicos;
- $a_i(Y)$ un término adicional, como la transferencia de oxígeno.

Para el oxígeno disuelto se incorpora el término de aireación

$$
a_{S_O}(Y)=K_La\left(S_{O,\mathrm{sat}}-S_O\right).
$$

### Tasas de proceso

Para abreviar las expresiones se define

$$
q(A,B)=\frac{A}{A+B}.
$$

Las tasas utilizadas por el motor numérico son:

$$
\rho_1=
\mu_H q(S_S,K_S)q(S_O,K_{OH})X_{BH},
$$

$$
\rho_2=
\eta_g\mu_H q(S_S,K_S)q(K_{OH},S_O)q(S_{NO},K_{NO})X_{BH},
$$

$$
\rho_3=
\mu_Aq(S_{NH},K_{NH})q(S_O,K_{OA})X_{BA},
$$

$$
\rho_4=b_HX_{BH},
\qquad
\rho_5=b_AX_{BA},
$$

$$
\rho_6=k_aS_{ND}X_{BH},
$$

$$
\rho_7=
k_hq\!\left(\frac{X_S}{X_{BH}},K_X\right)
\left[
q(S_O,K_{OH})+
\eta_hq(K_{OH},S_O)q(S_{NO},K_{NO})
\right]X_{BH},
$$

$$
\rho_8=\rho_7\frac{X_{ND}}{X_S}.
$$

Estas tasas representan, respectivamente, crecimiento heterótrofo aeróbico, crecimiento heterótrofo anóxico, crecimiento autótrofo, decaimiento de ambas biomasas, amonificación, hidrólisis de sustrato particulado e hidrólisis asociada al nitrógeno orgánico particulado.

Las once ecuaciones completas y sus coeficientes se encuentran en [`motor_asm1.py`](motor_asm1.py).

## Método numérico

El sistema se resuelve con `scipy.integrate.solve_ivp` utilizando el método **BDF** (*Backward Differentiation Formula*):

```python
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
```

BDF es un método implícito apropiado para sistemas de ecuaciones diferenciales que pueden presentar rigidez numérica. El integrador utiliza pasos internos adaptativos; el valor `dt` ingresado en la interfaz determina la malla en la que se entregan y muestran los resultados, no un paso fijo interno del método.

Para evitar evaluaciones indefinidas, el código protege divisiones cercanas a cero. Además, las concentraciones negativas producidas por errores numéricos pequeños se truncan a cero. Esta última medida es una protección computacional y no reemplaza un análisis matemático de positividad del sistema.

## Estructura del proyecto

```text
.
├── app_asm1.py              # Interfaz web con Streamlit y Plotly
├── motor_asm1.py            # Sistema de EDO y solución numérica
├── configuracion_asm1.json  # Ejemplo de configuración inicial
├── requirements.txt         # Dependencias de Python
└── README.md
```

## Ejecución local

### Windows PowerShell

Desde la carpeta del proyecto:

```powershell
py -m venv .venv
```

No es necesario activar el entorno virtual. Las dependencias pueden instalarse directamente con:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Luego ejecuta:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app_asm1.py
```

La aplicación debería abrirse en:

```text
http://localhost:8501
```

### Linux o macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app_asm1.py
```

## Uso de la aplicación

1. En **Parámetros**, modifica los valores cinéticos y estequiométricos.
2. En **Modelo**, define las condiciones iniciales, las condiciones de planta y las concentraciones del afluente.
3. Selecciona el horizonte temporal y el paso de salida.
4. Escoge las variables que deseas visualizar.
5. Presiona **Simular**.
6. Utiliza las herramientas del gráfico para hacer zoom, desplazarte y consultar valores.
7. Descarga la configuración en JSON o los resultados en CSV cuando sea necesario.

## Enlace a Streamlit

Una vez desplegado el repositorio, reemplaza el enlace de ejemplo por la URL pública:

```markdown
[Demo en Streamlit](https://tu-app.streamlit.app)
```

## Supuestos y limitaciones

- Es una implementación **simplificada e inspirada en ASM1**, no una reproducción certificada del modelo de referencia de la IWA.
- Representa un único reactor de mezcla completa con volumen constante.
- El caudal, el afluente, los parámetros y las condiciones operacionales permanecen constantes durante cada simulación.
- La recirculación se representa mediante un factor global `r` y factores de concentración `B_i`; no se modela explícitamente una red hidráulica completa.
- No se incluye un sedimentador secundario, balances de sólidos detallados, edad del lodo ni múltiples reactores conectados.
- No se modelan fósforo, temperatura variable, pH, toxicidad, inhibiciones adicionales ni transferencia de otros gases.
- Los componentes inertes `S_I` y `X_I` no forman parte del vector de estados.
- La versión reorganizada no incluye cargas puntuales o afluentes variables en el tiempo.
- Los valores predeterminados son ilustrativos y no han sido calibrados ni validados con datos de una planta específica.
- El truncamiento de concentraciones negativas es una salvaguarda numérica y puede ocultar configuraciones físicamente inconsistentes.
- La aplicación no debe utilizarse para decisiones de diseño, operación o cumplimiento normativo sin una revisión técnica especializada y una validación independiente.

## Contexto del proyecto

El prototipo original fue desarrollado en 2023 durante una práctica básica relacionada con tratamiento de aguas residuales. El objetivo era familiarizarse con Streamlit, implementar una primera plantilla para simular un proceso de lodos activados y visualizar la evolución de sus componentes.

La versión publicada en este repositorio conserva esa idea inicial, pero reorganiza el código, elimina dependencias innecesarias, concentra la configuración en un archivo JSON y utiliza una interfaz y un integrador numérico más fáciles de mantener.

## Tecnologías utilizadas

- Python
- NumPy
- SciPy
- Pandas
- Streamlit
- Plotly

## Referencia de base

Henze, M., Gujer, W., Mino, T. y van Loosdrecht, M. (2006). *Activated Sludge Models ASM1, ASM2, ASM2d and ASM3*. IWA Publishing.

## Autor

**Cristóbal Reyes**  
Código original desarrollado durante una práctica básica en 2023.
