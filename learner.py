import random
import json
from memory import Memory
from constants import *

"""
General Learner 4 (GL4) - Artificial Cognitive Engine
Based on Situational Transition Models (S1, A -> S2).
Incorporates:
1.  Bayesian Thompson Sampling for Action Selection.
2.  Visuospatial Working Memory (Agenda).
3.  Hippocampal Cognitive Mapping (Graph Nodes).
"""

class Learner:
    """
    The cognitive core of the robot. Implements the Universal Learner 
    principles (Fritz 1989): Stimulus -> Representation -> Decision -> Action.
    """
    def __init__(self, memory: Memory):
        self.memory = memory
        self.mode = "COMMAND" # 'AUTONOMOUS' or 'COMMAND'
        self.active_plan = [] # List of actions to execute
        self.agenda = []      # List of EXPECTED PERCEPTIONS (Mental Landmarks)
        self.bayesian = True  # Toggle for Bayesian Thompson Sampling

    def act(self, robot):
        """
        Determines the next move.
        1. Checks for an active plan.
        2. If no plan, tries to generate one toward a goal situation.
        3. If no plan possible, uses the best reactive rule.
        4. Fallback to random exploration.
        """
        state = robot.get_state()
        perception = state['perception']
        perc_str = json.dumps(perception)

        # 1. Follow active plan and update Visuospatial Agenda
        if self.active_plan:
            if self.agenda: self.agenda.pop(0)
            return self.active_plan.pop(0)
 
        # 2. Try to generate a plan to a goal (Cognitive Map check)
        new_plan, full_agenda = self.plan_with_agenda(perc_str)
        if new_plan:
            self.active_plan = new_plan
            self.agenda = full_agenda
            if self.agenda: self.agenda.pop(0)
            return self.active_plan.pop(0)
 
        # 3. Decision Logic: Select best action (Bayesian Thompson Sampling)
        rules = self.memory.get_rules()
        
        # Group rules by action for standard state
        action_options = {}
        for r in rules:
            if r['perception_pattern'] == perc_str:
                a = r['target_action']
                if a not in action_options: action_options[a] = []
                action_options[a].append(r['weight'])

        if not action_options:
            return random.choice([CMD_UP, CMD_DOWN, CMD_LEFT, CMD_RIGHT])

        # Thompson Sampling: Each action represents a probability distribution.
        # The agent samples from these distributions to balance exploration/exploitation.
        best_action = None
        if self.bayesian:
            best_sample = -1
            for action, weights in action_options.items():
                w = sum(weights) / len(weights)
                # Beta distribution parameters (alpha, beta).
                # Alpha represents successful trials + 1. Beta represents failure context.
                # This mimics the biological 'Confidence' weight in decision units.
                sample = random.betavariate(max(0.1, w + 1), 2)
                if sample > best_sample:
                    best_sample = sample
                    best_action = action
        else:
            # Deterministic Path: Picks the most stabilized rule.
            max_w = -1
            for action, weights in action_options.items():
                w = sum(weights) / len(weights)
                if w > max_w:
                    max_w = w
                    best_action = action
        
        return best_action
            
        # 4. Fallback to random discovery
        return random.choice([0, 1, 2, 3])

    def plan_to_goal(self, start_perc_str, max_depth=5):
        """
        Search for a sequence of actions leading from current situation to 
        a known 'goal' situation (one with a high-weight positive rule).
        Uses a BFS-like search over the known transition rules.
        """
        rules = self.memory.get_rules()
        
        # Build a transition graph from rules: Situation -> (Action, NextSituation, Weight)
        graph = {}
        for r in rules:
            s_from = r['perception_pattern']
            if s_from not in graph: graph[s_from] = []
            graph[s_from].append({
                'action': r['target_action'],
                'next_s': r['next_perception'],
                'weight': r['weight']
            })

        # Find goal situations (those with very high direct weights or objects)
        goals = {r['perception_pattern'] for r in rules if r['weight'] >= 5}
        
        if not goals: return []

        # Simple BFS to find the shortest path to any goal
        queue = [(start_perc_str, [])]
        visited = {start_perc_str}
        
        while queue:
            current_s, path = queue.pop(0)
            if len(path) >= max_depth: continue
            
            if current_s in goals and path:
                return path

            if current_s in graph:
                for transition in graph[current_s]:
                    next_s = transition['next_s']
                    if next_s and next_s not in visited:
                        visited.add(next_s)
                        new_path = path + [transition['action']]
                        queue.append((next_s, new_path))
                        
        return []

    def plan_with_agenda(self, start_perc_str, max_depth=8):
        """
        Extends planning to return both the actions and the EXPECTED SITUATIONS.
        Implements the 'Visuospatial Agenda' by anticipating landmarks.
        """
        rules = self.memory.get_rules()
        graph = {}
        for r in rules:
            s_from = r['perception_pattern']
            if s_from not in graph: graph[s_from] = []
            graph[s_from].append({
                'action': r['target_action'],
                'next_s': r['next_perception'],
                'weight': r['weight']
            })

        # Find goal situations (high reward)
        goals = {r['perception_pattern'] for r in rules if r['weight'] >= 5}
        if not goals: return [], []

        # BFS for shortest path + landmarks
        queue = [(start_perc_str, [], [start_perc_str])]
        visited = {start_perc_str}
        
        while queue:
            current_s, path, landmarks = queue.pop(0)
            if len(path) >= max_depth: continue
            
            if current_s in goals and path:
                return path, landmarks
 
            if current_s in graph:
                for trans in graph[current_s]:
                    next_s = trans['next_s']
                    if next_s and next_s not in visited:
                        visited.add(next_s)
                        queue.append((next_s, path + [trans['action']], landmarks + [next_s]))
                        
        return [], []

    def get_situational_graph(self, limit=20):
        """Returns the most important situational transitions for visualization."""
        rules = self.memory.get_rules()
        nodes = set()
        edges = []
        for r in rules[:limit]:
            s1 = r['perception_pattern']
            s2 = r['next_perception']
            if s2:
                nodes.add(s1)
                nodes.add(s2)
                edges.append((s1, r['target_action'], s2))
        return list(nodes), edges

    def sleep_cycle(self):
        """
        The 'Dream' phase. Analyzes chronological memory to:
        1. Apply the 'Forgetting Curve' (Entropy) to existing rules.
        2. Extract concrete rules from rewards.
        3. Extract 'Situational Transitions': (S1, A) -> S2.
        """
        # Step 1: Forgetting (Biological Pruning)
        self.memory.decay_rules(decay_amount=1)

        history = self.memory.get_all_chrono()
        if not history: return 0
        
        new_rules_count = 0
        
        for i in range(len(history)):
            record = history[i]
            perc_pattern = json.loads(record['perception'])
            action = record['action']
            reward = record['reward']
            
            next_perc = None
            if i < len(history) - 1:
                next_perc = json.loads(history[i+1]['perception'])

            if reward > 0:
                self.memory.add_rule(perc_pattern, action, weight=5, next_perception=next_perc)
                new_rules_count += 1
                
                if i > 0:
                    prev_record = history[i-1]
                    prev_perc = json.loads(prev_record['perception'])
                    self.memory.add_rule(prev_perc, prev_record['action'], weight=3, is_composite=1, next_perception=perc_pattern)
                    new_rules_count += 1

            elif reward < -5:
                self.memory.add_rule(perc_pattern, action, weight=-5, next_perception=next_perc)
                new_rules_count += 1
            
            else:
                self.memory.add_rule(perc_pattern, action, weight=1, next_perception=next_perc)
                new_rules_count += 1

        self.memory.conn.commit()
        return new_rules_count
