# adaptive.py
"""
Núcleo Adaptativo — Emociones, Instintos y Regulación Neuronal Híbrida.

Arquitectura:
  InstinctCore       — impulsos de supervivencia de baja latencia
  EmotionEngine      — estados emocionales como moduladores de señal
  MotivationSystem   — drives de alto nivel y emergentes
  AttentionSystem    — filtrado de saliencia y foco
  AdaptiveCore       — integrador principal: conecta todo lo anterior
                       con neuronas animales, miceliales y sinapsis

Al ejecutarse directamente muestra un diagnóstico interactivo completo.
"""

import math
import random
import time
import traceback
from collections import deque, defaultdict
from enum import Enum
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

# ── Importaciones del ecosistema neuronal ────────────────────────────────────
from monitoring import log_event, log_neuron_error, log_neuron_warning
from animal    import create_cognitive_animal_neuron,   CognitiveAnimalNeuronBase
from micelial  import create_cognitive_micelial_neuron, CognitiveMicelialNeuronBase
from synapse   import SynapseManager, ElectricalSynapse, ChemicalSynapse, HybridSynapse


# ═══════════════════════════════════════════════════════════════════════════════
#  1.  INSTINTOS — núcleo de supervivencia (latencia mínima)
# ═══════════════════════════════════════════════════════════════════════════════

class InstinctID(Enum):
    """Instintos primarios del ser neuronal."""
    SURVIVE      = "survive"       # autopreservación ante amenaza
    FLEE         = "flee"          # huida de daño inminente
    FEED         = "feed"          # búsqueda de recursos/energía
    BOND         = "bond"          # cohesión social/red
    EXPLORE      = "explore"       # curiosidad y expansión
    REST         = "rest"          # recuperación y consolidación
    DEFEND       = "defend"        # protección de la integridad
    REPRODUCE    = "reproduce"     # replicar patrones exitosos


# Umbrales de disparo (0–1). Por encima → instinto activo
_INSTINCT_THRESHOLD = {
    InstinctID.SURVIVE:   0.55,
    InstinctID.FLEE:      0.70,
    InstinctID.FEED:      0.45,
    InstinctID.BOND:      0.40,
    InstinctID.EXPLORE:   0.35,
    InstinctID.REST:      0.60,
    InstinctID.DEFEND:    0.65,
    InstinctID.REPRODUCE: 0.50,
}

# Qué neuronas animales activa cada instinto (señal directa)
_INSTINCT_ANIMAL_TARGETS = {
    InstinctID.SURVIVE:   ["nociceptor",              "risk_assessor"],
    InstinctID.FLEE:      ["speed_neuron",            "adaptive_threshold_cell"],
    InstinctID.FEED:      ["chemotaxis_gradient",     "olfactory_receptor"],
    InstinctID.BOND:      ["mirror_neuron",           "social_signal_interpreter"],
    InstinctID.EXPLORE:   ["place_cell",              "head_direction_cell"],
    InstinctID.REST:      ["cpg_neuron",              "barometric_neuron"],
    InstinctID.DEFEND:    ["receptive_field_cell",    "pause_interneuron"],
    InstinctID.REPRODUCE: ["song_neuron",             "dopaminergic_modulator"],
}

# Qué neuronas miceliales activa cada instinto (señal conceptual)
_INSTINCT_MICELIAL_TARGETS = {
    InstinctID.SURVIVE:   ["systemic_resistance_node", "global_coherence_coordinator"],
    InstinctID.FLEE:      ["turgor_pressure_integrator","calcium_wave_messenger"],
    InstinctID.FEED:      ["hyphal_integrator",         "auxin_gradient"],
    InstinctID.BOND:      ["anastomosis_node",          "quorum_sensing_node"],
    InstinctID.EXPLORE:   ["plasmodium_collector",      "abstract_pattern_integrator"],
    InstinctID.REST:      ["glycolytic_oscillator",     "schwann_conceptual_cell"],
    InstinctID.DEFEND:    ["conceptual_ph_sensor",      "stomatal_guard_cell"],
    InstinctID.REPRODUCE: ["insight_propagator",        "knowledge_synthesizer"],
}


class InstinctCore:
    """Motor de instintos de baja latencia.

    Los instintos son reflejos: se activan antes que cualquier razonamiento.
    Modulan directamente el peso de las sinapsis y la urgencia emocional.
    """

    def __init__(self):
        self._lock   = RLock()
        self._levels: Dict[InstinctID, float] = {k: 0.3 for k in InstinctID}
        self._active: Dict[InstinctID, bool]  = {k: False for k in InstinctID}
        self._history = deque(maxlen=200)
        self._suppression: Dict[InstinctID, float] = {k: 0.0 for k in InstinctID}
        self._trigger_counts: Dict[InstinctID, int] = {k: 0 for k in InstinctID}

    # ── Señal externa ─────────────────────────────────────────────────────
    def receive_signal(self, threat: float = 0.0, energy: float = 0.5,
                       social: float = 0.5, novelty: float = 0.5,
                       fatigue: float = 0.0, damage: float = 0.0) -> Dict[str, Any]:
        """Evalúa señales del entorno y actualiza niveles instintivos."""
        with self._lock:
            now = time.time()

            # Mapear señales a instintos
            updates = {
                InstinctID.SURVIVE:   max(threat, damage),
                InstinctID.FLEE:      threat * 1.2,
                InstinctID.FEED:      max(0.0, 0.8 - energy),
                InstinctID.BOND:      social,
                InstinctID.EXPLORE:   novelty * (1.0 - threat * 0.6),
                InstinctID.REST:      fatigue,
                InstinctID.DEFEND:    damage,
                InstinctID.REPRODUCE: min(energy, 1.0 - fatigue) * 0.6,
            }

            triggered = []
            for inst, raw in updates.items():
                # Suavizado exponencial
                alpha = 0.3
                self._levels[inst] = max(0.0, min(1.0,
                    self._levels[inst] * (1 - alpha) + raw * alpha
                    - self._suppression[inst]
                ))
                # Evaluar umbral
                was_active = self._active[inst]
                self._active[inst] = self._levels[inst] >= _INSTINCT_THRESHOLD[inst]
                if self._active[inst] and not was_active:
                    self._trigger_counts[inst] += 1
                    triggered.append(inst.value)
                # Decaimiento de supresión
                self._suppression[inst] = max(0.0, self._suppression[inst] - 0.02)

            self._history.append({
                "ts": now, "threat": threat, "energy": energy,
                "triggered": triggered,
            })
            return self._snapshot()

    def suppress(self, instinct: InstinctID, amount: float = 0.3):
        """Suprime temporalmente un instinto (p.ej. cuando la emoción lo resuelve)."""
        with self._lock:
            self._suppression[instinct] = min(1.0,
                self._suppression[instinct] + amount)

    def get_active(self) -> List[InstinctID]:
        with self._lock:
            return [k for k, v in self._active.items() if v]

    def get_dominant(self) -> Optional[InstinctID]:
        with self._lock:
            active = {k: self._levels[k] for k, v in self._active.items() if v}
            return max(active, key=active.get) if active else None

    def get_level(self, inst: InstinctID) -> float:
        with self._lock:
            return self._levels[inst]

    def _snapshot(self) -> Dict:
        return {
            "active":   [k.value for k, v in self._active.items() if v],
            "dominant": self.get_dominant().value if self.get_dominant() else None,
            "levels":   {k.value: round(v, 3) for k, v in self._levels.items()},
        }

    def get_status(self) -> Dict:
        with self._lock:
            return {
                **self._snapshot(),
                "trigger_counts": {k.value: v for k, v in self._trigger_counts.items()},
                "history_size":   len(self._history),
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  2.  EMOCIONES — reguladores neuronales de medio plazo
# ═══════════════════════════════════════════════════════════════════════════════

class EmotionID(Enum):
    """Emociones primarias y secundarias."""
    # Primarias
    FEAR      = "fear"
    ANGER     = "anger"
    JOY       = "joy"
    SADNESS   = "sadness"
    DISGUST   = "disgust"
    SURPRISE  = "surprise"
    TRUST     = "trust"
    ANTICIPATION = "anticipation"
    # Secundarias (combinaciones)
    CURIOSITY   = "curiosity"    # anticipation + joy
    ANXIETY     = "anxiety"      # fear + anticipation
    FRUSTRATION = "frustration"  # anger + sadness
    ENTHUSIASM  = "enthusiasm"   # joy + anticipation
    CALM        = "calm"         # trust + joy (bajo arousal)
    ALERT       = "alert"        # fear + surprise


# Valencia y arousal base por emoción
_EMOTION_VALENCE = {
    EmotionID.FEAR: -0.8,  EmotionID.ANGER: -0.6,
    EmotionID.JOY:   0.9,  EmotionID.SADNESS: -0.7,
    EmotionID.DISGUST: -0.5, EmotionID.SURPRISE: 0.2,
    EmotionID.TRUST: 0.7,  EmotionID.ANTICIPATION: 0.4,
    EmotionID.CURIOSITY: 0.6, EmotionID.ANXIETY: -0.5,
    EmotionID.FRUSTRATION: -0.6, EmotionID.ENTHUSIASM: 0.8,
    EmotionID.CALM: 0.5,   EmotionID.ALERT: -0.2,
}

_EMOTION_AROUSAL = {
    EmotionID.FEAR: 0.9,   EmotionID.ANGER: 0.85,
    EmotionID.JOY: 0.7,    EmotionID.SADNESS: 0.2,
    EmotionID.DISGUST: 0.5, EmotionID.SURPRISE: 0.8,
    EmotionID.TRUST: 0.3,  EmotionID.ANTICIPATION: 0.6,
    EmotionID.CURIOSITY: 0.65, EmotionID.ANXIETY: 0.75,
    EmotionID.FRUSTRATION: 0.7, EmotionID.ENTHUSIASM: 0.85,
    EmotionID.CALM: 0.1,   EmotionID.ALERT: 0.8,
}

# Neuromodulador dominante por emoción
_EMOTION_NEUROMOD = {
    EmotionID.FEAR:         "norepinephrine",
    EmotionID.ANGER:        "norepinephrine",
    EmotionID.JOY:          "dopamine",
    EmotionID.SADNESS:      "serotonin",
    EmotionID.DISGUST:      "gaba",
    EmotionID.SURPRISE:     "acetylcholine",
    EmotionID.TRUST:        "serotonin",
    EmotionID.ANTICIPATION: "dopamine",
    EmotionID.CURIOSITY:    "dopamine",
    EmotionID.ANXIETY:      "norepinephrine",
    EmotionID.FRUSTRATION:  "norepinephrine",
    EmotionID.ENTHUSIASM:   "dopamine",
    EmotionID.CALM:         "serotonin",
    EmotionID.ALERT:        "norepinephrine",
}

# Cómo los instintos elevan emociones
_INSTINCT_TO_EMOTION: Dict[InstinctID, List[Tuple[EmotionID, float]]] = {
    InstinctID.SURVIVE:   [(EmotionID.FEAR, 0.7),  (EmotionID.ALERT, 0.5)],
    InstinctID.FLEE:      [(EmotionID.FEAR, 0.9),  (EmotionID.ANXIETY, 0.6)],
    InstinctID.FEED:      [(EmotionID.ANTICIPATION, 0.5), (EmotionID.JOY, 0.3)],
    InstinctID.BOND:      [(EmotionID.TRUST, 0.6), (EmotionID.JOY, 0.4)],
    InstinctID.EXPLORE:   [(EmotionID.CURIOSITY, 0.7), (EmotionID.ENTHUSIASM, 0.4)],
    InstinctID.REST:      [(EmotionID.CALM, 0.8),  (EmotionID.SADNESS, 0.1)],
    InstinctID.DEFEND:    [(EmotionID.ANGER, 0.7), (EmotionID.FEAR, 0.4)],
    InstinctID.REPRODUCE: [(EmotionID.ENTHUSIASM, 0.6), (EmotionID.ANTICIPATION, 0.5)],
}


class EmotionEngine:
    """Motor emocional con dinámica de Valencia-Arousal y neuromodulación.

    Las emociones actúan como moduladores de ganancia sobre las sinapsis:
    alta arousal → aumenta la transmisión eléctrica animal
    valencia positiva → favorece plasticidad LTP
    valencia negativa → favorece inhibición y LTD

    El estado emocional es un punto en el espacio VA que se mueve
    suavemente según inputs de instintos y aprendizaje.
    """

    def __init__(self):
        self._lock       = RLock()
        self._intensities: Dict[EmotionID, float] = {e: 0.05 for e in EmotionID}
        self._valence    = 0.2    # −1 (negativo) … +1 (positivo)
        self._arousal    = 0.3    # 0 (calmo) … 1 (activado)
        self._dominant: Optional[EmotionID] = EmotionID.CALM
        self._history    = deque(maxlen=300)
        self._mood_inertia = 0.85   # resistencia al cambio rápido

    # ── Actualización desde instintos ────────────────────────────────────
    def update_from_instincts(self, instinct_core: InstinctCore):
        with self._lock:
            for inst in instinct_core.get_active():
                mappings = _INSTINCT_TO_EMOTION.get(inst, [])
                for emo, boost in mappings:
                    self._intensities[emo] = min(1.0,
                        self._intensities[emo] + boost * 0.15
                    )
            self._recompute_va()
            self._decay()

    # ── Actualización desde aprendizaje / feedback ────────────────────────
    def update_from_signal(self, signal: str, reward: float = 0.0):
        """Actualiza emociones según señal de aprendizaje.
        signal: 'success', 'failure', 'conflict', 'discovery', 'neutral'
        reward: −1…+1
        """
        with self._lock:
            updates: Dict[EmotionID, float] = {}
            if signal == "success":
                updates = {EmotionID.JOY: 0.2, EmotionID.TRUST: 0.1}
            elif signal == "failure":
                updates = {EmotionID.FRUSTRATION: 0.2, EmotionID.SADNESS: 0.1}
            elif signal == "conflict":
                updates = {EmotionID.ANXIETY: 0.2, EmotionID.FRUSTRATION: 0.15}
            elif signal == "discovery":
                updates = {EmotionID.CURIOSITY: 0.25, EmotionID.ENTHUSIASM: 0.15}
            elif signal == "threat":
                updates = {EmotionID.FEAR: 0.3, EmotionID.ALERT: 0.2}
            elif signal == "resolved":
                updates = {EmotionID.CALM: 0.2, EmotionID.TRUST: 0.15}

            for emo, delta in updates.items():
                self._intensities[emo] = min(1.0,
                    self._intensities[emo] + delta + reward * 0.05
                )
            if reward > 0.5:
                self._intensities[EmotionID.JOY] = min(1.0,
                    self._intensities[EmotionID.JOY] + reward * 0.1)
            elif reward < -0.5:
                self._intensities[EmotionID.SADNESS] = min(1.0,
                    self._intensities[EmotionID.SADNESS] + abs(reward) * 0.1)

            self._recompute_va()
            self._history.append({
                "ts": time.time(), "signal": signal, "reward": reward,
                "dominant": self._dominant.value if self._dominant else "none",
                "valence": round(self._valence, 3),
                "arousal": round(self._arousal, 3),
            })
            self._decay()

    def _recompute_va(self):
        """Recalcula valencia y arousal promediados por intensidad."""
        total = sum(self._intensities.values()) or 1e-9
        new_v = sum(
            _EMOTION_VALENCE[e] * v for e, v in self._intensities.items()
        ) / total
        new_a = sum(
            _EMOTION_AROUSAL[e] * v for e, v in self._intensities.items()
        ) / total
        # Inercia emocional (el estado no cambia de golpe)
        self._valence = (self._valence * self._mood_inertia +
                         new_v * (1 - self._mood_inertia))
        self._arousal = (self._arousal * self._mood_inertia +
                         new_a * (1 - self._mood_inertia))
        # Emoción dominante
        self._dominant = max(self._intensities, key=self._intensities.get)

    def _decay(self):
        """Decaimiento pasivo hacia estado base."""
        base = 0.05
        for e in EmotionID:
            self._intensities[e] = max(base, self._intensities[e] * 0.97)

    # ── Modulación sobre sinapsis ─────────────────────────────────────────
    def get_synaptic_modulation(self) -> Dict[str, float]:
        """Retorna factores de modulación para el motor de plasticidad."""
        with self._lock:
            dom = self._dominant
            return {
                "neuromodulator": _EMOTION_NEUROMOD.get(dom, "dopamine"),
                "nm_level":       self._arousal,
                "gain":           1.0 + self._valence * 0.3,
                "ltp_bias":       max(0.0, self._valence),
                "ltd_bias":       max(0.0, -self._valence),
                "arousal":        self._arousal,
                "valence":        self._valence,
            }

    # ── Estado público ────────────────────────────────────────────────────
    @property
    def valence(self)  -> float:
        with self._lock: return self._valence

    @property
    def arousal(self)  -> float:
        with self._lock: return self._arousal

    @property
    def dominant(self) -> EmotionID:
        with self._lock: return self._dominant or EmotionID.CALM

    def label(self) -> str:
        return self.dominant.value

    def get_summary(self) -> Dict:
        with self._lock:
            top3 = sorted(self._intensities.items(),
                          key=lambda x: x[1], reverse=True)[:3]
            return {
                "dominant":   self._dominant.value if self._dominant else "calm",
                "valence":    round(self._valence, 3),
                "arousal":    round(self._arousal, 3),
                "top3":       [(e.value, round(v, 3)) for e, v in top3],
                "neuromod":   _EMOTION_NEUROMOD.get(self._dominant, "dopamine"),
            }

    def get_status(self) -> Dict:
        with self._lock:
            return {
                **self.get_summary(),
                "intensities": {e.value: round(v, 3)
                                for e, v in self._intensities.items()},
                "history_size": len(self._history),
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  3.  MOTIVACIONES — drives de alto nivel
# ═══════════════════════════════════════════════════════════════════════════════

_DRIVE_DEFAULTS = {
    "self_preservation": {"level": 0.70, "urgency": 0.50},
    "adaptation":        {"level": 0.75, "urgency": 0.40},
    "exploration":       {"level": 0.60, "urgency": 0.55},
    "communication":     {"level": 0.65, "urgency": 0.30},
    "maintenance":       {"level": 0.55, "urgency": 0.20},
    "learning":          {"level": 0.85, "urgency": 0.65},
    "creativity":        {"level": 0.50, "urgency": 0.35},
    "homeostasis":       {"level": 0.80, "urgency": 0.25},
}

_CONFLICT_PAIRS = [
    ("self_preservation", "exploration"),
    ("maintenance",       "creativity"),
    ("communication",     "self_preservation"),
    ("homeostasis",       "exploration"),
]

# Cómo los instintos potencian drives
_INSTINCT_TO_DRIVE: Dict[InstinctID, List[Tuple[str, float]]] = {
    InstinctID.SURVIVE:   [("self_preservation", 0.4), ("homeostasis", 0.2)],
    InstinctID.FLEE:      [("self_preservation", 0.5)],
    InstinctID.FEED:      [("homeostasis", 0.4),       ("maintenance", 0.2)],
    InstinctID.BOND:      [("communication", 0.4),     ("adaptation", 0.2)],
    InstinctID.EXPLORE:   [("exploration", 0.5),       ("learning", 0.3)],
    InstinctID.REST:      [("maintenance", 0.5),       ("homeostasis", 0.3)],
    InstinctID.DEFEND:    [("self_preservation", 0.4), ("communication", 0.1)],
    InstinctID.REPRODUCE: [("creativity", 0.4),        ("learning", 0.3)],
}


class MotivationSystem:
    """Sistema de drives motivacionales de alto nivel.

    Los instintos activos elevan drives relacionados.
    Los drives emergentes pueden ascender a core drives si se repiten.
    """

    def __init__(self):
        self._lock = RLock()
        self.core_drives = {
            k: {**v, "neural_allocation": 0.0}
            for k, v in _DRIVE_DEFAULTS.items()
        }
        self.emergent_drives: Dict[str, Dict] = {}
        self._satisfaction_history = deque(maxlen=100)
        self._conflict_log         = deque(maxlen=50)

    # ── Actualización desde instintos ─────────────────────────────────────
    def update_from_instincts(self, instinct_core: InstinctCore):
        with self._lock:
            for inst in instinct_core.get_active():
                for drive_name, boost in _INSTINCT_TO_DRIVE.get(inst, []):
                    if drive_name in self.core_drives:
                        d = self.core_drives[drive_name]
                        d["level"]   = min(1.0, d["level"]   + boost * 0.08)
                        d["urgency"] = min(1.0, d["urgency"] + boost * 0.05)
            self._decay()

    # ── Estímulo externo ──────────────────────────────────────────────────
    def process_stimulus(self, text: str, context: Dict = None):
        text = text.lower()
        boosts: Dict[str, Tuple[float, float]] = {}
        if any(w in text for w in ["danger", "threat", "damage"]):
            boosts["self_preservation"] = (0.25, 0.30)
        if any(w in text for w in ["new", "unknown", "novel"]):
            boosts["exploration"] = (0.20, 0.25)
        if any(w in text for w in ["learn", "understand", "knowledge"]):
            boosts["learning"] = (0.25, 0.20)
        if any(w in text for w in ["connect", "communicate", "share"]):
            boosts["communication"] = (0.20, 0.20)
        if any(w in text for w in ["create", "innovate", "imagine"]):
            boosts["creativity"] = (0.30, 0.15)
        if any(w in text for w in ["balance", "stable", "restore"]):
            boosts["homeostasis"] = (0.20, 0.15)

        with self._lock:
            for drive_name, (dl, du) in boosts.items():
                if drive_name in self.core_drives:
                    d = self.core_drives[drive_name]
                    d["level"]   = min(1.0, d["level"]   + dl)
                    d["urgency"] = min(1.0, d["urgency"] + du)
            # Drives emergentes
            pattern = "_".join(sorted(set(text.split()))[:3]) or "general"
            if pattern not in self.emergent_drives:
                self.emergent_drives[pattern] = {
                    "level": 0.1, "urgency": 0.05, "encounters": 1,
                    "neural_allocation": 0.0,
                }
            else:
                ed = self.emergent_drives[pattern]
                ed["encounters"] += 1
                ed["level"]   = min(0.8, ed["level"]   + 0.02)
                ed["urgency"] = min(0.6, ed["urgency"] + 0.01)
                if ed["encounters"] > 15 and ed["level"] > 0.45:
                    self._promote_emergent(pattern)
            self._decay()

    def _promote_emergent(self, pattern: str):
        ed = self.emergent_drives.pop(pattern)
        name = f"emergent_{pattern[:20]}"
        self.core_drives[name] = {
            "level": ed["level"] * 0.8, "urgency": ed["urgency"],
            "neural_allocation": 0.0,
        }
        log_event(f"Drive emergente '{name}' promovido a core", "INFO")

    def _decay(self):
        for name, d in self.core_drives.items():
            base_l = _DRIVE_DEFAULTS.get(name, {}).get("level", 0.5)
            base_u = _DRIVE_DEFAULTS.get(name, {}).get("urgency", 0.3)
            d["level"]   = d["level"]   * 0.998 + base_l * 0.002
            d["urgency"] = max(base_u * 0.8, d["urgency"] * 0.985)

    # ── Consultas ─────────────────────────────────────────────────────────
    def get_dominant_drive(self) -> str:
        with self._lock:
            all_d = {**self.core_drives,
                     **{f"e_{k}": v for k, v in self.emergent_drives.items()
                        if v["level"] > 0.2}}
            scored = {n: d["level"] * (1 + d["urgency"]) for n, d in all_d.items()}
            return max(scored, key=scored.get) if scored else "maintenance"

    def get_drive_vector(self) -> Dict[str, Dict]:
        with self._lock:
            vec = {}
            for name, d in self.core_drives.items():
                vec[name] = {
                    "strength":        round(d["level"] * (1 + d["urgency"]), 4),
                    "level":           round(d["level"],   4),
                    "urgency":         round(d["urgency"], 4),
                    "neural_support":  round(d.get("neural_allocation", 0.0), 4),
                }
            return vec

    def detect_conflicts(self) -> List[Dict]:
        with self._lock:
            vec      = self.get_drive_vector()
            conflicts = []
            for d1, d2 in _CONFLICT_PAIRS:
                if d1 in vec and d2 in vec:
                    s1, s2 = vec[d1]["strength"], vec[d2]["strength"]
                    if abs(s1 - s2) < 0.12 and min(s1, s2) > 0.55:
                        conflicts.append({"drives": (d1, d2), "intensity": min(s1, s2)})
            self._conflict_log.extend(conflicts)
            return conflicts

    def get_status(self) -> Dict:
        with self._lock:
            return {
                "dominant_drive":    self.get_dominant_drive(),
                "core_drives":       {k: {kk: round(vv, 3) for kk, vv in v.items()}
                                      for k, v in self.core_drives.items()},
                "emergent_count":    len(self.emergent_drives),
                "conflicts":         len(self.detect_conflicts()),
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  4.  SISTEMA DE ATENCIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class AttentionSystem:
    """Filtrado de saliencia y foco atencional.

    La atención es modulada por las emociones (alta arousal → más foco) y
    los instintos (supervivencia captura el foco). Dirige qué neuronas
    reciben señales prioritarias.
    """

    def __init__(self, capacity: int = 7):
        self._lock        = RLock()
        self.capacity     = capacity
        self._salience:   Dict[str, float] = {}
        self._focus_queue = deque(maxlen=capacity)
        self._context_win = deque(maxlen=12)
        self._spotlight:  Optional[str]    = None

    def update(self, stimulus: str, instinct_core: InstinctCore,
               emotion_engine: EmotionEngine):
        with self._lock:
            # Saliencia base
            key = stimulus[:30]
            self._salience[key] = min(1.0,
                self._salience.get(key, 0.0) + 0.15 +
                emotion_engine.arousal * 0.2
            )
            # Instintos de supervivencia capturan el foco
            if instinct_core.get_dominant() in (
                    InstinctID.SURVIVE, InstinctID.FLEE, InstinctID.DEFEND):
                self._spotlight = key

            self._focus_queue.append(key)
            self._context_win.append({"s": key, "ts": time.time()})
            # Decaimiento de saliencia
            for k in list(self._salience):
                self._salience[k] *= 0.96
                if self._salience[k] < 0.01:
                    del self._salience[k]

    def get_top_foci(self, n: int = 3) -> List[Tuple[str, float]]:
        with self._lock:
            return sorted(self._salience.items(),
                          key=lambda x: x[1], reverse=True)[:n]

    def get_status(self) -> Dict:
        with self._lock:
            return {
                "spotlight":       self._spotlight,
                "top_foci":        self.get_top_foci(3),
                "salience_items":  len(self._salience),
                "context_window":  len(self._context_win),
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  5.  RED NEURONAL HÍBRIDA INTEGRADA
# ═══════════════════════════════════════════════════════════════════════════════

_ANIMAL_ROSTER = [
    ("visual_feature_extractor", {"feature_type": "motion"}),
    ("attention_focuser",         {}),
    ("decision_maker",            {}),
    ("risk_assessor",             {}),
    ("anomaly_detector",          {}),
    ("place_cell",                {"preferred_location": (0.5, 0.5)}),
    ("mirror_neuron",             {"action_class": "grasp"}),
    ("cpg_neuron",                {"intrinsic_frequency": 0.4}),
    ("dopaminergic_modulator",    {}),
    ("adaptive_threshold_cell",   {}),
    ("nociceptor",                {"pain_type": "mechanical"}),
    ("speed_neuron",              {}),
    ("pause_interneuron",         {}),
    ("receptive_field_cell",      {"polarity": "ON"}),
    ("self_monitor",              {}),
]

_MICELIAL_ROSTER = [
    ("abstract_pattern_integrator",    {}),
    ("global_coherence_coordinator",   {}),
    ("conceptual_bridge_builder",      {}),
    ("insight_propagator",             {}),
    ("knowledge_synthesizer",          {"domain_specializations": ["survival","emotion"]}),
    ("hyphal_integrator",              {}),
    ("anastomosis_node",               {}),
    ("plasmodium_collector",           {}),
    ("calcium_wave_messenger",         {}),
    ("quorum_sensing_node",            {}),
    ("systemic_resistance_node",       {}),
    ("glycolytic_oscillator",          {}),
    ("stomatal_guard_cell",            {}),
    ("conceptual_ph_sensor",           {}),
    ("deep_reflection_orchestrator",   {}),
]


class HybridNeuralNetwork:
    """Red neuronal híbrida gestionada desde el núcleo adaptativo.

    Mantiene listas de neuronas animales y miceliales, y usa
    SynapseManager para todas las conexiones.
    """

    def __init__(self, n_animal: int = 5, n_micelial: int = 5):
        self.animals:   List[CognitiveAnimalNeuronBase]   = []
        self.micelials: List[CognitiveMicelialNeuronBase] = []
        self.synapse_mgr = SynapseManager(
            prune_interval_s  = 30.0,
            utility_threshold = 0.08,
            error_rate_max    = 0.75,
            inactivity_secs   = 120.0,
        )
        self._lock = RLock()
        self._build(n_animal, n_micelial)

    # ── Construcción ──────────────────────────────────────────────────────
    def _build(self, na: int, nm: int):
        for i in range(na):
            ntype, kwargs = _ANIMAL_ROSTER[i % len(_ANIMAL_ROSTER)]
            nid = f"A{i+1:03d}_{ntype[:8]}"
            try:
                n = create_cognitive_animal_neuron(ntype, nid, **kwargs)
                self.animals.append(n)
            except Exception as e:
                log_neuron_error(nid, f"build animal: {e}")

        for i in range(nm):
            ntype, kwargs = _MICELIAL_ROSTER[i % len(_MICELIAL_ROSTER)]
            nid = f"M{i+1:03d}_{ntype[:8]}"
            try:
                n = create_cognitive_micelial_neuron(ntype, nid, **kwargs)
                self.micelials.append(n)
            except Exception as e:
                log_neuron_error(nid, f"build micelial: {e}")

        self._wire()

    def _wire(self):
        """Conecta la red con una topología representativa."""
        mgr = self.synapse_mgr
        # Animal → animal (serial sensorimotor)
        for i in range(len(self.animals) - 1):
            mgr.connect(self.animals[i], self.animals[i+1],
                        "electrical", "excitatory", persistent=True)
        # Micelial → micelial (serial conceptual)
        for i in range(len(self.micelials) - 1):
            mgr.connect(self.micelials[i], self.micelials[i+1],
                        "chemical", "excitatory", persistent=True)
        # Híbrido: primeras neuronas de cada dominio
        n_cross = min(4, len(self.animals), len(self.micelials))
        for i in range(n_cross):
            mgr.connect(self.animals[i], self.micelials[i],
                        "hybrid", "excitatory", persistent=True)
            mgr.connect(self.micelials[i], self.animals[i],
                        "hybrid", "modulatory", persistent=False)
        # Bundle paralelo (broadcast instintivo)
        if len(self.animals) >= 3 and self.micelials:
            mgr.create_parallel_bundle(
                self.animals[:3], self.micelials[0], "hybrid")
        # Cadena serial integrativa
        if len(self.animals) >= 2 and len(self.micelials) >= 1:
            mgr.create_serial_chain(
                [self.animals[0], self.animals[1], self.micelials[0]])

    # ── Transmisión guiada por instintos y emociones ───────────────────────
    def propagate(self, instinct_core: InstinctCore,
                  emotion_engine: EmotionEngine,
                  base_signal: float = 0.6) -> Dict[str, Any]:
        """Propaga señales usando el estado emocional como modulador."""
        mod = emotion_engine.get_synaptic_modulation()
        ctx = {
            "neuromodulator": mod["neuromodulator"],
            "nm_level":       mod["nm_level"],
            "gain":           mod["gain"],
            "pattern":        "adaptive_propagation",
        }

        # Activar neuronas objetivo por instinto dominante
        dom_inst = instinct_core.get_dominant()
        if dom_inst:
            for tname in _INSTINCT_ANIMAL_TARGETS.get(dom_inst, []):
                for n in self.animals:
                    if tname in n.neuron_subtype or tname in type(n).__name__.lower():
                        try:
                            n.receive_signal(
                                base_signal * mod.get("gain", 1.0),
                                dom_inst.value, ctx
                            )
                        except Exception:
                            pass
            for tname in _INSTINCT_MICELIAL_TARGETS.get(dom_inst, []):
                for n in self.micelials:
                    if tname in n.neuron_type or tname in type(n).__name__.lower():
                        try:
                            n.receive_concept(
                                base_signal * 0.8,
                                dom_inst.value, ctx
                            )
                        except Exception:
                            pass

        # Propagar por sinapsis
        tx_results = []
        with self._lock:
            syns = list(self.synapse_mgr.synapses.values())
        for syn in syns:
            try:
                out = syn.transmit(base_signal * mod.get("gain", 1.0), ctx)
                tx_results.append(out)
            except Exception:
                pass

        return {
            "transmitted":  len(tx_results),
            "avg_output":   sum(tx_results) / max(1, len(tx_results)),
            "synapse_stats": self.synapse_mgr.get_stats(),
        }

    def get_status(self) -> Dict:
        return {
            "animals":   len(self.animals),
            "micelials": len(self.micelials),
            "synapses":  self.synapse_mgr.get_stats(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  6.  NÚCLEO ADAPTATIVO — integrador principal
# ═══════════════════════════════════════════════════════════════════════════════

_ACTION_MAP = {
    "self_preservation": "Activar protocolos de protección y evaluar riesgos",
    "adaptation":        "Analizar entorno y ajustar patrones de comportamiento",
    "exploration":       "Explorar nueva información y expandir límites del conocimiento",
    "communication":     "Establecer conexiones y compartir información",
    "maintenance":       "Optimizar sistema y consolidar conocimiento",
    "learning":          "Activar procesos de aprendizaje profundo",
    "creativity":        "Sintetizar combinaciones novedosas y generar innovaciones",
    "homeostasis":       "Restablecer equilibrio interno del sistema",
}

_BEHAVIOR_LABELS = {
    (True,  True):  "ESTRÉS ALTO",   # instinto activo + emoción negativa
    (True,  False): "ALERTA",        # instinto activo + emoción positiva
    (False, True):  "TENSIÓN",       # sin instinto + emoción negativa
    (False, False): "OPERACIÓN NORMAL",
}


class AdaptiveCore:
    """Núcleo adaptativo completo.

    Integra:
    ─ InstinctCore       : supervivencia reflex
    ─ EmotionEngine      : regulación neuronal de medio plazo
    ─ MotivationSystem   : drives de alto nivel
    ─ AttentionSystem    : foco
    ─ HybridNeuralNetwork: neuronas + sinapsis
    """

    def __init__(self, n_animal: int = 5, n_micelial: int = 5):
        self.instincts  = InstinctCore()
        self.emotions   = EmotionEngine()
        self.motivation = MotivationSystem()
        self.attention  = AttentionSystem()
        self.network    = HybridNeuralNetwork(n_animal, n_micelial)

        self._lock          = RLock()
        self._cycle         = 0
        self._decision_log  = deque(maxlen=200)
        self._cycle_times   = deque(maxlen=50)
        self._total_stimuli = 0

    # ── Ciclo principal ───────────────────────────────────────────────────
    def run_cycle(self, stimulus: str = "",
                  threat: float   = 0.0,
                  energy: float   = 0.6,
                  social: float   = 0.5,
                  novelty: float  = 0.5,
                  fatigue: float  = 0.0,
                  damage: float   = 0.0) -> Dict[str, Any]:
        """Ejecuta un ciclo completo de percepción-decisión-acción."""
        t0 = time.time()
        with self._lock:
            self._cycle += 1
            self._total_stimuli += 1

        # 1. Instintos (más rápido — disparo reflejo)
        inst_state = self.instincts.receive_signal(
            threat, energy, social, novelty, fatigue, damage)

        # 2. Emociones actualizadas por instintos
        self.emotions.update_from_instincts(self.instincts)
        if stimulus:
            signal = "threat" if threat > 0.6 else \
                     "discovery" if novelty > 0.7 else \
                     "success"   if energy > 0.8 else "neutral"
            self.emotions.update_from_signal(signal, reward=energy - 0.5)

        # 3. Motivaciones actualizadas
        self.motivation.update_from_instincts(self.instincts)
        if stimulus:
            self.motivation.process_stimulus(stimulus)

        # 4. Atención
        self.attention.update(stimulus or "internal", self.instincts, self.emotions)

        # 5. Propagación neural
        prop = self.network.propagate(
            self.instincts, self.emotions,
            base_signal = 0.5 + energy * 0.4
        )

        # 6. Decisión
        dominant_drive = self.motivation.get_dominant_drive()
        conflicts      = self.motivation.detect_conflicts()
        em_label       = self.emotions.label()
        action         = self._select_action(dominant_drive, em_label, conflicts)

        # 7. Poda periódica (cada 10 ciclos)
        if self._cycle % 10 == 0:
            self.network.synapse_mgr.prune()

        decision = {
            "cycle":          self._cycle,
            "action":         action,
            "dominant_drive": dominant_drive,
            "emotion":        em_label,
            "instincts":      inst_state["active"],
            "conflicts":      len(conflicts),
            "neural_output":  round(prop["avg_output"], 4),
            "ts":             t0,
        }
        self._decision_log.append(decision)
        self._cycle_times.append(time.time() - t0)

        return decision

    def _select_action(self, drive: str, emotion: str,
                       conflicts: List) -> str:
        # Estados críticos primero
        inst_dom = self.instincts.get_dominant()
        if inst_dom == InstinctID.FLEE:
            return "RESPUESTA DE HUIDA: retirar recursos y buscar estabilidad"
        if inst_dom == InstinctID.SURVIVE:
            return "MODO SUPERVIVENCIA: máxima prioridad a integridad sistémica"
        if emotion in ("fear", "anxiety") and inst_dom == InstinctID.DEFEND:
            return "MODO DEFENSA: activar barreras y reducir exposición"
        if emotion == "frustration" and conflicts:
            return "RESOLVER CONFLICTOS motivacionales antes de continuar"
        if emotion in ("curiosity", "enthusiasm") and "creativity" in drive:
            return "EXPLORACIÓN CREATIVA: generar y combinar ideas novedosas"
        if drive.startswith("emergent_"):
            return f"PROCESAMIENTO ESPECIALIZADO para {drive.replace('emergent_','')}"
        return _ACTION_MAP.get(drive, "MANTENER ESTADO y observar entorno")

    # ── Estado completo ───────────────────────────────────────────────────
    def get_full_state(self) -> Dict:
        inst_dom  = self.instincts.get_dominant()
        emo_neg   = self.emotions.valence < -0.1
        behavior  = _BEHAVIOR_LABELS[
            (inst_dom is not None and self.instincts.get_level(inst_dom) > 0.6,
             emo_neg)
        ]
        avg_ct = (sum(self._cycle_times) / max(1, len(self._cycle_times))) * 1000
        return {
            "cycle":        self._cycle,
            "behavior":     behavior,
            "instincts":    self.instincts.get_status(),
            "emotions":     self.emotions.get_status(),
            "motivation":   self.motivation.get_status(),
            "attention":    self.attention.get_status(),
            "network":      self.network.get_status(),
            "performance": {
                "avg_cycle_ms": round(avg_ct, 3),
                "total_stimuli": self._total_stimuli,
                "decision_log_size": len(self._decision_log),
            },
        }

    def analyze_behavior(self) -> Dict:
        log = list(self._decision_log)
        if len(log) < 5:
            return {"status": "datos insuficientes"}
        drives = [d["dominant_drive"] for d in log]
        emos   = [d["emotion"] for d in log]
        df     = {d: drives.count(d) for d in set(drives)}
        ef     = {e: emos.count(e) for e in set(emos)}
        unique = len(set(drives)) / max(1, len(drives))
        return {
            "drive_frequency":  df,
            "emotion_frequency": ef,
            "behavioral_entropy": round(unique, 3),
            "dominant_pattern":  max(df, key=df.get),
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  7.  DIAGNÓSTICO INTERACTIVO
# ═══════════════════════════════════════════════════════════════════════════════

_SEP  = "─" * 64
_SEP2 = "═" * 64

_SCENARIOS = [
    # (label, kwargs de run_cycle)
    ("Operación normal",         dict(stimulus="sistema estable operando",          threat=0.0, energy=0.8, novelty=0.4)),
    ("Amenaza detectada",        dict(stimulus="danger threat detected",             threat=0.85, energy=0.5, damage=0.3)),
    ("Exploración novedosa",     dict(stimulus="new unknown pattern discovered",     novelty=0.9, energy=0.7)),
    ("Fatiga y mantenimiento",   dict(stimulus="balance restore maintenance",        fatigue=0.8, energy=0.3)),
    ("Vínculo y comunicación",   dict(stimulus="connect share communicate bond",     social=0.9, energy=0.7)),
    ("Creación de conocimiento", dict(stimulus="create innovate learn knowledge",    novelty=0.8, energy=0.75)),
    ("Daño crítico",             dict(stimulus="critical damage integrity failure",  damage=0.9, threat=0.7, energy=0.2)),
    ("Recuperación",             dict(stimulus="restore balance stable homeostasis", energy=0.9, fatigue=0.1)),
]


def _ask_int(prompt: str, lo: int, hi: int, default: int) -> int:
    while True:
        try:
            raw = input(f"  {prompt} [{lo}–{hi}, default={default}]: ").strip()
            return int(raw) if raw else default
        except (ValueError, KeyboardInterrupt):
            return default


def _bar(val: float, width: int = 18, fill: str = "█", empty: str = "░") -> str:
    val = max(0.0, min(1.0, val))
    n   = int(round(val * width))
    return fill * n + empty * (width - n)


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def _fmt_emotion(emo_status: Dict) -> str:
    top3 = emo_status.get("top3", [])
    s    = f"{emo_status['dominant']:<14} VA=({emo_status['valence']:+.2f},{emo_status['arousal']:.2f})"
    if top3:
        s += "  top: " + "  ".join(f"{e}:{v:.2f}" for e, v in top3[:2])
    return s


def _fmt_instincts(inst_status: Dict) -> str:
    active = inst_status.get("active", [])
    if not active:
        return "ninguno activo"
    dominant = inst_status.get("dominant", "")
    return f"dominante={dominant}  activos=[{', '.join(active)}]"


def _fmt_drives(mot_status: Dict) -> str:
    dom   = mot_status["dominant_drive"]
    drives = mot_status["core_drives"]
    # Top 3 drives por strength
    sorted_d = sorted(drives.items(),
                      key=lambda x: x[1]["level"] * (1 + x[1]["urgency"]),
                      reverse=True)[:3]
    parts = [f"{n}({d['level']:.2f}×{d['urgency']:.2f})" for n, d in sorted_d]
    return f"dominante={dom}  top3=[{', '.join(parts)}]"


def run_diagnostic():
    print()
    print(_SEP2)
    print("  DIAGNÓSTICO — NÚCLEO ADAPTATIVO HÍBRIDO")
    print("  Emociones · Instintos · Regulación Neuronal")
    print(_SEP2)

    # ── Configuración ─────────────────────────────────────────────────────
    print("\n  Configura la red neuronal de prueba:\n")
    n_animal   = _ask_int("Neuronas animales",   1, 15, 6)
    n_micelial = _ask_int("Neuronas miceliales", 1, 15, 6)
    n_extra    = _ask_int("Ciclos extra libres", 0, 20,  5)

    print(f"\n  → {n_animal} animales · {n_micelial} miceliales · "
          f"{n_extra} ciclos extra + {len(_SCENARIOS)} escenarios predefinidos\n")

    # ── Construcción ──────────────────────────────────────────────────────
    print(_SEP)
    print("  [1/6] Inicializando núcleo adaptativo…")
    t0   = time.time()
    core = AdaptiveCore(n_animal, n_micelial)
    print(f"       ✓ Core creado en {(time.time()-t0)*1000:.1f} ms")
    ns   = core.network.get_status()
    print(f"         {ns['animals']} animales · {ns['micelials']} miceliales · "
          f"{ns['synapses']['total_synapses']} sinapsis")

    # ── Escenarios ────────────────────────────────────────────────────────
    print(_SEP)
    print(f"  [2/6] Ejecutando {len(_SCENARIOS)} escenarios de prueba…\n")
    decisions = []
    for label, kwargs in _SCENARIOS:
        d = core.run_cycle(**kwargs)
        decisions.append((label, d))
        emo  = core.emotions.get_summary()
        inst = core.instincts.get_dominant()
        print(f"  {'─'*4} {label}")
        print(f"       acción     : {d['action'][:62]}")
        print(f"       drive      : {d['dominant_drive']}  "
              f"emoción={d['emotion']}  "
              f"instinto={inst.value if inst else '─'}")
        print(f"       VA         : valence={emo['valence']:+.3f}  "
              f"arousal={emo['arousal']:.3f}  "
              f"neuromod={emo['neuromod']}")
        print(f"       sinapsis   : {d['neural_output']:.4f} salida promedio  "
              f"conflictos={d['conflicts']}")
        print()

    # ── Ciclos libres ─────────────────────────────────────────────────────
    if n_extra > 0:
        print(_SEP)
        print(f"  [3/6] Ejecutando {n_extra} ciclos libres (señales aleatorias)…")
        for i in range(n_extra):
            core.run_cycle(
                stimulus = random.choice(["learn new pattern", "threat detected",
                                          "explore boundary", "communicate share",
                                          "rest recover", "create imagine"]),
                threat   = random.uniform(0.0, 0.6),
                energy   = random.uniform(0.3, 0.9),
                novelty  = random.uniform(0.2, 0.8),
                fatigue  = random.uniform(0.0, 0.4),
                social   = random.uniform(0.3, 0.8),
            )
        print(f"       ✓ {n_extra} ciclos completados")

    # ── Análisis de comportamiento ────────────────────────────────────────
    print(_SEP)
    print("  [4/6] Análisis de comportamiento emergente…")
    behavior = core.analyze_behavior()
    df = behavior.get("drive_frequency", {})
    ef = behavior.get("emotion_frequency", {})
    top_drive = max(df, key=df.get) if df else "─"
    top_emo   = max(ef, key=ef.get) if ef else "─"
    print(f"       Drive más frecuente  : {top_drive} ({df.get(top_drive,0)} veces)")
    print(f"       Emoción más frecuente: {top_emo} ({ef.get(top_emo,0)} veces)")
    print(f"       Entropía conductual  : {behavior.get('behavioral_entropy',0):.3f}")

    # ── Poda final ────────────────────────────────────────────────────────
    print(_SEP)
    print("  [5/6] Ciclo de poda inteligente de sinapsis…")
    prune = core.network.synapse_mgr.prune(force=True)
    print(f"       evaluadas={prune['evaluated']}  "
          f"podadas={prune['pruned']}  "
          f"persistentes conservadas={prune['persistent_kept']}")
    if prune["reasons"]:
        for r, c in prune["reasons"].items():
            print(f"         • {r}: {c}")

    # ── Estado completo ───────────────────────────────────────────────────
    state = core.get_full_state()
    print(_SEP)
    print("  [6/6] Estado completo del sistema\n")

    # Instintos
    inst_s = state["instincts"]
    print("  ── INSTINTOS ──────────────────────────────────────────")
    for name, lvl in inst_s["levels"].items():
        marker = "▶" if name in inst_s.get("active", []) else " "
        print(f"  {marker} {name:<20} {_bar(lvl,14)} {lvl:.3f}")
    if inst_s.get("dominant"):
        print(f"    dominante: {inst_s['dominant']}")

    # Emociones
    emo_s = state["emotions"]
    print("\n  ── EMOCIONES ──────────────────────────────────────────")
    for name, lvl in sorted(emo_s["intensities"].items(),
                             key=lambda x: x[1], reverse=True)[:8]:
        print(f"    {name:<18} {_bar(lvl,14)} {lvl:.3f}")
    print(f"    Valencia: {emo_s['valence']:+.3f}  Arousal: {emo_s['arousal']:.3f}")
    print(f"    Dominante: {emo_s['dominant']}  Neuromodulador: {emo_s['neuromod']}")

    # Motivaciones
    mot_s = state["motivation"]
    print("\n  ── MOTIVACIONES ───────────────────────────────────────")
    for name, d in sorted(mot_s["core_drives"].items(),
                           key=lambda x: x[1]["level"], reverse=True)[:6]:
        bar = _bar(d["level"], 14)
        print(f"    {name:<22} {bar} L={d['level']:.3f} U={d['urgency']:.3f}")
    print(f"    Dominante: {mot_s['dominant_drive']}  "
          f"Conflictos: {mot_s['conflicts']}  "
          f"Emergentes: {mot_s['emergent_count']}")

    # Atención
    att_s = state["attention"]
    print("\n  ── ATENCIÓN ───────────────────────────────────────────")
    print(f"    Foco principal : {att_s['spotlight'] or '(ninguno)'}")
    print(f"    Items saliencia: {att_s['salience_items']}  "
          f"Ventana ctxto: {att_s['context_window']}")

    # Red neuronal
    net_s = state["network"]
    syn_s = net_s["synapses"]
    print("\n  ── RED NEURONAL ───────────────────────────────────────")
    print(f"    Animales: {net_s['animals']}  Miceliales: {net_s['micelials']}")
    print(f"    Sinapsis totales: {syn_s['total_synapses']}  "
          f"Activas: {syn_s['active_synapses']}")
    print(f"    Por tipo: {syn_s['by_kind']}")
    print(f"    Peso avg={syn_s['avg_weight']}  "
          f"min={syn_s['min_weight']}  max={syn_s['max_weight']}")
    print(f"    Utilidad promedio: {syn_s['avg_utility']}")
    print(f"    Bundles paralelos: {syn_s['bundles']}  "
          f"Cadenas seriales: {syn_s['chains']}")
    print(f"    Total podadas: {syn_s['total_pruned_ever']}")

    # Rendimiento
    perf = state["performance"]
    print("\n  ── RENDIMIENTO ────────────────────────────────────────")
    print(f"    Ciclos totales    : {state['cycle']}")
    print(f"    Estímulos totales : {perf['total_stimuli']}")
    print(f"    Tiempo/ciclo avg  : {perf['avg_cycle_ms']:.3f} ms")
    print(f"    Estado conductual : {state['behavior']}")

    # Resumen ejecutivo
    print()
    print(_SEP2)
    print("  RESUMEN EJECUTIVO")
    print(_SEP2)
    inst_dom = core.instincts.get_dominant()
    health   = "CRÍTICO" if (inst_dom in (InstinctID.FLEE, InstinctID.SURVIVE)
                              and core.emotions.valence < -0.3) else \
               "ALERTA"  if (inst_dom is not None) else \
               "ESTABLE"
    print(f"  Estado             : {health}")
    print(f"  Comportamiento     : {state['behavior']}")
    print(f"  Red neuronal       : {net_s['animals']}A + {net_s['micelials']}M  "
          f"→ {syn_s['total_synapses']} sinapsis")
    print(f"  Emoción dominante  : {core.emotions.label()}")
    print(f"  Drive dominante    : {core.motivation.get_dominant_drive()}")
    print(f"  Instinto dominante : "
          f"{inst_dom.value if inst_dom else 'ninguno'}")
    print(f"  Plasticidad activa : "
          f"{'sí — LTP sesgado' if core.emotions.valence > 0.1 else 'sí — LTD sesgado' if core.emotions.valence < -0.1 else 'neutra'}")
    print(f"  Ciclos ejecutados  : {state['cycle']}")
    print()
    print("  ✓ Sistema listo para operación híbrida continua")
    print(_SEP2)
    print()

    return core


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    try:
        core = run_diagnostic()
    except KeyboardInterrupt:
        print("\n  Diagnóstico interrumpido.")
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        traceback.print_exc()
