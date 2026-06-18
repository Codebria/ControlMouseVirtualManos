import cv2
import numpy as np
import pyautogui
import time
import subprocess
from SeguimientoManos import DetectorManos

###########################
# CONFIGURACIÓN
###########################
wCam, hCam = 640, 480
frameR = 100
smoothening = 2  # Reducido para mayor precisión (antes era 5)

# Configuración mejorada para dibujo fluido
BUFFER_SIZE = 5  # Tamaño del buffer para suavizado adicional
posiciones_buffer = []  # Buffer de posiciones para suavizado

###########################
# VARIABLES GLOBALES
###########################
plocX, plocY = 0, 0
clocX, clocY = 0, 0
dibujando = False
paintAbierto = False
paintAbiertoUnaVez = False
ultimo_click = 0  # Control de tiempo entre clicks
INTERVALO_CLICK = 0.005  # Intervalo entre clicks (10ms = muy rápido)

###########################
# INICIALIZACIÓN
###########################
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# Aumentar FPS de la cámara para captura más fluida
cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reducir buffer para menor latencia

detector = DetectorManos(maxManos=2, confianzaSeguimiento=0.8)  # Aumentar confianza
wScr, hScr = pyautogui.size()

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0  # Sin retraso en movimientos
pyautogui.MINIMUM_SLEEP = 0

pTime = 0

print("=" * 60)
print("MOUSE VIRTUAL CON DOS MANOS - SISTEMA AVANZADO")
print("=" * 60)
print(f"Resolución: {wScr}x{hScr}")
print("\n CONTROLES:")
print("\n--- MANO DERECHA (Control del Cursor) ---")
print("   Índice solo: Mover cursor SIN dibujar")
print("   Índice + Medio: Click izquierdo")
print("   Índice + Medio + Anular: Click derecho")
print("\n--- MANO IZQUIERDA (Activador de Dibujo) ---")
print("   Índice solo: Mantener presionado = DIBUJAR ACTIVO")
print("\n--- CÓMO DIBUJAR ---")
print("    1. Levanta índice IZQUIERDO (activa clicks rápidos)")
print("    2. Mueve índice DERECHO (dibuja de forma continua)")
print("    3. Baja índice IZQUIERDO (detiene el dibujo)")
print("\n--- AMBAS MANOS ---")
print("   Ambas abiertas (5 dedos): Abrir Paint")
print("\n  Presiona 'q': Salir")
print("=" * 60)
print("\n TIPS PARA LÍNEAS MÁS FLUIDAS:")
print("  - Mueve la mano LENTAMENTE para mayor precisión")
print("  - Mantén buena iluminación frontal")
print("  - Mantén las manos a 40-60cm de la cámara")
print("  - Si las líneas siguen cortadas, ajusta 'smoothening' en línea 13")
print("=" * 60)

###########################
# FUNCIONES AUXILIARES
###########################

def contarDedos(lmList):
    """Cuenta cuántos dedos están levantados"""
    if len(lmList) == 0:
        return []
    
    dedos = []
    
    # Pulgar
    if lmList[4][1] > lmList[3][1]:
        dedos.append(1)
    else:
        dedos.append(0)
    
    # 4 dedos restantes
    for id in [8, 12, 16, 20]:
        if lmList[id][2] < lmList[id - 2][2]:
            dedos.append(1)
        else:
            dedos.append(0)
    
    return dedos

def identificarMano(lmList):
    """Identifica si es mano derecha o izquierda basándose en posición X"""
    if len(lmList) == 0:
        return None
    
    # Si la muñeca está en la mitad izquierda de la pantalla = mano derecha (efecto espejo)
    # Si está en la mitad derecha = mano izquierda
    munecaX = lmList[0][1]
    
    if munecaX < wCam // 2:
        return "derecha"
    else:
        return "izquierda"

def abrirPaint():
    """Abre Paint y lo maximiza"""
    global paintAbierto, paintAbiertoUnaVez
    
    if not paintAbiertoUnaVez:
        print("\n Abriendo Paint...")
        subprocess.Popen('mspaint.exe')
        time.sleep(2)
        pyautogui.hotkey('win', 'up')
        time.sleep(0.5)
        paintAbierto = True
        paintAbiertoUnaVez = True
        print("Edsn Paint abierto!")

def suavizarPosicion(x, y):
    """Suaviza la posición usando un buffer de posiciones anteriores"""
    global posiciones_buffer
    
    # Agregar nueva posición al buffer
    posiciones_buffer.append((x, y))
    
    # Mantener solo las últimas N posiciones
    if len(posiciones_buffer) > BUFFER_SIZE:
        posiciones_buffer.pop(0)
    
    # Calcular promedio de posiciones
    if len(posiciones_buffer) > 0:
        avg_x = sum(pos[0] for pos in posiciones_buffer) / len(posiciones_buffer)
        avg_y = sum(pos[1] for pos in posiciones_buffer) / len(posiciones_buffer)
        return avg_x, avg_y
    
    return x, y

###########################
# BUCLE PRINCIPAL
###########################
ultimo_click = 0  # Reiniciar variable

while True:
    success, img = cap.read()
    if not success:
        break
    
    # Detectar manos
    img = detector.encontrarManos(img)
    
    # Obtener todas las manos detectadas
    manos = []
    if detector.resultados.multi_hand_landmarks:
        for idx, mano_landmarks in enumerate(detector.resultados.multi_hand_landmarks):
            # Obtener puntos de cada mano
            listaPuntos = []
            alto, ancho, c = img.shape
            
            for id, lm in enumerate(mano_landmarks.landmark):
                cx, cy = int(lm.x * ancho), int(lm.y * alto)
                listaPuntos.append([id, cx, cy])
            
            manos.append(listaPuntos)
    
    # Identificar mano derecha e izquierda
    mano_derecha = None
    mano_izquierda = None
    dedos_derecha = []
    dedos_izquierda = []
    
    for mano in manos:
        tipo = identificarMano(mano)
        if tipo == "derecha":
            mano_derecha = mano
            dedos_derecha = contarDedos(mano)
        elif tipo == "izquierda":
            mano_izquierda = mano
            dedos_izquierda = contarDedos(mano)
    
    # Dibujar área activa
    cv2.rectangle(img, (frameR, frameR), 
                 (wCam - frameR, hCam - frameR),
                 (255, 0, 255), 2)
    
    modo = "ESPERANDO"
    color_modo = (128, 128, 128)
    
    # ============================================
    # GESTO 1: AMBAS MANOS ABIERTAS = ABRIR PAINT
    # ============================================
    if len(dedos_derecha) > 0 and len(dedos_izquierda) > 0:
        if sum(dedos_derecha) >= 4 and sum(dedos_izquierda) >= 4:
            modo = "ABRIENDO PAINT"
            color_modo = (0, 255, 255)
            abrirPaint()
            time.sleep(0.5)
    
    # ============================================
    # PROCESAMIENTO MANO DERECHA
    # ============================================
    if mano_derecha and len(dedos_derecha) > 0:
        x1, y1 = mano_derecha[8][1:]   # Índice
        x2, y2 = mano_derecha[12][1:]  # Medio
        x3, y3 = mano_derecha[16][1:]  # Anular
        
        # Convertir coordenadas con interpolación suave
        x_conv = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y_conv = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        
        # Aplicar suavizado con buffer
        x_suave, y_suave = suavizarPosicion(x_conv, y_conv)
        
        # Suavizar movimiento adicional
        clocX = plocX + (x_suave - plocX) / smoothening
        clocY = plocY + (y_suave - plocY) / smoothening
        
        # ============================================
        # GESTO 2: ÍNDICE IZQUIERDA = ACTIVAR DIBUJO (clicks rápidos)
        #          ÍNDICE DERECHA = CONTROLAR CURSOR Y DIBUJAR
        # ============================================
        if mano_izquierda and len(dedos_izquierda) > 0:
            # Índice izquierda levantado = Activar modo dibujo con clicks rápidos
            if dedos_izquierda[1] == 1 and dedos_izquierda[2] == 0:
                # Si la derecha también tiene índice levantado
                if dedos_derecha[1] == 1 and dedos_derecha[2] == 0:
                    modo = "DIBUJANDO"
                    color_modo = (0, 255, 0)
                    
                    # Mover el cursor de forma continua
                    pyautogui.moveTo(wScr - clocX, clocY, duration=0, _pause=False)
                    
                    # Hacer clicks rápidos continuos
                    tiempo_actual = time.time()
                    if tiempo_actual - ultimo_click >= INTERVALO_CLICK:
                        pyautogui.click(duration=0, _pause=False)
                        ultimo_click = tiempo_actual
                        dibujando = True
                    
                    # Dibujar indicadores visuales
                    cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                    cv2.circle(img, (mano_izquierda[8][1], mano_izquierda[8][2]), 
                              15, (0, 255, 0), cv2.FILLED)
                    
                    # Línea entre ambos índices
                    cv2.line(img, (x1, y1), 
                            (mano_izquierda[8][1], mano_izquierda[8][2]), 
                            (0, 255, 0), 3)
                    
                    # Dibujar rastro pulsante
                    pulso = int(20 + 10 * abs(np.sin(tiempo_actual * 20)))
                    cv2.circle(img, (x1, y1), pulso, (0, 255, 0), 2)
                else:
                    # Si derecha no tiene índice, detener
                    dibujando = False
            else:
                # Si izquierda no tiene índice levantado, detener
                dibujando = False
        
        # ============================================
        # GESTO 3: SOLO ÍNDICE DERECHA (sin izquierda activa) = MOVER CURSOR SIN DIBUJAR
        # ============================================
        if dedos_derecha[1] == 1 and dedos_derecha[2] == 0 and dedos_derecha[3] == 0:
            # Verificar si la mano izquierda NO está con índice levantado
            izquierda_inactiva = True
            if mano_izquierda and len(dedos_izquierda) > 0:
                if dedos_izquierda[1] == 1 and dedos_izquierda[2] == 0:
                    izquierda_inactiva = False
            
            if izquierda_inactiva:
                modo = "MOVER"
                color_modo = (255, 0, 255)
                
                dibujando = False
                
                # Mover cursor sin dibujar
                pyautogui.moveTo(wScr - clocX, clocY, duration=0, _pause=False)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        
        # ============================================
        # GESTO 4: ÍNDICE + MEDIO DERECHA = CLICK IZQUIERDO
        # ============================================
        elif dedos_derecha[1] == 1 and dedos_derecha[2] == 1 and dedos_derecha[3] == 0:
            length = np.hypot(x2 - x1, y2 - y1)
            
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 255, 0), cv2.FILLED)
            
            if length < 40:
                modo = "CLICK IZQ"
                color_modo = (0, 255, 0)
                
                dibujando = False
                
                pyautogui.click()
                cv2.circle(img, ((x1 + x2) // 2, (y1 + y2) // 2), 
                          15, (0, 255, 0), cv2.FILLED)
                time.sleep(0.3)
        
        # ============================================
        # GESTO 5: ÍNDICE + MEDIO + ANULAR DERECHA = CLICK DERECHO
        # ============================================
        elif dedos_derecha[1] == 1 and dedos_derecha[2] == 1 and dedos_derecha[3] == 1:
            dibujando = False
            
            length = np.hypot(x3 - x1, y3 - y1)
            
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
            cv2.line(img, (x2, y2), (x3, y3), (255, 0, 0), 3)
            cv2.line(img, (x3, y3), (x1, y1), (255, 0, 0), 3)
            
            if length < 60:
                modo = "CLICK DER"
                color_modo = (255, 0, 0)
                pyautogui.rightClick()
                time.sleep(0.3)
        
        plocX, plocY = clocX, clocY
    
    # ============================================
    # INDICADOR DE MANO IZQUIERDA
    # ============================================
    if mano_izquierda and len(dedos_izquierda) > 0:
        if dedos_izquierda[1] == 1 and dedos_izquierda[2] == 0:
            x_izq = mano_izquierda[8][1]
            y_izq = mano_izquierda[8][2]
            cv2.circle(img, (x_izq, y_izq), 15, (0, 255, 255), cv2.FILLED)
            cv2.putText(img, "PREP. DIBUJO", (x_izq - 50, y_izq - 20), 
                       cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2)
    
    # Si no hay manos, detener dibujo
    if len(manos) == 0:
        dibujando = False
    
    # ============================================
    # INTERFAZ
    # ============================================
    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), 
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    
    # Modo actual
    cv2.putText(img, f'MODO: {modo}', (20, 430), 
                cv2.FONT_HERSHEY_PLAIN, 2, color_modo, 3)
    
    # Contador de manos
    cv2.putText(img, f'Manos: {len(manos)}', (wCam - 150, 50), 
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    
    # Estado Paint
    if paintAbiertoUnaVez:
        cv2.putText(img, 'PAINT: ON', (wCam - 150, 80), 
                   cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
    
    cv2.imshow("Mouse Virtual Dos Manos", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

###########################
# LIMPIEZA
###########################
dibujando = False

cap.release()
cv2.destroyAllWindows()
print("\n¡Programa finalizado!")