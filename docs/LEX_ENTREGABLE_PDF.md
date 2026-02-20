# Arquitectura del Generador de Analizadores Léxicos

**Entrega — Laboratorio**

---

## Video

Enlace:

---

## Descripción del diseño

El trabajo consiste en la definición de arquitectura para un generador de analizadores léxicos. La herramienta toma especificaciones de tokens en forma de expresiones regulares y produce código que realiza la tokenización de cadenas de entrada. El diseño se organiza en nueve módulos con responsabilidades claras y un flujo de datos lineal.

### Módulos

1. **Lexical Spec Parser**: lee el archivo `.l` y construye el AST de la especificación.
2. **Regex Normalizer**: expande macros y une todas las reglas en una sola expresión regular.
3. **NFA Builder**: construye el AFN mediante el algoritmo de Thompson.
4. **NFA→DFA Converter**: obtiene el AFD por subset construction.
5. **DFA Minimizer**: reduce estados con el algoritmo de Hopcroft.
6. **Code Emitter**: genera el código fuente del scanner (C, Java, etc.).
7. **Runtime Engine**: ejecuta el scanner sobre la cadena de entrada.
8. **Symbol Table**: mantiene las definiciones de tokens y prioridades.
9. **Error Handler**: reporte de errores y estrategias de recuperación.

### Flujo

```
.l → Parser → AST → Normalizer → Regex → NFA Builder → AFN
  → Subset construction → AFD → Minimizer → AFD mín.
  → Code Emitter → Código → Runtime + input → Tokens
```

### Ejemplo

Gramática con identificadores `[a-zA-Z]([a-zA-Z]|[0-9])*`, números `[0-9]+` y operadores `+`, `*`, `=`.

Para la cadena `foo = 42 + x7`, el scanner emite: `TOKEN_ID(foo)`, `TOKEN_EQ`, `TOKEN_NUM(42)`, `TOKEN_PLUS`, `TOKEN_ID(x7)`.

El parser produce el AST; el normalizer une las regex; el builder construye el AFN; subset construction y Hopcroft producen el AFD mínimo; el emitter genera el código; el runtime aplica el scanner al input y devuelve la secuencia de tokens.

### Criterios de diseño

Se priorizó la separación de responsabilidades entre módulos, el flujo en pipeline y la cohesión de cada componente. Se utilizan patrones como Builder, Strategy y Facade. En cuanto a RNF: el DFA minimizado y la tabla de transiciones garantizan coste O(1) por carácter; la validación por fase y el error handler aportan confiabilidad; las interfaces acotadas facilitan mantenimiento y extensión.
