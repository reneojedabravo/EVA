# adaptive.py
"""
Optimized adaptive core integrating directly with cosmic neural model.
Manages motivations that drive neural growth and specialization using
atomic elements and chemical processes instead of traditional neurons.
"""

import random
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from collections import deque, defaultdict
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Import cosmic neural types
try:
    from cosmic import (
        CosmicNode, CosmicCluster, CosmicBrain, ElementCategory,
        NodeState, PERIODIC_TABLE, BosonType
    )
except ImportError as e:
    logging.warning(f"Cosmic neural imports not available: {e}")
    # Define dummy classes for testing
    class CosmicNode: pass
    class CosmicCluster: pass
    class CosmicBrain: pass
    class ElementCategory:
        NOBLE_GAS = "noble_gas"
        TRANSITION_METAL = "transition_metal"
        ALKALI_METAL = "alkali_metal"
        HALOGEN = "halogen"
        METALLOID = "metalloid"
        ALKALINE_EARTH = "alkaline_earth"
        ACTINIDE = "actinide"
        LANTHANIDE = "lanthanide"


@dataclass
class Drive:
    """Encapsulates a motivational drive with its properties."""
    level: float = 0.5
    urgency: float = 0.5
    chemical_affinity: float = 0.0  # Affinity to specific element categories
    element_allocation: float = 0.0  # How many elements support this drive
    base_level: float = 0.5
    encounters: int = 0
    preferred_elements: List[int] = field(default_factory=list)  # Atomic numbers
    
    def __post_init__(self):
        """Validate drive parameters."""
        self.level = max(0.0, min(1.0, self.level))
        self.urgency = max(0.0, min(1.0, self.urgency))
        self.chemical_affinity = max(0.0, min(1.0, self.chemical_affinity))
        self.element_allocation = max(0.0, min(1.0, self.element_allocation))


@dataclass
class CosmicFeedback:
    """Structured cosmic neural feedback data."""
    coherence_global: float = 0.5
    chemical_diversity: float = 0.5
    energy_efficiency: float = 0.5
    cluster_count: int = 0
    node_count: int = 0
    transmutation_activity: float = 0.0
    stability_average: float = 0.5
    reaction_products: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CosmicFeedback':
        """Create from dictionary, handling missing keys gracefully."""
        kwargs = {}
        for field_name in cls.__dataclass_fields__:
            if field_name in data:
                kwargs[field_name] = data[field_name]
        return cls(**kwargs)


class CosmicMotivationSystem:
    """
    Enhanced motivation system tailored for cosmic neural architecture.
    Manages drives through chemical affinities and elemental preferences.
    """
    
    # Element category preferences for each drive
    DRIVE_ELEMENT_PREFERENCES = {
        "self_preservation": {
            "primary": [ElementCategory.NOBLE_GAS, ElementCategory.TRANSITION_METAL],
            "secondary": [ElementCategory.ALKALINE_EARTH],
            "avoid": [ElementCategory.ACTINIDE]
        },
        "adaptation": {
            "primary": [ElementCategory.TRANSITION_METAL, ElementCategory.METALLOID],
            "secondary": [ElementCategory.LANTHANIDE],
            "avoid": []
        },
        "exploration": {
            "primary": [ElementCategory.HALOGEN, ElementCategory.ALKALI_METAL],
            "secondary": [ElementCategory.METALLOID],
            "avoid": [ElementCategory.NOBLE_GAS]
        },
        "communication": {
            "primary": [ElementCategory.TRANSITION_METAL, ElementCategory.METALLOID],
            "secondary": [ElementCategory.ALKALINE_EARTH],
            "avoid": []
        },
        "maintenance": {
            "primary": [ElementCategory.NOBLE_GAS, ElementCategory.ALKALINE_EARTH],
            "secondary": [ElementCategory.TRANSITION_METAL],
            "avoid": [ElementCategory.ACTINIDE]
        },
        "learning": {
            "primary": [ElementCategory.LANTHANIDE, ElementCategory.TRANSITION_METAL],
            "secondary": [ElementCategory.METALLOID],
            "avoid": []
        },
        "creativity": {
            "primary": [ElementCategory.ACTINIDE, ElementCategory.LANTHANIDE],
            "secondary": [ElementCategory.TRANSITION_METAL],
            "avoid": [ElementCategory.NOBLE_GAS]
        }
    }
    
    # Base drive configurations
    CORE_DRIVE_DEFAULTS = {
        "self_preservation": Drive(0.7, 0.5, base_level=0.7),
        "adaptation": Drive(0.8, 0.4, base_level=0.6),
        "exploration": Drive(0.6, 0.6, base_level=0.5),
        "communication": Drive(0.8, 0.3, base_level=0.4),
        "maintenance": Drive(0.7, 0.2, base_level=0.6),
        "learning": Drive(0.9, 0.7, base_level=0.8),
        "creativity": Drive(0.5, 0.4, base_level=0.3)
    }

    def __init__(self, cosmic_brain=None):
        self.cosmic_brain = cosmic_brain
        
        # Initialize drives from defaults
        self.core_drives = {name: Drive(**vars(drive)) 
                           for name, drive in self.CORE_DRIVE_DEFAULTS.items()}
        self.emergent_drives: Dict[str, Drive] = {}
        
        # Chemical tracking
        self.element_drive_mapping: Dict[int, str] = {}  # atomic_number -> drive_name
        self.drive_chemistry_history = deque(maxlen=100)
        
        # History tracking
        self.satisfaction_history = deque(maxlen=100)
        self.drive_conflicts = deque(maxlen=50)
        
        # Cache for expensive computations
        self._dominant_drive_cache = None
        self._cache_timestamp = 0
        self._cache_ttl = 1.0

    def set_cosmic_brain(self, cosmic_brain) -> None:
        """Establishes cosmic brain reference with validation."""
        self.cosmic_brain = cosmic_brain
        self._invalidate_cache()
        self._update_element_allocations()

    def evaluate_cosmic_state(self, cosmic_feedback: Union[Dict, CosmicFeedback]) -> None:
        """
        Evaluates motivational state based on cosmic neural feedback.
        """
        if isinstance(cosmic_feedback, dict):
            feedback = CosmicFeedback.from_dict(cosmic_feedback)
        elif isinstance(cosmic_feedback, CosmicFeedback):
            feedback = cosmic_feedback
        else:
            logging.warning(f"Invalid cosmic feedback type: {type(cosmic_feedback)}")
            return

        self._invalidate_cache()
        
        # Calculate drive updates based on cosmic state
        updates = self._calculate_cosmic_drive_updates(feedback)
        self._apply_drive_updates(updates)
        
        # Update chemical affinities
        self._update_chemical_affinities(feedback)

        logging.info(f"Cosmic state evaluated - Coherence: {feedback.coherence_global:.3f}, "
                    f"Diversity: {feedback.chemical_diversity:.3f}")

    def _calculate_cosmic_drive_updates(self, feedback: CosmicFeedback) -> Dict[str, Dict[str, float]]:
        """Calculate drive updates based on cosmic neural state."""
        updates = defaultdict(dict)
        
        # High coherence boosts adaptation and reduces maintenance urgency
        if feedback.coherence_global > 0.8:
            updates["adaptation"]["level_delta"] = 0.05
            updates["maintenance"]["urgency_multiplier"] = 0.9
        elif feedback.coherence_global < 0.4:
            updates["self_preservation"]["urgency_delta"] = 0.2
            
        # Low diversity boosts exploration
        if feedback.chemical_diversity < 0.3:
            updates["exploration"]["level_delta"] = 0.1
            updates["creativity"]["level_delta"] = 0.08
                
        # High transmutation activity affects drives differently
        if feedback.transmutation_activity > 0.05:
            updates["creativity"]["level_delta"] = 0.1
            updates["learning"]["level_delta"] = 0.05
        
        # Low energy efficiency boosts maintenance
        if feedback.energy_efficiency < 0.3:
            updates["maintenance"]["urgency_delta"] = 0.15
            
        # Few clusters boost communication need
        if feedback.cluster_count < 3:
            updates["communication"]["urgency_delta"] = 0.1
            
        return updates

    def _apply_drive_updates(self, updates: Dict[str, Dict[str, float]]) -> None:
        """Apply calculated updates efficiently."""
        for drive_name, drive_updates in updates.items():
            if drive_name in self.core_drives:
                drive = self.core_drives[drive_name]
                
                if "level_delta" in drive_updates:
                    drive.level = min(1.0, drive.level + drive_updates["level_delta"])
                if "urgency_delta" in drive_updates:
                    drive.urgency = min(1.0, drive.urgency + drive_updates["urgency_delta"])
                if "urgency_multiplier" in drive_updates:
                    drive.urgency = min(1.0, drive.urgency * drive_updates["urgency_multiplier"])

    def _update_chemical_affinities(self, feedback: CosmicFeedback) -> None:
        """Update chemical affinities based on cosmic state."""
        if not self.cosmic_brain:
            return
            
        try:
            # Get current chemical composition
            status = self.cosmic_brain.get_network_status()
            element_distribution = status.get("distribución_categorías", {})
            
            for drive_name, drive in self.core_drives.items():
                preferences = self.DRIVE_ELEMENT_PREFERENCES.get(drive_name, {})
                primary_cats = preferences.get("primary", [])
                
                # Calculate affinity based on available elements
                affinity_score = 0.0
                for cat in primary_cats:
                    cat_value = cat.value if hasattr(cat, 'value') else str(cat)
                    if cat_value in element_distribution:
                        affinity_score += element_distribution[cat_value] / status.get("total_nodos", 1)
                        
                drive.chemical_affinity = min(1.0, affinity_score)
                
        except Exception as e:
            logging.warning(f"Error updating chemical affinities: {e}")

    def process_external_stimulus(self, stimulus: Any, context: Optional[Dict] = None) -> None:
        """
        Processes external stimulus with chemical pattern matching.
        """
        self._invalidate_cache()
        
        stimulus_str = str(stimulus).lower()
        intensity = min(len(stimulus_str) / 100.0, 1.0)
        
        # Analyze stimulus for chemical/elemental patterns
        chemical_patterns = self._analyze_chemical_stimulus(stimulus_str)
        self._apply_chemical_stimulus_effects(chemical_patterns, intensity)
        
        # Standard stimulus processing
        stimulus_patterns = self._analyze_stimulus_patterns(stimulus_str)
        self._apply_stimulus_effects(stimulus_patterns, intensity)
        
        # Develop emergent drives
        self._develop_emergent_drives(stimulus_str, context)
        
        # Apply natural decay
        self._apply_natural_decay()

    def _analyze_chemical_stimulus(self, stimulus_str: str) -> Dict[str, float]:
        """Analyze stimulus for chemical/elemental content."""
        patterns = {}
        
        # Chemical keywords that affect drives
        chemical_keywords = {
            "stable": ("self_preservation", 0.2),
            "reactive": ("exploration", 0.3),
            "catalyst": ("communication", 0.25),
            "synthesis": ("creativity", 0.3),
            "decompose": ("maintenance", 0.2),
            "transmute": ("adaptation", 0.35),
            "noble": ("self_preservation", 0.15),
            "metallic": ("communication", 0.2),
            "bond": ("learning", 0.2),
            "electron": ("exploration", 0.15)
        }
        
        for keyword, (drive, boost) in chemical_keywords.items():
            if keyword in stimulus_str:
                if drive not in patterns:
                    patterns[drive] = 0.0
                patterns[drive] = max(patterns[drive], boost)
                
        return patterns

    def _apply_chemical_stimulus_effects(self, patterns: Dict[str, float], intensity: float) -> None:
        """Apply chemical stimulus effects."""
        for drive_name, boost in patterns.items():
            if drive_name in self.core_drives:
                drive = self.core_drives[drive_name]
                drive.level = min(1.0, drive.level + boost * intensity)
                drive.urgency = min(1.0, drive.urgency + boost * intensity * 0.5)

    def _analyze_stimulus_patterns(self, stimulus_str: str) -> Dict[str, Dict[str, float]]:
        """Analyze stimulus patterns for traditional drive activation."""
        patterns = {}
        
        pattern_keywords = {
            "danger": ("self_preservation", 0.3, 0.4),
            "threat": ("self_preservation", 0.3, 0.4),
            "new": ("exploration", 0.2, 0.3),
            "unknown": ("exploration", 0.2, 0.3),
            "learn": ("learning", 0.25, 0.2),
            "knowledge": ("learning", 0.25, 0.2),
            "connect": ("communication", 0.2, 0.25),
            "communicate": ("communication", 0.2, 0.25),
            "create": ("creativity", 0.3, 0.2),
            "innovate": ("creativity", 0.3, 0.2)
        }
        
        for keyword, (drive, level_boost, urgency_boost) in pattern_keywords.items():
            if keyword in stimulus_str:
                if drive not in patterns:
                    patterns[drive] = {"level_boost": 0, "urgency_boost": 0}
                patterns[drive]["level_boost"] = max(patterns[drive]["level_boost"], level_boost)
                patterns[drive]["urgency_boost"] = max(patterns[drive]["urgency_boost"], urgency_boost)
                
        return patterns

    def _apply_stimulus_effects(self, patterns: Dict[str, Dict[str, float]], intensity: float) -> None:
        """Apply stimulus effects with intensity scaling."""
        for drive_name, effects in patterns.items():
            if drive_name in self.core_drives:
                drive = self.core_drives[drive_name]
                drive.level = min(1.0, drive.level + effects["level_boost"] * intensity)
                drive.urgency = min(1.0, drive.urgency + effects["urgency_boost"] * intensity)

    def _develop_emergent_drives(self, stimulus: str, context: Optional[Dict]) -> None:
        """Develops emergent motivational patterns."""
        pattern = self._extract_pattern(stimulus, context)
        
        if pattern not in self.emergent_drives:
            self.emergent_drives[pattern] = Drive(0.1, 0.05, encounters=1)
        else:
            drive = self.emergent_drives[pattern]
            drive.encounters += 1
            drive.level = min(0.8, drive.level + 0.02)
            drive.urgency = min(0.6, drive.urgency + 0.01)
            
        # Check for promotion
        self._check_drive_promotion(pattern)

    def _extract_pattern(self, stimulus: str, context: Optional[Dict]) -> str:
        """Extract meaningful pattern from stimulus and context."""
        if context and isinstance(context, dict):
            pattern = context.get("pattern", "unknown")
        else:
            words = stimulus.split()
            pattern_words = sorted(set(words))[:3] if words else ["general"]
            pattern = "_".join(pattern_words)
            
        return pattern[:50]

    def _check_drive_promotion(self, pattern: str) -> None:
        """Check if emergent drive should be promoted to core drive."""
        if pattern in self.emergent_drives:
            emergent = self.emergent_drives[pattern]
            if emergent.encounters > 20 and emergent.level > 0.5:
                self._promote_emergent_drive(pattern)

    def _promote_emergent_drive(self, pattern: str) -> None:
        """Promotes emergent drive to core status."""
        emergent = self.emergent_drives[pattern]
        new_drive_name = f"emergent_{pattern}"
        
        self.core_drives[new_drive_name] = Drive(
            level=emergent.level * 0.8,
            urgency=emergent.urgency,
            base_level=emergent.level * 0.6
        )
        
        # Assign balanced element preferences for emergent drives
        self.DRIVE_ELEMENT_PREFERENCES[new_drive_name] = {
            "primary": [ElementCategory.TRANSITION_METAL, ElementCategory.METALLOID],
            "secondary": [ElementCategory.LANTHANIDE],
            "avoid": []
        }
        
        del self.emergent_drives[pattern]
        self._invalidate_cache()
        
        logging.info(f"Emergent drive '{pattern}' promoted to core drive")

    def _apply_natural_decay(self) -> None:
        """Applies natural decay to all motivations."""
        for drive_name, drive in self.core_drives.items():
            base_level = drive.base_level
            
            # Exponential decay toward base level
            if drive.level > base_level:
                drive.level = max(base_level, drive.level - 0.005)
            else:
                drive.level = min(base_level, drive.level + 0.002)
                
            drive.urgency = max(0.1, drive.urgency * 0.98)

    def get_dominant_drive(self) -> str:
        """Gets dominant drive with caching."""
        current_time = time.time()
        
        if (self._dominant_drive_cache and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._dominant_drive_cache
        
        all_drives = {**self.core_drives, **self.emergent_drives}
        
        # Calculate combined score including chemical affinity
        scored_drives = {}
        for name, drive in all_drives.items():
            base_score = drive.level * (1 + drive.urgency)
            chemical_bonus = drive.chemical_affinity * 0.3
            scored_drives[name] = base_score + chemical_bonus
        
        dominant = max(scored_drives, key=scored_drives.get) if scored_drives else "none"
        
        # Update cache
        self._dominant_drive_cache = dominant
        self._cache_timestamp = current_time
        
        return dominant

    def _invalidate_cache(self) -> None:
        """Invalidates cached computations."""
        self._dominant_drive_cache = None
        self._cache_timestamp = 0

    def get_drive_vector(self) -> Dict[str, Dict[str, float]]:
        """Returns comprehensive drive vector for decision making."""
        vector = {}
        
        # Include core drives
        for name, drive in self.core_drives.items():
            vector[name] = {
                "strength": drive.level * (1 + drive.urgency),
                "level": drive.level,
                "urgency": drive.urgency,
                "chemical_affinity": drive.chemical_affinity,
                "element_support": drive.element_allocation
            }
            
        # Include significant emergent drives
        for name, drive in self.emergent_drives.items():
            if drive.level > 0.2:
                vector[f"emergent_{name}"] = {
                    "strength": drive.level * (1 + drive.urgency),
                    "level": drive.level,
                    "urgency": drive.urgency,
                    "chemical_affinity": drive.chemical_affinity,
                    "element_support": drive.element_allocation
                }
                
        return vector

    def _update_element_allocations(self) -> None:
        """Updates element allocations based on current cosmic brain state."""
        if not self.cosmic_brain:
            return
            
        try:
            status = self.cosmic_brain.get_network_status()
            category_distribution = status.get("distribución_categorías", {})
            total_nodes = status.get("total_nodos", 1)
            
            # Update allocations for all drives
            for drive_name, drive in self.core_drives.items():
                drive.element_allocation = self._calculate_element_support(
                    drive_name, category_distribution, total_nodes
                )
                
        except Exception as e:
            logging.warning(f"Error updating element allocations: {e}")

    def _calculate_element_support(self, drive_name: str, category_dist: Dict, total_nodes: int) -> float:
        """Calculates current elemental support for a motivation."""
        if drive_name not in self.DRIVE_ELEMENT_PREFERENCES:
            return 0.1
            
        preferences = self.DRIVE_ELEMENT_PREFERENCES[drive_name]
        primary_cats = preferences.get("primary", [])
        secondary_cats = preferences.get("secondary", [])
        avoid_cats = preferences.get("avoid", [])
        
        support = 0.0
        
        # Add support from primary categories (full weight)
        for cat in primary_cats:
            cat_key = cat.value if hasattr(cat, 'value') else str(cat)
            if cat_key in category_dist:
                support += (category_dist[cat_key] / total_nodes) * 1.0
                
        # Add support from secondary categories (half weight)
        for cat in secondary_cats:
            cat_key = cat.value if hasattr(cat, 'value') else str(cat)
            if cat_key in category_dist:
                support += (category_dist[cat_key] / total_nodes) * 0.5
                
        # Subtract penalty from avoided categories
        for cat in avoid_cats:
            cat_key = cat.value if hasattr(cat, 'value') else str(cat)
            if cat_key in category_dist:
                support -= (category_dist[cat_key] / total_nodes) * 0.3
                
        return max(0.0, min(1.0, support))


class CosmicAdaptiveCore:
    """
    Adaptive core designed for cosmic neural architecture.
    Integrates motivational drives with chemical neural processes.
    """
    
    def __init__(self, cosmic_brain=None):
        self.cosmic_brain = cosmic_brain
        self.motivation = CosmicMotivationSystem(cosmic_brain)
        self.emotional_state = None
        
        # Metrics and history
        self.integration_cycles = 0
        self.decision_history = deque(maxlen=200)
        self.cosmic_feedback_history = deque(maxlen=100)
        
        # Chemical systems
        self.chemical_attention_system = self._init_chemical_attention_system()
        self.molecular_memory = deque(maxlen=1000)
        
        # Performance tracking
        self._last_cycle_time = time.time()

    def set_cosmic_brain(self, cosmic_brain) -> None:
        """Sets cosmic brain with proper propagation."""
        self.cosmic_brain = cosmic_brain
        self.motivation.set_cosmic_brain(cosmic_brain)

    def set_emotional_state(self, emotional_state) -> None:
        """Sets emotional system for integration."""
        self.emotional_state = emotional_state

    def _init_chemical_attention_system(self) -> Dict[str, Any]:
        """Initialize chemical attention system."""
        return {
            "focus_elements": [],  # Atomic numbers of focused elements
            "attention_strength": 0.5,
            "chemical_context": deque(maxlen=10),
            "element_salience": {}  # atomic_number -> salience_score
        }

    def perceive(self, stimulus: Any, context: Optional[Dict] = None) -> None:
        """
        Integrated perception with cosmic neural processing.
        """
        try:
            # Cosmic neural processing
            if self.cosmic_brain:
                cosmic_response = self._process_cosmic_stimulus(stimulus, context)
                self._record_cosmic_feedback(cosmic_response)
            else:
                cosmic_response = CosmicFeedback()
                
            # Motivational processing
            self.motivation.process_external_stimulus(stimulus, context)
            self.motivation.evaluate_cosmic_state(cosmic_response)
            
            # Create molecular memory episode
            episode = self._create_molecular_episode(stimulus, context, cosmic_response)
            self.molecular_memory.append(episode)
            
            # Update chemical attention
            self._update_chemical_attention_system(stimulus, context)
            
            logging.info(f"Cosmic perception - Stimulus: '{str(stimulus)[:30]}...'")
                
        except Exception as e:
            logging.error(f"Error in cosmic perception: {e}")

    def _process_cosmic_stimulus(self, stimulus: Any, context: Optional[Dict]) -> CosmicFeedback:
        """Process stimulus through cosmic brain."""
        try:
            # Simulate thinking process in cosmic brain
            stimulus_str = str(stimulus)
            self.cosmic_brain.simulate_thinking_process(stimulus_str[:20], 1.2)
            
            # Get current state
            status = self.cosmic_brain.get_network_status()
            
            return CosmicFeedback(
                coherence_global=status.get("coherencia_global", 0.5),
                chemical_diversity=status.get("diversidad_química", 0.0) / 100.0,
                energy_efficiency=status.get("eficiencia_energética", 0.5),
                cluster_count=status.get("total_clústeres", 0),
                node_count=status.get("total_nodos", 0),
                transmutation_activity=status.get("transmutaciones", 0) / 100.0,
                stability_average=0.5,  # Would need to calculate from detailed report
                reaction_products=status.get("productos_químicos", 0)
            )
            
        except Exception as e:
            logging.warning(f"Error processing cosmic stimulus: {e}")
            return CosmicFeedback()

    def _create_molecular_episode(self, stimulus: Any, context: Optional[Dict], 
                                 cosmic_response: CosmicFeedback) -> Dict[str, Any]:
        """Creates molecular memory episode."""
        return {
            "timestamp": time.time(),
            "stimulus": str(stimulus)[:100],
            "context": context,
            "cosmic_response": self._summarize_cosmic_response(cosmic_response),
            "dominant_drive": self.motivation.get_dominant_drive(),
            "emotional_state": (self.emotional_state.label() 
                              if self.emotional_state else "unknown"),
            "chemical_diversity": cosmic_response.chemical_diversity,
            "coherence": cosmic_response.coherence_global
        }

    def decide(self, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Integrated decision making with cosmic neural architecture.
        """
        drive_vector = self.motivation.get_drive_vector()
        dominant_drive = self.motivation.get_dominant_drive()
        
        # Get emotional context
        emotional_label = (self.emotional_state.label() 
                          if self.emotional_state else "neutral")
        
        # Detect drive conflicts
        conflicts = self._detect_drive_conflicts()
        
        # Select action based on cosmic state
        action = self._select_cosmic_action(dominant_drive, emotional_label, conflicts, context)
        
        # Create decision record
        decision = {
            "action": action,
            "primary_drive": dominant_drive,
            "drive_strength": drive_vector.get(dominant_drive, {}).get("strength", 0.5),
            "chemical_affinity": drive_vector.get(dominant_drive, {}).get("chemical_affinity", 0.0),
            "emotional_context": emotional_label,
            "conflicts": len(conflicts),
            "cosmic_capacity": self._assess_cosmic_capacity(),
            "context": context,
            "timestamp": time.time()
        }
        
        self.decision_history.append(decision)
        
        # Periodic cosmic growth direction
        if self.integration_cycles % 15 == 0:
            self._direct_cosmic_growth()
            
        logging.info(f"Cosmic decision - Action: '{action}' (Drive: {dominant_drive})")
            
        return decision

    def _detect_drive_conflicts(self) -> List[Dict[str, Any]]:
        """Detects motivational conflicts in cosmic context."""
        drive_vector = self.motivation.get_drive_vector()
        conflicts = []
        
        # Chemical conflict pairs (based on element categories)
        conflict_pairs = [
            ("self_preservation", "exploration"),  # Noble gases vs reactive elements
            ("maintenance", "creativity"),         # Stable vs unstable elements
            ("communication", "self_preservation") # Reactive vs inert elements
        ]
        
        for drive1, drive2 in conflict_pairs:
            if drive1 in drive_vector and drive2 in drive_vector:
                strength1 = drive_vector[drive1]["strength"]
                strength2 = drive_vector[drive2]["strength"]
                chemical1 = drive_vector[drive1]["chemical_affinity"]
                chemical2 = drive_vector[drive2]["chemical_affinity"]
                
                # Consider both motivational and chemical conflicts
                combined_conflict = (abs(strength1 - strength2) < 0.1 and 
                                   min(strength1, strength2) > 0.6 and
                                   abs(chemical1 - chemical2) > 0.3)
                
                if combined_conflict:
                    conflicts.append({
                        "drives": (drive1, drive2),
                        "intensity": min(strength1, strength2),
                        "chemical_tension": abs(chemical1 - chemical2),
                        "timestamp": time.time()
                    })
                    
        return conflicts

    def _select_cosmic_action(self, dominant_drive: str, emotional_state: str, 
                             conflicts: List, context: Optional[Dict]) -> str:
        """Selects action based on cosmic neural state."""
        # Critical emotional states
        critical_emotions = {
            "overwhelmed": "Consolidate chemical clusters and reduce diversity",
            "blocked": "Attempt nuclear transmutation for new perspectives"
        }
        
        if emotional_state in critical_emotions:
            return critical_emotions[emotional_state]
            
        # Handle creative/excited combinations with chemical context
        if emotional_state == "excited" and "creativity" in dominant_drive:
            return "Engage in chemical synthesis and elemental exploration"
        elif emotional_state == "stressed" and conflicts:
            return "Balance chemical affinities and resolve elemental tensions"
            
        # Cosmic drive-based actions
        cosmic_action_map = {
            "self_preservation": "Activate noble gas stabilization and assess chemical threats",
            "adaptation": "Facilitate elemental transmutations and adjust chemical composition",
            "exploration": "Seek new elemental combinations and expand chemical boundaries",
            "communication": "Establish metallic bonds and enhance cluster connectivity",
            "maintenance": "Perform chemical optimization and molecular consolidation",
            "learning": "Engage chemical learning processes and form new molecular patterns",
            "creativity": "Synthesize novel chemical combinations and generate elemental innovations"
        }
        
        if dominant_drive.startswith("emergent_"):
            clean_drive = dominant_drive.replace("emergent_", "")
            return f"Engage specialized chemical processing for {clean_drive}"
            
        return cosmic_action_map.get(dominant_drive, 
                                   "Maintain chemical equilibrium and observe elemental changes")

    def _assess_cosmic_capacity(self) -> float:
        """Assesses current cosmic neural capacity."""
        if not self.cosmic_brain:
            return 0.5
            
        try:
            status = self.cosmic_brain.get_network_status()
            
            # Calculate cosmic capacity metrics
            coherence = status.get("coherencia_global", 0.5)
            diversity = status.get("diversidad_química", 0.0) / 100.0
            efficiency = status.get("eficiencia_energética", 0.5)
            stability = 1.0  # Would need detailed calculation
            
            # Normalize cluster and node counts
            cluster_capacity = min(status.get("total_clústeres", 0) / 10.0, 1.0)
            node_capacity = min(status.get("total_nodos", 0) / 100.0, 1.0)
            
            cosmic_capacity = (coherence + diversity + efficiency + stability + 
                             cluster_capacity + node_capacity) / 6.0
            
            return max(0.0, min(1.0, cosmic_capacity))
            
        except Exception as e:
            logging.warning(f"Error assessing cosmic capacity: {e}")
            return 0.5

    def _direct_cosmic_growth(self) -> None:
        """Direct cosmic neural growth based on motivational needs."""
        if not self.cosmic_brain:
            return
            
        try:
            drive_vector = self.motivation.get_drive_vector()
            growth_needs = self._assess_cosmic_growth_needs(drive_vector)
            dominant = self.motivation.get_dominant_drive()
            
            for need_type, intensity in growth_needs.items():
                if intensity > 0.7:
                    self._request_cosmic_growth(need_type, dominant, intensity)
                    
        except Exception as e:
            logging.warning(f"Error directing cosmic growth: {e}")

    def _assess_cosmic_growth_needs(self, drive_vector: Dict) -> Dict[str, float]:
        """Assess cosmic neural growth needs based on drive vector."""
        needs = {
            "chemical_sensors": 0.0,
            "memory_molecules": 0.0,
            "communication_bonds": 0.0,
            "learning_plasticity": 0.0,
            "creative_synthesis": 0.0
        }
        
        for drive_name, drive_data in drive_vector.items():
            strength = drive_data["strength"]
            element_support = drive_data["element_support"]
            chemical_affinity = drive_data["chemical_affinity"]
            
            support_gap = max(0, strength - element_support)
            affinity_gap = max(0, strength - chemical_affinity)
            
            # Map drives to cosmic growth needs
            if any(keyword in drive_name for keyword in ["exploration", "self_preservation"]):
                needs["chemical_sensors"] += (support_gap + affinity_gap) * 0.4
                
            if any(keyword in drive_name for keyword in ["learning", "adaptation"]):
                needs["memory_molecules"] += (support_gap + affinity_gap) * 0.45
                needs["learning_plasticity"] += (support_gap + affinity_gap) * 0.35
                
            if "communication" in drive_name:
                needs["communication_bonds"] += (support_gap + affinity_gap) * 0.4
                
            if "creativity" in drive_name:
                needs["creative_synthesis"] += (support_gap + affinity_gap) * 0.5
                
        return needs

    def _request_cosmic_growth(self, need_type: str, dominant_drive: str, intensity: float) -> None:
        """Request specific cosmic neural growth."""
        if not hasattr(self.cosmic_brain, 'create_cluster'):
            return
            
        try:
            growth_mapping = {
                "chemical_sensors": {
                    "concept": "enhanced_perception",
                    "category": ElementCategory.HALOGEN
                },
                "memory_molecules": {
                    "concept": "molecular_memory",
                    "category": ElementCategory.LANTHANIDE
                },
                "communication_bonds": {
                    "concept": "inter_cluster_communication", 
                    "category": ElementCategory.TRANSITION_METAL
                },
                "learning_plasticity": {
                    "concept": "adaptive_learning",
                    "category": ElementCategory.METALLOID
                },
                "creative_synthesis": {
                    "concept": "creative_synthesis",
                    "category": ElementCategory.ACTINIDE
                }
            }
            
            if need_type in growth_mapping:
                growth_spec = growth_mapping[need_type]
                cluster_id = f"adaptive_{need_type}_{self.integration_cycles}"
                
                new_cluster = self.cosmic_brain.create_cluster(
                    cluster_id, 
                    growth_spec["concept"], 
                    growth_spec["category"]
                )
                
                logging.info(f"Requested cosmic growth: {need_type} -> {cluster_id}")
                
        except Exception as e:
            logging.warning(f"Error in cosmic growth request: {e}")

    def run_cycle(self, stimulus: Any, context: Optional[Dict] = None, 
                  learning_signal: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes complete cosmic integrated processing cycle.
        """
        cycle_start = time.time()
        self.integration_cycles += 1
        
        try:
            # Core cycle steps
            self.perceive(stimulus, context)
            decision = self.decide(context)
            self.act(decision, context)
            
            # Update emotional state if available
            if self.emotional_state and learning_signal:
                drive_vector = self.motivation.get_drive_vector()
                emotional_input = {k: v["level"] for k, v in drive_vector.items()}
                self.emotional_state.update(emotional_input, learning_signal)
            
            # Get cosmic brain state
            cosmic_state = {}
            if self.cosmic_brain:
                try:
                    cosmic_state = self.cosmic_brain.get_network_status()
                except:
                    cosmic_state = {"error": "cosmic_brain_unavailable"}
            
            # Compile cycle result
            cycle_result = {
                "cycle": self.integration_cycles,
                "decision": decision,
                "emotional_state": (self.emotional_state.get_emotional_summary() 
                                  if self.emotional_state else {"label": "unknown"}),
                "motivation": {
                    "dominant_drive": self.motivation.get_dominant_drive(),
                    "drive_vector": self.motivation.get_drive_vector(),
                    "conflicts": len(self._detect_drive_conflicts())
                },
                "cosmic_state": {
                    "coherence": cosmic_state.get("coherencia_global", 0.0),
                    "diversity": cosmic_state.get("diversidad_química", 0.0),
                    "efficiency": cosmic_state.get("eficiencia_energética", 0.0),
                    "clusters": cosmic_state.get("total_clústeres", 0),
                    "nodes": cosmic_state.get("total_nodos", 0),
                    "elements": cosmic_state.get("elementos_únicos", 0)
                },
                "cosmic_capacity": self._assess_cosmic_capacity(),
                "chemical_attention": len(self.chemical_attention_system["focus_elements"]),
                "molecular_memories": len(self.molecular_memory),
                "cycle_time": time.time() - cycle_start
            }
            
            self._last_cycle_time = cycle_start
            return cycle_result
            
        except Exception as e:
            logging.error(f"Error in cosmic cycle execution: {e}")
            return {"error": str(e), "cycle": self.integration_cycles}

    def act(self, decision: Dict[str, Any], context: Optional[Dict] = None) -> None:
        """Execute action with cosmic neural feedback."""
        try:
            action = decision.get("action", "No action")
            primary_drive = decision.get("primary_drive", "unknown")
            
            # Execute with cosmic integration
            if self.cosmic_brain:
                # Simulate learning from the action
                self.cosmic_brain.simulate_chemical_learning(action[:30])
                
                # Run a brief simulation cycle
                self.cosmic_brain.run_simulation_cycle()
                
            logging.info(f"Cosmic action executed: '{action}'")
                
        except Exception as e:
            logging.error(f"Error in cosmic action execution: {e}")

    def _record_cosmic_feedback(self, response: CosmicFeedback) -> None:
        """Records cosmic feedback for analysis."""
        feedback = {
            "timestamp": time.time(),
            "response": self._summarize_cosmic_response(response),
            "cycle": self.integration_cycles
        }
        self.cosmic_feedback_history.append(feedback)

    def _summarize_cosmic_response(self, response: CosmicFeedback) -> Dict[str, Any]:
        """Creates compact summary of cosmic response."""
        return {
            "coherence": round(response.coherence_global, 3),
            "diversity": round(response.chemical_diversity, 3),
            "efficiency": round(response.energy_efficiency, 3),
            "clusters": response.cluster_count,
            "nodes": response.node_count,
            "transmutations": round(response.transmutation_activity, 3)
        }

    def _update_chemical_attention_system(self, stimulus: Any, context: Optional[Dict]) -> None:
        """Updates chemical attention system."""
        # Add to chemical context window
        self.chemical_attention_system["chemical_context"].append({
            "stimulus": str(stimulus)[:50],
            "timestamp": time.time(),
            "context": context
        })
        
        # Extract elemental references from stimulus
        stimulus_str = str(stimulus).lower()
        
        # Simple element detection (could be enhanced)
        if self.cosmic_brain:
            try:
                from cosmic import PERIODIC_TABLE
                for atomic_num, element in PERIODIC_TABLE.items():
                    if (element.symbol.lower() in stimulus_str or 
                        element.name.lower() in stimulus_str):
                        if atomic_num not in self.chemical_attention_system["element_salience"]:
                            self.chemical_attention_system["element_salience"][atomic_num] = 0
                        self.chemical_attention_system["element_salience"][atomic_num] += 1
            except:
                pass
        
        # Maintain reasonable size
        if len(self.chemical_attention_system["element_salience"]) > 30:
            sorted_elements = sorted(
                self.chemical_attention_system["element_salience"].items(),
                key=lambda x: x[1], reverse=True
            )
            self.chemical_attention_system["element_salience"] = dict(sorted_elements[:20])

    def get_comprehensive_state(self) -> Dict[str, Any]:
        """Gets complete cosmic adaptive core state."""
        cosmic_network_state = {}
        if self.cosmic_brain:
            try:
                cosmic_network_state = self.cosmic_brain.get_network_status()
            except:
                cosmic_network_state = {"error": "unavailable"}
                
        return {
            "motivation_system": {
                "core_drives": {name: vars(drive) for name, drive in self.motivation.core_drives.items()},
                "emergent_drives": {name: vars(drive) for name, drive in self.motivation.emergent_drives.items()},
                "dominant_drive": self.motivation.get_dominant_drive(),
                "conflicts": self._detect_drive_conflicts()
            },
            "chemical_attention_system": self.chemical_attention_system,
            "cosmic_network": cosmic_network_state,
            "integration_metrics": {
                "total_cycles": self.integration_cycles,
                "cosmic_capacity": self._assess_cosmic_capacity(),
                "decision_history_length": len(self.decision_history),
                "cosmic_feedback_samples": len(self.cosmic_feedback_history),
                "average_cycle_time": self._calculate_average_cycle_time()
            },
            "molecular_memory": {
                "total_episodes": len(self.molecular_memory),
                "recent_episodes": list(self.molecular_memory)[-5:] if self.molecular_memory else []
            }
        }

    def _calculate_average_cycle_time(self) -> float:
        """Calculate average cycle execution time."""
        recent_decisions = list(self.decision_history)[-10:]
        if len(recent_decisions) < 2:
            return 0.0
            
        times = []
        for i in range(1, len(recent_decisions)):
            time_diff = recent_decisions[i]["timestamp"] - recent_decisions[i-1]["timestamp"]
            if time_diff > 0:
                times.append(time_diff)
                
        return sum(times) / len(times) if times else 0.0

    def analyze_cosmic_behavioral_patterns(self) -> Dict[str, Any]:
        """Analyzes emergent behavioral patterns in cosmic context."""
        if len(self.decision_history) < 10:
            return {"status": "insufficient_data"}
            
        recent_decisions = list(self.decision_history)[-50:]
        
        return {
            "drive_preferences": self._analyze_drive_frequency(recent_decisions),
            "chemical_patterns": self._analyze_chemical_patterns(recent_decisions),
            "temporal_trends": self._analyze_temporal_patterns(recent_decisions),
            "stability_score": self._calculate_behavioral_stability(recent_decisions),
            "chemical_adaptation_rate": self._calculate_chemical_adaptation_rate(),
            "cosmic_performance_metrics": self._calculate_cosmic_performance_metrics()
        }

    def _analyze_chemical_patterns(self, decisions: List[Dict]) -> Dict[str, Any]:
        """Analyze chemical affinity patterns in decisions."""
        patterns = {
            "high_affinity_drives": [],
            "low_affinity_drives": [],
            "average_chemical_support": 0.0
        }
        
        affinity_sum = 0.0
        affinity_count = 0
        
        for decision in decisions:
            drive_name = decision["primary_drive"]
            chemical_affinity = decision.get("chemical_affinity", 0.0)
            
            affinity_sum += chemical_affinity
            affinity_count += 1
            
            if chemical_affinity > 0.7 and drive_name not in patterns["high_affinity_drives"]:
                patterns["high_affinity_drives"].append(drive_name)
            elif chemical_affinity < 0.3 and drive_name not in patterns["low_affinity_drives"]:
                patterns["low_affinity_drives"].append(drive_name)
                
        if affinity_count > 0:
            patterns["average_chemical_support"] = affinity_sum / affinity_count
            
        return patterns

    def _analyze_drive_frequency(self, decisions: List[Dict]) -> Dict[str, int]:
        """Analyze frequency of drive activation."""
        frequency = defaultdict(int)
        for decision in decisions:
            drive = decision["primary_drive"]
            frequency[drive] += 1
        return dict(frequency)

    def _analyze_temporal_patterns(self, decisions: List[Dict]) -> Dict[str, int]:
        """Analyze temporal decision patterns."""
        if len(decisions) < 5:
            return {}
            
        temporal_shifts = defaultdict(int)
        prev_drive = None
        
        for decision in decisions:
            current_drive = decision["primary_drive"]
            if prev_drive and prev_drive != current_drive:
                shift_key = f"{prev_drive}_to_{current_drive}"
                temporal_shifts[shift_key] += 1
            prev_drive = current_drive
            
        return dict(temporal_shifts)

    def _calculate_behavioral_stability(self, decisions: List[Dict]) -> float:
        """Calculate behavioral stability score."""
        if len(decisions) < 5:
            return 0.5
            
        drives = [d["primary_drive"] for d in decisions]
        unique_drives = set(drives)
        drive_entropy = len(unique_drives) / len(drives)
        
        strengths = [d.get("drive_strength", 0.5) for d in decisions]
        chemical_affinities = [d.get("chemical_affinity", 0.0) for d in decisions]
        
        if len(strengths) > 1:
            mean_strength = sum(strengths) / len(strengths)
            strength_variance = sum((s - mean_strength)**2 for s in strengths) / len(strengths)
        else:
            strength_variance = 0.0
            
        if len(chemical_affinities) > 1:
            mean_affinity = sum(chemical_affinities) / len(chemical_affinities)
            affinity_variance = sum((a - mean_affinity)**2 for a in chemical_affinities) / len(chemical_affinities)
        else:
            affinity_variance = 0.0
        
        stability = 1.0 - (drive_entropy * 0.4 + min(strength_variance, 1.0) * 0.3 + min(affinity_variance, 1.0) * 0.3)
        return max(0.0, min(1.0, stability))

    def _calculate_chemical_adaptation_rate(self) -> float:
        """Calculate chemical adaptation rate."""
        if len(self.cosmic_feedback_history) < 10:
            return 0.5
            
        recent_feedback = list(self.cosmic_feedback_history)[-20:]
        
        early_values = []
        late_values = []
        
        for i, feedback in enumerate(recent_feedback):
            response = feedback.get("response", {})
            diversity = response.get("diversity", 0.0)
                
            if i < len(recent_feedback) // 2:
                early_values.append(diversity)
            else:
                late_values.append(diversity)
        
        if not early_values or not late_values:
            return 0.5
            
        early_avg = sum(early_values) / len(early_values)
        late_avg = sum(late_values) / len(late_values)
        
        adaptation_rate = (late_avg - early_avg + 1.0) / 2.0
        return max(0.0, min(1.0, adaptation_rate))

    def _calculate_cosmic_performance_metrics(self) -> Dict[str, float]:
        """Calculate cosmic system performance metrics."""
        return {
            "cycles_per_second": 1.0 / max(self._calculate_average_cycle_time(), 0.001),
            "molecular_memory_efficiency": len(self.molecular_memory) / 1000.0,
            "chemical_attention_focus": len(self.chemical_attention_system["focus_elements"]) / 20.0,
            "cosmic_integration": self._assess_cosmic_capacity()
        }


# Interfaz de prueba compatible con el sistema neural cósmico
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Prueba con un cerebro cósmico simulado si no está disponible el real
        try:
            from cosmic import CosmicBrain
            cosmic_brain = CosmicBrain(target_lifespan=850)
            
            # Crear algunos clústeres iniciales
            cosmic_brain.create_cluster("test_memory", "memoria", ElementCategory.TRANSITION_METAL)
            cosmic_brain.create_cluster("test_perception", "percepción", ElementCategory.HALOGEN)
            cosmic_brain.interconnect_clusters()
            
        except ImportError:
            cosmic_brain = None
            logging.warning("Usando cerebro cósmico simulado para pruebas")
        
        # Crear el núcleo adaptativo
        core = CosmicAdaptiveCore(cosmic_brain)
        
        # Estímulos de prueba
        test_stimuli = [
            "nuevo patrón químico detectado en el entorno",
            "la estabilidad del sistema está disminuyendo, se necesita mantenimiento",
            "oportunidad de síntesis creativa identificada",
            "solicitud de comunicación entre clústeres recibida",
            "objetivo de aprendizaje molecular alcanzado",
            "evento de transmutación detectado en la red",
            "concentración de gases nobles en aumento",
            "patrones de enlace metálico emergiendo"
        ]
        
        print("=== Ejecutando Prueba del Núcleo Adaptativo Cósmico ===")
        
        for i, stimulus in enumerate(test_stimuli):
            print(f"\n--- Ciclo {i+1}: {stimulus} ---")
            result = core.run_cycle(stimulus)
            
            if "error" not in result:
                print(f"Acción: {result['decision']['action']}")
                print(f"Drive dominante: {result['motivation']['dominant_drive']}")
                print(f"Afinidad química: {result['decision'].get('chemical_affinity', 0.0):.3f}")
                print(f"Capacidad cósmica: {result['cosmic_capacity']:.3f}")
                print(f"Tiempo del ciclo: {result.get('cycle_time', 0):.4f}s")
                
                # Mostrar estado cósmico si está disponible
                cosmic_state = result.get('cosmic_state', {})
                if cosmic_state and 'error' not in cosmic_state:
                    print(f"Coherencia: {cosmic_state.get('coherence', 0):.3f}, "
                          f"Diversidad: {cosmic_state.get('diversity', 0):.1f}%, "
                          f"Elementos: {cosmic_state.get('elements', 0)}")
            else:
                print(f"Error: {result['error']}")
                
        # Análisis de rendimiento
        print(f"\n--- Análisis del Rendimiento Cósmico ---")
        patterns = core.analyze_cosmic_behavioral_patterns()
        print(f"Puntuación de estabilidad: {patterns.get('stability_score', 0):.3f}")
        print(f"Tasa de adaptación química: {patterns.get('chemical_adaptation_rate', 0):.3f}")
        
        performance = patterns.get('cosmic_performance_metrics', {})
        for metric, value in performance.items():
            print(f"{metric}: {value:.3f}")
            
        # Patrones químicos
        chemical_patterns = patterns.get('chemical_patterns', {})
        print(f"Apoyo químico promedio: {chemical_patterns.get('average_chemical_support', 0):.3f}")
        print(f"Drives de alta afinidad: {chemical_patterns.get('high_affinity_drives', [])}")
        
    except Exception as e:
        logging.error(f"Error en la ejecución de la prueba: {e}")
        print(f"La prueba falló: {e}")
