# adaptive.py
"""
Núcleo adaptativo integrado que conecta directamente con el modelo neuronal híbrido.
Gestiona motivaciones que dirigen el crecimiento neural y la especialización.
"""

import random
import time
from typing import Dict, List, Optional, Tuple, Any
from collections import deque
# Las clases de neuronas se importan desde neural_model
from signal_utils import Signal
# Configuración opcional
try:
    import config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False
    # Valores por defecto si no existe el módulo config
    class Config:
        SHOW_INTERNAL_LOGS = False
    config = Config()


class EnhancedMotivation:
    """
    Sistema motivacional avanzado que dirige el crecimiento y especialización neural.
    Integra directamente con pools de neuronas para feedback neuroplástico.
    """
    
    def __init__(self, neural_model=None):
        # Motivaciones primarias con umbrales dinámicos
        self.core_drives = {
            "self_preservation": {"level": 0.7, "urgency": 0.5, "neural_allocation": 0.0},
            "adaptation": {"level": 0.8, "urgency": 0.4, "neural_allocation": 0.0},
            "exploration": {"level": 0.6, "urgency": 0.6, "neural_allocation": 0.0},
            "communication": {"level": 0.8, "urgency": 0.3, "neural_allocation": 0.0},
            "maintenance": {"level": 0.7, "urgency": 0.2, "neural_allocation": 0.0},
            "learning": {"level": 0.9, "urgency": 0.7, "neural_allocation": 0.0},
            "creativity": {"level": 0.5, "urgency": 0.4, "neural_allocation": 0.0}
        }
        
        # Motivaciones emergentes (se desarrollan con el tiempo)
        self.emergent_drives = {}
        
        # Referencia al modelo neuronal para dirigir crecimiento
        self.neural_model = neural_model
        
        # Historia de satisfacción motivacional
        self.satisfaction_history = deque(maxlen=100)
        self.drive_conflicts = deque(maxlen=50)
        
        # Mapeo de motivaciones a tipos neuronales
        # Las clases de neuronas se acceden a través de neural_model
        self.neural_preferences = {
            "self_preservation": {
                "animal": ["SensoryNeuron", "FeedbackControlNeuron"],
                "micelial": ["ChemicalSensorNeuron", "ChemicalModulatorNeuron"]
            },
            "adaptation": {
                "animal": ["PlasticityMemoryNeuron", "AssociativeNeuron"],
                "micelial": ["ChemicalLearningNeuron", "DistributedMemoryNeuron"]
            },
            "exploration": {
                "animal": ["SensoryNeuron", "TemporalIntegratorNeuron"],
                "micelial": ["ChemicalSensorNeuron", "CommunicatorNeuron"]
            },
            "communication": {
                "animal": ["MotorNeuron", "ModulatoryNeuron"],
                "micelial": ["CommunicatorNeuron", "ChemicalModulatorNeuron"]
            },
            "learning": {
                "animal": ["PlasticityMemoryNeuron", "AssociativeNeuron"],
                "micelial": ["ChemicalLearningNeuron", "DistributedMemoryNeuron"]
            },
            "creativity": {
                "animal": ["AssociativeNeuron", "ModulatoryNeuron"],
                "micelial": ["CommunicatorNeuron", "DistributedMemoryNeuron"]
            }
        }

    def set_neural_model(self, neural_model):
        """Establece referencia al modelo neuronal para integración"""
        self.neural_model = neural_model
        self._update_neural_allocations()

    def evaluate_neural_state(self, neural_feedback):
        """
        Evalúa estado motivacional basado en feedback del modelo neuronal.
        """
        if not isinstance(neural_feedback, dict):
            return

        # Extraer métricas del modelo neuronal
        neural_efficiency = neural_feedback.get("integration_strength", 0.5)
        specialization_count = neural_feedback.get("specialization_regions", 0)
        bridge_coherence = neural_feedback.get("bridge_coherence", 0.5)
        
        # Actualizar motivaciones basado en rendimiento neural
        if neural_efficiency > 0.8:
            self.core_drives["adaptation"]["level"] = min(1.0, 
                self.core_drives["adaptation"]["level"] + 0.05)
            self.core_drives["maintenance"]["urgency"] *= 0.9
        elif neural_efficiency < 0.4:
            self.core_drives["self_preservation"]["urgency"] = min(1.0, 
                self.core_drives["self_preservation"]["urgency"] + 0.2)
            
        # Impulsar exploración si hay pocas especializaciones
        if specialization_count < 3:
            self.core_drives["exploration"]["level"] = min(1.0,
                self.core_drives["exploration"]["level"] + 0.1)
                
        # Impulsar comunicación si coherencia de puentes es baja
        if bridge_coherence < 0.3:
            self.core_drives["communication"]["urgency"] = min(1.0,
                self.core_drives["communication"]["urgency"] + 0.15)

        if config.SHOW_INTERNAL_LOGS:
            print(f"[EnhancedMotivation] Estado neural evaluado - Eficiencia: {neural_efficiency:.3f}")

    def process_external_stimulus(self, stimulus, context=None):
        """
        Procesa estímulo externo y actualiza motivaciones.
        """
        stimulus_str = str(stimulus).lower()
        intensity = len(stimulus_str) / 100.0  # Normalizado
        
        # Análisis del estímulo
        if "danger" in stimulus_str or "threat" in stimulus_str:
            self._boost_drive("self_preservation", 0.3, 0.4)
        elif "new" in stimulus_str or "unknown" in stimulus_str:
            self._boost_drive("exploration", 0.2, 0.3)
        elif "learn" in stimulus_str or "knowledge" in stimulus_str:
            self._boost_drive("learning", 0.25, 0.2)
        elif "connect" in stimulus_str or "communicate" in stimulus_str:
            self._boost_drive("communication", 0.2, 0.25)
        elif "create" in stimulus_str or "innovate" in stimulus_str:
            self._boost_drive("creativity", 0.3, 0.2)
            
        # Desarrollar motivaciones emergentes
        self._develop_emergent_drives(stimulus_str, context)
        
        # Decay natural de urgencias
        self._apply_natural_decay()
        
        if config.SHOW_INTERNAL_LOGS:
            main_drive = self.get_dominant_drive()
            print(f"[EnhancedMotivation] Estímulo procesado: '{stimulus_str[:30]}...' - Drive dominante: {main_drive}")

    def _boost_drive(self, drive_name, level_boost, urgency_boost):
        """Aumenta nivel y urgencia de un impulso específico"""
        if drive_name in self.core_drives:
            drive = self.core_drives[drive_name]
            drive["level"] = min(1.0, drive["level"] + level_boost)
            drive["urgency"] = min(1.0, drive["urgency"] + urgency_boost)

    def _develop_emergent_drives(self, stimulus, context):
        """Desarrolla motivaciones emergentes basadas en experiencias repetidas"""
        # Extraer patrones del estímulo
        if context and isinstance(context, dict):
            pattern = context.get("pattern", "unknown")
        else:
            # Crear patrón simple basado en contenido
            words = stimulus.split()
            pattern = "_".join(sorted(set(words))[:3]) if words else "general"
            
        # Desarrollar impulso emergente
        if pattern not in self.emergent_drives:
            self.emergent_drives[pattern] = {
                "level": 0.1,
                "urgency": 0.05,
                "encounters": 1,
                "neural_allocation": 0.0
            }
        else:
            drive = self.emergent_drives[pattern]
            drive["encounters"] += 1
            drive["level"] = min(0.8, drive["level"] + 0.02)
            drive["urgency"] = min(0.6, drive["urgency"] + 0.01)
            
        # Promover impulsos emergentes exitosos a core drives
        if pattern in self.emergent_drives:
            emergent = self.emergent_drives[pattern]
            if emergent["encounters"] > 20 and emergent["level"] > 0.5:
                self._promote_emergent_drive(pattern)

    def _promote_emergent_drive(self, pattern):
        """Promueve impulso emergente a motivación core"""
        emergent = self.emergent_drives[pattern]
        new_drive_name = f"emergent_{pattern}"
        
        self.core_drives[new_drive_name] = {
            "level": emergent["level"] * 0.8,
            "urgency": emergent["urgency"],
            "neural_allocation": 0.0
        }
        
        # Asignar preferencias neuronales generales (usando nombres de clase como strings)
        self.neural_preferences[new_drive_name] = {
            "animal": ["AssociativeNeuron", "PlasticityMemoryNeuron"],
            "micelial": ["ChemicalLearningNeuron", "DistributedMemoryNeuron"]
        }
        
        del self.emergent_drives[pattern]
        
        if config.SHOW_INTERNAL_LOGS:
            print(f"[EnhancedMotivation] Impulso emergente '{pattern}' promovido a core drive")

    def _apply_natural_decay(self):
        """Aplica decay natural a todas las motivaciones"""
        for drive_name, drive in self.core_drives.items():
            base_levels = {
                "self_preservation": 0.7,
                "adaptation": 0.6,
                "exploration": 0.5,
                "communication": 0.4,
                "maintenance": 0.6,
                "learning": 0.8,
                "creativity": 0.3
            }
            
            base_level = base_levels.get(drive_name, 0.5)
            
            if drive["level"] > base_level:
                drive["level"] = max(base_level, drive["level"] - 0.005)
            else:
                drive["level"] = min(base_level, drive["level"] + 0.002)
                
            drive["urgency"] = max(0.1, drive["urgency"] * 0.98)

    def get_dominant_drive(self):
        """Obtiene el impulso dominante actual"""
        all_drives = {**self.core_drives, **self.emergent_drives}
        
        # Calcular score combinado (nivel * urgencia)
        scored_drives = {
            name: drive["level"] * (1 + drive["urgency"])
            for name, drive in all_drives.items()
        }
        
        return max(scored_drives, key=scored_drives.get)

    def get_drive_vector(self):
        """Devuelve vector completo de motivaciones para toma de decisiones"""
        vector = {}
        
        # Incluir core drives
        for name, drive in self.core_drives.items():
            vector[name] = {
                "strength": drive["level"] * (1 + drive["urgency"]),
                "level": drive["level"],
                "urgency": drive["urgency"],
                "neural_support": drive["neural_allocation"]
            }
            
        # Incluir emergent drives significativas
        for name, drive in self.emergent_drives.items():
            if drive["level"] > 0.2:
                vector[f"emergent_{name}"] = {
                    "strength": drive["level"] * (1 + drive["urgency"]),
                    "level": drive["level"],
                    "urgency": drive["urgency"],
                    "neural_support": drive["neural_allocation"]
                }
                
        return vector

    def direct_neural_growth(self):
        """
        Dirige crecimiento neural basado en necesidades motivacionales.
        """
        if not self.neural_model:
            return
            
        dominant = self.get_dominant_drive()
        drive_vector = self.get_drive_vector()
        
        # Determinar necesidades de crecimiento neural
        growth_needs = self._assess_neural_needs(drive_vector)
        
        # Dirigir crecimiento específico
        for need_type, intensity in growth_needs.items():
            if intensity > 0.7:
                self._request_targeted_growth(need_type, dominant, intensity)
                
        # Actualizar asignaciones neuronales
        self._update_neural_allocations()
        
        if config.SHOW_INTERNAL_LOGS:
            print(f"[EnhancedMotivation] Dirigiendo crecimiento neural para '{dominant}' - Necesidades: {growth_needs}")

    def _assess_neural_needs(self, drive_vector):
        """Evalúa necesidades de crecimiento neural"""
        needs = {
            "sensory_processing": 0.0,
            "memory_systems": 0.0,
            "communication_bridges": 0.0,
            "learning_plasticity": 0.0,
            "integration_capacity": 0.0
        }
        
        for drive_name, drive_data in drive_vector.items():
            strength = drive_data["strength"]
            neural_support = drive_data["neural_support"]
            
            # Gap entre demanda y soporte neural actual
            support_gap = max(0, strength - neural_support)
            
            if "exploration" in drive_name or "self_preservation" in drive_name:
                needs["sensory_processing"] += support_gap * 0.8
                
            if "learning" in drive_name or "adaptation" in drive_name:
                needs["memory_systems"] += support_gap * 0.9
                needs["learning_plasticity"] += support_gap * 0.7
                
            if "communication" in drive_name:
                needs["communication_bridges"] += support_gap * 0.8
                
            if "creativity" in drive_name:
                needs["integration_capacity"] += support_gap * 0.6
                
        return needs

    def _request_targeted_growth(self, need_type, dominant_drive, intensity):
        """Solicita crecimiento neural específico al modelo"""
        if not hasattr(self.neural_model, '_targeted_motivational_growth'):
            return
            
        # Mapear necesidades a tipos neuronales
        growth_mapping = {
            "sensory_processing": {
                "animal": ["SensoryNeuron", "TemporalIntegratorNeuron"],
                "micelial": ["ChemicalSensorNeuron"]
            },
            "memory_systems": {
                "animal": ["PlasticityMemoryNeuron"],
                "micelial": ["DistributedMemoryNeuron", "ChemicalLearningNeuron"]
            },
            "communication_bridges": {
                "bridges": True,
                "animal": ["MotorNeuron", "ModulatoryNeuron"],
                "micelial": ["CommunicatorNeuron", "ChemicalModulatorNeuron"]
            },
            "learning_plasticity": {
                "animal": ["PlasticityMemoryNeuron", "AssociativeNeuron"],
                "micelial": ["ChemicalLearningNeuron"]
            }
        }
        
        if need_type in growth_mapping:
            self.neural_model._targeted_motivational_growth(
                need_type, growth_mapping[need_type], intensity, dominant_drive
            )

    def _update_neural_allocations(self):
        """Actualiza asignaciones neuronales basadas en el estado del modelo"""
        if not self.neural_model:
            return
            
        # Obtener estado del modelo neuronal
        neural_state = self.neural_model.get_system_state()
        
        total_neurons = neural_state["operational_metrics"]["total_neurons"]
        specialization_regions = neural_state["specialization_regions"]
        
        # Calcular soporte neural para cada motivación
        for drive_name in self.core_drives:
            neural_support = self._calculate_neural_support(
                drive_name, specialization_regions, total_neurons
            )
            self.core_drives[drive_name]["neural_allocation"] = neural_support

    def _calculate_neural_support(self, drive_name, regions, total_neurons):
        """Calcula soporte neural actual para una motivación"""
        base_support = 0.1  # Soporte básico
        
        # Soporte de regiones especializadas relevantes
        relevant_regions = {
            "self_preservation": ["attention", "emotion"],
            "adaptation": ["learning", "memory"],
            "exploration": ["attention", "prediction"],
            "communication": ["language", "emotion"],
            "learning": ["memory", "learning"],
            "creativity": ["language", "prediction", "memory"]
        }
        
        if drive_name in relevant_regions:
            for region_type in relevant_regions[drive_name]:
                if region_type in regions:
                    region_data = regions[region_type]
                    efficiency = region_data.get("efficiency", 0.0)
                    neuron_count = region_data.get("neuron_count", 0)
                    
                    support_boost = (efficiency * neuron_count / max(1, total_neurons)) * 2.0
                    base_support += support_boost
                    
        return min(1.0, base_support)

    def detect_drive_conflicts(self):
        """Detecta conflictos entre motivaciones"""
        drive_vector = self.get_drive_vector()
        conflicts = []
        
        # Pares de drives potencialmente conflictivos
        conflict_pairs = [
            ("self_preservation", "exploration"),
            ("maintenance", "creativity"),
            ("communication", "self_preservation")
        ]
        
        for drive1, drive2 in conflict_pairs:
            if drive1 in drive_vector and drive2 in drive_vector:
                strength1 = drive_vector[drive1]["strength"]
                strength2 = drive_vector[drive2]["strength"]
                
                if abs(strength1 - strength2) < 0.1 and min(strength1, strength2) > 0.6:
                    conflict = {
                        "drives": (drive1, drive2),
                        "intensity": min(strength1, strength2),
                        "timestamp": time.time()
                    }
                    conflicts.append(conflict)
                    
        if conflicts:
            self.drive_conflicts.extend(conflicts)
            
        return conflicts


class AdaptiveCore:
    """
    Núcleo adaptativo integrado que combina motivación, emoción y procesamiento neural
    para el ser digital. Incluye feedback neuroplástico y especialización dirigida.
    """
    
    def __init__(self, neural_model=None):
        self.neural_model = neural_model
        self.motivation = EnhancedMotivation(neural_model)
        
        # Sistema emocional será inyectado externamente
        self.emotional_state = None
        
        # Métricas de integración
        self.integration_cycles = 0
        self.decision_history = deque(maxlen=200)
        self.neural_feedback_history = deque(maxlen=100)
        
        # Sistema de atención dirigida
        self.attention_system = self._init_attention_system()
        
        # Memoria episódica básica
        self.episodic_memory = deque(maxlen=1000)

    def set_neural_model(self, neural_model):
        """Establece modelo neuronal para integración"""
        self.neural_model = neural_model
        self.motivation.set_neural_model(neural_model)

    def set_emotional_state(self, emotional_state):
        """Establece sistema emocional para integración"""
        self.emotional_state = emotional_state

    def _init_attention_system(self):
        """Inicializa sistema de atención dirigida"""
        return {
            "focus_targets": [],
            "attention_strength": 0.5,
            "context_window": deque(maxlen=10),
            "salience_map": {}
        }

    def perceive(self, stimulus, context=None, neural_response=None):
        """
        Percepción integrada que combina procesamiento neural y motivacional.
        
        Args:
            stimulus: El estímulo a procesar
            context: Contexto adicional para el procesamiento
            neural_response: Respuesta neural preprocesada (opcional)
        """
        # Si no se proporciona una respuesta neural, usar valores por defecto
        if neural_response is None:
            neural_response = {"integration_strength": 0.5}
            
        # Procesamiento motivacional
        self.motivation.process_external_stimulus(stimulus, context)
        self.motivation.evaluate_neural_state(self._extract_neural_metrics(neural_response))
        
        # Crear episodio de memoria
        episode = {
            "timestamp": time.time(),
            "stimulus": str(stimulus)[:100],  # Truncar para eficiencia
            "context": context,
            "neural_response": self._summarize_neural_response(neural_response),
            "dominant_drive": self.motivation.get_dominant_drive(),
            "emotional_state": self.emotional_state.label() if self.emotional_state else "unknown"
        }
        self.episodic_memory.append(episode)
        
        # Actualizar sistema de atención
        self._update_attention_system(stimulus, context)
        
        if config.SHOW_INTERNAL_LOGS:
            print(f"[AdaptiveCore] Percepción integrada - Estímulo: '{str(stimulus)[:30]}...'")
            
        return neural_response

    def decide(self, context=None):
        """
        Toma de decisiones integrada basada en motivación, emoción y capacidad neural.
        """
        drive_vector = self.motivation.get_drive_vector()
        dominant_drive = self.motivation.get_dominant_drive()
        
        # Estado emocional actual
        emotional_label = self.emotional_state.label() if self.emotional_state else "neutral"
        emotional_states = self.emotional_state.get_state() if self.emotional_state else {}
        
        # Detectar conflictos motivacionales
        conflicts = self.motivation.detect_drive_conflicts()
        
        # Selección de acción basada en integración
        action = self._select_action(dominant_drive, emotional_label, conflicts, context)
        
        # Crear decisión detallada
        decision = {
            "action": action,
            "primary_drive": dominant_drive,
            "drive_strength": drive_vector.get(dominant_drive, {}).get("strength", 0.5),
            "emotional_context": emotional_label,
            "conflicts": len(conflicts),
            "neural_capacity": self._assess_neural_capacity(),
            "context": context,
            "timestamp": time.time()
        }
        
        self.decision_history.append(decision)
        
        # Dirigir crecimiento neural si es necesario
        if self.integration_cycles % 20 == 0:  # Cada 20 ciclos
            self.motivation.direct_neural_growth()
            
        if config.SHOW_INTERNAL_LOGS:
            print(f"[AdaptiveCore] Decisión tomada - Acción: '{action}' (Drive: {dominant_drive})")
            
        return decision

    def _select_action(self, dominant_drive, emotional_state, conflicts, context):
        """Selecciona acción basada en estado integrado"""
        
        # Manejar estado emocional crítico primero
        if emotional_state in ["overwhelmed", "blocked"]:
            return "Reduce cognitive load and consolidate"
        elif emotional_state == "excited" and "creativity" in dominant_drive:
            return "Engage in creative exploration"
        elif emotional_state == "stressed" and conflicts:
            return "Resolve motivational conflicts"
            
        # Acciones por impulso dominante
        action_map = {
            "self_preservation": "Activate protective protocols and assess risks",
            "adaptation": "Analyze environment and adjust behavioral patterns",
            "exploration": "Seek new information and expand knowledge boundaries",
            "communication": "Establish connections and share information",
            "maintenance": "Perform system optimization and memory consolidation",
            "learning": "Engage deep learning processes and form new associations",
            "creativity": "Synthesize novel combinations and generate innovations"
        }
        
        # Acciones para drives emergentes
        if dominant_drive.startswith("emergent_"):
            return f"Engage specialized processing for {dominant_drive.replace('emergent_', '')}"
            
        return action_map.get(dominant_drive, "Maintain current state and observe")

    def _assess_neural_capacity(self):
        """Evalúa capacidad neural actual"""
        if not self.neural_model:
            return 0.5
            
        state = self.neural_model.get_system_state()
        
        capacity_metrics = {
            "utilization": 1.0 - state["resource_management"]["neural_capacity_used"],
            "efficiency": state["longevity_indicators"]["structural_stability"],
            "adaptability": state["longevity_indicators"]["growth_potential"],
            "specialization": len(state["specialization_regions"]) / 10.0  # Normalizado
        }
        
        return sum(capacity_metrics.values()) / len(capacity_metrics)

    def _extract_neural_metrics(self, neural_response):
        """Extrae métricas relevantes de la respuesta neural"""
        if isinstance(neural_response, str):
            # Parsear respuesta de texto para extraer métricas
            metrics = {
                "integration_strength": 0.5,
                "bridge_coherence": 0.5,
                "specialization_regions": 0
            }
            
            if "Fast response:" in neural_response:
                try:
                    fast_val = float(neural_response.split("Fast response: ")[1].split()[0])
                    metrics["integration_strength"] = fast_val
                except:
                    pass
                    
            if "Cross-system sync:" in neural_response:
                try:
                    sync_val = float(neural_response.split("Cross-system sync: ")[1].split()[0])
                    metrics["bridge_coherence"] = sync_val
                except:
                    pass
                    
            return metrics
        elif isinstance(neural_response, dict):
            return neural_response
        else:
            return {"integration_strength": 0.5}

    def _record_neural_feedback(self, response):
        """Registra feedback neural para análisis"""
        feedback = {
            "timestamp": time.time(),
            "response": self._summarize_neural_response(response),
            "cycle": self.integration_cycles
        }
        self.neural_feedback_history.append(feedback)

    def _summarize_neural_response(self, response):
        """Crea resumen compacto de respuesta neural"""
        if isinstance(response, str):
            return response[:200]  # Truncar
        elif isinstance(response, dict):
            return {k: v for k, v in response.items() if k in 
                   ["integration_strength", "bridge_coherence", "specialization_regions"]}
        else:
            return str(response)[:100]

    def _update_attention_system(self, stimulus, context):
        """Actualiza sistema de atención dirigida"""
        # Agregar estímulo a ventana de contexto
        self.attention_system["context_window"].append({
            "stimulus": str(stimulus)[:50],
            "timestamp": time.time(),
            "context": context
        })
        
        # Actualizar mapa de saliencia
        stimulus_key = str(stimulus)[:20]
        if stimulus_key in self.attention_system["salience_map"]:
            self.attention_system["salience_map"][stimulus_key] += 1
        else:
            self.attention_system["salience_map"][stimulus_key] = 1
            
        # Mantener solo los más relevantes
        if len(self.attention_system["salience_map"]) > 50:
            sorted_items = sorted(
                self.attention_system["salience_map"].items(),
                key=lambda x: x[1], reverse=True
            )
            self.attention_system["salience_map"] = dict(sorted_items[:30])

    def act(self, decision, context=None):
        """
        Ejecuta acción con feedback al sistema neuronal.
        """
        action = decision.get("action", "No action")
        primary_drive = decision.get("primary_drive", "unknown")
        
        # Ejecutar acción con integración neural
        if self.neural_model and hasattr(self.neural_model, '_process_motivated_action'):
            neural_result = self.neural_model._process_motivated_action(action, primary_drive)
        else:
            neural_result = None
            
        # Feedback a sistema emocional
        if self.emotional_state:
            if "resolve conflicts" in action.lower():
                learning_signal = "conflict"
            elif "creative" in action.lower() or "innovate" in action.lower():
                learning_signal = "discovery"
            elif "optimize" in action.lower() or "consolidate" in action.lower():
                learning_signal = "resolved"
            else:
                learning_signal = "neutral"
                
            # Actualizar estado emocional con contexto motivacional
            drive_vector = self.motivation.get_drive_vector()
            # Asegurarse de que el drive_vector tenga el formato correcto
            motivation_update = {
                k: {"level": float(v.get("level", 0.0))} 
                if isinstance(v, dict) else 
                {"level": float(v) if isinstance(v, (int, float)) else 0.0}
                for k, v in drive_vector.items()
            }
            self.emotional_state.update(motivation_update, learning_signal)
        
        if config.SHOW_INTERNAL_LOGS:
            print(f"[AdaptiveCore] Acción ejecutada: '{action}' con resultado neural: {neural_result}")

    def run_cycle(self, stimulus, context=None, learning_signal=None, neural_response=None):
        """
        Ejecuta ciclo completo de procesamiento integrado.
        
        Args:
            stimulus: El estímulo a procesar
            context: Contexto adicional para el procesamiento
            learning_signal: Señal de aprendizaje (opcional)
            neural_response: Respuesta neural preprocesada (opcional)
        """
        self.integration_cycles += 1
        
        # Percepción integrada con respuesta neural opcional
        self.perceive(stimulus, context, neural_response)
        
        # Toma de decisión
        decision = self.decide(context)
        
        # Ejecución de acción
        self.act(decision, context)
        
        # Estado emocional actualizado automáticamente en act()
        
        # Compilar resultado del ciclo
        cycle_result = {
            "cycle": self.integration_cycles,
            "decision": decision,
            "emotional_state": self.emotional_state.get_emotional_summary() if self.emotional_state else {"label": "unknown"},
            "motivation": {
                "dominant_drive": self.motivation.get_dominant_drive(),
                "drive_vector": self.motivation.get_drive_vector(),
                "conflicts": len(self.motivation.detect_drive_conflicts())
            },
            "neural_capacity": self._assess_neural_capacity(),
            "attention_focus": len(self.attention_system["focus_targets"]),
            "episodic_memories": len(self.episodic_memory)
        }
        
        return cycle_result

    def get_comprehensive_state(self):
        """Obtiene estado completo del núcleo adaptativo"""
        return {
            "motivation_system": {
                "core_drives": self.motivation.core_drives,
                "emergent_drives": self.motivation.emergent_drives,
                "dominant_drive": self.motivation.get_dominant_drive(),
                "conflicts": self.motivation.detect_drive_conflicts()
            },
            "attention_system": self.attention_system,
            "integration_metrics": {
                "total_cycles": self.integration_cycles,
                "neural_capacity": self._assess_neural_capacity(),
                "decision_history_length": len(self.decision_history),
                "neural_feedback_samples": len(self.neural_feedback_history)
            },
            "episodic_memory": {
                "total_episodes": len(self.episodic_memory),
                "recent_episodes": list(self.episodic_memory)[-5:] if self.episodic_memory else []
            }
        }

    def analyze_behavioral_patterns(self):
        """Analiza patrones de comportamiento emergentes"""
        if len(self.decision_history) < 10:
            return {"status": "insufficient_data"}
            
        recent_decisions = list(self.decision_history)[-50:]
        
        # Análisis de patrones de drives
        drive_frequency = {}
        for decision in recent_decisions:
            drive = decision["primary_drive"]
            drive_frequency[drive] = drive_frequency.get(drive, 0) + 1
            
        # Análisis de patrones emocionales
        emotional_patterns = {}
        for decision in recent_decisions:
            emotion = decision.get("emotional_context", "unknown")
            emotional_patterns[emotion] = emotional_patterns.get(emotion, 0) + 1
            
        # Detectar tendencias temporales
        time_patterns = self._analyze_temporal_patterns(recent_decisions)
        
        return {
            "drive_preferences": drive_frequency,
            "emotional_patterns": emotional_patterns,
            "temporal_trends": time_patterns,
            "stability_score": self._calculate_behavioral_stability(recent_decisions),
            "adaptation_rate": self._calculate_adaptation_rate()
        }

    def _analyze_temporal_patterns(self, decisions):
        """Analiza patrones temporales en las decisiones"""
        if len(decisions) < 5:
            return {}
            
        # Agrupar decisiones por períodos de tiempo
        time_groups = {}
        base_time = decisions[0]["timestamp"]
        
        for decision in decisions:
            relative_time = int((decision["timestamp"] - base_time) // 300)  # Grupos de 5 minutos
            if relative_time not in time_groups:
                time_groups[relative_time] = []
            time_groups[relative_time].append(decision)
            
        # Analizar cambios en drives dominantes por período
        temporal_shifts = {}
        prev_dominant = None
        
        for time_period in sorted(time_groups.keys()):
            period_drives = [d["primary_drive"] for d in time_groups[time_period]]
            most_common = max(set(period_drives), key=period_drives.count)
            
            if prev_dominant and prev_dominant != most_common:
                shift_key = f"{prev_dominant}_to_{most_common}"
                temporal_shifts[shift_key] = temporal_shifts.get(shift_key, 0) + 1
                
            prev_dominant = most_common
            
        return temporal_shifts

    def _calculate_behavioral_stability(self, decisions):
        """Calcula puntuación de estabilidad comportamental"""
        if len(decisions) < 5:
            return 0.5
            
        # Medir variabilidad en drives dominantes
        drives = [d["primary_drive"] for d in decisions]
        unique_drives = set(drives)
        drive_entropy = len(unique_drives) / len(drives)
        
        # Medir variabilidad en fuerza de drives
        strengths = [d.get("drive_strength", 0.5) for d in decisions]
        strength_variance = sum((s - sum(strengths)/len(strengths))**2 for s in strengths) / len(strengths)
        
        # Combinar métricas (menor variabilidad = mayor estabilidad)
        stability = 1.0 - (drive_entropy * 0.6 + min(strength_variance, 1.0) * 0.4)
        return max(0.0, min(1.0, stability))

    def _calculate_adaptation_rate(self):
        """Calcula tasa de adaptación del sistema"""
        if len(self.neural_feedback_history) < 10:
            return 0.5
            
        # Medir mejora en feedback neural a lo largo del tiempo
        recent_feedback = list(self.neural_feedback_history)[-20:]
        
        early_performance = sum(
            f.get("response", {}).get("integration_strength", 0.5) 
            for f in recent_feedback[:10]
        ) / 10
        
        late_performance = sum(
            f.get("response", {}).get("integration_strength", 0.5) 
            for f in recent_feedback[10:]
        ) / 10
        
        # Tasa de adaptación normalizada
        adaptation_rate = (late_performance - early_performance + 1.0) / 2.0
        return max(0.0, min(1.0, adaptation_rate))

if __name__ == "__main__":
    # Test básico del sistema integrado
    core = AdaptiveCore()
    
    test_stimuli = [
        "new data pattern detected",
        "system performance declining",
        "creative opportunity identified", 
        "communication request received",
        "learning objective achieved"
    ]
    
    for stimulus in test_stimuli:
        print(f"\n--- Procesando: {stimulus} ---")
        result = core.run_cycle(stimulus)
        if config.SHOW_INTERNAL_LOGS:
            print(f"Resultado: {result}")
            
    # Análisis de patrones
    patterns = core.analyze_behavioral_patterns()
    print(f"\n--- Análisis de Patrones ---")
    print(f"Patrones detectados: {patterns}")