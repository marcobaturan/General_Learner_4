"""
Memory Subsystem for General Learner 4/5

This module implements the persistent storage layer for the cognitive architecture,
modelling the hippocampal formation's dual-trace memory system in silicon.

The memory hierarchy mirrors biological memory consolidation:
1. Episodic Buffer (Chrono Memory) — Short-term, experience-rich, rapidly decaying
2. Semantic Store (Rules) — Consolidated, abstract, slowly decaying
3. Relational Network (Frames) — Abstract inference, GL5 only

Based on the following neuroscientific and psychological theories:
- Squire, L.R. (1986). Mechanisms of memory. Science, 232(4758), 1612-1619.
  The distinction between hippocampal (episodic) and neocortical (semantic) memory.
- Ebbinghaus, H. (1885). Memory: A Contribution to Experimental Psychology.
  The forgetting curve and asymptotic decay of memory traces.
- Teyler, T.J. & DiDiscenna, P. (1985). The hippocampal memory indexing theory.
  Neural basis for pattern completion and relational mapping.

Author: Marco (extending Grey Walter's cybernetic heritage)
"""

import sqlite3
import json


class Memory:
    """
    The persistent storage subsystem modelling biological memory.

    In biological brains, memory is not a single homogeneous system but
    a collection of interacting processes with different properties:
    - Episodic (hippocampal): Fast encoding, fast decay, single events
    - Semantic (cortical): Slow encoding, slow decay, abstracted knowledge
    - Relational (prefrontal): Inference, generalisation, transitivity

    This class implements an analogous architecture using SQLite as the
    physical substrate, with separate tables mirroring these functional
    divisions while allowing seamless interaction.
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
        the human teacher. 'AVANZA', 'FORWARD', 'VORWÄRTS' all map to
        the same internal ID if the human uses them interchangeably.

        Biological analogue: The brain's ability to form orthographic
        pooling — combining character features into word-level
        representations regardless of font, case, or handwriting style.

        Reference: Dehaene, S. (2009). Reading in the Brain. Viking Press.

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
        Adds an experience to the episodic buffer (now Intermediate-Term Memory).

        Records a single perception-action-reward triplet, modelling the
        immediate encoding of experiences in the hippocampus. This data
        is used during consolidation to form more abstract rules.

        GL5: Added rehearsed flag to mark items that have been actively
        maintained in working memory (protected from faster decay).

        Biological analogue: The rapid encoding of novel experiences in
        the hippocampal formation — a process that occurs within seconds
        of the experience happening.

        Reference: Squire, L.R. & Zola, S.M. (1996). Structure and function
        of declarative and nondeclarative memory systems. PNAS, 93(24), 13515-13522.

        Args:
            perception: The fuzzy perceptual vector (JSON)
            action: The action taken (ACT_FORWARD, etc.)
            reward: The reinforcement signal (-1, 0, +10, etc.)
            command: Optional text command that triggered the action
            rehearsed: Whether item was actively rehearsed in WM
            weight: Initial weight for the experience
        """
        cur = self.conn.cursor()
        perc_str = json.dumps(perception)
        cur.execute(
            """
            INSERT INTO intermediate_memory (perception, action, reward, command_text, rehearsed, weight) 
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (perc_str, action, reward, command, 1 if rehearsed else 0, weight),
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
