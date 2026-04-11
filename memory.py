# memory.py
"""
Sistema de Memoria Híbrida — Superior a la Biológica.

Principios de diseño:
  ─ La memoria NO es almacenamiento: es reconstrucción dinámica.
  ─ Todo recuerdo lleva peso emocional (valencia + arousal) que modula
    su fuerza, accesibilidad y capacidad de contagiar otros recuerdos.
  ─ Los instintos actúan como amplificadores: un recuerdo de peligro
    siempre es más accesible que uno neutro.
  ─ Las memorias se combinan: algo reciente puede evocar algo lejano
    si comparten valencia emocional o etiquetas instintivas.
  ─ Hay memorias que construyen el yo (Self-Forming Memories, SFM):
    acumulan "peso de identidad" con cada acceso.
  ─ Hay memoria efímera (EM): alta volatilidad, pero influye en el yo
    en pequeña medida antes de desaparecer.
  ─ El tiempo degrada, pero la superposición emocional puede
    "rejuvenecer" recuerdos antiguos (como recordar lo que nos gustaba
    de niños cuando lo volvemos a encontrar).
  ─ Compatible con adaptive.py (instintos + emociones) y el ecosistema
    neuronal (animal.py, micelial.py, synapse.py).

Capas de memoria:
  EPHEMERAL   — segundos/minutos; alta volatilidad; Valencia decide si sube
  WORKING     — minutos/horas; se consolida si es accedida o emocionalmente fuerte
  ASSOCIATIVE — días/semanas; red de asociaciones; evoca por similitud emocional
  CONSOLIDATED— meses/años; estable; semi-permanente
  SELF        — permanente; forma el yo; consciente e inconsciente

Diagnóstico interactivo al ejecutar directamente.
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
from threading import RLock
from typing import Any, Dict, List, Optional, Tuple

# ── Integración opcional con adaptive.py ────────────────────────────────────
try:
    from adaptive import EmotionEngine, InstinctCore, InstinctID, EmotionID
    _HAS_ADAPTIVE = True
except ImportError:
    _HAS_ADAPTIVE = False


# ═══════════════════════════════════════════════════════════════════════════════
#  ESTRUCTURAS DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryLayer(Enum):
    EPHEMERAL    = "ephemeral"     # volatilidad máxima
    WORKING      = "working"       # activa, de trabajo
    ASSOCIATIVE  = "associative"   # red de relaciones
    CONSOLIDATED = "consolidated"  # estable a largo plazo
    SELF         = "self"          # núcleo identitario


# Parámetros de cada capa
_LAYER_CONFIG = {
    MemoryLayer.EPHEMERAL:    {"decay_rate": 0.15,  "min_valence_to_rise": 0.45, "max_age_s": 300},
    MemoryLayer.WORKING:      {"decay_rate": 0.04,  "min_valence_to_rise": 0.35, "max_age_s": 7200},
    MemoryLayer.ASSOCIATIVE:  {"decay_rate": 0.008, "min_valence_to_rise": 0.25, "max_age_s": 604800},
    MemoryLayer.CONSOLIDATED: {"decay_rate": 0.001, "min_valence_to_rise": 0.60, "max_age_s": None},
    MemoryLayer.SELF:         {"decay_rate": 0.0001,"min_valence_to_rise": None, "max_age_s": None},
}

# Capas en orden de ascenso
_LAYER_ORDER = [
    MemoryLayer.EPHEMERAL,
    MemoryLayer.WORKING,
    MemoryLayer.ASSOCIATIVE,
    MemoryLayer.CONSOLIDATED,
    MemoryLayer.SELF,
]


@dataclass
class EmotionalStamp:
    """Huella emocional que acompaña cada fragmento de memoria."""
    valence: float    = 0.0   # −1 (muy negativo) … +1 (muy positivo)
    arousal: float    = 0.3   # 0 (calmo) … 1 (intenso)
    instinct_tags: List[str] = field(default_factory=list)  # instintos vinculados

    def intensity(self) -> float:
        """Intensidad emocional combinada (arousal amplificado por valencia absoluta)."""
        return self.arousal * (0.7 + 0.3 * abs(self.valence))

    def resonance_with(self, other: "EmotionalStamp") -> float:
        """Resonancia emocional entre dos huellas (0..1)."""
        val_sim = 1.0 - abs(self.valence - other.valence) / 2.0
        aro_sim = 1.0 - abs(self.arousal - other.arousal)
        tag_sim = (len(set(self.instinct_tags) & set(other.instinct_tags)) /
                   max(1, len(set(self.instinct_tags) | set(other.instinct_tags))))
        return val_sim * 0.4 + aro_sim * 0.35 + tag_sim * 0.25


@dataclass
class Fragment:
    """Unidad mínima de memoria: una pieza de experiencia.

    No es texto completo: puede ser un color, una sensación, una palabra,
    un gesto, una temperatura — cualquier huella sensorial o conceptual.
    """
    fid:          str
    content:      str
    tags:         List[str]
    modality:     str           # visual, auditivo, emocional, motor, conceptual…
    emotion:      EmotionalStamp
    strength:     float         # 0..1 fuerza actual
    layer:        MemoryLayer
    creation_ts:  float         = field(default_factory=time.time)
    last_access:  float         = field(default_factory=time.time)
    access_count: int           = 0
    identity_weight: float      = 0.0   # contribución al yo
    conscious:    bool          = True  # False → memoria inconsciente del yo
    temporal_overlaps: List[str] = field(default_factory=list)  # FIDs que lo evocan

    def age_s(self) -> float:
        return time.time() - self.creation_ts

    def recency_s(self) -> float:
        return time.time() - self.last_access

    def tag_overlap(self, other: "Fragment") -> float:
        st, ot = set(self.tags), set(other.tags)
        if not st and not ot:
            return 0.0
        return len(st & ot) / len(st | ot)

    def associative_strength(self, other: "Fragment") -> float:
        """Fuerza de asociación total: etiquetas + resonancia emocional."""
        if self.fid == other.fid:
            return 0.0
        tag_s = self.tag_overlap(other)
        emo_s = self.emotion.resonance_with(other.emotion)
        mod_bonus = 0.05 if self.modality != other.modality else 0.0
        return min(1.0, tag_s * 0.55 + emo_s * 0.40 + mod_bonus)


# ═══════════════════════════════════════════════════════════════════════════════
#  ALMACÉN DE FRAGMENTOS
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryStore:
    """Almacén distribuido de fragmentos de memoria, organizado por capa."""

    def __init__(self):
        self._lock    = RLock()
        self._layers: Dict[MemoryLayer, Dict[str, Fragment]] = {
            l: {} for l in MemoryLayer
        }
        self._tag_index:     Dict[str, List[str]] = defaultdict(list)  # tag → [fid]
        self._emotion_index: Dict[str, List[str]] = defaultdict(list)  # instinct → [fid]
        self._total_stored   = 0
        self._total_decayed  = 0
        self._total_ascended = 0

    # ── Inserción ─────────────────────────────────────────────────────────
    def add(self, fragment: Fragment):
        with self._lock:
            self._layers[fragment.layer][fragment.fid] = fragment
            for t in fragment.tags:
                if fragment.fid not in self._tag_index[t]:
                    self._tag_index[t].append(fragment.fid)
            for inst in fragment.emotion.instinct_tags:
                if fragment.fid not in self._emotion_index[inst]:
                    self._emotion_index[inst].append(fragment.fid)
            self._total_stored += 1

    # ── Acceso ────────────────────────────────────────────────────────────
    def get(self, fid: str) -> Optional[Fragment]:
        with self._lock:
            for layer_dict in self._layers.values():
                if fid in layer_dict:
                    f = layer_dict[fid]
                    f.last_access  = time.time()
                    f.access_count += 1
                    return f
        return None

    def all_fragments(self) -> List[Fragment]:
        with self._lock:
            return [f for d in self._layers.values() for f in d.values()]

    def layer_fragments(self, layer: MemoryLayer) -> List[Fragment]:
        with self._lock:
            return list(self._layers[layer].values())

    # ── Búsqueda ──────────────────────────────────────────────────────────
    def search_by_tags(self, tags: List[str], top_k: int = 10) -> List[Fragment]:
        with self._lock:
            scored: Dict[str, float] = defaultdict(float)
            for t in tags:
                for fid in self._tag_index.get(t, []):
                    scored[fid] += 1.0
            ranked = sorted(scored.items(), key=lambda x: x[1], reverse=True)
            results = []
            for fid, _ in ranked[:top_k * 2]:
                f = self.get(fid)
                if f:
                    results.append(f)
            return results[:top_k]

    def search_by_instinct(self, instinct: str, top_k: int = 8) -> List[Fragment]:
        with self._lock:
            fids = list(self._emotion_index.get(instinct, []))
            results = []
            for fid in fids[:top_k * 2]:
                f = self.get(fid)
                if f:
                    results.append(f)
            results.sort(key=lambda x: x.strength * x.emotion.intensity(), reverse=True)
            return results[:top_k]

    def search_by_valence(self, target_valence: float,
                           tolerance: float = 0.3, top_k: int = 8) -> List[Fragment]:
        """Busca fragmentos cuya valencia esté cerca de target_valence."""
        with self._lock:
            candidates = []
            for f in self.all_fragments():
                dist = abs(f.emotion.valence - target_valence)
                if dist <= tolerance:
                    candidates.append((dist, f))
            candidates.sort(key=lambda x: x[0])
            return [f for _, f in candidates[:top_k]]

    def neighbors(self, fragment: Fragment, top_k: int = 6) -> List[Fragment]:
        """Fragmentos más asociados (por etiquetas + emoción)."""
        with self._lock:
            scored: Dict[str, float] = {}
            for t in fragment.tags:
                for fid in self._tag_index.get(t, []):
                    if fid != fragment.fid:
                        f = self._layers[fragment.layer].get(fid) or \
                            self.get(fid)
                        if f:
                            scored[fid] = max(
                                scored.get(fid, 0.0),
                                fragment.associative_strength(f)
                            )
            ranked = sorted(scored.items(), key=lambda x: x[1], reverse=True)
            results = []
            for fid, _ in ranked[:top_k]:
                f = self.get(fid)
                if f:
                    results.append(f)
            return results

    # ── Movimiento entre capas ────────────────────────────────────────────
    def move_layer(self, fid: str, new_layer: MemoryLayer):
        with self._lock:
            for layer, d in self._layers.items():
                if fid in d:
                    f = d.pop(fid)
                    f.layer = new_layer
                    self._layers[new_layer][fid] = f
                    self._total_ascended += 1
                    return

    # ── Eliminación ───────────────────────────────────────────────────────
    def remove(self, fid: str):
        with self._lock:
            for d in self._layers.values():
                if fid in d:
                    f = d.pop(fid)
                    for t in f.tags:
                        try:
                            self._tag_index[t].remove(fid)
                        except ValueError:
                            pass
                    self._total_decayed += 1
                    return

    # ── Estadísticas ──────────────────────────────────────────────────────
    def stats(self) -> Dict[str, Any]:
        with self._lock:
            counts = {l.value: len(d) for l, d in self._layers.items()}
            total  = sum(counts.values())
            avg_s  = 0.0
            if total:
                avg_s = sum(f.strength for f in self.all_fragments()) / total
            return {
                "total":          total,
                "by_layer":       counts,
                "avg_strength":   round(avg_s, 4),
                "total_stored":   self._total_stored,
                "total_decayed":  self._total_decayed,
                "total_ascended": self._total_ascended,
                "tag_index_size": len(self._tag_index),
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  MOTOR DE RECONSTRUCCIÓN (basado en recuerdo.py, mejorado)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ReconstructionParams:
    """Parámetros del motor de reconstrucción dinámica."""
    base_seeds:      int   = 6
    max_cloud:       int   = 14
    steps:           int   = 50
    decay:           float = 0.055
    noise:           float = 0.018
    support_gain:    float = 0.24
    competition:     float = 0.17
    min_activation:  float = 0.07
    coherence_target: float = 0.58
    stability_need:  int   = 4
    post_decay:      float = 0.10
    # Amplificación emocional
    emotion_amplify: float = 0.35
    # Amplificación instintiva (supervivencia capta fragmentos más rápido)
    instinct_amplify: float = 0.25


@dataclass
class ActiveFragment:
    fragment: Fragment
    act:      float


class ReconstructionEngine:
    """Motor de reconstrucción de recuerdos.

    Fases:
    1. Destello emocional — semillas por tags + boost emocional + instinto
    2. Nube dinámica     — soporte, competencia, ruido, reclutamiento
    3. Consolidación     — si alcanza coherencia, fortalece los fragmentos
    4. Superposición temporal — fragmentos lejanos pueden ser evocados
                               si resuenan emocionalmente con los activos
    """

    def __init__(self, store: MemoryStore,
                 params: ReconstructionParams = None):
        self.store  = store
        self.p      = params or ReconstructionParams()

    # ── Utilidades ────────────────────────────────────────────────────────
    def _coherence(self, actives: List[ActiveFragment]) -> float:
        if len(actives) < 2:
            return 0.0
        total, pairs = 0.0, 0
        for i in range(len(actives)):
            for j in range(i + 1, len(actives)):
                a, b = actives[i], actives[j]
                w  = (a.act + b.act) / 2.0
                c  = a.fragment.associative_strength(b.fragment)
                total += w * c
                pairs += 1
        return max(0.0, min(1.0, total / max(1, pairs)))

    def _step(self, actives: List[ActiveFragment]) -> List[ActiveFragment]:
        p = self.p
        # Decaimiento
        for a in actives:
            a.act = max(0.0, a.act * (1.0 - p.decay))
        # Soporte mutuo
        for i in range(len(actives)):
            for j in range(i + 1, len(actives)):
                c = actives[i].fragment.associative_strength(actives[j].fragment)
                if c > 0:
                    d = p.support_gain * c
                    actives[i].act += d
                    actives[j].act += d
        # Competencia (inhibición lateral)
        if actives:
            mean = sum(a.act for a in actives) / len(actives)
            for a in actives:
                a.act = max(0.0, a.act - p.competition * (a.act - mean))
        # Ruido
        for a in actives:
            a.act = max(0.0, a.act + random.uniform(-p.noise, p.noise))
        # Filtrar débiles y recortar
        actives = [a for a in actives if a.act >= p.min_activation]
        actives.sort(key=lambda x: x.act, reverse=True)
        return actives

    # ── Reconstrucción principal ───────────────────────────────────────────
    def reconstruct(self, cue_tags: List[str],
                    emotion: EmotionalStamp,
                    instinct: str = "") -> Dict[str, Any]:
        """Reconstruye un recuerdo a partir de pistas y estado emocional."""
        p      = self.p
        log    = []

        # ── Fase 1: Destello emocional ─────────────────────────────────
        seeds = self.store.search_by_tags(cue_tags, top_k=p.base_seeds)
        # Añadir fragmentos por resonancia de valencia
        val_seeds = self.store.search_by_valence(
            emotion.valence, tolerance=0.4, top_k=3)
        for f in val_seeds:
            if f not in seeds:
                seeds.append(f)
        # Añadir fragmentos por instinto activo
        if instinct:
            inst_seeds = self.store.search_by_instinct(instinct, top_k=3)
            for f in inst_seeds:
                if f not in seeds:
                    seeds.append(f)

        actives: List[ActiveFragment] = []
        emo_boost = emotion.intensity() * p.emotion_amplify
        inst_boost = p.instinct_amplify if instinct else 0.0

        for f in seeds:
            tag_rel = (len(set(f.tags) & set(cue_tags)) /
                       max(1, len(set(f.tags) | set(cue_tags))))
            emo_res = emotion.resonance_with(f.emotion)
            inst_bonus = inst_boost if instinct in f.emotion.instinct_tags else 0.0
            a0 = min(1.0, tag_rel * 0.5 + emo_res * 0.3 +
                     f.strength * 0.2 + emo_boost + inst_bonus)
            actives.append(ActiveFragment(f, a0))

        log.append(f"F1: {len(actives)} semillas | emo_boost={emo_boost:.3f}")

        # ── Fase 2: Nube dinámica ───────────────────────────────────────
        best_coh, stable = 0.0, 0
        timeline = []

        for step in range(p.steps):
            actives = self._step(actives)

            # Reclutamiento por vecindad de los top activos
            for top in actives[:2]:
                for nb in self.store.neighbors(top.fragment, top_k=2):
                    if nb.fid not in {a.fragment.fid for a in actives}:
                        prob = min(1.0, 0.35 + 0.65 *
                                   top.fragment.associative_strength(nb))
                        if random.random() < prob:
                            actives.append(ActiveFragment(
                                nb, nb.strength * 0.5))

            # Superposición temporal: fragmentos lejanos con valencia similar
            if step % 8 == 0:
                for top in actives[:2]:
                    time_evoked = self.store.search_by_valence(
                        top.fragment.emotion.valence,
                        tolerance=0.25, top_k=2)
                    for f_old in time_evoked:
                        if (f_old.fid not in {a.fragment.fid for a in actives}
                                and f_old.age_s() > 60):  # sólo "pasado"
                            actives.append(ActiveFragment(
                                f_old, f_old.strength * 0.35))
                            if top.fragment.fid not in f_old.temporal_overlaps:
                                f_old.temporal_overlaps.append(top.fragment.fid)

            actives = actives[:p.max_cloud]

            coh = self._coherence(actives)
            best_coh = max(best_coh, coh)
            timeline.append((step, round(coh, 3),
                              [(a.fragment.fid, round(a.act, 3))
                               for a in actives[:4]]))

            if coh >= p.coherence_target:
                stable += 1
                if stable >= p.stability_need:
                    log.append(f"F2→F3: coherencia estable paso={step} coh={coh:.3f}")
                    break
            else:
                stable = 0
        else:
            log.append("F2: coherencia objetivo no alcanzada; recuerdo parcial")

        # ── Fase 3: Consolidación ────────────────────────────────────────
        final_coh = self._coherence(actives)
        reconstructed_frags = []
        for a in actives:
            a.act *= (1.0 - p.post_decay)
            # Fortalecer fragmentos que participaron con alta coherencia
            if final_coh >= p.coherence_target:
                a.fragment.strength = min(1.0, a.fragment.strength +
                                          final_coh * 0.05)
            reconstructed_frags.append(a)

        return {
            "cue_tags":       cue_tags,
            "emotion":        (round(emotion.valence, 3),
                               round(emotion.arousal, 3)),
            "coherence":      round(final_coh, 3),
            "target_reached": final_coh >= p.coherence_target,
            "fragments":      [(a.fragment.fid, round(a.act, 3),
                                a.fragment.tags, a.fragment.layer.value)
                               for a in reconstructed_frags],
            "timeline_tail":  timeline[-5:],
            "log":            log,
            "best_coherence": round(best_coh, 3),
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  GESTOR DE MEMORIA — CAPA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryManager:
    """Gestor central del sistema de memoria híbrida.

    Responsabilidades:
    ─ Codificación de nuevas experiencias con peso emocional
    ─ Decaimiento diferencial por capa
    ─ Ascenso entre capas por fuerza emocional + acceso + instinto
    ─ Formación del yo (Self): acumulación de identity_weight
    ─ Consolidación periódica
    ─ Reconstrucción de recuerdos vía ReconstructionEngine
    ─ Superposición temporal (recuerdos lejanos evocados por valencia)
    ─ Integración con AdaptiveCore (emociones + instintos)
    """

    def __init__(self, decay_interval_s: float = 30.0):
        self.store       = MemoryStore()
        self.engine      = ReconstructionEngine(self.store)
        self._lock       = RLock()
        self._decay_interval   = decay_interval_s
        self._last_decay       = time.time()
        self._last_consolidate = time.time()
        self._total_encoded    = 0
        self._total_recalled   = 0

        # Registro de fragmentos constitutivos del yo
        self._self_fids:        List[str] = []  # conscientes
        self._shadow_fids:      List[str] = []  # inconscientes (alto instinto, baja valencia)

    # ── Codificación ──────────────────────────────────────────────────────
    def encode(self, content: str,
               tags: List[str],
               modality: str        = "conceptual",
               valence: float       = 0.0,
               arousal: float       = 0.3,
               instinct_tags: List[str] = None,
               base_strength: float = 0.5,
               forced_layer: MemoryLayer = None) -> str:
        """Codifica una nueva experiencia en memoria.

        La capa inicial depende de la intensidad emocional:
        - arousal > 0.75 y |valence| > 0.5 → WORKING (no efímero, es fuerte)
        - arousal > 0.85 y valence < -0.3  → ASSOCIATIVE (trauma/amenaza)
        - otherwise → EPHEMERAL
        """
        emo   = EmotionalStamp(valence=valence, arousal=arousal,
                               instinct_tags=instinct_tags or [])
        intensity = emo.intensity()

        if forced_layer:
            layer = forced_layer
        elif intensity > 0.85 and valence < -0.3:
            layer = MemoryLayer.ASSOCIATIVE   # experiencia intensa negativa
        elif intensity > 0.65:
            layer = MemoryLayer.WORKING
        else:
            layer = MemoryLayer.EPHEMERAL

        fid = self._new_fid(content)
        f   = Fragment(
            fid          = fid,
            content      = content,
            tags         = tags,
            modality     = modality,
            emotion      = emo,
            strength     = min(1.0, base_strength + intensity * 0.25),
            layer        = layer,
        )
        self.store.add(f)
        self._total_encoded += 1
        return fid

    # ── Recordar ──────────────────────────────────────────────────────────
    def recall(self, cue_tags: List[str],
               valence: float  = 0.0,
               arousal: float  = 0.5,
               instinct: str   = "") -> Dict[str, Any]:
        """Reconstruye un recuerdo a partir de pistas y estado emocional."""
        emo    = EmotionalStamp(valence=valence, arousal=arousal)
        result = self.engine.reconstruct(cue_tags, emo, instinct)
        self._total_recalled += 1

        # Fragmentos recordados ganan peso de identidad si son coherentes
        if result["target_reached"]:
            for fid, act, _, _ in result["fragments"]:
                f = self.store.get(fid)
                if f:
                    f.identity_weight = min(1.0,
                        f.identity_weight + act * 0.02)
                    self._check_self_formation(f)

        return result

    # ── Decaimiento diferencial ───────────────────────────────────────────
    def decay_cycle(self, force: bool = False) -> Dict[str, int]:
        """Aplica decaimiento a todas las capas según sus tasas."""
        now = time.time()
        if not force and (now - self._last_decay) < self._decay_interval:
            return {}

        report = defaultdict(int)
        with self._lock:
            all_frags = self.store.all_fragments()

        for f in all_frags:
            cfg = _LAYER_CONFIG[f.layer]
            dt  = now - f.last_access

            # Decaimiento de fuerza
            rate = cfg["decay_rate"]
            # Emoción intensa retrasa el decaimiento
            rate *= (1.0 - f.emotion.intensity() * 0.4)
            # Fragmentos del yo apenas decaen
            if f.identity_weight > 0.5:
                rate *= 0.1

            f.strength = max(0.0, f.strength - rate * (dt / 60.0))

            # Eliminar efímeros muy débiles o muy viejos
            max_age = cfg.get("max_age_s")
            if (f.layer == MemoryLayer.EPHEMERAL and
                    (f.strength < 0.05 or (max_age and f.age_s() > max_age))):
                # Pequeña influencia residual en el yo antes de desaparecer
                self._ephemeral_residual(f)
                self.store.remove(f.fid)
                report["ephemeral_removed"] += 1
                continue

            # Ascenso de capa
            ascended = self._maybe_ascend(f, now)
            if ascended:
                report["ascended"] += 1

        self._last_decay = now
        return dict(report)

    # ── Ascenso de capa ───────────────────────────────────────────────────
    def _maybe_ascend(self, f: Fragment, now: float) -> bool:
        """Decide si un fragmento asciende a la siguiente capa."""
        cfg        = _LAYER_CONFIG[f.layer]
        min_val    = cfg.get("min_valence_to_rise", 0.99)
        if min_val is None:
            return False  # SELF nunca asciende (ya está arriba)

        idx = _LAYER_ORDER.index(f.layer)
        if idx >= len(_LAYER_ORDER) - 1:
            return False

        # Criterio de ascenso: fuerza + emoción + accesos
        score = (f.strength * 0.4 +
                 f.emotion.intensity() * 0.35 +
                 min(1.0, f.access_count / 5) * 0.25)

        threshold = min_val + (1.0 - f.emotion.intensity()) * 0.2

        if score >= threshold:
            next_layer = _LAYER_ORDER[idx + 1]
            self.store.move_layer(f.fid, next_layer)
            return True
        return False

    # ── Formación del yo ──────────────────────────────────────────────────
    def _check_self_formation(self, f: Fragment):
        """Evalúa si un fragmento debe pasar a formar parte del yo."""
        if f.identity_weight < 0.35:
            return
        if f.layer == MemoryLayer.SELF:
            return

        # Alta valencia + alta identidad → yo consciente
        if f.identity_weight > 0.6 and abs(f.emotion.valence) > 0.4:
            self.store.move_layer(f.fid, MemoryLayer.SELF)
            f.conscious = True
            if f.fid not in self._self_fids:
                self._self_fids.append(f.fid)
            return

        # Alta intensidad instintiva + baja valencia → yo inconsciente (sombra)
        if (f.identity_weight > 0.4 and
                len(f.emotion.instinct_tags) >= 2 and
                abs(f.emotion.valence) < 0.3):
            self.store.move_layer(f.fid, MemoryLayer.SELF)
            f.conscious = False
            if f.fid not in self._shadow_fids:
                self._shadow_fids.append(f.fid)

    def _ephemeral_residual(self, f: Fragment):
        """Una memoria efímera deja una huella mínima antes de desaparecer."""
        # Busca fragmentos del yo que resuenen con ella y los potencia un poco
        for fid in self._self_fids[:5]:
            self_f = self.store.get(fid)
            if self_f:
                res = f.emotion.resonance_with(self_f.emotion)
                if res > 0.4:
                    self_f.strength       = min(1.0, self_f.strength + res * 0.01)
                    self_f.identity_weight = min(1.0, self_f.identity_weight + 0.005)

    # ── Consolidación ─────────────────────────────────────────────────────
    def consolidate(self, force: bool = False) -> Dict[str, int]:
        """Mueve fragmentos WORKING estables a ASSOCIATIVE."""
        now = time.time()
        if not force and (now - self._last_consolidate) < 120.0:
            return {}

        report = defaultdict(int)
        for f in self.store.layer_fragments(MemoryLayer.WORKING):
            if (f.strength > 0.6 and
                    f.access_count >= 2 and
                    f.emotion.intensity() > 0.35):
                self.store.move_layer(f.fid, MemoryLayer.ASSOCIATIVE)
                report["consolidated"] += 1

        # Mover ASSOCIATIVE con alto identity_weight a CONSOLIDATED
        for f in self.store.layer_fragments(MemoryLayer.ASSOCIATIVE):
            if f.identity_weight > 0.3 and f.strength > 0.5:
                self.store.move_layer(f.fid, MemoryLayer.CONSOLIDATED)
                report["deep_consolidated"] += 1

        self._last_consolidate = now
        return dict(report)

    # ── Integración con AdaptiveCore ──────────────────────────────────────
    def sync_with_adaptive(self, emotion_engine, instinct_core) -> None:
        """Sincroniza el estado emocional actual con la memoria.

        Eleva la fuerza de fragmentos cuya valencia resuene con la emoción
        dominante. Fragmentos instintivos activos ganan un boost extra.
        """
        if not _HAS_ADAPTIVE:
            return

        dom_emo      = emotion_engine.dominant
        cur_valence  = emotion_engine.valence
        cur_arousal  = emotion_engine.arousal
        active_insts = [i.value for i in instinct_core.get_active()]

        for f in self.store.all_fragments():
            # Resonancia emocional con estado actual
            emo_now = EmotionalStamp(valence=cur_valence, arousal=cur_arousal)
            res = f.emotion.resonance_with(emo_now)
            if res > 0.5:
                f.strength = min(1.0, f.strength + res * 0.02)

            # Boost instintivo
            inst_overlap = set(f.emotion.instinct_tags) & set(active_insts)
            if inst_overlap:
                f.strength = min(1.0, f.strength +
                                 len(inst_overlap) * 0.03)

    # ── Yo / Identidad ────────────────────────────────────────────────────
    def get_self_profile(self) -> Dict[str, Any]:
        """Retorna el perfil de identidad construido por las memorias del yo."""
        conscious = [self.store.get(fid) for fid in self._self_fids
                     if self.store.get(fid)]
        shadow    = [self.store.get(fid) for fid in self._shadow_fids
                     if self.store.get(fid)]

        all_self = conscious + shadow
        if not all_self:
            return {"identity_fragments": 0,
                    "avg_valence": 0.0, "avg_arousal": 0.0,
                    "dominant_tags": [], "shadow_fragments": 0}

        avg_v = sum(f.emotion.valence for f in all_self) / len(all_self)
        avg_a = sum(f.emotion.arousal for f in all_self) / len(all_self)

        tag_counts: Dict[str, int] = defaultdict(int)
        for f in all_self:
            for t in f.tags:
                tag_counts[t] += 1
        top_tags = sorted(tag_counts, key=tag_counts.get, reverse=True)[:8]

        return {
            "identity_fragments":  len(conscious),
            "shadow_fragments":    len(shadow),
            "avg_valence":         round(avg_v, 3),
            "avg_arousal":         round(avg_a, 3),
            "dominant_tags":       top_tags,
            "strongest_memory": max(all_self, key=lambda x: x.strength).content
                                 if all_self else None,
            "most_accessed": max(all_self, key=lambda x: x.access_count).content
                              if all_self else None,
        }

    # ── Integración con red neuronal ─────────────────────────────────────
    def encode_from_neuron(self, neuron, signal: float,
                           context: Dict = None,
                           emotion_stamp: EmotionalStamp = None) -> Optional[str]:
        """Codifica una experiencia generada por activación neuronal.

        La fuerza de la señal modula el arousal del fragmento.
        El tipo de neurona define la modalidad.
        """
        if signal < 0.05:
            return None

        ntype   = getattr(neuron, "neuron_subtype",
                  getattr(neuron, "neuron_type", "conceptual"))
        nid     = getattr(neuron, "neuron_id", "unknown")

        # Modalidad según tipo de neurona
        modal_map = {
            "visual": "visual", "auditory": "auditivo",
            "tactile": "tactil", "olfactory": "olfativo",
            "nociceptor": "dolor", "motor": "motor",
            "cognitive": "conceptual", "micelial": "conceptual",
        }
        modality = "conceptual"
        for key, val in modal_map.items():
            if key in ntype:
                modality = val
                break

        emo = emotion_stamp or EmotionalStamp(
            valence = (signal - 0.5) * 2,   # señal alta → valencia positiva
            arousal = signal,
        )
        tags = [ntype[:12], nid[:8], f"signal_{signal:.2f}"]
        if context:
            tags += [str(v)[:10] for v in list(context.values())[:2]]

        return self.encode(
            content      = f"[{ntype}:{nid}] señal={signal:.3f}",
            tags         = tags,
            modality     = modality,
            valence      = emo.valence,
            arousal      = emo.arousal,
            instinct_tags= emo.instinct_tags,
            base_strength= signal,
        )

    # ── Estadísticas ──────────────────────────────────────────────────────
    def get_status(self) -> Dict[str, Any]:
        store_s = self.store.stats()
        self_p  = self.get_self_profile()
        return {
            "store":           store_s,
            "self_profile":    self_p,
            "total_encoded":   self._total_encoded,
            "total_recalled":  self._total_recalled,
        }

    # ── Utilidades ────────────────────────────────────────────────────────
    @staticmethod
    def _new_fid(content: str) -> str:
        h = hashlib.md5(f"{content}{time.time()}{random.random()}".encode()).hexdigest()
        return f"F{h[:10]}"


# ═══════════════════════════════════════════════════════════════════════════════
#  RED NEURONAL HÍBRIDA PARA MEMORIA
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from animal   import create_cognitive_animal_neuron,   CognitiveAnimalNeuronBase
    from micelial import create_cognitive_micelial_neuron, CognitiveMicelialNeuronBase
    from synapse  import SynapseManager
    _HAS_NEURAL = True
except ImportError:
    _HAS_NEURAL = False

_ANIMAL_TYPES_MEM = [
    ("visual_feature_extractor",  {"feature_type": "motion"}),
    ("attention_focuser",          {}),
    ("decision_maker",             {}),
    ("risk_assessor",              {}),
    ("anomaly_detector",           {}),
    ("nociceptor",                 {"pain_type": "mechanical"}),
    ("dopaminergic_modulator",     {}),
    ("place_cell",                 {"preferred_location": (0.5, 0.5)}),
    ("mirror_neuron",              {"action_class": "grasp"}),
    ("speed_neuron",               {}),
    ("cpg_neuron",                 {"intrinsic_frequency": 0.4}),
    ("adaptive_threshold_cell",    {}),
    ("self_monitor",               {}),
    ("barometric_neuron",          {}),
    ("receptive_field_cell",       {"polarity": "ON"}),
]

_MICELIAL_TYPES_MEM = [
    ("abstract_pattern_integrator",  {}),
    ("global_coherence_coordinator", {}),
    ("conceptual_bridge_builder",    {}),
    ("insight_propagator",           {}),
    ("knowledge_synthesizer",        {"domain_specializations": ["memory","emotion"]}),
    ("hyphal_integrator",            {}),
    ("calcium_wave_messenger",       {}),
    ("quorum_sensing_node",          {}),
    ("systemic_resistance_node",     {}),
    ("glycolytic_oscillator",        {}),
    ("plasmodium_collector",         {}),
    ("stomatal_guard_cell",          {}),
    ("conceptual_ph_sensor",         {}),
    ("deep_reflection_orchestrator", {}),
    ("anastomosis_node",             {}),
]

# Mapa neurona-subtipo → etiquetas de memoria e instintos
_NEURON_MEMORY_MAP = {
    "visual":         (["visual","percepcion","forma"],   0.3,  0.6, ["explore"]),
    "attention":      (["atencion","foco","saliencia"],   0.4,  0.5, ["explore"]),
    "decision":       (["decision","accion","opcion"],    0.2,  0.5, ["survive"]),
    "risk":           (["riesgo","peligro","amenaza"],   -0.5,  0.8, ["survive","defend"]),
    "anomaly":        (["anomalia","cambio","alerta"],   -0.3,  0.7, ["survive"]),
    "nociceptor":     (["dolor","dano","urgencia"],      -0.9,  0.95,["survive","flee"]),
    "dopaminergic":   (["recompensa","placer","logro"],   0.8,  0.7, ["explore","reproduce"]),
    "place":          (["lugar","espacio","mapa"],        0.5,  0.4, ["explore"]),
    "mirror":         (["empatia","imitacion","social"],  0.6,  0.5, ["bond"]),
    "speed":          (["velocidad","movimiento","flujo"],0.2,  0.55,["explore"]),
    "cpg":            (["ritmo","ciclo","oscilacion"],    0.1,  0.4, ["rest"]),
    "adaptive":       (["adaptacion","umbral","ajuste"],  0.3,  0.45,["survive"]),
    "self_monitor":   (["automonitoreo","rendimiento"],   0.2,  0.35,["survive"]),
    "barometric":     (["presion","clima","ambiente"],    0.0,  0.3, ["rest"]),
    "receptive":      (["contraste","deteccion","borde"], 0.3,  0.5, ["explore"]),
    # miceliales
    "abstract":       (["patron","abstraccion","concepto"],0.5, 0.5, ["explore"]),
    "coherence":      (["coherencia","logica","orden"],   0.4,  0.4, ["survive"]),
    "bridge":         (["conexion","dominio","puente"],   0.6,  0.45,["explore","bond"]),
    "insight":        (["insight","descubrimiento"],      0.75, 0.65,["explore","reproduce"]),
    "knowledge":      (["conocimiento","sintesis"],       0.6,  0.5, ["explore"]),
    "hyphal":         (["crecimiento","gradiente"],       0.4,  0.4, ["feed","explore"]),
    "calcium":        (["alarma","onda","dano"],         -0.4,  0.8, ["survive","defend"]),
    "quorum":         (["colectivo","umbral","grupo"],    0.5,  0.55,["bond"]),
    "systemic":       (["resistencia","sistema","defensa"],-0.2,0.6, ["defend","survive"]),
    "glycolytic":     (["ritmo","metabolismo","energia"], 0.2,  0.45,["feed","rest"]),
    "plasmodium":     (["red","optimizacion","flujo"],    0.4,  0.5, ["explore","feed"]),
    "stomatal":       (["apertura","control","barrera"],  0.1,  0.4, ["defend"]),
    "conceptual_ph":  (["tono","balance","valencia"],     0.0,  0.3, ["survive"]),
    "deep_reflection":([" reflexion","profundidad","meta"],0.5, 0.4, ["explore"]),
    "anastomosis":    (["fusion","integracion","union"],  0.5,  0.5, ["bond","explore"]),
}


def _neuron_memory_profile(neuron) -> Tuple[List[str], float, float, List[str]]:
    """Retorna (tags, valence, arousal, instinct_tags) para una neurona."""
    ntype = getattr(neuron, "neuron_subtype",
            getattr(neuron, "neuron_type", "generic"))
    for key, profile in _NEURON_MEMORY_MAP.items():
        if key in ntype:
            tags, val, aro, inst = profile
            return tags, val, aro, inst
    return (["neurona","señal"], 0.0, 0.3, [])


class NeuralMemoryBridge:
    """Puente entre la red neuronal híbrida y el gestor de memoria.

    Construye la red (animales + miceliales + sinapsis), la activa
    con señales y convierte cada activación neuronal en un fragmento
    de memoria con su correspondiente huella emocional.
    """

    def __init__(self, n_animal: int = 5, n_micelial: int = 5):
        if not _HAS_NEURAL:
            raise RuntimeError("Módulos neurales no disponibles")

        self.animals:   List = []
        self.micelials: List = []
        self.synapse_mgr = SynapseManager(
            prune_interval_s  = 20.0,
            utility_threshold = 0.08,
            error_rate_max    = 0.75,
            inactivity_secs   = 60.0,
        )
        self._build(n_animal, n_micelial)
        self._wire()

    def _build(self, na: int, nm: int):
        for i in range(na):
            ntype, kwargs = _ANIMAL_TYPES_MEM[i % len(_ANIMAL_TYPES_MEM)]
            nid = f"MA{i+1:03d}_{ntype[:8]}"
            try:
                n = create_cognitive_animal_neuron(ntype, nid, **kwargs)
                self.animals.append(n)
            except Exception as e:
                pass

        for i in range(nm):
            ntype, kwargs = _MICELIAL_TYPES_MEM[i % len(_MICELIAL_TYPES_MEM)]
            nid = f"MM{i+1:03d}_{ntype[:8]}"
            try:
                n = create_cognitive_micelial_neuron(ntype, nid, **kwargs)
                self.micelials.append(n)
            except Exception as e:
                pass

    def _wire(self):
        mgr = self.synapse_mgr
        for i in range(len(self.animals) - 1):
            mgr.connect(self.animals[i], self.animals[i+1],
                        "electrical", "excitatory", persistent=True)
        for i in range(len(self.micelials) - 1):
            mgr.connect(self.micelials[i], self.micelials[i+1],
                        "chemical", "excitatory", persistent=True)
        n_cross = min(4, len(self.animals), len(self.micelials))
        for i in range(n_cross):
            mgr.connect(self.animals[i], self.micelials[i],
                        "hybrid", "excitatory", persistent=True)
            mgr.connect(self.micelials[i], self.animals[i],
                        "hybrid", "modulatory", persistent=False)
        if len(self.animals) >= 3 and self.micelials:
            mgr.create_parallel_bundle(
                self.animals[:3], self.micelials[0], "hybrid")
        if len(self.animals) >= 2 and self.micelials:
            mgr.create_serial_chain(
                [self.animals[0], self.animals[1], self.micelials[0]])

    def activate_and_memorize(self, memory_mgr: "MemoryManager",
                               n_rounds: int = 3,
                               base_signal: float = 0.65) -> Dict[str, int]:
        """Activa la red y convierte cada disparo en fragmento de memoria."""
        report = defaultdict(int)
        syns   = list(self.synapse_mgr.synapses.values())

        for rnd in range(n_rounds):
            sig = base_signal + random.uniform(-0.15, 0.15)
            sig = max(0.1, min(1.0, sig))

            # Activar neuronas directamente
            for n in self.animals:
                try:
                    act = n.receive_signal(sig, "memory_encoding", {})
                    if act and act > 0.05:
                        tags, val, aro, inst = _neuron_memory_profile(n)
                        # modular con la señal real
                        aro_mod = min(1.0, aro + act * 0.2)
                        fid = memory_mgr.encode(
                            content      = f"[A:{n.neuron_id}] act={act:.3f}",
                            tags         = tags,
                            modality     = "animal",
                            valence      = val,
                            arousal      = aro_mod,
                            instinct_tags= inst,
                            base_strength= act,
                        )
                        if fid:
                            report["animal_fragments"] += 1
                except Exception:
                    pass

            for n in self.micelials:
                try:
                    concept = f"concepto_{rnd}"
                    act = n.receive_concept(sig, concept, {})
                    if act and act > 0.05:
                        tags, val, aro, inst = _neuron_memory_profile(n)
                        aro_mod = min(1.0, aro + act * 0.15)
                        fid = memory_mgr.encode(
                            content      = f"[M:{n.neuron_id}] act={act:.3f}",
                            tags         = tags,
                            modality     = "conceptual",
                            valence      = val,
                            arousal      = aro_mod,
                            instinct_tags= inst,
                            base_strength= act,
                        )
                        if fid:
                            report["micelial_fragments"] += 1
                except Exception:
                    pass

            # Propagar por sinapsis
            ctx = {"pattern": "memory_pass", "neuromodulator": "dopamine",
                   "nm_level": 0.5}
            for syn in syns:
                try:
                    out = syn.transmit(sig, ctx)
                    if out and out > 0.05:
                        report["synaptic_tx"] += 1
                except Exception:
                    pass

        return dict(report)

    def get_neuron_states(self) -> List[Dict]:
        """Retorna estado resumido de todas las neuronas."""
        rows = []
        for n in self.animals:
            rows.append({
                "id":      n.neuron_id,
                "domain":  "animal",
                "subtype": getattr(n, "neuron_subtype", "?")[:20],
                "act":     round(getattr(n, "activation_level", 0.0), 4),
                "resil":   round(getattr(n, "cognitive_resilience", 1.0), 3),
                "plastic": round(getattr(n, "plasticity_score", 0.5), 3),
                "age_s":   round(getattr(n, "age", 0.0), 2),
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
                "age_s":   round(getattr(n, "age", 0.0), 2),
            })
        return rows

    def get_synapse_states(self) -> List[Dict]:
        return self.synapse_mgr.list_synapses()

    def prune(self) -> Dict:
        return self.synapse_mgr.prune(force=True)

    def get_status(self) -> Dict:
        return {
            "animals":   len(self.animals),
            "micelials": len(self.micelials),
            "synapses":  self.synapse_mgr.get_stats(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  BANCO DE EXPERIENCIAS DE PRUEBA
# ═══════════════════════════════════════════════════════════════════════════════

_EXPERIENCES = [
    # (content, tags, modality, valence, arousal, instinct_tags)
    ("La primera vez que vi el mar de niño",
     ["mar","agua","niñez","asombro","horizonte"], "visual",   0.90, 0.85,
     ["explore","bond"]),
    ("El olor a lluvia sobre tierra seca",
     ["lluvia","olor","tierra","calma","tarde"],   "olfativo",  0.70, 0.55,
     ["rest"]),
    ("Una amenaza repentina en la oscuridad",
     ["oscuridad","miedo","peligro","cuerpo","alerta"], "emocional", -0.85, 0.95,
     ["survive","flee","defend"]),
    ("El sabor del café de la abuela",
     ["café","cocina","abuela","hogar","amor"],    "gustativo",  0.85, 0.50,
     ["bond","feed"]),
    ("Aprender a montar en bicicleta",
     ["bicicleta","equilibrio","caída","logro","cuerpo"], "motor",  0.65, 0.75,
     ["explore","reproduce"]),
    ("Una canción que sonaba cuando era feliz",
     ["música","melodía","felicidad","verano","amigos"], "auditivo", 0.80, 0.70,
     ["bond","explore"]),
    ("Un dolor físico intenso",
     ["dolor","cuerpo","urgencia","calor","miedo"], "emocional", -0.75, 0.90,
     ["survive","defend"]),
    ("La sensación de resolver un problema difícil",
     ["logro","mente","solución","claridad","satisfacción"], "conceptual", 0.75, 0.65,
     ["explore","reproduce"]),
    ("Ver una puesta de sol desde una montaña",
     ["luz","color","silencio","belleza","tarde"], "visual",    0.90, 0.60,
     ["rest","explore"]),
    ("Una discusión que dejó huella",
     ["conflicto","voz","tensión","palabras","herida"], "auditivo", -0.60, 0.80,
     ["defend","bond"]),
    ("La textura de la arena entre los dedos",
     ["arena","tacto","calor","playa","niñez"],    "tactil",    0.70, 0.45,
     ["rest","explore"]),
    ("El momento de perder algo importante",
     ["pérdida","vacío","tristeza","pasado","silencio"], "emocional", -0.80, 0.70,
     ["survive","bond"]),
    ("Descubrir algo nuevo e inesperado",
     ["novedad","sorpresa","mente","curiosidad","energía"], "conceptual", 0.65, 0.80,
     ["explore","reproduce"]),
    ("El frío del invierno en la piel",
     ["frío","piel","invierno","mañana","despertar"], "tactil",   0.10, 0.50,
     ["survive","feed"]),
    ("Una conversación que cambió mi perspectiva",
     ["palabras","comprensión","cambio","voz","relación"], "auditivo", 0.70, 0.65,
     ["bond","explore","reproduce"]),
    ("El miedo antes de hablar en público",
     ["miedo","cuerpo","público","voz","nervios"], "emocional", -0.50, 0.85,
     ["survive","defend","bond"]),
    ("La paz de una mañana tranquila",
     ["silencio","calma","luz","mañana","descanso"], "visual",   0.75, 0.20,
     ["rest","homeostasis"]),
    ("Recordar el rostro de alguien querido",
     ["rostro","amor","memoria","presencia","calor"], "visual",   0.85, 0.55,
     ["bond","reproduce"]),
    # Memorias efímeras (baja arousal, baja valencia)
    ("Número de teléfono leído una vez",
     ["número","texto","dato","neutro"],           "conceptual",  0.00, 0.10, []),
    ("El color de un coche aparcado esta mañana",
     ["color","coche","calle","neutro"],           "visual",      0.05, 0.08, []),
    ("Lista de compras del martes pasado",
     ["lista","compras","comida","neutro"],        "conceptual",  0.02, 0.07, []),
]


def _build_demo_memory(mgr: MemoryManager):
    """Carga las experiencias de prueba en el gestor."""
    for (content, tags, mod, val, aro, inst) in _EXPERIENCES:
        # Variar un poco la fuerza base para realismo
        base = random.uniform(0.4, 0.8)
        mgr.encode(content, tags, mod, val, aro, inst, base)


# ═══════════════════════════════════════════════════════════════════════════════
#  DIAGNÓSTICO INTERACTIVO
# ═══════════════════════════════════════════════════════════════════════════════

_SEP  = "─" * 64
_SEP2 = "═" * 64


def _bar(v: float, w: int = 16) -> str:
    v = max(0.0, min(1.0, v))
    n = int(round(v * w))
    return "█" * n + "░" * (w - n)


def _ask_int(prompt: str, lo: int, hi: int, default: int) -> int:
    while True:
        try:
            raw = input(f"  {prompt} [{lo}–{hi}, default={default}]: ").strip()
            return int(raw) if raw else default
        except (ValueError, KeyboardInterrupt):
            return default


def _valence_label(v: float) -> str:
    if v >  0.6:  return "✦ muy positivo"
    if v >  0.2:  return "↑ positivo"
    if v > -0.2:  return "· neutro"
    if v > -0.6:  return "↓ negativo"
    return "✗ muy negativo"


def _print_neuron_table(rows: List[Dict], title: str):
    """Imprime tabla compacta de estado neuronal."""
    print(f"\n  ── {title} {'─'*(52-len(title))}")
    hdr = (f"  {'ID':<18} {'Subtipo':<22} {'Act':>6} "
           f"{'Res':>6} {'Plas':>6} {'Edad':>7}")
    print(hdr)
    print("  " + "─" * 62)
    for r in rows:
        act_bar = _bar(r["act"], 6)
        print(f"  {r['id']:<18} {r['subtype']:<22} "
              f"{r['act']:>6.4f} {r['resil']:>6.3f} "
              f"{r['plastic']:>6.3f} {r['age_s']:>6.2f}s")
    print(f"  Total: {len(rows)} neuronas")


def _print_synapse_table(syns: List[Dict]):
    """Imprime tabla compacta de sinapsis."""
    print(f"\n  ── SINAPSIS {'─' * 50}")
    hdr = (f"  {'ID':<14} {'Tipo':<12} {'Pol':<11} "
           f"{'Peso':>6} {'OK':>4} {'ERR':>4} {'Err%':>5} {'Pers':>5}")
    print(hdr)
    print("  " + "─" * 62)
    for s in syns[:35]:
        total  = s["success"] + s["failure"]
        err_p  = f"{s['error_rate']*100:.0f}%" if total > 0 else "─"
        pers   = "✓" if s["persistent"] else "─"
        actv   = "✓" if s["active"] else "✗"
        print(f"  {s['id']:<14} {s['kind']:<12} {s['polarity']:<11} "
              f"{s['weight']:>6.3f} {s['success']:>4} {s['failure']:>4} "
              f"{err_p:>5} {pers:>5}")
    if len(syns) > 35:
        print(f"  … y {len(syns)-35} sinapsis más (omitidas)")
    print(f"  Total: {len(syns)} sinapsis")


def run_diagnostic():
    print()
    print(_SEP2)
    print("  DIAGNÓSTICO — SISTEMA DE MEMORIA HÍBRIDA")
    print("  Emocional · Instintiva · Neuronal · Formadora del Yo")
    print(_SEP2)

    # ── Configuración ─────────────────────────────────────────────────────
    print("\n  Configura la red y la prueba:\n")
    n_animal   = _ask_int("Neuronas animales",              1, 15, 5)
    n_micelial = _ask_int("Neuronas miceliales",            1, 15, 5)
    n_cycles   = _ask_int("Ciclos de experiencia",          1, 60, 20)
    n_recalls  = _ask_int("Reconstrucciones de recuerdo",   1, 20,  6)
    n_rounds   = _ask_int("Rondas de activación neuronal",  1, 10,  3)

    print(f"\n  → {n_animal}A · {n_micelial}M · {n_cycles} ciclos · "
          f"{n_recalls} recalls · {n_rounds} rondas neuronales\n")

    # ── [1] Memoria + experiencias base ───────────────────────────────────
    print(_SEP)
    print("  [1/8] Inicializando gestor de memoria + experiencias base…")
    t0  = time.time()
    mgr = MemoryManager(decay_interval_s=5.0)
    _build_demo_memory(mgr)
    print(f"       ✓ {mgr._total_encoded} fragmentos base  "
          f"({(time.time()-t0)*1000:.1f} ms)")

    # ── [2] Red neuronal ──────────────────────────────────────────────────
    bridge = None
    if _HAS_NEURAL:
        print(_SEP)
        print("  [2/8] Construyendo red neuronal híbrida…")
        t0 = time.time()
        try:
            bridge = NeuralMemoryBridge(n_animal, n_micelial)
            ns     = bridge.get_status()
            print(f"       ✓ {ns['animals']}A + {ns['micelials']}M  "
                  f"→ {ns['synapses']['total_synapses']} sinapsis  "
                  f"({(time.time()-t0)*1000:.1f} ms)")
        except Exception as e:
            print(f"       ✗ Red neuronal no disponible: {e}")
            bridge = None
    else:
        print(_SEP)
        print("  [2/8] ⚠ Módulos neurales no disponibles (sin animal/micelial/synapse)")

    # ── [3] Activación neuronal → fragmentos de memoria ──────────────────
    if bridge:
        print(_SEP)
        print(f"  [3/8] Activando red neuronal ({n_rounds} rondas)…")
        t0 = time.time()
        neural_report = bridge.activate_and_memorize(mgr, n_rounds)
        print(f"       ✓ Fragmentos animales  : {neural_report.get('animal_fragments', 0)}")
        print(f"         Fragmentos miceliales: {neural_report.get('micelial_fragments', 0)}")
        print(f"         Transmisiones sinápticas: {neural_report.get('synaptic_tx', 0)}")
        print(f"         Total memoria post-neural: {mgr._total_encoded}  "
              f"({(time.time()-t0)*1000:.1f} ms)")
    else:
        print(_SEP)
        print("  [3/8] (sin red neuronal — omitido)")

    # ── [4] Ciclos de experiencia ─────────────────────────────────────────
    print(_SEP)
    print(f"  [4/8] Simulando {n_cycles} ciclos de experiencia…")
    for i in range(n_cycles):
        if random.random() < 0.7:
            exp = random.choice(_EXPERIENCES)
            content, tags, mod, val, aro, inst = exp
            if random.random() < 0.15:    # rejuvenecimiento emocional
                val = min(1.0, val + 0.15)
                aro = min(1.0, aro + 0.10)
            mgr.encode(content + f" [c{i}]", tags, mod, val, aro, inst,
                       base_strength=random.uniform(0.3, 0.75))
        if i % 5  == 0: mgr.decay_cycle(force=True)
        if i % 10 == 0: mgr.consolidate(force=True)
    print(f"       ✓ {mgr._total_encoded} fragmentos totales en memoria")

    # ── [5] Reconstrucciones ──────────────────────────────────────────────
    print(_SEP)
    print(f"  [5/8] Ejecutando {n_recalls} reconstrucciones de recuerdo…\n")

    cue_sets = [
        (["mar","niñez","asombro"],          0.85, 0.80, "explore"),
        (["miedo","peligro","cuerpo"],       -0.80, 0.92, "survive"),
        (["café","hogar","amor"],             0.82, 0.55, "bond"),
        (["lluvia","calma","tarde"],          0.65, 0.45, "rest"),
        (["logro","claridad","mente"],        0.70, 0.65, "explore"),
        (["pérdida","tristeza","silencio"],  -0.75, 0.65, "survive"),
        (["curiosidad","novedad","energía"],  0.60, 0.80, "explore"),
        (["silencio","calma","mañana"],       0.72, 0.20, "rest"),
        # Cues de recuerdos neurales
        (["riesgo","peligro","amenaza"],     -0.50, 0.80, "survive"),
        (["recompensa","placer","logro"],     0.80, 0.70, "explore"),
        (["empatia","imitacion","social"],    0.60, 0.50, "bond"),
        (["patron","abstraccion","concepto"], 0.50, 0.50, "explore"),
    ]

    for idx in range(n_recalls):
        cues, val, aro, inst = cue_sets[idx % len(cue_sets)]
        res = mgr.recall(cues, val, aro, inst)

        print(f"  ── Recall #{idx+1:02d}  cues={cues}  instinto={inst}")
        print(f"     coherencia={res['coherence']:.3f}  "
              f"{'✓' if res['target_reached'] else '✗'}  "
              f"emoción={_valence_label(val)}  "
              f"frags_activos={len(res['fragments'])}")
        if res["fragments"]:
            top   = res["fragments"][0]
            f_obj = mgr.store.get(top[0])
            preview = (f_obj.content[:52] + "…") if f_obj else "?"
            print(f"     top: [{top[3]:<12}] act={top[1]:.3f}  '{preview}'")
        temporal = [f for f in res["fragments"]
                    if mgr.store.get(f[0]) and
                    mgr.store.get(f[0]).temporal_overlaps]
        if temporal:
            print(f"     ↺ superposición temporal: {len(temporal)} frags lejanos")
        print()

    # ── [6] Formación del yo ──────────────────────────────────────────────
    print(_SEP)
    print("  [6/8] Analizando formación del yo…")
    self_p = mgr.get_self_profile()
    print(f"       Fragmentos conscientes   : {self_p['identity_fragments']}")
    print(f"       Fragmentos sombra        : {self_p['shadow_fragments']}")
    print(f"       Valencia promedio del yo : {self_p['avg_valence']:+.3f}  "
          f"{_valence_label(self_p['avg_valence'])}")
    print(f"       Arousal promedio         : {self_p['avg_arousal']:.3f}")
    if self_p["dominant_tags"]:
        print(f"       Temas dominantes del yo : {self_p['dominant_tags'][:6]}")
    if self_p.get("strongest_memory"):
        preview = self_p["strongest_memory"][:58]
        print(f"       Recuerdo más fuerte     : '{preview}…'")
    if self_p.get("most_accessed"):
        preview = self_p["most_accessed"][:58]
        print(f"       Más accedido            : '{preview}…'")

    # ── [7] Decaimiento + poda sináptica ──────────────────────────────────
    print(_SEP)
    print("  [7/8] Decaimiento, consolidación y poda sináptica…")
    dec   = mgr.decay_cycle(force=True)
    con   = mgr.consolidate(force=True)
    prune = bridge.prune() if bridge else {}
    print(f"       Decaimiento      : {dec}")
    print(f"       Consolidación    : {con}")
    if prune:
        print(f"       Poda sináptica   : evaluadas={prune.get('evaluated',0)}  "
              f"podadas={prune.get('pruned',0)}  "
              f"persistentes={prune.get('persistent_kept',0)}")

    # ── [8] Estado completo ───────────────────────────────────────────────
    print(_SEP)
    print("  [8/8] Estado completo del sistema\n")

    # Memoria
    status  = mgr.get_status()
    store_s = status["store"]
    print("  ── MEMORIA POR CAPA ─────────────────────────────────────")
    total_f = max(1, store_s["total"])
    for layer, count in store_s["by_layer"].items():
        pct = count / total_f * 100
        bar = _bar(count / total_f)
        print(f"    {layer:<15} {bar} {count:>4} ({pct:>5.1f}%)")

    print(f"\n  Fragmentos totales    : {store_s['total']}")
    print(f"  Fuerza promedio       : {store_s['avg_strength']:.4f}  "
          f"{_bar(store_s['avg_strength'], 12)}")
    print(f"  Codificados (sesión)  : {store_s['total_stored']}")
    print(f"  Decaídos/borrados     : {store_s['total_decayed']}")
    print(f"  Ascensos de capa      : {store_s['total_ascended']}")
    print(f"  Tags indexados        : {store_s['tag_index_size']}")
    print(f"  Recalls ejecutados    : {mgr._total_recalled}")

    # Neuronas
    if bridge:
        neuron_rows = bridge.get_neuron_states()
        animal_rows   = [r for r in neuron_rows if r["domain"] == "animal"]
        micelial_rows = [r for r in neuron_rows if r["domain"] == "micelial"]

        _print_neuron_table(animal_rows,   "NEURONAS ANIMALES")
        _print_neuron_table(micelial_rows, "NEURONAS MICELIALES")

        # Sinapsis
        syn_rows = bridge.get_synapse_states()
        _print_synapse_table(syn_rows)

        # Estadísticas de sinapsis
        syn_stats = bridge.get_status()["synapses"]
        print(f"\n  Estadísticas sinápticas:")
        print(f"    Total={syn_stats['total_synapses']}  "
              f"Activas={syn_stats['active_synapses']}  "
              f"Inactivas={syn_stats['inactive_synapses']}")
        print(f"    Por tipo    : {syn_stats['by_kind']}")
        print(f"    Por polaridad: {syn_stats['by_polarity']}")
        print(f"    Peso avg={syn_stats['avg_weight']}  "
              f"min={syn_stats['min_weight']}  max={syn_stats['max_weight']}")
        print(f"    Utilidad promedio : {syn_stats['avg_utility']}")
        print(f"    Bundles paralelos : {syn_stats['bundles']}  "
              f"Cadenas seriales: {syn_stats['chains']}")
        print(f"    Total podadas     : {syn_stats['total_pruned_ever']}")

    # Resumen ejecutivo
    print()
    print(_SEP2)
    print("  RESUMEN EJECUTIVO")
    print(_SEP2)

    self_f = store_s["by_layer"].get("self", 0)
    ep_f   = store_s["by_layer"].get("ephemeral", 0)
    co_f   = store_s["by_layer"].get("consolidated", 0)

    health = "CRÍTICO"  if store_s["avg_strength"] < 0.3 else \
             "ADVERTENCIA" if store_s["avg_strength"] < 0.55 else \
             "ESTABLE"   if store_s["avg_strength"] < 0.75 else "ÓPTIMO"

    print(f"  Estado del sistema    : {health}")
    print(f"  Fragmentos totales    : {store_s['total']}")
    print(f"    ├─ Efímeros         : {ep_f}")
    print(f"    ├─ Consolidados     : {co_f}")
    print(f"    └─ Formadores del yo: {self_f}  "
          f"(conscientes={self_p['identity_fragments']}  "
          f"sombra={self_p['shadow_fragments']})")
    print(f"  Fuerza promedio       : {store_s['avg_strength']:.4f}")
    print(f"  Ascensos de capa      : {store_s['total_ascended']}")
    print(f"  Recalls ejecutados    : {mgr._total_recalled}")
    if self_p["dominant_tags"]:
        print(f"  Temas del yo          : {self_p['dominant_tags'][:5]}")
    if bridge:
        ns = bridge.get_status()
        print(f"  Red neuronal          : {ns['animals']}A + {ns['micelials']}M  "
              f"→ {ns['synapses']['total_synapses']} sinapsis  "
              f"(util={ns['synapses']['avg_utility']})")
        print(f"  Fragmentos neurales   : "
              f"{neural_report.get('animal_fragments',0)}A + "
              f"{neural_report.get('micelial_fragments',0)}M")
    print()
    print("  ✓ Sistema completo listo para operación híbrida")
    print(_SEP2)
    print()

    return mgr, bridge


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    random.seed(42)
    try:
        mgr, bridge = run_diagnostic()
    except KeyboardInterrupt:
        print("\n  Diagnóstico interrumpido.")
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        traceback.print_exc()
