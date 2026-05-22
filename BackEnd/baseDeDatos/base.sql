-- Creación de la Base de Datos (Opcional si ya la tienen)
CREATE DATABASE microhub_logistica;
USE microhub_logistica;

-- 1. TABLA DE USUARIOS GENERALES
-- Centraliza las credenciales y datos básicos de cualquier persona en el sistema.
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('VENDEDOR', 'TENDER_HUB', 'RECOLECTOR', 'ADMIN')),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA DE VENDEDORES (Extension de Usuarios)
-- Guarda la información de los emprendedores que envían paquetes.
CREATE TABLE vendedores (
    usuario_id INT PRIMARY KEY,
    nombre_marca VARCHAR(100) NOT NULL,
    nivel_vendedor VARCHAR(20) DEFAULT 'BASICO' CHECK (nivel_vendedor IN ('BASICO', 'PRO')),
    eco_puntos INT DEFAULT 0,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- 3. TABLA DE MICRO-HUBS (Las Tienditas - Extension de Usuarios)
-- Controla la capacidad física y financiera de cada punto de acopio.
CREATE TABLE micro_hubs (
    usuario_id INT PRIMARY KEY,
    nombre_establecimiento VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    capacidad_max_paquetes INT NOT NULL,
    capacidad_actual INT DEFAULT 0,
    estatus VARCHAR(20) DEFAULT 'ACTIVO' CHECK (estatus IN ('ACTIVO', 'SATURADO', 'INACTIVO')),
    billetera_digital_mxn DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- 4. TABLA DE RUTAS DE RECOLECCIÓN
-- Organiza los viajes que hacen las camionetas para vaciar las tienditas.
CREATE TABLE rutas_recoleccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recolector_id INT,
    estatus_ruta VARCHAR(20) DEFAULT 'PROGRAMADA' CHECK (estatus_ruta IN ('PROGRAMADA', 'EN_CURSO', 'FINALIZADA')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recolector_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- 5. TABLA DE PAQUETES (El Corazón del Sistema)
-- Registra las dimensiones de la IA, costos, QR y en qué tiendita física está físicamente el paquete.
CREATE TABLE paquetes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendedor_id INT NOT NULL,
    micro_hub_id INT NOT NULL,
    ruta_id INT DEFAULT NULL, -- Se llena cuando el camión lo asigna a una ruta
    codigo_qr VARCHAR(255) UNIQUE NOT NULL,
    
    -- Dimensiones calculadas por la IA (Cubicaje)
    largo_cm DECIMAL(5,2) NOT NULL,
    ancho_cm DECIMAL(5,2) NOT NULL,
    alto_cm DECIMAL(5,2) NOT NULL,
    peso_kg DECIMAL(5,2) NOT NULL,
    costo_envio DECIMAL(7,2) NOT NULL,
    
    -- Flujo de estados del paquete
    estatus_paquete VARCHAR(30) DEFAULT 'REGISTRADO' 
        CHECK (estatus_paquete IN ('REGISTRADO', 'EN_ACOPIO', 'RECOLECTADO', 'ENTREGADO_FINAL')),
        
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_recibido_hub TIMESTAMP NULL,
    fecha_recolectado TIMESTAMP NULL,
    
    FOREIGN KEY (vendedor_id) REFERENCES vendedores(usuario_id),
    FOREIGN KEY (micro_hub_id) REFERENCES micro_hubs(usuario_id),
    FOREIGN KEY (ruta_id) REFERENCES rutas_recoleccion(id)
);

-- 6. TABLA HISTÓRICA DE RECOMPENSAS
-- Registra los $5 pesos base y los bonos del 10% ganados por las tienditas por cada paquete.
CREATE TABLE recompensas_hub (
    id INT AUTO_INCREMENT PRIMARY KEY,
    micro_hub_id INT NOT NULL,
    paquete_id INT NOT NULL,
    monto_base DECIMAL(5,2) DEFAULT 5.00,
    monto_bono DECIMAL(5,2) DEFAULT 0.00,
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (micro_hub_id) REFERENCES micro_hubs(usuario_id),
    FOREIGN KEY (paquete_id) REFERENCES paquetes(id)
);