from fpdf import FPDF
import requests
import os
import tempfile
from urllib.parse import urlparse

# Asegurar que el directorio pdfs existe
os.makedirs("pdfs", exist_ok=True)

# Crear una función para generar un PDF con formato profesional
def generar_cv(nombre, apellido, profesion, contacto, educacion, idiomas, habilidades, experiencia, publicaciones, proyectos, certificaciones, referencias, foto_url, output_path):
    # Reemplazar caracteres problemáticos
    habilidades = habilidades.replace('•', '-')
    experiencia = [exp.replace('•', '-') for exp in experiencia]
    proyectos = [proy.replace('•', '-') for proy in proyectos]
    referencias = [ref.replace('•', '-') for ref in referencias]
    publicaciones = publicaciones.replace('•', '-')
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Descargar y agregar foto desde URL
    temp_img = None
    try:
        response = requests.get(foto_url, stream=True)
        if response.status_code == 200:
            # Crear un archivo temporal para guardar la imagen
            file_extension = os.path.splitext(urlparse(foto_url).path)[1] or ".jpg"
            temp_img = tempfile.NamedTemporaryFile(suffix=file_extension, delete=False)
            temp_img.write(response.content)
            temp_img.close()
            
            # Agregar la imagen al PDF
            pdf.image(temp_img.name, x=150, y=10, w=40)
        else:
            print(f"No se pudo descargar la imagen desde {foto_url}")
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
    
    # Nombre y profesión
    pdf.cell(0, 10, f"{nombre} {apellido}", ln=True, align="L")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, profesion, ln=True, align="L")
    pdf.ln(10)
    
    # Contacto
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Contacto", ln=True)
    pdf.set_font("Arial", "", 11)
    for line in contacto:
        pdf.cell(0, 6, line, ln=True)
    pdf.ln(5)
    
    # Educación
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Educación", ln=True)
    pdf.set_font("Arial", "", 11)
    for line in educacion:
        pdf.cell(0, 6, line, ln=True)
    pdf.ln(5)
    
    # Idiomas
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Idiomas", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, idiomas)
    pdf.ln(5)
    
    # Habilidades
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Habilidades", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, habilidades)
    pdf.ln(5)
    
    # Experiencia
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Experiencia Profesional", ln=True)
    pdf.set_font("Arial", "", 11)
    for line in experiencia:
        pdf.multi_cell(0, 6, line)
        pdf.ln(3)
    pdf.ln(5)
    
    # Publicaciones
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Publicaciones", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, publicaciones)
    pdf.ln(5)
    
    # Proyectos
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Proyectos", ln=True)
    pdf.set_font("Arial", "", 11)
    for proyecto in proyectos:
        pdf.multi_cell(0, 6, proyecto)
        pdf.ln(3)
    pdf.ln(5)
    
    # Certificaciones
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Certificaciones", ln=True)
    pdf.set_font("Arial", "", 11)
    for cert in certificaciones:
        pdf.cell(0, 6, cert, ln=True)
    pdf.ln(5)
    
    # Referencias
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Referencias", ln=True)
    pdf.set_font("Arial", "", 11)
    for ref in referencias:
        pdf.multi_cell(0, 6, ref)
        pdf.ln(3)
    
    # Guardar el PDF
    pdf.output(output_path)
    
    # Eliminar el archivo temporal de la imagen si existe
    if temp_img and os.path.exists(temp_img.name):
        os.unlink(temp_img.name)


# Datos para Miguel Ángel Torres - Perfil de Mecánico Experto
nombre3 = "Miguel Ángel"
apellido3 = "Torres Ramírez"
profesion3 = "Jefe de Taller | Especialista en Mecánica Automotriz | Formador Técnico"
contacto3 = [
    "Valencia, España", 
    "+34 645 78 90 12", 
    "miguelangel.torres@tallermotors.es", 
    "LinkedIn: /miguelangel-torres-mecanico",
    "Instagram: @maestro_mecanico",
    "Canal YouTube: youtube.com/c/MiguelAngelMecanica"
]
educacion3 = [
    "Técnico Superior en Automoción - IES Politécnico de Valencia (2000-2002)",
    "Formación Profesional en Electromecánica de Vehículos - Centro de FP San José (1998-2000)",
    "Máster en Gestión de Talleres Automotrices - CEAC (2005-2006)",
]
idiomas3 = "Español - Nativo\nValenciano - Nativo\nInglés - B2\nAlemán - A2"
habilidades3 = """- Mecánica general: Motores, transmisiones, sistemas de frenos, suspensión, dirección
- Electrónica automotriz: Diagnosis con equipos multimarca, programación de centralitas
- Sistemas avanzados: Vehículos híbridos, eléctricos, sistemas ADAS, conducción autónoma
- Herramientas especializadas: Osciloscopios, analizadores de gases, alineadoras 3D"""
experiencia3 = [
    "Jefe de Taller - Talleres Motors Valencia (2015-Presente)\nDirección técnica y gestión integral del taller multimarca con especialización en vehículos premium. Supervisión de un equipo de 12 mecánicos. Implementación de procesos de calidad y mejora continua.\n• Incremento del 40% en la facturación anual en 5 años\n• Reducción del tiempo medio de reparación en un 25%\n• Implementación de un sistema de gestión digital que aumentó la eficiencia en un 35%\n• Desarrollo de un programa de fidelización que incrementó las revisiones periódicas en un 60%",
    
    "Mecánico Especialista - Concesionario Oficial Volkswagen-Audi (2008-2015)\nDiagnóstico y reparación de vehículos del grupo VAG. Especialización en sistemas electrónicos y cajas de cambio DSG. Formación de mecánicos junior.\n• Resolución de más de 200 casos complejos de diagnóstico electrónico\n• Desarrollo de procedimientos específicos para la reparación de cajas DSG\n• Participación en el programa de control de calidad con valoración de excelencia\n• Formación técnica a más de 30 mecánicos de la red de concesionarios",
]
publicaciones3 = """- "Guía práctica para el diagnóstico de averías en vehículos híbridos" - Revista Técnica del Automóvil (2022)
- "El futuro de los talleres ante la llegada masiva de vehículos eléctricos" - Autoprofesional (2021)
- "Procedimientos de calibración de sistemas ADAS: retos y soluciones" - InfoTaller (2020)"""
proyectos3 = [
    "Taller 4.0 (2021-Presente)\nImplementación de un sistema integral de gestión digital del taller con diagnóstico remoto, citas online y seguimiento en tiempo real de reparaciones.\n• Reducción del 50% en tiempos de espera para los clientes\n• Aumento de la satisfacción del cliente en un 35%\n• Optimización de la carga de trabajo y recursos humanos",
    
    "Academia del Motor (2019-Presente)\nCreación de una plataforma de formación online y presencial para mecánicos y aficionados a la mecánica automotriz.\n• Más de 5,000 alumnos formados en 3 años\n• Desarrollo de 25 cursos especializados con certificación propia\n• Colaboración con 15 talleres para prácticas profesionales",
    
    "EcoTaller (2017-2019)\nProyecto de transformación del taller hacia prácticas más sostenibles y respetuosas con el medio ambiente.\n• Reducción del 70% en residuos contaminantes\n• Implementación de un sistema de reciclaje de piezas y fluidos\n• Obtención de la certificación ISO 14001 de gestión ambiental",
    
    "DiagnosisVR (2016-2018)\nDesarrollo de un sistema de formación en diagnosis mediante realidad virtual para estudiantes de mecánica.\n• Creación de 30 escenarios virtuales de diagnóstico\n• Implementación en 5 centros de formación profesional\n• Reducción del 40% en el tiempo de aprendizaje práctico"
]
certificaciones3 = [
    "Master Technician - Grupo Volkswagen Audi (2019)",
    "Especialista en Vehículos Eléctricos e Híbridos - Tesla (2018)",
    "Técnico Certificado en Sistemas ADAS - Bosch (2020)",
    "Experto en Diagnosis Avanzada - Launch Tech (2017)",
    "Certificación en Gestión de Talleres Automotrices - CEAC (2016)",
    "Técnico Especialista en Cajas de Cambio DSG - ZF (2014)",
    "Certificado de Aptitud Profesional para Formadores - Ministerio de Educación (2015)"
]
referencias3 = [
    "Antonio Martínez - Director de Posventa, Grupo Automóviles Valencia\nEmail: antonio.martinez@grupoauto.com | Teléfono: +34 96 345 6789",
    "Dra. Carmen Sánchez - Directora del Centro de FP San José\nEmail: carmen.sanchez@fpsanjose.es | Teléfono: +34 96 234 5678",
    "Javier Ruiz - Responsable de Formación Técnica, Volkswagen España\nEmail: javier.ruiz@volkswagen.es | Teléfono: +34 91 348 8765",
    "Roberto García - Propietario de Talleres Rodríguez\nEmail: roberto.garcia@talleresrodriguez.es | Teléfono: +34 96 567 8901"
]
foto_url3 = "https://img.freepik.com/foto-gratis/mecanico-automoviles-guapo-taller_1303-22911.jpg"
output_path3 = "pdfs/Miguel_Angel_Torres_CV.pdf"

# Datos para Laura Mendoza - Perfil de Piloto Principiante
nombre4 = "Laura"
apellido4 = "Mendoza Ortiz"
profesion4 = "Piloto Comercial | Licencia ATPL Reciente | Especialista en Operaciones Aéreas"
contacto4 = [
    "Madrid, España", 
    "+34 678 90 12 34", 
    "laura.mendoza@pilotos.net", 
    "LinkedIn: /laura-mendoza-piloto",
    "Twitter: @laura_en_vuelo",
    "Blog: aventurasdeunanovapiloto.com"
]
educacion4 = [
    "Licencia de Piloto de Transporte de Línea Aérea (ATPL) - FTO European Flight Academy (2021-2023)",
    "Grado en Ingeniería Aeroespacial - Universidad Politécnica de Madrid (2017-2021)",
    "Curso de Gestión de Recursos de Cabina (CRM) - CAE (2023)",
    "Certificación en Meteorología Aeronáutica Avanzada - AEMET (2022)",
    "Curso de Inglés Aeronáutico - Aviation English Services (2022)",
    "Formación en Simulador A320 - Airbus Training Center (2023)"
]
idiomas4 = "Español - Nativo\nInglés - C1 (ICAO Level 5)\nFrancés - B1\nItaliano - A2"
habilidades4 = """- Pilotaje: Monomotores, bimotores, instrumentos, navegación, procedimientos de emergencia
- Aeronaves: Experiencia en Cessna 152/172, Piper PA-28, Diamond DA42, simulador A320
- Navegación: Sistemas tradicionales, GPS, FMS, planificación de rutas, cartas aeronáuticas
- Comunicaciones: Fraseología aeronáutica estándar, comunicaciones de emergencia
- Meteorología: Interpretación de METAR, TAF, cartas significativas, radar meteorológico
- Conocimientos técnicos: Sistemas de aeronaves, aerodinámica, performance, limitaciones
- Normativa: Regulaciones EASA, procedimientos operacionales, documentación de vuelo
- Gestión de recursos: CRM, toma de decisiones, gestión del estrés, trabajo en equipo
- Herramientas digitales: EFB, software de planificación de vuelo, simuladores
- Seguridad aérea: Procedimientos de emergencia, gestión de riesgos, factores humanos"""
experiencia4 = [
    "Piloto en Prácticas - Iberia Express (2023-Presente)\nPrograma de incorporación para nuevos pilotos. Observación y aprendizaje en operaciones reales. Familiarización con procedimientos de la aerolínea y cultura de seguridad.\n• Participación en más de 200 horas de vuelo como observador\n• Asistencia en la preparación de vuelos y briefings\n• Participación en sesiones de simulador bajo supervisión\n• Formación continua en procedimientos operacionales",
    
    "Instructora Asistente - European Flight Academy (2022-2023)\nColaboración en la formación de nuevos pilotos. Asistencia en clases teóricas y briefings prevuelo. Supervisión de estudiantes en simuladores básicos.\n• Participación en la formación de más de 30 estudiantes de piloto\n• Desarrollo de materiales didácticos para navegación y meteorología\n• Asistencia en 150 horas de instrucción en simulador\n• Colaboración en la revisión y actualización de procedimientos de formación",
    
    "Piloto en Formación - European Flight Academy (2021-2022)\nFormación práctica intensiva para la obtención de licencias PPL, CPL, IR y ATPL. Acumulación de horas de vuelo y experiencia en diferentes condiciones.\n• Completado 215 horas de vuelo en diferentes aeronaves\n• Realización de vuelos de navegación por toda Europa\n• Entrenamiento en condiciones meteorológicas adversas\n• Calificación con distinción en pruebas de vuelo y exámenes teóricos",
    
    "Becaria - Departamento de Operaciones, Air Europa (2020-2021)\nColaboración en el departamento de operaciones durante estudios universitarios. Asistencia en planificación de vuelos, análisis de rutas y eficiencia operacional.\n• Participación en el análisis de eficiencia de rutas que generó un ahorro del 3% en combustible\n• Colaboración en la actualización de manuales operacionales\n• Asistencia en la implementación de un nuevo software de planificación de vuelos\n• Desarrollo de una herramienta para optimizar la rotación de tripulaciones"
]
publicaciones4 = """- "Mi camino hacia la cabina de mando: Experiencias de una piloto novata" - Blog personal (2023-Presente)
- "Desafíos meteorológicos en la aviación comercial moderna" - Revista Aviador (2023)
- "La importancia del CRM en la formación inicial de pilotos" - Portal Aviación Digital (2022)
- "Análisis comparativo de sistemas de navegación en aviación general" - Trabajo Fin de Grado (2021)
- "El futuro de la aviación sostenible: retos y oportunidades" - Congreso de Jóvenes Ingenieros Aeroespaciales (2020)
- "La mujer en la aviación comercial: avances y desafíos pendientes" - Blog Mujeres en Vuelo (2019)"""
proyectos4 = [
    "Mentoring Aéreo (2023-Presente)\nPrograma de mentoría para estudiantes de piloto, especialmente mujeres, con orientación sobre formación y desarrollo profesional.\n• Mentoría a 15 estudiantes de piloto\n• Organización de 5 webinars sobre carrera profesional en aviación\n• Creación de una red de apoyo con más de 100 miembros",
    
    "Simuladores Accesibles (2022-2023)\nProyecto para facilitar el acceso a simuladores de vuelo a estudiantes con recursos limitados mediante sesiones gratuitas y materiales de estudio.\n• Organización de 30 sesiones gratuitas de simulador\n• Desarrollo de materiales de estudio para preparación de vuelos\n• Colaboración con 3 escuelas de vuelo para becas de formación",
    
    "Eco-Flying (2021-2022)\nInvestigación sobre técnicas de pilotaje eficiente para reducir el consumo de combustible y emisiones en aviación general.\n• Análisis de datos de más de 100 vuelos\n• Desarrollo de un manual de técnicas de pilotaje eficiente\n• Reducción media del 8% en consumo de combustible en vuelos de prueba",
    
    "Aviation Safety Podcast (2020-Presente)\nCreación y producción de un podcast en español sobre seguridad aérea, análisis de incidentes y cultura de seguridad.\n• Producción de 45 episodios con más de 50,000 descargas\n• Entrevistas a 20 profesionales de la industria\n• Colaboración con la Agencia Estatal de Seguridad Aérea para episodios especiales"
]
certificaciones4 = [
    "Licencia de Piloto de Transporte de Línea Aérea (ATPL) - EASA (2023)",
    "Habilitación de Vuelo Instrumental (IR) - EASA (2022)",
    "Licencia de Piloto Comercial (CPL) - EASA (2022)",
    "Certificado Médico Clase 1 - EASA (2023)",
    "Certificación de Inglés Aeronáutico ICAO Nivel 5 (2022)",
    "Certificado de Operador de Radiofonía Aeronáutica (2021)",
    "Habilitación de Clase MEP (Multi-Engine Piston) (2022)"
]
referencias4 = [
    "Capitán Carlos Vega - Instructor Jefe, European Flight Academy\nEmail: carlos.vega@euroflight.com | Teléfono: +34 91 789 0123",
    "Dra. Elena Martín - Directora del Grado en Ingeniería Aeroespacial, UPM\nEmail: elena.martin@upm.es | Teléfono: +34 91 336 7890",
    "Manuel Sánchez - Director de Operaciones, Iberia Express\nEmail: manuel.sanchez@iberiaexpress.com | Teléfono: +34 91 567 8901",
    "Ana López - Capitán A320, Air Europa\nEmail: ana.lopez@aireuropa.com | Teléfono: +34 91 401 6789"
]
foto_url4 = "https://img.freepik.com/foto-gratis/retrato-piloto-mujer-uniforme_23-2149338352.jpg"
output_path4 = "pdfs/Laura_Mendoza_CV.pdf"

# Datos para Dr. Javier Moreno - Perfil de Médico
nombre5 = "Javier"
apellido5 = "Moreno Sánchez"
profesion5 = "Médico Especialista en Cardiología"
contacto5 = [
    "Sevilla, España", 
    "+34 633 45 67 89", 
    "dr.javier.moreno@hospitaluniversitario.es"
]
educacion5 = [
    "Especialidad en Cardiología - Hospital Universitario Virgen del Rocío (2015-2019)",
    "Licenciatura en Medicina - Universidad de Sevilla (2007-2013)"
]
idiomas5 = "Español - Nativo\nInglés - C1"
habilidades5 = """- Cardiología clínica: Diagnóstico y tratamiento cardiovascular
- Técnicas diagnósticas: Ecocardiografía, electrocardiografía
- Investigación clínica: Diseño de estudios, publicación científica
- Urgencias cardiológicas: Manejo del síndrome coronario agudo"""
experiencia5 = [
    "Cardiólogo Adjunto - Hospital Universitario Virgen del Rocío (2019-Presente)\nAtención a pacientes con patologías cardiovasculares. Realización de pruebas diagnósticas especializadas.",
    
    "Investigador Clínico - Instituto de Biomedicina de Sevilla (2017-Presente)\nParticipación en estudios sobre cardiopatía isquémica y factores de riesgo cardiovascular.",
    
    "Médico Residente - Hospital Universitario Virgen del Rocío (2015-2019)\nFormación especializada en cardiología. Rotaciones por diferentes unidades."
]
publicaciones5 = """- "Impacto de los nuevos anticoagulantes en la prevención del ictus" - Revista Española de Cardiología (2022)
- "Factores predictores de reestenosis tras angioplastia coronaria" - European Heart Journal (2021)"""
proyectos5 = [
    "CARDIORISK (2021-Presente)\nEstudio multicéntrico sobre nuevos factores de riesgo cardiovascular.",
    
    "Programa de Telemedicina Cardíaca (2020-Presente)\nImplementación de un sistema de seguimiento remoto para pacientes con insuficiencia cardíaca."
]
certificaciones5 = [
    "Certificación en Ecocardiografía Avanzada - Sociedad Española de Cardiología (2020)",
    "Acreditación en Soporte Vital Avanzado - Consejo Español de RCP (2021)"
]
referencias5 = [
    "Dr. Antonio Fernández - Jefe de Servicio de Cardiología, Hospital Virgen del Rocío\nEmail: antonio.fernandez@hospitalvr.es"
]
foto_url5 = "https://img.freepik.com/foto-gratis/doctor-brazos-cruzados-sobre-fondo-blanco_1368-5790.jpg"
output_path5 = "pdfs/Javier_Moreno_CV.pdf"

# Datos para Elena Vázquez - Perfil de Arquitecta
nombre6 = "Elena"
apellido6 = "Vázquez Martín"
profesion6 = "Arquitecta | Especialista en Diseño Sostenible"
contacto6 = [
    "Barcelona, España", 
    "+34 622 33 44 55", 
    "elena.vazquez@estudioarquitectura.com"
]
educacion6 = [
    "Máster en Arquitectura Sostenible - Universidad Politécnica de Cataluña (2016-2018)",
    "Grado en Arquitectura - Universidad Politécnica de Cataluña (2010-2016)"
]
idiomas6 = "Español - Nativo\nCatalán - Nativo\nInglés - C1"
habilidades6 = """- Diseño arquitectónico: Proyectos residenciales y comerciales
- Arquitectura sostenible: Certificación LEED, Passivhaus
- Rehabilitación: Restauración de edificios, mejora energética
- Software: AutoCAD, Revit, SketchUp, Rhinoceros"""
experiencia6 = [
    "Socia Fundadora - Estudio Vázquez Arquitectura (2020-Presente)\nDirección de estudio especializado en diseño sostenible. Desarrollo de proyectos residenciales.",
    
    "Arquitecta Senior - BCN Arquitectos Asociados (2018-2020)\nDesarrollo de proyectos de edificación y urbanismo. Especialización en certificaciones ambientales.",
    
    "Arquitecta Junior - Estudio Martínez & Asociados (2016-2018)\nColaboración en proyectos de edificación. Desarrollo de planos técnicos y modelado 3D."
]
publicaciones6 = """- "Estrategias pasivas en la arquitectura mediterránea" - Revista Arquitectura Viva (2022)
- "Rehabilitación energética en edificios históricos" - Tectónica (2021)"""
proyectos6 = [
    "Eco-Barrio La Marina (2021-Presente)\nDiseño urbano para un desarrollo residencial sostenible.",
    
    "Rehabilitación Edificio Modernista (2020-2021)\nRestauración y mejora energética de un edificio catalogado del siglo XIX."
]
certificaciones6 = [
    "Arquitecta colegiada - COAC (Colegio Oficial de Arquitectos de Cataluña)",
    "Certificación LEED AP (Accredited Professional)"
]
referencias6 = [
    "Arq. Javier Torres - Director, BCN Arquitectos Asociados\nEmail: javier.torres@bcnarquitectos.com"
]
foto_url6 = "https://img.freepik.com/foto-gratis/arquitecto-mujer-oficina_23-2148176676.jpg"
output_path6 = "pdfs/Elena_Vazquez_CV.pdf"

# Datos para Pedro Gómez - Perfil de Jardinero
nombre7 = "Pedro"
apellido7 = "Gómez Ruiz"
profesion7 = "Jardinero Profesional | Paisajista"
contacto7 = [
    "Granada, España", 
    "+34 655 78 90 12", 
    "pedro.gomez@jardinesverdes.es"
]
educacion7 = [
    "Técnico Superior en Paisajismo y Medio Rural - IES Aynadamar (2015-2017)",
    "Formación Profesional en Jardinería - Centro de FP Agraria (2013-2015)"
]
idiomas7 = "Español - Nativo\nInglés - B1"
habilidades7 = """- Diseño de jardines: Planificación y selección de especies
- Técnicas de jardinería: Plantación, poda, injertos, mantenimiento
- Sistemas de riego: Instalación de riego por goteo y aspersión
- Jardinería sostenible: Xerojardinería, jardines autóctonos"""
experiencia7 = [
    "Propietario - Jardines Verdes (2019-Presente)\nCreación y gestión de empresa de jardinería. Diseño e instalación de jardines residenciales.",
    
    "Jardinero - Ayuntamiento de Granada (2017-2019)\nMantenimiento de parques y jardines públicos. Plantación y cuidado de árboles urbanos.",
    
    "Ayudante de Jardinería - Viveros El Edén (2015-2017)\nAtención a clientes y asesoramiento sobre plantas. Cuidado de plantas en vivero."
]
publicaciones7 = """- "Guía práctica de plantas autóctonas para jardines mediterráneos" - Blog Jardines Verdes (2022)
- "Técnicas de ahorro de agua en jardinería residencial" - Revista Verde Urbano (2021)"""
proyectos7 = [
    "Jardín Botánico Urbano (2022-Presente)\nDiseño de un jardín botánico educativo con especies autóctonas.",
    
    "Jardines Terapéuticos (2020-2021)\nDiseño de jardines sensoriales para residencias de ancianos."
]
certificaciones7 = [
    "Técnico Superior en Paisajismo y Medio Rural",
    "Certificado de Aplicador de Productos Fitosanitarios - Nivel Cualificado"
]
referencias7 = [
    "Ana Martínez - Jefa de Parques y Jardines, Ayuntamiento de Granada\nEmail: ana.martinez@granada.es"
]
foto_url7 = "https://img.freepik.com/foto-gratis/jardinero-masculino-maduro-que-trabaja-jardin_1301-6983.jpg"
output_path7 = "pdfs/Pedro_Gomez_CV.pdf"

# Datos para Sara Díaz - Perfil de Policía
nombre8 = "Sara"
apellido8 = "Díaz Navarro"
profesion8 = "Oficial de Policía Nacional"
contacto8 = [
    "Valencia, España", 
    "+34 644 56 78 90", 
    "sara.diaz@policia.es"
]
educacion8 = [
    "Academia de Policía Nacional - División de Formación (2015-2016)",
    "Grado en Criminología - Universidad de Valencia (2011-2015)"
]
idiomas8 = "Español - Nativo\nValenciano - Nativo\nInglés - B2"
habilidades8 = """- Seguridad ciudadana: Patrullaje y prevención del delito
- Atención al ciudadano: Recepción de denuncias e información
- Mediación: Resolución de conflictos
- Primeros auxilios: RCP y atención inicial"""
experiencia8 = [
    "Oficial de Policía - Comisaría de Distrito Centro, Valencia (2020-Presente)\nServicio de seguridad ciudadana en zona urbana. Coordinación de equipos de patrulla.",
    
    "Agente de Policía - Unidad de Prevención y Reacción, Valencia (2018-2020)\nParticipación en dispositivos especiales de seguridad. Prevención del orden público.",
    
    "Agente de Policía - Comisaría de Distrito Marítimo, Valencia (2016-2018)\nPatrullaje preventivo en zona turística. Atención a denuncias."
]
publicaciones8 = """- "La importancia de la policía de proximidad" - Revista Policía y Seguridad Pública (2022)
- "Estrategias de prevención del delito" - Boletín Interno CNP (2021)"""
proyectos8 = [
    "Comercio Seguro (2021-Presente)\nPrograma de colaboración con comerciantes para prevención de hurtos.",
    
    "Policía en las Escuelas (2020-Presente)\nPrograma educativo sobre seguridad y prevención del acoso escolar."
]
certificaciones8 = [
    "Oficial de Policía Nacional - Escala Básica",
    "Certificación en Mediación Policial - UNED"
]
referencias8 = [
    "Comisario Javier Martínez - Jefe de Comisaría Distrito Centro\nEmail: javier.martinez@policia.es"
]
foto_url8 = "https://img.freepik.com/foto-gratis/policia-mujer-posando-uniforme_23-2148786614.jpg"
output_path8 = "pdfs/Sara_Diaz_CV.pdf"

# Datos para Alejandro Mora - Perfil de Programador
nombre1 = "Alejandro"
apellido1 = "Mora Fernández"
profesion1 = "Desarrollador Full Stack | Especialista en Inteligencia Artificial"
contacto1 = [
    "Madrid, España", 
    "+34 612 45 78 90", 
    "alejandro.dev@gmail.com", 
    "LinkedIn: /alejandromf-dev",
    "GitHub: github.com/alejandromf-dev",
    "Portfolio: alejandromora.dev"
]
educacion1 = [
    "Grado en Ingeniería Informática - Universidad Complutense de Madrid (2018-2022)",
    "Curso de Especialización en Inteligencia Artificial - Universidad Politécnica de Madrid (2022-2023)"
]
idiomas1 = "Español - Nativo\nInglés - C1"
habilidades1 = """- Desarrollo de aplicaciones web: JavaScript, React, Node.js
- Desarrollo de aplicaciones móviles: Flutter, Dart
- Desarrollo de aplicaciones de escritorio: Python, PyQt
- Desarrollo de aplicaciones de base de datos: SQL, NoSQL
- Desarrollo de aplicaciones de inteligencia artificial: TensorFlow, PyTorch"""
experiencia1 = [
    "Desarrollador Full Stack - StartUp Tech (2022-Presente)\nDesarrollo de aplicaciones web y móviles. Implementación de sistemas de inteligencia artificial.",
    
    "Desarrollador de Software - Proyecto Final de Grado (2022)\nDesarrollo de una aplicación de gestión de tareas con IA.",
    
    "Desarrollador de Software - Proyecto de Empresa (2021)\nDesarrollo de una aplicación de gestión de recursos humanos."
]
publicaciones1 = """- "Desarrollo de aplicaciones de inteligencia artificial" - Revista Tecnológica (2023)
- "Inteligencia artificial en la gestión de recursos humanos" - Revista de Recursos Humanos (2022)"""
proyectos1 = [
    "StartUp Tech (2022-Presente)\nDesarrollo de aplicaciones web y móviles. Implementación de sistemas de inteligencia artificial.",
    
    "Proyecto Final de Grado (2022)\nDesarrollo de una aplicación de gestión de tareas con IA.",
    
    "Proyecto de Empresa (2021)\nDesarrollo de una aplicación de gestión de recursos humanos."
]
certificaciones1 = [
    "Certificado de Especialización en Inteligencia Artificial - Universidad Politécnica de Madrid (2023)",
    "Certificado de Desarrollador Full Stack - StartUp Tech (2022)"
]
referencias1 = [
    "Dr. Juan Pérez - Jefe de Departamento de Informática, Universidad Complutense de Madrid\nEmail: juan.perez@ucm.es"
]
foto_url1 = "https://img.freepik.com/foto-gratis/programador-mujer-oficina_23-2148176677.jpg"
output_path1 = "pdfs/Alejandro_Mora_CV.pdf"

# Datos para Carla Rodríguez - Perfil de Bióloga
nombre2 = "Carla"
apellido2 = "Rodríguez López"
profesion2 = "Bióloga Marina | Investigadora en Conservación de Ecosistemas Marinos"
contacto2 = [
    "Barcelona, España", 
    "+34 689 12 34 56", 
    "carla.rodriguez@cienciasmarina.org", 
    "LinkedIn: /carla-rodriguez-biologa",
    "ResearchGate: researchgate.net/profile/Carla_Rodriguez",
    "ORCID: 0000-0002-1234-5678"
]
educacion2 = [
    "Grado en Biología - Universidad de Barcelona (2015-2019)",
    "Máster en Ciencias Marinas - Universidad de Barcelona (2019-2021)",
    "Doctorado en Ciencias Marinas - Universidad de Barcelona (2021-Presente)"
]
idiomas2 = "Español - Nativo\nCatalán - Nativo\nInglés - C1"
habilidades2 = """- Investigación científica: Diseño de experimentos, análisis de datos
- Conservación de ecosistemas marinos: Monitoreo, evaluación, gestión
- Biodiversidad: Identificación, conservación, restauración de especies marinas
- Ecología: Interacciones entre organismos y su entorno"""
experiencia2 = [
    "Investigadora - Centro de Investigación en Ciencias Marinas (2019-Presente)\nDesarrollo de proyectos de investigación en áreas marinas.",
    
    "Colaboradora - Proyecto de Conservación de Especies Marinas (2019-2021)\nParticipación en la identificación y conservación de especies marinas.",
    
    "Becaria - Instituto de Investigación en Ciencias Marinas (2015-2019)\nColaboración en proyectos de investigación en áreas marinas."
]
publicaciones2 = """- "Efectos del cambio climático en la biodiversidad marina" - Revista de Investigación en Ciencias Marinas (2022)
- "Conservación de la tortuga marina en la costa catalana" - Boletín de Conservación de Especies Marinas (2021)"""
proyectos2 = [
    "Proyecto de Conservación de Especies Marinas (2019-Presente)\nIdentificación y conservación de especies marinas en peligro de extinción.",
    
    "Proyecto de Investigación en Áreas Marinas (2015-2019)\nDesarrollo de habilidades en investigación científica y conservación marina."
]
certificaciones2 = [
    "Máster en Ciencias Marinas - Universidad de Barcelona (2021)",
    "Doctorado en Ciencias Marinas - Universidad de Barcelona (2023)"
]
referencias2 = [
    "Dr. María García - Jefe de Departamento de Investigación, Centro de Investigación en Ciencias Marinas\nEmail: maria.garcia@cienciasmarinas.org"
]
foto_url2 = "https://img.freepik.com/foto-gratis/biologa-mujer-estudiando-microscopio_23-2148176678.jpg"
output_path2 = "pdfs/Carla_Rodriguez_CV.pdf"

# Generar los nuevos PDFs
generar_cv(nombre5, apellido5, profesion5, contacto5, educacion5, idiomas5, habilidades5, experiencia5, publicaciones5, proyectos5, certificaciones5, referencias5, foto_url5, output_path5)
generar_cv(nombre6, apellido6, profesion6, contacto6, educacion6, idiomas6, habilidades6, experiencia6, publicaciones6, proyectos6, certificaciones6, referencias6, foto_url6, output_path6)
generar_cv(nombre7, apellido7, profesion7, contacto7, educacion7, idiomas7, habilidades7, experiencia7, publicaciones7, proyectos7, certificaciones7, referencias7, foto_url7, output_path7)
generar_cv(nombre8, apellido8, profesion8, contacto8, educacion8, idiomas8, habilidades8, experiencia8, publicaciones8, proyectos8, certificaciones8, referencias8, foto_url8, output_path8)
generar_cv(nombre1, apellido1, profesion1, contacto1, educacion1, idiomas1, habilidades1, experiencia1, publicaciones1, proyectos1, certificaciones1, referencias1, foto_url1, output_path1)
generar_cv(nombre2, apellido2, profesion2, contacto2, educacion2, idiomas2, habilidades2, experiencia2, publicaciones2, proyectos2, certificaciones2, referencias2, foto_url2, output_path2)

print(f"Nuevos PDFs generados en: {os.path.abspath('pdfs')}")
