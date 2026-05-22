import cv2
import numpy as np
import imutils
from imutils import contours

ANCHO_REFERENCIA_CM = 8.56

def ordenar_puntos(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(bl)] if 'bl' in locals() else np.diff(pts, axis=1) # Ajuste rápido
    rect[3] = pts[np.argmax(diff)]
    return rect

def calcular_distancia(p1, p2):
    return np.sqrt(((p2[0] - p1[0]) ** 2) + ((p2[1] - p1[1]) ** 2))

# 1. Cargar la imagen
ruta_imagen = "foto_caja.jpg"  # <-- ASEGÚRATE DE QUE ESTE ARCHIVO ESTÉ EN LA MISMA CARPETA
imagen = cv2.imread(ruta_imagen)

if imagen is None:
    print(f"❌ Error: No se encontró la imagen '{C:\\Users\\rodri\\OneDrive\\Desktop\\hackatec wowwww\\hackatec-2026-nulls\\BackEnd\\modeloCotizarIA\\caja.png}'.")
    exit()

# Redimensionar para que OpenCV no se atranque con fotos de mucha resolución (4K/1080p)
imagen = imutils.resize(imagen, width=800)

# 2. Preprocesamiento más agresivo
gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
difuminado = cv2.GaussianBlur(gris, (7, 7), 0)

# Umbralizado adaptativo (detecta bordes ignorando sombras culeras)
bordes = cv2.Canny(difuminado, 30, 150)
bordes = cv2.dilate(bordes, None, iterations=2)
bordes = cv2.erode(bordes, None, iterations=1)

# 3. Encontrar contornos
cnts = cv2.findContours(bordes.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

print(f"\n[INFO] Objetos totales medio detectados: {len(cnts)}")
print("--- CALCULANDO MEDIDAS ---")

# Filtrar contornos basura por tamaño
contornos_buenos = [c for c in cnts if cv2.contourArea(c) > 1000]

if len(contornos_buenos) < 2:
    print(f"❌ La IA solo detectó {len(contornos_buenos)} objeto(s) claro(s).")
    print("👉 Consejo: Asegúrate de que la tarjeta y la caja contrasten bien con el fondo (ej. mesa oscura, objetos claros).")
    exit()

# Ordenar de izquierda a derecha
(contornos_buenos, _) = contours.sort_contours(contornos_buenos)
pixeles_por_cm = None

for c in contornos_buenos:
    box = cv2.minAreaRect(c)
    box = cv2.boxPoints(box)
    box = np.array(box, dtype="int")

    # Ordenar esquinas: [arriba-izquierda, arriba-derecha, abajo-derecha, abajo-izquierda]
    x_ordenado = box[np.argsort(box[:, 0]), :]
    en_la_izquierda = x_ordenado[:2, :]
    en_la_derecha = x_ordenado[2:, :]

    tl = en_la_izquierda[np.argmin(en_la_izquierda[:, 1]), :]
    bl = en_la_izquierda[np.argmax(en_la_izquierda[:, 1]), :]
    tr = en_la_derecha[np.argmin(en_la_derecha[:, 1]), :]
    br = en_la_derecha[np.argmax(en_la_derecha[:, 1]), :]

    ancho_en_pixeles = calcular_distancia(tl, tr)
    alto_en_pixeles = calcular_distancia(tl, bl)

    if pixeles_por_cm is None:
        pixeles_por_cm = ancho_en_pixeles / ANCHO_REFERENCIA_CM
        print(f"📌 Objeto de referencia (Tarjeta) detectado con éxito.")
        print(f"   Escala: {pixeles_por_cm:.2f} px/cm\n")
        continue

    ancho_real = ancho_en_pixeles / pixeles_por_cm
    alto_real = alto_en_pixeles / pixeles_por_cm

    print(f"📦 ¡Caja detectada!")
    print(f"   Ancho: {ancho_real:.2f} cm")
    print(f"   Alto:  {alto_real:.2f} cm")
    print("--------------------------\n")

print("Proceso terminado. 👍")