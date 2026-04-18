## a) Un usuario inicia sesión en una aplicación.

¿Es un evento? ¿Por qué?
evento, es un suceso que ocurre en un momento determinado, en este caso, el inicio de sesión de un usuario en una aplicación. un que se puede procesar en un backend, que genera un timestamp, un id de usuario, un id de sesion, un id de aplicacion, un id de evento, un tipo de evento, un estado, un mensaje, un id de transaccion, un id de usuario, un id de sesion, un id de aplicacion, un id de evento, un tipo de evento, un estado, un mensaje, un id de transaccion,

¿Qué información mínima debería contener? (Represéntala en formato JSON)
{
"timestamp": "2022-01-01T00:00:00Z",
"user_id": "1234567890",
"session_id": "1234567890",
"app_id": "1234567890",
"event_id": "1234567890",
"event_type": "login",
"status": "success",
"message": "User logged in successfully",
"transaction_id": "1234567890"
}

¿Requiere reacción inmediata o puede procesarse más tarde?
debe procesarse inmediatamente, ya que el usuario espera una respuesta inmediata. los usuarios no deben esperar a que se procese su solicitud.

## b) Un sensor reporta una temperatura cada segundo.

• ¿Es un evento? ¿Por qué?
es un evento, es inmutable, genera informacion basada en un momento de tiempo especifico, debe tratarse como un evento

• ¿Qué información mínima debería contener? (Represéntala en formato JSON)
{
"timestamp": "2022-01-01T00:00:00Z",
"sensor_id": "1234567890",
"temperature": "25",
"unit": "C",
"event_id": "1234567890",
"event_type": "temperature",
"status": "success",
"message": "Temperature reading",
"transaction_id": "1234567890"
}

• ¿Requiere reacción inmediata o puede procesarse más tarde?
debe procesarse inmediatamente, ya que el sensor puede estar en un sistema critico y se requiere reaccionar a cambios en la temperatura.

## c) Un cliente realiza una compra.

• ¿Es un evento? ¿Por qué?
Es un evento, una compra debe manejarse como un evento, enviarse a una cola de eventos,

• ¿Qué información mínima debería contener? (Represéntala en formato JSON)
{
"timestamp": "2022-01-01T00:00:00Z",
"user_id": "1234567890",
"session_id": "1234567890",
"app_id": "1234567890",
"event_id": "1234567890",
"event_type": "purchase",
"status": "success",
"message": "Purchase completed successfully",
"transaction_id": "1234567890"
}

• ¿Requiere reacción inmediata o puede procesarse más tarde?
Inmediata, el usuario espera una respuesta inmediata.

## d) Una tarjeta es rechazada por posible fraude.

• ¿Es un evento? ¿Por qué?

- Ocurre en un momento específico en el tiempo (timestamp puntual): el rechazo sucede en un instante determinado durante el intento de transacción.
- Es inmutable: una vez que la tarjeta fue rechazada, ese hecho no puede cambiarse; queda registrado como un suceso histórico.
- Representa un cambio de estado: la transacción pasa de "en proceso" a "rechazada por sospecha de fraude".
- Tiene relevancia de negocio: dispara reacciones en múltiples sistemas (notificación al cliente, alerta al equipo antifraude, bloqueo preventivo de la tarjeta, registro en auditoría).
- Es de naturaleza crítica y accionable: otros servicios (seguridad, notificaciones, CRM) necesitan reaccionar ante él, lo que lo hace un candidato ideal para ser publicado en una cola/stream de eventos
  y procesado por múltiples consumidores.

• ¿Qué información mínima debería contener? (Represéntala en formato JSON)
{
"timestamp": "2022-01-01T00:00:00Z",
"user_id": "1234567890",
"session_id": "1234567890",
"app_id": "1234567890",
"event_id": "1234567890",
"event_type": "card_declined",
"status": "declined",
"message": "Card declined due to possible fraud",
"transaction_id": "1234567890"
}

• ¿Requiere reacción inmediata o puede procesarse más tarde?
Inmediata, el usuario espera una respuesta inmediata.

## e) Un archivo es subido a un sistema.

• ¿Es un evento? ¿Por qué?
servicios como AWS S3, Azure Blob Storage y Google Cloud Storage emiten eventos nativos de tipo ObjectCreated/BlobCreated precisamente porque  
 la subida de archivos es el ejemplo canónico de un evento que debe propagarse a múltiples consumidores desacoplados.

• ¿Qué información mínima debería contener? (Represéntala en formato JSON)
{  
 "event_id": "evt_9f8a7b6c5d4e",  
 "event_type": "file.uploaded",  
 "timestamp": "2026-04-17T14:23:45Z",  
 "user_id": "usr_1234567890",  
 "session_id": "sess_abcdef123456",  
 "file": {  
 "file_id": "file_0987654321",  
 "name": "reporte_ventas_q1.pdf",  
 "size_bytes": 2458624,  
 "mime_type": "application/pdf",
"checksum": "sha256:3a7bd3e2360a3d29eea436fcfb7e44c735d117c42d1c1835420b6b9942dd4f1b",  
 "storage_path": "s3://mi-bucket/uploads/2026/04/17/file_0987654321.pdf"  
 },  
 "source": {  
 "ip_address": "192.168.1.45",  
 "user_agent": "Mozilla/5.0",  
 "app_id": "web-portal"  
 },
"status": "success"  
 }

• ¿Requiere reacción inmediata o puede procesarse más tarde?
Depende del caso de uso:

- Inmediata: si el archivo debe ser procesado inmediatamente (ej. validación de seguridad, indexación para búsqueda).
- Diferida: si el archivo puede procesarse más tarde (ej. generación de reportes, análisis de datos).

## f) Un reporte mensual es generado.

• ¿Es un evento? ¿Por qué?
Diferencia clave respecto a los eventos anteriores: es un evento programado/batch, no reactivo. Se genera por un scheduler (cron) en una fecha previsible, no como consecuencia de una acción de usuario en
tiempo real. Esto lo hace un evento de baja frecuencia y alta latencia tolerable.

• ¿Qué información mínima debería contener? (Represéntala en formato JSON)
{  
 "event_id": "evt_rpt_2026_03",
"event_type": "report.generated",  
 "timestamp": "2026-04-01T02:15:30Z",  
 "report": {
"report_id": "rpt_0987654321",  
 "name": "Reporte Mensual de Ventas",  
 "period": "2026-03",  
 "type": "monthly_sales",  
 "format": "pdf",  
 "storage_path": "s3://reportes/2026/03/ventas_mensual.pdf",
"size_bytes": 1048576,  
 "generated_by": "scheduler_job_monthly_sales"  
 },  
 "execution": {  
 "job_id": "job_abc123",  
 "duration_seconds": 142,  
 "records_processed": 85432
},  
 "status": "success"  
 }

• ¿Requiere reacción inmediata o puede procesarse más tarde?
Puede procesarse más tarde. Este evento NO requiere tiempo real, por varias razones:

Responde para cada caso:
• ¿Es un evento? ¿Por qué?
• ¿Qué información mínima debería contener? (Represéntala en formato JSON)
• ¿Requiere reacción inmediata o puede procesarse más tarde?

# Discusión

## • ¿Todos los eventos son igual de importantes?

Unos mas que otros, depende del contexto y del negocio. Por ejemplo, un evento de fraude es mas importante que un evento de inicio de sesión.

No, los eventos NO son igual de importantes. Varían en criticidad, urgencia y valor de negocio. Se pueden clasificar en varias dimensiones:

1. Por criticidad de negocio

- Críticos: fraude en tarjeta, fallos de pago, alertas de seguridad, caídas de sistema. Su pérdida o retraso genera pérdida monetaria, riesgo legal o daño reputacional.
- Importantes: login de usuario, compra realizada, archivo subido. Afectan la experiencia del usuario pero no son catastróficos si se demoran.
- Informativos: reportes mensuales, métricas agregadas, logs de navegación. Sirven para análisis y auditoría, tolerantes a demoras.

## • ¿Qué eventos no tienen sentido en tiempo real?

Los eventos que no tienen sentido en tiempo real son aquellos donde procesarlos con baja latencia no aporta valor adicional al negocio, o cuyo consumo natural es diferido. Procesarlos en streaming sería
sobreingeniería: mayor costo, complejidad operativa y consumo de recursos sin beneficio.

Categorías de eventos que NO requieren tiempo real

1. Reportes y agregaciones periódicas

- Reporte mensual de ventas, facturación, nómina: se consumen en ciclos contables (diario, semanal, mensual). Nadie los espera en milisegundos.
- Cierre contable, conciliaciones bancarias: por naturaleza son procesos batch de fin de período.

2. Procesos ETL y analítica histórica

- Carga de data warehouse: los dashboards de BI se actualizan cada hora o cada noche.
- Entrenamiento de modelos de ML: usa datos históricos, no necesita el último segundo.
- Análisis de cohortes, reportes de marketing: se calculan sobre ventanas largas (semanas, meses).

3. Notificaciones no urgentes

- Correos de resumen semanal, newsletters, recordatorios: se envían en ventanas programadas.
- Alertas de "tu suscripción vence en 30 días": no requieren inmediatez al segundo.

4. Auditoría y logs de cumplimiento

- Logs regulatorios para auditoría: se consultan al auditar, no en vivo.
- Archivado histórico: se mueve a almacenamiento frío (S3 Glacier) sin urgencia.

5. Backups, limpieza y mantenimiento

- Snapshots de base de datos, rotación de logs, purga de registros antiguos: se ejecutan en ventanas de baja carga (madrugada).

6. Telemetría agregada de bajo valor individual

- Métricas de uso de UI, analíticas de navegación para dashboards: el valor está en el agregado, no en cada clic individual. Se pueden procesar por lotes cada X minutos.

7. Eventos con destino humano no crítico

- Encuestas de satisfacción, feedback post-compra: se envían horas después sin impacto.

Criterios para identificar eventos que NO necesitan tiempo real

Contraste con eventos que SÍ requieren tiempo real

Como referencia inversa, SÍ tienen sentido en tiempo real:

- Detección de fraude (rechazo de tarjeta).
- Login y autenticación.
- Alertas de sensores críticos (temperatura en reactor, ritmo cardíaco en UCI).
- Trading bursátil.
- Notificaciones push transaccionales (OTP, confirmación de pago).
- Actualización de inventario en e-commerce durante el checkout.

## 2 Utilidad de las colas en los eventos

### ¿Qué pasa si el servicio de procesamiento es lento?

- La app web se vuelve lenta también:
- Timeouts en cascada
- Acumulación de conexiones abiertas
- Fallos en cascada
- Experiencia de usuario degradada

### ¿Qué ocurre si se cae?

- La funcionalidad de la app queda bloqueada:
- Pérdida de eventos/acciones
- Sin tolerancia a fallos
- SPOF (Single Point of Failure)

### ¿Qué pasa si la cantidad de usuarios se multiplica por 10?

- El servicio de procesamiento se satura
- Latencia creciente bajo carga
- Costos de infraestructura disparados:

Ahora el sistema emite eventos y los envía a una cola.

### ¿Qué cambia?

Ahora el sistema emite eventos y los envía a una cola.
Preguntas:
• ¿Qué cambia?

• ¿Qué problema se resuelve?

1.  Resiliencia ante caídas
2.  absorcion de picos de trafico
3.  experiencia de usuario mejorada
4.  escalabilidad
5.  desacoplamiento
6.  observabilidad
7.  durabilidad

• ¿Qué nuevos retos aparecen?

1. Consistencia eventual

- El resultado del procesamiento no es inmediato. Hay una ventana entre "evento publicado" y "evento procesado".
- La UI debe manejar estados intermedios ("en proceso", "pendiente de confirmación") y el usuario puede ver datos desactualizados momentáneamente.
- Flujos que antes eran transaccionales ahora requieren diseño de compensaciones (Saga pattern) si fallan pasos intermedios.
