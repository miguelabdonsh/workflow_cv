/**
 * Renderiza una barra de progreso con porcentaje para mostrar la compatibilidad
 * @param score Puntuación entre 0 y 1
 * @returns Objeto con clases CSS y porcentaje formateado
 */
export const getMatchScoreStyles = (score: number) => {
  const percentage = Math.round(score * 100);
  
  let barColorClass = '';
  let textColorClass = '';
  
  if (percentage >= 80) {
    barColorClass = 'bg-green-500';
    textColorClass = 'text-green-600';
  } else if (percentage >= 60) {
    barColorClass = 'bg-blue-500';
    textColorClass = 'text-blue-600';
  } else if (percentage >= 40) {
    barColorClass = 'bg-yellow-500';
    textColorClass = 'text-yellow-600';
  } else {
    barColorClass = 'bg-red-500';
    textColorClass = 'text-red-600';
  }
  
  return {
    barColorClass,
    textColorClass,
    percentage
  };
};

/**
 * Determina el color de fondo y texto según la relevancia
 * @param relevancia Nivel de relevancia (Alta, Media, Baja)
 * @returns Clase CSS para aplicar al elemento
 */
export const getRelevanceColor = (relevancia: string) => {
  switch (relevancia.toLowerCase()) {
    case 'alta':
      return 'bg-green-100 text-green-800';
    case 'media':
      return 'bg-blue-100 text-blue-800';
    case 'baja':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

/**
 * Determina el color del texto según el nivel de habilidad
 * @param nivel Nivel de habilidad (Experto, Avanzado, Intermedio, Básico)
 * @returns Clase CSS para aplicar al texto
 */
export const getLevelColor = (nivel: string) => {
  switch (nivel.toLowerCase()) {
    case 'experto':
      return 'text-green-600';
    case 'avanzado':
      return 'text-blue-600';
    case 'intermedio':
      return 'text-yellow-600';
    case 'básico':
    case 'basico':
      return 'text-orange-600';
    default:
      return 'text-gray-600';
  }
}; 