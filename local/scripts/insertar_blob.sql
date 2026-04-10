
USE escalabilidad;
CREATE TABLE IF NOT EXISTS datos_blob (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contenido LONGBLOB
);

DELIMITER $$

DROP PROCEDURE IF EXISTS insertar_blob$$
CREATE PROCEDURE insertar_blob()
BEGIN
  DECLARE i INT DEFAULT 0;

  WHILE i < 200 DO
    INSERT INTO datos_blob (contenido)
    VALUES (REPEAT(CONV(FLOOR(RAND() * 999999999), 10, 16), 500000)); -- Datos hexadecimales únicos por fila
    SET i = i + 1;
  END WHILE;

END$$

DELIMITER ;

-- Para ejecutar:
CALL insertar_blob();
SELECT COUNT(*) AS total_filas FROM datos_blob;
