# Mouse Virtual con Dos Manos

Autor: Ing. Edson Denis Zanabria Ticona
Email: ezanabria10@gmail.com

Sistema de control de mouse virtual mediante visión por computadora, reconocimiento de manos y gestos.  
El proyecto permite mover el cursor, hacer clic izquierdo, clic derecho, abrir Microsoft Paint y dibujar usando gestos con ambas manos frente a la cámara.

## Descripción

Este programa utiliza la cámara web para detectar las manos del usuario y convertir ciertos gestos en acciones del mouse.  
La mano derecha se utiliza principalmente para controlar el cursor, mientras que la mano izquierda funciona como activador del modo dibujo.

El sistema está pensado para controlar el mouse sin contacto físico, usando OpenCV, PyAutoGUI y un módulo personalizado de seguimiento de manos.

## Características principales

- Control del cursor con el dedo índice de la mano derecha.
- Clic izquierdo mediante gesto con índice y medio.
- Clic derecho mediante gesto con índice, medio y anular.
- Modo dibujo usando ambas manos.
- Apertura automática de Microsoft Paint con gesto de ambas manos abiertas.
- Suavizado del movimiento del cursor.
- Visualización en pantalla del modo activo.
- Indicador de FPS.
- Área activa delimitada en la ventana de cámara.

## Tecnologías utilizadas

- Python
- OpenCV
- NumPy
- PyAutoGUI
- Módulo personalizado `SeguimientoManos`
- Microsoft Paint

## Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instalado Python y las siguientes librerías:

```bash
pip install opencv-python numpy pyautogui