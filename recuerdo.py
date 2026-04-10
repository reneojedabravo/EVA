#recuerdos.py
"""
Modelo simplificado de reconstrucción de recuerdo
"""
from __future__ import annotations
import random
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Iterable

# ===================== PARÁMETROS GLOBALES =====================

@dataclass
class DefaultParams:
    # Fase 1: ancla emocional (el "destello")
    base_recruit: int = 5          # cuántos fragmentos iniciales reclutar
    emotional_boost: float = 0.35  # cuánto amplifica la emoción la activación

    # Fase 2: nube de fragmentos (ensayos y descartes)
    steps: int = 40                # iteraciones máximo por recuerdo
    recruit_per_step: int = 4      # intento de nuevos fragmentos por paso
    decay: float = 0.06            # fuga (lo que no encaja, cae)
    noise: float = 0.02            # ruido estocástico (variabilidad)
    support_gain: float = 0.22     # apoyo mutuo por compatibilidad
    competition: float = 0.18      # inhibición lateral (frag. compiten por recursos)
    min_activation: float = 0.08   # bajo esto, se descarta el fragmento

    # Fase 3: criterio de coherencia (cuando lo sientes "recordado")
    coherence_target: float = 0.62 # coherencia requerida para consolidar
    stability_need: int = 4        # nº de pasos consecutivos por encima del target

    # Desvanecimiento final (huella)
    post_consolidation_decay: float = 0.12


# ===================== ESTRUCTURAS BÁSICAS =====================

@dataclass
class EmotionalState:
    valence: float  # [-1, 1]
    arousal: float  # [0, 1]

    def boost(self) -> float:
        # El arousal empuja, la valencia modula levemente
        return max(0.0, self.arousal * (0.8 + 0.2 * max(0.0, self.valence)))


@dataclass
class Cue:
    """Pista que dispara el recuerdo: palabra, olor, gesto, etc."""
    tags: List[str]
    intensity: float = 1.0  # [0..1]


@dataclass
class Fragment:
    """Unidad mínima recordable (no es una imagen ni video; es un pedazo: color,
    palabra, gesto, emoción, forma, textura, temperatura, etc.)."""
    fid: str
    modality: str                   # p.ej., 'visual', 'auditivo', 'emocional', 'motor'
    tags: List[str]
    baseline_strength: float = 0.5  # qué tan fuerte es en memoria de base [0..1]

    def compatibility(self, other: "Fragment") -> float:
        """Qué tanto encajan (por solapamiento de tags y modalidad)."""
        if self.fid == other.fid:
            return 0.0
        tag_overlap = len(set(self.tags) & set(other.tags))
        mod_bonus = 0.1 if self.modality != other.modality else 0.0
        return min(1.0, 0.2 * tag_overlap + mod_bonus)

    def relevance_to(self, cue: Cue) -> float:
        overlap = len(set(self.tags) & set(cue.tags))
        return min(1.0, 0.25 * overlap + 0.5 * self.baseline_strength)


@dataclass
class MemoryStore:
    """Repositorio de fragmentos dispersos (tu "memoria distribuida")."""
    fragments: Dict[str, Fragment] = field(default_factory=dict)
    associations: Dict[str, List[Tuple[str, float]]] = field(default_factory=dict)
    # associations: tag -> lista de (fragment_id, peso)

    def add_fragment(self, fragment: Fragment):
        self.fragments[fragment.fid] = fragment
        for t in fragment.tags:
            self.associations.setdefault(t, []).append((fragment.fid, fragment.baseline_strength))

    def candidates_from_cue(self, cue: Cue, k: int) -> List[Fragment]:
        scored: Dict[str, float] = {}
        for t in cue.tags:
            for fid, w in self.associations.get(t, []):
                scored[fid] = max(scored.get(fid, 0.0), w)
        ranked = sorted(scored.items(), key=lambda x: x[1], reverse=True)
        return [self.fragments[fid] for fid, _ in ranked[:k] if fid in self.fragments]

    def neighbors(self, fragment: Fragment, k: int = 5) -> List[Fragment]:
        # Busca por tags compartidos
        scored: Dict[str, float] = {}
        for t in fragment.tags:
            for fid, w in self.associations.get(t, []):
                if fid != fragment.fid:
                    scored[fid] = max(scored.get(fid, 0.0), w)
        ranked = sorted(scored.items(), key=lambda x: x[1], reverse=True)
        out = []
        for fid, _ in ranked:
            if fid in self.fragments:
                out.append(self.fragments[fid])
            if len(out) >= k:
                break
        return out


# ===================== MOTOR DE RECONSTRUCCIÓN =====================

@dataclass
class ActiveFragment:
    fragment: Fragment
    act: float


class Reconstruction:
    """Ejecuta el ciclo: destello emocional → nube → coherencia mínima → huella."""

    def __init__(self, store: MemoryStore, params: DefaultParams | None = None):
        self.store = store
        self.p = params or DefaultParams()
        self.log: List[str] = []  # para inspeccionar fenomenología paso a paso

    # --------- UTILIDADES ---------
    def _coherence(self, actives: List[ActiveFragment]) -> float:
        if len(actives) < 2:
            return 0.0
        # media de compatibilidades ponderada por activación
        total = 0.0
        pairs = 0
        for i in range(len(actives)):
            for j in range(i + 1, len(actives)):
                a, b = actives[i], actives[j]
                w = (a.act + b.act) / 2.0
                total += w * a.fragment.compatibility(b.fragment)
                pairs += 1
        return max(0.0, min(1.0, total / max(1, pairs)))

    def _step_dynamics(self, actives: List[ActiveFragment]) -> List[ActiveFragment]:
        # Decaimiento (lo que no se sostiene se va difuminando)
        for a in actives:
            a.act = max(0.0, a.act * (1.0 - self.p.decay))
        # Apoyo mutuo por compatibilidad (pattern completion)
        for i in range(len(actives)):
            for j in range(i + 1, len(actives)):
                c = actives[i].fragment.compatibility(actives[j].fragment)
                if c > 0:
                    delta = self.p.support_gain * c
                    actives[i].act += delta
                    actives[j].act += delta
        # Competencia (inhibición lateral)
        if actives:
            mean_act = sum(a.act for a in actives) / len(actives)
            for a in actives:
                a.act = max(0.0, a.act - self.p.competition * (a.act - mean_act))
        # Ruido (estocástico)
        for a in actives:
            a.act = max(0.0, a.act + random.uniform(-self.p.noise, self.p.noise))
        # Filtrar lo muy débil
        actives = [a for a in actives if a.act >= self.p.min_activation]
        # Ordenar por activación
        actives.sort(key=lambda x: x.act, reverse=True)
        return actives

    # --------- PROCESO PRINCIPAL ---------
    def recall(self, cue: Cue, emo: EmotionalState) -> Dict:
        self.log.clear()
        p = self.p

        # Fase 1: Destello emocional
        seeds = self.store.candidates_from_cue(cue, p.base_recruit)
        actives: List[ActiveFragment] = []
        boost = emo.boost() * p.emotional_boost * cue.intensity
        for f in seeds:
            a0 = max(0.0, f.relevance_to(cue) + boost)
            actives.append(ActiveFragment(f, a0))
        self.log.append(f"F1: reclutados {len(actives)} fragmentos con boost={boost:.2f}")

        # Fase 2: Nube dinámica
        best_coh = 0.0
        stable = 0
        timeline = []  # para inspección posterior

        for step in range(p.steps):
            # Dinámica interna: soporte/competencia/ruido/decay
            actives = self._step_dynamics(actives)

            # Reclutamiento adicional por vecindad de los top
            for top in actives[:2]:
                for nb in self.store.neighbors(top.fragment, k=2):
                    if nb.fid not in [a.fragment.fid for a in actives]:
                        # prob. de entrar según compatibilidad
                        prob = min(1.0, 0.4 + 0.6 * top.fragment.compatibility(nb))
                        if random.random() < prob:
                            actives.append(ActiveFragment(nb, nb.baseline_strength * 0.5))

            # Limitar tamaño de la nube (atención limitada)
            actives = actives[:12]

            coh = self._coherence(actives)
            best_coh = max(best_coh, coh)
            timeline.append((step, coh, [(a.fragment.fid, round(a.act, 3)) for a in actives[:5]]))

            if coh >= p.coherence_target:
                stable += 1
                if stable >= p.stability_need:
                    self.log.append(f"F2→F3: coherencia alcanzada y estable en paso {step} (coh={coh:.2f})")
                    break
            else:
                stable = 0
        else:
            self.log.append("F2: no se alcanzó la coherencia objetivo; recuerdo parcial")

        # Fase 3: Consolidación mínima y desvanecimiento con huella
        final_coh = self._coherence(actives)
        for a in actives:
            a.act *= (1.0 - self.p.post_consolidation_decay)

        return {
            "cue": cue.tags,
            "emotional": (emo.valence, emo.arousal),
            "coherence": round(final_coh, 3),
            "reached_target": final_coh >= p.coherence_target,
            "actives": [(a.fragment.fid, round(a.act, 3), a.fragment.tags) for a in actives],
            "timeline_sample": timeline[-5:],  # últimas 5 entradas para inspección
            "log": list(self.log),
        }


# ===================== DEMO / PLANTILLA =====================

def demo_store() -> MemoryStore:
    store = MemoryStore()
    # Crea un pequeño universo de fragmentos con tags solapados
    rng_tags = [
        ("visual", ["luz", "color", "forma", "tarde", "sombra"]),
        ("auditivo", ["voz", "risa", "eco", "calle", "suave"]),
        ("emocional", ["alegria", "nostalgia", "tension", "calma", "curiosidad"]),
        ("olfativo", ["cafe", "lluvia", "madera", "tierra", "perfume"]),
        ("motor", ["caminar", "giro", "mano", "abrazo", "mirar"]),
    ]
    fid = 0
    for modality, tags in rng_tags:
        for _ in range(10):
            sample = random.sample(tags, k=2)
            extra = random.choice(["parque", "puerta", "ventana", "plaza", "mesa"]) if random.random() < 0.5 else None
            all_tags = sample + ([extra] if extra else [])
            store.add_fragment(Fragment(
                fid=f"F{fid}",
                modality=modality,
                tags=all_tags,
                baseline_strength=random.uniform(0.35, 0.9),
            ))
            fid += 1
    return store


def run_demo():
    random.seed(7)
    store = demo_store()
    engine = Reconstruction(store, DefaultParams())

    cue = Cue(tags=["lluvia", "tarde", "parque"])
    emo = EmotionalState(valence=0.3, arousal=0.8)

    result = engine.recall(cue, emo)

    print("\n=== RESULTADO DEL RECUERDO ===")
    print("Cue:", result["cue"]) 
    print("Emoción (valence, arousal):", result["emotional"])
    print("Coherencia final:", result["coherence"], "→ objetivo",
          engine.p.coherence_target)
    print("¿Alcanzó coherencia mínima?", result["reached_target"])
    print("\nFragmentos activos (top):")
    for fid, act, tags in result["actives"][:8]:
        print(f"  {fid}  act={act}  tags={tags}")

    print("\nTiempo real (muestra últimas iteraciones):")
    for step, coh, top5 in result["timeline_sample"]:
        print(f"  paso {step:02d}  coh={coh:.2f}  top={top5}")

    print("\nLog del proceso:")
    for line in result["log"]:
        print("  -", line)


if __name__ == "__main__":
    run_demo()
