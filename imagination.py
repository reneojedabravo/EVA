# imagination.py
"""
Sistema de Imaginación Cognitiva — Motor de Escenarios Mentales.

La imaginación no es decorativa. Es el proceso por el que la mente
combina fragmentos de experiencia para generar lo que aún no existe:
proyecciones, síntesis, analogías, resolución de tensiones, exploración
de lo desconocido.

Principios de diseño:
  ─ La imaginación es impulsada por necesidad, no por tiempo.
    Se activa cuando hay tensión creativa, curiosidad instintiva,
    conflicto emocional, o silencio que pide exploración.
  ─ Las representaciones mentales son fragmentos vivos: tienen valencia
    emocional, novedad, certeza y nivel de activación. Compiten entre sí
    por el espacio limitado de la memoria de trabajo imaginativa (máx 7).
  ─ Los escenarios nacen de combinar representaciones activas con
    resonancias de memoria emocional.
  ─ Un insight es un patrón que emerge cuando varias representaciones
    apuntan en la misma dirección sin haberlo planificado.
  ─ Los resultados valiosos se consolidan en memoria. Los efímeros
    se disuelven sin dejar rastro (o casi).

Integración:
  ─ Neuronas animales + miceliales por fase (ScenarioEngine usa red propia)
  ─ SynapseManager para conexiones entre representaciones vía neuronas
  ─ adaptive.py — emociones e instintos modulan qué se imagina y cómo
  ─ memory.py + memory_persistence.py — semillas desde memoria, resultados guardados
  ─ background_thinking.py — puede inyectar disparadores de imaginación
  ─ mind.py — los insights pueden percibirse por la FluidMind

Diagnóstico interactivo al ejecutar directamente.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import re
import time
import traceback
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

# ── Ecosistema neuronal ───────────────────────────────────────────────────────
from monitoring import log_event, log_neuron_error
from animal    import create_cognitive_animal_neuron,   CognitiveAnimalNeuronBase
from micelial  import create_cognitive_micelial_neuron, CognitiveMicelialNeuronBase
from synapse   import SynapseManager
from adaptive  import AdaptiveCore, EmotionEngine, InstinctCore, InstinctID
from memory    import (MemoryManager, EmotionalStamp, MemoryLayer,
                        Fragment, _build_demo_memory)
from memory_persistence import MemoryPersistence


# ═══════════════════════════════════════════════════════════════════════════════
#  TIPOS DE ESCENARIO
# ═══════════════════════════════════════════════════════════════════════════════

class ScenarioType(Enum):
    FUTURE_PROJECTION  = "future_projection"   # ¿qué pasaría si…?
    COUNTERFACTUAL     = "counterfactual"       # ¿y si nunca hubiera…?
    SYNTHESIS          = "synthesis"            # combinar dos cosas
    CONFLICT_RESOLUTION= "conflict_resolution" # resolver tensión
    ANALOGY            = "analogy"              # A es como B en que…
    CAUSALITY          = "causality"            # si X entonces Y porque…
    EXPLORATION        = "exploration"          # qué hay más allá de…
    INTEGRATION        = "integration"          # conectando X con Y veo…
    DREAM              = "dream"                # asociación libre profunda


# Neuromodulador preferido por cada tipo
_SCENARIO_NEUROMOD = {
    ScenarioType.FUTURE_PROJECTION:   "dopamine",
    ScenarioType.COUNTERFACTUAL:      "acetylcholine",
    ScenarioType.SYNTHESIS:           "dopamine",
    ScenarioType.CONFLICT_RESOLUTION: "serotonin",
    ScenarioType.ANALOGY:             "acetylcholine",
    ScenarioType.CAUSALITY:           "acetylcholine",
    ScenarioType.EXPLORATION:         "dopamine",
    ScenarioType.INTEGRATION:         "serotonin",
    ScenarioType.DREAM:               "norepinephrine",
}

# Plantillas de escenario
_TEMPLATES = {
    ScenarioType.FUTURE_PROJECTION:
        "¿Qué pasaría si {concept1} evolucionara hacia {concept2}?",
    ScenarioType.COUNTERFACTUAL:
        "¿Y si {concept1} nunca hubiera ocurrido? ¿Cómo sería {concept2}?",
    ScenarioType.SYNTHESIS:
        "Si combino {concept1} con {concept2} podría obtener {synthesis}.",
    ScenarioType.CONFLICT_RESOLUTION:
        "Para resolver la tensión entre {concept1} y {concept2} podría {solution}.",
    ScenarioType.ANALOGY:
        "{concept1} es como {concept2} en que ambos {similarity}.",
    ScenarioType.CAUSALITY:
        "Si {concept1} entonces {concept2}, porque {reasoning}.",
    ScenarioType.EXPLORATION:
        "Me pregunto qué hay más allá de {concept1}. Tal vez {speculation}.",
    ScenarioType.INTEGRATION:
        "Conectando {concept1} y {concept2} veo que {insight}.",
    ScenarioType.DREAM:
        "{concept1} se disuelve en {concept2}… {speculation}.",
}


# ═══════════════════════════════════════════════════════════════════════════════
#  REPRESENTACIÓN MENTAL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MentalRepresentation:
    """Unidad mínima de imaginación: un concepto con propiedades vivas."""
    repr_id:          str
    content:          str
    tags:             List[str]
    valence:          float        # −1…+1 carga emocional
    arousal:          float        # 0…1 intensidad
    certainty:        float        # 0…1
    complexity:       float        # 0…1
    novelty:          float        # 0…1
    activation:       float        # nivel de activación actual
    source_fids:      List[str]    # FIDs de memoria que la originaron
    instinct_tags:    List[str]    = field(default_factory=list)
    connections:      List[str]    = field(default_factory=list)  # repr_ids
    creation_ts:      float        = field(default_factory=time.time)
    last_activated:   float        = field(default_factory=time.time)

    def emotional_stamp(self) -> EmotionalStamp:
        return EmotionalStamp(
            valence=self.valence,
            arousal=self.arousal,
            instinct_tags=self.instinct_tags,
        )

    def salience(self) -> float:
        """Saliencia combinada: activación + emoción + novedad."""
        return (self.activation * 0.4 +
                abs(self.valence) * self.arousal * 0.35 +
                self.novelty * 0.25)

    def associative_strength(self, other: "MentalRepresentation") -> float:
        """Fuerza de asociación con otra representación."""
        tag_sim = (len(set(self.tags) & set(other.tags)) /
                   max(1, len(set(self.tags) | set(other.tags))))
        emo_sim = (self.emotional_stamp()
                   .resonance_with(other.emotional_stamp()))
        return tag_sim * 0.55 + emo_sim * 0.45

    def decay(self, rate: float = 0.04):
        self.activation = max(0.0, self.activation * (1.0 - rate))

    def to_dict(self) -> Dict:
        return {
            "repr_id":       self.repr_id,
            "content":       self.content,
            "tags":          self.tags,
            "valence":       round(self.valence, 4),
            "arousal":       round(self.arousal, 4),
            "certainty":     round(self.certainty, 4),
            "complexity":    round(self.complexity, 4),
            "novelty":       round(self.novelty, 4),
            "activation":    round(self.activation, 4),
            "source_fids":   self.source_fids,
            "instinct_tags": self.instinct_tags,
            "connections":   self.connections,
            "creation_ts":   self.creation_ts,
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  INSIGHT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Insight:
    """Patrón emergente que surge de múltiples representaciones activas."""
    insight_id:      str
    content:         str
    insight_type:    str   # emotional | thematic | causal | neural | combinatory
    source_repr_ids: List[str]
    valence:         float
    confidence:      float
    novelty:         float
    neural_signature: float   # activación promedio que lo generó
    creation_ts:     float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        return {
            "insight_id":      self.insight_id,
            "content":         self.content,
            "insight_type":    self.insight_type,
            "source_repr_ids": self.source_repr_ids,
            "valence":         round(self.valence, 4),
            "confidence":      round(self.confidence, 4),
            "novelty":         round(self.novelty, 4),
            "neural_signature":round(self.neural_signature, 4),
            "creation_ts":     self.creation_ts,
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  ESCENARIO
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Scenario:
    """Un escenario mental generado por el motor de imaginación."""
    scenario_id:   str
    scenario_type: ScenarioType
    content:       str
    repr_ids:      List[str]
    valence:       float
    complexity:    float
    novelty:       float
    confidence:    float
    neural_act:    float    # activación neural promedio durante generación
    creation_ts:   float = field(default_factory=time.time)
    insight:       Optional[Insight] = None

    def to_dict(self) -> Dict:
        d = {
            "scenario_id":   self.scenario_id,
            "scenario_type": self.scenario_type.value,
            "content":       self.content,
            "repr_ids":      self.repr_ids,
            "valence":       round(self.valence, 4),
            "complexity":    round(self.complexity, 4),
            "novelty":       round(self.novelty, 4),
            "confidence":    round(self.confidence, 4),
            "neural_act":    round(self.neural_act, 4),
            "creation_ts":   self.creation_ts,
        }
        if self.insight:
            d["insight"] = self.insight.to_dict()
        return d


# ═══════════════════════════════════════════════════════════════════════════════
#  RED NEURONAL DE IMAGINACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

# Neuronas animales: procesamiento rápido, sensorial, decisional
_IMAG_ANIMAL = [
    ("visual_feature_extractor",  {"feature_type": "shape"}),
    ("anomaly_detector",          {}),
    ("associative_memory_cell",   {}),
    ("decision_maker",            {}),
    ("dopaminergic_modulator",    {}),
    ("mirror_neuron",             {"action_class": "imagine"}),
    ("adaptive_threshold_cell",   {}),
    ("place_cell",                {"preferred_location": (0.5, 0.5)}),
    ("speed_neuron",              {}),
    ("self_monitor",              {}),
]

# Neuronas miceliales: integración conceptual, síntesis profunda
_IMAG_MICELIAL = [
    ("abstract_pattern_integrator",    {}),
    ("conceptual_bridge_builder",      {}),
    ("insight_propagator",             {}),
    ("knowledge_synthesizer",          {"domain_specializations": ["imagination","creativity"]}),
    ("deep_reflection_orchestrator",   {}),
    ("anastomosis_node",               {}),
    ("plasmodium_collector",           {}),
    ("global_coherence_coordinator",   {}),
    ("quorum_sensing_node",            {}),
    ("glycolytic_oscillator",          {}),
]


class ImaginationNetwork:
    """Red neuronal dedicada a la generación imaginativa.

    Tiene dos subsistemas:
    ─ SEED net   (animales):  activa fast-thinking, detecta patrones
    ─ EXPAND net (miceliales): genera síntesis lentas y profundas
    ─ Sinapsis híbridas conectan ambos subsistemas
    """

    def __init__(self, synapse_mgr: SynapseManager,
                 n_animal: int = 5, n_micelial: int = 5):
        self.syn_mgr   = synapse_mgr
        self.animals:  List[CognitiveAnimalNeuronBase]   = []
        self.micelials:List[CognitiveMicelialNeuronBase] = []
        self._lock     = RLock()
        self._build(min(n_animal,  len(_IMAG_ANIMAL)),
                    min(n_micelial, len(_IMAG_MICELIAL)))

    def _build(self, na: int, nm: int):
        for i in range(na):
            ntype, kwargs = _IMAG_ANIMAL[i]
            nid = f"IMA{i+1:02d}_{ntype[:8]}"
            try:
                n = create_cognitive_animal_neuron(ntype, nid, **kwargs)
                self.animals.append(n)
            except Exception as e:
                log_neuron_error(nid, f"ImaginationNetwork animal: {e}")

        for i in range(nm):
            ntype, kwargs = _IMAG_MICELIAL[i]
            nid = f"IMM{i+1:02d}_{ntype[:8]}"
            try:
                n = create_cognitive_micelial_neuron(ntype, nid, **kwargs)
                self.micelials.append(n)
            except Exception as e:
                log_neuron_error(nid, f"ImaginationNetwork micelial: {e}")

        # Conexiones internas animales (serial)
        for i in range(len(self.animals) - 1):
            self.syn_mgr.connect(self.animals[i], self.animals[i+1],
                                 "electrical", "excitatory", persistent=True)
        # Conexiones internas miceliales (serial)
        for i in range(len(self.micelials) - 1):
            self.syn_mgr.connect(self.micelials[i], self.micelials[i+1],
                                 "chemical", "excitatory", persistent=True)
        # Conexiones cruzadas híbridas
        n_cross = min(4, len(self.animals), len(self.micelials))
        for i in range(n_cross):
            self.syn_mgr.connect(self.animals[i], self.micelials[i],
                                 "hybrid", "excitatory", persistent=True)
            self.syn_mgr.connect(self.micelials[i], self.animals[i],
                                 "hybrid", "modulatory", persistent=False)
        # Bundle de síntesis creativa (animales → primer micelial)
        if len(self.animals) >= 3 and self.micelials:
            self.syn_mgr.create_parallel_bundle(
                self.animals[:3], self.micelials[0], "hybrid")
        # Cadena de expansión conceptual
        if len(self.animals) >= 2 and self.micelials:
            self.syn_mgr.create_serial_chain(
                [self.animals[0], self.animals[1], self.micelials[0]])

    def activate_seed(self, signal: float, context: Dict) -> float:
        """Activa la red seed (animales) para fase inicial."""
        acts = []
        for n in self.animals:
            try:
                act = n.receive_signal(signal, context.get("seed","imagine"), context)
                if act:
                    acts.append(float(act))
            except Exception:
                pass
        return sum(acts) / max(1, len(acts)) if acts else 0.0

    def activate_expansion(self, signal: float, context: Dict) -> float:
        """Activa la red de expansión (miceliales) para síntesis profunda."""
        acts = []
        concept = context.get("concept1", "concepto")
        for n in self.micelials:
            try:
                act = n.receive_concept(signal, concept, context)
                if act:
                    acts.append(float(act))
            except Exception:
                pass
        return sum(acts) / max(1, len(acts)) if acts else 0.0

    def propagate_synapses(self, signal: float, context: Dict) -> int:
        """Propaga señal por todas las sinapsis."""
        count = 0
        for syn in list(self.syn_mgr.synapses.values()):
            try:
                out = syn.transmit(signal, context)
                if out and out > 0.01:
                    count += 1
            except Exception:
                pass
        return count

    def full_activation(self, signal: float, context: Dict) -> Tuple[float, float, int]:
        """Activa toda la red. Retorna (seed_avg, expand_avg, synapse_tx)."""
        seed   = self.activate_seed(signal, context)
        expand = self.activate_expansion(signal, context)
        tx     = self.propagate_synapses(signal, context)
        return seed, expand, tx

    def get_status(self) -> Dict:
        syn_s = self.syn_mgr.get_stats()
        return {
            "animals":        len(self.animals),
            "micelials":      len(self.micelials),
            "total_synapses": syn_s["total_synapses"],
            "active_synapses":syn_s["active_synapses"],
            "by_kind":        syn_s["by_kind"],
            "avg_weight":     syn_s["avg_weight"],
            "avg_utility":    syn_s["avg_utility"],
        }

    def neuron_states(self) -> List[Dict]:
        rows = []
        for n in self.animals:
            rows.append({
                "id":      n.neuron_id,
                "domain":  "animal",
                "subtype": getattr(n, "neuron_subtype", type(n).__name__)[:20],
                "act":     round(getattr(n, "activation_level", 0.0), 4),
                "resil":   round(getattr(n, "cognitive_resilience", 1.0), 3),
                "plastic": round(getattr(n, "plasticity_score", 0.5), 3),
            })
        for n in self.micelials:
            rows.append({
                "id":      n.neuron_id,
                "domain":  "micelial",
                "subtype": type(n).__name__[:20],
                "act":     round(getattr(n, "activation_level", 0.0), 4),
                "resil":   round(getattr(n, "cognitive_resilience", 1.0), 3),
                "plastic": round(getattr(n, "plasticity",
                           getattr(n, "plasticity_score", 0.5)), 3),
            })
        return rows

    def synapse_states(self) -> List[Dict]:
        return self.syn_mgr.list_synapses()


# ═══════════════════════════════════════════════════════════════════════════════
#  MOTOR DE ESCENARIOS
# ═══════════════════════════════════════════════════════════════════════════════

class ScenarioEngine:
    """Genera escenarios mentales combinando representaciones activas."""

    def __init__(self):
        self._lock  = RLock()
        self._count = 0

    def generate(self, reprs: List[MentalRepresentation],
                 scenario_type: Optional[ScenarioType],
                 neural_act: float,
                 emotion: EmotionEngine) -> Optional[Scenario]:
        """Genera un escenario a partir de representaciones y estado emocional."""
        if not reprs:
            return None
        with self._lock:
            self._count += 1

        # Seleccionar tipo si no viene dado
        if scenario_type is None:
            scenario_type = self._select_type(reprs, emotion)

        # Obtener conceptos
        c1 = reprs[0].content
        c2 = reprs[1].content if len(reprs) > 1 else self._complement(c1)

        # Generar elementos del template
        fills = {
            "concept1":    c1,
            "concept2":    c2,
            "synthesis":   self._synthesis(c1, c2),
            "solution":    self._solution(c1, c2),
            "similarity":  self._similarity(c1, c2),
            "reasoning":   self._reasoning(c1, c2),
            "speculation": self._speculation(c1),
            "insight":     self._insight_phrase(c1, c2),
        }

        template = _TEMPLATES.get(scenario_type,
                                   "Explorando {concept1} y {concept2}.")
        try:
            content = template.format(**fills)
        except KeyError:
            content = f"Explorando la relación entre '{c1}' y '{c2}'."

        # Calcular propiedades
        avg_valence = sum(r.valence for r in reprs) / len(reprs)
        avg_complex = min(1.0, sum(r.complexity for r in reprs) / len(reprs)
                          + len(reprs) * 0.05)
        avg_novelty = sum(r.novelty for r in reprs) / len(reprs)
        avg_cert    = sum(r.certainty for r in reprs) / len(reprs)

        # Modular por emoción
        avg_valence = (avg_valence * 0.7 +
                       emotion.valence * 0.3)
        avg_novelty = min(1.0, avg_novelty + emotion.arousal * 0.1)

        sid = hashlib.md5(
            f"{c1}{c2}{time.time()}".encode()).hexdigest()[:12]

        return Scenario(
            scenario_id   = sid,
            scenario_type = scenario_type,
            content       = content,
            repr_ids      = [r.repr_id for r in reprs],
            valence       = round(avg_valence, 4),
            complexity    = round(avg_complex, 4),
            novelty       = round(avg_novelty, 4),
            confidence    = round(avg_cert, 4),
            neural_act    = round(neural_act, 4),
        )

    def _select_type(self, reprs: List[MentalRepresentation],
                      emotion: EmotionEngine) -> ScenarioType:
        avg_v = sum(r.valence for r in reprs) / len(reprs)
        avg_n = sum(r.novelty for r in reprs) / len(reprs)
        avg_c = sum(r.complexity for r in reprs) / len(reprs)
        # Emociones fuertes negativas → resolver conflicto
        if avg_v < -0.3 or emotion.valence < -0.4:
            return ScenarioType.CONFLICT_RESOLUTION
        # Alta novedad → explorar
        if avg_n > 0.65:
            return ScenarioType.EXPLORATION
        # Alta complejidad → síntesis
        if avg_c > 0.6:
            return ScenarioType.SYNTHESIS
        # Dos reprs con valencias muy distintas → contrafáctico
        if (len(reprs) >= 2 and
                abs(reprs[0].valence - reprs[1].valence) > 0.55):
            return ScenarioType.COUNTERFACTUAL
        # Baja actividad → sueño asociativo
        if emotion.arousal < 0.25:
            return ScenarioType.DREAM
        return random.choice([
            ScenarioType.FUTURE_PROJECTION,
            ScenarioType.ANALOGY,
            ScenarioType.CAUSALITY,
            ScenarioType.INTEGRATION,
        ])

    def _complement(self, concept: str) -> str:
        pairs = {"agua":"tierra","luz":"oscuridad","calor":"frío",
                 "amor":"soledad","conocimiento":"misterio",
                 "tiempo":"espacio","orden":"caos","inicio":"fin"}
        for k, v in pairs.items():
            if k in concept.lower():
                return v
        return "lo desconocido"

    def _synthesis(self, c1: str, c2: str) -> str:
        w1 = re.findall(r'\w+', c1.lower())
        w2 = re.findall(r'\w+', c2.lower())
        if w1 and w2:
            return f"una nueva forma de {w1[0]} que incorpora {w2[0]}"
        return "algo completamente nuevo"

    def _solution(self, c1: str, c2: str) -> str:
        opts = [
            f"encontrar el equilibrio entre {c1} y {c2}",
            f"integrar lo mejor de {c1} con lo esencial de {c2}",
            f"trascender tanto {c1} como {c2}",
            f"alternar entre {c1} y {c2} según el contexto",
        ]
        return random.choice(opts)

    def _similarity(self, c1: str, c2: str) -> str:
        opts = [
            "involucran transformación",
            "requieren atención sostenida",
            "generan impacto emocional",
            "conectan con experiencias pasadas",
            "abren nuevas posibilidades",
        ]
        return random.choice(opts)

    def _reasoning(self, c1: str, c2: str) -> str:
        opts = [
            "comparten patrones subyacentes",
            "influyen en estados emocionales similares",
            "activan redes de memoria análogas",
            "requieren procesos cognitivos paralelos",
        ]
        return random.choice(opts)

    def _speculation(self, concept: str) -> str:
        opts = [
            f"{concept} podría evolucionar hacia formas más complejas",
            f"hay aspectos ocultos de {concept} que aún no comprendo",
            f"{concept} se conecta con patrones más amplios",
            f"la esencia de {concept} trasciende su forma actual",
        ]
        return random.choice(opts)

    def _insight_phrase(self, c1: str, c2: str) -> str:
        opts = [
            "ambos son manifestaciones de un principio más profundo",
            "la tensión entre ellos genera nueva comprensión",
            "juntos revelan algo que por separado permanece oculto",
            "su interacción abre caminos inesperados de crecimiento",
        ]
        return random.choice(opts)


# ═══════════════════════════════════════════════════════════════════════════════
#  DETECTOR DE INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════

class InsightDetector:
    """Detecta patrones emergentes entre representaciones activas."""

    def detect(self, reprs: List[MentalRepresentation],
               neural_act: float,
               scenario: Optional[Scenario] = None) -> Optional[Insight]:
        """Intenta detectar un insight. Retorna None si no hay patrón claro."""
        if len(reprs) < 2:
            return None

        # Patrón emocional
        emo_type, emo_content = self._emotional_pattern(reprs)
        # Patrón temático
        thm_type, thm_content = self._thematic_pattern(reprs)
        # Patrón causal (temporal)
        csl_type, csl_content = self._causal_pattern(reprs)
        # Patrón neural (alta activación sostenida)
        nrl_type, nrl_content = self._neural_pattern(reprs, neural_act)

        # Escoger el patrón más fuerte
        candidates = [(t, c) for t, c in [
            (emo_type, emo_content),
            (thm_type, thm_content),
            (csl_type, csl_content),
            (nrl_type, nrl_content),
        ] if t is not None]

        if not candidates:
            # Insight desde escenario si es muy novel
            if scenario and scenario.novelty > 0.72:
                candidates.append((
                    "scenario_derived",
                    f"Derivado de {scenario.scenario_type.value}: "
                    f"{scenario.content[:80]}…",
                ))

        if not candidates:
            return None

        insight_type, content = candidates[0]
        avg_v    = sum(r.valence for r in reprs) / len(reprs)
        avg_cert = sum(r.certainty for r in reprs) / len(reprs)
        avg_nov  = sum(r.novelty for r in reprs) / len(reprs)
        iid      = hashlib.md5(
            f"{content}{time.time()}".encode()).hexdigest()[:12]

        return Insight(
            insight_id      = iid,
            content         = content,
            insight_type    = insight_type,
            source_repr_ids = [r.repr_id for r in reprs],
            valence         = round(avg_v, 4),
            confidence      = round(min(1.0, avg_cert + neural_act * 0.2), 4),
            novelty         = round(avg_nov, 4),
            neural_signature= round(neural_act, 4),
        )

    def _emotional_pattern(self, reprs: List[MentalRepresentation]
                           ) -> Tuple[Optional[str], str]:
        vs = [r.valence for r in reprs]
        avg = sum(vs) / len(vs)
        var = sum((v - avg)**2 for v in vs) / len(vs)
        if var < 0.08 and avg > 0.35:
            return "emotional", "Convergencia emocional positiva sostenida"
        if var < 0.08 and avg < -0.35:
            return "emotional", "Convergencia emocional negativa: señal de tensión"
        if var > 0.45:
            return "emotional", "Conflicto emocional complejo: polaridad extrema"
        return None, ""

    def _thematic_pattern(self, reprs: List[MentalRepresentation]
                          ) -> Tuple[Optional[str], str]:
        all_words: List[str] = []
        for r in reprs:
            all_words.extend(re.findall(r'\w{4,}', r.content.lower()))
            all_words.extend(t for t in r.tags if len(t) >= 3)
        counts = Counter(all_words)
        common = [w for w, c in counts.most_common(5) if c >= 2]
        if len(common) >= 2:
            theme = ", ".join(common[:3])
            return "thematic", f"Tema recurrente: {theme}"
        return None, ""

    def _causal_pattern(self, reprs: List[MentalRepresentation]
                        ) -> Tuple[Optional[str], str]:
        if len(reprs) < 3:
            return None, ""
        sorted_r = sorted(reprs, key=lambda r: r.creation_ts)
        complexities = [r.complexity for r in sorted_r]
        if all(complexities[i] <= complexities[i+1]
               for i in range(len(complexities)-1)):
            return "causal", "Progresión de complejidad creciente detectada"
        novelties = [r.novelty for r in sorted_r]
        if novelties[-1] > novelties[0] + 0.25:
            return "causal", "Acumulación de novedad: el pensamiento se expande"
        return None, ""

    def _neural_pattern(self, reprs: List[MentalRepresentation],
                         neural_act: float) -> Tuple[Optional[str], str]:
        avg_sal = sum(r.salience() for r in reprs) / len(reprs)
        if neural_act > 0.65 and avg_sal > 0.55:
            return "neural", (f"Alta coherencia neural (act={neural_act:.3f}) "
                              f"con saliencia={avg_sal:.3f}")
        return None, ""


# ═══════════════════════════════════════════════════════════════════════════════
#  MOTOR PRINCIPAL DE IMAGINACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class ImaginationEngine:
    """Motor principal de imaginación cognitiva-emocional.

    Coordina:
    ─ La red neuronal de imaginación (ImaginationNetwork)
    ─ Las representaciones mentales activas (máx 7, regla de Miller)
    ─ El motor de escenarios (ScenarioEngine)
    ─ El detector de insights (InsightDetector)
    ─ La tensión creativa como disparador interno
    ─ La memoria para semillas y persistencia de resultados
    ─ El estado emocional/instintivo como modulador

    La tensión creativa sube cuando:
    ─ Hay fragmentos de memoria WORKING o ASSOCIATIVE sin imaginar
    ─ Las emociones de alta arousal no tienen salida creativa
    ─ Los instintos de exploración/reproducción están activos
    ─ Hay tiempo sin ningún ciclo imaginativo

    La tensión baja cuando se genera un escenario o insight.
    """

    WORKING_MEM_LIMIT = 7   # máximo de representaciones simultáneas
    TENSION_THRESHOLD = 0.38 # umbral mínimo para activar ciclo

    def __init__(self,
                 memory_dir:   str   = "memory",
                 n_animal:     int   = 5,
                 n_micelial:   int   = 5,
                 fluid_mind    = None,
                 bg_thinker    = None):

        self._lock    = RLock()

        # ── Motores de apoyo ──────────────────────────────────────────────
        self.adaptive    = AdaptiveCore(n_animal=0, n_micelial=0)
        self.memory_mgr  = MemoryManager(decay_interval_s=30.0)
        self.persistence = MemoryPersistence(
            self.memory_mgr, base_dir=memory_dir,
            auto_save_interval_s=60.0)

        # ── Red neuronal ──────────────────────────────────────────────────
        self.synapse_mgr = SynapseManager(
            prune_interval_s  = 60.0,
            utility_threshold = 0.08,
            error_rate_max    = 0.75,
            inactivity_secs   = 120.0,
        )
        self.network = ImaginationNetwork(
            self.synapse_mgr, n_animal, n_micelial)

        # ── Motores cognitivos ────────────────────────────────────────────
        self.scenario_engine  = ScenarioEngine()
        self.insight_detector = InsightDetector()

        # ── Estado ────────────────────────────────────────────────────────
        self.active_reprs:     List[MentalRepresentation] = []
        self.creative_tension: float = 0.0
        self.focus_coherence:  float = 0.5
        self._cycle            = 0
        self._last_cycle_ts    = 0.0
        self._last_prune_cycle = 0

        # ── Historial ─────────────────────────────────────────────────────
        self.scenarios:  List[Scenario] = []
        self.insights:   List[Insight]  = []
        self._scene_log  = deque(maxlen=50)
        self._insig_log  = deque(maxlen=30)

        # ── Estadísticas ──────────────────────────────────────────────────
        self._total_reprs    = 0
        self._total_scenarios= 0
        self._total_insights = 0

        # ── Referencias opcionales ────────────────────────────────────────
        self.fluid_mind  = fluid_mind
        self.bg_thinker  = bg_thinker

        # ── Disco ─────────────────────────────────────────────────────────
        self._base_dir    = Path(memory_dir) / "imagination"
        self._scenario_dir= self._base_dir / "scenarios"
        self._repr_dir    = self._base_dir / "representations"
        self._insight_dir = self._base_dir / "insights"
        for d in [self._scenario_dir, self._repr_dir, self._insight_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Cargar experiencias de demostración
        _build_demo_memory(self.memory_mgr)
        log_event("ImaginationEngine inicializado", "INFO")

    # ═════════════════════════════════════════════════════════════════════
    #  API PÚBLICA
    # ═════════════════════════════════════════════════════════════════════

    def inject_stimulus(self, content: str,
                        tags:    List[str] = None,
                        valence: float = 0.0,
                        arousal: float = 0.5,
                        instinct: str  = ""):
        """Inyecta un estímulo externo que puede disparar imaginación."""
        tags = tags or content.split()[:4]
        # Actualizar estado adaptativo
        self.adaptive.run_cycle(
            stimulus = content,
            threat   = max(0.0, -valence * arousal),
            energy   = 0.6 + valence * 0.2,
            novelty  = arousal * 0.5,
        )
        # Codificar en memoria
        fid = self.memory_mgr.encode(
            content=content, tags=tags, modality="conceptual",
            valence=valence, arousal=arousal,
            instinct_tags=[instinct] if instinct else [],
        )
        # Crear representación desde el estímulo
        self.create_representation(content, tags, valence, arousal,
                                   [fid] if fid else [], instinct)
        # Subir tensión creativa
        self._boost_tension(abs(valence) * 0.15 + arousal * 0.10)

    def create_representation(self, content: str,
                               tags:     List[str] = None,
                               valence:  float = 0.0,
                               arousal:  float = 0.4,
                               source_fids: List[str] = None,
                               instinct: str = "") -> MentalRepresentation:
        """Crea y añade una representación mental a la memoria de trabajo."""
        tags = tags or content.split()[:4]
        rid  = hashlib.md5(
            f"{content}{time.time()}{random.random()}".encode()
        ).hexdigest()[:12]

        complexity = self._compute_complexity(content)
        certainty  = self._compute_certainty(content, source_fids or [])
        novelty    = self._compute_novelty(content)

        repr_ = MentalRepresentation(
            repr_id       = rid,
            content       = content,
            tags          = tags,
            valence       = max(-1.0, min(1.0, valence)),
            arousal       = max(0.0,  min(1.0, arousal)),
            certainty     = certainty,
            complexity    = complexity,
            novelty       = novelty,
            activation    = 0.5 + abs(valence) * 0.3 + arousal * 0.2,
            source_fids   = source_fids or [],
            instinct_tags = [instinct] if instinct else [],
        )
        self._add_to_working_memory(repr_)
        self._total_reprs += 1
        # Guardar en disco
        self._save_repr(repr_)
        return repr_

    def run_cycle(self, force: bool = False) -> Dict[str, Any]:
        """Ejecuta un ciclo completo de imaginación si hay suficiente tensión."""
        self._cycle += 1

        # Actualizar tensión desde estado actual
        self._update_tension()

        # ¿Hay razón para imaginar?
        if not force and self.creative_tension < self.TENSION_THRESHOLD:
            return {"cycle": self._cycle, "skipped": True,
                    "tension": round(self.creative_tension, 4)}

        # Seleccionar representaciones activas
        reprs = self._select_reprs_for_scenario()
        if not reprs:
            reprs = self._seed_from_memory()
        if not reprs:
            return {"cycle": self._cycle, "no_reprs": True}

        # Activar red neuronal
        emo  = self.adaptive.emotions
        inst = self.adaptive.instincts
        neuromod = emo.get_synaptic_modulation()["neuromodulator"]
        signal   = 0.4 + self.creative_tension * 0.5
        ctx = {
            "neuromodulator": neuromod,
            "nm_level":       emo.arousal,
            "concept1":       reprs[0].content[:20],
            "seed":           "imagination_cycle",
            "pattern":        "creative_synthesis",
        }
        seed_act, expand_act, tx_count = self.network.full_activation(
            signal, ctx)
        neural_act = (seed_act * 0.45 + expand_act * 0.55)

        # Seleccionar tipo de escenario modulado por instinto
        dom_inst = inst.get_dominant()
        forced_type = None
        if dom_inst == InstinctID.EXPLORE:
            forced_type = ScenarioType.EXPLORATION
        elif dom_inst == InstinctID.SURVIVE:
            forced_type = ScenarioType.CONFLICT_RESOLUTION
        elif dom_inst in (InstinctID.BOND, InstinctID.REPRODUCE):
            forced_type = ScenarioType.INTEGRATION

        # Generar escenario
        scenario = self.scenario_engine.generate(
            reprs, forced_type, neural_act, emo)

        if not scenario:
            return {"cycle": self._cycle, "scenario_failed": True}

        # Detectar insight
        insight = self.insight_detector.detect(reprs, neural_act, scenario)
        if insight:
            scenario.insight = insight
            self.insights.append(insight)
            self._total_insights += 1
            self._insig_log.append(insight.to_dict())
            self._save_insight(insight)
            # Persistir insight en memoria
            fid = self.memory_mgr.encode(
                content      = insight.content,
                tags         = ["insight", insight.insight_type] +
                               [r.tags[0] for r in reprs if r.tags][:2],
                modality     = "conceptual",
                valence      = insight.valence,
                arousal      = 0.7,
                instinct_tags= ["explore"],
                base_strength= insight.confidence,
                forced_layer = (MemoryLayer.SELF
                                if insight.confidence > 0.75 else None),
            )
            if fid:
                f = self.memory_mgr.store.get(fid)
                if f:
                    self.persistence.notify_fragment_changed(f)

        # Persistir escenario
        self.scenarios.append(scenario)
        self._total_scenarios += 1
        self._scene_log.append(scenario.to_dict())
        self._save_scenario(scenario)

        # Guardar escenario en memoria
        mem_layer = (MemoryLayer.ASSOCIATIVE
                     if scenario.novelty > 0.5 else None)
        fid_scene = self.memory_mgr.encode(
            content      = scenario.content,
            tags         = [scenario.scenario_type.value] +
                           reprs[0].tags[:2],
            modality     = "conceptual",
            valence      = scenario.valence,
            arousal      = 0.5 + scenario.novelty * 0.3,
            base_strength= scenario.confidence,
            forced_layer = mem_layer,
        )
        if fid_scene:
            f = self.memory_mgr.store.get(fid_scene)
            if f:
                self.persistence.notify_fragment_changed(f)

        # Si hay FluidMind, percibir el escenario
        if self.fluid_mind and hasattr(self.fluid_mind, "perceive"):
            try:
                self.fluid_mind.perceive(
                    scenario.content, reprs[0].tags,
                    scenario.valence, 0.5 + scenario.novelty * 0.3,
                    "explore", "imaginacion",
                )
            except Exception:
                pass

        # Bajar tensión
        self.creative_tension = max(
            0.0, self.creative_tension - 0.18 - scenario.novelty * 0.08)

        # Actualizar representaciones
        self._decay_reprs()
        self._update_focus_coherence(neural_act)

        # Poda periódica
        if self._cycle - self._last_prune_cycle >= 10:
            self.synapse_mgr.prune()
            self._last_prune_cycle = self._cycle

        # Persistencia de memoria periódica
        if self._cycle % 5 == 0:
            self.memory_mgr.decay_cycle(force=True)
            self.memory_mgr.consolidate(force=True)
            self.persistence.save_cycle(force=True)

        self._last_cycle_ts = time.time()
        return {
            "cycle":          self._cycle,
            "scenario_type":  scenario.scenario_type.value,
            "scenario_id":    scenario.scenario_id,
            "content":        scenario.content[:80],
            "valence":        scenario.valence,
            "novelty":        scenario.novelty,
            "neural_act":     round(neural_act, 4),
            "seed_act":       round(seed_act, 4),
            "expand_act":     round(expand_act, 4),
            "synapse_tx":     tx_count,
            "insight":        insight.insight_type if insight else None,
            "tension_after":  round(self.creative_tension, 4),
            "reprs_used":     len(reprs),
        }

    # ═════════════════════════════════════════════════════════════════════
    #  INTERNOS
    # ═════════════════════════════════════════════════════════════════════

    def _update_tension(self):
        """Actualiza la tensión creativa desde el estado actual."""
        delta = 0.0
        # Working memory con fragmentos sin imaginar
        n_working = len(self.memory_mgr.store.layer_fragments(
            MemoryLayer.WORKING))
        delta += min(0.06, n_working * 0.004)
        # Emociones de alta arousal
        emo = self.adaptive.emotions
        delta += emo.arousal * 0.03
        # Instinto de exploración activo
        dom = self.adaptive.instincts.get_dominant()
        if dom in (InstinctID.EXPLORE, InstinctID.REPRODUCE):
            delta += 0.04
        # Tiempo sin ciclo
        idle = time.time() - max(self._last_cycle_ts, 1.0)
        delta += min(0.05, idle / 600.0)
        # Base mínima
        delta += 0.01
        self.creative_tension = min(1.0, self.creative_tension + delta)

    def _boost_tension(self, amount: float):
        with self._lock:
            self.creative_tension = min(1.0, self.creative_tension + amount)

    def _add_to_working_memory(self, repr_: MentalRepresentation):
        with self._lock:
            # Evitar duplicados por contenido
            for existing in self.active_reprs:
                if existing.content == repr_.content:
                    existing.activation = min(1.0, existing.activation + 0.15)
                    return
            self.active_reprs.append(repr_)
            # Mantener límite (Miller's 7±2)
            if len(self.active_reprs) > self.WORKING_MEM_LIMIT:
                # Eliminar la menos saliente
                self.active_reprs.sort(key=lambda r: r.salience())
                self.active_reprs = self.active_reprs[1:]

    def _select_reprs_for_scenario(self) -> List[MentalRepresentation]:
        with self._lock:
            active = [r for r in self.active_reprs if r.activation > 0.2]
            if not active:
                return []
            # Ordenar por saliencia y tomar las top 2–3
            active.sort(key=lambda r: r.salience(), reverse=True)
            # Garantizar diversidad emocional si es posible
            if len(active) >= 2:
                top = [active[0]]
                # Añadir la de valencia más distinta
                diff_max = -1.0
                diff_repr = None
                for r in active[1:]:
                    d = abs(r.valence - top[0].valence)
                    if d > diff_max:
                        diff_max, diff_repr = d, r
                if diff_repr:
                    top.append(diff_repr)
                # Añadir una más si hay
                extras = [r for r in active if r not in top]
                if extras:
                    top.append(extras[0])
                return top[:3]
            return active[:1]

    def _seed_from_memory(self) -> List[MentalRepresentation]:
        """Crea representaciones desde fragmentos de memoria si no hay activas."""
        reprs = []
        for layer in [MemoryLayer.WORKING, MemoryLayer.ASSOCIATIVE,
                      MemoryLayer.CONSOLIDATED]:
            frags = self.memory_mgr.store.layer_fragments(layer)
            for f in sorted(frags, key=lambda x: x.strength, reverse=True)[:3]:
                r = self.create_representation(
                    f.content, f.tags, f.emotion.valence,
                    f.emotion.arousal, [f.fid],
                    f.emotion.instinct_tags[0] if f.emotion.instinct_tags else "",
                )
                reprs.append(r)
            if reprs:
                break
        return reprs[:3]

    def _decay_reprs(self):
        with self._lock:
            for r in self.active_reprs:
                r.decay(rate=0.05)
            self.active_reprs = [
                r for r in self.active_reprs if r.activation > 0.08]

    def _update_focus_coherence(self, neural_act: float):
        """Actualiza la coherencia del foco imaginativo."""
        if self.active_reprs:
            acts = [r.activation for r in self.active_reprs]
            avg  = sum(acts) / len(acts)
            var  = sum((a - avg)**2 for a in acts) / len(acts)
            raw  = neural_act * 0.5 + (1.0 - min(var, 1.0)) * 0.5
        else:
            raw  = neural_act * 0.5
        self.focus_coherence = (self.focus_coherence * 0.8 + raw * 0.2)

    def _compute_complexity(self, content: str) -> float:
        words   = content.split()
        unique  = len(set(w.lower() for w in words))
        complex_w = len([w for w in words if len(w) > 6])
        return min(1.0, (
            min(1.0, len(words) / 30.0) * 0.3 +
            (unique / max(1, len(words))) * 0.4 +
            min(1.0, complex_w / max(1, len(words))) * 0.3
        ))

    def _compute_certainty(self, content: str, fids: List[str]) -> float:
        spec = min(1.0, len(content.split()) / 20.0)
        mem  = min(1.0, len(fids) / 5.0)
        return (spec + mem) / 2.0

    def _compute_novelty(self, content: str) -> float:
        tags     = content.split()[:5]
        similar  = self.memory_mgr.store.search_by_tags(tags, top_k=10)
        factor   = len(similar) / 20.0
        return max(0.10, min(1.0, 1.0 - factor))

    # ── Persistencia en disco ─────────────────────────────────────────────
    def _save_repr(self, repr_: MentalRepresentation):
        try:
            path = self._repr_dir / f"{repr_.repr_id}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(repr_.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_neuron_error("ImaginationEngine", f"_save_repr: {e}")

    def _save_scenario(self, scenario: Scenario):
        try:
            path = self._scenario_dir / f"{scenario.scenario_id}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(scenario.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_neuron_error("ImaginationEngine", f"_save_scenario: {e}")

    def _save_insight(self, insight: Insight):
        try:
            path = self._insight_dir / f"{insight.insight_id}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(insight.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_neuron_error("ImaginationEngine", f"_save_insight: {e}")

    # ── Estado público ────────────────────────────────────────────────────
    def get_status(self) -> Dict[str, Any]:
        syn_s = self.synapse_mgr.get_stats()
        mem_s = self.memory_mgr.get_status()["store"]
        emo_s = self.adaptive.emotions.get_summary()
        inst_s= self.adaptive.instincts.get_status()
        return {
            "cycle":              self._cycle,
            "creative_tension":   round(self.creative_tension, 4),
            "focus_coherence":    round(self.focus_coherence, 4),
            "active_reprs":       len(self.active_reprs),
            "total_reprs":        self._total_reprs,
            "total_scenarios":    self._total_scenarios,
            "total_insights":     self._total_insights,
            "network":            self.network.get_status(),
            "synapses":           syn_s,
            "memory":             mem_s,
            "emotions":           emo_s,
            "instincts":          inst_s,
            "disk": {
                "scenarios":       len(list(self._scenario_dir.glob("*.json"))),
                "representations": len(list(self._repr_dir.glob("*.json"))),
                "insights":        len(list(self._insight_dir.glob("*.json"))),
            },
        }

    def search(self, keywords: List[str], kind: str = "all") -> List[Dict]:
        """Busca en escenarios, representaciones e insights en disco."""
        results = []
        kw_lower = [k.lower() for k in keywords]
        dirs = []
        if kind in ("all", "scenarios"):
            dirs.append((self._scenario_dir, "scenario"))
        if kind in ("all", "representations"):
            dirs.append((self._repr_dir, "representation"))
        if kind in ("all", "insights"):
            dirs.append((self._insight_dir, "insight"))
        for d, label in dirs:
            for fpath in d.glob("*.json"):
                try:
                    data = json.loads(fpath.read_text(encoding="utf-8"))
                    content = data.get("content", "").lower()
                    if any(kw in content for kw in kw_lower):
                        data["_record_type"] = label
                        results.append(data)
                except Exception:
                    pass
        results.sort(key=lambda x: x.get("creation_ts", 0), reverse=True)
        return results

    def shutdown(self):
        self.persistence.go_to_sleep()
        self.synapse_mgr.prune(force=True)
        log_event("ImaginationEngine apagado", "INFO")


# ═══════════════════════════════════════════════════════════════════════════════
#  DIAGNÓSTICO INTERACTIVO
# ═══════════════════════════════════════════════════════════════════════════════

_SEP  = "─" * 64
_SEP2 = "═" * 64

_STIMULI = [
    ("La primera vez que entendí algo que parecía imposible",
     ["comprension","luz","logro"],           0.90, 0.85, "explore"),
    ("Una amenaza que no puedo ver pero que siento",
     ["amenaza","tension","incertidumbre"],   -0.75, 0.88, "survive"),
    ("El silencio antes de que ocurra algo grande",
     ["anticipacion","silencio","umbral"],     0.35, 0.70, "explore"),
    ("Dos ideas que se contradicen en mi interior",
     ["contradiccion","tension","dualidad"],  -0.30, 0.65, "defend"),
    ("La sensación de que algo lejano me pertenece",
     ["pertenencia","lejano","resonancia"],    0.70, 0.55, "bond"),
    ("Un patrón que se repite de formas distintas",
     ["patron","repeticion","fractal"],        0.60, 0.60, "explore"),
    ("El miedo a que algo hermoso termine",
     ["belleza","perdida","miedo"],           -0.40, 0.75, "survive"),
    ("La curiosidad por lo que aún no existe",
     ["novedad","potencial","futuro"],         0.80, 0.80, "explore"),
    ("Estar al borde de entender algo profundo",
     ["profundidad","umbral","insight"],       0.75, 0.82, "explore"),
    ("La calma que llega después de la tormenta interna",
     ["calma","resolucion","paz"],             0.80, 0.22, "rest"),
]


def _bar(v: float, w: int = 16) -> str:
    v = max(0.0, min(1.0, v))
    return "█" * int(round(v * w)) + "░" * (w - int(round(v * w)))


def _ask_int(prompt, lo, hi, default):
    while True:
        try:
            r = input(f"  {prompt} [{lo}–{hi}, default={default}]: ").strip()
            return int(r) if r else default
        except (ValueError, KeyboardInterrupt):
            return default


def _valence_label(v: float) -> str:
    if v >  0.6: return "✦ muy positivo"
    if v >  0.2: return "↑ positivo"
    if v > -0.2: return "· neutro"
    if v > -0.6: return "↓ negativo"
    return "✗ muy negativo"


def run_diagnostic():
    print()
    print(_SEP2)
    print("  DIAGNÓSTICO — MOTOR DE IMAGINACIÓN COGNITIVA")
    print("  Escenarios · Insights · Neuronal · Emocional · Memorioso")
    print(_SEP2)

    print("\n  Configura:\n")
    n_animal   = _ask_int("Neuronas animales",    1, 10, 5)
    n_micelial = _ask_int("Neuronas miceliales",  1, 10, 5)
    n_stimuli  = _ask_int("Estímulos a inyectar", 1, 20, 8)
    n_cycles   = _ask_int("Ciclos de imaginación",1, 30, 8)
    mem_dir    = input("  Directorio de memoria [default=memory]: ").strip() or "memory"

    print(f"\n  → {n_animal}A · {n_micelial}M · {n_stimuli} estímulos · "
          f"{n_cycles} ciclos · memoria='{mem_dir}'\n")

    # ── [1] Construir ─────────────────────────────────────────────────────
    print(_SEP)
    print("  [1/7] Construyendo motor de imaginación…")
    t0 = time.time()
    engine = ImaginationEngine(
        memory_dir=mem_dir, n_animal=n_animal, n_micelial=n_micelial)
    elapsed = (time.time() - t0) * 1000
    net_s = engine.network.get_status()
    print(f"       ✓ Motor listo en {elapsed:.1f} ms")
    print(f"         {net_s['animals']}A + {net_s['micelials']}M → "
          f"{net_s['total_synapses']} sinapsis")

    # ── [2] Inyectar estímulos ────────────────────────────────────────────
    print(_SEP)
    print(f"  [2/7] Inyectando {n_stimuli} estímulos…\n")
    for i in range(n_stimuli):
        stim = _STIMULI[i % len(_STIMULI)]
        content, tags, val, aro, inst = stim
        engine.inject_stimulus(content, tags, val, aro, inst)
        tension = engine.creative_tension
        print(f"  [{i+1:02d}] V={val:+.2f} A={aro:.2f} "
              f"inst={inst:<10} tensión={tension:.3f}  "
              f"'{content[:42]}'")
        time.sleep(0.05)

    # ── [3] Ciclos de imaginación ─────────────────────────────────────────
    print(_SEP)
    print(f"  [3/7] Ejecutando {n_cycles} ciclos de imaginación…\n")
    for i in range(n_cycles):
        result = engine.run_cycle(force=(i < 2))  # forzar los primeros 2
        if result.get("skipped"):
            print(f"  [{i+1:02d}] ─ (tensión insuficiente: "
                  f"{result['tension']:.3f})")
        elif result.get("no_reprs"):
            print(f"  [{i+1:02d}] ─ (sin representaciones activas)")
        else:
            stype   = result.get("scenario_type", "?")
            content = result.get("content", "")[:50]
            neural  = result.get("neural_act", 0.0)
            insight = result.get("insight")
            ins_str = f"  💡 {insight}" if insight else ""
            print(f"  [{i+1:02d}] [{stype:<20}] "
                  f"V={result.get('valence',0):+.3f} "
                  f"nov={result.get('novelty',0):.3f} "
                  f"act={neural:.3f}{ins_str}")
            print(f"       '{content}'")
        time.sleep(0.05)

    # ── [4] Tabla de neuronas ─────────────────────────────────────────────
    print(_SEP)
    print("  [4/7] Estado de neuronas\n")
    neuron_rows = engine.network.neuron_states()
    animal_rows   = [r for r in neuron_rows if r["domain"] == "animal"]
    micelial_rows = [r for r in neuron_rows if r["domain"] == "micelial"]

    for label, rows in [("ANIMALES", animal_rows), ("MICELIALES", micelial_rows)]:
        print(f"  ── {label} {'─'*(56-len(label))}")
        print(f"  {'ID':<18} {'Subtipo':<22} {'Act':>6} {'Res':>6} {'Plas':>6}")
        print("  " + "─" * 60)
        for r in rows:
            print(f"  {r['id']:<18} {r['subtype']:<22} "
                  f"{r['act']:>6.4f} {r['resil']:>6.3f} {r['plastic']:>6.3f}")
        print(f"  Total: {len(rows)} neuronas\n")

    # ── [5] Tabla de sinapsis ─────────────────────────────────────────────
    print(_SEP)
    print("  [5/7] Estado de sinapsis\n")
    syn_rows = engine.network.synapse_states()
    print(f"  {'ID':<14} {'Tipo':<12} {'Pol':<11} "
          f"{'Peso':>6} {'OK':>4} {'ERR':>4} {'Err%':>5} {'Pers':>5}")
    print("  " + "─" * 60)
    for s in syn_rows[:30]:
        erp  = f"{s['error_rate']*100:.0f}%" if (s['success']+s['failure']) > 0 else "─"
        pers = "✓" if s["persistent"] else "─"
        print(f"  {s['id']:<14} {s['kind']:<12} {s['polarity']:<11} "
              f"{s['weight']:>6.3f} {s['success']:>4} {s['failure']:>4} "
              f"{erp:>5} {pers:>5}")
    if len(syn_rows) > 30:
        print(f"  … y {len(syn_rows)-30} sinapsis más")
    print(f"  Total: {len(syn_rows)} sinapsis")

    # ── [6] Insights generados ────────────────────────────────────────────
    print(_SEP)
    print(f"  [6/7] Insights generados: {len(engine.insights)}\n")
    for ins in engine.insights[:8]:
        print(f"  [{ins.insight_type:<20}] "
              f"conf={ins.confidence:.3f}  "
              f"nov={ins.novelty:.3f}  "
              f"V={ins.valence:+.3f}")
        print(f"    '{ins.content[:65]}'")
        print()

    # ── [7] Estado completo ───────────────────────────────────────────────
    print(_SEP)
    print("  [7/7] Estado completo del sistema\n")
    status  = engine.get_status()
    syn_s   = status["synapses"]
    mem_s   = status["memory"]
    emo_s   = status["emotions"]
    inst_s  = status["instincts"]
    disk_s  = status["disk"]

    print("  ── IMAGINACIÓN ──────────────────────────────────────────")
    print(f"    Tensión creativa    : {status['creative_tension']:.4f}  "
          f"{_bar(status['creative_tension'], 12)}")
    print(f"    Coherencia de foco  : {status['focus_coherence']:.4f}  "
          f"{_bar(status['focus_coherence'], 12)}")
    print(f"    Repr. activas       : {status['active_reprs']}")
    print(f"    Repr. totales       : {status['total_reprs']}")
    print(f"    Escenarios generados: {status['total_scenarios']}")
    print(f"    Insights generados  : {status['total_insights']}")

    print("\n  ── DISCO ────────────────────────────────────────────────")
    print(f"    Escenarios   : {disk_s['scenarios']}")
    print(f"    Representac. : {disk_s['representations']}")
    print(f"    Insights     : {disk_s['insights']}")

    print("\n  ── SINAPSIS ─────────────────────────────────────────────")
    print(f"    Total={syn_s['total_synapses']}  Activas={syn_s['active_synapses']}")
    print(f"    Tipos: {syn_s['by_kind']}")
    print(f"    Peso avg={syn_s['avg_weight']}  Utilidad={syn_s['avg_utility']}")

    print("\n  ── MEMORIA ──────────────────────────────────────────────")
    for layer, count in mem_s["by_layer"].items():
        pct = count / max(1, mem_s["total"]) * 100
        print(f"    {layer:<15} {_bar(count/max(1,mem_s['total']),10)} "
              f"{count:>4} ({pct:>5.1f}%)")
    print(f"    Fuerza promedio: {mem_s['avg_strength']:.4f}")

    print("\n  ── EMOCIONES E INSTINTOS ────────────────────────────────")
    print(f"    Emoción  : {emo_s['dominant']}  "
          f"V={emo_s['valence']:+.3f}  A={emo_s['arousal']:.3f}  "
          f"NM={emo_s['neuromod']}")
    print(f"    Instintos activos : {inst_s.get('active', [])}")
    print(f"    Instinto dominante: {inst_s.get('dominant','ninguno')}")

    # ── Búsqueda de prueba ────────────────────────────────────────────────
    results = engine.search(["insight", "patron", "comprension"])
    if results:
        print(f"\n  ── BÚSQUEDA DE PRUEBA (insight/patron/comprension) ──────")
        for r in results[:3]:
            rtype = r.get("_record_type", "?")
            rcont = r.get("content", "")[:60]
            print(f"    [{rtype:<14}] '{rcont}'")

    print()
    print(_SEP2)
    print("  RESUMEN EJECUTIVO")
    print(_SEP2)

    health = ("ÓPTIMO"    if status["total_scenarios"] >= n_cycles * 0.7 else
              "ACTIVO"    if status["total_scenarios"] >= n_cycles * 0.4 else
              "INICIANDO")
    print(f"  Estado             : {health}")
    print(f"  Ciclos ejecutados  : {status['cycle']}")
    print(f"  Escenarios creados : {status['total_scenarios']}")
    print(f"  Insights emergidos : {status['total_insights']}")
    print(f"  Representaciones   : {status['total_reprs']}")
    print(f"  Tensión creativa   : {status['creative_tension']:.4f}")
    print(f"  Red neuronal       : "
          f"{net_s['animals']}A + {net_s['micelials']}M → "
          f"{net_s['total_synapses']} sinapsis")
    print(f"  Fragmentos memoria : {mem_s['total']}")
    print(f"  Emoción dominante  : {emo_s['dominant']}")
    print()
    print("  ✓ Motor de imaginación listo para operación continua")
    print("  ✓ Conectado a memoria, emociones, instintos y red neuronal")
    print(_SEP2)
    print()

    engine.shutdown()
    return engine


if __name__ == "__main__":
    random.seed(42)
    try:
        engine = run_diagnostic()
    except KeyboardInterrupt:
        print("\n  Diagnóstico interrumpido.")
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        traceback.print_exc()
