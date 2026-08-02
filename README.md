# Simulador ASM1

Desarrollado en Python y Streamlit para simular de forma simplificada la evolución de distintas variables de un sistema de tratamiento de aguas residuales por lodos activados.

**Demo:** [Abrir aplicación en Streamlit](https://ejemploasm1.streamlit.app/)

La app permite:

- Modificar parámetros del modelo.
- Definir condiciones iniciales y datos de entrada.
- Simular la evolución temporal del sistema.
- Visualizar los resultados en gráficos.
- Descargar configuraciones y resultados.

Esta aplicación se basa en una versión simplificada del modelo **ASM1 (Activated Sludge Model No. 1)**. 
Aquí la estructura general del sistema es:

```text
dY/dt = entradas y salidas + recirculación + reacciones biológicas + aireación
```
