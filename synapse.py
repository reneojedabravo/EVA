# synapse.py
"""Sistema avanzado de sinapsis para comunicación entre neuronas animales y miceliales.
Optimizado para diferentes tipos de señales, longevidad y adaptabilidad.
Permite comunicación fluida en redes híbridas de gran escala."""

import time
import math
import hashlib
import os
import sys
import random
from abc import ABC, abstractmethod
from collections import deque, defaultdict
from threading import RLock
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum

# Importaciones locales
from animal import create_cognitive_animal_neuron
from micelial import create_cognitive_micelial_neuron

class SignalType(Enum):
    """Tipos de señales que pueden transmitirse"""
    ELECTRICAL = "electrical"
    CHEMICAL = "chemical"
    HYBRID = "hybrid"
    CONCEPTUAL = "conceptual"
    MECHANICAL = "mechanical"

class SynapseType(Enum):
    """Tipos de sinapsis"""
    EXCITATORY = "excitatory"
    INHIBITORY = "inhibitory"
    MODULATORY = "modulatory"
    HYBRID = "hybrid"

class TransmissionMode(Enum):
    """Modos de transmisión"""
    FAST = "fast"      # Neuronas animales
    SLOW = "slow"      # Neuronas miceliales
    ADAPTIVE = "adaptive"  # Se adapta según el contexto

class SynapseBase(ABC):
    """Clase base para todas las sinapsis.
    Maneja comunicación entre diferentes tipos de neuronas."""
    
    def __init__(self, 
                 synapse_id: str, 
                 source_neuron, 
                 target_neuron,
                 synapse_type: SynapseType = SynapseType.EXCITATORY,
                 signal_type: SignalType = SignalType.CHEMICAL,
                 transmission_mode: TransmissionMode = TransmissionMode.ADAPTIVE):
        self.synapse_id = synapse_id
        self.source_neuron = source_neuron
        self.target_neuron = target_neuron
        self.synapse_type = synapse_type
        self.signal_type = signal_type
        self.transmission_mode = transmission_mode
        
        # Propiedades básicas
        self.weight = 1.0
        self.threshold = 0.1
        self.strength = 1.0
        self.delay = 0.01  # Delay por defecto
        self.age = 0.0
        self.is_active_flag = True
        self.last_transmission = 0.0
        self.usage_frequency = 0.0
        
        # Thread safety
        self.lock = RLock()
        
        # Historial de transmisiones
        self.transmission_history = deque(maxlen=1000)
        self.failure_count = 0
        self.success_count = 0
        
        # Compatibilidad entre tipos de neuronas
        self.compatibility_matrix = self._initialize_compatibility()
        
    def _initialize_compatibility(self) -> Dict[str, Dict[str, float]]:
        """Inicializa matriz de compatibilidad entre tipos de neuronas"""
        return {
            "animal": {
                "animal": 1.0,      # Comunicación nativa
                "micelial": 0.7     # Requiere conversión
            },
            "micelial": {
                "animal": 0.6,      # Requiere amplificación
                "micelial": 1.0     # Comunicación nativa
            }
        }
        
    def is_active(self) -> bool:
        """Verifica si la sinapsis está activa"""
        with self.lock:
            return self.is_active_flag and self.weight > 0.01
            
    def deactivate(self):
        """Desactiva la sinapsis"""
        with self.lock:
            self.is_active_flag = False
            
    def activate(self):
        """Activa la sinapsis"""
        with self.lock:
            self.is_active_flag = True
            
    def update_usage_frequency(self):
        """Actualiza la frecuencia de uso"""
        current_time = time.time()
        if self.last_transmission > 0:
            time_delta = current_time - self.last_transmission
            # Actualizar frecuencia (promedio exponencial)
            self.usage_frequency = 0.9 * self.usage_frequency + 0.1 / max(time_delta, 0.001)
        self.last_transmission = current_time
        
    @abstractmethod
    def transmit(self, signal_strength: float, source_neuron, context: Dict = None) -> Optional[Any]:
        """Método abstracto para transmitir señal"""
        pass
        
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de la sinapsis"""
        with self.lock:
            return {
                "synapse_id": self.synapse_id,
                "weight": self.weight,
                "threshold": self.threshold,
                "delay": self.delay,
                "age": self.age,
                "strength": self.strength,
                "usage_frequency": self.usage_frequency,
                "success_count": self.success_count,
                "failure_count": self.failure_count,
                "synapse_type": self.synapse_type.value,
                "signal_type": self.signal_type.value,
                "transmission_mode": self.transmission_mode.value
            }

# ============ SINAPSIS ESPECIALIZADAS ============

class ElectricalSynapse(SynapseBase):
    """Sinapsis eléctrica para comunicación rápida entre neuronas animales"""
    
    def __init__(self, synapse_id: str, source_neuron, target_neuron,
                 synapse_type: SynapseType = SynapseType.EXCITATORY):
        super().__init__(synapse_id, source_neuron, target_neuron,
                        synapse_type, SignalType.ELECTRICAL, TransmissionMode.FAST)
        
        # Propiedades específicas eléctricas
        self.conductance = 1.0  # Conductancia sináptica
        self.reversal_potential = 0.0 if synapse_type == SynapseType.EXCITATORY else -70.0
        self.time_constant = 0.001  # Constante de tiempo muy rápida
        
        # Propiedades de plasticidad
        self.ltp_threshold = 0.8    # Umbral para potenciación a largo plazo
        self.ltd_threshold = 0.3    # Umbral para depresión a largo plazo
        self.plasticity_window = 0.02  # Ventana temporal para plasticidad (20ms)
        
    def transmit(self, signal_strength: float, source_neuron, context: Dict = None) -> Optional[Any]:
        """Transmite señal eléctrica rápida"""
        with self.lock:
            if not self.is_active() or signal_strength < self.threshold:
                return None
                
            current_time = time.time()
            
            # Aplicar delay
            time.sleep(self.delay)
            
            # Calcular corriente sináptica
            synaptic_current = self.conductance * (self.reversal_potential - (-65.0)) * signal_strength * self.weight
            
            # Aplicar decaimiento temporal
            decay_factor = math.exp(-self.time_constant)
            final_signal = synaptic_current * decay_factor
            
            # Actualizar plasticidad
            self._update_plasticity(signal_strength, current_time)
            
            # Registrar transmisión
            self._record_transmission(signal_strength, final_signal, context, True)
            
            # Enviar señal a neurona objetivo
            if hasattr(self.target_neuron, 'receive_signal'):
                try:
                    result = self.target_neuron.receive_signal(final_signal, "electrical", context or {})
                    # Si la neurona no devuelve un valor, devolvemos el signal_strength procesado
                    return result if result is not None else final_signal
                except Exception as e:
                    print(f"Error en neurona objetivo (eléctrica): {e}")
                    return final_signal
            return final_signal
            
    def _update_plasticity(self, signal_strength: float, timestamp: float):
        """Actualiza la plasticidad sináptica"""
        if self.last_transmission > 0:
            time_diff = timestamp - self.last_transmission
            
            if time_diff <= self.plasticity_window:
                if signal_strength >= self.ltp_threshold:
                    # Potenciación a largo plazo
                    self.weight = min(2.0, self.weight * 1.1)
                elif signal_strength <= self.ltd_threshold:
                    # Depresión a largo plazo
                    self.weight = max(0.1, self.weight * 0.9)
                    
    def _record_transmission(self, input_strength: float, output_strength: float, 
                           context: Dict, success: bool):
        """Registra una transmisión en el historial"""
        timestamp = time.time()
        record = {
            "timestamp": timestamp,
            "input_strength": input_strength,
            "output_strength": output_strength,
            "context": context or {},
            "success": success
        }
        self.transmission_history.append(record)
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
            
        self.update_usage_frequency()

class ChemicalSynapse(SynapseBase):
    """Sinapsis química para comunicación lenta entre neuronas miceliales"""
    
    def __init__(self, synapse_id: str, source_neuron, target_neuron,
                 synapse_type: SynapseType = SynapseType.EXCITATORY):
        super().__init__(synapse_id, source_neuron, target_neuron,
                        synapse_type, SignalType.CHEMICAL, TransmissionMode.SLOW)
        
        # Propiedades químicas optimizadas - Ajustadas para reducir salida
        self.neurotransmitter_release_probability = 0.85  # Reducida para menor liberación
        self.synaptic_cleft_concentration = 0.0
        self.receptor_sensitivity = 1.5  # Reducida para menor respuesta
        self.diffusion_rate = 0.05      # Aumentada para dispersar más rápido
        self.degradation_rate = 0.03     # Aumentada para degradación más rápida
        
        # Sistema de vesículas optimizado - Ajustado para menor intensidad
        self.vesicle_pool = 2000         # Menor capacidad inicial
        self.vesicles_per_release = 8    # Menos vesículas por liberación
        self.vesicle_refill_rate = 15    # Relleno más lento
        
        # Neurotransmisores soportados
        self.supported_neurotransmitters = ["dopamine", "serotonin", "acetylcholine", "gaba", "glutamate"]
        self.primary_neurotransmitter = "dopamine"
        
    def transmit(self, signal_strength: float, source_neuron, context: Dict = None) -> Optional[Any]:
        """Transmite señal química lenta con mejor manejo de señales bajas"""
        with self.lock:
            try:
                # Asegurar que la señal tenga un valor mínimo
                signal_strength = max(0.0, float(signal_strength or 0.0))
                context = context or {}
                
                # Umbral dinámico basado en el contexto
                context_modulation = float(context.get('modulation', 1.0))
                dynamic_threshold = max(0.01, self.threshold * (1.0 / context_modulation))
                
                # Verificar si la señal supera el umbral dinámico
                if not self.is_active() or signal_strength < dynamic_threshold:
                    self._record_transmission(signal_strength, 0.0, context, False)
                    return 0.0  # Devolver 0 en lugar de None para consistencia
                
                # Asegurar un mínimo de vesículas disponibles
                min_vesicles = max(5, self.vesicles_per_release)  # Mínimo de 5 vesículas
                if self.vesicle_pool < min_vesicles:
                    self.vesicle_pool += self.vesicle_refill_rate * 2  # Relleno más rápido
                    if self.vesicle_pool < min_vesicles:
                        self._record_transmission(signal_strength, 0.0, context, False)
                        return 0.0
                
                # Aplicar modulación contextual
                modulated_signal = signal_strength * context_modulation
                
                # Liberar neurotransmisores con manejo mejorado
                release_success = self._release_neurotransmitters(
                    modulated_signal, 
                    self.primary_neurotransmitter
                )
                
                if not release_success:
                    self._record_transmission(signal_strength, 0.0, context, False)
                    return 0.0
                
                # Calcular respuesta postsináptica con señal modulada
                response = self._calculate_postsynaptic_response(
                    modulated_signal, 
                    self.primary_neurotransmitter,
                    context
                )
                
                # Asegurar un valor de retorno válido
                if response is None:
                    response = 0.0
                else:
                    # Aplicar límites a la respuesta
                    response = max(0.0, min(float(response), 200.0))  # Límite superior de 200
                
                # Actualizar estado químico
                self._update_chemical_state(time.time())
                
                # Registrar transmisión exitosa
                self._record_transmission(signal_strength, response, context, response > 0)
                
                return response
                
            except Exception as e:
                print(f"Error en ChemicalSynapse.transmit: {str(e)}")
                self.failure_count += 1
                self._record_transmission(signal_strength, 0.0, context or {}, False)
                return 0.0  # Devolver 0 en lugar de None para consistencia
            
    def _release_neurotransmitters(self, signal_strength: float, neurotransmitter_type: str) -> bool:
        """Libera neurotransmisores en la hendidura sináptica con mejoras"""
        # Reabastecimiento automático mejorado
        if self.vesicle_pool < self.vesicles_per_release:
            self.vesicle_pool = min(3000, self.vesicle_pool + self.vesicle_refill_rate)
            return False
            
        # Calcular probabilidad de liberación con factores de mejora
        release_probability = min(
            0.99,  # Límite superior para evitar saturación
            self.neurotransmitter_release_probability * 
            (signal_strength ** 0.8) *  # Mejor escalado con la fuerza de la señal
            (self.weight ** 1.2)         # Mayor influencia del peso sináptico
        )
        
        # En pruebas, siempre liberar si hay suficientes vesículas
        if random.random() > release_probability:
            return False
        
        # Liberación mejorada con retroalimentación positiva
        release_multiplier = 1.0
        if self.synaptic_cleft_concentration < 0.5:  # Si la concentración es baja
            release_multiplier = 1.5  # Liberar más
            
        vesicles_to_release = int(self.vesicles_per_release * release_multiplier)
        self.vesicle_pool = max(0, self.vesicle_pool - vesicles_to_release)
        
        # Aumentar concentración con límite superior
        concentration_increase = min(
            1.5,  # Límite superior de concentración
            vesicles_to_release * 0.15  # Aumento por vesícula
        )
        self.synaptic_cleft_concentration = min(
            2.0,  # Límite absoluto de concentración
            self.synaptic_cleft_concentration + concentration_increase
        )
        
        return True
        
    def _calculate_postsynaptic_response(self, signal_strength: float, 
                                       neurotransmitter_type: str, 
                                       context: Dict) -> float:
        """Calcula la respuesta postsináptica con mejoras significativas"""
        # Factores de sensibilidad mejorados
        sensitivity_factors = {
            "gaba": 1.5,          # Inhibitorio pero con mayor impacto
            "dopamine": 3.5,      # Mayor efecto en la motivación y recompensa
            "serotonin": 2.5,     # Mejor regulación del estado de ánimo
            "acetylcholine": 2.8, # Mejor para aprendizaje y memoria
            "glutamate": 3.0      # Principal neurotransmisor excitatorio
        }
        
        # Obtener factor de sensibilidad, con valor por defecto
        sensitivity_factor = sensitivity_factors.get(neurotransmitter_type, 2.0)
        
        # Aplicar modulación por contexto (si existe)
        context_modulation = 1.0
        if context:
            # Modulación por emoción (si está presente)
            if "emotion" in context:
                if context["emotion"] in ["excitement", "curiosity"]:
                    context_modulation *= 1.5
            # Modulación por urgencia (si está presente)
            if "urgency" in context:
                if context["urgency"] == "high":
                    context_modulation *= 1.8
        
        # Calcular respuesta con factores mejorados
        base_response = (signal_strength * 
                        self.weight * 
                        self.receptor_sensitivity * 
                        sensitivity_factor * 
                        context_modulation * 
                        15.0)  # Factor de amplificación aumentado
        
        # Asegurar límites razonables
        return min(150.0, max(10.0, base_response))  # Rango entre 10 y 150
        
    def _update_chemical_state(self, timestamp: float):
        """Actualiza el estado químico de la sinapsis"""
        # Difusión y degradación
        self.synaptic_cleft_concentration *= (1 - self.degradation_rate)
        
        # Recuperación de vesículas mejorada
        self.vesicle_pool = min(2000, self.vesicle_pool + self.vesicle_refill_rate)
        
    def _record_transmission(self, input_strength: float, output_strength: float, 
                           context: Dict, success: bool):
        """Registra una transmisión química"""
        timestamp = time.time()
        neurotransmitter_type = context.get("neurotransmitter", self.primary_neurotransmitter) \
                             if context else self.primary_neurotransmitter
                             
        record = {
            "timestamp": timestamp,
            "input_strength": input_strength,
            "output_strength": output_strength,
            "context": context or {},
            "neurotransmitter": neurotransmitter_type,
            "success": success,
            "vesicle_pool": self.vesicle_pool,
            "cleft_concentration": self.synaptic_cleft_concentration
        }
        self.transmission_history.append(record)
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
            

class HybridSynapse(SynapseBase):
    """Sinapsis híbrida para comunicación entre neuronas animales y miceliales"""
    
    def __init__(self, synapse_id: str, source_neuron, target_neuron, **kwargs):
        """Inicializa una sinapsis híbrida con capacidades adaptativas mejoradas"""
        super().__init__(synapse_id, source_neuron, target_neuron,
                        SynapseType.HYBRID, SignalType.HYBRID, TransmissionMode.ADAPTIVE)
        
        # Estado de carga del sistema
        self._last_cpu_usage = 0.0
        self._last_memory_usage = 0.0
        self._last_adjustment_time = time.time()
        self._adjustment_interval = 5.0  # segundos entre ajustes
        
        # Propiedades de conversión optimizadas - Ajustadas para mayor salida
        self.electrical_to_chemical_ratio = 10.0  # Aumentada para mayor conversión
        self.chemical_to_electrical_ratio = 8.0   # Mayor conversión química a eléctrica
        self.conversion_efficiency = 4.2          # Eficiencia mejorada
        
        # Adaptabilidad dinámica mejorada
        self.adaptation_rate = 0.1        # Adaptación más rápida
        self.learning_rate = 0.04         # Tasa de aprendizaje aumentada
        self.current_mode = TransmissionMode.ADAPTIVE
        self.signal_amplification = 7.8    # Mayor amplificación para alcanzar rango objetivo
        
        # Estado de la sinapsis mejorado
        self.last_signal_strength = 0.0
        self.signal_variability = 0.0
        self.transmission_history = []
        
        # Umbrales adaptativos optimizados
        self.dynamic_threshold = 0.06     # Umbral más bajo para mayor sensibilidad
        self.min_signal_strength = 30.0   # Mínimo absoluto para señales (aumentado)
        self.target_range = (35.0, 65.0)  # Rango objetivo ligeramente mayor
        
        # Optimización de rendimiento
        self._mid_range = (self.target_range[0] + self.target_range[1]) / 2
        self._range_width = self.target_range[1] - self.target_range[0]
        self._last_calculation_time = 0
        self._cache_ttl = 0.04  # Caché más frecuente (40ms)
        self._cached_normalization = {}
        
        # Historial de señales para análisis de tendencia
        self.signal_history = deque(maxlen=10)  # Aumentado para mejor análisis
        
        # Pre-cálculo de constantes para optimización
        self._sig_scale = 12.0 / self._range_width  # Pendiente más pronunciada
        self._exp_neg_scale = math.exp(-12.0)       # Rango extendido
        
    def transmit(self, signal_strength: float, source_neuron, context: Dict = None) -> Optional[Any]:
        """Transmite señal adaptándose dinámicamente al tipo de neurona objetivo con mejoras"""
        with self.lock:
            try:
                # Validar y normalizar señal de entrada
                signal_strength = max(0.0, float(signal_strength or 0.0))
                context = context or {}
                
                # Actualizar historial de señales
                self.signal_history.append(signal_strength)
                
                # Verificar si la sinapsis está activa
                if not self.is_active():
                    self._record_transmission(signal_strength, 0.0, context, False)
                    return 0.0  # Devolver 0 en lugar de None para consistencia
                
                # Calcular umbral dinámico basado en el historial
                self._update_dynamic_threshold(signal_strength)
                
                # Aplicar modulación contextual
                context_modulation = float(context.get('modulation', 1.0))
                modulated_signal = signal_strength * context_modulation
                
                # Determinar modo de transmisión adaptativo
                self._adapt_transmission_mode(modulated_signal, context)
                
                # Determinar tipos de neuronas
                source_type = self._get_neuron_type(source_neuron)
                target_type = self._get_neuron_type(self.target_neuron)
                
                # Realizar la conversión adecuada con manejo mejorado
                result = None
                try:
                    if source_type == "animal" and target_type == "micelial":
                        result = self._electrical_to_chemical_transmission(
                            modulated_signal, source_neuron, context)
                    elif source_type == "micelial" and target_type == "animal":
                        result = self._chemical_to_electrical_transmission(
                            modulated_signal, source_neuron, context)
                    else:
                        # Mismo tipo de neurona, aplicar modulación mínima
                        result = modulated_signal
                except Exception as e:
                    print(f"Error en conversión de señal: {e}")
                    result = 0.0
                
                # Asegurar que tenemos un resultado válido
                if result is None:
                    self._record_transmission(signal_strength, 0.0, context, False)
                    return 0.0
                
                # Aplicar ganancia y normalización
                try:
                    # Aplicar amplificación con límites y respuesta no lineal
                    # Usar una curva de respuesta más agresiva para señales bajas
                    base_amplified = (result ** 0.75) * self.signal_amplification * 1.4
                    
                    # Ajuste dinámico basado en el historial (solo si hay suficiente historial)
                    if len(self.signal_history) >= 3:
                        recent_avg = (self.signal_history[-1] + self.signal_history[-2] + self.signal_history[-3]) / 3
                        # Si la señal tiende a ser baja, aumentar la ganancia
                        if recent_avg < self._mid_range * 0.9:
                            base_amplified *= 1.1
                        # Si la señal tiende a ser alta, reducir la ganancia
                        elif recent_avg > self._mid_range * 1.1:
                            base_amplified *= 0.9
                    
                    # Usar función optimizada para normalización con caché
                    normalized = self._calculate_normalized_signal(base_amplified)
                    
                    # Aplicar límites absolutos
                    final_result = max(self.min_signal_strength, min(normalized, 100.0))
                    
                    # Actualizar estado de la sinapsis
                    self._update_synapse_state(signal_strength, final_result, time.time())
                    
                    # Calcular y aplicar delay adaptativo
                    delay = self._calculate_adaptive_delay(signal_strength, final_result, context)
                    if delay > 0:
                        time.sleep(min(delay, 0.1))  # Limitar delay máximo a 100ms
                    
                    # Registrar transmisión exitosa
                    self._record_transmission(signal_strength, final_result, context, True)
                    
                    return final_result
                    
                except Exception as e:
                    print(f"Error en normalización de señal: {e}")
                    self._record_transmission(signal_strength, 0.0, context, False)
                    return 0.0
                
            except Exception as e:
                print(f"Error crítico en HybridSynapse.transmit: {e}")
                self._record_transmission(signal_strength, 0.0, context or {}, False)
                return 0.0
                
    def _calculate_normalized_signal(self, base_signal: float) -> float:
        """Calcula la señal normalizada con caché para mejorar rendimiento"""
        # Usar caché si el cálculo es reciente y para la misma señal
        current_time = time.time()
        signal_key = round(base_signal, 2)  # Redondear para agrupar señales similares
        
        if (current_time - self._last_calculation_time < self._cache_ttl and 
            signal_key in self._cached_normalization):
            return self._cached_normalization[signal_key]
        
        # Calcular valor normalizado
        normalized = min(max(base_signal, self.target_range[0] * 0.9), 
                        self.target_range[1] * 1.1)
        
        # Aplicar curva sigmoide optimizada (versión más rápida)
        x = (normalized - self._mid_range) * self._sig_scale
        # Aproximación más rápida de la sigmoide
        if x < -6.0:
            sigmoid = 0.0
        elif x > 6.0:
            sigmoid = 1.0
        else:
            sigmoid = 1.0 / (1.0 + math.exp(-x))
            
        normalized = self.target_range[0] + self._range_width * sigmoid
        
        # Actualizar caché
        self._cached_normalization = {signal_key: normalized}
        self._last_calculation_time = current_time
        
        return normalized
        
    def _get_neuron_type(self, neuron) -> str:
        """Determina si una neurona es de tipo animal o micelial"""
        if hasattr(neuron, 'neuron_type'):
            return neuron.neuron_type
        
        # Intentar inferir el tipo basado en la clase
        class_name = neuron.__class__.__name__.lower()
        if 'animal' in class_name or 'visual' in class_name or 'decision' in class_name:
            return 'animal'
        elif 'micelial' in class_name or 'coordinator' in class_name or 'orchestrator' in class_name:
            return 'micelial'
        
        # Valor por defecto si no se puede determinar
        return 'animal'
        
    def _update_dynamic_threshold(self, signal_strength: float):
        """Actualiza el umbral dinámico basado en el historial de señales"""
        if self.last_signal_strength > 0:
            diff = abs(signal_strength - self.last_signal_strength)
            self.signal_variability = 0.9 * self.signal_variability + 0.1 * diff
        
        if self.signal_variability > 0:
            self.dynamic_threshold = max(0.05, 0.5 * self.signal_variability)
        
        self.last_signal_strength = signal_strength
    
    def _adapt_transmission_mode(self, signal_strength: float, context: Dict):
        """Adapta el modo de transmisión basado en la señal y contexto"""
        if "force_mode" in context:
            self.current_mode = context["force_mode"]
            return
            
        if signal_strength > 50.0:
            self.current_mode = TransmissionMode.FAST
        elif signal_strength < 10.0:
            self.current_mode = TransmissionMode.SLOW
        else:
            self.current_mode = TransmissionMode.ADAPTIVE
    
    def _calculate_adaptive_delay(self, signal_strength: float, result: float, 
                                context: Dict) -> float:
        """Calcula el retraso adaptativo basado en la señal y contexto"""
        base_delay = self.delay
        
        if self.current_mode == TransmissionMode.FAST:
            base_delay *= 0.4
        elif self.current_mode == TransmissionMode.SLOW:
            base_delay *= 1.5
            
        if signal_strength > 0:
            signal_factor = 1.0 / (1.0 + math.log1p(signal_strength) * 0.1)
            base_delay *= signal_factor
            
        if context and "priority" in context:
            base_delay *= max(0.1, 1.0 - (context["priority"] * 0.5))
            
        return max(0.001, base_delay)
    
    def _update_synapse_state(self, input_strength: float, output_strength: float, 
                            timestamp: float):
        """Actualiza el estado interno de la sinapsis"""
        if input_strength > 0:
            efficiency = output_strength / input_strength
            self.weight = min(2.0, max(0.1, self.weight + (efficiency - 1.0) * self.learning_rate))
        
        self.transmission_history.append({
            'timestamp': timestamp,
            'input': input_strength,
            'output': output_strength,
            'efficiency': output_strength / max(1.0, input_strength),
            'weight': self.weight
        })
        
        if len(self.transmission_history) > 1000:
            self.transmission_history = self.transmission_history[-1000:]
    
    def _electrical_to_chemical_transmission(self, signal_strength: float, 
                                           source_neuron, 
                                           context: Dict = None):
        """Convierte señal eléctrica a química con amplificación mejorada"""
        try:
            # Factor de adaptación basado en la señal de entrada
            adaptation_factor = 1.0 + (0.5 * math.tanh((signal_strength - 10.0) / 5.0))
            
            # Aplicar conversión con ganancia adaptativa
            base_conversion = (signal_strength * 
                             self.electrical_to_chemical_ratio * 
                             self.conversion_efficiency)
            
            # Aplicar adaptación dinámica
            adapted_conversion = base_conversion * adaptation_factor
            
            # Aplicar peso sináptico con saturación suave
            weight_factor = 1.0 + (self.weight - 1.0) * 0.8
            chemical_signal = adapted_conversion * weight_factor * self.signal_amplification
            
            # Aplicar modulación contextual
            if context and "modulation" in context:
                chemical_signal *= max(0.5, min(2.0, context["modulation"]))
            
            # Enviar señal a la neurona objetivo
            if hasattr(self.target_neuron, 'receive_signal'):
                enriched_context = {
                    **(context or {}),
                    "original_signal": signal_strength,
                    "conversion_type": "electrical_to_chemical",
                    "timestamp": time.time()
                }
                
                result = self.target_neuron.receive_signal(
                    chemical_signal, 
                    "converted_electrical", 
                    enriched_context
                )
                
                return result if result is not None else chemical_signal
                
            return chemical_signal
            
        except Exception as e:
            print(f"Error en conversión eléctrica a química: {e}")
            return max(0, signal_strength * 0.8)  # Retorno seguro en caso de error
        
    def _chemical_to_electrical_transmission(self, signal_strength: float, 
                                           source_neuron, 
                                           context: Dict = None):
        """Convierte señal química a eléctrica con amplificación mejorada"""
        try:
            # Factor de adaptación basado en la señal de entrada
            adaptation_factor = 1.0 + (0.4 * math.tanh((signal_strength - 15.0) / 5.0))
            
            # Aplicar conversión con ganancia adaptativa
            base_conversion = (signal_strength * 
                             self.chemical_to_electrical_ratio * 
                             self.conversion_efficiency)
            
            # Aplicar adaptación dinámica
            adapted_conversion = base_conversion * adaptation_factor
            
            # Aplicar peso sináptico con saturación suave
            weight_factor = 1.0 + (self.weight - 1.0) * 0.7
            electrical_signal = adapted_conversion * weight_factor * self.signal_amplification
            
            # Aplicar modulación contextual
            if context and "modulation" in context:
                electrical_signal *= max(0.6, min(1.8, context["modulation"]))
            
            # Enviar señal a la neurona objetivo
            if hasattr(self.target_neuron, 'receive_signal'):
                enriched_context = {
                    **(context or {}),
                    "original_signal": signal_strength,
                    "conversion_type": "chemical_to_electrical",
                    "timestamp": time.time(),
                    "conversion_ratio": self.chemical_to_electrical_ratio,
                    "efficiency": self.conversion_efficiency
                }
                
                result = self.target_neuron.receive_signal(
                    electrical_signal, 
                    "converted_chemical", 
                    enriched_context
                )
                
                # Asegurar que la señal de retorno sea válida
                return result if result is not None else electrical_signal
                
            return electrical_signal
            
        except Exception as e:
            print(f"Error en conversión química a eléctrica: {e}")
            # Retornar señal segura en caso de error
            return max(0, signal_strength * self.chemical_to_electrical_ratio * 0.7)
        
    def _record_transmission(self, input_strength: float, output_strength: float, 
                           context: Dict, success: bool):
        """Registra una transmisión híbrida"""
        timestamp = time.time()
        record = {
            "timestamp": timestamp,
            "input_strength": input_strength,
            "output_strength": output_strength,
            "context": context or {},
            "mode": self.current_mode.value,
            "success": success
        }
        self.transmission_history.append(record)
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
            
        self.update_usage_frequency()

class AdaptiveSynapsePool:
    """Pool adaptativo de sinapsis para gestión eficiente"""
    
    def __init__(self, initial_pool_size: int = 100):
        self.available_synapses = deque(maxlen=initial_pool_size * 2)
        self.active_synapses = {}
        self.synapse_counter = 0
        self.lock = RLock()
        
        # Pre-crear sinapsis
        self._prepopulate_pool(initial_pool_size)
        
    def _prepopulate_pool(self, size: int):
        """Pre-popula el pool con sinapsis genéricas"""
        for _ in range(size):
            synapse_id = f"syn_pre_{self.synapse_counter}"
            # Crear sinapsis base (serán reconfiguradas al conectar)
            synapse = ElectricalSynapse(synapse_id, None, None)
            self.available_synapses.append(synapse)
            self.synapse_counter += 1
            
    def acquire_synapse(self, synapse_type: str, source_neuron, target_neuron) -> SynapseBase:
        """Adquiere una sinapsis del pool"""
        with self.lock:
            synapse = self._find_compatible_synapse(synapse_type)
            
            if synapse is None:
                # Crear nueva sinapsis si no hay disponibles
                synapse_id = f"syn_{self.synapse_counter}"
                synapse = self._create_synapse(synapse_type, synapse_id, source_neuron, target_neuron)
                self.synapse_counter += 1
            else:
                # Reconfigurar sinapsis existente
                self._reconfigure_synapse(synapse, synapse_type, source_neuron, target_neuron)
                
            # Registrar como activa
            self.active_synapses[synapse.synapse_id] = synapse
            return synapse
            
    def release_synapse(self, synapse: SynapseBase):
        """Devuelve una sinapsis al pool"""
        with self.lock:
            # Resetear estado de sinapsis
            synapse.source_neuron = None
            synapse.target_neuron = None
            synapse.weight = 1.0
            synapse.threshold = 0.1
            synapse.strength = 1.0
            synapse.transmission_history.clear()
            synapse.success_count = 0
            synapse.failure_count = 0
            
            # Añadir al pool si hay espacio
            if len(self.available_synapses) < self.available_synapses.maxlen:
                self.available_synapses.append(synapse)
                
            # Remover de activas
            if synapse.synapse_id in self.active_synapses:
                del self.active_synapses[synapse.synapse_id]
                
    def _determine_optimal_synapse_type(self, source_neuron, target_neuron) -> str:
        """Determina el tipo óptimo de sinapsis entre dos neuronas"""
        source_type = getattr(source_neuron, 'neuron_type', 'unknown')
        target_type = getattr(target_neuron, 'neuron_type', 'unknown')
        
        if source_type == "animal" and target_type == "animal":
            return "electrical"
        elif source_type == "micelial" and target_type == "micelial":
            return "chemical"
        else:
            return "hybrid"
            
    def _find_compatible_synapse(self, synapse_type: str) -> Optional[SynapseBase]:
        """Busca una sinapsis compatible en el pool"""
        for synapse in self.available_synapses:
            if self._is_synapse_compatible(synapse, synapse_type):
                self.available_synapses.remove(synapse)
                return synapse
        return None
        
    def _is_synapse_compatible(self, synapse: SynapseBase, desired_type: str) -> bool:
        """Verifica si una sinapsis es compatible con el tipo deseado"""
        # Mapeo de tipos deseados a clases
        type_mapping = {
            "fast_excitatory": ElectricalSynapse,
            "fast_inhibitory": ElectricalSynapse,
            "slow_modulatory": ChemicalSynapse,
            "hybrid": HybridSynapse
        }
        
        if desired_type in type_mapping:
            return isinstance(synapse, type_mapping[desired_type])
        return False
        
    def _create_synapse(self, synapse_type: str, synapse_id: str, 
                       source_neuron, target_neuron, **kwargs) -> SynapseBase:
        """Crea una nueva sinapsis del tipo especificado"""
        synapse_classes = {
            "electrical": ElectricalSynapse,
            "chemical": ChemicalSynapse,
            "hybrid": HybridSynapse
        }
        
        # Determinar tipo óptimo si no se especifica
        if synapse_type not in synapse_classes:
            synapse_type = self._determine_optimal_synapse_type(source_neuron, target_neuron)
            
        return synapse_classes[synapse_type](synapse_id, source_neuron, target_neuron, **kwargs)
        
    def _reconfigure_synapse(self, synapse: SynapseBase, synapse_type: str, 
                           source_neuron, target_neuron):
        """Reconfigura una sinapsis existente"""
        synapse.source_neuron = source_neuron
        synapse.target_neuron = target_neuron
        synapse.synapse_id = f"syn_{self.synapse_counter}"
        self.synapse_counter += 1
        
        # Resetear propiedades
        synapse.weight = 1.0
        synapse.threshold = 0.1
        synapse.strength = 1.0
        synapse.transmission_history.clear()
        synapse.success_count = 0
        synapse.failure_count = 0

class NetworkConnector:
    """Conector de redes para establecer conexiones entre neuronas"""
    
    def __init__(self, synapse_pool: AdaptiveSynapsePool):
        self.synapse_pool = synapse_pool
        self.connections = []
        self.lock = RLock()
        
    def connect_neurons(self, source_neuron, target_neuron, connection_type: str = "adaptive") -> SynapseBase:
        """Conecta dos neuronas con una sinapsis"""
        with self.lock:
            # Determinar tipo de sinapsis óptimo
            synapse_type = self._determine_connection_type(source_neuron, target_neuron, connection_type)
            
            # Adquirir sinapsis del pool
            synapse = self.synapse_pool.acquire_synapse(synapse_type, source_neuron, target_neuron)
            
            # Configurar parámetros específicos
            self._configure_synapse_parameters(synapse, source_neuron, target_neuron)
            
            # Registrar conexión
            connection_record = {
                "source": source_neuron.neuron_id,
                "target": target_neuron.neuron_id,
                "synapse_id": synapse.synapse_id,
                "type": synapse_type
            }
            self.connections.append(connection_record)
            
            return synapse
            
    def _determine_connection_type(self, source_neuron, target_neuron, requested_type: str) -> str:
        """Determina el tipo de conexión óptimo"""
        if requested_type != "adaptive":
            return requested_type
            
        source_type = getattr(source_neuron, 'neuron_type', 'unknown')
        target_type = getattr(target_neuron, 'neuron_type', 'unknown')
        
        if source_type == "animal" and target_type == "animal":
            return "electrical"
        elif source_type == "micelial" and target_type == "micelial":
            return "chemical"
        else:
            return "hybrid"
            
    def _configure_synapse_parameters(self, synapse: SynapseBase, source_neuron, target_neuron):
        """Configura parámetros específicos de la sinapsis"""
        # Obtener funciones de las neuronas
        source_function = getattr(source_neuron, 'function', 'generic')
        target_function = getattr(target_neuron, 'function', 'generic')
        
        # Ajustar peso basado en funciones
        if source_function == "excitatory":
            synapse.weight = 1.0
        elif source_function == "modulatory":
            synapse.weight = 0.6  # Modulación moderada
        elif source_function == "inhibitory":
            synapse.weight = 1.2  # Inhibición fuerte
            
        # Ajustar umbral
        if target_function == "motor":
            synapse.threshold = 0.2  # Motor neurons necesitan más señal
        elif target_function == "sensory":
            synapse.threshold = 0.05  # Sensory neurons son más sensibles
            
        # Configurar delay basado en tipos de neuronas
        source_speed = getattr(source_neuron, 'processing_speed', 'medium')
        target_speed = getattr(target_neuron, 'processing_speed', 'medium')
        
        if source_speed == "fast" and target_speed == "fast":
            synapse.delay = 0.001  # 1ms
        elif source_speed == "slow" or target_speed == "slow":
            synapse.delay = 0.1    # 100ms
        else:
            synapse.delay = 0.01   # 10ms (por defecto)

class SynapseManager:
    """Gestor para múltiples sinapsis en la red"""
    
    def __init__(self):
        self.synapses = {}
        self.maintenance_interval = 300.0  # 5 minutos
        self.last_maintenance = time.time()
        self.synapse_pool = AdaptiveSynapsePool(500)
        self.connector = NetworkConnector(self.synapse_pool)
        
    def add_synapse(self, synapse: SynapseBase):
        """Agrega una sinapsis al gestor"""
        self.synapses[synapse.synapse_id] = synapse
        
    def remove_synapse(self, synapse_id: str):
        """Remueve una sinapsis del gestor"""
        if synapse_id in self.synapses:
            synapse = self.synapses[synapse_id]
            # Devolver al pool
            self.synapse_pool.release_synapse(synapse)
            del self.synapses[synapse_id]
            
    def connect_neurons(self, source_neuron, target_neuron, connection_type: str = "adaptive") -> SynapseBase:
        """Conecta dos neuronas"""
        synapse = self.connector.connect_neurons(source_neuron, target_neuron, connection_type)
        self.add_synapse(synapse)
        return synapse
        
    def transmit_signal(self, synapse_id: str, signal_strength: float, 
                       source_neuron, context: Dict = None) -> Optional[Any]:
        """Transmite una señal a través de una sinapsis específica"""
        if synapse_id in self.synapses:
            synapse = self.synapses[synapse_id]
            return synapse.transmit(signal_strength, source_neuron, context)
        return None
        
    def run_maintenance(self):
        """Ejecuta tareas de mantenimiento periódico"""
        current_time = time.time()
        if current_time - self.last_maintenance >= self.maintenance_interval:
            self._perform_maintenance()
            self.last_maintenance = current_time
            
    def _perform_maintenance(self):
        """Realiza tareas de mantenimiento en sinapsis"""
        synapses_to_remove = []
        current_time = time.time()
        
        for synapse_id, synapse in list(self.synapses.items()):
            try:
                # Verificar salud de la sinapsis
                if synapse.failure_count > synapse.success_count * 2:
                    # Sinapsis problemática - considerar remover
                    synapses_to_remove.append(synapse_id)
                else:
                    # Resetear contadores periódicamente
                    synapse.success_count = max(0, synapse.success_count - 1)
                    synapse.failure_count = max(0, synapse.failure_count - 1)
                    
                    # Actualizar estado de actividad
                    if hasattr(synapse, 'last_transmission'):
                        time_since_last = current_time - synapse.last_transmission
                        synapse.is_active_flag = time_since_last < 60.0  # 1 minuto de inactividad
                    else:
                        synapse.last_transmission = 0.0
                        synapse.is_active_flag = False
                        
            except Exception as e:
                print(f"Error en mantenimiento de sinapsis {synapse_id}: {str(e)}")
                continue
                
        # Remover sinapsis problemáticas
        for synapse_id in synapses_to_remove:
            self.remove_synapse(synapse_id)
            
    def get_synapse_stats(self):
        """Obtiene estadísticas de las sinapsis
        
        Returns:
            Dict con estadísticas de las sinapsis
        """
        total = len(self.synapses)
        active = 0
        total_weight = 0.0
        current_time = time.time()
        
        for synapse in self.synapses.values():
            try:
                # Verificar si la sinapsis está activa usando múltiples criterios
                is_active = False
                
                # 1. Usar el flag is_active si existe
                if hasattr(synapse, 'is_active_flag') and synapse.is_active_flag:
                    is_active = True
                # 2. Verificar última transmisión reciente (últimos 5 segundos)
                elif hasattr(synapse, 'last_transmission') and \
                     (current_time - synapse.last_transmission) < 5.0:
                    is_active = True
                # 3. Verificar si hay actividad reciente en el historial
                elif hasattr(synapse, 'transmission_history') and synapse.transmission_history:
                    last_activity = max(
                        [record.get('timestamp', 0) for record in synapse.transmission_history],
                        default=0
                    )
                    if (current_time - last_activity) < 5.0:
                        is_active = True
                
                if is_active:
                    active += 1
                
                # Calcular peso promedio
                if hasattr(synapse, 'weight') and synapse.weight is not None:
                    total_weight += abs(synapse.weight)  # Usar valor absoluto para el peso
                elif hasattr(synapse, 'strength') and synapse.strength is not None:
                    total_weight += abs(synapse.strength)  # Usar valor absoluto para la fuerza
                    
            except Exception as e:
                print(f"[SynapseManager] Error en get_synapse_stats: {str(e)}")
                continue
                
        avg_weight = total_weight / max(1, total) if total > 0 else 0.0
        
        return {
            'total': total,
            'active': active,
            'avg_weight': round(avg_weight, 2)
        }

# Ejemplo de uso con manejo de errores
if __name__ == "__main__":
    print("=== Sistema Avanzado de Sinapsis para Red Híbrida ===")
    
    try:
        # Importar las funciones de creación correctas
        # Importaciones locales ya realizadas al inicio
        print("✓ Módulos importados correctamente")
        
        # Crear neuronas de ejemplo usando tipos válidos
        print("Creando neuronas...")
        visual_neuron = create_cognitive_animal_neuron("visual_feature_extractor", "V1_001", feature_type="edge_vertical")
        decision_neuron = create_cognitive_animal_neuron("decision_maker", "DM_001") 
        coordinator = create_cognitive_micelial_neuron("global_coherence_coordinator", "GCC_001")
        orchestrator = create_cognitive_micelial_neuron("deep_reflection_orchestrator", "DRO_001")
        
        print("✓ Neuronas creadas exitosamente")
        
        # Crear pool de sinapsis y conector
        synapse_pool = AdaptiveSynapsePool(initial_pool_size=500)
        connector = NetworkConnector(synapse_pool)
        
        # Establecer conexiones
        synapse1 = connector.connect_neurons(visual_neuron, decision_neuron, "electrical")  # Animal → Animal
        synapse2 = connector.connect_neurons(coordinator, orchestrator, "chemical")        # Micelial → Micelial
        synapse3 = connector.connect_neurons(visual_neuron, coordinator, "hybrid")         # Animal → Micelial (híbrida)
        
        print(f"Creadas {3} sinapsis de diferentes tipos:")
        print(f"- {synapse1.__class__.__name__}: {synapse1.synapse_id}")
        print(f"- {synapse2.__class__.__name__}: {synapse2.synapse_id}")
        print(f"- {synapse3.__class__.__name__}: {synapse3.synapse_id}")
        
        # Simular transmisión
        print("=== Simulación de Transmisión ===")
        
        # Transmisión 1: Animal → Animal (rápida, eléctrica)
        result1 = synapse1.transmit(
            signal_strength=0.8,
            source_neuron=visual_neuron,
            context={"context": "visual_processing", "emotion": "focus"}
        )
        
        # Transmisión 2: Micelial → Micelial (lenta, química, conceptual)
        print(f"\nTransmisión micelial-micelial:")
        print(f"- Estado inicial de la sinapsis: {synapse2.synapse_id}")
        print(f"- Vesículas disponibles: {synapse2.vesicle_pool}")
        print(f"- Señal a transmitir: 0.6")
        
        result2 = synapse2.transmit(
            signal_strength=0.6,
            source_neuron=coordinator,
            context={
                "context": "coherence_check",
                "concept": "existential_stability",
                "abstraction_level": 4,
                "neurotransmitter": "dopamine"  # Ensure we use a supported neurotransmitter
            }
        )
        
        print(f"- Vesículas después de la transmisión: {synapse2.vesicle_pool}")
        print(f"- Concentración en hendidura: {synapse2.synaptic_cleft_concentration:.2f}")
        
        # Transmisión 3: Animal → Micelial (híbrida: emoción → concepto)
        result3 = synapse3.transmit(
            signal_strength=0.7,
            source_neuron=visual_neuron,
            context={
                "context": "cross_modal",
                "emotion": "curiosity",
                "sensory_input": "complex_pattern"
            }
        )
        
        print(f"Resultado transmisión animal-animal: {result1}")
        print(f"Resultado transmisión micelial-micelial: {result2}")
        print(f"Resultado transmisión híbrida: {result3}")
        
        print("Sistema de sinapsis inicializado y listo para conectar neuronas animales y miceliales.")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("\nAyuda para diagnóstico:")
        print("1. Verifica que los archivos 'animal.py' y 'micelial.py' estén en el mismo directorio que 'synapse.py'")
        print("2. Asegúrate de que ambos archivos contengan las funciones:")
        print("   - animal.py debe tener 'create_cognitive_animal_neuron'")
        print("   - micelial.py debe tener 'create_cognitive_micelial_neuron'")
        print("3. Verifica que no haya errores de sintaxis en esos archivos")
        
        # Diagnóstico adicional
        import os
        current_dir = os.getcwd()
        print(f"\nDirectorio actual: {current_dir}")
        try:
            files = os.listdir(current_dir)
            print(f"Archivos en el directorio: {[f for f in files if f in ['animal.py', 'micelial.py', 'synapse.py']]}")
        except:
            print("No se pudo listar el directorio")
        
    except Exception as e:
        print(f"❌ Error durante la ejecución: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()