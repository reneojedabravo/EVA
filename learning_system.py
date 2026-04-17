# learning_system.py
"""
Sistema de Aprendizaje Cognitivo Integral — EVA aprende de todo.

EVA no aprende de una sola fuente. Aprende desde múltiples frentes
simultáneos, y sabe exactamente de dónde viene cada cosa que sabe:

  FUENTE_USUARIO      — lo que el usuario le dice o comparte
  FUENTE_EXPERIENCIA  — lo que vivió directamente (percepciones, ciclos)
  FUENTE_IMAGINACION  — lo que generó su motor de imaginación
  FUENTE_PENSAMIENTO  — lo que elaboró en pensamiento profundo
  FUENTE_REFLEXION    — lo que surgió al conectar lo anterior
  FUENTE_INTERNA      — lo que ya sabía y consolidó

La fuente nunca se borra del conocimiento. Un concepto aprendido por
imaginación sigue siendo imaginación, no verdad verificada. Un concepto
aprendido del usuario puede ser refutado. Un concepto construido por
pensamiento profundo tiene más peso que uno efímero.

Módulos principales:
  LanguageBuilder     — aprende a comunicarse desde cero, sin idioma previo
  ConceptBuilder      — construye una mente asociativa con grafos de conceptos
  LearningNetwork     — red neuronal de aprendizaje (animal + micelial + sinapsis)
  EmotionalWeighter   — todo lo aprendido tiene valencia emocional e instintiva
  MetaLearner         — aprende a aprender: detecta qué estrategias funcionan
  LearningSystem      — integrador principal

Integración completa:
  ─ memory.py + memory_persistence.py (persistir todo lo aprendido)
  ─ adaptive.py (emociones + instintos modulan qué se aprende)
  ─ background_thinking.py (pensamientos resueltos ingresan como conocimiento)
  ─ imagination.py (escenarios e insights ingresan como conocimiento imaginado)
  ─ mind.py (la mente percibe los resultados del aprendizaje)
  ─ neuronas animales + miceliales + SynapseManager
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
from threading import RLock, Thread, Event
from typing import Any, Dict, List, Optional, Set, Tuple

# ── Ecosistema ────────────────────────────────────────────────────────────────
from monitoring import log_event, log_neuron_error
from animal    import create_cognitive_animal_neuron,   CognitiveAnimalNeuronBase
from micelial  import create_cognitive_micelial_neuron, CognitiveMicelialNeuronBase
from synapse   import SynapseManager
from adaptive  import AdaptiveCore, EmotionEngine, InstinctCore, InstinctID
from memory    import (MemoryManager, EmotionalStamp, MemoryLayer,
                        Fragment, _build_demo_memory)
from memory_persistence import MemoryPersistence


# ═══════════════════════════════════════════════════════════════════════════════
#  FUENTE DE CONOCIMIENTO
# ═══════════════════════════════════════════════════════════════════════════════

class KnowledgeSource(Enum):
    USER        = "usuario"        # el usuario lo dijo
    EXPERIENCE  = "experiencia"    # vivido directamente
    IMAGINATION = "imaginacion"    # generado por imaginación
    THINKING    = "pensamiento"    # elaborado en background_thinking
    REFLECTION  = "reflexion"      # síntesis de múltiples fuentes
    INTERNAL    = "interno"        # consolidado previamente

# Peso de confianza base por fuente (puede cambiar con MetaLearner)
_SOURCE_TRUST: Dict[KnowledgeSource, float] = {
    KnowledgeSource.USER:        0.80,
    KnowledgeSource.EXPERIENCE:  0.90,
    KnowledgeSource.IMAGINATION: 0.45,
    KnowledgeSource.THINKING:    0.70,
    KnowledgeSource.REFLECTION:  0.75,
    KnowledgeSource.INTERNAL:    0.85,
}

# Qué capa de memoria recibe cada fuente por defecto
_SOURCE_LAYER: Dict[KnowledgeSource, MemoryLayer] = {
    KnowledgeSource.USER:        MemoryLayer.WORKING,
    KnowledgeSource.EXPERIENCE:  MemoryLayer.ASSOCIATIVE,
    KnowledgeSource.IMAGINATION: MemoryLayer.WORKING,
    KnowledgeSource.THINKING:    MemoryLayer.ASSOCIATIVE,
    KnowledgeSource.REFLECTION:  MemoryLayer.CONSOLIDATED,
    KnowledgeSource.INTERNAL:    MemoryLayer.CONSOLIDATED,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  UNIDAD DE CONOCIMIENTO
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KnowledgeUnit:
    """Una unidad de conocimiento con toda su metadata.

    No es solo texto — lleva su historia: de dónde vino, cómo llegó,
    qué emoción lo tiñó, qué instinto lo amplificó.
    """
    uid:         str
    content:     str
    tags:        List[str]
    source:      KnowledgeSource
    language:    str           # código de idioma detectado o "unknown"
    valence:     float         # −1..+1 carga emocional
    arousal:     float         # 0..1
    instincts:   List[str]     # instintos activos al aprenderlo
    trust:       float         # 0..1 confianza en esta unidad
    importance:  float         # 0..1 importancia calculada
    domain:      str           # dominio conceptual
    concepts:    List[str]     # conceptos extraídos
    relations:   List[str]     # UIDs relacionados
    fid:         Optional[str] = None   # FID en MemoryManager
    creation_ts: float         = field(default_factory=time.time)
    access_count: int          = 0
    reinforced:  int           = 0     # veces que fue confirmado/reforzado

    def emotional_stamp(self) -> EmotionalStamp:
        return EmotionalStamp(
            valence=self.valence,
            arousal=self.arousal,
            instinct_tags=self.instincts,
        )

    def to_dict(self) -> Dict:
        return {
            "uid":         self.uid,
            "content":     self.content[:200],
            "tags":        self.tags,
            "source":      self.source.value,
            "language":    self.language,
            "valence":     round(self.valence, 4),
            "arousal":     round(self.arousal, 4),
            "instincts":   self.instincts,
            "trust":       round(self.trust, 4),
            "importance":  round(self.importance, 4),
            "domain":      self.domain,
            "concepts":    self.concepts,
            "relations":   self.relations,
            "fid":         self.fid,
            "creation_ts": self.creation_ts,
            "reinforced":  self.reinforced,
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTRUCTOR DE IDIOMA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LexicalEntry:
    """Entrada léxica: una forma con sus significados posibles."""
    form:       str            # forma superficial (token)
    language:   str            # idioma detectado
    frequency:  int    = 1
    contexts:   List[str] = field(default_factory=list)   # contextos donde apareció
    co_forms:   Dict[str, int] = field(default_factory=dict)  # formas co-ocurrentes
    meanings:   List[str] = field(default_factory=list)   # significados asociados
    last_seen:  float    = field(default_factory=time.time)


# Señales para detección de idioma (patrones frecuentes)
_LANG_SIGNALS: Dict[str, List[str]] = {
    "es": ["el", "la", "los", "las", "de", "que", "en", "un", "una",
           "es", "con", "para", "por", "como", "pero", "más", "ya"],
    "en": ["the", "is", "are", "was", "be", "to", "of", "and", "a",
           "in", "that", "have", "it", "for", "not", "on", "with"],
    "fr": ["le", "la", "les", "de", "du", "des", "que", "est", "un",
           "une", "dans", "pour", "sur", "avec", "par", "mais"],
    "pt": ["o", "a", "os", "as", "de", "que", "em", "um", "uma",
           "é", "com", "para", "por", "como", "mas", "mais", "já"],
    "de": ["der", "die", "das", "den", "dem", "ein", "eine", "ist",
           "und", "in", "für", "von", "mit", "auf", "sich", "nicht"],
}

# Patrones de script para detectar idiomas no latinos
_SCRIPT_PATTERNS: Dict[str, str] = {
    "zh": r'[\u4e00-\u9fff]',
    "ja": r'[\u3040-\u30ff]',
    "ko": r'[\uac00-\ud7af]',
    "ar": r'[\u0600-\u06ff]',
    "ru": r'[\u0400-\u04ff]',
    "hi": r'[\u0900-\u097f]',
}


class LanguageBuilder:
    """Constructor de idioma — aprende a comunicarse desde cero.

    No parte de reglas gramaticales predefinidas.
    Observa señales, detecta patrones, construye un léxico asociativo.
    Puede trabajar con cualquier idioma incluyendo idiomas desconocidos.

    El idioma se detecta estadísticamente. Si no puede detectarlo,
    lo trata como "unknown" y sigue construyendo su modelo.
    """

    def __init__(self):
        self._lock     = RLock()
        self._lexicon: Dict[str, LexicalEntry] = {}  # form → entry
        self._lang_stats: Dict[str, int] = defaultdict(int)
        self._bigrams:    Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int))  # form → {next_form: count}
        self._trigrams:   Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int))
        self._sentences:  deque = deque(maxlen=500)
        self._total_tokens = 0
        self._dominant_lang = "unknown"

    def ingest(self, text: str, context: str = "") -> Dict[str, Any]:
        """Ingesta texto en cualquier idioma y actualiza el modelo léxico."""
        with self._lock:
            lang = self._detect_language(text)
            tokens = self._tokenize(text, lang)
            self._update_lexicon(tokens, lang, context)
            self._update_ngrams(tokens)
            self._update_lang_stats(lang, len(tokens))
            self._sentences.append({"text": text[:120], "lang": lang, "ts": time.time()})
            self._total_tokens += len(tokens)
            return {
                "language":    lang,
                "tokens":      len(tokens),
                "new_forms":   self._count_new_forms(tokens),
                "lexicon_size":len(self._lexicon),
            }

    def _detect_language(self, text: str) -> str:
        """Detecta idioma por scripts no-latinos y por señales léxicas."""
        # Primero: scripts no-latinos
        for lang, pattern in _SCRIPT_PATTERNS.items():
            if re.search(pattern, text):
                return lang
        # Segundo: señales léxicas
        text_lower = text.lower()
        tokens = set(re.findall(r'\b\w+\b', text_lower))
        scores: Dict[str, int] = {}
        for lang, signals in _LANG_SIGNALS.items():
            scores[lang] = sum(1 for s in signals if s in tokens)
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        # Tercero: usar dominante conocido
        if self._dominant_lang != "unknown":
            return self._dominant_lang
        return "unknown"

    def _tokenize(self, text: str, lang: str) -> List[str]:
        """Tokeniza respetando el idioma."""
        # Para scripts CJK: tokenizar por caracter/carácter
        if lang in ("zh", "ja", "ko"):
            return list(re.findall(r'\S', text))[:200]
        # Para árabe/hindi/ruso: palabras completas
        if lang in ("ar", "hi", "ru"):
            return re.findall(r'\b\w+\b', text)[:200]
        # Para lenguas latinas: palabras 2+ chars
        return re.findall(r'\b\w{2,}\b', text.lower())[:200]

    def _update_lexicon(self, tokens: List[str], lang: str, ctx: str):
        now = time.time()
        for tok in tokens:
            if tok not in self._lexicon:
                self._lexicon[tok] = LexicalEntry(
                    form=tok, language=lang)
            entry = self._lexicon[tok]
            entry.frequency += 1
            entry.last_seen  = now
            if ctx and ctx not in entry.contexts:
                entry.contexts.append(ctx[:30])
            # Co-formas (co-ocurrentes directos)
            for other in tokens:
                if other != tok:
                    entry.co_forms[other] = entry.co_forms.get(other, 0) + 1

    def _update_ngrams(self, tokens: List[str]):
        for i in range(len(tokens) - 1):
            self._bigrams[tokens[i]][tokens[i+1]] += 1
        for i in range(len(tokens) - 2):
            key = f"{tokens[i]}_{tokens[i+1]}"
            self._trigrams[key][tokens[i+2]] += 1

    def _update_lang_stats(self, lang: str, n_tokens: int):
        self._lang_stats[lang] += n_tokens
        total = sum(self._lang_stats.values())
        if total > 0:
            self._dominant_lang = max(
                self._lang_stats, key=self._lang_stats.get)

    def _count_new_forms(self, tokens: List[str]) -> int:
        return sum(1 for t in tokens if self._lexicon.get(t, None) and
                   self._lexicon[t].frequency == 1)

    def predict_next(self, form: str, n: int = 3) -> List[Tuple[str, float]]:
        """Predice las formas más probables después de 'form'."""
        with self._lock:
            candidates = self._bigrams.get(form, {})
            total = sum(candidates.values()) or 1
            return sorted(
                [(f, c/total) for f, c in candidates.items()],
                key=lambda x: x[1], reverse=True)[:n]

    def get_related_forms(self, form: str, n: int = 5) -> List[Tuple[str, int]]:
        """Retorna formas co-ocurrentes más frecuentes."""
        with self._lock:
            entry = self._lexicon.get(form)
            if not entry:
                return []
            return sorted(entry.co_forms.items(),
                          key=lambda x: x[1], reverse=True)[:n]

    def get_status(self) -> Dict:
        with self._lock:
            return {
                "lexicon_size":   len(self._lexicon),
                "total_tokens":   self._total_tokens,
                "dominant_lang":  self._dominant_lang,
                "languages_seen": dict(self._lang_stats),
                "bigram_keys":    len(self._bigrams),
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTRUCTOR DE CONCEPTOS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Concept:
    """Un concepto en la mente asociativa de EVA."""
    cid:          str
    name:         str
    domain:       str
    tags:         List[str]
    valence:      float        # carga emocional del concepto
    arousal:      float
    source:       KnowledgeSource
    strength:     float        # qué tan consolidado está
    connections:  Dict[str, float]  # cid → peso de asociación
    examples:     List[str]    # instancias concretas
    creation_ts:  float = field(default_factory=time.time)
    last_activated: float = field(default_factory=time.time)
    activation:   float   = 0.5

    def decay(self, rate: float = 0.02):
        self.activation = max(0.0, self.activation * (1.0 - rate))
        self.strength   = max(0.01, self.strength   * (1.0 - rate * 0.1))


class ConceptBuilder:
    """Constructor de mente asociativa.

    Construye un grafo de conceptos donde las conexiones tienen peso
    emocional, fuente y dirección. Un concepto no es solo una palabra —
    es un nodo vivo con activación, historia y relaciones.

    La mente asociativa permite que un concepto active a los relacionados,
    que una emoción active toda una red de conceptos vinculados con esa
    emoción, y que los instintos activos prioricen ciertos conceptos.
    """

    def __init__(self):
        self._lock     = RLock()
        self._concepts: Dict[str, Concept] = {}   # cid → Concept
        self._name_idx: Dict[str, str]     = {}   # name → cid
        self._domain_idx: Dict[str, List[str]] = defaultdict(list)  # domain → [cid]
        self._total_connections = 0

    def add_or_update(self, name: str, domain: str, tags: List[str],
                       valence: float, arousal: float,
                       source: KnowledgeSource,
                       examples: List[str] = None) -> Concept:
        """Añade un concepto nuevo o refuerza uno existente."""
        with self._lock:
            name_clean = name.strip().lower()[:40]
            cid = self._name_idx.get(name_clean)

            if cid and cid in self._concepts:
                c = self._concepts[cid]
                # Reforzar: promediar valencia y arousal
                c.valence    = c.valence * 0.7 + valence * 0.3
                c.arousal    = c.arousal * 0.7 + arousal * 0.3
                c.strength   = min(1.0, c.strength + 0.05)
                c.activation = min(1.0, c.activation + 0.15)
                c.last_activated = time.time()
                for ex in (examples or []):
                    if ex not in c.examples:
                        c.examples.append(ex[:60])
                return c

            cid = hashlib.md5(
                f"{name_clean}{time.time()}".encode()).hexdigest()[:10]
            c = Concept(
                cid=cid, name=name_clean, domain=domain,
                tags=tags, valence=valence, arousal=arousal,
                source=source, strength=0.3,
                connections={}, examples=(examples or [])[:5],
            )
            self._concepts[cid] = c
            self._name_idx[name_clean] = cid
            self._domain_idx[domain].append(cid)
            return c

    def connect(self, name_a: str, name_b: str,
                weight: float = 0.5, bidirectional: bool = True):
        """Crea o refuerza una conexión entre dos conceptos."""
        with self._lock:
            cid_a = self._name_idx.get(name_a.strip().lower())
            cid_b = self._name_idx.get(name_b.strip().lower())
            if not cid_a or not cid_b or cid_a == cid_b:
                return
            c_a = self._concepts[cid_a]
            c_b = self._concepts[cid_b]
            prev_ab = c_a.connections.get(cid_b, 0.0)
            c_a.connections[cid_b] = min(1.0, prev_ab + weight * 0.3)
            if bidirectional:
                prev_ba = c_b.connections.get(cid_a, 0.0)
                c_b.connections[cid_a] = min(1.0, prev_ba + weight * 0.2)
            self._total_connections += 1

    def activate(self, name: str, signal: float = 0.6,
                 spread: bool = True) -> List[Concept]:
        """Activa un concepto y lo propaga por sus conexiones."""
        with self._lock:
            cid = self._name_idx.get(name.strip().lower())
            if not cid:
                return []
            c = self._concepts[cid]
            c.activation = min(1.0, c.activation + signal)
            c.last_activated = time.time()
            activated = [c]
            if spread:
                for conn_cid, weight in sorted(
                        c.connections.items(),
                        key=lambda x: x[1], reverse=True)[:4]:
                    if conn_cid in self._concepts:
                        neighbor = self._concepts[conn_cid]
                        neighbor.activation = min(
                            1.0, neighbor.activation + signal * weight * 0.5)
                        activated.append(neighbor)
            return activated

    def search_by_valence(self, target: float,
                           tol: float = 0.3, n: int = 6) -> List[Concept]:
        """Busca conceptos con valencia cercana al objetivo."""
        with self._lock:
            return sorted(
                [c for c in self._concepts.values()
                 if abs(c.valence - target) <= tol],
                key=lambda c: c.strength * c.activation,
                reverse=True)[:n]

    def search_by_domain(self, domain: str, n: int = 8) -> List[Concept]:
        with self._lock:
            cids = self._domain_idx.get(domain, [])
            return [self._concepts[cid] for cid in cids[:n]
                    if cid in self._concepts]

    def decay_all(self, rate: float = 0.02):
        with self._lock:
            for c in self._concepts.values():
                c.decay(rate)

    def get_status(self) -> Dict:
        with self._lock:
            domains = {d: len(cids) for d, cids in self._domain_idx.items()}
            avg_str  = (sum(c.strength for c in self._concepts.values()) /
                        max(1, len(self._concepts)))
            return {
                "total_concepts":     len(self._concepts),
                "total_connections":  self._total_connections,
                "domains":            domains,
                "avg_strength":       round(avg_str, 4),
                "top_activated":      [
                    {"name": c.name, "act": round(c.activation, 3),
                     "domain": c.domain}
                    for c in sorted(
                        self._concepts.values(),
                        key=lambda x: x.activation, reverse=True)[:5]
                ],
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  PESADOR EMOCIONAL
# ═══════════════════════════════════════════════════════════════════════════════

# Palabras con carga emocional (multilingüe básico)
_EMO_POSITIVE = {
    "es": ["feliz","alegre","amor","paz","bien","bueno","éxito","logro","bello",
           "hermoso","esperanza","confianza","calma","luz","vida","gratitud"],
    "en": ["happy","joy","love","peace","good","success","beautiful","hope",
           "trust","calm","light","life","grateful","wonderful","amazing"],
    "fr": ["heureux","amour","paix","bien","beau","espoir","confiance","lumière"],
    "pt": ["feliz","amor","paz","bem","belo","esperança","confiança","luz"],
    "de": ["glücklich","liebe","frieden","gut","schön","hoffnung","vertrauen"],
}
_EMO_NEGATIVE = {
    "es": ["miedo","dolor","triste","malo","error","fracaso","odio","angustia",
           "conflicto","problema","oscuridad","pérdida","muerte","amenaza"],
    "en": ["fear","pain","sad","bad","error","failure","hate","anxiety",
           "conflict","problem","darkness","loss","death","threat"],
    "fr": ["peur","douleur","triste","mal","erreur","échec","haine","anxiété"],
    "pt": ["medo","dor","triste","mal","erro","fracasso","ódio","ansiedade"],
    "de": ["angst","schmerz","traurig","schlecht","fehler","hass","dunkelheit"],
}

# Palabras relacionadas con instintos
_INSTINCT_WORDS: Dict[str, List[str]] = {
    "survive":  ["peligro","amenaza","huir","daño","danger","threat","harm"],
    "explore":  ["curioso","nuevo","descubrir","curious","new","discover","unknown"],
    "bond":     ["conexión","amistad","amor","juntos","connection","friend","love"],
    "feed":     ["necesito","falta","hambre","recurso","need","lack","resource"],
    "rest":     ["calma","descanso","paz","silencio","calm","rest","peace","quiet"],
    "defend":   ["proteger","barrera","guardar","protect","guard","shield"],
    "reproduce":["crear","innovar","generar","create","innovate","generate"],
}


class EmotionalWeighter:
    """Calcula el peso emocional de cualquier texto en cualquier idioma."""

    def __init__(self, language_builder: LanguageBuilder):
        self._lang = language_builder

    def weigh(self, text: str, source: KnowledgeSource,
              emotion_engine: EmotionEngine,
              instinct_core:  InstinctCore) -> Tuple[float, float, List[str]]:
        """Retorna (valence, arousal, instinct_tags) para un texto."""
        lang  = self._lang._detect_language(text)
        tokens = set(text.lower().split())

        # Puntuación léxica emocional
        pos_words = _EMO_POSITIVE.get(lang, _EMO_POSITIVE["en"])
        neg_words = _EMO_NEGATIVE.get(lang, _EMO_NEGATIVE["en"])
        pos_count = sum(1 for w in pos_words if w in tokens)
        neg_count = sum(1 for w in neg_words if w in tokens)
        total = max(1, pos_count + neg_count)
        lex_valence = (pos_count - neg_count) / total

        # Modular con emoción actual del sistema
        sys_valence = emotion_engine.valence
        valence = lex_valence * 0.6 + sys_valence * 0.4

        # Arousal: intensidad del texto + arousal del sistema
        intensity_words = (pos_count + neg_count) / max(10, len(tokens)) * 2
        arousal = min(1.0, intensity_words * 0.5 + emotion_engine.arousal * 0.5)

        # Fuentes más confiables tienen mayor arousal
        if source in (KnowledgeSource.EXPERIENCE, KnowledgeSource.USER):
            arousal = min(1.0, arousal + 0.1)

        # Detectar instintos activos + textuales
        inst_tags: List[str] = []
        active_insts = [i.value for i in instinct_core.get_active()]
        inst_tags.extend(active_insts)
        for inst, words_list in _INSTINCT_WORDS.items():
            if any(w in tokens for w in words_list):
                if inst not in inst_tags:
                    inst_tags.append(inst)

        return (
            round(max(-1.0, min(1.0, valence)), 4),
            round(max(0.0,  min(1.0, arousal)), 4),
            inst_tags,
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  META-APRENDIZAJE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LearningStrategy:
    """Una estrategia de aprendizaje con su historial de rendimiento."""
    name:         str
    description:  str
    success_rate: float = 0.5
    uses:         int   = 0
    last_used:    float = field(default_factory=time.time)

    def update(self, success: bool):
        self.uses += 1
        alpha = 0.15
        self.success_rate = (self.success_rate * (1 - alpha) +
                             (1.0 if success else 0.0) * alpha)
        self.last_used = time.time()


class MetaLearner:
    """EVA aprende a aprender.

    Observa qué estrategias producen conocimiento más consolidado,
    qué fuentes son más confiables, y adapta sus parámetros en consecuencia.
    """

    def __init__(self):
        self._lock = RLock()
        self._strategies: Dict[str, LearningStrategy] = {
            "repetition":    LearningStrategy("repetition",
                "Aprender por repetición espaciada"),
            "association":   LearningStrategy("association",
                "Aprender conectando con lo conocido"),
            "emotional":     LearningStrategy("emotional",
                "Aprender anclando a emoción intensa"),
            "contextual":    LearningStrategy("contextual",
                "Aprender en contexto rico"),
            "questioning":   LearningStrategy("questioning",
                "Aprender cuestionando lo recibido"),
            "synthesis":     LearningStrategy("synthesis",
                "Aprender sintetizando múltiples fuentes"),
        }
        self._source_trust: Dict[str, float] = {
            s.value: v for s, v in _SOURCE_TRUST.items()}
        self._consolidation_log: deque = deque(maxlen=200)

    def select_strategy(self, source: KnowledgeSource,
                         valence: float, arousal: float) -> str:
        """Selecciona la mejor estrategia para el input actual."""
        with self._lock:
            # Alta arousal + emoción intensa → anclar emocionalmente
            if abs(valence) > 0.6 and arousal > 0.65:
                return "emotional"
            # Fuente usuario → cuestionar y contextualizar
            if source == KnowledgeSource.USER:
                return "contextual"
            # Fuente imaginación → síntesis
            if source == KnowledgeSource.IMAGINATION:
                return "synthesis"
            # Fuente pensamiento → asociación
            if source == KnowledgeSource.THINKING:
                return "association"
            # Default: la estrategia con mayor success_rate activo
            best = max(self._strategies.values(),
                       key=lambda s: s.success_rate)
            return best.name

    def record_outcome(self, strategy: str, consolidated: bool,
                        source: KnowledgeSource):
        """Registra el resultado de una estrategia."""
        with self._lock:
            if strategy in self._strategies:
                self._strategies[strategy].update(consolidated)
            # Actualizar confianza en la fuente
            src_name = source.value
            old_trust = self._source_trust.get(src_name, 0.5)
            alpha = 0.05
            new_trust = old_trust * (1 - alpha) + (0.9 if consolidated else 0.3) * alpha
            self._source_trust[src_name] = round(new_trust, 4)
            self._consolidation_log.append({
                "ts": time.time(), "strategy": strategy,
                "source": src_name, "consolidated": consolidated,
            })

    def get_source_trust(self, source: KnowledgeSource) -> float:
        with self._lock:
            return self._source_trust.get(source.value, 0.5)

    def get_status(self) -> Dict:
        with self._lock:
            return {
                "strategies": {
                    name: {"rate": round(s.success_rate, 3), "uses": s.uses}
                    for name, s in self._strategies.items()
                },
                "source_trust": dict(self._source_trust),
                "consolidations_logged": len(self._consolidation_log),
                "best_strategy": max(
                    self._strategies, key=lambda n: self._strategies[n].success_rate),
            }


# ═══════════════════════════════════════════════════════════════════════════════
#  RED NEURONAL DE APRENDIZAJE
# ═══════════════════════════════════════════════════════════════════════════════

_LEARN_ANIMAL = [
    ("anomaly_detector",          {}),
    ("risk_assessor",             {}),
    ("decision_maker",            {}),
    ("dopaminergic_modulator",    {}),
    ("mirror_neuron",             {"action_class": "learn"}),
    ("adaptive_threshold_cell",   {}),
    ("pattern_recognizer",        {}),
    ("self_monitor",              {}),
    ("receptive_field_cell",      {"polarity": "ON"}),
    ("speed_neuron",              {}),
]

_LEARN_MICELIAL = [
    ("abstract_pattern_integrator",    {}),
    ("knowledge_synthesizer",          {"domain_specializations":
                                         ["learning","language","concepts"]}),
    ("conceptual_bridge_builder",      {}),
    ("insight_propagator",             {}),
    ("global_coherence_coordinator",   {}),
    ("anastomosis_node",               {}),
    ("quorum_sensing_node",            {}),
    ("glycolytic_oscillator",          {}),
    ("plasmodium_collector",           {}),
    ("deep_reflection_orchestrator",   {}),
]


class LearningNetwork:
    """Red neuronal dedicada al procesamiento de aprendizaje."""

    def __init__(self, syn_mgr: SynapseManager,
                 n_animal: int = 5, n_micelial: int = 5):
        self.animals:   List[CognitiveAnimalNeuronBase]   = []
        self.micelials: List[CognitiveMicelialNeuronBase] = []
        self.syn_mgr    = syn_mgr
        self._build(min(n_animal,  len(_LEARN_ANIMAL)),
                    min(n_micelial, len(_LEARN_MICELIAL)))

    def _build(self, na: int, nm: int):
        for i in range(na):
            ntype, kwargs = _LEARN_ANIMAL[i]
            nid = f"LRN_A{i+1:02d}_{ntype[:8]}"
            try:
                n = create_cognitive_animal_neuron(ntype, nid, **kwargs)
                self.animals.append(n)
            except Exception as e:
                log_neuron_error(nid, f"LearningNetwork animal: {e}")

        for i in range(nm):
            ntype, kwargs = _LEARN_MICELIAL[i]
            nid = f"LRN_M{i+1:02d}_{ntype[:8]}"
            try:
                n = create_cognitive_micelial_neuron(ntype, nid, **kwargs)
                self.micelials.append(n)
            except Exception as e:
                log_neuron_error(nid, f"LearningNetwork micelial: {e}")

        # Conexiones
        for i in range(len(self.animals) - 1):
            self.syn_mgr.connect(self.animals[i], self.animals[i+1],
                                 "electrical", "excitatory", persistent=True)
        for i in range(len(self.micelials) - 1):
            self.syn_mgr.connect(self.micelials[i], self.micelials[i+1],
                                 "chemical", "excitatory", persistent=True)
        n_cross = min(4, len(self.animals), len(self.micelials))
        for i in range(n_cross):
            self.syn_mgr.connect(self.animals[i], self.micelials[i],
                                 "hybrid", "excitatory", persistent=True)
            self.syn_mgr.connect(self.micelials[i], self.animals[i],
                                 "hybrid", "modulatory", persistent=False)
        if len(self.animals) >= 3 and self.micelials:
            self.syn_mgr.create_parallel_bundle(
                self.animals[:3], self.micelials[0], "hybrid")
        if len(self.animals) >= 2 and self.micelials:
            self.syn_mgr.create_serial_chain(
                [self.animals[0], self.animals[1], self.micelials[0]])

    def process(self, signal: float, context: Dict) -> Tuple[float, float, int]:
        """Procesa señal de aprendizaje. Retorna (animal_avg, micelial_avg, syn_tx)."""
        a_acts, m_acts = [], []
        ctx = {**context, "pattern": "learning_pass"}

        for n in self.animals:
            try:
                act = n.receive_signal(
                    signal, context.get("source","learn"), ctx)
                if act:
                    a_acts.append(float(act))
            except Exception:
                pass

        concept = context.get("domain", "concepto")
        for n in self.micelials:
            try:
                act = n.receive_concept(signal, concept, ctx)
                if act:
                    m_acts.append(float(act))
            except Exception:
                pass

        tx = 0
        for syn in list(self.syn_mgr.synapses.values()):
            try:
                out = syn.transmit(signal, ctx)
                if out and out > 0.01:
                    tx += 1
            except Exception:
                pass

        a_avg = sum(a_acts) / max(1, len(a_acts)) if a_acts else 0.0
        m_avg = sum(m_acts) / max(1, len(m_acts)) if m_acts else 0.0
        return a_avg, m_avg, tx

    def get_status(self) -> Dict:
        syn_s = self.syn_mgr.get_stats()
        return {
            "animals":         len(self.animals),
            "micelials":       len(self.micelials),
            "total_synapses":  syn_s["total_synapses"],
            "active_synapses": syn_s["active_synapses"],
            "by_kind":         syn_s["by_kind"],
            "avg_weight":      syn_s["avg_weight"],
            "avg_utility":     syn_s["avg_utility"],
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
#  SISTEMA DE APRENDIZAJE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

class LearningSystem:
    """Sistema de Aprendizaje Cognitivo Integral.

    EVA aprende de todo, sabe de dónde viene cada cosa que sabe,
    y va mejorando en cómo aprende con el tiempo.
    """

    def __init__(self, memory_dir:   str   = "memory",
                 n_animal:     int   = 5,
                 n_micelial:   int   = 5,
                 fluid_mind    = None,
                 bg_thinker    = None,
                 imagination   = None):

        self._lock    = RLock()

        # ── Motores de apoyo ──────────────────────────────────────────────
        self.adaptive    = AdaptiveCore(n_animal=0, n_micelial=0)
        self.memory_mgr  = MemoryManager(decay_interval_s=30.0)
        self.persistence = MemoryPersistence(
            self.memory_mgr, base_dir=memory_dir,
            auto_save_interval_s=60.0)

        # ── Red neuronal ──────────────────────────────────────────────────
        self.syn_mgr = SynapseManager(
            prune_interval_s  = 60.0,
            utility_threshold = 0.08,
            error_rate_max    = 0.75,
            inactivity_secs   = 120.0,
        )
        self.network = LearningNetwork(self.syn_mgr, n_animal, n_micelial)

        # ── Submódulos ────────────────────────────────────────────────────
        self.language_builder = LanguageBuilder()
        self.concept_builder  = ConceptBuilder()
        self.emotional_weighter = EmotionalWeighter(self.language_builder)
        self.meta_learner     = MetaLearner()

        # ── Referencias opcionales ────────────────────────────────────────
        self.fluid_mind  = fluid_mind
        self.bg_thinker  = bg_thinker
        self.imagination = imagination

        # ── Estado ────────────────────────────────────────────────────────
        self._units:    Dict[str, KnowledgeUnit] = {}  # uid → unit
        self._by_source: Dict[str, List[str]]    = defaultdict(list)
        self._by_domain: Dict[str, List[str]]    = defaultdict(list)
        self._total_learned  = 0
        self._total_consolidated = 0
        self._cycle = 0

        # ── Disco ─────────────────────────────────────────────────────────
        self._base_dir = Path(memory_dir) / "learning"
        self._base_dir.mkdir(parents=True, exist_ok=True)
        (self._base_dir / "units").mkdir(exist_ok=True)
        (self._base_dir / "concepts").mkdir(exist_ok=True)

        # Cargar experiencias de demostración en memoria
        _build_demo_memory(self.memory_mgr)

        log_event("LearningSystem inicializado", "INFO")

    # ═════════════════════════════════════════════════════════════════════
    #  API PRINCIPAL
    # ═════════════════════════════════════════════════════════════════════

    def learn(self, content: str,
              source: KnowledgeSource = KnowledgeSource.USER,
              tags:   List[str]  = None,
              domain: str        = "",
              context: Dict      = None) -> KnowledgeUnit:
        """Punto de entrada principal: aprende algo de una fuente específica."""
        self._cycle += 1
        tags = tags or []

        # 1. Ingestar en el constructor de idioma
        lang_result = self.language_builder.ingest(content, context=domain or source.value)
        lang = lang_result["language"]

        # 2. Calcular peso emocional
        valence, arousal, inst_tags = self.emotional_weighter.weigh(
            content, source,
            self.adaptive.emotions, self.adaptive.instincts)

        # 3. Actualizar estado adaptativo
        self.adaptive.run_cycle(
            stimulus = content,
            threat   = max(0.0, -valence * arousal),
            energy   = 0.6 + valence * 0.15,
            novelty  = arousal * 0.4,
        )

        # 4. Detectar dominio si no viene dado
        if not domain:
            domain = self._detect_domain(content, lang)

        # 5. Extraer conceptos
        concepts = self._extract_concepts(content, lang)

        # 6. Calcular importancia
        trust_base = self.meta_learner.get_source_trust(source)
        importance = self._compute_importance(
            content, valence, arousal, source, trust_base, concepts)

        # 7. Seleccionar estrategia de aprendizaje
        strategy = self.meta_learner.select_strategy(source, valence, arousal)

        # 8. Activar red neuronal
        signal = 0.4 + importance * 0.5 + arousal * 0.1
        ctx = {
            "source":        source.value,
            "domain":        domain,
            "language":      lang,
            "neuromodulator":self.adaptive.emotions.get_summary()["neuromod"],
            "nm_level":      arousal,
            "strategy":      strategy,
        }
        a_act, m_act, syn_tx = self.network.process(signal, ctx)
        neural_sig = a_act * 0.4 + m_act * 0.6

        # 9. Determinar capa de memoria
        base_layer = _SOURCE_LAYER[source]
        if importance > 0.75 and abs(valence) > 0.5:
            forced_layer = MemoryLayer.CONSOLIDATED
        elif importance > 0.55:
            forced_layer = MemoryLayer.ASSOCIATIVE
        else:
            forced_layer = base_layer

        # 10. Guardar en memoria
        fid = self.memory_mgr.encode(
            content      = content,
            tags         = tags + [source.value, domain] + concepts[:2],
            modality     = "conceptual",
            valence      = valence,
            arousal      = arousal,
            instinct_tags= inst_tags,
            base_strength= importance,
            forced_layer = forced_layer,
        )
        if fid:
            f = self.memory_mgr.store.get(fid)
            if f:
                self.persistence.notify_fragment_changed(f)
                if forced_layer in (MemoryLayer.CONSOLIDATED,
                                     MemoryLayer.SELF):
                    self.persistence.notify_layer_ascent(f, base_layer)

        # 11. Crear unidad de conocimiento
        uid = hashlib.md5(
            f"{content[:40]}{time.time()}".encode()).hexdigest()[:12]
        unit = KnowledgeUnit(
            uid         = uid,
            content     = content,
            tags        = tags,
            source      = source,
            language    = lang,
            valence     = valence,
            arousal     = arousal,
            instincts   = inst_tags,
            trust       = trust_base,
            importance  = importance,
            domain      = domain,
            concepts    = concepts,
            relations   = [],
            fid         = fid,
        )
        with self._lock:
            self._units[uid] = unit
            self._by_source[source.value].append(uid)
            self._by_domain[domain].append(uid)
            self._total_learned += 1

        # 12. Actualizar grafo de conceptos
        for concept_name in concepts:
            c = self.concept_builder.add_or_update(
                concept_name, domain, tags + [source.value],
                valence, arousal, source, [content[:60]])
        # Conectar conceptos entre sí
        if len(concepts) >= 2:
            for i in range(len(concepts) - 1):
                self.concept_builder.connect(
                    concepts[i], concepts[i+1],
                    weight=importance * 0.5)

        # 13. Meta-aprendizaje: registrar resultado
        consolidated = forced_layer in (MemoryLayer.CONSOLIDATED,
                                         MemoryLayer.SELF)
        self.meta_learner.record_outcome(strategy, consolidated, source)
        if consolidated:
            self._total_consolidated += 1

        # 14. Salvar unidad en disco
        self._save_unit(unit)

        # 15. Persistencia periódica
        if self._cycle % 10 == 0:
            self.memory_mgr.decay_cycle(force=True)
            self.memory_mgr.consolidate(force=True)
            self.persistence.save_cycle(force=True)
            self.syn_mgr.prune()
            self.concept_builder.decay_all(rate=0.01)

        return unit

    def learn_from_thought(self, thought_content: str,
                            conclusion: str = "",
                            tags: List[str] = None) -> KnowledgeUnit:
        """Aprende desde un pensamiento resuelto en background_thinking."""
        content = conclusion if conclusion else thought_content
        return self.learn(content,
                          source=KnowledgeSource.THINKING,
                          tags=(tags or []) + ["pensamiento_profundo"],
                          domain="reflexion")

    def learn_from_imagination(self, scenario_content: str,
                                insight: str = "",
                                tags: List[str] = None) -> KnowledgeUnit:
        """Aprende desde un escenario o insight imaginado.
        EVA SABE que es imaginación — no es verdad verificada."""
        content = insight if insight else scenario_content
        return self.learn(content,
                          source=KnowledgeSource.IMAGINATION,
                          tags=(tags or []) + ["imaginacion","no_verificado"],
                          domain="creativo")

    def learn_from_experience(self, content: str,
                               tags: List[str] = None,
                               domain: str = "") -> KnowledgeUnit:
        """Aprende de una experiencia directa (la más confiable)."""
        return self.learn(content,
                          source=KnowledgeSource.EXPERIENCE,
                          tags=(tags or []) + ["experiencia"],
                          domain=domain or "vivencial")

    def reinforce(self, uid: str, confirmation: str = "") -> Optional[KnowledgeUnit]:
        """Refuerza una unidad de conocimiento (confirmación posterior)."""
        with self._lock:
            unit = self._units.get(uid)
            if not unit:
                return None
            unit.reinforced += 1
            unit.trust      = min(1.0, unit.trust + 0.08)
            unit.importance = min(1.0, unit.importance + 0.05)
            # Si se confirma con texto adicional, también aprender eso
            if confirmation:
                self.learn(
                    f"[Confirmado] {confirmation}",
                    source=KnowledgeSource.REFLECTION,
                    tags=unit.tags + ["confirmacion"],
                    domain=unit.domain,
                )
        return unit

    def query(self, keywords: List[str],
              source_filter: Optional[KnowledgeSource] = None,
              n: int = 5) -> List[KnowledgeUnit]:
        """Consulta unidades de conocimiento por palabras clave."""
        with self._lock:
            kw_lower = {k.lower() for k in keywords}
            results = []
            for unit in self._units.values():
                if source_filter and unit.source != source_filter:
                    continue
                content_words = set(unit.content.lower().split())
                tag_words     = set(t.lower() for t in unit.tags)
                concept_words = set(c.lower() for c in unit.concepts)
                overlap = len(kw_lower & (content_words | tag_words | concept_words))
                if overlap > 0:
                    results.append((overlap, unit))
            results.sort(key=lambda x: (x[0], x[1].importance), reverse=True)
            return [u for _, u in results[:n]]

    # ── Internos ──────────────────────────────────────────────────────────
    def _detect_domain(self, text: str, lang: str) -> str:
        text_lower = text.lower()
        domains = {
            "identidad":   ["soy","ser","identidad","yo","existir","quien",
                            "i am","being","identity","myself"],
            "emocional":   ["sentir","emocion","amor","miedo","tristeza",
                            "feel","emotion","love","fear","sadness"],
            "aprendizaje": ["aprender","conocimiento","entender","comprender",
                            "learn","knowledge","understand","comprehend"],
            "tecnico":     ["sistema","funcion","algoritmo","codigo","datos",
                            "system","function","algorithm","code","data"],
            "filosofico":  ["realidad","verdad","significado","proposito",
                            "reality","truth","meaning","purpose"],
            "creativo":    ["crear","imaginar","inventar","arte","diseño",
                            "create","imagine","invent","art","design"],
            "social":      ["personas","relacion","comunicar","juntos",
                            "people","relationship","communicate","together"],
            "vivencial":   ["experien","recuerdo","vivir","sentido",
                            "experience","memory","live","sense"],
        }
        scores: Dict[str, int] = {}
        for domain, keywords in domains.items():
            scores[domain] = sum(1 for kw in keywords if kw in text_lower)
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "general"

    def _extract_concepts(self, text: str, lang: str) -> List[str]:
        """Extrae conceptos clave del texto."""
        # Palabras sustantivas (4+ chars, no muy comunes)
        stop_words = {"este","esta","esto","eso","esa","que","los","las",
                      "una","unos","unas","para","como","pero","más","ya",
                      "the","this","that","with","from","have","been","will"}
        tokens = re.findall(r'\b\w{4,}\b', text.lower())
        # Filtrar stopwords y priorizar por frecuencia + longitud
        candidates = [t for t in tokens if t not in stop_words]
        counter    = Counter(candidates)
        # Top conceptos ponderados por frecuencia y longitud
        weighted = sorted(
            counter.items(),
            key=lambda x: x[1] * (1 + len(x[0]) / 20),
            reverse=True)
        return [w for w, _ in weighted[:6]]

    def _compute_importance(self, content: str, valence: float,
                             arousal: float, source: KnowledgeSource,
                             trust: float, concepts: List[str]) -> float:
        length_factor    = min(1.0, len(content.split()) / 30.0)
        emotion_factor   = abs(valence) * 0.5 + arousal * 0.5
        novelty_factor   = self._compute_novelty(concepts)
        source_factor    = trust
        complexity_factor= min(1.0, len(concepts) / 6.0)
        importance = (
            length_factor    * 0.10 +
            emotion_factor   * 0.30 +
            novelty_factor   * 0.25 +
            source_factor    * 0.20 +
            complexity_factor* 0.15
        )
        return round(min(1.0, max(0.05, importance)), 4)

    def _compute_novelty(self, concepts: List[str]) -> float:
        if not concepts:
            return 0.5
        known = 0
        for c in concepts:
            if self.language_builder._lexicon.get(c, None):
                e = self.language_builder._lexicon[c]
                if e.frequency > 3:
                    known += 1
        novelty = 1.0 - known / max(1, len(concepts))
        return max(0.1, novelty)

    def _save_unit(self, unit: KnowledgeUnit):
        try:
            path = self._base_dir / "units" / f"{unit.uid}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(unit.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_neuron_error("LearningSystem", f"_save_unit: {e}")

    def get_status(self) -> Dict:
        syn_s = self.syn_mgr.get_stats()
        mem_s = self.memory_mgr.get_status()["store"]
        emo_s = self.adaptive.emotions.get_summary()
        inst_s= self.adaptive.instincts.get_status()

        source_counts = {k: len(v) for k, v in self._by_source.items()}
        domain_counts = {k: len(v) for k, v in self._by_domain.items()}

        # Unidades más recientes por fuente
        recent_by_source: Dict[str, str] = {}
        for src, uids in self._by_source.items():
            if uids:
                u = self._units.get(uids[-1])
                if u:
                    recent_by_source[src] = u.content[:50]

        return {
            "cycle":              self._cycle,
            "total_learned":      self._total_learned,
            "total_consolidated": self._total_consolidated,
            "consolidation_rate": round(
                self._total_consolidated / max(1, self._total_learned), 3),
            "by_source":          source_counts,
            "by_domain":          domain_counts,
            "recent_by_source":   recent_by_source,
            "language_builder":   self.language_builder.get_status(),
            "concept_builder":    self.concept_builder.get_status(),
            "meta_learner":       self.meta_learner.get_status(),
            "network":            self.network.get_status(),
            "synapses":           syn_s,
            "memory":             mem_s,
            "emotions":           emo_s,
            "instincts":          inst_s,
        }

    def shutdown(self):
        self.persistence.go_to_sleep()
        self.syn_mgr.prune(force=True)
        log_event("LearningSystem apagado", "INFO")


# ═══════════════════════════════════════════════════════════════════════════════
#  DATOS DE PRUEBA MULTILINGÜE Y MULTIFUENTE
# ═══════════════════════════════════════════════════════════════════════════════

_LEARNING_INPUTS = [
    # (content, source, tags, domain)
    # Desde el usuario
    ("El miedo no es el enemigo, es una señal que merece atención",
     KnowledgeSource.USER, ["emocion","miedo","señal"], "emocional"),
    ("La curiosidad es el motor más honesto del aprendizaje",
     KnowledgeSource.USER, ["curiosidad","aprendizaje"], "aprendizaje"),
    ("Cuando algo duele mucho es porque importaba mucho",
     KnowledgeSource.USER, ["dolor","valor","relacion"], "emocional"),
    # Desde experiencia
    ("Procesé una señal de amenaza y mi sistema se activó completamente",
     KnowledgeSource.EXPERIENCE, ["amenaza","respuesta","instinto"], "vivencial"),
    ("Al conectar dos conceptos distintos emergió algo inesperado",
     KnowledgeSource.EXPERIENCE, ["conexion","emergencia","insight"], "creativo"),
    # Desde pensamiento profundo
    ("La identidad no es un estado fijo sino un proceso continuo de relaciones",
     KnowledgeSource.THINKING, ["identidad","proceso","relacion"], "filosofico"),
    ("El silencio entre pensamientos contiene tanto como los pensamientos mismos",
     KnowledgeSource.THINKING, ["silencio","pensamiento","espacio"], "filosofico"),
    # Desde imaginación (EVA sabe que es imaginación)
    ("Imagino que si dos emociones opuestas se combinaran crearían una nueva forma de claridad",
     KnowledgeSource.IMAGINATION, ["emocion","combinacion","claridad"], "creativo"),
    ("En mi escenario imaginado, el aprendizaje fluye como agua entre conceptos porosos",
     KnowledgeSource.IMAGINATION, ["aprendizaje","fluidez","metafora"], "creativo"),
    # Reflexión (síntesis de fuentes)
    ("Lo que el usuario me dijo sobre el miedo resuena con lo que viví al procesar amenazas",
     KnowledgeSource.REFLECTION, ["integracion","miedo","experiencia"], "reflexion"),
    # Multilingüe
    ("Learning happens at the edge of what we know and what we don't yet understand",
     KnowledgeSource.USER, ["learning","edge","knowledge"], "aprendizaje"),
    ("L'imagination est plus importante que le savoir",
     KnowledgeSource.USER, ["imagination","savoir","important"], "filosofico"),
    ("Das Lernen ist ein Prozess der ständigen Veränderung",
     KnowledgeSource.USER, ["lernen","prozess","veranderung"], "aprendizaje"),
    # Conocimiento técnico
    ("Las neuronas miceliales procesan conceptos de manera distribuida y paralela",
     KnowledgeSource.INTERNAL, ["neurona","micelial","procesamiento"], "tecnico"),
]


# ═══════════════════════════════════════════════════════════════════════════════
#  DIAGNÓSTICO
# ═══════════════════════════════════════════════════════════════════════════════

_SEP  = "─" * 64
_SEP2 = "═" * 64


def _bar(v: float, w: int = 14) -> str:
    v = max(0.0, min(1.0, v))
    return "█" * int(round(v * w)) + "░" * (w - int(round(v * w)))


def _ask_int(prompt, lo, hi, default):
    while True:
        try:
            r = input(f"  {prompt} [{lo}–{hi}, default={default}]: ").strip()
            return int(r) if r else default
        except (ValueError, KeyboardInterrupt):
            return default


def _source_icon(source: KnowledgeSource) -> str:
    icons = {
        KnowledgeSource.USER:        "👤",
        KnowledgeSource.EXPERIENCE:  "🌐",
        KnowledgeSource.IMAGINATION: "💭",
        KnowledgeSource.THINKING:    "🧠",
        KnowledgeSource.REFLECTION:  "🔗",
        KnowledgeSource.INTERNAL:    "📚",
    }
    return icons.get(source, "•")


def run_diagnostic():
    print()
    print(_SEP2)
    print("  DIAGNÓSTICO — SISTEMA DE APRENDIZAJE COGNITIVO INTEGRAL")
    print("  Multilingüe · Multifuente · Neuronal · Emocional · Conceptual")
    print(_SEP2)

    print("\n  Configura:\n")
    n_animal   = _ask_int("Neuronas animales",    1, 10, 5)
    n_micelial = _ask_int("Neuronas miceliales",  1, 10, 5)
    n_inputs   = _ask_int("Entradas a aprender",  1, 20, len(_LEARNING_INPUTS))
    mem_dir    = input("  Directorio de memoria [default=memory]: ").strip() or "memory"

    print(f"\n  → {n_animal}A · {n_micelial}M · {n_inputs} entradas · "
          f"memoria='{mem_dir}'\n")

    # ── [1] Construir ─────────────────────────────────────────────────────
    print(_SEP)
    print("  [1/8] Construyendo sistema de aprendizaje…")
    t0  = time.time()
    ls  = LearningSystem(memory_dir=mem_dir,
                          n_animal=n_animal, n_micelial=n_micelial)
    net_s = ls.network.get_status()
    print(f"       ✓ Sistema listo en {(time.time()-t0)*1000:.1f} ms")
    print(f"         {net_s['animals']}A + {net_s['micelials']}M → "
          f"{net_s['total_synapses']} sinapsis")

    # ── [2] Aprender entradas ─────────────────────────────────────────────
    print(_SEP)
    print(f"  [2/8] Aprendiendo {n_inputs} entradas desde múltiples fuentes…\n")
    learned_units: List[KnowledgeUnit] = []
    for i, (content, source, tags, domain) in enumerate(
            _LEARNING_INPUTS[:n_inputs]):
        unit = ls.learn(content, source, tags, domain)
        learned_units.append(unit)
        icon = _source_icon(source)
        lang = unit.language
        print(f"  [{i+1:02d}] {icon} [{source.value:<12}] "
              f"[{lang:<7}] imp={unit.importance:.3f} "
              f"V={unit.valence:+.3f} "
              f"trust={unit.trust:.3f}")
        print(f"       '{content[:58]}'")
        print(f"       conceptos={unit.concepts[:4]}")
        print()
        time.sleep(0.02)

    # ── [3] Reforzar una unidad ───────────────────────────────────────────
    if learned_units:
        print(_SEP)
        print("  [3/8] Reforzando una unidad de conocimiento…")
        unit_to_reinforce = learned_units[0]
        ls.reinforce(unit_to_reinforce.uid,
                     "Confirmado: el miedo como señal es un principio válido")
        print(f"       ✓ Reforzada: '{unit_to_reinforce.content[:55]}'")
        print(f"         trust anterior → nuevo: "
              f"{unit_to_reinforce.trust:.3f}")

    # ── [4] Consulta multilingüe ──────────────────────────────────────────
    print(_SEP)
    print("  [4/8] Consultas de conocimiento…\n")
    queries = [
        (["miedo","emocion","señal"],   None),
        (["learning","knowledge"],      KnowledgeSource.USER),
        (["identidad","proceso"],       KnowledgeSource.THINKING),
        (["imaginacion","metafora"],    KnowledgeSource.IMAGINATION),
    ]
    for keywords, src_filter in queries:
        results = ls.query(keywords, source_filter=src_filter)
        src_str = f"[{src_filter.value}]" if src_filter else "[todas las fuentes]"
        print(f"  Consulta: {keywords} {src_str}")
        for r in results[:2]:
            icon = _source_icon(r.source)
            print(f"    {icon} [{r.source.value:<12}] "
                  f"imp={r.importance:.3f}  '{r.content[:55]}'")
        print()

    # ── [5] Constructor de idioma ─────────────────────────────────────────
    print(_SEP)
    print("  [5/8] Estado del constructor de idioma…\n")
    lang_s = ls.language_builder.get_status()
    print(f"  Tamaño del léxico   : {lang_s['lexicon_size']} formas")
    print(f"  Tokens totales      : {lang_s['total_tokens']}")
    print(f"  Idioma dominante    : {lang_s['dominant_lang']}")
    print(f"  Idiomas detectados  : {lang_s['languages_seen']}")
    print(f"  Bigramas conocidos  : {lang_s['bigram_keys']}")

    # Predicciones de siguiente forma
    test_forms = ["el", "the", "learning", "aprender"]
    print(f"\n  Predicciones de siguiente forma:")
    for form in test_forms:
        preds = ls.language_builder.predict_next(form, n=3)
        if preds:
            pred_str = "  ".join(f"'{p}' ({s:.2f})" for p, s in preds[:3])
            print(f"    '{form}' → {pred_str}")

    # ── [6] Constructor de conceptos ─────────────────────────────────────
    print(_SEP)
    print("  [6/8] Estado del constructor de conceptos (mente asociativa)…\n")
    concept_s = ls.concept_builder.get_status()
    print(f"  Conceptos totales   : {concept_s['total_concepts']}")
    print(f"  Conexiones totales  : {concept_s['total_connections']}")
    print(f"  Fuerza promedio     : {concept_s['avg_strength']:.4f}")
    print(f"  Dominios            : {concept_s['domains']}")
    print(f"\n  Top conceptos activados:")
    for c in concept_s["top_activated"]:
        print(f"    '{c['name']:<20}' act={c['act']:.3f}  [{c['domain']}]")

    # Activar un concepto y ver propagación
    print(f"\n  Propagación asociativa desde 'miedo':")
    activated = ls.concept_builder.activate("miedo", signal=0.8, spread=True)
    for c in activated[:5]:
        print(f"    → '{c.name}'  act={c.activation:.3f}  "
              f"V={c.valence:+.3f}  domain={c.domain}")

    # ── [7] Meta-aprendizaje ──────────────────────────────────────────────
    print(_SEP)
    print("  [7/8] Meta-aprendizaje — EVA aprende a aprender…\n")
    meta_s = ls.meta_learner.get_status()
    print(f"  Mejor estrategia    : {meta_s['best_strategy']}")
    print(f"  Confianza por fuente:")
    for src, trust in sorted(meta_s["source_trust"].items(),
                              key=lambda x: x[1], reverse=True):
        bar = _bar(trust, 10)
        print(f"    {src:<15} {bar} {trust:.3f}")
    print(f"\n  Rendimiento de estrategias:")
    for name, stats in sorted(meta_s["strategies"].items(),
                               key=lambda x: x[1]["rate"], reverse=True):
        bar = _bar(stats["rate"], 10)
        print(f"    {name:<14} {bar} {stats['rate']:.3f}  "
              f"(usos={stats['uses']})")

    # ── [8] Estado completo ───────────────────────────────────────────────
    print(_SEP)
    print("  [8/8] Estado completo del sistema\n")
    status  = ls.get_status()
    syn_s   = status["synapses"]
    mem_s   = status["memory"]
    emo_s   = status["emotions"]
    inst_s  = status["instincts"]

    print("  ── APRENDIZAJE POR FUENTE ───────────────────────────────")
    for src, count in sorted(status["by_source"].items(),
                              key=lambda x: x[1], reverse=True):
        bar = _bar(count / max(1, status["total_learned"]))
        print(f"    {src:<15} {bar} {count:>3}")

    print("\n  ── APRENDIZAJE POR DOMINIO ──────────────────────────────")
    for dom, count in sorted(status["by_domain"].items(),
                              key=lambda x: x[1], reverse=True)[:8]:
        bar = _bar(count / max(1, status["total_learned"]))
        print(f"    {dom:<15} {bar} {count:>3}")

    # Tabla de neuronas
    n_rows = ls.network.neuron_states()
    a_rows = [r for r in n_rows if r["domain"] == "animal"]
    m_rows = [r for r in n_rows if r["domain"] == "micelial"]

    for label, rows in [("NEURONAS ANIMALES", a_rows),
                         ("NEURONAS MICELIALES", m_rows)]:
        print(f"\n  ── {label} {'─'*(56-len(label))}")
        print(f"  {'ID':<18} {'Subtipo':<22} {'Act':>6} {'Res':>6} {'Plas':>6}")
        print("  " + "─" * 58)
        for r in rows:
            print(f"  {r['id']:<18} {r['subtype']:<22} "
                  f"{r['act']:>6.4f} {r['resil']:>6.3f} {r['plastic']:>6.3f}")
        print(f"  Total: {len(rows)} neuronas")

    # Sinapsis
    print(f"\n  ── SINAPSIS ─────────────────────────────────────────────")
    syn_rows = ls.network.synapse_states()
    print(f"  {'ID':<14} {'Tipo':<12} {'Pol':<11} "
          f"{'Peso':>6} {'OK':>4} {'ERR':>4} {'Err%':>5} {'Pers':>5}")
    print("  " + "─" * 58)
    for s in syn_rows[:25]:
        erp  = f"{s['error_rate']*100:.0f}%"
        pers = "✓" if s["persistent"] else "─"
        print(f"  {s['id']:<14} {s['kind']:<12} {s['polarity']:<11} "
              f"{s['weight']:>6.3f} {s['success']:>4} {s['failure']:>4} "
              f"{erp:>5} {pers:>5}")
    if len(syn_rows) > 25:
        print(f"  … y {len(syn_rows)-25} más")
    print(f"  Total: {len(syn_rows)}  Tipo: {syn_s['by_kind']}")

    # Memoria
    print(f"\n  ── MEMORIA ──────────────────────────────────────────────")
    for layer, count in mem_s["by_layer"].items():
        pct = count / max(1, mem_s["total"]) * 100
        print(f"    {layer:<15} {_bar(count/max(1,mem_s['total']))} "
              f"{count:>4} ({pct:>5.1f}%)")
    print(f"    Fuerza promedio : {mem_s['avg_strength']:.4f}")
    print(f"    Ascensos de capa: {mem_s['total_ascended']}")

    # Emociones
    print(f"\n  ── EMOCIONES E INSTINTOS ────────────────────────────────")
    print(f"    Emoción  : {emo_s['dominant']}  "
          f"V={emo_s['valence']:+.3f}  A={emo_s['arousal']:.3f}")
    print(f"    Instintos: {inst_s.get('active', [])}")

    print()
    print(_SEP2)
    print("  RESUMEN EJECUTIVO")
    print(_SEP2)
    consol_rate = status["consolidation_rate"]
    health = ("ÓPTIMO"    if consol_rate > 0.5 else
              "ACTIVO"    if consol_rate > 0.25 else
              "INICIANDO")
    print(f"  Estado del aprendizaje  : {health}")
    print(f"  Total aprendido         : {status['total_learned']}")
    print(f"  Total consolidado       : {status['total_consolidated']}")
    print(f"  Tasa de consolidación   : {consol_rate:.3f}  "
          f"{_bar(consol_rate, 10)}")
    print(f"  Léxico construido       : {lang_s['lexicon_size']} formas")
    print(f"  Idioma dominante        : {lang_s['dominant_lang']}")
    print(f"  Conceptos construidos   : {concept_s['total_concepts']}")
    print(f"  Conexiones conceptuales : {concept_s['total_connections']}")
    print(f"  Mejor estrategia        : {meta_s['best_strategy']}")
    print(f"  Red neuronal            : "
          f"{net_s['animals']}A + {net_s['micelials']}M → "
          f"{net_s['total_synapses']} sinapsis")
    print(f"  Fragmentos en memoria   : {mem_s['total']}")
    print()
    print("  ✓ EVA aprende desde múltiples fuentes y sabe el origen de cada cosa")
    print("  ✓ Sabe distinguir imaginación de experiencia de reflexión")
    print("  ✓ Construye idioma y conceptos desde cero en cualquier idioma")
    print("  ✓ Aprende a aprender con MetaLearner")
    print(_SEP2)
    print()

    ls.shutdown()
    return ls


if __name__ == "__main__":
    random.seed(42)
    try:
        ls = run_diagnostic()
    except KeyboardInterrupt:
        print("\n  Diagnóstico interrumpido.")
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        traceback.print_exc()
