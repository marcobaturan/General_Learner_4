# General Learner 4 (GL4): Cognitive Simulation & Situational Mapping

General Learner 4 is an autonomous intelligent system inspired by the principles of the **Universal Learner** (Fritz et al., 1989) and modern cognitive neuroscience. It demonstrates emergent planning, biological homeostasis, and probabilistic reasoning within a 2D environment.

## 🧠 Cognitive Architecture

The agent operates on a **Situational Transition Model**, where it learns the relationship between its perceptions, its actions, and the resulting state changes.

### 1. Situational World Map (Conceptual Network)
Inspired by the **O'Keefe & Nadel Hippocampal Model**, the agent builds a relational graph of the world:
- **Nodes**: Unique 3x3 visual perceptions (Situations).
- **Edges**: Learned actions that link these situations.
- **Cognitive Map**: The agent treats the environment as a network, allowing it to calculate shortcuts and detours using its situational memory.

### 2. Visuospatial Agenda (Mental Imagery)
Unlike simple reactive agents, GL4 maintains a **Visuospatial Working Memory**:
- When a goal is identified (e.g., a Battery), the robot performs a **mental search** through its situational graph.
- It generates an **Agenda**: a sequence of "Mental Landmarks" (expected perceptions) that it predicts it will encounter.
- This allows for high-level goal-oriented behavior beyond simple stimulus-response.

### 3. Bayesian Decision Engine (Thompson Sampling)
Action selection utilizes **Bayesian Inference** to balance exploration and exploitation:
- **Thompson Sampling**: The agent maintains a probability distribution for each action's success.
- **Probabilistic Action**: Instead of always picking the "best" move, it samples from a **Beta Distribution**. This mimics biological uncertainty, allowing the robot to explore when unsure and exploit when confident.
- **Adaptive Learning**: As rules gain weight, their probability curves tighten, leading to more decisive autonomous behavior.

### 4. Biological Homeostasis & Forgetting
The system implements a homeostatic cycle (Sleep/Dream) to maintain cognitive health:
- **Forgetting Curve**: Based on Ebbinghaus's principles, information decays over time. 
- **Differential Persistence**: Spatial landmarks (nodes in the graph) have a **protected status**. They decay at 1/5th the rate of episodic rules, ensuring that the "Map of the World" remains stable while fleeting behavioral noise is pruned.
- **Memory Consolidation**: During the "Dream" phase, episodic experiences are converted into stable transition rules and the semantic graph is updated.

## 🛠️ Technical Implementation
- **Core**: Python 3.11+
- **Graphics**: Pygame (Hardware accelerated rendering)
- **Persistence**: SQLite3 (Semantic Rule Engine)
- **Algorithm**: BFS Graph Planning / Bayesian Thompson Sampling

## 🚀 How to Run
```bash
python main.py
```
- **GUIDE MODE**: Click the grid to "teach" the robot specific paths and watch its graph grow.
- **TOGGLE BAYES**: Switch between deterministic and probabilistic (Thompson Sampling) decision-making.
- **SHOW NETWORK**: Visualize the robot's internal "Mental Map."

---
*Created as an advanced implementation of agentic AI and autonomous cognitive systems.*
