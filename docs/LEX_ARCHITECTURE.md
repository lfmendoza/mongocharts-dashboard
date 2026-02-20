# Arquitectura del Generador de Analizadores Léxicos

**Versión:** 1.0 — Febrero 2025

---

## 1. Alcance

Un generador de analizadores léxicos toma especificaciones de tokens (expresiones regulares con asociación a acciones) y produce código ejecutable que realiza la tokenización de cadenas de entrada. El diseño que se presenta organiza este proceso en módulos acotados, con flujos de datos explícitos y énfasis en RNF (rendimiento, confiabilidad, mantenibilidad, escalabilidad).

---

## 2. Fases del sistema

La herramienta opera en tres grandes etapas:

| Fase | Entrada | Salida |
|------|---------|--------|
| Compilación de especificación | Archivo `.l` / `.lex` | AFN/AFD + tablas de acciones |
| Generación de código | AFD minimizado | Código fuente (C, Java, etc.) |
| Ejecución | Scanner compilado + input | Secuencia de tokens |

---

## 3. Módulos

### Desglose

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LEX GENERATOR - ARQUITECTURA MODULAR                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  M1: Lexical Spec Parser    │  M2: Regex Normalizer    │  M3: NFA Builder   │
│  M4: NFA→DFA Converter     │  M5: DFA Minimizer       │  M6: Code Emitter  │
│  M7: Runtime Engine         │  M8: Symbol Table        │  M9: Error Handler │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Responsabilidades e I/O

| Módulo | Función | Input | Output |
|--------|---------|-------|--------|
| **M1: Lexical Spec Parser** | Parseo del archivo `.l` y construcción del AST de especificación | Archivo `.l` | AST |
| **M2: Regex Normalizer** | Expansión de macros y unificación de reglas en una sola regex | AST | Regex normalizada |
| **M3: NFA Builder** | Construcción de AFN vía algoritmo de Thompson | Regex | AFN |
| **M4: NFA→DFA Converter** | Subset construction | AFN | AFD |
| **M5: DFA Minimizer** | Minimización de estados (Hopcroft) | AFD | AFD mínimo |
| **M6: Code Emitter** | Emisión de código del scanner | AFD mínimo + acciones | Código fuente |
| **M7: Runtime Engine** | Ejecución del scanner sobre el input | Código + cadena | Stream de tokens |
| **M8: Symbol Table** | Mapeo de identificadores a tipos de token | Definiciones | Tabla de símbolos |
| **M9: Error Handler** | Reporte y recuperación ante errores | Excepciones | Mensajes / estado recuperado |

---

## 4. High-Level Design (HLD)

### 4.1 Contexto del sistema (nivel 0)

```mermaid
flowchart LR
    subgraph EXTERNAL["Externo"]
        USER[Usuario]
    end

    subgraph LEX_GEN["Lex Generator"]
        direction TB
        CORE[Sistema]
    end

    USER -->|Archivo .l + Cadena input| LEX_GEN
    LEX_GEN -->|Stream de tokens| USER
```

### 4.2 Diagrama HLD — subsistemas (nivel 1)

```mermaid
flowchart TB
    subgraph INPUT["Entradas"]
        SPEC[Archivo especificación .l]
        SOURCE[Cadena fuente]
    end

    subgraph LEX_GEN["Lex Generator"]
        subgraph SPEC_COMPILER["Specification Compiler"]
            PARSER[Spec Parser\nM1]
            NORM[Regex Normalizer\nM2]
            NFA_BUILD[NFA Builder\nM3]
            DFA_CONV[DFA Converter\nM4]
            DFA_MIN[DFA Minimizer\nM5]
        end

        subgraph CODE_GEN["Code Generator"]
            EMITTER[Code Emitter\nM6]
        end

        subgraph RUNTIME_SUB["Scanner Runtime"]
            SCANNER[Runtime Engine\nM7]
        end

        subgraph CROSS["Cross-cutting"]
            SYMTAB[Symbol Table M8]
            ERR_HAND[Error Handler M9]
        end
    end

    subgraph OUTPUT["Salidas"]
        CODE[Código fuente]
        TOKENS[Tokens]
    end

    SPEC --> PARSER
    PARSER --> NORM
    NORM --> NFA_BUILD
    NFA_BUILD --> DFA_CONV
    DFA_CONV --> DFA_MIN
    PARSER -.-> SYMTAB
    SYMTAB -.-> EMITTER
    DFA_MIN --> EMITTER
    EMITTER --> CODE
    CODE --> SCANNER
    SOURCE --> SCANNER
    SCANNER --> TOKENS
    ERR_HAND -.-> PARSER
```

### 4.3 Bloques HLD — responsabilidades

| Bloque | Módulos | Responsabilidad |
|--------|---------|-----------------|
| **Specification Compiler** | M1–M5 | Parsear `.l`, normalizar regex, construir AFN, convertir a AFD, minimizar |
| **Code Generator** | M6 | Emitir código del scanner a partir del AFD y tablas de acciones |
| **Scanner Runtime** | M7 | Ejecutar el scanner compilado sobre la cadena de entrada |
| **Cross-cutting** | M8, M9 | Tabla de símbolos y manejo de errores en todo el pipeline |

---

## 5. Diagramas de detalle

### 5.1 Flujo de datos general

```mermaid
flowchart TB
    subgraph INPUT["Entrada"]
        A[Archivo .l]
        B[Cadena a analizar]
    end

    subgraph COMP["Compilación"]
        M1[Lexical Spec Parser]
        M2[Regex Normalizer]
        M3[NFA Builder]
        M4[NFA→DFA]
        M5[DFA Minimizer]
        M8[Symbol Table]
    end

    subgraph GEN["Generación"]
        M6[Code Emitter]
    end

    subgraph RUNTIME["Ejecución"]
        M7[Runtime Scanner]
    end

    subgraph OUT["Salida"]
        C[AFD]
        D[Código]
        E[Tokens]
    end

    A --> M1
    M1 --> M2
    M2 --> M3
    M3 --> M4
    M4 --> M5
    M1 -.-> M8
    M5 --> M6
    M8 --> M6
    M6 --> D
    M5 --> C
    D --> M7
    B --> M7
    M7 --> E
```

### 5.2 Secuencia del pipeline de compilación

```mermaid
sequenceDiagram
    participant User
    participant M1 as Lexical Spec Parser
    participant M2 as Regex Normalizer
    participant M3 as NFA Builder
    participant M4 as NFA→DFA Converter
    participant M5 as DFA Minimizer
    participant M6 as Code Emitter
    participant M8 as Symbol Table

    User->>M1: parse(specFilePath): LexSpecAST
    M1->>M8: registerTokenTypes(definitions)
    M1->>M2: LexSpecAST

    M2->>M2: expandMacros / mergeWithAlternation
    M2->>M3: NormalizedRegex

    M3->>M3: thompson(regex)
    M3->>M4: NFA

    M4->>M4: subsetConstruction(nfa)
    M4->>M5: DFA

    M5->>M5: hopcroftMinimize(dfa)
    M5->>M6: MinimalDFA

    M6->>M8: getTokenTypeMappings
    M6->>User: SourceCode
```

### 4.3 Clases principales

```mermaid
classDiagram
    class LexSpecParser {
        -grammar: LexGrammar
        -scanner: SpecScanner
        +parse(path: Path): LexSpecAST
        -parseDefinitions(): Map~String, String~
        -parseRules(): List~Rule~
    }

    class RegexNormalizer {
        -macroTable: Map~String, String~
        +normalize(ast: LexSpecAST): NormalizedRegex
        -expandMacros(regex: String): String
        -mergeWithAlternation(rules: List~Rule~): String
        -shuntingYard(infix: String): List~Token~
    }

    class NFA {
        +startState: NFAState
        +acceptStates: Set~NFAState~
        +transitions: Map
        +epsilonClosure(state: NFAState): Set~NFAState~
    }

    class DFA {
        +states: Set~DFAState~
        +startState: DFAState
        +transitions: Map
        +acceptingStateToRule: Map~DFAState, Int~
    }

    class ThompsonBuilder {
        +build(regex: String): NFA
        -concat(nfa1, nfa2): NFA
        -alternation(nfa1, nfa2): NFA
        -kleeneStar(nfa): NFA
    }

    class SubsetConstruction {
        +convert(nfa: NFA): DFA
        -move(states: Set, char: Char): Set~NFAState~
    }

    class CodeEmitter {
        +emit(dfa: DFA, actions: Map, lang: Lang): SourceCode
    }

    LexSpecParser --> RegexNormalizer
    RegexNormalizer --> ThompsonBuilder
    ThompsonBuilder --> NFA
    NFA --> SubsetConstruction
    SubsetConstruction --> DFA
    DFA --> CodeEmitter
```

### 5.4 Vista de componentes

```mermaid
flowchart TB
    subgraph LEXGEN["Lex Generator"]
        M1[Lexical Spec Parser]
        M2[Regex Normalizer]
        M3[NFA Builder]
        M4[DFA Converter]
        M5[DFA Minimizer]
        M6[Code Emitter]
        M8[Symbol Table]
        M9[Error Handler]
    end

    M1 -->|LexSpecAST| M2
    M2 -->|NormalizedRegex| M3
    M3 -->|NFA| M4
    M4 -->|DFA| M5
    M5 -->|MinimalDFA| M6
    M8 -->|TokenTypeMap| M6
    M9 -.-> M1
```

---

## 5. Firmas de métodos

### M1 — Lexical Spec Parser

```java
LexSpecAST parse(Path specFilePath);
// LexSpecAST: getMacroDefinitions(), getRules(), getActionCodes(), getUserCode()
```

### M2 — Regex Normalizer

```java
NormalizedRegex normalize(LexSpecAST ast);
// expandMacros(), mergeWithAlternation(), shuntingYard() / infixToPostfix()
```

### M3 — NFA Builder (Thompson)

```java
NFA build(String regex);
// literal(char), concat(nfa1, nfa2), alternation(nfa1, nfa2), kleeneStar(nfa)
```

### M4 — NFA→DFA

```java
DFA convert(NFA nfa);
// epsilonClosure(states), move(states, char), getOrCreateDFAState(nfaStates)
```

### M5 — DFA Minimizer

```java
DFA minimize(DFA dfa);
// initialPartition(), refinePartition(), buildMinimalDFA()
```

### M6 — Code Emitter

```java
SourceCode emit(DFA dfa, Map<Integer, String> actions, TargetLanguage lang);
```

---

## 7. Ejemplo: gramática mini y cadena de prueba

### Gramática

```
%%
DIGIT   [0-9]
LETTER  [a-zA-Z]
ID      {LETTER}({LETTER}|{DIGIT})*
NUM     {DIGIT}+
%%
{ID}    { return TOKEN_ID; }
{NUM}   { return TOKEN_NUM; }
"+"     { return TOKEN_PLUS; }
"*"     { return TOKEN_STAR; }
"="     { return TOKEN_EQ; }
[ \t\n]+ { /* skip */ }
%%
```

### Cadena

```
foo = 42 + x7
```

### Recorrido por fases

**M1 — Parser**

El AST contiene las definiciones de macros (DIGIT, LETTER, ID, NUM) y las reglas con sus prioridades y acciones. Cada regla queda asociada a un `actionId`.

**M2 — Normalizer**

Se expanden las macros y se unifica todo en una sola expresión con alternancia. Ejemplo de regex unificada:

```
([a-zA-Z]([a-zA-Z]|[0-9])*)|([0-9]+)|(\+)|(\*)|(=)|([ \t\n]+)
```

**M3 — NFA Builder**

A partir de la regex en postfix se construye el AFN mediante Thompson. Cada literal, concatenación, alternancia y clausura de Kleene genera subgrafos que se integran en el AFN global.

**M4 — Subset construction**

Se obtiene el AFD equivalente. Cada estado del AFD corresponde a un conjunto de estados del AFN. Las transiciones se determinan con `move` y `epsilonClosure`.

**M5 — Minimización**

Hopcroft reduce el número de estados agrupando equivalentes en particiones.

**M6 — Code Emitter**

Se emite una tabla de transiciones y un driver que, en cada paso, avanza el estado según el carácter leído y dispara la acción asociada al estado de aceptación.

**M7 — Runtime sobre `foo = 42 + x7`**

| Lexema | Token |
|--------|-------|
| foo | TOKEN_ID |
| (espacio) | skip |
| = | TOKEN_EQ |
| (espacio) | skip |
| 42 | TOKEN_NUM |
| (espacio) | skip |
| + | TOKEN_PLUS |
| (espacio) | skip |
| x7 | TOKEN_ID |
| EOF | TOKEN_EOF |

---

## 8. Patrones de diseño

- **Builder**: construcción incremental del AFN y del código emitido.
- **Strategy**: alternativas de minimización (Hopcroft, Moore) y de lenguajes objetivo en el emitter.
- **Visitor**: recorrido del AST sin acoplar lógica al árbol.
- **Factory**: creación de estados y transiciones en NFA/DFA.
- **Facade**: orquestador del pipeline que oculta la complejidad de los módulos internos.
- **Pipeline**: flujo lineal donde cada módulo consume la salida del anterior.

---

## 9. Requerimientos no funcionales

| RNF | Enfoque |
|-----|---------|
| Rendimiento | Tabla de transiciones O(1) por carácter; DFA minimizado; compilación separada de la ejecución |
| Confiabilidad | Validación por fase; error handler centralizado; recuperación ante caracteres ilegales |
| Escalabilidad | Módulos desacoplados; sub-AFNs construibles en paralelo |
| Mantenibilidad | Interfaces bien definidas; cohesión por módulo; pruebas por fase |
| Seguridad | Validación estricta en el parser; límites de recursión en la expansión de regex |
| Extensibilidad | Nuevos targets de código vía Strategy; nuevos operadores regex vía Visitor |

---

## 10. Flujo resumido

```mermaid
flowchart LR
    A[.l] --> B[AST]
    B --> C[Regex]
    C --> D[AFN]
    D --> E[AFD]
    E --> F[AFD mín.]
    F --> G[Código]
    G --> H[Scanner]
    H --> I[Tokens]
```

---

## Referencias

- Aho, Sethi, Ullman — *Compilers: Principles, Techniques, and Tools*
- Thompson, K. — *Regular Expression Search Algorithm* (CACM 1968)
- Hopcroft, J. — *An n log n Algorithm for Minimizing States in a Finite Automaton*
