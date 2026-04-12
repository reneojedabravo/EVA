# background_thinking.py
"""
Pensamiento Profundo en Segundo Plano — Impulsado por Necesidad.

Este sistema no piensa porque haya un temporizador. Piensa cuando hay razón:
  ─ URGENCIA    — instinto activo, arousal alto, señal de amenaza
  ─ CURIOSIDAD  — algo no encaja, hay una laguna, una pregunta sin respuesta
  ─ DUDA        — contradicción detectada entre recuerdos o creencias
  ─ RESONANCIA  — algo reciente resuena con algo antiguo inesperadamente
  ─ NECESIDAD   — un drive motivacional supera su umbral
  ─ RUIDO       — la mente está demasiado activa y necesita integrar
  ─ SILENCIO    — la mente está demasiado quieta y necesita explorar

Los pensamientos pasan por fases:
  1. SEED       — impulso inicial (emocional/instintivo/cognitivo)
  2. EXPANSION  — exploración libre, neuronas miceliales se ramifican
  3. TENSION    — colisión con contradicciones, preguntas sin respuesta
  4. SYNTHESIS  — intentar llegar a consenso interno
  5. RESOLUTION — si hay consenso: consolidar; si no: olvidar o aislar

Si no se llega a resolución en N pasos: el pensamiento se disuelve.
Los pensamientos disueltos dejan una huella efímera en memoria.
Los pensamientos resueltos se consolidan como fragmentos ASSOCIATIVE o SELF.

Integración:
  ─ Neuronas animales + miceliales + sinapsis
  ─ adaptive.py (emociones + instintos como disparadores)
  ─ memory.py + memory_persistence.py (guardar proceso y resultado)
  ─ mind.py (opcional: percibir resultados por la FluidMind)
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
from threading import RLock, Thread, Event
from typing import Any, Dict, List, Optional, Tuple

from monitoring import log_event, log_neuron_error
from animal    import create_cognitive_animal_neuron,   CognitiveAnimalNeuronBase
from micelial  import create_cognitive_micelial_neuron, CognitiveMicelialNeuronBase
from synapse   import SynapseManager
from adaptive  import AdaptiveCore, EmotionEngine, InstinctCore, InstinctID
from memory    import (MemoryManager, EmotionalStamp, MemoryLayer,
                        Fragment, _build_demo_memory)
from memory_persistence import MemoryPersistence


# ═══════════════════════════════════════════════════════════════════════════════
#  DISPARADORES DE PENSAMIENTO
# ═══════════════════════════════════════════════════════════════════════════════

class ThinkingTrigger(Enum):
    URGENCY    = "urgency"     # instinto activo + arousal alto
    CURIOSITY  = "curiosity"   # pregunta o laguna detectada
    DOUBT      = "doubt"       # contradicción interna
    RESONANCE  = "resonance"   # eco entre algo nuevo y algo viejo
    DRIVE      = "drive"       # motivación supera umbral
    NOISE      = "noise"       # exceso de actividad → integrar
    SILENCE    = "silence"     # quietud excesiva → explorar
    EXTERNAL   = "external"    # señal externa explícita


# Prioridad de cada disparador (mayor = más urgente)
_TRIGGER_PRIORITY = {
    ThinkingTrigger.URGENCY:   1.0,
    ThinkingTrigger.DOUBT:     0.85,
    ThinkingTrigger.DRIVE:     0.75,
    ThinkingTrigger.RESONANCE: 0.65,
    ThinkingTrigger.CURIOSITY: 0.60,
    ThinkingTrigger.NOISE:     0.45,
    ThinkingTrigger.SILENCE:   0.35,
    ThinkingTrigger.EXTERNAL:  0.80,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  FASES DEL PENSAMIENTO
# ═══════════════════════════════════════════════════════════════════════════════

class ThoughtPhase(Enum):
    SEED       = "seed"
    EXPANSION  = "expansion"
    TENSION    = "tension"
    SYNTHESIS  = "synthesis"
    RESOLUTION = "resolution"
    DISSOLVED  = "dissolved"   # no llegó a consenso → se disuelve


# ═══════════════════════════════════════════════════════════════════════════════
#  ESTRUCTURA DE PENSAMIENTO
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Thought:
    """Un pensamiento activo en proceso de elaboración."""
    thought_id:  str
    trigger:     ThinkingTrigger
    seed_content: str           # el impulso inicial
    tags:        List[str]
    valence:     float          # carga emocional del pensamiento
    arousal:     float
    instinct:    str            = ""
    phase:       ThoughtPhase  = ThoughtPhase.SEED
    coherence:   float         = 0.0    # 0..1 qué tan integrado está
    tension:     float         = 0.0    # 0..1 nivel de contradicción interna
    steps:       int           = 0
    max_steps:   int           = 20
    fragments:   List[str]     = field(default_factory=list)  # FIDs de mem
    neural_acts: List[float]   = field(default_factory=list)  # activaciones
    associations: List[str]    = field(default_factory=list)  # conceptos asociados
    conclusion:  str           = ""
    creation_ts: float         = field(default_factory=time.time)
    resolution_ts: Optional[float] = None

    def age_s(self) -> float:
        return time.time() - self.creation_ts

    def is_resolvable(self) -> bool:
        return self.coherence >= 0.55 and self.tension < 0.65

    def priority(self) -> float:
        base = _TRIGGER_PRIORITY.get(self.trigger, 0.5)
        emo_boost = abs(self.valence) * 0.2 + self.arousal * 0.2
        return min(1.0, base + emo_boost)


# ═══════════════════════════════════════════════════════════════════════════════
#  RED NEURONAL DE PENSAMIENTO PROFUNDO
# ═══════════════════════════════════════════════════════════════════════════════

_THINKING_ANIMAL = [
    ("abstract_pattern_integrator" if False else "anomaly_detector",   {}),
    ("decision_maker",             {}),
    ("risk_assessor",              {}),
    ("pattern_recognizer",         {}),
    ("insight_trigger",            {}),
    ("divergent_thinker",          {}),
    ("convergent_thinker",         {}),
    ("self_monitor",               {}),
    ("dopaminergic_modulator",     {}),
    ("adaptive_threshold_cell",    {}),
]

_THINKING_MICELIAL = [
    ("abstract_pattern_integrator",    {}),
    ("global_coherence_coordinator",   {}),
    ("conceptual_bridge_builder",      {}),
    ("insight_propagator",             {}),
    ("deep_reflection_orchestrator",   {}),
    ("knowledge_synthesizer",          {"domain_specializations": ["thinking","identity"]}),
    ("plasmodium_collector",           {}),
    ("anastomosis_node",               {}),
    ("glycolytic_oscillator",          {}),
    ("quorum_sensing_node",            {}),
]


class ThinkingNetwork:
    """Red neuronal dedicada al pensamiento profundo."""

    def __init__(self, synapse_mgr: SynapseManager,
                 n_animal: int = 5, n_micelial: int = 5):
        self.animals:   List[CognitiveAnimalNeuronBase]   = []
        self.micelials: List[CognitiveMicelialNeuronBase] = []
        self.syn_mgr    = synapse_mgr
        self._build(min(n_animal, len(_THINKING_ANIMAL)),
                    min(n_micelial, len(_THINKING_MICELIAL)))

    def _build(self, na: int, nm: int):
        for i in range(na):
            ntype, kwargs = _THINKING_ANIMAL[i]
            nid = f"THK_A{i+1:02d}_{ntype[:8]}"
            try:
                n = create_cognitive_animal_neuron(ntype, nid, **kwargs)
                self.animals.append(n)
            except Exception as e:
                log_neuron_error(nid, f"ThinkingNetwork animal: {e}")

        for i in range(nm):
            ntype, kwargs = _THINKING_MICELIAL[i]
            nid = f"THK_M{i+1:02d}_{ntype[:8]}"
            try:
                n = create_cognitive_micelial_neuron(ntype, nid, **kwargs)
                self.micelials.append(n)
            except Exception as e:
                log_neuron_error(nid, f"ThinkingNetwork micelial: {e}")

        # Conectar
        for i in range(len(self.animals) - 1):
            self.syn_mgr.connect(self.animals[i], self.animals[i+1],
                                 "electrical", "excitatory", persistent=True)
        for i in range(len(self.micelials) - 1):
            self.syn_mgr.connect(self.micelials[i], self.micelials[i+1],
                                 "chemical", "excitatory", persistent=True)
        n_cross = min(3, len(self.animals), len(self.micelials))
        for i in range(n_cross):
            self.syn_mgr.connect(self.animals[i], self.micelials[i],
                                 "hybrid", "excitatory", persistent=True)
        # Bundle de síntesis (varios animales → primer micelial)
        if len(self.animals) >= 3 and self.micelials:
            self.syn_mgr.create_parallel_bundle(
                self.animals[:3], self.micelials[0], "hybrid")

    def activate(self, signal: float, context: Dict = None,
                 phase: ThoughtPhase = ThoughtPhase.EXPANSION) -> Dict[str, float]:
        """Activa la red con una señal y retorna activaciones."""
        ctx = context or {}
        ctx["pattern"] = phase.value

        results = {}
        # Animales → más activos en fases rápidas
        for n in self.animals:
            try:
                act = n.receive_signal(signal, phase.value, ctx)
                if act:
                    results[n.neuron_id] = float(act)
            except Exception:
                pass
        # Miceliales → más activos en fases lentas (expansión, síntesis)
        if phase in (ThoughtPhase.EXPANSION, ThoughtPhase.SYNTHESIS,
                     ThoughtPhase.TENSION):
            concept = ctx.get("seed", "thought")
            for n in self.micelials:
                try:
                    act = n.receive_concept(signal, concept, ctx)
                    if act:
                        results[n.neuron_id] = float(act)
                except Exception:
                    pass
        # Propagar por sinapsis
        syns = list(self.syn_mgr.synapses.values())
        for syn in syns:
            try:
                syn.transmit(signal, ctx)
            except Exception:
                pass
        return results

    def get_status(self) -> Dict:
        return {
            "animals":  len(self.animals),
            "micelials":len(self.micelials),
            "synapses": self.syn_mgr.get_stats()["total_synapses"],
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  DETECTOR DE NECESIDAD DE PENSAR
# ═══════════════════════════════════════════════════════════════════════════════

class ThinkingNeedDetector:
    """Detecta cuándo la mente necesita pensar.

    No hay temporizadores fijos. El sistema evalúa continuamente si hay
    una razón genuina para iniciar un pensamiento profundo.
    """

    def __init__(self, adaptive: AdaptiveCore, memory: MemoryManager):
        self.adaptive = adaptive
        self.memory   = memory
        self._lock    = RLock()
        self._last_check = time.time()
        self._pending_triggers: deque = deque(maxlen=20)
        self._detection_log   = deque(maxlen=100)

        # Umbrales
        self.urgency_threshold   = 0.65
        self.curiosity_threshold = 0.50
        self.doubt_threshold     = 0.45
        self.silence_timeout     = 30.0   # segundos sin actividad → explorar
        self._last_activity      = time.time()

    def notify_activity(self):
        """Notifica que hubo actividad reciente."""
        self._last_activity = time.time()

    def check(self) -> List[Tuple[ThinkingTrigger, str, float]]:
        """Evalúa si hay razón para pensar. Retorna lista de (trigger, seed, urgencia)."""
        with self._lock:
            triggers = []
            now      = time.time()

            # ── 1. URGENCIA: instinto activo + arousal alto ───────────────
            dom_inst = self.adaptive.instincts.get_dominant()
            arousal  = self.adaptive.emotions.arousal
            valence  = self.adaptive.emotions.valence
            if (dom_inst and
                    self.adaptive.instincts.get_level(dom_inst) > self.urgency_threshold
                    and arousal > 0.6):
                triggers.append((
                    ThinkingTrigger.URGENCY,
                    f"instinto_{dom_inst.value}_activo",
                    self.adaptive.instincts.get_level(dom_inst),
                ))

            # ── 2. DUDA: contradicción en memoria reciente ────────────────
            recent = self.memory.store.layer_fragments(MemoryLayer.WORKING)
            if len(recent) >= 3:
                valences = [f.emotion.valence for f in recent[-5:]]
                variance = (sum((v - sum(valences)/len(valences))**2
                                for v in valences) / len(valences))
                if variance > self.doubt_threshold:
                    triggers.append((
                        ThinkingTrigger.DOUBT,
                        "contradiccion_emocional_reciente",
                        min(1.0, variance * 2),
                    ))

            # ── 3. CURIOSIDAD: drive de exploración alto ──────────────────
            drive_vec  = self.adaptive.motivation.get_drive_vector()
            exploration = drive_vec.get("exploration", {}).get("strength", 0.0)
            learning    = drive_vec.get("learning",    {}).get("strength", 0.0)
            if max(exploration, learning) > self.curiosity_threshold + 0.2:
                seed = ("explorar_desconocido" if exploration > learning
                        else "integrar_conocimiento")
                triggers.append((
                    ThinkingTrigger.CURIOSITY, seed,
                    max(exploration, learning),
                ))

            # ── 4. RESONANCIA: fragmento reciente resuena con uno antiguo ─
            all_self = self.memory.store.layer_fragments(MemoryLayer.SELF)
            working  = self.memory.store.layer_fragments(MemoryLayer.WORKING)
            if working and all_self:
                newest = working[-1]
                for old in all_self[:5]:
                    res = newest.emotion.resonance_with(old.emotion)
                    if res > 0.72:
                        triggers.append((
                            ThinkingTrigger.RESONANCE,
                            f"eco_con_{old.fid[:6]}",
                            res,
                        ))
                        break

            # ── 5. DRIVE: motivación muy alta sin acción ──────────────────
            dominant_drive = self.adaptive.motivation.get_dominant_drive()
            dom_str = drive_vec.get(dominant_drive, {}).get("strength", 0.0)
            if dom_str > 0.85:
                triggers.append((
                    ThinkingTrigger.DRIVE,
                    f"drive_{dominant_drive}_muy_alto",
                    dom_str,
                ))

            # ── 6. SILENCIO: sin actividad reciente ───────────────────────
            idle = now - self._last_activity
            if idle > self.silence_timeout:
                triggers.append((
                    ThinkingTrigger.SILENCE,
                    "quietud_prolongada",
                    min(1.0, idle / (self.silence_timeout * 3)),
                ))

            # ── 7. RUIDO: demasiados fragmentos en working sin consolidar ──
            n_working = len(self.memory.store.layer_fragments(MemoryLayer.WORKING))
            if n_working > 15:
                triggers.append((
                    ThinkingTrigger.NOISE,
                    "exceso_working_memory",
                    min(1.0, n_working / 30),
                ))

            # Añadir pendientes externos
            while self._pending_triggers:
                triggers.append(self._pending_triggers.popleft())

            if triggers:
                self._detection_log.append({
                    "ts": now, "count": len(triggers),
                    "triggers": [t[0].value for t in triggers],
                })

            return sorted(triggers, key=lambda x: x[2], reverse=True)

    def inject(self, trigger: ThinkingTrigger, seed: str, urgency: float = 0.7):
        """Inyecta un disparador externo."""
        with self._lock:
            self._pending_triggers.append((trigger, seed, urgency))

    def detection_stats(self) -> Dict:
        with self._lock:
            type_counts: Dict[str, int] = defaultdict(int)
            for entry in self._detection_log:
                for t in entry["triggers"]:
                    type_counts[t] += 1
            return {
                "total_detections": len(self._detection_log),
                "by_trigger":       dict(type_counts),
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  MOTOR DE PENSAMIENTO PROFUNDO
# ═══════════════════════════════════════════════════════════════════════════════

class DeepThinkingEngine:
    """Motor que elabora un pensamiento por fases hasta resolución o disolución."""

    MAX_STEPS_DEFAULT = 20
    COHERENCE_TARGET  = 0.55
    TENSION_MAX       = 0.70

    def __init__(self, network: ThinkingNetwork,
                 memory: MemoryManager,
                 persistence: MemoryPersistence,
                 adaptive: AdaptiveCore):
        self.network     = network
        self.memory      = memory
        self.persistence = persistence
        self.adaptive    = adaptive
        self._lock       = RLock()

    def elaborate(self, thought: Thought) -> Thought:
        """Elabora un pensamiento hasta resolución o disolución."""
        ctx = {
            "seed":       thought.seed_content,
            "trigger":    thought.trigger.value,
            "valence":    thought.valence,
            "arousal":    thought.arousal,
            "neuromodulator": self.adaptive.emotions.get_summary()["neuromod"],
            "nm_level":   self.adaptive.emotions.arousal,
        }

        while thought.phase not in (ThoughtPhase.RESOLUTION,
                                     ThoughtPhase.DISSOLVED):
            thought.steps += 1
            if thought.steps > thought.max_steps:
                thought.phase = ThoughtPhase.DISSOLVED
                break

            # Activar red según fase
            signal = thought.priority() * (0.5 + thought.arousal * 0.5)
            acts   = self.network.activate(signal, ctx, thought.phase)
            avg_act = sum(acts.values()) / max(1, len(acts))
            thought.neural_acts.append(round(avg_act, 4))

            # Buscar fragmentos resonantes en memoria
            resonant = self.memory.store.search_by_valence(
                thought.valence, tolerance=0.35, top_k=4)
            for f in resonant:
                if f.fid not in thought.fragments:
                    thought.fragments.append(f.fid)
                    thought.associations.extend(
                        [t for t in f.tags if t not in thought.associations][:2])

            # Calcular coherencia y tensión
            thought = self._update_metrics(thought, avg_act)

            # Transición de fase
            thought = self._transition_phase(thought)

        # Finalizar
        thought.resolution_ts = time.time()
        self._persist_thought(thought)
        return thought

    def _update_metrics(self, thought: Thought, avg_act: float) -> Thought:
        """Actualiza coherencia y tensión según la activación neural."""
        # Coherencia crece con activación sostenida y baja tensión
        if avg_act > 0.4:
            thought.coherence = min(1.0, thought.coherence +
                                    avg_act * 0.08 * (1 - thought.tension))
        else:
            thought.coherence = max(0.0, thought.coherence - 0.03)

        # Tensión: sube si hay contradicciones (valence muy negativa + alta activación)
        if thought.valence < -0.3 and avg_act > 0.6:
            thought.tension = min(1.0, thought.tension + 0.06)
        elif thought.valence > 0.3:
            thought.tension = max(0.0, thought.tension - 0.04)

        return thought

    def _transition_phase(self, thought: Thought) -> Thought:
        """Decide si el pensamiento debe cambiar de fase."""
        p = thought.phase

        if p == ThoughtPhase.SEED:
            thought.phase = ThoughtPhase.EXPANSION

        elif p == ThoughtPhase.EXPANSION:
            if thought.tension > 0.4:
                thought.phase = ThoughtPhase.TENSION
            elif thought.coherence > 0.45 and thought.steps > 4:
                thought.phase = ThoughtPhase.SYNTHESIS

        elif p == ThoughtPhase.TENSION:
            if thought.coherence > 0.50:
                thought.phase = ThoughtPhase.SYNTHESIS
            elif thought.tension > self.TENSION_MAX:
                thought.phase = ThoughtPhase.DISSOLVED  # demasiada tensión
            elif thought.steps > thought.max_steps * 0.6:
                thought.phase = ThoughtPhase.SYNTHESIS  # intentar igual

        elif p == ThoughtPhase.SYNTHESIS:
            if thought.coherence >= self.COHERENCE_TARGET:
                thought.phase = ThoughtPhase.RESOLUTION
                thought.conclusion = self._generate_conclusion(thought)
            elif thought.steps >= thought.max_steps:
                thought.phase = ThoughtPhase.DISSOLVED

        return thought

    def _generate_conclusion(self, thought: Thought) -> str:
        top_assoc = thought.associations[:3]
        assoc_str = ", ".join(top_assoc) if top_assoc else "sin asociaciones claras"
        valence_word = ("positivo" if thought.valence > 0.2 else
                        "negativo" if thought.valence < -0.2 else "neutro")
        return (f"[{thought.trigger.value}] "
                f"Pensamiento {valence_word} resuelto tras {thought.steps} pasos. "
                f"Coherencia={thought.coherence:.3f}. "
                f"Asociado a: {assoc_str}.")

    def _persist_thought(self, thought: Thought):
        """Guarda el pensamiento en memoria según su resultado."""
        if thought.phase == ThoughtPhase.RESOLUTION:
            # Consolidar: guardar como ASSOCIATIVE o SELF si es identitario
            forced = (MemoryLayer.SELF
                      if abs(thought.valence) > 0.7 and thought.coherence > 0.75
                      else None)
            fid = self.memory.encode(
                content      = thought.conclusion or thought.seed_content,
                tags         = thought.tags + ["pensamiento_resuelto",
                                               thought.trigger.value],
                modality     = "conceptual",
                valence      = thought.valence,
                arousal      = thought.arousal,
                instinct_tags= [thought.instinct] if thought.instinct else [],
                base_strength= thought.coherence,
                forced_layer = forced,
            )
            if fid:
                f = self.memory.store.get(fid)
                if f:
                    self.persistence.notify_fragment_changed(f)
                    if thought.phase == ThoughtPhase.RESOLUTION:
                        self.persistence.notify_layer_ascent(
                            f, MemoryLayer.WORKING)

        else:
            # Disuelto: huella efímera
            self.memory.encode(
                content      = f"[DISUELTO] {thought.seed_content[:60]}",
                tags         = thought.tags + ["pensamiento_disuelto"],
                modality     = "conceptual",
                valence      = thought.valence * 0.3,
                arousal      = thought.arousal * 0.3,
                base_strength= 0.15,
                forced_layer = MemoryLayer.EPHEMERAL,
            )


# ═══════════════════════════════════════════════════════════════════════════════
#  PENSADOR EN SEGUNDO PLANO
# ═══════════════════════════════════════════════════════════════════════════════

class BackgroundThinker:
    """Pensador en segundo plano impulsado por necesidad, no por temporizadores.

    Monitorea continuamente el estado emocional, instintivo y de memoria.
    Cuando detecta razón para pensar, inicia un proceso de pensamiento
    profundo que se elabora hasta resolución o disolución.

    Integra:
    ─ Neuronas animales + miceliales + sinapsis
    ─ adaptive.py (disparadores emocionales e instintivos)
    ─ memory.py + memory_persistence.py
    ─ FluidMind (opcional: percibir resultados)
    """

    def __init__(self,
                 memory_dir:   str   = "memory",
                 n_animal:     int   = 5,
                 n_micelial:   int   = 5,
                 check_interval_s: float = 2.0,
                 fluid_mind   = None):

        self._lock  = RLock()
        self._stop  = Event()

        # ── Motores ───────────────────────────────────────────────────────
        self.adaptive    = AdaptiveCore(n_animal=0, n_micelial=0)
        self.memory_mgr  = MemoryManager(decay_interval_s=30.0)
        self.persistence = MemoryPersistence(
            self.memory_mgr, base_dir=memory_dir, auto_save_interval_s=60.0)
        self.fluid_mind  = fluid_mind  # referencia opcional a FluidMind

        # ── Red neuronal de pensamiento ───────────────────────────────────
        self.synapse_mgr = SynapseManager(
            prune_interval_s  = 60.0,
            utility_threshold = 0.08,
            error_rate_max    = 0.75,
            inactivity_secs   = 120.0,
        )
        self.network = ThinkingNetwork(self.synapse_mgr, n_animal, n_micelial)
        self.engine  = DeepThinkingEngine(
            self.network, self.memory_mgr, self.persistence, self.adaptive)

        # ── Detector de necesidad ─────────────────────────────────────────
        self.detector = ThinkingNeedDetector(self.adaptive, self.memory_mgr)

        # ── Estado interno ────────────────────────────────────────────────
        self._check_interval  = check_interval_s
        self._active_thought: Optional[Thought] = None
        self._thought_queue:  deque = deque(maxlen=10)
        self._completed:      List[Thought] = []
        self._dissolved:      List[Thought] = []
        self._thread:         Optional[Thread] = None
        self._is_running      = False
        self._total_thoughts  = 0
        self._cycle           = 0
        self._last_activity   = time.time()
        self._momentum        = 0.5   # inercia del pensamiento

        log_event("BackgroundThinker inicializado", "INFO")

    # ── Control ───────────────────────────────────────────────────────────
    def start(self):
        """Inicia el pensamiento en segundo plano."""
        if self._is_running:
            return
        self._is_running = True
        self._stop.clear()
        self._thread = Thread(target=self._loop, daemon=True,
                              name="BackgroundThinker")
        self._thread.start()
        log_event("BackgroundThinker iniciado", "INFO")

    def stop(self):
        """Detiene el pensamiento y persiste resultados."""
        self._is_running = False
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5.0)
        self.persistence.go_to_sleep()
        self.synapse_mgr.prune(force=True)
        log_event("BackgroundThinker detenido", "INFO")

    def inject_stimulus(self, content: str, tags: List[str] = None,
                        valence: float = 0.0, arousal: float = 0.5,
                        instinct: str = ""):
        """Inyecta un estímulo externo que puede disparar un pensamiento."""
        self.detector.notify_activity()
        self._last_activity = time.time()
        # Actualizar estado adaptativo
        self.adaptive.run_cycle(
            stimulus = content,
            threat   = max(0.0, -valence * arousal),
            energy   = 0.6 + valence * 0.2,
            novelty  = arousal * 0.5,
        )
        # Codificar en memoria
        fid = self.memory_mgr.encode(
            content      = content,
            tags         = tags or content.split()[:4],
            modality     = "conceptual",
            valence      = valence,
            arousal      = arousal,
            instinct_tags= [instinct] if instinct else [],
        )
        # Verificar si el estímulo dispara pensamiento inmediato
        if abs(valence) > 0.7 or arousal > 0.75:
            self.detector.inject(
                ThinkingTrigger.EXTERNAL, content[:50],
                urgency=abs(valence) * arousal,
            )

    # ── Bucle principal ───────────────────────────────────────────────────
    def _loop(self):
        """Bucle de monitoreo y pensamiento."""
        while not self._stop.is_set():
            try:
                self._cycle += 1

                # 1. Detectar necesidad
                triggers = self.detector.check()

                # 2. Si hay razón para pensar, crear pensamiento
                if triggers and self._active_thought is None:
                    top_trigger, seed, urgency = triggers[0]
                    thought = self._create_thought(top_trigger, seed, urgency)
                    self._thought_queue.append(thought)

                # 3. Procesar pensamiento en cola
                if self._thought_queue and self._active_thought is None:
                    thought = self._thought_queue.popleft()
                    self._active_thought = thought
                    self._process_thought(thought)

                # 4. Decaimiento y consolidación periódica
                if self._cycle % 15 == 0:
                    self.memory_mgr.decay_cycle(force=True)
                if self._cycle % 30 == 0:
                    self.memory_mgr.consolidate(force=True)
                    self.persistence.save_cycle(force=True)
                    self.synapse_mgr.prune()

                # 5. Actualizar momentum
                self._update_momentum()

                self._stop.wait(self._check_interval)

            except Exception as e:
                log_neuron_error("BackgroundThinker", f"loop error: {e}")
                self._stop.wait(self._check_interval * 2)

    def _create_thought(self, trigger: ThinkingTrigger,
                         seed: str, urgency: float) -> Thought:
        """Crea un nuevo pensamiento."""
        self._total_thoughts += 1
        tid = hashlib.md5(
            f"{seed}{time.time()}{random.random()}".encode()).hexdigest()[:10]

        emo_sum = self.adaptive.emotions.get_summary()
        valence = self.adaptive.emotions.valence
        arousal = self.adaptive.emotions.arousal
        dom_inst = self.adaptive.instincts.get_dominant()
        inst_name = dom_inst.value if dom_inst else ""

        tags = seed.replace("_", " ").split()[:5] + [trigger.value]

        return Thought(
            thought_id   = tid,
            trigger      = trigger,
            seed_content = seed,
            tags         = tags,
            valence      = valence,
            arousal      = arousal,
            instinct     = inst_name,
            max_steps    = int(8 + urgency * 12),
        )

    def _process_thought(self, thought: Thought):
        """Elabora un pensamiento hasta resolución."""
        try:
            result = self.engine.elaborate(thought)
            if result.phase == ThoughtPhase.RESOLUTION:
                self._completed.append(result)
                self._momentum = min(1.0, self._momentum + 0.1)
                # Si hay FluidMind, percibir el resultado
                if self.fluid_mind and hasattr(self.fluid_mind, "perceive"):
                    try:
                        self.fluid_mind.perceive(
                            result.conclusion or result.seed_content,
                            result.tags, result.valence, result.arousal,
                            result.instinct, "pensamiento_profundo",
                        )
                    except Exception:
                        pass
            else:
                self._dissolved.append(result)
                self._momentum = max(0.1, self._momentum - 0.05)
        except Exception as e:
            log_neuron_error("DeepThinking", f"process_thought: {e}")
        finally:
            self._active_thought = None

    def _update_momentum(self):
        """Actualiza el momentum cognitivo."""
        # Decaimiento natural
        self._momentum = max(0.2, self._momentum * 0.99)
        # Boost por actividad reciente
        idle = time.time() - self._last_activity
        if idle < 10.0:
            self._momentum = min(0.9, self._momentum + 0.02)

    # ── Estado y estadísticas ─────────────────────────────────────────────
    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            completed_recent = self._completed[-5:] if self._completed else []
            dissolved_recent = self._dissolved[-3:] if self._dissolved else []
            return {
                "is_running":          self._is_running,
                "cycle":               self._cycle,
                "total_thoughts":      self._total_thoughts,
                "completed":           len(self._completed),
                "dissolved":           len(self._dissolved),
                "resolution_rate":     round(
                    len(self._completed) / max(1, self._total_thoughts), 3),
                "momentum":            round(self._momentum, 4),
                "active_thought":      (self._active_thought.seed_content[:40]
                                        if self._active_thought else None),
                "queue_size":          len(self._thought_queue),
                "detection_stats":     self.detector.detection_stats(),
                "network":             self.network.get_status(),
                "memory":              self.memory_mgr.get_status()["store"],
                "synapses":            self.synapse_mgr.get_stats(),
                "emotions":            self.adaptive.emotions.get_summary(),
                "instincts":           self.adaptive.instincts.get_status(),
                "recent_completed":    [
                    {"id": t.thought_id[:8], "trigger": t.trigger.value,
                     "coherence": round(t.coherence, 3),
                     "steps": t.steps, "seed": t.seed_content[:40]}
                    for t in completed_recent
                ],
                "recent_dissolved":    [
                    {"id": t.thought_id[:8], "trigger": t.trigger.value,
                     "steps": t.steps, "seed": t.seed_content[:40]}
                    for t in dissolved_recent
                ],
            }

    @property
    def is_running(self) -> bool:
        return self._is_running


# ═══════════════════════════════════════════════════════════════════════════════
#  DIAGNÓSTICO INTERACTIVO
# ═══════════════════════════════════════════════════════════════════════════════

_SEP  = "─" * 64
_SEP2 = "═" * 64

_TEST_STIMULI = [
    ("Algo que no entiendo sobre mí mismo",         ["identidad","pregunta","yo"],     -0.20, 0.70, "explore"),
    ("Una amenaza repentina que me hace reaccionar", ["amenaza","reaccion","instinto"], -0.85, 0.95, "survive"),
    ("Una idea que conecta dos cosas distantes",     ["conexion","insight","patron"],    0.75, 0.80, "explore"),
    ("El peso de algo que no puedo resolver",        ["peso","bloqueo","tension"],      -0.60, 0.65, "defend"),
    ("La sensación de que algo está por ocurrir",    ["anticipacion","inminente"],       0.30, 0.75, "explore"),
    ("Quietud profunda, sin nada urgente",           ["calma","quietud","espacio"],      0.65, 0.15, "rest"),
    ("Un recuerdo que resurge sin razón aparente",   ["memoria","eco","resonancia"],     0.50, 0.55, "bond"),
    ("Demasiados pensamientos al mismo tiempo",      ["ruido","exceso","saturacion"],   -0.20, 0.80, "survive"),
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
    print("  DIAGNÓSTICO — PENSAMIENTO PROFUNDO EN SEGUNDO PLANO")
    print("  Impulsado por Necesidad · Neuronal · Emocional · Memorioso")
    print(_SEP2)

    print("\n  Configura:\n")
    n_animal   = _ask_int("Neuronas animales",   1, 10, 5)
    n_micelial = _ask_int("Neuronas miceliales", 1, 10, 5)
    n_stimuli  = _ask_int("Estímulos a inyectar", 1, 20, 8)
    run_secs   = _ask_int("Segundos de observación", 3, 30, 8)
    mem_dir    = input("  Directorio de memoria [default=memory]: ").strip() or "memory"

    print(f"\n  → {n_animal}A · {n_micelial}M · {n_stimuli} estímulos · "
          f"{run_secs}s · memoria='{mem_dir}'\n")

    # ── [1] Construir ─────────────────────────────────────────────────────
    print(_SEP)
    print("  [1/6] Construyendo pensador profundo…")
    t0     = time.time()
    thinker = BackgroundThinker(
        memory_dir=mem_dir, n_animal=n_animal, n_micelial=n_micelial,
        check_interval_s=0.5)
    _build_demo_memory(thinker.memory_mgr)
    print(f"       ✓ {(time.time()-t0)*1000:.1f} ms")
    net_s = thinker.network.get_status()
    print(f"         {net_s['animals']}A + {net_s['micelials']}M → "
          f"{net_s['synapses']} sinapsis")

    # ── [2] Iniciar ───────────────────────────────────────────────────────
    print(_SEP)
    print("  [2/6] Iniciando pensamiento en segundo plano…")
    thinker.start()
    time.sleep(0.5)

    # ── [3] Inyectar estímulos ────────────────────────────────────────────
    print(_SEP)
    print(f"  [3/6] Inyectando {n_stimuli} estímulos…\n")
    for i in range(n_stimuli):
        stim = _TEST_STIMULI[i % len(_TEST_STIMULI)]
        content, tags, val, aro, inst = stim
        thinker.inject_stimulus(content, tags, val, aro, inst)
        print(f"  [{i+1:02d}] val={val:+.2f} aro={aro:.2f} "
              f"inst={inst:<10} '{content[:45]}'")
        time.sleep(0.3)

    # ── [4] Observar ──────────────────────────────────────────────────────
    print(_SEP)
    print(f"  [4/6] Observando {run_secs}s de pensamiento autónomo…")
    for sec in range(run_secs):
        time.sleep(1.0)
        status = thinker.get_status()
        active = status["active_thought"] or "─"
        completed = status["completed"]
        dissolved  = status["dissolved"]
        momentum   = status["momentum"]
        print(f"  t+{sec+1:02d}s  comp={completed}  disueltos={dissolved}  "
              f"mom={momentum:.3f}  activo='{active[:35]}'")

    # ── [5] Detener ───────────────────────────────────────────────────────
    print(_SEP)
    print("  [5/6] Deteniendo y persistiendo…")
    thinker.stop()

    # ── [6] Diagnóstico completo ──────────────────────────────────────────
    status  = thinker.get_status()
    syn_s   = status["synapses"]
    mem_s   = status["memory"]
    emo_s   = status["emotions"]
    inst_s  = status["instincts"]
    det_s   = status["detection_stats"]

    print(_SEP)
    print("  [6/6] Estado completo\n")

    print("  ── PENSAMIENTOS ─────────────────────────────────────────")
    print(f"    Total generados  : {status['total_thoughts']}")
    print(f"    Resueltos        : {status['completed']}")
    print(f"    Disueltos        : {status['dissolved']}")
    print(f"    Tasa resolución  : {status['resolution_rate']:.3f}  "
          f"{_bar(status['resolution_rate'], 12)}")
    print(f"    Momentum         : {status['momentum']:.4f}  "
          f"{_bar(status['momentum'], 12)}")

    if status["recent_completed"]:
        print(f"\n  Pensamientos resueltos:")
        for t in status["recent_completed"]:
            print(f"    [{t['trigger']:<12}] coh={t['coherence']:.3f}  "
                  f"pasos={t['steps']}  '{t['seed']}'")

    if status["recent_dissolved"]:
        print(f"\n  Pensamientos disueltos:")
        for t in status["recent_dissolved"]:
            print(f"    [{t['trigger']:<12}] pasos={t['steps']}  "
                  f"'{t['seed']}'")

    print("\n  ── DISPARADORES DETECTADOS ──────────────────────────────")
    print(f"    Total detecciones: {det_s['total_detections']}")
    for trigger, count in sorted(det_s["by_trigger"].items(),
                                  key=lambda x: x[1], reverse=True):
        bar = _bar(count / max(1, det_s["total_detections"]), 10)
        print(f"    {trigger:<12} {bar} {count}")

    print("\n  ── RED NEURONAL ─────────────────────────────────────────")
    print(f"    {net_s['animals']}A + {net_s['micelials']}M  "
          f"→ {syn_s['total_synapses']} sinapsis")
    print(f"    Por tipo: {syn_s['by_kind']}")
    print(f"    Peso avg={syn_s['avg_weight']}  "
          f"Utilidad={syn_s['avg_utility']}")

    print("\n  ── MEMORIA ──────────────────────────────────────────────")
    for layer, count in mem_s["by_layer"].items():
        pct = count / max(1, mem_s["total"]) * 100
        print(f"    {layer:<15} {_bar(count/max(1,mem_s['total']),10)} "
              f"{count:>4} ({pct:>5.1f}%)")
    print(f"    Fuerza promedio: {mem_s['avg_strength']:.4f}")

    print("\n  ── EMOCIONES E INSTINTOS ────────────────────────────────")
    print(f"    Emoción: {emo_s['dominant']}  "
          f"V={emo_s['valence']:+.3f}  A={emo_s['arousal']:.3f}")
    print(f"    Instintos activos: {inst_s.get('active', [])}")

    print()
    print(_SEP2)
    print("  RESUMEN EJECUTIVO")
    print(_SEP2)
    health = ("ÓPTIMO"    if status["resolution_rate"] > 0.6 else
              "ESTABLE"   if status["resolution_rate"] > 0.35 else
              "DISPERSO")
    print(f"  Estado cognitivo    : {health}")
    print(f"  Pensamientos totales: {status['total_thoughts']}")
    print(f"  Tasa de resolución  : {status['resolution_rate']:.3f}")
    print(f"  Momentum cognitivo  : {status['momentum']:.4f}")
    print(f"  Fragmentos memoria  : {mem_s['total']}")
    print(f"  Ciclos de pensamiento: {status['cycle']}")
    print()
    print("  ✓ Pensamiento profundo lista para operación continua")
    print("  ✓ Piensa cuando hay razón — no por temporizador")
    print(_SEP2)
    print()

    return thinker


if __name__ == "__main__":
    random.seed(42)
    try:
        thinker = run_diagnostic()
    except KeyboardInterrupt:
        print("\n  Diagnóstico interrumpido.")
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        traceback.print_exc()
