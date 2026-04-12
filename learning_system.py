# learning_system.py - Sistema de Aprendizaje Mejorado e Integrado
# Integración completa con TranscendentMemory

import re
from collections import defaultdict, Counter
import os
import json
import threading
import time
from datetime import datetime, timedelta
import hashlib
import numpy as np
from typing import Dict, List, Set, Optional, Tuple, Any

class EnhancedLearningSystem:
    def __init__(self, transcendent_memory=None):
        """
        Inicializa el sistema de aprendizaje léxico mejorado.
        Observa palabras, construye asociaciones con decaimiento y se integra con TranscendentMemory.
        
        Args:
            transcendent_memory: Instancia de TranscendentMemory para integración bidireccional
        """
        # Referencia al sistema de memoria trascendente
        self.transcendent_memory = transcendent_memory
        
        # Datos principales
        self.observations = []  # Registro de entradas procesadas
        self.associations = defaultdict(float)  # Asociaciones con decaimiento
        self.last_used = {}  # Última vez que se usó cada palabra
        self.semantic_clusters = {}  # Clusters semánticos de palabras
        self.concept_evolution = {}  # Evolución de conceptos a lo largo del tiempo
        
        # Nuevas estructuras para integración
        self.contextual_associations = defaultdict(lambda: defaultdict(float))  # Asociaciones por contexto
        self.causal_patterns = {}  # Patrones causales detectados
        self.learning_patterns = {}  # Patrones de aprendizaje identificados
        self.feedback_loop = []  # Retroalimentación del sistema trascendente
        
        # Configuración adaptable
        self.threshold = 2.0  # Umbral para asociaciones fuertes
        self.decay_rate = 0.95  # Tasa de decaimiento diario
        self.adaptation_rate = 0.1  # Velocidad de adaptación de parámetros
        self.semantic_threshold = 0.3  # Umbral para conexiones semánticas
        
        # Métricas de aprendizaje
        self.learning_velocity = 0.0  # Velocidad de aprendizaje actual
        self.pattern_recognition_accuracy = 0.0  # Precisión en reconocimiento de patrones
        self.knowledge_integration_rate = 0.0  # Tasa de integración con memoria trascendente
        
        # Sistema de archivos mejorado
        self.memory_dir = "learning_memory"
        self.associations_file = os.path.join(self.memory_dir, "enhanced_associations.json")
        self.patterns_file = os.path.join(self.memory_dir, "learning_patterns.json")
        self.metrics_file = os.path.join(self.memory_dir, "learning_metrics.json")
        self.evolution_file = os.path.join(self.memory_dir, "concept_evolution.json")
        
        # Threading para procesamiento continuo
        self.continuous_learning = False
        self.learning_thread = None
        self.processing_queue = []
        self.queue_lock = threading.Lock()
        
        # Cargar estado
        self.load_enhanced_state()
        
        # Iniciar integración si hay memoria trascendente
        if self.transcendent_memory:
            self._establish_bidirectional_integration()
        
        print(f"[EnhancedLearningSystem] Sistema mejorado inicializado con {len(self.associations)} asociaciones")

    def observe(self, text: str, context: Dict = None, priority: int = 1) -> Dict:
        """
        Observa un nuevo texto y actualiza las asociaciones con contexto mejorado.
        Integra directamente con TranscendentMemory si está disponible.
        
        Args:
            text: Texto a observar
            context: Contexto adicional (dominio, fuente, etc.)
            priority: Prioridad de procesamiento (1-3)
        
        Returns:
            Dict con métricas de importancia y recomendaciones de almacenamiento
        """
        try:
            # Procesar con decaimiento
            self._decay_old_associations()
            
            # Registrar observación
            observation_entry = {
                "text": text,
                "context": context or {},
                "timestamp": datetime.now().isoformat(),
                "priority": priority
            }
            self.observations.append(observation_entry)
            
            # Mantener solo las últimas 1000 observaciones
            if len(self.observations) > 1000:
                self.observations = self.observations[-1000:]
            
            # Tokenización y análisis mejorado
            words = self._enhanced_tokenize(text)
            semantic_features = self._extract_semantic_features(text, words)
            contextual_domain = self._detect_domain(text, context)
            
            # Actualizar asociaciones con contexto
            now = datetime.now().timestamp()
            base_increment = priority * 0.5  # Incremento basado en prioridad
            
            for word in words:
                # Asociación general
                self.associations[word] += base_increment
                self.last_used[word] = now
                
                # Asociación contextual
                if contextual_domain:
                    self.contextual_associations[contextual_domain][word] += base_increment
            
            # Detectar patrones emergentes
            emerging_patterns = self._detect_emerging_patterns(text, words, context)
            
            # Calcular importancia multi-dimensional
            importance_metrics = self._calculate_enhanced_importance(
                text, words, semantic_features, contextual_domain, emerging_patterns
            )
            
            # Integración con TranscendentMemory
            transcendent_feedback = None
            if self.transcendent_memory:
                transcendent_feedback = self._integrate_with_transcendent_memory(
                    text, context, importance_metrics
                )
            
            # Actualizar métricas de aprendizaje
            self._update_learning_metrics(importance_metrics, transcendent_feedback)
            
            # Construir respuesta
            response = {
                "importance_score": importance_metrics["total_importance"],
                "contextual_domain": contextual_domain,
                "semantic_features": semantic_features,
                "emerging_patterns": emerging_patterns,
                "storage_recommendation": self._generate_storage_recommendation(importance_metrics),
                "transcendent_feedback": transcendent_feedback,
                "learning_velocity": self.learning_velocity,
                "processing_timestamp": datetime.now().isoformat()
            }
            
            # Agregar a cola de procesamiento continuo si está activo
            if self.continuous_learning:
                with self.queue_lock:
                    self.processing_queue.append((text, context, importance_metrics))
            
            # Logging mejorado
            print(f"[EnhancedLearningSystem] Observado: '{text[:50]}...' | "
                  f"Importancia: {importance_metrics['total_importance']:.2f} | "
                  f"Dominio: {contextual_domain}")
            
            return response
            
        except Exception as e:
            print(f"[EnhancedLearningSystem] Error en observe: {e}")
            return {
                "importance_score": 1.0,
                "error": str(e),
                "processing_timestamp": datetime.now().isoformat()
            }

    def _enhanced_tokenize(self, text: str) -> List[str]:
        """Tokenización mejorada con detección de entidades y conceptos."""
        text_lower = text.lower()
        
        # Palabras básicas (3+ caracteres)
        basic_words = re.findall(r'\b\w{3,}\b', text_lower)
        
        # Detectar entidades nombradas simples (mayúsculas)
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Detectar conceptos técnicos (palabras con guiones, puntos)
        technical_terms = re.findall(r'\b\w+[-_.]\w+\b', text_lower)
        
        # Detectar frases importantes (palabras entre comillas)
        quoted_phrases = re.findall(r'"([^"]+)"', text)
        
        # Combinar todos los tokens
        all_tokens = basic_words + [e.lower() for e in entities] + technical_terms
        
        # Agregar frases importantes como tokens únicos
        for phrase in quoted_phrases:
            phrase_token = phrase.lower().replace(' ', '_')
            all_tokens.append(phrase_token)
        
        return list(set(all_tokens))  # Eliminar duplicados

    def _extract_semantic_features(self, text: str, words: List[str]) -> Dict:
        """Extrae características semánticas del texto."""
        features = {
            "word_count": len(words),
            "unique_words": len(set(words)),
            "complexity_score": 0.0,
            "emotional_indicators": [],
            "temporal_references": [],
            "causal_indicators": [],
            "certainty_level": 0.5
        }
        
        text_lower = text.lower()
        
        # Puntuación de complejidad
        long_words = [w for w in words if len(w) >= 7]
        features["complexity_score"] = len(long_words) / max(len(words), 1)
        
        # Indicadores emocionales
        emotion_words = {
            "positive": ["feliz", "alegre", "bueno", "excelente", "genial", "amor", "paz"],
            "negative": ["triste", "malo", "terrible", "odio", "miedo", "dolor", "problema"],
            "neutral": ["normal", "regular", "común", "típico"]
        }
        
        for category, words_list in emotion_words.items():
            found = [word for word in words_list if word in text_lower]
            if found:
                features["emotional_indicators"].append({
                    "category": category,
                    "words": found,
                    "intensity": len(found)
                })
        
        # Referencias temporales
        temporal_patterns = ["ayer", "hoy", "mañana", "antes", "después", "ahora", "luego"]
        features["temporal_references"] = [t for t in temporal_patterns if t in text_lower]
        
        # Indicadores causales
        causal_patterns = ["porque", "debido a", "causa", "resultado", "consecuencia", "por tanto"]
        features["causal_indicators"] = [c for c in causal_patterns if c in text_lower]
        
        # Nivel de certeza
        certainty_high = ["seguro", "cierto", "definitivo", "obvio", "claro"]
        certainty_low = ["quizás", "tal vez", "posible", "probable", "creo"]
        
        if any(word in text_lower for word in certainty_high):
            features["certainty_level"] = 0.8
        elif any(word in text_lower for word in certainty_low):
            features["certainty_level"] = 0.3
        
        return features

    def _detect_domain(self, text: str, context: Dict = None) -> str:
        """Detecta el dominio contextual del texto."""
        if context and context.get("domain"):
            return context["domain"]
        
        text_lower = text.lower()
        
        # Diccionario de dominios con palabras clave
        domain_keywords = {
            "technical": ["sistema", "función", "algoritmo", "código", "programa", "datos", "proceso"],
            "emotional": ["sentir", "emoción", "corazón", "alma", "amor", "miedo", "alegría"],
            "learning": ["aprender", "conocimiento", "estudiar", "entender", "descubrir", "información"],
            "social": ["personas", "gente", "comunicar", "relación", "social", "interactuar"],
            "philosophical": ["ser", "existir", "realidad", "verdad", "significado", "propósito"],
            "creative": ["crear", "arte", "imaginación", "creatividad", "inspiración", "diseño"],
            "self_reflection": ["reflexionar", "pensar", "considerar", "analizar", "introspección"],
            "problem_solving": ["problema", "solución", "resolver", "método", "estrategia"],
            "memory": ["recordar", "memoria", "olvidar", "almacenar", "guardar", "recuperar"],
            "identity": ["identidad", "quien", "soy", "personalidad", "carácter", "EVA"]
        }
        
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        else:
            return "general"

    def _detect_emerging_patterns(self, text: str, words: List[str], context: Dict = None) -> List[Dict]:
        """Detecta patrones emergentes en el texto."""
        patterns = []
        
        # Patrón de secuencia temporal
        if any(temp in text.lower() for temp in ["antes", "después", "luego", "entonces"]):
            patterns.append({
                "type": "temporal_sequence",
                "confidence": 0.7,
                "description": "Secuencia temporal detectada"
            })
        
        # Patrón causa-efecto
        if any(causal in text.lower() for causal in ["porque", "causa", "resultado", "debido"]):
            patterns.append({
                "type": "causal_relationship",
                "confidence": 0.8,
                "description": "Relación causal identificada"
            })
        
        # Patrón de comparación
        if any(comp in text.lower() for comp in ["mejor", "peor", "igual", "diferente", "similar"]):
            patterns.append({
                "type": "comparison",
                "confidence": 0.6,
                "description": "Patrón comparativo detectado"
            })
        
        # Patrón de categorización
        categories = ["tipo", "clase", "categoría", "grupo", "conjunto"]
        if any(cat in text.lower() for cat in categories):
            patterns.append({
                "type": "categorization",
                "confidence": 0.5,
                "description": "Intento de categorización"
            })
        
        # Patrón de aprendizaje
        if any(learn in text.lower() for learn in ["aprender", "entender", "comprender", "descubrir"]):
            patterns.append({
                "type": "learning_intent",
                "confidence": 0.9,
                "description": "Intención de aprendizaje detectada"
            })
        
        return patterns

    def _calculate_enhanced_importance(self, text: str, words: List[str], 
                                     semantic_features: Dict, domain: str, 
                                     patterns: List[Dict]) -> Dict:
        """Calcula importancia multi-dimensional mejorada."""
        metrics = {
            "length_factor": 0.0,
            "complexity_factor": 0.0,
            "novelty_factor": 0.0,
            "emotional_factor": 0.0,
            "pattern_factor": 0.0,
            "domain_factor": 0.0,
            "familiarity_factor": 0.0,
            "temporal_factor": 0.0,
            "total_importance": 0.0
        }
        
        # Factor de longitud (normalizado)
        word_count = len(words)
        metrics["length_factor"] = min(word_count / 20.0, 1.0)  # Máximo en 20 palabras
        
        # Factor de complejidad
        metrics["complexity_factor"] = semantic_features["complexity_score"]
        
        # Factor de novedad (palabras no vistas frecuentemente)
        novel_words = [w for w in words if self.associations[w] < 2.0]
        metrics["novelty_factor"] = len(novel_words) / max(len(words), 1)
        
        # Factor emocional
        emotion_intensity = sum(ei["intensity"] for ei in semantic_features["emotional_indicators"])
        metrics["emotional_factor"] = min(emotion_intensity / 3.0, 1.0)
        
        # Factor de patrones
        pattern_confidence = sum(p["confidence"] for p in patterns) / max(len(patterns), 1)
        metrics["pattern_factor"] = pattern_confidence if patterns else 0.0
        
        # Factor de dominio (algunos dominios son más importantes)
        domain_weights = {
            "identity": 1.0,
            "philosophical": 0.9,
            "learning": 0.8,
            "self_reflection": 0.8,
            "emotional": 0.7,
            "technical": 0.6,
            "social": 0.5,
            "general": 0.3
        }
        metrics["domain_factor"] = domain_weights.get(domain, 0.4)
        
        # Factor de familiaridad (balance entre conocido y nuevo)
        known_words = sum(1 for w in words if self.associations[w] > 1.0)
        familiarity_ratio = known_words / max(len(words), 1)
        # Máxima importancia en ratio 0.3-0.7 (ni muy nuevo ni muy conocido)
        metrics["familiarity_factor"] = 1.0 - abs(familiarity_ratio - 0.5) * 2
        
        # Factor temporal (presencia de referencias temporales)
        metrics["temporal_factor"] = min(len(semantic_features["temporal_references"]) / 2.0, 1.0)
        
        # Cálculo final con pesos
        weights = {
            "length_factor": 0.1,
            "complexity_factor": 0.15,
            "novelty_factor": 0.2,
            "emotional_factor": 0.15,
            "pattern_factor": 0.2,
            "domain_factor": 0.1,
            "familiarity_factor": 0.05,
            "temporal_factor": 0.05
        }
        
        total = sum(metrics[factor] * weight for factor, weight in weights.items())
        metrics["total_importance"] = min(max(total, 0.1), 3.0)  # Entre 0.1 y 3.0
        
        return metrics

    def _generate_storage_recommendation(self, importance_metrics: Dict) -> Dict:
        """Genera recomendación de almacenamiento basada en métricas."""
        importance = importance_metrics["total_importance"]
        
        if importance >= 2.5:
            recommendation = {
                "layer": "consolidated",
                "priority": "high",
                "create_variants": True,
                "establish_connections": True,
                "reason": "Muy alta importancia - conocimiento crítico"
            }
        elif importance >= 1.5:
            recommendation = {
                "layer": "associative",
                "priority": "medium",
                "create_variants": False,
                "establish_connections": True,
                "reason": "Importancia media - conocimiento relevante"
            }
        else:
            recommendation = {
                "layer": "working",
                "priority": "low",
                "create_variants": False,
                "establish_connections": False,
                "reason": "Baja importancia - información temporal"
            }
        
        return recommendation

    def _integrate_with_transcendent_memory(self, text: str, context: Dict, 
                                          importance_metrics: Dict) -> Dict:
        """Integración bidireccional con TranscendentMemory."""
        if not self.transcendent_memory:
            return None
        
        try:
            feedback = {}
            
            # Almacenar en memoria trascendente con contexto enriquecido
            enhanced_context = context.copy() if context else {}
            enhanced_context.update({
                "learning_system_metrics": importance_metrics,
                "domain": importance_metrics.get("contextual_domain", "general"),
                "importance_override": importance_metrics["total_importance"] / 3.0,
                "source": "enhanced_learning_system"
            })
            
            # Almacenar
            node_id = self.transcendent_memory.store_transcendent(
                content=text,
                context=enhanced_context
            )
            
            feedback["stored_node_id"] = node_id
            feedback["storage_successful"] = node_id is not None
            
            # Obtener feedback de la memoria trascendente
            if node_id:
                # Buscar nodos relacionados
                related_nodes = self.transcendent_memory.retrieve_by_resonance(
                    text, context=enhanced_context, limit=5
                )
                
                feedback["related_nodes_count"] = len(related_nodes)
                feedback["semantic_connections"] = len(related_nodes)
                
                # Actualizar patrones causales basándose en nodos relacionados
                self._update_causal_patterns(text, related_nodes)
                
                # Obtener insights de la memoria trascendente
                if hasattr(self.transcendent_memory, 'get_transcendent_insights'):
                    insights = self.transcendent_memory.get_transcendent_insights()
                    feedback["transcendent_insights"] = insights
                    
                    # Adaptar parámetros basándose en insights
                    self._adapt_parameters_from_insights(insights)
            
            # Registrar feedback para análisis futuro
            self.feedback_loop.append({
                "timestamp": datetime.now().isoformat(),
                "text": text[:100],  # Solo los primeros 100 caracteres
                "importance": importance_metrics["total_importance"],
                "feedback": feedback
            })
            
            # Mantener solo los últimos 100 feedbacks
            if len(self.feedback_loop) > 100:
                self.feedback_loop = self.feedback_loop[-100:]
            
            return feedback
            
        except Exception as e:
            print(f"[EnhancedLearningSystem] Error en integración con TranscendentMemory: {e}")
            return {"error": str(e), "storage_successful": False}

    def _update_causal_patterns(self, text: str, related_nodes: List) -> None:
        """Actualiza patrones causales basándose en nodos relacionados."""
        if not related_nodes:
            return
        
        text_words = set(self._enhanced_tokenize(text))
        
        for node in related_nodes:
            if hasattr(node, 'content'):
                node_words = set(self._enhanced_tokenize(node.content))
                common_words = text_words & node_words
                
                if len(common_words) >= 2:  # Suficiente solapamiento
                    pattern_key = "_".join(sorted(list(common_words)[:3]))  # Máximo 3 palabras
                    
                    if pattern_key not in self.causal_patterns:
                        self.causal_patterns[pattern_key] = {
                            "frequency": 0,
                            "contexts": [],
                            "strength": 0.0
                        }
                    
                    self.causal_patterns[pattern_key]["frequency"] += 1
                    self.causal_patterns[pattern_key]["strength"] = min(
                        self.causal_patterns[pattern_key]["strength"] + 0.1, 1.0
                    )

    def _adapt_parameters_from_insights(self, insights: Dict) -> None:
        """Adapta parámetros del sistema basándose en insights de TranscendentMemory."""
        if not insights:
            return
        
        # Adaptar threshold basándose en salud de memoria
        memory_health = insights.get("memory_health", 0.5)
        if memory_health > 0.8:
            # Memoria saludable - podemos ser más selectivos
            self.threshold = min(self.threshold + 0.1, 3.0)
        elif memory_health < 0.4:
            # Memoria con problemas - ser menos restrictivos
            self.threshold = max(self.threshold - 0.1, 1.0)
        
        # Adaptar tasa de decaimiento basándose en velocidad de aprendizaje
        learning_velocity = insights.get("learning_velocity", 0.0)
        if learning_velocity > 5.0:  # Aprendizaje muy rápido
            self.decay_rate = min(self.decay_rate + 0.01, 0.99)  # Decaimiento más lento
        elif learning_velocity < 1.0:  # Aprendizaje lento
            self.decay_rate = max(self.decay_rate - 0.01, 0.90)  # Decaimiento más rápido
        
        # Adaptar umbral semántico basándose en diversidad del conocimiento
        knowledge_diversity = insights.get("knowledge_diversity", 0.5)
        if knowledge_diversity > 0.8:
            self.semantic_threshold = min(self.semantic_threshold + 0.05, 0.5)
        elif knowledge_diversity < 0.3:
            self.semantic_threshold = max(self.semantic_threshold - 0.05, 0.1)

    def _update_learning_metrics(self, importance_metrics: Dict, transcendent_feedback: Dict) -> None:
        """Actualiza métricas de aprendizaje del sistema."""
        # Velocidad de aprendizaje basada en observaciones recientes
        recent_observations = [
            obs for obs in self.observations 
            if (datetime.now() - datetime.fromisoformat(obs["timestamp"])).days <= 1
        ]
        self.learning_velocity = len(recent_observations)
        
        # Precisión en reconocimiento de patrones
        if transcendent_feedback and transcendent_feedback.get("semantic_connections", 0) > 0:
            # Si encontró conexiones semánticas, nuestro análisis fue bueno
            self.pattern_recognition_accuracy = min(self.pattern_recognition_accuracy + 0.05, 1.0)
        else:
            # Si no encontró conexiones, quizás nuestro análisis fue impreciso
            self.pattern_recognition_accuracy = max(self.pattern_recognition_accuracy - 0.02, 0.0)
        
        # Tasa de integración con memoria trascendente
        successful_integrations = sum(
            1 for feedback in self.feedback_loop[-10:] 
            if feedback["feedback"].get("storage_successful", False)
        )
        self.knowledge_integration_rate = successful_integrations / min(len(self.feedback_loop), 10)

    def start_continuous_learning(self):
        """Inicia el procesamiento continuo en hilo separado."""
        if not self.continuous_learning:
            self.continuous_learning = True
            self.learning_thread = threading.Thread(target=self._continuous_learning_loop, daemon=True)
            self.learning_thread.start()
            print("[EnhancedLearningSystem] Aprendizaje continuo iniciado")

    def stop_continuous_learning(self):
        """Detiene el procesamiento continuo."""
        self.continuous_learning = False
        if self.learning_thread:
            self.learning_thread.join(timeout=5)
        print("[EnhancedLearningSystem] Aprendizaje continuo detenido")

    def _continuous_learning_loop(self):
        """Bucle de procesamiento continuo."""
        while self.continuous_learning:
            try:
                # Procesar cola de elementos pendientes
                with self.queue_lock:
                    if self.processing_queue:
                        text, context, importance_metrics = self.processing_queue.pop(0)
                        
                        # Procesamiento adicional en background
                        self._background_processing(text, context, importance_metrics)
                
                # Mantenimiento periódico cada minuto
                time.sleep(60)
                if self.continuous_learning:
                    self._periodic_maintenance()
                    
            except Exception as e:
                print(f"[EnhancedLearningSystem] Error en bucle continuo: {e}")

    def _background_processing(self, text: str, context: Dict, importance_metrics: Dict) -> None:
        """Procesamiento adicional en background."""
        # Análisis de clustering semántico
        self._update_semantic_clusters(text, importance_metrics)
        
        # Análisis de evolución conceptual
        self._track_concept_evolution(text, context, importance_metrics)
        
        # Optimización de asociaciones
        self._optimize_associations()

    def _update_semantic_clusters(self, text: str, importance_metrics: Dict) -> None:
        """Actualiza clusters semánticos basándose en nuevo texto."""
        words = self._enhanced_tokenize(text)
        domain = importance_metrics.get("contextual_domain", "general")
        
        if domain not in self.semantic_clusters:
            self.semantic_clusters[domain] = {
                "words": Counter(),
                "centroid": None,
                "coherence": 0.0
            }
        
        # Actualizar contador de palabras del cluster
        for word in words:
            self.semantic_clusters[domain]["words"][word] += 1
        
        # Recalcular coherencia del cluster
        self._recalculate_cluster_coherence(domain)

    def _recalculate_cluster_coherence(self, domain: str) -> None:
        """Recalcula la coherencia de un cluster semántico."""
        cluster = self.semantic_clusters[domain]
        words = list(cluster["words"].keys())
        
        if len(words) < 2:
            cluster["coherence"] = 1.0
            return
        
        # Calcular coherencia basada en co-ocurrencia
        coherence_sum = 0.0
        comparisons = 0
        
        for i, word1 in enumerate(words):
            for word2 in words[i+1:]:
                # Coherencia basada en asociaciones contextuales
                if domain in self.contextual_associations:
                    assoc1 = self.contextual_associations[domain][word1]
                    assoc2 = self.contextual_associations[domain][word2]
                    coherence_sum += min(assoc1, assoc2) / max(assoc1, assoc2, 1.0)
                    comparisons += 1
        
        cluster["coherence"] = coherence_sum / max(comparisons, 1)

    def _track_concept_evolution(self, text: str, context: Dict, importance_metrics: Dict) -> None:
        """Rastrea la evolución de conceptos a lo largo del tiempo."""
        domain = importance_metrics.get("contextual_domain", "general")
        words = self._enhanced_tokenize(text)
        
        timestamp = datetime.now().isoformat()
        
        # Crear entrada de evolución
        evolution_entry = {
            "timestamp": timestamp,
            "domain": domain,
            "importance": importance_metrics["total_importance"],
            "word_count": len(words),
            "complexity": importance_metrics.get("complexity_factor", 0.0),
            "novelty": importance_metrics.get("novelty_factor", 0.0)
        }
        
        if domain not in self.concept_evolution:
            self.concept_evolution[domain] = []
        
        self.concept_evolution[domain].append(evolution_entry)
        
        # Mantener solo las últimas 100 entradas por dominio
        if len(self.concept_evolution[domain]) > 100:
            self.concept_evolution[domain] = self.concept_evolution[domain][-100:]

    def _optimize_associations(self) -> None:
        """Optimiza las asociaciones eliminando ruido y fortaleciendo patrones."""
        # Eliminar asociaciones muy débiles
        weak_associations = [
            word for word, strength in self.associations.items() 
            if strength < 0.1
        ]
        
        for word in weak_associations:
            del self.associations[word]
            self.last_used.pop(word, None)
        
        # Fortalecer asociaciones que aparecen en múltiples contextos
        for word in list(self.associations.keys()):
            context_count = sum(
                1 for domain_assocs in self.contextual_associations.values()
                if word in domain_assocs and domain_assocs[word] > 0.5
            )
            
            if context_count >= 3:  # Aparece en 3+ contextos
                self.associations[word] *= 1.1  # Bonus del 10%

    def _periodic_maintenance(self) -> None:
        """Mantenimiento periódico del sistema."""
        # Guardar estado cada cierto tiempo
        self.save_enhanced_state()
        
        # Limpiar observaciones muy antiguas
        cutoff_date = datetime.now() - timedelta(days=30)
        self.observations = [
            obs for obs in self.observations
            if datetime.fromisoformat(obs["timestamp"]) > cutoff_date
        ]
        
        # Optimizar clusters semánticos
        self._optimize_semantic_clusters()
        
        # Sincronizar con TranscendentMemory si está disponible
        if self.transcendent_memory:
            self._synchronize_with_transcendent_memory()

    def _optimize_semantic_clusters(self) -> None:
        """Optimiza la estructura de clusters semánticos."""
        clusters_to_remove = []
        
        for domain, cluster in self.semantic_clusters.items():
            # Eliminar clusters con muy pocas palabras o baja coherencia
            if len(cluster["words"]) < 3 or cluster["coherence"] < 0.3:
                clusters_to_remove.append(domain)
            else:
                # Mantener solo las palabras más relevantes
                top_words = cluster["words"].most_common(50)
                cluster["words"] = Counter(dict(top_words))
        
        # Eliminar clusters débiles
        for domain in clusters_to_remove:
            del self.semantic_clusters[domain]

    def _synchronize_with_transcendent_memory(self) -> None:
        """Sincroniza conocimiento con TranscendentMemory."""
        try:
            # Obtener asociaciones fuertes del learning system
            strong_associations = self.get_strong_associations()
            
            # Buscar estas asociaciones en TranscendentMemory
            for word in strong_associations:
                related_nodes = self.transcendent_memory.retrieve_by_resonance(
                    word, limit=3
                )
                
                # Fortalecer asociaciones basándose en nodos encontrados
                if related_nodes:
                    bonus = len(related_nodes) * 0.1
                    self.associations[word] += bonus
            
            print(f"[EnhancedLearningSystem] Sincronización completada: {len(strong_associations)} asociaciones procesadas")
            
        except Exception as e:
            print(f"[EnhancedLearningSystem] Error en sincronización: {e}")

    def _establish_bidirectional_integration(self) -> None:
        """Establece integración bidireccional con TranscendentMemory."""
        if not self.transcendent_memory:
            return
        
        try:
            # Establecer referencia mutua
            self.transcendent_memory.learning_system = self
            
            # Sincronizar valores y configuración inicial
            if hasattr(self.transcendent_memory, 'core_values'):
                core_values = self.transcendent_memory.core_values
                
                # Adaptar threshold basándose en valor de aprendizaje
                learning_drive = core_values.get('learning_drive', 0.5)
                self.threshold = 2.0 * (2 - learning_drive)  # Inversa: más drive = menor threshold
                
                # Adaptar decay rate basándose en continuidad de identidad
                identity_continuity = core_values.get('identity_continuity', 0.5)
                self.decay_rate = 0.9 + (identity_continuity * 0.09)  # Más continuidad = menos decay
            
            print("[EnhancedLearningSystem] Integración bidireccional establecida")
            
        except Exception as e:
            print(f"[EnhancedLearningSystem] Error estableciendo integración: {e}")

    def get_learning_analytics(self) -> Dict:
        """Obtiene análisis avanzado del proceso de aprendizaje."""
        analytics = {
            "system_metrics": {
                "total_associations": len(self.associations),
                "strong_associations": len(self.get_strong_associations()),
                "learning_velocity": self.learning_velocity,
                "pattern_recognition_accuracy": self.pattern_recognition_accuracy,
                "knowledge_integration_rate": self.knowledge_integration_rate
            },
            "semantic_analysis": {
                "active_clusters": len(self.semantic_clusters),
                "average_cluster_coherence": self._calculate_average_cluster_coherence(),
                "domain_distribution": self._get_domain_distribution(),
                "cluster_details": {
                    domain: {
                        "word_count": len(cluster["words"]),
                        "coherence": cluster["coherence"],
                        "top_words": cluster["words"].most_common(5)
                    }
                    for domain, cluster in self.semantic_clusters.items()
                }
            },
            "learning_patterns": {
                "causal_patterns_detected": len(self.causal_patterns),
                "concept_evolution_domains": len(self.concept_evolution),
                "pattern_strength_distribution": self._get_pattern_strength_distribution()
            },
            "integration_status": {
                "transcendent_memory_connected": self.transcendent_memory is not None,
                "successful_integrations": len([
                    f for f in self.feedback_loop 
                    if f["feedback"].get("storage_successful", False)
                ]),
                "average_importance_score": self._calculate_average_importance(),
                "last_sync": self._get_last_sync_time()
            },
            "adaptation_metrics": {
                "current_threshold": self.threshold,
                "current_decay_rate": self.decay_rate,
                "semantic_threshold": self.semantic_threshold,
                "adaptation_history": self._get_recent_adaptations()
            }
        }
        
        return analytics

    def _calculate_average_cluster_coherence(self) -> float:
        """Calcula coherencia promedio de clusters."""
        if not self.semantic_clusters:
            return 0.0
        
        total_coherence = sum(cluster["coherence"] for cluster in self.semantic_clusters.values())
        return total_coherence / len(self.semantic_clusters)

    def _get_domain_distribution(self) -> Dict[str, int]:
        """Obtiene distribución de palabras por dominio."""
        distribution = {}
        for domain, cluster in self.semantic_clusters.items():
            distribution[domain] = len(cluster["words"])
        return distribution

    def _get_pattern_strength_distribution(self) -> Dict[str, int]:
        """Obtiene distribución de fortaleza de patrones."""
        distribution = {"weak": 0, "medium": 0, "strong": 0}
        
        for pattern in self.causal_patterns.values():
            strength = pattern["strength"]
            if strength < 0.3:
                distribution["weak"] += 1
            elif strength < 0.7:
                distribution["medium"] += 1
            else:
                distribution["strong"] += 1
        
        return distribution

    def _calculate_average_importance(self) -> float:
        """Calcula importancia promedio de observaciones recientes."""
        if not self.feedback_loop:
            return 0.0
        
        recent_feedback = self.feedback_loop[-20:]  # Últimas 20
        total_importance = sum(f["importance"] for f in recent_feedback)
        return total_importance / len(recent_feedback)

    def _get_last_sync_time(self) -> str:
        """Obtiene timestamp de la última sincronización."""
        if not self.feedback_loop:
            return "never"
        return self.feedback_loop[-1]["timestamp"]

    def _get_recent_adaptations(self) -> List[Dict]:
        """Obtiene adaptaciones recientes de parámetros."""
        # Placeholder - en implementación real se registrarían cambios de parámetros
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "parameter": "threshold",
                "old_value": 2.0,
                "new_value": self.threshold,
                "reason": "adaptation_from_transcendent_insights"
            }
        ]

    def reflect(self) -> Dict:
        """Reflexión mejorada que integra múltiples fuentes de conocimiento."""
        reflection_data = {
            "strong_associations": self.get_strong_associations(),
            "semantic_clusters": list(self.semantic_clusters.keys()),
            "learning_velocity": self.learning_velocity,
            "dominant_domains": self._get_dominant_domains(),
            "emerging_concepts": self._identify_emerging_concepts(),
            "knowledge_gaps": self._identify_knowledge_gaps(),
            "integration_health": self._assess_integration_health()
        }
        
        print(f"[EnhancedLearningSystem] Reflexión completada:")
        print(f"  - Asociaciones fuertes: {len(reflection_data['strong_associations'])}")
        print(f"  - Clusters semánticos: {len(reflection_data['semantic_clusters'])}")
        print(f"  - Dominios dominantes: {reflection_data['dominant_domains']}")
        print(f"  - Conceptos emergentes: {len(reflection_data['emerging_concepts'])}")
        
        return reflection_data

    def _get_dominant_domains(self) -> List[str]:
        """Identifica dominios dominantes basándose en actividad."""
        domain_activity = defaultdict(float)
        
        # Contar actividad por dominio en observaciones recientes
        recent_observations = self.observations[-50:]  # Últimas 50
        for obs in recent_observations:
            text = obs["text"]
            domain = self._detect_domain(text, obs.get("context"))
            domain_activity[domain] += obs.get("priority", 1)
        
        # Devolver top 3 dominios
        sorted_domains = sorted(domain_activity.items(), key=lambda x: x[1], reverse=True)
        return [domain for domain, _ in sorted_domains[:3]]

    def _identify_emerging_concepts(self) -> List[Dict]:
        """Identifica conceptos emergentes basándose en tendencias."""
        emerging = []
        
        # Buscar palabras con crecimiento rápido reciente
        for word, current_strength in self.associations.items():
            if current_strength > 1.0:  # Solo considerar palabras con cierta fortaleza
                # Simular tendencia (en implementación real se registraría historial)
                recent_growth = current_strength - self.threshold
                if recent_growth > 0.5:
                    emerging.append({
                        "concept": word,
                        "strength": current_strength,
                        "growth": recent_growth,
                        "contexts": [
                            domain for domain, words in self.contextual_associations.items()
                            if word in words and words[word] > 0.5
                        ]
                    })
        
        # Ordenar por fortaleza
        emerging.sort(key=lambda x: x["strength"], reverse=True)
        return emerging[:10]  # Top 10

    def _identify_knowledge_gaps(self) -> List[str]:
        """Identifica posibles gaps en el conocimiento."""
        gaps = []
        
        # Buscar dominios con pocas asociaciones fuertes
        domain_strength = {}
        for domain in self.semantic_clusters.keys():
            if domain in self.contextual_associations:
                strong_words = [
                    word for word, strength in self.contextual_associations[domain].items()
                    if strength > self.threshold
                ]
                domain_strength[domain] = len(strong_words)
        
        # Identificar dominios débiles
        if domain_strength:
            avg_strength = sum(domain_strength.values()) / len(domain_strength)
            gaps = [
                domain for domain, strength in domain_strength.items()
                if strength < avg_strength * 0.5
            ]
        
        return gaps

    def _assess_integration_health(self) -> Dict:
        """Evalúa la salud de la integración con TranscendentMemory."""
        if not self.transcendent_memory:
            return {"status": "disconnected", "score": 0.0}
        
        health_metrics = {
            "connection_status": "connected",
            "successful_integrations_ratio": self.knowledge_integration_rate,
            "sync_frequency": len(self.feedback_loop) / max(len(self.observations), 1),
            "mutual_reinforcement": self._calculate_mutual_reinforcement(),
            "overall_score": 0.0
        }
        
        # Calcular puntuación general
        score_components = [
            health_metrics["successful_integrations_ratio"],
            min(health_metrics["sync_frequency"], 1.0),
            health_metrics["mutual_reinforcement"]
        ]
        health_metrics["overall_score"] = sum(score_components) / len(score_components)
        
        return health_metrics

    def _calculate_mutual_reinforcement(self) -> float:
        """Calcula el nivel de refuerzo mutuo con TranscendentMemory."""
        if not self.transcendent_memory or not self.feedback_loop:
            return 0.0
        
        # Contar cuántas asociaciones fuertes han sido reforzadas por TranscendentMemory
        strong_associations = self.get_strong_associations()
        reinforced_count = 0
        
        for feedback in self.feedback_loop[-20:]:  # Últimas 20 interacciones
            if feedback["feedback"].get("semantic_connections", 0) > 0:
                reinforced_count += 1
        
        return reinforced_count / min(len(self.feedback_loop), 20)

    # ==================== MÉTODOS DE COMPATIBILIDAD MEJORADOS ====================

    def get_associations(self) -> Dict[str, float]:
        """Retorna todas las asociaciones con sus conteos."""
        return dict(self.associations)

    def get_strong_associations(self) -> List[str]:
        """Retorna solo las palabras cuyo peso supera el umbral."""
        return [word for word, strength in self.associations.items() if strength >= self.threshold]

    def get_contextual_associations(self, domain: str = None) -> Dict:
        """Retorna asociaciones contextuales, opcionalmente filtradas por dominio."""
        if domain and domain in self.contextual_associations:
            return dict(self.contextual_associations[domain])
        else:
            return {
                domain: dict(associations) 
                for domain, associations in self.contextual_associations.items()
            }

    def get_learning_patterns(self) -> Dict:
        """Retorna patrones de aprendizaje detectados."""
        return {
            "causal_patterns": dict(self.causal_patterns),
            "semantic_clusters": {
                domain: {
                    "word_count": len(cluster["words"]),
                    "top_words": cluster["words"].most_common(10),
                    "coherence": cluster["coherence"]
                }
                for domain, cluster in self.semantic_clusters.items()
            },
            "concept_evolution": self.concept_evolution
        }

    # ==================== PERSISTENCIA MEJORADA ====================

    def save_enhanced_state(self) -> None:
        """Guarda el estado completo del sistema mejorado."""
        try:
            os.makedirs(self.memory_dir, exist_ok=True)
            
            # Guardar asociaciones principales
            associations_data = {
                "associations": dict(self.associations),
                "last_used": self.last_used,
                "contextual_associations": {
                    domain: dict(assocs) 
                    for domain, assocs in self.contextual_associations.items()
                },
                "threshold": self.threshold,
                "decay_rate": self.decay_rate,
                "semantic_threshold": self.semantic_threshold,
                "save_timestamp": datetime.now().isoformat()
            }
            
            with open(self.associations_file, "w", encoding="utf-8") as f:
                json.dump(associations_data, f, indent=2, ensure_ascii=False)
            
            # Guardar patrones de aprendizaje
            patterns_data = {
                "causal_patterns": self.causal_patterns,
                "semantic_clusters": {
                    domain: {
                        "words": dict(cluster["words"]),
                        "coherence": cluster["coherence"]
                    }
                    for domain, cluster in self.semantic_clusters.items()
                },
                "concept_evolution": self.concept_evolution,
                "learning_patterns": self.learning_patterns
            }
            
            with open(self.patterns_file, "w", encoding="utf-8") as f:
                json.dump(patterns_data, f, indent=2, ensure_ascii=False)
            
            # Guardar métricas
            metrics_data = {
                "learning_velocity": self.learning_velocity,
                "pattern_recognition_accuracy": self.pattern_recognition_accuracy,
                "knowledge_integration_rate": self.knowledge_integration_rate,
                "feedback_loop": self.feedback_loop[-50:],  # Últimas 50
                "recent_observations": [
                    {k: v for k, v in obs.items() if k != "text"}  # Sin contenido completo
                    for obs in self.observations[-100:]  # Últimas 100
                ]
            }
            
            with open(self.metrics_file, "w", encoding="utf-8") as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
            
            # Guardar evolución conceptual
            with open(self.evolution_file, "w", encoding="utf-8") as f:
                json.dump(self.concept_evolution, f, indent=2, ensure_ascii=False)
            
            print(f"[EnhancedLearningSystem] Estado completo guardado en {self.memory_dir}")
            
        except Exception as e:
            print(f"[EnhancedLearningSystem] Error guardando estado: {e}")

    def load_enhanced_state(self) -> None:
        """Carga el estado completo del sistema mejorado."""
        try:
            # Cargar asociaciones principales
            if os.path.exists(self.associations_file):
                with open(self.associations_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.associations = defaultdict(float, data.get("associations", {}))
                self.last_used = data.get("last_used", {})
                
                # Cargar asociaciones contextuales
                contextual_data = data.get("contextual_associations", {})
                self.contextual_associations = defaultdict(lambda: defaultdict(float))
                for domain, assocs in contextual_data.items():
                    self.contextual_associations[domain] = defaultdict(float, assocs)
                
                # Cargar configuración
                self.threshold = data.get("threshold", 2.0)
                self.decay_rate = data.get("decay_rate", 0.95)
                self.semantic_threshold = data.get("semantic_threshold", 0.3)
            
            # Cargar patrones
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.causal_patterns = data.get("causal_patterns", {})
                self.learning_patterns = data.get("learning_patterns", {})
                
                # Reconstruir clusters semánticos
                clusters_data = data.get("semantic_clusters", {})
                self.semantic_clusters = {}
                for domain, cluster_data in clusters_data.items():
                    self.semantic_clusters[domain] = {
                        "words": Counter(cluster_data.get("words", {})),
                        "coherence": cluster_data.get("coherence", 0.0),
                        "centroid": None  # Se recalculará si es necesario
                    }
                
                self.concept_evolution = data.get("concept_evolution", {})
            
            # Cargar métricas
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.learning_velocity = data.get("learning_velocity", 0.0)
                self.pattern_recognition_accuracy = data.get("pattern_recognition_accuracy", 0.0)
                self.knowledge_integration_rate = data.get("knowledge_integration_rate", 0.0)
                self.feedback_loop = data.get("feedback_loop", [])
            
            print(f"[EnhancedLearningSystem] Estado cargado: {len(self.associations)} asociaciones, "
                  f"{len(self.semantic_clusters)} clusters semánticos")
            
        except Exception as e:
            print(f"[EnhancedLearningSystem] Error cargando estado: {e}")
            print("[EnhancedLearningSystem] Iniciando con estado limpio")

    # ==================== MÉTODOS DE ANÁLISIS Y DEBUGGING ====================

    def export_learning_report(self) -> str:
        """Exporta un reporte completo del estado de aprendizaje."""
        try:
            analytics = self.get_learning_analytics()
            reflection = self.reflect()
            
            report = {
                "report_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "system_version": "EnhancedLearningSystem_v2.0",
                    "transcendent_memory_connected": self.transcendent_memory is not None
                },
                "learning_analytics": analytics,
                "reflection_data": reflection,
                "current_configuration": {
                    "threshold": self.threshold,
                    "decay_rate": self.decay_rate,
                    "semantic_threshold": self.semantic_threshold,
                    "adaptation_rate": self.adaptation_rate
                },
                "recent_activity": {
                    "observations_last_24h": len([
                        obs for obs in self.observations
                        if (datetime.now() - datetime.fromisoformat(obs["timestamp"])).days < 1
                    ]),
                    "integrations_last_week": len([
                        f for f in self.feedback_loop
                        if (datetime.now() - datetime.fromisoformat(f["timestamp"])).days < 7
                    ])
                }
            }
            
            # Guardar reporte
            report_file = os.path.join(
                self.memory_dir, 
                f"learning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"[EnhancedLearningSystem] Reporte exportado: {report_file}")
            return report_file
            
        except Exception as e:
            print(f"[EnhancedLearningSystem] Error exportando reporte: {e}")
            return ""

    def __del__(self):
        """Destructor que asegura limpieza adecuada."""
        try:
            self.stop_continuous_learning()
            self.save_enhanced_state()
        except:
            pass  # Evitar errores en destructor

    def _decay_old_associations(self) -> None:
        """Aplicar decaimiento temporal a las asociaciones basado en la última vez de uso.
        
        - El decaimiento se aplica exponencialmente por día: strength *= (decay_rate ** days_passed)
        - Se eliminan asociaciones insignificantes por debajo de un umbral mínimo.
        """
        try:
            now_ts = datetime.now().timestamp()
            min_keep = 0.01  # umbral mínimo para conservar

            # Decaimiento de asociaciones globales
            words_to_delete = []
            for word, strength in list(self.associations.items()):
                last_ts = self.last_used.get(word, now_ts)
                days = max(0.0, (now_ts - float(last_ts)) / 86400.0)
                if days > 0:
                    decayed = strength * (self.decay_rate ** days)
                else:
                    decayed = strength
                if decayed < min_keep:
                    words_to_delete.append(word)
                else:
                    self.associations[word] = decayed
            for w in words_to_delete:
                self.associations.pop(w, None)
                self.last_used.pop(w, None)

            # Opcional: decaimiento simple para asociaciones contextuales (sin last_used granular)
            for domain, assocs in self.contextual_associations.items():
                for word in list(assocs.keys()):
                    assocs[word] *= self.decay_rate
                    if assocs[word] < min_keep:
                        del assocs[word]
        except Exception as e:
            print(f"[EnhancedLearningSystem] Error en _decay_old_associations: {e}")