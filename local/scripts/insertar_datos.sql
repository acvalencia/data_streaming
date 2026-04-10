USE escalabilidad;

DELIMITER $$

DROP PROCEDURE IF EXISTS insertar_datos$$

CREATE PROCEDURE insertar_datos()
BEGIN
  DECLARE i INT DEFAULT 0;

  WHILE i < 100 DO
    INSERT INTO datos (contenido) VALUES (REPEAT('A', 10000000));
    SET i = i + 1;
  END WHILE;

END$$

DELIMITER ;

-- Ejecutar varias veces:
CALL insertar_datos();
SELECT COUNT(*) AS total_filas FROM datos;