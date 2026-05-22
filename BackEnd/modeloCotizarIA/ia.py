import cv2
import imutils

# 1. Cargar la imagen
image = cv2.imread("foto_caja.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (7, 7), 0)

# 2. Detectar bordes
edged = cv2.Canny(blur, 50, 100)
edged = cv2.dilate(edged, None, iterations=1)
edged = cv2.erode(edged, None, iterations=1)

# 3. Encontrar los contornos de la caja
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

# Aquí programarías la lógica para medir los píxeles del contorno más grande (la caja)
print(f"Se encontraron {len(cnts)} objetos en la foto.")