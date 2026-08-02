# Simulador ASM1

Aplicación web desarrollada en Python y Streamlit para simular, de forma simplificada, la evolución de distintas variables de un sistema de tratamiento de aguas residuales por lodos activados.

🔗 **Demo:** [Abrir aplicación en Streamlit](https://tu-app.streamlit.app)

## ¿Qué permite hacer?

- Modificar parámetros del modelo.
- Definir condiciones iniciales y datos de entrada.
- Simular la evolución temporal del sistema.
- Visualizar los resultados en gráficos interactivos.
- Descargar configuraciones y resultados.

## Modelo utilizado

El proyecto está basado en una versión simplificada del modelo **ASM1 (Activated Sludge Model No. 1)**.

Se consideran variables asociadas a:

- biomasa heterótrofa y autótrofa;
- materia orgánica biodegradable;
- nitrógeno amoniacal, orgánico y nitratos;
- oxígeno disuelto;
- alcalinidad.

La estructura general del sistema es:

```text
dY/dt = entradas y salidas + recirculación + reacciones biológicas + aireación
```

Las ecuaciones completas están implementadas en `motor_asm1.py`.

## Método numérico

El sistema de ecuaciones diferenciales se resuelve con:

```python
scipy.integrate.solve_ivp(..., method="BDF")
```

Se utiliza BDF porque este tipo de modelos puede presentar rigidez numérica.

## Ejecución local

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app_asm1.py
```

La aplicación se abrirá normalmente en:

```text
http://localhost:8501
```

## Archivos principales

```text
app_asm1.py              Interfaz de la aplicación
motor_asm1.py            Modelo y solución numérica
configuracion_asm1.json  Configuración inicial
requirements.txt         Dependencias
```

## Limitaciones

- Es un prototipo académico y no una herramienta para diseño u operación real de plantas.
- El modelo implementado es una simplificación de ASM1.
- Se considera un reactor de mezcla completa.
- No incluye sedimentador secundario ni calibración con datos reales.
- Los resultados dependen de los parámetros ingresados.

## Tecnologías

Python, NumPy, SciPy, Pandas, Streamlit y Plotly.

## Contexto

Proyecto desarrollado originalmente durante una práctica profesional y reorganizado posteriormente para mejorar su ejecución y presentación.
