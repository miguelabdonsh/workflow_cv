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

# Datos para Lucía Martínez - Perfil de Chef
nombre9 = "Lucía"
apellido9 = "Martínez Gómez"
profesion9 = "Chef Ejecutiva | Especialista en Cocina Mediterránea"
contacto9 = [
    "Valencia, España", 
    "+34 611 22 33 44", 
    "lucia.martinez@gastronomia.es"
]
educacion9 = [
    "Diplomatura en Gastronomía - Escuela de Hostelería de Valencia (2010-2013)",
    "Especialización en Cocina Mediterránea - Le Cordon Bleu Madrid (2014)"
]
idiomas9 = "Español - Nativo\nInglés - B2\nFrancés - B1"
habilidades9 = """- Cocina mediterránea: Técnicas tradicionales y modernas
- Gestión de cocina: Organización, costes, personal
- Maridaje: Selección de vinos y combinaciones gastronómicas
- Presentación: Técnicas de emplatado y estética culinaria"""
experiencia9 = [
    "Chef Ejecutiva - Restaurante Azahar (2018-Presente)\nDirección de cocina en restaurante con estrella Michelin. Creación de menús estacionales.",
    
    "Jefa de Cocina - Hotel Mediterráneo (2015-2018)\nGestión de equipo de cocina. Elaboración de cartas y menús para eventos.",
    
    "Cocinera - Restaurante El Olivo (2013-2015)\nPreparación de platos mediterráneos. Especialización en arroces y pescados."
]
publicaciones9 = """- "Sabores del Mediterráneo: Recetas con historia" - Editorial Gastronómica (2021)
- "El arroz perfecto: Técnicas y secretos" - Revista Cocina Actual (2020)"""
proyectos9 = [
    "Escuela de Cocina Azahar (2019-Presente)\nTalleres gastronómicos para aficionados y profesionales.",
    
    "Programa de Televisión 'Sabores de Valencia' (2020-2021)\nParticipación como chef invitada en programa culinario regional."
]
certificaciones9 = [
    "Certificación en Seguridad Alimentaria - APPCC",
    "Sommelier Nivel 2 - Federación de Asociaciones de Sumilleres"
]
referencias9 = [
    "Carlos Navarro - Director Gastronómico, Hotel Mediterráneo\nEmail: carlos.navarro@hotelmediterraneo.com"
]
foto_url9 = "https://img.freepik.com/foto-gratis/chef-mujer-posando-brazos-cruzados_23-2148516564.jpg"
output_path9 = "pdfs/Lucia_Martinez_CV.pdf"

# Datos para Andrés Herrera - Perfil de Periodista
nombre10 = "Andrés"
apellido10 = "Herrera Blanco"
profesion10 = "Periodista | Corresponsal Internacional"
contacto10 = [
    "Madrid, España", 
    "+34 677 88 99 00", 
    "andres.herrera@prensa.es"
]
educacion10 = [
    "Grado en Periodismo - Universidad Complutense de Madrid (2008-2012)",
    "Máster en Relaciones Internacionales - UNED (2013-2014)"
]
idiomas10 = "Español - Nativo\nInglés - C2\nFrancés - C1\nÁrabe - B1"
habilidades10 = """- Periodismo de investigación: Fuentes, verificación, análisis
- Corresponsalía: Cobertura internacional, zonas de conflicto
- Comunicación: Redacción, locución, presentación
- Medios digitales: Edición web, redes sociales, podcasting"""
experiencia10 = [
    "Corresponsal Internacional - Diario El Mundo (2018-Presente)\nCobertura de noticias en Oriente Medio. Reportajes especiales sobre conflictos.",
    
    "Redactor Jefe - Revista Internacional (2015-2018)\nCoordinación de contenidos. Edición de reportajes y entrevistas.",
    
    "Periodista - Agencia EFE (2012-2015)\nRedacción de noticias internacionales. Cobertura de eventos políticos."
]
publicaciones10 = """- "Voces del conflicto: Testimonios desde la frontera" - Editorial Planeta (2022)
- "Periodismo en tiempos de crisis: Manual para corresponsales" - Universidad Complutense (2020)"""
proyectos10 = [
    "Podcast 'Mundo en Conflicto' (2020-Presente)\nSerie de entrevistas con protagonistas de zonas en crisis.",
    
    "Documental 'Refugiados: El largo camino' (2019)\nProducción audiovisual sobre la crisis migratoria en Europa."
]
certificaciones10 = [
    "Curso de Seguridad en Zonas Hostiles - Reuters",
    "Especialista en Verificación Digital - Google News Initiative"
]
referencias10 = [
    "Elena Sánchez - Directora de Internacional, Diario El Mundo\nEmail: elena.sanchez@elmundo.es"
]
foto_url10 = "https://img.freepik.com/foto-gratis/periodista-masculino-microfono-entrevistando_23-2148921901.jpg"
output_path10 = "pdfs/Andres_Herrera_CV.pdf"

# Datos para Carmen Ortiz - Perfil de Psicóloga
nombre11 = "Carmen"
apellido11 = "Ortiz Navarro"
profesion11 = "Psicóloga Clínica | Especialista en Terapia Familiar"
contacto11 = [
    "Sevilla, España", 
    "+34 633 44 55 66", 
    "carmen.ortiz@psicologia.es"
]
educacion11 = [
    "Licenciatura en Psicología - Universidad de Sevilla (2009-2014)",
    "Máster en Psicología Clínica - Universidad de Sevilla (2014-2016)"
]
idiomas11 = "Español - Nativo\nInglés - B2"
habilidades11 = """- Terapia familiar: Intervención sistémica, mediación
- Psicoterapia: Enfoque cognitivo-conductual, mindfulness
- Evaluación psicológica: Tests, entrevistas clínicas
- Intervención en crisis: Manejo de situaciones traumáticas"""
experiencia11 = [
    "Psicóloga Clínica - Centro de Psicología Integral (2018-Presente)\nTerapia individual y familiar. Especialización en problemas de pareja.",
    
    "Psicóloga - Hospital Universitario Virgen del Rocío (2016-2018)\nAtención psicológica a pacientes hospitalizados y familiares.",
    
    "Psicóloga en Prácticas - Centro de Salud Mental (2014-2016)\nAsistencia en terapias grupales. Evaluación psicológica."
]
publicaciones11 = """- "Estrategias de intervención familiar en casos de divorcio conflictivo" - Revista de Psicología Clínica (2021)
- "Mindfulness como herramienta terapéutica en adolescentes" - Cuadernos de Psicología (2019)"""
proyectos11 = [
    "Programa 'Familias en Armonía' (2019-Presente)\nTalleres para mejorar la comunicación familiar y resolución de conflictos.",
    
    "Investigación sobre Estrés Postraumático (2017-2018)\nColaboración en estudio sobre intervención temprana en trauma."
]
certificaciones11 = [
    "Especialista en Terapia Familiar Sistémica - Instituto de Terapia Familiar",
    "Certificación en Mindfulness para Terapeutas - Asociación Española de Mindfulness"
]
referencias11 = [
    "Dra. Laura Jiménez - Directora, Centro de Psicología Integral\nEmail: laura.jimenez@psicologiaintegral.es"
]
foto_url11 = "https://img.freepik.com/foto-gratis/psicologa-mujer-sesion-terapia_23-2148761195.jpg"
output_path11 = "pdfs/Carmen_Ortiz_CV.pdf"

# Datos para Roberto Campos - Perfil de Ingeniero Civil
nombre12 = "Roberto"
apellido12 = "Campos Vega"
profesion12 = "Ingeniero Civil | Especialista en Estructuras"
contacto12 = [
    "Barcelona, España", 
    "+34 644 77 88 99", 
    "roberto.campos@ingenieria.es"
]
educacion12 = [
    "Grado en Ingeniería Civil - Universidad Politécnica de Cataluña (2010-2015)",
    "Máster en Estructuras - Universidad Politécnica de Cataluña (2015-2017)"
]
idiomas12 = "Español - Nativo\nCatalán - Nativo\nInglés - C1"
habilidades12 = """- Cálculo estructural: Hormigón, acero, madera
- Gestión de proyectos: Planificación, presupuestos, supervisión
- Software técnico: AutoCAD, CYPE, SAP2000, Revit
- Normativa: CTE, Eurocódigos, normativas sísmicas"""
experiencia12 = [
    "Ingeniero de Estructuras - Constructora Internacional (2019-Presente)\nDiseño y cálculo de estructuras para edificios residenciales y comerciales.",
    
    "Ingeniero de Proyectos - Estudio de Ingeniería BCN (2017-2019)\nDesarrollo de proyectos de edificación. Cálculo de estructuras.",
    
    "Ingeniero Junior - Consultora Técnica (2015-2017)\nAsistencia en proyectos de ingeniería civil. Modelado estructural."
]
publicaciones12 = """- "Análisis comparativo de soluciones estructurales en edificios de altura" - Revista de Ingeniería Civil (2022)
- "Rehabilitación estructural de edificios históricos" - Hormigón y Acero (2020)"""
proyectos12 = [
    "Centro Comercial Mediterráneo (2020-2022)\nDiseño estructural de complejo comercial de 50.000 m².",
    
    "Rehabilitación Puente Histórico (2018-2019)\nEvaluación y refuerzo estructural de puente catalogado."
]
certificaciones12 = [
    "Ingeniero Civil Colegiado - Colegio de Ingenieros de Caminos, Canales y Puertos",
    "Certificación BIM - Building Smart Spanish Chapter"
]
referencias12 = [
    "Ing. Carlos Martínez - Director Técnico, Constructora Internacional\nEmail: carlos.martinez@constructora.es"
]
foto_url12 = "https://img.freepik.com/foto-gratis/ingeniero-construccion-trabajando-oficina_23-2148816365.jpg"
output_path12 = "pdfs/Roberto_Campos_CV.pdf"

# Datos para Sofía Ramos - Perfil de Traductora
nombre13 = "Sofía"
apellido13 = "Ramos Iglesias"
profesion13 = "Traductora e Intérprete | Especialista en Traducción Jurídica"
contacto13 = [
    "Madrid, España", 
    "+34 655 66 77 88", 
    "sofia.ramos@traduccion.es"
]
educacion13 = [
    "Grado en Traducción e Interpretación - Universidad Autónoma de Madrid (2012-2016)",
    "Máster en Traducción Jurídica - Universidad Complutense de Madrid (2016-2017)"
]
idiomas13 = "Español - Nativo\nInglés - C2\nFrancés - C2\nAlemán - B2\nItaliano - B1"
habilidades13 = """- Traducción jurídica: Contratos, sentencias, documentos legales
- Interpretación: Simultánea, consecutiva, de enlace
- Localización: Adaptación cultural de contenidos
- Herramientas TAO: SDL Trados, MemoQ, Wordfast"""
experiencia13 = [
    "Traductora Freelance (2018-Presente)\nTraducción especializada para despachos de abogados y empresas internacionales.",
    
    "Traductora Jurídica - Despacho Legal Internacional (2017-2018)\nTraducción de documentación legal. Asistencia en reuniones internacionales.",
    
    "Intérprete - Agencia de Traducción Global (2016-2017)\nInterpretación en conferencias y reuniones empresariales."
]
publicaciones13 = """- "Desafíos en la traducción de contratos internacionales" - Revista de Traducción Jurídica (2021)
- "La interpretación en el ámbito judicial: guía práctica" - Manual del Traductor (2019)"""
proyectos13 = [
    "Traducción Tratado Comercial UE-Canadá (2020)\nParticipación en equipo de traducción de documentación oficial.",
    
    "Interpretación Conferencia Internacional de Derecho (2019)\nInterpretación simultánea inglés-español en congreso jurídico."
]
certificaciones13 = [
    "Traductor Jurado inglés-español - Ministerio de Asuntos Exteriores",
    "Certificación SDL Trados - Nivel Avanzado"
]
referencias13 = [
    "Dra. Marta López - Directora, Departamento de Traducción, Universidad Autónoma de Madrid\nEmail: marta.lopez@uam.es"
]
foto_url13 = "https://img.freepik.com/foto-gratis/mujer-joven-trabajando-computadora-portatil_23-2148452495.jpg"
output_path13 = "pdfs/Sofia_Ramos_CV.pdf"

# Generar los nuevos PDFs
generar_cv(nombre5, apellido5, profesion5, contacto5, educacion5, idiomas5, habilidades5, experiencia5, publicaciones5, proyectos5, certificaciones5, referencias5, foto_url5, output_path5)
generar_cv(nombre6, apellido6, profesion6, contacto6, educacion6, idiomas6, habilidades6, experiencia6, publicaciones6, proyectos6, certificaciones6, referencias6, foto_url6, output_path6)
generar_cv(nombre7, apellido7, profesion7, contacto7, educacion7, idiomas7, habilidades7, experiencia7, publicaciones7, proyectos7, certificaciones7, referencias7, foto_url7, output_path7)
generar_cv(nombre8, apellido8, profesion8, contacto8, educacion8, idiomas8, habilidades8, experiencia8, publicaciones8, proyectos8, certificaciones8, referencias8, foto_url8, output_path8)

# Generar los nuevos PDFs adicionales
generar_cv(nombre9, apellido9, profesion9, contacto9, educacion9, idiomas9, habilidades9, experiencia9, publicaciones9, proyectos9, certificaciones9, referencias9, foto_url9, output_path9)
generar_cv(nombre10, apellido10, profesion10, contacto10, educacion10, idiomas10, habilidades10, experiencia10, publicaciones10, proyectos10, certificaciones10, referencias10, foto_url10, output_path10)
generar_cv(nombre11, apellido11, profesion11, contacto11, educacion11, idiomas11, habilidades11, experiencia11, publicaciones11, proyectos11, certificaciones11, referencias11, foto_url11, output_path11)
generar_cv(nombre12, apellido12, profesion12, contacto12, educacion12, idiomas12, habilidades12, experiencia12, publicaciones12, proyectos12, certificaciones12, referencias12, foto_url12, output_path12)
generar_cv(nombre13, apellido13, profesion13, contacto13, educacion13, idiomas13, habilidades13, experiencia13, publicaciones13, proyectos13, certificaciones13, referencias13, foto_url13, output_path13)

print(f"Todos los PDFs generados en: {os.path.abspath('pdfs')}") 