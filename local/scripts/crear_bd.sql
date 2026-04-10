CREATE DATABASE escalabilidad;
USE escalabilidad;
CREATE TABLE datos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contenido TEXT
);
INSERT INTO datos (contenido) VALUES (REPEAT('A', 10000000));
SELECT * FROM escalabilidad.datos;