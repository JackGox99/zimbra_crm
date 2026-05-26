-- =====================================================================
-- Proyecto: Sistema Transaccional Zimbra CRM — Sesión 2
-- Curso:    Sistemas Transaccionales de Bases de Datos — UNIMINUTO
-- Docente:  Ladi Paola Ballen Carrasco
-- Equipo:   Hayder Esteban Barrera Pérez
--           Julian Mateo Artunduaga Gomez
--           Valery Tatiana Pamplona Gómez
--
-- Este script crea la base de datos, las 9 tablas con sus restricciones,
-- carga 30+ registros por tabla y ejecuta 7 transacciones de negocio
-- que demuestran las propiedades ACID a través de operaciones reales
-- del CRM (no a través de ejemplos artificiales).
-- =====================================================================

CREATE DATABASE zimbra_crm;
USE zimbra_crm;


-- =====================================================================
-- TABLA 1: CAMPANA
-- Campañas de marketing ejecutadas por Zimbra.
-- =====================================================================
CREATE TABLE CAMPANA (
    id_campana       INT AUTO_INCREMENT PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    tipo             VARCHAR(50)  NOT NULL,
    canal            VARCHAR(50)  NOT NULL,
    fecha_inicio     DATE NOT NULL,
    fecha_fin        DATE NOT NULL,
    presupuesto      DECIMAL(12,2),
    estado           VARCHAR(30) NOT NULL,
    CHECK (fecha_fin >= fecha_inicio),
    CHECK (presupuesto >= 0)
);


-- =====================================================================
-- TABLA 2: PROSPECTO
-- =====================================================================
CREATE TABLE PROSPECTO (
    id_prospecto         INT AUTO_INCREMENT PRIMARY KEY,
    nombre               VARCHAR(100) NOT NULL,
    correo               VARCHAR(100) NOT NULL UNIQUE,
    empresa              VARCHAR(100),
    telefono             VARCHAR(20),
    puntuacion           INT DEFAULT 0,
    estado               VARCHAR(30) NOT NULL,
    fecha_registro       DATE NOT NULL,
    fecha_inicio_prueba  DATE,
    fecha_fin_prueba     DATE,
    id_campana_origen    INT,
    FOREIGN KEY (id_campana_origen) REFERENCES CAMPANA(id_campana),
    CHECK (puntuacion >= 0)
);


-- =====================================================================
-- TABLA 3: INTERACCION_MARKETING
-- =====================================================================
CREATE TABLE INTERACCION_MARKETING (
    id_interaccion     INT AUTO_INCREMENT PRIMARY KEY,
    accion             VARCHAR(80) NOT NULL,
    fecha_interaccion  DATETIME NOT NULL,
    peso_scoring       INT NOT NULL,
    id_prospecto       INT NOT NULL,
    id_campana         INT NOT NULL,
    FOREIGN KEY (id_prospecto) REFERENCES PROSPECTO(id_prospecto),
    FOREIGN KEY (id_campana)   REFERENCES CAMPANA(id_campana),
    CHECK (peso_scoring >= 0)
);


-- =====================================================================
-- TABLA 4: PLANTILLA_COMUNICACION
-- =====================================================================
CREATE TABLE PLANTILLA_COMUNICACION (
    id_plantilla     INT AUTO_INCREMENT PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    asunto           VARCHAR(150) NOT NULL,
    cuerpo           TEXT NOT NULL,
    tipo             VARCHAR(40) NOT NULL,
    fecha_creacion   DATE NOT NULL,
    activa           BOOLEAN NOT NULL
);


-- =====================================================================
-- TABLA 5: COMUNICACION_ENVIADA
-- =====================================================================
CREATE TABLE COMUNICACION_ENVIADA (
    id_comunicacion   INT AUTO_INCREMENT PRIMARY KEY,
    fecha_envio       DATETIME NOT NULL,
    estado_envio      VARCHAR(30) NOT NULL,
    id_plantilla      INT NOT NULL,
    id_prospecto      INT NOT NULL,
    id_campana        INT,
    FOREIGN KEY (id_plantilla) REFERENCES PLANTILLA_COMUNICACION(id_plantilla),
    FOREIGN KEY (id_prospecto) REFERENCES PROSPECTO(id_prospecto),
    FOREIGN KEY (id_campana)   REFERENCES CAMPANA(id_campana)
);


-- =====================================================================
-- TABLA 6: PROPUESTA
-- =====================================================================
CREATE TABLE PROPUESTA (
    id_propuesta     INT AUTO_INCREMENT PRIMARY KEY,
    descripcion      TEXT NOT NULL,
    fecha_propuesta  DATE NOT NULL,
    estado           VARCHAR(30) NOT NULL,
    valor_estimado   DECIMAL(12,2) NOT NULL,
    id_prospecto     INT NOT NULL,
    FOREIGN KEY (id_prospecto) REFERENCES PROSPECTO(id_prospecto),
    CHECK (valor_estimado >= 0)
);


-- =====================================================================
-- TABLA 7: CLIENTE
-- =====================================================================
CREATE TABLE CLIENTE (
    id_cliente        INT AUTO_INCREMENT PRIMARY KEY,
    nombre            VARCHAR(100) NOT NULL,
    correo            VARCHAR(100) NOT NULL UNIQUE,
    empresa           VARCHAR(100),
    telefono          VARCHAR(20),
    fecha_registro    DATE NOT NULL,
    id_prospecto      INT UNIQUE,
    sync_salesforce   BOOLEAN NOT NULL,
    fecha_ult_sync    DATETIME,
    FOREIGN KEY (id_prospecto) REFERENCES PROSPECTO(id_prospecto)
);


-- =====================================================================
-- TABLA 8: VENTA
-- =====================================================================
CREATE TABLE VENTA (
    id_venta       INT AUTO_INCREMENT PRIMARY KEY,
    fecha_venta    DATE NOT NULL,
    monto          DECIMAL(12,2) NOT NULL,
    estado         VARCHAR(30) NOT NULL,
    metodo_pago    VARCHAR(40),
    id_propuesta   INT NOT NULL UNIQUE,
    id_cliente     INT NOT NULL,
    FOREIGN KEY (id_propuesta) REFERENCES PROPUESTA(id_propuesta),
    FOREIGN KEY (id_cliente)   REFERENCES CLIENTE(id_cliente),
    CHECK (monto > 0)
);


-- =====================================================================
-- TABLA 9: REPORTE
-- =====================================================================
CREATE TABLE REPORTE (
    id_reporte         INT AUTO_INCREMENT PRIMARY KEY,
    tipo_reporte       VARCHAR(60) NOT NULL,
    fecha_generacion   DATETIME NOT NULL,
    periodo_inicio     DATE,
    periodo_fin        DATE,
    resultado          TEXT,
    id_campana         INT,
    FOREIGN KEY (id_campana) REFERENCES CAMPANA(id_campana)
);


-- =====================================================================
-- INSERTS TABLA CAMPANA (30 registros)
-- =====================================================================
INSERT INTO CAMPANA (nombre, tipo, canal, fecha_inicio, fecha_fin, presupuesto, estado) VALUES
('Lanzamiento ZCS 2026', 'Email', 'Email', '2026-01-01', '2026-01-31', 5000000, 'Finalizada'),
('Promo Empresarial', 'Banner Web', 'Web', '2026-01-05', '2026-02-05', 3500000, 'Activa'),
('Webinar Productividad', 'Webinar', 'Eventos', '2026-01-10', '2026-01-10', 1500000, 'Finalizada'),
('Campaña LinkedIn', 'Banner Web', 'Redes Sociales', '2026-01-15', '2026-02-15', 2800000, 'Activa'),
('Descarga ZCS', 'Descarga Trial', 'Web', '2026-01-20', '2026-12-31', 7000000, 'Activa'),
('Automatización Comercial', 'Email', 'Email', '2026-02-01', '2026-02-28', 3200000, 'Finalizada'),
('Cloud Security', 'Webinar', 'Eventos', '2026-02-05', '2026-02-05', 1800000, 'Finalizada'),
('Infraestructura TI', 'Banner Web', 'Web', '2026-02-10', '2026-03-10', 4000000, 'Activa'),
('Integración CRM', 'Email', 'Email', '2026-02-15', '2026-03-15', 4500000, 'Activa'),
('Sector Salud', 'Banner Web', 'Redes Sociales', '2026-02-20', '2026-03-20', 3900000, 'Planeada'),
('Campaña Educación', 'Email', 'Email', '2026-03-01', '2026-03-31', 4100000, 'Activa'),
('Webinar Analítica', 'Webinar', 'Eventos', '2026-03-05', '2026-03-05', 1700000, 'Finalizada'),
('Migración Empresarial', 'Banner Web', 'Web', '2026-03-10', '2026-04-10', 5300000, 'Activa'),
('Campaña Finanzas', 'Email', 'Email', '2026-03-15', '2026-04-15', 4900000, 'Activa'),
('Transformación Digital', 'Webinar', 'Eventos', '2026-03-20', '2026-03-20', 2000000, 'Finalizada'),
('Colaboración Corporativa', 'Banner Web', 'Web', '2026-04-01', '2026-04-30', 3700000, 'Planeada'),
('Promoción PYMES', 'Email', 'Email', '2026-04-05', '2026-05-05', 2600000, 'Activa'),
('Seguridad Cloud', 'Webinar', 'Eventos', '2026-04-10', '2026-04-10', 2100000, 'Finalizada'),
('Campaña Retail', 'Banner Web', 'Redes Sociales', '2026-04-15', '2026-05-15', 3400000, 'Activa'),
('Modernización TI', 'Email', 'Email', '2026-04-20', '2026-05-20', 4400000, 'Planeada'),
('Innovación Empresarial', 'Webinar', 'Eventos', '2026-05-01', '2026-05-01', 2200000, 'Finalizada'),
('Productividad Empresarial', 'Banner Web', 'Web', '2026-05-05', '2026-06-05', 3600000, 'Activa'),
('Campaña Gobierno', 'Email', 'Email', '2026-05-10', '2026-06-10', 4700000, 'Activa'),
('Infraestructura Híbrida', 'Banner Web', 'Web', '2026-05-15', '2026-06-15', 3900000, 'Planeada'),
('Webinar IA', 'Webinar', 'Eventos', '2026-05-20', '2026-05-20', 2500000, 'Finalizada'),
('Cloud Collaboration', 'Email', 'Email', '2026-06-01', '2026-06-30', 5200000, 'Activa'),
('Campaña Telecom', 'Banner Web', 'Redes Sociales', '2026-06-05', '2026-07-05', 3300000, 'Activa'),
('Automatización CRM', 'Email', 'Email', '2026-06-10', '2026-07-10', 4100000, 'Planeada'),
('Webinar DevOps', 'Webinar', 'Eventos', '2026-06-15', '2026-06-15', 2400000, 'Finalizada'),
('Expansión Empresarial', 'Banner Web', 'Web', '2026-06-20', '2026-07-20', 6000000, 'Activa');


-- =====================================================================
-- INSERTS TABLA PROSPECTO (30 registros)
-- =====================================================================
INSERT INTO PROSPECTO (nombre, correo, empresa, telefono, puntuacion, estado, fecha_registro, fecha_inicio_prueba, fecha_fin_prueba, id_campana_origen) VALUES
('Carlos Mendoza', 'carlos@innovasoft.com', 'InnovaSoft SAS', '3001110001', 15, 'Calificado', '2026-01-01', '2026-01-01', '2026-03-02', 1),
('Ana Rojas', 'ana@grupodigital.com', 'Grupo Digital', '3001110002', 8, 'Contactado', '2026-01-02', NULL, NULL, 2),
('Luis Perez', 'luis@cloudnet.com', 'CloudNet SAS', '3001110003', 20, 'Calificado', '2026-01-03', '2026-01-03', '2026-03-04', 3),
('Laura Gomez', 'laura@businessware.com', 'BusinessWare', '3001110004', 4, 'Pendiente', '2026-01-04', NULL, NULL, 4),
('Pedro Ruiz', 'pedro@solucionesweb.com', 'Soluciones Web', '3001110005', 17, 'Calificado', '2026-01-05', '2026-01-05', '2026-03-06', 5),
('Maria Diaz', 'maria@openservices.com', 'Open Services', '3001110006', 2, 'Pendiente', '2026-01-06', NULL, NULL, 6),
('Sofia Torres', 'sofia@netgroup.com', 'NetGroup', '3001110007', 11, 'Contactado', '2026-01-07', NULL, NULL, 7),
('Camilo Castro', 'camilo@multitech.com', 'MultiTech', '3001110008', 19, 'Calificado', '2026-01-08', '2026-01-08', '2026-03-09', 8),
('Andres Gil', 'andres@alphadata.com', 'AlphaData', '3001110009', 6, 'Contactado', '2026-01-09', NULL, NULL, 9),
('Paula Vega', 'paula@futurecloud.com', 'FutureCloud', '3001110010', 1, 'Pendiente', '2026-01-10', NULL, NULL, 10),
('Julian Herrera', 'julian@logicsoft.com', 'LogicSoft', '3001110011', 12, 'Calificado', '2026-01-11', '2026-01-11', '2026-03-12', 11),
('Valentina Cruz', 'valentina@intercloud.com', 'InterCloud', '3001110012', 7, 'Contactado', '2026-01-12', NULL, NULL, 12),
('Daniel Ramirez', 'daniel@visioncloud.com', 'VisionCloud', '3001110013', 14, 'Calificado', '2026-01-13', '2026-01-13', '2026-03-14', 13),
('Natalia Pardo', 'natalia@conexiondigital.com', 'Conexion Digital', '3001110014', 5, 'Pendiente', '2026-01-14', NULL, NULL, 14),
('Sebastian Leon', 'sebastian@globalware.com', 'GlobalWare', '3001110015', 18, 'Calificado', '2026-01-15', '2026-01-15', '2026-03-16', 15),
('Gabriela Martinez', 'gabriela@networkplus.com', 'Network Plus', '3001110016', 4, 'Contactado', '2026-01-16', NULL, NULL, 16),
('Felipe Navarro', 'felipe@datahub.com', 'DataHub', '3001110017', 13, 'Calificado', '2026-01-17', '2026-01-17', '2026-03-18', 17),
('Tatiana Morales', 'tatiana@techgroup.com', 'TechGroup', '3001110018', 9, 'Contactado', '2026-01-18', NULL, NULL, 18),
('Ricardo Salazar', 'ricardo@cybernetics.com', 'Cybernetics', '3001110019', 16, 'Calificado', '2026-01-19', '2026-01-19', '2026-03-20', 19),
('Carolina Ortiz', 'carolina@digitalsolutions.com', 'Digital Solutions', '3001110020', 2, 'Pendiente', '2026-01-20', NULL, NULL, 20),
('Mauricio Fuentes', 'mauricio@innovatech.com', 'InnovaTech', '3001110021', 15, 'Calificado', '2026-01-21', '2026-01-21', '2026-03-22', 21),
('Diana Herrera', 'diana@tecnored.com', 'TecnoRed', '3001110022', 8, 'Contactado', '2026-01-22', NULL, NULL, 22),
('Kevin Morales', 'kevin@redglobal.com', 'Red Global', '3001110023', 11, 'Calificado', '2026-01-23', '2026-01-23', '2026-03-24', 23),
('Andrea Lozano', 'andrea@cloudenterprise.com', 'Cloud Enterprise', '3001110024', 4, 'Pendiente', '2026-01-24', NULL, NULL, 24),
('Jorge Benitez', 'jorge@securemail.com', 'SecureMail', '3001110025', 17, 'Calificado', '2026-01-25', '2026-01-25', '2026-03-26', 25),
('Sandra Cifuentes', 'sandra@digitalpoint.com', 'Digital Point', '3001110026', 6, 'Contactado', '2026-01-26', NULL, NULL, 26),
('Miguel Torres', 'miguel@futureit.com', 'Future IT', '3001110027', 10, 'Calificado', '2026-01-27', '2026-01-27', '2026-03-28', 27),
('Paola Medina', 'paola@smartbusiness.com', 'Smart Business', '3001110028', 3, 'Pendiente', '2026-01-28', NULL, NULL, 28),
('Cristian Vargas', 'cristian@nextcloud.com', 'NextCloud SAS', '3001110029', 19, 'Calificado', '2026-01-29', '2026-01-29', '2026-03-30', 29),
('Alejandra Romero', 'alejandra@empresarial360.com', 'Empresarial 360', '3001110030', 5, 'Contactado', '2026-01-30', NULL, NULL, 30);


-- =====================================================================
-- INSERTS TABLA INTERACCION_MARKETING (30 registros)
-- =====================================================================
INSERT INTO INTERACCION_MARKETING (accion, fecha_interaccion, peso_scoring, id_prospecto, id_campana) VALUES
('Apertura Correo', '2026-02-01 08:00:00', 2, 1, 1),
('Click Enlace', '2026-02-01 08:15:00', 4, 2, 2),
('Descarga Prueba', '2026-02-01 08:30:00', 10, 3, 3),
('Registro Formulario', '2026-02-01 08:45:00', 5, 4, 4),
('Visita Pagina Precios', '2026-02-01 09:00:00', 6, 5, 5),
('Apertura Correo', '2026-02-02 08:00:00', 2, 6, 6),
('Click Enlace', '2026-02-02 08:15:00', 4, 7, 7),
('Descarga Prueba', '2026-02-02 08:30:00', 10, 8, 8),
('Registro Formulario', '2026-02-02 08:45:00', 5, 9, 9),
('Visita Pagina Precios', '2026-02-02 09:00:00', 6, 10, 10),
('Apertura Correo', '2026-02-03 08:00:00', 2, 11, 11),
('Click Enlace', '2026-02-03 08:15:00', 4, 12, 12),
('Descarga Prueba', '2026-02-03 08:30:00', 10, 13, 13),
('Registro Formulario', '2026-02-03 08:45:00', 5, 14, 14),
('Visita Pagina Precios', '2026-02-03 09:00:00', 6, 15, 15),
('Apertura Correo', '2026-02-04 08:00:00', 2, 16, 16),
('Click Enlace', '2026-02-04 08:15:00', 4, 17, 17),
('Descarga Prueba', '2026-02-04 08:30:00', 10, 18, 18),
('Registro Formulario', '2026-02-04 08:45:00', 5, 19, 19),
('Visita Pagina Precios', '2026-02-04 09:00:00', 6, 20, 20),
('Apertura Correo', '2026-02-05 08:00:00', 2, 21, 21),
('Click Enlace', '2026-02-05 08:15:00', 4, 22, 22),
('Descarga Prueba', '2026-02-05 08:30:00', 10, 23, 23),
('Registro Formulario', '2026-02-05 08:45:00', 5, 24, 24),
('Visita Pagina Precios', '2026-02-05 09:00:00', 6, 25, 25),
('Apertura Correo', '2026-02-06 08:00:00', 2, 26, 26),
('Click Enlace', '2026-02-06 08:15:00', 4, 27, 27),
('Descarga Prueba', '2026-02-06 08:30:00', 10, 28, 28),
('Registro Formulario', '2026-02-06 08:45:00', 5, 29, 29),
('Visita Pagina Precios', '2026-02-06 09:00:00', 6, 30, 30);


-- =====================================================================
-- INSERTS TABLA PLANTILLA_COMUNICACION (30 registros)
-- =====================================================================
INSERT INTO PLANTILLA_COMUNICACION (nombre, asunto, cuerpo, tipo, fecha_creacion, activa) VALUES
('Bienvenida Trial', 'Bienvenido a Zimbra — Tu prueba comienza hoy', 'Hola, gracias por iniciar tu prueba de 60 días de Zimbra Collaboration Suite.', 'Email', '2026-01-01', TRUE),
('Recordatorio Trial 7 días', 'Tu prueba de Zimbra termina en 7 días', 'Te quedan 7 días para aprovechar todas las funciones. Conversa con nuestro equipo comercial.', 'Email', '2026-01-01', TRUE),
('Recordatorio Trial 1 día', 'Última oportunidad: tu prueba expira mañana', 'Mañana finaliza tu periodo gratuito. Selecciona un plan para continuar.', 'Email', '2026-01-01', TRUE),
('Oferta 20% Anual', 'Plan anual con 20% de descuento', 'Aprovecha la promoción exclusiva por nuestro plan anual empresarial.', 'Email', '2026-01-05', TRUE),
('Caso éxito Salud', 'Cómo el sector salud usa Zimbra', 'Conoce el caso de una clínica con 500 usuarios migrada exitosamente.', 'Email', '2026-01-10', TRUE),
('Caso éxito Finanzas', 'Zimbra en el sector financiero', 'Aseguramiento de comunicación corporativa en banca.', 'Email', '2026-01-12', TRUE),
('Invitación Webinar', 'Webinar técnico: Migración de Exchange a Zimbra', 'Te invitamos al webinar técnico el próximo jueves.', 'Email', '2026-01-15', TRUE),
('Documentación Técnica', 'Manual de administración Zimbra', 'Accede a la documentación oficial de Zimbra Admin.', 'Email', '2026-01-20', TRUE),
('Soporte 24/7', 'Conoce nuestro plan de soporte premium', 'Soporte técnico 24/7 con SLA garantizado.', 'Email', '2026-01-22', TRUE),
('Comparativa', 'Zimbra vs Microsoft 365', 'Compara funcionalidades y precios.', 'Email', '2026-01-25', TRUE),
('Notificación nuevo lead', 'Tienes un nuevo prospecto calificado', 'Un prospecto cruzó el umbral de scoring. Revisa el dashboard.', 'Notificacion', '2026-02-01', TRUE),
('SMS confirmación demo', 'Tu demo Zimbra está confirmada', 'Tu demostración está confirmada para mañana a las 10am.', 'SMS', '2026-02-05', TRUE),
('Email seguridad', 'Buenas prácticas de seguridad en correo', 'Recomendaciones para asegurar tu instancia Zimbra.', 'Email', '2026-02-10', TRUE),
('Cierre comercial', 'Tu propuesta personalizada está lista', 'Hemos preparado una propuesta basada en tus necesidades.', 'Email', '2026-02-15', TRUE),
('Bienvenida cliente', 'Bienvenido a la familia Zimbra', 'Gracias por elegirnos. Tu activación inicia ahora.', 'Email', '2026-02-20', TRUE),
('Notificación alerta', 'Alerta: prospecto inactivo', 'Un prospecto lleva 14 días sin interacciones.', 'Notificacion', '2026-02-25', TRUE),
('SMS recordatorio webinar', 'Webinar Zimbra hoy a las 3pm', 'Recuerda el webinar de hoy a las 3pm. Conéctate puntual.', 'SMS', '2026-03-01', TRUE),
('Promoción referidos', 'Refiere y gana un mes gratis', 'Comparte Zimbra con otros equipos y obtén bonificaciones.', 'Email', '2026-03-05', TRUE),
('Upgrade Cloud', 'Lleva tu correo a la nube', 'Migración a Zimbra Cloud sin interrupción del servicio.', 'Email', '2026-03-10', TRUE),
('Plantilla obsoleta v1', 'Promo descontinuada (no usar)', 'Plantilla antigua mantenida solo por histórico.', 'Email', '2025-12-01', FALSE),
('Email integración Salesforce', 'Integra tu CRM con Zimbra', 'Sincroniza contactos y leads con Salesforce de forma automática.', 'Email', '2026-03-15', TRUE),
('SMS vencimiento prueba', 'Tu prueba termina mañana', 'Última oportunidad para suscribirte sin perder configuración.', 'SMS', '2026-03-18', TRUE),
('Notificación campaña activa', 'Nueva campaña en curso', 'La campaña Sector Salud está activa para tu segmento.', 'Notificacion', '2026-03-20', TRUE),
('Email roadmap', 'Roadmap Zimbra 2026', 'Conoce las próximas funciones de la plataforma.', 'Email', '2026-04-01', TRUE),
('Recuperación abandonados', 'Volvamos a hablar', 'Nos diste tus datos pero no completaste el registro. Te ayudamos.', 'Email', '2026-04-05', TRUE),
('SMS alerta venta', 'Tu venta fue procesada', 'Tu compra fue confirmada. Recibirás credenciales en breve.', 'SMS', '2026-04-10', TRUE),
('Notificación fin trial', 'Recordatorio interno: prospecto sale del trial', 'Notificación interna para el equipo de ventas.', 'Notificacion', '2026-04-12', TRUE),
('Email encuesta NPS', 'Cuéntanos cómo te fue', 'Tu opinión es valiosa. Responde nuestra encuesta breve.', 'Email', '2026-04-15', TRUE),
('Plantilla legacy v0', 'Lanzamiento original ZCS (no usar)', 'Plantilla del primer lanzamiento, archivada.', 'Email', '2025-09-01', FALSE),
('Email feliz aniversario', 'Felicitaciones por tu aniversario con Zimbra', 'Celebramos un año contigo. Gracias por confiar.', 'Email', '2026-05-01', TRUE);


-- =====================================================================
-- INSERTS TABLA COMUNICACION_ENVIADA (30 registros)
-- =====================================================================
INSERT INTO COMUNICACION_ENVIADA (fecha_envio, estado_envio, id_plantilla, id_prospecto, id_campana) VALUES
('2026-02-01 09:00:00', 'Enviado',  1,  1, 1),
('2026-02-01 09:05:00', 'Abierto',  1,  2, 2),
('2026-02-02 09:00:00', 'Enviado',  4,  3, 3),
('2026-02-02 09:05:00', 'Rebotado', 1,  4, 4),
('2026-02-03 09:00:00', 'Enviado',  2,  5, 5),
('2026-02-03 09:05:00', 'Abierto',  5,  6, 6),
('2026-02-04 09:00:00', 'Enviado',  7,  7, 7),
('2026-02-04 09:05:00', 'Abierto',  3,  8, 8),
('2026-02-05 09:00:00', 'Fallido',  4,  9, 9),
('2026-02-05 09:05:00', 'Enviado',  6, 10, 10),
('2026-02-06 09:00:00', 'Abierto', 14, 11, 11),
('2026-02-06 09:05:00', 'Enviado',  8, 12, 12),
('2026-02-07 09:00:00', 'Abierto',  9, 13, 13),
('2026-02-07 09:05:00', 'Enviado', 10, 14, 14),
('2026-02-08 09:00:00', 'Abierto', 14, 15, 15),
('2026-02-08 09:05:00', 'Enviado', 13, 16, 16),
('2026-02-09 09:00:00', 'Abierto', 14, 17, 17),
('2026-02-09 09:05:00', 'Rebotado', 4, 18, 18),
('2026-02-10 09:00:00', 'Enviado', 18, 19, 19),
('2026-02-10 09:05:00', 'Abierto', 15, 20, 20),
('2026-02-11 09:00:00', 'Enviado', 19, 21, 21),
('2026-02-11 09:05:00', 'Abierto', 17, 22, 22),
('2026-02-12 09:00:00', 'Enviado', 21, 23, 23),
('2026-02-12 09:05:00', 'Fallido', 22, 24, 24),
('2026-02-13 09:00:00', 'Enviado', 23, 25, 25),
('2026-02-13 09:05:00', 'Abierto', 24, 26, 26),
('2026-02-14 09:00:00', 'Enviado', 25, 27, 27),
('2026-02-14 09:05:00', 'Rebotado', 4, 28, 28),
('2026-02-15 09:00:00', 'Enviado', 26, 29, 29),
('2026-02-15 09:05:00', 'Abierto',  2, 30, 30);


-- =====================================================================
-- INSERTS TABLA PROPUESTA (30 registros)
-- =====================================================================
INSERT INTO PROPUESTA (descripcion, fecha_propuesta, estado, valor_estimado, id_prospecto) VALUES
('Licenciamiento Zimbra 50 usuarios', '2026-03-01', 'Aceptada', 12000000, 1),
('Migración de correo empresarial', '2026-03-02', 'Pendiente', 8500000, 2),
('Implementación ZCS corporativo', '2026-03-03', 'Rechazada', 9300000, 3),
('Soporte premium empresarial', '2026-03-04', 'Aceptada', 4500000, 4),
('Infraestructura colaborativa', '2026-03-05', 'Pendiente', 7800000, 5),
('Correo corporativo seguro', '2026-03-06', 'Aceptada', 5600000, 6),
('Automatización comercial', '2026-03-07', 'Pendiente', 4900000, 7),
('Renovación plataforma cloud', '2026-03-08', 'Aceptada', 15000000, 8),
('Sincronización Salesforce', '2026-03-09', 'Pendiente', 6200000, 9),
('Infraestructura híbrida', '2026-03-10', 'Rechazada', 7300000, 10),
('Actualización tecnológica', '2026-03-11', 'Aceptada', 9800000, 11),
('Seguridad de correo', '2026-03-12', 'Pendiente', 4100000, 12),
('Servicios colaborativos', '2026-03-13', 'Aceptada', 8600000, 13),
('Administración centralizada', '2026-03-14', 'Pendiente', 5300000, 14),
('Migración cloud empresarial', '2026-03-15', 'Aceptada', 11700000, 15),
('Optimización TI', '2026-03-16', 'Rechazada', 6600000, 16),
('Mensajería empresarial', '2026-03-17', 'Pendiente', 3900000, 17),
('Infraestructura avanzada', '2026-03-18', 'Aceptada', 13200000, 18),
('Modernización digital', '2026-03-19', 'Pendiente', 7200000, 19),
('Implementación corporativa', '2026-03-20', 'Aceptada', 9100000, 20),
('Servicios Zimbra Enterprise', '2026-03-21', 'Pendiente', 8300000, 21),
('Migración institucional', '2026-03-22', 'Aceptada', 14400000, 22),
('Seguridad avanzada', '2026-03-23', 'Rechazada', 5100000, 23),
('Colaboración premium', '2026-03-24', 'Aceptada', 12500000, 24),
('Administración cloud', '2026-03-25', 'Pendiente', 6100000, 25),
('Infraestructura TI avanzada', '2026-03-26', 'Aceptada', 8700000, 26),
('Integración CRM', '2026-03-27', 'Pendiente', 7600000, 27),
('Modernización empresarial', '2026-03-28', 'Aceptada', 9600000, 28),
('Mensajería segura', '2026-03-29', 'Pendiente', 4700000, 29),
('Infraestructura empresarial', '2026-03-30', 'Aceptada', 13800000, 30);


-- =====================================================================
-- INSERTS TABLA CLIENTE (30 registros)
-- =====================================================================
INSERT INTO CLIENTE (nombre, correo, empresa, telefono, fecha_registro, id_prospecto, sync_salesforce, fecha_ult_sync) VALUES
('Carlos Mendoza', 'cliente1@innovasoft.com', 'InnovaSoft SAS', '3100000001', '2026-04-01', 1, TRUE, '2026-04-01 08:00:00'),
('Ana Rojas', 'cliente2@grupodigital.com', 'Grupo Digital', '3100000002', '2026-04-02', 2, TRUE, '2026-04-02 08:00:00'),
('Luis Perez', 'cliente3@cloudnet.com', 'CloudNet SAS', '3100000003', '2026-04-03', 3, FALSE, NULL),
('Laura Gomez', 'cliente4@businessware.com', 'BusinessWare', '3100000004', '2026-04-04', 4, TRUE, '2026-04-04 08:00:00'),
('Pedro Ruiz', 'cliente5@solucionesweb.com', 'Soluciones Web', '3100000005', '2026-04-05', 5, FALSE, NULL),
('Maria Diaz', 'cliente6@openservices.com', 'Open Services', '3100000006', '2026-04-06', 6, TRUE, '2026-04-06 08:00:00'),
('Sofia Torres', 'cliente7@netgroup.com', 'NetGroup', '3100000007', '2026-04-07', 7, TRUE, '2026-04-07 08:00:00'),
('Camilo Castro', 'cliente8@multitech.com', 'MultiTech', '3100000008', '2026-04-08', 8, FALSE, NULL),
('Andres Gil', 'cliente9@alphadata.com', 'AlphaData', '3100000009', '2026-04-09', 9, TRUE, '2026-04-09 08:00:00'),
('Paula Vega', 'cliente10@futurecloud.com', 'FutureCloud', '3100000010', '2026-04-10', 10, FALSE, NULL),
('Julian Herrera', 'cliente11@logicsoft.com', 'LogicSoft', '3100000011', '2026-04-11', 11, TRUE, '2026-04-11 08:00:00'),
('Valentina Cruz', 'cliente12@intercloud.com', 'InterCloud', '3100000012', '2026-04-12', 12, TRUE, '2026-04-12 08:00:00'),
('Daniel Ramirez', 'cliente13@visioncloud.com', 'VisionCloud', '3100000013', '2026-04-13', 13, FALSE, NULL),
('Natalia Pardo', 'cliente14@conexiondigital.com', 'Conexion Digital', '3100000014', '2026-04-14', 14, TRUE, '2026-04-14 08:00:00'),
('Sebastian Leon', 'cliente15@globalware.com', 'GlobalWare', '3100000015', '2026-04-15', 15, FALSE, NULL),
('Gabriela Martinez', 'cliente16@networkplus.com', 'Network Plus', '3100000016', '2026-04-16', 16, TRUE, '2026-04-16 08:00:00'),
('Felipe Navarro', 'cliente17@datahub.com', 'DataHub', '3100000017', '2026-04-17', 17, TRUE, '2026-04-17 08:00:00'),
('Tatiana Morales', 'cliente18@techgroup.com', 'TechGroup', '3100000018', '2026-04-18', 18, FALSE, NULL),
('Ricardo Salazar', 'cliente19@cybernetics.com', 'Cybernetics', '3100000019', '2026-04-19', 19, TRUE, '2026-04-19 08:00:00'),
('Carolina Ortiz', 'cliente20@digitalsolutions.com', 'Digital Solutions', '3100000020', '2026-04-20', 20, FALSE, NULL),
('Mauricio Fuentes', 'cliente21@innovatech.com', 'InnovaTech', '3100000021', '2026-04-21', 21, TRUE, '2026-04-21 08:00:00'),
('Diana Herrera', 'cliente22@tecnored.com', 'TecnoRed', '3100000022', '2026-04-22', 22, TRUE, '2026-04-22 08:00:00'),
('Kevin Morales', 'cliente23@redglobal.com', 'Red Global', '3100000023', '2026-04-23', 23, FALSE, NULL),
('Andrea Lozano', 'cliente24@cloudenterprise.com', 'Cloud Enterprise', '3100000024', '2026-04-24', 24, TRUE, '2026-04-24 08:00:00'),
('Jorge Benitez', 'cliente25@securemail.com', 'SecureMail', '3100000025', '2026-04-25', 25, FALSE, NULL),
('Sandra Cifuentes', 'cliente26@digitalpoint.com', 'Digital Point', '3100000026', '2026-04-26', 26, TRUE, '2026-04-26 08:00:00'),
('Miguel Torres', 'cliente27@futureit.com', 'Future IT', '3100000027', '2026-04-27', 27, TRUE, '2026-04-27 08:00:00'),
('Paola Medina', 'cliente28@smartbusiness.com', 'Smart Business', '3100000028', '2026-04-28', 28, FALSE, NULL),
('Cristian Vargas', 'cliente29@nextcloud.com', 'NextCloud SAS', '3100000029', '2026-04-29', 29, TRUE, '2026-04-29 08:00:00'),
('Alejandra Romero', 'cliente30@empresarial360.com', 'Empresarial 360', '3100000030', '2026-04-30', 30, FALSE, NULL);


-- =====================================================================
-- INSERTS TABLA VENTA (30 registros)
-- =====================================================================
INSERT INTO VENTA (fecha_venta, monto, estado, metodo_pago, id_propuesta, id_cliente) VALUES
('2026-05-01', 12000000, 'Pagada', 'Transferencia', 1, 1),
('2026-05-02', 8500000, 'Pendiente', 'Tarjeta', 2, 2),
('2026-05-03', 9300000, 'Pagada', 'PayPal', 3, 3),
('2026-05-04', 4500000, 'Pagada', 'Transferencia', 4, 4),
('2026-05-05', 7800000, 'Pendiente', 'Tarjeta', 5, 5),
('2026-05-06', 5600000, 'Pagada', 'Transferencia', 6, 6),
('2026-05-07', 4900000, 'Pendiente', 'PayPal', 7, 7),
('2026-05-08', 15000000, 'Pagada', 'Transferencia', 8, 8),
('2026-05-09', 6200000, 'Pagada', 'Tarjeta', 9, 9),
('2026-05-10', 7300000, 'Pendiente', 'PayPal', 10, 10),
('2026-05-11', 9800000, 'Pagada', 'Transferencia', 11, 11),
('2026-05-12', 4100000, 'Pendiente', 'Tarjeta', 12, 12),
('2026-05-13', 8600000, 'Pagada', 'Transferencia', 13, 13),
('2026-05-14', 5300000, 'Pagada', 'PayPal', 14, 14),
('2026-05-15', 11700000, 'Pendiente', 'Tarjeta', 15, 15),
('2026-05-16', 6600000, 'Pagada', 'Transferencia', 16, 16),
('2026-05-17', 3900000, 'Pendiente', 'PayPal', 17, 17),
('2026-05-18', 13200000, 'Pagada', 'Transferencia', 18, 18),
('2026-05-19', 7200000, 'Pagada', 'Tarjeta', 19, 19),
('2026-05-20', 9100000, 'Pendiente', 'Transferencia', 20, 20),
('2026-05-21', 8300000, 'Pagada', 'PayPal', 21, 21),
('2026-05-22', 14400000, 'Pagada', 'Transferencia', 22, 22),
('2026-05-23', 5100000, 'Pendiente', 'Tarjeta', 23, 23),
('2026-05-24', 12500000, 'Pagada', 'Transferencia', 24, 24),
('2026-05-25', 6100000, 'Pendiente', 'PayPal', 25, 25),
('2026-05-26', 8700000, 'Pagada', 'Transferencia', 26, 26),
('2026-05-27', 7600000, 'Pagada', 'Tarjeta', 27, 27),
('2026-05-28', 9600000, 'Pendiente', 'PayPal', 28, 28),
('2026-05-29', 4700000, 'Pagada', 'Transferencia', 29, 29),
('2026-05-30', 13800000, 'Pagada', 'Tarjeta', 30, 30);


-- =====================================================================
-- INSERTS TABLA REPORTE (30 registros)
-- =====================================================================
INSERT INTO REPORTE (tipo_reporte, fecha_generacion, periodo_inicio, periodo_fin, resultado, id_campana) VALUES
('Rendimiento Campana', '2026-04-01 18:00:00', '2026-03-01', '2026-03-31', 'Campaña con alto nivel de conversión empresarial.', 1),
('Prospectos Calificados', '2026-04-02 18:00:00', '2026-03-01', '2026-03-31', 'Incremento de prospectos calificados.', 2),
('Ventas Periodo', '2026-04-03 18:00:00', '2026-03-01', '2026-03-31', 'Ventas superiores al objetivo mensual.', 3),
('Conversion Embudo', '2026-04-04 18:00:00', '2026-03-01', '2026-03-31', 'Conversión positiva en campañas digitales.', 4),
('Rendimiento Campana', '2026-04-05 18:00:00', '2026-03-01', '2026-03-31', 'Buen desempeño comercial.', 5),
('Prospectos Calificados', '2026-04-06 18:00:00', '2026-03-01', '2026-03-31', 'Prospectos activos incrementaron.', 6),
('Ventas Periodo', '2026-04-07 18:00:00', '2026-03-01', '2026-03-31', 'Incremento en ingresos corporativos.', 7),
('Conversion Embudo', '2026-04-08 18:00:00', '2026-03-01', '2026-03-31', 'Conversión estable.', 8),
('Rendimiento Campana', '2026-04-09 18:00:00', '2026-03-01', '2026-03-31', 'Campaña con alta interacción.', 9),
('Prospectos Calificados', '2026-04-10 18:00:00', '2026-03-01', '2026-03-31', 'Más prospectos empresariales.', 10),
('Ventas Periodo', '2026-04-11 18:00:00', '2026-03-01', '2026-03-31', 'Objetivo financiero alcanzado.', 11),
('Conversion Embudo', '2026-04-12 18:00:00', '2026-03-01', '2026-03-31', 'Embudo comercial optimizado.', 12),
('Rendimiento Campana', '2026-04-13 18:00:00', '2026-03-01', '2026-03-31', 'Excelente rendimiento digital.', 13),
('Prospectos Calificados', '2026-04-14 18:00:00', '2026-03-01', '2026-03-31', 'Calificación comercial positiva.', 14),
('Ventas Periodo', '2026-04-15 18:00:00', '2026-03-01', '2026-03-31', 'Incremento de ventas cloud.', 15),
('Conversion Embudo', '2026-04-16 18:00:00', '2026-03-01', '2026-03-31', 'Conversión superior al trimestre anterior.', 16),
('Rendimiento Campana', '2026-04-17 18:00:00', '2026-03-01', '2026-03-31', 'Campaña con buena cobertura.', 17),
('Prospectos Calificados', '2026-04-18 18:00:00', '2026-03-01', '2026-03-31', 'Prospectos listos para ventas.', 18),
('Ventas Periodo', '2026-04-19 18:00:00', '2026-03-01', '2026-03-31', 'Ventas corporativas estables.', 19),
('Conversion Embudo', '2026-04-20 18:00:00', '2026-03-01', '2026-03-31', 'Conversión efectiva en sector TI.', 20),
('Rendimiento Campana', '2026-04-21 18:00:00', '2026-03-01', '2026-03-31', 'Resultados positivos.', 21),
('Prospectos Calificados', '2026-04-22 18:00:00', '2026-03-01', '2026-03-31', 'Incremento comercial.', 22),
('Ventas Periodo', '2026-04-23 18:00:00', '2026-03-01', '2026-03-31', 'Ingresos superiores a lo esperado.', 23),
('Conversion Embudo', '2026-04-24 18:00:00', '2026-03-01', '2026-03-31', 'Buen comportamiento de clientes.', 24),
('Rendimiento Campana', '2026-04-25 18:00:00', '2026-03-01', '2026-03-31', 'Campaña con crecimiento constante.', 25),
('Prospectos Calificados', '2026-04-26 18:00:00', '2026-03-01', '2026-03-31', 'Mayor interés empresarial.', 26),
('Ventas Periodo', '2026-04-27 18:00:00', '2026-03-01', '2026-03-31', 'Ventas empresariales positivas.', 27),
('Conversion Embudo', '2026-04-28 18:00:00', '2026-03-01', '2026-03-31', 'Embudo comercial eficiente.', 28),
('Rendimiento Campana', '2026-04-29 18:00:00', '2026-03-01', '2026-03-31', 'Buen rendimiento general.', 29),
('Prospectos Calificados', '2026-04-30 18:00:00', '2026-03-01', '2026-03-31', 'Resultados comerciales positivos.', 30);


-- =====================================================================
-- TRANSACCIONES DE NEGOCIO
--
-- Cada transacción modela una operación REAL del CRM de Zimbra y
-- demuestra una o más propiedades ACID a través de la lógica del
-- negocio, no mediante ejemplos artificiales.
--
-- Comandos utilizados:
--   * START TRANSACTION  → inicia una transacción.
--   * COMMIT             → confirma todos los cambios.
--   * ROLLBACK           → revierte todos los cambios.
--   * SAVEPOINT nombre   → punto intermedio dentro de la transacción.
--   * ROLLBACK TO nombre → revierte hasta ese savepoint sin abortar.
-- =====================================================================


-- ---------------------------------------------------------------------
-- TRANSACCIÓN 1: Onboarding de un nuevo prospecto desde una campaña
--
-- ESCENARIO DE NEGOCIO:
-- Un visitante diligencia el formulario web de la campaña "Descarga
-- ZCS" (id 5). El sistema debe crear su registro como PROSPECTO y
-- dejar evidencia de su primera INTERACCION_MARKETING (la descarga).
--
-- PROPIEDAD ACID DEMOSTRADA: ATOMICIDAD.
-- Las dos operaciones son indivisibles: si la inserción de la
-- interacción falla, el prospecto tampoco debe persistir, porque
-- quedaría huérfano sin evidencia de entrada al embudo.
-- ---------------------------------------------------------------------
START TRANSACTION;

INSERT INTO PROSPECTO (
    nombre, correo, empresa, telefono, puntuacion, estado, fecha_registro,
    fecha_inicio_prueba, fecha_fin_prueba, id_campana_origen
) VALUES (
    'Diego Martinez',
    'diego.martinez@techsolutions.com',
    'Tech Solutions SAS',
    '3205551111',
    10,
    'Contactado',
    CURDATE(),
    CURDATE(),
    DATE_ADD(CURDATE(), INTERVAL 60 DAY),
    5
);

SET @nuevo_prospecto = LAST_INSERT_ID();

INSERT INTO INTERACCION_MARKETING (
    accion, fecha_interaccion, peso_scoring, id_prospecto, id_campana
) VALUES (
    'Descarga Prueba',
    NOW(),
    10,
    @nuevo_prospecto,
    5
);

COMMIT;


-- ---------------------------------------------------------------------
-- TRANSACCIÓN 2: Calificación automática por scoring acumulado
--
-- ESCENARIO DE NEGOCIO:
-- Diego visita la página de precios. El sistema registra la nueva
-- interacción (peso 6), suma los puntos al scoring y, como Diego ya
-- tenía 10, alcanza 16 → cruza el umbral de 15 → es promovido
-- automáticamente a 'Calificado'.
--
-- PROPIEDADES ACID DEMOSTRADAS: ATOMICIDAD + CONSISTENCIA.
-- Las 3 operaciones (insertar interacción, sumar puntos, promover
-- estado) deben ser una sola unidad. Si la BD cayera entre ellas
-- quedarían datos inconsistentes (puntuación desfasada, prospecto
-- promovido sin justificación, etc.).
-- ---------------------------------------------------------------------
START TRANSACTION;

INSERT INTO INTERACCION_MARKETING (
    accion, fecha_interaccion, peso_scoring, id_prospecto, id_campana
) VALUES (
    'Visita Pagina Precios',
    NOW(),
    6,
    @nuevo_prospecto,
    5
);

UPDATE PROSPECTO
SET puntuacion = puntuacion + 6
WHERE id_prospecto = @nuevo_prospecto;

UPDATE PROSPECTO
SET estado = 'Calificado'
WHERE id_prospecto = @nuevo_prospecto
  AND puntuacion >= 15
  AND estado IN ('Pendiente', 'Contactado');

COMMIT;


-- ---------------------------------------------------------------------
-- TRANSACCIÓN 3: Generación de propuesta comercial
--
-- ESCENARIO DE NEGOCIO:
-- Diego ya es prospecto Calificado. El equipo comercial le genera una
-- propuesta personalizada de licenciamiento empresarial.
--
-- PROPIEDADES ACID DEMOSTRADAS: ATOMICIDAD + DURABILIDAD.
-- Tras el COMMIT, la propuesta queda persistida en el redo log de
-- InnoDB; sobrevive a cualquier caída posterior del servidor.
-- ---------------------------------------------------------------------
START TRANSACTION;

INSERT INTO PROPUESTA (
    descripcion, fecha_propuesta, estado, valor_estimado, id_prospecto
) VALUES (
    'Licenciamiento Zimbra Collaboration Suite Enterprise — 120 usuarios + soporte premium 12 meses',
    CURDATE(),
    'Pendiente',
    18500000,
    @nuevo_prospecto
);

SET @nueva_propuesta = LAST_INSERT_ID();

COMMIT;


-- ---------------------------------------------------------------------
-- TRANSACCIÓN 4: Cierre de venta con SAVEPOINT
--                (la transacción más crítica del CRM)
--
-- ESCENARIO DE NEGOCIO:
-- Diego acepta la propuesta. El sistema debe ejecutar 4 operaciones
-- encadenadas como una sola unidad:
--   1) Marcar la PROPUESTA como 'Aceptada'.
--   2) Crear el registro de CLIENTE desde el PROSPECTO.
--   3) Marcar el PROSPECTO como 'Convertido'.
--   4) Registrar la VENTA con el monto de la propuesta.
--
-- PROPIEDADES ACID DEMOSTRADAS: ATOMICIDAD + CONSISTENCIA + DURABILIDAD.
-- Si cualquier paso falla, NINGUNA escritura debe persistir, porque
-- el negocio no acepta estados parciales (p.ej. una venta sin
-- cliente, o un cliente sin venta).
--
-- USO DE SAVEPOINT:
-- La creación del cliente se aísla con un SAVEPOINT porque puede
-- fallar por UNIQUE en el caso de "recompra" (el cliente ya existía
-- de una venta anterior). En ese escenario haríamos ROLLBACK TO
-- sp_crear_cliente, recuperaríamos el cliente existente y
-- continuaríamos con la venta sin abortar toda la transacción.
-- ---------------------------------------------------------------------
START TRANSACTION;

-- 1) Aceptar la propuesta
UPDATE PROPUESTA
SET estado = 'Aceptada'
WHERE id_propuesta = @nueva_propuesta
  AND estado = 'Pendiente';

-- 2) Crear el cliente (protegido por SAVEPOINT)
SAVEPOINT sp_crear_cliente;

INSERT INTO CLIENTE (
    nombre, correo, empresa, telefono, fecha_registro,
    id_prospecto, sync_salesforce, fecha_ult_sync
)
SELECT
    nombre,
    CONCAT('cliente_', correo),
    empresa,
    telefono,
    CURDATE(),
    id_prospecto,
    FALSE,
    NULL
FROM PROSPECTO
WHERE id_prospecto = @nuevo_prospecto;

SET @nuevo_cliente = LAST_INSERT_ID();

-- 3) Marcar el prospecto como Convertido
UPDATE PROSPECTO
SET estado = 'Convertido'
WHERE id_prospecto = @nuevo_prospecto;

-- 4) Registrar la venta
INSERT INTO VENTA (
    fecha_venta, monto, estado, metodo_pago, id_propuesta, id_cliente
)
SELECT
    CURDATE(),
    valor_estimado,
    'Pagada',
    'Transferencia',
    id_propuesta,
    @nuevo_cliente
FROM PROPUESTA
WHERE id_propuesta = @nueva_propuesta;

COMMIT;


-- ---------------------------------------------------------------------
-- TRANSACCIÓN 5: Descalificación de prospecto (operación atómica)
--
-- ESCENARIO DE NEGOCIO:
-- El equipo comercial detecta que Laura Gomez (id 4) no es un fit
-- real para Zimbra: su empresa es muy pequeña para el licenciamiento
-- empresarial. Se la descalifica del flujo de marketing y se le
-- resetea el scoring para evitar alertas falsas.
--
-- PROPIEDAD ACID DEMOSTRADA: ATOMICIDAD.
-- El cambio de estado y el reseteo de puntuación deben ocurrir
-- juntos: un prospecto Inadecuado con scoring alto residual
-- dispararía alertas erróneas al equipo de ventas.
-- ---------------------------------------------------------------------
START TRANSACTION;

UPDATE PROSPECTO
SET estado     = 'Inadecuado',
    puntuacion = 0
WHERE id_prospecto = 4;

COMMIT;


-- ---------------------------------------------------------------------
-- TRANSACCIÓN 6: ROLLBACK TO SAVEPOINT — corrección selectiva
--
-- ESCENARIO DE NEGOCIO:
-- El equipo está actualizando manualmente el estado de Carolina Ortiz
-- (id 20) a 'Calificado' porque pasó un proceso de validación
-- empresarial. En el mismo flujo intentan registrarle una interacción
-- "Asistencia Webinar". Justo antes de COMMIT descubren que la
-- asistencia fue mal atribuida (era de otro prospecto). Hacen
-- ROLLBACK TO sp_antes_interaccion para anular SOLO la interacción y
-- conservar la calificación correcta.
--
-- PROPIEDAD ACID DEMOSTRADA: ATOMICIDAD PARCIAL mediante SAVEPOINTs.
-- Se revierte una parte sin abortar el resto de la transacción.
-- ---------------------------------------------------------------------
START TRANSACTION;

UPDATE PROSPECTO
SET estado = 'Calificado'
WHERE id_prospecto = 20;

SAVEPOINT sp_antes_interaccion;

INSERT INTO INTERACCION_MARKETING (
    accion, fecha_interaccion, peso_scoring, id_prospecto, id_campana
) VALUES (
    'Asistencia Webinar',
    NOW(),
    6,
    20,
    20
);

-- El equipo se da cuenta del error de atribución.
ROLLBACK TO sp_antes_interaccion;

COMMIT;


-- ---------------------------------------------------------------------
-- TRANSACCIÓN 7: ROLLBACK total por regla de negocio
--
-- ESCENARIO DE NEGOCIO:
-- Un comercial intenta crear una propuesta para Laura Gomez (id 4),
-- pero ella ya fue marcada como 'Inadecuado' en la transacción 5. La
-- regla del CRM prohíbe enviar propuestas a prospectos inadecuados.
-- Tras iniciar la transacción y antes de confirmar, se detecta la
-- condición → ROLLBACK total.
--
-- PROPIEDAD ACID DEMOSTRADA: ATOMICIDAD.
-- Aunque el INSERT no viola ninguna restricción del DDL, la regla
-- del negocio exige revertir todo.
-- ---------------------------------------------------------------------
START TRANSACTION;

INSERT INTO PROPUESTA (
    descripcion, fecha_propuesta, estado, valor_estimado, id_prospecto
) VALUES (
    'Propuesta tentativa servicios corporativos',
    CURDATE(),
    'Pendiente',
    9800000,
    4
);

-- Motor de reglas detecta que el prospecto está Inadecuado.
ROLLBACK;


-- =====================================================================
-- FIN DE LAS TRANSACCIONES (Sesión 2).
-- =====================================================================



-- #####################################################################
-- #                                                                   #
-- #   SESIÓN 3 — AUTOMATIZACIÓN Y LÓGICA AVANZADA                     #
-- #                                                                   #
-- #   4 triggers + 3 procedimientos almacenados + 3 funciones UDF     #
-- #   sobre las 9 tablas existentes (sin crear tablas adicionales).   #
-- #                                                                   #
-- #   IMPORTANTE: estos objetos se crean DESPUÉS de cargar los datos  #
-- #   y de ejecutar las 7 transacciones de la Sesión 2, porque el     #
-- #   trigger trg_interaccion_actualiza_scoring sumaría dos veces el  #
-- #   peso si estuviera activo durante los INSERT iniciales.          #
-- #                                                                   #
-- #####################################################################


-- =====================================================================
-- TRIGGERS
-- =====================================================================

-- --------------------------------------------------------------------
-- TRIGGER 1: trg_interaccion_actualiza_scoring
-- AFTER INSERT en INTERACCION_MARKETING.
-- Suma el peso al scoring del prospecto y lo promueve a 'Calificado'
-- si supera 15 puntos y estaba en estado promovible (Pendiente o
-- Contactado). Lleva la regla de calificación a la BD para que se
-- cumpla incluso si la interacción se inserta desde fuera del backend.
-- --------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_interaccion_actualiza_scoring;
DELIMITER //
CREATE TRIGGER trg_interaccion_actualiza_scoring
AFTER INSERT ON INTERACCION_MARKETING
FOR EACH ROW
BEGIN
    UPDATE PROSPECTO
    SET puntuacion = puntuacion + NEW.peso_scoring
    WHERE id_prospecto = NEW.id_prospecto;

    UPDATE PROSPECTO
    SET estado = 'Calificado'
    WHERE id_prospecto = NEW.id_prospecto
      AND puntuacion >= 15
      AND estado IN ('Pendiente', 'Contactado');
END//
DELIMITER ;


-- --------------------------------------------------------------------
-- TRIGGER 2: trg_propuesta_aceptada_promueve_prospecto
-- AFTER UPDATE en PROPUESTA.
-- Cuando una propuesta cambia a 'Aceptada', el prospecto pasa a
-- 'Convertido' automáticamente. Cumple "actualizar estado de propuesta"
-- del enunciado de la sesión 3.
-- --------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_propuesta_aceptada_promueve_prospecto;
DELIMITER //
CREATE TRIGGER trg_propuesta_aceptada_promueve_prospecto
AFTER UPDATE ON PROPUESTA
FOR EACH ROW
BEGIN
    IF OLD.estado <> 'Aceptada' AND NEW.estado = 'Aceptada' THEN
        UPDATE PROSPECTO
        SET estado = 'Convertido'
        WHERE id_prospecto = NEW.id_prospecto
          AND estado <> 'Convertido';
    END IF;
END//
DELIMITER ;


-- --------------------------------------------------------------------
-- TRIGGER 3: trg_prospecto_inadecuado_resetea_score
-- BEFORE UPDATE en PROSPECTO.
-- Si un prospecto se marca 'Inadecuado', su puntuación queda en 0 a
-- nivel BD aunque la aplicación olvide resetearla.
-- --------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_prospecto_inadecuado_resetea_score;
DELIMITER //
CREATE TRIGGER trg_prospecto_inadecuado_resetea_score
BEFORE UPDATE ON PROSPECTO
FOR EACH ROW
BEGIN
    IF NEW.estado = 'Inadecuado' AND OLD.estado <> 'Inadecuado' THEN
        SET NEW.puntuacion = 0;
    END IF;
END//
DELIMITER ;


-- --------------------------------------------------------------------
-- TRIGGER 4: trg_audit_estado_prospecto
-- AFTER UPDATE en PROSPECTO.
-- Cada cambio de estado de un prospecto se registra como un REPORTE
-- de tipo 'Auditoria Estado Prospecto'. Reusamos la tabla REPORTE en
-- vez de crear una tabla nueva. El campo `resultado` guarda los datos
-- como JSON para poder consultarlos desde el backend.
-- --------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_audit_estado_prospecto;
DELIMITER //
CREATE TRIGGER trg_audit_estado_prospecto
AFTER UPDATE ON PROSPECTO
FOR EACH ROW
BEGIN
    IF OLD.estado <> NEW.estado THEN
        INSERT INTO REPORTE (
            tipo_reporte, fecha_generacion, periodo_inicio, periodo_fin,
            resultado, id_campana
        ) VALUES (
            'Auditoria Estado Prospecto',
            NOW(),
            CURDATE(),
            CURDATE(),
            JSON_OBJECT(
                'id_prospecto',     NEW.id_prospecto,
                'estado_anterior',  OLD.estado,
                'estado_nuevo',     NEW.estado,
                'puntuacion',       NEW.puntuacion
            ),
            NEW.id_campana_origen
        );
    END IF;
END//
DELIMITER ;


-- =====================================================================
-- PROCEDIMIENTOS ALMACENADOS
-- =====================================================================

-- --------------------------------------------------------------------
-- SP 1: sp_reporte_mensual_ventas(p_anio, p_mes)
-- Reporte mensual de ventas pagadas con totales y top campaña.
-- Persiste el resultado en la tabla REPORTE.
-- --------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_reporte_mensual_ventas;
DELIMITER //
CREATE PROCEDURE sp_reporte_mensual_ventas(
    IN p_anio INT,
    IN p_mes  INT
)
BEGIN
    DECLARE v_total_facturado DECIMAL(14,2) DEFAULT 0;
    DECLARE v_num_ventas      INT DEFAULT 0;
    DECLARE v_periodo_inicio  DATE;
    DECLARE v_periodo_fin     DATE;
    DECLARE v_top_campana     VARCHAR(100) DEFAULT NULL;
    DECLARE v_resumen         TEXT;

    IF p_mes < 1 OR p_mes > 12 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El mes debe estar entre 1 y 12';
    END IF;

    SET v_periodo_inicio = STR_TO_DATE(
        CONCAT(p_anio, '-', LPAD(p_mes, 2, '0'), '-01'),
        '%Y-%m-%d'
    );
    SET v_periodo_fin = LAST_DAY(v_periodo_inicio);

    SELECT COALESCE(SUM(monto), 0), COUNT(*)
    INTO v_total_facturado, v_num_ventas
    FROM VENTA
    WHERE estado = 'Pagada'
      AND fecha_venta BETWEEN v_periodo_inicio AND v_periodo_fin;

    SELECT c.nombre INTO v_top_campana
    FROM VENTA v
    JOIN CLIENTE   cl ON v.id_cliente = cl.id_cliente
    JOIN PROSPECTO p  ON cl.id_prospecto = p.id_prospecto
    JOIN CAMPANA   c  ON p.id_campana_origen = c.id_campana
    WHERE v.estado = 'Pagada'
      AND v.fecha_venta BETWEEN v_periodo_inicio AND v_periodo_fin
    GROUP BY c.id_campana, c.nombre
    ORDER BY SUM(v.monto) DESC
    LIMIT 1;

    SET v_resumen = CONCAT(
        'Ventas pagadas: ', v_num_ventas,
        ' | Facturado: $', FORMAT(v_total_facturado, 0), ' COP',
        ' | Top campaña: ', COALESCE(v_top_campana, 'N/A')
    );

    INSERT INTO REPORTE (
        tipo_reporte, fecha_generacion, periodo_inicio,
        periodo_fin, resultado
    ) VALUES (
        'Ventas Periodo (SP)', NOW(), v_periodo_inicio,
        v_periodo_fin, v_resumen
    );

    SELECT
        LAST_INSERT_ID()    AS id_reporte,
        v_periodo_inicio    AS periodo_inicio,
        v_periodo_fin       AS periodo_fin,
        v_total_facturado   AS total_facturado,
        v_num_ventas        AS num_ventas,
        v_top_campana       AS top_campana,
        v_resumen           AS resumen;
END//
DELIMITER ;


-- --------------------------------------------------------------------
-- SP 2: sp_extender_trial(p_id_prospecto, p_dias)
-- Extiende el periodo de prueba de un prospecto entre 1 y 90 días.
-- --------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_extender_trial;
DELIMITER //
CREATE PROCEDURE sp_extender_trial(
    IN p_id_prospecto INT,
    IN p_dias         INT
)
BEGIN
    DECLARE v_fecha_actual DATE;
    DECLARE v_nueva_fecha  DATE;
    DECLARE v_nombre       VARCHAR(100);

    IF p_dias <= 0 OR p_dias > 90 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La extensión debe estar entre 1 y 90 días';
    END IF;

    SELECT fecha_fin_prueba, nombre
    INTO v_fecha_actual, v_nombre
    FROM PROSPECTO
    WHERE id_prospecto = p_id_prospecto;

    IF v_fecha_actual IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El prospecto no tiene periodo de prueba activo';
    END IF;

    SET v_nueva_fecha = DATE_ADD(v_fecha_actual, INTERVAL p_dias DAY);

    UPDATE PROSPECTO
    SET fecha_fin_prueba = v_nueva_fecha
    WHERE id_prospecto = p_id_prospecto;

    SELECT
        p_id_prospecto    AS id_prospecto,
        v_nombre          AS nombre,
        v_fecha_actual    AS fecha_anterior,
        v_nueva_fecha     AS fecha_nueva,
        p_dias            AS dias_extendidos;
END//
DELIMITER ;


-- --------------------------------------------------------------------
-- SP 3: sp_marcar_trials_vencidos()
-- Marca como 'Inadecuado' a los prospectos cuyo trial venció y no son
-- ya clientes. Encadena los triggers de score y de auditoría.
-- --------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_marcar_trials_vencidos;
DELIMITER //
CREATE PROCEDURE sp_marcar_trials_vencidos()
BEGIN
    DECLARE v_afectados INT;

    UPDATE PROSPECTO
    SET estado = 'Inadecuado'
    WHERE fecha_fin_prueba IS NOT NULL
      AND fecha_fin_prueba < CURDATE()
      AND estado NOT IN ('Convertido', 'Inadecuado');

    SET v_afectados = ROW_COUNT();

    SELECT
        v_afectados   AS prospectos_marcados,
        CURDATE()     AS fecha_proceso;
END//
DELIMITER ;


-- =====================================================================
-- FUNCIONES UDF
-- =====================================================================

-- --------------------------------------------------------------------
-- UDF 1: fn_nivel_interes(p_puntuacion)
-- Devuelve 'Alto' / 'Medio' / 'Bajo' según el scoring del prospecto.
-- --------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_nivel_interes;
DELIMITER //
CREATE FUNCTION fn_nivel_interes(p_puntuacion INT)
RETURNS VARCHAR(10)
DETERMINISTIC
BEGIN
    IF p_puntuacion IS NULL THEN
        RETURN 'Bajo';
    ELSEIF p_puntuacion >= 15 THEN
        RETURN 'Alto';
    ELSEIF p_puntuacion >= 5 THEN
        RETURN 'Medio';
    ELSE
        RETURN 'Bajo';
    END IF;
END//
DELIMITER ;


-- --------------------------------------------------------------------
-- UDF 2: fn_dias_restantes_trial(p_id_prospecto)
-- Días que faltan para que termine el trial. NULL si no tiene trial,
-- negativo si ya venció.
-- --------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_dias_restantes_trial;
DELIMITER //
CREATE FUNCTION fn_dias_restantes_trial(p_id_prospecto INT)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_fecha DATE;

    SELECT fecha_fin_prueba INTO v_fecha
    FROM PROSPECTO
    WHERE id_prospecto = p_id_prospecto;

    IF v_fecha IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN DATEDIFF(v_fecha, CURDATE());
END//
DELIMITER ;


-- --------------------------------------------------------------------
-- UDF 3: fn_lifetime_value(p_id_cliente)
-- Suma de las ventas pagadas del cliente.
-- --------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_lifetime_value;
DELIMITER //
CREATE FUNCTION fn_lifetime_value(p_id_cliente INT)
RETURNS DECIMAL(14,2)
READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(14,2);
    SELECT COALESCE(SUM(monto), 0) INTO v_total
    FROM VENTA
    WHERE id_cliente = p_id_cliente
      AND estado = 'Pagada';
    RETURN v_total;
END//
DELIMITER ;


-- =====================================================================
-- REFRESCO DE FECHAS DE PRUEBA
-- Las fechas estáticas de los INSERT iniciales ya pasaron respecto a
-- hoy. Ajustamos 5 prospectos para que el dashboard muestre "Trials
-- por vencer" > 0 al abrir la app. Estos UPDATEs no cambian el estado
-- del prospecto, por lo cual el trigger de auditoría no se dispara.
-- =====================================================================
UPDATE PROSPECTO
SET fecha_inicio_prueba = DATE_SUB(CURDATE(), INTERVAL 55 DAY),
    fecha_fin_prueba    = DATE_ADD(CURDATE(), INTERVAL 5  DAY)
WHERE id_prospecto = 3;

UPDATE PROSPECTO
SET fecha_inicio_prueba = DATE_SUB(CURDATE(), INTERVAL 58 DAY),
    fecha_fin_prueba    = DATE_ADD(CURDATE(), INTERVAL 2  DAY)
WHERE id_prospecto = 5;

UPDATE PROSPECTO
SET fecha_inicio_prueba = DATE_SUB(CURDATE(), INTERVAL 53 DAY),
    fecha_fin_prueba    = DATE_ADD(CURDATE(), INTERVAL 7  DAY)
WHERE id_prospecto = 8;

UPDATE PROSPECTO
SET fecha_inicio_prueba = DATE_SUB(CURDATE(), INTERVAL 56 DAY),
    fecha_fin_prueba    = DATE_ADD(CURDATE(), INTERVAL 4  DAY)
WHERE id_prospecto = 11;

UPDATE PROSPECTO
SET fecha_inicio_prueba = DATE_SUB(CURDATE(), INTERVAL 59 DAY),
    fecha_fin_prueba    = DATE_ADD(CURDATE(), INTERVAL 1  DAY)
WHERE id_prospecto = 17;


-- =====================================================================
-- FIN DEL SCRIPT.
-- Validaciones post-ejecución:
--   SELECT COUNT(*) FROM PROSPECTO;                          -- 31
--   SELECT COUNT(*) FROM CLIENTE;                            -- 31
--   SELECT COUNT(*) FROM VENTA;                              -- 31
--   SHOW TRIGGERS;                                            -- 4 triggers
--   SHOW PROCEDURE STATUS WHERE Db = 'zimbra_crm';            -- 3 SPs
--   SHOW FUNCTION STATUS  WHERE Db = 'zimbra_crm';            -- 3 UDFs
--   SELECT fn_nivel_interes(20);                              -- 'Alto'
--   CALL sp_reporte_mensual_ventas(2026, 5);
-- =====================================================================