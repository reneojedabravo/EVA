# mind.py
"""
Mente Fluida — Arquitectura de Consciencia No-Tripartita.

La mente no tiene tres compartimentos fijos. Tiene niveles de luminosidad:
algunos pensamientos están en plena luz, otros en penumbra, otros en
oscuridad total. Entre ellos hay puentes, guardianes, orquestadores y
regiones que la mente aísla para protegerse — pero que siguen ejerciendo
influencia sutil desde la sombra.

Capas de luminosidad:
  FOCAL       — lo que está en el centro de la atención consciente
  PERIPHERAL  — lo que rodea al foco: semi-consciente, listo para emerger
  SUBMERGED   — procesamiento paralelo: patrones, intuiciones, asociaciones
  DEEP        — estructuras profundas: identidad, valores, traumas, instintos
  SHADOW      — lo que la mente aísla conscientemente (sutil, pero presente)

Estructuras especiales:
  MindBridge       — puentes entre capas (bidireccionales, graduales)
  Orchestrator     — coordina qué capa domina en cada momento
  Guardian         — protege regiones del yo; filtra señales amenazantes
  IsolationCell    — contiene material que la mente decidió aislar

Integración completa:
  ─ Neuronas animales + miceliales + sinapsis (synapse.py)
  ─ Emociones + instintos (adaptive.py)
  ─ Memoria con huella emocional (memory.py + memory_persistence.py)
"""

from __future__ import annotations

import math
import random
import time
import hashlib
import traceback
from collections import deque, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock, Thread
from typing import Any, Dict, List, Optional, Tuple

# ── Ecosistema neuronal ───────────────────────────────────────────────────────
from monitoring import log_event, log_neuron_error
from animal    import create_cognitive_animal_neuron,   CognitiveAnimalNeuronBase
from micelial  import create_cognitive_micelial_neuron, CognitiveMicelialNeuronBase
from synapse   import SynapseManager
from adaptive  import (AdaptiveCore, EmotionEngine, InstinctCore,
                        InstinctID, EmotionID)
from memory    import MemoryManager, EmotionalStamp, MemoryLayer, _build_demo_memory
from memory_persistence import MemoryPersistence


# ═══════════════════════════════════════════════════════════════════════════════
#  ENUMERACIONES Y CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════

class LuminosityLayer(Enum):
    FOCAL      = "focal"       # plena atención consciente
    PERIPHERAL = "peripheral"  # semi-consciente, listo para emerger
    SUBMERGED  = "submerged"   # procesamiento paralelo, intuiciones
    DEEP       = "deep"        # identidad, valores, instintos
    SHADOW     = "shadow"      # aislado; influencia sutil

# Permeabilidad entre capas (cuánto puede pasar entre ellas)
_LAYER_PERMEABILITY: Dict[Tuple[LuminosityLayer, LuminosityLayer], float] = {
    (LuminosityLayer.FOCAL,      LuminosityLayer.PERIPHERAL): 0.85,
    (LuminosityLayer.PERIPHERAL, LuminosityLayer.FOCAL):      0.70,
    (LuminosityLayer.PERIPHERAL, LuminosityLayer.SUBMERGED):  0.60,
    (LuminosityLayer.SUBMERGED,  LuminosityLayer.PERIPHERAL): 0.45,
    (LuminosityLayer.SUBMERGED,  LuminosityLayer.DEEP):       0.30,
    (LuminosityLayer.DEEP,       LuminosityLayer.SUBMERGED):  0.20,
    (LuminosityLayer.SHADOW,     LuminosityLayer.DEEP):       0.05,  # sutil
    (LuminosityLayer.SHADOW,     LuminosityLayer.SUBMERGED):  0.02,  # muy sutil
}

# Neuronas que habitan cada capa
_LAYER_ANIMAL_NEURONS = {
    LuminosityLayer.FOCAL:      [("attention_focuser", {}),
                                  ("decision_maker", {}),
                                  ("self_monitor", {})],
    LuminosityLayer.PERIPHERAL: [("visual_feature_extractor", {"feature_type": "motion"}),
                                  ("anomaly_detector", {}),
                                  ("selective_attention_filter", {})],
    LuminosityLayer.SUBMERGED:  [("place_cell", {"preferred_location": (0.5, 0.5)}),
                                  ("mirror_neuron", {"action_class": "grasp"}),
                                  ("pattern_recognizer", {})],
    LuminosityLayer.DEEP:       [("dopaminergic_modulator", {}),
                                  ("nociceptor", {"pain_type": "mechanical"}),
                                  ("adaptive_threshold_cell", {})],
    LuminosityLayer.SHADOW:     [("pause_interneuron", {}),
                                  ("receptive_field_cell", {"polarity": "OFF"})],
}

_LAYER_MICELIAL_NEURONS = {
    LuminosityLayer.FOCAL:      [("global_coherence_coordinator", {}),
                                  ("knowledge_synthesizer",
                                   {"domain_specializations": ["identity","emotion"]})],
    LuminosityLayer.PERIPHERAL: [("abstract_pattern_integrator", {}),
                                  ("conceptual_bridge_builder", {})],
    LuminosityLayer.SUBMERGED:  [("insight_propagator", {}),
                                  ("anastomosis_node", {}),
                                  ("glycolytic_oscillator", {})],
    LuminosityLayer.DEEP:       [("deep_reflection_orchestrator", {}),
                                  ("systemic_resistance_node", {}),
                                  ("plasmodium_collector", {})],
    LuminosityLayer.SHADOW:     [("calcium_wave_messenger", {}),
                                  ("conceptual_ph_sensor", {})],
}


# ═══════════════════════════════════════════════════════════════════════════════
#  ESTRUCTURAS DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MindSignal:
    """Señal que viaja entre capas de la mente."""
    content:    str
    tags:       List[str]
    origin:     LuminosityLayer
    strength:   float          # 0..1
    valence:    float          # −1..+1
    arousal:    float          # 0..1
    instinct:   str = ""
    ts:         float = field(default_factory=time.time)
    path:       List[str] = field(default_factory=list)  # capas atravesadas

    def attenuate(self, factor: float) -> "MindSignal":
        return MindSignal(
            content=self.content, tags=self.tags,
            origin=self.origin,
            strength=max(0.0, self.strength * factor),
            valence=self.valence, arousal=self.arousal,
            instinct=self.instinct, ts=self.ts,
            path=list(self.path),
        )

    def to_emotional_stamp(self) -> EmotionalStamp:
        return EmotionalStamp(
            valence=self.valence, arousal=self.arousal,
            instinct_tags=[self.instinct] if self.instinct else [],
        )


@dataclass
class IsolatedContent:
    """Contenido aislado en Shadow layer. Tiene influencia sutil residual."""
    content_id: str
    content:    str
    reason:     str       # por qué fue aislado
    valence:    float
    arousal:    float
    isolation_ts: float   = field(default_factory=time.time)
    leak_rate:  float     = 0.03   # qué tan fuerte es la influencia residual
    access_count: int     = 0
    symbolic_form: str    = ""


# ═══════════════════════════════════════════════════════════════════════════════
#  PUENTE ENTRE CAPAS
# ═══════════════════════════════════════════════════════════════════════════════

class MindBridge:
    """Puente bidireccional entre dos capas de luminosidad.

    Los puentes no son siempre activos: su apertura depende del estado
    emocional, del arousal y de si el orquestador lo permite.
    Un puente cerrado no bloquea completamente — todavía filtra señales
    muy fuertes (umbral de emergencia).
    """

    EMERGENCY_THRESHOLD = 0.85   # señal tan fuerte que pasa aunque el puente esté cerrado

    def __init__(self, layer_a: LuminosityLayer, layer_b: LuminosityLayer,
                 synapse_mgr: SynapseManager,
                 neuron_a, neuron_b):
        self.layer_a     = layer_a
        self.layer_b     = layer_b
        self.synapse_mgr = synapse_mgr
        self.neuron_a    = neuron_a
        self.neuron_b    = neuron_b
        self.aperture    = 0.5    # 0=cerrado, 1=completamente abierto
        self._lock       = RLock()
        self.crossings   = 0
        self.last_signal: Optional[MindSignal] = None

        # Sinapsis del puente (bidireccional)
        kind = "electrical" if (layer_a in (LuminosityLayer.FOCAL, LuminosityLayer.PERIPHERAL)
                                and layer_b in (LuminosityLayer.FOCAL, LuminosityLayer.PERIPHERAL)) \
               else "hybrid"
        if neuron_a and neuron_b:
            self.syn_a_to_b = synapse_mgr.connect(
                neuron_a, neuron_b, kind, "excitatory", persistent=True)
            self.syn_b_to_a = synapse_mgr.connect(
                neuron_b, neuron_a, kind, "modulatory", persistent=True)
        else:
            self.syn_a_to_b = None
            self.syn_b_to_a = None

    def set_aperture(self, value: float):
        with self._lock:
            self.aperture = max(0.0, min(1.0, value))

    def transmit(self, signal: MindSignal,
                 direction: str = "a_to_b") -> Optional[MindSignal]:
        """Transmite una señal a través del puente."""
        with self._lock:
            permeability = _LAYER_PERMEABILITY.get(
                (signal.origin, self.layer_b if direction == "a_to_b"
                 else self.layer_a), 0.1)

            effective_aperture = self.aperture * permeability

            # Emergencia: señales muy fuertes pasan aunque el puente esté cerrado
            if signal.strength >= self.EMERGENCY_THRESHOLD:
                effective_aperture = max(effective_aperture, 0.3)

            if signal.strength * effective_aperture < 0.05:
                return None

            # Transmitir por sinapsis
            syn = self.syn_a_to_b if direction == "a_to_b" else self.syn_b_to_a
            out_strength = signal.strength * effective_aperture
            if syn:
                ctx = {"neuromodulator": "dopamine", "nm_level": signal.arousal,
                       "concept": signal.content[:20], "pattern": "bridge_pass"}
                try:
                    syn.transmit(out_strength, ctx)
                except Exception:
                    pass

            attenuated = signal.attenuate(effective_aperture)
            attenuated.path.append(f"{self.layer_a.value}→{self.layer_b.value}")
            self.crossings += 1
            self.last_signal = attenuated
            return attenuated


# ═══════════════════════════════════════════════════════════════════════════════
#  GUARDIÁN
# ═══════════════════════════════════════════════════════════════════════════════

class Guardian:
    """Guardián de una región de la mente.

    Protege capas sensibles filtrando señales amenazantes. No bloquea
    completamente — las señales que pasan simplemente llegan atenuadas y
    marcadas. El guardián aprende: si una señal pasó y causó daño
    (arousal muy alto + valence muy negativa), aumenta su umbral.
    """

    def __init__(self, protected_layer: LuminosityLayer):
        self.protected   = protected_layer
        self.threshold   = 0.55   # umbral de valencia negativa para activarse
        self.sensitivity = 0.7
        self._activations = 0
        self._lock        = RLock()
        self._history     = deque(maxlen=50)

    def filter(self, signal: MindSignal) -> Tuple[MindSignal, bool]:
        """Filtra una señal. Retorna (señal_filtrada, fue_intervenida)."""
        with self._lock:
            # Condición de activación: señal amenazante
            threat = (-signal.valence * signal.arousal *
                      (1.0 if signal.instinct in ("survive","flee","defend") else 0.5))

            if threat > self.threshold:
                self._activations += 1
                # Atenuar la señal pero no bloquearla
                attenuation = max(0.15, 1.0 - threat * self.sensitivity)
                filtered    = signal.attenuate(attenuation)
                self._history.append({"threat": round(threat, 3),
                                       "attenuation": round(attenuation, 3),
                                       "ts": time.time()})
                # Aprendizaje: si el daño fue alto, aumentar sensibilidad
                if threat > 0.8:
                    self.sensitivity = min(0.95, self.sensitivity + 0.02)
                return filtered, True
            return signal, False

    @property
    def activations(self) -> int:
        return self._activations


# ═══════════════════════════════════════════════════════════════════════════════
#  CELDA DE AISLAMIENTO (Shadow)
# ═══════════════════════════════════════════════════════════════════════════════

class IsolationCell:
    """Contiene material que la mente decidió aislar.

    El material aislado no está inerte: filtra sutilmente hacia las capas
    adyacentes con una tasa de goteo (leak_rate) muy baja. Esta influencia
    residual puede colorear el estado emocional sin que la mente sea
    consciente de la fuente.
    """

    def __init__(self):
        self._lock    = RLock()
        self._contents: Dict[str, IsolatedContent] = {}
        self._leak_log = deque(maxlen=100)

    def isolate(self, content: str, reason: str,
                valence: float, arousal: float,
                leak_rate: float = 0.03) -> str:
        cid = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:10]
        # Forma simbólica
        symbols = {-1.0: "oscuridad_densa", -0.5: "niebla_gris",
                    0.0: "espejo_roto", 0.5: "luz_velada", 1.0: "llama_contenida"}
        closest = min(symbols.keys(), key=lambda k: abs(k - valence))
        ic = IsolatedContent(
            content_id=cid, content=content, reason=reason,
            valence=valence, arousal=arousal,
            leak_rate=leak_rate, symbolic_form=symbols[closest],
        )
        with self._lock:
            self._contents[cid] = ic
        return cid

    def get_residual_influence(self) -> Dict[str, float]:
        """Calcula la influencia residual total del contenido aislado."""
        with self._lock:
            if not self._contents:
                return {"valence_leak": 0.0, "arousal_leak": 0.0,
                        "instinct_pressure": 0.0}
            total_v, total_a, total_pressure = 0.0, 0.0, 0.0
            for ic in self._contents.values():
                age_factor = max(0.1, 1.0 - (time.time() - ic.isolation_ts) / 3600)
                leak = ic.leak_rate * age_factor
                total_v       += ic.valence * leak
                total_a       += ic.arousal * leak
                total_pressure += leak
            n = max(1, len(self._contents))
            result = {
                "valence_leak":    round(total_v / n, 4),
                "arousal_leak":    round(total_a / n, 4),
                "instinct_pressure": round(total_pressure, 4),
            }
            self._leak_log.append({"ts": time.time(), **result})
            return result

    def get_all(self) -> List[IsolatedContent]:
        with self._lock:
            return list(self._contents.values())

    def stats(self) -> Dict:
        with self._lock:
            return {
                "isolated_count": len(self._contents),
                "avg_valence":    round(
                    sum(ic.valence for ic in self._contents.values()) /
                    max(1, len(self._contents)), 3),
                "total_leak_events": len(self._leak_log),
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  ORQUESTADOR INTERNO
# ═══════════════════════════════════════════════════════════════════════════════

class MindOrchestrator:
    """Orquestador interno de la mente.

    Decide en cada momento qué capa domina, qué puentes abrir,
    y cómo integrar señales de múltiples capas. No es "el yo" —
    es el proceso que coordina el yo sin ser consciente de sí mismo.
    """

    def __init__(self, bridges: Dict[str, MindBridge],
                 guardians: Dict[LuminosityLayer, Guardian]):
        self._bridges  = bridges
        self._guardians = guardians
        self._lock     = RLock()
        self._dominant = LuminosityLayer.FOCAL
        self._history  = deque(maxlen=200)
        self._cycles   = 0

    def orchestrate(self, emotion: EmotionEngine,
                    instinct: InstinctCore,
                    isolation: IsolationCell) -> Dict[str, Any]:
        """Ciclo de orquestación: ajusta apertura de puentes y dominancia."""
        with self._lock:
            self._cycles += 1
            valence = emotion.valence
            arousal = emotion.arousal
            dom_inst = instinct.get_dominant()
            inst_name = dom_inst.value if dom_inst else ""

            # Decidir capa dominante
            prev_dominant = self._dominant
            if arousal > 0.8 and inst_name in ("survive", "flee", "defend"):
                self._dominant = LuminosityLayer.DEEP      # instinto toma el control
            elif arousal > 0.6 and abs(valence) > 0.5:
                self._dominant = LuminosityLayer.SUBMERGED # emoción fuerte → intuición
            elif arousal < 0.3 and abs(valence) < 0.2:
                self._dominant = LuminosityLayer.PERIPHERAL # calma → periferia activa
            else:
                self._dominant = LuminosityLayer.FOCAL     # estado normal

            # Ajustar apertura de puentes según estado
            self._adjust_bridges(valence, arousal, inst_name)

            # Influencia residual del Shadow
            residual = isolation.get_residual_influence()
            shadow_mod = residual["valence_leak"] * 0.2

            report = {
                "dominant_layer":   self._dominant.value,
                "prev_dominant":    prev_dominant.value,
                "layer_changed":    self._dominant != prev_dominant,
                "shadow_influence": round(residual["instinct_pressure"], 4),
                "bridge_apertures": {k: round(b.aperture, 3)
                                     for k, b in self._bridges.items()},
                "cycle":            self._cycles,
            }
            self._history.append(report)
            return report

    def _adjust_bridges(self, valence: float, arousal: float, inst: str):
        """Abre/cierra puentes según el estado mental."""
        # Puente focal↔peripheral: más abierto en estado normal
        for key, bridge in self._bridges.items():
            a_name = bridge.layer_a.value
            b_name = bridge.layer_b.value

            if "focal" in (a_name, b_name) and "peripheral" in (a_name, b_name):
                bridge.set_aperture(0.8 - arousal * 0.3)

            elif "submerged" in (a_name, b_name):
                # Más abierto cuando hay alta emoción
                bridge.set_aperture(min(0.9, 0.3 + abs(valence) * 0.5 + arousal * 0.2))

            elif "deep" in (a_name, b_name):
                # Instintos abrirán el puente con el profundo
                if inst in ("survive", "flee", "defend", "feed"):
                    bridge.set_aperture(min(0.9, 0.5 + arousal * 0.4))
                else:
                    bridge.set_aperture(max(0.1, 0.3 - arousal * 0.1))

            elif "shadow" in (a_name, b_name):
                # Shadow casi siempre cerrado; se abre levemente en calma profunda
                bridge.set_aperture(0.05 if arousal > 0.4 else 0.12)

    @property
    def dominant(self) -> LuminosityLayer:
        return self._dominant

    def get_status(self) -> Dict:
        with self._lock:
            return {
                "dominant_layer": self._dominant.value,
                "total_cycles":   self._cycles,
                "bridge_states":  {k: {"aperture": round(b.aperture, 3),
                                        "crossings": b.crossings}
                                    for k, b in self._bridges.items()},
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  CAPA DE LUMINOSIDAD
# ═══════════════════════════════════════════════════════════════════════════════

class MindLayer:
    """Una capa de la mente con sus neuronas, sinapsis y señales activas."""

    def __init__(self, layer: LuminosityLayer, synapse_mgr: SynapseManager):
        self.layer       = layer
        self.syn_mgr     = synapse_mgr
        self._lock       = RLock()
        self.animals:    List[CognitiveAnimalNeuronBase]   = []
        self.micelials:  List[CognitiveMicelialNeuronBase] = []
        self.signal_queue: deque = deque(maxlen=30)
        self.processed    = 0
        self._activation_avg = 0.0

    def build(self):
        """Construye las neuronas de esta capa."""
        for ntype, kwargs in _LAYER_ANIMAL_NEURONS.get(self.layer, []):
            nid = f"{self.layer.value[:3].upper()}A_{ntype[:8]}"
            try:
                n = create_cognitive_animal_neuron(ntype, nid, **kwargs)
                self.animals.append(n)
            except Exception as e:
                log_neuron_error(nid, f"MindLayer.build animal: {e}")

        for ntype, kwargs in _LAYER_MICELIAL_NEURONS.get(self.layer, []):
            nid = f"{self.layer.value[:3].upper()}M_{ntype[:8]}"
            try:
                n = create_cognitive_micelial_neuron(ntype, nid, **kwargs)
                self.micelials.append(n)
            except Exception as e:
                log_neuron_error(nid, f"MindLayer.build micelial: {e}")

        # Conectar neuronas dentro de la capa
        for i in range(len(self.animals) - 1):
            self.syn_mgr.connect(self.animals[i], self.animals[i+1],
                                 "electrical", "excitatory", persistent=True)
        for i in range(len(self.micelials) - 1):
            self.syn_mgr.connect(self.micelials[i], self.micelials[i+1],
                                 "chemical", "excitatory", persistent=True)
        # Conexiones híbridas intra-capa
        n_cross = min(2, len(self.animals), len(self.micelials))
        for i in range(n_cross):
            self.syn_mgr.connect(self.animals[i], self.micelials[i],
                                 "hybrid", "excitatory", persistent=True)

    def process_signal(self, signal: MindSignal) -> float:
        """Procesa una señal y retorna la activación promedio resultante."""
        with self._lock:
            self.signal_queue.append(signal)
            ctx = {"neuromodulator": "dopamine", "nm_level": signal.arousal,
                   "concept": signal.content[:15], "pattern": self.layer.value}
            activations = []

            for n in self.animals:
                try:
                    act = n.receive_signal(signal.strength, signal.content[:20], ctx)
                    if act:
                        activations.append(float(act))
                except Exception:
                    pass

            for n in self.micelials:
                try:
                    act = n.receive_concept(signal.strength, signal.content[:20], ctx)
                    if act:
                        activations.append(float(act))
                except Exception:
                    pass

            avg = sum(activations) / max(1, len(activations)) if activations else 0.0
            self._activation_avg = avg
            self.processed += 1
            return avg

    def get_status(self) -> Dict:
        with self._lock:
            return {
                "layer":          self.layer.value,
                "animals":        len(self.animals),
                "micelials":      len(self.micelials),
                "signals_queued": len(self.signal_queue),
                "processed":      self.processed,
                "avg_activation": round(self._activation_avg, 4),
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  MENTE FLUIDA
# ═══════════════════════════════════════════════════════════════════════════════

class FluidMind:
    """La mente como proceso continuo, no como contenedor.

    No hay tres compartimentos fijos. Hay capas de luminosidad, puentes,
    guardianes, un orquestador invisible y una celda de sombra que filtra
    sutilmente hacia el resto.

    Todo está integrado con:
    ─ Neuronas animales y miceliales por capa
    ─ SynapseManager para todas las conexiones
    ─ AdaptiveCore (emociones + instintos) como modulador
    ─ MemoryManager + MemoryPersistence para persistir experiencias
    """

    def __init__(self, memory_dir: str = "memory",
                 n_cycles_before_persist: int = 10):
        self._lock = RLock()

        # ── Motor emocional e instintivo ──────────────────────────────────
        self.adaptive = AdaptiveCore(n_animal=0, n_micelial=0)  # solo motores
        self.emotions = self.adaptive.emotions
        self.instincts = self.adaptive.instincts

        # ── Memoria ───────────────────────────────────────────────────────
        self.memory_mgr  = MemoryManager(decay_interval_s=30.0)
        self.persistence = MemoryPersistence(
            self.memory_mgr, base_dir=memory_dir, auto_save_interval_s=60.0)

        # ── SynapseManager global ─────────────────────────────────────────
        self.synapse_mgr = SynapseManager(
            prune_interval_s  = 60.0,
            utility_threshold = 0.08,
            error_rate_max    = 0.75,
            inactivity_secs   = 120.0,
        )

        # ── Capas ──────────────────────────────────────────────────────────
        self.layers: Dict[LuminosityLayer, MindLayer] = {}
        for layer in LuminosityLayer:
            ml = MindLayer(layer, self.synapse_mgr)
            ml.build()
            self.layers[layer] = ml

        # ── Puentes entre capas ───────────────────────────────────────────
        self.bridges: Dict[str, MindBridge] = {}
        bridge_pairs = [
            (LuminosityLayer.FOCAL,      LuminosityLayer.PERIPHERAL),
            (LuminosityLayer.PERIPHERAL, LuminosityLayer.SUBMERGED),
            (LuminosityLayer.SUBMERGED,  LuminosityLayer.DEEP),
            (LuminosityLayer.FOCAL,      LuminosityLayer.SUBMERGED),  # atajo directo
            (LuminosityLayer.DEEP,       LuminosityLayer.SHADOW),
        ]
        for la, lb in bridge_pairs:
            key   = f"{la.value}↔{lb.value}"
            na    = self.layers[la].animals[0]  if self.layers[la].animals   else None
            nb    = self.layers[lb].animals[0]  if self.layers[lb].animals   else None
            bridge = MindBridge(la, lb, self.synapse_mgr, na, nb)
            self.bridges[key] = bridge

        # ── Guardianes ────────────────────────────────────────────────────
        self.guardians: Dict[LuminosityLayer, Guardian] = {
            LuminosityLayer.DEEP:   Guardian(LuminosityLayer.DEEP),
            LuminosityLayer.SHADOW: Guardian(LuminosityLayer.SHADOW),
        }

        # ── Celda de aislamiento ──────────────────────────────────────────
        self.isolation = IsolationCell()

        # ── Orquestador ───────────────────────────────────────────────────
        self.orchestrator = MindOrchestrator(self.bridges, self.guardians)

        # ── Estado interno ────────────────────────────────────────────────
        self._cycle          = 0
        self._n_persist      = n_cycles_before_persist
        self._signal_log     = deque(maxlen=100)
        self._orch_log       = deque(maxlen=50)
        self._total_signals  = 0

        log_event("FluidMind inicializada", "INFO")

    # ── Proceso principal ─────────────────────────────────────────────────
    def perceive(self, content: str,
                 tags: List[str] = None,
                 valence: float  = 0.0,
                 arousal: float  = 0.5,
                 instinct: str   = "",
                 modality: str   = "conceptual") -> Dict[str, Any]:
        """Introduce una señal en la mente y la propaga por las capas."""
        with self._lock:
            self._cycle += 1
            self._total_signals += 1

        tags = tags or content.split()[:4]

        # Actualizar estado emocional e instintivo
        self.adaptive.run_cycle(
            stimulus  = content,
            threat    = max(0.0, -valence * arousal),
            energy    = 0.6 + valence * 0.2,
            novelty   = arousal * 0.5,
            social    = 0.5,
        )

        # Influencia residual del Shadow sobre la señal
        residual = self.isolation.get_residual_influence()
        valence_mod = valence + residual["valence_leak"]
        arousal_mod = min(1.0, arousal + residual["arousal_leak"])

        signal = MindSignal(
            content  = content,
            tags     = tags,
            origin   = LuminosityLayer.FOCAL,
            strength = 0.6 + arousal * 0.3,
            valence  = max(-1.0, min(1.0, valence_mod)),
            arousal  = arousal_mod,
            instinct = instinct,
        )

        # Orquestar (ajustar puentes y dominancia)
        orch = self.orchestrator.orchestrate(
            self.emotions, self.instincts, self.isolation)

        # Propagar por capas según dominancia
        layer_activations = {}
        dominant = self.orchestrator.dominant
        propagation_order = self._propagation_order(dominant, signal)

        for layer in propagation_order:
            # Pasar por guardián si existe
            guardian = self.guardians.get(layer)
            proc_signal = signal
            guarded = False
            if guardian:
                proc_signal, guarded = guardian.filter(signal)

            act = self.layers[layer].process_signal(proc_signal)
            layer_activations[layer.value] = round(act, 4)

            # Transmitir por puentes hacia siguientes capas
            signal = self._route_through_bridges(signal, layer) or signal

        # Guardar en memoria
        fid = self.memory_mgr.encode(
            content   = content,
            tags      = tags,
            modality  = modality,
            valence   = valence_mod,
            arousal   = arousal_mod,
            instinct_tags = [instinct] if instinct else [],
        )
        if fid:
            f = self.memory_mgr.store.get(fid)
            if f:
                self.persistence.notify_fragment_changed(f)

        # Persistencia periódica
        if self._cycle % self._n_persist == 0:
            self.memory_mgr.decay_cycle(force=True)
            self.memory_mgr.consolidate(force=True)
            self.persistence.save_cycle(force=True)

        result = {
            "cycle":             self._cycle,
            "dominant_layer":    dominant.value,
            "layer_activations": layer_activations,
            "orchestration":     orch,
            "shadow_influence":  residual,
            "memory_fragment":   fid,
            "emotion":           self.emotions.get_summary(),
            "instincts":         self.instincts.get_status(),
        }
        self._signal_log.append({
            "ts": time.time(), "content": content[:40],
            "dominant": dominant.value,
            "strength": signal.strength,
        })
        return result

    def isolate(self, content: str, reason: str = "protects_integrity",
                valence: float = -0.5, arousal: float = 0.6) -> str:
        """Aísla contenido en la Shadow layer."""
        cid = self.isolation.isolate(content, reason, valence, arousal)
        # Registrar en memoria con capa SELF (forma identidad)
        fid = self.memory_mgr.encode(
            content      = f"[AISLADO] {content[:60]}",
            tags         = ["shadow","aislado",reason],
            modality     = "emocional",
            valence      = valence,
            arousal      = arousal,
            instinct_tags= ["defend"],
            forced_layer = MemoryLayer.SELF,
        )
        log_event(f"Contenido aislado: {content[:40]} — razón: {reason}", "INFO")
        return cid

    def _propagation_order(self, dominant: LuminosityLayer,
                            signal: MindSignal) -> List[LuminosityLayer]:
        """Orden de propagación según la capa dominante y la señal."""
        base_order = [LuminosityLayer.FOCAL, LuminosityLayer.PERIPHERAL,
                      LuminosityLayer.SUBMERGED, LuminosityLayer.DEEP]
        # Shadow siempre al final, siempre
        order = [l for l in base_order if l != dominant] + [dominant]
        order = sorted(order, key=lambda l: l != dominant)
        order.append(LuminosityLayer.SHADOW)
        return order

    def _route_through_bridges(self, signal: MindSignal,
                                 current_layer: LuminosityLayer
                                 ) -> Optional[MindSignal]:
        """Pasa la señal por los puentes relevantes de la capa actual."""
        for key, bridge in self.bridges.items():
            if bridge.layer_a == current_layer:
                result = bridge.transmit(signal, "a_to_b")
                if result:
                    return result
            elif bridge.layer_b == current_layer:
                result = bridge.transmit(signal, "b_to_a")
                if result:
                    return result
        return None

    # ── Estado y diagnóstico ──────────────────────────────────────────────
    def get_status(self) -> Dict[str, Any]:
        return {
            "cycle":          self._cycle,
            "total_signals":  self._total_signals,
            "dominant_layer": self.orchestrator.dominant.value,
            "layers":         {l.value: self.layers[l].get_status()
                               for l in LuminosityLayer},
            "orchestrator":   self.orchestrator.get_status(),
            "guardians":      {l.value: {"activations": g.activations,
                                          "threshold": g.threshold,
                                          "sensitivity": g.sensitivity}
                               for l, g in self.guardians.items()},
            "isolation":      self.isolation.stats(),
            "memory":         self.memory_mgr.get_status()["store"],
            "synapse_stats":  self.synapse_mgr.get_stats(),
            "emotions":       self.emotions.get_summary(),
            "instincts":      self.instincts.get_status(),
        }

    def shutdown(self):
        self.persistence.go_to_sleep()
        self.synapse_mgr.prune(force=True)
        log_event("FluidMind apagada", "INFO")


# ═══════════════════════════════════════════════════════════════════════════════
#  DIAGNÓSTICO
# ═══════════════════════════════════════════════════════════════════════════════

_SEP  = "─" * 64
_SEP2 = "═" * 64

_STIMULI = [
    ("La primera vez que entendí algo profundo",       ["comprension","luz","mente"],    0.85,  0.75, "explore"),
    ("Una amenaza inesperada me hace dudar",            ["amenaza","duda","miedo"],       -0.80,  0.90, "survive"),
    ("El recuerdo de algo bello que ya no existe",      ["belleza","perdida","memoria"],   0.40,  0.60, "bond"),
    ("Algo que no quiero recordar pero persiste",       ["represion","peso","sombra"],    -0.70,  0.70, "defend"),
    ("Una idea nueva que cambia mi perspectiva",        ["novedad","cambio","insight"],    0.80,  0.80, "explore"),
    ("El peso de una decisión difícil",                 ["decision","peso","dilema"],     -0.30,  0.75, "survive"),
    ("La calma después de resolver un conflicto",       ["calma","resolucion","paz"],      0.75,  0.25, "rest"),
    ("Algo que me hace cuestionar quién soy",          ["identidad","pregunta","yo"],      0.20,  0.65, "explore"),
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


def run_diagnostic():
    print()
    print(_SEP2)
    print("  DIAGNÓSTICO — MENTE FLUIDA")
    print("  Capas de Luminosidad · Puentes · Guardianes · Sombra")
    print(_SEP2)

    print("\n  Configura:\n")
    n_cycles  = _ask_int("Ciclos de estimulación", 1, 40, 12)
    mem_dir   = input("  Directorio de memoria [default=memory]: ").strip() or "memory"

    print(f"\n  → {n_cycles} ciclos · memoria en '{mem_dir}'\n")

    print(_SEP)
    print("  [1/6] Construyendo mente fluida…")
    t0   = time.time()
    mind = FluidMind(memory_dir=mem_dir)
    _build_demo_memory(mind.memory_mgr)
    print(f"       ✓ Mente construida en {(time.time()-t0)*1000:.1f} ms")
    total_neurons = sum(
        len(ml.animals) + len(ml.micelials)
        for ml in mind.layers.values())
    print(f"         {total_neurons} neuronas · "
          f"{mind.synapse_mgr.get_stats()['total_synapses']} sinapsis · "
          f"{len(mind.bridges)} puentes")

    print(_SEP)
    print(f"  [2/6] Estimulando con {n_cycles} ciclos…\n")
    for i in range(n_cycles):
        stim = _STIMULI[i % len(_STIMULI)]
        content, tags, val, aro, inst = stim
        result = mind.perceive(content, tags, val, aro, inst)
        dom    = result["dominant_layer"]
        emo    = result["emotion"]["dominant"]
        shadow = result["shadow_influence"]["instinct_pressure"]
        print(f"  [{i+1:02d}] dom={dom:<12} emo={emo:<15} "
              f"sombra={shadow:.3f}  '{content[:40]}'")
        # Aislar el estímulo oscuro
        if val < -0.6 and i == 3:
            cid = mind.isolate(content, "demasiado_pesado", val, aro)
            print(f"       → Contenido aislado en Shadow (id={cid[:8]})")

    print(_SEP)
    print("  [3/6] Estado de capas de luminosidad…\n")
    for layer in LuminosityLayer:
        ls = mind.layers[layer].get_status()
        act_bar = _bar(ls["avg_activation"])
        print(f"  {layer.value:<12} A={ls['animals']}  M={ls['micelials']}  "
              f"proc={ls['processed']:>4}  act={act_bar} {ls['avg_activation']:.4f}")

    print(_SEP)
    print("  [4/6] Puentes entre capas…\n")
    orch_s = mind.orchestrator.get_status()
    print(f"  {'Puente':<25} {'Apertura':>9} {'Cruces':>7}")
    print("  " + "─" * 44)
    for key, bs in orch_s["bridge_states"].items():
        bar = _bar(bs["aperture"], 10)
        print(f"  {key:<25} {bar} {bs['aperture']:.3f}  {bs['crossings']:>6}")

    print(_SEP)
    print("  [5/6] Guardianes y Shadow…\n")
    status = mind.get_status()
    for layer, gs in status["guardians"].items():
        print(f"  Guardián [{layer:<8}]  "
              f"activaciones={gs['activations']}  "
              f"umbral={gs['threshold']:.3f}  "
              f"sensibilidad={gs['sensitivity']:.3f}")

    iso_s = status["isolation"]
    print(f"\n  Shadow (aislados):")
    print(f"    Contenidos aislados  : {iso_s['isolated_count']}")
    print(f"    Valencia promedio    : {iso_s['avg_valence']:+.3f}")
    print(f"    Eventos de goteo     : {iso_s['total_leak_events']}")
    residual = mind.isolation.get_residual_influence()
    print(f"    Influencia residual  : "
          f"V={residual['valence_leak']:+.4f}  "
          f"A={residual['arousal_leak']:.4f}  "
          f"presión={residual['instinct_pressure']:.4f}")

    print(_SEP)
    print("  [6/6] Estado completo\n")
    syn_s = status["synapse_stats"]
    mem_s = status["memory"]
    emo_s = status["emotions"]
    inst_s= status["instincts"]

    print("  ── SINAPSIS ─────────────────────────────────────────────")
    print(f"    Total={syn_s['total_synapses']}  "
          f"Activas={syn_s['active_synapses']}  "
          f"Tipo={syn_s['by_kind']}")
    print(f"    Peso avg={syn_s['avg_weight']}  "
          f"Utilidad={syn_s['avg_utility']}")

    print("\n  ── MEMORIA ──────────────────────────────────────────────")
    for layer, count in mem_s["by_layer"].items():
        pct = count / max(1, mem_s["total"]) * 100
        print(f"    {layer:<15} {_bar(count/max(1,mem_s['total']),10)} "
              f"{count:>4} ({pct:>5.1f}%)")
    print(f"    Fuerza promedio: {mem_s['avg_strength']:.4f}")

    print("\n  ── EMOCIONES ────────────────────────────────────────────")
    print(f"    Dominante : {emo_s['dominant']}  "
          f"Neuromod={emo_s['neuromod']}")
    print(f"    Valencia  : {emo_s['valence']:+.3f}  "
          f"Arousal={emo_s['arousal']:.3f}")

    print("\n  ── INSTINTOS ────────────────────────────────────────────")
    print(f"    Activos   : {inst_s.get('active', [])}")
    print(f"    Dominante : {inst_s.get('dominant','ninguno')}")

    print()
    print(_SEP2)
    print("  RESUMEN EJECUTIVO")
    print(_SEP2)
    print(f"  Capa dominante al cierre : {mind.orchestrator.dominant.value}")
    print(f"  Ciclos procesados        : {mind._cycle}")
    print(f"  Señales totales          : {mind._total_signals}")
    print(f"  Neuronas totales         : {total_neurons}")
    print(f"  Sinapsis                 : {syn_s['total_synapses']}")
    print(f"  Fragmentos en memoria    : {mem_s['total']}")
    print(f"  Contenidos aislados      : {iso_s['isolated_count']}")
    print(f"  Activaciones de guardianes: "
          f"{sum(g.activations for g in mind.guardians.values())}")
    print(f"  Emoción dominante        : {emo_s['dominant']}")
    print()
    print("  ✓ Mente fluida lista para operación continua")
    print(_SEP2)
    print()

    mind.shutdown()
    return mind


if __name__ == "__main__":
    random.seed(42)
    try:
        mind = run_diagnostic()
    except KeyboardInterrupt:
        print("\n  Diagnóstico interrumpido.")
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        traceback.print_exc()
