# synapse.py
"""
Sistema de sinapsis híbridas para redes de neuronas animales y miceliales.

Características:
  ─ Conexiones animal↔animal, micelial↔micelial, animal↔micelial (híbrida)
  ─ Topología en paralelo y en serie
  ─ Conexiones persistentes con registro histórico compacto
  ─ Poda inteligente basada en utilidad, edad y tasa de error
  ─ Plasticidad sináptica: LTP / LTD / STDP / Hebbian / modulatoria

Ejecutar directamente para obtener un diagnóstico interactivo:
    python synapse.py
"""

import time
import math
import hashlib
import random
import traceback
from abc import ABC, abstractmethod
from collections import deque, defaultdict
from enum import Enum
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

from monitoring import log_event, log_neuron_error, log_neuron_warning
from animal   import create_cognitive_animal_neuron,   CognitiveAnimalNeuronBase
from micelial import create_cognitive_micelial_neuron, CognitiveMicelialNeuronBase

# ─── Enumeraciones ───────────────────────────────────────────────────────────

class SynapseKind(Enum):
    ELECTRICAL  = "electrical"   # animal → animal  (rápida)
    CHEMICAL    = "chemical"     # micelial → micelial (lenta/conceptual)
    HYBRID      = "hybrid"       # cruce de tipos

class Polarity(Enum):
    EXCITATORY  = "excitatory"
    INHIBITORY  = "inhibitory"
    MODULATORY  = "modulatory"

class TopoMode(Enum):
    SERIAL   = "serial"    # señal pasa en cadena
    PARALLEL = "parallel"  # señal se difunde simultáneamente


# ═══════════════════════════════════════════════════════════════════════════════
#  PLASTICIDAD SINÁPTICA
# ═══════════════════════════════════════════════════════════════════════════════

class PlasticityEngine:
    """Motor de plasticidad sináptica con cuatro mecanismos independientes.

    Mecanismos:
    ┌─────────────┬──────────────────────────────────────────────────────┐
    │  LTP / LTD  │ Potenciación/Depresión a Largo Plazo clásica        │
    │  STDP       │ Spike-Timing Dependent Plasticity (ventana ±20 ms)  │
    │  Hebbiano   │ "Neuronas que disparan juntas, se conectan"          │
    │  Modulatorio│ Escala de peso por neuromodulador externo (DA, ACh) │
    └─────────────┴──────────────────────────────────────────────────────┘
    """

    # Límites de peso sináptico
    W_MIN = 0.05
    W_MAX = 3.0

    # Parámetros LTP/LTD
    LTP_THRESHOLD  = 0.75
    LTD_THRESHOLD  = 0.30
    LTP_RATE       = 0.06
    LTD_RATE       = 0.04

    # Parámetros STDP
    STDP_WINDOW    = 0.025   # ±25 ms
    STDP_A_PLUS    = 0.05    # potenciación máxima
    STDP_A_MINUS   = 0.04    # depresión máxima

    # Parámetros Hebbiano
    HEBB_RATE      = 0.02
    HEBB_DECAY     = 0.001   # decaimiento pasivo del peso

    def __init__(self):
        self._last_pre_ts  = 0.0   # timestamp último disparo pre-sináptico
        self._last_post_ts = 0.0   # timestamp último disparo post-sináptico
        self._coact_sum    = 0.0   # acumulador de co-activación (Hebbian)
        self._coact_n      = 0

    # ── LTP / LTD ─────────────────────────────────────────────────────────
    def ltp_ltd(self, weight: float, signal: float, dt: float) -> float:
        """Ajusta el peso por LTP/LTD según fuerza de la señal."""
        if signal >= self.LTP_THRESHOLD:
            delta = self.LTP_RATE * (self.W_MAX - weight)   # satura suavemente
        elif signal <= self.LTD_THRESHOLD:
            delta = -self.LTD_RATE * (weight - self.W_MIN)
        else:
            delta = 0.0
        return self._clip(weight + delta)

    # ── STDP ──────────────────────────────────────────────────────────────
    def stdp(self, weight: float, pre_ts: float, post_ts: float) -> float:
        """Ajusta el peso por diferencia temporal pre/post."""
        if pre_ts <= 0 or post_ts <= 0:
            return weight
        dt = post_ts - pre_ts
        if abs(dt) > self.STDP_WINDOW * 4:
            return weight
        if dt > 0:   # pre antes que post → potenciación
            delta = self.STDP_A_PLUS * math.exp(-dt / self.STDP_WINDOW)
        else:        # post antes que pre → depresión
            delta = -self.STDP_A_MINUS * math.exp(dt / self.STDP_WINDOW)
        return self._clip(weight + delta)

    # ── Hebbiano ──────────────────────────────────────────────────────────
    def hebbian(self, weight: float, pre_act: float, post_act: float) -> float:
        """Regla Hebbiana: Δw = η·pre·post − decay·w"""
        delta = self.HEBB_RATE * pre_act * post_act - self.HEBB_DECAY * weight
        return self._clip(weight + delta)

    # ── Modulatorio ───────────────────────────────────────────────────────
    def modulatory(self, weight: float, neuromodulator: str,
                   level: float) -> float:
        """Escala el peso por nivel de neuromodulador."""
        factors = {
            "dopamine":      1.0 + level * 0.20,   # refuerzo
            "acetylcholine": 1.0 + level * 0.15,   # atención/aprendizaje
            "serotonin":     1.0 - level * 0.10,   # modulación inhibitoria leve
            "norepinephrine":1.0 + level * 0.12,   # alerta
            "gaba":          1.0 - level * 0.25,   # inhibición
        }
        scale = factors.get(neuromodulator, 1.0)
        return self._clip(weight * scale)

    # ── Registro de timestamps ────────────────────────────────────────────
    def record_pre(self):  self._last_pre_ts  = time.time()
    def record_post(self): self._last_post_ts = time.time()

    def apply_all(self, weight: float, signal: float,
                  pre_act: float = 0.5, post_act: float = 0.5,
                  neuromodulator: str = "", mod_level: float = 0.0) -> float:
        """Aplica todos los mecanismos en secuencia."""
        w = self.ltp_ltd(weight, signal, 0)
        w = self.stdp(w, self._last_pre_ts, self._last_post_ts)
        w = self.hebbian(w, pre_act, post_act)
        if neuromodulator:
            w = self.modulatory(w, neuromodulator, mod_level)
        return w

    @staticmethod
    def _clip(w: float) -> float:
        return max(PlasticityEngine.W_MIN, min(PlasticityEngine.W_MAX, w))


# ═══════════════════════════════════════════════════════════════════════════════
#  PODA INTELIGENTE
# ═══════════════════════════════════════════════════════════════════════════════

class PruningEngine:
    """Motor de poda inteligente multi-criterio.

    Criterios (ponderados):
        utilidad  – transmisiones exitosas recientes
        edad      – sinapsis muy jóvenes o muy viejas sin uso
        error     – tasa de fallo acumulada
        peso      – pesos que han caído por debajo del umbral mínimo
        frecuencia– inactividad prolongada
    """

    def __init__(self,
                 utility_threshold: float = 0.10,
                 error_rate_max:    float = 0.70,
                 inactivity_secs:   float = 300.0,
                 min_weight:        float = 0.06,
                 min_age_secs:      float = 5.0):
        self.utility_threshold = utility_threshold
        self.error_rate_max    = error_rate_max
        self.inactivity_secs   = inactivity_secs
        self.min_weight        = min_weight
        self.min_age_secs      = min_age_secs

    def should_prune(self, syn: "SynapseBase") -> Tuple[bool, str]:
        """Retorna (debe_podar, razón)."""
        now = time.time()

        # ── 1. Peso demasiado bajo ────────────────────────────────────────
        if syn.weight < self.min_weight:
            return True, f"peso_bajo({syn.weight:.3f})"

        # ── 2. Sinapsis muy joven: no podar aún ───────────────────────────
        if (now - syn.creation_time) < self.min_age_secs:
            return False, ""

        # ── 3. Inactividad prolongada ─────────────────────────────────────
        if syn.last_transmission > 0:
            idle = now - syn.last_transmission
            if idle > self.inactivity_secs:
                return True, f"inactividad({idle:.0f}s)"

        # ── 4. Tasa de error alta ─────────────────────────────────────────
        total = syn.success_count + syn.failure_count
        if total >= 5:
            error_rate = syn.failure_count / total
            if error_rate > self.error_rate_max:
                return True, f"tasa_error({error_rate:.2f})"

        # ── 5. Utilidad baja ──────────────────────────────────────────────
        utility = self._utility(syn)
        if utility < self.utility_threshold and total >= 10:
            return True, f"utilidad_baja({utility:.3f})"

        return False, ""

    def utility_score(self, syn: "SynapseBase") -> float:
        return self._utility(syn)

    @staticmethod
    def _utility(syn: "SynapseBase") -> float:
        total = syn.success_count + syn.failure_count
        if total == 0:
            return 0.5   # desconocido → neutro
        base = syn.success_count / total
        # Penalizar peso bajo
        weight_factor = min(1.0, syn.weight / 1.0)
        # Bonificar uso frecuente
        freq_factor = min(1.0, syn.usage_frequency * 10)
        return base * 0.6 + weight_factor * 0.2 + freq_factor * 0.2


# ═══════════════════════════════════════════════════════════════════════════════
#  SINAPSIS BASE
# ═══════════════════════════════════════════════════════════════════════════════

class SynapseBase(ABC):
    """Base para todas las sinapsis del sistema."""

    def __init__(self,
                 synapse_id:   str,
                 source,
                 target,
                 kind:         SynapseKind = SynapseKind.ELECTRICAL,
                 polarity:     Polarity    = Polarity.EXCITATORY,
                 persistent:   bool        = True):

        self.synapse_id    = synapse_id
        self.source_neuron = source
        self.target_neuron = target
        self.kind          = kind
        self.polarity      = polarity
        self.persistent    = persistent   # Si es False, puede borrarse en poda

        # Propiedades de transmisión
        self.weight         = 1.0
        self.threshold      = 0.08
        self.delay          = 0.001      # segundos
        self.is_active_flag = True

        # Estadísticas
        self.creation_time    = time.time()
        self.last_transmission = 0.0
        self.usage_frequency   = 0.0
        self.success_count     = 0
        self.failure_count     = 0

        # Historial compacto (no memoria persistente de contenido)
        self.transmission_history = deque(maxlen=200)

        # Motores
        self.plasticity = PlasticityEngine()
        self.lock        = RLock()

    # ── Activación ────────────────────────────────────────────────────────
    def is_active(self) -> bool:
        return self.is_active_flag and self.weight >= PlasticityEngine.W_MIN

    def activate(self):
        with self.lock:
            self.is_active_flag = True

    def deactivate(self):
        with self.lock:
            self.is_active_flag = False

    # ── Frecuencia de uso ─────────────────────────────────────────────────
    def _update_frequency(self):
        now = time.time()
        if self.last_transmission > 0:
            dt = max(1e-4, now - self.last_transmission)
            self.usage_frequency = 0.9 * self.usage_frequency + 0.1 / dt
        self.last_transmission = now

    # ── Registro ──────────────────────────────────────────────────────────
    def _record(self, sig_in: float, sig_out: float, success: bool,
                context: Dict = None):
        self.transmission_history.append({
            "ts":      time.time(),
            "in":      round(sig_in,  4),
            "out":     round(sig_out, 4),
            "ok":      success,
            "ctx_keys": list((context or {}).keys()),
        })
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self._update_frequency()

    # ── Estado ────────────────────────────────────────────────────────────
    def get_status(self) -> Dict[str, Any]:
        with self.lock:
            total = self.success_count + self.failure_count
            return {
                "id":            self.synapse_id,
                "kind":          self.kind.value,
                "polarity":      self.polarity.value,
                "weight":        round(self.weight, 4),
                "threshold":     self.threshold,
                "active":        self.is_active(),
                "persistent":    self.persistent,
                "success":       self.success_count,
                "failure":       self.failure_count,
                "error_rate":    round(self.failure_count / max(1, total), 3),
                "usage_freq":    round(self.usage_frequency, 4),
                "age_s":         round(time.time() - self.creation_time, 2),
                "last_tx_s_ago": round(time.time() - self.last_transmission, 2)
                                 if self.last_transmission > 0 else None,
            }

    @abstractmethod
    def transmit(self, signal: float, context: Dict = None) -> float:
        """Transmite señal y retorna la señal resultante en destino."""
        pass


# ═══════════════════════════════════════════════════════════════════════════════
#  SINAPSIS CONCRETA: ELÉCTRICA  (animal → animal)
# ═══════════════════════════════════════════════════════════════════════════════

class ElectricalSynapse(SynapseBase):
    """Sinapsis eléctrica rápida. Ideal para neuronas animales.

    Modela una unión gap: bidireccional, baja latencia, sin vesículas.
    La plasticidad es STDP + LTP/LTD. El signo depende de la polaridad.
    """

    def __init__(self, synapse_id: str, source, target,
                 polarity: Polarity = Polarity.EXCITATORY,
                 persistent: bool   = True):
        super().__init__(synapse_id, source, target,
                         SynapseKind.ELECTRICAL, polarity, persistent)
        self.conductance     = 1.0
        self.time_constant   = 0.002    # 2 ms
        self.delay           = 0.001    # 1 ms

    def transmit(self, signal: float, context: Dict = None) -> float:
        with self.lock:
            context = context or {}
            if not self.is_active() or signal < self.threshold:
                self._record(signal, 0.0, False, context)
                return 0.0

            self.plasticity.record_pre()

            # Corriente sináptica
            decay   = math.exp(-self.time_constant)
            raw_out = self.conductance * signal * self.weight * decay

            # Polaridad
            if self.polarity == Polarity.INHIBITORY:
                raw_out = -raw_out
            elif self.polarity == Polarity.MODULATORY:
                raw_out *= 0.5

            raw_out = max(0.0, min(1.0, raw_out))

            # Plasticidad
            nm  = context.get("neuromodulator", "")
            nml = context.get("nm_level", 0.0)
            pre_act  = signal
            post_act = getattr(self.target_neuron, "activation_level", 0.5)
            self.weight = self.plasticity.apply_all(
                self.weight, signal, pre_act, post_act, nm, nml
            )

            # Enviar a la neurona destino
            result = self._dispatch_animal(raw_out, context)
            self.plasticity.record_post()
            self._record(signal, result, True, context)
            return result

    def _dispatch_animal(self, sig: float, context: Dict) -> float:
        if self.target_neuron is None:
            return sig
        try:
            if hasattr(self.target_neuron, "receive_signal"):
                r = self.target_neuron.receive_signal(sig, "electrical", context)
                return float(r) if r is not None else sig
            return sig
        except Exception as e:
            log_neuron_error(self.synapse_id, f"dispatch_animal: {e}")
            self.failure_count += 1
            return 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  SINAPSIS CONCRETA: QUÍMICA  (micelial → micelial)
# ═══════════════════════════════════════════════════════════════════════════════

class ChemicalSynapse(SynapseBase):
    """Sinapsis química lenta. Ideal para neuronas miceliales.

    Modela liberación de vesículas, difusión y degradación en la hendidura.
    La plasticidad es Hebbiana + modulatoria.
    """

    NEUROTRANSMITTERS = ["dopamine", "serotonin", "acetylcholine",
                         "gaba", "glutamate", "octopamine"]

    def __init__(self, synapse_id: str, source, target,
                 polarity: Polarity   = Polarity.EXCITATORY,
                 primary_nt: str      = "dopamine",
                 persistent: bool     = True):
        super().__init__(synapse_id, source, target,
                         SynapseKind.CHEMICAL, polarity, persistent)
        self.primary_nt          = primary_nt if primary_nt in self.NEUROTRANSMITTERS else "dopamine"
        self.vesicle_pool        = 1000
        self.vesicles_per_pulse  = 10
        self.refill_rate         = 12
        self.release_prob        = 0.82
        self.cleft_conc          = 0.0
        self.diffusion_rate      = 0.06
        self.degradation_rate    = 0.04
        self.receptor_sensitivity = 1.2
        self.delay               = 0.005    # 5 ms

    def transmit(self, signal: float, context: Dict = None) -> float:
        with self.lock:
            context = context or {}
            if not self.is_active() or signal < self.threshold:
                self._record(signal, 0.0, False, context)
                return 0.0

            # Vesículas
            if self.vesicle_pool < self.vesicles_per_pulse:
                self.vesicle_pool += self.refill_rate
                self._record(signal, 0.0, False, context)
                return 0.0

            if random.random() > self.release_prob * signal:
                self._record(signal, 0.0, False, context)
                return 0.0

            # Liberar vesículas
            released = min(self.vesicles_per_pulse,
                           int(self.vesicles_per_pulse * (0.8 + signal * 0.4)))
            self.vesicle_pool = max(0, self.vesicle_pool - released)
            conc_delta = released * 0.12
            self.cleft_conc = min(2.0, self.cleft_conc + conc_delta)

            # Respuesta post-sináptica
            nt       = context.get("neurotransmitter", self.primary_nt)
            sens_map = {"gaba": 0.6, "glutamate": 1.4, "dopamine": 1.1,
                        "serotonin": 0.9, "acetylcholine": 1.0, "octopamine": 1.2}
            nt_sens  = sens_map.get(nt, 1.0)
            sign     = -1.0 if self.polarity == Polarity.INHIBITORY else 1.0
            raw_out  = max(0.0, min(1.0,
                self.cleft_conc * self.receptor_sensitivity * nt_sens *
                self.weight * signal * sign * 0.3
            ))

            # Plasticidad
            nm  = context.get("neuromodulator", nt)
            nml = context.get("nm_level", self.cleft_conc)
            pre_act  = signal
            post_act = getattr(self.target_neuron, "activation_level", 0.5)
            self.weight = self.plasticity.apply_all(
                self.weight, signal, pre_act, post_act, nm, nml
            )

            # Actualizar estado químico
            self.cleft_conc    *= (1 - self.degradation_rate)
            self.vesicle_pool   = min(1200, self.vesicle_pool + self.refill_rate)

            # Enviar a neurona destino
            result = self._dispatch_micelial(raw_out, context)
            self._record(signal, result, True, context)
            return result

    def _dispatch_micelial(self, sig: float, context: Dict) -> float:
        if self.target_neuron is None:
            return sig
        try:
            if hasattr(self.target_neuron, "receive_concept"):
                concept = context.get("concept", "chemical_signal")
                r = self.target_neuron.receive_concept(sig, concept, context)
                return float(r) if r is not None else sig
            if hasattr(self.target_neuron, "receive_signal"):
                r = self.target_neuron.receive_signal(sig, "chemical", context)
                return float(r) if r is not None else sig
            return sig
        except Exception as e:
            log_neuron_error(self.synapse_id, f"dispatch_micelial: {e}")
            self.failure_count += 1
            return 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  SINAPSIS CONCRETA: HÍBRIDA  (cruces animal ↔ micelial)
# ═══════════════════════════════════════════════════════════════════════════════

class HybridSynapse(SynapseBase):
    """Sinapsis híbrida que convierte señales entre dominios.

    animal  → micelial : eléctrica → química  (normaliza a [0,1], añade contexto)
    micelial → animal  : química  → eléctrica (extrae activación del concepto)
    animal  → animal   : delegado a ElectricalSynapse
    micelial → micelial: delegado a ChemicalSynapse
    """

    COMPAT = {
        ("animal",   "micelial"): ("elec→chem", 0.75),
        ("micelial", "animal"):   ("chem→elec", 0.65),
        ("animal",   "animal"):   ("elec→elec", 1.00),
        ("micelial", "micelial"): ("chem→chem", 1.00),
    }

    def __init__(self, synapse_id: str, source, target,
                 polarity: Polarity = Polarity.EXCITATORY,
                 persistent: bool   = True):
        super().__init__(synapse_id, source, target,
                         SynapseKind.HYBRID, polarity, persistent)
        self.conversion_efficiency = 0.82
        self.signal_amplification  = 1.15
        self.delay                 = 0.003    # 3 ms

    @staticmethod
    def _neuron_domain(neuron) -> str:
        nt = getattr(neuron, "neuron_type", "")
        if "micelial" in nt or isinstance(neuron, CognitiveMicelialNeuronBase):
            return "micelial"
        return "animal"

    def transmit(self, signal: float, context: Dict = None) -> float:
        with self.lock:
            context = context or {}
            if not self.is_active() or signal < self.threshold:
                self._record(signal, 0.0, False, context)
                return 0.0

            src_domain = self._neuron_domain(self.source_neuron)
            tgt_domain = self._neuron_domain(self.target_neuron)
            route, compat = self.COMPAT.get(
                (src_domain, tgt_domain), ("generic", 0.7)
            )

            self.plasticity.record_pre()

            # Conversión
            converted = signal * self.weight * self.conversion_efficiency * \
                        self.signal_amplification * compat
            if self.polarity == Polarity.INHIBITORY:
                converted *= 0.3
            converted = max(0.0, min(1.0, converted))

            # Plasticidad
            nm  = context.get("neuromodulator", "dopamine")
            nml = context.get("nm_level", 0.3)
            pre_act  = signal
            post_act = getattr(self.target_neuron, "activation_level", 0.5)
            self.weight = self.plasticity.apply_all(
                self.weight, signal, pre_act, post_act, nm, nml
            )

            # Despachar según dirección
            result = self._dispatch(converted, route, context)
            self.plasticity.record_post()
            self._record(signal, result, True, context)
            return result

    def _dispatch(self, sig: float, route: str, context: Dict) -> float:
        if self.target_neuron is None:
            return sig
        try:
            if route in ("elec→chem", "chem→chem"):
                # Destino micelial: receive_concept
                if hasattr(self.target_neuron, "receive_concept"):
                    concept = context.get("concept", "hybrid_signal")
                    r = self.target_neuron.receive_concept(sig, concept, context)
                    return float(r) if r is not None else sig
            # Destino animal o genérico: receive_signal
            if hasattr(self.target_neuron, "receive_signal"):
                pattern = context.get("pattern", route)
                r = self.target_neuron.receive_signal(sig, pattern, context)
                return float(r) if r is not None else sig
            return sig
        except Exception as e:
            log_neuron_error(self.synapse_id, f"hybrid_dispatch: {e}")
            self.failure_count += 1
            return 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  TOPOLOGÍA: PARALELO Y SERIAL
# ═══════════════════════════════════════════════════════════════════════════════

class ParallelBundle:
    """Agrupa N sinapsis en paralelo: la señal se difunde a todas simultáneamente.

    La salida es el promedio ponderado de todas las respuestas activas.
    Útil para broadcast de señales sensoriales o conceptuales.
    """

    def __init__(self, bundle_id: str):
        self.bundle_id  = bundle_id
        self.synapses: List[SynapseBase] = []
        self.lock       = RLock()

    def add(self, syn: SynapseBase):
        with self.lock:
            self.synapses.append(syn)

    def transmit(self, signal: float, context: Dict = None) -> Dict[str, float]:
        """Difunde la señal. Retorna {synapse_id: resultado}."""
        results = {}
        with self.lock:
            active = [s for s in self.synapses if s.is_active()]
        for syn in active:
            try:
                results[syn.synapse_id] = syn.transmit(signal, context)
            except Exception as e:
                log_neuron_error(syn.synapse_id, f"parallel_tx: {e}")
                results[syn.synapse_id] = 0.0
        return results

    def aggregate(self, results: Dict[str, float]) -> float:
        """Promedio ponderado de salidas (peso de cada sinapsis)."""
        if not results:
            return 0.0
        with self.lock:
            weight_map = {s.synapse_id: s.weight for s in self.synapses}
        total_w = sum(weight_map.get(k, 1.0) for k in results)
        if total_w == 0:
            return 0.0
        return sum(v * weight_map.get(k, 1.0) for k, v in results.items()) / total_w

    def get_status(self) -> Dict:
        with self.lock:
            return {
                "bundle_id":    self.bundle_id,
                "mode":         "parallel",
                "total":        len(self.synapses),
                "active":       sum(1 for s in self.synapses if s.is_active()),
                "avg_weight":   round(sum(s.weight for s in self.synapses) /
                                      max(1, len(self.synapses)), 4),
            }


class SerialChain:
    """Encadena N sinapsis en serie: la salida de cada una alimenta la siguiente.

    Útil para pipelines de procesamiento (sensorial → integrativa → motora).
    """

    def __init__(self, chain_id: str):
        self.chain_id  = chain_id
        self.synapses: List[SynapseBase] = []
        self.lock       = RLock()

    def add(self, syn: SynapseBase):
        with self.lock:
            self.synapses.append(syn)

    def transmit(self, signal: float, context: Dict = None) -> float:
        """Propaga la señal por la cadena. Retorna la señal final."""
        current = signal
        with self.lock:
            chain = list(self.synapses)
        for syn in chain:
            if not syn.is_active():
                continue
            try:
                current = syn.transmit(current, context)
            except Exception as e:
                log_neuron_error(syn.synapse_id, f"serial_tx: {e}")
                current = 0.0
            if current <= 0:
                break
        return current

    def get_status(self) -> Dict:
        with self.lock:
            return {
                "chain_id": self.chain_id,
                "mode":     "serial",
                "length":   len(self.synapses),
                "active":   sum(1 for s in self.synapses if s.is_active()),
                "stages":   [s.synapse_id for s in self.synapses],
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  GESTOR CENTRAL DE SINAPSIS
# ═══════════════════════════════════════════════════════════════════════════════

class SynapseManager:
    """Gestor central de todas las sinapsis de la red híbrida.

    Responsabilidades:
    ─ Crear/registrar sinapsis individuales, bundles y cadenas
    ─ Ejecutar poda inteligente periódica
    ─ Exponer estadísticas globales
    ─ Seleccionar automáticamente el tipo de sinapsis óptimo
    """

    _SYN_COUNTER = 0
    _COUNTER_LOCK = RLock()

    def __init__(self,
                 prune_interval_s: float   = 60.0,
                 utility_threshold: float  = 0.10,
                 error_rate_max:    float  = 0.70,
                 inactivity_secs:   float  = 300.0):

        self.synapses:  Dict[str, SynapseBase]   = {}
        self.bundles:   Dict[str, ParallelBundle] = {}
        self.chains:    Dict[str, SerialChain]    = {}

        self.pruning    = PruningEngine(utility_threshold, error_rate_max,
                                        inactivity_secs)
        self.lock        = RLock()
        self._prune_interval  = prune_interval_s
        self._last_prune      = time.time()
        self._pruned_total    = 0
        self._prune_log       = deque(maxlen=100)

    # ── IDs únicos ────────────────────────────────────────────────────────
    @classmethod
    def _new_id(cls, prefix: str = "syn") -> str:
        with cls._COUNTER_LOCK:
            cls._SYN_COUNTER += 1
            return f"{prefix}_{cls._SYN_COUNTER:05d}"

    # ── Selección automática de tipo ──────────────────────────────────────
    @staticmethod
    def _auto_kind(source, target) -> str:
        def domain(n):
            nt = getattr(n, "neuron_type", "")
            return "micelial" if ("micelial" in nt or
                    isinstance(n, CognitiveMicelialNeuronBase)) else "animal"
        s, t = domain(source), domain(target)
        if s == "animal"   and t == "animal":   return "electrical"
        if s == "micelial" and t == "micelial": return "chemical"
        return "hybrid"

    # ── Crear sinapsis individual ─────────────────────────────────────────
    def connect(self, source, target,
                kind: str        = "auto",
                polarity: str    = "excitatory",
                persistent: bool = True,
                weight: float    = 1.0) -> SynapseBase:
        """Crea y registra una sinapsis entre dos neuronas."""

        if kind == "auto":
            kind = self._auto_kind(source, target)

        pol = {
            "excitatory": Polarity.EXCITATORY,
            "inhibitory": Polarity.INHIBITORY,
            "modulatory": Polarity.MODULATORY,
        }.get(polarity, Polarity.EXCITATORY)

        sid = self._new_id("syn")
        cls_map = {
            "electrical": ElectricalSynapse,
            "chemical":   ChemicalSynapse,
            "hybrid":     HybridSynapse,
        }
        SynCls = cls_map.get(kind, HybridSynapse)
        syn    = SynCls(sid, source, target, pol, persistent)
        syn.weight = max(PlasticityEngine.W_MIN,
                         min(PlasticityEngine.W_MAX, weight))

        with self.lock:
            self.synapses[sid] = syn

        log_event(f"Sinapsis {sid} ({kind}|{polarity}) "
                  f"{getattr(source,'neuron_id','?')}→"
                  f"{getattr(target,'neuron_id','?')}", "DEBUG")
        return syn

    # ── Bundles y cadenas ─────────────────────────────────────────────────
    def create_parallel_bundle(self,
                               sources: List,
                               target,
                               kind: str    = "auto",
                               polarity: str = "excitatory") -> ParallelBundle:
        """Crea un bundle paralelo: múltiples fuentes → un destino."""
        bid    = self._new_id("bnd")
        bundle = ParallelBundle(bid)
        for src in sources:
            syn = self.connect(src, target, kind, polarity)
            bundle.add(syn)
        with self.lock:
            self.bundles[bid] = bundle
        return bundle

    def create_serial_chain(self,
                            neurons: List,
                            kind: str     = "auto",
                            polarity: str = "excitatory") -> SerialChain:
        """Crea una cadena serial: neurona[0]→[1]→[2]→… """
        cid   = self._new_id("chn")
        chain = SerialChain(cid)
        for i in range(len(neurons) - 1):
            syn = self.connect(neurons[i], neurons[i+1], kind, polarity)
            chain.add(syn)
        with self.lock:
            self.chains[cid] = chain
        return chain

    # ── Transmisión ───────────────────────────────────────────────────────
    def transmit(self, synapse_id: str, signal: float,
                 context: Dict = None) -> float:
        syn = self.synapses.get(synapse_id)
        if syn is None:
            return 0.0
        return syn.transmit(signal, context)

    # ── Poda inteligente ──────────────────────────────────────────────────
    def prune(self, force: bool = False) -> Dict[str, Any]:
        """Ejecuta un ciclo de poda. Retorna reporte."""
        now = time.time()
        if not force and (now - self._last_prune) < self._prune_interval:
            return {"skipped": True}

        report = {"evaluated": 0, "pruned": 0, "reasons": defaultdict(int),
                  "persistent_kept": 0}

        with self.lock:
            candidates = list(self.synapses.items())

        to_remove = []
        for sid, syn in candidates:
            report["evaluated"] += 1
            if syn.persistent:
                report["persistent_kept"] += 1
                continue
            should, reason = self.pruning.should_prune(syn)
            if should:
                to_remove.append((sid, reason))
                report["pruned"] += 1
                report["reasons"][reason.split("(")[0]] += 1

        with self.lock:
            for sid, reason in to_remove:
                self.synapses.pop(sid, None)
                self._prune_log.append({"ts": now, "id": sid, "reason": reason})

        self._pruned_total += report["pruned"]
        self._last_prune    = now
        report["total_pruned_ever"] = self._pruned_total

        if report["pruned"] > 0:
            log_event(f"Poda: {report['pruned']}/{report['evaluated']} "
                      f"eliminadas. {dict(report['reasons'])}", "INFO")
        return report

    # ── Estadísticas globales ─────────────────────────────────────────────
    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            syns = list(self.synapses.values())

        total   = len(syns)
        active  = sum(1 for s in syns if s.is_active())
        by_kind = defaultdict(int)
        by_pol  = defaultdict(int)
        weights = []
        utilities = []

        for s in syns:
            by_kind[s.kind.value] += 1
            by_pol[s.polarity.value] += 1
            weights.append(s.weight)
            utilities.append(self.pruning.utility_score(s))

        avg_w = sum(weights)   / max(1, total)
        avg_u = sum(utilities) / max(1, total)
        min_w = min(weights,   default=0.0)
        max_w = max(weights,   default=0.0)

        return {
            "total_synapses":    total,
            "active_synapses":   active,
            "inactive_synapses": total - active,
            "bundles":           len(self.bundles),
            "chains":            len(self.chains),
            "by_kind":           dict(by_kind),
            "by_polarity":       dict(by_pol),
            "avg_weight":        round(avg_w, 4),
            "min_weight":        round(min_w, 4),
            "max_weight":        round(max_w, 4),
            "avg_utility":       round(avg_u, 4),
            "total_pruned_ever": self._pruned_total,
            "prune_log_size":    len(self._prune_log),
        }

    def list_synapses(self) -> List[Dict]:
        with self.lock:
            return [s.get_status() for s in self.synapses.values()]

    def remove(self, synapse_id: str) -> bool:
        with self.lock:
            if synapse_id in self.synapses:
                del self.synapses[synapse_id]
                return True
        return False


# ═══════════════════════════════════════════════════════════════════════════════
#  DIAGNÓSTICO INTERACTIVO
# ═══════════════════════════════════════════════════════════════════════════════

_SEP  = "─" * 62
_SEP2 = "═" * 62

_ANIMAL_TYPES = [
    "visual_feature_extractor",
    "attention_focuser",
    "decision_maker",
    "risk_assessor",
    "anomaly_detector",
    "place_cell",
    "mirror_neuron",
    "cpg_neuron",
    "dopaminergic_modulator",
    "adaptive_threshold_cell",
    "chemotaxis_gradient",
    "head_direction_cell",
    "speed_neuron",
    "song_neuron",
    "barometric_neuron",
]

_MICELIAL_TYPES = [
    "abstract_pattern_integrator",
    "global_coherence_coordinator",
    "conceptual_bridge_builder",
    "insight_propagator",
    "knowledge_synthesizer",
    "hyphal_integrator",
    "anastomosis_node",
    "plasmodium_collector",
    "calcium_wave_messenger",
    "quorum_sensing_node",
    "stomatal_guard_cell",
    "glycolytic_oscillator",
    "systemic_resistance_node",
    "auxin_gradient",
    "turgor_pressure_integrator",
]


def _ask_int(prompt: str, lo: int, hi: int, default: int) -> int:
    while True:
        try:
            raw = input(f"{prompt} [{lo}-{hi}, default={default}]: ").strip()
            if raw == "":
                return default
            val = int(raw)
            if lo <= val <= hi:
                return val
            print(f"  ⚠ Ingresa un número entre {lo} y {hi}.")
        except (ValueError, KeyboardInterrupt):
            return default


def _build_network(n_animal: int, n_micelial: int):
    """Crea las neuronas animales y miceliales solicitadas."""
    animals, micelials = [], []

    for i in range(n_animal):
        ntype = _ANIMAL_TYPES[i % len(_ANIMAL_TYPES)]
        nid   = f"A_{i+1:03d}_{ntype[:6]}"
        kwargs = {}
        if ntype == "visual_feature_extractor":
            kwargs["feature_type"] = "motion"
        elif ntype == "chemotaxis_gradient":
            kwargs["chemical"] = "glucose"
        elif ntype == "place_cell":
            kwargs["preferred_location"] = (random.random(), random.random())
        elif ntype == "mirror_neuron":
            kwargs["action_class"] = "grasp"
        elif ntype == "head_direction_cell":
            kwargs["preferred_angle_deg"] = random.uniform(0, 360)
        elif ntype == "song_neuron":
            kwargs["template"] = [random.uniform(0.2, 0.9) for _ in range(5)]
        try:
            n = create_cognitive_animal_neuron(ntype, nid, **kwargs)
            animals.append(n)
        except Exception as e:
            log_neuron_error(nid, f"build_network (animal): {e}")

    for i in range(n_micelial):
        ntype = _MICELIAL_TYPES[i % len(_MICELIAL_TYPES)]
        nid   = f"M_{i+1:03d}_{ntype[:6]}"
        kwargs = {}
        if ntype == "knowledge_synthesizer":
            kwargs["domain_specializations"] = ["science", "art"]
        try:
            n = create_cognitive_micelial_neuron(ntype, nid, **kwargs)
            micelials.append(n)
        except Exception as e:
            log_neuron_error(nid, f"build_network (micelial): {e}")

    return animals, micelials


def _wire_network(mgr: SynapseManager,
                  animals: List, micelials: List) -> Dict:
    """Crea un conjunto representativo de sinapsis."""
    created = {"electrical": 0, "chemical": 0, "hybrid": 0,
               "bundles": 0, "chains": 0}

    # ── Sinapsis eléctricas: animal → animal ──────────────────────────────
    for i in range(min(len(animals), max(1, len(animals) - 1))):
        src = animals[i]
        tgt = animals[(i + 1) % len(animals)]
        pol = "inhibitory" if i % 4 == 3 else "excitatory"
        mgr.connect(src, tgt, "electrical", pol, persistent=(i % 3 != 0))
        created["electrical"] += 1

    # ── Sinapsis químicas: micelial → micelial ────────────────────────────
    for i in range(min(len(micelials), max(1, len(micelials) - 1))):
        src = micelials[i]
        tgt = micelials[(i + 1) % len(micelials)]
        pol = "modulatory" if i % 5 == 4 else "excitatory"
        mgr.connect(src, tgt, "chemical", pol, persistent=True)
        created["chemical"] += 1

    # ── Sinapsis híbridas: animal ↔ micelial ──────────────────────────────
    n_hybrid = min(len(animals), len(micelials), 4)
    for i in range(n_hybrid):
        a = animals[i]
        m = micelials[i % len(micelials)]
        mgr.connect(a, m, "hybrid", "excitatory", persistent=True)
        created["hybrid"] += 1
        if len(micelials) > 1:
            mgr.connect(micelials[(i+1) % len(micelials)], a,
                        "hybrid", "modulatory", persistent=False)
            created["hybrid"] += 1

    # ── Bundle paralelo ───────────────────────────────────────────────────
    if len(animals) >= 3:
        tgt = micelials[0] if micelials else animals[-1]
        b   = mgr.create_parallel_bundle(animals[:3], tgt, "hybrid")
        created["bundles"] += 1

    # ── Cadena serial ─────────────────────────────────────────────────────
    if len(animals) >= 3:
        chain_nodes = animals[:3]
        if micelials:
            chain_nodes = animals[:2] + [micelials[0]]
        mgr.create_serial_chain(chain_nodes)
        created["chains"] += 1

    return created


def _run_transmissions(mgr: SynapseManager,
                       animals: List, micelials: List,
                       n_rounds: int = 5) -> Dict:
    """Ejecuta rondas de transmisión por todas las sinapsis registradas."""
    report = {"rounds": n_rounds, "total_tx": 0, "successful": 0, "failed": 0}

    with mgr.lock:
        syns = list(mgr.synapses.values())

    for rnd in range(n_rounds):
        for syn in syns:
            signal = random.uniform(0.3, 1.0)
            ctx    = {
                "concept":       f"test_concept_{rnd}",
                "neuromodulator": random.choice(["dopamine", "gaba", "serotonin"]),
                "nm_level":       random.uniform(0.1, 0.8),
                "pattern":        "diagnostic",
            }
            try:
                out = syn.transmit(signal, ctx)
                report["total_tx"]  += 1
                if out > 0:
                    report["successful"] += 1
                else:
                    report["failed"] += 1
            except Exception as e:
                log_neuron_error(syn.synapse_id, f"diagnostic_tx: {e}")
                report["failed"] += 1
                report["total_tx"] += 1

    # Bundles
    for bnd in mgr.bundles.values():
        sig     = random.uniform(0.5, 0.9)
        results = bnd.transmit(sig, {"concept": "bundle_test"})
        agg     = bnd.aggregate(results)
        report["total_tx"] += len(results)
        report["successful"] += sum(1 for v in results.values() if v > 0)
        report["failed"]    += sum(1 for v in results.values() if v <= 0)

    # Chains
    for chn in mgr.chains.values():
        sig = random.uniform(0.5, 0.9)
        out = chn.transmit(sig, {"pattern": "chain_test"})
        report["total_tx"]  += 1
        report["successful"] += 1 if out > 0 else 0
        report["failed"]    += 0 if out > 0 else 1

    return report


def _print_synapse_table(synapse_list: List[Dict]):
    """Imprime tabla compacta de sinapsis."""
    header = (f"{'ID':<14} {'Tipo':<12} {'Pol':<11} "
              f"{'Peso':>6} {'Util':>5} {'OK':>4} {'ERR':>4} "
              f"{'Err%':>5} {'Pers':>5}")
    print(header)
    print(_SEP)
    for s in synapse_list:
        total  = s["success"] + s["failure"]
        err_p  = f"{s['error_rate']*100:.0f}%" if total > 0 else "N/A"
        pers   = "✓" if s["persistent"] else "─"
        active = "✓" if s["active"] else "✗"
        print(f"{s['id']:<14} {s['kind']:<12} {s['polarity']:<11} "
              f"{s['weight']:>6.3f} {s['age_s']:>5.1f}s "
              f"{s['success']:>4} {s['failure']:>4} "
              f"{err_p:>5} {pers:>5}")


def run_diagnostic():
    """Diagnóstico interactivo completo del sistema de sinapsis."""
    print()
    print(_SEP2)
    print(f"  DIAGNÓSTICO – SISTEMA DE SINAPSIS HÍBRIDAS")
    print(_SEP2)

    # ── 1. Elegir cantidad de neuronas ────────────────────────────────────
    print("\nConfigura el tamaño de la red de prueba:\n")
    n_animal   = _ask_int("  Neuronas animales",   1, 15, 5)
    n_micelial = _ask_int("  Neuronas miceliales", 1, 15, 5)
    n_rounds   = _ask_int("  Rondas de transmisión", 1, 20, 5)

    print(f"\n  → {n_animal} animales · {n_micelial} miceliales · "
          f"{n_rounds} rondas\n")

    # ── 2. Construir red ──────────────────────────────────────────────────
    print(_SEP)
    print("  [1/5] Creando neuronas…")
    t0 = time.time()
    animals, micelials = _build_network(n_animal, n_micelial)
    print(f"       ✓ {len(animals)} animales · {len(micelials)} miceliales "
          f"({(time.time()-t0)*1000:.1f} ms)")

    # ── 3. Cablear sinapsis ───────────────────────────────────────────────
    print(_SEP)
    print("  [2/5] Creando sinapsis…")
    mgr = SynapseManager(prune_interval_s=10.0,
                          utility_threshold=0.10,
                          error_rate_max=0.75,
                          inactivity_secs=60.0)
    t0 = time.time()
    wire_report = _wire_network(mgr, animals, micelials)
    stats = mgr.get_stats()
    print(f"       ✓ {stats['total_synapses']} sinapsis  "
          f"({wire_report['electrical']} eléctricas · "
          f"{wire_report['chemical']} químicas · "
          f"{wire_report['hybrid']} híbridas)")
    print(f"         {wire_report['bundles']} bundles paralelos · "
          f"{wire_report['chains']} cadenas seriales "
          f"({(time.time()-t0)*1000:.1f} ms)")

    # ── 4. Transmisiones ──────────────────────────────────────────────────
    print(_SEP)
    print(f"  [3/5] Ejecutando {n_rounds} rondas de transmisión…")
    t0 = time.time()
    tx_report = _run_transmissions(mgr, animals, micelials, n_rounds)
    elapsed   = (time.time() - t0) * 1000
    sr = tx_report["successful"] / max(1, tx_report["total_tx"]) * 100
    print(f"       ✓ {tx_report['total_tx']} transmisiones  "
          f"({tx_report['successful']} ✓  {tx_report['failed']} ✗  "
          f"tasa_éxito={sr:.1f}%)  [{elapsed:.1f} ms]")

    # ── 5. Plasticidad: verificar cambios de peso ─────────────────────────
    print(_SEP)
    print("  [4/5] Analizando plasticidad sináptica…")
    with mgr.lock:
        syns_snap = [(s.synapse_id, s.weight, s.kind.value)
                     for s in mgr.synapses.values()]
    changed  = sum(1 for _, w, _ in syns_snap if abs(w - 1.0) > 0.01)
    avg_w    = sum(w for _, w, _ in syns_snap) / max(1, len(syns_snap))
    min_w    = min((w for _, w, _ in syns_snap), default=0)
    max_w    = max((w for _, w, _ in syns_snap), default=0)
    print(f"       ✓ {changed}/{len(syns_snap)} sinapsis modificaron su peso")
    print(f"         peso promedio={avg_w:.4f}  min={min_w:.4f}  max={max_w:.4f}")

    # ── 6. Poda ───────────────────────────────────────────────────────────
    print(_SEP)
    print("  [5/5] Ejecutando ciclo de poda inteligente…")
    prune_report = mgr.prune(force=True)
    print(f"       ✓ Evaluadas={prune_report['evaluated']}  "
          f"Podadas={prune_report['pruned']}  "
          f"Persistentes conservadas={prune_report['persistent_kept']}")
    if prune_report["reasons"]:
        for reason, count in prune_report["reasons"].items():
            print(f"         • {reason}: {count}")

    # ── 7. Tabla de sinapsis ──────────────────────────────────────────────
    final_stats = mgr.get_stats()
    print()
    print(_SEP2)
    print("  ESTADO FINAL DE SINAPSIS")
    print(_SEP2)
    print(f"  Total: {final_stats['total_synapses']}  "
          f"Activas: {final_stats['active_synapses']}  "
          f"Inactivas: {final_stats['inactive_synapses']}")
    print(f"  Por tipo:     {final_stats['by_kind']}")
    print(f"  Por polaridad:{final_stats['by_polarity']}")
    print(f"  Peso: avg={final_stats['avg_weight']}  "
          f"min={final_stats['min_weight']}  max={final_stats['max_weight']}")
    print(f"  Utilidad promedio: {final_stats['avg_utility']}")
    print(f"  Bundles paralelos: {final_stats['bundles']}  "
          f"Cadenas seriales: {final_stats['chains']}")
    print()

    syn_list = mgr.list_synapses()
    if syn_list:
        print(_SEP)
        print(f"  {'ID':<14} {'Tipo':<12} {'Pol':<11} "
              f"{'Peso':>6} {'Edad':>6} {'OK':>4} {'ERR':>4} "
              f"{'Err%':>5} {'Pers':>5}")
        print(_SEP)
        for s in syn_list[:30]:   # máximo 30 filas
            total = s["success"] + s["failure"]
            err_p = f"{s['error_rate']*100:.0f}%" if total > 0 else "─"
            pers  = "✓" if s["persistent"] else "─"
            actv  = "✓" if s["active"] else "✗"
            print(f"  {s['id']:<14} {s['kind']:<12} {s['polarity']:<11} "
                  f"{s['weight']:>6.3f} {s['age_s']:>5.1f}s "
                  f"{s['success']:>4} {s['failure']:>4} "
                  f"{err_p:>5} {pers:>5}")
        if len(syn_list) > 30:
            print(f"  … y {len(syn_list)-30} sinapsis más (omitidas)")

    # ── 8. Resumen ejecutivo ──────────────────────────────────────────────
    print()
    print(_SEP2)
    print("  RESUMEN EJECUTIVO")
    print(_SEP2)
    health = "ÓPTIMO"
    if sr < 50:  health = "CRÍTICO"
    elif sr < 75: health = "ADVERTENCIA"
    elif sr < 90: health = "ESTABLE"

    print(f"  Estado:          {health}")
    print(f"  Neuronas:        {len(animals)} animales  +  {len(micelials)} miceliales")
    print(f"  Sinapsis finales:{final_stats['total_synapses']}")
    print(f"  Tasa de éxito:   {sr:.1f}%")
    print(f"  Podadas total:   {final_stats['total_pruned_ever']}")
    print(f"  Plasticidad:     {changed} sinapsis modificadas de {len(syns_snap)}")
    print()
    print("  ✓ Sistema listo para integración híbrida animal-micelial")
    print(_SEP2)
    print()

    return mgr, animals, micelials


# ═══════════════════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        mgr, animals, micelials = run_diagnostic()
    except KeyboardInterrupt:
        print("\n  Diagnóstico interrumpido por el usuario.")
    except Exception as exc:
        print(f"\n❌ Error inesperado: {exc}")
        traceback.print_exc()
