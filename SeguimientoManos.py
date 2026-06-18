import cv2
import mediapipe as mp
import time

class DetectorManos:
    def __init__(self, mode=False, maxManos=2, modelComplexity=1, 
                 confianzaDeteccion=0.5, confianzaSeguimiento=0.5):
        """
        Inicializa el detector de manos con MediaPipe
        
        Args:
            mode: Si es False, trata las imágenes como video. Si es True, como imágenes estáticas
            maxManos: Número máximo de manos a detectar
            modelComplexity: Complejidad del modelo (0 o 1)
            confianzaDeteccion: Confianza mínima para la detección
            confianzaSeguimiento: Confianza mínima para el seguimiento
        """
        self.mode = mode
        self.maxManos = maxManos
        self.modelComplexity = modelComplexity
        self.confianzaDeteccion = confianzaDeteccion
        self.confianzaSeguimiento = confianzaSeguimiento
        
        # Inicializar MediaPipe Hands
        self.mpManos = mp.solutions.hands
        self.manos = self.mpManos.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxManos,
            model_complexity=self.modelComplexity,
            min_detection_confidence=self.confianzaDeteccion,
            min_tracking_confidence=self.confianzaSeguimiento
        )
        self.dibujo = mp.solutions.drawing_utils
        
    def encontrarManos(self, img, dibujar=True):
        """
        Detecta las manos en la imagen
        
        Args:
            img: Imagen de entrada (BGR)
            dibujar: Si es True, dibuja las marcas de las manos
            
        Returns:
            Imagen con las manos dibujadas (si dibujar=True)
        """
        # Convertir BGR a RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Procesar la imagen
        self.resultados = self.manos.process(imgRGB)
        
        # Dibujar las manos si se detectaron
        if self.resultados.multi_hand_landmarks:
            for mano in self.resultados.multi_hand_landmarks:
                if dibujar:
                    self.dibujo.draw_landmarks(
                        img, 
                        mano, 
                        self.mpManos.HAND_CONNECTIONS
                    )
        
        return img
    
    def encontrarPosicion(self, img, numeroMano=0, dibujar=True):
        """
        Encuentra la posición de los puntos de referencia de la mano
        
        Args:
            img: Imagen de entrada
            numeroMano: Índice de la mano (0 para la primera mano)
            dibujar: Si es True, dibuja círculos en los puntos
            
        Returns:
            Lista con las posiciones [id, x, y] de cada punto
        """
        listaPuntos = []
        
        if self.resultados.multi_hand_landmarks:
            if numeroMano < len(self.resultados.multi_hand_landmarks):
                miMano = self.resultados.multi_hand_landmarks[numeroMano]
                
                # Obtener dimensiones de la imagen
                alto, ancho, c = img.shape
                
                for id, lm in enumerate(miMano.landmark):
                    # Convertir coordenadas normalizadas a píxeles
                    cx, cy = int(lm.x * ancho), int(lm.y * alto)
                    listaPuntos.append([id, cx, cy])
                    
                    if dibujar:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        
        return listaPuntos


def main():
    """
    Función principal para probar el detector de manos
    """
    # Inicializar captura de video
    cap = cv2.VideoCapture(0)
    
    # Configurar resolución (opcional)
    cap.set(3, 1280)  # Ancho
    cap.set(4, 720)   # Alto
    
    # Crear detector de manos
    detector = DetectorManos()
    
    # Variables para calcular FPS
    tiempoAnterior = 0
    tiempoActual = 0
    
    print("Presiona 'q' para salir")
    
    while True:
        # Leer frame de la cámara
        success, img = cap.read()
        
        if not success:
            print("No se pudo acceder a la cámara")
            break
        
        # Detectar manos
        img = detector.encontrarManos(img)
        
        # Encontrar posiciones de los puntos
        listaPuntos = detector.encontrarPosicion(img)
        
        # Ejemplo: resaltar el dedo índice (punto 8)
        if len(listaPuntos) != 0:
            # Punto 8 es la punta del dedo índice
            cv2.circle(img, (listaPuntos[8][1], listaPuntos[8][2]), 
                      15, (0, 255, 0), cv2.FILLED)
        
        # Calcular FPS
        tiempoActual = time.time()
        fps = 1 / (tiempoActual - tiempoAnterior)
        tiempoAnterior = tiempoActual
        
        # Mostrar FPS en la imagen
        cv2.putText(img, f'FPS: {int(fps)}', (10, 70), 
                   cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        
        # Mostrar imagen
        cv2.imshow("Seguimiento de Manos", img)
        
        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()