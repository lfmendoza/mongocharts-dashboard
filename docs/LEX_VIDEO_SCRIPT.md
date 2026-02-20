# Guion — Video Arquitectura Lex Generator

**Duración:** 6–8 min | Leer mientras se muestra el documento

---

## 1. Apertura (30 s)

**Mostrar:** Título del documento / Alcance

*"Este video presenta la arquitectura de un generador de analizadores léxicos. La herramienta toma especificaciones de tokens —expresiones regulares con acciones asociadas— y genera código que tokeniza cadenas de entrada. El diseño se organiza en módulos acotados, con flujos de datos explícitos y énfasis en requerimientos no funcionales como rendimiento, confiabilidad y mantenibilidad."*

---

## 2. Fases del sistema (45 s)

**Mostrar:** Tabla de las 3 fases

*"El sistema opera en tres fases. Primera: compilación de la especificación —entramos con un archivo punto l y salimos con AFN, AFD y tablas de acciones. Segunda: generación de código —el AFD minimizado alimenta al emitter, que produce código fuente en C, Java u otros lenguajes. Tercera: ejecución —el scanner compilado recibe la cadena de entrada y devuelve la secuencia de tokens. Esta separación permite compilar una vez y ejecutar muchas veces, lo que mejora rendimiento y reutilización."*

---

## 3. Módulos y HLD (2 min)

**Mostrar:** Desglose de módulos (M1–M9) y diagrama HLD nivel 1

*"Definimos nueve módulos. El parser lee el archivo punto l y construye el AST. El normalizer expande macros y une todas las reglas en una sola expresión regular. El NFA Builder usa Thompson para construir el AFN. El conversor aplica subset construction para obtener el AFD. El minimizer reduce estados con Hopcroft. El Code Emitter genera el código del scanner. El Runtime Engine ejecuta ese código sobre el input. La Symbol Table y el Error Handler son transversales: la tabla sirve al parser y al emitter; el handler se usa en todo el pipeline."*

*"En el diagrama HLD se ven cuatro subsistemas. El Specification Compiler agrupa los módulos uno al cinco: todo el camino desde el parser hasta el AFD minimizado. El Code Generator es solo el emitter. El Scanner Runtime es el motor de ejecución. Y Cross-cutting engloba la tabla de símbolos y el manejo de errores. Esta agrupación permite sustituir o extender bloques sin tocar el resto —por ejemplo, cambiar el algoritmo de minimización o añadir un nuevo lenguaje objetivo."*

---

## 4. Flujo de datos y secuencia (1 min)

**Mostrar:** Diagrama de flujo general y diagrama de secuencia

*"El flujo es lineal: archivo punto l al parser, AST al normalizer, regex al NFA Builder, AFN al conversor, AFD al minimizer, AFD mínimo y tabla de símbolos al emitter, código al runtime que recibe también la cadena fuente, y salida la secuencia de tokens. El diagrama de secuencia detalla las llamadas entre módulos: el parser registra los tipos en la Symbol Table antes de pasar el AST al normalizer; cada módulo recibe la salida del anterior y la transforma. Este pipeline desacoplado facilita pruebas unitarias por fase y mantenimiento."*

---

## 5. Diagrama de clases (45 s)

**Mostrar:** Clases principales

*"Las clases centrales son LexSpecParser, RegexNormalizer, ThompsonBuilder, NFA, SubsetConstruction, DFA y CodeEmitter. El Parser produce un AST; el Normalizer lo recibe y devuelve regex normalizada; el ThompsonBuilder construye el NFA; SubsetConstruction convierte a DFA; el Emitter toma el DFA y genera código. Cada una tiene una responsabilidad clara y una interfaz acotada. Usamos Builder para la construcción del AFN, Strategy para minimización y lenguajes objetivo, y Visitor para recorrer el AST sin modificar su estructura."*

---

## 6. Ejemplo práctico (2 min)

**Mostrar:** Gramática, cadena `foo = 42 + x7`, tabla de tokens

*"Veamos un ejemplo concreto. La gramática define identificadores con letras y dígitos, números, y los operadores más, asterisco e igual. La cadena de prueba es foo igual 42 más x7."*

*"El parser extrae macros y reglas con prioridades. El normalizer las expande y une en una sola regex con alternancia. Thompson construye el AFN; subset construction produce el AFD; Hopcroft lo minimiza. El emitter genera la tabla de transiciones y el driver. Al ejecutar sobre foo igual 42 más x7, el scanner emite: TOKEN_ID para foo, TOKEN_EQ para el igual, TOKEN_NUM para 42, TOKEN_PLUS, y TOKEN_ID para x7. Los espacios se omiten por la regla de skip."*

*"Con este recorrido se ve cómo cada módulo transforma su entrada en una salida bien definida y cómo el flujo termina en tokens listos para el analizador sintáctico."*

---

## 7. Patrones y RNF (1 min)

**Mostrar:** Patrones de diseño y tabla RNF

*"Los patrones usados son Builder para AFN y código, Strategy para minimización y emisión a distintos lenguajes, Visitor para el AST, Factory para estados y transiciones, y Facade como orquestador del pipeline. El flujo lineal es en sí un patrón Pipeline."*

*"En requerimientos no funcionales: rendimiento se logra con tabla de transiciones O(1) por carácter y DFA minimizado; confiabilidad con validación por fase y error handler centralizado; escalabilidad con módulos desacoplados y posibilidad de paralelizar sub-AFNs; mantenibilidad con interfaces claras y cohesión por módulo; y extensibilidad vía Strategy y Visitor para nuevos targets y operadores."*

---

## 8. Cierre (30 s)

**Mostrar:** Flujo resumido (.l → AST → Regex → AFN → AFD → Código → Tokens)

*"En resumen: nueve módulos organizados en cuatro subsistemas, flujo lineal de datos, ejemplo aplicado de foo igual 42 más x7, y criterios de diseño basados en patrones y RNF. El resultado es una arquitectura modular, extensible y alineada con los requisitos de rendimiento y mantenibilidad."*

---

## Notas para la grabación

- Leer con ritmo natural, sin acelerar.
- Pausar brevemente al cambiar de diagrama o sección.
- Si usas presentación con diapositivas, sincroniza cada bloque con su diagrama.
- Revisar pronunciación de términos: Thompson, Hopcroft, subset construction, emitter.
