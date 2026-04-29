# Fase 2: Análisis de utilidad y aplicación (Caso de Uso: Alberti Steelworks S.A.)

**Criterio 6a) Objetivos estratégicos:**
El software aborda el objetivo estratégico principal de la empresa: **"Reducción de costes operativos por inactividad y mejora integral de la seguridad laboral"**. Al simular un entorno SCADA en tiempo real, se alinea con la estrategia de transformación digital, permitiendo a la empresa pasar de un mantenimiento puramente reactivo (reparar maquinaria rota) a un control activo que previene colapsos térmicos mediante bloqueos automáticos.

**Criterio 6b) Áreas de negocio y comunicaciones:**
El área de **Producción (Planta/OT)** se beneficia directamente al tener una visualización intuitiva y en tiempo real del estado de motores y hornos. Paralelamente, el área de **Gerencia y Calidad (IT)** puede auditar el sistema mediante el *Datalogger* integrado. El impacto operativo es drástico: se eliminan las lecturas analógicas manuales, y el sistema interrumpe automáticamente la producción ante peligros inminentes, protegiendo los activos.

**Criterio 6c) Áreas susceptibles de digitalización:**
El área crítica elegida es la **Monitorización de Maquinaria Pesada (Hornos de Fundición y Motores Principales)**. Es altamente susceptible a ser digitalizada porque, históricamente, la recolección de variables físicas (temperatura, presión, carga) dependía de la inspección humana. Con el Gemelo Digital, la recolección es automatizada, eliminando el error humano y permitiendo reacciones en milisegundos.

**Criterio 6d) Encaje de áreas digitalizadas (AD):**
El panel de control IT (área digitalizada) interactúa constantemente con los mecánicos de planta (área física no digitalizada). Cuando el software detecta una anomalía severa (ej. temperatura > 1200ºC) bloquea la interfaz y genera un registro. La propuesta para cohesionar estas áreas es usar este *Datalogger* para emitir "Tickets de Trabajo" que se impriman automáticamente en el taller físico, uniendo la alerta digital con la reparación manual.

**Criterio 6e) Necesidades presentes y futuras:**
* **Presente:** Resuelve la necesidad crítica de visualizar datos físicos complejos en un dashboard sencillo para el operador humano, previniendo averías por sobrecarga.
* **Futuro:** Como se detalla en el archivo `CONTRIBUTING.md`, el sistema está preparado para escalar hacia necesidades futuras, como la integración con modelos de IA para mantenimiento predictivo y el almacenamiento Big Data en la nube (AWS).

**Criterio 6f) Relación con tecnologías:**
Se han empleado tecnologías habilitadoras clave como **Gemelos Digitales (Simulación en memoria)** y **Procesamiento de Datos en Tiempo Real (Python/Matplotlib)**. El beneficio directo de esta implantación es la capacidad de inyectar fallos (pruebas de estrés) en un entorno virtualizado sin poner en riesgo equipos físicos de millones de euros, agilizando la toma de decisiones empresariales.

**Criterio 6g) Brechas de seguridad:**
Al unir redes OT (fábrica) con IT (panel de control), la principal brecha es un ataque de Denegación de Servicio (DoS) o inyección maliciosa de datos que falsee las gráficas, provocando que los sistemas de seguridad no salten.
* **Mitigación:** Se propone implementar una arquitectura *Zero-Trust*, aislando la red de los sensores en VLANs dedicadas, deshabilitando puertos USB en las terminales y utilizando encriptación para la telemetría, asegurando que el panel solo lea datos de fuentes autenticadas.

**Criterio 6h) Tratamiento de datos y análisis:**
El sistema gestiona la telemetría generada simulando sensores reales, capturando datos a una frecuencia de 30 iteraciones por segundo en memoria compartida. Para garantizar la calidad y consistencia del análisis, los datos crudos se cruzan en tiempo real contra umbrales estáticos de seguridad ("Hard Limits"). Los eventos críticos se archivan con sellos de tiempo inmutables, permitiendo auditorías consistentes post-incidente.