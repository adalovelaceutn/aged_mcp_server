curriculo_data = {
  "NODO_01": {
    "nombre_nivel": "NIVEL 1: Fundamentos del Sistema",
    "titulo": "Sistema de Numeración Decimal",
    "capacidad": "Resolver problemas aplicando criterios de cálculo y estimación en el sistema decimal, reconociendo su naturaleza posicional [1, 2].",
    "saberes": [
      "Identificación de símbolos (dígitos) y reglas de generación de base 10 [3].",
      "Comprensión del valor posicional (unidades, decenas, centenas) [4].",
      "Descomposición aditiva y multiplicativa de números [5]."
    ],
    "prerrequisitos": [],
    "lista_actividades": ["ACT_NUM_01", "ACT_NUM_02", "ACT_NUM_03"],
    "experiencia_didactica": {
      "situacion_anclaje": "Se presentan dos cheques de pago: uno por $756 y otro por $614. Se observa que ambos tienen el dígito '6' [4].",
      "pregunta_indagacion": "¿Por qué el 6 en el primer cheque no permite comprar lo mismo que el 6 en el segundo cheque?",
      "andamiaje": [
        "Observa la ubicación del 6 respecto al final del número en cada caso.",
        "Cuenta cuántas unidades representa el 6 si estuviera solo y compáralo con su posición actual (centenas vs unidades)."
      ]
    },
    "vocabulario_clave": ["Dígito", "Valor posicional", "Base 10", "Descomposición multiplicativa"]
  },
  "NODO_02": {
    "nombre_nivel": "NIVEL 2: Expansión de los Conjuntos Numéricos",
    "titulo": "Conjuntos Numéricos: Naturales (N) y Enteros (Z)",
    "capacidad": "Diferenciar y operar con números naturales y enteros en situaciones de orden, cardinalidad y simetría [6, 7].",
    "saberes": [
      "Uso de números como cardinal, ordinal y nominal [7, 8].",
      "Relación de inclusión N ⊂ Z [9].",
      "Representación en la recta numérica y concepto de opuesto aditivo [10, 11]."
    ],
    "prerrequisitos": ["NODO_01"],
    "lista_actividades": ["ACT_C1_10"],
    "experiencia_didactica": {
      "situacion_anclaje": "Una persona tiene $5 en su billetera e intenta pagar una deuda de $7 [10].",
      "pregunta_indagacion": "¿Es posible realizar esta operación dentro de los números que usamos para contar objetos naturales?",
      "andamiaje": [
        "Piensa qué sucede cuando el sustraendo es mayor que el minuendo.",
        "Imagina la recta numérica extendiéndose hacia la izquierda del cero para representar lo que 'falta' o se 'debe'."
      ]
    },
    "vocabulario_clave": ["Cardinal", "Ordinal", "Inverso aditivo", "Simetría"]
  },
  "NODO_03": {
    "nombre_nivel": "NIVEL 2: Expansión de los Conjuntos Numéricos",
    "titulo": "Números Racionales y Fracciones",
    "capacidad": "Modelizar situaciones de reparto y proporción mediante el uso de números racionales y sus diversas representaciones [2, 12].",
    "saberes": [
      "Definición de número racional como cociente a/b (b ≠ 0) [13].",
      "Obtención de fracciones equivalentes por amplificación y simplificación [14].",
      "Clasificación de fracciones: propias, impropias y aparentes [15]."
    ],
    "prerrequisitos": ["NODO_02"],
    "lista_actividades": ["ACT_C1_04", "ACT_C1_09_G"],
    "experiencia_didactica": {
      "situacion_anclaje": "Dos amigos piden pizzas iguales. Uno la corta en 4 porciones y come 2; el otro la corta en 8 porciones y come 4 [16].",
      "pregunta_indagacion": "¿Quién comió más pizza si las fracciones 2/4 y 4/8 parecen números distintos?",
      "andamiaje": [
        "Representa ambas situaciones en un dibujo circular (pictográfico).",
        "Intenta dividir o multiplicar el numerador y denominador de una de las fracciones por un mismo número para llegar a la otra."
      ]
    },
    "vocabulario_clave": ["Numerador", "Denominador", "Fracción irreducible", "Equivalencia"]
  },
  "NODO_04": {
    "nombre_nivel": "NIVEL 2: Expansión de los Conjuntos Numéricos",
    "titulo": "Operaciones en el Conjunto Q",
    "capacidad": "Resolver operaciones combinadas con números racionales aplicando propiedades algebraicas y criterios de simplificación [2, 17].",
    "saberes": [
      "Adición y sustracción con igual y distinto denominador (mínimo común múltiplo) [17, 18].",
      "Multiplicación y división (producto por el inverso multiplicativo) [18-20].",
      "Aplicación de la regla de los signos y propiedades (conmutativa, asociativa, distributiva) [19, 21]."
    ],
    "prerrequisitos": ["NODO_03"],
    "lista_actividades": ["ACT_C1_09_H"],
    "experiencia_didactica": {
      "situacion_anclaje": "Se deben sumar tres retazos de tela de 1/6 m, 5/2 m y 16/3 m [18].",
      "pregunta_indagacion": "¿Podemos sumar directamente los numeradores si las partes en que se dividió cada metro son diferentes?",
      "andamiaje": [
        "Busca una forma de que todas las telas estén expresadas en porciones del mismo tamaño (denominador común).",
        "Recuerda que amplificar es multiplicar numerador y denominador por un mismo factor para no alterar el valor."
      ]
    },
    "vocabulario_clave": ["Sumandos", "Factores", "Inverso multiplicativo", "Mínimo común múltiplo"]
  },
  "NODO_05": {
    "nombre_nivel": "NIVEL 3: Aplicaciones de la Proporcionalidad",
    "titulo": "Expresiones Decimales y Porcentaje",
    "capacidad": "Interpretar la relación entre porcentajes, fracciones y decimales en contextos de la vida cotidiana y comercial [1, 22].",
    "saberes": [
      "Clasificación de decimales: finitos y periódicos (puros y mixtos) [15].",
      "Conversión de fracción a porcentaje y viceversa [22].",
      "Cálculo de variaciones porcentuales en superficies y cantidades [21, 23]."
    ],
    "prerrequisitos": ["NODO_04"],
    "lista_actividades": ["ACT_C1_01", "ACT_C1_08", "ACT_C1_09_B"],
    "experiencia_didactica": {
      "situacion_anclaje": "En una tienda, un producto de $120 tiene un 25% de descuento. En otra tienda, el mismo producto tiene un descuento de 1/4 de su valor [22, 24].",
      "pregunta_indagacion": "¿En qué tienda el ahorro es mayor?",
      "andamiaje": [
        "Transforma el porcentaje 25% en una fracción decimal con denominador 100.",
        "Simplifica esa fracción y compárala con 1/4."
      ]
    },
    "vocabulario_clave": ["Parte decimal", "Período", "Fracción decimal", "Tanto por ciento"]
  },
  "NODO_06": {
    "nombre_nivel": "NIVEL 3: Aplicaciones de la Proporcionalidad",
    "titulo": "Razones y Proporciones",
    "capacidad": "Aplicar el razonamiento proporcional para comparar magnitudes y resolver problemas de covariación [24, 25].",
    "saberes": [
      "Diferenciación entre fracción (parte de un todo) y razón (comparación de magnitudes) [25, 26].",
      "Definición de proporción y constante de proporcionalidad [27].",
      "Teorema Fundamental de las Proporciones (producto de medios y extremos) [28]."
    ],
    "prerrequisitos": ["NODO_04"],
    "lista_actividades": ["ACT_C1_15", "ACT_C1_09_I", "ACT_C1_16"],
    "experiencia_didactica": {
      "situacion_anclaje": "Una máquina fabrica 6 caramelos cada 11 segundos. Se quiere saber cuántos hará en 22 segundos [27].",
      "pregunta_indagacion": "¿Cómo se mantiene el 'ritmo' de producción si duplicamos el tiempo de espera?",
      "andamiaje": [
        "Identifica si al aumentar una magnitud (tiempo), la otra (caramelos) aumenta en la misma proporción.",
        "Plantea la igualdad de dos razones y verifica si el producto cruzado es igual."
      ]
    },
    "vocabulario_clave": ["Antecedente", "Consecuente", "Magnitud", "Constante de proporcionalidad"]
  },
  "NODO_07": {
    "nombre_nivel": "NIVEL 4: Modelización Algebraica y Funciones",
    "titulo": "Sistema de Referencia y Concepto de Función",
    "capacidad": "Interpretar representaciones en el plano cartesiano reconociendo la relación de dependencia única entre variables [28, 29].",
    "saberes": [
      "Ubicación de pares ordenados (x; y) en ejes cartesianos [30, 31].",
      "Definición de función: ley de asignación única (unicidad) [32].",
      "Identificación de dominio, codominio e imagen [33, 34]."
    ],
    "prerrequisitos": ["NODO_01", "NODO_02"],
    "lista_actividades": ["ACT_C2_01", "ACT_C2_04"],
    "experiencia_didactica": {
      "situacion_anclaje": "Se analiza el gráfico de una circunferencia y el de una parábola en el plano [35].",
      "pregunta_indagacion": "¿Por qué la circunferencia no puede considerarse una función si relaciona valores de X e Y?",
      "andamiaje": [
        "Traza rectas verticales sobre ambos gráficos.",
        "Observa en cuántos puntos la recta vertical corta a cada figura; recuerda la regla de un 'único valor de y' para cada 'x'."
      ]
    },
    "vocabulario_clave": ["Abscisa", "Ordenada", "Variable independiente", "Imagen"]
  },
  "NODO_08": {
    "nombre_nivel": "NIVEL 4: Modelización Algebraica y Funciones",
    "titulo": "Funciones Lineales y Afines",
    "capacidad": "Modelizar situaciones de variación constante mediante funciones afines y de proporcionalidad directa e inversa [29, 36].",
    "saberes": [
      "Fórmula general de la función afín: y = ax + b [37].",
      "Interpretación de la pendiente (a) y la ordenada al origen (b) en contexto [37].",
      "Propiedades de la proporcionalidad directa (y/x=k) e inversa (y*x=k) [38, 39]."
    ],
    "prerrequisitos": ["NODO_06", "NODO_07"],
    "lista_actividades": ["ACT_C2_05", "ACT_C2_08"],
    "experiencia_didactica": {
      "situacion_anclaje": "Un taxi cobra $1.377 por 'bajada de bandera' y $73 por cada ficha (distancia) [36, 37].",
      "pregunta_indagacion": "¿Cuánto pagarías si el taxi recorre 0 fichas? ¿Qué parte de la fórmula representa ese valor fijo?",
      "andamiaje": [
        "Identifica qué valor no cambia sin importar la distancia recorrida (valor inicial).",
        "Piensa cómo se suma el costo cada vez que avanza una ficha adicional."
      ]
    },
    "vocabulario_clave": ["Pendiente", "Ordenada al origen", "Variación lineal", "Covariación"]
  },
  "NODO_09": {
    "nombre_nivel": "NIVEL 4: Modelización Algebraica y Funciones",
    "titulo": "Función Cuadrática",
    "capacidad": "Analizar comportamientos de trayectorias parabólicas identificando puntos críticos y formas de representación [29, 40].",
    "saberes": [
      "Forma polinómica: f(x) = ax² + bx + c [40, 41].",
      "Identificación de elementos: vértice, eje de simetría, raíces y ordenada al origen [41, 42].",
      "Análisis de concavidad según el signo del coeficiente principal [42]."
    ],
    "prerrequisitos": ["NODO_07", "NODO_08"],
    "lista_actividades": ["ACT_C2_13", "ACT_C2_14"],
    "experiencia_didactica": {
      "situacion_anclaje": "Un cañón dispara un proyectil que sigue una trayectoria modelada por f(t) = -4,9t² + 24,5t + 9,8 [40].",
      "pregunta_indagacion": "¿En qué momento el proyectil alcanza su altura máxima y cuándo toca el suelo?",
      "andamiaje": [
        "Busca el punto más alto de la curva (vértice) usando la fórmula del eje de simetría.",
        "Identifica los valores de 't' donde la altura f(t) es igual a cero (raíces)."
      ]
    },
    "vocabulario_clave": ["Parábola", "Vértice", "Concavidad", "Raíces"]
  },
  "NODO_10": {
    "nombre_nivel": "NIVEL 4: Modelización Algebraica y Funciones",
    "titulo": "Ecuaciones e Inecuaciones",
    "capacidad": "Resolver problemas de equilibrio y rangos de valores mediante métodos algebraicos justificando los resultados [29, 43].",
    "saberes": [
      "Concepto de ecuación como igualdad y métodos de transposición de términos [44, 45].",
      "Resolución de ecuaciones modulares o con valor absoluto [46, 47].",
      "Inecuaciones lineales y representación de soluciones en intervalos reales [47-49]."
    ],
    "prerrequisitos": ["NODO_04", "NODO_08"],
    "lista_actividades": ["ACT_C3_02", "ACT_C3_12"],
    "experiencia_didactica": {
      "situacion_anclaje": "Se presenta una balanza con pesas conocidas en un platillo y una caja incógnita 'x' con pesas en el otro para mantener el equilibrio [44].",
      "pregunta_indagacion": "¿Cómo podemos saber el peso de la caja sin abrirla, manteniendo la balanza nivelada?",
      "andamiaje": [
        "Si quitas el mismo peso de ambos lados, ¿se mantiene el equilibrio?",
        "Piensa en la operación inversa: si algo está sumando a la incógnita, ¿qué operación lo anularía?"
      ]
    },
    "vocabulario_clave": ["Incógnita", "Monomio", "Miembro", "Intervalo acotado"]
  },
  "NODO_11": {
    "nombre_nivel": "NIVEL 5: Geometría y Relaciones Métricas",
    "titulo": "Geometría: Semejanza y Triángulos",
    "capacidad": "Analizar situaciones geométricas que involucren proporcionalidad de formas y relaciones métricas en triángulos rectángulos [29, 49].",
    "saberes": [
      "Criterios de semejanza de triángulos (AA, LAL, LLL) [50, 51].",
      "Clasificación de triángulos por lados y ángulos [35, 52].",
      "Teorema de Pitágoras: relación entre catetos e hipotenusa [53, 54]."
    ],
    "prerrequisitos": ["NODO_06", "NODO_10"],
    "lista_actividades": ["ACT_C4_01", "ACT_C4_02"],
    "experiencia_didactica": {
      "situacion_anclaje": "Se desea calcular la longitud de una escalera apoyada en una pared si conocemos la altura de la pared y la distancia al pie de la misma [54, 55].",
      "pregunta_indagacion": "¿Qué relación matemática permite conectar las medidas de los dos lados que forman el rincón recto con el lado inclinado?",
      "andamiaje": [
        "Dibuja la situación e identifica cuál es el ángulo de 90°.",
        "Aplica la suma de los cuadrados de los lados cortos y observa si coincide con el cuadrado del lado largo."
      ]
    },
    "vocabulario_clave": ["Homólogo", "Congruente", "Hipotenusa", "Cateto"]
  },
  "NODO_12": {
    "nombre_nivel": "NIVEL 5: Geometría y Relaciones Métricas",
    "titulo": "Perímetro y Área",
    "capacidad": "Cuantificar la extensión superficial y contornos de figuras planas aplicando fórmulas específicas y unidades cuadradas [29, 56].",
    "saberes": [
      "Cálculo de perímetro como suma de longitudes de contorno [57].",
      "Longitud de circunferencia (2πr) y área del círculo (πr²) [56, 58].",
      "Fórmulas de área para polígonos (triángulo, cuadriláteros, polígono regular) [58, 59]."
    ],
    "prerrequisitos": ["NODO_05", "NODO_11"],
    "lista_actividades": ["ACT_C4_03", "ACT_C4_04"],
    "experiencia_didactica": {
      "situacion_anclaje": "Se tiene un campo cuadrado de 100m de lado. Se quiere alambrar el contorno y luego sembrar papas en toda la superficie [23].",
      "pregunta_indagacion": "¿Se usará el mismo número para comprar el alambre que para comprar las semillas?",
      "andamiaje": [
        "Distingue entre medir una línea (bordes) y medir un espacio plano (interior).",
        "Considera qué unidad de medida es lineal (m) y cuál es de superficie (m²)."
      ]
    },
    "vocabulario_clave": ["Bidimensional", "Contorno", "Radio", "Apotema"]
  },
  "NODO_13": {
    "nombre_nivel": "NIVEL 5: Geometría y Relaciones Métricas",
    "titulo": "Trigonometría",
    "capacidad": "Resolver triángulos rectángulos vinculando medidas angulares y de longitud mediante razones trigonométricas [29, 60].",
    "saberes": [
      "Definición de razones: Seno, Coseno y Tangente [61].",
      "Identificación de cateto opuesto y adyacente según el ángulo de referencia [62].",
      "Uso del acrónimo SOH-CAH-TOA para la resolución de problemas [63]."
    ],
    "prerrequisitos": ["NODO_11"],
    "lista_actividades": ["ACT_C4_06", "ACT_C4_08"],
    "experiencia_didactica": {
      "situacion_anclaje": "Desde el suelo, una persona observa la copa de un árbol con un ángulo de 30°. Conoce la distancia al tronco pero no puede trepar para medir la altura [60].",
      "pregunta_indagacion": "¿Cómo puede la 'sombra' o distancia horizontal ayudarnos a encontrar la altura vertical si solo tenemos el ángulo de visión?",
      "andamiaje": [
        "Identifica qué cateto es la altura (opuesto o adyacente) respecto al ángulo dado.",
        "Selecciona la razón trigonométrica que relaciona el cateto que buscas con el que ya conoces."
      ]
    },
    "vocabulario_clave": ["Seno", "Coseno", "Tangente", "Ángulo agudo"]
  },
  "NODO_14": {
    "nombre_nivel": "NIVEL 6: Análisis de Datos y Azar",
    "titulo": "Estadística y Probabilidad",
    "capacidad": "Interpretar y comunicar información estadística y probabilística para la toma de decisiones informadas [29, 64].",
    "saberes": [
      "Clasificación de variables (cualitativas y cuantitativas) [65, 66].",
      "Medidas de tendencia central: media (promedio), mediana y moda [67-69].",
      "Cálculo de probabilidad mediante la Regla de Laplace (casos favorables / posibles) [70, 71]."
    ],
    "prerrequisitos": ["NODO_05", "NODO_06"],
    "lista_actividades": ["ACT_C5_05", "ACT_C5_08", "ACT_C5_10", "ACT_C5_12"],
    "experiencia_didactica": {
      "situacion_anclaje": "Se lanza un dado legal y se quiere saber la probabilidad de obtener un número mayor que 4 [70].",
      "pregunta_indagacion": "¿Es más probable sacar un 6 o sacar cualquier número par?",
      "andamiaje": [
        "Enumera todos los resultados posibles del dado (espacio muestral).",
        "Cuenta cuántos de esos resultados cumplen con ser 'mayor que 4' y compáralo con el total."
      ]
    },
    "vocabulario_clave": ["Muestra", "Frecuencia", "Media", "Evento aleatorio"]
  }
}
