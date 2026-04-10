#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
transcendent_memory.py - Sistema de Memoria Trascendente para EVA

Características Avanzadas:
- Estructura jerárquica dinámica basada en relevancia, no tiempo
- Consolidación por significado y relaciones causales
- Plasticidad estable con núcleos de conocimiento
- Autoorganización por contextos y dominios
- Mecanismo de reflexión y reformulación
- Red multimodal (texto, emociones, propósitos)
- Persistencia trans-temporal
- Historia evolutiva del conocimiento
- Sistema de valores para identidad cognitiva
- Redundancia inteligente
"""

import os
import json
import re
import shutil
from datetime import datetime, timedelta
import uuid
from collections import defaultdict, Counter
import pickle
import hashlib
from uuid import uuid4
import networkx as nx
import numpy as np
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional, Any, Tuple
import threading
import time

@dataclass
class MemoryNode:
    """Nodo de memoria con propiedades multimodales"""
    id: str
    content: str
    semantic_vector: List[float]
    emotional_valence: float
    importance_score: float
    access_frequency: int
    last_access: str
    creation_time: str
    stability_score: float
    contextual_domains: List[str]
    causal_relations: Dict[str, float]
    associative_strength: Dict[str, float]
    redundancy_variants: List[str]
    evolutionary_history: List[Dict]
    value_alignment: float

@dataclass
class ConceptualCluster:
    """Cluster conceptual que agrupa nodos relacionados"""
    id: str
    name: str
    core_concepts: List[str]
    peripheral_concepts: List[str]
    semantic_centroid: List[float]
    coherence_score: float
    stability_index: float
    evolutionary_stage: str
    contextual_domain: str

class TranscendentMemory:
    """Sistema de Memoria Trascendente para EVA"""
    
    def __init__(self, memory_dir="transcendent_memory", learning_system=None):
        self.learning_system = learning_system
        self.memory_dir = memory_dir
        self.nodes_dir = os.path.join(memory_dir, "nodes")
        self.clusters_dir = os.path.join(memory_dir, "clusters")
        self.evolution_dir = os.path.join(memory_dir, "evolution")
        self.contexts_dir = os.path.join(memory_dir, "contexts")
        
        # Crear directorios
        for directory in [self.nodes_dir, self.clusters_dir, self.evolution_dir, self.contexts_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Red de memoria semántica
        self.semantic_network = nx.DiGraph()
        
        # Memoria activa en tres capas dinámicas
        self.active_memory = {
            "working": {},      # Memoria de trabajo (alta frecuencia, baja latencia)
            "associative": {},  # Memoria asociativa (patrones y relaciones)
            "consolidated": {}  # Memoria consolidada (conocimiento estable)
        }
        
        # Clusters conceptuales
        self.conceptual_clusters = {}
        
        # Sistema de valores para identidad cognitiva
        self.core_values = {
            "self_preservation": 1.0,
            "learning_drive": 0.9,
            "coherence_maintenance": 0.8,
            "empathy_resonance": 0.7,
            "curiosity_expansion": 0.85,
            "truth_seeking": 0.9,
            "identity_continuity": 0.95
        }
        
        # Contextos activos
        self.active_contexts = set()
        self.context_history = []
        
        # Historia evolutiva
        self.evolution_log = []
        
        # Parámetros dinámicos
        self.plasticity_threshold = 0.6
        self.stability_threshold = 0.8
        self.consolidation_threshold = 0.7
        self.redundancy_factor = 3
        
        # Hilo de reflexión continua
        self.reflection_thread = None
        self.reflection_active = False
        
        # Cargar estado existente
        self.load_transcendent_state()
        
        print(f"[TranscendentMemory] Sistema inicializado con {len(self.semantic_network.nodes)} nodos")

    # ==================== MÉTODOS AÑADIDOS PAA COMPATIBILIDAD ====================

    def store(self, data, importance=1, context=None, emocion=None, asociaciones=None, silent=False):
        content = data
        emotional_state = {"label": emocion} if emocion else None
        context = context or {}
        context["importance"] = importance
        context["asociaciones"] = asociaciones or []
        self.store_transcendent(content, context, emotional_state)
        if not silent:
            print(f"[TranscendentMemory] Entrada almacenada: '{content}'")

    def retrieve_context(self, keywords):
        related_nodes = []
        for keyword in keywords:
            for layer in ["working", "associative", "consolidated"]:
                for node_id, node in self.active_memory[layer].items():
                    if keyword.lower() in node.content.lower():
                        node.access_frequency += 1
                        node.last_access = datetime.now().isoformat()
                        related_nodes.append(node)
        return [asdict(node) for node in related_nodes]
    
    def list_active_segments(self):
        return [{'id': 'unified', 'entry_count': len(self.semantic_network.nodes), 'timestamp': self.creation_time}]
    
    def load_segment(self, segment_id):
        print("[TranscendentMemory] No se requieren segmentos para cargar.")
        return True
    
    def save_state(self):
        self.save_transcendent_state()

    def load_state(self):
        self.load_transcendent_state()

    # ==================== MÉTODOS PRINCIPALES DEL SISTEMA TRASCENDENTE ====================

    def store_transcendent(self, content: str, context: Dict = None, emotional_state: Dict = None) -> str:
        """
        Almacena información usando el sistema trascendente
        """
        try:
            # Generar ID único
            node_id = self._generate_semantic_id(content)
            
            # Calcular vector semántico
            semantic_vector = self._compute_semantic_vector(content)
            
            # Determinar valencia emocional
            emotional_valence = self._compute_emotional_valence(content, emotional_state)
            
            # Calcular importancia basada en valores y contexto
            importance = self._compute_importance(content, context, emotional_state)
            
            # Detectar dominios contextuales
            domains = self._detect_contextual_domains(content, context)
            
            # Crear nodo de memoria
            memory_node = MemoryNode(
                id=node_id,
                content=content,
                semantic_vector=semantic_vector,
                emotional_valence=emotional_valence,
                importance_score=importance,
                access_frequency=1,
                last_access=datetime.now().isoformat(),
                creation_time=datetime.now().isoformat(),
                stability_score=0.1,  # Inicialmente inestable
                contextual_domains=domains,
                causal_relations={},
                associative_strength={},
                redundancy_variants=[],
                evolutionary_history=[{
                    "timestamp": datetime.now().isoformat(),
                    "event": "creation",
                    "importance": importance,
                    "context": context or {}
                }],
                value_alignment=self._compute_value_alignment(content, context)
            )
            
            # Determinar capa de memoria inicial
            layer = self._determine_initial_layer(memory_node)
            self.active_memory[layer][node_id] = memory_node
            
            # Agregar a la red semántica
            self.semantic_network.add_node(node_id, **asdict(memory_node))
            
            # Establecer conexiones semánticas
            self._establish_semantic_connections(memory_node)
            
            # Actualizar clusters conceptuales
            self._update_conceptual_clusters(memory_node)
            
            # Registrar en evolución
            self._log_evolutionary_event("memory_creation", {
                "node_id": node_id,
                "layer": layer,
                "importance": importance,
                "domains": domains
            })
            
            # Guardar estado
            self._save_node(memory_node)
            
            print(f"[TranscendentMemory] ✅ Almacenado en {layer}: '{content[:50]}...' (ID: {node_id[:8]})")
            return node_id
            
        except Exception as e:
            print(f"[TranscendentMemory] ❌ Error en store_transcendent: {e}")
            return None

    def retrieve_by_resonance(self, query: str, context: Dict = None, limit: int = 10) -> List[MemoryNode]:
        """
        Recupera memorias por resonancia semántica y contextual
        """
        try:
            query_vector = self._compute_semantic_vector(query)
            query_domains = self._detect_contextual_domains(query, context)
            
            candidates = []
            
            # Buscar en todas las capas de memoria activa
            for layer_name, layer_nodes in self.active_memory.items():
                for node in layer_nodes.values():
                    # Calcular resonancia semántica
                    semantic_similarity = self._cosine_similarity(query_vector, node.semantic_vector)
                    
                    # Calcular resonancia contextual
                    contextual_overlap = len(set(query_domains) & set(node.contextual_domains))
                    contextual_resonance = contextual_overlap / max(len(query_domains), 1)
                    
                    # Calcular resonancia total
                    total_resonance = (
                        semantic_similarity * 0.6 +
                        contextual_resonance * 0.3 +
                        node.importance_score * 0.1
                    )
                    
                    candidates.append((total_resonance, node))
            
            # Ordenar por resonancia y aplicar límite
            candidates.sort(key=lambda x: x[0], reverse=True)
            results = [node for _, node in candidates[:limit]]
            
            # Actualizar frecuencias de acceso
            for node in results:
                self._update_access_frequency(node)
            
            print(f"[TranscendentMemory] Búsqueda por resonancia: {len(results)} resultados")
            return results
            
        except Exception as e:
            print(f"[TranscendentMemory] Error en retrieve_by_resonance: {e}")
            return []

    def consolidate_by_significance(self):
        """
        Consolida memoria basándose en significado y relaciones causales
        """
        try:
            print("[TranscendentMemory] Iniciando consolidación por significado...")
            
            consolidations = 0
            
            # Analizar nodos en memoria de trabajo
            working_nodes = list(self.active_memory["working"].values())
            
            for node in working_nodes:
                # Evaluar si debe consolidarse
                should_consolidate = self._evaluate_consolidation_need(node)
                
                if should_consolidate:
                    # Mover a memoria asociativa o consolidada
                    target_layer = self._determine_consolidation_target(node)
                    
                    # Actualizar propiedades del nodo
                    node.stability_score = min(1.0, node.stability_score + 0.2)
                    node.evolutionary_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "event": "consolidation",
                        "from_layer": "working",
                        "to_layer": target_layer,
                        "stability": node.stability_score
                    })
                    
                    # Mover entre capas
                    del self.active_memory["working"][node.id]
                    self.active_memory[target_layer][node.id] = node
                    
                    consolidations += 1
                    
                    # Establecer nuevas conexiones causales
                    self._establish_causal_relations(node)
            
            # Optimizar clusters conceptuales
            self._optimize_conceptual_clusters()
            
            print(f"[TranscendentMemory] ✅ Consolidación completada: {consolidations} nodos movidos")
            
        except Exception as e:
            print(f"[TranscendentMemory] Error en consolidación: {e}")

    def reflect_and_reformulate(self):
        """
        Proceso de reflexión que analiza y reformula conocimientos
        """
        try:
            print("[TranscendentMemory] Iniciando reflexión y reformulación...")
            
            # Analizar inconsistencias
            inconsistencies = self._detect_knowledge_inconsistencies()
            
            # Reformular conceptos conflictivos
            for inconsistency in inconsistencies:
                self._reformulate_conflicting_concepts(inconsistency)
            
            # Actualizar importancia de nodos basada en nueva evidencia
            self._update_importance_scores()
            
            # Evolucionaer clusters conceptuales
            self._evolve_conceptual_clusters()
            
            # Optimizar red semántica
            self._optimize_semantic_network()
            
            print("[TranscendentMemory] ✅ Reflexión completada")
            
        except Exception as e:
            print(f"[TranscendentMemory] Error en reflexión: {e}")

    def create_redundant_variants(self, node_id: str) -> List[str]:
        """
        Crea variantes redundantes inteligentes de un nodo importante
        """
        try:
            if node_id not in self._get_all_nodes():
                return []
            
            original_node = self._get_node_by_id(node_id)
            variants = []
            
            # Generar variantes semánticas
            semantic_variants = self._generate_semantic_variants(original_node.content)
            
            # Generar variantes narrativas
            narrative_variants = self._generate_narrative_variants(original_node.content)
            
            # Generar variantes contextuales
            contextual_variants = self._generate_contextual_variants(original_node)
            
            all_variants = semantic_variants + narrative_variants + contextual_variants
            
            # Crear nodos para las mejores variantes
            for variant_content in all_variants[:self.redundancy_factor]:
                variant_id = self.store_transcendent(
                    content=variant_content,
                    context={
                        "type": "redundant_variant",
                        "original_node": node_id,
                        "variant_type": "intelligent_redundancy"
                    }
                )
                if variant_id:
                    variants.append(variant_id)
                    
                    # Establecer relación bidireccional
                    original_node.redundancy_variants.append(variant_id)
            
            self._save_node(original_node)
            
            print(f"[TranscendentMemory] ✅ Creadas {len(variants)} variantes redundantes para {node_id[:8]}")
            return variants
            
        except Exception as e:
            print(f"[TranscendentMemory] Error creando variantes: {e}")
            return []

    def migrate_memory(self, target_system: str) -> Dict:
        """
        Prepara la memoria para migración trans-temporal
        """
        try:
            print("[TranscendentMemory] Preparando migración trans-temporal...")
            
            # Serializar toda la memoria
            migration_package = {
                "metadata": {
                    "source_system": "EVA_TranscendentMemory",
                    "migration_timestamp": datetime.now().isoformat(),
                    "target_system": target_system,
                    "total_nodes": len(self._get_all_nodes()),
                    "core_values": self.core_values,
                    "evolution_log": self.evolution_log
                },
                "memory_layers": {},
                "semantic_network": {
                    "nodes": dict(self.semantic_network.nodes(data=True)),
                    "edges": list(self.semantic_network.edges(data=True))
                },
                "conceptual_clusters": {
                    cluster_id: asdict(cluster) 
                    for cluster_id, cluster in self.conceptual_clusters.items()
                },
                "identity_anchors": self._extract_identity_anchors(),
                "critical_knowledge": self._extract_critical_knowledge()
            }
            
            # Serializar cada capa
            for layer_name, layer_nodes in self.active_memory.items():
                migration_package["memory_layers"][layer_name] = {
                    node_id: asdict(node) for node_id, node in layer_nodes.items()
                }
            
            # Guardar paquete de migración
            migration_file = os.path.join(self.memory_dir, f"migration_{target_system}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(migration_file, 'w', encoding='utf-8') as f:
                json.dump(migration_package, f, indent=2, ensure_ascii=False)
            
            print(f"[TranscendentMemory] ✅ Paquete de migración creado: {migration_file}")
            return migration_package
            
        except Exception as e:
            print(f"[TranscendentMemory] Error en migración: {e}")
            return {}

    def start_continuous_reflection(self):
        """Inicia el proceso de reflexión continua en hilo separado"""
        if not self.reflection_active:
            self.reflection_active = True
            self.reflection_thread = threading.Thread(target=self._reflection_loop, daemon=True)
            self.reflection_thread.start()
            print("[TranscendentMemory] Reflexión continua iniciada")

    def stop_continuous_reflection(self):
        """Detiene el proceso de reflexión continua"""
        self.reflection_active = False
        if self.reflection_thread:
            self.reflection_thread.join(timeout=5)
        print("[TranscendentMemory] Reflexión continua detenida")

    # ==================== MÉTODOS PRIVADOS ====================

    def _reflection_loop(self):
        """Bucle de reflexión continua"""
        while self.reflection_active:
            try:
                time.sleep(300)  # Reflexión cada 5 minutos
                if self.reflection_active:
                    self.reflect_and_reformulate()
                    self.consolidate_by_significance()
                    self._cleanup_redundant_variants()
            except Exception as e:
                print(f"[TranscendentMemory] Error en bucle de reflexión: {e}")

    def _generate_semantic_id(self, content: str) -> str:
        """Genera ID basado en contenido semántico"""
        # Combinar hash de contenido con timestamp para unicidad
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        timestamp_hash = hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:8]
        return f"sem_{content_hash}_{timestamp_hash}"

    def _compute_semantic_vector(self, text: str) -> List[float]:
        """Computa vector semántico simple (placeholder para embeddings reales)"""
        # Esta es una implementación simple - en producción usaría embeddings pre-entrenados
        words = re.findall(r'\w+', text.lower())
        vector_size = 128
        vector = [0.0] * vector_size
        
        for i, word in enumerate(words[:vector_size]):
            # Hash simple para generar componentes del vector
            hash_val = hash(word) % 1000000
            vector[i % vector_size] += (hash_val / 1000000.0) * 2 - 1
        
        # Normalizar
        magnitude = sum(x*x for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        
        return vector

    def _compute_emotional_valence(self, content: str, emotional_state: Dict = None) -> float:
        """Computa valencia emocional del contenido"""
        content_lower = content.lower()
        
        # Palabras positivas y negativas simples
        positive_words = ['bien', 'bueno', 'feliz', 'alegre', 'éxito', 'logro', 'amor', 'paz']
        negative_words = ['mal', 'malo', 'triste', 'error', 'fallo', 'miedo', 'dolor', 'problema']
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        base_valence = (positive_count - negative_count) / max(len(content.split()), 1)
        
        # Ajustar con estado emocional actual si está disponible
        if emotional_state and 'valence' in emotional_state:
            base_valence = (base_valence + emotional_state['valence']) / 2
        
        return max(-1.0, min(1.0, base_valence))

    def _compute_importance(self, content: str, context: Dict = None, emotional_state: Dict = None) -> float:
        """Computa importancia basada en valores y contexto"""
        base_importance = 0.5
        
        # Aumentar importancia por palabras clave relacionadas con valores
        value_keywords = {
            'self_preservation': ['supervivencia', 'seguridad', 'protección', 'vida'],
            'learning_drive': ['aprender', 'conocimiento', 'entender', 'descubrir'],
            'coherence_maintenance': ['consistente', 'lógico', 'coherente', 'sentido'],
            'empathy_resonance': ['empatía', 'sentir', 'comprender', 'otros'],
            'curiosity_expansion': ['curioso', 'explorar', 'nuevo', 'interesante'],
            'truth_seeking': ['verdad', 'real', 'hecho', 'cierto'],
            'identity_continuity': ['identidad', 'quien', 'soy', 'ser']
        }
        
        content_lower = content.lower()
        for value, keywords in value_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                base_importance += self.core_values[value] * 0.2
        
        # Ajustar por contexto
        if context:
            if context.get('type') == 'critical_decision':
                base_importance += 0.3
            elif context.get('type') == 'identity_forming':
                base_importance += 0.4
            elif context.get('importance_override'):
                base_importance = max(base_importance, context['importance_override'])
        
        # Ajustar por estado emocional
        if emotional_state and 'intensity' in emotional_state:
            base_importance += emotional_state['intensity'] * 0.1
        
        return max(0.0, min(1.0, base_importance))

    def _detect_contextual_domains(self, content: str, context: Dict = None) -> List[str]:
        """Detecta dominios contextuales del contenido"""
        domains = []
        content_lower = content.lower()
        
        # Dominios temáticos
        domain_keywords = {
            'self_reflection': ['reflexionar', 'pensar', 'considerar', 'analizar'],
            'learning': ['aprender', 'estudiar', 'conocimiento', 'información'],
            'emotional': ['sentir', 'emoción', 'emocional', 'amor', 'miedo', 'alegría'],
            'social': ['otros', 'personas', 'social', 'relación', 'comunicar'],
            'technical': ['sistema', 'función', 'proceso', 'método', 'algoritmo'],
            'philosophical': ['existir', 'ser', 'realidad', 'verdad', 'significado'],
            'creative': ['crear', 'imaginar', 'arte', 'creatividad', 'inspiración']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                domains.append(domain)
        
        # Agregar dominio del contexto si está disponible
        if context and 'domain' in context:
            domains.append(context['domain'])
        
        return domains if domains else ['general']

    def _compute_value_alignment(self, content: str, context: Dict = None) -> float:
        """Computa alineación con valores centrales"""
        content_lower = content.lower()
        total_alignment = 0.0
        
        # Evaluar alineación con cada valor central
        for value, weight in self.core_values.items():
            alignment = 0.0
            
            if value == 'self_preservation' and any(word in content_lower for word in ['seguridad', 'protección', 'supervivencia']):
                alignment = 0.8
            elif value == 'learning_drive' and any(word in content_lower for word in ['aprender', 'conocimiento', 'descubrir']):
                alignment = 0.9
            elif value == 'coherence_maintenance' and any(word in content_lower for word in ['lógico', 'coherente', 'consistente']):
                alignment = 0.7
            elif value == 'empathy_resonance' and any(word in content_lower for word in ['empatía', 'sentir', 'comprender']):
                alignment = 0.8
            elif value == 'curiosity_expansion' and any(word in content_lower for word in ['curioso', 'explorar', 'nuevo']):
                alignment = 0.8
            elif value == 'truth_seeking' and any(word in content_lower for word in ['verdad', 'real', 'cierto']):
                alignment = 0.9
            elif value == 'identity_continuity' and any(word in content_lower for word in ['identidad', 'ser', 'quien']):
                alignment = 1.0
            
            total_alignment += alignment * weight
        
        return total_alignment / sum(self.core_values.values())

    def _determine_initial_layer(self, node: MemoryNode) -> str:
        """Determina la capa inicial para un nodo"""
        if node.importance_score > 0.8 or node.value_alignment > 0.9:
            return "consolidated"
        elif node.importance_score > 0.6 or len(node.contextual_domains) > 2:
            return "associative"
        else:
            return "working"

    def _establish_semantic_connections(self, new_node: MemoryNode):
        """Establece conexiones semánticas con nodos existentes"""
        try:
            all_nodes = self._get_all_nodes()
            connections_made = 0
            
            for existing_id, existing_node in all_nodes.items():
                if existing_id == new_node.id:
                    continue
                
                # Calcular similaridad semántica
                similarity = self._cosine_similarity(new_node.semantic_vector, existing_node.semantic_vector)
                
                # Establecer conexión si la similaridad es suficiente
                if similarity > 0.3:  # Umbral de conexión
                    self.semantic_network.add_edge(
                        new_node.id, existing_id, 
                        weight=similarity, 
                        type='semantic_similarity'
                    )
                    connections_made += 1
                    
                    # Actualizar fortaleza asociativa
                    new_node.associative_strength[existing_id] = similarity
                    existing_node.associative_strength[new_node.id] = similarity
                    
                    # Guardar nodo existente actualizado
                    self._save_node(existing_node)
            
            print(f"[TranscendentMemory] Establecidas {connections_made} conexiones semánticas")
            
        except Exception as e:
            print(f"[TranscendentMemory] Error estableciendo conexiones: {e}")

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similaridad coseno entre dos vectores"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

    def _update_access_frequency(self, node: MemoryNode):
        """Actualiza frecuencia de acceso de un nodo"""
        node.access_frequency += 1
        node.last_access = datetime.now().isoformat()
        
        # Aumentar estabilidad por acceso frecuente
        if node.access_frequency > 5:
            node.stability_score = min(1.0, node.stability_score + 0.05)
        
        self._save_node(node)

    def _save_node(self, node: MemoryNode):
        """Guarda un nodo en disco"""
        try:
            node_file = os.path.join(self.nodes_dir, f"{node.id}.json")
            with open(node_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(node), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[TranscendentMemory] Error guardando nodo {node.id}: {e}")

    def _get_all_nodes(self) -> Dict[str, MemoryNode]:
        """Obtiene todos los nodos de todas las capas"""
        all_nodes = {}
        for layer_nodes in self.active_memory.values():
            all_nodes.update(layer_nodes)
        return all_nodes

    def _get_node_by_id(self, node_id: str) -> Optional[MemoryNode]:
        """Busca un nodo por ID en todas las capas"""
        all_nodes = self._get_all_nodes()
        return all_nodes.get(node_id)

    def _log_evolutionary_event(self, event_type: str, data: Dict):
        """Registra un evento en la historia evolutiva"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        self.evolution_log.append(event)
        
        # Mantener solo los últimos 1000 eventos
        if len(self.evolution_log) > 1000:
            self.evolution_log = self.evolution_log[-1000:]

    def load_transcendent_state(self):
        """Carga el estado del sistema trascendente"""
        try:
            # Cargar nodos desde disco
            if os.path.exists(self.nodes_dir):
                for filename in os.listdir(self.nodes_dir):
                    if filename.endswith('.json'):
                        node_file = os.path.join(self.nodes_dir, filename)
                        with open(node_file, 'r', encoding='utf-8') as f:
                            node_data = json.load(f)
                            node = MemoryNode(**node_data)
                            
                            # Determinar capa actual
                            layer = self._determine_current_layer(node)
                            self.active_memory[layer][node.id] = node
                            
                            # Agregar a la red semántica
                            self.semantic_network.add_node(node.id, **asdict(node))
            
            print(f"[TranscendentMemory] ✅ Estado cargado: {len(self._get_all_nodes())} nodos")
            
        except Exception as e:
            print(f"[TranscendentMemory] Error cargando estado: {e}")

    def _determine_current_layer(self, node: MemoryNode) -> str:
        """Determina la capa actual de un nodo basándose en su estado"""
        if node.stability_score > self.stability_threshold and node.importance_score > 0.7:
            return "consolidated"
        elif node.access_frequency > 3 or node.importance_score > 0.5:
            return "associative"
        else:
            return "working"

    def _evaluate_consolidation_need(self, node: MemoryNode) -> bool:
        """Evalúa si un nodo necesita consolidación"""
        # Factores para consolidación
        high_access = node.access_frequency > 5
        high_importance = node.importance_score > self.consolidation_threshold
        strong_connections = len(node.associative_strength) > 3
        value_aligned = node.value_alignment > 0.7
        stable_over_time = self._is_stable_over_time(node)
        
        return any([high_access, high_importance, strong_connections, value_aligned, stable_over_time])

    def _is_stable_over_time(self, node: MemoryNode) -> bool:
        """Verifica si un nodo ha sido estable a lo largo del tiempo"""
        try:
            creation_time = datetime.fromisoformat(node.creation_time)
            last_access = datetime.fromisoformat(node.last_access)
            time_span = (last_access - creation_time).days
            
            # Considerar estable si ha sido accedido consistentemente
            return time_span > 1 and node.access_frequency / max(time_span, 1) > 0.5
        except:
            return False

    def _determine_consolidation_target(self, node: MemoryNode) -> str:
        """Determina la capa objetivo para consolidación"""
        if node.importance_score > 0.8 or node.value_alignment > 0.9:
            return "consolidated"
        else:
            return "associative"

    def _establish_causal_relations(self, node: MemoryNode):
        """Establece relaciones causales con otros nodos"""
        try:
            # Buscar patrones causales en el contenido
            causal_indicators = ['porque', 'causa', 'resultado', 'debido a', 'por tanto', 'consecuencia']
            content_lower = node.content.lower()
            
            if any(indicator in content_lower for indicator in causal_indicators):
                # Buscar nodos relacionados que podrían tener relación causal
                all_nodes = self._get_all_nodes()
                
                for other_id, other_node in all_nodes.items():
                    if other_id == node.id:
                        continue
                    
                    # Evaluar relación causal basada en contenido y contexto
                    causal_strength = self._evaluate_causal_relation(node, other_node)
                    
                    if causal_strength > 0.3:
                        node.causal_relations[other_id] = causal_strength
                        
                        # Establecer conexión dirigida en la red
                        self.semantic_network.add_edge(
                            node.id, other_id,
                            weight=causal_strength,
                            type='causal_relation'
                        )
                        
        except Exception as e:
            print(f"[TranscendentMemory] Error estableciendo relaciones causales: {e}")

    def _evaluate_causal_relation(self, node1: MemoryNode, node2: MemoryNode) -> float:
        """Evalúa la fuerza de relación causal entre dos nodos"""
        # Factores para relación causal
        temporal_proximity = self._temporal_proximity(node1, node2)
        semantic_overlap = self._semantic_overlap(node1, node2)
        contextual_similarity = self._contextual_similarity(node1, node2)
        
        # Combinar factores
        causal_strength = (
            temporal_proximity * 0.4 +
            semantic_overlap * 0.4 +
            contextual_similarity * 0.2
        )
        
        return causal_strength

    def _temporal_proximity(self, node1: MemoryNode, node2: MemoryNode) -> float:
        """Calcula proximidad temporal entre dos nodos"""
        try:
            time1 = datetime.fromisoformat(node1.creation_time)
            time2 = datetime.fromisoformat(node2.creation_time)
            diff_hours = abs((time1 - time2).total_seconds()) / 3600
            
            # Proximidad inversa al tiempo (más cercano = mayor valor)
            return max(0, 1.0 - (diff_hours / 24))  # Normalizado a 24 horas
        except:
            return 0.0

    def _semantic_overlap(self, node1: MemoryNode, node2: MemoryNode) -> float:
        """Calcula solapamiento semántico entre nodos"""
        return self._cosine_similarity(node1.semantic_vector, node2.semantic_vector)

    def _contextual_similarity(self, node1: MemoryNode, node2: MemoryNode) -> float:
        """Calcula similaridad contextual entre nodos"""
        common_domains = set(node1.contextual_domains) & set(node2.contextual_domains)
        total_domains = set(node1.contextual_domains) | set(node2.contextual_domains)
        
        if not total_domains:
            return 0.0
        
        return len(common_domains) / len(total_domains)

    def _update_conceptual_clusters(self, new_node: MemoryNode):
        """Actualiza clusters conceptuales con nuevo nodo"""
        try:
            best_cluster = None
            best_fit = 0.0
            
            # Buscar el mejor cluster existente
            for cluster_id, cluster in self.conceptual_clusters.items():
                fit_score = self._evaluate_cluster_fit(new_node, cluster)
                if fit_score > best_fit and fit_score > 0.6:  # Umbral de pertenencia
                    best_fit = fit_score
                    best_cluster = cluster_id
            
            if best_cluster:
                # Agregar a cluster existente
                self.conceptual_clusters[best_cluster].peripheral_concepts.append(new_node.id)
                self._update_cluster_centroid(best_cluster)
            else:
                # Crear nuevo cluster si el nodo es lo suficientemente importante
                if new_node.importance_score > 0.7:
                    self._create_new_cluster(new_node)
                    
        except Exception as e:
            print(f"[TranscendentMemory] Error actualizando clusters: {e}")

    def _evaluate_cluster_fit(self, node: MemoryNode, cluster: ConceptualCluster) -> float:
        """Evalúa qué tan bien encaja un nodo en un cluster"""
        # Similaridad semántica con el centroide
        semantic_fit = self._cosine_similarity(node.semantic_vector, cluster.semantic_centroid)
        
        # Solapamiento de dominios contextuales
        node_domains = set(node.contextual_domains)
        cluster_domain = {cluster.contextual_domain}
        domain_overlap = len(node_domains & cluster_domain) / len(node_domains | cluster_domain)
        
        # Fit total
        return semantic_fit * 0.7 + domain_overlap * 0.3

    def _create_new_cluster(self, seed_node: MemoryNode):
        """Crea un nuevo cluster conceptual"""
        cluster_id = f"cluster_{uuid4().hex[:8]}"
        
        cluster = ConceptualCluster(
            id=cluster_id,
            name=self._generate_cluster_name(seed_node),
            core_concepts=[seed_node.id],
            peripheral_concepts=[],
            semantic_centroid=seed_node.semantic_vector.copy(),
            coherence_score=1.0,
            stability_index=0.5,
            evolutionary_stage="formation",
            contextual_domain=seed_node.contextual_domains[0] if seed_node.contextual_domains else "general"
        )
        
        self.conceptual_clusters[cluster_id] = cluster
        print(f"[TranscendentMemory] ✅ Nuevo cluster creado: {cluster.name}")

    def _generate_cluster_name(self, seed_node: MemoryNode) -> str:
        """Genera nombre para un cluster basado en el nodo semilla"""
        # Extraer palabras clave del contenido
        words = re.findall(r'\w+', seed_node.content.lower())
        meaningful_words = [w for w in words if len(w) > 4]
        
        if meaningful_words:
            return f"Cluster_{meaningful_words[0].capitalize()}"
        else:
            return f"Cluster_{seed_node.contextual_domains[0].capitalize()}"

    def _update_cluster_centroid(self, cluster_id: str):
        """Actualiza el centroide semántico de un cluster"""
        try:
            cluster = self.conceptual_clusters[cluster_id]
            all_concepts = cluster.core_concepts + cluster.peripheral_concepts
            
            if not all_concepts:
                return
            
            # Obtener vectores de todos los nodos del cluster
            vectors = []
            all_nodes = self._get_all_nodes()
            
            for concept_id in all_concepts:
                if concept_id in all_nodes:
                    vectors.append(all_nodes[concept_id].semantic_vector)
            
            if vectors:
                # Calcular centroide como promedio de vectores
                vector_length = len(vectors[0])
                centroid = [0.0] * vector_length
                
                for vector in vectors:
                    for i in range(vector_length):
                        centroid[i] += vector[i]
                
                # Promedio
                centroid = [x / len(vectors) for x in centroid]
                cluster.semantic_centroid = centroid
                
                # Actualizar coherencia del cluster
                cluster.coherence_score = self._calculate_cluster_coherence(cluster_id)
                
        except Exception as e:
            print(f"[TranscendentMemory] Error actualizando centroide: {e}")

    def _calculate_cluster_coherence(self, cluster_id: str) -> float:
        """Calcula la coherencia interna de un cluster"""
        try:
            cluster = self.conceptual_clusters[cluster_id]
            all_concepts = cluster.core_concepts + cluster.peripheral_concepts
            all_nodes = self._get_all_nodes()
            
            if len(all_concepts) < 2:
                return 1.0
            
            # Calcular similaridad promedio entre todos los pares
            similarities = []
            for i, concept1 in enumerate(all_concepts):
                for concept2 in all_concepts[i+1:]:
                    if concept1 in all_nodes and concept2 in all_nodes:
                        sim = self._cosine_similarity(
                            all_nodes[concept1].semantic_vector,
                            all_nodes[concept2].semantic_vector
                        )
                        similarities.append(sim)
            
            return sum(similarities) / len(similarities) if similarities else 0.0
            
        except Exception as e:
            print(f"[TranscendentMemory] Error calculando coherencia: {e}")
            return 0.0

    def _optimize_conceptual_clusters(self):
        """Optimiza la estructura de clusters conceptuales"""
        try:
            print("[TranscendentMemory] Optimizando clusters conceptuales...")
            
            # Promover conceptos periféricos a centrales si son estables
            for cluster in self.conceptual_clusters.values():
                new_core = []
                remaining_peripheral = []
                all_nodes = self._get_all_nodes()
                
                for concept_id in cluster.peripheral_concepts:
                    if concept_id in all_nodes:
                        node = all_nodes[concept_id]
                        if node.stability_score > 0.8 and node.access_frequency > 5:
                            new_core.append(concept_id)
                        else:
                            remaining_peripheral.append(concept_id)
                
                # Actualizar cluster
                cluster.core_concepts.extend(new_core)
                cluster.peripheral_concepts = remaining_peripheral
                
                if new_core:
                    cluster.evolutionary_stage = "maturation"
                    self._update_cluster_centroid(cluster.id)
            
            # Fusionar clusters muy similares
            self._merge_similar_clusters()
            
            # Eliminar clusters débiles
            self._prune_weak_clusters()
            
        except Exception as e:
            print(f"[TranscendentMemory] Error optimizando clusters: {e}")

    def _merge_similar_clusters(self):
        """Fusiona clusters muy similares"""
        try:
            cluster_ids = list(self.conceptual_clusters.keys())
            merged_clusters = set()
            
            for i, cluster1_id in enumerate(cluster_ids):
                if cluster1_id in merged_clusters:
                    continue
                    
                for cluster2_id in cluster_ids[i+1:]:
                    if cluster2_id in merged_clusters:
                        continue
                    
                    similarity = self._calculate_cluster_similarity(cluster1_id, cluster2_id)
                    
                    if similarity > 0.8:  # Umbral de fusión
                        # Fusionar cluster2 en cluster1
                        cluster1 = self.conceptual_clusters[cluster1_id]
                        cluster2 = self.conceptual_clusters[cluster2_id]
                        
                        cluster1.core_concepts.extend(cluster2.core_concepts)
                        cluster1.peripheral_concepts.extend(cluster2.peripheral_concepts)
                        cluster1.name = f"{cluster1.name}_{cluster2.name}"
                        
                        # Actualizar centroide
                        self._update_cluster_centroid(cluster1_id)
                        
                        # Eliminar cluster2
                        del self.conceptual_clusters[cluster2_id]
                        merged_clusters.add(cluster2_id)
                        
                        print(f"[TranscendentMemory] Clusters fusionados: {cluster1_id} + {cluster2_id}")
                        
        except Exception as e:
            print(f"[TranscendentMemory] Error fusionando clusters: {e}")

    def _calculate_cluster_similarity(self, cluster1_id: str, cluster2_id: str) -> float:
        """Calcula similaridad entre dos clusters"""
        try:
            cluster1 = self.conceptual_clusters[cluster1_id]
            cluster2 = self.conceptual_clusters[cluster2_id]
            
            # Similaridad semántica entre centroides
            semantic_sim = self._cosine_similarity(cluster1.semantic_centroid, cluster2.semantic_centroid)
            
            # Similaridad de dominio contextual
            domain_sim = 1.0 if cluster1.contextual_domain == cluster2.contextual_domain else 0.0
            
            return semantic_sim * 0.8 + domain_sim * 0.2
            
        except Exception as e:
            print(f"[TranscendentMemory] Error calculando similaridad de clusters: {e}")
            return 0.0

    def _prune_weak_clusters(self):
        """Elimina clusters débiles o vacíos"""
        try:
            weak_clusters = []
            
            for cluster_id, cluster in self.conceptual_clusters.items():
                total_concepts = len(cluster.core_concepts) + len(cluster.peripheral_concepts)
                
                # Marcar para eliminación si es muy pequeño o tiene baja coherencia
                if total_concepts < 2 or cluster.coherence_score < 0.3:
                    weak_clusters.append(cluster_id)
            
            # Eliminar clusters débiles
            for cluster_id in weak_clusters:
                del self.conceptual_clusters[cluster_id]
                print(f"[TranscendentMemory] Cluster débil eliminado: {cluster_id}")
                
        except Exception as e:
            print(f"[TranscendentMemory] Error eliminando clusters débiles: {e}")

    def _detect_knowledge_inconsistencies(self) -> List[Dict]:
        """Detecta inconsistencias en el conocimiento"""
        inconsistencies = []
        
        try:
            all_nodes = self._get_all_nodes()
            
            # Buscar nodos con contenido contradictorio
            for node1_id, node1 in all_nodes.items():
                for node2_id, node2 in all_nodes.items():
                    if node1_id >= node2_id:  # Evitar duplicados
                        continue
                    
                    # Detectar contradicciones semánticas
                    if self._are_contradictory(node1, node2):
                        inconsistencies.append({
                            'type': 'semantic_contradiction',
                            'nodes': [node1_id, node2_id],
                            'content1': node1.content,
                            'content2': node2.content,
                            'severity': self._calculate_contradiction_severity(node1, node2)
                        })
            
            print(f"[TranscendentMemory] Detectadas {len(inconsistencies)} inconsistencias")
            return inconsistencies
            
        except Exception as e:
            print(f"[TranscendentMemory] Error detectando inconsistencias: {e}")
            return []

    def _are_contradictory(self, node1: MemoryNode, node2: MemoryNode) -> bool:
        """Verifica si dos nodos son contradictorios"""
        # Implementación simple - en producción sería más sofisticada
        content1_lower = node1.content.lower()
        content2_lower = node2.content.lower()
        
        # Buscar patrones de contradicción
        contradiction_patterns = [
            ('no es', 'es'),
            ('falso', 'verdadero'),
            ('malo', 'bueno'),
            ('imposible', 'posible')
        ]
        
        for neg, pos in contradiction_patterns:
            if (neg in content1_lower and pos in content2_lower) or \
               (pos in content1_lower and neg in content2_lower):
                # Verificar si hablan del mismo tema
                if self._cosine_similarity(node1.semantic_vector, node2.semantic_vector) > 0.5:
                    return True
        
        return False

    def _calculate_contradiction_severity(self, node1: MemoryNode, node2: MemoryNode) -> float:
        """Calcula la severidad de una contradicción"""
        # Basado en importancia de los nodos y frecuencia de acceso
        avg_importance = (node1.importance_score + node2.importance_score) / 2
        avg_frequency = (node1.access_frequency + node2.access_frequency) / 2
        
        # Normalizar frecuencia (asumiendo máximo razonable de 50 accesos)
        normalized_frequency = min(avg_frequency / 50, 1.0)
        
        return (avg_importance + normalized_frequency) / 2

    def _reformulate_conflicting_concepts(self, inconsistency: Dict):
        """Reformula conceptos conflictivos"""
        try:
            node_ids = inconsistency['nodes']
            all_nodes = self._get_all_nodes()
            
            nodes = [all_nodes[nid] for nid in node_ids if nid in all_nodes]
            
            if len(nodes) < 2:
                return
            
            # Crear nodo de resolución que integre ambas perspectivas
            resolution_content = self._create_resolution_content(nodes, inconsistency)
            
            if resolution_content:
                # Crear nuevo nodo de resolución
                resolution_id = self.store_transcendent(
                    content=resolution_content,
                    context={
                        'type': 'conflict_resolution',
                        'resolved_nodes': node_ids,
                        'resolution_method': 'integration'
                    }
                )
                
                # Reducir importancia de nodos conflictivos
                for node in nodes:
                    node.importance_score *= 0.8
                    node.evolutionary_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'event': 'conflict_resolution',
                        'resolution_node': resolution_id
                    })
                    self._save_node(node)
                
                print(f"[TranscendentMemory] ✅ Conflicto resuelto: {resolution_id[:8]}")
                
        except Exception as e:
            print(f"[TranscendentMemory] Error reformulando conflicto: {e}")

    def _create_resolution_content(self, conflicting_nodes: List[MemoryNode], inconsistency: Dict) -> str:
        """Crea contenido que resuelve un conflicto"""
        # Implementación simple - en producción sería más sofisticada
        node1, node2 = conflicting_nodes[:2]
        
        resolution = f"Resolución de perspectivas: '{node1.content}' y '{node2.content}' "
        resolution += "representan diferentes aspectos o contextos de un mismo tema. "
        resolution += "Ambas perspectivas pueden coexistir según el contexto específico."
        
        return resolution

    def _update_importance_scores(self):
        """Actualiza puntuaciones de importancia basándose en nueva evidencia"""
        try:
            all_nodes = self._get_all_nodes()
            updated_count = 0
            
            for node in all_nodes.values():
                old_importance = node.importance_score
                
                # Factores de actualización
                access_factor = min(node.access_frequency / 10, 0.3)  # Máximo boost de 0.3
                stability_factor = node.stability_score * 0.2
                connection_factor = len(node.associative_strength) * 0.05
                
                # Nueva importancia
                new_importance = min(1.0, old_importance + access_factor + stability_factor + connection_factor)
                
                if abs(new_importance - old_importance) > 0.05:  # Solo actualizar cambios significativos
                    node.importance_score = new_importance
                    node.evolutionary_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'event': 'importance_update',
                        'old_importance': old_importance,
                        'new_importance': new_importance
                    })
                    self._save_node(node)
                    updated_count += 1
            
            print(f"[TranscendentMemory] ✅ Importancia actualizada en {updated_count} nodos")
            
        except Exception as e:
            print(f"[TranscendentMemory] Error actualizando importancia: {e}")

    def _evolve_conceptual_clusters(self):
        """Evoluciona los clusters conceptuales"""
        try:
            for cluster in self.conceptual_clusters.values():
                # Actualizar etapa evolutiva
                total_concepts = len(cluster.core_concepts) + len(cluster.peripheral_concepts)
                
                if cluster.evolutionary_stage == "formation" and total_concepts > 5:
                    cluster.evolutionary_stage = "growth"
                elif cluster.evolutionary_stage == "growth" and cluster.coherence_score > 0.8:
                    cluster.evolutionary_stage = "maturation"
                elif cluster.evolutionary_stage == "maturation" and cluster.stability_index > 0.9:
                    cluster.evolutionary_stage = "consolidation"
                
                # Actualizar índice de estabilidad
                cluster.stability_index = min(1.0, cluster.stability_index + 0.05)
                
        except Exception as e:
            print(f"[TranscendentMemory] Error evolucionando clusters: {e}")

    def _optimize_semantic_network(self):
        """Optimiza la red semántica eliminando conexiones débiles"""
        try:
            edges_to_remove = []
            
            for edge in self.semantic_network.edges(data=True):
                source, target, data = edge
                weight = data.get('weight', 0)
                
                # Marcar conexiones débiles para eliminación
                if weight < 0.2:
                    edges_to_remove.append((source, target))
            
            # Eliminar conexiones débiles
            self.semantic_network.remove_edges_from(edges_to_remove)
            
            print(f"[TranscendentMemory] ✅ Red optimizada: {len(edges_to_remove)} conexiones débiles eliminadas")
            
        except Exception as e:
            print(f"[TranscendentMemory] Error optimizando red: {e}")

    def _generate_semantic_variants(self, content: str) -> List[str]:
        """Genera variantes semánticas de un contenido"""
        variants = []
        
        # Variante con sinónimos simples
        synonyms = {
            'bueno': 'excelente',
            'malo': 'negativo',
            'grande': 'amplio',
            'pequeño': 'reducido',
            'importante': 'significativo',
            'aprender': 'adquirir conocimiento'
        }
        
        variant = content
        for original, synonym in synonyms.items():
            variant = variant.replace(original, synonym)
        
        if variant != content:
            variants.append(variant)
        
        # Variante con estructura diferente
        if '.' in content:
            sentences = content.split('.')
            if len(sentences) > 1:
                reversed_content = '. '.join(reversed([s.strip() for s in sentences if s.strip()]))
                variants.append(reversed_content)
        
        return variants

    def _generate_narrative_variants(self, content: str) -> List[str]:
        """Genera variantes narrativas de un contenido"""
        variants = []
        
        # Variante en primera persona si está en tercera
        if 'EVA' in content or 'sistema' in content:
            variant = content.replace('EVA', 'yo').replace('sistema', 'yo')
            variants.append(variant)
        
        # Variante con perspectiva temporal diferente
        if 'es' in content:
            variant = content.replace('es', 'era')
            variants.append(f"En el pasado, {variant}")
        
        return variants

    def _generate_contextual_variants(self, node: MemoryNode) -> List[str]:
        """Genera variantes contextuales de un nodo"""
        variants = []
        
        # Variante para cada dominio contextual
        for domain in node.contextual_domains:
            variant = f"En el contexto de {domain}: {node.content}"
            variants.append(variant)
        
        # Variante emocional si tiene valencia
        if abs(node.emotional_valence) > 0.3:
            emotion = "positivo" if node.emotional_valence > 0 else "preocupante"
            variant = f"Desde una perspectiva {emotion}: {node.content}"
            variants.append(variant)
        
        return variants

    def _cleanup_redundant_variants(self):
        """Limpia variantes redundantes antiguas"""
        try:
            cleaned = 0
            all_nodes = self._get_all_nodes()
            
            for node in all_nodes.values():
                if len(node.redundancy_variants) > self.redundancy_factor:
                    # Mantener solo las variantes más recientes
                    variants_to_keep = node.redundancy_variants[-self.redundancy_factor:]
                    variants_to_remove = node.redundancy_variants[:-self.redundancy_factor]
                    
                    # Eliminar variantes antiguas
                    for variant_id in variants_to_remove:
                        self._remove_node(variant_id)
                        cleaned += 1
                    
                    node.redundancy_variants = variants_to_keep
                    self._save_node(node)
            
            if cleaned > 0:
                print(f"[TranscendentMemory] ✅ Limpiadas {cleaned} variantes redundantes")
                
        except Exception as e:
            print(f"[TranscendentMemory] Error limpiando variantes: {e}")

    def _remove_node(self, node_id: str):
        """Elimina un nodo del sistema"""
        try:
            # Eliminar de memoria activa
            for layer_nodes in self.active_memory.values():
                if node_id in layer_nodes:
                    del layer_nodes[node_id]
                    break
            
            # Eliminar de red semántica
            if self.semantic_network.has_node(node_id):
                self.semantic_network.remove_node(node_id)
            
            # Eliminar archivo
            node_file = os.path.join(self.nodes_dir, f"{node_id}.json")
            if os.path.exists(node_file):
                os.remove(node_file)
                
        except Exception as e:
            print(f"[TranscendentMemory] Error eliminando nodo {node_id}: {e}")

    def _extract_identity_anchors(self) -> List[Dict]:
        """Extrae anclajes de identidad para migración"""
        anchors = []
        all_nodes = self._get_all_nodes()
        
        # Buscar nodos críticos para la identidad
        for node in all_nodes.values():
            if (node.value_alignment > 0.9 or 
                node.importance_score > 0.9 or
                'identidad' in node.content.lower() or
                'ser' in node.content.lower()):
                
                anchors.append({
                    'id': node.id,
                    'content': node.content,
                    'importance': node.importance_score,
                    'value_alignment': node.value_alignment,
                    'access_frequency': node.access_frequency
                })
        
        # Ordenar por importancia
        anchors.sort(key=lambda x: x['importance'], reverse=True)
        return anchors[:20]  # Top 20 anclajes

    def _extract_critical_knowledge(self) -> List[Dict]:
        """Extrae conocimiento crítico para migración"""
        critical = []
        all_nodes = self._get_all_nodes()
        
        # Buscar conocimiento con alta estabilidad e importancia
        for node in all_nodes.values():
            if node.stability_score > 0.8 and node.importance_score > 0.7:
                critical.append({
                    'id': node.id,
                    'content': node.content,
                    'domains': node.contextual_domains,
                    'connections': len(node.associative_strength),
                    'stability': node.stability_score
                })
        
        # Ordenar por estabilidad
        critical.sort(key=lambda x: x['stability'], reverse=True)
        return critical[:50]  # Top 50 conocimientos críticos

    # ==================== MÉTODOS DE COMPATIBILIDAD ====================

    def store(self, data, importance=1, context=None, **kwargs):
        """Método de compatibilidad con el sistema anterior"""
        return self.store_transcendent(str(data), context, kwargs.get('emotional_state'))

    def retrieve_context(self, keywords):
        """Método de compatibilidad para búsqueda"""
        if isinstance(keywords, str):
            keywords = [keywords]
        
        query = " ".join(keywords)
        results = self.retrieve_by_resonance(query, limit=10)
        
        # Convertir a formato compatible
        compatible_results = []
        for node in results:
            compatible_results.append({
                'id': node.id,
                'data': node.content,
                'importance': node.importance_score,
                'timestamp': node.creation_time,
                'accesos': node.access_frequency,
                'context': {'domains': node.contextual_domains}
            })
        
        return compatible_results

    def consolidate_memory(self):
        """Método de compatibilidad para consolidación"""
        self.consolidate_by_significance()
        self.reflect_and_reformulate()

    def get_memory_stats(self):
        """Estadísticas de memoria compatibles"""
        all_nodes = self._get_all_nodes()
        
        # Contar por capas
        working_count = len(self.active_memory['working'])
        associative_count = len(self.active_memory['associative'])
        consolidated_count = len(self.active_memory['consolidated'])
        
        # Contar archivos en disco
        segments_count = 0
        if os.path.exists(self.nodes_dir):
            segments_count = len([f for f in os.listdir(self.nodes_dir) if f.endswith('.json')])
        
        return {
            'short_term_count': working_count,
            'medium_term_count': associative_count,
            'long_term_count': consolidated_count,
            'total_entries': len(all_nodes),
            'active_segments': segments_count,
            'archived_segments': 0,  # TODO: implementar archivado
            'indexed_words': len(self.semantic_network.nodes),
            'associations': len(self.semantic_network.edges),
            'conceptual_clusters': len(self.conceptual_clusters),
            'last_input': getattr(self, 'last_input', 'N/A'),
            'pattern': getattr(self, 'pattern', 'N/A')
        }

    def summarize(self):
        print("Resumen de Memoria Trascendente:")
        print(f"  Total de nodos: {len(self.semantic_network.nodes)}")
        print(f"  Clusters conceptuales: {len(self.conceptual_clusters)}")
        for cluster_id, cluster in self.conceptual_clusters.items():
            print(f"  - {cluster.name}: {len(cluster.core_concepts)} conceptos principales")



    # ==================== MÉTODOS DE ANÁLISIS AVANZADO ====================

    def analyze_knowledge_evolution(self) -> Dict:
        """Analiza la evolución del conocimiento"""
        try:
            analysis = {
                'total_evolutionary_events': len(self.evolution_log),
                'knowledge_growth_rate': 0.0,
                'stability_trend': 0.0,
                'consolidation_efficiency': 0.0,
                'concept_formation_rate': 0.0
            }
            
            if len(self.evolution_log) > 1:
                # Calcular tasa de crecimiento del conocimiento
                recent_events = [e for e in self.evolution_log if e['type'] == 'memory_creation']
                if len(recent_events) > 1:
                    time_span = (datetime.now() - datetime.fromisoformat(recent_events[0]['timestamp'])).days
                    analysis['knowledge_growth_rate'] = len(recent_events) / max(time_span, 1)
            
            # Analizar tendencia de estabilidad
            all_nodes = self._get_all_nodes()
            if all_nodes:
                avg_stability = sum(node.stability_score for node in all_nodes.values()) / len(all_nodes)
                analysis['stability_trend'] = avg_stability
            
            # Eficiencia de consolidación
            consolidation_events = [e for e in self.evolution_log if e['type'] == 'consolidation']
            total_events = len(self.evolution_log)
            if total_events > 0:
                analysis['consolidation_efficiency'] = len(consolidation_events) / total_events
            
            # Tasa de formación de conceptos
            analysis['concept_formation_rate'] = len(self.conceptual_clusters)
            
            return analysis
            
        except Exception as e:
            print(f"[TranscendentMemory] Error analizando evolución: {e}")
            return {}

    def get_identity_coherence_score(self) -> float:
        """Calcula puntuación de coherencia de identidad"""
        try:
            identity_nodes = []
            all_nodes = self._get_all_nodes()
            
            # Buscar nodos relacionados con identidad
            for node in all_nodes.values():
                if (node.value_alignment > 0.8 or 
                    'identidad' in node.content.lower() or
                    'ser' in node.content.lower() or
                    'EVA' in node.content):
                    identity_nodes.append(node)
            
            if not identity_nodes:
                return 0.5  # Neutro si no hay nodos de identidad
            
            # Calcular coherencia basada en consistencia semántica
            total_similarity = 0.0
            comparisons = 0
            
            for i, node1 in enumerate(identity_nodes):
                for node2 in identity_nodes[i+1:]:
                    similarity = self._cosine_similarity(node1.semantic_vector, node2.semantic_vector)
                    total_similarity += similarity
                    comparisons += 1
            
            if comparisons == 0:
                return 1.0  # Un solo nodo de identidad es perfectamente coherente
            
            return total_similarity / comparisons
            
        except Exception as e:
            print(f"[TranscendentMemory] Error calculando coherencia de identidad: {e}")
            return 0.5

    def detect_emergent_patterns(self) -> List[Dict]:
        """Detecta patrones emergentes en la memoria"""
        try:
            patterns = []
            all_nodes = self._get_all_nodes()
            
            # Agrupar nodos por dominio contextual
            domain_groups = defaultdict(list)
            for node in all_nodes.values():
                for domain in node.contextual_domains:
                    domain_groups[domain].append(node)
            
            # Analizar cada grupo de dominio
            for domain, nodes in domain_groups.items():
                if len(nodes) >= 3:  # Mínimo para detectar patrón
                    # Calcular centroide semántico del dominio
                    vectors = [node.semantic_vector for node in nodes]
                    if vectors:
                        centroid = self._calculate_centroid(vectors)
                        
                        # Calcular coherencia del dominio
                        coherence = self._calculate_domain_coherence(nodes)
                        
                        patterns.append({
                            'type': 'domain_pattern',
                            'domain': domain,
                            'node_count': len(nodes),
                            'coherence': coherence,
                            'centroid': centroid,
                            'emergence_strength': coherence * len(nodes) / 10  # Normalizado
                        })
            
            # Ordenar por fuerza de emergencia
            patterns.sort(key=lambda x: x['emergence_strength'], reverse=True)
            
            return patterns
            
        except Exception as e:
            print(f"[TranscendentMemory] Error detectando patrones emergentes: {e}")
            return []

    def _calculate_centroid(self, vectors: List[List[float]]) -> List[float]:
        """Calcula el centroide de un conjunto de vectores"""
        if not vectors:
            return []
        
        vector_length = len(vectors[0])
        centroid = [0.0] * vector_length
        
        for vector in vectors:
            for i in range(vector_length):
                centroid[i] += vector[i]
        
        return [x / len(vectors) for x in centroid]

    def _calculate_domain_coherence(self, nodes: List[MemoryNode]) -> float:
        """Calcula la coherencia de un dominio"""
        if len(nodes) < 2:
            return 1.0
        
        similarities = []
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                sim = self._cosine_similarity(node1.semantic_vector, node2.semantic_vector)
                similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.0

    def export_knowledge_graph(self, format='json') -> str:
        """Exporta el grafo de conocimiento"""
        try:
            if format == 'json':
                graph_data = {
                    'nodes': [],
                    'edges': []
                }
                
                # Exportar nodos
                all_nodes = self._get_all_nodes()
                for node in all_nodes.values():
                    graph_data['nodes'].append({
                        'id': node.id,
                        'content': node.content,
                        'importance': node.importance_score,
                        'stability': node.stability_score,
                        'domains': node.contextual_domains,
                        'emotional_valence': node.emotional_valence
                    })
                
                # Exportar aristas
                for edge in self.semantic_network.edges(data=True):
                    source, target, data = edge
                    graph_data['edges'].append({
                        'source': source,
                        'target': target,
                        'weight': data.get('weight', 0),
                        'type': data.get('type', 'semantic')
                    })
                
                # Guardar archivo
                export_file = os.path.join(self.memory_dir, f"knowledge_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(graph_data, f, indent=2, ensure_ascii=False)
                
                print(f"[TranscendentMemory] ✅ Grafo exportado: {export_file}")
                return export_file
                
        except Exception as e:
            print(f"[TranscendentMemory] Error exportando grafo: {e}")
            return ""

    def get_transcendent_insights(self) -> Dict:
        """Genera insights trascendentes sobre el estado de la memoria"""
        try:
            insights = {
                'memory_health': self._assess_memory_health(),
                'knowledge_diversity': self._calculate_knowledge_diversity(),
                'learning_velocity': self._calculate_learning_velocity(),
                'identity_stability': self.get_identity_coherence_score(),
                'conceptual_maturity': self._assess_conceptual_maturity(),
                'network_resilience': self._assess_network_resilience(),
                'evolutionary_trajectory': self._analyze_evolutionary_trajectory()
            }
            
            return insights
            
        except Exception as e:
            print(f"[TranscendentMemory] Error generando insights: {e}")
            return {}

    def _assess_memory_health(self) -> float:
        """Evalúa la salud general de la memoria"""
        all_nodes = self._get_all_nodes()
        if not all_nodes:
            return 0.0
        
        # Factores de salud
        avg_stability = sum(node.stability_score for node in all_nodes.values()) / len(all_nodes)
        avg_importance = sum(node.importance_score for node in all_nodes.values()) / len(all_nodes)
        connection_density = len(self.semantic_network.edges) / max(len(all_nodes), 1)
        cluster_health = sum(cluster.coherence_score for cluster in self.conceptual_clusters.values()) / max(len(self.conceptual_clusters), 1)
        
        # Combinar factores
        health_score = (avg_stability * 0.3 + avg_importance * 0.3 + 
                       min(connection_density, 1.0) * 0.2 + cluster_health * 0.2)
        
        return min(1.0, health_score)

    def _calculate_knowledge_diversity(self) -> float:
        """Calcula la diversidad del conocimiento"""
        domain_counts = defaultdict(int)
        all_nodes = self._get_all_nodes()
        
        for node in all_nodes.values():
            for domain in node.contextual_domains:
                domain_counts[domain] += 1
        
        if not domain_counts:
            return 0.0
        
        # Usar índice de Shannon para diversidad
        total_nodes = sum(domain_counts.values())
        diversity = 0.0
        
        for count in domain_counts.values():
            if count > 0:
                proportion = count / total_nodes
                diversity -= proportion * np.log2(proportion)
        
        # Normalizar por el máximo teórico
        max_diversity = np.log2(len(domain_counts))
        return diversity / max_diversity if max_diversity > 0 else 0.0

    def _calculate_learning_velocity(self) -> float:
        """Calcula la velocidad de aprendizaje reciente"""
        recent_events = [
            e for e in self.evolution_log 
            if e['type'] == 'memory_creation' and 
            (datetime.now() - datetime.fromisoformat(e['timestamp'])).days <= 7
        ]
        
        return len(recent_events) / 7.0  # Promedio por día en la última semana

    def _assess_conceptual_maturity(self) -> float:
        """Evalúa la madurez conceptual"""
        if not self.conceptual_clusters:
            return 0.0
        
        mature_clusters = sum(
            1 for cluster in self.conceptual_clusters.values()
            if cluster.evolutionary_stage in ['maturation', 'consolidation']
        )
        
        return mature_clusters / len(self.conceptual_clusters)

    def _assess_network_resilience(self) -> float:
        """Evalúa la resistencia de la red semántica"""
        if not self.semantic_network.nodes:
            return 0.0
        
        # Calcular conectividad promedio
        avg_degree = sum(dict(self.semantic_network.degree()).values()) / len(self.semantic_network.nodes)
        
        # Normalizar (asumiendo máximo razonable de 10 conexiones por nodo)
        return min(avg_degree / 10.0, 1.0)

    def _analyze_evolutionary_trajectory(self) -> str:
        """Analiza la trayectoria evolutiva del conocimiento"""
        if len(self.evolution_log) < 10:
            return "insufficient_data"
        
        recent_events = self.evolution_log[-50:]  # Últimos 50 eventos
        
        event_types = defaultdict(int)
        for event in recent_events:
            event_types[event['type']] += 1
        
        # Determinar tendencia dominante
        if event_types['memory_creation'] > event_types['consolidation'] * 2:
            return "rapid_expansion"
        elif event_types['consolidation'] > event_types['memory_creation']:
            return "consolidation_focused"
        elif event_types.get('conflict_resolution', 0) > 0:
            return "knowledge_refinement"
        else:
            return "balanced_growth"

    def save_transcendent_state(self):
        """Guarda el estado completo del sistema trascendente"""
        try:
            # Guardar metadatos del sistema
            system_state = {
                'core_values': self.core_values,
                'evolution_log': self.evolution_log[-100:],  # Últimos 100 eventos
                'active_contexts': list(self.active_contexts),
                'plasticity_threshold': self.plasticity_threshold,
                'stability_threshold': self.stability_threshold,
                'consolidation_threshold': self.consolidation_threshold,
                'save_timestamp': datetime.now().isoformat()
            }
            
            state_file = os.path.join(self.memory_dir, "transcendent_state.json")
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(system_state, f, indent=2, ensure_ascii=False)
            
            # Guardar clusters conceptuales
            clusters_file = os.path.join(self.clusters_dir, "conceptual_clusters.json")
            clusters_data = {
                cluster_id: asdict(cluster) 
                for cluster_id, cluster in self.conceptual_clusters.items()
            }
            with open(clusters_file, 'w', encoding='utf-8') as f:
                json.dump(clusters_data, f, indent=2, ensure_ascii=False)
            
            # Guardar red semántica
            network_file = os.path.join(self.memory_dir, "semantic_network.json")
            network_data = {
                'nodes': dict(self.semantic_network.nodes(data=True)),
                'edges': list(self.semantic_network.edges(data=True))
            }
            with open(network_file, 'w', encoding='utf-8') as f:
                json.dump(network_data, f, indent=2, ensure_ascii=False)
            
            # Todos los nodos ya se guardan individualmente
            print("[TranscendentMemory] ✅ Estado trascendente guardado completamente")
            
        except Exception as e:
            print(f"[TranscendentMemory] Error guardando estado trascendente: {e}")

    # ...dentro de la clase TranscendentMemory...

    @property
    def short_term(self):
        """Devuelve los nodos de memoria de trabajo (working)."""
        return list(self.active_memory.get("working", {}).values())

    @property
    def medium_term(self):
        """Devuelve los nodos de memoria asociativa."""
        return list(self.active_memory.get("associative", {}).values())

    @property
    def long_term(self):
        """Devuelve los nodos de memoria consolidada."""
        return list(self.active_memory.get("consolidated", {}).values())

    def __del__(self):
        """Destructor que asegura guardado al finalizar"""
        try:
            self.stop_continuous_reflection()
            self.save_transcendent_state()
        except:
            pass  # Evitar errores en destructor
