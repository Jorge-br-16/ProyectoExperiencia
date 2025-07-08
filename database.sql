-- Crear base de datos
CREATE DATABASE IF NOT EXISTS colegio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE colegio;

-- Crear tabla de inscripciones
CREATE TABLE IF NOT EXISTS inscripciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    grado VARCHAR(10) NOT NULL,
    ano_escolar VARCHAR(10) NOT NULL,
    padre_nombres VARCHAR(150),
    madre_nombres VARCHAR(150),
    padre_telefono VARCHAR(20),
    madre_telefono VARCHAR(20),
    email_padre VARCHAR(100),
    email_madre VARCHAR(100),
    direccion TEXT,
    profesion VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_fecha_registro (fecha_registro),
    INDEX idx_nombres (nombres, apellidos)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;