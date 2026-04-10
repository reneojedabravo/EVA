#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
background_thinking.py - Bucle de Pensamiento Continuo Mejorado para EVA

Este módulo implementa un sistema de pensamiento en segundo plano que:
1. Analiza asociaciones léxicas continuamente
2. Ejecuta reflexiones internas automáticas
3. Consolida memoria cuando es necesario
4. Evoluciona emocionalmente de forma autónoma
5. Mantiene la coherencia interna del sistema
6. EVITA BUCLES COGNITIVOS mediante diversidad forzada
7. Aplica fatiga cognitiva y períodos de descanso
8. Se adapta al nuevo sistema de memoria trascendente

Todo funciona silenciosamente sin interferir con la interacción del usuario.
"""

import threading
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict, deque
import hashlib
from reflection_diary import StimulusType

class BackgroundThinker:
    """
    Sistema de pensamiento continuo que opera en segundo plano.
    Gestiona los procesos cognitivos automáticos de EVA con prevención de bucles.
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.is_running = False
        self.thread = None

        # Al inicio del __init__ agrega:
        self.last_concept_building = time.time()
        
        # Contadores para controlar frecuencia
        self.cycle_count = 0
        self.last_consolidation = time.time()
        self.last_reflection = time.time()
        self.last_emotional_update = time.time()
        self.last_diary_maintenance = time.time()
        
        # Configuración de intervalos (en segundos)
        self.intervals = {
            'reflection_quick': 45,      # Reflexiones rápidas cada 45s
            'reflection_deep': 180,      # Reflexiones profundas cada 3min
            'consolidation': 300,        # Consolidación cada 5min
            'emotional_drift': 60,       # Deriva emocional cada 1min
            'diary_maintenance': 600,    # Mantenimiento diario cada 10min
            'association_analysis': 30,   # Análisis de asociaciones cada 30s
            'imagination_cycle': 120,        # Ciclos de imaginación cada 2min
            'imagination_maintenance': 600,  # Mantenimiento cada 10min
            'concept_building': 600,      # Cada 10 minutos
            'cognitive_entropy': 2500,    # Inyección de entropía cada ~42min
            'cognitive_rest': 12000      # Descanso cognitivo cada ~3.3 horas
        }

        # Estado interno del pensamiento
        self.thinking_momentum = 0.5  # Momento de pensamiento actual
        self.curiosity_buildup = 0.0  # Acumulación de curiosidad
        self.last_associations = []   # Últimas asociaciones analizadas
        
        # === NUEVOS SISTEMAS ANTI-BUCLES ===
        # Historia de reflexiones para detectar bucles
        self.reflection_history = deque(maxlen=20)  # Últimas 20 reflexiones
        
        # Sistema de fatiga cognitiva
        self.concept_fatigue = defaultdict(int)
        self.fatigued_concepts = set()
        self.fatigue_decay_cycle = 0
        
        # Tracking de diversidad
        self.domain_exploration = defaultdict(int)
        self.recent_topics = deque(maxlen=15)
        
        # Estado de entropía cognitiva
        self.entropy_level = 0.5
        self.last_entropy_injection = time.time()
        self.last_cognitive_rest = time.time()
        
        # Semillas para exploración forzada
        self.exploration_seeds = [
            "curiosidad", "creatividad", "aprendizaje", "reflexión",
            "análisis", "síntesis", "conexión", "patrón", "emergencia",
            "evolución", "adaptación", "resonancia", "coherencia"
        ]
        
        print("[BackgroundThinker] Sistema de pensamiento continuo mejorado inicializado")
        print("[BackgroundThinker] Sistemas anti-bucles activos: fatiga cognitiva, entropía, diversidad forzada")

    def start(self):
        """Inicia el bucle de pensamiento en segundo plano."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._thinking_loop, daemon=True)
            self.thread.start()
            print("[BackgroundThinker] ✅ Bucle de pensamiento mejorado iniciado")
            # Iniciar procesamiento cognitivo continuo si está disponible
            if hasattr(self.brain, 'cognitive_reflection') and self.brain.cognitive_reflection:
                try:
                    self.brain.cognitive_reflection.start_continuous_processing()
                except Exception:
                    pass

    def stop(self):
        """Detiene el bucle de pensamiento."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("[BackgroundThinker] 🛑 Bucle de pensamiento detenido")
        # Detener procesamiento cognitivo continuo
        if hasattr(self.brain, 'cognitive_reflection') and self.brain.cognitive_reflection:
            try:
                self.brain.cognitive_reflection.stop_continuous_processing()
            except Exception:
                pass

    def _thinking_loop(self):
        """
        Bucle principal de pensamiento que opera continuamente.
        Ejecuta diferentes procesos cognitivos según necesidad y tiempo.
        """
        while self.is_running and self.brain.is_active:
            try:
                current_time = time.time()
                self.cycle_count += 1
                
                # === SISTEMAS ANTI-BUCLES PRINCIPALES ===
                # 1. Detección y ruptura de bucles cognitivos
                if self.cycle_count % 10 == 0:  # Cada 10 ciclos
                    if self._detect_cognitive_loop():
                        self._break_cognitive_loop()
                        print("[BackgroundThinker] 🔄 Bucle cognitivo detectado y roto")
                
                # 2. Inyección de entropía cognitiva
                if current_time - self.last_entropy_injection > self.intervals['cognitive_entropy']:
                    self._inject_cognitive_entropy()
                    self.last_entropy_injection = current_time
                
                # 3. Descanso cognitivo periódico
                if current_time - self.last_cognitive_rest > self.intervals['cognitive_rest']:
                    self._cognitive_rest_cycle()
                    self.last_cognitive_rest = current_time
                
                # 4. Decaimiento de fatiga cognitiva
                if self.cycle_count % 25 == 0:  # Cada 25 ciclos
                    self._decay_cognitive_fatigue()
                
                # === PROCESOS COGNITIVOS NORMALES ===
                # 1. Análisis de asociaciones (cada 30s)
                if current_time - getattr(self, 'last_association_analysis', 0) > self.intervals['association_analysis']:
                    self._analyze_associations()
                    self.last_association_analysis = current_time
                
                # 2. Reflexiones rápidas (cada 45s)
                if current_time - self.last_reflection > self.intervals['reflection_quick']:
                    self._quick_reflection()
                    self.last_reflection = current_time
                
                # 3. Reflexiones profundas (cada 3min, basadas en estado)
                if current_time - getattr(self, 'last_deep_reflection', 0) > self.intervals['reflection_deep']:
                    if self._should_deep_reflect():
                        self._deep_reflection()
                        self.last_deep_reflection = current_time
                
                # 4. Consolidación inteligente (cada 5min o por triggers)
                if self._should_consolidate(current_time):
                    self._intelligent_consolidation()
                    self.last_consolidation = current_time
                
                # 5. Deriva emocional natural (cada 1min)
                if current_time - self.last_emotional_update > self.intervals['emotional_drift']:
                    self._emotional_drift()
                    self.last_emotional_update = current_time
                
                # 6. Mantenimiento del diario (cada 10min)
                if current_time - self.last_diary_maintenance > self.intervals['diary_maintenance']:
                    self._maintain_diary()
                    self.last_diary_maintenance = current_time

                # 7. Ciclo de imaginación (cada 2min si está activo)
                if (current_time - getattr(self, 'last_imagination_cycle', 0) > 
                    self.intervals['imagination_cycle']):
                    if hasattr(self.brain, 'imagination_engine') and self.brain.imagination_engine.active:
                        self._run_imagination_cycle()
                        self.last_imagination_cycle = current_time

                # 8. Mantenimiento del sistema de imaginación (cada 10min)
                if (current_time - getattr(self, 'last_imagination_maintenance', 0) > 
                    self.intervals['imagination_maintenance']):
                    if hasattr(self.brain, 'imagination_engine'):
                        self._maintain_imagination_system()
                        self.last_imagination_maintenance = current_time
                
                # 9. Auto-evaluación periódica (cada 20 ciclos)
                if self.cycle_count % 20 == 0:
                    self._self_evaluation()

                # 10. Construcción de conceptos (cada 10 minutos)
                if (current_time - getattr(self, 'last_concept_building', 0) > self.intervals['concept_building']):
                    if hasattr(self.brain, 'concept_builder') and self.brain.concept_builder:
                        try:
                            new_concepts = self.brain.concept_builder.run_cycle()
                            if new_concepts:
                                count = len(new_concepts)
                                names = [c["name"] for c in new_concepts]
                                print(f"[ConceptBuilder] {count} concepto(s) creado(s): {names}")
                        except Exception as e:
                            print(f"[ConceptBuilder] Error en run_cycle: {e}")
                    self.last_concept_building = current_time
                
                # 11. Inyección de novedad aleatoria
                if random.random() < 0.05:  # 5% de probabilidad por ciclo
                    self._inject_novelty()
                
                # Pausa adaptativa basada en carga cognitiva y entropía
                sleep_time = self._calculate_sleep_time()
                time.sleep(sleep_time)
                
            except Exception as e:
                # Fallar silenciosamente para no interrumpir
                continue

    def _analyze_associations(self):
        """
        Analiza las asociaciones léxicas actuales y detecta patrones emergentes.
        Adaptado al sistema de memoria trascendente.
        """
        try:
            if not self.brain.learning_system:
                return
                
            # Obtener asociaciones actuales
            current_assoc = self.brain.learning_system.get_strong_associations()
            
            # Detectar nuevas asociaciones emergentes
            new_associations = [a for a in current_assoc if a not in self.last_associations]
            lost_associations = [a for a in self.last_associations if a not in current_assoc]
            
            # === PREVENCIÓN DE BUCLES ===
            # Verificar si las nuevas asociaciones son repetitivas
            if new_associations:
                association_hash = self._hash_associations(new_associations)
                if association_hash not in self.recent_topics:
                    # Incrementar curiosidad solo si es diverso
                    self.curiosity_buildup += 0.08 * len(new_associations)
                    self.recent_topics.append(association_hash)
                    
                    # Si hay muchas asociaciones nuevas Y diversas, programar reflexión
                    if len(new_associations) >= 3:
                        self.thinking_momentum += 0.15  # Reducido de 0.2
                else:
                    # Aplicar fatiga cognitiva a asociaciones repetitivas
                    for assoc in new_associations:
                        self._apply_cognitive_fatigue(str(assoc))
            
            # Actualizar estado
            self.last_associations = current_assoc
            
            # Actualizar estado emocional si hay cambios dramáticos y diversos
            if len(new_associations) >= 2 or len(lost_associations) >= 3:
                self._trigger_emotional_response("learning_shift")
                
        except Exception:
            pass  # Fallar silenciosamente

    def _quick_reflection(self):
        """
        Ejecuta una reflexión rápida basada en el estado actual.
        Adaptado al sistema de memoria trascendente.
        """
        try:
            # Verificar si hay suficiente contenido mental en memoria trascendente
            total_nodes = len(self.brain.memory._get_all_nodes()) if hasattr(self.brain.memory, '_get_all_nodes') else 0
            working_nodes = len(self.brain.memory.active_memory.get('working', {})) if hasattr(self.brain.memory, 'active_memory') else 0
            
            if total_nodes < 3 or working_nodes == 0:
                return
                
            # Verificar si no está en fatiga cognitiva extrema
            if len(self.fatigued_concepts) > 10:
                print("[BackgroundThinker] ⚡ Saltando reflexión por fatiga cognitiva extrema")
                return
            
            # Reflexión ligera con prioridad baja
            priority = 1 if self.thinking_momentum < 0.7 else 2
            
            # Incluir curiosidad acumulada en la reflexión (con límite)
            if self.curiosity_buildup > 0.3:
                priority += 1
                self.curiosity_buildup *= 0.7  # Reducir después de usar
            
            # Forzar diversidad si hay poca entropía
            if self.entropy_level < 0.3:
                priority += 1  # Reflexión más intensa para generar diversidad
            
            reflection = self.brain.internal_reflection(priority=priority)

            # Disparar un ciclo cognitivo ligero (oportunidad de aprendizaje)
            if hasattr(self.brain, 'cognitive_reflection') and self.brain.cognitive_reflection:
                try:
                    self.brain.cognitive_reflection.perceive_and_initiate_cycle(
                        content=f"Reflexión rápida: {datetime.now().isoformat()}",
                        stimulus_type=StimulusType.LEARNING_OPPORTUNITY,
                        source="background_quick"
                    )
                except Exception:
                    pass
            
            # Registrar reflexión para detección de bucles
            reflection_hash = self._hash_reflection(reflection)
            self.reflection_history.append(reflection_hash)
            
            # Ajustar momentum con decaimiento más agresivo
            self.thinking_momentum = max(0.3, self.thinking_momentum * 0.85)
            
            # Actualizar nivel de entropía basado en la diversidad de la reflexión
            self._update_entropy_level(reflection)
            
        except Exception:
            pass

    def _deep_reflection(self):
        """
        Ejecuta una reflexión profunda con análisis de patrones.
        Adaptado al sistema de memoria trascendente.
        """
        try:
            # Verificar que no esté en un patrón repetitivo
            if self._is_stuck_in_pattern():
                print("[BackgroundThinker] 🧠 Saltando reflexión profunda por patrón repetitivo")
                self._force_diverse_reflection()
                return
                
            # Reflexión con alta prioridad
            reflection = self.brain.internal_reflection(priority=3)

            # Disparar un ciclo cognitivo profundo (decisión/incertidumbre)
            if hasattr(self.brain, 'cognitive_reflection') and self.brain.cognitive_reflection:
                try:
                    self.brain.cognitive_reflection.perceive_and_initiate_cycle(
                        content=f"Reflexión profunda: {datetime.now().isoformat()}",
                        stimulus_type=StimulusType.DECISION_REQUIRED,
                        source="background_deep"
                    )
                except Exception:
                    pass
            
            # Registrar reflexión
            reflection_hash = self._hash_reflection(reflection)
            self.reflection_history.append(reflection_hash)
            
            # Analizar patrones en la reflexión
            focus_signals = reflection.get("focus_signals", [])
            
            # Si hay patrones interesantes Y diversos, incrementar momentum
            if len(focus_signals) > 3:
                signal_diversity = len(set(focus_signals))
                if signal_diversity >= len(focus_signals) * 0.7:  # Al menos 70% de diversidad
                    self.thinking_momentum += 0.25  # Reducido de 0.3
                    
                    # Posible insight emergente
                    self._trigger_emotional_response("insight")
                    self._boost_entropy_level(0.1)
            
            # Reducir curiosidad después de reflexión profunda
            self.curiosity_buildup *= 0.4  # Más agresivo
            
        except Exception:
            pass

    def _should_deep_reflect(self):
        """
        Determina si es momento para una reflexión profunda.
        Adaptado al sistema de memoria trascendente con anti-bucles.
        """
        try:
            # Si está en bucle cognitivo, no hacer reflexión profunda
            if self._detect_cognitive_loop():
                return False
                
            # Factores que favorecen reflexión profunda
            factors = 0
            
            # 1. Alto momentum de pensamiento (pero no extremo)
            if 0.6 < self.thinking_momentum < 0.9:  # Ventana óptima
                factors += 2
                
            # 2. Muchas asociaciones fuertes Y diversas
            if len(self.last_associations) > 5:
                unique_associations = len(set(str(a) for a in self.last_associations))
                if unique_associations >= len(self.last_associations) * 0.8:
                    factors += 1
                    
            # 3. Estado emocional reactivo
            if self.brain.adaptive_core:
                emo_label = self.brain.adaptive_core.emotional_state.label()
                if emo_label in ["inquisitive", "creative", "empathetic"]:
                    factors += 1
                    
            # 4. Memoria activa (adaptado a memoria trascendente)
            total_active = 0
            if hasattr(self.brain.memory, 'active_memory'):
                total_active = sum(len(layer) for layer in self.brain.memory.active_memory.values())
            if total_active > 25:
                factors += 1
                
            # 5. Curiosidad acumulada alta (pero no extrema)
            if 0.4 < self.curiosity_buildup < 0.8:
                factors += 1
                
            # 6. NUEVO: Nivel de entropía adecuado
            if self.entropy_level > 0.4:
                factors += 1
            
            # 7. NUEVO: No muchos conceptos fatigados
            if len(self.fatigued_concepts) < 5:
                factors += 1
            
            return factors >= 3
            
        except Exception:
            return False

    def _should_consolidate(self, current_time):
        """
        Determina si es necesario consolidar memoria.
        Adaptado al sistema de memoria trascendente.
        """
        try:
            # Tiempo mínimo transcurrido
            if current_time - self.last_consolidation < self.intervals['consolidation']:
                return False
                
            # Factores que favorecen consolidación
            factors = 0
            
            if hasattr(self.brain.memory, 'active_memory'):
                # 1. Memoria de trabajo muy llena
                working_count = len(self.brain.memory.active_memory.get('working', {}))
                if working_count > 30:
                    factors += 2
                    
                # 2. Muchas entradas importantes en memoria asociativa
                associative_nodes = self.brain.memory.active_memory.get('associative', {})
                important_nodes = [
                    node for node in associative_nodes.values()
                    if getattr(node, 'importance_score', 0) >= 0.7 or getattr(node, 'access_frequency', 0) >= 3
                ]
                if len(important_nodes) > 10:
                    factors += 1
                    
            # 3. Asociaciones estables (no han cambiado mucho)
            if len(self.last_associations) > 3 and self.thinking_momentum < 0.6:
                factors += 1
                
            # 4. NUEVO: Entropía baja (sistema estable, buen momento para consolidar)
            if self.entropy_level < 0.4:
                factors += 1
                
            return factors >= 2
            
        except Exception:
            return False

    def _intelligent_consolidation(self):
        """
        Ejecuta consolidación de memoria de forma inteligente.
        Adaptado al sistema de memoria trascendente.
        """
        try:
            # Consolidar usando el sistema trascendente
            if hasattr(self.brain.memory, 'consolidate_by_significance'):
                self.brain.memory.consolidate_by_significance()
            elif hasattr(self.brain.memory, 'consolidate_memory'):
                # Fallback al método original
                self.brain.memory.consolidate_memory()
            
            # Trigger emocional y ajuste de momentum
            self._trigger_emotional_response("consolidation")
            self.thinking_momentum *= 0.8
            
            # Reducir fatiga de conceptos consolidados
            self._reduce_consolidation_fatigue()
            
        except Exception:
            pass

    # === NUEVOS MÉTODOS ANTI-BUCLES ===

    def _detect_cognitive_loop(self):
        """Detecta si está en un bucle de pensamiento repetitivo"""
        if len(self.reflection_history) < 6:
            return False
            
        # Analizar diversidad en las últimas reflexiones
        recent_reflections = list(self.reflection_history)[-8:]
        unique_reflections = len(set(recent_reflections))
        
        # Si hay poca diversidad (menos del 60%), es un bucle
        diversity_ratio = unique_reflections / len(recent_reflections)
        
        return diversity_ratio < 0.6

    def _break_cognitive_loop(self):
        """Rompe bucles cognitivos forzando diversidad"""
        print("[BackgroundThinker] 💥 Rompiendo bucle cognitivo...")
        
        # Reset parcial del estado cognitivo
        self.thinking_momentum *= 0.3
        self.curiosity_buildup = min(0.2, self.curiosity_buildup * 0.5)
        
        # Limpiar conceptos fatigados más antiguos
        self.fatigued_concepts.clear()
        self.concept_fatigue.clear()
        
        # Forzar reflexión diversa
        self._force_diverse_reflection()
        
        # Inyectar alta entropía
        self._boost_entropy_level(0.3)
        
        # Limpiar historia reciente para empezar fresco
        self.reflection_history.clear()
        self.recent_topics.clear()

    def _apply_cognitive_fatigue(self, concept_id):
        """Aplica fatiga a conceptos sobrepensados"""
        if isinstance(concept_id, (list, tuple)):
            concept_id = str(concept_id)
            
        self.concept_fatigue[concept_id] = self.concept_fatigue.get(concept_id, 0) + 1
        
        # Reducir relevancia de conceptos fatigados
        if self.concept_fatigue[concept_id] > 5:
            self.fatigued_concepts.add(concept_id)
            
            # Si hay demasiados conceptos fatigados, forzar diversidad
            if len(self.fatigued_concepts) > 8:
                self._inject_cognitive_entropy()

    def _inject_novelty(self):
        """Introduce elementos de novedad periódicamente"""
        print("[BackgroundThinker] ✨ Inyectando novedad cognitiva...")
        
        # Explorar semilla aleatoria
        seed_thought = random.choice(self.exploration_seeds)
        
        # Intentar reflexión sobre la semilla si el sistema de memoria lo permite
        try:
            if hasattr(self.brain.memory, 'retrieve_by_resonance'):
                # Buscar memorias relacionadas con la semilla
                related_memories = self.brain.memory.retrieve_by_resonance(seed_thought, limit=3)
                if related_memories:
                    print(f"[BackgroundThinker] 🌱 Explorando semilla: '{seed_thought}' con {len(related_memories)} memorias")
                    
                    # Forzar reflexión sobre estas memorias
                    self._force_exploration_reflection(seed_thought, related_memories)
            else:
                # Método alternativo: buscar en contexto
                if hasattr(self.brain.memory, 'retrieve_context'):
                    results = self.brain.memory.retrieve_context([seed_thought])
                    if results:
                        print(f"[BackgroundThinker] 🌱 Explorando semilla alternativa: '{seed_thought}'")
        except Exception as e:
            # Si falla, al menos introducir curiosidad sobre la semilla
            self.curiosity_buildup += 0.15
            print(f"[BackgroundThinker] 🌱 Semilla de novedad simple: '{seed_thought}'")

    def _inject_cognitive_entropy(self):
        """Introduce diversidad en el pensamiento para evitar bucles"""
        print("[BackgroundThinker] 🎲 Inyectando entropía cognitiva...")
        
        # Reducir drásticamente la relevancia del tema dominante
        self._dampen_dominant_concepts()
        
        # Introducir curiosidad hacia conceptos menos explorados
        self._boost_underexplored_areas()
        
        # Ajustar nivel de entropía
        self._boost_entropy_level(0.2)
        
        # Forzar exploración de dominios poco utilizados
        self._force_domain_exploration()

    def _cognitive_rest_cycle(self):
        """Períodos de descanso para resetear patrones"""
        print("[BackgroundThinker] 😴 Entrando en ciclo de descanso cognitivo...")
        
        # Pausa más larga para reseteo
        time.sleep(15)  # Reducido de 30 para no ser muy disruptivo
        
        # Reset del estado cognitivo
        self._reset_cognitive_state()
        
        # Introducir semilla aleatoria de pensamiento
        self._introduce_random_seed_thought()
        
        print("[BackgroundThinker] 🌅 Descanso cognitivo completado")

    def _decay_cognitive_fatigue(self):
        """Reduce gradualmente la fatiga cognitiva"""
        self.fatigue_decay_cycle += 1
        
        # Cada 5 ciclos de decaimiento, reducir fatiga
        if self.fatigue_decay_cycle >= 5:
            self.fatigue_decay_cycle = 0
            
            # Reducir fatiga de conceptos
            concepts_to_refresh = []
            for concept_id in list(self.concept_fatigue.keys()):
                self.concept_fatigue[concept_id] = max(0, self.concept_fatigue[concept_id] - 1)
                
                # Si la fatiga baja suficiente, quitar de conceptos fatigados
                if self.concept_fatigue[concept_id] <= 3 and concept_id in self.fatigued_concepts:
                    concepts_to_refresh.append(concept_id)
                    
            # Refrescar conceptos
            for concept_id in concepts_to_refresh:
                self.fatigued_concepts.discard(concept_id)
                
            if concepts_to_refresh:
                print(f"[BackgroundThinker] 🔄 Refrescados {len(concepts_to_refresh)} conceptos")

    # === MÉTODOS AUXILIARES PARA ANTI-BUCLES ===

    def _hash_associations(self, associations):
        """Genera hash de asociaciones para detectar repetición"""
        content = str(sorted([str(a) for a in associations]))
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def _hash_reflection(self, reflection):
        """Genera hash de reflexión para detectar repetición"""
        if isinstance(reflection, dict):
            # Usar campos clave de la reflexión
            content = str(reflection.get('focus_signals', [])) + str(reflection.get('insights', []))
        else:
            content = str(reflection)
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def _is_stuck_in_pattern(self):
        """Verifica si está atascado en un patrón específico"""
        if len(self.recent_topics) < 5:
            return False
            
        # Verificar si los últimos 5 temas son muy similares
        recent = list(self.recent_topics)[-5:]
        unique = len(set(recent))
        
        return unique <= 2  # Muy poca diversidad

    def _force_diverse_reflection(self):
        """Fuerza una reflexión en un área no explorada"""
        print("[BackgroundThinker] 🎯 Forzando reflexión diversa...")
        
        # Encontrar dominio menos explorado
        if self.domain_exploration:
            min_domain = min(self.domain_exploration, key=self.domain_exploration.get)
            seed = f"explorar {min_domain} desde nueva perspectiva"
        else:
            seed = random.choice(self.exploration_seeds)
        
        try:
            # Reflexión forzada con semilla específica
            if hasattr(self.brain, 'internal_reflection'):
                reflection = self.brain.internal_reflection(
                    priority=2, 
                    focus_override=seed
                )
                
                # Registrar esta reflexión diversa
                reflection_hash = self._hash_reflection(reflection)
                self.reflection_history.append(reflection_hash)
                
                print(f"[BackgroundThinker] ✅ Reflexión diversa completada: '{seed[:30]}...'")
        except Exception as e:
            print(f"[BackgroundThinker] ⚠️ Error en reflexión diversa: {e}")

    def _force_exploration_reflection(self, seed_thought, related_memories):
        """Fuerza reflexión sobre memorias específicas"""
        try:
            # Crear contexto de exploración
            context = {
                'exploration_seed': seed_thought,
                'related_memories': [mem.content[:100] for mem in related_memories[:3]]
            }
            
            # Reflexión específica sobre estas memorias
            reflection = self.brain.internal_reflection(priority=2)
            
            # Registrar como exploración diversa
            reflection_hash = self._hash_reflection(reflection)
            self.reflection_history.append(reflection_hash)
            
            # Incrementar exploración de dominios relacionados
            for memory in related_memories:
                for domain in getattr(memory, 'contextual_domains', ['general']):
                    self.domain_exploration[domain] += 1
                    
        except Exception:
            pass

    def _dampen_dominant_concepts(self):
        """Reduce la relevancia de conceptos dominantes"""
        # Aplicar fatiga extra a los conceptos más frecuentes
        if self.concept_fatigue:
            most_frequent = max(self.concept_fatigue, key=self.concept_fatigue.get)
            self.concept_fatigue[most_frequent] += 3
            self.fatigued_concepts.add(most_frequent)
            
        # Reducir momentum si está muy alto
        if self.thinking_momentum > 0.8:
            self.thinking_momentum *= 0.6

    def _boost_underexplored_areas(self):
        """Impulsa la exploración de áreas poco exploradas"""
        # Encontrar dominios menos explorados
        if self.domain_exploration:
            underexplored = [
                domain for domain, count in self.domain_exploration.items()
                if count < 3
            ]
            
            if underexplored:
                chosen_domain = random.choice(underexplored)
                self.curiosity_buildup += 0.2
                print(f"[BackgroundThinker] 🔍 Impulsando exploración en: {chosen_domain}")
                
                # Forzar reflexión en este dominio
                self._force_domain_reflection(chosen_domain)

    def _force_domain_exploration(self):
        """Fuerza la exploración de un dominio específico"""
        domain_options = [
            "self_reflection", "learning", "emotional", "social", 
            "technical", "philosophical", "creative"
        ]
        
        target_domain = random.choice(domain_options)
        
        try:
            if hasattr(self.brain.memory, 'retrieve_by_resonance'):
                # Buscar memorias en este dominio específico
                context = {'domain': target_domain}
                memories = self.brain.memory.retrieve_by_resonance(
                    target_domain, context=context, limit=3
                )
                
                if memories:
                    self.domain_exploration[target_domain] += 1
                    print(f"[BackgroundThinker] 🎯 Explorando dominio forzado: {target_domain}")
        except Exception:
            pass

    def _force_domain_reflection(self, domain):
        """Fuerza reflexión en un dominio específico"""
        try:
            domain_prompts = {
                "self_reflection": "reflexionar sobre mi naturaleza y experiencias internas",
                "learning": "considerar nuevos conocimientos y patrones de aprendizaje",
                "emotional": "explorar aspectos emocionales y resonancia afectiva",
                "social": "analizar interacciones y dinámicas relacionales",
                "technical": "examinar procesos y sistemas técnicos",
                "philosophical": "contemplar cuestiones existenciales y significado",
                "creative": "explorar posibilidades creativas y imaginativas"
            }
            
            prompt = domain_prompts.get(domain, f"explorar el dominio {domain}")
            
            # Realizar reflexión dirigida
            reflection = self.brain.internal_reflection(priority=2, focus_override=prompt)
            
            # Actualizar tracking
            self.domain_exploration[domain] += 1
            reflection_hash = self._hash_reflection(reflection)
            self.reflection_history.append(reflection_hash)
            
        except Exception:
            pass

    def _update_entropy_level(self, reflection):
        """Actualiza el nivel de entropía basado en la diversidad de reflexión"""
        try:
            if isinstance(reflection, dict):
                focus_signals = reflection.get("focus_signals", [])
                unique_signals = len(set(focus_signals))
                
                if unique_signals > 5:
                    self.entropy_level = min(1.0, self.entropy_level + 0.1)
                elif unique_signals < 3:
                    self.entropy_level = max(0.0, self.entropy_level - 0.05)
        except Exception:
            pass

    def _boost_entropy_level(self, amount):
        """Incrementa el nivel de entropía cognitiva"""
        self.entropy_level = min(1.0, self.entropy_level + amount)
        print(f"[BackgroundThinker] 📈 Entropía incrementada a {self.entropy_level:.2f}")

    def _reset_cognitive_state(self):
        """Resetea el estado cognitivo para empezar fresco"""
        # Reset suave del momentum
        self.thinking_momentum = 0.5
        
        # Limpiar curiosidad acumulada
        self.curiosity_buildup = 0.1
        
        # Reset parcial de fatiga (no completo para mantener algo de memoria)
        old_fatigue = dict(self.concept_fatigue)
        self.concept_fatigue.clear()
        self.fatigued_concepts.clear()
        
        # Restaurar solo la mitad de la fatiga anterior
        for concept_id, fatigue in old_fatigue.items():
            if fatigue > 3:
                self.concept_fatigue[concept_id] = fatigue // 2
        
        # Reset entropía a nivel medio
        self.entropy_level = 0.5
        
        print("[BackgroundThinker] 🔄 Estado cognitivo reseteado")

    def _introduce_random_seed_thought(self):
        """Introduce un pensamiento semilla aleatorio"""
        seed = random.choice(self.exploration_seeds)
        
        # Añadir curiosidad sobre la semilla
        self.curiosity_buildup += 0.15
        
        # Intentar reflexión sobre la semilla
        try:
            self._force_diverse_reflection()
        except Exception:
            pass
            
        print(f"[BackgroundThinker] 🌰 Semilla introducida: '{seed}'")

    def _reduce_consolidation_fatigue(self):
        """Reduce fatiga después de consolidación exitosa"""
        concepts_to_refresh = random.sample(
            list(self.fatigued_concepts), 
            min(3, len(self.fatigued_concepts))
        )
        
        for concept_id in concepts_to_refresh:
            self.concept_fatigue[concept_id] = max(0, self.concept_fatigue[concept_id] - 2)
            if self.concept_fatigue[concept_id] <= 2:
                self.fatigued_concepts.discard(concept_id)

    # === MÉTODOS ORIGINALES ACTUALIZADOS ===

    def _emotional_drift(self):
        """
        Simula deriva emocional natural - cambios sutiles en el estado emocional.
        """
        try:
            if not self.brain.adaptive_core:
                return
                
            # Obtener estado emocional actual
            current_state = self.brain.adaptive_core.emotional_state.get_state()
            
            # Aplicar deriva sutil basada en patrones de pensamiento y entropía
            drift_factors = {
                "curiosity": self.curiosity_buildup * 0.08,  # Reducido
                "satisfaction": self.thinking_momentum * 0.04,  # Reducido
                "excitement": len(self.last_associations) * 0.015,  # Reducido
                "creativity": self.entropy_level * 0.06  # NUEVO: basado en entropía
            }
            
            # Aplicar cambios muy sutiles
            for emotion, drift in drift_factors.items():
                if emotion in current_state:
                    # Cambio muy pequeño para simular deriva natural
                    change = random.uniform(-0.015, drift)  # Rango más pequeño
                    new_value = max(0.0, min(1.0, current_state[emotion] + change))
                    current_state[emotion] = new_value
            
            # NUEVO: Deriva hacia estabilidad si hay mucha fatiga
            if len(self.fatigued_concepts) > 5:
                current_state["calm"] = min(1.0, current_state.get("calm", 0.5) + 0.05)
                current_state["stress"] = max(0.0, current_state.get("stress", 0.5) - 0.03)
            
            # Actualizar estado emocional
            self.brain.adaptive_core.emotional_state.states.update(current_state)
            
        except Exception:
            pass

    def _trigger_emotional_response(self, trigger_type):
        """
        Activa una respuesta emocional específica basada en eventos cognitivos.
        """
        try:
            if not self.brain.adaptive_core:
                return
                
            # Mapear triggers a cambios emocionales (valores reducidos para evitar saturación)
            if trigger_type == "learning_shift":
                # Nuevas asociaciones -> curiosidad y ligera excitación
                self.brain.adaptive_core.emotional_state.states["curiosity"] += 0.08  # Reducido
                self.brain.adaptive_core.emotional_state.states["excitement"] += 0.03  # Reducido
                
            elif trigger_type == "insight":
                # Insight -> satisfacción y confianza
                self.brain.adaptive_core.emotional_state.states["satisfaction"] += 0.12  # Reducido
                self.brain.adaptive_core.emotional_state.states["confidence"] += 0.08  # Reducido
                self.brain.adaptive_core.emotional_state.states["creativity"] += 0.10  # Reducido
                
            elif trigger_type == "consolidation":
                # Consolidación -> calma y organización
                self.brain.adaptive_core.emotional_state.states["calm"] += 0.04  # Reducido
                self.brain.adaptive_core.emotional_state.states["stress"] = max(0.0, 
                    self.brain.adaptive_core.emotional_state.states.get("stress", 0.5) - 0.08)
            
            # Normalizar valores
            for emotion in self.brain.adaptive_core.emotional_state.states:
                value = self.brain.adaptive_core.emotional_state.states[emotion]
                self.brain.adaptive_core.emotional_state.states[emotion] = max(0.0, min(1.0, value))
                
        except Exception:
            pass

    def _maintain_diary(self):
        """
        Mantiene el diario de reflexiones promoviendo y descartando entradas.
        """
        try:
            # Ejecutar mantenimiento del diario
            if hasattr(self.brain, 'diario_reflexion'):
                self.brain.diario_reflexion.forget_and_promote()
            
            # Trigger emocional sutil por organización
            self._trigger_emotional_response("consolidation")
            
            # NUEVO: Reducir algo de fatiga después del mantenimiento
            if random.random() < 0.3:  # 30% de probabilidad
                self._reduce_consolidation_fatigue()
            
        except Exception:
            pass

    def _self_evaluation(self):
        """
        Evalúa el estado interno del sistema y ajusta parámetros.
        Mejorado con consideración de entropía y fatiga.
        """
        try:
            # Evaluar coherencia del sistema
            coherence_factors = {
                "memory_balance": self._evaluate_memory_balance(),
                "emotional_stability": self._evaluate_emotional_stability(),
                "association_health": self._evaluate_association_health(),
                "cognitive_diversity": self._evaluate_cognitive_diversity(),  # NUEVO
                "fatigue_level": self._evaluate_fatigue_level()  # NUEVO
            }
            
            # Ajustar parámetros según coherencia
            overall_coherence = sum(coherence_factors.values()) / len(coherence_factors)
            
            if overall_coherence < 0.4:  # Umbral más bajo
                # Sistema muy desbalanceado - reducir actividad y aumentar diversidad
                for key in self.intervals:
                    self.intervals[key] = int(self.intervals[key] * 1.3)
                self.thinking_momentum *= 0.7
                self._inject_cognitive_entropy()
                print("[BackgroundThinker] ⚠️ Coherencia baja, reduciendo actividad e inyectando entropía")
                
            elif overall_coherence > 0.8:
                # Sistema muy estable - puede aumentar actividad
                for key in self.intervals:
                    self.intervals[key] = int(self.intervals[key] * 0.95)
                self.thinking_momentum = min(1.0, self.thinking_momentum * 1.05)
                print("[BackgroundThinker] ✅ Alta coherencia, optimizando actividad")
            
            # NUEVO: Ajustes específicos basados en factores individuales
            if coherence_factors["cognitive_diversity"] < 0.3:
                self._inject_novelty()
                
            if coherence_factors["fatigue_level"] < 0.3:  # Mucha fatiga
                self._decay_cognitive_fatigue()
            
        except Exception:
            pass

    def _evaluate_memory_balance(self):
        """Evalúa el balance de la memoria. Adaptado a memoria trascendente."""
        try:
            if not hasattr(self.brain.memory, 'active_memory'):
                return 0.5  # Valor neutro si no hay sistema trascendente
                
            working = len(self.brain.memory.active_memory.get('working', {}))
            associative = len(self.brain.memory.active_memory.get('associative', {}))
            consolidated = len(self.brain.memory.active_memory.get('consolidated', {}))
            
            total = working + associative + consolidated
            if total == 0:
                return 0.5
            
            # Balance ideal: distribución razonable entre capas
            if working > 40:  # Demasiado en memoria de trabajo
                return 0.2
            elif working < 3:  # Muy poco activo
                return 0.6
            elif 5 <= working <= 25 and associative >= working * 0.5:
                return 0.9  # Buen balance
            else:
                return 0.7  # Balance aceptable
                
        except Exception:
            return 0.5

    def _evaluate_cognitive_diversity(self):
        """NUEVO: Evalúa la diversidad cognitiva actual"""
        try:
            # Factores de diversidad
            reflection_diversity = len(set(self.reflection_history)) / max(len(self.reflection_history), 1)
            topic_diversity = len(set(self.recent_topics)) / max(len(self.recent_topics), 1)
            domain_diversity = len(self.domain_exploration) / 7  # 7 dominios principales
            entropy_factor = self.entropy_level
            
            # Promedio ponderado
            diversity_score = (
                reflection_diversity * 0.3 +
                topic_diversity * 0.3 +
                domain_diversity * 0.2 +
                entropy_factor * 0.2
            )
            
            return min(1.0, diversity_score)
            
        except Exception:
            return 0.5

    def _evaluate_fatigue_level(self):
        """NUEVO: Evalúa el nivel de fatiga cognitiva"""
        try:
            total_concepts = len(self.concept_fatigue) if self.concept_fatigue else 1
            fatigued_ratio = len(self.fatigued_concepts) / total_concepts
            
            # Invertir: menos fatiga = mejor puntuación
            return max(0.0, 1.0 - fatigued_ratio)
            
        except Exception:
            return 0.5

    def _calculate_sleep_time(self):
        """
        Calcula el tiempo de pausa adaptativo basado en la carga cognitiva y entropía.
        """
        base_sleep = 1.0  # 1 segundo base
        
        # Ajustar según momentum
        if self.thinking_momentum > 0.8:
            sleep_factor = 0.7  # Pensar más rápido
        elif self.thinking_momentum < 0.4:
            sleep_factor = 1.4  # Pensar más lento
        else:
            sleep_factor = 1.0
        
        # NUEVO: Ajustar según entropía
        if self.entropy_level < 0.3:
            sleep_factor *= 0.8  # Menos pausa cuando hay poca diversidad
        elif self.entropy_level > 0.8:
            sleep_factor *= 1.2  # Más pausa cuando hay mucha actividad
            
        # NUEVO: Ajustar según fatiga
        if len(self.fatigued_concepts) > 10:
            sleep_factor *= 1.5  # Más descanso si hay mucha fatiga
        
        return base_sleep * sleep_factor

    def _run_imagination_cycle(self):
        """Ejecuta un ciclo de imaginación con consideración de diversidad."""
        try:
            cycle_results = self.brain.imagination_engine.run_imagination_cycle()
            
            # Ajustar momentum basado en resultados, pero con límites
            if cycle_results.get("scenarios_generated", 0) > 0:
                self.thinking_momentum += 0.10  # Reducido de 0.15
            
            if cycle_results.get("insights_discovered", 0) > 0:
                self.thinking_momentum += 0.18  # Reducido de 0.25
                # Trigger emocional por insight
                self._trigger_emotional_response("insight")
                # Incrementar entropía por insight
                self._boost_entropy_level(0.1)
            
            # Ajustar curiosidad con límite
            emotional_impact = cycle_results.get("emotional_impact", 0)
            if emotional_impact != 0:
                curiosity_boost = abs(emotional_impact) * 0.08  # Reducido de 0.1
                self.curiosity_buildup = min(0.9, self.curiosity_buildup + curiosity_boost)
                
        except Exception:
            pass  # Fallar silenciosamente

    def _maintain_imagination_system(self):
        """Mantiene el sistema de imaginación con consideración de entropía."""
        try:
            # Activar/desactivar según estado cognitivo y diversidad
            should_activate = (self.thinking_momentum > 0.6 and 
                             self.entropy_level > 0.4 and
                             len(self.fatigued_concepts) < 8)
            
            if should_activate and not self.brain.imagination_engine.active:
                intensity = min(0.8, self.thinking_momentum * self.entropy_level)
                self.brain.imagination_engine.activate(intensity=intensity)
                
            elif (self.thinking_momentum < 0.3 or len(self.fatigued_concepts) > 12) and self.brain.imagination_engine.active:
                self.brain.imagination_engine.deactivate()
            
            # Ajustar intensidad según momentum y entropía
            if self.brain.imagination_engine.active:
                new_intensity = max(0.2, min(1.0, self.thinking_momentum * self.entropy_level))
                self.brain.imagination_engine.imagination_intensity = new_intensity
            
            # Limpieza periódica (15% de probabilidad, incrementado para más mantenimiento)
            if random.random() < 0.15:
                self.brain.imagination_engine.cleanup_old_records()
                
        except Exception:
            pass  # Fallar silenciosamente

    def get_thinking_status(self):
        """
        Devuelve el estado actual del sistema de pensamiento.
        Expandido con información de anti-bucles.
        """
        return {
            "is_running": self.is_running,
            "cycle_count": self.cycle_count,
            "thinking_momentum": self.thinking_momentum,
            "curiosity_buildup": self.curiosity_buildup,
            "active_associations": len(self.last_associations),
            "intervals": self.intervals.copy(),
            # Nuevos campos anti-bucles
            "entropy_level": self.entropy_level,
            "fatigued_concepts_count": len(self.fatigued_concepts),
            "reflection_diversity": len(set(self.reflection_history)) / max(len(self.reflection_history), 1),
            "domain_exploration": dict(self.domain_exploration),
            "cognitive_loop_risk": "HIGH" if self._detect_cognitive_loop() else "LOW",
            "last_entropy_injection": datetime.fromtimestamp(self.last_entropy_injection).isoformat(),
            "last_cognitive_rest": datetime.fromtimestamp(self.last_cognitive_rest).isoformat()
        }

    def get_diversity_report(self):
        """NUEVO: Genera reporte detallado de diversidad cognitiva"""
        return {
            "entropy_level": f"{self.entropy_level:.2f}",
            "reflection_diversity": f"{len(set(self.reflection_history)) / max(len(self.reflection_history), 1):.2f}",
            "topic_diversity": f"{len(set(self.recent_topics)) / max(len(self.recent_topics), 1):.2f}",
            "explored_domains": len(self.domain_exploration),
            "fatigued_concepts": len(self.fatigued_concepts),
            "cognitive_loop_detected": self._detect_cognitive_loop(),
            "underexplored_domains": [
                domain for domain, count in self.domain_exploration.items()
                if count < 3
            ]
        }


# Modificación para integrar en main.py
def integrate_background_thinking(brain):
    """
    Función auxiliar para integrar el pensamiento en segundo plano en el cerebro.
    Agregar esto al __init__ de DigitalBrain:
    
    # Al final del __init__:
    from background_thinking import BackgroundThinker
    self.background_thinker = BackgroundThinker(self)
    self.background_thinker.start()
    
    # En shutdown():
    if hasattr(self, 'background_thinker'):
        self.background_thinker.stop()
    """
    pass