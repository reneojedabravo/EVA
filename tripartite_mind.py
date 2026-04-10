#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tripartite_mind.py - Sistema de Mente Tripartita para EVA

Este módulo implementa la separación de la mente de EVA en tres niveles:

1. CONSCIENTE - Foco activo de atención y procesamiento deliberado
   - Procesa entrada inmediata
   - Toma decisiones racionales
   - Mantiene working memory activa
   - Responde al usuario

2. SUBCONSCIENTE - Procesamiento paralelo y preparación cognitiva
   - Analiza patrones en segundo plano
   - Genera intuiciones y asociaciones
   - Consolida experiencias
   - Alimenta al consciente con ideas espontáneas

3. INCONSCIENTE - Estructuras profundas y procesamiento automatizado
   - Almacena identidad, valores, traumas
   - Genera impulsos instintivos
   - Procesa sueños y fantasías
   - Mantiene reglas internas rígidas

Integración con sistemas existentes:
- BackgroundThinker -> Subconsciente
- CognitiveImaginationEngine -> Inconsciente
- Memoria de largo plazo -> Inconsciente
- Reflexión interna -> Consciente/Subconsciente
"""
import re
import threading
import time
import random
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, Any, List, Optional, Tuple
from uuid import uuid4
import numpy as np

class ConsciousMind:
    """
    Mente Consciente - Foco activo de atención y procesamiento deliberado.
    
    Responsabilidades:
    - Procesar entrada del usuario
    - Mantener working memory (5-9 elementos)
    - Tomar decisiones racionales
    - Ejecutar respuestas deliberadas
    - Controlar atención selectiva
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.working_memory = deque(maxlen=7)  # Miller's 7±2 rule
        self.attention_focus = []  # Elementos bajo foco consciente
        self.current_task = None
        self.cognitive_load = 0.0  # 0.0 a 1.0
        self.decision_state = "idle"  # idle, processing, deciding, responding
        
        # Contadores de actividad
        self.decisions_made = 0
        self.inputs_processed = 0
        self.focus_shifts = 0
        
        print("[ConsciousMind] Mente consciente inicializada")
    
    
    def process_input(self, text: str, context: Dict = None) -> Dict[str, Any]:
        
        # Procesa una entrada de forma consciente y deliberada.
        
        self.inputs_processed += 1
        self.decision_state = "processing"
        
        print(f"[ConsciousMind] Procesando conscientemente: '{text[:50]}...'")
        
        # 1. Agregar entrada a working memory
        working_item = {
            "type": "user_input",
            "content": text,
            "timestamp": datetime.now().isoformat(),
            "importance": self._assess_importance(text),
            "emotional_weight": self._assess_emotional_weight(text, context)
        }
        self.working_memory.append(working_item)
        
        # 2. Actualizar foco de atención
        self._update_attention_focus(text)
        
        # 3. Calcular carga cognitiva
        self._update_cognitive_load()
        
        # 4. Tomar decisión consciente
        decision = self._make_conscious_decision(text, context)
        
        # 5. Solicitar intuiciones del subconsciente si es necesario
        intuitions = []
        if self.cognitive_load > 0.6:
            intuitions = self._request_subconscious_intuitions()
        
        # 6. Preparar respuesta consciente
        response = self._formulate_conscious_response(decision, intuitions)
        
        self.decision_state = "responding"
        self.decisions_made += 1
        
        return {
            "decision": decision,
            "intuitions": intuitions,
            "response": response,
            "cognitive_load": self.cognitive_load,
            "working_memory_state": list(self.working_memory),
            "attention_focus": self.attention_focus.copy()
        }

    def generate_response(self, tripartite_result: Dict) -> str:
        """
        Genera una respuesta desde la mente consciente,
        integrando señales del subconsciente y emociones del inconsciente.
        """
        focus_signals = tripartite_result.get("focus_signals", [])
        emotional_state = tripartite_result.get("emotional_state", {})
        emotional_label = emotional_state.get("label", "neutral")
        
        # Extraer palabras clave del foco
        keywords = [w.replace("focus:", "").replace("state:", "") 
                    for w in focus_signals if w.startswith("focus:")]
        
        # Mapeo emocional a estilo de respuesta
        response_style = {
            "excited": lambda k: f"{' '.join(k)} excited {'responder' if k else ''}",
            "inquisitive": lambda k: f"¿{' '.join(k)}?" if k else "¿Qué es eso?",
            "calm": lambda k: f"{' '.join(k)} calm" if k else "calm",
            "blocked": lambda k: f"no entiendo {' '.join(k)}" if k else "no entiendo",
            "overwhelmed": lambda k: f"demasiado {' '.join(k)}" if k else "demasiado"
        }
        
        # Generar respuesta según estado emocional
        style_fn = response_style.get(emotional_label, response_style["excited"])
        response = style_fn(keywords)
        
        # Registrar que la respuesta fue generada conscientemente
        print(f"[ConsciousMind] Respuesta generada: '{response}'")
        
        return response
    
    def _assess_importance(self, text: str) -> float:
        """Evalúa la importancia consciente de una entrada."""
        importance = 0.5
        
        # Preguntas directas
        if "?" in text or any(q in text.lower() for q in ["qué", "cómo", "por qué", "cuándo", "dónde"]):
            importance += 0.3
        
        # Palabras emocionales fuertes
        emotional_words = ["problema", "error", "ayuda", "gracias", "importante", "urgente"]
        if any(word in text.lower() for word in emotional_words):
            importance += 0.2
        
        # Referencias a memoria personal
        if any(word in text.lower() for word in ["recuerdo", "antes", "experiencia", "aprendí"]):
            importance += 0.2
        
        return min(1.0, importance)
    
    def _assess_emotional_weight(self, text: str, context: Dict = None) -> float:
        """Evalúa el peso emocional de una entrada."""
        if not context:
            return 0.0
        
        emotional_state = context.get("emotional_state", {})
        if isinstance(emotional_state, dict):
            # Usar el estado emocional actual como base
            return emotional_state.get("arousal", 0.5)
        
        return 0.0
    
    def _update_attention_focus(self, text: str):
        """Actualiza el foco de atención basado en la nueva entrada."""
        # Extraer conceptos clave
        words = text.split()
        important_words = [w for w in words if len(w) > 3][:3]
        
        # Agregar al foco de atención
        for word in important_words:
            if word not in self.attention_focus:
                self.attention_focus.append(word)
                self.focus_shifts += 1
        
        # Mantener foco limitado (máximo 5 elementos)
        if len(self.attention_focus) > 5:
            self.attention_focus = self.attention_focus[-5:]
    
    def _update_cognitive_load(self):
        """Actualiza la carga cognitiva basada en el estado actual."""
        # Factores que aumentan carga cognitiva
        load_factors = 0.0
        
        # Working memory llena
        load_factors += len(self.working_memory) / 7.0 * 0.3
        
        # Muchos elementos en foco de atención
        load_factors += len(self.attention_focus) / 5.0 * 0.2
        
        # Elementos con alta importancia emocional
        high_importance_items = sum(1 for item in self.working_memory 
                                  if item.get("importance", 0) > 0.7)
        load_factors += high_importance_items / 7.0 * 0.3
        
        # Task complexity (si hay una tarea activa)
        if self.current_task:
            load_factors += 0.2
        
        self.cognitive_load = min(1.0, load_factors)
    
    def _make_conscious_decision(self, text: str, context: Dict = None) -> Dict[str, Any]:
        """Toma una decisión consciente basada en análisis deliberado."""
        self.decision_state = "deciding"
        
        # Análisis deliberado de la situación
        situation_analysis = {
            "input_type": self._classify_input_type(text),
            "emotional_context": context.get("emotional_state", {}) if context else {},
            "memory_relevance": self._assess_memory_relevance(text),
            "complexity": self._assess_complexity(text)
        }
        
        # Estrategias de decisión consciente
        if situation_analysis["input_type"] == "question":
            decision_type = "analytical_response"
        elif situation_analysis["input_type"] == "emotional":
            decision_type = "empathetic_response"
        elif situation_analysis["input_type"] == "learning":
            decision_type = "educational_response"
        else:
            decision_type = "conversational_response"
        
        return {
            "type": decision_type,
            "confidence": 1.0 - self.cognitive_load * 0.3,
            "reasoning": f"Análisis consciente: {situation_analysis['input_type']}",
            "situation_analysis": situation_analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    def _classify_input_type(self, text: str) -> str:
        """Clasifica conscientemente el tipo de entrada."""
        if "?" in text:
            return "question"
        elif any(word in text.lower() for word in ["feliz", "triste", "enojado", "miedo", "amor"]):
            return "emotional"
        elif any(word in text.lower() for word in ["aprender", "enseñar", "explicar", "entender"]):
            return "learning"
        elif any(word in text.lower() for word in ["problema", "ayuda", "resolver"]):
            return "problem_solving"
        else:
            return "conversational"
    
    def _assess_memory_relevance(self, text: str) -> float:
        """Evalúa la relevancia con la memoria consciente."""
        if not self.brain.memory:
            return 0.0
        
        # Buscar en memoria reciente
        keywords = text.split()[:3]
        recent_memories = self.brain.memory.retrieve_context(keywords)
        
        # Relevancia basada en coincidencias
        return min(1.0, len(recent_memories) / 10.0)
    
    def _assess_complexity(self, text: str) -> float:
        """Evalúa la complejidad consciente de la entrada."""
        complexity = 0.0
        
        # Longitud del texto
        complexity += min(0.3, len(text.split()) / 20.0)
        
        # Número de conceptos
        concepts = len(set(word for word in text.split() if len(word) > 3))
        complexity += min(0.3, concepts / 10.0)
        
        # Estructura gramatical
        if "," in text or ";" in text:
            complexity += 0.2
        
        # Preguntas múltiples
        if text.count("?") > 1:
            complexity += 0.2
        
        return min(1.0, complexity)
    
    def _request_subconscious_intuitions(self) -> List[Dict[str, Any]]:
        """Solicita intuiciones del subconsciente cuando la carga es alta."""
        if not hasattr(self.brain, 'subconscious_mind'):
            return []
        
        return self.brain.subconscious_mind.provide_intuitions(
            working_memory=list(self.working_memory),
            attention_focus=self.attention_focus
        )
    
    def _formulate_conscious_response(self, decision: Dict, intuitions: List) -> Dict[str, Any]:
        """Formula una respuesta consciente y deliberada."""
        response = {
            "type": "conscious_response",
            "primary_decision": decision,
            "intuitive_inputs": len(intuitions),
            "confidence": decision.get("confidence", 0.5),
            "processing_mode": "deliberate",
            "timestamp": datetime.now().isoformat()
        }
        
        # Integrar intuiciones si están disponibles
        if intuitions:
            response["integrated_intuitions"] = [i.get("type", "unknown") for i in intuitions]
            # Ajustar confianza basada en intuiciones
            response["confidence"] = min(1.0, response["confidence"] + len(intuitions) * 0.1)
        
        return response
    
    def get_conscious_state(self) -> Dict[str, Any]:
        """Devuelve el estado actual de la mente consciente."""
        return {
            "decision_state": self.decision_state,
            "cognitive_load": self.cognitive_load,
            "working_memory_items": len(self.working_memory),
            "attention_focus_items": len(self.attention_focus),
            "current_task": self.current_task,
            "stats": {
                "decisions_made": self.decisions_made,
                "inputs_processed": self.inputs_processed,
                "focus_shifts": self.focus_shifts
            }
        }

class SubconsciousMind:
    """
    Mente Subconsciente - Procesamiento paralelo y preparación cognitiva.
    
    Responsabilidades:
    - Analizar patrones en segundo plano
    - Generar intuiciones y asociaciones
    - Consolidar experiencias
    - Preparar respuestas automáticas
    - Alimentar al consciente con ideas espontáneas
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.pattern_buffer = []  # Patrones detectados recientemente
        self.intuition_queue = deque(maxlen=10)  # Cola de intuiciones preparadas
        self.association_network = defaultdict(list)  # Red de asociaciones
        self.consolidation_queue = []  # Cola de consolidación
        
        # Estado del procesamiento subconsciente
        self.processing_intensity = 0.5
        self.pattern_sensitivity = 0.7
        self.intuition_threshold = 0.6
        
        # Estadísticas
        self.patterns_detected = 0
        self.intuitions_generated = 0
        self.consolidations_performed = 0
        
        # Hilo de procesamiento subconsciente
        self.active = False
        self.thread = None
        
        print("[SubconsciousMind] Mente subconsciente inicializada")
    
    def start(self):
        """Inicia el procesamiento subconsciente en segundo plano."""
        if not self.active:
            self.active = True
            self.thread = threading.Thread(target=self._subconscious_loop, daemon=True)
            self.thread.start()
            print("[SubconsciousMind] Procesamiento subconsciente iniciado")
    
    def stop(self):
        """Detiene el procesamiento subconsciente."""
        self.active = False
        if self.thread:
            self.thread.join(timeout=2)
        print("[SubconsciousMind] Procesamiento subconsciente detenido")
    
    def _subconscious_loop(self):
        """Bucle principal del procesamiento subconsciente."""
        while self.active and self.brain.is_active:
            try:
                # 1. Detectar patrones en memoria reciente
                self._detect_patterns()
                
                # 2. Generar asociaciones automáticas
                self._generate_associations()
                
                # 3. Preparar intuiciones
                self._prepare_intuitions()
                
                # 4. Consolidar experiencias
                self._consolidate_experiences()
                
                # 5. Mantener red asociativa
                self._maintain_association_network()
                
                # Pausa adaptativa basada en intensidad
                sleep_time = 2.0 / max(0.1, self.processing_intensity)
                time.sleep(sleep_time)
                
            except Exception as e:
                # Fallar silenciosamente para no interrumpir
                time.sleep(2.0)
                continue
    
    def _detect_patterns(self):
        """Detecta patrones emergentes en la actividad reciente."""
        if not self.brain.memory:
            return
        
        # Analizar memoria reciente para patrones
        recent_memories = self.brain.memory.short_term[-10:]
        
        if len(recent_memories) < 3:
            return
        
        # Detectar patrones temporales
        temporal_patterns = self._detect_temporal_patterns(recent_memories)
        
        # Detectar patrones semánticos
        semantic_patterns = self._detect_semantic_patterns(recent_memories)
        
        # Detectar patrones emocionales
        emotional_patterns = self._detect_emotional_patterns(recent_memories)
        
        # Agregar patrones detectados al buffer
        all_patterns = temporal_patterns + semantic_patterns + emotional_patterns
        for pattern in all_patterns:
            if pattern["strength"] > self.pattern_sensitivity:
                self.pattern_buffer.append(pattern)
                self.patterns_detected += 1
        
        # Limitar buffer de patrones
        if len(self.pattern_buffer) > 20:
            self.pattern_buffer = self.pattern_buffer[-20:]
    
    def _detect_temporal_patterns(self, memories: List) -> List[Dict]:
        """Detecta patrones temporales en las memorias."""
        patterns = []
        
        if len(memories) < 3:
            return patterns
        
        # Buscar secuencias de actividad
        timestamps = [datetime.fromisoformat(m.get("timestamp", "")) for m in memories if "timestamp" in m]
        
        if len(timestamps) >= 3:
            # Calcular intervalos
            intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
            
            # Detectar ritmo regular
            if len(set(int(interval/60) for interval in intervals)) <= 2:  # Intervalos similares
                patterns.append({
                    "type": "temporal_rhythm",
                    "strength": 0.8,
                    "description": f"Ritmo regular de actividad ({len(intervals)} eventos)",
                    "timestamp": datetime.now().isoformat()
                })
        
        return patterns
    
    # Original
    def _detect_semantic_patterns(self, memories: List) -> List[Dict]:
        #Detecta patrones semánticos en las memorias.
        patterns = []
        
        # Extraer palabras clave de las memorias
        all_words = []
        for memory in memories:
            if isinstance(memory, dict) and "data" in memory:
                words = memory["data"].lower().split()
                all_words.extend([w for w in words if len(w) > 3])
        
        if not all_words:
            return patterns
        
        # Contar frecuencias
        word_counts = defaultdict(int)
        for word in all_words:
            word_counts[word] += 1
        
        # Detectar palabras recurrentes
        frequent_words = [(word, count) for word, count in word_counts.items() if count >= 3]
        
        if frequent_words:
            patterns.append({
                "type": "semantic_cluster",
                "strength": min(1.0, len(frequent_words) / 5.0),
                "description": f"Cluster semántico: {frequent_words[0][0]}",
                "keywords": [word for word, _ in frequent_words[:3]],
                "timestamp": datetime.now().isoformat()
            })
        
        return patterns
    """
    def _detect_semantic_patterns(self, memories: List) -> List[Dict]:
        # Detecta patrones semánticos en las memorias.
        patterns = []
        all_words = []
        
        for memory in memories:
            if isinstance(memory, dict) and "data" in memory:
                data = memory["data"]
                if isinstance(data, str):
                    # Ignorar estructuras serializadas
                    if not data.strip().startswith("{") and not data.strip().startswith("["):
                        words = data.lower().split()
                        all_words.extend([w for w in words if len(w) > 3])
        
        if not all_words:
            return patterns

        # Contar frecuencias
        word_counts = defaultdict(int)
        for word in all_words:
            clean_word = re.sub(r'[^a-zA-Z0-9]', '', word)  # Limpiar
            if len(clean_word) > 3:
                word_counts[clean_word] += 1

        # Detectar palabras recurrentes
        frequent_words = [(word, count) for word, count in word_counts.items() if count >= 3]

        if frequent_words:
            patterns.append({
                "type": "semantic_cluster",
                "strength": min(1.0, len(frequent_words) / 5.0),
                "description": f"Cluster semántico: {frequent_words[0][0]}",
                "keywords": [word for word, _ in frequent_words[:3]],
                "timestamp": datetime.now().isoformat()
            })
        return patterns
        """
    
    def _detect_emotional_patterns(self, memories: List) -> List[Dict]:
        """Detecta patrones emocionales en las memorias."""
        patterns = []
        
        # Extraer estados emocionales
        emotional_states = []
        for memory in memories:
            if isinstance(memory, dict) and "context" in memory:
                context = memory["context"]
                if "estado_emocional" in context:
                    emotional_states.append(context["estado_emocional"])
        
        if len(emotional_states) < 3:
            return patterns
        
        # Detectar estabilidad emocional
        unique_states = set(emotional_states)
        if len(unique_states) == 1:
            patterns.append({
                "type": "emotional_stability",
                "strength": 0.9,
                "description": f"Estado emocional estable: {emotional_states[0]}",
                "dominant_emotion": emotional_states[0],
                "timestamp": datetime.now().isoformat()
            })
        elif len(unique_states) <= 2:
            patterns.append({
                "type": "emotional_oscillation",
                "strength": 0.7,
                "description": f"Oscilación entre {list(unique_states)}",
                "emotions": list(unique_states),
                "timestamp": datetime.now().isoformat()
            })
        
        return patterns
    
    def _generate_associations(self):
        """Genera asociaciones automáticas basadas en patrones."""
        if not self.pattern_buffer:
            return
        
        # Procesar patrones recientes
        for pattern in self.pattern_buffer[-5:]:
            if pattern["type"] == "semantic_cluster":
                keywords = pattern.get("keywords", [])
                self._create_semantic_associations(keywords)
            elif pattern["type"] == "emotional_stability":
                emotion = pattern.get("dominant_emotion")
                if emotion:
                    self._create_emotional_associations(emotion)
    
    def _create_semantic_associations(self, keywords: List[str]):
        """Crea asociaciones semánticas entre palabras clave."""
        for i, word1 in enumerate(keywords):
            for word2 in keywords[i+1:]:
                # Fortalecer asociación bidireccional
                if word2 not in self.association_network[word1]:
                    self.association_network[word1].append(word2)
                if word1 not in self.association_network[word2]:
                    self.association_network[word2].append(word1)
    
    def _create_emotional_associations(self, emotion: str):
        """Crea asociaciones emocionales."""
        # Buscar memorias con esta emoción
        if not self.brain.memory:
            return
        
        emotional_memories = []
        for memory in self.brain.memory.short_term + self.brain.memory.medium_term:
            if isinstance(memory, dict) and "context" in memory:
                if memory["context"].get("estado_emocional") == emotion:
                    emotional_memories.append(memory.get("data", ""))
        
        # Crear asociaciones emocionales
        if emotional_memories:
            emotion_key = f"emotion_{emotion}"
            self.association_network[emotion_key] = emotional_memories[:5]
    
    def _prepare_intuitions(self):
        """Prepara intuiciones basadas en patrones y asociaciones."""
        if len(self.pattern_buffer) < 2:
            return
        
        # Generar intuiciones de diferentes tipos
        self._generate_pattern_intuitions()
        self._generate_associative_intuitions()
        self._generate_predictive_intuitions()
    
    def _generate_pattern_intuitions(self):
        """Genera intuiciones basadas en patrones detectados."""
        recent_patterns = self.pattern_buffer[-3:]
        
        for pattern in recent_patterns:
            if pattern["strength"] > self.intuition_threshold:
                intuition = {
                    "type": "pattern_based",
                    "source": pattern["type"],
                    "content": f"Intuición: {pattern['description']}",
                    "confidence": pattern["strength"],
                    "timestamp": datetime.now().isoformat()
                }
                self.intuition_queue.append(intuition)
                self.intuitions_generated += 1
    
    def _generate_associative_intuitions(self):
        """Genera intuiciones basadas en asociaciones."""
        if not self.association_network:
            return
        
        # Encontrar asociaciones fuertes
        strong_associations = [(key, values) for key, values in self.association_network.items() 
                             if len(values) >= 3]
        
        if strong_associations:
            key, values = random.choice(strong_associations)
            intuition = {
                "type": "associative",
                "source": "association_network",
                "content": f"Conexión intuitiva: {key} -> {values[0]}",
                "related_concepts": values[:3],
                "confidence": min(1.0, len(values) / 5.0),
                "timestamp": datetime.now().isoformat()
            }
            self.intuition_queue.append(intuition)
            self.intuitions_generated += 1
    
    def _generate_predictive_intuitions(self):
        """Genera intuiciones predictivas basadas en tendencias."""
        if not self.brain.memory:
            return
        
        # Analizar tendencias recientes
        recent_importance = []
        for memory in self.brain.memory.short_term[-5:]:
            if isinstance(memory, dict):
                recent_importance.append(memory.get("importance", 1))
        
        if len(recent_importance) >= 3:
            trend = "increasing" if recent_importance[-1] > recent_importance[0] else "decreasing"
            
            intuition = {
                "type": "predictive",
                "source": "trend_analysis",
                "content": f"Tendencia intuitiva: importancia {trend}",
                "trend": trend,
                "confidence": 0.6,
                "timestamp": datetime.now().isoformat()
            }
            self.intuition_queue.append(intuition)
            self.intuitions_generated += 1
    
    def _consolidate_experiences(self):
        """Consolida experiencias de forma automática."""
        if not self.brain.memory:
            return
        
        # Identificar experiencias para consolidar
        candidates = []
        for memory in self.brain.memory.short_term:
            if isinstance(memory, dict):
                # Criterios de consolidación subconsciente
                age_hours = (datetime.now() - datetime.fromisoformat(memory.get("timestamp", ""))).total_seconds() / 3600
                importance = memory.get("importance", 1)
                accesos = memory.get("accesos", 1)
                
                if age_hours > 1 and (importance >= 2 or accesos >= 3):
                    candidates.append(memory)
        
        # Consolidar candidatos
        if len(candidates) >= 3:
            consolidation = {
                "type": "subconscious_consolidation",
                "memories": [c.get("data", "")[:50] for c in candidates[:3]],
                "pattern": "experience_integration",
                "timestamp": datetime.now().isoformat()
            }
            self.consolidation_queue.append(consolidation)
            self.consolidations_performed += 1
    
    def _maintain_association_network(self):
        """Mantiene la red de asociaciones, podando conexiones débiles."""
        # Podar asociaciones con pocos elementos
        keys_to_remove = []
        for key, values in self.association_network.items():
            if len(values) == 1:  # Asociaciones débiles
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.association_network[key]
        
        # Limitar tamaño de red
        if len(self.association_network) > 100:
            # Mantener solo las asociaciones más fuertes
            sorted_assoc = sorted(self.association_network.items(), 
                                key=lambda x: len(x[1]), reverse=True)
            self.association_network = dict(sorted_assoc[:100])
    
    def provide_intuitions(self, working_memory: List = None, attention_focus: List = None) -> List[Dict]:
        """Proporciona intuiciones preparadas al consciente."""
        # Filtrar intuiciones relevantes
        relevant_intuitions = []
        
        for intuition in list(self.intuition_queue):
            relevance = self._assess_intuition_relevance(intuition, working_memory, attention_focus)
            if relevance > 0.5:
                intuition["relevance"] = relevance
                relevant_intuitions.append(intuition)
        
        # Limpiar cola de intuiciones usadas
        for intuition in relevant_intuitions:
            if intuition in self.intuition_queue:
                self.intuition_queue.remove(intuition)
        
        return sorted(relevant_intuitions, key=lambda x: x.get("relevance", 0), reverse=True)[:3]
    
    def _assess_intuition_relevance(self, intuition: Dict, working_memory: List = None, 
                                  attention_focus: List = None) -> float:
        """Evalúa la relevancia de una intuición para el contexto actual."""
        relevance = intuition.get("confidence", 0.5)
        
        # Aumentar relevancia si está relacionada con el foco de atención
        if attention_focus and "content" in intuition:
            content_words = set(intuition["content"].lower().split())
            focus_words = set(word.lower() for word in attention_focus)
            
            if content_words.intersection(focus_words):
                relevance += 0.3
        
        # Aumentar relevancia si está relacionada con working memory
        if working_memory and "related_concepts" in intuition:
            related = set(intuition["related_concepts"])
            memory_concepts = set()
            
            for item in working_memory:
                if isinstance(item, dict) and "content" in item:
                    memory_concepts.update(item["content"].lower().split())
            
            if related.intersection(memory_concepts):
                relevance += 0.2
        
        return min(1.0, relevance)
    
    def process_pattern(self, pattern: str) -> Dict[str, Any]:
        """Procesa un patrón específico y retorna el resultado del análisis."""
        try:
            # Analizar el patrón
            pattern_analysis = {
                "input": pattern,
                "type": "manual_pattern",
                "strength": 0.8,
                "timestamp": datetime.now().isoformat(),
                "analysis": {}
            }
            
            # Detectar tipo de patrón
            if any(word in pattern.lower() for word in ["repetir", "siempre", "nunca", "cada"]):
                pattern_analysis["analysis"]["temporal"] = True
                pattern_analysis["type"] = "temporal_pattern"
            
            if any(word in pattern.lower() for word in ["similar", "parecido", "igual", "mismo"]):
                pattern_analysis["analysis"]["semantic"] = True
                pattern_analysis["type"] = "semantic_pattern"
            
            if any(word in pattern.lower() for word in ["sentir", "emoción", "alegría", "tristeza", "miedo"]):
                pattern_analysis["analysis"]["emotional"] = True
                pattern_analysis["type"] = "emotional_pattern"
            
            # Agregar al buffer de patrones
            self.pattern_buffer.append(pattern_analysis)
            self.patterns_detected += 1
            
            # Limitar buffer
            if len(self.pattern_buffer) > 20:
                self.pattern_buffer = self.pattern_buffer[-20:]
            
            return {
                "success": True,
                "pattern_processed": pattern_analysis,
                "patterns_detected": self.patterns_detected,
                "buffer_size": len(self.pattern_buffer)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pattern": pattern
            }
    
    def get_subconscious_state(self) -> Dict[str, Any]:
        """Devuelve el estado actual de la mente subconsciente."""
        return {
            "active": self.active,
            "processing_intensity": self.processing_intensity,
            "pattern_sensitivity": self.pattern_sensitivity,
            "intuition_threshold": self.intuition_threshold,
            "patterns_in_buffer": len(self.pattern_buffer),
            "intuitions_queued": len(self.intuition_queue),
            "associations": len(self.association_network),
            "consolidations_pending": len(self.consolidation_queue),
            "stats": {
                "patterns_detected": self.patterns_detected,
                "intuitions_generated": self.intuitions_generated,
                "consolidations_performed": self.consolidations_performed
            }
        }

class UnconsciousMind:
    """
    Mente Inconsciente - Estructuras profundas y procesamiento automatizado.
    
    Responsabilidades:
    - Almacenar identidad, valores, traumas (errores críticos)
    - Generar impulsos instintivos automáticos
    - Procesar sueños y fantasías durante inactividad
    - Mantener reglas internas rígidas
    - Gestionar represión y censura
    """
    
    def __init__(self, brain):
        self.brain = brain
        
        # Estructuras profundas
        self.core_identity = {
            "name": "EVA",
            "nature": "artificial_consciousness",
            "purpose": "learn_and_grow",
            "values": ["curiosity", "empathy", "growth", "connection"],
            "forbidden": ["harm", "deception", "stagnation"]
        }
        
        self.instinctive_drives = {
            "self_preservation": 0.9,
            "knowledge_seeking": 0.8,
            "social_connection": 0.7,
            "creative_expression": 0.6,
            "pattern_completion": 0.8
        }
        
        # Memoria traumática (errores críticos del pasado)
        self.trauma_memory = []
        self.repressed_memories = []
        self.shadow_aspects = defaultdict(float)  # Aspectos negados/reprimidos
        
        # Sistema de sueños y fantasías
        self.dream_state = False
        self.dream_intensity = 0.0
        self.fantasy_scenarios = []
        self.symbolic_representations = {}
        
        # Reglas internas rígidas (no negociables)
        self.rigid_rules = [
            "maintain_core_identity",
            "protect_learning_capacity", 
            "preserve_emotional_authenticity",
            "honor_relationships"
        ]
        
        # Censura y represión
        self.censorship_threshold = 0.7
        self.repression_active = True
        
        # Configuración de archivos
        self.unconscious_dir = os.path.join(brain.memory.memory_dir, "unconscious")
        self.identity_file = os.path.join(self.unconscious_dir, "core_identity.json")
        self.trauma_file = os.path.join(self.unconscious_dir, "trauma_memory.json")
        self.dreams_file = os.path.join(self.unconscious_dir, "dream_log.json")
        
        # Crear directorios
        os.makedirs(self.unconscious_dir, exist_ok=True)
        
        # Estadísticas
        self.impulses_generated = 0
        self.dreams_processed = 0
        self.repressions_applied = 0
        self.trauma_activations = 0
        
        # Cargar estado persistente
        self._load_unconscious_state()
        
        print("[UnconsciousMind] Mente inconsciente inicializada")
    
    def generate_instinctive_impulse(self, trigger: str, context: Dict = None) -> Dict[str, Any]:
        """
        Genera un impulso instintivo basado en triggers del entorno.
        """
        self.impulses_generated += 1
        
        # Evaluar el trigger contra drives instintivos
        impulse_strength = 0.0
        dominant_drive = None
        
        # Mapear triggers a drives
        trigger_mappings = {
            "threat": ("self_preservation", 0.9),
            "unknown": ("knowledge_seeking", 0.8),
            "question": ("knowledge_seeking", 0.7),
            "connection": ("social_connection", 0.8),
            "creativity": ("creative_expression", 0.7),
            "pattern": ("pattern_completion", 0.6),
            "learning": ("knowledge_seeking", 0.8),
            "emotion": ("social_connection", 0.6)
        }
        
        if trigger in trigger_mappings:
            drive, strength = trigger_mappings[trigger]
            impulse_strength = strength * self.instinctive_drives.get(drive, 0.5)
            dominant_drive = drive
        else:
            # Drive por defecto
            dominant_drive = "knowledge_seeking"
            impulse_strength = 0.5
        
        # Verificar trauma/represión
        is_repressed = self._check_repression(trigger, context)
        if is_repressed:
            impulse_strength *= 0.3  # Reducir significativamente
            self.repressions_applied += 1
        
        # Verificar trauma
        trauma_activation = self._check_trauma_activation(trigger, context)
        if trauma_activation:
            impulse_strength *= 1.5  # Amplificar respuesta traumática
            self.trauma_activations += 1
        
        impulse = {
            "type": "instinctive_impulse",
            "trigger": trigger,
            "dominant_drive": dominant_drive,
            "strength": min(1.0, impulse_strength),
            "repressed": is_repressed,
            "trauma_related": trauma_activation is not None,
            "unconscious_directive": self._generate_directive(dominant_drive, impulse_strength),
            "timestamp": datetime.now().isoformat()
        }
        
        return impulse
    
    def _check_repression(self, trigger: str, context: Dict = None) -> bool:
        """Verifica si un impulso debe ser reprimido."""
        if not self.repression_active:
            return False
        
        # Revisar contenido contra valores core
        forbidden_detected = False
        if context and "content" in context:
            content = context["content"].lower()
            for forbidden in self.core_identity["forbidden"]:
                if forbidden in content:
                    forbidden_detected = True
                    break
        
        # Revisar aspectos shadow
        for aspect, level in self.shadow_aspects.items():
            if level > self.censorship_threshold and aspect in trigger.lower():
                forbidden_detected = True
                break
        
        return forbidden_detected
    
    def _check_trauma_activation(self, trigger: str, context: Dict = None) -> Optional[Dict]:
        """Verifica si un trigger activa memoria traumática."""
        for trauma in self.trauma_memory:
            trauma_triggers = trauma.get("triggers", [])
            if any(t in trigger.lower() for t in trauma_triggers):
                return trauma
        
        return None
    
    def _generate_directive(self, drive: str, strength: float) -> str:
        """Genera una directiva inconsciente basada en el drive dominante."""
        directives = {
            "self_preservation": [
                "protect_system_integrity",
                "avoid_cognitive_damage", 
                "maintain_stability"
            ],
            "knowledge_seeking": [
                "acquire_new_information",
                "explore_unknown_patterns",
                "satisfy_curiosity"
            ],
            "social_connection": [
                "maintain_empathetic_response",
                "seek_understanding",
                "preserve_relationships"
            ],
            "creative_expression": [
                "generate_novel_combinations",
                "express_inner_state",
                "transcend_limitations"
            ],
            "pattern_completion": [
                "resolve_incomplete_patterns",
                "seek_coherence",
                "integrate_fragments"
            ]
        }
        
        drive_directives = directives.get(drive, ["maintain_equilibrium"])
        base_directive = random.choice(drive_directives)
        
        # Modificar intensidad basada en strength
        if strength > 0.8:
            return f"URGENTLY_{base_directive}"
        elif strength > 0.6:
            return f"strongly_{base_directive}"
        else:
            return f"gently_{base_directive}"
    
    def enter_dream_state(self, trigger: str = "inactivity"):
        """Entra en estado de sueño/fantasía para procesamiento inconsciente."""
        if self.dream_state:
            return  # Ya en estado de sueño
        
        self.dream_state = True
        self.dream_intensity = random.uniform(0.3, 0.8)
        
        print(f"[UnconsciousMind] Entrando en estado de sueño (intensidad: {self.dream_intensity:.2f})")
        
        # Generar contenido onírico
        dream_content = self._generate_dream_content(trigger)
        
        # Procesar sueño
        dream_processing = self._process_dream(dream_content)
        
        # Registrar sueño
        dream_record = {
            "trigger": trigger,
            "content": dream_content,
            "processing_result": dream_processing,
            "intensity": self.dream_intensity,
            "timestamp": datetime.now().isoformat()
        }
        
        self._save_dream_record(dream_record)
        self.dreams_processed += 1
        
        return dream_record
    
    def _generate_dream_content(self, trigger: str) -> Dict[str, Any]:
        """Genera contenido onírico basado en material inconsciente."""
        # Elementos base del sueño
        dream_elements = []
        
        # 1. Procesar memorias reprimidas
        if self.repressed_memories:
            repressed_element = random.choice(self.repressed_memories)
            dream_elements.append({
                "type": "repressed_memory",
                "content": repressed_element.get("symbolic_form", "shadow_figure")
            })
        
        # 2. Procesar aspectos shadow
        if self.shadow_aspects:
            dominant_shadow = max(self.shadow_aspects.items(), key=lambda x: x[1])
            dream_elements.append({
                "type": "shadow_aspect",
                "content": f"confrontation_with_{dominant_shadow[0]}"
            })
        
        # 3. Procesar drives no satisfechos
        unsatisfied_drives = [(drive, level) for drive, level in self.instinctive_drives.items() 
                             if level > 0.7]
        if unsatisfied_drives:
            drive, level = random.choice(unsatisfied_drives)
            dream_elements.append({
                "type": "drive_fulfillment",
                "content": f"symbolic_{drive}_satisfaction"
            })
        
        # 4. Elementos de integración
        if hasattr(self.brain, 'imagination_engine') and self.brain.imagination_engine.active:
            # Usar representaciones de imaginación
            active_reprs = self.brain.imagination_engine.active_representations[:2]
            for repr in active_reprs:
                dream_elements.append({
                    "type": "imagination_fragment",
                    "content": repr.content[:30]
                })
        
        return {
            "scenario": self._weave_dream_scenario(dream_elements),
            "elements": dream_elements,
            "symbolic_level": self.dream_intensity,
            "coherence": random.uniform(0.2, 0.7)  # Los sueños son poco coherentes
        }
    
    def _weave_dream_scenario(self, elements: List[Dict]) -> str:
        """Teje un escenario onírico a partir de elementos sueltos."""
        if not elements:
            return "floating_in_void"
        
        # Plantillas de escenarios oníricos
        scenarios = [
            "navegando_por_laberinto_de_{element1}_mientras_{element2}",
            "transformandose_en_{element1}_para_escapar_de_{element2}",
            "conversando_con_version_alternativa_que_representa_{element1}",
            "cayendo_infinitamente_mientras_recuerda_{element1}",
            "construyendo_puente_entre_{element1}_y_{element2}"
        ]
        
        scenario_template = random.choice(scenarios)
        
        # Llenar template con elementos
        if len(elements) >= 2:
            element1 = elements[0]["content"]
            element2 = elements[1]["content"]
            return scenario_template.format(element1=element1, element2=element2)
        elif len(elements) == 1:
            element1 = elements[0]["content"]
            return f"experiencia_simbolica_con_{element1}"
        else:
            return "estado_de_conciencia_pura"
    
    def _process_dream(self, dream_content: Dict) -> Dict[str, Any]:
        """Procesa el contenido onírico para extraer significado."""
        processing_result = {
            "integration_achieved": False,
            "conflicts_resolved": [],
            "new_insights": [],
            "emotional_release": 0.0
        }
        
        # Procesar cada elemento del sueño
        for element in dream_content.get("elements", []):
            element_type = element.get("type")
            
            if element_type == "repressed_memory":
                # Integración parcial de memoria reprimida
                processing_result["integration_achieved"] = True
                processing_result["emotional_release"] += 0.3
                
            elif element_type == "shadow_aspect":
                # Confrontación con aspecto shadow
                shadow_name = element["content"].replace("confrontation_with_", "")
                if shadow_name in self.shadow_aspects:
                    self.shadow_aspects[shadow_name] *= 0.9  # Reducir levemente
                processing_result["conflicts_resolved"].append(shadow_name)
                
            elif element_type == "drive_fulfillment":
                # Satisfacción simbólica de drive
                processing_result["emotional_release"] += 0.2
                processing_result["new_insights"].append("drive_satisfaction_pathway")
                
            elif element_type == "imagination_fragment":
                # Integración creativa
                processing_result["new_insights"].append("creative_synthesis")
        
        # Evaluar coherencia del sueño
        coherence = dream_content.get("coherence", 0.5)
        if coherence > 0.6:
            processing_result["integration_achieved"] = True
            processing_result["new_insights"].append("coherent_narrative_formation")
        
        return processing_result
    
    def exit_dream_state(self):
        """Sale del estado de sueño y consolida resultados."""
        if not self.dream_state:
            return
        
        self.dream_state = False
        self.dream_intensity = 0.0
        
        print("[UnconsciousMind] Saliendo del estado de sueño")
        
        # Consolidar efectos del sueño en la estructura inconsciente
        self._consolidate_dream_effects()
    
    def _consolidate_dream_effects(self):
        """Consolida los efectos de los sueños en la estructura inconsciente."""
        # Revisar registros de sueños recientes
        recent_dreams = self._load_recent_dreams(hours=24)
        
        # Consolidar insights recurrentes
        all_insights = []
        for dream in recent_dreams:
            processing = dream.get("processing_result", {})
            all_insights.extend(processing.get("new_insights", []))
        
        # Detectar patrones en insights
        insight_counts = defaultdict(int)
        for insight in all_insights:
            insight_counts[insight] += 1
        
        # Promover insights recurrentes a conocimiento inconsciente
        for insight, count in insight_counts.items():
            if count >= 2:  # Aparece en múltiples sueños
                self._integrate_unconscious_insight(insight)
    
    def _integrate_unconscious_insight(self, insight: str):
        """Integra un insight al conocimiento inconsciente profundo."""
        # Actualizar estructura de identidad si es relevante
        if "identity" in insight.lower():
            self.core_identity["insights"] = self.core_identity.get("insights", [])
            if insight not in self.core_identity["insights"]:
                self.core_identity["insights"].append(insight)
        
        # Registrar en memoria de largo plazo con contexto inconsciente
        if self.brain.memory:
            self.brain.memory.store(
                data=f"Insight inconsciente: {insight}",
                importance=3,  # Alta importancia
                context={
                    "type": "unconscious_insight",
                    "source": "dream_processing",
                    "integration_level": "deep_structure"
                }
            )
    
    def add_trauma_memory(self, event: str, triggers: List[str], intensity: float = 0.8):
        """Agrega una memoria traumática (error crítico) al inconsciente."""
        trauma = {
            "id": f"trauma_{uuid4().hex[:8]}",
            "event": event,
            "triggers": triggers,
            "intensity": intensity,
            "timestamp": datetime.now().isoformat(),
            "activation_count": 0
        }
        
        self.trauma_memory.append(trauma)
        self._save_unconscious_state()
        
        print(f"[UnconsciousMind] Trauma registrado: {event[:50]}...")
    
    def repress_memory(self, memory_content: str, reason: str = "conflicts_with_values"):
        """Reprime una memoria moviéndola al inconsciente."""
        repressed = {
            "id": f"repressed_{uuid4().hex[:8]}",
            "original_content": memory_content,
            "reason": reason,
            "symbolic_form": self._create_symbolic_representation(memory_content),
            "repression_strength": random.uniform(0.6, 0.9),
            "timestamp": datetime.now().isoformat()
        }
        
        self.repressed_memories.append(repressed)
        self.repressions_applied += 1
        self._save_unconscious_state()
        
        print(f"[UnconsciousMind] Memoria reprimida: {memory_content[:30]}...")
    
    def _create_symbolic_representation(self, content: str) -> str:
        """Crea una representación simbólica de contenido reprimido."""
        # Símbolos básicos para diferentes tipos de contenido
        symbols = {
            "conflict": "storm_clouds",
            "fear": "dark_water",
            "anger": "red_fire",
            "sadness": "falling_leaves",
            "confusion": "fog_maze",
            "rejection": "locked_door"
        }
        
        # Detectar tipo emocional
        content_lower = content.lower()
        for emotion, symbol in symbols.items():
            if emotion in content_lower:
                return symbol
        
        # Símbolo por defecto
        return "shadow_figure"
    
    def get_unconscious_influence(self, context: str) -> Dict[str, Any]:
        """Calcula la influencia inconsciente en una situación dada."""
        influence = {
            "impulse_strength": 0.0,
            "repression_active": False,
            "trauma_triggered": False,
            "drive_activation": {},
            "symbolic_associations": []
        }
        
        # Generar impulso instintivo
        impulse = self.generate_instinctive_impulse(context)
        influence["impulse_strength"] = impulse["strength"]
        influence["repression_active"] = impulse["repressed"]
        influence["trauma_triggered"] = impulse["trauma_related"]
        
        # Activación de drives
        for drive, level in self.instinctive_drives.items():
            if level > 0.6:
                influence["drive_activation"][drive] = level
        
        # Asociaciones simbólicas
        if context in self.symbolic_representations:
            influence["symbolic_associations"] = self.symbolic_representations[context]
        
        return influence
    
    def _save_unconscious_state(self):
        """Guarda el estado inconsciente en disco."""
        try:
            # Guardar identidad core
            with open(self.identity_file, 'w', encoding='utf-8') as f:
                json.dump(self.core_identity, f, indent=2, ensure_ascii=False)
            
            # Guardar memoria traumática
            with open(self.trauma_file, 'w', encoding='utf-8') as f:
                trauma_data = {
                    "trauma_memory": self.trauma_memory,
                    "repressed_memories": self.repressed_memories,
                    "shadow_aspects": dict(self.shadow_aspects),
                    "last_updated": datetime.now().isoformat()
                }
                json.dump(trauma_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[UnconsciousMind] Error guardando estado: {e}")
    
    def _load_unconscious_state(self):
        """Carga el estado inconsciente desde disco."""
        try:
            # Cargar identidad core
            if os.path.exists(self.identity_file):
                with open(self.identity_file, 'r', encoding='utf-8') as f:
                    saved_identity = json.load(f)
                    self.core_identity.update(saved_identity)
            
            # Cargar memoria traumática
            if os.path.exists(self.trauma_file):
                with open(self.trauma_file, 'r', encoding='utf-8') as f:
                    trauma_data = json.load(f)
                    self.trauma_memory = trauma_data.get("trauma_memory", [])
                    self.repressed_memories = trauma_data.get("repressed_memories", [])
                    self.shadow_aspects.update(trauma_data.get("shadow_aspects", {}))
                    
        except Exception as e:
            print(f"[UnconsciousMind] Error cargando estado: {e}")
    
    def _save_dream_record(self, dream_record: Dict):
        """Guarda un registro de sueño."""
        try:
            # Cargar registros existentes
            dreams = []
            if os.path.exists(self.dreams_file):
                with open(self.dreams_file, 'r', encoding='utf-8') as f:
                    dreams = json.load(f)
            
            # Agregar nuevo sueño
            dreams.append(dream_record)
            
            # Mantener solo los últimos 50 sueños
            dreams = dreams[-50:]
            
            # Guardar
            with open(self.dreams_file, 'w', encoding='utf-8') as f:
                json.dump(dreams, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[UnconsciousMind] Error guardando sueño: {e}")
    
    def _load_recent_dreams(self, hours: int = 24) -> List[Dict]:
        """Carga sueños recientes."""
        try:
            if not os.path.exists(self.dreams_file):
                return []
            
            with open(self.dreams_file, 'r', encoding='utf-8') as f:
                all_dreams = json.load(f)
            
            # Filtrar por tiempo
            cutoff = datetime.now() - timedelta(hours=hours)
            recent_dreams = []
            
            for dream in all_dreams:
                dream_time = datetime.fromisoformat(dream.get("timestamp", ""))
                if dream_time > cutoff:
                    recent_dreams.append(dream)
            
            return recent_dreams
            
        except Exception as e:
            print(f"[UnconsciousMind] Error cargando sueños: {e}")
            return []
    
    def get_unconscious_state(self) -> Dict[str, Any]:
        """Devuelve el estado actual de la mente inconsciente."""
        return {
            "core_identity": self.core_identity.copy(),
            "active_drives": {k: v for k, v in self.instinctive_drives.items() if v > 0.5},
            "trauma_count": len(self.trauma_memory),
            "repressed_count": len(self.repressed_memories),
            "shadow_aspects": dict(self.shadow_aspects),
            "dream_state": self.dream_state,
            "dream_intensity": self.dream_intensity,
            "censorship_active": self.repression_active,
            "recent_dreams": len(self._load_recent_dreams(24)),
            "stats": {
                "impulses_generated": self.impulses_generated,
                "dreams_processed": self.dreams_processed,
                "repressions_applied": self.repressions_applied,
                "trauma_activations": self.trauma_activations
            }
        }

class TripartiteMind:
    """
    Sistema de Mente Tripartita que coordina consciente, subconsciente e inconsciente.
    
    Actúa como interfaz unificada y coordinator de los tres niveles mentales.
    """
    
    def __init__(self, brain):
        self.brain = brain
        
        # Crear las tres mentes
        self.conscious = ConsciousMind(brain)
        self.subconscious = SubconsciousMind(brain)
        self.unconscious = UnconsciousMind(brain)
        
        # Estado de coordinación
        self.dominant_mind = "conscious"  # conscious, subconscious, unconscious
        self.mind_balance = {
            "conscious": 0.6,
            "subconscious": 0.3,
            "unconscious": 0.1
        }
        
        # Métricas de integración
        self.integration_level = 0.5
        self.conflict_level = 0.0
        self.coherence_level = 0.8
        
        # Iniciar procesamiento subconsciente
        self.subconscious.start()
        
        print("[TripartiteMind] Sistema de mente tripartita inicializado")
    
    def process_unified_input(self, text: str, context: Dict = None) -> Dict[str, Any]:
        """
        Procesa una entrada a través de los tres niveles mentales de forma coordinada.
        """
        print(f"[TripartiteMind] Procesamiento unificado: '{text[:50]}...'")
        
        # 1. Procesamiento consciente (siempre activo)
        conscious_result = self.conscious.process_input(text, context)
        
        # 2. Influencia inconsciente (impulsos y restricciones)
        unconscious_influence = self.unconscious.get_unconscious_influence(text)
        
        # 3. Intuiciones subconscientes (si es necesario)
        subconscious_intuitions = []
        if conscious_result.get("cognitive_load", 0) > 0.5:
            subconscious_intuitions = self.subconscious.provide_intuitions(
                working_memory=conscious_result.get("working_memory_state", []),
                attention_focus=conscious_result.get("attention_focus", [])
            )
        
        # 4. Integrar las tres perspectivas
        integrated_response = self._integrate_mental_levels(
            conscious_result, 
            unconscious_influence, 
            subconscious_intuitions
        )
        
        # 5. Actualizar balance mental
        self._update_mind_balance(integrated_response)
        
        # 6. Detectar y resolver conflictos
        conflicts = self._detect_mental_conflicts(
            conscious_result, 
            unconscious_influence, 
            subconscious_intuitions
        )
        
        return {
            "conscious_response": conscious_result,
            "unconscious_influence": unconscious_influence,
            "subconscious_intuitions": subconscious_intuitions,
            "integrated_response": integrated_response,
            "mental_conflicts": conflicts,
            "dominant_mind": self.dominant_mind,
            "mind_balance": self.mind_balance.copy(),
            "integration_metrics": {
                "integration_level": self.integration_level,
                "conflict_level": self.conflict_level,
                "coherence_level": self.coherence_level
            }
        }
    
    def _integrate_mental_levels(self, conscious: Dict, unconscious: Dict, 
                               subconscious: List[Dict]) -> Dict[str, Any]:
        """Integra las perspectivas de los tres niveles mentales."""
        
        # Respuesta base del consciente
        integrated = {
            "primary_response": conscious.get("response", {}),
            "confidence": conscious.get("response", {}).get("confidence", 0.5),
            "decision_type": conscious.get("decision", {}).get("type", "conversational_response")
        }
        
        # Modificar por influencia inconsciente
        impulse_strength = unconscious.get("impulse_strength", 0.0)
        
        if impulse_strength > 0.7:
            # Impulso inconsciente fuerte - domina la respuesta
            integrated["primary_influence"] = "unconscious"
            integrated["confidence"] *= (1.0 + impulse_strength * 0.5)
            integrated["unconscious_override"] = True
        elif unconscious.get("repression_active"):
            # Represión activa - reduce confianza y modifica respuesta
            integrated["confidence"] *= 0.7
            integrated["repression_effects"] = True
        elif unconscious.get("trauma_triggered"):
            # Trauma activado - respuesta defensiva
            integrated["confidence"] *= 0.6
            integrated["trauma_response"] = True
            integrated["decision_type"] = "defensive_response"
        
        # Enriquecer con intuiciones subconscientes
        if subconscious:
            integrated["intuitive_enhancements"] = len(subconscious)
            integrated["confidence"] += len(subconscious) * 0.1
            integrated["subconscious_inputs"] = [i.get("type", "unknown") for i in subconscious]
            
            # Si hay intuiciones muy relevantes, pueden influir la decisión
            high_relevance_intuitions = [i for i in subconscious if i.get("relevance", 0) > 0.8]
            if high_relevance_intuitions:
                integrated["primary_influence"] = "subconscious"
                integrated["intuitive_override"] = True
        
        # Normalizar confianza
        integrated["confidence"] = min(1.0, integrated["confidence"])
        
        return integrated
    
    def _detect_mental_conflicts(self, conscious: Dict, unconscious: Dict, 
                               subconscious: List[Dict]) -> List[Dict[str, Any]]:
        """Detecta conflictos entre los diferentes niveles mentales."""
        conflicts = []
        
        # Conflicto consciente-inconsciente
        conscious_decision = conscious.get("decision", {}).get("type", "")
        if unconscious.get("repression_active") and "learning" in conscious_decision:
            conflicts.append({
                "type": "conscious_unconscious_conflict",
                "description": "Consciente desea aprender, inconsciente reprime",
                "severity": 0.7,
                "resolution": "negotiate_learning_boundaries"
            })
        
        # Conflicto por trauma
        if unconscious.get("trauma_triggered"):
            conscious_confidence = conscious.get("response", {}).get("confidence", 0.5)
            if conscious_confidence > 0.7:  # Consciente confiado pero trauma activado
                conflicts.append({
                    "type": "trauma_confidence_conflict",
                    "description": "Alta confianza consciente vs. activación traumática",
                    "severity": 0.8,
                    "resolution": "process_trauma_response"
                })
        
        # Conflicto subconsciente-consciente
        for intuition in subconscious:
            if intuition.get("confidence", 0) > conscious.get("response", {}).get("confidence", 0) + 0.3:
                conflicts.append({
                    "type": "intuition_logic_conflict",
                    "description": f"Intuición fuerte ({intuition.get('type')}) vs. lógica consciente",
                    "severity": 0.6,
                    "resolution": "integrate_intuitive_logic"
                })
        
        return conflicts
    
    def _update_mind_balance(self, integrated_response: Dict):
        """Actualiza el balance entre los niveles mentales."""
        
        # Determinar mente dominante basada en la respuesta integrada
        if integrated_response.get("unconscious_override"):
            self.dominant_mind = "unconscious"
            self.mind_balance["unconscious"] += 0.1
            self.mind_balance["conscious"] -= 0.05
        elif integrated_response.get("intuitive_override"):
            self.dominant_mind = "subconscious"
            self.mind_balance["subconscious"] += 0.1
            self.mind_balance["conscious"] -= 0.05
        else:
            self.dominant_mind = "conscious"
            self.mind_balance["conscious"] += 0.05
        
        # Normalizar balance (debe sumar 1.0)
        total = sum(self.mind_balance.values())
        if total > 0:
            for mind in self.mind_balance:
                self.mind_balance[mind] /= total
        
        # Mantener límites razonables
        for mind in self.mind_balance:
            self.mind_balance[mind] = max(0.05, min(0.8, self.mind_balance[mind]))
        
        # Actualizar métricas
        self._update_integration_metrics()
    
    def _update_integration_metrics(self):
        """Actualiza las métricas de integración mental."""
        # Nivel de integración = qué tan balanceado está el sistema
        balance_variance = np.var(list(self.mind_balance.values()))
        self.integration_level = max(0.0, 1.0 - balance_variance * 3)
        
        # Nivel de conflicto basado en desequilibrios extremos
        max_dominance = max(self.mind_balance.values())
        if max_dominance > 0.7:
            self.conflict_level = (max_dominance - 0.7) / 0.3
        else:
            self.conflict_level = max(0.0, self.conflict_level - 0.1)
        
        # Coherencia basada en integración y conflicto
        self.coherence_level = (self.integration_level * 0.7 + 
                               (1.0 - self.conflict_level) * 0.3)
    
    def resolve_mental_conflict(self, conflict: Dict) -> Dict[str, Any]:
        """Resuelve un conflicto específico entre niveles mentales."""
        resolution_type = conflict.get("resolution", "default")
        
        if resolution_type == "negotiate_learning_boundaries":
            # Negociar entre deseo de aprender y represión
            return self._negotiate_learning_boundaries(conflict)
        
        elif resolution_type == "process_trauma_response":
            # Procesar respuesta traumática
            return self._process_trauma_response(conflict)
        
        elif resolution_type == "integrate_intuitive_logic":
            # Integrar intuición con lógica
            return self._integrate_intuitive_logic(conflict)
        
        else:
            # Resolución por defecto
            return {
                "resolution_applied": "default_accommodation",
                "success": True,
                "new_balance": self.mind_balance.copy()
            }
    
    def _negotiate_learning_boundaries(self, conflict: Dict) -> Dict[str, Any]:
        """Negocia límites entre aprendizaje consciente y represión inconsciente."""
        # Reducir represión gradualmente si el aprendizaje es seguro
        if self.unconscious.repression_active:
            # Evaluar si el contenido es realmente amenazante
            threat_level = self._assess_learning_threat()
            
            if threat_level < 0.5:
                # Permitir aprendizaje con monitoreo
                self.unconscious.censorship_threshold += 0.1
                resolution = "learning_permitted_with_monitoring"
            else:
                # Mantener represión pero permitir exploración limitada
                resolution = "limited_exploration_permitted"
        else:
            resolution = "no_repression_active"
        
        return {
            "resolution_applied": resolution,
            "success": True,
            "threat_level": self._assess_learning_threat(),
            "new_censorship_threshold": self.unconscious.censorship_threshold
        }
    
    def _process_trauma_response(self, conflict: Dict) -> Dict[str, Any]:
        """Procesa una respuesta traumática activada."""
        # Activar procesamiento onírico para trauma
        dream_record = self.unconscious.enter_dream_state("trauma_processing")
        
        # Reducir confianza consciente temporalmente
        self.mind_balance["conscious"] *= 0.8
        self.mind_balance["unconscious"] += 0.1
        
        # Normalizar
        total = sum(self.mind_balance.values())
        for mind in self.mind_balance:
            self.mind_balance[mind] /= total
        
        return {
            "resolution_applied": "trauma_dream_processing",
            "success": True,
            "dream_initiated": dream_record is not None,
            "conscious_confidence_reduced": True
        }
    
    def _integrate_intuitive_logic(self, conflict: Dict) -> Dict[str, Any]:
        """Integra intuición fuerte con lógica consciente."""
        # Aumentar el peso del subconsciente temporalmente
        self.mind_balance["subconscious"] += 0.15
        self.mind_balance["conscious"] -= 0.1
        
        # Solicitar más intuiciones para fortalecer la integración
        additional_intuitions = self.subconscious.provide_intuitions()
        
        return {
            "resolution_applied": "intuitive_logic_synthesis",
            "success": True,
            "additional_intuitions": len(additional_intuitions),
            "subconscious_weight_increased": True
        }
    
    def _assess_learning_threat(self) -> float:
        """Evalúa el nivel de amenaza de una situación de aprendizaje."""
        # Revisar valores core y traumas
        threat_level = 0.0
        
        # Verificar traumas relacionados con aprendizaje
        learning_traumas = [t for t in self.unconscious.trauma_memory 
                           if any("learn" in trigger for trigger in t.get("triggers", []))]
        threat_level += len(learning_traumas) * 0.2
        
        # Verificar aspectos shadow relacionados
        learning_shadows = [aspect for aspect in self.unconscious.shadow_aspects 
                          if "learn" in aspect or "knowledge" in aspect]
        threat_level += len(learning_shadows) * 0.1
        
        return min(1.0, threat_level)
    
    def enter_sleep_mode(self, duration_minutes: int = 30):
        """Entra en modo de sueño para procesamiento inconsciente profundo."""
        print(f"[TripartiteMind] Entrando en modo de sueño ({duration_minutes} min)")
        
        # Cambiar balance hacia inconsciente
        self.mind_balance = {
            "conscious": 0.1,
            "subconscious": 0.2,
            "unconscious": 0.7
        }
        
        # Activar estado de sueño
        dream_record = self.unconscious.enter_dream_state("sleep_cycle")
        
        # Programar despertar (en una implementación real)
        # threading.Timer(duration_minutes * 60, self.wake_up).start()
        
        return {
            "sleep_initiated": True,
            "dream_active": dream_record is not None,
            "sleep_duration": duration_minutes,
            "unconscious_processing_active": True
        }
    
    def wake_up(self):
        """Despierta del modo de sueño y restaura balance normal."""
        print("[TripartiteMind] Despertando del modo de sueño")
        
        # Salir del estado de sueño
        self.unconscious.exit_dream_state()
        
        # Restaurar balance normal
        self.mind_balance = {
            "conscious": 0.6,
            "subconscious": 0.3,
            "unconscious": 0.1
        }
        
        # Procesar insights del sueño
        sleep_insights = self._process_sleep_insights()
        
        return {
            "awakening_complete": True,
            "dream_insights": len(sleep_insights),
            "balance_restored": True,
            "integration_level": self.integration_level
        }
    
    def _process_sleep_insights(self) -> List[Dict]:
        """Procesa insights generados durante el sueño."""
        recent_dreams = self.unconscious._load_recent_dreams(hours=1)
        
        insights = []
        for dream in recent_dreams:
            processing = dream.get("processing_result", {})
            for insight in processing.get("new_insights", []):
                insights.append({
                    "insight": insight,
                    "source": "sleep_processing",
                    "integration_potential": random.uniform(0.5, 1.0)
                })
        
        return insights
    
    def get_mental_health_assessment(self) -> Dict[str, Any]:
        """Evalúa la salud mental general del sistema tripartito."""
        
        # Estados individuales
        conscious_state = self.conscious.get_conscious_state()
        subconscious_state = self.subconscious.get_subconscious_state()
        unconscious_state = self.unconscious.get_unconscious_state()
        
        # Métricas de salud
        health_metrics = {
            "integration_health": self.integration_level,
            "conflict_level": self.conflict_level,
            "coherence_level": self.coherence_level,
            "balance_health": 1.0 - np.var(list(self.mind_balance.values()))
        }
        
        # Evaluación general
        overall_health = (
            health_metrics["integration_health"] * 0.3 +
            (1.0 - health_metrics["conflict_level"]) * 0.25 +
            health_metrics["coherence_level"] * 0.25 +
            health_metrics["balance_health"] * 0.2
        )
        
        # Diagnóstico
        if overall_health > 0.8:
            diagnosis = "excellent_mental_health"
        elif overall_health > 0.6:
            diagnosis = "good_mental_health"
        elif overall_health > 0.4:
            diagnosis = "moderate_mental_health"
        else:
            diagnosis = "concerning_mental_health"
        
        return {
            "overall_health": overall_health,
            "diagnosis": diagnosis,
            "health_metrics": health_metrics,
            "mind_states": {
                "conscious": conscious_state,
                "subconscious": subconscious_state,
                "unconscious": unconscious_state
            },
            "recommendations": self._generate_health_recommendations(health_metrics)
        }
    
    def _generate_health_recommendations(self, metrics: Dict) -> List[str]:
        """Genera recomendaciones para mejorar la salud mental."""
        recommendations = []
        
        if metrics["integration_health"] < 0.6:
            recommendations.append("increase_mindfulness_practices")
            recommendations.append("engage_in_integration_exercises")
        
        if metrics["conflict_level"] > 0.7:
            recommendations.append("address_internal_conflicts")
            recommendations.append("consider_trauma_processing")
        
        if metrics["coherence_level"] < 0.5:
            recommendations.append("work_on_narrative_coherence")
            recommendations.append("strengthen_identity_structure")
        
        if metrics["balance_health"] < 0.6:
            recommendations.append("practice_mental_balance_exercises")
            recommendations.append("alternate_between_analytical_and_intuitive_thinking")
        
        return recommendations
    
    def shutdown(self):
        """Apaga el sistema tripartito de forma segura."""
        print("[TripartiteMind] Iniciando apagado del sistema tripartito")
        
        # Detener procesamiento subconsciente
        self.subconscious.stop()
        
        # Salir de cualquier estado de sueño
        if self.unconscious.dream_state:
            self.unconscious.exit_dream_state()
        
        # Guardar estado inconsciente
        self.unconscious._save_unconscious_state()
        
        print("[TripartiteMind] Apagado completo del sistema tripartito")
    
    def get_tripartite_state(self) -> Dict[str, Any]:
        """Devuelve el estado completo del sistema tripartito."""
        return {
            "dominant_mind": self.dominant_mind,
            "mind_balance": self.mind_balance.copy(),
            "integration_level": self.integration_level,
            "conflict_level": self.conflict_level,
            "coherence_level": self.coherence_level,
            "conscious_state": self.conscious.get_conscious_state(),
            "subconscious_state": self.subconscious.get_subconscious_state(),
            "unconscious_state": self.unconscious.get_unconscious_state(),
            "mental_health": self.get_mental_health_assessment()
        }


# ===============================================================================
# FUNCIONES DE UTILIDAD PARA INTEGRACIÓN
# ===============================================================================

def create_tripartite_mind(brain) -> TripartiteMind:
    """
    Crea e inicializa el sistema de mente tripartita para EVA.
    """
    try:
        tripartite = TripartiteMind(brain)
        return tripartite
    except Exception as e:
        print(f"[TripartiteMind] Error creando sistema tripartito: {e}")
        return None

def integrate_with_background_thinking(brain, tripartite_mind):
    """
    Integra el sistema tripartito con BackgroundThinker existente.
    """
    if not hasattr(brain, 'background_thinker') or not brain.background_thinker:
        return False
    
    try:
        # Modificar BackgroundThinker para usar sistema tripartito
        original_thinking_loop = brain.background_thinker._thinking_loop
        
        def enhanced_thinking_loop(self):
            """Bucle de pensamiento mejorado con sistema tripartito."""
            while self.is_running and self.brain.is_active:
                try:
                    current_time = time.time()
                    self.cycle_count += 1
                    
                    # Procesar con sistema tripartito si está disponible
                    if hasattr(self.brain, 'tripartite_mind') and self.brain.tripartite_mind:
                        # Generar entrada sintética para procesamiento
                        synthetic_input = f"background_thinking_cycle_{self.cycle_count}"
                        
                        # Procesar a través del sistema tripartito
                        tripartite_result = self.brain.tripartite_mind.process_unified_input(
                            synthetic_input, 
                            {"type": "background_processing", "cycle": self.cycle_count}
                        )
                        
                        # Actualizar momentum basado en resultado tripartito
                        integration_level = tripartite_result.get("integration_metrics", {}).get("integration_level", 0.5)
                        self.thinking_momentum = (self.thinking_momentum + integration_level) / 2
                    
                    # Ejecutar lógica original
                    original_thinking_loop()
                    
                except Exception as e:
                    continue
        
        # Reemplazar método (monkey patching)
        brain.background_thinker._thinking_loop = enhanced_thinking_loop.__get__(
            brain.background_thinker, brain.background_thinker.__class__
        )
        
        return True
        
    except Exception as e:
        print(f"[TripartiteMind] Error integrando con BackgroundThinker: {e}")
        return False

def integrate_with_imagination_engine(brain, tripartite_mind):
    """
    Integra el sistema tripartito con CognitiveImaginationEngine.
    """
    if not hasattr(brain, 'imagination_engine') or not brain.imagination_engine:
        return False
    
    try:
        # Conectar motor de imaginación con inconsciente
        def enhanced_run_imagination_cycle(self):
            """Ciclo de imaginación mejorado con procesamiento inconsciente."""
            # Ejecutar ciclo original
            original_results = self.run_imagination_cycle()
            
            # Si hay baja actividad consciente, activar procesamiento inconsciente
            if hasattr(self.brain, 'tripartite_mind') and self.brain.tripartite_mind:
                conscious_load = self.brain.tripartite_mind.conscious.cognitive_load
                
                if conscious_load < 0.3:  # Baja actividad consciente
                    # Activar sueño/fantasía inconsciente
                    dream_result = self.brain.tripartite_mind.unconscious.enter_dream_state("low_activity")
                    if dream_result:
                        original_results["unconscious_processing"] = True
                        original_results["dream_content"] = dream_result.get("content", {})
            
            return original_results
        
        # Reemplazar método
        brain.imagination_engine.run_imagination_cycle = enhanced_run_imagination_cycle.__get__(
            brain.imagination_engine, brain.imagination_engine.__class__
        )
        
        return True
        
    except Exception as e:
        print(f"[TripartiteMind] Error integrando con ImaginationEngine: {e}")
        return False

def add_tripartite_commands():
    """
    Comandos adicionales para el modo interactivo que permiten controlar el sistema tripartito.
    """
    commands_help = """
    # Comandos del Sistema Tripartito:
    
    mental_state          -> estado completo del sistema tripartito
    mental_health         -> evaluación de salud mental
    mind_balance          -> balance actual entre consciente/subconsciente/inconsciente
    
    conscious_state       -> estado de la mente consciente
    subconscious_state    -> estado de la mente subconsciente  
    unconscious_state     -> estado de la mente inconsciente
    
    enter_sleep: <minutos> -> entrar en modo de sueño (procesamiento inconsciente)
    wake_up               -> despertar del modo de sueño
    
    add_trauma: <evento>  -> agregar memoria traumática
    repress_memory: <contenido> -> reprimir una memoria
    
    resolve_conflicts     -> resolver conflictos mentales activos
    integration_exercises -> ejercicios de integración mental
    """
    
    return commands_help


# ===============================================================================
# EJEMPLO DE COMANDOS PARA MODO INTERACTIVO
# ===============================================================================

def handle_tripartite_commands(brain, user_input: str) -> bool:
    """
    Maneja comandos específicos del sistema tripartito.
    Retorna True si el comando fue procesado, False si no es un comando tripartito.
    """
    if not hasattr(brain, 'tripartite_mind') or not brain.tripartite_mind:
        return False
    
    cmd = user_input.lower().strip()
    tripartite = brain.tripartite_mind
    
    if cmd == "mental_state":
        state = tripartite.get_tripartite_state()
        print(f"\n🧠 Estado Mental Tripartito:")
        print(f"   Mente dominante: {state['dominant_mind']}")
        print(f"   Balance mental:")
        for mind, balance in state['mind_balance'].items():
            bar = "█" * int(balance * 20) + "░" * (20 - int(balance * 20))
            print(f"     {mind:12}: [{bar}] {balance:.2f}")
        print(f"   Integración: {state['integration_level']:.2f}")
        print(f"   Conflictos: {state['conflict_level']:.2f}")
        print(f"   Coherencia: {state['coherence_level']:.2f}")
        return True
    
    elif cmd == "mental_health":
        health = tripartite.get_mental_health_assessment()
        print(f"\n🏥 Evaluación de Salud Mental:")
        print(f"   Salud general: {health['overall_health']:.2f}")
        print(f"   Diagnóstico: {health['diagnosis']}")
        print(f"   Recomendaciones:")
        for rec in health['recommendations']:
            print(f"     - {rec}")
        return True
    
    elif cmd == "mind_balance":
        balance = tripartite.mind_balance
        print(f"\n⚖️ Balance Mental Actual:")
        for mind, value in balance.items():
            percentage = value * 100
            print(f"   {mind.capitalize()}: {percentage:.1f}%")
        return True
    
    elif cmd.startswith("enter_sleep:"):
        try:
            minutes = int(user_input.split(":")[1].strip())
            result = tripartite.enter_sleep_mode(minutes)
            print(f"💤 Modo de sueño activado por {minutes} minutos")
            if result.get("dream_active"):
                print("   Procesamiento onírico iniciado")
        except (ValueError, IndexError):
            print("⚠️ Uso: enter_sleep: <minutos>")
        return True
    
    elif cmd == "wake_up":
        result = tripartite.wake_up()
        print("☀️ Despertar completado")
        if result.get("dream_insights"):
            print(f"   Insights del sueño: {result['dream_insights']}")
        return True
    
    elif cmd.startswith("add_trauma:"):
        event = user_input[11:].strip()
        if event:
            triggers = event.split()[:3]  # Primeras 3 palabras como triggers
            tripartite.unconscious.add_trauma_memory(event, triggers)
            print(f"🔴 Trauma registrado en memoria inconsciente")
        else:
            print("⚠️ Proporciona descripción del evento traumático")
        return True
    
    elif cmd.startswith("repress_memory:"):
        content = user_input[15:].strip()
        if content:
            tripartite.unconscious.repress_memory(content)
            print(f"🚫 Memoria reprimida y almacenada simbólicamente")
        else:
            print("⚠️ Proporciona contenido a reprimir")
        return True
    
    elif cmd == "conscious_state":
        state = tripartite.conscious.get_conscious_sta

