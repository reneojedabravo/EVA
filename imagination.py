#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cognitive_imagination.py - Sistema Cognitivo-Emocional Avanzado para EVA

Este módulo implementa:
1. Motor de Imaginación Artificial avanzado
2. Simulación y evaluación de escenarios mentales
3. Predicción basada en memoria emocional
4. Resolución creativa de problemas
5. Generación de significado contextual
6. Sistema de registro persistente

Integrado con:
- Sistema de memoria segmentada
- Reflexión continua (BackgroundThinker)
- Estados emocionales adaptativos
- Diario de autoreflexiones
"""

import os
import json
import random
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict, Counter
from uuid import uuid4
import numpy as np

class MentalRepresentation:
    """
    Representa un concepto, escenario o evento mental con propiedades emocionales y cognitivas.
    """
    def __init__(self, content: str, source_memories: List[str] = None, 
                 emotional_valence: float = 0.0, certainty: float = 0.5,
                 complexity: float = 0.5, novelty: float = 0.5):
        self.id = f"repr_{uuid4().hex[:12]}"
        self.content = content
        self.source_memories = source_memories or []
        self.emotional_valence = max(-1.0, min(1.0, emotional_valence))  # -1 a 1
        self.certainty = max(0.0, min(1.0, certainty))  # 0 a 1
        self.complexity = max(0.0, min(1.0, complexity))  # 0 a 1
        self.novelty = max(0.0, min(1.0, novelty))  # 0 a 1
        self.timestamp = datetime.now().isoformat()
        self.activation_level = 0.5
        self.connections = []  # Otras representaciones relacionadas
        
    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "source_memories": self.source_memories,
            "emotional_valence": self.emotional_valence,
            "certainty": self.certainty,
            "complexity": self.complexity,
            "novelty": self.novelty,
            "timestamp": self.timestamp,
            "activation_level": self.activation_level,
            "connections": [c.id if hasattr(c, 'id') else str(c) for c in self.connections]
        }

class ScenarioEngine:
    """
    Motor para generar, simular y evaluar escenarios mentales complejos.
    """
    def __init__(self, brain):
        self.brain = brain
        self.scenario_templates = {
            "future_projection": "¿Qué pasaría si {concept1} evolucionara hacia {concept2}?",
            "counterfactual": "¿Y si {concept1} nunca hubiera ocurrido? ¿Cómo sería {concept2}?",
            "synthesis": "Si combino {concept1} con {concept2}, podría obtener {synthesis}",
            "conflict_resolution": "Para resolver la tensión entre {concept1} y {concept2}, podría {solution}",
            "analogy": "{concept1} es como {concept2} en el sentido de que ambos {similarity}",
            "causality": "Si {concept1} entonces {concept2}, porque {reasoning}",
            "exploration": "Me pregunto qué hay más allá de {concept1}, tal vez {speculation}",
            "integration": "Conectando {concept1} y {concept2}, veo que {insight}"
        }
        
    def generate_scenario(self, representations: List[MentalRepresentation], 
                         scenario_type: str = None) -> Dict[str, Any]:
        """
        Genera un escenario mental basado en representaciones dadas.
        """
        if len(representations) < 1:
            return None
            
        if not scenario_type:
            scenario_type = self._select_scenario_type(representations)
            
        template = self.scenario_templates.get(scenario_type, 
                                              "Explorando {concept1} y {concept2}")
        
        # Seleccionar conceptos para el escenario
        if len(representations) >= 2:
            concept1 = representations[0].content
            concept2 = representations[1].content
        else:
            concept1 = representations[0].content
            concept2 = self._generate_complementary_concept(concept1)
            
        # Generar elementos adicionales según el tipo
        synthesis = self._generate_synthesis(concept1, concept2)
        solution = self._generate_solution(concept1, concept2)
        similarity = self._find_similarity(concept1, concept2)
        reasoning = self._generate_reasoning(concept1, concept2)
        speculation = self._generate_speculation(concept1)
        insight = self._generate_insight(concept1, concept2)
        
        # Construir contenido del escenario
        try:
            content = template.format(
                concept1=concept1,
                concept2=concept2,
                synthesis=synthesis,
                solution=solution,
                similarity=similarity,
                reasoning=reasoning,
                speculation=speculation,
                insight=insight
            )
        except KeyError:
            content = f"Explorando la relación entre '{concept1}' y '{concept2}'"
            
        # Calcular propiedades del escenario
        emotional_valence = self._calculate_scenario_valence(representations)
        complexity = self._calculate_complexity(representations)
        novelty = self._calculate_novelty(concept1, concept2)
        
        return {
            "id": f"scenario_{uuid4().hex[:12]}",
            "type": scenario_type,
            "content": content,
            "representations": [r.id for r in representations],
            "emotional_valence": emotional_valence,
            "complexity": complexity,
            "novelty": novelty,
            "timestamp": datetime.now().isoformat(),
            "confidence": self._calculate_confidence(representations)
        }
    
    def _select_scenario_type(self, representations: List[MentalRepresentation]) -> str:
        """Selecciona el tipo de escenario más apropiado."""
        avg_valence = sum(r.emotional_valence for r in representations) / len(representations)
        avg_novelty = sum(r.novelty for r in representations) / len(representations)
        avg_complexity = sum(r.complexity for r in representations) / len(representations)
        
        if avg_valence < -0.3:
            return "conflict_resolution"
        elif avg_novelty > 0.7:
            return "exploration"
        elif avg_complexity > 0.6:
            return "synthesis"
        elif len(representations) >= 2 and abs(representations[0].emotional_valence - representations[1].emotional_valence) > 0.5:
            return "counterfactual"
        else:
            return random.choice(["future_projection", "analogy", "causality", "integration"])
    
    def _generate_complementary_concept(self, concept: str) -> str:
        """Genera un concepto complementario usando memoria."""
        # Buscar conceptos relacionados en memoria
        keywords = concept.split()[:3]
        related_memories = self.brain.memory.retrieve_context(keywords)
        
        if related_memories:
            # Seleccionar una memoria diferente
            candidates = [m for m in related_memories if concept.lower() not in m["data"].lower()]
            if candidates:
                return candidates[0]["data"][:50]
                
        # Fallback: generar basado en patrones comunes
        complements = {
            "agua": "tierra", "luz": "oscuridad", "calor": "frío",
            "amor": "miedo", "conocimiento": "misterio", "tiempo": "espacio"
        }
        
        for key, value in complements.items():
            if key in concept.lower():
                return value
                
        return "lo desconocido"
    
    def _generate_synthesis(self, concept1: str, concept2: str) -> str:
        """Genera una síntesis creativa de dos conceptos."""
        # Extraer palabras clave
        words1 = re.findall(r'\w+', concept1.lower())
        words2 = re.findall(r'\w+', concept2.lower())
        
        # Combinar elementos
        if words1 and words2:
            return f"una nueva forma de {words1[0]} que incorpora {words2[0]}"
        return "algo completamente nuevo"
    
    def _generate_solution(self, concept1: str, concept2: str) -> str:
        """Genera una solución para resolver tensiones."""
        solutions = [
            f"encontrar el equilibrio entre {concept1} y {concept2}",
            f"integrar lo mejor de {concept1} con lo esencial de {concept2}",
            f"transcender tanto {concept1} como {concept2}",
            f"alternar entre {concept1} y {concept2} según el contexto"
        ]
        return random.choice(solutions)
    
    def _find_similarity(self, concept1: str, concept2: str) -> str:
        """Encuentra similitudes entre conceptos."""
        similarities = [
            "involucran transformación",
            "requieren atención consciente",
            "generan impacto emocional",
            "conectan con experiencias pasadas",
            "abren nuevas posibilidades"
        ]
        return random.choice(similarities)
    
    def _generate_reasoning(self, concept1: str, concept2: str) -> str:
        """Genera razonamiento causal."""
        reasons = [
            "comparten patrones subyacentes",
            "influyen en estados emocionales similares",
            "activan las mismas redes de memoria",
            "requieren procesos cognitivos análogos"
        ]
        return random.choice(reasons)
    
    def _generate_speculation(self, concept: str) -> str:
        """Genera especulación creativa."""
        speculations = [
            f"{concept} podría evolucionar hacia formas más complejas",
            f"hay aspectos ocultos de {concept} que aún no comprendo",
            f"{concept} se conecta con patrones más amplios",
            f"la esencia de {concept} trasciende su forma actual"
        ]
        return random.choice(speculations)
    
    def _generate_insight(self, concept1: str, concept2: str) -> str:
        """Genera insights creativos."""
        insights = [
            f"ambos son manifestaciones de un principio más profundo",
            f"la tensión entre ellos genera nueva comprensión",
            f"juntos revelan algo que por separado permanece oculto",
            f"su interacción abre caminos inesperados de crecimiento"
        ]
        return random.choice(insights)
    
    def _calculate_scenario_valence(self, representations: List[MentalRepresentation]) -> float:
        """Calcula la valencia emocional del escenario."""
        if not representations:
            return 0.0
        return sum(r.emotional_valence for r in representations) / len(representations)
    
    def _calculate_complexity(self, representations: List[MentalRepresentation]) -> float:
        """Calcula la complejidad del escenario."""
        if not representations:
            return 0.5
        return min(1.0, sum(r.complexity for r in representations) / len(representations) + 
                   len(representations) * 0.1)
    
    def _calculate_novelty(self, concept1: str, concept2: str) -> float:
        """Calcula la novedad del escenario."""
        # Buscar en memoria si esta combinación ya se exploró
        combined = f"{concept1} {concept2}"
        similar_memories = self.brain.memory.retrieve_context(combined.split())
        
        # Más memorias similares = menor novedad
        novelty = max(0.1, 1.0 - len(similar_memories) * 0.1)
        return min(1.0, novelty)
    
    def _calculate_confidence(self, representations: List[MentalRepresentation]) -> float:
        """Calcula la confianza en el escenario."""
        if not representations:
            return 0.5
        return sum(r.certainty for r in representations) / len(representations)

class CognitiveImaginationEngine:
    """
    Motor principal de imaginación cognitiva-emocional de EVA.
    """
    def __init__(self, brain):
        self.brain = brain
        self.scenario_engine = ScenarioEngine(brain)
        
        # Estado del motor
        self.active = False
        self.imagination_intensity = 0.5  # 0 a 1
        self.creative_tension = 0.0  # Acumulación de necesidad creativa
        self.focus_coherence = 0.5  # Coherencia del foco mental
        
        # Estadísticas
        self.scenarios_generated = 0
        self.representations_created = 0
        self.insights_discovered = 0
        
        # Configuración de archivos
        self.imagination_dir = os.path.join(brain.memory.memory_dir, "imagination")
        self.scenarios_dir = os.path.join(self.imagination_dir, "scenarios")
        self.representations_dir = os.path.join(self.imagination_dir, "representations")
        self.insights_dir = os.path.join(self.imagination_dir, "insights")
        
        # Crear directorios
        os.makedirs(self.scenarios_dir, exist_ok=True)
        os.makedirs(self.representations_dir, exist_ok=True)
        os.makedirs(self.insights_dir, exist_ok=True)
        
        # Representaciones activas en memoria de trabajo
        self.active_representations = []
        self.max_active_representations = 7  # Límite de memoria de trabajo
        
        print("[CognitiveImaginationEngine] Motor de imaginación cognitiva inicializado")
    
    def activate(self, intensity: float = 0.7):
        """Activa el motor de imaginación con intensidad específica."""
        self.active = True
        self.imagination_intensity = max(0.1, min(1.0, intensity))
        print(f"[CognitiveImaginationEngine] Activado con intensidad {self.imagination_intensity:.2f}")
    
    def deactivate(self):
        """Desactiva el motor de imaginación."""
        self.active = False
        print("[CognitiveImaginationEngine] Desactivado")
    
    def create_mental_representation(self, content: str, source_memories: List[str] = None,
                                   emotional_context: Dict = None) -> MentalRepresentation:
        """
        Crea una representación mental enriquecida con propiedades cognitivas.
        """
        # Calcular propiedades basadas en contenido y contexto
        emotional_valence = self._calculate_emotional_valence(content, emotional_context)
        certainty = self._calculate_certainty(content, source_memories)
        complexity = self._calculate_content_complexity(content)
        novelty = self._calculate_content_novelty(content)
        
        representation = MentalRepresentation(
            content=content,
            source_memories=source_memories,
            emotional_valence=emotional_valence,
            certainty=certainty,
            complexity=complexity,
            novelty=novelty
        )
        
        # Agregar a memoria de trabajo
        self._add_to_working_memory(representation)
        
        # Guardar en disco
        self._save_representation(representation)
        
        self.representations_created += 1
        return representation
    
    def generate_imaginative_scenario(self, trigger_type: str = None, recursion_depth: int = 0) -> Optional[Dict[str, Any]]:
        """
        Genera un escenario imaginativo basado en el estado actual de la memoria.
        """
        if not self.active or recursion_depth > 2:  # Límite de recursión
            return None
        
        # Seleccionar representaciones para el escenario
        representations = self._select_representations_for_scenario(trigger_type)
        
        if not representations:
            # Crear representaciones desde memoria si no hay suficientes
            representations = self._extract_representations_from_memory(recursion_depth + 1)
        
        if not representations:
            return None
        
        # Generar escenario
        scenario = self.scenario_engine.generate_scenario(representations, trigger_type)
        
        if scenario:
            # Guardar escenario
            self._save_scenario(scenario)
            
            # Actualizar estado
            self.scenarios_generated += 1
            self.creative_tension = max(0.0, self.creative_tension - 0.15)
            
            # Crear insight si el escenario es muy novel o complejo
            if scenario.get("novelty", 0) > 0.7 or scenario.get("complexity", 0) > 0.7:
                insight = self._generate_insight_from_scenario(scenario)
                if insight:
                    self._save_insight(insight)
                    self.insights_discovered += 1
            
            print(f"[CognitiveImaginationEngine] Escenario generado: {scenario['type']}")
            
        return scenario
    
    def run_imagination_cycle(self) -> Dict[str, Any]:
        """
        Ejecuta un ciclo completo de imaginación cognitiva.
        """
        cycle_results = {
            "scenarios_generated": 0,
            "insights_discovered": 0,
            "representations_updated": 0,
            "emotional_impact": 0.0
        }
        
        if not self.active:
            return cycle_results
        
        # 1. Actualizar tensión creativa
        self._update_creative_tension()
        
        # 2. Generar escenarios si hay suficiente tensión
        if self.creative_tension > 0.4:
            scenario = self.generate_imaginative_scenario()
            if scenario:
                cycle_results["scenarios_generated"] = 1
                cycle_results["emotional_impact"] = scenario.get("emotional_valence", 0.0)
        
        # 3. Actualizar representaciones activas
        updated = self._update_active_representations()
        cycle_results["representations_updated"] = updated
        
        # 4. Consolidar insights si hay patrones emergentes
        if len(self.active_representations) > 4:
            insight = self._consolidate_patterns()
            if insight:
                cycle_results["insights_discovered"] = 1
        
        # 5. Mantener coherencia del foco
        self._maintain_focus_coherence()
        
        return cycle_results
    
    def _select_representations_for_scenario(self, trigger_type: str = None) -> List[MentalRepresentation]:
        """Selecciona representaciones apropiadas para generar un escenario."""
        if not self.active_representations:
            return []
        
        # Filtrar por activación y relevancia
        candidates = [r for r in self.active_representations if r.activation_level > 0.3]
        
        if not candidates:
            candidates = self.active_representations[:3]  # Tomar las primeras
        
        # Seleccionar según tipo de trigger
        if trigger_type == "emotional_conflict":
            # Buscar representaciones con valencia opuesta
            candidates.sort(key=lambda r: abs(r.emotional_valence))
            return candidates[:2]
        elif trigger_type == "creative_synthesis":
            # Buscar representaciones con alta novedad
            candidates.sort(key=lambda r: r.novelty, reverse=True)
            return candidates[:3]
        elif trigger_type == "problem_solving":
            # Buscar representaciones con alta complejidad
            candidates.sort(key=lambda r: r.complexity, reverse=True)
            return candidates[:2]
        else:
            # Selección balanceada
            return candidates[:min(3, len(candidates))]
    
    def _extract_representations_from_memory(self, recursion_depth: int = 0) -> List[MentalRepresentation]:
        """Extrae representaciones de la memoria cuando no hay suficientes activas."""
        representations = []
        
        # Límite de recursión para evitar bucles infinitos
        if recursion_depth > 1:
            return representations
        
        # Buscar en memoria reciente entradas importantes
        recent_memories = (self.brain.memory.short_term[-10:] + 
                         self.brain.memory.medium_term[-5:])
        
        important_memories = [m for m in recent_memories 
                            if m.get("importance", 1) >= 2 or m.get("accesos", 1) >= 3]
        
        for memory in important_memories[:3]:
            # Evitar crear representaciones de contenido muy largo o complejo
            content = memory.get("data", "")
            if len(content) > 200:  # Limitar contenido largo
                content = content[:200] + "..."
            
            repr = self.create_mental_representation(
                content=content,
                source_memories=[memory.get("id", "unknown")],
                emotional_context=memory.get("context", {})
            )
            representations.append(repr)
        
        return representations
    
    def _add_to_working_memory(self, representation: MentalRepresentation):
        """Agrega una representación a la memoria de trabajo."""
        self.active_representations.append(representation)
        
        # Mantener límite de memoria de trabajo
        if len(self.active_representations) > self.max_active_representations:
            # Remover las menos activas
            self.active_representations.sort(key=lambda r: r.activation_level, reverse=True)
            self.active_representations = self.active_representations[:self.max_active_representations]
    
    def _update_creative_tension(self):
        """Actualiza la tensión creativa basada en el estado del sistema."""
        # Factores que aumentan tensión creativa
        factors = 0.0
        
        # 1. Memoria activa sin procesar
        if len(self.brain.memory.short_term) > 15:
            factors += 0.05
        
        # 2. Asociaciones fuertes sin explorar
        if self.brain.learning_system:
            strong_assoc = len(self.brain.learning_system.get_strong_associations())
            if strong_assoc > 5:
                factors += 0.03
        
        # 3. Estado emocional creativo
        if self.brain.adaptive_core:
            emo_state = self.brain.adaptive_core.emotional_state.get_state()
            if emo_state.get("curiosity", 0) > 0.6 or emo_state.get("creativity", 0) > 0.6:
                factors += 0.04
        
        # 4. Tiempo sin imaginar
        factors += 0.02  # Tensión base
        
        self.creative_tension = min(1.0, self.creative_tension + factors)
    
    def _update_active_representations(self) -> int:
        """Actualiza el estado de las representaciones activas."""
        updated = 0
        
        for repr in self.active_representations:
            # Decaimiento natural de activación
            repr.activation_level *= 0.95
            
            # Reactivar si aparece en memoria reciente
            recent_content = " ".join([m.get("data", "") for m in self.brain.memory.short_term[-5:]])
            if any(word in recent_content.lower() for word in repr.content.lower().split()):
                repr.activation_level = min(1.0, repr.activation_level + 0.2)
                updated += 1
        
        # Remover representaciones con baja activación
        self.active_representations = [r for r in self.active_representations if r.activation_level > 0.1]
        
        return updated
    
    def _maintain_focus_coherence(self):
        """Mantiene la coherencia del foco mental."""
        if not self.active_representations:
            self.focus_coherence = 0.5
            return
        
        # Calcular coherencia basada en similitud de contenido
        contents = [r.content for r in self.active_representations]
        
        # Método simple: calcular overlap de palabras
        all_words = set()
        for content in contents:
            words = set(re.findall(r'\w+', content.lower()))
            all_words.update(words)
        
        if len(all_words) == 0:
            self.focus_coherence = 0.5
            return
        
        # Coherencia = palabras compartidas / total de palabras
        shared_count = 0
        for word in all_words:
            appearances = sum(1 for content in contents if word in content.lower())
            if appearances > 1:
                shared_count += 1
        
        self.focus_coherence = min(1.0, shared_count / len(all_words))
    
    def _consolidate_patterns(self) -> Optional[Dict[str, Any]]:
        """Consolida patrones emergentes en insights."""
        if len(self.active_representations) < 3:
            return None
        
        # Buscar patrones en las representaciones
        emotional_pattern = self._detect_emotional_pattern()
        thematic_pattern = self._detect_thematic_pattern()
        causal_pattern = self._detect_causal_pattern()
        
        if emotional_pattern or thematic_pattern or causal_pattern:
            insight = {
                "id": f"insight_{uuid4().hex[:12]}",
                "type": "pattern_consolidation",
                "emotional_pattern": emotional_pattern,
                "thematic_pattern": thematic_pattern,
                "causal_pattern": causal_pattern,
                "source_representations": [r.id for r in self.active_representations],
                "timestamp": datetime.now().isoformat(),
                "confidence": self.focus_coherence
            }
            return insight
        
        return None
    
    def _detect_emotional_pattern(self) -> Optional[str]:
        """Detecta patrones emocionales en las representaciones."""
        valences = [r.emotional_valence for r in self.active_representations]
        
        if len(valences) < 3:
            return None
        
        avg_valence = sum(valences) / len(valences)
        variance = sum((v - avg_valence) ** 2 for v in valences) / len(valences)
        
        if variance < 0.1 and avg_valence > 0.3:
            return "tendencia_positiva_coherente"
        elif variance < 0.1 and avg_valence < -0.3:
            return "tendencia_negativa_coherente"
        elif variance > 0.5:
            return "conflicto_emocional_complejo"
        
        return None
    
    def _detect_thematic_pattern(self) -> Optional[str]:
        """Detecta patrones temáticos en las representaciones."""
        # Extraer palabras clave de todas las representaciones
        all_words = []
        for repr in self.active_representations:
            words = re.findall(r'\w{4,}', repr.content.lower())
            all_words.extend(words)
        
        # Encontrar palabras frecuentes
        word_counts = Counter(all_words)
        common_words = [word for word, count in word_counts.items() if count >= 2]
        
        if len(common_words) >= 3:
            return f"tema_recurrente_{common_words[0]}"
        
        return None
    
    def _detect_causal_pattern(self) -> Optional[str]:
        """Detecta patrones causales simples."""
        # Buscar secuencias temporales en las representaciones
        sorted_repr = sorted(self.active_representations, key=lambda r: r.timestamp)
        
        if len(sorted_repr) >= 3:
            # Verificar si hay progresión en complejidad o certeza
            complexities = [r.complexity for r in sorted_repr]
            if all(complexities[i] <= complexities[i+1] for i in range(len(complexities)-1)):
                return "progresión_complejidad_creciente"
        
        return None
    
    def _generate_insight_from_scenario(self, scenario: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Genera un insight a partir de un escenario."""
        if scenario.get("novelty", 0) < 0.6:
            return None
        
        insight = {
            "id": f"insight_{uuid4().hex[:12]}",
            "type": "scenario_derived",
            "content": f"Insight derivado de {scenario['type']}: {scenario['content'][:100]}...",
            "source_scenario": scenario["id"],
            "novelty": scenario.get("novelty", 0.5),
            "emotional_impact": scenario.get("emotional_valence", 0.0),
            "timestamp": datetime.now().isoformat()
        }
        return insight
    
    def _calculate_emotional_valence(self, content: str, emotional_context: Dict = None) -> float:
        """Calcula la valencia emocional de un contenido."""
        # Palabras con carga emocional
        positive_words = ["feliz", "amor", "éxito", "logro", "alegría", "esperanza", "paz"]
        negative_words = ["miedo", "dolor", "error", "fracaso", "tristeza", "ansiedad", "conflicto"]
        
        content_lower = content.lower()
        
        pos_count = sum(1 for word in positive_words if word in content_lower)
        neg_count = sum(1 for word in negative_words if word in content_lower)
        
        if pos_count + neg_count == 0:
            base_valence = 0.0
        else:
            base_valence = (pos_count - neg_count) / (pos_count + neg_count)
        
        # Ajustar con contexto emocional si está disponible
        if emotional_context and "estado_emocional" in emotional_context:
            emo_state = emotional_context["estado_emocional"]
            if emo_state in ["excited", "calm", "confident"]:
                base_valence += 0.2
            elif emo_state in ["overwhelmed", "blocked", "confused"]:
                base_valence -= 0.2
        
        return max(-1.0, min(1.0, base_valence))
    
    def _calculate_certainty(self, content: str, source_memories: List[str] = None) -> float:
        """Calcula la certeza de una representación."""
        # Base: contenido más específico = mayor certeza
        word_count = len(content.split())
        specificity = min(1.0, word_count / 20.0)
        
        # Ajustar por fuentes de memoria
        if source_memories:
            memory_factor = min(1.0, len(source_memories) / 5.0)
            return (specificity + memory_factor) / 2.0
        
        return specificity
    
    def _calculate_content_complexity(self, content: str) -> float:
        """Calcula la complejidad de un contenido."""
        # Factores de complejidad
        word_count = len(content.split())
        unique_words = len(set(content.lower().split()))
        sentence_count = len([s for s in content.split('.') if s.strip()])
        
        # Palabras complejas (más de 6 letras)
        complex_words = len([w for w in content.split() if len(w) > 6])
        
        # Normalizar factores
        word_factor = min(1.0, word_count / 30.0)
        diversity_factor = unique_words / max(1, word_count)
        sentence_factor = min(1.0, sentence_count / 5.0)
        complexity_factor = min(1.0, complex_words / max(1, word_count))
        
        return (word_factor + diversity_factor + sentence_factor + complexity_factor) / 4.0
    
    def _calculate_content_novelty(self, content: str) -> float:
        """Calcula la novedad de un contenido comparándolo con memoria."""
        # Buscar contenido similar en memoria
        keywords = content.split()[:5]
        similar_memories = self.brain.memory.retrieve_context(keywords)
        
        # Más memorias similares = menor novedad
        similarity_factor = len(similar_memories) / 20.0  # Normalizar por 20 memorias
        novelty = max(0.1, 1.0 - similarity_factor)
        
        # Bonus por palabras únicas
        unique_words = set(re.findall(r'\w{4,}', content.lower()))
        if self.brain.learning_system:
            known_words = set(self.brain.learning_system.associations.keys())
            new_words = unique_words - known_words
            novelty += len(new_words) * 0.1
        
        return min(1.0, novelty)
    
    def _save_representation(self, representation: MentalRepresentation):
        """Guarda una representación mental en disco."""
        try:
            filename = f"repr_{representation.id}.json"
            filepath = os.path.join(self.representations_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(representation.to_dict(), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[CognitiveImaginationEngine] Error guardando representación: {e}")
    
    def _save_scenario(self, scenario: Dict[str, Any]):
        """Guarda un escenario en disco."""
        try:
            filename = f"scenario_{scenario['id']}.json"
            filepath = os.path.join(self.scenarios_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scenario, f, indent=2, ensure_ascii=False)
                
            # También registrar en el diario de reflexiones
            self.brain.diario_reflexion.add_reflection(
                content={
                    "type": f"imaginación_{scenario['type']}",
                    "content": scenario["content"],
                    "emotional_valence": scenario.get("emotional_valence", 0.0),
                    "focus_signals": [f"imaginación:{scenario['type']}"]
                },
                importance=min(3, max(1, int(scenario.get("novelty", 0.5) * 3))),
                priority=2
            )
                
        except Exception as e:
            print(f"[CognitiveImaginationEngine] Error guardando escenario: {e}")
    
    def _save_insight(self, insight: Dict[str, Any]):
        """Guarda un insight en disco."""
        try:
            filename = f"insight_{insight['id']}.json"
            filepath = os.path.join(self.insights_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(insight, f, indent=2, ensure_ascii=False)
                
            # Registrar insight en memoria principal con alta importancia
            self.brain.memory.store(
                data=f"Insight: {insight.get('content', 'Patrón descubierto')}",
                importance=3,
                context={
                    "type": "cognitive_insight",
                    "insight_type": insight["type"],
                    "source": "imagination_engine"
                }
            )
                
        except Exception as e:
            print(f"[CognitiveImaginationEngine] Error guardando insight: {e}")
    
    def get_imagination_stats(self) -> Dict[str, Any]:
        """Devuelve estadísticas del motor de imaginación."""
        return {
            "active": self.active,
            "imagination_intensity": self.imagination_intensity,
            "creative_tension": self.creative_tension,
            "focus_coherence": self.focus_coherence,
            "active_representations": len(self.active_representations),
            "scenarios_generated": self.scenarios_generated,
            "representations_created": self.representations_created,
            "insights_discovered": self.insights_discovered,
            "files": {
                "scenarios": len([f for f in os.listdir(self.scenarios_dir) if f.endswith('.json')]) if os.path.exists(self.scenarios_dir) else 0,
                "representations": len([f for f in os.listdir(self.representations_dir) if f.endswith('.json')]) if os.path.exists(self.representations_dir) else 0,
                "insights": len([f for f in os.listdir(self.insights_dir) if f.endswith('.json')]) if os.path.exists(self.insights_dir) else 0
            }
        }
    
    def search_imagination_records(self, keywords: List[str], record_type: str = "all") -> List[Dict[str, Any]]:
        """Busca en los registros de imaginación."""
        results = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        try:
            # Buscar en escenarios
            if record_type in ["all", "scenarios"]:
                for filename in os.listdir(self.scenarios_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.scenarios_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            content = data.get("content", "").lower()
                            if any(kw in content for kw in keywords_lower):
                                data["record_type"] = "scenario"
                                results.append(data)
            
            # Buscar en representaciones
            if record_type in ["all", "representations"]:
                for filename in os.listdir(self.representations_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.representations_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            content = data.get("content", "").lower()
                            if any(kw in content for kw in keywords_lower):
                                data["record_type"] = "representation"
                                results.append(data)
            
            # Buscar en insights
            if record_type in ["all", "insights"]:
                for filename in os.listdir(self.insights_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.insights_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            content = data.get("content", "").lower()
                            if any(kw in content for kw in keywords_lower):
                                data["record_type"] = "insight"
                                results.append(data)
        
        except Exception as e:
            print(f"[CognitiveImaginationEngine] Error buscando registros: {e}")
        
        # Ordenar por timestamp
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return results
    
    def cleanup_old_records(self, days_old: int = 30):
        """Limpia registros antiguos para mantener el sistema eficiente."""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cutoff_iso = cutoff_date.isoformat()
        
        cleaned = {"scenarios": 0, "representations": 0, "insights": 0}
        
        try:
            # Limpiar escenarios antiguos
            for filename in os.listdir(self.scenarios_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.scenarios_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if data.get("timestamp", "") < cutoff_iso:
                                os.remove(filepath)
                                cleaned["scenarios"] += 1
                    except:
                        continue
            
            # Limpiar representaciones antiguas (mantener solo las de alta activación)
            for filename in os.listdir(self.representations_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.representations_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if (data.get("timestamp", "") < cutoff_iso and 
                                data.get("activation_level", 0) < 0.3):
                                os.remove(filepath)
                                cleaned["representations"] += 1
                    except:
                        continue
            
            # Los insights son valiosos, solo limpiar los muy antiguos y de baja confianza
            very_old_cutoff = (datetime.now() - timedelta(days=days_old * 2)).isoformat()
            for filename in os.listdir(self.insights_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.insights_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if (data.get("timestamp", "") < very_old_cutoff and 
                                data.get("confidence", 1.0) < 0.3):
                                os.remove(filepath)
                                cleaned["insights"] += 1
                    except:
                        continue
        
        except Exception as e:
            print(f"[CognitiveImaginationEngine] Error en limpieza: {e}")
        
        total_cleaned = sum(cleaned.values())
        if total_cleaned > 0:
            print(f"[CognitiveImaginationEngine] Limpieza completada: {cleaned}")
        
        return cleaned


# ===============================================================================
# INTEGRACIÓN CON BACKGROUND_THINKING
# ===============================================================================

def integrate_imagination_with_background_thinking():
    """
    Función para mostrar cómo integrar el motor de imaginación con BackgroundThinker.
    
    Agregar al BackgroundThinker.__init__():
    
    from cognitive_imagination import CognitiveImaginationEngine
    self.imagination_engine = CognitiveImaginationEngine(brain)
    self.imagination_engine.activate(intensity=0.6)
    
    Agregar al _thinking_loop() estos intervalos:
    
    self.intervals['imagination_cycle'] = 120  # Cada 2 minutos
    self.intervals['imagination_cleanup'] = 3600  # Cada hora
    
    Y estos métodos:
    """
    pass

# Métodos para BackgroundThinker
def _run_imagination_cycle(self):
    """Ejecuta un ciclo de imaginación (agregar a BackgroundThinker)."""
    try:
        if hasattr(self.brain, 'imagination_engine'):
            cycle_results = self.brain.imagination_engine.run_imagination_cycle()
            
            # Ajustar momentum basado en resultados
            if cycle_results.get("scenarios_generated", 0) > 0:
                self.thinking_momentum += 0.15
            
            if cycle_results.get("insights_discovered", 0) > 0:
                self.thinking_momentum += 0.25
                # Trigger emocional por insight
                self._trigger_emotional_response("insight")
            
            # Ajustar curiosidad
            if cycle_results.get("emotional_impact", 0) != 0:
                self.curiosity_buildup += abs(cycle_results["emotional_impact"]) * 0.1
                
    except Exception:
        pass

def _maintain_imagination_system(self):
    """Mantiene el sistema de imaginación (agregar a BackgroundThinker)."""
    try:
        if hasattr(self.brain, 'imagination_engine'):
            # Activar/desactivar según estado cognitivo
            if self.thinking_momentum > 0.7 and not self.brain.imagination_engine.active:
                self.brain.imagination_engine.activate(intensity=0.8)
            elif self.thinking_momentum < 0.3 and self.brain.imagination_engine.active:
                self.brain.imagination_engine.deactivate()
            
            # Ajustar intensidad según momentum
            if self.brain.imagination_engine.active:
                new_intensity = max(0.2, min(1.0, self.thinking_momentum))
                self.brain.imagination_engine.imagination_intensity = new_intensity
            
            # Limpieza periódica
            if random.random() < 0.1:  # 10% de probabilidad cada llamada
                self.brain.imagination_engine.cleanup_old_records()
                
    except Exception:
        pass


# ===============================================================================
# COMANDOS PARA MODO INTERACTIVO
# ===============================================================================

def add_imagination_commands_to_interactive_mode():
    """
    Comandos para agregar al modo interactivo de main.py:
    
    imagination_stats    -> estadísticas del motor de imaginación
    imagine: <tema>      -> forzar generación de escenario sobre tema
    search_imagination: <palabras> -> buscar en registros de imaginación
    representations      -> mostrar representaciones activas
    insights             -> mostrar insights recientes
    cleanup_imagination  -> limpiar registros antiguos
    activate_imagination -> activar motor de imaginación
    deactivate_imagination -> desactivar motor de imaginación
    """
    
    # Ejemplo de implementaciones:
    imagination_commands = """
    elif cmd == "imagination_stats":
        if hasattr(brain, 'imagination_engine'):
            stats = brain.imagination_engine.get_imagination_stats()
            print(f"\\n🎨 Estadísticas del Motor de Imaginación:")
            print(f"   - Estado: {'✅ Activo' if stats['active'] else '❌ Inactivo'}")
            print(f"   - Intensidad: {stats['imagination_intensity']:.2f}")
            print(f"   - Tensión creativa: {stats['creative_tension']:.2f}")
            print(f"   - Coherencia de foco: {stats['focus_coherence']:.2f}")
            print(f"   - Representaciones activas: {stats['active_representations']}")
            print(f"   - Escenarios generados: {stats['scenarios_generated']}")
            print(f"   - Insights descubiertos: {stats['insights_discovered']}")
            print(f"   - Archivos guardados:")
            print(f"     - Escenarios: {stats['files']['scenarios']}")
            print(f"     - Representaciones: {stats['files']['representations']}")
            print(f"     - Insights: {stats['files']['insights']}")
        else:
            print("❌ Motor de imaginación no disponible")
    
    elif cmd.startswith("imagine:"):
        if hasattr(brain, 'imagination_engine'):
            tema = user_input[8:].strip()
            if tema:
                # Crear representación del tema
                repr = brain.imagination_engine.create_mental_representation(tema)
                # Generar escenario
                scenario = brain.imagination_engine.generate_imaginative_scenario("creative_synthesis")
                if scenario:
                    print(f"\\n🎭 Escenario imaginado ({scenario['type']}):")
                    print(f"   {scenario['content']}")
                    print(f"   Valencia emocional: {scenario.get('emotional_valence', 0):.2f}")
                    print(f"   Novedad: {scenario.get('novelty', 0):.2f}")
                else:
                    print("⚠️ No se pudo generar escenario")
            else:
                print("⚠️ Proporciona un tema para imaginar")
        else:
            print("❌ Motor de imaginación no disponible")
    
    elif cmd.startswith("search_imagination:"):
        if hasattr(brain, 'imagination_engine'):
            palabras = user_input[19:].strip().split()
            if palabras:
                results = brain.imagination_engine.search_imagination_records(palabras)
                print(f"\\n🔍 Búsqueda en imaginación: {palabras}")
                print(f"   Encontrados {len(results)} resultados:")
                for i, result in enumerate(results[:5], 1):
                    tipo = result.get('record_type', 'unknown')
                    contenido = result.get('content', 'N/A')[:60]
                    timestamp = result.get('timestamp', '')[:10]
                    print(f"   {i}. [{tipo}] {contenido}... ({timestamp})")
                if len(results) > 5:
                    print(f"   ... y {len(results) - 5} resultados más")
            else:
                print("⚠️ Proporciona palabras para buscar")
        else:
            print("❌ Motor de imaginación no disponible")
    """
    
    return imagination_commands


# ===============================================================================
# FUNCIÓN DE INTEGRACIÓN PRINCIPAL
# ===============================================================================

def integrate_cognitive_imagination_to_eva(brain):
    """
    Integra el sistema cognitivo-emocional al cerebro EVA.
    Llamar desde DigitalBrain.__init__() después de inicializar otros sistemas.
    """
    try:
        # Crear motor de imaginación
        brain.imagination_engine = CognitiveImaginationEngine(brain)
        
        # Activar con intensidad moderada
        brain.imagination_engine.activate(intensity=0.6)
        
        # Integrar con BackgroundThinker si está disponible
        if hasattr(brain, 'background_thinker') and brain.background_thinker:
            # Agregar intervalos de imaginación
            brain.background_thinker.intervals['imagination_cycle'] = 120
            brain.background_thinker.intervals['imagination_cleanup'] = 3600
            
            # Agregar métodos (esto requiere modificar BackgroundThinker)
            # brain.background_thinker._run_imagination_cycle = _run_imagination_cycle.__get__(brain.background_thinker)
            # brain.background_thinker._maintain_imagination_system = _maintain_imagination_system.__get__(brain.background_thinker)
        
        print("   - Motor de Imaginación Cognitiva: ✅")
        return True
        
    except Exception as e:
        print(f"   - Motor de Imaginación Cognitiva: ❌ Error: {e}")
        return False