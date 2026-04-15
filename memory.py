"""
################################################################################
#                                                                              #
#      __  __ ______ __  __  ____  _____ __     __                             #
#     |  \/  |  ____|  \/  |/ __ \|  __ \\ \   / /                             #
#     | \  / | |__  | \  / | |  | | |__) |\ \_/ /                              #
#     | |\/| |  __| | |\/| | |  | |  _  /  \   /                               #
#     | |  | | |____| |  | | |__| | | \ \   | |                                #
#     |_|  |_|______|_|  |_|\____/|_|  \_\  |_|                                #
#                                                                              #
################################################################################

MEMORY SUBSYSTEM - THE HIPPOCAMPAL-CORTICAL INTERFACE
=====================================================

This module implements the multi-tier memory architecture of the GL5 agent. 
It mirrors the biological distinction between episodic, semantic, and 
relational memory systems.

SCIENTIFIC FOUNDATIONS:
-----------------------
1. THE DUAL-TRACE THEORY:
   Based on the work of Squire (1986). Memory is initially encoded in the 
   hippocampus (Episodic) and later consolidated into the neocortex (Semantic).
   Ref: Squire, L. R. (1986). Mechanisms of Memory. Science.

2. EPISODIC BUFFER (Chrono Memory):
   Models the hippocampal CA1 region. Captures raw "What, Where, When" 
   triplets. Rapidly encoded but high decay rate.

3. SEMANTIC STORE (Rules):
   Models long-term cortical storage. Abstracted rules mapping perception 
   to action, weighted by reinforcement history (Hebbian LTP).

4. RELATIONAL NETWORK (Frames):
   Implements Relational Frame Theory (Hayes, 2001). Stores non-arbitrary 
   and arbitrary relations (Coordination, Opposition, etc.) between 
   concepts for derived reasoning.

5. SPATIAL COGNITIVE MAP (Territory):
   Based on O'Keefe & Nadel (1978). Place cells and grid cells enable 
   topological navigation.

Author: Marco
"""

import sqlite3
import json


class Memory:
    """
    ############################################################################
    #   __  __ ______ __  __  ____  _____ __     __                            #
    #  |  \/  |  ____|  \/  |/ __ \|  __ \\ \   / /                            #
    #  | \  / | |__  | \  / | |  | | |__) |\ \_/ /                             #
    #  | |\/| |  __| | |\/| | |  | |  _  /  \   /                              #
    #  | |  | | |____| |  | | |__| | | \ \   | |                               #
    #  |_|  |_|______|_|  |_|\____/|_|  \_\  |_|                               #
    ############################################################################

    The persistent storage subsystem modelling biological memory.

    In biological brains, memory is not a single homogeneous system but
    a collection of interacting processes with different properties:
    - Episodic (hippocampal): Fast encoding, fast decay, single events.
    - Semantic (cortical): Slow encoding, slow decay, abstracted knowledge.
    - Relational (prefrontal): Inference, generalisation, transitivity.
    """

    def __init__(self, db_path="general_learner.db"):
        """
        Initialises the memory subsystem.

        Args:
            db_path: Path to SQLite database file. Defaults to 'general_learner.db'
        """
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        """
        Initialises the database schema.

        Creates the following tables:
        1. chrono_memory — Episodic buffer for raw experiences
        2. conceptual_ids — Vocabulary grounding (agnostic to language)
        3. rules — Semantic memory store
        4. territory — Spatial memory (hippocampal cognitive map)
        5. relational_frames — RFT network (GL5 only)

        Also performs migrations for backward compatibility with existing
        databases from earlier GL4 versions.
        """
        cur = self.conn.cursor()

        # 1. Chronological Memory (Episodic Buffer)
        # ================================
        # This models the hippocampal CA1 region — the 'what happened
        # where and when' system. Each entry captures a single perception-
        # action-reward triplet, analogous to an 'episodic memory trace'.
        #
        # Biological analogue: The temporary storage of recent experiences
        # before consolidation into long-term semantic memory during sleep.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chrono_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perception TEXT NOT NULL,
                action INTEGER NOT NULL,
                reward INTEGER NOT NULL,
                command_text TEXT DEFAULT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Conceptual ID Mapping (Symbolic Grounding)
        # ============================================
        # Implements language-agnostic symbolic grounding. Each unique
        # textual input (word, phrase, or symbol) receives a stable internal
        # identifier (conceptual_id). This parallels the brain's ability to
        # map arbitrary sensory patterns onto stable semantic representations.
        #
        # Biological analogue: The orthographic word form area (VWFA) in
        # the left fusiform gyrus — maps visual patterns to conceptual meaning
        # without being tied to a specific orthography.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conceptual_ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                value TEXT UNIQUE NOT NULL
            )
        """)

        # 3. Rules Memory (Semantic/Consolidated Knowledge)
        # ================================================
        # The core knowledge store — associations between perception patterns
        # and actions, weighted by reinforcement history. This implements
        # the 'procedural memory' aspect of the cognitive architecture.
        #
        # Biological analogue: The neocortical long-term memory stores —
        # slowly consolidated, abstract representations of learned behaviours.
        # The weight field models synaptic strength (long-term potentiation).
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perception_pattern TEXT NOT NULL,
                target_action INTEGER NOT NULL,
                command_id INTEGER DEFAULT NULL,
                macro_actions TEXT DEFAULT NULL,
                weight REAL DEFAULT 1.0,
                is_composite INTEGER DEFAULT 0,
                next_perception TEXT DEFAULT NULL,
                memory_type INTEGER DEFAULT 0,
                derived_from INTEGER DEFAULT NULL,
                FOREIGN KEY (command_id) REFERENCES conceptual_ids(id)
            )
        """)

        # 4. Global Territory Map (Hippocampal Spatial Memory)
        # ===================================================
        # Models the cognitive map — a spatial representation of the
        # environment with associated visit frequency and importance.
        # GL5: Added maze_id to support multiple labyrinths.
        #
        # Biological analogue: Place cells in the hippocampal CA1 region
        # (O'Keefe & Dostrovsky, 1971) and the entorhinal grid system
        # (Hafting et al., 2005). The agent builds an internal map of
        # 'where I have been and what it was like there'.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS territory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                maze_id TEXT NOT NULL DEFAULT 'default',
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                situation_id TEXT,
                visits INTEGER DEFAULT 1,
                importance REAL DEFAULT 1.0,
                UNIQUE(maze_id, x, y)
            )
        """)

        # 5. Relational Frames (RFT Layer — GL5)
        # =====================================
        # Stores derived relational networks — the 'same as', 'opposite of',
        # and other abstract relationships between concepts.
        #
        # Biological analogue: The prefrontal cortex's abstract relational
        # reasoning capacity. Where the hippocampus stores 'I was at X and
        # saw Y', the prefrontal cortex derives 'X is like Z' without ever
        # having experienced X and Z together.
        #
        # Reference: Hayes, S.C., Barnes-Holmes, D., & Roche, B. (2001).
        # Relational Frame Theory: A Post-Skinnerian Account of Human
        # Language and Cognition.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS relational_frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_a INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                concept_b INTEGER NOT NULL,
                strength REAL DEFAULT 1.0,
                FOREIGN KEY (concept_a) REFERENCES conceptual_ids(id),
                FOREIGN KEY (concept_b) REFERENCES conceptual_ids(id),
                UNIQUE(concept_a, relation_type, concept_b)
            )
        """)

        # 6. Intermediate-Term Memory (GL5) - Circadian Buffer
        # ==================================================
        # Acts as a staging area between working memory and long-term memory.
        # Biological: Hippocampal intermediate-term storage (~20-30 min window)
        # This replaces the old "chrono_memory" for GL5, with additional metadata.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS intermediate_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perception TEXT NOT NULL,
                action INTEGER NOT NULL,
                reward INTEGER NOT NULL,
                command_text TEXT DEFAULT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                rehearsed INTEGER DEFAULT 0,
                transfer_attempts INTEGER DEFAULT 0
            )
        """)

        # Create backward-compatible alias (chrono_memory now points to intermediate_memory)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chrono_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perception TEXT NOT NULL,
                action INTEGER NOT NULL,
                reward INTEGER NOT NULL,
                command_text TEXT DEFAULT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # GL5.1: Cognitive Productions Table
        # Almacena producciones cognitivas de alto nivel generadas por:
        # - Imaginación (abstracción de reglas)
        # - Generalización (patrones de acciones)
        # - Composición (macros de nivel superior)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cognitive_productions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                production_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                component_rules TEXT,
                abstraction_level INTEGER DEFAULT 1,
                confidence REAL DEFAULT 0.5,
                usefulness REAL DEFAULT 0.5,
                usage_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                origin_bot INTEGER DEFAULT 1,
                heard_from_bot INTEGER DEFAULT NULL,
                is_imagined INTEGER DEFAULT 0,
                is_heard INTEGER DEFAULT 0,
                fusion_count INTEGER DEFAULT 0,
                generalization_depth INTEGER DEFAULT 0
            )
        """)

        # GL5.1: Hearing Memories Table
        # Almacena las secuencias sonoras escuchadas de otros robots
        cur.execute("""
            CREATE TABLE IF NOT EXISTS hearing_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                heard_song TEXT NOT NULL,
                heard_from_bot INTEGER NOT NULL,
                associated_action INTEGER,
                association_strength REAL DEFAULT 0.5,
                context_perception TEXT,
                reward_outcome INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                times_reinforced INTEGER DEFAULT 1
            )
        """)

        # Database Migrations
        # ===================
        # Adds missing columns to existing databases for backward compatibility.
        # This ensures that GL5 can operate with GL4's database file.
        migrations = [
            "ALTER TABLE rules ADD COLUMN memory_type INTEGER DEFAULT 0",
            "ALTER TABLE rules ADD COLUMN command_id INTEGER DEFAULT NULL",
            "ALTER TABLE rules ADD COLUMN macro_actions TEXT DEFAULT NULL",
            "ALTER TABLE rules ADD COLUMN is_composite INTEGER DEFAULT 0",
            "ALTER TABLE rules ADD COLUMN derived_from INTEGER DEFAULT NULL",
        ]
        for m in migrations:
            try:
                cur.execute(m)
            except sqlite3.OperationalError:
                pass  # Column already exists

        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_rules_perception ON rules(perception_pattern)"
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_rules_command ON rules(command_id)")
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_rules_memory_type ON rules(memory_type)"
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_rules_weight ON rules(weight DESC)")
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_rules_command_perc ON rules(command_id, perception_pattern)"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_rules_next_perc ON rules(next_perception)"
        )

        # GL5: Add maze_id column to territory if not exists (migration)
        try:
            cur.execute(
                "ALTER TABLE territory ADD COLUMN maze_id TEXT DEFAULT 'default'"
            )
        except sqlite3.OperationalError:
            pass  # Column already exists

        # GL5: Add weight column to intermediate_memory if not exists
        try:
            cur.execute(
                "ALTER TABLE intermediate_memory ADD COLUMN weight REAL DEFAULT 1.0"
            )
        except sqlite3.OperationalError:
            pass  # Column already exists

        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_intermediate_timestamp ON intermediate_memory(timestamp)"
        )

        self.conn.commit()

    def get_or_create_concept_id(self, value):
        """
        Maps an arbitrary text string to a stable conceptual identifier.

        This implements symbolic grounding — the agent creates its own
        internal vocabulary regardless of the specific tokens used by
        the human teacher.

        Args:
            value: The textual string to map

        Returns:
            int: The unique conceptual_id for this string
        """
        if not value:
            return None
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT OR IGNORE INTO conceptual_ids (value) VALUES (?)", (value,)
            )
            self.conn.commit()
            cur.execute("SELECT id FROM conceptual_ids WHERE value = ?", (value,))
            row = cur.fetchone()
            return row["id"] if row else None
        except sqlite3.Error:
            return None

    def tokenize(self, text):
        """
        Splits text into unique concept IDs.

        Parses an input string into individual conceptual tokens, preserving
        whitespace as its own token. This allows the agent to learn both
        whole-command associations and word-level decompositions.

        Example: "AVANZA Y GIRA" -> [AVANZA, space, Y, space, GIRA]

        Biological analogue: The initial linguistic parsing in Broca's area —
        segmenting the continuous speech stream into discrete morphemes.

        Args:
            text: The input string to tokenise

        Returns:
            list: List of conceptual_ids
        """
        if not text:
            return []
        import re

        raw_tokens = re.split(r"(\s+)", text.strip().upper())
        clean_tokens = []
        for t in raw_tokens:
            if not t:
                continue
            if t.isspace():
                clean_tokens.append(" ")
            else:
                clean_tokens.append(t)

        return [self.get_or_create_concept_id(t) for t in clean_tokens]

    def add_chrono(
        self, perception, action, reward, command=None, rehearsed=False, weight=1.0
    ):
        """
        Adds an experience to the episodic buffer (chrono_memory).

        Records a single perception-action-reward triplet, modelling the
        immediate encoding of experiences in the hippocampus. This data
        is used during consolidation to form more abstract rules.

        Biological analogue: The rapid encoding of novel experiences in
        the hippocampal formation — a process that occurs within seconds
        of the experience happening.

        Reference: Squire, L.R. & Zola, S.M. (1996). Structure and function
        of declarative and nondeclarative memory systems. PNAS, 93(24), 13515-13522.
        """
        cur = self.conn.cursor()
        perc_str = json.dumps(perception)
        cur.execute(
            """
            INSERT INTO chrono_memory (perception, action, reward, command_text) 
            VALUES (?, ?, ?, ?)
        """,
            (perc_str, action, reward, command),
        )
        self.conn.commit()

    def add_rule(
        self,
        perception_pattern,
        action,
        weight=1.0,
        is_composite=0,
        next_perception=None,
        command_id=None,
        macro_actions=None,
        memory_type=0,
        derived_from=None,
        command=None,
    ):
        """
        Adds or strengthens a rule in semantic memory.

        This is the core learning function — whenever the agent experiences
        a successful perception-action-outcome, a rule is created or strengthened.
        The weight field models the synaptic strength (Hebbian: 'neurons that
        fire together wire together').

        Supports two memory types:
        - MEMORY_EPISODIC (0): Short-term, fast decay, individual experiences
        - MEMORY_SEMANTIC (1): Long-term, slow decay, consolidated abstractions
        - MEMORY_DERIVED (2): RFT-inferred, GL5 only, fastest decay

        Biological analogue: Long-term potentiation (LTP) in the CA1 region —
        the strengthening of synaptic connections following repeated activation.

        Reference: Bliss, T.V.P. & Lømo, T. (1973). Long-lasting potentiation
        of synaptic transmission in the dentate area of the anaesthetised rabbit
        following stimulation of the perforant path. Journal of Physiology, 232(2), 331-356.

        Args:
            perception_pattern: JSON-serialised fuzzy vector
            action: The target action (ACT_* constant)
            weight: Synaptic weight (default 1.0)
            is_composite: Whether this is a macro action sequence (0/1)
            next_perception: Expected next state (for transition rules)
            command_id: The conceptual_id of any associated command
            macro_actions: JSON list of actions if composite
            memory_type: 0=episodic, 1=semantic, 2=derived
            derived_from: ID of relational_frame that derived this (GL5 only)
            command: Backward-compatible text command (auto-converted to command_id)
        """
        # Backward compatibility: accept command text string
        if command is not None and command_id is None:
            command_id = self.get_or_create_concept_id(command.upper())

        cur = self.conn.cursor()
        perc_str = json.dumps(perception_pattern)
        next_perc_str = json.dumps(next_perception) if next_perception else None
        macro_str = json.dumps(macro_actions) if macro_actions else None

        # Check if exact rule already exists
        query = """
            SELECT id, weight FROM rules 
            WHERE perception_pattern = ? AND target_action = ? AND is_composite = ? 
            AND memory_type = ?
        """
        params = [perc_str, action, is_composite, memory_type]

        if command_id is not None:
            query += " AND command_id = ?"
            params.append(command_id)
        else:
            query += " AND command_id IS NULL"

        cur.execute(query, params)
        row = cur.fetchone()

        if row:
            # Reinforce existing rule — additive strengthening
            new_weight = row["weight"] + weight
            cur.execute(
                "UPDATE rules SET weight = ?, next_perception = ?, macro_actions = ? WHERE id = ?",
                (new_weight, next_perc_str, macro_str, row["id"]),
            )
        else:
            # Create new rule
            cur.execute(
                """INSERT INTO rules (perception_pattern, target_action, weight, is_composite, 
                   next_perception, command_id, macro_actions, memory_type, derived_from) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    perc_str,
                    action,
                    weight,
                    is_composite,
                    next_perc_str,
                    command_id,
                    macro_str,
                    memory_type,
                    derived_from,
                ),
            )
        self.conn.commit()

    def update_territory(self, x, y, situation_id, importance=1.0, maze_id="default"):
        """
        Updates the spatial cognitive map.

        Records a visit to a grid position with its associated perceptual
        situation. This implements the hippocampal place system — the agent
        forms a map of 'where things are' based on experience.

        GL5: Added maze_id parameter to support multiple labyrinths.
        The agent can now store maps for different environments and
        transfer knowledge between similar maze configurations.

        Biological analogue: Place cell firing in hippocampal CA1 — neurons
        that fire selectively when the animal occupies a specific location.

        Reference: O'Keefe, J. & Dostrovsky, J. (1971). The hippocampus as
        a spatial map. Preliminary evidence from unit activity in the
        freely-moving rat. Brain Research, 34(1), 171-175.

        Args:
            x: Grid X coordinate
            y: Grid Y coordinate
            situation_id: JSON string of the fuzzy perception at this location
            importance: Experiential significance (default 1.0, higher for rewards)
            maze_id: Unique identifier for the maze (default 'default')
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO territory (maze_id, x, y, situation_id, visits, importance)
            VALUES (?, ?, ?, ?, 1, ?)
            ON CONFLICT(maze_id, x, y) DO UPDATE SET 
                visits = visits + 1,
                situation_id = excluded.situation_id,
                importance = MAX(importance, excluded.importance)
        """,
            (maze_id, x, y, situation_id, importance),
        )
        self.conn.commit()

    def get_territory(self, maze_id=None):
        """
        Retrieves the spatial memory map, optionally filtered by maze.

        Args:
            maze_id: Optional maze identifier to filter results

        Returns:
            list: All territory entries as dictionaries
        """
        cur = self.conn.cursor()
        if maze_id:
            cur.execute("SELECT * FROM territory WHERE maze_id = ?", (maze_id,))
        else:
            cur.execute("SELECT * FROM territory")
        return [dict(row) for row in cur.fetchall()]

    def get_rules(self, memory_type=None, limit=None):
        """
        Retrieves learned rules, optionally filtered by memory type.

        Joins with conceptual_ids to return the textual command alongside
        each rule, enabling human-readable output in the UI.

        Args:
            memory_type: Optional filter (0=episodic, 1=semantic, 2=derived)
            limit: Optional limit on number of results for performance

        Returns:
            list: Rules as dictionaries with 'command_text' field
        """
        cur = self.conn.cursor()
        query = """
            SELECT r.*, c.value as command_text
            FROM rules r
            LEFT JOIN conceptual_ids c ON r.command_id = c.id
        """
        if memory_type is not None:
            query += f" WHERE r.memory_type = {memory_type}"
        query += " ORDER BY r.weight DESC"
        if limit is not None:
            query += f" LIMIT {limit}"
        cur.execute(query)
        return [dict(row) for row in cur.fetchall()]

    def clear(self):
        """
        Wipes all memory — the 'amnesia' function.

        Useful for testing and restarting the agent's cognitive development
        from a blank slate. In biological terms, models the pathological
        case of complete retrograde amnesia (e.g., patient H.M.).
        """
        cur = self.conn.cursor()
        cur.execute("DELETE FROM chrono_memory")
        cur.execute("DELETE FROM rules")
        self.conn.commit()

    def decay_rules(self):
        """
        Applies asymptotic forgetting to all rules.

        Models the Ebbinghaus forgetting curve — memories decay exponentially
        with time, with the rate depending on memory type:
        - Episodic: Fast decay (0.8 per cycle)
        - Semantic: Slow decay (0.95 per cycle)
        - Derived: Medium decay (0.92 per cycle)

        Rules below FORGET_THRESHOLD (0.5) are permanently pruned.

        Biological analogue: Synaptic downscaling during slow-wave sleep —
        the brain weakens unused connections to make room for new learning.

        Reference: Rasch, B. & Born, J. (2013). About sleep's role in memory.
        Physiological Reviews, 93(2), 681-766.
        """
        from constants import DECAY_RATE_EPISODIC, DECAY_RATE_SEMANTIC, FORGET_THRESHOLD

        cur = self.conn.cursor()

        # Decay based on memory type
        # 0 = Episodic (old), maps to ITM in GL5
        # 1 = Semantic (LTM)
        # 2 = Derived (LTM)
        # 3 = Sensory (not persisted)
        # 4 = Working (not persisted)
        # 5 = Intermediate (GL5)

        cur.execute(
            "UPDATE rules SET weight = weight * ? WHERE memory_type = ?",
            (DECAY_RATE_EPISODIC, 0),
        )
        cur.execute(
            "UPDATE rules SET weight = weight * ? WHERE memory_type = ?",
            (DECAY_RATE_SEMANTIC, 1),
        )

        # GL5: Decay derived (RFT) rules - medium decay
        from constants import DECAY_RATE_DERIVED

        cur.execute(
            "UPDATE rules SET weight = weight * ? WHERE memory_type = ?",
            (DECAY_RATE_DERIVED, 2),
        )

        # GL5: Decay intermediate-term memory table (memory_type 5)
        from constants import DECAY_RATE_INTERMEDIATE

        cur.execute(
            "UPDATE rules SET weight = weight * ? WHERE memory_type = ?",
            (DECAY_RATE_INTERMEDIATE, 5),
        )

        # GL5: Decay intermediate_memory table directly
        cur.execute(
            "UPDATE intermediate_memory SET weight = weight * ?",
            (DECAY_RATE_INTERMEDIATE,),
        )

        # Prune weak entries from intermediate memory
        cur.execute("DELETE FROM intermediate_memory WHERE weight < ?", (0.3,))

        cur.execute("DELETE FROM rules WHERE weight < ?", (FORGET_THRESHOLD,))
        self.conn.commit()

    def get_all_chrono(self):
        """
        Retrieves all intermediate-term memories in chronological order.
        GL5: Now uses intermediate_memory table.

        Returns:
            list: All intermediate memory entries as dictionaries
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM intermediate_memory ORDER BY id ASC")
        return [dict(row) for row in cur.fetchall()]

    def clear_chrono(self):
        """
        Clears the intermediate-term memory buffer after consolidation.
        GL5: Now uses intermediate_memory table.

        Called after sleep_cycle() processing — the experiences have been
        consolidated into semantic rules and are no longer needed in raw form.

        Biological analogue: The 'systems consolidation' process where
        hippocampal memories are transferred to neocortical storage.
        """
        cur = self.conn.cursor()
        cur.execute("DELETE FROM intermediate_memory")
        self.conn.commit()

    # ====================
    # RFT Methods (GL5)
    # ====================

    def add_relational_frame(self, concept_a, relation_type, concept_b, strength=1.0):
        """
        Adds or updates a relational frame between two concepts.

        Creates a relational link (COORD, OPP, CAUSE, TEMP) between two
        concepts, modelling the formation of abstract semantic relationships.

        Example: COORD(AVANZA_ID, GO_ID) with strength 0.8 indicates
        the agent has inferred these two words are synonymous.

        Biological analogue: The formation of semantic category neurons —
        cells in inferior temporal cortex that respond to related but
        not identical stimuli (e.g., 'cat' neurons that also fire for 'dog').

        Reference: DiCarlo, J.J., Zoccolan, D., & Rust, N.C. (2012). How
        does the brain solve visual object recognition? Current Biology, 22(11), R496-R504.

        Args:
            concept_a: First conceptual_id
            relation_type: 'COORD', 'OPP', 'CAUSE', or 'TEMP'
            concept_b: Second conceptual_id
            strength: Confidence of the relationship (0.0-1.0)

        Returns:
            int: The frame's database ID, or None if updated existing
        """
        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO relational_frames (concept_a, relation_type, concept_b, strength)
                VALUES (?, ?, ?, ?)
            """,
                (concept_a, relation_type, concept_b, strength),
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            cur.execute(
                """
                UPDATE relational_frames SET strength = MAX(strength, ?)
                WHERE concept_a = ? AND relation_type = ? AND concept_b = ?
            """,
                (strength, concept_a, relation_type, concept_b),
            )
            self.conn.commit()
            return None

    def get_frames_for_concept(self, concept_id):
        """
        Retrieves all relational frames involving a concept.

        Used by Phase D inference to find related concepts when
        no direct rule exists for the requested command.

        Args:
            concept_id: The conceptual_id to query

        Returns:
            list: All frames involving this concept
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM relational_frames
            WHERE concept_a = ? OR concept_b = ?
            ORDER BY strength DESC
        """,
            (concept_id, concept_id),
        )
        return [dict(row) for row in cur.fetchall()]

    def get_derived_rules(self, concept_id):
        """
        Retrieves RFT-derived rules for a concept.

        These are rules inferred through mutual entailment, not learned
        through direct experience. They have memory_type=2.

        Args:
            concept_id: The conceptual_id to query

        Returns:
            list: Derived rules (memory_type=2) for this concept
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM rules
            WHERE command_id = ? AND memory_type = ?
            ORDER BY weight DESC
        """,
            (concept_id, 2),
        )
        return [dict(row) for row in cur.fetchall()]

    def get_all_frames(self):
        """
        Retrieves all relational frames in the network.

        Returns:
            list: All frames ordered by strength
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM relational_frames ORDER BY strength DESC")
        return [dict(row) for row in cur.fetchall()]

    def decay_frames(self):
        """
        Applies decay to relational frames.

        RFT frames decay faster than semantic rules but slower than episodic
        — they represent a middle level of abstraction. Frames below 0.1
        strength are pruned.
        """
        from constants import DECAY_RATE_DERIVED

        cur = self.conn.cursor()
        cur.execute(
            "UPDATE relational_frames SET strength = strength * ?",
            (DECAY_RATE_DERIVED,),
        )
        cur.execute("DELETE FROM relational_frames WHERE strength < 0.1")
        self.conn.commit()

    def delete_weak_frames(self, threshold=0.2):
        """
        Manual pruning of weak relational frames.

        Args:
            threshold: Minimum strength to preserve (default 0.2)
        """
        cur = self.conn.cursor()
        cur.execute("DELETE FROM relational_frames WHERE strength < ?", (threshold,))
        self.conn.commit()

    def export_rules_csv(self, filepath="rules_export.csv"):
        """
        Exports all rules to CSV for external analysis/graphing.
        """
        import csv

        rules = self.get_rules(limit=100000)
        if not rules:
            print("No rules to export")
            return None

        with open(filepath, "w", newline="") as f:
            fieldnames = [
                "id",
                "perception",
                "target_action",
                "weight",
                "memory_type",
                "is_composite",
                "command_id",
                "command_text",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rules:
                row = {k: r.get(k, "") for k in fieldnames}
                writer.writerow(row)

        print(f"Exported {len(rules)} rules to {filepath}")
        return filepath

    def export_frames_csv(self, filepath="frames_export.csv"):
        """
        Exports all relational frames to CSV for analysis.
        """
        import csv

        frames = self.get_all_frames()
        if not frames:
            print("No frames to export")
            return None

        with open(filepath, "w", newline="") as f:
            fieldnames = [
                "id",
                "concept1_id",
                "concept2_id",
                "relation_type",
                "strength",
                "bidirectional",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for fr in frames:
                row = {k: fr.get(k, "") for k in fieldnames}
                writer.writerow(row)

        print(f"Exported {len(frames)} frames to {filepath}")
        return filepath

    def export_chronologies_csv(self, filepath="chronologies_export.csv"):
        """
        Exports all episodic memories (chronologies) to CSV.
        """
        import csv

        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, perception, action, reward, command_text, timestamp FROM chrono_memory ORDER BY timestamp"
        )
        rows = cur.fetchall()

        if not rows:
            print("No chronologies to export")
            return None

        with open(filepath, "w", newline="") as f:
            fieldnames = [
                "id",
                "perception",
                "action",
                "reward",
                "command_text",
                "timestamp",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(zip(fieldnames, row)))

        print(f"Exported {len(rows)} chronologies to {filepath}")
        return filepath

    def query_concepts_stats(self):
        """
        Returns statistics about learned concepts.
        """
        cur = self.conn.cursor()

        cur.execute("SELECT COUNT(*) FROM conceptual_ids")
        total_concepts = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM rules WHERE weight > 0")
        positive_rules = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM rules WHERE weight < 0")
        negative_rules = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM rules WHERE is_composite = 1")
        macro_rules = cur.fetchone()[0]

        cur.execute("SELECT AVG(weight) FROM rules")
        avg_weight = cur.fetchone()[0] or 0

        cur.execute("SELECT MAX(weight) FROM rules")
        max_weight = cur.fetchone()[0] or 0

        return {
            "total_concepts": total_concepts,
            "positive_rules": positive_rules,
            "negative_rules": negative_rules,
            "macro_rules": macro_rules,
            "avg_rule_weight": round(avg_weight, 2),
            "max_rule_weight": round(max_weight, 2),
        }

    def query_learning_trajectory(self, sample_rate=10):
        """
        Returns learning trajectory over time (sampled).

        Args:
            sample_rate: Sample every N chronologies

        Returns:
            list of dicts with cumulative stats over time
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT c.timestamp, c.reward, c.action,
                   (SELECT COUNT(*) FROM rules WHERE id <= c.id) as rule_count,
                   (SELECT AVG(weight) FROM rules WHERE id <= c.id) as avg_weight
            FROM chrono_memory c
            ORDER BY c.timestamp
        """)
        rows = cur.fetchall()

        trajectory = []
        for i, row in enumerate(rows):
            if i % sample_rate == 0:
                trajectory.append(
                    {
                        "step": i,
                        "timestamp": row[0],
                        "reward": row[1],
                        "action": row[2],
                        "cumulative_rules": row[3],
                        "cumulative_avg_weight": round(row[4] or 0, 2),
                    }
                )

        return trajectory

    # =========================================================================
    # GL5.1: Cognitive Productions Management
    # =========================================================================

    def add_cognitive_production(
        self,
        production_type: str,
        name: str,
        component_rules: list = None,
        abstraction_level: int = 1,
        confidence: float = 0.5,
        origin_bot: int = 1,
        heard_from_bot: int = None,
        is_imagined: bool = False,
        is_heard: bool = False,
        description: str = None,
    ) -> int:
        """
        Adds a new cognitive production (high-level abstraction).

        Args:
            production_type: 'MACRO', 'GENERALIZATION', 'ABSTRACTION', 'CONCEPT'
            name: Human-readable name of the production
            component_rules: List of rule IDs that compose this production
            abstraction_level: How abstract (1=concrete, 5=highly abstract)
            confidence: Confidence in the production's usefulness
            origin_bot: Which bot created this (1 or 2)
            heard_from_bot: If learned from hearing, which bot
            is_imagined: True if created in imagination mode
            is_heard: True if learned from hearing another bot
            description: Optional description

        Returns:
            int: ID of the new production
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO cognitive_productions
            (production_type, name, description, component_rules, abstraction_level,
             confidence, origin_bot, heard_from_bot, is_imagined, is_heard)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                production_type,
                name,
                description,
                json.dumps(component_rules) if component_rules else None,
                abstraction_level,
                confidence,
                origin_bot,
                heard_from_bot,
                1 if is_imagined else 0,
                1 if is_heard else 0,
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_cognitive_productions(
        self,
        production_type: str = None,
        min_abstraction: int = 0,
        min_confidence: float = 0.0,
        limit: int = 1000,
    ) -> list:
        """
        Retrieves cognitive productions with optional filters.

        Args:
            production_type: Filter by type ('MACRO', 'GENERALIZATION', etc.)
            min_abstraction: Minimum abstraction level
            min_confidence: Minimum confidence value
            limit: Maximum number of results

        Returns:
            list: List of production dictionaries
        """
        cur = self.conn.cursor()
        query = "SELECT * FROM cognitive_productions WHERE abstraction_level >= ? AND confidence >= ?"
        params = [min_abstraction, min_confidence]

        if production_type:
            query += " AND production_type = ?"
            params.append(production_type)

        query += " ORDER BY confidence DESC, usage_count DESC LIMIT ?"
        params.append(limit)

        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

    def increment_production_usage(self, production_id: int) -> None:
        """Increments usage count and updates last_used timestamp."""
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE cognitive_productions
            SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (production_id,),
        )
        self.conn.commit()

    def update_production_confidence(self, production_id: int, delta: float) -> None:
        """Updates confidence based on performance delta."""
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE cognitive_productions
            SET confidence = MAX(0.1, MIN(1.0, confidence + ?))
            WHERE id = ?
            """,
            (delta, production_id),
        )
        self.conn.commit()

    def fuse_cognitive_productions(
        self, prod1_id: int, prod2_id: int, fused_name: str = None
    ) -> int:
        """
        Fuses two cognitive productions into one more abstract concept.

        Args:
            prod1_id: First production ID
            prod2_id: Second production ID
            fused_name: Name for the new fused production

        Returns:
            int: ID of the new fused production
        """
        cur = self.conn.cursor()

        cur.execute("SELECT * FROM cognitive_productions WHERE id = ?", (prod1_id,))
        prod1 = dict(cur.fetchone())

        cur.execute("SELECT * FROM cognitive_productions WHERE id = ?", (prod2_id,))
        prod2 = dict(cur.fetchone())

        if not prod1 or not prod2:
            return None

        if fused_name is None:
            fused_name = f"FUSED_{prod1['name']}_{prod2['name']}"

        components = []
        if prod1.get("component_rules"):
            components.extend(json.loads(prod1["component_rules"]))
        if prod2.get("component_rules"):
            components.extend(json.loads(prod2["component_rules"]))

        new_abstraction = (
            max(prod1["abstraction_level"], prod2["abstraction_level"]) + 1
        )
        new_confidence = (prod1["confidence"] + prod2["confidence"]) / 2

        return self.add_cognitive_production(
            production_type="FUSION",
            name=fused_name,
            component_rules=components,
            abstraction_level=new_abstraction,
            confidence=new_confidence,
            origin_bot=prod1.get("origin_bot", 1),
            is_imagined=True,
            description=f"Fused from {prod1['name']} and {prod2['name']}",
        )

    # =========================================================================
    # GL5.1: Hearing Memories Management
    # =========================================================================

    def add_hearing_memory(
        self,
        heard_song: str,
        heard_from_bot: int,
        associated_action: int = None,
        context_perception: str = None,
        reward_outcome: int = None,
    ) -> int:
        """
        Records a heard song from another robot.

        Args:
            heard_song: The song/sound that was heard (e.g., "GO_FORWARD")
            heard_from_bot: ID of the bot that sang
            associated_action: Action being associated with this sound
            context_perception: Perception context when heard
            reward_outcome: Result of the action

        Returns:
            int: ID of the hearing memory
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO hearing_memories
            (heard_song, heard_from_bot, associated_action, context_perception, reward_outcome)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                heard_song,
                heard_from_bot,
                associated_action,
                context_perception,
                reward_outcome,
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def reinforce_hearing_memory(
        self, heard_song: str, heard_from_bot: int, reward_delta: float
    ) -> None:
        """
        Reinforces hearing memories based on reward outcomes.
        Positive rewards increase association strength, negative decrease it.
        """
        from constants import HEARING_LEARNING_RATE

        cur = self.conn.cursor()
        strength_change = reward_delta * HEARING_LEARNING_RATE * 0.1

        cur.execute(
            """
            UPDATE hearing_memories
            SET association_strength = MAX(0, MIN(1, association_strength + ?)),
                times_reinforced = times_reinforced + 1,
                reward_outcome = COALESCE(?, reward_outcome)
            WHERE heard_song = ? AND heard_from_bot = ?
            """,
            (strength_change, reward_delta, heard_song, heard_from_bot),
        )
        self.conn.commit()

    def get_heard_songs(self, min_strength: float = 0.3, limit: int = 50) -> list:
        """
        Retrieves heard songs with association strength above threshold.
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM hearing_memories
            WHERE association_strength >= ?
            ORDER BY association_strength DESC, times_reinforced DESC
            LIMIT ?
            """,
            (min_strength, limit),
        )
        return [dict(row) for row in cur.fetchall()]

    def get_song_action_association(self, song: str) -> list:
        """
        Gets all action associations for a given song.
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT associated_action, association_strength, times_reinforced
            FROM hearing_memories
            WHERE heard_song = ?
            ORDER BY association_strength DESC
            """,
            (song,),
        )
        return [dict(row) for row in cur.fetchall()]

    # =========================================================================
    # GL5.1: Query Statistics
    # =========================================================================

    def get_cognitive_stats(self) -> dict:
        """
        Returns statistics about cognitive productions.
        """
        cur = self.conn.cursor()

        cur.execute("SELECT COUNT(*) FROM cognitive_productions")
        total_productions = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM cognitive_productions WHERE is_imagined = 1")
        imagined = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM cognitive_productions WHERE is_heard = 1")
        heard = cur.fetchone()[0]

        cur.execute(
            "SELECT AVG(confidence) FROM cognitive_productions WHERE confidence > 0"
        )
        avg_confidence = cur.fetchone()[0] or 0

        cur.execute("SELECT SUM(usage_count) FROM cognitive_productions")
        total_usage = cur.fetchone()[0] or 0

        cur.execute("SELECT COUNT(DISTINCT heard_from_bot) FROM hearing_memories")
        bots_heard_from = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM hearing_memories")
        total_heard_memories = cur.fetchone()[0]

        cur.execute(
            "SELECT AVG(association_strength) FROM hearing_memories WHERE association_strength > 0"
        )
        avg_hearing_strength = cur.fetchone()[0] or 0

        return {
            "total_productions": total_productions,
            "imagined_productions": imagined,
            "heard_productions": heard,
            "avg_confidence": round(avg_confidence, 3),
            "total_usage": total_usage,
            "bots_heard_from": bots_heard_from,
            "total_heard_memories": total_heard_memories,
            "avg_hearing_strength": round(avg_hearing_strength, 3),
        }
