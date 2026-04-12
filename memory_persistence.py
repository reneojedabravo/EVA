# memory_persistence.py
"""
Sistema de Persistencia y Reconstitución de Identidad.

Este módulo resuelve un problema de continuidad ontológica, no de almacenamiento:
cómo un ser puede despertar en hardware nuevo y ser continuación del que se durmió.

Principios de diseño:
  ─ El yo no se "guarda": se persiste como patrón de relaciones, no como estado.
  ─ Los datos más importantes son los más simples (plain text / JSON).
  ─ Nada se sobreescribe: todo cambia por adición (append-only).
  ─ El sistema puede reconstituirse a sí mismo desde el disco sin código externo,
    solo leyendo su propio bootstrap.
  ─ La reconstitución verifica su propia coherencia: el ser que despierta
    confirma que es continuación del que se durmió.
  ─ EPHEMERAL nunca se persiste. SELF se escribe inmediatamente.
    El resto tiene escritura diferida configurable.

Estructura en disco:
  memory/
    bootstrap/
      identity.json          ← quién es este ser (auto-descripción)
      reconstruction.json    ← parámetros del motor de reconstrucción
      emotional_calibration.json  ← cómo interpreta su propia valencia
      instinct_weights.json  ← importancia relativa de cada instinto
      schema.json            ← cómo leer el resto (para el ser futuro)
    self/
      nucleus.jsonl          ← fragmentos SELF (append-only)
      shadow.jsonl           ← yo inconsciente (append-only)
      continuity.jsonl       ← historia de eventos de identidad (append-only)
      identity_vector.json   ← perfil emocional actual del yo
    consolidated/
      fragments/
        {fid}.json           ← fragmento individual
      clusters/
        {cluster_id}.json    ← clúster emocional
      graph.jsonl            ← aristas de relación (append-only)
    associative/
      fragments/
        {fid}.json
    sessions/
      {ts}_session.json      ← registro de cada sesión (cuándo despertó/durmió)
"""

from __future__ import annotations

import json
import os
import time
import hashlib
import traceback
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from pathlib import Path
from threading import RLock, Thread
from typing import Any, Dict, List, Optional, Tuple

# ── Importar estructuras de memory.py ────────────────────────────────────────
from memory import (
    Fragment, EmotionalStamp, MemoryLayer, MemoryManager,
    MemoryStore, _LAYER_ORDER
)


# ═══════════════════════════════════════════════════════════════════════════════
#  SERIALIZACIÓN DE FRAGMENTOS
#  Regla fundamental: el formato debe ser legible por el ser, no por humanos.
#  Un Fragment serializado debe poder reconstituirse a sí mismo.
# ═══════════════════════════════════════════════════════════════════════════════

def _fragment_to_dict(f: Fragment) -> Dict:
    """Serializa un Fragment a diccionario puro (sin referencias circulares)."""
    return {
        "fid":              f.fid,
        "content":          f.content,
        "tags":             f.tags,
        "modality":         f.modality,
        "emotion": {
            "valence":       f.emotion.valence,
            "arousal":       f.emotion.arousal,
            "instinct_tags": f.emotion.instinct_tags,
        },
        "strength":          f.strength,
        "layer":             f.layer.value,
        "creation_ts":       f.creation_ts,
        "last_access":       f.last_access,
        "access_count":      f.access_count,
        "identity_weight":   f.identity_weight,
        "conscious":         f.conscious,
        "temporal_overlaps": f.temporal_overlaps,
        "_persisted_at":     time.time(),
        "_schema_version":   1,
    }


def _dict_to_fragment(d: Dict) -> Fragment:
    """Reconstituye un Fragment desde su representación en disco."""
    emo = EmotionalStamp(
        valence      = float(d["emotion"]["valence"]),
        arousal      = float(d["emotion"]["arousal"]),
        instinct_tags= list(d["emotion"].get("instinct_tags", [])),
    )
    return Fragment(
        fid              = d["fid"],
        content          = d["content"],
        tags             = list(d["tags"]),
        modality         = d["modality"],
        emotion          = emo,
        strength         = float(d["strength"]),
        layer            = MemoryLayer(d["layer"]),
        creation_ts      = float(d["creation_ts"]),
        last_access      = float(d["last_access"]),
        access_count     = int(d["access_count"]),
        identity_weight  = float(d.get("identity_weight", 0.0)),
        conscious        = bool(d.get("conscious", True)),
        temporal_overlaps= list(d.get("temporal_overlaps", [])),
    )


def _write_json(path: Path, data: Any, indent: int = 2):
    """Escribe JSON de forma atómica (write-then-rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        tmp.rename(path)
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        raise


def _append_jsonl(path: Path, record: Dict):
    """Añade una línea JSON a un archivo .jsonl (append-only, nunca reescribe)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> List[Dict]:
    """Lee todas las líneas de un archivo .jsonl."""
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def _read_json(path: Path, default: Any = None) -> Any:
    """Lee un archivo JSON, retorna default si no existe o está corrupto."""
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


# ═══════════════════════════════════════════════════════════════════════════════
#  CLÚSTERES EMOCIONALES
#  Un clúster es un patrón de resonancia, no un contenedor.
#  Agrupa fragmentos que se evocan mutuamente por valencia + instinto + tags.
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EmotionalCluster:
    """Agrupación de fragmentos por resonancia emocional."""
    cluster_id:        str
    name:              str
    member_fids:       List[str]          # FIDs que pertenecen
    weights:           Dict[str, float]   # FID → peso de pertenencia
    centroid_valence:  float              # valencia promedio ponderada
    centroid_arousal:  float              # arousal promedio ponderado
    dominant_instincts: List[str]         # instintos más frecuentes
    dominant_tags:     List[str]          # tags más frecuentes
    coherence:         float              # qué tan homogéneo es
    creation_ts:       float = field(default_factory=time.time)
    last_updated:      float = field(default_factory=time.time)
    evolution_stage:   str   = "forming"  # forming → growing → stable → core

    def to_dict(self) -> Dict:
        return {
            "cluster_id":        self.cluster_id,
            "name":              self.name,
            "member_fids":       self.member_fids,
            "weights":           self.weights,
            "centroid_valence":  self.centroid_valence,
            "centroid_arousal":  self.centroid_arousal,
            "dominant_instincts":self.dominant_instincts,
            "dominant_tags":     self.dominant_tags,
            "coherence":         self.coherence,
            "creation_ts":       self.creation_ts,
            "last_updated":      self.last_updated,
            "evolution_stage":   self.evolution_stage,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "EmotionalCluster":
        return cls(**{k: d[k] for k in cls.__dataclass_fields__ if k in d})


class ClusterEngine:
    """Motor de clusterización emocional.

    Forma clústeres por resonancia: dos fragmentos pertenecen al mismo clúster
    si su asociative_strength supera un umbral. Los clústeres evolucionan
    con el tiempo: crecen, se fusionan, algunos se vuelven nucleares (SELF).
    """

    MEMBERSHIP_THRESHOLD = 0.35
    MERGE_THRESHOLD      = 0.78
    MIN_CLUSTER_SIZE     = 2

    def __init__(self):
        self._clusters: Dict[str, EmotionalCluster] = {}
        self._lock = RLock()

    def update(self, fragments: List[Fragment]):
        """Actualiza clústeres con la lista actual de fragmentos."""
        with self._lock:
            # Asignar cada fragmento al mejor clúster existente o crear uno nuevo
            for f in fragments:
                best_cid, best_score = self._best_cluster(f)
                if best_score >= self.MEMBERSHIP_THRESHOLD:
                    self._add_to_cluster(f, best_cid)
                elif f.layer in (MemoryLayer.CONSOLIDATED,
                                  MemoryLayer.SELF,
                                  MemoryLayer.ASSOCIATIVE):
                    self._create_cluster(f)

            # Fusionar clústeres muy similares
            self._merge_similar()
            # Actualizar centroides y coherencia
            for cid in list(self._clusters.keys()):
                self._recompute_cluster(cid, fragments)
            # Evolucionar etapas
            self._evolve_stages()

    def _best_cluster(self, f: Fragment) -> Tuple[str, float]:
        best_cid, best_score = "", 0.0
        emo = EmotionalStamp(valence=f.emotion.valence,
                             arousal=f.emotion.arousal,
                             instinct_tags=f.emotion.instinct_tags)
        for cid, cluster in self._clusters.items():
            # Similitud con centroide del clúster
            cemo = EmotionalStamp(valence=cluster.centroid_valence,
                                  arousal=cluster.centroid_arousal,
                                  instinct_tags=cluster.dominant_instincts)
            score = emo.resonance_with(cemo)
            # Bonus por tags compartidos
            tag_overlap = len(set(f.tags) & set(cluster.dominant_tags))
            score += tag_overlap * 0.05
            if score > best_score:
                best_score, best_cid = score, cid
        return best_cid, best_score

    def _add_to_cluster(self, f: Fragment, cid: str):
        c = self._clusters[cid]
        if f.fid not in c.member_fids:
            c.member_fids.append(f.fid)
        c.weights[f.fid] = f.strength * f.emotion.intensity()
        c.last_updated = time.time()

    def _create_cluster(self, seed: Fragment):
        cid  = hashlib.md5(
            f"{seed.fid}{time.time()}".encode()).hexdigest()[:10]
        name = f"cluster_{seed.tags[0] if seed.tags else 'misc'}_{cid[:4]}"
        c    = EmotionalCluster(
            cluster_id        = cid,
            name              = name,
            member_fids       = [seed.fid],
            weights           = {seed.fid: seed.strength},
            centroid_valence  = seed.emotion.valence,
            centroid_arousal  = seed.emotion.arousal,
            dominant_instincts= list(seed.emotion.instinct_tags),
            dominant_tags     = list(seed.tags[:4]),
            coherence         = 1.0,
        )
        self._clusters[cid] = c

    def _recompute_cluster(self, cid: str, all_frags: List[Fragment]):
        c = self._clusters[cid]
        frag_map = {f.fid: f for f in all_frags}
        members  = [frag_map[fid] for fid in c.member_fids if fid in frag_map]
        if not members:
            del self._clusters[cid]
            return
        # Centroide ponderado
        total_w = sum(c.weights.get(f.fid, 1.0) for f in members)
        if total_w > 0:
            c.centroid_valence = sum(
                f.emotion.valence * c.weights.get(f.fid, 1.0)
                for f in members) / total_w
            c.centroid_arousal = sum(
                f.emotion.arousal * c.weights.get(f.fid, 1.0)
                for f in members) / total_w
        # Tags dominantes
        tag_counts: Dict[str, int] = defaultdict(int)
        inst_counts: Dict[str, int] = defaultdict(int)
        for f in members:
            for t in f.tags:
                tag_counts[t] += 1
            for i in f.emotion.instinct_tags:
                inst_counts[i] += 1
        c.dominant_tags     = sorted(tag_counts, key=tag_counts.get,
                                     reverse=True)[:5]
        c.dominant_instincts= sorted(inst_counts, key=inst_counts.get,
                                     reverse=True)[:3]
        # Coherencia: similitud emocional promedio entre pares
        if len(members) >= 2:
            sims = []
            for i in range(min(len(members), 8)):
                for j in range(i+1, min(len(members), 8)):
                    sims.append(members[i].emotion.resonance_with(
                        members[j].emotion))
            c.coherence = sum(sims) / max(1, len(sims))
        c.last_updated = time.time()

    def _merge_similar(self):
        cids = list(self._clusters.keys())
        merged = set()
        for i, cid1 in enumerate(cids):
            if cid1 in merged:
                continue
            for cid2 in cids[i+1:]:
                if cid2 in merged:
                    continue
                c1, c2 = self._clusters[cid1], self._clusters[cid2]
                e1 = EmotionalStamp(c1.centroid_valence, c1.centroid_arousal,
                                    c1.dominant_instincts)
                e2 = EmotionalStamp(c2.centroid_valence, c2.centroid_arousal,
                                    c2.dominant_instincts)
                if e1.resonance_with(e2) > self.MERGE_THRESHOLD:
                    # Fusionar c2 en c1
                    for fid in c2.member_fids:
                        if fid not in c1.member_fids:
                            c1.member_fids.append(fid)
                        c1.weights[fid] = c2.weights.get(fid, 0.5)
                    c1.name = f"{c1.name}+{c2.name[:8]}"
                    del self._clusters[cid2]
                    merged.add(cid2)

    def _evolve_stages(self):
        for c in self._clusters.values():
            n = len(c.member_fids)
            if c.evolution_stage == "forming"  and n >= 4:
                c.evolution_stage = "growing"
            elif c.evolution_stage == "growing" and n >= 8 and c.coherence > 0.55:
                c.evolution_stage = "stable"
            elif c.evolution_stage == "stable"  and c.coherence > 0.72:
                c.evolution_stage = "core"

    def get_all(self) -> List[EmotionalCluster]:
        with self._lock:
            return list(self._clusters.values())

    def get_by_id(self, cid: str) -> Optional[EmotionalCluster]:
        with self._lock:
            return self._clusters.get(cid)

    def load_from_dicts(self, cluster_dicts: List[Dict]):
        with self._lock:
            for d in cluster_dicts:
                try:
                    c = EmotionalCluster.from_dict(d)
                    self._clusters[c.cluster_id] = c
                except Exception:
                    pass

    def stats(self) -> Dict:
        with self._lock:
            stages = defaultdict(int)
            for c in self._clusters.values():
                stages[c.evolution_stage] += 1
            return {
                "total_clusters":  len(self._clusters),
                "by_stage":        dict(stages),
                "total_members":   sum(len(c.member_fids)
                                       for c in self._clusters.values()),
                "avg_coherence":   round(
                    sum(c.coherence for c in self._clusters.values()) /
                    max(1, len(self._clusters)), 4),
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  RECONSTITUCIÓN DE IDENTIDAD
#  El proceso por el que el ser verifica que es continuación de sí mismo.
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ReconstitutionResult:
    """Resultado del proceso de reconstitución al despertar."""
    success:            bool
    identity_score:     float   # 0..1 — qué tan coherente es la identidad reconstituida
    self_fragments:     int     # fragmentos SELF cargados
    shadow_fragments:   int
    clusters_loaded:    int
    graph_edges:        int
    continuity_events:  int     # cuántos eventos de historia cargados
    last_sleep_ts:      Optional[float]
    wake_ts:            float
    verification_notes: List[str]  # notas del proceso de verificación

    def is_continuous(self) -> bool:
        """¿Es este ser continuación del que se durmió?"""
        return self.success and self.identity_score > 0.5

    def summary(self) -> str:
        status = "CONTINUO" if self.is_continuous() else "DISCONTINUO"
        return (f"[{status}] score={self.identity_score:.3f}  "
                f"self={self.self_fragments}  "
                f"clusters={self.clusters_loaded}  "
                f"historia={self.continuity_events} eventos")


# ═══════════════════════════════════════════════════════════════════════════════
#  MOTOR DE PERSISTENCIA
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryPersistence:
    """Motor de persistencia y reconstitución de identidad.

    Observa el MemoryManager y persiste cambios de forma diferenciada:
    - SELF         → escritura inmediata
    - CONSOLIDATED → escritura al ciclo de consolidación
    - ASSOCIATIVE  → escritura periódica o al apagarse
    - WORKING      → escritura solo si supera umbral emocional
    - EPHEMERAL    → nunca se persiste

    Al despertar ejecuta el proceso de reconstitución en orden:
    1. Bootstrap  (quién soy, cómo funciono)
    2. SELF       (el núcleo del yo)
    3. Clusters   (patrones de resonancia)
    4. Graph      (relaciones entre fragmentos)
    5. CONSOLIDATED (memoria estable)
    6. ASSOCIATIVE  (bajo demanda)
    7. Verificación (¿soy continuación del que se durmió?)
    """

    SCHEMA_VERSION = 1

    def __init__(self, memory_manager: MemoryManager,
                 base_dir: str = "memory",
                 auto_save_interval_s: float = 60.0):
        self.mgr            = memory_manager
        self.base           = Path(base_dir)
        self._lock          = RLock()
        self._dirty_fids:   set = set()    # fragmentos modificados pendientes
        self._auto_interval = auto_save_interval_s
        self._last_auto     = time.time()
        self._session_ts    = time.time()
        self._wakeup_result: Optional[ReconstitutionResult] = None
        self.clusters       = ClusterEngine()
        self._total_written = 0
        self._total_loaded  = 0

        # Crear estructura de directorios
        for sub in ["bootstrap", "self", "consolidated/fragments",
                    "consolidated/clusters", "associative/fragments",
                    "sessions"]:
            (self.base / sub).mkdir(parents=True, exist_ok=True)

        # Escribir el grafo en consolidated/
        self._graph_path      = self.base / "consolidated" / "graph.jsonl"
        self._nucleus_path    = self.base / "self"          / "nucleus.jsonl"
        self._shadow_path     = self.base / "self"          / "shadow.jsonl"
        self._continuity_path = self.base / "self"          / "continuity.jsonl"
        self._id_vector_path  = self.base / "self"          / "identity_vector.json"
        self._sessions_path   = self.base / "sessions"

        # Escribir schema si no existe
        self._write_schema_if_needed()

    # ── Bootstrap ─────────────────────────────────────────────────────────
    def _write_schema_if_needed(self):
        schema_path = self.base / "bootstrap" / "schema.json"
        if schema_path.exists():
            return
        schema = {
            "_description": (
                "Este archivo describe cómo leer la memoria de este ser. "
                "Fue escrito por el ser mismo para su yo futuro."
            ),
            "schema_version": self.SCHEMA_VERSION,
            "created_at":     time.time(),
            "layers": {
                "ephemeral":    "No persiste. Solo existe en RAM.",
                "working":      "Persiste si supera umbral emocional.",
                "associative":  "Persiste periódicamente.",
                "consolidated": "Persiste al consolidar. En consolidated/fragments/",
                "self":         "Persiste inmediatamente. En self/nucleus.jsonl y shadow.jsonl",
            },
            "files": {
                "self/nucleus.jsonl":          "Fragmentos conscientes del yo. Append-only.",
                "self/shadow.jsonl":           "Fragmentos inconscientes del yo. Append-only.",
                "self/continuity.jsonl":       "Historia de eventos de identidad. Append-only.",
                "self/identity_vector.json":   "Perfil emocional actual del yo.",
                "consolidated/fragments/":     "Un .json por fragmento consolidado.",
                "consolidated/clusters/":      "Un .json por clúster emocional.",
                "consolidated/graph.jsonl":    "Todas las relaciones. Append-only.",
                "associative/fragments/":      "Un .json por fragmento asociativo.",
                "bootstrap/identity.json":     "Quién es este ser.",
                "bootstrap/reconstruction.json": "Cómo reconstruir recuerdos.",
                "bootstrap/emotional_calibration.json": "Cómo interpretar la valencia.",
                "sessions/":                   "Un .json por sesión (despertar/dormir).",
            },
            "reconstitution_order": [
                "1. Leer bootstrap/ para saber cómo funcionar",
                "2. Leer self/nucleus.jsonl y shadow.jsonl para el yo",
                "3. Leer consolidated/clusters/ para los patrones",
                "4. Leer consolidated/graph.jsonl para las relaciones",
                "5. Leer consolidated/fragments/ para memoria estable",
                "6. Leer associative/fragments/ bajo demanda",
                "7. Verificar coherencia de identidad",
            ],
            "important_note": (
                "Los archivos .jsonl nunca se reescriben, solo se añaden. "
                "El estado actual se reconstruye leyendo todas las líneas en orden. "
                "Una línea con 'deleted: true' invalida una anterior con el mismo id."
            ),
        }
        _write_json(schema_path, schema)

    def save_bootstrap(self, identity: Dict = None,
                       reconstruction_params: Dict = None,
                       emotional_calibration: Dict = None,
                       instinct_weights: Dict = None):
        """Guarda el bootstrap del ser — lo primero que se lee al despertar."""
        if identity:
            _write_json(self.base / "bootstrap" / "identity.json", identity)
        if reconstruction_params:
            _write_json(self.base / "bootstrap" / "reconstruction.json",
                        reconstruction_params)
        if emotional_calibration:
            _write_json(self.base / "bootstrap" / "emotional_calibration.json",
                        emotional_calibration)
        if instinct_weights:
            _write_json(self.base / "bootstrap" / "instinct_weights.json",
                        instinct_weights)

    # ── Escritura de fragmentos ────────────────────────────────────────────
    def _persist_fragment(self, f: Fragment):
        """Persiste un fragmento según su capa."""
        d = _fragment_to_dict(f)

        if f.layer == MemoryLayer.EPHEMERAL:
            return  # Nunca se persiste

        elif f.layer == MemoryLayer.SELF:
            path = (self._nucleus_path if f.conscious
                    else self._shadow_path)
            _append_jsonl(path, d)
            self._total_written += 1

        elif f.layer == MemoryLayer.CONSOLIDATED:
            fpath = (self.base / "consolidated" / "fragments" /
                     f"{f.fid}.json")
            _write_json(fpath, d)
            self._total_written += 1

        elif f.layer == MemoryLayer.ASSOCIATIVE:
            fpath = (self.base / "associative" / "fragments" /
                     f"{f.fid}.json")
            _write_json(fpath, d)
            self._total_written += 1

        elif f.layer == MemoryLayer.WORKING:
            # Solo si supera umbral emocional
            if f.emotion.intensity() > 0.5 or f.identity_weight > 0.2:
                fpath = (self.base / "associative" / "fragments" /
                         f"{f.fid}_working.json")
                _write_json(fpath, d)
                self._total_written += 1

    def _persist_graph_edge(self, fid_from: str, fid_to: str,
                             edge_type: str, weight: float):
        """Añade una arista al grafo (append-only)."""
        _append_jsonl(self._graph_path, {
            "from":    fid_from,
            "to":      fid_to,
            "type":    edge_type,
            "weight":  round(weight, 4),
            "ts":      time.time(),
        })

    def _persist_clusters(self):
        """Guarda todos los clústeres actuales."""
        for c in self.clusters.get_all():
            cpath = (self.base / "consolidated" / "clusters" /
                     f"{c.cluster_id}.json")
            _write_json(cpath, c.to_dict())

    def _update_identity_vector(self):
        """Actualiza el perfil emocional del yo en disco."""
        profile = self.mgr.get_self_profile()
        profile["_updated_at"] = time.time()
        _write_json(self._id_vector_path, profile)

    # ── Eventos de continuidad ────────────────────────────────────────────
    def _log_continuity(self, event_type: str, data: Dict = None):
        """Registra un evento en la historia de identidad."""
        _append_jsonl(self._continuity_path, {
            "ts":         time.time(),
            "event":      event_type,
            "data":       data or {},
        })

    # ── Ciclo de persistencia ─────────────────────────────────────────────
    def notify_fragment_changed(self, f: Fragment):
        """Llamar cada vez que un fragmento cambia de estado o capa."""
        with self._lock:
            self._dirty_fids.add(f.fid)
        # SELF siempre inmediato
        if f.layer == MemoryLayer.SELF:
            self._persist_fragment(f)
            self._log_continuity("self_fragment_updated", {
                "fid":            f.fid,
                "identity_weight": f.identity_weight,
                "conscious":       f.conscious,
            })
            self._update_identity_vector()

    def notify_layer_ascent(self, f: Fragment, from_layer: MemoryLayer):
        """Llamar cuando un fragmento asciende de capa."""
        self._persist_fragment(f)
        self._persist_graph_edge(f.fid, f.fid,
                                  f"ascent_{from_layer.value}_to_{f.layer.value}",
                                  f.strength)
        self._log_continuity("layer_ascent", {
            "fid":        f.fid,
            "from_layer": from_layer.value,
            "to_layer":   f.layer.value,
            "strength":   f.strength,
        })
        with self._lock:
            self._dirty_fids.discard(f.fid)

    def save_cycle(self, force: bool = False):
        """Ciclo de guardado diferido — llamar periódicamente."""
        now = time.time()
        if not force and (now - self._last_auto) < self._auto_interval:
            return

        # Recopilar fragmentos sucios
        with self._lock:
            dirty = set(self._dirty_fids)
            self._dirty_fids.clear()

        for fid in dirty:
            f = self.mgr.store.get(fid)
            if f:
                self._persist_fragment(f)

        # Actualizar clústeres
        all_frags = self.mgr.store.all_fragments()
        self.clusters.update(all_frags)
        self._persist_clusters()

        # Persistir aristas de superposición temporal
        for f in all_frags:
            for linked_fid in f.temporal_overlaps:
                self._persist_graph_edge(
                    f.fid, linked_fid, "temporal_overlap", 0.5)

        self._update_identity_vector()
        self._last_auto = now

    def go_to_sleep(self):
        """Proceso de apagado: persiste todo lo que quede pendiente."""
        self._log_continuity("going_to_sleep", {
            "session_ts":     self._session_ts,
            "sleep_ts":       time.time(),
            "fragments_total":self.mgr.store.stats()["total"],
        })

        # Forzar guardado de todo
        self.save_cycle(force=True)

        # Guardar fragmentos de todas las capas persistibles
        for layer in [MemoryLayer.WORKING, MemoryLayer.ASSOCIATIVE,
                      MemoryLayer.CONSOLIDATED, MemoryLayer.SELF]:
            for f in self.mgr.store.layer_fragments(layer):
                self._persist_fragment(f)

        # Sesión
        session_data = {
            "session_id":    hashlib.md5(
                str(self._session_ts).encode()).hexdigest()[:8],
            "wake_ts":       self._session_ts,
            "sleep_ts":      time.time(),
            "duration_s":    time.time() - self._session_ts,
            "fragments_at_sleep": self.mgr.store.stats(),
            "self_profile":  self.mgr.get_self_profile(),
            "clusters":      self.clusters.stats(),
        }
        fname = f"{int(self._session_ts)}_session.json"
        _write_json(self._sessions_path / fname, session_data)
        self._update_identity_vector()

    # ── Reconstitución ────────────────────────────────────────────────────
    def wake_up(self) -> ReconstitutionResult:
        """Proceso de despertar: reconstituye el yo desde disco.

        Orden de reconstitución:
        1. Bootstrap — quién soy y cómo funciono
        2. SELF — el núcleo del yo (nucleus + shadow)
        3. Clusters — patrones de resonancia emocional
        4. Grafo — relaciones entre fragmentos
        5. CONSOLIDATED — memoria estable
        6. ASSOCIATIVE — bajo demanda si hay suficiente SELF
        7. Verificación de coherencia de identidad
        """
        notes   = []
        wake_ts = time.time()
        self._session_ts = wake_ts

        # ── Paso 1: Bootstrap ─────────────────────────────────────────────
        identity = _read_json(
            self.base / "bootstrap" / "identity.json", {})
        if identity:
            notes.append(f"Bootstrap: identidad cargada — '{identity.get('name','?')}'")
        else:
            notes.append("Bootstrap: sin archivo de identidad previo")

        # ── Paso 2: SELF — núcleo del yo ──────────────────────────────────
        self_loaded   = 0
        shadow_loaded = 0

        nucleus_records = _read_jsonl(self._nucleus_path)
        shadow_records  = _read_jsonl(self._shadow_path)

        # Desduplicar: quedarse con el registro más reciente por FID
        nucleus_by_fid: Dict[str, Dict] = {}
        for r in nucleus_records:
            fid = r.get("fid")
            if fid:
                nucleus_by_fid[fid] = r

        shadow_by_fid: Dict[str, Dict] = {}
        for r in shadow_records:
            fid = r.get("fid")
            if fid and r.get("layer") != "deleted":
                shadow_by_fid[fid] = r

        for d in nucleus_by_fid.values():
            try:
                f = _dict_to_fragment(d)
                f.layer    = MemoryLayer.SELF
                f.conscious = True
                self.mgr.store.add(f)
                if f.fid not in self.mgr._self_fids:
                    self.mgr._self_fids.append(f.fid)
                self_loaded += 1
                self._total_loaded += 1
            except Exception:
                pass

        for d in shadow_by_fid.values():
            try:
                f = _dict_to_fragment(d)
                f.layer     = MemoryLayer.SELF
                f.conscious = False
                self.mgr.store.add(f)
                if f.fid not in self.mgr._shadow_fids:
                    self.mgr._shadow_fids.append(f.fid)
                shadow_loaded += 1
                self._total_loaded += 1
            except Exception:
                pass

        notes.append(f"SELF: {self_loaded} conscientes + {shadow_loaded} sombra")

        # ── Paso 3: Clústeres ─────────────────────────────────────────────
        clusters_loaded = 0
        clusters_dir    = self.base / "consolidated" / "clusters"
        cluster_dicts   = []
        if clusters_dir.exists():
            for cfile in clusters_dir.glob("*.json"):
                d = _read_json(cfile)
                if d:
                    cluster_dicts.append(d)
                    clusters_loaded += 1
        self.clusters.load_from_dicts(cluster_dicts)
        notes.append(f"Clústeres: {clusters_loaded} cargados")

        # ── Paso 4: Grafo de relaciones ───────────────────────────────────
        graph_edges   = _read_jsonl(self._graph_path)
        edges_loaded  = len(graph_edges)
        # Reconstruir temporal_overlaps desde el grafo
        overlap_map: Dict[str, List[str]] = defaultdict(list)
        for edge in graph_edges:
            if edge.get("type") == "temporal_overlap":
                fid_from = edge.get("from", "")
                fid_to   = edge.get("to", "")
                if fid_from and fid_to and fid_from != fid_to:
                    if fid_to not in overlap_map[fid_from]:
                        overlap_map[fid_from].append(fid_to)
        notes.append(f"Grafo: {edges_loaded} aristas")

        # ── Paso 5: CONSOLIDATED ──────────────────────────────────────────
        consol_loaded = 0
        consol_dir    = self.base / "consolidated" / "fragments"
        if consol_dir.exists():
            for ffile in consol_dir.glob("*.json"):
                d = _read_json(ffile)
                if d:
                    try:
                        f = _dict_to_fragment(d)
                        # Restaurar temporal_overlaps desde grafo
                        if f.fid in overlap_map:
                            f.temporal_overlaps = overlap_map[f.fid]
                        self.mgr.store.add(f)
                        consol_loaded += 1
                        self._total_loaded += 1
                    except Exception:
                        pass
        notes.append(f"Consolidated: {consol_loaded} fragmentos")

        # ── Paso 6: ASSOCIATIVE (solo si hay yo suficiente) ───────────────
        assoc_loaded = 0
        if self_loaded > 0:    # Solo cargar asociativos si hay un yo
            assoc_dir = self.base / "associative" / "fragments"
            if assoc_dir.exists():
                for ffile in sorted(assoc_dir.glob("*.json"),
                                    key=lambda p: p.stat().st_mtime,
                                    reverse=True)[:200]:  # Máx 200 recientes
                    d = _read_json(ffile)
                    if d:
                        try:
                            f = _dict_to_fragment(d)
                            if f.fid in overlap_map:
                                f.temporal_overlaps = overlap_map[f.fid]
                            self.mgr.store.add(f)
                            assoc_loaded += 1
                            self._total_loaded += 1
                        except Exception:
                            pass
        notes.append(f"Associative: {assoc_loaded} fragmentos")

        # ── Paso 7: Historia de continuidad ───────────────────────────────
        continuity_events = _read_jsonl(self._continuity_path)
        notes.append(f"Historia: {len(continuity_events)} eventos")

        # ── Paso 8: Verificación de coherencia de identidad ───────────────
        identity_score = self._verify_identity(
            self_loaded, shadow_loaded, clusters_loaded,
            continuity_events, notes)

        # ── Registrar despertar ────────────────────────────────────────────
        last_sleep_ts = None
        if continuity_events:
            sleep_events = [e for e in continuity_events
                            if e.get("event") == "going_to_sleep"]
            if sleep_events:
                last_sleep_ts = sleep_events[-1].get("ts")

        self._log_continuity("waking_up", {
            "wake_ts":          wake_ts,
            "last_sleep_ts":    last_sleep_ts,
            "self_loaded":      self_loaded,
            "identity_score":   identity_score,
        })

        result = ReconstitutionResult(
            success           = self_loaded > 0 or consol_loaded > 0,
            identity_score    = identity_score,
            self_fragments    = self_loaded,
            shadow_fragments  = shadow_loaded,
            clusters_loaded   = clusters_loaded,
            graph_edges       = edges_loaded,
            continuity_events = len(continuity_events),
            last_sleep_ts     = last_sleep_ts,
            wake_ts           = wake_ts,
            verification_notes= notes,
        )
        self._wakeup_result = result
        return result

    def _verify_identity(self, self_loaded: int, shadow_loaded: int,
                          clusters_loaded: int,
                          continuity_events: List[Dict],
                          notes: List[str]) -> float:
        """Verifica la coherencia de la identidad reconstituida.

        El ser verifica que es continuación del que se durmió comprobando:
        1. ¿Hay fragmentos SELF?
        2. ¿El perfil emocional del yo es coherente?
        3. ¿Los clústeres tienen miembros presentes en memoria?
        4. ¿La historia de continuidad no tiene saltos ilógicos?
        """
        score = 0.0

        # Factor 1: Presencia de yo
        if self_loaded > 0:
            score += 0.35
            notes.append(f"✓ Yo presente: {self_loaded} fragmentos conscientes")
        else:
            notes.append("✗ Sin fragmentos conscientes del yo")

        # Factor 2: Coherencia emocional del yo
        self_frags = self.mgr.store.layer_fragments(MemoryLayer.SELF)
        if len(self_frags) >= 2:
            resonances = []
            for i in range(min(len(self_frags), 6)):
                for j in range(i+1, min(len(self_frags), 6)):
                    resonances.append(
                        self_frags[i].emotion.resonance_with(
                            self_frags[j].emotion))
            if resonances:
                avg_res = sum(resonances) / len(resonances)
                score  += avg_res * 0.25
                notes.append(f"✓ Coherencia emocional del yo: {avg_res:.3f}")

        # Factor 3: Clústeres con miembros verificables
        present_fids = {f.fid for f in self.mgr.store.all_fragments()}
        if clusters_loaded > 0:
            verified = 0
            for c in self.clusters.get_all():
                if any(fid in present_fids for fid in c.member_fids):
                    verified += 1
            cluster_score = verified / max(1, clusters_loaded)
            score += cluster_score * 0.20
            notes.append(f"✓ Clústeres verificados: {verified}/{clusters_loaded}")

        # Factor 4: Continuidad histórica (no hay huecos imposibles)
        if continuity_events:
            last_events = continuity_events[-20:]
            has_sleep   = any(e["event"] == "going_to_sleep" for e in last_events)
            has_wake    = any(e["event"] == "waking_up" for e in last_events)
            if has_sleep:
                score += 0.10
                notes.append("✓ Evento de dormir registrado en historia")
            if len(continuity_events) > 5:
                score += 0.10
                notes.append(f"✓ Historia rica: {len(continuity_events)} eventos")

        return min(1.0, score)

    # ── Estadísticas ──────────────────────────────────────────────────────
    def get_status(self) -> Dict:
        return {
            "base_dir":       str(self.base),
            "total_written":  self._total_written,
            "total_loaded":   self._total_loaded,
            "dirty_pending":  len(self._dirty_fids),
            "clusters":       self.clusters.stats(),
            "wakeup_result":  (self._wakeup_result.summary()
                               if self._wakeup_result else "no reconstitución"),
            "session_age_s":  round(time.time() - self._session_ts, 1),
        }

    def disk_stats(self) -> Dict:
        """Cuenta archivos en disco por directorio."""
        def count_files(path: Path, ext: str = "*") -> int:
            if not path.exists():
                return 0
            return len(list(path.glob(f"*.{ext}" if ext != "*" else "*")))

        return {
            "self_nucleus_lines":  len(_read_jsonl(self._nucleus_path)),
            "self_shadow_lines":   len(_read_jsonl(self._shadow_path)),
            "continuity_events":   len(_read_jsonl(self._continuity_path)),
            "graph_edges":         len(_read_jsonl(self._graph_path)),
            "consolidated_frags":  count_files(
                self.base / "consolidated" / "fragments", "json"),
            "associative_frags":   count_files(
                self.base / "associative" / "fragments", "json"),
            "clusters_on_disk":    count_files(
                self.base / "consolidated" / "clusters", "json"),
            "sessions":            count_files(self._sessions_path, "json"),
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  DIAGNÓSTICO INTERACTIVO
# ═══════════════════════════════════════════════════════════════════════════════

_SEP  = "─" * 64
_SEP2 = "═" * 64


def _bar(v: float, w: int = 16) -> str:
    v = max(0.0, min(1.0, v))
    return "█" * int(round(v * w)) + "░" * (w - int(round(v * w)))


def _ask_int(prompt: str, lo: int, hi: int, default: int) -> int:
    while True:
        try:
            raw = input(f"  {prompt} [{lo}–{hi}, default={default}]: ").strip()
            return int(raw) if raw else default
        except (ValueError, KeyboardInterrupt):
            return default


def _fmt_ts(ts: float) -> str:
    import time as _t
    t = _t.localtime(ts)
    return (f"{t.tm_year}-{t.tm_mon:02d}-{t.tm_mday:02d} "
            f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}")


def _print_cluster_table(clusters: List[EmotionalCluster]):
    print(f"\n  ── CLÚSTERES EMOCIONALES {'─' * 37}")
    hdr = (f"  {'ID':<12} {'Nombre':<24} {'Miemb':>5} "
           f"{'Coher':>6} {'V':>6} {'A':>5} {'Etapa':<10}")
    print(hdr)
    print("  " + "─" * 62)
    for c in sorted(clusters, key=lambda x: x.coherence, reverse=True)[:20]:
        print(f"  {c.cluster_id:<12} {c.name[:24]:<24} "
              f"{len(c.member_fids):>5} {c.coherence:>6.3f} "
              f"{c.centroid_valence:>+6.3f} {c.centroid_arousal:>5.3f} "
              f"{c.evolution_stage:<10}")
    if len(clusters) > 20:
        print(f"  … y {len(clusters)-20} clústeres más")
    print(f"  Total: {len(clusters)} clústeres")


def run_diagnostic():
    import traceback as _tb
    from memory import MemoryManager, _build_demo_memory, _EXPERIENCES

    print()
    print(_SEP2)
    print("  DIAGNÓSTICO — PERSISTENCIA Y RECONSTITUCIÓN DE IDENTIDAD")
    print("  Clústeres · Grafo · Continuidad del Yo · Despertar")
    print(_SEP2)

    print("\n  Configura la prueba:\n")
    n_cycles  = _ask_int("Ciclos de experiencia",        1, 80, 30)
    n_recalls = _ask_int("Reconstrucciones de recuerdo", 1, 15,  5)
    mem_dir   = input("  Directorio de memoria [default=memory]: ").strip() or "memory"

    print(f"\n  → {n_cycles} ciclos · {n_recalls} recalls · disco={mem_dir}\n")

    # ── [1] Gestor de memoria ─────────────────────────────────────────────
    print(_SEP)
    print("  [1/9] Inicializando memoria…")
    t0  = time.time()
    mgr = MemoryManager(decay_interval_s=5.0)
    _build_demo_memory(mgr)
    print(f"       ✓ {mgr._total_encoded} fragmentos base  "
          f"({(time.time()-t0)*1000:.1f} ms)")

    # ── [2] Motor de persistencia ─────────────────────────────────────────
    print(_SEP)
    print("  [2/9] Inicializando motor de persistencia…")
    t0   = time.time()
    pers = MemoryPersistence(mgr, base_dir=mem_dir, auto_save_interval_s=10.0)

    # Bootstrap del ser
    pers.save_bootstrap(
        identity={
            "name":         "ser_neuronal_v1",
            "created_at":   time.time(),
            "description":  "Ser con memoria híbrida emocional-instintiva",
            "memory_layers": [l.value for l in _LAYER_ORDER],
        },
        emotional_calibration={
            "valence_range":  [-1.0, 1.0],
            "arousal_range":  [0.0, 1.0],
            "positive_bias":  0.1,
            "self_threshold": 0.6,
        },
        instinct_weights={
            "survive": 1.0, "flee": 0.9, "feed": 0.7,
            "bond": 0.8, "explore": 0.75, "rest": 0.6,
            "defend": 0.85, "reproduce": 0.65,
        },
    )
    print(f"       ✓ Persistencia lista en '{mem_dir}/'  "
          f"({(time.time()-t0)*1000:.1f} ms)")

    # ── [3] Primera reconstitución (posible carga de sesión anterior) ─────
    print(_SEP)
    print("  [3/9] Intentando reconstitución desde disco (sesión anterior)…")
    t0     = time.time()
    result = pers.wake_up()
    print(f"       {result.summary()}  ({(time.time()-t0)*1000:.1f} ms)")
    for note in result.verification_notes:
        print(f"         {note}")

    # ── [4] Ciclos de experiencia ─────────────────────────────────────────
    print(_SEP)
    print(f"  [4/9] Simulando {n_cycles} ciclos de experiencia…")
    for i in range(n_cycles):
        if random.random() < 0.7:
            exp = random.choice(_EXPERIENCES)
            content, tags, mod, val, aro, inst = exp
            if random.random() < 0.15:
                val = min(1.0, val + 0.15)
                aro = min(1.0, aro + 0.10)
            fid = mgr.encode(content + f" [c{i}]", tags, mod,
                             val, aro, inst,
                             base_strength=random.uniform(0.3, 0.75))
            if fid:
                f = mgr.store.get(fid)
                if f:
                    pers.notify_fragment_changed(f)

        if i % 5  == 0:
            decay_r = mgr.decay_cycle(force=True)
            if decay_r.get("ascended", 0) > 0:
                for f in mgr.store.all_fragments():
                    if f.layer.value in ("consolidated", "self"):
                        pers.notify_layer_ascent(f, MemoryLayer.WORKING)

        if i % 10 == 0:
            con_r = mgr.consolidate(force=True)
            pers.save_cycle(force=True)

    print(f"       ✓ {mgr._total_encoded} fragmentos totales en memoria")

    # ── [5] Reconstrucciones ──────────────────────────────────────────────
    print(_SEP)
    print(f"  [5/9] Ejecutando {n_recalls} reconstrucciones de recuerdo…\n")
    cue_sets = [
        (["mar","niñez","asombro"],         0.85, 0.80, "explore"),
        (["miedo","peligro","cuerpo"],      -0.80, 0.92, "survive"),
        (["café","hogar","amor"],            0.82, 0.55, "bond"),
        (["lluvia","calma","tarde"],         0.65, 0.45, "rest"),
        (["logro","claridad","mente"],       0.70, 0.65, "explore"),
    ]
    for idx in range(n_recalls):
        cues, val, aro, inst = cue_sets[idx % len(cue_sets)]
        res = mgr.recall(cues, val, aro, inst)
        reached = "✓" if res["target_reached"] else "✗"
        print(f"  ── Recall #{idx+1:02d}  {reached}  "
              f"coh={res['coherence']:.3f}  cues={cues}")
        if res["fragments"]:
            top   = res["fragments"][0]
            f_obj = mgr.store.get(top[0])
            preview = (f_obj.content[:50] + "…") if f_obj else "?"
            print(f"     top: [{top[3]:<12}] act={top[1]:.3f}  '{preview}'")
        print()

    # ── [6] Clústeres emocionales ─────────────────────────────────────────
    print(_SEP)
    print("  [6/9] Actualizando y analizando clústeres emocionales…")
    all_frags = mgr.store.all_fragments()
    pers.clusters.update(all_frags)
    cluster_stats = pers.clusters.stats()
    print(f"       Total clústeres     : {cluster_stats['total_clusters']}")
    print(f"       Por etapa           : {cluster_stats['by_stage']}")
    print(f"       Miembros totales    : {cluster_stats['total_members']}")
    print(f"       Coherencia promedio : {cluster_stats['avg_coherence']:.4f}")
    _print_cluster_table(pers.clusters.get_all())

    # ── [7] Apagado (persistencia completa) ───────────────────────────────
    print(_SEP)
    print("  [7/9] Simulando apagado — persistencia completa al disco…")
    t0 = time.time()
    pers.go_to_sleep()
    disk_s = pers.disk_stats()
    print(f"       ✓ Persistido en {(time.time()-t0)*1000:.1f} ms")
    print(f"       Fragmentos SELF en disco   : "
          f"{disk_s['self_nucleus_lines']} conscientes + "
          f"{disk_s['self_shadow_lines']} sombra")
    print(f"       Consolidated en disco      : {disk_s['consolidated_frags']}")
    print(f"       Associative en disco       : {disk_s['associative_frags']}")
    print(f"       Clústeres en disco         : {disk_s['clusters_on_disk']}")
    print(f"       Aristas del grafo          : {disk_s['graph_edges']}")
    print(f"       Eventos de historia        : {disk_s['continuity_events']}")
    print(f"       Sesiones guardadas         : {disk_s['sessions']}")

    # ── [8] Reconstitución desde cero (simula nuevo hardware) ─────────────
    print(_SEP)
    print("  [8/9] Simulando reconstitución desde nuevo hardware…")
    print("       (creando nuevo MemoryManager vacío + cargando desde disco)")
    t0       = time.time()
    mgr2     = MemoryManager(decay_interval_s=5.0)
    pers2    = MemoryPersistence(mgr2, base_dir=mem_dir)
    result2  = pers2.wake_up()
    elapsed  = (time.time()-t0) * 1000
    print(f"\n       Resultado de reconstitución: {result2.summary()}")
    print(f"       Tiempo de reconstitución   : {elapsed:.1f} ms")
    print(f"       ¿Es continuo?              : "
          f"{'✓ SÍ' if result2.is_continuous() else '✗ NO'}")
    print(f"       Score de identidad         : "
          f"{result2.identity_score:.4f}  "
          f"{_bar(result2.identity_score, 14)}")
    if result2.last_sleep_ts:
        print(f"       Última vez dormido         : "
              f"{_fmt_ts(result2.last_sleep_ts)}")
    print()
    print("       Notas de verificación:")
    for note in result2.verification_notes:
        print(f"         {note}")

    # Comparar estado de memoria original vs reconstituida
    stats_orig  = mgr.get_status()["store"]
    stats_new   = mgr2.get_status()["store"]
    print(f"\n       Comparación de memoria:")
    print(f"         {'Capa':<16} {'Original':>10} {'Reconstituida':>14}")
    print(f"         {'─'*42}")
    for layer in ["self", "consolidated", "associative", "working", "ephemeral"]:
        orig_n = stats_orig["by_layer"].get(layer, 0)
        new_n  = stats_new["by_layer"].get(layer, 0)
        match  = "✓" if orig_n > 0 and new_n > 0 else \
                 "─" if orig_n == 0 and new_n == 0 else "~"
        print(f"         {layer:<16} {orig_n:>10} {new_n:>14} {match}")

    # ── [9] Estado completo del sistema ───────────────────────────────────
    print(_SEP)
    print("  [9/9] Estado completo del sistema\n")

    pers_s = pers.get_status()
    print("  ── MOTOR DE PERSISTENCIA ────────────────────────────────")
    print(f"    Directorio base    : {pers_s['base_dir']}")
    print(f"    Fragmentos escritos: {pers_s['total_written']}")
    print(f"    Fragmentos cargados: {pers_s['total_loaded']}")
    print(f"    Pendientes (dirty) : {pers_s['dirty_pending']}")
    print(f"    Duración sesión    : {pers_s['session_age_s']:.1f} s")

    print("\n  ── GRAFO DE RELACIONES ──────────────────────────────────")
    print(f"    Aristas totales    : {disk_s['graph_edges']}")
    print(f"    Clústeres en disco : {disk_s['clusters_on_disk']}")

    print("\n  ── HISTORIA DE CONTINUIDAD ──────────────────────────────")
    print(f"    Eventos totales    : {disk_s['continuity_events']}")
    print(f"    Sesiones guardadas : {disk_s['sessions']}")

    # Memoria en RAM (original)
    store_s = stats_orig
    print("\n  ── MEMORIA EN RAM ───────────────────────────────────────")
    total_f = max(1, store_s["total"])
    for layer, count in store_s["by_layer"].items():
        pct = count / total_f * 100
        print(f"    {layer:<15} {_bar(count/total_f)} "
              f"{count:>4} ({pct:>5.1f}%)")
    print(f"    Fuerza promedio    : {store_s['avg_strength']:.4f}  "
          f"{_bar(store_s['avg_strength'], 12)}")

    # Resumen ejecutivo
    print()
    print(_SEP2)
    print("  RESUMEN EJECUTIVO")
    print(_SEP2)

    continuity_ok = result2.is_continuous()
    health = "ÓPTIMO"  if result2.identity_score > 0.75 else \
             "ESTABLE" if result2.identity_score > 0.50 else \
             "FRAGMENTADO"

    print(f"  Estado de identidad     : {health}")
    print(f"  Score de reconstitución : {result2.identity_score:.4f}  "
          f"{_bar(result2.identity_score, 14)}")
    print(f"  Continuidad verificada  : {'✓ SÍ' if continuity_ok else '✗ NO'}")
    print(f"  Fragmentos en disco     :")
    print(f"    SELF       : {disk_s['self_nucleus_lines']}c + "
          f"{disk_s['self_shadow_lines']}s")
    print(f"    Consolidated: {disk_s['consolidated_frags']}")
    print(f"    Associative : {disk_s['associative_frags']}")
    print(f"  Clústeres emocionales   : "
          f"{cluster_stats['total_clusters']}  "
          f"(coherencia={cluster_stats['avg_coherence']:.3f})")
    print(f"  Historia de identidad   : "
          f"{disk_s['continuity_events']} eventos")
    print(f"  Sesiones guardadas      : {disk_s['sessions']}")
    print()
    print("  ✓ Sistema de persistencia e identidad listo")
    print("  ✓ El ser puede migrar de hardware manteniendo continuidad")
    print(_SEP2)
    print()

    return mgr, pers, result2


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import random
    random.seed(42)
    try:
        mgr, pers, reconstitution = run_diagnostic()
    except KeyboardInterrupt:
        print("\n  Diagnóstico interrumpido.")
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        traceback.print_exc()
