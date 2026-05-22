import cv2
import numpy as np
import imutils
from imutils import contours

# =====================================================================
# CONFIGURACIÓN: El ancho de tu objeto de referencia en la vida real
# En este caso, una tarjeta de crédito mide exactamente 8.56 cm de ancho
# =====================================================================
ANCHO_REFERENCIA_CM = 8.56

def ordenar_puntos(pts):
    # Ordena los puntos del contorno: arriba-izquierda, arriba-derecha, abajo-derecha, abajo-izquierda
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def calcular_distancia(p1, p2):
    return np.sqrt(((p2[0] - p1[0]) ** 2) + ((p2[1] - p1[1]) ** 2))

# 1. Cargar la imagen
ruta_imagen = "foto_caja.jpg"  # <-- CAMBIA ESTO por el nombre de tu foto
imagen = cv2.imread(ruta_imagen)

if imagen is None:
    print(f"❌ Error: No se pudo encontrar o abrir la imagen '{ruta_imagen}'. ¡Revisa el nombre!")
    exit()

# 2. Preprocesamiento para detectar bordes
gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
difuminado = cv2.GaussianBlur(gris, (7, 7), 0)
bordes = cv2.Canny(difuminado, 50, 100)
bordes = cv2.dilate(bordes, None, iterations=1)
bordes = cv2.erode(bordes, None, iterations=1)

# 3. Encontrar contornos en la imagen
cnts = cv2.findContours(bordes.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

if len(cnts) < 2:
    print("❌ Error: No se detectaron suficientes objetos. Necesito al menos la tarjeta y la caja.")
    exit()

# Ordenar los contornos de izquierda a derecha
(cnts, _) = contours.sort_contours(cnts)
pixeles_por_cm = None

print("\n--- CALCULANDO MEDIDAS ---")

# 4. Analizar los objetos detectados
for i, c in enumerate(cnts):
    # Ignorar contornos demasiado pequeños (ruido en la foto)
    if cv2.contourArea(c) < 500:
        continue

    # Calcular la caja delimitadora del objeto
    orig = imagen.copy()
    box = cv2.minAreaRect(c)
    box = cv2.boxPoints(box)
    box = np.array(box, dtype="int")
    box = ordenar_puntos(box)

    # Puntos para medir ancho (arriba-izquierda a arriba-derecha)
    (tl, tr, br, bl) = box
    ancho_en_pixeles = calcular_distancia(tl, tr)
    alto_en_pixeles = calcular_distancia(tl, bl)

    # Si es el PRIMER objeto de la izquierda, asumimos que es la tarjeta de referencia
    if pixeles_por_cm is None:
        pixeles_por_cm = ancho_en_pixeles / ANCHO_REFERENCIA_CM
        print(f"📌 Objeto de referencia (Tarjeta) detectado.")
        print(f"   Escala calculada: {pixeles_por_cm:.2f} píxeles por cm.\n")
        continue

    # Para los siguientes objetos (la caja), calculamos el tamaño real usando la escala
    ancho_real = ancho_en_pixeles / pixeles_por_cm
    alto_real = alto_en_pixeles / pixeles_por_cm

    print(f"📦 ¡Caja detectada!")
    print(f"   Ancho: {ancho_real:.2f} cm")
    print(f"   Alto:  {alto_real:.2f} cm")
    print("--------------------------\n")

print("Proceso terminado con éxito. 👍")ia 