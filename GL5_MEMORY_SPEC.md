# GL5 Memory Architecture Specification

## Executive Summary

This document specifies the implementation of a comprehensive multi-store memory system for General Learner 5 (GL5), based on neuroscientific research on human memory systems. The architecture extends GL4's existing memory model to include five distinct memory stores with biologically-inspired decay rates, transfer mechanisms, and workflow connections.

---

## 1. Memory System Overview

### 1.1 The Five Memory Stores

Based on Atkinson-Shiffrin (1968), Baddeley (1974), and contemporary neuroscience, GL5 implements:

| Store | Duration | Capacity | Biological Analogue | GL4 Equivalent |
|-------|----------|----------|---------------------|----------------|
| **Sensory Memory (SM)** | ~250ms | 12 items | Thalamus/Neocortex | Robot raw sensors (instant) |
| **Working Memory (WM)** | ~18 seconds | 4 chunks | Prefrontal Cortex | active_plan + agenda |
| **Intermediate-Term (ITM)** | ~20-30 minutes | 50 items | Hippocampus (bridge) | chrono_memory |
| **Short-Term (STM)** | ~20-30 seconds | 7 items | Parietal Cortex | Not yet implemented |
| **Long-Term (LTM)** | Indefinite | Unlimited | Neocortex | rules (semantic) |

### 1.2 Memory Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ENVIRONMENT (SENSORY INPUT)                       │
│                     Robot Sensors → Fuzzy Logic Processor                    │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SENSORY MEMORY (SM)                                   │
│  Duration: 250ms                                                            │
│  Decay Rate: 0.1 (90% loss per cycle)                                       │
│  Purpose: Raw perception buffer, immediate filtering                        │
│  Contains: Unprocessed fuzzy vectors before attention selection            │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    (Attention / Selection)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       WORKING MEMORY (WM)                                    │
│  Duration: ~18 seconds (40 cycles at 500ms/step)                          │
│  Capacity: 4 chunks max                                                     │
│  Decay Rate: 0.7 (30% loss per cycle without rehearsal)                     │
│  Purpose: Active manipulation, planning, decision-making                   │
│  Contains: active_plan, agenda, current_action_history                      │
│  Biological: Prefrontal Cortex, Central Executive (Baddeley)                │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    (Encoding / Maintenance)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTERMEDIATE-TERM MEMORY (ITM)                           │
│  Duration: ~20-30 minutes (~40-60 cycles)                                  │
│  Capacity: 50 items                                                         │
│  Decay Rate: 0.85 (15% loss per cycle)                                      │
│  Purpose: Buffer for consolidation, circadian transfer                     │
│  Contains: Recent chrono records before sleep/transfer                     │
│  Biological: Hippocampal formation (circadian bridge)                       │
│  Note: MODIFIED - This is the "sleep dump" target                          │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
              (Sleep Cycle / Circadian Transfer / Maintenance Rehearsal)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LONG-TERM MEMORY (LTM)                               │
│  Duration: Indefinite (lifetime)                                           │
│  Capacity: Unlimited                                                        │
│  Decay Rate: 0.95 (5% loss per cycle - slow, semantic)                      │
│  Purpose: Permanent knowledge storage                                       │
│  Contains: Semantic rules, procedural knowledge, RFT frames                │
│  Biological: Neocortex (consolidated)                                        │
│  Subdivisions:                                                              │
│    - Explicit (Declarative): rules with perception patterns               │
│    - Implicit (Procedural): action sequences, macros                      │
│    - Semantic: conceptual_ids, relational frames                          │
└────────────────────────────────┬────────────────────────────────────────────┘
```

---

## 2. Detailed Store Specifications

### 2.1 Sensory Memory (SM)

**Purpose**: Holds raw sensor data before attention filtering.

**Implementation**:
- Buffer size: 1 fuzzy vector (current state)
- Auto-clears after each decision cycle
- No persistence - pure immediate perception

**Biological Basis**: 
- Iconic memory (visual): 250ms, 12 items (Sperling, 1960)
- Echoic memory (auditory): 2-3 seconds
- Haptic memory: 2-4 seconds

### 2.2 Working Memory (WM)

**Purpose**: Active manipulation and planning workspace.

**Implementation**:
- Maintains: `active_plan` (max 4 action sequences)
- Maintains: `agenda` (expected future perceptions, max 4)
- Maintains: `action_history` (last 10 actions)
- Rehearsal: Items in WM that are repeated get protected from decay

**Biological Basis** (Baddeley, 1974):
- Central Executive: attention, inhibition, coordination
- Phonological Loop: rehearsal
- Visuospatial Sketchpad: spatial planning
- Episodic Buffer: integration

### 2.3 Intermediate-Term Memory (ITM)

**Purpose**: Circadian buffer - the "sleep dump" target.

**Implementation**:
- Max items: 50 most recent experiences
- Acts as staging area before sleep consolidation
- Survives between sleep cycles

**Biological Basis**:
- Research shows memory persists 20-30 minutes before either transfer to LTM or decay
- Circadian rhythms modulate this transfer (Eskin et al.)

### 2.4 Long-Term Memory (LTM)

**Purpose**: Permanent, consolidated knowledge.

**Implementation**:
- Rules table (semantic)
- Relational frames (RFT)
- Conceptual IDs (semantic categories)
- Macro actions (procedural)

**Biological Basis**:
- Synaptic consolidation: protein synthesis required
- Systems consolidation: hippocampus → neocortex
- Two types: Explicit (declarative) vs Implicit (procedural)

---

## 3. Transfer Mechanisms

### 3.1 SM → WM: Attention Selection

The fuzzy processor selects which perception features enter WM based on:
- Relevance (battery proximity)
- Novelty (changed states)
- Homeostatic need (hunger/tiredness priority)

### 3.2 WM → ITM: Encoding

Every action stores to ITM (chronological buffer) if:
- WM was active (not idle)
- Item not already in buffer

### 3.3 ITM → LTM: Consolidation (Sleep)

During `sleep_cycle()`:
1. Process ITM items in order
2. Convert to semantic rules (LTM)
3. Apply macro induction
4. Run RFT derivation (GL5)
5. Clear ITM buffer

### 3.4 WM Rehearsal Loop

If same perception-action pair repeated in WM:
- Boost weight by 1.2x (not 2x - bounded)
- Extend WM retention time
- Mark as "rehearsed" for consolidation priority

---

## 4. Decay Rates Summary

| Store | Decay Rate | Threshold | Notes |
|-------|------------|-----------|-------|
| SM | 0.1 (90%) | N/A | Immediate decay, no persistence |
| WM | 0.7 (30%) | N/A | Without rehearsal |
| ITM | 0.85 (15%) | 0.3 | Below threshold → discard |
| STM | 0.8 (20%) | 0.5 | Not fully implemented |
| LTM | 0.95 (5%) | 0.5 | Slow, semantic |

---

## 5. Implementation Changes Required

### 5.1 Memory Class Enhancements

1. Add `intermediate_memory` table for ITM
2. Add `sensory_buffer` for SM (in-memory, not persisted)
3. Add `working_memory_state` for WM tracking
4. Implement `transfer_to_ltm()` method
5. Implement `rehearse_item()` method
6. Update `decay_all_stores()` for multi-store decay

### 5.2 Learner Class Changes

1. Track WM occupancy (max 4 chunks)
2. Implement rehearsal detection
3. Call ITM→LTM transfer during sleep
4. Adjust Thompson Sampling to consider WM state

### 5.3 Constants Updates

Add new memory type constants and decay rates.

---

## 6. Backward Compatibility

The system preserves all GL4 learning pathways:
- Existing rules table format maintained
- Memory type 0 = Episodic (maps to ITM in new model)
- Memory type 1 = Semantic (maps to LTM)
- Memory type 2 = Derived (RFT, maps to LTM)

The new architecture adds layers on top without breaking existing functionality.

---

## References

1. Atkinson, R.C., & Shiffrin, R.M. (1968). Human memory: A proposed system and its control processes. Psychology of Learning and Motivation, 2, 89-195.
2. Baddeley, A.D., & Hitch, G. (1974). Working memory. The Psychology of Learning and Motivation, 8, 47-89.
3. Cowan, N. (2001). The magical number 4 in short-term memory. Behavioral and Brain Sciences, 24(1), 97-185.
4. Squire, L.R. (1986). Mechanisms of memory. Science, 232(4758), 1612-1619.
5. Ebbinghaus, H. (1885). Memory: A Contribution to Experimental Psychology.
6. Hayes, S.C., Barnes-Holmes, D., & Roche, B. (2001). Relational Frame Theory.
7. Kamiński, J. (2017). Intermediate-Term Memory as a Bridge between Working and Long-Term Memory. J Neurosci, 37(20), 5045-5047.

---

*Document Version: 1.0*  
*Author: Marco*  
*Date: 2026-04-08*  
*Branch: GL5_branch*