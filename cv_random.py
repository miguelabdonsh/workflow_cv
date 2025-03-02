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
    "Máster en Inteligencia Artificial - Universidad Politécnica de Madrid (2021-2023)",
    "Grado en Ingeniería Informática - Universidad Complutense de Madrid (2017-2021)",
    "Bootcamp de Desarrollo Web Full Stack - Le Wagon (2016-2017)",
    "Curso especializado en DevOps y CI/CD - Platzi (2022)",
    "Certificación en Cloud Computing - AWS Academy (2023)"
]
idiomas1 = "Español - Nativo\nInglés - C1\nAlemán - B1\nFrancés - A2"
habilidades1 = """- Lenguajes de programación: JavaScript, TypeScript, Python, Java, C++, Rust
- Frameworks Frontend: React, Angular, Vue.js, Next.js
- Frameworks Backend: Node.js, Django, Flask, Spring Boot
- Bases de datos: MongoDB, PostgreSQL, MySQL, Redis, Elasticsearch
- Cloud: AWS, Google Cloud Platform, Azure, Heroku
- DevOps: Docker, Kubernetes, Jenkins, GitHub Actions, GitLab CI
- Machine Learning: TensorFlow, PyTorch, scikit-learn, Keras
- Metodologías: Agile, Scrum, Kanban, TDD, BDD
- Herramientas: Git, JIRA, Confluence, Slack, Figma
- Soft Skills: Liderazgo, Trabajo en equipo, Comunicación, Resolución de problemas"""
experiencia1 = [
    "Senior Full Stack Developer - Google (2022-Presente)\nDesarrollo de aplicaciones web escalables utilizando React y Node.js. Implementación de arquitecturas serverless con Google Cloud Functions. Optimización de rendimiento y accesibilidad. Liderazgo de un equipo de 5 desarrolladores junior.\n• Reduje el tiempo de carga de la aplicación principal en un 40%\n• Implementé CI/CD con GitHub Actions, reduciendo el tiempo de despliegue en un 60%\n• Desarrollé una API RESTful que procesa más de 1 millón de solicitudes diarias",
    
    "Machine Learning Engineer - Microsoft (2020-2022)\nDesarrollo de modelos de aprendizaje automático para análisis de datos y predicciones. Implementación de pipelines de procesamiento de datos. Optimización de algoritmos de ML.\n• Creé un modelo de predicción con una precisión del 94%\n• Optimicé el procesamiento de datos reduciendo el tiempo en un 70%\n• Colaboré en el desarrollo de una biblioteca de ML de código abierto",
    
    "Desarrollador Backend - Telefónica (2019-2020)\nDesarrollo de microservicios con Spring Boot y Node.js. Implementación de bases de datos NoSQL. Integración con sistemas de terceros mediante APIs.\n• Desarrollé una arquitectura de microservicios que mejoró la escalabilidad\n• Implementé un sistema de caché que redujo la carga del servidor en un 50%\n• Creé documentación técnica detallada para facilitar el mantenimiento",
    
    "Desarrollador Frontend - Freelance (2017-2019)\nDesarrollo de interfaces de usuario para startups y empresas medianas. Implementación de diseños responsivos y accesibles. Optimización de rendimiento.\n• Desarrollé más de 20 sitios web para clientes de diversos sectores\n• Implementé estrategias de SEO que aumentaron el tráfico orgánico en un 200%\n• Creé componentes reutilizables que aceleraron el desarrollo de nuevos proyectos"
]
publicaciones1 = """- "Implementación de Arquitecturas Serverless en Aplicaciones Empresariales" - InfoWorld (2023)
- "Optimización de Modelos de Deep Learning para Dispositivos Móviles" - Towards Data Science (2022)
- "Patrones de Diseño en Aplicaciones React" - Medium (2021)
- "Microservicios vs Monolitos: Un Análisis Comparativo" - Dev.to (2020)
- "El Futuro del Desarrollo Web: WebAssembly y sus Aplicaciones" - Hackernoon (2019)"""
proyectos1 = [
    "AI Code Assistant (2023)\nHerramienta de asistencia para programadores basada en IA que sugiere mejoras de código, detecta bugs y optimiza rendimiento. Desarrollada con Python, TensorFlow y React.\n• Más de 5,000 usuarios activos\n• Integración con VSCode, IntelliJ y GitHub\n• Reconocimiento de patrones en más de 10 lenguajes de programación",
    
    "EcoTrack (2022)\nAplicación móvil para seguimiento de huella de carbono personal. Desarrollada con React Native, Node.js y MongoDB.\n• Más de 50,000 descargas en Google Play y App Store\n• Integración con APIs de transporte público y servicios de energía\n• Gamificación para incentivar hábitos sostenibles",
    
    "SmartHome Hub (2021)\nSistema de gestión domótica para hogares inteligentes. Desarrollado con Raspberry Pi, Python y MQTT.\n• Compatible con más de 50 dispositivos IoT diferentes\n• Interfaz web y móvil para control remoto\n• Algoritmos de aprendizaje para optimizar consumo energético",
    
    "CryptoAnalyzer (2020)\nHerramienta de análisis de criptomonedas con predicciones de precios. Desarrollada con Python, scikit-learn y D3.js.\n• Análisis en tiempo real de más de 100 criptomonedas\n• Algoritmos de predicción con precisión del 85%\n• Visualizaciones interactivas de tendencias históricas"
]
certificaciones1 = [
    "AWS Certified Solutions Architect - Professional (2023)",
    "Google Cloud Professional Data Engineer (2022)",
    "Microsoft Certified: Azure Developer Associate (2022)",
    "TensorFlow Developer Certificate (2021)",
    "Certified Kubernetes Administrator (2021)",
    "Certified Scrum Master (2020)",
    "Oracle Certified Professional, Java SE 11 Developer (2019)"
]
referencias1 = [
    "Dr. Carlos Martínez - Director de Ingeniería en Google\nEmail: carlos.martinez@google.com | Teléfono: +34 91 234 5678",
    "Dra. Laura Sánchez - CTO en TechStartup\nEmail: laura.sanchez@techstartup.com | Teléfono: +34 93 876 5432",
    "Javier López - Director de Desarrollo en Microsoft\nEmail: javier.lopez@microsoft.com | Teléfono: +34 91 567 8901"
]
foto_url1 = "https://vivolabs.es/wp-content/uploads/2022/03/perfil-hombre-vivo.png"
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
    "Doctorado en Biología Marina - Universidad de Barcelona (2019-2023)",
    "Máster en Oceanografía y Gestión del Medio Marino - Universidad de Cádiz (2017-2019)",
    "Grado en Biología - Universidad Autónoma de Barcelona (2013-2017)",
    "Curso especializado en Técnicas Moleculares Aplicadas a la Ecología - CSIC (2020)",
    "Programa de Intercambio - Woods Hole Oceanographic Institution, EE.UU. (2018)",
    "Curso de Buceo Científico - PADI & AAUS (2016)"
]
idiomas2 = "Español - Nativo\nCatalán - Nativo\nInglés - C2\nFrancés - B2\nPortugués - B1"
habilidades2 = """- Técnicas de campo: Muestreo marino, buceo científico, transectos submarinos, censos visuales
- Técnicas de laboratorio: PCR, qPCR, secuenciación de ADN, ELISA, cromatografía, microscopía
- Análisis de datos: R, Python, SPSS, análisis estadístico multivariante, modelado ecológico
- Sistemas de Información Geográfica: ArcGIS, QGIS, teledetección, análisis espacial
- Conservación marina: Evaluación de impacto ambiental, diseño de áreas marinas protegidas
- Taxonomía: Identificación de especies marinas (peces, invertebrados, algas)
- Oceanografía: Análisis de parámetros físico-químicos, corrientes, batimetría
- Comunicación científica: Publicaciones científicas, divulgación, educación ambiental
- Gestión de proyectos: Diseño experimental, presupuestos, coordinación de equipos
- Legislación ambiental: Normativas nacionales e internacionales, Directiva Marco del Agua, CITES"""
experiencia2 = [
    "Investigadora Postdoctoral - Instituto de Ciencias del Mar (CSIC) (2023-Presente)\nInvestigación sobre el impacto del cambio climático en los ecosistemas coralinos del Mediterráneo. Coordinación de campañas oceanográficas. Análisis de datos de biodiversidad y parámetros ambientales.\n• Liderazgo de un proyecto internacional con 5 instituciones colaboradoras\n• Publicación de 8 artículos científicos en revistas de alto impacto\n• Desarrollo de nuevos protocolos para la restauración de arrecifes de coral",
    
    "Investigadora Doctoral - Universidad de Barcelona (2019-2023)\nEstudio de la conectividad genética de poblaciones de peces en el Mediterráneo Occidental. Análisis de ADN ambiental para monitoreo de biodiversidad marina. Evaluación de la efectividad de áreas marinas protegidas.\n• Desarrollo de nuevos marcadores genéticos para especies amenazadas\n• Participación en 12 campañas oceanográficas\n• Obtención de 3 becas competitivas para investigación",
    
    "Técnica de Medio Ambiente - Generalitat de Catalunya (2017-2019)\nMonitoreo de la calidad del agua en la costa catalana. Evaluación del estado ecológico de ecosistemas costeros. Elaboración de informes técnicos para la administración pública.\n• Implementación de un nuevo sistema de alerta temprana para floraciones algales nocivas\n• Coordinación de la red de vigilancia de especies invasoras marinas\n• Desarrollo de protocolos estandarizados para el monitoreo costero",
    
    "Asistente de Investigación - Estación Biológica Marina de Blanes (2016-2017)\nParticipación en proyectos de investigación sobre biodiversidad marina. Muestreo y análisis de comunidades bentónicas. Mantenimiento de acuarios experimentales.\n• Colaboración en el descubrimiento de dos nuevas especies de invertebrados marinos\n• Desarrollo de un sistema automatizado para el monitoreo de parámetros en acuarios\n• Participación en programas de ciencia ciudadana con pescadores locales",
    
    "Educadora Ambiental - Acuario de Barcelona (2014-2016)\nDesarrollo e implementación de programas educativos sobre conservación marina. Guía de visitas escolares y talleres prácticos. Elaboración de materiales didácticos.\n• Diseño de un programa educativo sobre plásticos marinos que llegó a más de 10,000 estudiantes\n• Coordinación de actividades de voluntariado para limpieza de playas\n• Desarrollo de una aplicación móvil para identificación de especies mediterráneas"
]
publicaciones2 = """- "Genetic connectivity patterns of Posidonia oceanica meadows in the Western Mediterranean: Implications for conservation" - Marine Ecology Progress Series (2023)
- "Environmental DNA as a tool for monitoring marine biodiversity in Mediterranean Marine Protected Areas" - Scientific Reports (2022)
- "Effects of marine heatwaves on gorgonian forests: a case study in the Medes Islands Marine Reserve" - Global Change Biology (2022)
- "Microplastic ingestion in commercial fish species from the Catalan coast" - Marine Pollution Bulletin (2021)
- "Long-term monitoring reveals declining coral populations in a Marine Protected Area" - Ecological Indicators (2021)
- "Citizen science contributions to marine biodiversity monitoring: a Mediterranean case study" - Ocean & Coastal Management (2020)
- "Taxonomic and functional diversity of benthic communities in submarine caves of the Western Mediterranean" - Marine Biology (2019)
- "New records of invasive algae in the Balearic Islands: ecological implications" - Mediterranean Marine Science (2018)"""
proyectos2 = [
    "MedResilience (2023-Presente)\nProyecto internacional para evaluar la resiliencia de ecosistemas mediterráneos frente al cambio climático. Financiado por la Unión Europea (Horizonte Europa).\n• Coordinación de una red de 15 áreas marinas protegidas en 6 países\n• Implementación de técnicas innovadoras de restauración ecológica\n• Desarrollo de modelos predictivos para escenarios de cambio climático",
    
    "BioDNA (2020-2023)\nDesarrollo y aplicación de técnicas de ADN ambiental para el monitoreo de biodiversidad marina en el Mediterráneo. Financiado por el Ministerio de Ciencia e Innovación.\n• Creación de una biblioteca de referencia genética con más de 500 especies\n• Implementación de protocolos estandarizados para muestreo y análisis\n• Transferencia de conocimiento a gestores de espacios protegidos",
    
    "MicroMed (2019-2021)\nEstudio del impacto de microplásticos en ecosistemas marinos mediterráneos. Colaboración entre universidades y ONGs ambientales.\n• Análisis de la presencia de microplásticos en más de 30 playas\n• Evaluación de la ingesta de microplásticos en especies comerciales\n• Campañas de sensibilización en escuelas y comunidades costeras",
    
    "CoralRestore (2018-2020)\nProyecto piloto de restauración de poblaciones de coral rojo (Corallium rubrum) en áreas degradadas. Financiado por la Fundación Biodiversidad.\n• Desarrollo de técnicas de cultivo ex situ de colonias de coral\n• Implementación de trasplantes experimentales en zonas protegidas\n• Monitoreo a largo plazo del éxito de las acciones de restauración"
]
certificaciones2 = [
    "Certificación en Buceo Científico AAUS/ESDP (2022)",
    "Técnico Superior en Gestión y Organización de Recursos Naturales (2020)",
    "Certificación en Sistemas de Información Geográfica Aplicados a la Ecología (2019)",
    "Patrón de Embarcaciones de Recreo (2018)",
    "Certificación en Técnicas Moleculares para Estudios Ecológicos (2017)",
    "PADI Divemaster (2016)"
]
referencias2 = [
    "Dra. María Gómez - Directora del Instituto de Ciencias del Mar (CSIC)\nEmail: maria.gomez@icm.csic.es | Teléfono: +34 93 230 9500",
    "Dr. Juan Pérez - Catedrático de Ecología Marina, Universidad de Barcelona\nEmail: juan.perez@ub.edu | Teléfono: +34 93 402 1450",
    "Dra. Sophie Martin - Investigadora en Station Biologique de Roscoff, Francia\nEmail: sophie.martin@sb-roscoff.fr | Teléfono: +33 2 98 29 23 23",
    "Dr. Roberto Danovaro - Presidente de la Estación Zoológica Anton Dohrn, Italia\nEmail: roberto.danovaro@szn.it | Teléfono: +39 081 583 3111"
]
foto_url2 = "https://content.cuerpomente.com/medio/2024/10/28/foto-perfil_44cc84cf_241028152214_1280x720.jpg"
output_path2 = "pdfs/Carla_Rodriguez_CV.pdf"

# Generar los PDFs
generar_cv(nombre1, apellido1, profesion1, contacto1, educacion1, idiomas1, habilidades1, experiencia1, publicaciones1, proyectos1, certificaciones1, referencias1, foto_url1, output_path1)
generar_cv(nombre2, apellido2, profesion2, contacto2, educacion2, idiomas2, habilidades2, experiencia2, publicaciones2, proyectos2, certificaciones2, referencias2, foto_url2, output_path2)

print(f"PDFs generados en: {os.path.abspath('pdfs')}")
