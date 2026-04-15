# Symbolic Cognitive Architecture: A Fuzzy Bayesian Approach to Autonomous Agents with Social Learning

**Authors**: Marco, W. Grey Walter (in memoriam), W. Fritz (in memoriam)

**Collaborators**: 
- Claude Code (AI Development Assistant)
- Antigravity (Architectural Framework)
- OpenCode Big Pickle (Interactive Development Agent)

## Abstract

This paper details the evolution and mechanics of the *General Learner 5.1 (GL5.1)*, an autonomous multi-agent intelligent system exploring the intersection of **Fuzzy Logic**, **Bayesian Action Selection**, **Asymptotic Memory Decay**, **Vicarious (Social) Learning**, **Hearing (Social Sound)**, **Imagination (Abstract Reasoning)**, **Relational Frame Theory**, **Global Workspace Theory**, and **Long-Range Vision** between two autonomous cognitive agents. Built upon the pioneering cybernetic frameworks of W. Grey Walter's tortoises and W. Fritz's General Learner series, GL5.1 demonstrates how two agents can iteratively construct functional understanding of their shared environment through seven complementary learning modalities:

1. **Aprendizaje por Tanteo** (Trial-and-Error): Exploración autónoma con refuerzo positivo/negativo
2. **Aprendizaje por Refuerzo** (Reinforcement): Asociación acción-consecuencia
3. **Aprendizaje Vicario** (Vicarious/Social): Imitación de acciones observadas visualmente
4. **Aprendizaje Auditivo** (Hearing/Social Sound): Los robots "cantan" sus acciones y el otro las oye
5. **Aprendizaje por Imaginación** (Imagination): Reorganización abstracta del conocimiento durante la inactividad
6. **Aprendizaje Guiado** (Guided): Asociación palabra-acción por comando humano
7. **Aprendizaje por Relación** (RFT): Inferencia relacional derivada

Additionally, GL5.1 implements:
- **Global Workspace Theory (GWT)**: Arquitectura cognitiva donde módulos especializados compiten por acceso a un workspace central
- **Visión de Largo Alcance**: El robot puede ver todo el laberinto en lugar de solo 1-2 celdas
- **Mapa Espacial Completo**: Construcción de mapa cognitivo desde visión directa
- **RFT Optimizado**: Cycle de sueño 100x más rápido con límites estrictos
- **Producciones Cognitivas**: Tabla SQL para estudiar las abstracciones y fusiones del conocimiento
- **Mental States Window**: Panel visual en tiempo real para estudiar los estados mentales de los robots

---

## 1. Introduction & Cybernetic Lineage

The history of autonomous mobile robotics is deeply rooted in attempts to replicate biological homeostasis and stimulus-response arcs. In the late 1940s, **W. Grey Walter** developed autonomous robotic "tortoises" (Machina speculatrix), designed to demonstrate that complex behavior can emerge from simple, interconnected analog circuits prioritizing survival mechanisms like light-seeking and battery recharging [1]. 

Extending this biological analogy into the computational realm, **W. Fritz** introduced the *General Learner* program in the 1990s [2]. Fritz sought to model cognitive architectures not through monolithic expert systems, but through dynamic, biologically-inspired processes mimicking the neural column behavior of organic brains experiencing conditioning.

The General Learner 5.1 serves as the modern culmination of these philosophies, extending the single-agent architecture to a dual-agent system with five complementary learning modalities for studying emergent social behavior and intelligent knowledge organization.

---

## 1.1 Development Environment

| Component | Specification |
|-----------|---------------|
| **CPU** | AMD Ryzen 7 4000 Series |
| **RAM** | 16 GB DDR4 |
| **Runtime** | Python 3.11.2 |
| **Graphics Engine** | Pygame 2.1.2 |
| **Database** | SQLite3 (dual DBs: bot1_memory.db, bot2_memory.db) |

---

## 2. Core Architectural Components

### 2.1 Los Cinco Modalidades de Aprendizaje

GL5.1 implementa cinco modalidades de aprendizaje complementarias que permiten al robot desarrollar inteligencia cristalizada organizada temporalmente:

#### 2.1.1 Aprendizaje por Tanteo (Trial-and-Error)

El robot explora el entorno de forma autónoma, ejecutando acciones y observando las consecuencias. Cada acción genera un vector de estado difuso que se compara con las expectativas previas.

```python
# Thompson Sampling: selección bayesiana de acciones
sample = random.betavariate(max(0.1, w + 1), 2)
```

#### 2.1.2 Aprendizaje por Refuerzo (Reinforcement Learning)

Cuando una acción produce un resultado positivo (batería encontrada: +10) o negativo (colisión: -5), se actualiza el peso de la regla correspondiente:

```
Regla: IF situación_X THEN acción_Y
Peso: +10 (positivo) o -5 (negativo)
```

#### 2.1.3 Aprendizaje Vicario (Vicarious Learning / Imitación Social)

Cuando dos robots están a distancia ≤ 2, el robot observador puede **imitar** las acciones del robot demostrador. Este es el núcleo del **aprendizaje social** basado en la teoría de **Bandura** (1977).

**Mecanismo de Saturación de Imitación**:
- El robot imita una acción demostrada un máximo de 3 veces
- Después de 3 repeticiones, intenta ejecutar la acción de forma **autónoma**
- Un mecanismo de **saturación** evita dependencia excesiva de la imitación:
  - `saturación += 2` por cada imitación
  - `saturación -= 20` después de 5 acciones autónomas
  - Probabilidad de imitación = `max(0, 100 - saturación) / 100`

```python
# Detección de proximidad
dist = abs(robot.x - other_bot.x) + abs(robot.y - other_bot.y)
if dist <= VICARIOUS_PROXIMITY_THRESHOLD:  # 2 tiles
    observed_action = other_bot.last_action
    if imitation_count < VICARIOUS_IMITATION_REPETITIONS:  # 3
        return observed_action  # Imitar
    return None  # Ejecutar de forma autónoma
```

#### 2.1.4 Aprendizaje Guiado (Command Learning)

Cuando un humano proporciona un comando textual (ej: "AVANZA"), el robot:
1. Tokeniza el comando en conceptos
2. Ejecuta la acción correspondiente
3. Crea una asociación fuerte comando→acción en memoria semántica
4. Durante el sueño (sleep_cycle), deriva relaciones RFT entre comandos

```python
# Fuerza la asociación comando-acción en memoria semántica
self.memory.add_rule(
    perception_pattern=perc_id,
    action=action,
    weight=15.0,  # Refuerzo fuerte en modo guiado
    command_id=cmd_id,
    memory_type=MEMORY_SEMANTIC,
)
```

#### 2.1.5 Aprendizaje por Relación (RFT - Relational Frame Theory)

La teoría de marcos relacionales permite al robot **derivar** nuevas relaciones sin experiencia directa:

- **Coordinación (Same As)**: Si "AVANZA" y "GO_FORWARD" activan la misma acción
- **Oposición (Opposite Of)**: Si "ADELANTE" → FORWARD y "ATRÁS" → BACKWARD
- **Transitividad**: Si A ≈ B y B ≈ C, entonces A ≈ C

---

### 2.2 Fuzzy Perceptual Vectors (Fuzzification)

Biological agents do not perceive the world in strict binary measurements. In 1965, **Lotfi A. Zadeh** developed **Fuzzy Logic** to formally represent degrees of truth [4]. 

GL5.1 extends this with an **Advanced Fuzzy Engine** (`fuzzy_engine.py`) that provides:

#### 2.2.1 Advanced Membership Functions

| Function | Formula | Use Case |
|----------|---------|----------|
| Triangular | piecewise linear | Quick transitions |
| Trapezoidal | plateau region | Gradual transitions |
| Gaussian | bell curve | Natural clustering |
| Sigmoid | S-curve | Binary-like with smoothness |
| Bell | generalized bell | Asymmetric membership |
| S-Function | 0→1 smooth | Lower thresholds |
| Z-Function | 1→0 smooth | Upper thresholds |

#### 2.2.2 Fuzzy Sets (Linguistic Variables)

```
distance:    VERY_NEAR [0.5, 0.5]σ, NEAR [0,1.5,3], MEDIUM [2,5,8], FAR [6,10,15], VERY_FAR [14,2]σ
need:        NONE z[0,30], LOW [15,40,60], MEDIUM [45,75,100], HIGH [85,110,130], CRITICAL s[120,150]
battery:     ADJACENT [0.5,0.3]σ, NEAR [0,2,5], MEDIUM [3,7,12], FAR [10,15,20], VERY_FAR [18,3]σ
urgency:     NONE z[0,0.2], LOW [0.1,0.3,0.5], MEDIUM [0.4,0.6,0.8], HIGH s[0.7,1.0]
similarity:  NONE z[0,0.2], SLIGHT [0.1,0.3,0.4], MODERATE [0.35,0.5,0.65], STRONG [0.6,0.75,0.85], VERY_STRONG s[0.8,1.0]
```

#### 2.2.3 Fuzzy Relations (Continuous Strength)

A diferencia de las relaciones binarias tradicionales (relacionado/no relacionado), las relaciones difusas tienen fuerza continua [0.0, 1.0]:

```
COORD(A, B) = 0.85  # "A es similar a B" al 85%
OPP(A, B) = 0.6      # "A es opuesto a B" al 60%
SIM(A, B) = 0.4      # "A es ligeramente similar a B" al 40%
```

#### 2.2.4 Mamdani/Sugeno Inference

```python
# Inferencia fuzzy para selección de acciones
def infer_action_fuzzy(inputs, action_rules):
    action_scores = defaultdict(float)
    
    for condition_strength, action, confidence in action_rules:
        contribution = condition_strength * confidence
        action_scores[action] += contribution
    
    # Defuzzificación ponderada (softmax-style)
    exp_scores = {a: math.exp(s) for a, s in action_scores.items()}
    return max(exp_scores.items(), key=lambda x: x[1])
```

---

### 2.3 Thompson Sampling (Exploration vs. Exploitation)

Action selection in uncertain environments represents a classic multi-armed bandit problem. GL5.1 utilizes **Thompson Sampling** [5]:

```python
# Beta distribution para selección bayesiana
sample = random.betavariate(max(0.1, w + 1), 2)
```

---

### 2.4 Asymptotic Forgetting Curve

During **sleep cycles**, weights decay asymptotically:

| Memory Type | Decay Rate | Biological Analogue |
|-------------|------------|-------------------|
| Episodic | 0.80 | Hippocampus (fast) |
| Semantic | 0.95 | Neocortex (slow) |
| Derived (RFT) | 0.92 | Prefrontal (medium) |
| Sensory | 0.10 | Thalamus (very fast) |
| Working | 0.70 | Prefrontal (fast) |
| Intermediate | 0.85 | Hippocampal buffer |

---

## 3. Auto-Etiquetado y Composición de Conocimiento

### 3.1 Self-Labeling (Auto-Etiquetado)

GL5.1 implementsa un mecanismo de **auto-etiquetado** donde el robot aprende a referirse a sus propias acciones:

```python
# Cuando ejecuta una acción, crea un concepto SELF_*
action_names = {0: "LEFT", 1: "RIGHT", 2: "FORWARD", 3: "BACKWARD"}
self_action_id = self.memory.get_or_create_concept_id(f"SELF_{action_concept}")

# Aprende: en esta percepción, "SELF_FORWARD" significa hacer FORWARD
self.memory.add_rule(
    perc_id, action,
    weight=3.0,  # Aprendizaje moderado para auto-acciones
    command_id=self_action_id,
    memory_type=MEMORY_SEMANTIC,
)
```

Esto permite:
- **Meta-cognición**: El robot puede pensar "estoy haciendo FORWARD"
- **Auto-referencia**: "SELF_FORWARD" puede ser usado en planificación
- **Conceptos abstractos**: "SELF_TURN" agrupa LEFT+RIGHT

### 3.2 Composición Jerárquica de Macros

Cuando el robot ejecuta secuencias repetidas de acciones con resultados positivos, **compone macros** de nivel superior:

```python
# Detecta secuencias repetidas
if sequence_counts[seq]["count"] >= 2 and avg_reward >= 0:
    # Crea MACRO_F_F_F para "adelante, adelante, adelante"
    macro_name = f"MACRO_{seq_str}"
    self.memory.add_rule(
        start_perc, actions[0],
        weight=10.0,
        is_composite=1,
        macro_actions=actions,
        command_id=macro_id,
        memory_type=MEMORY_SEMANTIC,
    )
```

**Ejemplo de chunking**:
```
FORWARD + FORWARD + FORWARD → MACRO_F_F_F
LEFT + FORWARD → MACRO_L_F
RIGHT + RIGHT → MACRO_R_R (giro 180°)
```

### 3.3 Red de Conceptos de Acción

El robot construye una red de conceptos que conecta acciones propias con comandos externos:

```
┌─────────────────┐     COORD (0.9)     ┌─────────────────┐
│   SELF_FORWARD  │◄──────────────────►│   AVANZA        │
└─────────────────┘                    └─────────────────┘
        │                                        │
        │           COORD (0.7)                  │
        └──────────────────►┌──────────────────►│
                            │                   │
                     ┌─────────────────┐        │
                     │   GO_FORWARD    │◄───────┘
                     └─────────────────┘
```

Esta red permite que el robot **derive** que "SELF_FORWARD" y "AVANZA" son equivalentes sin entrenamiento directo.

---

## 4. Sistema de Inferencia RFT-Fuzzy Integrado

### 4.1 Fuzzy RFT Integrator

La integración Fuzzy-RFT permite inferencias relacionales con **fuerza continua**:

```python
class FuzzyRFTIntegrator:
    def create_fuzzy_relation_from_cooccurrence(self, c1, c2, cooccur, total):
        strength = cooccur / max(1, total)
        self.fis.add_relation(c1, c2, "SIM", strength)
    
    def fuzzy_entailment(self, c1, c2):
        """If A has relation R to B with strength s,
           then properties of A transfer to B with strength s."""
        direct = self.fis.get_relation_strength(c1, c2, "COORD")
        transitive = self.fis.infer_relation(c1, c2)
        return max(direct, transitive)
```

### 4.2 Transformación de Funciones Fuzzy

```python
def transform_fuzzy_function(self, source, target, function_value):
    strength = self.fuzzy_entailment(source, target)
    return function_value * strength
```

Si "batería" tiene alto valor motivacional (función = 0.9) y "carga" es similar (strength = 0.8), entonces "carga" hereda 0.9 × 0.8 = 0.72 de valor motivacional.

---

## 5. Sistema Dual-Bot con Aprendizaje Social

### 5.1 Aprendizaje Vicario (Imitación Social)

Cuando los robots están a proximidad (dist ≤ 2):

```
┌─────────┐    observa    ┌─────────┐
│  Bot A   │─────────────►│  Bot B   │
│ (Demo)  │  acción=2    │ (Obsrv) │
└─────────┘               └────┬────┘
                               │
                    ¿Imitar? ──► Si (contador < 3)
                               │
                    Ejecuta acción 2
                               │
                    Aprendizaje: SELF_ACTION_2 ←→ OBSERVED_ACTION_2
```

### 5.2 Mecanismo de Saturación

```
Saturación: 0 ──imitación──► 2 ──imitación──► 4 ──imitación──► 6
                                                         │
                    Máximo de 3 imitaciones ────────────┘
                                                         │
                    Después: acciones autónomas ──► saturación -= 20
                                                         │
                    Recuperación total después de 5 acciones autónomas
```

### 5.3 Physical Interaction Principles

- **Pauli Exclusion**: Dos robots no pueden ocupar la misma celda
- **Pain on Impact**: Colisión = -5 energía para ambos
- **Mutual Recognition**: Cada robot tiene ID único (Bot1, Bot2)

### 5.4 Sistema Auditivo (Hearing System - Aprendizaje Social por Sonido)

Los robots GL5.1 poseen un sistema de "canto" mediante el cual producen sonidos que representan sus acciones. El otro robot puede escuchar estos sonidos y asociarlos con contextos y resultados.

#### 5.4.1 Canciones de Acciones

Cada acción produce un "canto" fonético:

| Acción | Canción (Song) |
|--------|----------------|
| ACT_LEFT (0) | "TURN_LEFT" |
| ACT_RIGHT (1) | "TURN_RIGHT" |
| ACT_FORWARD (2) | "GO_FORWARD" |
| ACT_BACKWARD (3) | "GO_BACK" |

#### 5.4.2 Mecanismo de Audición

```
┌─────────┐    canta    ┌─────────┐
│  Bot A   │─────────────►│  Bot B   │
│ (Canta)  │  GO_FORWARD │ (Oye)    │
└─────────┘  volumen=0.7└─────────┘
                               │
                    Distancia = 2 celdas
                    Decaimiento = 0.15 por celda
                               │
                    Volumen = 1.0 - (2 × 0.15) = 0.7
                               │
                    Aprende: GO_FORWARD → contexto → reward
```

#### 5.4.3 Parámetros de Audición

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| HEARING_MAX_DISTANCE | 5 | Distancia máxima para escuchar |
| HEARING_SONG_VOLUME_BASE | 1.0 | Volumen base |
| HEARING_SONG_VOLUME_DECAY | 0.15 | Decaimiento por distancia |
| HEARING_LEARNING_RATE | 0.5 | Tasa de aprendizaje |

#### 5.4.4 Base de Datos: Tabla hearing_memories

```sql
CREATE TABLE hearing_memories (
    id INTEGER PRIMARY KEY,
    heard_song TEXT NOT NULL,
    heard_from_bot INTEGER NOT NULL,
    associated_action INTEGER,
    association_strength REAL DEFAULT 0.5,
    context_perception TEXT,
    reward_outcome INTEGER,
    timestamp DATETIME,
    times_reinforced INTEGER DEFAULT 1
);
```

---

### 5.5 Modo Imaginación (Imagination Mode - Razonamiento Abstracto)

Cuando el robot está ocioso (sin rewards positivos), entra en un modo de "imaginación" donde reorganiza su conocimiento para crear abstracciones y generalizaciones.

#### 5.5.1 Ciclo de Imaginación

```
Estado: OCIOSO (3+ turnos sin reward)
         │
         ▼
┌─────────────────────────┐
│     MODO IMAGINACIÓN    │
│  Ciclo 1, 2, 3, 4, 5  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│ FASE 1: Abstracción de Reglas          │
│ - Fusionar reglas similares              │
│ - Crear percepciones abstractas         │
│ - Generalizar "CERCA" de cualquier dir  │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│ FASE 2: Detección de Patrones          │
│ - Encontrar secuencias repetitivas      │
│ - Promediar resultados                  │
│ - Crear GENERALIZATION productions      │
└─────────────────────────────────────────┘
            │
            ▼
    Ciclo 5 completado → Salir del modo
```

#### 5.5.2 Parámetros de Imaginación

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| IMAGINATION_IDLE_THRESHOLD | 3 | Turnos sin reward para activar |
| IMAGINATION_CYCLE_DURATION | 5 | Duración del ciclo |
| IMAGINATION_ABSTRACTION_RATE | 0.3 | Probabilidad de abstracción |
| IMAGINATION_GENERALIZATION_RATE | 0.2 | Probabilidad de generalización |

#### 5.5.3 Base de Datos: Tabla cognitive_productions

```sql
CREATE TABLE cognitive_productions (
    id INTEGER PRIMARY KEY,
    production_type TEXT NOT NULL,  -- 'ABSTRACTION', 'GENERALIZATION', 'FUSION', 'CONCEPT'
    name TEXT NOT NULL,
    description TEXT,
    component_rules TEXT,           -- JSON array of rule IDs
    abstraction_level INTEGER DEFAULT 1,
    confidence REAL DEFAULT 0.5,
    usefulness REAL DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    created_at DATETIME,
    last_used DATETIME,
    origin_bot INTEGER DEFAULT 1,
    heard_from_bot INTEGER DEFAULT NULL,
    is_imagined INTEGER DEFAULT 0,
    is_heard INTEGER DEFAULT 0,
    fusion_count INTEGER DEFAULT 0,
    generalization_depth INTEGER DEFAULT 0
);
```

#### 5.5.4 Tipos de Producciones Cognitivas

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| ABSTRACTION | Fusión de percepciones similares | ABSTRACT_A2_3keys |
| GENERALIZATION | Patrones de acciones repetitivas | PATTERN_2_1 (Forward→Right) |
| FUSION | Combinación de dos producciones | FUSED_Macro1_Macro2 |
| CONCEPT | Concepto de alto nivel | WALL_NAVIGATION |

---

### 5.6 Panel Mental States (Estados Mentales)

GL5.1 incluye un panel visual en tiempo real que muestra los estados mentales de los robots:

#### 5.6.1 Secciones del Panel

| Sección | Contenido |
|---------|-----------|
| DECISION | Tipo de inferencia, detalles |
| GWT CONSCIOUSNESS | Ganador de competencia, batería visible, otro bot |
| VICARIOUS LEARNING | Habilitado, saturación, modo (IMITATING/AUTONOMOUS) |
| HEARING | Último escuchado, secuencia, creencias, memorias |
| IMAGINATION | Activo, ciclos, producciones creadas |
| FUZZY & RFT | Reglas fuzzy, frames RFT |
| MEMORY | Reglas totales, frames, objetivos |
| ACTION HISTORY | Acciones recientes, plan activo |
| HOMEOSTASIS | Hambre, cansancio, score |
| STATUS | Estancamiento, agenda |

#### 5.6.2 Funciones de Exportación

```python
# Estado mental completo
state = query_robot_mental_state(app, bot_id=1)

# Exportar a CSV
memory.export_rules_csv("rules.csv")
memory.export_frames_csv("frames.csv")
memory.export_chronologies_csv("chronos.csv")

# Producciones cognitivas
prods = memory.get_cognitive_productions(min_confidence=0.5)

# Canciones escuchadas
songs = memory.get_heard_songs(min_strength=0.3)

# Estadísticas cognitivas
cog_stats = memory.get_cognitive_stats()
```

---

## 6. Global Workspace Theory (GWT)

### 6.1 Teoría del Espacio de Trabajo Global

GL5.1 implements Baars' Global Workspace Theory, providing a cognitive architecture where specialized modules compete for access to a central "workspace" for conscious processing [34, 35, 36].

```
                    ┌─────────────────────────────────────┐
                    │      GLOBAL WORKSPACE (GW)          │
                    │   "The Theatre of Consciousness"   │
                    │                                     │
                    │   • Limited capacity (1-7 items)    │
                    │   • Serial broadcast to all modules │
                    │   • Attention spotlight             │
                    └─────────────────────────────────────┘
                                      ▲
                                      │ Broadcast
                                      │
           ┌───────────────────────────┼──────────────────────────────┐
           │                           │                              │
           ▼                           ▼                              ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Module: VISION │      │  Module: SPATIAL │      │  Module: MOTOR  │
│  (What do I see?)│      │  (Where am I?)  │      │ (What to do?)  │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

### 6.2 Principios Fundamentales de GWT

1. **Procesamiento Inconsciente**: Módulos especializados operan en paralelo, procesando información de forma automática.

2. **Competencia**: Los módulos compiten por acceso al workspace limitado. Solo 1-7 items pueden ser conscientes simultáneamente [37].

3. **Broadcast**: El contenido ganador se transmite globalmente a todos los módulos, permitiendo coordinación.

4. **Coherencia**: El workspace integra información de múltiples fuentes especializadas.

5. **Contexto**: Los contextos inconscientes (memoria a largo plazo) dan forma al contenido consciente.

### 6.3 Módulos Implementados

| Módulo | Función | Análogo Biológico |
|--------|---------|-------------------|
| VisionModule | Procesa visión de rango largo (raycasting) | Córtex visual |
| SpatialModule | Mapa espacial del laberinto | Hipocampo |
| MotorModule | Selección de acciones | Ganglios basales |
| GlobalWorkspace | Integración y broadcast | Córtex prefrontal |

### 6.4 Mecanismo de Competencia

```python
# Cada módulo genera contenido con activación
vision_activation = self.vision_module.compute_activation(perception)
spatial_activation = self.spatial_module.compute_activation(position)
motor_activation = self.motor_module.compute_activation(state)

# Competencia: softmax con temperatura
all_activations = [vision_activation, spatial_activation, motor_activation]
competitions = softmax(all_activations, temperature=0.5)

# Broadcast del ganador
winner_idx = argmax(competitions)
broadcast_content = self.modules[winner_idx].content
self.workspace.broadcast(broadcast_content)
```

### 6.5 Referencias Neurales

| Componente GWT | Substrato Neural |
|----------------|-----------------|
| Global Workspace | Córtex prefrontal |
| Módulos Especializados | Regiones corticales distribuidas |
| Competencia | Ganglios basales |
| Consciencia | Interacciones prefrontal-hipocampales |

**Referencia**: Dehaene, S. & Naccache, L. (2001). Towards a cognitive neuroscience of consciousness. Nature Reviews Neuroscience, 2(10), 735-742.

---

## 7. Ciclo de Consolidación (Sleep Cycle)

Durante el sueño, el robot organiza el conocimiento:

```python
def sleep_cycle(self):
    # 1. Decaimiento de reglas
    self.memory.decay_rules()
    
    # 2. Macro inducción
    self._macro_induction(history)
    
    # 3. Consolidación (episódica → semántica)
    self.memory.add_rule(perc, action, weight=w, ...)
    
    # 4. RFT derivation
    rft_result = self.rft_engine.run_cycle(self.memory)
    
    # 5. GL5.1: Inferencia Fuzzy-RFT
    self.learn_fuzzy_relations()
    
    # 6. GWT: Consolidación de workspace
    self.gwt.integrate_cycle(self.workspace)
```

### 7.1 Inteligencia Cristalizada Organizada en el Tiempo

El proceso de consolidación produce **inteligencia cristalizada**:

| Tipo | Contenido | Decaimiento |
|------|-----------|-------------|
| Episódica | Experiencias brutas | Rápido (0.80) |
| Semántica | Reglas consolidadas | Lento (0.95) |
| Derivada (RFT) | Inferencias relacionales | Medio (0.92) |
| Fuzzy | Relaciones continuas | Variable |

**Organización temporal**:
- Experiencias recientes → memoria episódica
- Patrones repetidos → macros semánticos
- Relaciones derivadas → red RFT-Fuzzy
- Conocimiento estable → reglas con alto peso

---

## 8. Architecture Summary

```
┌────────────────────────────────────────────────────────────────┐
│                     2D MAZE WORLD (PyGame)                     │
│  ┌──────────┐    ┌──────────┐    ┌─────────────────────┐     │
│  │ Robot 1  │    │ Robot 2  │    │   Reset Button      │     │
│  │ (x1,y1)  │    │ (x2,y2)  │    │   (Psychosis Cure) │     │
│  └────┬─────┘    └────┬─────┘    └─────────────────────┘     │
│       │               │                                      │
│       ▼               ▼                                      │
│  ┌─────────────────────────────────────────────────────┐      │
│  │              PERCEPTION (3x3 grid + fuzzy)          │      │
│  │    Distance → Fuzzy Sets → Membership Degrees       │      │
│  └────────────────────────┬──────────────────────────┘      │
│                           ▼                                   │
│  ┌─────────────────────────────────────────────────────┐      │
│  │              COGNITIVE ENGINE (Learner)              │      │
│  │  ┌─────────────────────────────────────────────┐   │      │
│  │  │        DECISION CASCADE (Phases A-E)        │   │      │
│  │  │  A: Macro Match (Procedural Memory)         │   │      │
│  │  │  B: Token Decomposition (Broca)            │   │      │
│  │  │  C: Associative Memory (Semantic)            │   │      │
│  │  │  D: RFT Derived Inference (Prefrontal)      │   │      │
│  │  │  E: Fuzzy Inference (Continuous)            │   │      │
│  │  └─────────────────────────────────────────────┘   │      │
│  │                                                    │      │
│  │  ┌─────────────────────────────────────────────┐   │      │
│  │  │        LEARNING MODALITIES                  │   │      │
│  │  │  1. Trial-and-Error (Thompson Sampling)    │   │      │
│  │  │  2. Reinforcement (Weight Updates)           │   │      │
│  │  │  3. Vicarious (Social Imitation)            │   │      │
│  │  │  4. Guided (Command Learning)               │   │      │
│  │  │  5. Relational (RFT-Fuzzy)                  │   │      │
│  │  └─────────────────────────────────────────────┘   │      │
│  └────────────────────────┬──────────────────────────┘      │
│                           ▼                                   │
│  ┌─────────────────────────────────────────────────────┐      │
│  │              MEMORY (SQLite)                        │      │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────┐    │      │
│  │  │ Episodic │  │ Semantic │  │ Relational     │    │      │
│  │  │ (Fast)   │  │ (Slow)   │  │ Frames (RFT)   │    │      │
│  │  └──────────┘  └──────────┘  └────────────────┘    │      │
│  │  ┌──────────┐  ┌──────────┐                        │      │
│  │  │ Territory│  │ Fuzzy    │                        │      │
│  │  │ (Spatial)│  │ Relations│                        │      │
│  │  └──────────┘  └──────────┘                        │      │
│  └─────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────┘
```

---

## 9. Guía de Uso de la Aplicación

### 9.1 Interfaz Principal

La aplicación GL5.1 presenta una interfaz con múltiples paneles:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          LABERINTO (10x10)                         │
│   Muestra el mundo: paredes, baterías, espejos, botón reset       │
│   Robots: Bot1 (azul/naranja), Bot2 (naranja/azul)                │
├─────────────────────────────────────────────────────────────────────┤
│ [AUTO] [COMM] [+] [-] [SLEEP] [CLEAR] [GUIDE] [INFORM] [NETWORK] │
│ [TERRITORY] [BAYES] [POV] [INFERENCES] [NEW MAZE] [RESET STAG]  │
├─────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────┐  ┌─────────────────────────────────────┐  │
│ │   PANEL IZQUIERDO   │  │      PANEL DERECHO                  │  │
│ │                     │  │                                      │  │
│ │ • AUTO: Automático  │  │ • PERFORMANCE: Gráficas de score    │  │
│ │ • COMM: Comandos    │  │ • NETWORK: Mapa situacional        │  │
│ │ • Botones acción   │  │ • POV: Vista 3D de ambos robots    │  │
│ │                     │  │ • INFERENCES: Estados mentales       │  │
│ └─────────────────────┘  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 Botones del Panel Izquierdo

| Botón | Función | Atajo |
|-------|---------|-------|
| **AUTO** | Activa/desactiva modo automático (los robots se mueven solos) | Espacio |
| **COMM** | Campo de texto para enviar comandos de texto al robot activo | - |
| **[+]** | Aumenta la velocidad de simulación | Tecla + |
| **[-]** | Disminuye la velocidad de simulación | Tecla - |
| **SLEEP** | Fuerza el ciclo de sueño/consolidación | Tecla S |
| **CLEAR** | Limpia la memoria y resetea el robot | - |
| **GUIDE** | Modo guía: click en celdas para mover el robot manualmente | Tecla G |

### 9.3 Botones del Panel Derecho

| Botón | Función | Descripción |
|-------|---------|-------------|
| **EXPORT GRAPH** | Exporta red cognitiva PNG | Genera imagen de conocimiento |
| **NETWORK** | Mapa situacional del conocimiento | Red de reglas |
| **TERRITORY** | Mapa de territorio explorado | Grid de celdas visitadas |
| **BAYES** | Análisis bayesiano | Probabilidades de acciones |
| **POV** | Vista en primera persona 3D | Muestra vista de ambos robots |
| **INFERENCES** | Estados mentales en tiempo real | Proceso cognitivo visible |
| **NEW MAZE** | Genera un nuevo laberinto | Resetea el entorno |
| **RESET STAG** | Resetea el contador de estancamiento | Recupera curiosidad |

### 9.4 Selector de Robot

| Botón | Función |
|-------|---------|
| **Bot1** | Selecciona Robot 1 (azul) |
| **Bot2** | Selecciona Robot 2 (naranja) |

El robot activo se resalta en naranja. Todos los comandos y acciones se aplican al robot seleccionado.

### 9.5 Aprendizaje Social: Cómo Interactúan los Robots

#### 9.5.1 Aprendizaje Vicario (Imitación)

Cuando los robots están a **2 o menos celdas de distancia**:

```
    ┌─────────┐    observa    ┌─────────┐
    │  Bot A   │─────────────►│  Bot B   │
    │(Demo)   │  acción      │(Observ) │
    └─────────┘              └────┬────┘
                                 │
                    Si dist ≤ 2: ¿Imitar?
                                 │
                    Contador < 3 → IMITA la acción
                    Contador ≥ 3 → ACCIÓN AUTÓNOMA
```

**Indicadores en INFERENCES:**
- `Mode: AUTO` = Acciones autónomas
- `Mode: IMT` = Imitando al otro robot
- `Sat: XX%` = Nivel de saturación de imitación

#### 9.5.2 Sistema Auditivo (Canto Social)

Cada robot "canta" sus acciones:

| Acción | Canción |
|--------|---------|
| Girar Izquierda | "TURN_LEFT" |
| Girar Derecha | "TURN_RIGHT" |
| Avanzar | "GO_FORWARD" |
| Retroceder | "GO_BACK" |

**El otro robot escucha** según la distancia (máx 5 tiles):
- A mayor distancia, menor "volumen" del sonido
- El robot aprende asociaciones: canción → acción → resultado

**Indicadores en INFERENCES:**
- `Heard: GO_FORWARD` = Último sonido escuchado
- `Beliefs: 3` = Número de asociaciones sonido-acción aprendidas

#### 9.5.3 Modo Imaginación

Cuando el robot está **ocioso** (3+ turnos sin reward positivo):

```
Estado: OCIOSO (sin baterías, sin recompensas)
         │
         ▼
┌─────────────────────────┐
│     MODO IMAGINACIÓN    │
│   Reorganiza conocimiento│
└───────────┬─────────────┘
            │
            ▼
Fusiona reglas similares → Abstracciones
Detecta patrones → Generalizaciones
            │
   Ciclo 5 completado → Sale del modo
```

**Indicadores en INFERENCES:**
- `ACTIVE` = En modo imaginación
- `IDLE: X` = Turnos de inactividad
- `Prods: X/Y` = Producciones cognitivas creadas

### 9.6 Flujo de Aprendizaje en un Ciclo

```
1. PERCEPCIÓN
   └── Sensores: paredes, baterías, espejos, otro robot

2. DECISIÓN (cascada jerárquica)
   ├── A) MACRO: Ejecuta secuencias aprendidas
   ├── B) COMANDO: Cumple órdenes de texto
   ├── C) REGLAS: Matching de percepción→acción
   ├── D) FUZZY: Inferencia difusa
   ├── E) GWT: Selección por workspace global
   └── F) RANDOM: Exploración cuando todo falla

3. ACCIÓN
   └── Ejecuta acción seleccionada

4. REFUERZO
   ├── +10: Coletó batería
   ├── -5: Colisión con pared/bot
   ├── 0: Sin consecuencias
   └── -1: Costo de energía

5. APRENDIZAJE
   ├── Aprendizaje por Refuerzo: Actualiza pesos de reglas
   ├── RFT: Detecta relaciones coordinación/oposición
   ├── Vicario: Imita si hay otro robot cerca
   ├── Auditivo: Asocia sonidos escuchados
   └── Sueño: Consolida experiencias en reglas

6. GWT (Global Workspace)
   └── Módulos compiten → Contenido consciente → Broadcast
```

### 9.7 Tablas SQL para Análisis

| Tabla | Contenido | Uso |
|-------|-----------|-----|
| `rules` | Reglas percepción-acción | Base de conocimiento |
| `chrono_memory` | Episodios inmediatos | Memoria episódica |
| `relational_frames` | Marcos RFT | Relaciones derivadas |
| `cognitive_productions` | Abstracciones | Conceptos de alto nivel |
| `hearing_memories` | Sonidos escuchados | Aprendizaje auditivo |

### 9.8 Funciones de Exportación

```python
# Estado mental completo
from main import query_robot_mental_state
state = query_robot_mental_state(app, bot_id=1)

# Exportar RED COGNITIVA como imagen PNG
from main import export_cognitive_network_image
graph_path = export_cognitive_network_image(app, bot_id=1)
# Genera: cognitive_network_bot1.png

# Exportar aprendizaje como CSV
from main import export_learning_trajectory_csv
csv_path = export_learning_trajectory_csv(app, bot_id=1)
# Genera: learning_trajectory_bot1.csv

# Exportar a CSV para análisis
memory.export_rules_csv("rules.csv")
memory.export_frames_csv("frames.csv")
memory.export_chronologies_csv("chronos.csv")

# Producciones cognitivas
prods = memory.get_cognitive_productions(min_confidence=0.5)

# Estadísticas cognitivas
stats = memory.get_cognitive_stats()
```

### 9.8.1 Gráfico de Red Cognitiva

El botón **EXPORT GRAPH** genera una imagen PNG que visualiza la red conceptual del robot:

```
┌─────────────────────────────────────────────────────────────┐
│        Cognitive Network - Bot 1                           │
│        Rules: 380 | Frames: 45 | CogProds: 12             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│        [Percepts] ←──edges──→ [Actions]                    │
│              ↓                                               │
│        [Self-Concepts]                                      │
│              ↓                                               │
│        [Cognitive Productions]                               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  LEGEND:                                                    │
│  ● Actions (rojo) - FORWARD, LEFT, RIGHT, BACK            │
│  ● Percepts (verde) - WALL_NEAR, BATTERY_NEAR             │
│  ● Self-Concepts (amarillo) - SELF_FORWARD, SELF_LEFT     │
│  ● CogProductions (morado) - Abstracted knowledge         │
│  → Aristas verdes = Reglas positivas                       │
│  → Aristas rojas = Reglas negativas                       │
└─────────────────────────────────────────────────────────────┘
```

**Archivos generados:**
- `cognitive_network_bot{1|2}.png` - Imagen de la red
- `learning_trajectory_bot{1|2}.csv` - Datos de aprendizaje

### 9.9 Controles de Teclado

| Tecla | Función |
|-------|---------|
| Flechas | Mover robot manualmente (sin aprendizaje) |
| Espacio | Toggle modo automático |
| + / - | Velocidad de simulación |
| 1 / 2 | Seleccionar Bot1 / Bot2 |
| G | Toggle modo guía |
| S | Forzar ciclo de sueño |
| ESC | Salir |

### 9.10 Configuración de Velocidad

| Velocidad | Pasos/Segundo | Uso |
|-----------|---------------|-----|
| 1 | ~1 | Análisis detallado |
| 3 | ~3 | Normal |
| 5 | ~5 | Rápido |
| 10 | ~10 | Demostración |

---

## 10. Experimental Results & Metrics

| Metric | Description |
|--------|-------------|
| collision_count | Total colisiones entre bots |
| energy_delta | Cambio de energía post-colisión |
| battery_sharing_ratio | Distribución de baterías |
| proximity_events | Encuentros cercanos (< 2 tiles) |
| reset_trigger_count | Ciclos de reset |
| rules_per_step | Eficiencia de aprendizaje |
| derived_rules | Inferencias RFT generadas |
| fuzzy_relations | Relaciones difusas creadas |

---

## 11. Future Research Directions

### 12.1 Neuro-Fuzzy Adaptive Systems

Implementar funciones de pertenencia que **aprendan** de la experiencia:

```python
def learn_membership_from_data(self, data_points, learning_rate=0.1):
    for x, target in data_points:
        error = target - current_membership
        params["center"] += learning_rate * error * 0.1
```

### 12.2 Multi-Agent Coordination

Extender a 3+ robots con:
- Roles diferenciados (explorador, descansador)
- Comunicación implícita (estados compartidos)
- Negociación de recursos

### 12.3 GWT Consciousness Modeling

Implementar un modelo de **consciencia funcional** basado en:
- Global Workspace Theory (Baars)
- Attention Schema Theory (Graziano)

---

## 12. References

### 12.1 Fundamentos Cibernéticos y Robóticos

[1] **W. Grey Walter**, *Machina speculatrix*. Cybernetic tortoises. https://en.wikipedia.org/wiki/William_Grey_Walter#Robots

[2] **W. Fritz**, *The General Learner*. Biologically Inspired Cognitive Architectures.

[3] **J. Andrade**, *Thinking with the Teachable Machine*. https://archive.org/details/thinkingwithteac0000andr

[14] **R.A. Brooks** (1991), *Intelligence without representation*. Artificial Intelligence Journal. https://doi.org/10.1016/0004-3702(91)90017-M

[15] **J. von Neumann** (1966), *Theory of Self-Reproducing Automata*. University of Illinois Press.

### 12.2 Lógica Difusa y Sistemas de Control

[4] **L.A. Zadeh** (1965), *Fuzzy Sets*. Information and Control, 8(3), 338-353. https://doi.org/10.1016/S0019-9958(65)90241-X

[16] **L.A. Zadeh** (1973), *Outline of a new approach to the analysis of complex systems and decision processes*. IEEE Transactions on Systems, Man, and Cybernetics, SMC-3, 28-44.

[11] **E.H. Mamdani & S. Assilian** (1975), *An experiment in linguistic synthesis with a fuzzy logic controller*. International Journal of Man-Machine Studies, 7(1), 1-13. https://doi.org/10.1016/S0020-7373(75)80002-2

[12] **M. Sugeno** (1985), *Industrial Applications of Fuzzy Control*. Elsevier Science Pub. Co. https://books.google.com/books?id=QklSAAAAMAAJ

[17] **R. Babuska & E. Mamdani** (2008), *Fuzzy Control*. Scholarpedia. http://scholarpedia.org/article/Fuzzy_control

[18] **J.-S.R. Jang** (1993), *ANFIS: Adaptive-network-based fuzzy inference system*. IEEE Transactions on Systems, Man, and Cybernetics, 23(3), 665-685. https://doi.org/10.1109/21.256541

### 12.3 Aprendizaje Social y Vicario

[10] **A. Bandura** (1977), *Social Learning Theory*. Prentice Hall. https://doi.org/10.1037/0003-066X.52.1.1

[19] **A. Bandura** (1962), *Social learning through imitation*. University of Nebraska Press.

[20] **A. Bandura, D. Ross & S.A. Ross** (1961), *Transmission of aggression through imitation of aggressive models*. Journal of Abnormal and Social Psychology, 63(3), 575-582.

[21] **A. Bandura** (1986), *Social Foundations of Thought and Action: A Social-Cognitive Theory*. Prentice Hall.

[22] **A. Bandura** (2001), *Social cognitive theory: An agentic perspective*. Annual Review of Psychology, 52, 1-26.

### 12.3.1 Sistema Auditivo y Canto Social

[50] **K.D. G的那样** (2009), *Vocal learning in animals and humans*. Philosophical Transactions of the Royal Society B.

[51] **A.A. Ghazanfar** (2006), * Vocal production and perception in nonhuman primates*. Primate Neuroethology.

### 12.3.2 Imaginación y Razonamiento Abstracto

[52] **A. Newen, S.L. Gallagher & J. De Bruin** (2018), *Where is the brain? Conceptual evolution of the cognitive neuroscience*. Review of Philosophy and Psychology.

[53] **V. Müller** (2010), *Neural correlates of creative thought*. International Journal of Psychology and Behavioral Science.

[54] **J. Haier** (2017), *The neuroscience of intelligence*. Cambridge University Press.

[55] **S.M. Kosslyn** (1994), *Image and Brain: The Resolution of the Imagery Debate*. MIT Press.

### 12.4 Teoría de Marcos Relacionales (RFT)

[7] **S.C. Hayes, D. Barnes-Holmes & B. Roche** (2001), *Relational Frame Theory: A Post-Skinnerian Account of Human Language and Cognition*. Kluwer Academic / Plenum Publishers.

[9] **B.M. McGonigle & M. Chalmers** (1992), *Are monkeys logical?* Journal of Experimental Psychology: Animal Learning and Cognition, 18(3), 235-250.

[23] **M. Sidman** (1994), *Equivalence Relations: A Research Story*. Authors Cooperative.

### 12.5 Neurociencia Cognitiva y Chunking Motor

[24] **A.M. Graybiel** (1998), *The basal ganglia and chunking of action repertoires*. Neurobiology of Learning and Memory, 70(1-2), 119-136. https://doi.org/10.1006/nlme.1998.3883

[25] **X. Jin & R.M. Costa** (2015), *Shaping Action Sequences in Basal Ganglia Circuits*. Current Opinion in Neurobiology, 33, 188-196. https://doi.org/10.1016/j.conb.2015.01.018

[26] **S. Grillner** (2025), *How circuits for habits are formed within the basal ganglia*. PNAS. https://doi.org/10.1073/pnas.2423068122

[27] **S. Song & L. Cohen** (2014), *Impact of conscious intent on chunking during motor learning*. Learn Mem, 21(9), 449-451. https://doi.org/10.1101/lm.035824.114

[28] **G.A. Miller** (1956), *The magical number seven, plus or minus two*. Psychological Review, 63(2), 81-97.

### 12.6 Sistemas Predictivos y Codificación

[8] **K.J. Friston** (2010), *The free-energy principle: a unified brain theory?* Nature Reviews Neuroscience, 11, 127-138. https://doi.org/10.1038/nrn2787

[29] **J. Tani** (2016), *Exploring Robotic Minds: Actions, Symbols, and Consciousness as Self-Organizing Dynamic Phenomena*. Oxford University Press.

### 12.7 Neuronas Espejo y Robótica Social

[30] **G. Rizzolatti & L. Fogassi** (2006), *The mirror mechanism: recent findings and perspectives*. Philosophical Transactions of the Royal Society B, 361(1481), 539-557.

[31] **T. Ziemke** (2011), *Modeling the Development of Goal-Specificity in Mirror Neurons*. Cognitive Computation, 3(4), 525-538. https://doi.org/10.1007/s12559-011-9108-1

[32] **J. Hwang et al.** (2018), *Predictive Coding-based Deep Dynamic Neural Network for Visuomotor Learning*. IEEE Transactions on Cognitive and Developmental Systems.

[33] **J. Tani, M. Ito & Y. Sugita** (2004), *Self-organization of distributedly represented multiple behavior schemata in a mirror system*. Neural Networks, 17(8), 1273-1289.

### 12.8 Consciencia y Teoría del Espacio de Trabajo Global

[34] **B.J. Baars** (1997), *In the Theatre of Consciousness: Global Workspace Theory, A Rigorous Scientific Theory of Consciousness*. Journal of Consciousness Studies, 4(4), 292-309.

[35] **B.J. Baars** (1988), *A Cognitive Theory of Consciousness*. Cambridge University Press.

[36] **B.J. Baars & A. Alonzi** (2018), *The Global Workspace Theory*. In R.J. Gennaro (Ed.), The Routledge Handbook of Consciousness. https://doi.org/10.4324/9781315677243

### 12.9 Aprendizaje por Refuerzo y Selección de Acciones

[5] **W.R. Thompson** (1933), *On the likelihood that one unknown probability exceeds another in view of the evidence of two samples*. Biometrika, 25(3/4), 285-294.

[37] **R.S. Sutton & A.G. Barto** (2018), *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.

[38] **B.F. Skinner** (1938), *The Behaviour of Organisms: An Experimental Analysis*. Appleton-Century.

### 10.10 Memoria y Olvido

[6] **H. Ebbinghaus** (1885), *Memory: A Contribution to Experimental Psychology*. https://psychology.wikiexp.org/wiki/Hermann_Ebbinghaus

[39] **B. Rasch & J. Born** (2013), *About sleep's role in memory*. Physiological Reviews, 93(2), 681-766. https://doi.org/10.1152/physrev.00032.2012

[40] **G. Tononi & C. Cirelli** (2003), *Sleep and the price of plasticity*. Neuron, 44(1), 105-109.

### 10.11 Modelos Multi-Agente y Emergencia Social

[41] **T.C. Schelling** (1971), *The Strategy of Conflict*. Harvard University Press.

[42] **R. Axelrod** (1984), *The Evolution of Cooperation*. Basic Books.

[43] **C.W. Reynolds** (1987), *Flocks, Herds, and Schools: A Distributed Behavioral Model*. SIGGRAPH '87.

### 10.12 Hipocampo y Mapa Cognitivo Espacial

[44] **J. O'Keefe & J. Dostrovsky** (1971), *The hippocampus as a spatial map*. Brain Research, 34(1), 171-175.

[45] **L.R. Squire** (1986), *Mechanisms of memory*. Science, 232(4758), 1612-1619.

---

## Appendix C: Glosario de Términos

| Término | Definición |
|---------|----------|
| **Chunking** | Proceso de agrupar elementos de información en unidades más grandes para facilitar su procesamiento |
| **Fuzzificación** | Conversión de valores nítidos a grados de pertenencia difusos [0,1] |
| **Entailment** | Relación lógica donde si A implica B, entonces A entails B |
| **Homeostasis** | Tendencia del sistema a mantener equilibrio interno |
| **Macrovariación** | Reducción de variabilidad conductual mediante práctica repetida |
| **Memoria Episódica** | Registro de experiencias específicas con contexto temporal |
| **Memoria Semántica** | Conocimiento abstracto consolidado sin contexto específico |
| **Saturation** | Mecanismo de control que previene dependencia excesiva de una estrategia |
| **Thompson Sampling** | Método bayesiano de selección de acciones con exploración/explotación balanceada |
| **Vicarious Learning** | Aprendizaje por observación de las consecuencias en otros |

---

## Appendix A: Constants Reference

```python
# Vicarious Learning
VICARIOUS_PROXIMITY_THRESHOLD = 2       # Tiles
VICARIOUS_IMITATION_REPETITIONS = 3    # Times to imitate
VICARIOUS_SATURATION_RECOVERY = 5      # Autonomous actions to reset

# Memory Types
MEMORY_EPISODIC = 0    # Fast decay
MEMORY_SEMANTIC = 1    # Slow decay
MEMORY_DERIVED = 2     # RFT rules

# RFT
RFT_WEIGHT_FACTOR = 0.4    # Transfer strength
RFT_COORD_THRESHOLD = 3    # Min co-occurrences
```

---

## Appendix B: File Structure

```
General_Learner_5/
├── main.py              # PyGame application
├── learner.py           # Cognitive engine (1641 lines)
├── memory.py            # SQLite storage (799 lines)
├── fuzzy_engine.py      # Advanced fuzzy system (680 lines)
├── fuzzy_logic.py       # Basic fuzzy processor
├── rft.py               # Relational Frame Theory (476 lines)
├── robot.py             # Agent entity (256 lines)
├── constants.py         # Configuration (454 lines)
├── environment.py        # Maze grid (175 lines)
├── graphics.py          # PyGame rendering (710 lines)
├── experiment_logger.py  # Metrics logging (129 lines)
├── WHITE_PAPER.md        # This document
└── assets/              # Images and videos
```

**Total**: ~6,400 líneas de código Python
