CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    avatar_color VARCHAR(7) NOT NULL
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    fecha DATE NOT NULL,
    status CHAR(1) NOT NULL, -- 'P' (Presente) o 'A' (Ausente)
    UNIQUE KEY student_date (student_id, fecha), -- Clave única para evitar duplicados
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Datos de ejemplo
INSERT INTO students (nombre, apellido, avatar_color) VALUES
('Juan', 'Pérez', '#3b82f6'),
('María', 'García', '#10b981'),
('Carlos', 'López', '#f59e0b'),
('Ana', 'Rodríguez', '#ec4899'),
('Pedro', 'Martínez', '#6366f1'),
('Laura', 'Sánchez', '#ef4444');
