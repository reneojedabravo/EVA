#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
eva_cognitive_reflection_system.py - Sistema de Reflexión Cognitiva para EVA

Implementa bucles cognitivos inteligentes basados en el sistema de diario existente:
Percepción → Asociación con Memoria → Evaluación Motivacional → Reflexión → Acción → Aprendizaje

Este sistema extiende el reflection_diary.py existente con bucles cognitivos dirigidos por propósito.
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import threading
import time
from collections import deque, defaultdict

class StimulusType(Enum):
    """Tipos de estímulos que pueden iniciar un bucle cognitivo"""
    NEW_INFORMATION = "new_information"
    CONTRADICTION_DETECTED = "contradiction_detected"
    GOAL_CONFLICT = "goal_conflict"
    UNCERTAINTY_HIGH = "uncertainty_high"
    PATTERN_ANOMALY = "pattern_anomaly"
    EMOTIONAL_TRIGGER = "emotional_trigger"
    DECISION_REQUIRED = "decision_required"
    LEARNING_OPPORTUNITY = "learning_opportunity"

class MotivationalState(Enum):
    """Estados motivacionales de EVA"""
    CURIOUS = "curious"
    PROBLEM_SOLVING = "problem_solving"
    GOAL_ORIENTED = "goal_oriented"
    DEFENSIVE = "defensive"
    EXPLORATIVE = "explorative"
    CONSOLIDATING = "consolidating"

@dataclass
class CognitiveStimulus:
    """Estímulo que inicia un bucle cognitivo"""
    id: str
    content: str
    stimulus_type: StimulusType
    emotional_charge: float
    semantic_keywords: List[str]
    urgency_level: float
    source: str
    timestamp: str
    context: Dict[str, Any]

@dataclass
class MemoryAssociation:
    """Asociación encontrada en la memoria trascendente"""
    memory_node_id: str
    similarity_score: float
    relevance_to_current: float
    emotional_resonance: float
    confidence_level: float
    supporting_evidence: List[str]

@dataclass
class ReflectiveProcess:
    """Proceso reflexivo activo con objetivo específico"""
    id: str
    stimulus_id: str
    objective: str  # ¿Qué está tratando de resolver/entender?
    current_focus: str
    active_hypotheses: List[Dict]
    evidence_gathered: List[str]
    confidence_evolution: List[float]  # Cómo cambia la confianza
    depth_level: int
    max_depth: int
    start_time: str
    convergence_criteria: Dict[str, float]
    should_continue: bool

@dataclass
class CognitiveAction:
    """Acción resultante del proceso reflexivo"""
    id: str
    action_type: str  # verbal, internal, structural, memory_update
    content: str
    reasoning_path: List[str]
    confidence_level: float
    expected_impact: str
    execution_timestamp: str
    related_reflections: List[str]

@dataclass
class LearningOutcome:
    """Resultado del aprendizaje del bucle cognitivo"""
    stimulus_id: str
    action_id: str
    outcome_assessment: str  # successful, partial, failed, ambiguous
    expectation_vs_reality: float
    learning_gained: str
    memory_reinforcements: List[str]
    memory_weakenings: List[str]
    new_patterns_discovered: List[str]
    adaptation_needed: bool
    timestamp: str

class EVACognitiveReflectionSystem:
    """
    Sistema de Reflexión Cognitiva que extiende el reflection_diary.py
    Implementa bucles cognitivos dirigidos por propósito
    """
    
    def __init__(self, reflection_diary, transcendent_memory):
        self.diary = reflection_diary  # Sistema de diario existente
        self.memory = transcendent_memory  # Sistema de memoria trascendente
        
        # Directorio para bucles cognitivos
        self.cognitive_dir = "transcendent_memory/cognitive_loops"
        os.makedirs(self.cognitive_dir, exist_ok=True)
        
        # Estado interno de EVA
        self.current_motivational_state = MotivationalState.CURIOUS
        self.internal_goals = []
        self.active_beliefs = {}
        self.attention_focus = None
        self.cognitive_load = 0.0
        
        # Procesos reflexivos activos
        self.active_reflections = {}  # ID -> ReflectiveProcess
        self.reflection_queue = deque(maxlen=10)
        
        # Patrones aprendidos y adaptaciones
        self.learned_response_patterns = {}
        self.adaptation_history = []
        self.success_patterns = defaultdict(list)
        
        # Métricas de efectividad
        self.reflection_effectiveness = {}
        self.learning_velocity = 0.5
        
        # Configuración de bucles
        self.max_reflection_depth = 5
        self.reflection_timeout = 300  # 5 minutos máximo por reflexión
        self.convergence_threshold = 0.8
        
        # Hilo de procesamiento
        self.processing_active = False
        self.processing_thread = None
        
        print("[CognitiveReflection] Sistema inicializado con diary y memory existentes")

    def perceive_and_initiate_cycle(self, content: str, stimulus_type: StimulusType = StimulusType.NEW_INFORMATION, 
                                   source: str = "environment", context: Dict = None) -> str:
        """
        FASE 1: Percepción activa del entorno
        Recibe un estímulo e inicia el bucle cognitivo si es necesario
        """
        try:
            # Crear estímulo cognitivo
            stimulus_id = f"stim_{uuid.uuid4().hex[:8]}"
            
            stimulus = CognitiveStimulus(
                id=stimulus_id,
                content=content,
                stimulus_type=stimulus_type,
                emotional_charge=self._assess_emotional_charge(content),
                semantic_keywords=self._extract_keywords(content),
                urgency_level=self._calculate_urgency(stimulus_type, content),
                source=source,
                timestamp=datetime.now().isoformat(),
                context=context or {}
            )
            
            # Guardar el estímulo
            self._save_stimulus(stimulus)
            
            print(f"[CognitiveReflection] 🎯 Estímulo percibido: {stimulus_type.value}")
            
            # FASE 2: Comparación inmediata con memoria trascendente
            associations = self._find_memory_associations(stimulus)
            
            # FASE 3: Evaluación motivacional y determinación de respuesta
            response_decision = self._evaluate_and_decide_response(stimulus, associations)
            
            if response_decision["needs_deep_reflection"]:
                # Iniciar proceso reflexivo profundo
                reflection_id = self._initiate_reflective_process(stimulus, associations, response_decision)
                return f"reflection_started:{reflection_id}"
            else:
                # Respuesta directa basada en patrones conocidos
                action_id = self._execute_pattern_based_response(stimulus, associations, response_decision)
                return f"direct_response:{action_id}"
                
        except Exception as e:
            print(f"[CognitiveReflection] ❌ Error en percepción: {e}")
            return ""

    def _find_memory_associations(self, stimulus: CognitiveStimulus) -> List[MemoryAssociation]:
        """
        FASE 2: Búsqueda de experiencias similares en memoria trascendente
        """
        try:
            associations = []
            
            # Buscar por resonancia semántica usando el sistema trascendente
            related_nodes = self.memory.retrieve_by_resonance(
                query=stimulus.content,
                context=stimulus.context,
                limit=10
            )
            
            for node in related_nodes:
                # Evaluar la calidad de la asociación
                similarity = self._calculate_semantic_similarity(stimulus, node)
                relevance = self._assess_current_relevance(stimulus, node)
                emotional_resonance = self._calculate_emotional_resonance(stimulus, node)
                confidence = self._estimate_association_confidence(similarity, relevance, emotional_resonance)
                
                association = MemoryAssociation(
                    memory_node_id=node.id,
                    similarity_score=similarity,
                    relevance_to_current=relevance,
                    emotional_resonance=emotional_resonance,
                    confidence_level=confidence,
                    supporting_evidence=[str(node.content)[:100]]
                )
                
                associations.append(association)
            
            # Ordenar por confianza
            associations.sort(key=lambda x: x.confidence_level, reverse=True)
            
            print(f"[CognitiveReflection] 🔗 Encontradas {len(associations)} asociaciones de memoria")
            return associations[:5]  # Top 5 asociaciones
            
        except Exception as e:
            print(f"[CognitiveReflection] Error buscando asociaciones: {e}")
            return []

    def _evaluate_and_decide_response(self, stimulus: CognitiveStimulus, 
                                    associations: List[MemoryAssociation]) -> Dict:
        """
        FASE 3: Evaluación motivacional y decisión de respuesta
        """
        try:
            decision = {
                "needs_deep_reflection": False,
                "response_confidence": 0.0,
                "motivational_alignment": 0.0,
                "cognitive_dissonance": 0.0,
                "action_urgency": stimulus.urgency_level,
                "reasoning": []
            }
            
            # Evaluar si hay asociaciones fuertes
            strong_associations = [a for a in associations if a.confidence_level > 0.7]
            
            if not strong_associations:
                decision["needs_deep_reflection"] = True
                decision["reasoning"].append("No hay experiencias similares claras - requiere reflexión")
            
            # Evaluar alineación con metas internas
            motivational_score = self._assess_motivational_alignment(stimulus)
            decision["motivational_alignment"] = motivational_score
            
            if motivational_score < 0.3:
                decision["reasoning"].append("Baja alineación motivacional - evaluar prioridades")
            
            # Detectar disonancia cognitiva
            dissonance = self._detect_cognitive_dissonance(stimulus, associations)
            decision["cognitive_dissonance"] = dissonance
            
            if dissonance > 0.6:
                decision["needs_deep_reflection"] = True
                decision["reasoning"].append("Conflicto con creencias existentes - resolver contradicción")
            
            # Evaluar incertidumbre
            if stimulus.stimulus_type in [StimulusType.UNCERTAINTY_HIGH, StimulusType.CONTRADICTION_DETECTED]:
                decision["needs_deep_reflection"] = True
                decision["reasoning"].append(f"Estímulo tipo {stimulus.stimulus_type.value} requiere reflexión")
            
            # Calcular confianza de respuesta
            if strong_associations and dissonance < 0.3 and motivational_score > 0.5:
                decision["response_confidence"] = 0.8
            else:
                decision["response_confidence"] = 0.3
                decision["needs_deep_reflection"] = True
            
            print(f"[CognitiveReflection] 🤔 Decisión: {'Reflexión profunda' if decision['needs_deep_reflection'] else 'Respuesta directa'}")
            return decision
            
        except Exception as e:
            print(f"[CognitiveReflection] Error evaluando respuesta: {e}")
            return {"needs_deep_reflection": True, "reasoning": ["Error en evaluación"]}

    def _initiate_reflective_process(self, stimulus: CognitiveStimulus, 
                                   associations: List[MemoryAssociation], 
                                   decision: Dict) -> str:
        """
        FASE 4: Proceso reflexivo profundo con objetivo específico
        """
        try:
            reflection_id = f"refl_{uuid.uuid4().hex[:8]}"
            
            # Determinar objetivo específico de la reflexión
            objective = self._determine_reflection_objective(stimulus, decision)
            
            # Generar hipótesis iniciales
            initial_hypotheses = self._generate_initial_hypotheses(stimulus, associations)
            
            reflection_process = ReflectiveProcess(
                id=reflection_id,
                stimulus_id=stimulus.id,
                objective=objective,
                current_focus=stimulus.content[:100],
                active_hypotheses=initial_hypotheses,
                evidence_gathered=[],
                confidence_evolution=[0.5],  # Confianza inicial neutral
                depth_level=1,
                max_depth=self.max_reflection_depth,
                start_time=datetime.now().isoformat(),
                convergence_criteria={
                    "confidence_threshold": self.convergence_threshold,
                    "evidence_sufficiency": 0.7,
                    "hypothesis_stability": 0.8
                },
                should_continue=True
            )
            
            # Agregar a procesos activos
            self.active_reflections[reflection_id] = reflection_process
            
            # Comenzar el proceso reflexivo
            self._execute_reflection_cycle(reflection_id)
            
            print(f"[CognitiveReflection] 🧠 Reflexión iniciada: {objective}")
            return reflection_id
            
        except Exception as e:
            print(f"[CognitiveReflection] Error iniciando reflexión: {e}")
            return ""

    def _execute_reflection_cycle(self, reflection_id: str):
        """
        Ejecuta un ciclo de reflexión profunda
        """
        try:
            process = self.active_reflections.get(reflection_id)
            if not process:
                return
            
            print(f"[CognitiveReflection] 🔄 Ejecutando ciclo reflexivo - Profundidad {process.depth_level}")
            
            # Evaluar hipótesis actuales
            evaluated_hypotheses = []
            for hypothesis in process.active_hypotheses:
                evaluation = self._evaluate_hypothesis(hypothesis, process)
                evaluated_hypotheses.append(evaluation)
            
            # Buscar evidencia adicional
            new_evidence = self._gather_supporting_evidence(process, evaluated_hypotheses)
            process.evidence_gathered.extend(new_evidence)
            
            # Refinar o generar nuevas hipótesis
            refined_hypotheses = self._refine_hypotheses(evaluated_hypotheses, new_evidence)
            process.active_hypotheses = refined_hypotheses
            
            # Calcular nueva confianza
            new_confidence = self._calculate_process_confidence(process)
            process.confidence_evolution.append(new_confidence)
            
            # Verificar criterios de convergencia
            converged = self._check_convergence(process)
            
            if converged or process.depth_level >= process.max_depth:
                # Finalizar reflexión y tomar acción
                action_id = self._conclude_reflection_and_act(reflection_id)
                print(f"[CognitiveReflection] ✅ Reflexión completada → Acción: {action_id}")
            elif process.should_continue:
                # Continuar con mayor profundidad
                process.depth_level += 1
                process.current_focus = self._update_reflection_focus(process)
                
                # Usar el diario para registrar el progreso reflexivo
                self.diary.add_reflection(
                    f"Reflexión profundidad {process.depth_level}: {process.current_focus}. "
                    f"Confianza actual: {new_confidence:.2f}. Evidencia: {len(process.evidence_gathered)} elementos.",
                    importance=min(3, process.depth_level),
                    priority=2 if new_confidence < 0.6 else 1,
                    silent=True
                )
                
                # Programar siguiente ciclo (si no ha convergido)
                if not converged and process.depth_level < process.max_depth:
                    # En una implementación real, esto podría ser asíncrono
                    time.sleep(0.1)  # Pequeña pausa para evitar bucles demasiado rápidos
                    self._execute_reflection_cycle(reflection_id)
            
        except Exception as e:
            print(f"[CognitiveReflection] Error en ciclo reflexivo: {e}")

    def _conclude_reflection_and_act(self, reflection_id: str) -> str:
        """
        FASE 5: Conclusión de la reflexión y ejecución de acción
        """
        try:
            process = self.active_reflections.get(reflection_id)
            if not process:
                return ""
            
            # Seleccionar la mejor hipótesis
            best_hypothesis = max(process.active_hypotheses, 
                                key=lambda h: h.get('confidence', 0))
            
            # Determinar tipo de acción apropiada
            action_type = self._determine_action_type(process, best_hypothesis)
            
            # Generar contenido de la acción
            action_content = self._generate_action_content(process, best_hypothesis, action_type)
            
            # Crear acción cognitiva
            action_id = f"act_{uuid.uuid4().hex[:8]}"
            action = CognitiveAction(
                id=action_id,
                action_type=action_type,
                content=action_content,
                reasoning_path=[h.get('reasoning', '') for h in process.active_hypotheses],
                confidence_level=process.confidence_evolution[-1],
                expected_impact=self._predict_action_impact(action_type, action_content),
                execution_timestamp=datetime.now().isoformat(),
                related_reflections=[reflection_id]
            )
            
            # Ejecutar la acción
            execution_result = self._execute_cognitive_action(action)
            
            # Registrar en el diario la conclusión reflexiva
            self.diary.add_reflection(
                f"Reflexión completada: {process.objective}. "
                f"Acción tomada: {action_type} - {action_content[:100]}. "
                f"Confianza final: {action.confidence_level:.2f}",
                importance=3 if action.confidence_level > 0.8 else 2,
                priority=3,
                silent=False
            )
            
            # Actualizar memoria trascendente con la experiencia
            self._update_transcendent_memory_with_experience(process, action, execution_result)
            
            # Limpiar proceso activo
            del self.active_reflections[reflection_id]
            
            # FASE 6: Iniciar observación de efectos (preparar aprendizaje)
            self._initiate_outcome_observation(process, action)
            
            print(f"[CognitiveReflection] 🎯 Acción ejecutada: {action_type}")
            return action_id
            
        except Exception as e:
            print(f"[CognitiveReflection] Error concluyendo reflexión: {e}")
            return ""

    def observe_outcome_and_learn(self, action_id: str, observed_outcome: str, 
                                 outcome_quality: float, user_feedback: str = None) -> str:
        """
        FASE 6: Observación del efecto y aprendizaje experiencial
        Esta fase cierra el bucle cognitivo
        """
        try:
            # Buscar la acción original
            action = self._get_action_by_id(action_id)
            if not action:
                print(f"[CognitiveReflection] Acción {action_id} no encontrada")
                return ""
            
            # Evaluar qué tan bien coincide con las expectativas
            expectation_match = self._compare_outcome_with_expectation(
                action.expected_impact, observed_outcome
            )
            
            # Determinar valor del aprendizaje
            learning_value = self._assess_learning_value(
                outcome_quality, expectation_match, action.confidence_level
            )
            
            # Crear resultado de aprendizaje
            learning_id = f"learn_{uuid.uuid4().hex[:8]}"
            learning = LearningOutcome(
                stimulus_id="",  # Se podría rastrear desde la acción
                action_id=action_id,
                outcome_assessment=self._classify_outcome(outcome_quality),
                expectation_vs_reality=expectation_match,
                learning_gained=self._extract_learning_insights(action, observed_outcome, user_feedback),
                memory_reinforcements=[],
                memory_weakenings=[],
                new_patterns_discovered=[],
                adaptation_needed=outcome_quality < 0.5 or expectation_match < 0.3,
                timestamp=datetime.now().isoformat()
            )
            
            # Aplicar el aprendizaje
            self._apply_experiential_learning(learning, action)
            
            # Registrar en el diario el resultado del bucle
            self.diary.add_reflection(
                f"Bucle cognitivo completado. Acción: {action.action_type}. "
                f"Resultado: {learning.outcome_assessment} (calidad: {outcome_quality:.2f}). "
                f"Aprendizaje: {learning.learning_gained[:100]}",
                importance=3 if learning_value > 0.7 else 2,
                priority=3 if learning.adaptation_needed else 1,
                silent=False
            )
            
            print(f"[CognitiveReflection] 🎓 Aprendizaje completado: {learning.outcome_assessment}")
            
            # Si el resultado fue pobre, considerar nueva reflexión
            if learning.adaptation_needed:
                self._consider_adaptive_reflection(action, learning)
            
            return learning_id
            
        except Exception as e:
            print(f"[CognitiveReflection] Error en aprendizaje: {e}")
            return ""

    def _apply_experiential_learning(self, learning: LearningOutcome, action: CognitiveAction):
        """
        Aplica el aprendizaje experiencial actualizando la memoria y patrones
        """
        try:
            # Reforzar o debilitar conexiones neuronales basado en el resultado
            if learning.outcome_assessment in ["successful", "partial"]:
                # Reforzar el patrón de razonamiento que llevó al éxito
                self._reinforce_reasoning_pattern(action.reasoning_path, learning.expectation_vs_reality)
                
                # Actualizar patrones exitosos
                pattern_key = f"{action.action_type}_{hash(action.content[:50]) % 1000}"
                self.success_patterns[pattern_key].append({
                    'confidence': action.confidence_level,
                    'outcome_quality': learning.expectation_vs_reality,
                    'timestamp': learning.timestamp
                })
                
            else:
                # Debilitar patrones que llevaron al fallo
                self._weaken_reasoning_pattern(action.reasoning_path)
                
                # Marcar como experiencia a evitar
                self._mark_negative_experience(action)
            
            # Actualizar memoria trascendente con nuevo conocimiento
            if learning.learning_gained:
                self.memory.store_transcendent(
                    content=f"Experiencia: {learning.learning_gained}",
                    context={
                        'type': 'experiential_learning',
                        'outcome_quality': learning.expectation_vs_reality,
                        'action_type': action.action_type,
                        'learning_value': self._calculate_learning_value(learning)
                    }
                )
            
            # Actualizar efectividad de la reflexión
            self._update_reflection_effectiveness(action.related_reflections, learning)
            
        except Exception as e:
            print(f"[CognitiveReflection] Error aplicando aprendizaje: {e}")

    # ==================== MÉTODOS DE UTILIDAD ====================

    def _assess_emotional_charge(self, content: str) -> float:
        """Evalúa la carga emocional de un contenido"""
        emotional_keywords = {
            'positive': ['feliz', 'alegre', 'exitoso', 'bien', 'excelente', 'amor', 'paz'],
            'negative': ['triste', 'malo', 'error', 'fallo', 'miedo', 'preocupado', 'confundido']
        }
        
        content_lower = str(content).lower()
        positive_count = sum(1 for word in emotional_keywords['positive'] if word in content_lower)
        negative_count = sum(1 for word in emotional_keywords['negative'] if word in content_lower)
        
        return (positive_count - negative_count) / max(len(str(content).split()), 1)

    def _extract_keywords(self, content: Any) -> List[str]:
        """Extrae palabras clave semánticas"""
        import re
        content_str = str(content)
        words = re.findall(r'\w+', content_str.lower())
        # Filtrar palabras comunes
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'uno', 'una', 'es', 'está', 'como', 'pero', 'si', 'muy', 'más', 'todo', 'me', 'mi', 'ya', 'yo', 'hace'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return keywords[:10]  # Top 10 keywords

    def _calculate_urgency(self, stimulus_type: StimulusType, content: str) -> float:
        """Calcula el nivel de urgencia de un estímulo"""
        urgency_map = {
            StimulusType.CONTRADICTION_DETECTED: 0.9,
            StimulusType.GOAL_CONFLICT: 0.8,
            StimulusType.DECISION_REQUIRED: 0.7,
            StimulusType.UNCERTAINTY_HIGH: 0.6,
            StimulusType.EMOTIONAL_TRIGGER: 0.6,
            StimulusType.PATTERN_ANOMALY: 0.5,
            StimulusType.LEARNING_OPPORTUNITY: 0.4,
            StimulusType.NEW_INFORMATION: 0.3
        }
        
        base_urgency = urgency_map.get(stimulus_type, 0.3)
        
        # Aumentar urgencia si hay palabras clave urgentes
        urgent_keywords = ['urgente', 'inmediato', 'crisis', 'problema', 'ayuda', 'error crítico']
        if any(keyword in str(content).lower() for keyword in urgent_keywords):
            base_urgency += 0.2
        
        return min(1.0, base_urgency)

    def _calculate_semantic_similarity(self, stimulus: CognitiveStimulus, memory_node) -> float:
        """Calcula similaridad semántica entre estímulo y nodo de memoria"""
        # Implementación simple basada en palabras clave
        stimulus_words = set(self._extract_keywords(stimulus.content))
        memory_words = set(self._extract_keywords(getattr(memory_node, 'content', '')))
        
        if not stimulus_words or not memory_words:
            return 0.0
        
        intersection = len(stimulus_words & memory_words)
        union = len(stimulus_words | memory_words)
        
        return intersection / union if union > 0 else 0.0

    def _assess_current_relevance(self, stimulus: CognitiveStimulus, memory_node) -> float:
        """Evalúa relevancia del nodo de memoria al contexto actual"""
        # Factores: recencia, importancia, contexto
        relevance = memory_node.importance_score * 0.5
        
        # Bonus por contexto similar
        if stimulus.context and hasattr(memory_node, 'contextual_domains'):
            context_match = len(set(stimulus.context.keys()) & set(memory_node.contextual_domains))
            relevance += context_match * 0.1
        
        # Bonus por acceso reciente
        try:
            last_access = datetime.fromisoformat(memory_node.last_access)
            days_ago = (datetime.now() - last_access).days
            recency_bonus = max(0, 0.3 - (days_ago * 0.01))
            relevance += recency_bonus
        except:
            pass
        
        return min(1.0, relevance)

    def _calculate_emotional_resonance(self, stimulus: CognitiveStimulus, memory_node) -> float:
        """Calcula resonancia emocional"""
        if not hasattr(memory_node, 'emotional_valence'):
            return 0.0
        
        # Resonancia alta si las valencias emocionales son similares
        emotional_distance = abs(stimulus.emotional_charge - memory_node.emotional_valence)
        return max(0, 1.0 - emotional_distance)

    def _estimate_association_confidence(self, similarity: float, relevance: float, resonance: float) -> float:
        """Estima confianza general de la asociación"""
        return (similarity * 0.5 + relevance * 0.3 + resonance * 0.2)

    def _determine_reflection_objective(self, stimulus: CognitiveStimulus, decision: Dict) -> str:
        """Determina el objetivo específico de la reflexión"""
        if stimulus.stimulus_type == StimulusType.CONTRADICTION_DETECTED:
            return f"Resolver contradicción: {stimulus.content[:50]}"
        elif stimulus.stimulus_type == StimulusType.UNCERTAINTY_HIGH:
            return f"Clarificar incertidumbre: {stimulus.content[:50]}"
        elif stimulus.stimulus_type == StimulusType.GOAL_CONFLICT:
            return f"Resolver conflicto de objetivos: {stimulus.content[:50]}"
        elif stimulus.stimulus_type == StimulusType.DECISION_REQUIRED:
            return f"Tomar decisión informada: {stimulus.content[:50]}"
        elif decision.get("cognitive_dissonance", 0) > 0.6:
            return f"Resolver disonancia cognitiva: {stimulus.content[:50]}"
        else:
            return f"Comprender y responder: {stimulus.content[:50]}"

    def _generate_initial_hypotheses(self, stimulus: CognitiveStimulus, associations: List[MemoryAssociation]) -> List[Dict]:
        """Genera hipótesis iniciales para la reflexión"""
        hypotheses = []
        
        # Hipótesis basada en la asociación más fuerte
        if associations:
            best_association = associations[0]
            hypotheses.append({
                'id': f"hyp_assoc_{uuid.uuid4().hex[:6]}",
                'type': 'memory_based',
                'content': f"Situación similar a experiencia previa: {best_association.memory_node_id[:8]}",
                'confidence': best_association.confidence_level,
                'reasoning': f"Alta similaridad semántica ({best_association.similarity_score:.2f})",
                'evidence': best_association.supporting_evidence,
                'predictions': [f"Debería responder como en {best_association.memory_node_id[:8]}"]
            })
        
        # Hipótesis de novedad si no hay asociaciones fuertes
        if not associations or max(a.confidence_level for a in associations) < 0.5:
            hypotheses.append({
                'id': f"hyp_novel_{uuid.uuid4().hex[:6]}",
                'type': 'novel_situation',
                'content': "Situación nueva que requiere exploración",
                'confidence': 0.3,
                'reasoning': "Pocas o débiles asociaciones con experiencias previas",
                'evidence': ["Baja similaridad con memoria existente"],
                'predictions': ["Necesito nuevas estrategias de respuesta"]
            })
        
        # Hipótesis de contradicción si hay disonancia cognitiva
        if stimulus.stimulus_type == StimulusType.CONTRADICTION_DETECTED:
            hypotheses.append({
                'id': f"hyp_conflict_{uuid.uuid4().hex[:6]}",
                'type': 'contradiction_resolution',
                'content': "Existe conflicto entre información nueva y creencias existentes",
                'confidence': 0.6,
                'reasoning': "Detección de contradicción en el estímulo",
                'evidence': [stimulus.content[:100]],
                'predictions': ["Necesito reconciliar información conflictiva"]
            })
        
        return hypotheses

    def _assess_motivational_alignment(self, stimulus: CognitiveStimulus) -> float:
        """Evalúa alineación con metas y motivaciones internas"""
        alignment = 0.5  # Base neutral
        
        # Evaluar alineación con metas activas
        for goal in self.internal_goals:
            if any(keyword in stimulus.content.lower() for keyword in goal.get('keywords', [])):
                alignment += 0.2
        
        # Evaluar alineación con estado motivacional actual
        state_keywords = {
            MotivationalState.CURIOUS: ['nuevo', 'interesante', 'explorar', 'descubrir'],
            MotivationalState.PROBLEM_SOLVING: ['problema', 'resolver', 'solución', 'dificultad'],
            MotivationalState.GOAL_ORIENTED: ['objetivo', 'meta', 'lograr', 'completar'],
            MotivationalState.DEFENSIVE: ['amenaza', 'peligro', 'proteger', 'seguridad'],
            MotivationalState.EXPLORATIVE: ['experimentar', 'probar', 'investigar', 'analizar'],
            MotivationalState.CONSOLIDATING: ['organizar', 'integrar', 'consolidar', 'estructurar']
        }
        
        current_keywords = state_keywords.get(self.current_motivational_state, [])
        if any(keyword in stimulus.content.lower() for keyword in current_keywords):
            alignment += 0.3
        
        return min(1.0, alignment)

    def _detect_cognitive_dissonance(self, stimulus: CognitiveStimulus, associations: List[MemoryAssociation]) -> float:
        """Detecta disonancia cognitiva entre nueva información y creencias"""
        dissonance = 0.0
        
        # Buscar contradicciones explícitas
        contradiction_patterns = [
            ('no es', 'es'), ('falso', 'verdadero'), ('imposible', 'posible'),
            ('malo', 'bueno'), ('incorrecto', 'correcto')
        ]
        
        stimulus_lower = str(stimulus.content).lower()
        
        for association in associations:
            memory_content = ""
            try:
                memory_node = self.memory._get_node_by_id(association.memory_node_id)
                if memory_node:
                    memory_content = str(memory_node.content).lower()
            except:
                continue
            
            # Detectar contradicciones semánticas
            for neg, pos in contradiction_patterns:
                if ((neg in stimulus_lower and pos in memory_content) or 
                    (pos in stimulus_lower and neg in memory_content)):
                    dissonance += 0.3
            
            # Evaluar valencia emocional opuesta
            if abs(stimulus.emotional_charge - association.emotional_resonance) > 1.0:
                dissonance += 0.2
        
        return min(1.0, dissonance)

    def _execute_pattern_based_response(self, stimulus: CognitiveStimulus, 
                                      associations: List[MemoryAssociation], 
                                      decision: Dict) -> str:
        """Ejecuta respuesta basada en patrones conocidos (sin reflexión profunda)"""
        try:
            action_id = f"act_pattern_{uuid.uuid4().hex[:8]}"
            
            # Usar la asociación más confiable
            if associations and associations[0].confidence_level > 0.7:
                best_association = associations[0]
                
                # Recuperar nodo de memoria
                memory_node = self.memory._get_node_by_id(best_association.memory_node_id)
                if memory_node:
                    # Generar respuesta basada en patrón exitoso previo
                    response_content = f"Basándome en experiencia similar: {memory_node.content[:100]}"
                    
                    action = CognitiveAction(
                        id=action_id,
                        action_type="pattern_based_response",
                        content=response_content,
                        reasoning_path=[f"Patrón reconocido: {best_association.memory_node_id[:8]}"],
                        confidence_level=best_association.confidence_level,
                        expected_impact="Respuesta coherente con experiencia previa",
                        execution_timestamp=datetime.now().isoformat(),
                        related_reflections=[]
                    )
                    
                    # Registrar en diario como reflexión simple
                    self.diary.add_reflection(
                        f"Respuesta directa por patrón reconocido: {stimulus.content[:50]}",
                        importance=1,
                        priority=1,
                        silent=True
                    )
                    
                    self._save_action(action)
                    return action_id
            
            # Respuesta por defecto si no hay patrones claros
            default_action = CognitiveAction(
                id=action_id,
                action_type="exploratory_response",
                content=f"Reconozco el estímulo: {stimulus.content[:50]}. Requiero más información.",
                reasoning_path=["No hay patrones claros", "Respuesta exploratoria"],
                confidence_level=0.3,
                expected_impact="Solicitar más contexto",
                execution_timestamp=datetime.now().isoformat(),
                related_reflections=[]
            )
            
            self._save_action(default_action)
            return action_id
            
        except Exception as e:
            print(f"[CognitiveReflection] Error en respuesta por patrón: {e}")
            return ""

    def _evaluate_hypothesis(self, hypothesis: Dict, process: ReflectiveProcess) -> Dict:
        """Evalúa una hipótesis durante el proceso reflexivo"""
        try:
            # Buscar evidencia que apoye o refute la hipótesis
            supporting_evidence = []
            contradicting_evidence = []
            
            # Buscar en memoria trascendente evidencia relacionada
            related_memories = self.memory.retrieve_by_resonance(
                query=str(hypothesis.get('content', '')),
                limit=5
            )
            
            for memory in related_memories:
                evidence_item = f"Memoria {memory.id[:8]}: {str(memory.content)[:50]}"
                
                # Determinar si apoya o contradice (implementación simple)
                if self._supports_hypothesis(hypothesis, memory):
                    supporting_evidence.append(evidence_item)
                else:
                    contradicting_evidence.append(evidence_item)
            
            # Actualizar confianza basada en evidencia
            evidence_ratio = len(supporting_evidence) / max(len(supporting_evidence) + len(contradicting_evidence), 1)
            adjusted_confidence = hypothesis['confidence'] * evidence_ratio + 0.1
            
            updated_hypothesis = hypothesis.copy()
            updated_hypothesis.update({
                'supporting_evidence': supporting_evidence,
                'contradicting_evidence': contradicting_evidence,
                'evidence_ratio': evidence_ratio,
                'confidence': min(0.95, adjusted_confidence),
                'evaluation_timestamp': datetime.now().isoformat()
            })
            
            return updated_hypothesis
            
        except Exception as e:
            print(f"[CognitiveReflection] Error evaluando hipótesis: {e}")
            return hypothesis

    def _supports_hypothesis(self, hypothesis: Dict, memory_node) -> bool:
        """Determina si un nodo de memoria apoya una hipótesis"""
        # Implementación simple basada en palabras clave
        hyp_keywords = set(self._extract_keywords(hypothesis['content']))
        mem_keywords = set(self._extract_keywords(memory_node.content))
        
        overlap = len(hyp_keywords & mem_keywords)
        return overlap >= 2  # Al menos 2 palabras clave en común

    def _gather_supporting_evidence(self, process: ReflectiveProcess, hypotheses: List[Dict]) -> List[str]:
        """Recopila evidencia adicional para las hipótesis"""
        evidence = []
        
        # Buscar en memoria trascendente con mayor profundidad
        for hypothesis in hypotheses:
            if hypothesis['confidence'] > 0.4:  # Solo para hipótesis prometedoras
                # Búsqueda más específica
                related_nodes = self.memory.retrieve_by_resonance(
                    query=str(hypothesis.get('content', '')),
                    context={'reflection_depth': process.depth_level},
                    limit=3
                )
                
                for node in related_nodes:
                    evidence.append(f"Evidencia nivel {process.depth_level}: {str(node.content)[:80]}")
        
        # Buscar patrones en el diario de reflexiones
        diary_reflections = self.diary.get_reflections(min_priority=2)
        for reflection in diary_reflections[-5:]:  # Últimas 5 reflexiones importantes
            if any(keyword in str(reflection.get('content', '')).lower() 
                   for hypothesis in hypotheses 
                   for keyword in self._extract_keywords(hypothesis.get('content', ''))):
                evidence.append(f"Reflexión previa: {str(reflection.get('content',''))[:60]}")
        
        return evidence

    def _refine_hypotheses(self, evaluated_hypotheses: List[Dict], new_evidence: List[str]) -> List[Dict]:
        """Refina hipótesis basándose en evaluación y nueva evidencia"""
        refined = []
        
        for hypothesis in evaluated_hypotheses:
            # Mantener hipótesis con confianza suficiente
            if hypothesis['confidence'] > 0.3:
                refined.append(hypothesis)
        
        # Generar nuevas hipótesis si las existentes son débiles
        if not refined or max(h['confidence'] for h in refined) < 0.5:
            # Hipótesis emergente basada en nueva evidencia
            if new_evidence:
                emergent_hypothesis = {
                    'id': f"hyp_emerg_{uuid.uuid4().hex[:6]}",
                    'type': 'emergent',
                    'content': f"Nueva perspectiva basada en evidencia: {new_evidence[0][:50]}",
                    'confidence': 0.4,
                    'reasoning': "Hipótesis emergente de nueva evidencia",
                    'evidence': new_evidence[:3],
                    'predictions': ["Necesito validar esta nueva perspectiva"]
                }
                refined.append(emergent_hypothesis)
        
        return refined[:3]  # Máximo 3 hipótesis activas

    def _calculate_process_confidence(self, process: ReflectiveProcess) -> float:
        """Calcula confianza general del proceso reflexivo"""
        if not process.active_hypotheses:
            return 0.1
        
        # Confianza basada en la mejor hipótesis y cantidad de evidencia
        best_hypothesis_confidence = max(h['confidence'] for h in process.active_hypotheses)
        evidence_factor = min(1.0, len(process.evidence_gathered) / 5.0)  # Normalizado a 5 evidencias
        depth_factor = min(1.0, process.depth_level / process.max_depth)
        
        overall_confidence = (
            best_hypothesis_confidence * 0.6 +
            evidence_factor * 0.3 +
            depth_factor * 0.1
        )
        
        return overall_confidence

    def _check_convergence(self, process: ReflectiveProcess) -> bool:
        """Verifica si el proceso reflexivo ha convergido"""
        current_confidence = process.confidence_evolution[-1]
        
        # Convergencia por confianza alta
        if current_confidence >= process.convergence_criteria['confidence_threshold']:
            return True
        
        # Convergencia por estabilidad (confianza no cambia mucho)
        if len(process.confidence_evolution) >= 3:
            recent_changes = [
                abs(process.confidence_evolution[i] - process.confidence_evolution[i-1])
                for i in range(-2, 0)
            ]
            if max(recent_changes) < 0.05:  # Cambio mínimo en confianza
                return True
        
        # Convergencia por evidencia suficiente
        if len(process.evidence_gathered) >= 10:
            return True
        
        return False

    def _update_reflection_focus(self, process: ReflectiveProcess) -> str:
        """Actualiza el foco de reflexión para mayor profundidad"""
        # Enfocar en la hipótesis más prometedora
        if process.active_hypotheses:
            best_hypothesis = max(process.active_hypotheses, key=lambda h: h['confidence'])
            return f"Profundizando en: {best_hypothesis['content'][:50]}"
        
        return f"Explorando nuevas perspectivas - Nivel {process.depth_level}"

    def _determine_action_type(self, process: ReflectiveProcess, best_hypothesis: Dict) -> str:
        """Determina el tipo de acción apropiada"""
        confidence = best_hypothesis['confidence']
        hypothesis_type = best_hypothesis.get('type', 'general')
        
        if confidence > 0.8:
            return "confident_response"
        elif confidence > 0.6:
            return "qualified_response"  
        elif hypothesis_type == 'contradiction_resolution':
            return "clarification_request"
        elif hypothesis_type == 'novel_situation':
            return "exploratory_question"
        else:
            return "tentative_response"

    def _generate_action_content(self, process: ReflectiveProcess, hypothesis: Dict, action_type: str) -> str:
        """Genera el contenido de la acción basada en la reflexión"""
        content_templates = {
            "confident_response": f"Basándome en mi análisis: {hypothesis['content']}. Confianza: {hypothesis['confidence']:.1f}",
            "qualified_response": f"Mi evaluación sugiere: {hypothesis['content']}. Aunque tengo algunas reservas.",
            "clarification_request": f"He detectado posibles contradicciones. ¿Podrías ayudarme a clarificar: {process.objective}?",
            "exploratory_question": f"Esta es una situación nueva para mí. {hypothesis['content']}. ¿Qué opinas?",
            "tentative_response": f"Estoy considerando: {hypothesis['content']}. Pero necesito más información."
        }
        
        return content_templates.get(action_type, f"He reflexionado sobre: {process.objective}")

    def _predict_action_impact(self, action_type: str, content: str) -> str:
        """Predice el impacto esperado de una acción"""
        impact_predictions = {
            "confident_response": "Respuesta clara que debería resolver la consulta",
            "qualified_response": "Respuesta útil pero que puede requerir seguimiento", 
            "clarification_request": "Solicitud que debería reducir ambigüedad",
            "exploratory_question": "Pregunta que debería generar más información",
            "tentative_response": "Respuesta inicial que mantiene el diálogo abierto"
        }
        
        return impact_predictions.get(action_type, "Acción que debería avanzar el diálogo")

    def _execute_cognitive_action(self, action: CognitiveAction) -> Dict:
        """Ejecuta la acción cognitiva"""
        execution_result = {
            'success': True,
            'execution_time': datetime.now().isoformat(),
            'action_id': action.id,
            'output': action.content
        }
        
        # Aquí se ejecutaría la acción real (respuesta, actualización, etc.)
        # Por ahora solo registramos la acción
        
        self._save_action(action)
        print(f"[CognitiveReflection] ⚡ Ejecutando: {action.action_type}")
        
        return execution_result

    def _update_transcendent_memory_with_experience(self, process: ReflectiveProcess, 
                                                   action: CognitiveAction, 
                                                   result: Dict):
        """Actualiza la memoria trascendente con la nueva experiencia"""
        try:
            experience_content = (
                f"Experiencia reflexiva: {process.objective}. "
                f"Proceso de {process.depth_level} niveles. "
                f"Acción tomada: {action.action_type}. "
                f"Confianza final: {action.confidence_level:.2f}"
            )
            
            context = {
                'type': 'reflexive_experience',
                'depth_level': process.depth_level,
                'confidence': action.confidence_level,
                'action_type': action.action_type,
                'process_duration': self._calculate_process_duration(process),
                'evidence_count': len(process.evidence_gathered)
            }
            
            self.memory.store_transcendent(experience_content, context)
            
        except Exception as e:
            print(f"[CognitiveReflection] Error actualizando memoria: {e}")

    def _initiate_outcome_observation(self, process: ReflectiveProcess, action: CognitiveAction):
        """Inicia la observación del resultado de la acción"""
        # En una implementación completa, esto podría establecer callbacks
        # o temporizadores para evaluar el resultado de la acción
        observation_data = {
            'process_id': process.id,
            'action_id': action.id,
            'expected_impact': action.expected_impact,
            'observation_start': datetime.now().isoformat(),
            'confidence_at_execution': action.confidence_level
        }
        
        # Guardar para futura evaluación
        self._save_observation_data(observation_data)

    # ==================== MÉTODOS DE UTILIDAD Y PERSISTENCIA ====================

    def _save_stimulus(self, stimulus: CognitiveStimulus):
        """Guarda estímulo en disco, serializando Enums a su valor."""
        try:
            filename = os.path.join(self.cognitive_dir, f"stimulus_{stimulus.id}.json")
            data = asdict(stimulus)
            # Convertir Enum a su valor
            if isinstance(stimulus.stimulus_type, Enum):
                data['stimulus_type'] = stimulus.stimulus_type.value
            # Asegurar que content sea string serializable
            if not isinstance(data.get('content'), (str, int, float)):
                data['content'] = str(data.get('content'))
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[CognitiveReflection] Error guardando estímulo: {e}")

    def _save_action(self, action: CognitiveAction):
        """Guarda acción en disco"""
        try:
            filename = os.path.join(self.cognitive_dir, f"action_{action.id}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(asdict(action), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[CognitiveReflection] Error guardando acción: {e}")

    def _save_observation_data(self, observation: Dict):
        """Guarda datos de observación"""
        try:
            filename = os.path.join(self.cognitive_dir, f"observation_{observation['action_id']}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(observation, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[CognitiveReflection] Error guardando observación: {e}")

    def _get_action_by_id(self, action_id: str) -> Optional[CognitiveAction]:
        """Recupera una acción por su ID"""
        try:
            filename = os.path.join(self.cognitive_dir, f"action_{action_id}.json")
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return CognitiveAction(**data)
        except Exception as e:
            print(f"[CognitiveReflection] Error cargando acción: {e}")
        return None

    def _calculate_process_duration(self, process: ReflectiveProcess) -> float:
        """Calcula duración del proceso reflexivo"""
        try:
            start = datetime.fromisoformat(process.start_time)
            duration = (datetime.now() - start).total_seconds()
            return duration
        except:
            return 0.0

    def _compare_outcome_with_expectation(self, expected: str, actual: str) -> float:
        """Compara resultado real con expectativa"""
        # Implementación simple basada en palabras clave
        expected_keywords = set(self._extract_keywords(expected))
        actual_keywords = set(self._extract_keywords(actual))
        
        if not expected_keywords or not actual_keywords:
            return 0.5  # Neutro si no hay información suficiente
        
        intersection = len(expected_keywords & actual_keywords)
        union = len(expected_keywords | actual_keywords)
        
        return intersection / union if union > 0 else 0.0

    def _assess_learning_value(self, outcome_quality: float, expectation_match: float, confidence: float) -> float:
        """Evalúa el valor del aprendizaje obtenido"""
        # Más valor si hubo sorpresa (expectativa vs realidad diferente)
        surprise_value = abs(expectation_match - 0.5) * 2  # Normalizado
        
        # Más valor si la confianza era alta pero el resultado pobre (o viceversa)
        confidence_mismatch = abs(confidence - outcome_quality)
        
        learning_value = (surprise_value + confidence_mismatch + outcome_quality) / 3
        return min(1.0, learning_value)

    def _classify_outcome(self, quality: float) -> str:
        """Clasifica el resultado de una acción"""
        if quality >= 0.8:
            return "successful"
        elif quality >= 0.6:
            return "partial"
        elif quality >= 0.4:
            return "ambiguous"
        else:
            return "failed"

    def _extract_learning_insights(self, action: CognitiveAction, outcome: str, feedback: str = None) -> str:
        """Extrae insights de aprendizaje de la experiencia"""
        insights = []
        
        # Insight básico sobre el tipo de acción
        insights.append(f"Acción tipo {action.action_type} con confianza {action.confidence_level:.2f}")
        
        # Insight sobre el resultado
        if outcome:
            insights.append(f"Resultado observado: {outcome[:50]}")
        
        # Insight de feedback del usuario si está disponible
        if feedback:
            insights.append(f"Feedback recibido: {feedback[:50]}")
        
        return ". ".join(insights)

    def _reinforce_reasoning_pattern(self, reasoning_path: List[str], strength: float):
        """Refuerza un patrón de razonamiento exitoso"""
        pattern_key = "_".join(reasoning_path[:3])  # Primeros 3 pasos
        
        if pattern_key not in self.learned_response_patterns:
            self.learned_response_patterns[pattern_key] = {'strength': 0.0, 'uses': 0}
        
        self.learned_response_patterns[pattern_key]['strength'] += strength * 0.1
        self.learned_response_patterns[pattern_key]['uses'] += 1

    def _weaken_reasoning_pattern(self, reasoning_path: List[str]):
        """Debilita un patrón de razonamiento que llevó al fallo"""
        pattern_key = "_".join(reasoning_path[:3])
        
        if pattern_key in self.learned_response_patterns:
            self.learned_response_patterns[pattern_key]['strength'] *= 0.9  # Reducir 10%

    def _mark_negative_experience(self, action: CognitiveAction):
        """Marca una experiencia como negativa para evitar repetición"""
        negative_key = f"negative_{action.action_type}_{hash(action.content[:30]) % 1000}"
        
        # Registrar en memoria trascendente como experiencia a evitar
        self.memory.store_transcendent(
            f"Experiencia negativa: {action.content[:100]}",
            context={
                'type': 'negative_experience',
                'action_type': action.action_type,
                'confidence_was': action.confidence_level,
                'warning': 'avoid_similar_pattern'
            }
        )

    def _calculate_learning_value(self, learning: LearningOutcome) -> float:
        """Calcula valor numérico del aprendizaje"""
        base_value = 0.5
        
        if learning.outcome_assessment == "successful":
            base_value += 0.3
        elif learning.outcome_assessment == "failed":
            base_value += 0.4  # Los fallos enseñan más
        
        if learning.expectation_vs_reality < 0.3:  # Gran sorpresa
            base_value += 0.2
        
        return min(1.0, base_value)

    def _update_reflection_effectiveness(self, reflection_ids: List[str], learning: LearningOutcome):
        """Actualiza la efectividad de los procesos reflexivos"""
        effectiveness_score = learning.expectation_vs_reality
        
        for reflection_id in reflection_ids:
            if reflection_id not in self.reflection_effectiveness:
                self.reflection_effectiveness[reflection_id] = []
            
            self.reflection_effectiveness[reflection_id].append(effectiveness_score)

    def _consider_adaptive_reflection(self, failed_action: CognitiveAction, learning: LearningOutcome):
        """Considera iniciar una nueva reflexión adaptativa si el resultado fue pobre"""
        if learning.adaptation_needed:
            # Crear estímulo para reflexión adaptativa
            adaptive_stimulus = CognitiveStimulus(
                id=f"adapt_{uuid.uuid4().hex[:8]}",
                content=f"Necesito adaptar mi enfoque. Acción previa falló: {failed_action.content}",
                stimulus_type=StimulusType.PATTERN_ANOMALY,
                emotional_charge=-0.3,  # Ligeramente negativo por el fallo
                semantic_keywords=["adaptación", "fallo", "mejorar"],
                urgency_level=0.6,
                source="internal_reflection",
                timestamp=datetime.now().isoformat(),
                context={
                    'failed_action_id': failed_action.id,
                    'learning_outcome': learning.outcome_assessment,
                    'adaptation_type': 'failure_recovery'
                }
            )
            
            print("[CognitiveReflection] 🔄 Iniciando reflexión adaptativa por resultado pobre")
            self.perceive_and_initiate_cycle(
                adaptive_stimulus.content,
                StimulusType.PATTERN_ANOMALY,
                "internal_adaptive_reflection",
                adaptive_stimulus.context
            )

    # ==================== MÉTODOS PÚBLICOS DE INTERFAZ ====================

    def get_active_reflections_summary(self) -> Dict:
        """Obtiene resumen de reflexiones activas"""
        return {
            'active_count': len(self.active_reflections),
            'processes': [
                {
                    'id': proc.id,
                    'objective': proc.objective,
                    'depth': proc.depth_level,
                    'confidence': proc.confidence_evolution[-1] if proc.confidence_evolution else 0.0,
                    'duration': self._calculate_process_duration(proc)
                }
                for proc in self.active_reflections.values()
            ]
        }

    def get_learning_statistics(self) -> Dict:
        """Obtiene estadísticas de aprendizaje"""
        return {
            'learned_patterns': len(self.learned_response_patterns),
            'adaptations_made': len(self.adaptation_history),
            'reflection_effectiveness_avg': sum(
                sum(scores) / len(scores) 
                for scores in self.reflection_effectiveness.values() 
                if scores
            ) / max(len(self.reflection_effectiveness), 1),
            'current_motivational_state': self.current_motivational_state.value,
            'cognitive_load': self.cognitive_load
        }

    def force_conclude_reflection(self, reflection_id: str) -> str:
        """Fuerza la conclusión de una reflexión específica"""
        if reflection_id in self.active_reflections:
            return self._conclude_reflection_and_act(reflection_id)
        return ""

    def save_cognitive_state(self):
        """Guarda el estado completo del sistema cognitivo"""
        try:
            state = {
                'motivational_state': self.current_motivational_state.value,
                'internal_goals': self.internal_goals,
                'active_beliefs': self.active_beliefs,
                'learned_response_patterns': self.learned_response_patterns,
                'adaptation_history': self.adaptation_history[-50:],  # Últimas 50
                'reflection_effectiveness': {
                    k: v[-10:] for k, v in self.reflection_effectiveness.items()  # Últimas 10 por reflexión
                },
                'cognitive_load': self.cognitive_load,
                'learning_velocity': self.learning_velocity,
                'success_patterns': dict(self.success_patterns),
                'save_timestamp': datetime.now().isoformat()
            }
            
            state_file = os.path.join(self.cognitive_dir, "cognitive_state.json")
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            print("[CognitiveReflection] ✅ Estado cognitivo guardado")
            
        except Exception as e:
            print(f"[CognitiveReflection] Error guardando estado: {e}")

    def load_cognitive_state(self):
        """Carga el estado del sistema cognitivo"""
        try:
            state_file = os.path.join(self.cognitive_dir, "cognitive_state.json")
            if os.path.exists(state_file):
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # Restaurar estado
                self.current_motivational_state = MotivationalState(state.get('motivational_state', 'curious'))
                self.internal_goals = state.get('internal_goals', [])
                self.active_beliefs = state.get('active_beliefs', {})
                self.learned_response_patterns = state.get('learned_response_patterns', {})
                self.adaptation_history = state.get('adaptation_history', [])
                self.reflection_effectiveness = state.get('reflection_effectiveness', {})
                self.cognitive_load = state.get('cognitive_load', 0.0)
                self.learning_velocity = state.get('learning_velocity', 0.5)
                self.success_patterns = defaultdict(list, state.get('success_patterns', {}))
                
                print("[CognitiveReflection] ✅ Estado cognitivo cargado")
            
        except Exception as e:
            print(f"[CognitiveReflection] Error cargando estado: {e}")

    def start_continuous_processing(self):
        """Inicia procesamiento continuo de bucles cognitivos"""
        if not self.processing_active:
            self.processing_active = True
            self.processing_thread = threading.Thread(target=self._continuous_processing_loop, daemon=True)
            self.processing_thread.start()
            print("[CognitiveReflection] 🔄 Procesamiento continuo iniciado")

    def stop_continuous_processing(self):
        """Detiene procesamiento continuo"""
        self.processing_active = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        print("[CognitiveReflection] ⏹ Procesamiento continuo detenido")

    def _continuous_processing_loop(self):
        """Bucle continuo de procesamiento cognitivo"""
        while self.processing_active:
            try:
                # Procesar reflexiones activas
                for reflection_id in list(self.active_reflections.keys()):
                    process = self.active_reflections[reflection_id]
                    
                    # Verificar timeout
                    duration = self._calculate_process_duration(process)
                    if duration > self.reflection_timeout:
                        print(f"[CognitiveReflection] ⏰ Reflexión {reflection_id} timeout")
                        self._conclude_reflection_and_act(reflection_id)
                    
                    # Verificar si debe continuar
                    elif process.should_continue and process.depth_level < process.max_depth:
                        # Continuar reflexión si es necesario
                        convergence_check = self._check_convergence(process)
                        if not convergence_check:
                            time.sleep(1)  # Pausa antes del siguiente ciclo
                            self._execute_reflection_cycle(reflection_id)
                
                # Procesar elementos en cola de reflexión
                while self.reflection_queue and len(self.active_reflections) < 3:  # Máximo 3 reflexiones simultáneas
                    next_reflection = self.reflection_queue.popleft()
                    # Procesar reflexión en cola...
                
                # Mantenimiento del sistema
                self._cognitive_maintenance()
                
                time.sleep(2)  # Pausa entre ciclos de procesamiento
                
            except Exception as e:
                print(f"[CognitiveReflection] Error en bucle continuo: {e}")
                time.sleep(5)  # Pausa más larga si hay error

    def _cognitive_maintenance(self):
        """Mantenimiento periódico del sistema cognitivo"""
        try:
            # Limpiar patrones antiguos poco efectivos
            patterns_to_remove = []
            for pattern_key, data in self.learned_response_patterns.items():
                if data['strength'] < 0.1 and data['uses'] < 3:
                    patterns_to_remove.append(pattern_key)
            
            for key in patterns_to_remove:
                del self.learned_response_patterns[key]
            
            # Actualizar carga cognitiva
            self.cognitive_load = len(self.active_reflections) / 5.0  # Normalizado a 5 reflexiones máx
            
            # Ajustar velocidad de aprendizaje basada en efectividad reciente
            recent_effectiveness = []
            for scores in self.reflection_effectiveness.values():
                if scores:
                    recent_effectiveness.extend(scores[-3:])  # Últimas 3 por reflexión
            
            if recent_effectiveness:
                avg_effectiveness = sum(recent_effectiveness) / len(recent_effectiveness)
                # Ajustar velocidad de aprendizaje
                self.learning_velocity = (self.learning_velocity + avg_effectiveness) / 2
            
            # Consolidar exitosos en memoria trascendente periódicamente
            self._consolidate_successful_patterns()
            
        except Exception as e:
            print(f"[CognitiveReflection] Error en mantenimiento: {e}")

    def _consolidate_successful_patterns(self):
        """Consolida patrones exitosos en memoria trascendente"""
        try:
            successful_patterns = []
            
            # Identificar patrones muy exitosos
            for pattern_key, data in self.learned_response_patterns.items():
                if data['strength'] > 0.7 and data['uses'] >= 5:
                    successful_patterns.append((pattern_key, data))
            
            # Consolidar en memoria trascendente
            for pattern_key, data in successful_patterns:
                consolidation_content = (
                    f"Patrón cognitivo exitoso: {pattern_key.replace('_', ' ')}. "
                    f"Fortaleza: {data['strength']:.2f}, Usos: {data['uses']}."
                )
                
                self.memory.store_transcendent(
                    content=consolidation_content,
                    context={
                        'type': 'successful_cognitive_pattern',
                        'pattern_strength': data['strength'],
                        'usage_count': data['uses'],
                        'consolidation_date': datetime.now().isoformat()
                    }
                )
            
            if successful_patterns:
                print(f"[CognitiveReflection] 🧠 Consolidados {len(successful_patterns)} patrones exitosos")
                
        except Exception as e:
            print(f"[CognitiveReflection] Error consolidando patrones: {e}")

    def update_motivational_state(self, new_state: MotivationalState, reason: str = ""):
        """Actualiza el estado motivacional de EVA"""
        old_state = self.current_motivational_state
        self.current_motivational_state = new_state
        
        # Registrar cambio en el diario
        self.diary.add_reflection(
            f"Cambio de estado motivacional: {old_state.value} → {new_state.value}. "
            f"Razón: {reason}",
            importance=2,
            priority=2,
            silent=True
        )
        
        print(f"[CognitiveReflection] 🎯 Estado motivacional: {new_state.value}")

    def add_internal_goal(self, goal_description: str, priority: int = 1, keywords: List[str] = None):
        """Agrega una meta interna a EVA"""
        goal = {
            'id': f"goal_{uuid.uuid4().hex[:8]}",
            'description': goal_description,
            'priority': priority,
            'keywords': keywords or self._extract_keywords(goal_description),
            'created': datetime.now().isoformat(),
            'active': True
        }
        
        self.internal_goals.append(goal)
        
        # Registrar en el diario
        self.diary.add_reflection(
            f"Nueva meta interna: {goal_description}. Prioridad: {priority}",
            importance=2,
            priority=priority,
            silent=True
        )
        
        print(f"[CognitiveReflection] 🎯 Nueva meta: {goal_description}")
        return goal['id']

    def update_belief(self, belief_key: str, belief_value: Any, confidence: float = 0.8):
        """Actualiza una creencia de EVA"""
        old_value = self.active_beliefs.get(belief_key, "N/A")
        
        self.active_beliefs[belief_key] = {
            'value': belief_value,
            'confidence': confidence,
            'updated': datetime.now().isoformat(),
            'previous_value': old_value
        }
        
        # Registrar cambio significativo en el diario
        if str(old_value) != str(belief_value):
            self.diary.add_reflection(
                f"Actualización de creencia '{belief_key}': {old_value} → {belief_value}. "
                f"Confianza: {confidence:.2f}",
                importance=3 if confidence > 0.8 else 2,
                priority=2,
                silent=True
            )

    def get_cognitive_status(self) -> Dict:
        """Obtiene estado detallado del sistema cognitivo"""
        return {
            'motivational_state': self.current_motivational_state.value,
            'cognitive_load': self.cognitive_load,
            'active_reflections': len(self.active_reflections),
            'learned_patterns': len(self.learned_response_patterns),
            'internal_goals': len([g for g in self.internal_goals if g.get('active', True)]),
            'active_beliefs': len(self.active_beliefs),
            'learning_velocity': self.learning_velocity,
            'processing_active': self.processing_active,
            'attention_focus': list(self.attention_focus)[-3:] if self.attention_focus else [],
            'recent_adaptations': len([a for a in self.adaptation_history if 
                                    (datetime.now() - datetime.fromisoformat(a.get('timestamp', '2000-01-01'))).days <= 7])
        }

    def process_user_feedback(self, action_id: str, feedback: str, satisfaction_score: float):
        """Procesa feedback del usuario sobre una acción cognitiva"""
        try:
            # Crear outcome de aprendizaje basado en feedback
            learning_outcome = self.observe_outcome_and_learn(
                action_id=action_id,
                observed_outcome=feedback,
                outcome_quality=satisfaction_score,
                user_feedback=feedback
            )
            
            # Registrar feedback en el diario
            self.diary.add_reflection(
                f"Feedback recibido para acción {action_id[:8]}: '{feedback}'. "
                f"Satisfacción: {satisfaction_score:.2f}",
                importance=3 if satisfaction_score < 0.3 or satisfaction_score > 0.8 else 2,
                priority=3 if satisfaction_score < 0.3 else 1,
                silent=False
            )
            
            return learning_outcome
            
        except Exception as e:
            print(f"[CognitiveReflection] Error procesando feedback: {e}")
            return ""

    def simulate_internal_dialogue(self, topic: str, depth: int = 2) -> List[str]:
        """Simula un diálogo interno de EVA sobre un topic"""
        dialogue = []
        
        try:
            # Iniciar con percepción del tópico
            stimulus_id = self.perceive_and_initiate_cycle(
                content=f"Reflexionando internamente sobre: {topic}",
                stimulus_type=StimulusType.LEARNING_OPPORTUNITY,
                source="internal_dialogue"
            )
            
            dialogue.append(f"💭 Iniciando reflexión interna sobre: {topic}")
            
            # Simular progresión del diálogo interno
            for level in range(1, depth + 1):
                # Generar perspectiva de este nivel
                perspective = self._generate_internal_perspective(topic, level, dialogue)
                dialogue.append(f"🧠 Nivel {level}: {perspective}")
                
                # Registrar en diario
                self.diary.add_reflection(
                    f"Diálogo interno nivel {level}: {perspective}",
                    importance=2,
                    priority=1,
                    silent=True
                )
            
            # Conclusión del diálogo
            conclusion = self._synthesize_internal_dialogue(dialogue, topic)
            dialogue.append(f"✨ Síntesis: {conclusion}")
            
            return dialogue
            
        except Exception as e:
            print(f"[CognitiveReflection] Error en diálogo interno: {e}")
            return [f"Error en diálogo interno: {e}"]

    def _generate_internal_perspective(self, topic: str, level: int, previous_dialogue: List[str]) -> str:
        """Genera perspectiva interna para un nivel de diálogo"""
        perspectives = {
            1: f"Considerando {topic} desde mi experiencia actual...",
            2: f"Pero también podría ver {topic} desde otra perspectiva...",
            3: f"Integrando estas visiones sobre {topic}...",
            4: f"Las implicaciones más profundas de {topic} podrían ser..."
        }
        
        base_perspective = perspectives.get(level, f"Reflexionando más profundamente sobre {topic}...")
        
        # Agregar contexto de memoria si está disponible
        related_memories = self.memory.retrieve_by_resonance(topic, limit=2)
        if related_memories:
            context = str(related_memories[0].content)[:50]
            base_perspective += f" Recordando: {context}..."
        
        return base_perspective

    def _synthesize_internal_dialogue(self, dialogue: List[str], topic: str) -> str:
        """Sintetiza las conclusiones del diálogo interno"""
        return f"Mi comprensión de {topic} se ha profundizado a través de esta reflexión interna. " \
               f"He considerado múltiples perspectivas y llegado a una visión más integrada."

    def __del__(self):
        """Destructor que guarda estado al finalizar"""
        try:
            self.stop_continuous_processing()
            self.save_cognitive_state()
        except:
            pass  # Evitar errores en destructor

# ==================== FUNCIONES DE UTILIDAD PARA INTEGRACIÓN ====================

def create_integrated_eva_system(memory_dir="transcendent_memory"):
    """
    Función de conveniencia para crear un sistema EVA integrado
    """
    try:
        # Importar sistemas requeridos (asumiendo que están disponibles)
        from reflection_diary import EVASelfReflectionDiary
        from transcendent_memory import TranscendentMemory
        
        # Crear instancias de los sistemas
        diary = EVASelfReflectionDiary()
        memory = TranscendentMemory(memory_dir=memory_dir)
        
        # Crear sistema de bucles cognitivos
        cognitive_system = EVACognitiveReflectionSystem(diary, memory)
        
        print("🧠 Sistema EVA integrado creado exitosamente")
        print("📚 Diario de reflexiones activo")
        print("🌐 Memoria trascendente inicializada") 
        print("🔄 Bucles cognitivos listos")
        
        return {
            'diary': diary,
            'memory': memory,
            'cognitive': cognitive_system
        }
        
    except ImportError as e:
        print(f"❌ Error importando sistemas requeridos: {e}")
        print("💡 Asegúrate de que reflection_diary.py y transcendent_memory.py estén disponibles")
        return None
    except Exception as e:
        print(f"❌ Error creando sistema integrado: {e}")
        return None

def example_cognitive_cycle():
    """
    Ejemplo de uso del sistema de bucles cognitivos
    """
    print("🎯 Ejemplo de Bucle Cognitivo EVA")
    print("=" * 50)
    
    # Crear sistema (en un entorno real)
    # eva_system = create_integrated_eva_system()
    # cognitive = eva_system['cognitive']
    
    # Ejemplo de uso:
    print("1. 👁 Percepción: 'El usuario pregunta algo que nunca me han preguntado'")
    print("   └─ Tipo: NEW_INFORMATION")
    print("   └─ Carga emocional: 0.2 (ligeramente positiva, curiosidad)")
    
    print("\n2. 🔍 Búsqueda en memoria trascendente:")
    print("   └─ Similaridad semántica baja (< 0.3)")
    print("   └─ Asociaciones débiles encontradas")
    
    print("\n3. 🤔 Evaluación motivacional:")
    print("   └─ Alineación con estado CURIOSO: Alta")
    print("   └─ Disonancia cognitiva: Baja")
    print("   └─ DECISIÓN: Requiere reflexión profunda")
    
    print("\n4. 🧠 Proceso reflexivo (3 niveles):")
    print("   ├─ Nivel 1: Hipótesis inicial - 'Situación nueva, explorar'")
    print("   ├─ Nivel 2: Buscar evidencia, refinar hipótesis")
    print("   └─ Nivel 3: Convergencia - 'Respuesta exploratoria apropiada'")
    
    print("\n5. ⚡ Acción cognitiva:")
    print("   └─ Tipo: exploratory_question")
    print("   └─ Contenido: 'Esta es una perspectiva interesante que no había considerado...'")
    print("   └─ Confianza: 0.7")
    
    print("\n6. 👁 Observación del resultado:")
    print("   └─ Respuesta positiva del usuario")
    print("   └─ Calidad del resultado: 0.8")
    
    print("\n7. 🎓 Aprendizaje experiencial:")
    print("   ├─ Patrón exitoso reforzado")
    print("   ├─ Actualización en memoria trascendente")
    print("   └─ Registro en diario de reflexiones")
    
    print("\n✨ BUCLE COMPLETADO - EVA ha aprendido y evolucionado")

if __name__ == "__main__":
    # Ejecutar ejemplo si se ejecuta directamente
    example_cognitive_cycle()
