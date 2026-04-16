# Symbolic Cognitive Architecture: A Fuzzy Bayesian Approach to Autonomous Agents with Social Learning

```text
################################################################################
#  __          贬  _ _             _____                                      #
#  \ \        / / | (_)           |  __ \                                     #
#   \ \  /\  / /| |_| |_ ___ _ __ | |__) |__ _ _ __   ___ _ __                #
#    \ \/  \/ / | __| | __/ _ \ '__||  ___/ _` | '_ \ / _ \ '__|               #
#     \  /\  /  | |_| | ||  __/ |   | |  | (_| | |_) |  __/ |                  #
#      \/  \/    \__|_|\__\___|_|   |_|   \__,_| .__/ \___|_|                  #
#                                              | |                             #
#                                              |_|                             #
################################################################################
```

**Document Version**: 5.1.2 (Optimized)
**Authors**: Marco Baturan, W. Grey Walter (in memoriam), Walter Fritz (in memoriam)
**Scientific Lineage**: Schelling, Axelrod, Reynolds, von Neumann, Brooks, Bandura, Hayes, Baars

---

## Abstract

This technical white paper details the architecture and operational mechanics of **General Learner 5.1 (GL5.1)**, an advanced cognitive system featuring two autonomous agents. The architecture bridges classical cybernetics with modern AI by integrating **Fuzzy Logic**, **Bayesian Inference**, **Relational Frame Theory (RFT)**, and **Global Workspace Theory (GWT)**. Built upon the "Intelligent System" (IS) paradigm proposed by Walter Fritz, GL5.1 demonstrates how agents can perceive, learn, and act based on homeostatic drives while constructing a hierarchical semantic network through social and individual experience. Key innovations include **Dynamic Attentional Spotlights**, **Deictic Perspectival Framing**, and **Headless Cognitive Simulation** for large-scale data gathering.

---

## 1. Theoretical Foundations & Historical Lineage

### 1.1 From Machina Speculatrix to General Learner
The intellectual journey of GL5.1 begins with **W. Grey Walter's** cybernetic tortoises (1948), which proved that simple goal-seeking circuits could produce lifelike autonomous behavior. GL5.1 extends this by moving from analog circuits to a **Symbolic-Fuzzy Architecture**.

### 1.2 The Walter Fritz Paradigm: The IS Framework
Following Fritz's "Intelligent Systems", GL5.1 models the agent as a "Special System" (SP) interacting with an environment. The core data unit is the **Atomic Experience 4-tuple**:
$$x = (S_t, a, u, S_{t+1})$$
Where:
- $S_t$: Initial fuzzy situation (Perception)
- $a$: Action executed
- $u$: Utility or Pleasure/Pain signal (Reinforcement)
- $S_{t+1}$: Resulting situation (Prediction verification)

### 1.3 Paradigm Central: Stimulus → Rule → Response
Unlike hardcoded state machines, GL5.1 treats rules as **hypotheses**. The agent does not "know" what to do; it maintains a probabilistic database of response rules that compete based on historical success and current homeostatic needs.

---

## 2. Cognitive Architecture

### 2.1 Multi-Store Memory System
GL5.1 implements a neuro-inspired memory hierarchy to manage the lifecycle of information:

| Store | Capacity | Decay Rate | Biological Analogue |
|-------|----------|------------|---------------------|
| **Sensory** | Unlimited | Instant | Thalamic buffer |
| **Working** | 7 ± 2 items | Fast (0.70) | Prefrontal cortex |
| **Episodic** | 500 episodes | Medium (0.80) | Hippocampus |
| **Semantic** | Large | Slow (0.95) | Neocortex |
| **Relational**| Network-based | Slow (0.92) | Associative areas |

### 2.2 Global Workspace Theory (GWT) Implementation
GL5.1 utilizes **Baars' Theatre of Consciousness**. Multiple unconscious modules (Vision, Spatial, Motor, Homeostatic) compete for access to a central **attentional spotlight**.

**Recent Optimizations:**
- **Inhibition of Return (IOR)**: Prevents cognitive "loops" by temporarily penalizing recent winners, forcing attentional shifts.
- **Dynamic Spotlight**: The competition threshold tightens during critical states (e.g., low battery), ensuring pure serial focus on survival.
- **Entropy-Based Bidding**: Modules only bid for consciousness if their information provides a significant reduction in uncertainty (Bayesian Surprise).

---

## 3. Relational Frame Theory (RFT) & Language

### 3.1 Derived Relational Responding
Based on the work of **Steven C. Hayes**, GL5.1's RFT engine allows robots to derive knowledge without direct training through three processes:
1. **Mutual Entailment**: If A is the same as B, then B is the same as A.
2. **Combinatorial Entailment**: If A ≈ B and B ≈ C, then A ≈ C.
3. **Transformation of Functions**: If "BATTERY" is good and "CHARGER" is coordinated with "BATTERY", the "CHARGER" inherits the motivational value of the battery.

### 3.2 Social Perspective Taking (Deictic Frames)
GL5.1 implements **Deictic Framing** (I-YOU, HERE-THERE). Robots learn to distinguish between "SELF_ACTION" and "OTHER_ACTION", a fundamental requirement for **Theory of Mind**. This is visualized in the semantic network through distinction frames between the "Self" concept and the "Other" (Bot ID 99).

---

## 4. Learning & Generalization

### 4.1 Vertical Abstraction (Induction)
The **Pattern Finder** module analyzes specific response rules and induces abstract versions. For example, specific rules like `IF (Wall at North) THEN Turn Left` are abstracted into `IF (Obstacle Ahead) THEN Change Direction`.

### 4.2 Horizontal Composition (Macros)
The system performs **Action Chunking** (analogue to Basal Ganglia behavior). Repeated sequences of successful actions are compressed into **Composite Macros** (e.g., `MACRO_F_F_R` for navigating a corner).

### 4.3 Social Learning Modalities
- **Vicarious Learning**: Observing and imitating the demonstrator bot with a **Saturation Mechanism** to prevent social dependency.
- **Social Sound (Hearing)**: Robots "sing" their actions. The observer associates the phonetic signal with the perceived outcome, creating a shared "proto-language".

---

## 5. Formal Bayesian Decision Model

Action selection is handled via **Thompson Sampling** on the rule weights:
$$P(a | S) \propto \text{Beta}(\alpha = w_{pos} + 1, \beta = w_{neg} + 1)$$

The RFT engine modifies this by boosting actions from coordinated concepts:
$$w_{eff} = w_{direct} + \sum (w_{rel} \cdot \text{strength}_{RFT})$$

This ensures that "Thinking" (RFT) and "Feeling" (Reinforcement) both influence the "Acting" (Motor).

---

## 6. Visualization & Research Tools

### 6.1 Expert Semantic Network Export
The system generates a high-contrast graph of the robot's mind:
- **Teal Nodes**: Sensory Percepts
- **Red Nodes**: Motor Actions
- **Yellow Nodes**: Self-Identity Concepts
- **Purple Nodes**: Cognitive Productions (Abstractions)
- **Blue Nodes**: Heard Social Memories
- **Green/Red Edges**: Positive/Negative associations (darker indicates higher confidence).

### 6.2 Performance Metrics
Researchers can monitor the following in real-time:
- **Learning Efficiency**: Rules generated per step.
- **Homeostatic Flux**: Hunger and fatigue curves.
- **Derived Knowledge Ratio**: Rules learned via RFT vs. direct experience.

---

## 7. Conclusion & Future Directions

GL5.1 represents a significant step towards a **functional model of the synthetic mind**. By combining the rigid logic of symbolic systems with the fluid adaptability of fuzzy-Bayesian models, we have created an agent that does not just "calculate" but "perceives and understands" its environment.

**Future Work**:
- **Grammar Evolution**: Moving from single tokens to structured social communication.
- **Epigenetic Environment**: Mazes that evolve based on agent behavior.
- **Ethical Framing**: Implementing Fritz's "Ethical IS" constraints into the decision cascade.

---

## 8. Selected Bibliography

1. **Grey Walter, W.** (1950). *An imitation of life*. Scientific American.
2. **Fritz, W.** (1989). *The Intelligent System: A Mathematical Approach*.
3. **Hayes, S. C. et al.** (2001). *Relational Frame Theory: A Post-Skinnerian Account*.
4. **Baars, B. J.** (1988). *A Cognitive Theory of Consciousness*.
5. **Bandura, A.** (1977). *Social Learning Theory*.
6. **Zadeh, L. A.** (1965). *Fuzzy Sets*.
7. **Friston, K.** (2010). *The free-energy principle: a unified brain theory?* Nature Reviews Neuroscience.

---
*Developed by Marco Baturan | Cognitive Architecture Review by Claude Code 2026*
