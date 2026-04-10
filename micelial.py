# micelial.py
"""
Sistema de neuronas miceliales cognitivas para pensamiento profundo e integración
conceptual. Inspirado en redes miceliales (hongos), plasmodios, líquenes y sistemas
de señalización química distribuida de organismos no-neurales.

Compatible con neuronas animales (animal.py) para pensamiento híbrido.
Procesamiento: conceptual, lento, masivo, distribuido.

Sin tiempo de vida · Sin memoria persistente · Sin poda interna
(la poda es responsabilidad de un módulo externo)

Nuevos tipos biológicamente inspirados:
  - Hifa de integración (estilo crecimiento apical de hongos)
  - Nodo de anastomosis (fusión de hifas, estilo Phanerochaete)
  - Gradiente de auxina (estilo señalización vegetal)
  - Plasmodio colector (estilo Physarum polycephalum)
  - Mensajero de calcio (onda de Ca²⁺ inter-celular)
  - Nodo de quórum (quorum sensing estilo bacterias)
  - Célula guardiana estomática (apertura/cierre por señal)
  - Sensor de pH conceptual (estilo vacuola fúngica)
  - Integrador de presión de turgor (estilo célula vegetal)
  - Nodo de resistencia sistémica (SAR estilo planta)
  - Oscilador glicolitico (estilo levadura sincronizada)
  - Célula Schwann conceptual (soporte/envolvimiento)
"""

import time
import hashlib
import math
import random
from abc import ABC, abstractmethod
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

from monitoring import log_event, log_neuron_error, log_neuron_warning


# ─── Constantes ─────────────────────────────────────────────────────────────
DEFAULT_MAX_SYNAPSES    = 100
DEFAULT_MAX_CONCEPTS    = 1000
KNOWLEDGE_DECAY_RATE    = 1e-10
INSIGHT_REGEN_RATE      = 1e-8
DEFAULT_INTEGRATION_RATE = 1e-6


# ═══════════════════════════════════════════════════════════════════════════════
#  BASE
# ═══════════════════════════════════════════════════════════════════════════════

class CognitiveMicelialNeuronBase(ABC):
    """Base para todas las neuronas miceliales cognitivas.

    Características principales:
    - Procesamiento conceptual lento y profundo
    - Integración distribuida de conocimiento
    - Compatible en paralelo/serie con neuronas animales
    - Sin límite de vida, sin poda interna, sin memoria persistente
    """

    def __init__(self, neuron_id: str,
                 max_synapses: int = DEFAULT_MAX_SYNAPSES,
                 max_concepts: int = DEFAULT_MAX_CONCEPTS):
        if not isinstance(neuron_id, str) or not neuron_id.strip():
            raise ValueError("Se requiere un neuron_id no vacío")
        if not isinstance(max_synapses, int) or max_synapses <= 0:
            raise ValueError("max_synapses debe ser un entero positivo")
        if not isinstance(max_concepts, int) or max_concepts <= 0:
            raise ValueError("max_concepts debe ser un entero positivo")

        self.neuron_id    = neuron_id
        self.max_synapses = max_synapses
        self.max_concepts = max_concepts
        self.synapses     = []

        self.activation_level     = 0.0
        self.last_activation_time = time.time()
        self.age                  = 0.0
        self.cognitive_resilience = 1.0
        self.lock                 = RLock()

        # Características miceliales
        self.concept_concentration  = {}
        self._concept_access_times  = {}
        self.integration_rate       = DEFAULT_INTEGRATION_RATE
        self.network_depth          = 0.5
        self.distributed_insights   = {}

        # Longevidad
        self.knowledge_decay_rate      = KNOWLEDGE_DECAY_RATE
        self.insight_regeneration_rate = INSIGHT_REGEN_RATE
        self.cognitive_interference    = 0.0

        # Compatibilidad híbrida
        self.neuron_type     = "cognitive_micelial"
        self.processing_speed = "deep_slow"
        self.signal_type      = "conceptual"

        # Métricas
        self._activation_buffer  = deque(maxlen=10)
        self.impact              = 0.5
        self.plasticity          = 0.7
        self.efficiency          = 0.6
        self._impact_history     = deque(maxlen=50)
        self._plasticity_history = deque(maxlen=50)
        self._efficiency_history = deque(maxlen=50)

    # ── Envejecimiento (sin muerte, sin poda) ──────────────────────────────
    def age_neuron(self, delta_time: float) -> None:
        """Actualiza el estado interno con el paso del tiempo.
        No aplica tiempo de vida máximo. No realiza poda.
        """
        if not isinstance(delta_time, (int, float)) or delta_time <= 0:
            return

        try:
            with self.lock:
                self.age = max(0.0, self.age + delta_time)

                # Decaimiento de resiliencia (extremadamente lento)
                loss = self.knowledge_decay_rate * delta_time * (1 + self.cognitive_interference * 0.1)
                self.cognitive_resilience = max(0.0, min(1.0, self.cognitive_resilience - loss))

                # Regeneración
                if self.cognitive_resilience < 1.0:
                    growth = self.insight_regeneration_rate * delta_time
                    self.cognitive_resilience = min(1.0, self.cognitive_resilience + growth)

                # Actualizar profundidad de red
                self.network_depth = max(0.0, min(1.0,
                    self.network_depth + self.integration_rate * delta_time))

                # Reducir interferencia gradualmente
                self.cognitive_interference = max(0.0,
                    min(1.0, self.cognitive_interference - delta_time * 1e-8))

                self._update_metrics()

        except Exception as e:
            log_neuron_error(self.neuron_id, f"Error en age_neuron: {e}")
            self._restore_safe_state()

    def _restore_safe_state(self):
        for attr, val in [("cognitive_resilience", 0.5), ("network_depth", 0.5),
                          ("cognitive_interference", 0.0), ("activation_level", 0.0)]:
            try:
                setattr(self, attr, val)
            except Exception:
                pass

    # ── Conceptos ─────────────────────────────────────────────────────────
    def update_concept(self, concept_type: str, concentration: float):
        """Actualiza la concentración de un concepto (sin persistencia externa)."""
        if not isinstance(concept_type, str) or not concept_type.strip():
            raise ValueError("concept_type debe ser una cadena no vacía")
        concentration = max(0.0, min(1.0, float(concentration)))

        with self.lock:
            self.concept_concentration[concept_type]    = concentration
            self._concept_access_times[concept_type]    = time.time()

            # Purga ligera si se acerca al límite (sin poda compleja)
            if len(self.concept_concentration) > self.max_concepts:
                oldest = sorted(self._concept_access_times.items(), key=lambda x: x[1])
                for key, _ in oldest[:max(1, len(oldest) // 10)]:
                    self.concept_concentration.pop(key, None)
                    self._concept_access_times.pop(key, None)

    def add_cognitive_interference(self, amount: float):
        amount = max(0.0, min(1.0, float(amount)))
        with self.lock:
            self.cognitive_interference = min(
                1.0, self.cognitive_interference + amount * (1.0 - self.cognitive_resilience)
            )

    # ── Métricas ──────────────────────────────────────────────────────────
    def _update_metrics(self):
        try:
            self._impact_history.append(self.impact)
            self._plasticity_history.append(self.plasticity)
            self._efficiency_history.append(self.efficiency)

            w = 10
            if self._impact_history:
                self.impact      = sum(list(self._impact_history)[-w:]) / min(w, len(self._impact_history))
            if self._plasticity_history:
                self.plasticity  = sum(list(self._plasticity_history)[-w:]) / min(w, len(self._plasticity_history))
            if self._efficiency_history:
                self.efficiency  = sum(list(self._efficiency_history)[-w:]) / min(w, len(self._efficiency_history))

            self.impact     = max(0.0, min(1.0, self.impact))
            self.plasticity = max(0.0, min(1.0, self.plasticity))
            self.efficiency = max(0.0, min(1.0, self.efficiency))
        except Exception as e:
            log_neuron_error(self.neuron_id, f"Error en _update_metrics: {e}")

    def _update_plasticity(self):
        activity = min(1.0, len(self._activation_buffer) / 5.0)
        age_factor = 1.0 - min(1.0, self.age / 1e6)
        new_p = (activity * 0.6 + self.impact * 0.4) * age_factor
        self.plasticity = max(0.1, min(1.0, self.plasticity * 0.8 + new_p * 0.2))

    def _update_efficiency(self):
        stability = 1.0 - self.cognitive_interference * 0.5
        new_e = (self.impact * 0.4 + self.plasticity * 0.4 + stability * 0.2)
        new_e *= (0.8 + self.cognitive_resilience * 0.4)
        self.efficiency = max(0.1, min(1.0, self.efficiency * 0.7 + new_e * 0.3))

    # ── Propagación ───────────────────────────────────────────────────────
    def propagate_conceptual_signal(self, signal_strength: float,
                                    concept_type: str, context: Dict = None):
        if not self.synapses:
            return []
        compatible = [s for s in self.synapses
                      if hasattr(s, "conceptual_compatibility")
                      and concept_type in s.conceptual_compatibility] or self.synapses
        results = []
        with ThreadPoolExecutor(max_workers=min(2, len(compatible))) as ex:
            futures = []
            for syn in compatible:
                if hasattr(syn, "is_conceptually_active") and syn.is_conceptually_active(concept_type):
                    mod = signal_strength * self.cognitive_resilience * self.network_depth
                    futures.append(ex.submit(syn.transmit_concept, mod, concept_type, self, context))
            for f in as_completed(futures, timeout=2.0):
                try:
                    r = f.result()
                    if r is not None:
                        results.append(r)
                except Exception:
                    pass
        return results

    # ── Estado ────────────────────────────────────────────────────────────
    def get_state(self) -> Dict:
        with self.lock:
            return {
                "neuron_id":              self.neuron_id,
                "activation_level":       self.activation_level,
                "age":                    self.age,
                "cognitive_resilience":   self.cognitive_resilience,
                "network_depth":          self.network_depth,
                "concept_count":          len(self.concept_concentration),
                "distributed_insights":   len(self.distributed_insights),
                "cognitive_interference": self.cognitive_interference,
                "synapses_count":         len(self.synapses),
                "last_activation":        self.last_activation_time,
            }

    @abstractmethod
    def receive_concept(self, concentration: float, concept_type: str,
                        context: Dict = None) -> float:
        pass

    @abstractmethod
    def process(self, context: Dict = None) -> Dict[str, float]:
        pass


# ═══════════════════════════════════════════════════════════════════════════════
#  CATEGORÍA 1 – INTEGRADORES CONCEPTUALES (tipos originales)
# ═══════════════════════════════════════════════════════════════════════════════

class AbstractPatternIntegrator(CognitiveMicelialNeuronBase):
    """Integra patrones abstractos multi-nivel y detecta conexiones no obvias."""

    def __init__(self, neuron_id: str, abstraction_levels: int = 5):
        super().__init__(neuron_id, max_synapses=200)
        self.abstraction_levels      = abstraction_levels
        self.pattern_history         = defaultdict(lambda: deque(maxlen=50))
        self.conceptual_bridges      = {}
        self.abstraction_threshold   = 0.3

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            level = context.get("abstraction_level", 1) if context else 1
            related = context.get("related_concepts", []) if context else []
            key = f"L{level}_{concept_type}"
            self.pattern_history[key].append({
                "concentration": concentration,
                "concept": concept_type,
                "related": related,
                "ts": time.time(),
                "level": level,
            })
            self.update_concept(concept_type, concentration)

            for other in related:
                bk = tuple(sorted([concept_type, other]))
                if bk not in self.conceptual_bridges:
                    self.conceptual_bridges[bk] = {"strength": 0.0, "co": 0}
                self.conceptual_bridges[bk]["co"] += 1
                self.conceptual_bridges[bk]["strength"] = min(
                    1.0, self.conceptual_bridges[bk]["strength"] + concentration * 0.1
                )

            novelty = self._novelty(concept_type, concentration, level)
            self.activation_level = novelty * concentration
            return self.activation_level

    def _novelty(self, concept_type, concentration, level):
        key = f"L{level}_{concept_type}"
        hist = self.pattern_history[key]
        if len(hist) < 3:
            return 1.0
        recent = [e["concentration"] for e in list(hist)[-5:]]
        avg = sum(recent) / len(recent)
        return min(1.0, abs(concentration - avg) * 2.0)

    def process(self, context=None):
        with self.lock:
            out = {}
            # Puentes fuertes → señal de emergencia conceptual
            for (c1, c2), info in self.conceptual_bridges.items():
                if info["strength"] > 0.7 and info["co"] > 3:
                    out[f"bridge_{c1}_x_{c2}"] = info["strength"]
            # Actividad por nivel de abstracción
            for lvl in range(1, self.abstraction_levels + 1):
                vals = [e["concentration"]
                        for k, h in self.pattern_history.items()
                        if k.startswith(f"L{lvl}_")
                        for e in list(h)[-3:]]
                if vals:
                    out[f"L{lvl}_activity"] = sum(vals) / len(vals)
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in out.items()}


class ContextualTemporalIntegrator(CognitiveMicelialNeuronBase):
    """Mantiene contexto histórico de argumentos a través de múltiples escalas temporales."""

    def __init__(self, neuron_id: str, temporal_scales: Dict[str, int] = None):
        super().__init__(neuron_id, max_synapses=300)
        self.temporal_scales = temporal_scales or {
            "immediate":   60,
            "short_term":  3600,
            "medium_term": 86400,
            "long_term":   604800,
        }
        self.context_layers = {s: deque(maxlen=100) for s in self.temporal_scales}
        self.argument_threads = {}

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            now    = time.time()
            arg_id = context.get("argument_id", "default") if context else "default"
            pos    = context.get("logical_position", "premise") if context else "premise"

            entry = {"concept": concept_type, "concentration": concentration,
                     "ts": now, "argument_id": arg_id, "position": pos}

            for scale, max_age in self.temporal_scales.items():
                cutoff = now - max_age
                while self.context_layers[scale] and self.context_layers[scale][0]["ts"] < cutoff:
                    self.context_layers[scale].popleft()
                self.context_layers[scale].append(entry)

            if arg_id not in self.argument_threads:
                self.argument_threads[arg_id] = {
                    "premises": [], "conclusions": [], "evidence": [], "start": now
                }
            thread = self.argument_threads[arg_id]
            if pos == "premise":       thread["premises"].append(entry)
            elif pos == "conclusion":  thread["conclusions"].append(entry)
            elif pos == "evidence":    thread["evidence"].append(entry)

            self.update_concept(concept_type, concentration)
            relevance = self._relevance(concept_type, arg_id)
            self.activation_level = concentration * relevance
            return self.activation_level

    def _relevance(self, concept_type, arg_id):
        factors = []
        if arg_id in self.argument_threads:
            all_c = [e["concept"] for lst in self.argument_threads[arg_id].values()
                     if isinstance(lst, list) for e in lst]
            if all_c:
                factors.append(all_c.count(concept_type) / len(all_c))
        presence = sum(1 for layer in self.context_layers.values()
                       if any(e["concept"] == concept_type for e in layer))
        factors.append(presence / max(1, len(self.temporal_scales)))
        return sum(factors) / max(1, len(factors))

    def process(self, context=None):
        with self.lock:
            out = {}
            for scale, layer in self.context_layers.items():
                if layer:
                    avg = sum(e["concentration"] for e in layer) / len(layer)
                    out[f"temporal_{scale}_activity"] = avg
            for arg_id, thread in list(self.argument_threads.items())[-3:]:
                if thread["premises"] and thread["conclusions"]:
                    out[f"argument_{arg_id}_coherence"] = min(
                        1.0, len(thread["conclusions"]) / max(1, len(thread["premises"]))
                    )
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in out.items()}


class KnowledgeSynthesizer(CognitiveMicelialNeuronBase):
    """Sintetiza conocimiento de múltiples dominios en estructuras integradas."""

    def __init__(self, neuron_id: str, domain_specializations: List[str] = None):
        super().__init__(neuron_id, max_synapses=250)
        self.domain_specializations = domain_specializations or ["general"]
        self.domain_knowledge       = defaultdict(lambda: defaultdict(float))
        self.synthesis_outputs      = deque(maxlen=50)
        self.synthesis_threshold    = 0.6

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            domain = context.get("domain", "general") if context else "general"
            self.domain_knowledge[domain][concept_type] = max(
                self.domain_knowledge[domain].get(concept_type, 0.0),
                concentration
            )
            self.update_concept(concept_type, concentration)
            domain_weight = 1.2 if domain in self.domain_specializations else 0.8
            self.activation_level = concentration * domain_weight
            return min(1.0, self.activation_level)

    def process(self, context=None):
        with self.lock:
            out = {}
            # Buscar conceptos compartidos entre dominios
            domains = list(self.domain_knowledge.keys())
            for i, d1 in enumerate(domains):
                for d2 in domains[i+1:]:
                    shared = set(self.domain_knowledge[d1]) & set(self.domain_knowledge[d2])
                    for concept in shared:
                        avg = (self.domain_knowledge[d1][concept] +
                               self.domain_knowledge[d2][concept]) / 2
                        if avg > self.synthesis_threshold:
                            out[f"synthesis_{d1}_{d2}_{concept}"] = avg
            for domain, concepts in self.domain_knowledge.items():
                if concepts:
                    out[f"domain_{domain}_depth"] = sum(concepts.values()) / len(concepts)
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in out.items()}


class GlobalCoherenceCoordinator(CognitiveMicelialNeuronBase):
    """Mantiene coherencia lógica global en el espacio conceptual."""

    def __init__(self, neuron_id: str):
        super().__init__(neuron_id, max_synapses=400)
        self.reasoning_threads    = {}
        self.contradiction_log    = deque(maxlen=30)
        self.coherence_score      = 1.0

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            thread_id = context.get("reasoning_thread", "default") if context else "default"
            role      = context.get("logical_role", "premise") if context else "premise"

            if thread_id not in self.reasoning_threads:
                self.reasoning_threads[thread_id] = {
                    "premises": {}, "conclusions": {}, "start": time.time()
                }
            rt = self.reasoning_threads[thread_id]
            if role == "premise":
                rt["premises"][concept_type] = concentration
            elif role == "conclusion":
                rt["conclusions"][concept_type] = concentration
                # Detectar contradicciones lógicas simples
                if concept_type.startswith("not_") and concept_type[4:] in rt["premises"]:
                    self.contradiction_log.append({
                        "concept": concept_type, "thread": thread_id, "ts": time.time()
                    })
                    self.coherence_score = max(0.0, self.coherence_score - 0.05)

            self.update_concept(concept_type, concentration)
            self.activation_level = concentration * self.coherence_score
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            out = {
                "global_coherence":       self.coherence_score,
                "active_threads":         min(1.0, len(self.reasoning_threads) / 10.0),
                "contradictions_detected": min(1.0, len(self.contradiction_log) / 10.0),
            }
            # Recuperación de coherencia
            self.coherence_score = min(1.0, self.coherence_score + 0.001)
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in out.items()}


class ConceptualBridgeBuilder(CognitiveMicelialNeuronBase):
    """Construye puentes semánticos entre dominios conceptuales distantes."""

    def __init__(self, neuron_id: str):
        super().__init__(neuron_id, max_synapses=300)
        self.domain_concepts   = defaultdict(dict)
        self.bridge_proposals  = deque(maxlen=50)
        self.bridge_threshold  = 0.5

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            domain   = context.get("domain", "general") if context else "general"
            features = context.get("semantic_features", []) if context else []
            self.domain_concepts[domain][concept_type] = {
                "concentration": concentration,
                "features": set(features),
                "ts": time.time(),
            }
            self.update_concept(concept_type, concentration)
            self.activation_level = concentration
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            out = {}
            domains = list(self.domain_concepts.keys())
            for i, d1 in enumerate(domains):
                for d2 in domains[i+1:]:
                    for c1, info1 in self.domain_concepts[d1].items():
                        for c2, info2 in self.domain_concepts[d2].items():
                            shared = info1["features"] & info2["features"]
                            if shared:
                                strength = (len(shared) /
                                            max(1, len(info1["features"] | info2["features"])))
                                strength *= (info1["concentration"] + info2["concentration"]) / 2
                                if strength > self.bridge_threshold:
                                    key = f"bridge_{d1}_{c1}_to_{d2}_{c2}"
                                    out[key] = strength
                                    self.bridge_proposals.append(
                                        {"from": (d1, c1), "to": (d2, c2), "strength": strength}
                                    )
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in out.items()}


class InsightPropagator(CognitiveMicelialNeuronBase):
    """Propaga insights de alto valor a través de la red conceptual."""

    def __init__(self, neuron_id: str, propagation_radius: int = 500):
        super().__init__(neuron_id, max_synapses=350)
        self.propagation_radius = propagation_radius
        self.insight_catalog    = {}
        self.propagation_log    = deque(maxlen=100)

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            insight_type     = context.get("insight_type", "discovery") if context else "discovery"
            validation_level = context.get("validation", 0.5) if context else 0.5
            source_region    = context.get("source_region", "unknown") if context else "unknown"

            iid = hashlib.md5(f"{concept_type}_{insight_type}_{time.time()}".encode()).hexdigest()[:8]
            self.insight_catalog[iid] = {
                "concept": concept_type,
                "type": insight_type,
                "strength": concentration,
                "validation": validation_level,
                "source": source_region,
                "ts": time.time(),
                "propagations": 0,
            }
            self.update_concept(concept_type, concentration)
            importance = {"discovery": 1.0, "contradiction": 0.9,
                          "synthesis": 0.8, "analogy": 0.7, "refinement": 0.5}
            priority = (concentration + validation_level) / 2 * importance.get(insight_type, 0.6)
            self.activation_level = priority
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            out = {}
            # Propagar insights de alta prioridad
            for iid, info in list(self.insight_catalog.items())[-10:]:
                priority = (info["strength"] + info["validation"]) / 2
                if priority > 0.6:
                    out[f"propagate_{info['type']}_{info['concept']}"] = priority
                    info["propagations"] += 1
            out["insight_catalog_size"]   = min(1.0, len(self.insight_catalog) / 100)
            out["propagation_log_size"]   = min(1.0, len(self.propagation_log) / 100)
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in out.items()}


class DeepReflectionOrchestrator(CognitiveMicelialNeuronBase):
    """Orquesta reflexión profunda y metacognición multi-nivel."""

    def __init__(self, neuron_id: str, depth_levels: int = 5):
        super().__init__(neuron_id, max_synapses=300)
        self.depth_levels     = depth_levels
        self.reflection_states = {f"L{i}": {"active": False, "content": {}} for i in range(depth_levels)}
        self.metacognitive     = {}
        self.deep_insights     = deque(maxlen=30)

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            trigger    = context.get("reflection_trigger", None) if context else None
            meta_flag  = context.get("metacognitive", False) if context else False

            if trigger:
                base = {"contradiction": 3, "novel_insight": 4, "paradigm_shift": 5,
                        "ethical_dilemma": 4, "conceptual_gap": 2}.get(trigger, 1)
                level = min(self.depth_levels - 1, max(0, base + (1 if concentration > 0.8 else 0)))
                self.reflection_states[f"L{level}"]["active"] = True
                self.reflection_states[f"L{level}"]["content"][concept_type] = concentration

            if meta_flag:
                mtype = context.get("metacognitive_type", "monitoring") if context else "monitoring"
                if mtype not in self.metacognitive:
                    self.metacognitive[mtype] = {"concepts": defaultdict(float), "activity": 0.0}
                self.metacognitive[mtype]["concepts"][concept_type] += concentration * 0.1
                self.metacognitive[mtype]["activity"] = (
                    self.metacognitive[mtype]["activity"] * 0.9 + concentration * 0.1
                )

            active_levels = sum(1 for s in self.reflection_states.values() if s["active"])
            self.activation_level = concentration * (active_levels + 1) / (self.depth_levels + 1)
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            out = {}
            for name, state in self.reflection_states.items():
                if state["active"]:
                    avg = sum(state["content"].values()) / max(1, len(state["content"]))
                    out[f"reflection_{name}_intensity"] = avg
                    # Desactivar gradualmente
                    if avg < 0.1:
                        state["active"] = False
            for mtype, data in self.metacognitive.items():
                out[f"meta_{mtype}_activity"] = data["activity"]
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in out.items()}


class InterDomainMessenger(CognitiveMicelialNeuronBase):
    """Mensajero entre dominios cognitivos especializados."""

    def __init__(self, neuron_id: str, specialized_domains: List[str] = None):
        super().__init__(neuron_id, max_synapses=200)
        self.specialized_domains = specialized_domains or ["general"]
        self.message_queue       = deque(maxlen=200)
        self.routing_table       = {}

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            source = context.get("source_domain", "unknown") if context else "unknown"
            dest   = context.get("target_domain", "broadcast") if context else "broadcast"
            msg = {
                "concept": concept_type, "concentration": concentration,
                "source": source, "destination": dest, "ts": time.time(),
            }
            self.message_queue.append(msg)
            self.update_concept(concept_type, concentration)
            relay_boost = 1.2 if (source in self.specialized_domains or
                                   dest in self.specialized_domains) else 0.8
            self.activation_level = min(1.0, concentration * relay_boost)
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            out = {}
            pending = list(self.message_queue)[-20:]
            for msg in pending:
                key = f"relay_{msg['source']}_to_{msg['destination']}_{msg['concept']}"
                out[key] = msg["concentration"]
            out["message_queue_load"] = min(1.0, len(self.message_queue) / 200)
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in out.items()}


class ChemicalLearningNeuron(CognitiveMicelialNeuronBase):
    """Aprendizaje modulado por señales neuroquímicas (dopamina, GABA, etc.)."""

    def __init__(self, neuron_id: str, learning_rate: float = 0.01):
        super().__init__(neuron_id)
        self.learning_rate = learning_rate
        self.neurotransmitters = {
            "dopamine": 0.0, "serotonin": 0.0,
            "acetylcholine": 0.0, "norepinephrine": 0.0, "gaba": 0.0,
        }
        self.synaptic_plasticity = {}

    def _update_nt(self, activation: float):
        nt = self.neurotransmitters
        nt["dopamine"]       = min(1.0, nt["dopamine"] * 0.9 + activation * 0.1)
        nt["serotonin"]      = min(1.0, nt["serotonin"] * 0.95 + activation * 0.05)
        nt["acetylcholine"]  = min(1.0, nt["acetylcholine"] * 0.8 + activation * 0.2)
        nt["norepinephrine"] = min(1.0, nt["norepinephrine"] * 0.7 + activation * 0.3)
        nt["gaba"]           = min(1.0, nt["gaba"] * 0.85 + (1 - activation) * 0.15)

    def _lr_modulation(self) -> float:
        nt  = self.neurotransmitters
        mod = 1.0 * (1.0 + nt["dopamine"] * 0.5) * (1.0 - nt["gaba"] * 0.3)
        return max(0.1, min(5.0, mod))

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            mod = self._lr_modulation()
            try:
                act = 1 / (1 + math.exp(-(concentration * mod) * 10 + 5))
            except OverflowError:
                act = 1.0
            self.activation_level = act
            self._update_nt(act)
            self.update_concept(concept_type, concentration)
            return act

    def process(self, context=None):
        with self.lock:
            out = {f"nt_{k}": v for k, v in self.neurotransmitters.items()}
            out["lr_modulation"] = self._lr_modulation() / 5.0
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in out.items()}


# ═══════════════════════════════════════════════════════════════════════════════
#  CATEGORÍA 2 – NEURONAS BIOLÓGICAMENTE INSPIRADAS (NUEVAS)
# ═══════════════════════════════════════════════════════════════════════════════

# ── 2.1  Hifa de integración (crecimiento apical de hongo) ────────────────
class HyphalIntegratorNeuron(CognitiveMicelialNeuronBase):
    """Neurona de crecimiento hiphal apical.

    Simula el crecimiento direccional de una hifa fúngica: avanza hacia
    gradientes de nutrientes (conceptos de alta concentración) y ramifica
    cuando encuentra resistencia. Biología: Neurospora crassa, Aspergillus.
    """

    def __init__(self, neuron_id: str, growth_rate: float = 0.05,
                 branching_threshold: float = 0.7):
        super().__init__(neuron_id, max_synapses=150)
        self.growth_rate          = growth_rate
        self.branching_threshold  = branching_threshold
        self.tip_concentration    = 0.0   # Concentración en el ápice
        self.branch_count         = 0
        self.growth_history       = deque(maxlen=30)
        self.nutrient_gradient    = defaultdict(float)

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            gradient = context.get("gradient", concentration) if context else concentration
            self.nutrient_gradient[concept_type] = max(
                self.nutrient_gradient.get(concept_type, 0.0), gradient
            )
            # Crecimiento hacia el gradiente más alto
            self.tip_concentration = max(self.tip_concentration,
                                         gradient * self.growth_rate)
            self.tip_concentration = min(1.0, self.tip_concentration)

            # Ramificación al encontrar resistencia
            if concentration > self.branching_threshold and self.branch_count < 10:
                self.branch_count += 1

            self.update_concept(concept_type, concentration)
            self.activation_level = self.tip_concentration
            self.growth_history.append({"concept": concept_type, "grad": gradient, "ts": time.time()})
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            # Dirección de crecimiento: concepto con mayor gradiente
            top = max(self.nutrient_gradient.items(), key=lambda x: x[1], default=("none", 0.0))
            out = {
                "hyphal_tip_activity":        self.tip_concentration * self.cognitive_resilience,
                "hyphal_branch_density":      min(1.0, self.branch_count / 10) * self.cognitive_resilience,
                f"hyphal_target_{top[0]}":    top[1] * self.cognitive_resilience,
                "hyphal_growth_momentum":     (sum(e["grad"] for e in self.growth_history) /
                                               max(1, len(self.growth_history))) * self.cognitive_resilience,
            }
            # Decaimiento del ápice sin nueva señal
            self.tip_concentration *= 0.95
            self.last_activation_time = time.time()
            return out


# ── 2.2  Nodo de anastomosis (fusión de hifas) ────────────────────────────
class AnastomosisNeuron(CognitiveMicelialNeuronBase):
    """Nodo de anastomosis (fusión de hifas).

    Fusiona flujos conceptuales de múltiples fuentes en una sola señal
    integrada, igual que cuando dos hifas se fusionan para compartir
    citoplasma. Biología: Phanerochaete chrysosporium, Neurospora crassa.
    """

    def __init__(self, neuron_id: str, max_inputs: int = 8):
        super().__init__(neuron_id, max_synapses=200)
        self.max_inputs      = max_inputs
        self.input_streams   = {}   # {stream_id: {concept, conc, ts}}
        self.fusion_strength = 0.0

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            stream_id = context.get("stream_id", concept_type[:6]) if context else concept_type[:6]
            self.input_streams[stream_id] = {
                "concept": concept_type, "conc": concentration, "ts": time.time()
            }
            # Limitar entradas
            if len(self.input_streams) > self.max_inputs:
                oldest = min(self.input_streams, key=lambda k: self.input_streams[k]["ts"])
                del self.input_streams[oldest]

            self.update_concept(concept_type, concentration)
            # Activación: promedio ponderado de todas las entradas
            if self.input_streams:
                self.fusion_strength = sum(s["conc"] for s in self.input_streams.values()) / len(self.input_streams)
            self.activation_level = self.fusion_strength
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            out = {
                "anastomosis_fusion_strength": self.fusion_strength * self.cognitive_resilience,
                "anastomosis_input_count":     min(1.0, len(self.input_streams) / self.max_inputs) * self.cognitive_resilience,
            }
            # Señal fusionada por concepto
            concept_sums = defaultdict(list)
            for s in self.input_streams.values():
                concept_sums[s["concept"]].append(s["conc"])
            for concept, vals in concept_sums.items():
                out[f"fused_{concept}"] = (sum(vals) / len(vals)) * self.cognitive_resilience
            self.last_activation_time = time.time()
            return out


# ── 2.3  Gradiente de auxina (señalización vegetal) ───────────────────────
class AuxinGradientNeuron(CognitiveMicelialNeuronBase):
    """Neurona de gradiente de auxina.

    Modela el transporte polar de auxina en plantas para orientar el
    crecimiento conceptual hacia la luz (señales fuertes) y lejos de
    inhibición (señales negativas). Biología: PIN1/AUX1 transportadores
    en Arabidopsis thaliana.
    """

    def __init__(self, neuron_id: str, polar_direction: str = "apical"):
        super().__init__(neuron_id, max_synapses=120)
        self.polar_direction  = polar_direction   # 'apical' | 'basal'
        self.auxin_pool       = 0.0
        self.canalization     = {}   # Rutas preferentes
        self.phototropic_bias = 0.5  # Sesgo hacia señales positivas

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            light_signal  = context.get("light_intensity", concentration) if context else concentration
            gravity_signal = context.get("gravity", 0.5) if context else 0.5

            # Acumulación de auxina según luz y gravedad
            delta_auxin = light_signal * self.phototropic_bias - gravity_signal * (1 - self.phototropic_bias)
            self.auxin_pool = max(0.0, min(1.0, self.auxin_pool + delta_auxin * 0.1))

            # Canalización: refuerza rutas de alto flujo
            route = concept_type[:8]
            self.canalization[route] = min(1.0, self.canalization.get(route, 0.0) + concentration * 0.05)

            self.update_concept(concept_type, concentration)
            self.activation_level = self.auxin_pool
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            top_route = max(self.canalization.items(), key=lambda x: x[1], default=("none", 0.0))
            r = self.cognitive_resilience
            out = {
                "auxin_pool_level":         self.auxin_pool * r,
                f"canalized_route_{top_route[0]}": top_route[1] * r,
                "auxin_canalization_count":  min(1.0, len(self.canalization) / 20) * r,
                "polar_transport_direction": (1.0 if self.polar_direction == "apical" else -1.0) * r,
            }
            # Decaimiento del pool
            self.auxin_pool *= 0.98
            self.last_activation_time = time.time()
            return out


# ── 2.4  Plasmodio colector (Physarum polycephalum) ───────────────────────
class PlasmodiumCollectorNeuron(CognitiveMicelialNeuronBase):
    """Neurona plasmodio colector (Physarum polycephalum).

    Implementa el algoritmo de optimización de red del plasmodio:
    refuerza las venas (rutas conceptuales) por las que fluye más señal
    y debilita las menos usadas. Resuelve rutas cortas en grafos
    conceptuales por optimización biológica.
    """

    def __init__(self, neuron_id: str):
        super().__init__(neuron_id, max_synapses=500)
        self.vein_conductances = defaultdict(lambda: 1.0)   # {(c1,c2): conductance}
        self.flow_history      = deque(maxlen=50)
        self.nutrient_sources  = {}   # {concept: strength}
        self.oscillation_phase = 0.0

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            food_source = context.get("food_source", False) if context else False
            pathway     = context.get("pathway", []) if context else []

            if food_source:
                self.nutrient_sources[concept_type] = concentration

            # Reforzar venas del camino actual
            if len(pathway) >= 2:
                for i in range(len(pathway) - 1):
                    key = tuple(sorted([pathway[i], pathway[i+1]]))
                    self.vein_conductances[key] = min(
                        2.0, self.vein_conductances[key] + concentration * 0.1
                    )

            # Oscilación contráctil (marca temporal del plasmodio)
            self.oscillation_phase = (self.oscillation_phase + 0.1) % (2 * math.pi)
            oscillation = (1 + math.sin(self.oscillation_phase)) / 2

            self.update_concept(concept_type, concentration)
            self.activation_level = concentration * oscillation
            self.flow_history.append({"concept": concept_type, "conc": concentration})
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            # Decaimiento de conductancias no usadas recientemente
            for key in list(self.vein_conductances):
                self.vein_conductances[key] = max(0.1, self.vein_conductances[key] * 0.99)

            top_veins = sorted(self.vein_conductances.items(), key=lambda x: x[1], reverse=True)[:3]
            r = self.cognitive_resilience
            out = {
                "plasmodium_oscillation":  (1 + math.sin(self.oscillation_phase)) / 2 * r,
                "plasmodium_food_sources": min(1.0, len(self.nutrient_sources) / 5) * r,
                "plasmodium_network_size": min(1.0, len(self.vein_conductances) / 50) * r,
            }
            for (c1, c2), cond in top_veins:
                out[f"vein_{c1}_{c2}_conductance"] = min(1.0, cond / 2.0) * r
            self.last_activation_time = time.time()
            return out


# ── 2.5  Mensajero de calcio (onda Ca²⁺) ─────────────────────────────────
class CalciumWaveMessenger(CognitiveMicelialNeuronBase):
    """Mensajero de onda de calcio intercelular.

    Propaga ondas de Ca²⁺ que coordinan respuestas a lo largo del
    micelio/tejido. La onda se inicia ante señales de daño o novedad
    y se propaga decrementalmente. Biología: señalización de Ca²⁺ en
    hongos y plantas (Nicotiana tabacum, Arabidopsis).
    """

    def __init__(self, neuron_id: str, wave_decay: float = 0.15):
        super().__init__(neuron_id, max_synapses=300)
        self.wave_decay       = wave_decay
        self.calcium_level    = 0.0   # [Ca²⁺] intracelular normalizado
        self.wave_active      = False
        self.wave_origin      = ""
        self.wave_propagations = deque(maxlen=20)
        self.refractory_period = 0.0
        self._last_wave_ts    = 0.0

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            now          = time.time()
            is_damage    = context.get("damage_signal", False) if context else False
            is_novelty   = context.get("novelty_signal", False) if context else False

            # Período refractario
            if now - self._last_wave_ts < self.refractory_period:
                self.calcium_level *= 0.9
                self.activation_level = self.calcium_level
                return self.activation_level

            if (is_damage or is_novelty) and concentration > 0.5:
                # Iniciar onda de calcio
                self.calcium_level   = min(1.0, concentration * 1.5)
                self.wave_active     = True
                self.wave_origin     = concept_type
                self._last_wave_ts   = now
                self.refractory_period = 2.0   # 2 s de refractariedad
                self.wave_propagations.append({
                    "origin": concept_type, "strength": self.calcium_level, "ts": now
                })
            else:
                # Recibir onda propagada y atenuar
                incoming = concentration * (1 - self.wave_decay)
                self.calcium_level = max(self.calcium_level, incoming)

            self.update_concept(concept_type, concentration)
            self.activation_level = self.calcium_level
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            # Decaimiento del calcio
            self.calcium_level *= (1 - self.wave_decay * 0.5)
            if self.calcium_level < 0.05:
                self.wave_active = False

            r = self.cognitive_resilience
            out = {
                "ca2_wave_level":        self.calcium_level * r,
                "ca2_wave_active":       (1.0 if self.wave_active else 0.0) * r,
                "ca2_refractory":        min(1.0, max(0.0,
                                              1.0 - (time.time() - self._last_wave_ts) /
                                              max(0.01, self.refractory_period))) * r,
                "ca2_propagation_count": min(1.0, len(self.wave_propagations) / 20) * r,
            }
            self.last_activation_time = time.time()
            return out


# ── 2.6  Nodo de quórum (Quorum Sensing bacteriano) ───────────────────────
class QuorumSensingNeuron(CognitiveMicelialNeuronBase):
    """Neurona de percepción de quórum (Quorum Sensing).

    No actúa hasta que la concentración colectiva de señal supera un umbral
    de quórum (como las bacterias que coordinan comportamiento en masa).
    Por debajo del umbral: silencio. Por encima: activación sincronizada.
    Biología: N-acil-homoserina lactonas en Pseudomonas aeruginosa,
    autoinductor-2 en Vibrio harveyi.
    """

    def __init__(self, neuron_id: str, quorum_threshold: float = 0.65,
                 autoinducer_decay: float = 0.02):
        super().__init__(neuron_id, max_synapses=200)
        self.quorum_threshold  = quorum_threshold
        self.autoinducer_pool  = 0.0   # Concentración de autoinductor
        self.autoinducer_decay = autoinducer_decay
        self.quorum_reached    = False
        self.participant_count = 0

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            # Cada señal recibida aumenta el pool de autoinductor
            self.autoinducer_pool = min(
                1.0, self.autoinducer_pool + concentration * 0.08
            )
            self.participant_count += 1
            self.update_concept(concept_type, concentration)

            # Solo activar si se supera el quórum
            if self.autoinducer_pool >= self.quorum_threshold:
                self.quorum_reached   = True
                self.activation_level = self.autoinducer_pool
            else:
                self.quorum_reached   = False
                self.activation_level = 0.0   # Silencio pre-quórum

            return self.activation_level

    def process(self, context=None):
        with self.lock:
            # Decaimiento del autoinductor
            self.autoinducer_pool = max(0.0, self.autoinducer_pool - self.autoinducer_decay)
            if self.autoinducer_pool < self.quorum_threshold:
                self.quorum_reached = False

            r = self.cognitive_resilience
            out = {
                "quorum_autoinducer":   self.autoinducer_pool * r,
                "quorum_reached":       (1.0 if self.quorum_reached else 0.0) * r,
                "quorum_participants":  min(1.0, self.participant_count / 50) * r,
                "quorum_gap":           max(0.0, self.quorum_threshold - self.autoinducer_pool) * r,
            }
            self.last_activation_time = time.time()
            return out


# ── 2.7  Célula guardiana estomática ──────────────────────────────────────
class StomatalGuardCellNeuron(CognitiveMicelialNeuronBase):
    """Célula guardiana estomática.

    Abre o cierra el 'poro conceptual' que permite la entrada de señales
    del exterior en función de señales ambientales (luz, CO₂, ABA).
    Biología: células oclusivas de Arabidopsis que controlan la apertura
    estomática mediante turgencia regulada por K⁺ y H₂O.
    """

    def __init__(self, neuron_id: str, aperture_sensitivity: float = 0.5):
        super().__init__(neuron_id, max_synapses=100)
        self.aperture_sensitivity = aperture_sensitivity
        self.stomata_aperture     = 0.5   # 0=cerrado, 1=abierto
        self.turgor_pressure      = 0.5
        self.aba_level            = 0.0   # Ácido abscísico (cierre)
        self.co2_level            = 0.5
        self._aperture_history    = deque(maxlen=20)

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            light   = context.get("light",   concentration) if context else concentration
            co2     = context.get("co2",     0.5)           if context else 0.5
            aba     = context.get("aba",     0.0)           if context else 0.0
            self.aba_level  = max(self.aba_level * 0.9, aba)
            self.co2_level  = 0.9 * self.co2_level + 0.1 * co2

            # Regla de apertura: luz abre, ABA cierra, CO₂ alto cierra
            target_aperture = (light * 0.6 - self.aba_level * 0.8 - (self.co2_level - 0.4) * 0.3)
            target_aperture = max(0.0, min(1.0, target_aperture))
            self.stomata_aperture = 0.8 * self.stomata_aperture + 0.2 * target_aperture
            self.turgor_pressure  = 0.5 + 0.5 * self.stomata_aperture

            # Señal pasa solo si el estoma está abierto
            self.update_concept(concept_type, concentration)
            self.activation_level = concentration * self.stomata_aperture
            self._aperture_history.append(self.stomata_aperture)
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            avg_aperture = (sum(self._aperture_history) / max(1, len(self._aperture_history)))
            r = self.cognitive_resilience
            out = {
                "stomata_aperture":        self.stomata_aperture * r,
                "stomata_turgor":          self.turgor_pressure * r,
                "stomata_aba_level":       self.aba_level * r,
                "stomata_avg_aperture":    avg_aperture * r,
                "stomata_gating_signal":   self.activation_level * r,
            }
            self.last_activation_time = time.time()
            return out


# ── 2.8  Sensor de pH conceptual (vacuola fúngica) ───────────────────────
class ConceptualPHSensor(CognitiveMicelialNeuronBase):
    """Sensor de pH conceptual.

    El pH conceptual representa el 'tono' de un espacio de ideas:
    ácido = conceptos negativos/destructivos, básico = constructivos/positivos.
    Biología: vacuolas de hongos regulan pH intracelular; ATPasas de membrana
    de Saccharomyces cerevisiae bombean H⁺ para homeostasis.
    """

    def __init__(self, neuron_id: str, optimal_ph: float = 0.5,
                 buffer_capacity: float = 0.3):
        super().__init__(neuron_id, max_synapses=120)
        self.optimal_ph       = optimal_ph       # 0=muy ácido, 1=muy básico
        self.current_ph       = optimal_ph
        self.buffer_capacity  = buffer_capacity  # Resistencia al cambio de pH
        self.ph_history       = deque(maxlen=30)
        self.proton_pump_rate = 0.05

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            valence = context.get("valence", 0.0) if context else 0.0
            # valence > 0: básico (positivo), < 0: ácido (negativo)
            ph_perturbation = valence * concentration * (1 - self.buffer_capacity)
            self.current_ph = max(0.0, min(1.0, self.current_ph + ph_perturbation))
            self.ph_history.append(self.current_ph)

            # Activación: desviación del pH óptimo activa la bomba de protones
            deviation = abs(self.current_ph - self.optimal_ph)
            self.activation_level = min(1.0, deviation * 2)
            self.update_concept(concept_type, concentration)
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            # Bomba de protones restaura pH óptimo lentamente
            direction = 1.0 if self.current_ph < self.optimal_ph else -1.0
            self.current_ph = max(0.0, min(1.0,
                self.current_ph + direction * self.proton_pump_rate * self.plasticity))

            avg_ph = sum(self.ph_history) / max(1, len(self.ph_history))
            r = self.cognitive_resilience
            out = {
                "ph_current":         self.current_ph * r,
                "ph_deviation":       abs(self.current_ph - self.optimal_ph) * r,
                "ph_avg":             avg_ph * r,
                "ph_pump_activity":   self.activation_level * r,
                "ph_buffer_strength": self.buffer_capacity * r,
            }
            self.last_activation_time = time.time()
            return out


# ── 2.9  Integrador de presión de turgor (célula vegetal) ─────────────────
class TurgorPressureIntegrator(CognitiveMicelialNeuronBase):
    """Integrador de presión de turgor conceptual.

    La turgencia metafórica refleja la 'presión' acumulada de conceptos
    sin procesar. Cuando la turgencia supera un umbral, la célula 'estalla'
    liberando una señal de emergencia. Biología: células vegetales cuya
    turgencia genera fuerza mecánica (Venus atrapamoscas, Mimosa pudica).
    """

    def __init__(self, neuron_id: str, burst_threshold: float = 0.9,
                 wall_rigidity: float = 0.6):
        super().__init__(neuron_id, max_synapses=150)
        self.burst_threshold  = burst_threshold
        self.wall_rigidity    = wall_rigidity   # Rigidez de la pared celular
        self.turgor           = 0.0
        self.burst_count      = 0
        self._last_burst_ts   = 0.0
        self.osmotic_gradient = 0.0

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            osmolyte = context.get("osmolyte_strength", concentration) if context else concentration
            self.osmotic_gradient = 0.9 * self.osmotic_gradient + 0.1 * osmolyte
            # Aumento de turgor por entrada osmótica
            delta_turgor = osmolyte * (1 - self.wall_rigidity) * 0.1
            self.turgor  = min(1.0, self.turgor + delta_turgor)

            self.update_concept(concept_type, concentration)

            # Burst: descarga repentina si se supera el umbral
            if self.turgor >= self.burst_threshold:
                self.activation_level = 1.0
                self.burst_count     += 1
                self._last_burst_ts   = time.time()
                self.turgor           = 0.2   # Alivio de presión
            else:
                self.activation_level = self.turgor
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            # Relajación gradual de turgor
            self.turgor = max(0.0, self.turgor - 0.005 * (1 - self.wall_rigidity))
            r = self.cognitive_resilience
            out = {
                "turgor_pressure":      self.turgor * r,
                "turgor_burst_count":   min(1.0, self.burst_count / 10) * r,
                "turgor_osmotic_grad":  self.osmotic_gradient * r,
                "turgor_wall_rigidity": self.wall_rigidity * r,
                "turgor_burst_ready":   (1.0 if self.turgor > self.burst_threshold * 0.8 else 0.0) * r,
            }
            self.last_activation_time = time.time()
            return out


# ── 2.10  Nodo de resistencia sistémica (SAR vegetal) ────────────────────
class SystemicResistanceNeuron(CognitiveMicelialNeuronBase):
    """Neurona de Resistencia Sistémica Adquirida (SAR).

    Cuando una región del sistema detecta 'patógenos conceptuales' (ideas
    incoherentes, contradicciones), envía señal de alarma sistémica
    (ácido salicílico) que prepara otras regiones para mayor vigilancia.
    Biología: SAR en Arabidopsis, Nicotiana; señalización SA-dependiente.
    """

    def __init__(self, neuron_id: str, sensitivity: float = 0.5):
        super().__init__(neuron_id, max_synapses=200)
        self.sensitivity     = sensitivity
        self.sa_level        = 0.0   # Nivel de ácido salicílico (señal de alarma)
        self.primed_concepts = set()
        self.threat_log      = deque(maxlen=30)

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            threat    = context.get("threat_level", 0.0) if context else 0.0
            pathogen  = context.get("pathogen_signal", False) if context else False

            if pathogen or threat > 0.6:
                # Elevar ácido salicílico
                self.sa_level = min(1.0, self.sa_level + concentration * self.sensitivity)
                self.threat_log.append({
                    "concept": concept_type, "threat": threat, "ts": time.time()
                })
                self.primed_concepts.add(concept_type)

            self.update_concept(concept_type, concentration)
            # Activación proporcional al nivel de SA
            self.activation_level = self.sa_level * concentration
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            # Decaimiento gradual del SA
            self.sa_level = max(0.0, self.sa_level - 0.01)
            r = self.cognitive_resilience
            out = {
                "sar_sa_level":         self.sa_level * r,
                "sar_primed_concepts":  min(1.0, len(self.primed_concepts) / 20) * r,
                "sar_threat_log_size":  min(1.0, len(self.threat_log) / 30) * r,
                "sar_alert_broadcast":  (1.0 if self.sa_level > 0.5 else 0.0) * r,
            }
            self.last_activation_time = time.time()
            return out


# ── 2.11  Oscilador glicolítico (levadura sincronizada) ──────────────────
class GlycolyticOscillatorNeuron(CognitiveMicelialNeuronBase):
    """Oscilador glicolítico conceptual.

    Genera oscilaciones metabólicas intrínsecas que sincronizan el ritmo
    de procesamiento de grupos de neuronas miceliales. Biología:
    oscilaciones glicolíticas en Saccharomyces cerevisiae sincronizadas
    a través de NADH y acetaldehído compartidos.
    """

    def __init__(self, neuron_id: str, period: float = 1.0,
                 coupling_strength: float = 0.3):
        super().__init__(neuron_id, max_synapses=150)
        self.period           = max(0.1, period)   # Período de oscilación (s equiv)
        self.coupling_strength = coupling_strength
        self._phase           = random.uniform(0, 2 * math.pi)
        self._last_tick       = time.time()
        self.nadh_level       = 0.5
        self.phase_history    = deque(maxlen=30)
        self.coupled_phases   = []   # Fases de osciladores vecinos

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            now   = time.time()
            dt    = now - self._last_tick
            self._last_tick = now
            # Avanzar fase
            self._phase = (self._phase + 2 * math.pi * dt / self.period) % (2 * math.pi)
            # Acoplamiento con vecinos (promedio de Kuramoto simplificado)
            if context and "neighbor_phase" in context:
                neighbor_phase = context["neighbor_phase"]
                self.coupled_phases.append(neighbor_phase)
                if len(self.coupled_phases) > 5:
                    self.coupled_phases = self.coupled_phases[-5:]
                coupling_term = (self.coupling_strength *
                                 math.sin(neighbor_phase - self._phase))
                self._phase = (self._phase + coupling_term) % (2 * math.pi)

            # NADH oscila con la glicólisis
            self.nadh_level = 0.5 + 0.5 * math.sin(self._phase)
            self.activation_level = self.nadh_level * concentration
            self.phase_history.append(self._phase)
            self.update_concept(concept_type, concentration)
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            r = self.cognitive_resilience
            out = {
                "glyco_phase":          (self._phase / (2 * math.pi)) * r,
                "glyco_nadh":           self.nadh_level * r,
                "glyco_oscillation":    self.activation_level * r,
                "glyco_period":         min(1.0, 1.0 / self.period) * r,
                "glyco_coupled_count":  min(1.0, len(self.coupled_phases) / 5) * r,
            }
            self.last_activation_time = time.time()
            return out


# ── 2.12  Célula de Schwann conceptual (soporte y mielinización) ──────────
class SchawnConceptualCell(CognitiveMicelialNeuronBase):
    """Célula de Schwann conceptual.

    No procesa señales directamente sino que las envuelve, amplifica y
    protege: aumenta la velocidad de conducción de señales conceptuales
    adyacentes mediante 'mielinización cognitiva'. Biología: células de
    Schwann que forman la vaina de mielina del SNP.
    """

    def __init__(self, neuron_id: str, myelination_rate: float = 0.01):
        super().__init__(neuron_id, max_synapses=100)
        self.myelination_rate  = myelination_rate
        self.myelin_sheath     = {}   # {neuron_id: myelination_level}
        self.supported_neurons = set()
        self.node_of_ranvier   = defaultdict(float)   # Saltos de señal
        self.metabolic_support = 0.8   # Soporte metabólico a vecinos

    def receive_concept(self, concentration, concept_type, context=None):
        with self.lock:
            target_neuron = context.get("target_neuron_id", "") if context else ""
            if target_neuron:
                current = self.myelin_sheath.get(target_neuron, 0.0)
                self.myelin_sheath[target_neuron] = min(
                    1.0, current + self.myelination_rate * self.plasticity
                )
                self.supported_neurons.add(target_neuron)

            # Amplificar señal conceptual según mielinización promedio
            avg_myelin = (sum(self.myelin_sheath.values()) /
                          max(1, len(self.myelin_sheath)))
            amplification  = 1.0 + avg_myelin
            self.activation_level = min(1.0, concentration * amplification * 0.5)
            self.update_concept(concept_type, concentration)
            return self.activation_level

    def process(self, context=None):
        with self.lock:
            avg_myelin = (sum(self.myelin_sheath.values()) /
                          max(1, len(self.myelin_sheath)))
            r = self.cognitive_resilience
            out = {
                "schwann_avg_myelination":    avg_myelin * r,
                "schwann_supported_neurons":  min(1.0, len(self.supported_neurons) / 10) * r,
                "schwann_metabolic_support":  self.metabolic_support * r,
                "schwann_conduction_boost":   (1.0 + avg_myelin) * 0.5 * r,
            }
            # Mantenimiento gradual de mielina
            for nid in list(self.myelin_sheath):
                self.myelin_sheath[nid] = max(0.0, self.myelin_sheath[nid] - 0.0001)
            self.last_activation_time = time.time()
            return out


# ═══════════════════════════════════════════════════════════════════════════════
#  FÁBRICA
# ═══════════════════════════════════════════════════════════════════════════════

def create_cognitive_micelial_neuron(neuron_type: str, neuron_id: str,
                                     **kwargs) -> CognitiveMicelialNeuronBase:
    """Fábrica para crear neuronas miceliales cognitivas por tipo."""
    neuron_classes: Dict[str, type] = {
        # ── Tipos originales ──────────────────────────────────────────────
        "abstract_pattern_integrator":       AbstractPatternIntegrator,
        "contextual_temporal_integrator":    ContextualTemporalIntegrator,
        "knowledge_synthesizer":             KnowledgeSynthesizer,
        "global_coherence_coordinator":      GlobalCoherenceCoordinator,
        "conceptual_bridge_builder":         ConceptualBridgeBuilder,
        "insight_propagator":                InsightPropagator,
        "deep_reflection_orchestrator":      DeepReflectionOrchestrator,
        "inter_domain_messenger":            InterDomainMessenger,
        "chemical_learning_neuron":          ChemicalLearningNeuron,
        # ── Biológicamente inspiradas (nuevas) ────────────────────────────
        "hyphal_integrator":                 HyphalIntegratorNeuron,
        "anastomosis_node":                  AnastomosisNeuron,
        "auxin_gradient":                    AuxinGradientNeuron,
        "plasmodium_collector":              PlasmodiumCollectorNeuron,
        "calcium_wave_messenger":            CalciumWaveMessenger,
        "quorum_sensing_node":               QuorumSensingNeuron,
        "stomatal_guard_cell":               StomatalGuardCellNeuron,
        "conceptual_ph_sensor":              ConceptualPHSensor,
        "turgor_pressure_integrator":        TurgorPressureIntegrator,
        "systemic_resistance_node":          SystemicResistanceNeuron,
        "glycolytic_oscillator":             GlycolyticOscillatorNeuron,
        "schwann_conceptual_cell":           SchawnConceptualCell,
    }

    if neuron_type not in neuron_classes:
        raise ValueError(
            f"Tipo desconocido: '{neuron_type}'.\n"
            f"Disponibles: {sorted(neuron_classes.keys())}"
        )
    return neuron_classes[neuron_type](neuron_id, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
#  MANTENIMIENTO DE RED
# ═══════════════════════════════════════════════════════════════════════════════

class CognitiveMicelialNetworkMaintenance:
    """Mantenimiento de la red micelial cognitiva.
    Sin poda. Sin tiempo de vida. Sin memoria persistente.
    """

    def __init__(self):
        self.neurons: List[CognitiveMicelialNeuronBase] = []
        self.maintenance_interval = 60.0
        self.last_maintenance     = time.time()
        self.network_coherence_score = 0.9

    def add_neuron(self, neuron: CognitiveMicelialNeuronBase):
        self.neurons.append(neuron)

    def run_maintenance_cycle(self):
        now  = time.time()
        dt   = now - self.last_maintenance
        for n in self.neurons:
            n.age_neuron(dt)
        self._maintain_global_cognitive_coherence()
        self.last_maintenance = now

    def _maintain_global_cognitive_coherence(self):
        if not self.neurons:
            return
        # Varianza de resiliencia como proxy de coherencia
        res = [n.cognitive_resilience for n in self.neurons]
        mean = sum(res) / len(res)
        var  = sum((r - mean) ** 2 for r in res) / len(res)
        self.network_coherence_score = max(0.0, 1.0 - var * 2)

    def get_network_stats(self) -> Dict[str, Any]:
        stats: Dict[str, Any] = {
            "total_neurons":      len(self.neurons),
            "network_coherence":  self.network_coherence_score,
            "average_age":        0.0,
            "average_resilience": 0.0,
            "total_concepts":     0,
            "neuron_types":       defaultdict(int),
        }
        if self.neurons:
            stats["average_age"]       = sum(n.age for n in self.neurons) / len(self.neurons)
            stats["average_resilience"] = sum(n.cognitive_resilience for n in self.neurons) / len(self.neurons)
            for n in self.neurons:
                stats["total_concepts"] += len(n.concept_concentration)
                stats["neuron_types"][n.__class__.__name__] += 1
        return stats


# ═══════════════════════════════════════════════════════════════════════════════
#  DEMOSTRACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def create_cognitive_micelial_network(
    config: Dict[str, Any]
) -> List[CognitiveMicelialNeuronBase]:
    """Crea una red micelial cognitiva a partir de una configuración."""
    network = []
    for ntype, count in config.items():
        clean_type = ntype.rstrip("s")
        for i in range(count):
            nid = f"{clean_type}_{len(network)+1:03d}"
            try:
                n = create_cognitive_micelial_neuron(clean_type, nid)
                network.append(n)
            except Exception as e:
                log_event(f"Error creando {nid}: {e}", "WARNING")
    return network


def demonstrate_cognitive_micelial_system():
    """Demostración del sistema de neuronas miceliales cognitivas."""
    import time as _t
    print("=" * 60)
    print("SISTEMA DE NEURONAS MICELIALES COGNITIVAS")
    print("=" * 60)

    maintenance = CognitiveMicelialNetworkMaintenance()
    inicio = _t.time()

    # Crear una neurona de cada tipo
    types_to_demo = [
        ("abstract_pattern_integrator",    "api_001"),
        ("contextual_temporal_integrator", "cti_001"),
        ("knowledge_synthesizer",          "ks_001"),
        ("global_coherence_coordinator",   "gcc_001"),
        ("conceptual_bridge_builder",      "cbb_001"),
        ("insight_propagator",             "ip_001"),
        ("deep_reflection_orchestrator",   "dro_001"),
        ("inter_domain_messenger",         "idm_001"),
        ("chemical_learning_neuron",       "cln_001"),
        # Nuevas biológicas
        ("hyphal_integrator",              "hyph_001"),
        ("anastomosis_node",               "anast_001"),
        ("auxin_gradient",                 "auxin_001"),
        ("plasmodium_collector",           "plas_001"),
        ("calcium_wave_messenger",         "ca2_001"),
        ("quorum_sensing_node",            "qs_001"),
        ("stomatal_guard_cell",            "stom_001"),
        ("conceptual_ph_sensor",           "ph_001"),
        ("turgor_pressure_integrator",     "turg_001"),
        ("systemic_resistance_node",       "sar_001"),
        ("glycolytic_oscillator",          "glyco_001"),
        ("schwann_conceptual_cell",        "sch_001"),
    ]

    network = []
    for ntype, nid in types_to_demo:
        n = create_cognitive_micelial_neuron(ntype, nid)
        network.append(n)
        maintenance.add_neuron(n)

    print(f"\n✓ Red creada: {len(network)} neuronas\n")
    print("── Activaciones de muestra ─────────────────────────────────")

    tests = [
        ("api_001",   0.8, "consciousness",      {"abstraction_level": 4, "related_concepts": ["awareness"]}),
        ("gcc_001",   0.9, "premise_A",           {"reasoning_thread": "t1", "logical_role": "premise"}),
        ("cbb_001",   0.7, "neural_nets",         {"domain": "cs", "semantic_features": ["network", "learning"]}),
        ("ip_001",    0.8, "emergence",            {"insight_type": "discovery", "validation": 0.9}),
        ("hyph_001",  0.7, "nutrient_concept",    {"gradient": 0.8}),
        ("anast_001", 0.6, "stream_A",            {"stream_id": "s1"}),
        ("auxin_001", 0.8, "growth_signal",       {"light_intensity": 0.9, "gravity": 0.3}),
        ("plas_001",  0.7, "food_source",         {"food_source": True, "pathway": ["a","b","c"]}),
        ("ca2_001",   0.9, "damage_signal",       {"damage_signal": True}),
        ("qs_001",    0.7, "quorum_signal",       {}),
        ("stom_001",  0.8, "light_signal",        {"light": 0.9, "co2": 0.3, "aba": 0.1}),
        ("ph_001",    0.6, "acidic_concept",      {"valence": -0.8}),
        ("turg_001",  0.9, "pressure_concept",   {"osmolyte_strength": 0.85}),
        ("sar_001",   0.8, "threat_concept",      {"threat_level": 0.9, "pathogen_signal": True}),
        ("glyco_001", 0.7, "metabolic_rhythm",   {}),
        ("sch_001",   0.6, "support_signal",      {"target_neuron_id": "hyph_001"}),
    ]

    for nid, conc, concept, ctx in tests:
        n = next((x for x in network if x.neuron_id == nid), None)
        if n:
            act  = n.receive_concept(conc, concept, ctx)
            out  = n.process(ctx)
            label = n.__class__.__name__
            print(f"  {label:<38} act={act:.3f}  salidas={len(out)}")

    maintenance.run_maintenance_cycle()
    stats = maintenance.get_network_stats()

    print("\n── Estadísticas de red ─────────────────────────────────────")
    print(f"  Neuronas totales:     {stats['total_neurons']}")
    print(f"  Coherencia de red:    {stats['network_coherence']:.3f}")
    print(f"  Resiliencia promedio: {stats['average_resilience']:.3f}")
    print(f"  Conceptos totales:    {stats['total_concepts']}")
    print(f"  Subtipos únicos:      {len(stats['neuron_types'])}")
    print(f"  Tiempo total:         {_t.time() - inicio:.4f} s")
    print("\n✓ Listo para integración con neuronas animales.")
    return network, maintenance


if __name__ == "__main__":
    try:
        network, maintenance = demonstrate_cognitive_micelial_system()
        print(f"\nSistema completo inicializado con {len(network)} neuronas miceliales.")
        print("Listo para pensamiento híbrido con neuronas animales.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    
    bridge_output = bridge_builder.process()
    print(f"  - Puentes propuestos: {len(bridge_output)} conexiones conceptuales")
    
    # Ejecutar mantenimiento
    print(f"\n4. Ejecutando mantenimiento de red...")
    maintenance_system.run_maintenance_cycle()
    stats = maintenance_system.get_network_stats()
    
    print(f"  - Coherencia de red: {stats['network_coherence']:.3f}")
    print(f"  - Conceptos totales: {stats['total_concepts']}")
    print(f"  - Resilience promedio: {stats['average_resilience']:.3f}")
    
    print(f"\n=== Sistema Cognitivo Micelial Listo ===")
    print("Optimizado para:")
    print("  ✓ Integración conceptual profunda")
    print("  ✓ Mantenimiento de coherencia lógica")
    print("  ✓ Construcción de puentes entre dominios")
    print("  ✓ Propagación de insights")
    print("  ✓ Reflexión metacognitiva")
    print("  ✓ Comunicación inter-dominio")
    print("  ✓ Longevidad de conocimiento")
    
    return network, maintenance_system


if __name__ == "__main__":
    # Ejecutar demostración
    network, maintenance = demonstrate_cognitive_micelial_system()
    
    print(f"\nSistema completo inicializado con {len(network)} neuronas cognitivas.")
    print("Listo para integración con neuronas animales para pensamiento híbrido.")
