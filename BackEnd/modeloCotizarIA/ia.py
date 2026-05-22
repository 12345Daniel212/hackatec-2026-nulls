import cv2
import numpy as np

# 1. Cargar la imagen
ruta_imagen = "caja.png"  # <-- Asegúrate de cambiar la foto aquí para probar
imagen = cv2.imread(ruta_imagen)

if imagen is None:
    print(f"❌ Error: No se pudo abrir '{ruta_imagen}'.")
    exit()

# Redimensionar a un tamaño fijo para que la escala de píxeles no se vuelva loca
imagen = cv2.resize(imagen, (800, 600))
resultado = imagen.copy()

# 2. Procesamiento de imagen limpio
gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
difuminado = cv2.GaussianBlur(gris, (7, 7), 0)

# Detectar bordes de manera más precisa
bordes = cv2.Canny(difuminado, 50, 150)
bordes = cv2.dilate(bordes, None, iterations=1)
bordes = cv2.erode(bordes, None, iterations=1)

# 3. Encontrar contornos
cnts, _ = cv2.findContours(bordes.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print("\n--- ESCANEANDO OBJETO REAL ---")

caja_encontrada = False

# Ordenar contornos del más grande al más chico
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

for c in cnts:
    # Ignorar cosas muy pequeñas (ruido de fondo)
    if cv2.contourArea(c) < 8000:
        continue

    # --- EL FILTRO INTELIGENTE: Aproximar la forma del objeto ---
    perimetro = cv2.arcLength(c, True)
    aproximacion = cv2.approxPolyDP(c, 0.04 * perimetro, True)

    # Si el objeto tiene exactamente 4 esquinas, ¡ES UN RECTÁNGULO/CUADRADO (UNA CAJA)!
    if len(aproximacion) == 4:
        caja_encontrada = True

        # Obtener las coordenadas de la caja
        x, y, w, h = cv2.boundingRect(aproximacion)

        # Escala matemática real: Ajustada para fotos de celular promedio a distancia normal
        # Unos 22 píxeles equivalen a 1 cm en una pantalla de 800x600
        ESCALA_REAL_PX_CM = 22.0

        ancho_real = w / ESCALA_REAL_PX_CM
        alto_real = h / ESCALA_REAL_PX_CM

        # La profundidad en una foto 2D la estimamos manteniendo la proporción de la caja
        profundidad_real = (ancho_real + alto_real) / 2

        print(f"📦 ¡Caja geométrica detectada!")
        print(f"   --------------------------------------")
        print(f"   Ancho:        {ancho_real:.1f} cm")
        print(f"   Alto:         {alto_real:.1f} cm")
        print(f"   Profundidad:  {profundidad_real:.1f} cm")
        print(f"   Volumen:      {ancho_real * alto_real * profundidad_real:.1f} cm³")
        print(f"   --------------------------------------")

        # Dibujar el rectángulo verde de éxito
        cv2.rectangle(resultado, (x, y), (x + w, y + h), (0, 255, 0), 3)
        cv2.putText(resultado, f"{ancho_real:.1f}x{alto_real:.1f}cm", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        break  # Ya encontramos la caja principal, paramos el ciclo

if not caja_encontrada:
    print("❌ No se detectó ninguna caja.")
    print("👉 El objeto en la foto no tiene forma rectangular o cuadrada clara.")

# Guardar lo que calculó
cv2.imwrite("ia_resultado.png", resultado)
print("\nProceso terminado. 👍")