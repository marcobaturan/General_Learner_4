import pygame
import json
import random
from constants import *
from graphics import Button, TextBox


# =========================================================================
# Grid constants for the VisionWindow drawing board
# =========================================================================
VISION_GRID_SIZE = 10
VISION_GRID_CELLS = VISION_GRID_SIZE * VISION_GRID_SIZE
VISION_DEFAULT_ANCHOR_X = 5
VISION_DEFAULT_ANCHOR_Y = 5


def _extract_template(flat_grid):
    """
    Extracts a structural template from a flat pixel grid.

    Computes relative offsets from the centroid of all active pixels.
    This transforms a literal pixel map into an abstract, relocatable
    representation — analogous to semantic vs episodic visual memory.

    Args:
        flat_grid: List of 100 ints (0 or 1) representing a 10x10 grid.

    Returns:
        list of (dx, dy) tuples: Relative offsets from centroid.
    """
    active_pixels = _find_active_pixels(flat_grid)
    if not active_pixels:
        return []

    centroid_x, centroid_y = _compute_centroid(active_pixels)
    return _pixels_to_offsets(active_pixels, centroid_x, centroid_y)


def _find_active_pixels(flat_grid):
    """Returns list of (x, y) for all active (==1) pixels."""
    return [
        (i % VISION_GRID_SIZE, i // VISION_GRID_SIZE)
        for i, val in enumerate(flat_grid)
        if val == 1
    ]


def _compute_centroid(active_pixels):
    """Computes the integer centroid of a list of (x, y) points."""
    sum_x = sum(x for x, _ in active_pixels)
    sum_y = sum(y for _, y in active_pixels)
    count = len(active_pixels)
    return round(sum_x / count), round(sum_y / count)


def _pixels_to_offsets(active_pixels, cx, cy):
    """Converts absolute pixel positions to relative offsets from (cx, cy)."""
    return [(x - cx, y - cy) for x, y in active_pixels]


def _render_template_to_grid(grid, template, anchor_x, anchor_y):
    """
    Renders a structural template onto a 10x10 grid at the given anchor.

    Pixels that fall outside the grid bounds are silently clipped.

    Args:
        grid: 2D list [10][10] to modify in-place.
        template: List of (dx, dy) offset tuples.
        anchor_x: X coordinate of the anchor point.
        anchor_y: Y coordinate of the anchor point.
    """
    for dx, dy in template:
        px = anchor_x + dx
        py = anchor_y + dy
        if 0 <= px < VISION_GRID_SIZE and 0 <= py < VISION_GRID_SIZE:
            grid[py][px] = 1


def _parse_query_command(text):
    """
    Parses a vision query command into (label, anchor_x, anchor_y).

    Supported formats:
        "CROSS"         → ("CROSS", 5, 5)       default center
        "CROSS AT 2,3"  → ("CROSS", 2, 3)       explicit position
        "CROSS RANDOM"  → ("CROSS", rand, rand)  random position

    Args:
        text: Raw command text from the user.

    Returns:
        tuple: (label, anchor_x, anchor_y)
    """
    parts = text.strip().upper().split()
    if not parts:
        return ("", VISION_DEFAULT_ANCHOR_X, VISION_DEFAULT_ANCHOR_Y)

    if "RANDOM" in parts:
        label = " ".join(p for p in parts if p != "RANDOM")
        anchor_x = random.randint(1, VISION_GRID_SIZE - 2)
        anchor_y = random.randint(1, VISION_GRID_SIZE - 2)
        return (label, anchor_x, anchor_y)

    if "AT" in parts:
        at_idx = parts.index("AT")
        label = " ".join(parts[:at_idx])
        coords_str = " ".join(parts[at_idx + 1:])
        anchor_x, anchor_y = _parse_coordinates(coords_str)
        return (label, anchor_x, anchor_y)

    label = " ".join(parts)
    return (label, VISION_DEFAULT_ANCHOR_X, VISION_DEFAULT_ANCHOR_Y)


def _parse_coordinates(coords_str):
    """
    Parses 'x,y' or 'x y' into (int, int), clamped to grid bounds.

    Args:
        coords_str: String like "2,3" or "2 3".

    Returns:
        tuple: (x, y) clamped to [0, 9].
    """
    coords_str = coords_str.replace(",", " ")
    nums = coords_str.split()
    if len(nums) >= 2:
        x = max(0, min(VISION_GRID_SIZE - 1, int(nums[0])))
        y = max(0, min(VISION_GRID_SIZE - 1, int(nums[1])))
        return (x, y)
    return (VISION_DEFAULT_ANCHOR_X, VISION_DEFAULT_ANCHOR_Y)


class VisionWindow:
    """
    Visual pattern learning and recall window.

    Supports two modes of recall:
    - Literal (backward compat): exact pixel replay from stored description.
    - Generalized (new): structural template rendered at arbitrary positions.
    """

    def __init__(self, screen, memory, learner=None):
        self.screen = screen
        self.memory = memory
        self.learner = learner
        self.grid = [[0 for _ in range(VISION_GRID_SIZE)] for _ in range(VISION_GRID_SIZE)]
        self.pixel_size = 25
        self.board_rect = pygame.Rect(50, 100, VISION_GRID_SIZE * self.pixel_size, VISION_GRID_SIZE * self.pixel_size)
        self.cmd_box = TextBox(350, 100, 200, 40)
        self.btn_learn = Button(350, 160, 70, 40, "LEARN", GREEN)
        self.btn_intro = Button(430, 160, 70, 40, "INTRO", BLUE)
        self.btn_clear = Button(350, 220, 150, 40, "CLEAR", RED)
        self.btn_dream = Button(350, 280, 150, 40, "DREAM", PURPLE)
        self.btn_good = Button(350, 340, 70, 40, "GOOD", GREEN)
        self.btn_bad = Button(430, 340, 70, 40, "BAD", ORANGE)
        self.btn_close = Button(750, 10, 40, 40, "X", RED)
        self.status_msg = "Draw primitives (dots, lines, angles)..."
        self.last_match_id = None  # Track last production for reinforcement
        self.font = pygame.font.SysFont("Arial", 16)
        self.active = True

    def _extract_template(self, flat_grid):
        """Delegates to module-level function for testability."""
        return _extract_template(flat_grid)

    def _render_template(self, template, anchor_x, anchor_y):
        """Clears grid and renders template at anchor position."""
        self.grid = [[0] * VISION_GRID_SIZE for _ in range(VISION_GRID_SIZE)]
        _render_template_to_grid(self.grid, template, anchor_x, anchor_y)

    def _extract_components(self, current_grid):
        """Analytical Decomposition: Decompose current board into known patterns."""
        known = [
            p for p in self.memory.get_cognitive_productions()
            if p.get("production_type") == "VISUAL_PATTERN"
        ]
        components = []
        for kp in known:
            desc = kp.get('description')
            if not desc:
                continue
            kp_grid = [int(b) for b in desc]
            if all(
                not (kp_grid[i] == 1) or (current_grid[i] == 1)
                for i in range(VISION_GRID_CELLS)
            ):
                components.append(kp['id'])
        return components

    def _process_learning(self):
        """
        Learns a visual pattern: stores both raw pixels AND structural template.

        The raw pixel string (description) provides backward compatibility.
        The template (stored in component_rules as JSON) enables generalization.
        """
        label = self.cmd_box.text.strip().upper()
        if not label:
            return

        flat_grid = [int(bit) for row in self.grid for bit in row]
        pattern_str = "".join(map(str, flat_grid))

        # Extract structural template for generalized recall
        template = self._extract_template(flat_grid)

        # Hierarchical decomposition: check known sub-patterns
        known = [
            p for p in self.memory.get_cognitive_productions()
            if p.get("production_type") == "VISUAL_PATTERN"
        ]
        concept_id = self.memory.get_or_create_concept_id(label)

        components = []
        for kp in known:
            if kp['name'] != label and kp.get('description'):
                kp_grid = [int(b) for b in kp['description']]
                is_part = all(
                    not (kp_grid[i] == 1) or (flat_grid[i] == 1)
                    for i in range(VISION_GRID_CELLS)
                )
                if is_part:
                    components.append(kp['id'])
                    self.memory.add_relational_frame(
                        kp['id'], "PART_OF", concept_id, 0.8
                    )

        # Store template as JSON in component_rules (repurposed for VISUAL_PATTERN)
        template_data = {
            "type": "visual_template",
            "offsets": template,
            "component_ids": components,
        }

        self.last_match_id = self.memory.add_cognitive_production(
            production_type="VISUAL_PATTERN",
            name=label,
            description=pattern_str,
            component_rules=[json.dumps(template_data)],
            confidence=0.9,
        )
        self.status_msg = f"Synthesized: {label} ({len(template)} px, {len(components)} parts)"

    def _process_query(self):
        """
        Recalls a visual pattern with optional position generalization.

        Parses the command for AT x,y or RANDOM keywords. Falls back to
        literal pixel recall if no template is found (backward compat).
        """
        raw_text = self.cmd_box.text.strip().upper()
        if not raw_text:
            self.status_msg = "???"
            return

        label, anchor_x, anchor_y = _parse_query_command(raw_text)

        # 1. ANALYSIS: Search for direct visual patterns and pick most confident
        prods = self.memory.get_cognitive_productions(production_type="VISUAL_PATTERN")
        matches = [p for p in prods if p['name'].upper() == label]
        
        match = max(matches, key=lambda x: x['confidence']) if matches else None

        # 2. SYNTHESIS Fallback: Search Multimodal Anchors (Speech-Vision bridge)
        if not match:
            anchors = self.memory.get_cognitive_productions(production_type="MULTIMODAL_ANCHOR")
            for a in anchors:
                try:
                    meta = json.loads(a["description"])
                    if meta.get("token") == label:
                        v_id = meta.get("vision_id")
                        cur = self.memory.conn.cursor()
                        cur.execute("SELECT * FROM cognitive_productions WHERE id=?", (v_id,))
                        row = cur.fetchone()
                        if row:
                            match = dict(row)
                            break
                except: continue

        # 3. GENERALIZATION Fallback: Search RFT Coordinate Concepts
        if not match:
            label_id = self.memory.get_or_create_concept_id(label)
            frames = self.memory.get_all_frames()
            for f in frames:
                if f["relation_type"] == "COORD" and (f["concept_a"] == label_id or f["concept_b"] == label_id):
                    partner_id = f["concept_b"] if f["concept_a"] == label_id else f["concept_a"]
                    partner_name = self.memory.get_concept_value(partner_id)
                    if partner_name:
                        prods = self.memory.get_cognitive_productions(production_type="VISUAL_PATTERN")
                        match = next((p for p in prods if p["name"].upper() == partner_name.upper()), None)
                        if match: break

        if not match:
            self.status_msg = "???"
            self.last_match_id = None
            return

        self.last_match_id = match['id']

        template = self._try_load_template(match)

        if template is not None:
            self._render_template(template, anchor_x, anchor_y)
            self.status_msg = f"Generalized {label} at ({anchor_x},{anchor_y})"
        elif match.get('description'):
            self._recall_literal(match['description'])
            self.status_msg = f"Literal recall: {label}"
        else:
            self.status_msg = "???"

    def _try_load_template(self, production):
        """
        Attempts to extract a template from a production's component_rules.

        Returns:
            list of (dx,dy) tuples, or None if no template found.
        """
        comp_rules = production.get("component_rules")
        if not comp_rules:
            return None
        try:
            parsed = json.loads(comp_rules)
            if isinstance(parsed, list) and len(parsed) > 0:
                first = parsed[0]
                if isinstance(first, str):
                    data = json.loads(first)
                    if isinstance(data, dict) and data.get("type") == "visual_template":
                        return [tuple(o) for o in data["offsets"]]
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
        return None

    def _recall_literal(self, description):
        """Backward-compatible literal pixel recall from raw binary string."""
        self.grid = [[0 for _ in range(VISION_GRID_SIZE)] for _ in range(VISION_GRID_SIZE)]
        for i, bit in enumerate(description):
            if bit == '1':
                self.grid[i // VISION_GRID_SIZE][i % VISION_GRID_SIZE] = 1

    def handle_event(self, event):
        """Routes UI events to the appropriate handler."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_close.is_clicked(event.pos):
                self.active = False
            if self.board_rect.collidepoint(event.pos):
                self._handle_board_click(event)
            if self.btn_clear.is_clicked(event.pos):
                self.grid = [[0 for _ in range(VISION_GRID_SIZE)] for _ in range(VISION_GRID_SIZE)]
            if self.btn_learn.is_clicked(event.pos):
                self._process_learning()
            if self.btn_intro.is_clicked(event.pos):
                self._process_query()
            if self.btn_dream.is_clicked(event.pos) and self.learner:
                self.learner.sleep_cycle()
            if self.btn_good.is_clicked(event.pos):
                self._process_reinforcement(0.2)
            if self.btn_bad.is_clicked(event.pos):
                self._process_reinforcement(-0.2)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._process_query()
        self.cmd_box.handle_event(event)

    def _handle_board_click(self, event):
        """Toggles a pixel on the drawing board."""
        gx = (event.pos[0] - self.board_rect.x) // self.pixel_size
        gy = (event.pos[1] - self.board_rect.y) // self.pixel_size
        if 0 <= gx < VISION_GRID_SIZE and 0 <= gy < VISION_GRID_SIZE:
            self.grid[gy][gx] = 1 if event.button == 1 else 0

    def _process_reinforcement(self, delta):
        """Applies manual reinforcement to the last recalled pattern."""
        if not self.last_match_id:
            self.status_msg = "Nothing to reinforce!"
            return

        # 1. Update confidence in permanent memory
        self.memory.update_production_confidence(self.last_match_id, delta)
        
        # 2. Inject high reward/punishment into the bot's episodic stream
        # This biases the bot's valence and helps it learn the context
        if self.learner:
            # We simulate a 'manual' learning step
            reward_val = 10.0 if delta > 0 else -10.0
            # We use a dummy perception or the bot's current one
            # For simplicity, we just trigger the learn method if possible
            # or directly influence the body state if learner allows
            if hasattr(self.learner, "energy"):
                self.learner.valence += delta * 2.0 # Instant mood swing
            
        self.status_msg = f"Reinforced ({'+' if delta>0 else ''}{delta})!"

    def draw(self):
        """Renders the vision window UI."""
        self.screen.fill((30, 30, 40))
        pygame.draw.rect(self.screen, WHITE, self.board_rect, 2)
        for y in range(VISION_GRID_SIZE):
            for x in range(VISION_GRID_SIZE):
                color = WHITE if self.grid[y][x] == 1 else (50, 50, 60)
                rect = (
                    self.board_rect.x + x * self.pixel_size,
                    self.board_rect.y + y * self.pixel_size,
                    self.pixel_size - 1,
                    self.pixel_size - 1,
                )
                pygame.draw.rect(self.screen, color, rect)
        self.cmd_box.draw(self.screen)
        self.btn_learn.draw(self.screen)
        self.btn_intro.draw(self.screen)
        self.btn_clear.draw(self.screen)
        self.btn_dream.draw(self.screen)
        self.btn_good.draw(self.screen)
        self.btn_bad.draw(self.screen)
        self.btn_close.draw(self.screen)
        self.screen.blit(
            self.font.render(self.status_msg, True, CYAN), (50, 50)
        )


# =========================================================================
# Speech pattern constants
# =========================================================================
SPEECH_HISTORY_MAX = 15
SPEECH_DEFAULT_CONFIDENCE = 0.7
SPEECH_REINFORCE_AMOUNT = 0.15


def _tokenize_speech(text):
    """Splits input text into uppercase tokens for concept mapping."""
    return [t.upper() for t in text.strip().split() if t.strip()]


def _compute_token_overlap(pattern_tokens, input_tokens):
    """
    Computes a similarity score between a stored pattern and current input.

    Uses Jaccard-like overlap: |intersection| / |pattern|.
    Returns a float in [0.0, 1.0].
    """
    if not pattern_tokens:
        return 0.0
    pattern_set = set(pattern_tokens)
    input_set = set(input_tokens)
    overlap = pattern_set & input_set
    return len(overlap) / len(pattern_set)


class SpeechWindow:
    """
    Speech pattern learning and associative recall window.

    Implements the General Learner's text-to-concept decomposition:
    1. User provides stimulus (input text).
    2. System searches for associative matches via token overlap.
    3. User reinforces (+/-) to strengthen/weaken associations.
    4. Sleep cycle consolidates patterns into long-term memory.

    Learning flow:
        "hola hola" → stores pattern: input="hola" → response="hola"
        "me llamo marco" → stores: input="me llamo" → response="marco"
    """

    def __init__(self, screen, memory, learner=None):
        self.screen = screen
        self.memory = memory
        self.learner = learner
        self.history = []
        self.last_matched_prod_id = None
        self.input_box = TextBox(50, 500, 350, 40)
        self.btn_intro = Button(410, 500, 70, 40, "INTRO", BLUE)
        self.btn_pos = Button(490, 500, 50, 40, "+", GREEN)
        self.btn_neg = Button(550, 500, 50, 40, "-", RED)
        self.btn_dream = Button(610, 500, 90, 40, "DREAM", PURPLE)
        self.btn_close = Button(750, 10, 40, 40, "X", RED)
        self.font = pygame.font.SysFont("Arial", 16)
        self.active = True

    def handle_event(self, event):
        """Routes UI events to the appropriate handler."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_close.is_clicked(event.pos):
                self.active = False
            if self.btn_intro.is_clicked(event.pos):
                self._process_speech(self.input_box.text.strip())
            if self.btn_pos.is_clicked(event.pos):
                self._reinforce(SPEECH_REINFORCE_AMOUNT)
            if self.btn_neg.is_clicked(event.pos):
                self._reinforce(-SPEECH_REINFORCE_AMOUNT)
            if self.btn_dream.is_clicked(event.pos) and self.learner:
                self.learner.sleep_cycle()
                self._append_history("SYS: Dream cycle complete")
        if self.input_box.handle_event(event):
            text = self.input_box.text.strip()
            if text:
                self._process_speech(text)

    def _process_speech(self, text):
        """
        Processes speech input: learns patterns and generates responses.

        Pattern format: "input_pattern response_pattern"
        - Repeated tokens: "hola hola" → learns hola→hola
        - Sequence: "me llamo bot1" → learns "me llamo"→"bot1"
        - Single word: "hola" → searches for matching patterns
        """
        if not text:
            return

        self._append_history(f"User: {text}")
        tokens = _tokenize_speech(text)

        # Register all tokens as concepts in semantic memory
        for token in tokens:
            self.memory.get_or_create_concept_id(token)

        # Create RFT coordination frames between adjacent tokens
        self._create_token_frames(tokens)

        # Try to find an associative response
        response = self._find_associative_response(tokens)

        if response != "???":
            self._append_history(f"Agent: {response}")
        else:
            # No match found → store as new pattern for learning
            self._store_speech_pattern(tokens)
            self._append_history(f"Agent: ??? (stored for learning)")

        self.input_box.text = ""

    def _create_token_frames(self, tokens):
        """Creates RFT COORD frames between adjacent tokens in a phrase."""
        for i in range(len(tokens) - 1):
            id_a = self.memory.get_or_create_concept_id(tokens[i])
            id_b = self.memory.get_or_create_concept_id(tokens[i + 1])
            self.memory.add_relational_frame(id_a, "COORD", id_b, 0.5)

    def _store_speech_pattern(self, tokens):
        """
        Stores a speech pattern as a cognitive production.

        Decomposes input into stimulus→response pairs:
        - "hola hola" → stimulus=["HOLA"], response="HOLA"
        - "me llamo bot1" → stimulus=["ME","LLAMO"], response="BOT1"
        - Single token: stimulus=[token], response=token (echo pattern)
        """
        if len(tokens) < 1:
            return

        stimulus, response = _split_stimulus_response(tokens)
        pattern_data = {
            "type": "speech_pattern",
            "stimulus": stimulus,
            "response": response,
        }

        self.memory.add_cognitive_production(
            production_type="SPEECH_PATTERN",
            name=f"SP_{'_'.join(stimulus[:3])}",
            description=json.dumps(pattern_data),
            confidence=SPEECH_DEFAULT_CONFIDENCE,
        )

    def _find_associative_response(self, input_tokens):
        """
        Searches cognitive productions for the best matching speech pattern.

        Uses token overlap scoring to find the most similar stored stimulus.
        Returns the associated response, or "???" if no match exceeds threshold.
        """
        patterns = self.memory.get_cognitive_productions(
            production_type="SPEECH_PATTERN"
        )
        best_match = _find_best_pattern_match(patterns, input_tokens)

        if best_match is None:
            self.last_matched_prod_id = None
            return "???"

        self.last_matched_prod_id = best_match["id"]
        self.memory.increment_production_usage(best_match["id"])

        data = json.loads(best_match["description"])
        return data.get("response", "???")

    def _reinforce(self, amount):
        """
        Reinforces or weakens the last matched speech pattern.

        Updates the confidence of the cognitive production.
        Positive = strengthen association. Negative = weaken it.
        """
        if self.last_matched_prod_id is None:
            self._append_history("SYS: Nothing to reinforce")
            return

        _update_production_confidence(
            self.memory, self.last_matched_prod_id, amount
        )
        sign = "+" if amount > 0 else ""
        self._append_history(f"SYS: Reinforcement {sign}{amount:.2f}")

    def _append_history(self, message):
        """Appends a message to the chat history with overflow pruning."""
        self.history.append(message)
        if len(self.history) > SPEECH_HISTORY_MAX:
            self.history = self.history[-SPEECH_HISTORY_MAX:]

    def draw(self):
        """Renders the speech window UI."""
        self.screen.fill((20, 20, 30))
        chat_rect = pygame.Rect(50, 60, 700, 400)
        pygame.draw.rect(self.screen, GRAY, chat_rect, 2)
        for i, msg in enumerate(self.history):
            color = WHITE if "User" in msg else CYAN
            if "SYS" in msg:
                color = YELLOW
            self.screen.blit(
                self.font.render(msg, True, color), (60, 70 + i * 25)
            )
        self.input_box.draw(self.screen)
        self.btn_intro.draw(self.screen)
        self.btn_pos.draw(self.screen)
        self.btn_neg.draw(self.screen)
        self.btn_dream.draw(self.screen)
        self.btn_close.draw(self.screen)


def _split_stimulus_response(tokens):
    """
    Splits a token list into stimulus and response parts.

    Rules:
    - Repeated pattern: [A, A] → stimulus=[A], response=A
    - Multi-token: [A, B, C] → stimulus=[A, B], response=C
    - Single token: [A] → stimulus=[A], response=A (echo)

    Returns:
        tuple: (stimulus_list, response_string)
    """
    if len(tokens) == 1:
        return (tokens, tokens[0])
    if _has_repeated_pattern(tokens):
        half = len(tokens) // 2
        return (tokens[:half], " ".join(tokens[half:]))
    return (tokens[:-1], tokens[-1])


def _has_repeated_pattern(tokens):
    """Checks if the token list is a repeated pattern (e.g., [A,B,A,B])."""
    if len(tokens) < 2 or len(tokens) % 2 != 0:
        return False
    half = len(tokens) // 2
    return tokens[:half] == tokens[half:]


def _find_best_pattern_match(patterns, input_tokens):
    """
    Finds the best matching speech pattern using token overlap scoring.

    Returns the pattern dict with highest score above threshold, or None.
    """
    best = None
    best_score = 0.3  # Minimum threshold for a match

    for pat in patterns:
        desc = pat.get("description")
        if not desc:
            continue
        try:
            data = json.loads(desc)
        except (json.JSONDecodeError, TypeError):
            continue

        if data.get("type") != "speech_pattern":
            continue

        stimulus = data.get("stimulus", [])
        score = _compute_token_overlap(stimulus, input_tokens)
        # Weight by confidence
        weighted_score = score * pat.get("confidence", 0.5)

        if weighted_score > best_score:
            best_score = weighted_score
            best = pat

    return best


def _update_production_confidence(memory, prod_id, delta):
    """Updates the confidence of a cognitive production, clamped to [0, 1]."""
    cur = memory.conn.cursor()
    cur.execute(
        "SELECT confidence FROM cognitive_productions WHERE id = ?",
        (prod_id,),
    )
    row = cur.fetchone()
    if row:
        new_conf = max(0.0, min(1.0, row[0] + delta))
        cur.execute(
            "UPDATE cognitive_productions SET confidence = ? WHERE id = ?",
            (new_conf, prod_id),
        )
        memory.conn.commit()
