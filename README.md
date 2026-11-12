# U4ACT02 RESTCONF with Python

Práctica de RESTCONF con Python y Tkinter para Catalyst 8000v.

## Archivos

- `lab2.5.py`: consulta RESTCONF GET y muestra la respuesta JSON.
- `lab2.5_part2.py`: crea o actualiza Loopback99 mediante PUT.
- `restconf_gui.py`: cliente Tkinter con consulta GET, formulario PUT, eliminación DELETE con confirmación y barra de estado.
- `U4ACT02 RESTCONF with Python Aza.docx`: informe con capturas y respuestas de reflexión.
- `evidence/`: capturas de las operaciones y estados de la interfaz.

## Ejecución

Requiere Python 3.x y `requests`; Tkinter viene con la instalación de Python. Ejecuta con `py -3.14 restconf_gui.py` y escribe las credenciales del sandbox directamente en la ventana. La contraseña no está guardada en el código.
