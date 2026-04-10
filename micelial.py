# micelial.py
"""
Sistema avanzado de neuronas miceliales cognitivas para pensamiento profundo.
Inspirado en redes miceliales pero optimizado para procesamiento conceptual,
integración de conocimiento y coordinación cognitiva de larga duración.
Compatible con neuronas animales para pensamiento híbrido.
"""

import time
import json
import hashlib
import os
import sys
from abc import ABC, abstractmethod
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import RLock, Event
from typing import Any, Dict, List, Set, Optional, Callable, Tuple
import math
from monitoring import log_neuron_error


class CognitiveMicelialNeuronBase(ABC):
    """
    Clase base abstracta para neuronas miceliales cognitivas.
    Optimizada para pensamiento profundo, integración conceptual y coordinación cognitiva.
    
    Args:
        neuron_id (str): Identificador único para la neurona.
        max_synapses (int, optional): Número máximo de sinapsis permitidas. Por defecto 100.
        max_concepts (int, optional): Número máximo de conceptos a mantener. Por defecto 1000.
        
    Atributos:
        neuron_id (str): Identificador único de la neurona.
        max_synapses (int): Límite máximo de conexiones sinápticas.
        max_concepts (int): Límite máximo de conceptos a mantener.
        synapses (list): Lista de sinapsis conectadas a esta neurona.
        activation_level (float): Nivel de activación actual (0.0 a 1.0).
        last_activation_time (float): Timestamp de la última activación.
        age (float): Edad de la neurona en segundos.
        cognitive_resilience (float): Resistencia a interferencia cognitiva (0.0 a 1.0).
        lock (RLock): Bloqueo para operaciones concurrentes.
        concept_concentration (dict): Mapeo de conceptos a sus concentraciones.
        integration_rate (float): Tasa de integración conceptual.
        network_depth (float): Profundidad de conexión con la red (0.0 a 1.0).
        distributed_insights (dict): Insights distribuidos.
    """
    
    __slots__ = [
        'neuron_id', 'max_synapses', 'max_concepts', 'synapses',
        'activation_level', 'last_activation_time', 'age', 'cognitive_resilience',
        'lock', 'concept_concentration', '_concept_access_times', 'integration_rate',
        'network_depth', 'distributed_insights', 'knowledge_decay_rate',
        'insight_regeneration_rate', 'cognitive_interference', 'neuron_type',
        'processing_speed', 'signal_type', '_activation_buffer', 'impact',
        'plasticity', 'efficiency', '_impact_history', '_plasticity_history',
        '_efficiency_history'
    ]
    
    def __init__(self, neuron_id: str, max_synapses: int = 100, max_concepts: int = 1000):
        if not isinstance(neuron_id, str) or not neuron_id.strip():
            raise ValueError("Se requiere un ID de neurona no vacío")
        if not isinstance(max_synapses, int) or max_synapses <= 0:
            raise ValueError("max_synapses debe ser un entero positivo")
        if not isinstance(max_concepts, int) or max_concepts <= 0:
            raise ValueError("max_concepts debe ser un entero positivo")
            
        self.neuron_id = neuron_id
        self.max_synapses = max_synapses
        self.max_concepts = max_concepts
        self.synapses = []
        self.activation_level = 0.0
        self.last_activation_time = time.time()
        self.age = 0.0
        self.cognitive_resilience = 1.0  # Resistencia a interferencia cognitiva
        self.lock = RLock()
        
        # Características cognitivas miceliales con límites
        self.concept_concentration = {}  # Concentración de diferentes conceptos
        self._concept_access_times = {}  # Para limpieza LRU
        self.integration_rate = 1e-6  # Tasa de integración conceptual (valor por defecto)
        self.network_depth = 0.5  # Profundidad de red (0.0 a 1.0)
        self.distributed_insights = {}  # Insights distribuidos
        
        # Longevidad cognitiva con límites
        self.knowledge_decay_rate = 1e-10  # Tasa de decaimiento del conocimiento
        self.insight_regeneration_rate = 1e-8  # Tasa de regeneración de insights
        self.cognitive_interference = 0.0  # Interferencia por sobrecarga (0.0 a 1.0)
        
        # Compatibilidad
        self.neuron_type = "cognitive_micelial"
        self.processing_speed = "deep_slow"
        self.signal_type = "conceptual"
        
        # Estado de activación y métricas con límites de tamaño
        self._activation_buffer = deque(maxlen=10)  # Buffer con tamaño fijo de 10
        self.impact = 0.5  # Impacto de la neurona (0.0 a 1.0)
        self.plasticity = 0.7  # Plasticidad base (0.0 a 1.0)
        self.efficiency = 0.6  # Eficiencia base (0.0 a 1.0)
        
        # Historiales con límites de tamaño
        max_history = min(100, max(10, 50))  # Límite razonable
        self._impact_history = deque(maxlen=max_history)
        self._plasticity_history = deque(maxlen=max_history)
        self._efficiency_history = deque(maxlen=max_history)

    def age_neuron(self, delta_time: float) -> None:
        """
        Envejece la neurona con preservación extrema del conocimiento y limpieza de memoria.
        
        Este método actualiza el estado interno de la neurona basado en el tiempo transcurrido,
        incluyendo la limpieza de conceptos no utilizados, el decaimiento del conocimiento,
        la regeneración de insights y la actualización de métricas de rendimiento.
        
        Args:
            delta_time (float): Tiempo transcurrido desde la última actualización en segundos.
            
        Raises:
            ValueError: Si delta_time no es un número positivo.
            RuntimeError: Si ocurre un error durante el proceso de envejecimiento.
            
        Example:
            >>> neurona = CognitiveMicelialNeuronBase(neuron_id="test")
            >>> neurona.age_neuron(1.0)  # Envejecer la neurona 1 segundo
        """
        if not isinstance(delta_time, (int, float)):
            error_msg = f"delta_time debe ser un número, se recibió: {type(delta_time).__name__}"
            log_neuron_error(self.neuron_id, error_msg)
            raise ValueError(error_msg)
            
        if delta_time <= 0:
            error_msg = f"delta_time debe ser positivo, se recibió: {delta_time}"
            log_neuron_error(self.neuron_id, error_msg)
            raise ValueError(error_msg)
        
        try:
            with self.lock:
                try:
                    # Actualizar edad
                    self.age = max(0.0, self.age + delta_time)
                    
                    # Limpieza periódica de conceptos no utilizados (si superamos el 90% de capacidad)
                    if hasattr(self, 'concept_concentration') and hasattr(self, 'max_concepts'):
                        if len(self.concept_concentration) > self.max_concepts * 0.9:
                            try:
                                removed = self._cleanup_unused_concepts()
                                log_neuron_error(self.neuron_id, f"Limpieza LRU: eliminados {removed} conceptos")
                            except Exception as e:
                                log_neuron_error(self.neuron_id, f"Error en limpieza LRU: {str(e)}")
                    
                    # Actualizar resiliencia cognitiva con límites seguros
                    if hasattr(self, 'knowledge_decay_rate') and hasattr(self, 'cognitive_interference'):
                        knowledge_loss = self.knowledge_decay_rate * delta_time * (1 + self.cognitive_interference * 0.1)
                        self.cognitive_resilience = max(0.0, min(1.0, self.cognitive_resilience - knowledge_loss))
                    
                    # Regeneración de insights con límites
                    if hasattr(self, 'cognitive_resilience') and hasattr(self, 'insight_regeneration_rate'):
                        if self.cognitive_resilience < 1.0:
                            insight_growth = self.insight_regeneration_rate * delta_time
                            self.cognitive_resilience = min(1.0, self.cognitive_resilience + insight_growth)
                    
                    # Actualizar profundidad de red con límites
                    if hasattr(self, 'network_depth') and hasattr(self, 'integration_rate'):
                        self.network_depth = max(0.0, min(1.0, 
                            self.network_depth + (self.integration_rate * delta_time)))
                    
                    # Reducir interferencia gradualmente con límites
                    if hasattr(self, 'cognitive_interference'):
                        self.cognitive_interference = max(0.0, 
                            min(1.0, self.cognitive_interference - (delta_time * 1e-8)))
                    
                    # Actualizar métricas de rendimiento
                    self._update_metrics()
                    
                except Exception as e:
                    error_msg = f"Error en age_neuron (interno): {str(e)}"
                    log_neuron_error(self.neuron_id, error_msg)
                    raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Error crítico en age_neuron: {str(e)}"
            log_neuron_error(self.neuron_id, error_msg)
            # Intentar restaurar valores críticos en caso de error
            self._restore_safe_state()
            raise RuntimeError(error_msg) from e
            
    def _restore_safe_state(self) -> None:
        """
        Restaura la neurona a un estado seguro después de un error crítico.
        """
        safe_attrs = {
            'cognitive_resilience': 0.5,
            'network_depth': 0.5,
            'cognitive_interference': 0.0,
            'activation_level': 0.0
        }
        
        for attr, default_value in safe_attrs.items():
            if hasattr(self, attr):
                try:
                    setattr(self, attr, default_value)
                except Exception as e:
                    log_neuron_error(self.neuron_id, f"No se pudo restaurar {attr}: {str(e)}")

    def _cleanup_unused_concepts(self) -> int:
        """
        Limpia conceptos no utilizados utilizando el algoritmo LRU (Least Recently Used).
        Mantiene los conceptos más recientemente utilizados dentro del límite establecido.
        
        Returns:
            int: Número de conceptos eliminados
            
        Raises:
            RuntimeError: Si ocurre un error durante la limpieza
        """
        removed_count = 0
        try:
            with self.lock:
                # Verificar si hay conceptos para limpiar
                if not hasattr(self, '_concept_access_times') or not self._concept_access_times:
                    return 0
                
                if not hasattr(self, 'concept_concentration') or not self.concept_concentration:
                    return 0
                    
                # Si no hemos superado el límite, no hacemos nada
                if len(self.concept_concentration) <= self.max_concepts:
                    return 0
                    
                # Ordenar conceptos por último acceso (más antiguos primero)
                concepts_by_access = sorted(
                    self._concept_access_times.items(),
                    key=lambda x: x[1]  # Ordenar por timestamp de acceso
                )
                
                # Calcular cuántos conceptos necesitamos eliminar (10% más allá del límite)
                target_size = int(self.max_concepts * 0.9)
                current_size = len(self.concept_concentration)
                
                if current_size <= target_size:
                    return 0  # No es necesario eliminar nada
                
                excess = current_size - target_size
                
                # Tomar los conceptos más antiguos
                to_remove = []
                for concept, _ in concepts_by_access:
                    if len(to_remove) >= excess:
                        break
                    if concept in self.concept_concentration:
                        to_remove.append(concept)
                
                # Eliminar conceptos menos usados
                for concept in to_remove:
                    if concept in self.concept_concentration:
                        del self.concept_concentration[concept]
                        removed_count += 1
                    if hasattr(self, '_concept_access_times') and concept in self._concept_access_times:
                        del self._concept_access_times[concept]
                
                return removed_count
                        
        except Exception as e:
            error_msg = f"Error en _cleanup_unused_concepts: {str(e)}"
            log_neuron_error(self.neuron_id, error_msg)
            raise RuntimeError(error_msg) from e
            
    def _update_metrics(self):
        """
        Actualiza las métricas de rendimiento de la neurona.
        Este método se llama periódicamente para mantener las métricas actualizadas.
        """
        try:
            with self.lock:
                # Actualizar historial de métricas
                self._impact_history.append(self.impact)
                self._plasticity_history.append(self.plasticity)
                self._efficiency_history.append(self.efficiency)
                
                # Calcular promedios móviles (últimos 10 ciclos)
                window_size = min(10, len(self._impact_history))
                if window_size > 0:
                    self.impact = sum(
                        self._impact_history[-window_size:]
                    ) / window_size
                    self.plasticity = sum(
                        self._plasticity_history[-window_size:]
                    ) / window_size
                    self.efficiency = sum(
                        self._efficiency_history[-window_size:]
                    ) / window_size
                    
                # Asegurar que las métricas estén en el rango correcto
                self.impact = max(0.0, min(1.0, self.impact))
                self.plasticity = max(0.0, min(1.0, self.plasticity))
                self.efficiency = max(0.0, min(1.0, self.efficiency))
                    
        except Exception as e:
            log_neuron_error(
                self.neuron_id, 
                f"Error en _update_metrics: {str(e)}"
            )
            
    def add_cognitive_interference(self, interference_amount: float):
        """
        Añade interferencia cognitiva a la neurona.
        
        Args:
            interference_amount (float): Cantidad de interferencia a añadir (0.0 a 1.0).
            
        Raises:
            ValueError: Si interference_amount no es un número válido entre 0.0 y 1.0
        """
        try:
            if not isinstance(interference_amount, (int, float)):
                raise ValueError(
                    "La cantidad de interferencia debe ser un número"
                )
                
            if not 0.0 <= interference_amount <= 1.0:
                raise ValueError(
                    "La interferencia debe estar entre 0.0 y 1.0"
                )
                
            with self.lock:
                # Aplicar interferencia con límite superior
                self.cognitive_interference = min(
                    1.0, 
                    self.cognitive_interference + interference_amount * 
                    (1.0 - self.cognitive_resilience)
                )
                
                # Registrar el evento para seguimiento
                self._activation_buffer.append({
                    'type': 'interference',
                    'amount': interference_amount,
                    'timestamp': time.time()
                })

        except Exception as e:
            log_neuron_error(
                self.neuron_id, 
                f"Error en add_cognitive_interference: {str(e)}"
            )

    def update_concept(self, concept_type: str, concentration: float):
        """
        Actualiza la concentración de un concepto específico en la neurona.
        
        Args:
            concept_type (str): Identificador del tipo de concepto.
            concentration (float): Nueva concentración del concepto (0.0 a 1.0).
            
        Raises:
            ValueError: Si los parámetros no son válidos o están fuera de rango.
        """
        if not isinstance(concept_type, str) or not concept_type.strip():
            raise ValueError("concept_type debe ser una cadena no vacía")
        if not isinstance(concentration, (int, float)) or not (0.0 <= concentration <= 1.0):
            raise ValueError("concentration debe ser un número entre 0.0 y 1.0")
            
        with self.lock:
            try:
                # Actualizar el concepto y su tiempo de acceso
                self.concept_concentration[concept_type] = concentration
                self._concept_access_times[concept_type] = time.time()
                
                # Actualizar métricas de plasticidad
                self._plasticity_history.append(
                    max(0.1, 1.0 - (len(self.concept_concentration) / 
                                  (self.max_concepts * 2)))
                )
                    
                # Limpiar conceptos si es necesario
                if len(self.concept_concentration) > self.max_concepts * 0.9:
                    self._cleanup_unused_concepts()
                    
            except Exception as e:
                log_neuron_error(
                    self.neuron_id,
                    f"Error en update_concept: {str(e)}"
                )
    
    def _cleanup_unused_concepts(self) -> int:
        """
        Limpia conceptos no utilizados recientemente de la memoria de la neurona.
        Utiliza un enfoque LRU (Least Recently Used) para determinar qué conceptos eliminar.
        
        Returns:
            int: Número de conceptos eliminados
            
        Raises:
            RuntimeError: Si ocurre un error durante la limpieza
        """
        removed_count = 0
        try:
            with self.lock:
                # Inicializar atributos si no existen (defensa en profundidad)
                if not hasattr(self, '_concept_access_times'):
                    self._concept_access_times = {}
                if not hasattr(self, 'concept_concentration'):
                    self.concept_concentration = {}
                
                # Verificar si hay conceptos para limpiar
                if not self._concept_access_times or not self.concept_concentration:
                    return 0
                
                # Ordenar conceptos por último acceso (más antiguo primero)
                try:
                    # Validar que todos los timestamps sean números
                    valid_access_times = {
                        k: v for k, v in self._concept_access_times.items()
                        if isinstance(v, (int, float))
                    }
                    
                    # Registrar advertencia si se encontraron timestamps inválidos
                    invalid_count = len(self._concept_access_times) - len(valid_access_times)
                    if invalid_count > 0:
                        log_neuron_error(
                            self.neuron_id,
                            f"Se encontraron {invalid_count} timestamps de acceso inválidos"
                        )
                    
                    concepts_by_access = sorted(
                        valid_access_times.items(),
                        key=lambda x: x[1]  # Ordenar por timestamp de acceso
                    )
                except (TypeError, AttributeError) as e:
                    # Si hay un error en los datos, limpiar todo
                    removed_count = len(self.concept_concentration)
                    self.concept_concentration.clear()
                    self._concept_access_times.clear()
                    log_neuron_error(
                        self.neuron_id,
                        f"Error al ordenar conceptos por acceso: {str(e)}. " +
                        f"Se eliminaron {removed_count} conceptos."
                    )
                    return removed_count
                
                # Calcular cuántos conceptos necesitamos eliminar (10% más allá del límite)
                target_size = max(1, int(self.max_concepts * 0.9))  # Al menos 1 concepto
                current_size = len(self.concept_concentration)
                
                if current_size <= target_size:
                    return 0  # No es necesario eliminar nada
                
                # Tomar los conceptos más antiguos que no han sido accedidos recientemente
                to_remove = []
                for concept, _ in concepts_by_access:
                    if len(to_remove) >= (current_size - target_size):
                        break
                    if concept in self.concept_concentration:
                        to_remove.append(concept)
                
                # Eliminar conceptos menos usados en una sola pasada
                for concept in to_remove:
                    try:
                        if concept in self.concept_concentration:
                            del self.concept_concentration[concept]
                            removed_count += 1
                        if concept in self._concept_access_times:
                            del self._concept_access_times[concept]
                    except Exception as e:
                        log_neuron_error(
                            self.neuron_id,
                            f"Error al eliminar concepto '{concept}': {str(e)}"
                        )
                        continue
                
                # Verificar consistencia después de la limpieza
                if removed_count > 0:
                    self._verify_consistency_after_cleanup()
                
                return removed_count
                        
        except Exception as e:
            error_msg = (
                f"Error en _cleanup_unused_concepts: {str(e)}. " +
                f"Conceptos: {len(getattr(self, 'concept_concentration', {}))}, " +
                f"Accesos: {len(getattr(self, '_concept_access_times', {}))}"
            )
            log_neuron_error(self.neuron_id, error_msg)
            raise RuntimeError(error_msg) from e
    
    def _verify_consistency_after_cleanup(self):
        """
        Verifica la consistencia entre conceptos y sus tiempos de acceso
        después de una limpieza.
        """
        try:
            # Verificar que todos los conceptos tengan entrada de tiempo de acceso
            missing_access = [
                c for c in self.concept_concentration 
                if c not in self._concept_access_times
            ]
            
            if missing_access:
                log_neuron_error(
                    self.neuron_id,
                    f"{len(missing_access)} conceptos sin tiempo de acceso. Actualizando..."
                )
                current_time = time.time()
                for concept in missing_access:
                    self._concept_access_times[concept] = current_time
            
            # Verificar que no haya tiempos de acceso huérfanos
            orphaned_access = [
                c for c in self._concept_access_times 
                if c not in self.concept_concentration
            ]
            
            if orphaned_access:
                log_neuron_error(
                    self.neuron_id,
                    f"{len(orphaned_access)} tiempos de acceso huérfanos. Limpiando..."
                )
                for concept in orphaned_access:
                    del self._concept_access_times[concept]
                    
        except Exception as e:
            log_neuron_error(
                self.neuron_id,
                f"Error en _verify_consistency_after_cleanup: {str(e)}"
            )
    
    def _update_metrics(self):
        """
        Actualiza las métricas de rendimiento de la neurona.
        Este método se llama periódicamente para mantener las métricas actualizadas.
        """
        try:
            with self.lock:
                # Inicializar métricas si es necesario
                if not hasattr(self, '_impact_history'):
                    self._impact_history = deque(maxlen=100)
                if not hasattr(self, '_plasticity_history'):
                    self._plasticity_history = deque(maxlen=100)
                if not hasattr(self, '_efficiency_history'):
                    self._efficiency_history = deque(maxlen=100)
                
                # Calcular métricas de impacto, plasticidad y eficiencia
                self._update_impact()
                self._update_plasticity()
                self._update_efficiency()
                
        except Exception as e:
            log_neuron_error(
                self.neuron_id,
                f"Error en _update_metrics: {str(e)}"
            )
    
    def _update_impact(self):
        """
        Actualiza el impacto de la neurona basado en su actividad reciente,
        considerando su nivel de activación, frecuencia de activación y conexiones.
        """
        try:
            # Calcular impacto basado en activación reciente (50% de peso)
            activation_impact = 0.0
            if hasattr(self, '_activation_buffer') and self._activation_buffer:
                activation_impact = (
                    sum(a[1] for a in self._activation_buffer) / 
                    len(self._activation_buffer)
                )
            activation_impact *= 0.5
            
            # Calcular impacto basado en frecuencia de activación (30% de peso)
            freq_impact = 0.0
            if (hasattr(self, '_activation_buffer') and 
                len(self._activation_buffer) > 1):
                time_window = (
                    self._activation_buffer[-1][0] - 
                    self._activation_buffer[0][0]
                )
                if time_window > 0:
                    # Ajustar factor de escala para mayor sensibilidad
                    freq_impact = min(
                        1.0, 
                        len(self._activation_buffer) / (time_window + 0.1)
                    ) * 0.3
            
            # Impacto basado en integración en la red (20% de peso)
            network_impact = 0.0
            if hasattr(self, 'synapses'):
                network_impact = min(1.0, len(self.synapses) / 5.0) * 0.2
            
            # Calcular nuevo impacto (promedio ponderado)
            new_impact = activation_impact + freq_impact + network_impact
            
            # Suavizar la transición del impacto
            self.impact = (self.impact * 0.7) + (new_impact * 0.3)
            self._impact_history.append(self.impact)
            
            # Ajustar basado en resiliencia cognitiva
            self.impact = max(0.1, min(1.0, self.impact * (0.8 + (self.cognitive_resilience * 0.4))))
            
            # Actualizar plasticidad basada en la actividad
            self._update_plasticity()
            
            # Actualizar eficiencia basada en impacto y plasticidad
            self._update_efficiency()
            
        except Exception as e:
            log_neuron_error(self.neuron_id, f"Error en _update_impact: {str(e)}")
            self.impact = max(0.1, self.impact * 0.9)  # Reducir impacto pero no a cero

    def _update_plasticity(self):
        """Actualiza la plasticidad de la neurona basada en su actividad reciente."""
        try:
            # La plasticidad aumenta con la actividad reciente pero disminuye con la edad
            activity_level = min(1.0, len(self._activation_buffer) / 5.0)
            age_factor = 1.0 - min(1.0, self.age / 1e6)  # Reducción muy lenta con la edad
            
            # Ajustar plasticidad basada en actividad reciente
            new_plasticity = (activity_level * 0.6) + (self.impact * 0.4)
            new_plasticity *= age_factor
            
            # Suavizar la transición
            self.plasticity = (self.plasticity * 0.8) + (new_plasticity * 0.2)
            self.plasticity = max(0.1, min(1.0, self.plasticity))
            self._plasticity_history.append(self.plasticity)
            
        except Exception as e:
            log_neuron_error(self.neuron_id, f"Error en _update_plasticity: {str(e)}")
            self.plasticity = max(0.1, self.plasticity * 0.9)

    def _update_efficiency(self):
        """Actualiza la eficiencia de la neurona basada en su actividad y plasticidad."""
        try:
            # La eficiencia aumenta con la actividad sostenida pero se ve afectada por la interferencia
            stability = 1.0 - (self.cognitive_interference * 0.5)
            
            # Calcular eficiencia basada en impacto, plasticidad y estabilidad
            new_efficiency = (self.impact * 0.4) + (self.plasticity * 0.4) + (stability * 0.2)
            
            # Ajustar por resiliencia cognitiva
            new_efficiency *= (0.8 + (self.cognitive_resilience * 0.4))
            
            # Suavizar la transición
            self.efficiency = (self.efficiency * 0.7) + (new_efficiency * 0.3)
            self.efficiency = max(0.1, min(1.0, self.efficiency))
            self._efficiency_history.append(self.efficiency)
            
        except Exception as e:
            log_neuron_error(self.neuron_id, f"Error en _update_efficiency: {str(e)}")
            self.efficiency = max(0.1, self.efficiency * 0.9)

    def propagate_conceptual_signal(self, signal_strength: float, concept_type: str, context: Dict = None):
        """Propaga señales conceptuales lentas a través de la red cognitiva"""
        if not self.synapses:
            return []
        
        # Filtrar sinapsis compatibles con este concepto
        compatible_synapses = [s for s in self.synapses 
                             if hasattr(s, 'conceptual_compatibility') 
                             and concept_type in s.conceptual_compatibility]
        
        if not compatible_synapses:
            compatible_synapses = self.synapses
        
        # Propagación lenta con profundidad
        with ThreadPoolExecutor(max_workers=min(2, len(compatible_synapses))) as executor:
            futures = []
            for synapse in compatible_synapses:
                if synapse.is_conceptually_active(concept_type):
                    # Señal modulada por resilience y profundidad
                    modulated_signal = (signal_strength * self.cognitive_resilience * 
                                      self.network_depth)
                    
                    future = executor.submit(
                        synapse.transmit_concept,
                        modulated_signal,
                        concept_type,
                        self,
                        context
                    )
                    futures.append(future)
            
            results = []
            for future in as_completed(futures, timeout=2.0):  # Más tiempo para pensamiento profundo
                try:
                    result = future.result()
                    if result is not None:
                        results.append(result)
                except Exception:
                    continue
            
            return results

    @abstractmethod
    def receive_concept(self, concentration: float, concept_type: str, context: Dict = None) -> float:
        """Recibe señal conceptual y la procesa"""
        pass

    @abstractmethod
    def process(self, context: Dict = None) -> Dict[str, float]:
        """Procesa información y retorna múltiples conceptos de salida"""
        pass

    def get_state(self) -> Dict:
        """Retorna estado cognitivo completo para persistencia"""
        with self.lock:
            return {
                "neuron_id": self.neuron_id,
                "activation_level": self.activation_level,
                "age": self.age,
                "cognitive_resilience": self.cognitive_resilience,
                "network_depth": self.network_depth,
                "concept_concentration": self.concept_concentration.copy(),
                "distributed_insights": self.distributed_insights.copy(),
                "cognitive_interference": self.cognitive_interference,
                "synapses_count": len(self.synapses),
                "last_activation": self.last_activation_time
            }


# ============ INTEGRADORES CONCEPTUALES (5 tipos) ============

class AbstractPatternIntegrator(CognitiveMicelialNeuronBase):
    """Integra patrones abstractos y conexiones conceptuales no obvias"""
    
    def __init__(self, neuron_id: str, abstraction_levels: int = 5):
        super().__init__(neuron_id, max_synapses=200)
        self.abstraction_levels = abstraction_levels
        self.pattern_memory = defaultdict(lambda: deque(maxlen=100))
        self.conceptual_bridges = {}  # Puentes entre conceptos distantes
        self.abstraction_threshold = 0.3
        self.pattern_recognition_depth = 3

    def receive_concept(self, concentration: float, concept_type: str, context: Dict = None) -> float:
        with self.lock:
            abstraction_level = context.get("abstraction_level", 1) if context else 1
            related_concepts = context.get("related_concepts", []) if context else []
            
            # Almacenar en el nivel de abstracción apropiado
            pattern_key = f"L{abstraction_level}_{concept_type}"
            self.pattern_memory[pattern_key].append({
                'concentration': concentration,
                'concept': concept_type,
                'related': related_concepts,
                'timestamp': time.time(),
                'abstraction': abstraction_level
            })
            
            # Actualizar concentración del concepto en el diccionario de la clase base
            self.update_concept(concept_type, concentration)
            
            # Buscar conexiones entre conceptos aparentemente no relacionados
            for other_concept in related_concepts:
                bridge_key = tuple(sorted([concept_type, other_concept]))
                if bridge_key not in self.conceptual_bridges:
                    self.conceptual_bridges[bridge_key] = {
                        'strength': 0.0,
                        'co_occurrences': 0,
                        'last_seen': time.time()
                    }
                
                # Fortalecer puente conceptual
                bridge = self.conceptual_bridges[bridge_key]
                bridge['co_occurrences'] += 1
                bridge['strength'] = min(1.0, bridge['strength'] + concentration * 0.1)
                bridge['last_seen'] = time.time()
            
            # Activación basada en novedad del patrón
            novelty = self._assess_pattern_novelty(concept_type, concentration, abstraction_level)
            self.activation_level = novelty * concentration
            
            return self.activation_level

    def _assess_pattern_novelty(self, concept_type: str, concentration: float, abstraction_level: int) -> float:
        """Evalúa qué tan novedoso es este patrón conceptual"""
        pattern_key = f"L{abstraction_level}_{concept_type}"
        history = self.pattern_memory[pattern_key]
        
        if len(history) < 3:
            return 1.0  # Muy novedoso si es nuevo
        
        # Comparar con patrones históricos
        recent_concentrations = [entry['concentration'] for entry in list(history)[-5:]]
        avg_concentration = sum(recent_concentrations) / len(recent_concentrations)
        
        # Novelty alta si difiere significativamente del promedio
        difference = abs(concentration - avg_concentration)
        novelty = min(1.0, difference * 2.0)
        
        return novelty

    def process(self, context: Dict = None) -> Dict[str, float]:
        with self.lock:
            output_concepts = {}
            
            # Generar insights de patrones abstractos
            abstraction_insights = self._generate_abstraction_insights()
            for insight_type, strength in abstraction_insights.items():
                if strength > self.abstraction_threshold:
                    output_concepts[insight_type] = strength
            
            # Descubrir conexiones conceptuales emergentes
            emergent_connections = self._discover_emergent_connections()
            for connection_type, strength in emergent_connections.items():
                output_concepts[f"bridge_{connection_type}"] = strength
            
            # Generar meta-patrones (patrones de patrones)
            meta_patterns = self._extract_meta_patterns()
            for meta_pattern, confidence in meta_patterns.items():
                if confidence > 0.6:
                    output_concepts[f"meta_{meta_pattern}"] = confidence
            
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in output_concepts.items()}

    def _generate_abstraction_insights(self) -> Dict[str, float]:
        """Genera insights basados en patrones de abstracción"""
        insights = {}
        
        # Analizar cada nivel de abstracción
        for level in range(1, self.abstraction_levels + 1):
            level_patterns = {}
            for pattern_key, history in self.pattern_memory.items():
                if pattern_key.startswith(f"L{level}_"):
                    concept = pattern_key.split("_", 1)[1]
                    if len(history) > 3:
                        level_patterns[concept] = list(history)
            
            # Buscar patrones emergentes en este nivel
            if len(level_patterns) > 2:
                cross_concept_correlations = self._find_cross_concept_patterns(level_patterns)
                for correlation, strength in cross_concept_correlations.items():
                    insights[f"L{level}_correlation_{correlation}"] = strength
        
        return insights

    def _find_cross_concept_patterns(self, level_patterns: Dict) -> Dict[str, float]:
        """Encuentra patrones que cruzan múltiples conceptos"""
        correlations = {}
        concepts = list(level_patterns.keys())
        
        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i+1:]:
                # Calcular correlación temporal entre conceptos
                history1 = level_patterns[concept1]
                history2 = level_patterns[concept2]
                
                if len(history1) > 2 and len(history2) > 2:
                    correlation = self._calculate_temporal_correlation(history1, history2)
                    if correlation > 0.5:
                        correlations[f"{concept1}_x_{concept2}"] = correlation
        
        return correlations

    def _calculate_temporal_correlation(self, history1: List, history2: List) -> float:
        """Calcula correlación temporal entre dos historiales conceptuales"""
        # Sincronizar por timestamp y calcular correlación
        timestamps1 = [entry['timestamp'] for entry in history1]
        timestamps2 = [entry['timestamp'] for entry in history2]
        
        # Encontrar ventana temporal común
        common_start = max(min(timestamps1), min(timestamps2))
        common_end = min(max(timestamps1), max(timestamps2))
        
        if common_end <= common_start:
            return 0.0
        
        # Extraer valores en ventana común
        values1 = [entry['concentration'] for entry in history1 
                  if common_start <= entry['timestamp'] <= common_end]
        values2 = [entry['concentration'] for entry in history2 
                  if common_start <= entry['timestamp'] <= common_end]
        
        if len(values1) < 2 or len(values2) < 2:
            return 0.0
        
        # Calcular correlación
        min_len = min(len(values1), len(values2))
        v1, v2 = values1[:min_len], values2[:min_len]
        
        if min_len < 2:
            return 0.0
        
        mean1, mean2 = sum(v1)/len(v1), sum(v2)/len(v2)
        num = sum((v1[i] - mean1) * (v2[i] - mean2) for i in range(min_len))
        den1 = sum((v1[i] - mean1)**2 for i in range(min_len))
        den2 = sum((v2[i] - mean2)**2 for i in range(min_len))
        
        if den1 == 0 or den2 == 0:
            return 0.0
        
        return abs(num / math.sqrt(den1 * den2))

    def _discover_emergent_connections(self) -> Dict[str, float]:
        """Descubre conexiones emergentes entre conceptos"""
        emergent = {}
        
        # Analizar puentes conceptuales que se han fortalecido
        for bridge_key, bridge_info in self.conceptual_bridges.items():
            if bridge_info['strength'] > 0.7 and bridge_info['co_occurrences'] > 5:
                concept1, concept2 = bridge_key
                emergent[f"{concept1}_emerges_with_{concept2}"] = bridge_info['strength']
        
        return emergent

    def _extract_meta_patterns(self) -> Dict[str, float]:
        """Extrae meta-patrones (patrones de patrones)"""
        meta_patterns = {}
        
        # Buscar patrones en cómo evolucionan los patrones
        abstraction_trends = {}
        for level in range(1, self.abstraction_levels + 1):
            level_activity = 0.0
            level_count = 0
            
            for pattern_key in self.pattern_memory:
                if pattern_key.startswith(f"L{level}_"):
                    history = self.pattern_memory[pattern_key]
                    if len(history) > 0:
                        level_activity += history[-1]['concentration']
                        level_count += 1
            
            if level_count > 0:
                abstraction_trends[level] = level_activity / level_count
        
        # Detectar tendencias de abstracción
        if len(abstraction_trends) > 2:
            levels = sorted(abstraction_trends.keys())
            for i in range(len(levels) - 1):
                current_level = abstraction_trends[levels[i]]
                next_level = abstraction_trends[levels[i + 1]]
                
                if next_level > current_level * 1.2:
                    meta_patterns[f"abstraction_emergence_L{levels[i]}_to_L{levels[i+1]}"] = min(1.0, next_level / current_level - 1.0)
        
        return meta_patterns


class ContextualTemporalIntegrator(CognitiveMicelialNeuronBase):
    """Mantiene contexto histórico de ideas y argumentos durante períodos muy largos"""
    
    def __init__(self, neuron_id: str, temporal_scales: Dict[str, int] = None, abstraction_levels: int = 5):
        super().__init__(neuron_id, max_synapses=300)
        self.temporal_scales = temporal_scales or {
            "immediate": 60,      # 1 minuto
            "short_term": 3600,   # 1 hora  
            "medium_term": 86400, # 1 día
            "long_term": 604800,  # 1 semana
            "deep_memory": 2592000 # 1 mes
        }
        self.abstraction_levels = abstraction_levels  # Niveles de abstracción para sugerencias de exploración
        self.context_layers = {scale: deque(maxlen=100) for scale in self.temporal_scales}
        self.argument_threads = {}  # Hilos de argumentación
        self.contextual_associations = defaultdict(list)

    def receive_concept(self, concentration: float, concept_type: str, context: Dict = None) -> float:
        with self.lock:
            current_time = time.time()
            argument_id = context.get("argument_id", "default") if context else "default"
            logical_position = context.get("logical_position", "premise") if context else "premise"
            
            # Crear entrada contextual
            contextual_entry = {
                'concept': concept_type,
                'concentration': concentration,
                'timestamp': current_time,
                'argument_id': argument_id,
                'position': logical_position,
                'context_snapshot': context.copy() if context else {}
            }
            
            # Almacenar en todas las escalas temporales apropiadas
            for scale, max_age in self.temporal_scales.items():
                # Limpiar entradas viejas
                cutoff_time = current_time - max_age
                while (self.context_layers[scale] and 
                       self.context_layers[scale][0]['timestamp'] < cutoff_time):
                    self.context_layers[scale].popleft()
                
                # Añadir nueva entrada
                self.context_layers[scale].append(contextual_entry)
            
            # Mantener hilos de argumentación
            if argument_id not in self.argument_threads:
                self.argument_threads[argument_id] = {
                    'premises': [],
                    'conclusions': [],
                    'evidence': [],
                    'counterarguments': [],
                    'start_time': current_time
                }
            
            thread = self.argument_threads[argument_id]
            if logical_position == "premise":
                thread['premises'].append(contextual_entry)
            elif logical_position == "conclusion":
                thread['conclusions'].append(contextual_entry)
            elif logical_position == "evidence":
                thread['evidence'].append(contextual_entry)
            elif logical_position == "counterargument":
                thread['counterarguments'].append(contextual_entry)
            
            # Crear asociaciones contextuales
            self._create_contextual_associations(contextual_entry)
            
            # Activación basada en relevancia contextual
            contextual_relevance = self._assess_contextual_relevance(concept_type, argument_id)
            self.activation_level = concentration * contextual_relevance
            
            return self.activation_level

    def _create_contextual_associations(self, entry: Dict):
        """Crea asociaciones entre conceptos en contextos similares"""
        concept = entry['concept']
        context_signature = self._generate_context_signature(entry['context_snapshot'])
        
        # Buscar conceptos en contextos similares
        for other_concept, associations in self.contextual_associations.items():
            if other_concept != concept:
                for assoc in associations:
                    if self._contexts_similar(context_signature, assoc['context_sig']):
                        # Fortalecer asociación
                        assoc['strength'] = min(1.0, assoc['strength'] + 0.05)
                        assoc['last_reinforcement'] = time.time()
        
        # Añadir nueva asociación
        self.contextual_associations[concept].append({
            'context_sig': context_signature,
            'strength': entry['concentration'],
            'last_reinforcement': time.time(),
            'argument_id': entry['argument_id']
        })

    def _generate_context_signature(self, context: Dict) -> str:
        """Genera firma del contexto para comparación"""
        if not context:
            return "empty"
        
        # Crear hash basado en claves y tipos de valores
        context_items = []
        for key, value in sorted(context.items()):
            if isinstance(value, (str, int, float)):
                context_items.append(f"{key}:{type(value).__name__}")
        
        return hashlib.md5("_".join(context_items).encode()).hexdigest()[:8]

    def _contexts_similar(self, sig1: str, sig2: str) -> bool:
        """Determina si dos contextos son similares"""
        if sig1 == sig2:
            return True
        # Similitud básica por prefijo (podría mejorarse)
        return sig1[:4] == sig2[:4]

    def _assess_contextual_relevance(self, concept_type: str, argument_id: str) -> float:
        """Evalúa relevancia contextual del concepto"""
        relevance_factors = []
        
        # Factor 1: Frecuencia en argumentos activos
        if argument_id in self.argument_threads:
            thread = self.argument_threads[argument_id]
            all_concepts = []
            for position_list in [thread['premises'], thread['conclusions'], 
                                thread['evidence'], thread['counterarguments']]:
                all_concepts.extend([entry['concept'] for entry in position_list])
            
            if all_concepts:
                frequency = all_concepts.count(concept_type) / len(all_concepts)
                relevance_factors.append(frequency)
        
        # Factor 2: Fuerza de asociaciones contextuales
        if concept_type in self.contextual_associations:
            avg_association_strength = sum(assoc['strength'] for assoc in 
                                         self.contextual_associations[concept_type]) / len(self.contextual_associations[concept_type])
            relevance_factors.append(avg_association_strength)
        
        # Factor 3: Presencia en múltiples escalas temporales
        presence_count = 0
        for scale, layer in self.context_layers.items():
            if any(entry['concept'] == concept_type for entry in layer):
                presence_count += 1
        
        scale_relevance = presence_count / len(self.temporal_scales)
        relevance_factors.append(scale_relevance)
        
        return sum(relevance_factors) / len(relevance_factors) if relevance_factors else 0.5

    def process(self, context: Dict = None) -> Dict[str, float]:
        with self.lock:
            output_concepts = {}
            
            # Análisis de consistencia argumentativa
            for arg_id, thread in self.argument_threads.items():
                consistency = self._analyze_argument_consistency(thread)
                if consistency < 0.3:
                    output_concepts[f"inconsistency_detected_{arg_id}"] = 1.0 - consistency
                elif consistency > 0.8:
                    output_concepts[f"strong_argument_{arg_id}"] = consistency
            
            # Síntesis contextual por escala temporal
            for scale, layer in self.context_layers.items():
                if len(layer) > 10:
                    synthesis = self._synthesize_temporal_context(list(layer), scale)
                    for concept, strength in synthesis.items():
                        output_concepts[f"{scale}_context_{concept}"] = strength
            
            # Recomendaciones de exploración contextual
            exploration_suggestions = self._suggest_contextual_exploration()
            for suggestion, confidence in exploration_suggestions.items():
                output_concepts[f"explore_{suggestion}"] = confidence
            
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in output_concepts.items()}

    def _analyze_argument_consistency(self, thread: Dict) -> float:
        """Analiza consistencia lógica de un hilo argumentativo"""
        premise_concepts = [entry['concept'] for entry in thread['premises']]
        conclusion_concepts = [entry['concept'] for entry in thread['conclusions']]
        counter_concepts = [entry['concept'] for entry in thread['counterarguments']]
        
        if not premise_concepts or not conclusion_concepts:
            return 0.5  # Argumento incompleto
        
        # Verificar si las conclusiones siguen lógicamente de las premisas
        premise_strength = sum(entry['concentration'] for entry in thread['premises']) / len(thread['premises'])
        conclusion_strength = sum(entry['concentration'] for entry in thread['conclusions']) / len(thread['conclusions'])
        
        # Penalizar por contraargumentos fuertes
        counter_penalty = 0.0
        if counter_concepts:
            counter_strength = sum(entry['concentration'] for entry in thread['counterarguments']) / len(thread['counterarguments'])
            counter_penalty = counter_strength * 0.3
        
        # Calcular consistencia
        consistency = min(1.0, (conclusion_strength / max(premise_strength, 0.1)) - counter_penalty)
        return max(0.0, consistency)

    def _synthesize_temporal_context(self, layer_data: List, scale: str) -> Dict[str, float]:
        """Sintetiza contexto en una escala temporal específica"""
        synthesis = {}
        
        # Agrupar por concepto
        concept_groups = defaultdict(list)
        for entry in layer_data:
            concept_groups[entry['concept']].append(entry)
        
        # Sintetizar cada concepto
        for concept, entries in concept_groups.items():
            if len(entries) > 1:
                # Calcular evolución del concepto en esta escala
                concentrations = [entry['concentration'] for entry in entries]
                
                # Tendencia
                if len(concentrations) > 2:
                    trend = (concentrations[-1] - concentrations[0]) / len(concentrations)
                    if abs(trend) > 0.1:
                        synthesis[f"{concept}_trend"] = min(1.0, abs(trend) * 2.0)
                
                # Persistencia
                avg_concentration = sum(concentrations) / len(concentrations)
                if avg_concentration > 0.5:
                    synthesis[f"{concept}_persistent"] = avg_concentration
        
        return synthesis

    def _suggest_contextual_exploration(self) -> Dict[str, float]:
        """Sugiere direcciones de exploración contextual"""
        suggestions = {}
        
        # Sugerir exploración de asociaciones débiles
        for concept, associations in self.contextual_associations.items():
            weak_associations = [assoc for assoc in associations if 0.2 < assoc['strength'] < 0.5]
            if len(weak_associations) > 0:
                suggestions[f"strengthen_{concept}_associations"] = len(weak_associations) / 10.0
        
        # Sugerir exploración de contextos temporales menos frecuentes
        for scale, entries in self.context_layers.items():
            if len(entries) < 5:  # Si hay pocas entradas en esta escala temporal
                suggestions[f"explore_{scale}_context"] = 0.8 - (len(entries) * 0.1)
        
        return suggestions


class KnowledgeSynthesizer(CognitiveMicelialNeuronBase):
    """Combina información de múltiples dominios para generar síntesis complejas"""
    
    def __init__(self, neuron_id: str, domain_specializations: List[str] = None):
        super().__init__(neuron_id, max_synapses=400)
        self.domain_specializations = domain_specializations or []
        self.domain_knowledge = defaultdict(lambda: defaultdict(float))
        self.synthesis_templates = {}
        self.interdisciplinary_connections = defaultdict(set)
        self.synthesis_history = deque(maxlen=50)

    def receive_concept(self, concentration: float, concept_type: str, context: Dict = None) -> float:
        with self.lock:
            domain = context.get("domain", "general") if context else "general"
            knowledge_type = context.get("knowledge_type", "fact") if context else "fact"
            
            # Almacenar conocimiento por dominio
            self.domain_knowledge[domain][concept_type] += concentration * 0.1
            
            # Crear conexiones interdisciplinarias
            for other_domain in self.domain_knowledge:
                if other_domain != domain and concept_type in self.domain_knowledge[other_domain]:
                    # Conexión encontrada entre dominios
                    self.interdisciplinary_connections[concept_type].add((domain, other_domain))
                    
                    # Fortalecer la conexión
                    connection_strength = min(1.0, 
                        self.domain_knowledge[domain][concept_type] * 
                        self.domain_knowledge[other_domain][concept_type])
                    
                    if connection_strength > 0.3:
                        self.update_concept(f"bridge_{domain}_{other_domain}_{concept_type}", 
                                          connection_strength)
            
            # Activación basada en potencial de síntesis
            synthesis_potential = self._assess_synthesis_potential(concept_type, domain)
            self.activation_level = concentration * synthesis_potential
            
            return self.activation_level

    def _assess_synthesis_potential(self, concept_type: str, domain: str) -> float:
        """Evalúa el potencial de síntesis de este concepto"""
        potential_factors = []
        
        # Factor 1: Presencia en múltiples dominios
        domain_count = sum(1 for d in self.domain_knowledge 
                          if concept_type in self.domain_knowledge[d])
        if domain_count > 1:
            potential_factors.append(min(1.0, domain_count / 3.0))
        
        # Factor 2: Fuerza de conexiones interdisciplinarias
        if concept_type in self.interdisciplinary_connections:
            connection_strength = len(self.interdisciplinary_connections[concept_type]) / 5.0
            potential_factors.append(min(1.0, connection_strength))
        
        # Factor 3: Novedad de la síntesis
        recent_syntheses = [entry for entry in self.synthesis_history 
                           if concept_type in entry.get('concepts_involved', [])]
        novelty = 1.0 - min(0.8, len(recent_syntheses) / 10.0)
        potential_factors.append(novelty)
        
        return sum(potential_factors) / len(potential_factors) if potential_factors else 0.3

    def process(self, context: Dict = None) -> Dict[str, float]:
        with self.lock:
            output_concepts = {}
            
            # Generar síntesis interdisciplinarias
            interdisciplinary_syntheses = self._generate_interdisciplinary_syntheses()
            for synthesis_type, confidence in interdisciplinary_syntheses.items():
                if confidence > 0.4:
                    output_concepts[synthesis_type] = confidence
            
            # Crear templates de síntesis emergentes
            emergent_templates = self._discover_synthesis_templates()
            for template_type, applicability in emergent_templates.items():
                output_concepts[f"template_{template_type}"] = applicability
            
            # Proponer nuevas conexiones conceptuales
            novel_connections = self._propose_novel_connections()
            for connection, strength in novel_connections.items():
                output_concepts[f"novel_{connection}"] = strength
            
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in output_concepts.items()}

    def _generate_interdisciplinary_syntheses(self) -> Dict[str, float]:
        """Genera síntesis que cruzan múltiples dominios"""
        syntheses = {}
        
        # Buscar conceptos que aparecen en múltiples dominios
        cross_domain_concepts = {}
        for domain, concepts in self.domain_knowledge.items():
            for concept, strength in concepts.items():
                if strength > 0.3:  # Solo conceptos significativos
                    if concept not in cross_domain_concepts:
                        cross_domain_concepts[concept] = []
                    cross_domain_concepts[concept].append((domain, strength))
        
        # Generar síntesis para conceptos cross-domain
        for concept, domain_data in cross_domain_concepts.items():
            if len(domain_data) >= 2:  # Al menos 2 dominios
                domains = [d[0] for d in domain_data]
                avg_strength = sum(d[1] for d in domain_data) / len(domain_data)
                
                # Crear síntesis específica
                synthesis_key = f"synthesis_{concept}_across_{'_'.join(sorted(domains))}"
                syntheses[synthesis_key] = avg_strength * 0.8
                
                # Registrar síntesis en historial
                self.synthesis_history.append({
                    'type': synthesis_key,
                    'concept': concept,
                    'domains_involved': domains,
                    'concepts_involved': [concept],
                    'strength': avg_strength,
                    'timestamp': time.time()
                })
        
        return syntheses

    def _discover_synthesis_templates(self) -> Dict[str, float]:
        """Descubre plantillas de síntesis reutilizables"""
        templates = {}
        
        if len(self.synthesis_history) > 5:
            # Buscar patrones en síntesis exitosas
            successful_syntheses = [s for s in self.synthesis_history if s['strength'] > 0.6]
            
            # Agrupar por patrones de dominios
            domain_patterns = defaultdict(list)
            for synthesis in successful_syntheses:
                domains_pattern = tuple(sorted(synthesis['domains_involved']))
                domain_patterns[domains_pattern].append(synthesis)
            
            # Crear templates para patrones frecuentes
            for pattern, syntheses in domain_patterns.items():
                if len(syntheses) >= 2:
                    avg_strength = sum(s['strength'] for s in syntheses) / len(syntheses)
                    template_name = "_to_".join(pattern)
                    templates[template_name] = avg_strength * 0.9
                    
                    # Almacenar template para reutilización
                    self.synthesis_templates[template_name] = {
                        'pattern': pattern,
                        'average_strength': avg_strength,
                        'usage_count': len(syntheses),
                        'last_used': time.time()
                    }
        
        return templates

    def _propose_novel_connections(self) -> Dict[str, float]:
        """Propone nuevas conexiones conceptuales no exploradas"""
        novel_connections = {}
        
        # Analizar dominios con alta actividad pero pocas conexiones
        active_domains = {domain: sum(concepts.values()) 
                         for domain, concepts in self.domain_knowledge.items()
                         if sum(concepts.values()) > 1.0}
        
        domain_pairs = []
        domains = list(active_domains.keys())
        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                domain_pairs.append((domains[i], domains[j]))
        
        # Proponer conexiones para pares de dominios poco conectados
        for domain1, domain2 in domain_pairs:
            # Contar conexiones existentes entre estos dominios
            existing_connections = 0
            for concept in self.interdisciplinary_connections:
                connections = self.interdisciplinary_connections[concept]
                if any((d1, d2) == (domain1, domain2) or (d1, d2) == (domain2, domain1) 
                      for d1, d2 in connections):
                    existing_connections += 1
            
            # Si hay pocas conexiones, proponer exploración
            if existing_connections < 3:
                connection_potential = (active_domains[domain1] + active_domains[domain2]) / 2.0
                connection_potential *= (1.0 - existing_connections / 5.0)  # Bonus por novedad
                novel_connections[f"connect_{domain1}_with_{domain2}"] = min(1.0, connection_potential)
        
        return novel_connections


class GlobalCoherenceCoordinator(CognitiveMicelialNeuronBase):
    """Mantiene coherencia lógica global en razonamientos complejos distribuidos"""
    
    def __init__(self, neuron_id: str, coherence_radius: int = 1000):
        super().__init__(neuron_id, max_synapses=500)
        self.coherence_radius = coherence_radius
        self.global_logical_state = {
            "active_arguments": {},
            "logical_constraints": {},
            "contradiction_alerts": {},
            "coherence_score": 0.8
        }
        self.reasoning_threads = {}
        self.contradiction_detector = deque(maxlen=100)
        self.logical_rules = self._initialize_logical_rules()

    def _initialize_logical_rules(self) -> Dict[str, Callable]:
        """Inicializa reglas lógicas básicas"""
        return {
            "non_contradiction": lambda p, not_p: not (p > 0.7 and not_p > 0.7),
            "modus_ponens": lambda if_p_then_q, p: if_p_then_q * p if p > 0.5 else 0.0,
            "transitivity": lambda a_to_b, b_to_c: min(a_to_b, b_to_c) * 0.9,
            "consistency": lambda premises: 1.0 - max(0.0, sum(premises) - 1.0) if len(premises) > 1 else 1.0
        }

    def receive_concept(self, concentration: float, concept_type: str, context: Dict = None) -> float:
        with self.lock:
            reasoning_thread_id = context.get("reasoning_thread", "main") if context else "main"
            logical_role = context.get("logical_role", "premise") if context else "premise"
            logical_operator = context.get("logical_operator", "and") if context else "and"
            
            # Registrar en hilo de razonamiento
            if reasoning_thread_id not in self.reasoning_threads:
                self.reasoning_threads[reasoning_thread_id] = {
                    "premises": [],
                    "intermediate_steps": [],
                    "conclusions": [],
                    "logical_operators": [],
                    "coherence_score": 1.0,
                    "start_time": time.time()
                }
            
            thread = self.reasoning_threads[reasoning_thread_id]
            
            reasoning_step = {
                "concept": concept_type,
                "concentration": concentration,
                "role": logical_role,
                "operator": logical_operator,
                "timestamp": time.time()
            }
            
            if logical_role == "premise":
                thread["premises"].append(reasoning_step)
            elif logical_role == "conclusion":
                thread["conclusions"].append(reasoning_step)
            else:
                thread["intermediate_steps"].append(reasoning_step)
            
            thread["logical_operators"].append(logical_operator)
            
            # Verificar coherencia inmediata
            coherence_violation = self._check_immediate_coherence(reasoning_step, thread)
            if coherence_violation:
                self.contradiction_detector.append({
                    "thread_id": reasoning_thread_id,
                    "violation_type": coherence_violation,
                    "concept": concept_type,
                    "timestamp": time.time()
                })
                self.add_cognitive_interference(0.1)
            
            # Activación basada en importancia lógica
            logical_importance = self._assess_logical_importance(reasoning_step, thread)
            self.activation_level = concentration * logical_importance
            
            return self.activation_level

    def _check_immediate_coherence(self, new_step: Dict, thread: Dict) -> Optional[str]:
        """Verifica coherencia lógica inmediata"""
        concept = new_step["concept"]
        concentration = new_step["concentration"]
        
        # Verificar contradicciones directas
        for step in thread["premises"] + thread["intermediate_steps"] + thread["conclusions"]:
            other_concept = step["concept"]
            other_concentration = step["concentration"]
            
            # Detectar conceptos contradictorios (simple heurística)
            if (("not_" + concept == other_concept or concept == "not_" + other_concept) and
                concentration > 0.6 and other_concentration > 0.6):
                return "direct_contradiction"
            
            # Detectar inconsistencias de fuerza
            if (concept == other_concept and 
                abs(concentration - other_concentration) > 0.5):
                return "strength_inconsistency"
        
        # Verificar reglas lógicas
        if len(thread["premises"]) > 1:
            premise_values = [step["concentration"] for step in thread["premises"]]
            if not self.logical_rules["consistency"](premise_values):
                return "premise_inconsistency"
        
        return None

    def _assess_logical_importance(self, step: Dict, thread: Dict) -> float:
        """Evalúa importancia lógica de un paso de razonamiento"""
        importance_factors = []
        
        # Factor 1: Rol lógico
        role_importance = {
            "premise": 0.9,
            "conclusion": 1.0,
            "evidence": 0.7,
            "intermediate": 0.6
        }
        importance_factors.append(role_importance.get(step["role"], 0.5))
        
        # Factor 2: Fuerza de concentración
        importance_factors.append(step["concentration"])
        
        # Factor 3: Posición en cadena lógica
        total_steps = len(thread["premises"]) + len(thread["intermediate_steps"]) + len(thread["conclusions"])
        if total_steps > 0:
            position_importance = 1.0 if step["role"] == "conclusion" else 0.8
            importance_factors.append(position_importance)
        
        # Factor 4: Novedad lógica
        concept = step["concept"]
        existing_concepts = [s["concept"] for s in 
                           thread["premises"] + thread["intermediate_steps"] + thread["conclusions"]]
        if concept not in existing_concepts[:-1]:  # Excluir el paso actual
            importance_factors.append(0.9)  # Bonus por novedad
        else:
            importance_factors.append(0.6)  # Penalización por repetición
        
        return sum(importance_factors) / len(importance_factors)

    def process(self, context: Dict = None) -> Dict[str, float]:
        with self.lock:
            output_concepts = {}
            
            # Evaluar coherencia global de todos los hilos activos
            global_coherence = self._evaluate_global_coherence()
            self.global_logical_state["coherence_score"] = global_coherence
            
            if global_coherence < 0.6:
                output_concepts["coherence_warning"] = 1.0 - global_coherence
                output_concepts["resolution_needed"] = (0.6 - global_coherence) * 2.0
            
            # Detectar y reportar contradicciones
            contradiction_analysis = self._analyze_contradictions()
            for contradiction_type, severity in contradiction_analysis.items():
                output_concepts[f"contradiction_{contradiction_type}"] = severity
            
            # Sugerir pasos lógicos faltantes
            missing_steps = self._identify_missing_logical_steps()
            for step_type, necessity in missing_steps.items():
                output_concepts[f"missing_{step_type}"] = necessity
            
            # Coordinar resolución de conflictos lógicos
            conflict_resolutions = self._coordinate_conflict_resolution()
            for resolution_type, effectiveness in conflict_resolutions.items():
                output_concepts[f"resolve_{resolution_type}"] = effectiveness
            
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in output_concepts.items()}

    def _evaluate_global_coherence(self) -> float:
        """Evalúa coherencia lógica global de todos los hilos de razonamiento"""
        if not self.reasoning_threads:
            return 1.0
        
        coherence_scores = []
        
        for thread_id, thread in self.reasoning_threads.items():
            # Coherencia interna del hilo
            internal_coherence = self._evaluate_thread_coherence(thread)
            coherence_scores.append(internal_coherence)
            
            # Actualizar score del hilo
            thread["coherence_score"] = internal_coherence
        
        # Coherencia entre hilos
        inter_thread_coherence = self._evaluate_inter_thread_coherence()
        coherence_scores.append(inter_thread_coherence)
        
        return sum(coherence_scores) / len(coherence_scores)

    def _evaluate_thread_coherence(self, thread: Dict) -> float:
        """Evalúa coherencia interna de un hilo de razonamiento"""
        coherence_factors = []
        
        # Factor 1: Consistencia de premisas
        if thread["premises"]:
            premise_concentrations = [step["concentration"] for step in thread["premises"]]
            premise_consistency = self.logical_rules["consistency"](premise_concentrations)
            coherence_factors.append(premise_consistency)
        
        # Factor 2: Validez de conclusiones
        if thread["premises"] and thread["conclusions"]:
            # Simplificado: las conclusiones deberían seguir de las premisas
            avg_premise_strength = sum(step["concentration"] for step in thread["premises"]) / len(thread["premises"])
            avg_conclusion_strength = sum(step["concentration"] for step in thread["conclusions"]) / len(thread["conclusions"])
            
            # Las conclusiones no deberían ser mucho más fuertes que las premisas
            conclusion_validity = 1.0 - max(0.0, avg_conclusion_strength - avg_premise_strength)
            coherence_factors.append(conclusion_validity)
        
        # Factor 3: Ausencia de contradicciones internas
        contradiction_penalty = 0.0
        all_steps = thread["premises"] + thread["intermediate_steps"] + thread["conclusions"]
        
        for i, step1 in enumerate(all_steps):
            for step2 in all_steps[i+1:]:
                if self._steps_contradict(step1, step2):
                    contradiction_penalty += 0.2
        
        coherence_factors.append(max(0.0, 1.0 - contradiction_penalty))
        
        return sum(coherence_factors) / len(coherence_factors) if coherence_factors else 0.5

    def _steps_contradict(self, step1: Dict, step2: Dict) -> bool:
        """Verifica si dos pasos se contradicen"""
        concept1, concept2 = step1["concept"], step2["concept"]
        conc1, conc2 = step1["concentration"], step2["concentration"]
        
        # Contradicción directa
        if ("not_" + concept1 == concept2 or concept1 == "not_" + concept2):
            return conc1 > 0.6 and conc2 > 0.6
        
        # Contradicción por fuerza inconsistente del mismo concepto
        if concept1 == concept2:
            return abs(conc1 - conc2) > 0.6
        
        return False

    def _evaluate_inter_thread_coherence(self) -> float:
        """Evalúa coherencia entre diferentes hilos de razonamiento"""
        if len(self.reasoning_threads) < 2:
            return 1.0
        
        thread_pairs = []
        thread_ids = list(self.reasoning_threads.keys())
        
        for i in range(len(thread_ids)):
            for j in range(i + 1, len(thread_ids)):
                thread_pairs.append((thread_ids[i], thread_ids[j]))
        
        coherence_scores = []
        
        for thread1_id, thread2_id in thread_pairs:
            thread1 = self.reasoning_threads[thread1_id]
            thread2 = self.reasoning_threads[thread2_id]
            
            # Verificar contradicciones entre conclusiones
            conclusions1 = [step["concept"] for step in thread1["conclusions"]]
            conclusions2 = [step["concept"] for step in thread2["conclusions"]]
            
            contradiction_count = 0
            for c1 in conclusions1:
                for c2 in conclusions2:
                    if ("not_" + c1 == c2 or c1 == "not_" + c2):
                        contradiction_count += 1
            
            # Score basado en ausencia de contradicciones
            pair_coherence = 1.0 - min(1.0, contradiction_count / max(len(conclusions1), len(conclusions2), 1))
            coherence_scores.append(pair_coherence)
        
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 1.0

    def _analyze_contradictions(self) -> Dict[str, float]:
        """Analiza contradicciones detectadas y su severidad"""
        contradiction_analysis = {}
        
        if not self.contradiction_detector:
            return contradiction_analysis
        
        # Agrupar contradicciones por tipo
        contradiction_types = defaultdict(list)
        for contradiction in self.contradiction_detector:
            contradiction_types[contradiction["violation_type"]].append(contradiction)
        
        # Evaluar severidad por tipo
        for violation_type, violations in contradiction_types.items():
            # Severidad basada en frecuencia reciente
            recent_violations = [v for v in violations 
                               if time.time() - v["timestamp"] < 300]  # Últimos 5 minutos
            
            if recent_violations:
                severity = min(1.0, len(recent_violations) / 5.0)
                contradiction_analysis[violation_type] = severity
        
        return contradiction_analysis

    def _identify_missing_logical_steps(self) -> Dict[str, float]:
        """Identifica pasos lógicos faltantes en los razonamientos"""
        missing_steps = {}
        
        for thread_id, thread in self.reasoning_threads.items():
            # Verificar si hay suficientes pasos intermedios
            premise_count = len(thread["premises"])
            conclusion_count = len(thread["conclusions"])
            intermediate_count = len(thread["intermediate_steps"])
            
            # Heurística: argumentos complejos necesitan pasos intermedios
            if premise_count > 2 and conclusion_count > 0 and intermediate_count == 0:
                missing_steps[f"intermediate_steps_{thread_id}"] = 0.8
            
            # Verificar si conclusiones siguen lógicamente
            if thread["premises"] and thread["conclusions"]:
                logical_gap = self._assess_logical_gap(thread["premises"], thread["conclusions"])
                if logical_gap > 0.5:
                    missing_steps[f"logical_bridge_{thread_id}"] = logical_gap
        
        return missing_steps

    def _assess_logical_gap(self, premises: List[Dict], conclusions: List[Dict]) -> float:
        """Evalúa la brecha lógica entre premisas y conclusiones"""
        if not premises or not conclusions:
            return 0.0
        
        # Calcular fuerza promedio de premisas y conclusiones
        avg_premise_strength = sum(step["concentration"] for step in premises) / len(premises)
        avg_conclusion_strength = sum(step["concentration"] for step in conclusions) / len(conclusions)
        
        # Brecha = conclusiones más fuertes que lo que justifican las premisas
        gap = max(0.0, avg_conclusion_strength - avg_premise_strength)
        return min(1.0, gap * 2.0)

    def _coordinate_conflict_resolution(self) -> Dict[str, float]:
        """Coordina resolución de conflictos lógicos"""
        resolutions = {}
        
        # Identificar hilos con baja coherencia
        problematic_threads = {tid: thread for tid, thread in self.reasoning_threads.items()
                             if thread["coherence_score"] < 0.6}
        
        for thread_id, thread in problematic_threads.items():
            # Estrategias de resolución
            
            # 1. Debilitar premisas conflictivas
            if len(thread["premises"]) > 2:
                resolutions[f"weaken_conflicting_premises_{thread_id}"] = 1.0 - thread["coherence_score"]
            
            # 2. Añadir pasos intermedios
            premise_count = len(thread["premises"])
            conclusion_count = len(thread["conclusions"])
            if premise_count > 1 and conclusion_count > 0:
                resolutions[f"add_intermediate_steps_{thread_id}"] = 0.8
            
            # 3. Revisar operadores lógicos
            if thread["logical_operators"]:
                operator_diversity = len(set(thread["logical_operators"]))
                if operator_diversity == 1:  # Solo un tipo de operador
                    resolutions[f"diversify_operators_{thread_id}"] = 0.6
        
        return resolutions


class ConceptualBridgeBuilder(CognitiveMicelialNeuronBase):
    """Construye puentes conceptuales entre ideas aparentemente no relacionadas"""
    
    def __init__(self, neuron_id: str, bridge_discovery_threshold: float = 0.4):
        super().__init__(neuron_id, max_synapses=350)
        self.bridge_discovery_threshold = bridge_discovery_threshold
        self.conceptual_space = defaultdict(lambda: defaultdict(float))
        self.bridge_inventory = {}
        self.analogy_patterns = deque(maxlen=200)
        self.semantic_clusters = {}

    def receive_concept(self, concentration: float, concept_type: str, context: Dict = None) -> float:
        with self.lock:
            concept_domain = context.get("domain", "general") if context else "general"
            semantic_features = context.get("semantic_features", []) if context else []
            analogy_source = context.get("analogy_source", None) if context else None
            
            # Almacenar en espacio conceptual multidimensional
            self.conceptual_space[concept_domain][concept_type] = concentration
            
            # Procesar características semánticas
            if semantic_features:
                self._process_semantic_features(concept_type, semantic_features, concentration)
            
            # Procesar analogías explícitas
            if analogy_source:
                self._process_analogy(concept_type, analogy_source, concentration, context)
            
            # Búsqueda automática de puentes conceptuales
            potential_bridges = self._discover_potential_bridges(concept_type, concept_domain, concentration)
            
            # Activación basada en potencial de bridging
            bridge_potential = len(potential_bridges) / 10.0
            self.activation_level = concentration * min(1.0, bridge_potential + 0.3)
            
            return self.activation_level

    def _process_semantic_features(self, concept: str, features: List[str], concentration: float):
        """Procesa características semánticas para clustering"""
        for feature in features:
            if feature not in self.semantic_clusters:
                self.semantic_clusters[feature] = {}
            
            # Añadir concepto al cluster semántico
            if concept not in self.semantic_clusters[feature]:
                self.semantic_clusters[feature][concept] = 0.0
            
            self.semantic_clusters[feature][concept] += concentration * 0.1

    def _process_analogy(self, target_concept: str, source_concept: str, concentration: float, context: Dict):
        """Procesa una analogía explícita entre conceptos"""
        analogy_entry = {
            'source': source_concept,
            'target': target_concept,
            'strength': concentration,
            'context': context,
            'timestamp': time.time(),
            'type': context.get('analogy_type', 'structural')
        }
        
        self.analogy_patterns.append(analogy_entry)
        
        # Crear puente bidireccional
        bridge_key = tuple(sorted([source_concept, target_concept]))
        if bridge_key not in self.bridge_inventory:
            self.bridge_inventory[bridge_key] = {
                'strength': 0.0,
                'analogy_count': 0,
                'discovery_method': 'explicit_analogy',
                'creation_time': time.time()
            }
        
        bridge = self.bridge_inventory[bridge_key]
        bridge['analogy_count'] += 1
        bridge['strength'] = min(1.0, bridge['strength'] + concentration * 0.2)

    def _discover_potential_bridges(self, concept: str, domain: str, concentration: float) -> List[Tuple[str, str, float]]:
        """Descubre puentes conceptuales potenciales automáticamente"""
        potential_bridges = []
        
        # Método 1: Clustering semántico
        concept_features = []
        for feature, cluster in self.semantic_clusters.items():
            if concept in cluster and cluster[concept] > 0.2:
                concept_features.append(feature)
        
        # Buscar conceptos con características semánticas similares
        for feature in concept_features:
            for other_concept, strength in self.semantic_clusters[feature].items():
                if other_concept != concept and strength > 0.2:
                    semantic_similarity = min(strength, self.semantic_clusters[feature].get(concept, 0))
                    if semantic_similarity > self.bridge_discovery_threshold:
                        potential_bridges.append((concept, other_concept, semantic_similarity))
        
        # Método 2: Distancia conceptual en el espacio
        for other_domain, concepts in self.conceptual_space.items():
            for other_concept, other_concentration in concepts.items():
                if other_concept != concept and other_concentration > 0.3:
                    # Calcular distancia conceptual (heurística simple)
                    conceptual_distance = self._calculate_conceptual_distance(
                        concept, domain, other_concept, other_domain)
                    
                    if 0.3 < conceptual_distance < 0.8:  # Ni muy cerca ni muy lejos
                        bridge_strength = (concentration + other_concentration) / 2.0 * (1.0 - conceptual_distance)
                        if bridge_strength > self.bridge_discovery_threshold:
                            potential_bridges.append((concept, other_concept, bridge_strength))
        
        return potential_bridges

    def _calculate_conceptual_distance(self, concept1: str, domain1: str, concept2: str, domain2: str) -> float:
        """Calcula distancia conceptual heurística entre dos conceptos"""
        distance_factors = []
        
        # Factor 1: Distancia de dominio
        if domain1 == domain2:
            domain_distance = 0.0
        else:
            # Distancia heurística entre dominios (podría mejorarse con embeddings)
            domain_distance = 0.5
        distance_factors.append(domain_distance)
        
        # Factor 2: Distancia lexical simple
        common_chars = set(concept1.lower()) & set(concept2.lower())
        max_chars = max(len(set(concept1.lower())), len(set(concept2.lower())))
        lexical_similarity = len(common_chars) / max_chars if max_chars > 0 else 0.0
        lexical_distance = 1.0 - lexical_similarity
        distance_factors.append(lexical_distance)
        
        # Factor 3: Presencia en analogías históricas
        bridge_key = tuple(sorted([concept1, concept2]))
        if bridge_key in self.bridge_inventory:
            analogy_distance = 1.0 - self.bridge_inventory[bridge_key]['strength']
        else:
            analogy_distance = 0.8  # Distancia moderada si no hay historial
        distance_factors.append(analogy_distance)
        
        return sum(distance_factors) / len(distance_factors)

    def process(self, context: Dict = None) -> Dict[str, float]:
        with self.lock:
            output_concepts = {}
            
            # Proponer nuevos puentes conceptuales
            bridge_proposals = self._propose_new_bridges()
            for bridge_type, confidence in bridge_proposals.items():
                if confidence > 0.5:
                    output_concepts[f"bridge_proposal_{bridge_type}"] = confidence
                    # Añadir el puente al inventario
                    concept1, concept2 = bridge_type.split('_to_')
                    concept2 = concept2.split('_via_')[0]  # Eliminar sufijo _via_*
                    bridge_key = tuple(sorted([concept1, concept2]))
                    if bridge_key not in self.bridge_inventory:
                        self.bridge_inventory[bridge_key] = {
                            'strength': confidence,
                            'analogy_count': 1,
                            'discovery_method': 'automatic',
                            'creation_time': time.time()
                        }
            
            # Fortalecer puentes existentes exitosos
            bridge_reinforcements = self._reinforce_successful_bridges()
            for bridge_id, strength in bridge_reinforcements.items():
                output_concepts[f"strengthen_{bridge_id}"] = strength
            
            # Generar analogías estructurales
            structural_analogies = self._generate_structural_analogies()
            for analogy_type, applicability in structural_analogies.items():
                output_concepts[f"analogy_{analogy_type}"] = applicability
            
            # Identificar clusters conceptuales emergentes
            emergent_clusters = self._identify_emergent_clusters()
            for cluster_type, cohesion in emergent_clusters.items():
                output_concepts[f"cluster_{cluster_type}"] = cohesion
            
            # Añadir los puentes actuales a la salida
            for bridge_key, bridge_info in self.bridge_inventory.items():
                concept1, concept2 = bridge_key
                output_concepts[f"bridge_{concept1}_{concept2}"] = bridge_info['strength']
            
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in output_concepts.items() if v > 0.3}  # Filtrar solo conexiones fuertes

    def _propose_new_bridges(self) -> Dict[str, float]:
        """Propone nuevos puentes conceptuales no explorados"""
        proposals = {}
        
        # Analizar clusters semánticos para encontrar gaps
        for feature, cluster in self.semantic_clusters.items():
            if len(cluster) > 2:
                # Buscar conceptos en el cluster que no están conectados
                concepts = list(cluster.keys())
                for i, concept1 in enumerate(concepts):
                    for concept2 in concepts[i+1:]:
                        bridge_key = tuple(sorted([concept1, concept2]))
                        
                        # Si no existe puente pero están en el mismo cluster
                        if bridge_key not in self.bridge_inventory:
                            # Calcular potencial de puente basado en co-presencia
                            strength1 = cluster[concept1]
                            strength2 = cluster[concept2]
                            bridge_potential = min(strength1, strength2) * 0.8
                            
                            if bridge_potential > self.bridge_discovery_threshold:
                                proposals[f"{concept1}_to_{concept2}_via_{feature}"] = bridge_potential
        
        return proposals

    def _reinforce_successful_bridges(self) -> Dict[str, float]:
        """Refuerza puentes que han demostrado ser útiles"""
        reinforcements = {}
        
        for bridge_key, bridge_info in self.bridge_inventory.items():
            # Puentes con múltiples analogías exitosas
            if bridge_info['analogy_count'] > 3 and bridge_info['strength'] > 0.6:
                concept1, concept2 = bridge_key
                reinforcement_strength = min(1.0, bridge_info['strength'] * 1.1)
                reinforcements[f"{concept1}_bridge_{concept2}"] = reinforcement_strength
                
                # Actualizar fuerza del puente
                bridge_info['strength'] = reinforcement_strength
        
        return reinforcements

    def _generate_structural_analogies(self) -> Dict[str, float]:
        """Genera analogías estructurales basadas en patrones"""
        analogies = {}
        
        if len(self.analogy_patterns) > 5:
            # Buscar patrones estructurales en analogías exitosas
            successful_analogies = [a for a in self.analogy_patterns if a['strength'] > 0.6]
            
            # Agrupar por tipo de analogía
            analogy_types = defaultdict(list)
            for analogy in successful_analogies:
                analogy_types[analogy['type']].append(analogy)
            
            # Generar nuevas analogías basadas en patrones exitosos
            for analogy_type, examples in analogy_types.items():
                if len(examples) > 2:
                    avg_strength = sum(ex['strength'] for ex in examples) / len(examples)
                    applicability = min(1.0, avg_strength * len(examples) / 5.0)
                    analogies[f"structural_{analogy_type}"] = applicability
        
        return analogies

    def _identify_emergent_clusters(self) -> Dict[str, float]:
        """Identifica clusters conceptuales emergentes"""
        clusters = {}
        
        # Analizar conectividad en el inventario de puentes
        concept_connections = defaultdict(set)
        for bridge_key, bridge_info in self.bridge_inventory.items():
            if bridge_info['strength'] > 0.5:
                concept1, concept2 = bridge_key
                concept_connections[concept1].add(concept2)
                concept_connections[concept2].add(concept1)
        
        # Identificar clusters densamente conectados
        for concept, connections in concept_connections.items():
            if len(connections) > 2:
                # Calcular cohesión del cluster
                cluster_concepts = list(connections) + [concept]
                total_possible_connections = len(cluster_concepts) * (len(cluster_concepts) - 1) // 2
                actual_connections = 0
                
                for i, c1 in enumerate(cluster_concepts):
                    for c2 in cluster_concepts[i+1:]:
                        bridge_key = tuple(sorted([c1, c2]))
                        if bridge_key in self.bridge_inventory:
                            actual_connections += 1
                
                cohesion = actual_connections / total_possible_connections if total_possible_connections > 0 else 0.0
                if cohesion > 0.6:
                    clusters[f"dense_cluster_around_{concept}"] = cohesion
        
        return clusters


class InsightPropagator(CognitiveMicelialNeuronBase):
    """Difunde descubrimientos conceptuales y insights por toda la red cognitiva"""
    
    def __init__(self, neuron_id: str, propagation_radius: int = 500):
        super().__init__(neuron_id, max_synapses=400)
        self.propagation_radius = propagation_radius
        self.insight_catalog = {}
        self.propagation_history = deque(maxlen=100)
        self.insight_validation_scores = {}
        self.diffusion_gradients = defaultdict(lambda: defaultdict(float))

    def receive_concept(self, concentration: float, concept_type: str, context: Dict = None) -> float:
        with self.lock:
            insight_type = context.get("insight_type", "discovery") if context else "discovery"
            source_region = context.get("source_region", "unknown") if context else "unknown"
            validation_level = context.get("validation", 0.5) if context else 0.5
            
            # Catalogar insight con metadata completa
            insight_id = f"{concept_type}_{insight_type}_{int(time.time())}"
            self.insight_catalog[insight_id] = {
                'concept': concept_type,
                'type': insight_type,
                'strength': concentration,
                'source_region': source_region,
                'validation': validation_level,
                'discovery_time': time.time(),
                'propagation_count': 0,
                'regions_reached': set([source_region])
            }
            
            # Evaluar si el insight merece propagación
            propagation_priority = self._evaluate_propagation_priority(
                concept_type, insight_type, concentration, validation_level)
            
            if propagation_priority > 0.6:
                # Marcar para propagación inmediata
                self._initiate_propagation(insight_id, propagation_priority)
            
            self.activation_level = concentration * propagation_priority
            return self.activation_level

    def _evaluate_propagation_priority(self, concept: str, insight_type: str, 
                                     concentration: float, validation: float) -> float:
        """Evalúa prioridad de propagación de un insight"""
        priority_factors = []
        
        # Factor 1: Novedad del insight
        similar_insights = [i for i in self.insight_catalog.values() 
                           if i['concept'] == concept and i['type'] == insight_type]
        novelty = 1.0 - min(0.9, len(similar_insights) / 10.0)
        priority_factors.append(novelty)
        
        # Factor 2: Fuerza y validación
        strength_validation = (concentration + validation) / 2.0
        priority_factors.append(strength_validation)
        
        # Factor 3: Tipo de insight
        insight_importance = {
            "discovery": 1.0,
            "contradiction": 0.9,
            "synthesis": 0.8,
            "analogy": 0.7,
            "refinement": 0.5
        }
        priority_factors.append(insight_importance.get(insight_type, 0.6))
        
        # Factor 4: Demanda de la red (cuántas regiones podrían beneficiarse)
        network_demand = self._assess_network_demand(concept, insight_type)
        priority_factors.append(network_demand)
        
        return sum(priority_factors) / len(priority_factors)

    def _assess_network_demand(self, concept: str, insight_type: str) -> float:
        """Evalúa cuánto demanda la red este tipo de insight"""
        # Contar regiones que han mostrado interés en este concepto
        interested_regions = set()
        
        for insight_id, insight_info in self.insight_catalog.items():
            if insight_info['concept'] == concept:
                interested_regions.update(insight_info['regions_reached'])
        
        # Más regiones interesadas = mayor demanda
        demand = len(interested_regions) / 10.0  # Normalizar
        return min(1.0, demand)

    def _initiate_propagation(self, insight_id: str, priority: float):
        """Inicia propagación de un insight específico"""
        insight = self.insight_catalog[insight_id]
        
        propagation_entry = {
            'insight_id': insight_id,
            'concept': insight['concept'],
            'priority': priority,
            'start_time': time.time(),
            'target_regions': self._select_target_regions(insight),
            'propagation_method': self._select_propagation_method(insight, priority)
        }
        
        self.propagation_history.append(propagation_entry)
        
        # Actualizar contador de propagación
        insight['propagation_count'] += 1

    def _select_target_regions(self, insight: Dict) -> List[str]:
        """Selecciona regiones objetivo para propagación"""
        targets = []
        
        # Método 1: Regiones con conceptos relacionados
        concept = insight['concept']
        for other_insight in self.insight_catalog.values():
            if (other_insight['concept'] != concept and 
                self._concepts_related(concept, other_insight['concept'])):
                targets.extend(other_insight['regions_reached'])
        
        # Método 2: Regiones que han solicitado este tipo de insight
        insight_type = insight['type']
        # (Aquí se conectaría con un sistema de solicitudes/demandas)
        
        # Limitar y deduplificar
        targets = list(set(targets))
        return targets[:self.propagation_radius // 100]  # Limitar alcance

    def _concepts_related(self, concept1: str, concept2: str) -> bool:
        """Verifica si dos conceptos están relacionados"""
        # Heurística simple: buscar raíces comunes o substring
        return (concept1 in concept2 or concept2 in concept1 or 
                len(set(concept1.split('_')) & set(concept2.split('_'))) > 0)

    def _select_propagation_method(self, insight: Dict, priority: float) -> str:
        """Selecciona método de propagación basado en prioridad e insight"""
        if priority > 0.8:
            return "broadcast"  # Difusión amplia
        elif priority > 0.6:
            return "targeted"   # Propagación dirigida
        else:
            return "gradual"    # Difusión lenta

    def process(self, context: Dict = None) -> Dict[str, float]:
        with self.lock:
            output_concepts = {}
            
            # Procesar propagaciones pendientes
            active_propagations = self._process_active_propagations()
            for prop_type, intensity in active_propagations.items():
                output_concepts[prop_type] = intensity
            
            # Evaluar efectividad de propagaciones pasadas
            propagation_effectiveness = self._evaluate_propagation_effectiveness()
            for effectiveness_metric, value in propagation_effectiveness.items():
                output_concepts[f"effectiveness_{effectiveness_metric}"] = value
            
            # Optimizar rutas de propagación
            route_optimizations = self._optimize_propagation_routes()
            for optimization, improvement in route_optimizations.items():
                output_concepts[f"optimize_{optimization}"] = improvement
            
            # Detectar insights que necesitan re-propagación
            repropagation_needs = self._detect_repropagation_needs()
            for need_type, urgency in repropagation_needs.items():
                output_concepts[f"repropagate_{need_type}"] = urgency
            
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in output_concepts.items()}

    def _process_active_propagations(self) -> Dict[str, float]:
        """Procesa propagaciones actualmente en curso"""
        active = {}
        current_time = time.time()
        
        for prop_entry in list(self.propagation_history)[-10:]:  # Últimas 10 propagaciones
            time_since_start = current_time - prop_entry['start_time']
            
            # Propagaciones activas (menos de 5 minutos)
            if time_since_start < 300:
                insight_id = prop_entry['insight_id']
                if insight_id in self.insight_catalog:
                    insight = self.insight_catalog[insight_id]
                    
                    # Calcular intensidad de propagación actual
                    base_intensity = insight['strength'] * prop_entry['priority']
                    
                    # Decaimiento temporal
                    time_decay = math.exp(-time_since_start / 180.0)  # 3 minutos half-life
                    current_intensity = base_intensity * time_decay
                    
                    if current_intensity > 0.1:
                        method = prop_entry['propagation_method']
                        active[f"{method}_propagation_{insight['concept']}"] = current_intensity
        
        return active

    def _evaluate_propagation_effectiveness(self) -> Dict[str, float]:
        """Evalúa efectividad de propagaciones pasadas"""
        effectiveness = {}
        
        if len(self.propagation_history) > 5:
            # Análisis de propagaciones completadas (más de 5 minutos)
            completed = [p for p in self.propagation_history 
                        if time.time() - p['start_time'] > 300]
            
            if completed:
                # Efectividad por método de propagación
                methods = defaultdict(list)
                for prop in completed:
                    insight_id = prop['insight_id']
                    if insight_id in self.insight_catalog:
                        insight = self.insight_catalog[insight_id]
                        reach = len(insight['regions_reached'])
                        methods[prop['propagation_method']].append(reach)
                
                for method, reaches in methods.items():
                    avg_reach = sum(reaches) / len(reaches)
                    effectiveness[f"{method}_method"] = min(1.0, avg_reach / 5.0)
        
        return effectiveness

    def _optimize_propagation_routes(self) -> Dict[str, float]:
        """Optimiza rutas de propagación futuras"""
        optimizations = {}
        
        # Identificar cuellos de botella en propagación
        region_traffic = defaultdict(int)
        for prop in self.propagation_history:
            for region in prop.get('target_regions', []):
                region_traffic[region] += 1
        
        # Sugerir rutas alternativas para regiones congestionadas
        avg_traffic = sum(region_traffic.values()) / len(region_traffic) if region_traffic else 0
        for region, traffic in region_traffic.items():
            if traffic > avg_traffic * 1.5:
                congestion_level = min(1.0, traffic / (avg_traffic * 2.0))
                optimizations[f"bypass_congested_{region}"] = congestion_level
        
        return optimizations

    def _detect_repropagation_needs(self) -> Dict[str, float]:
        """Detecta insights que necesitan ser re-propagados"""
        needs = {}
        
        # Insights que no alcanzaron suficiente alcance
        for insight_id, insight in self.insight_catalog.items():
            if insight['propagation_count'] > 0:
                reach_ratio = len(insight['regions_reached']) / max(insight['propagation_count'], 1)
                
                # Si el alcance fue bajo para la cantidad de propagaciones
                if reach_ratio < 0.3 and insight['validation'] > 0.7:
                    urgency = (0.3 - reach_ratio) * insight['validation']
                    needs[f"low_reach_{insight['concept']}"] = urgency
                
                # Insights importantes que se propagaron hace mucho tiempo
                time_since_last = time.time() - insight['discovery_time']
                if (time_since_last > 3600 and insight['strength'] > 0.8 and 
                    insight['validation'] > 0.8):
                    decay_urgency = min(1.0, time_since_last / 7200.0)  # 2 horas máximo
                    needs[f"refresh_{insight['concept']}"] = decay_urgency * insight['strength']
        
        return needs


class DeepReflectionOrchestrator(CognitiveMicelialNeuronBase):
    """Orquesta procesos de reflexión profunda y metacognición"""
    
    def __init__(self, neuron_id: str, reflection_depth_levels: int = 5):
        super().__init__(neuron_id, max_synapses=300)
        self.reflection_depth_levels = reflection_depth_levels
        self.reflection_states = {
            f"level_{i}": {"active": False, "content": {}, "duration": 0.0} 
            for i in range(reflection_depth_levels)
        }
        self.metacognitive_monitoring = {}
        self.reflection_triggers = deque(maxlen=20)
        self.deep_insights = deque(maxlen=30)

    def receive_concept(self, concentration: float, concept_type: str, context: Dict = None) -> float:
        with self.lock:
            reflection_trigger = context.get("reflection_trigger", None) if context else None
            metacognitive_signal = context.get("metacognitive", False) if context else False
            
            # Procesar triggers de reflexión
            if reflection_trigger:
                self.reflection_triggers.append({
                    'trigger_type': reflection_trigger,
                    'concept': concept_type,
                    'strength': concentration,
                    'timestamp': time.time()
                })
                
                # Determinar nivel de reflexión apropiado
                reflection_level = self._determine_reflection_level(reflection_trigger, concentration)
                self._activate_reflection_level(reflection_level, concept_type, concentration)
            
            # Procesar señales metacognitivas
            if metacognitive_signal:
                self._process_metacognitive_signal(concept_type, concentration, context)
            
            # Activación basada en profundidad de reflexión requerida
            required_depth = self._assess_required_reflection_depth(concept_type, concentration)
            self.activation_level = concentration * (required_depth / self.reflection_depth_levels)
            
            return self.activation_level

    def _determine_reflection_level(self, trigger_type: str, strength: float) -> int:
        """Determina qué nivel de reflexión es apropiado"""
        base_levels = {
            "contradiction": 3,
            "novel_insight": 4,
            "paradigm_shift": 5,
            "ethical_dilemma": 4,
            "conceptual_gap": 2,
            "validation_failure": 3
        }
        
        base_level = base_levels.get(trigger_type, 1)
        
        # Ajustar por fuerza de la señal
        if strength > 0.8:
            base_level = min(self.reflection_depth_levels, base_level + 1)
        elif strength < 0.3:
            base_level = max(1, base_level - 1)
        
        return base_level

    def _activate_reflection_level(self, level: int, concept: str, concentration: float):
        """Activa un nivel específico de reflexión"""
        if 0 < level <= self.reflection_depth_levels:
            level_key = f"level_{level}"
            self.reflection_states[level_key]["active"] = True
            self.reflection_states[level_key]["content"][concept] = concentration
            self.reflection_states[level_key]["start_time"] = time.time()

    def _process_metacognitive_signal(self, concept: str, concentration: float, context: Dict):
        """Procesa señales metacognitivas (pensar sobre el pensamiento)"""
        metacognitive_type = context.get("metacognitive_type", "monitoring")
        
        if metacognitive_type not in self.metacognitive_monitoring:
            self.metacognitive_monitoring[metacognitive_type] = {
                "concepts": defaultdict(float),
                "activity_level": 0.0,
                "last_update": time.time()
            }
        
        monitor = self.metacognitive_monitoring[metacognitive_type]
        monitor["concepts"][concept] += concentration * 0.1
        monitor["activity_level"] = (monitor["activity_level"] * 0.9 + concentration * 0.1)
        monitor["last_update"] = time.time()

    def _assess_required_reflection_depth(self, concept: str, concentration: float) -> float:
        """Evalúa qué profundidad de reflexión requiere este concepto"""
        depth_indicators = []
        
        # Indicador 1: Complejidad conceptual (heurística por longitud y estructura)
        concept_complexity = min(5.0, len(concept.split('_')) + len(concept) / 10.0)
        depth_indicators.append(concept_complexity)
        
        # Indicador 2: Fuerza de concentración (conceptos fuertes requieren más reflexión)
        depth_indicators.append(concentration * 3.0)
        
        # Indicador 3: Frecuencia de aparición (conceptos frecuentes necesitan menos reflexión profunda)
        concept_frequency = sum(1 for insight in self.insight_catalog.values() 
                               if insight['concept'] == concept)
        frequency_factor = max(1.0, 5.0 - concept_frequency)
        depth_indicators.append(frequency_factor)
        
        # Indicador 4: Número de triggers de reflexión activos
        active_triggers = sum(1 for state in self.reflection_states.values() if state["active"])
        trigger_depth = min(5.0, active_triggers + 1.0)
        depth_indicators.append(trigger_depth)
        
        avg_depth = sum(depth_indicators) / len(depth_indicators)
        return min(float(self.reflection_depth_levels), avg_depth)

    def process(self, context: Dict = None) -> Dict[str, float]:
        with self.lock:
            output_concepts = {}
            
            # Procesar cada nivel de reflexión activo
            for level_name, state in self.reflection_states.items():
                if state["active"]:
                    level_outputs = self._process_reflection_level(level_name, state)
                    for output_type, strength in level_outputs.items():
                        output_concepts[f"{level_name}_{output_type}"] = strength
            
            # Generar insights metacognitivos
            metacognitive_insights = self._generate_metacognitive_insights()
            for insight_type, confidence in metacognitive_insights.items():
                output_concepts[f"metacognitive_{insight_type}"] = confidence
            
            # Coordinar transiciones entre niveles de reflexión
            level_transitions = self._coordinate_reflection_transitions()
            for transition_type, necessity in level_transitions.items():
                output_concepts[f"transition_{transition_type}"] = necessity
            
            # Generar insights profundos consolidados
            deep_insights = self._consolidate_deep_insights()
            for insight_type, depth_score in deep_insights.items():
                if depth_score > 0.7:
                    output_concepts[f"deep_insight_{insight_type}"] = depth_score
                    
                    # Almacenar insight profundo
                    self.deep_insights.append({
                        'type': insight_type,
                        'depth_score': depth_score,
                        'timestamp': time.time(),
                        'reflection_levels_involved': [name for name, state in self.reflection_states.items() if state["active"]]
                    })
            
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in output_concepts.items()}

    def _process_reflection_level(self, level_name: str, state: Dict) -> Dict[str, float]:
        """Procesa un nivel específico de reflexión"""
        level_outputs = {}
        current_time = time.time()
        
        # Calcular duración de reflexión en este nivel
        if "start_time" in state:
            state["duration"] = current_time - state["start_time"]
        
        level_num = int(level_name.split('_')[1])
        
        # Procesamiento específico por nivel
        if level_num == 1:  # Reflexión básica
            level_outputs.update(self._basic_reflection(state))
        elif level_num == 2:  # Análisis de implicaciones
            level_outputs.update(self._implication_analysis(state))
        elif level_num == 3:  # Búsqueda de contradicciones
            level_outputs.update(self._contradiction_search(state))
        elif level_num == 4:  # Síntesis conceptual profunda
            level_outputs.update(self._deep_conceptual_synthesis(state))
        elif level_num == 5:  # Metacognición y paradigmas
            level_outputs.update(self._paradigm_reflection(state))
        
        # Desactivar nivel si ha estado activo mucho tiempo
        if state["duration"] > 600:  # 10 minutos máximo por nivel
            state["active"] = False
            state["content"] = {}
            level_outputs["reflection_timeout"] = 1.0
        
        return level_outputs

    def _basic_reflection(self, state: Dict) -> Dict[str, float]:
        """Reflexión de nivel 1: análisis básico de conceptos"""
        outputs = {}
        
        for concept, concentration in state["content"].items():
            # Validación básica de consistencia
            if concentration > 0.5:
                outputs[f"validated_{concept}"] = concentration * 0.8
            
            # Identificación de aspectos que necesitan más exploración
            if concentration < 0.4:
                outputs[f"needs_exploration_{concept}"] = 1.0 - concentration
        
        return outputs

    def _implication_analysis(self, state: Dict) -> Dict[str, float]:
        """Reflexión de nivel 2: análisis de implicaciones"""
        outputs = {}
        
        for concept, concentration in state["content"].items():
            # Generar implicaciones lógicas
            if concentration > 0.6:
                outputs[f"implies_further_investigation_{concept}"] = concentration * 0.9
                outputs[f"potential_consequences_{concept}"] = concentration * 0.7
            
            # Identificar suposiciones implícitas
            outputs[f"hidden_assumptions_{concept}"] = concentration * 0.6
        
        return outputs

    def _contradiction_search(self, state: Dict) -> Dict[str, float]:
        """Reflexión de nivel 3: búsqueda activa de contradicciones"""
        outputs = {}
        
        concepts = list(state["content"].keys())
        
        # Buscar contradicciones potenciales entre conceptos
        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i+1:]:
                contradiction_likelihood = self._assess_contradiction_likelihood(
                    concept1, state["content"][concept1],
                    concept2, state["content"][concept2]
                )
                
                if contradiction_likelihood > 0.5:
                    outputs[f"potential_contradiction_{concept1}_vs_{concept2}"] = contradiction_likelihood
        
        return outputs

    def _assess_contradiction_likelihood(self, concept1: str, conc1: float, 
                                       concept2: str, conc2: float) -> float:
        """Evalúa probabilidad de contradicción entre dos conceptos"""
        # Heurísticas simples para detectar contradicciones potenciales
        
        # Contradicción directa por negación
        if "not_" + concept1 == concept2 or concept1 == "not_" + concept2:
            return min(conc1, conc2)
        
        # Contradicción semántica (keywords opuestos)
        opposing_pairs = [
            ("positive", "negative"), ("increase", "decrease"), ("presence", "absence"),
            ("strong", "weak"), ("fast", "slow"), ("high", "low")
        ]
        
        for pos, neg in opposing_pairs:
            if ((pos in concept1 and neg in concept2) or 
                (neg in concept1 and pos in concept2)):
                return min(conc1, conc2) * 0.8
        
        return 0.0

    def _deep_conceptual_synthesis(self, state: Dict) -> Dict[str, float]:
        """Reflexión de nivel 4: síntesis conceptual profunda"""
        outputs = {}
        
        concepts = list(state["content"].items())
        
        if len(concepts) > 1:
            # Buscar síntesis emergentes
            for i, (concept1, conc1) in enumerate(concepts):
                for concept2, conc2 in concepts[i+1:]:
                    synthesis_potential = min(conc1, conc2) * 0.9
                    if synthesis_potential > 0.5:
                        outputs[f"deep_synthesis_{concept1}_with_{concept2}"] = synthesis_potential
            
            # Generar abstracciones de orden superior
            if len(concepts) > 2:
                avg_concentration = sum(conc for _, conc in concepts) / len(concepts)
                if avg_concentration > 0.6:
                    concept_names = [name for name, _ in concepts]
                    abstraction_name = f"abstract_pattern_{'_'.join(concept_names[:3])}"
                    outputs[abstraction_name] = avg_concentration * 0.8
        
        return outputs

    def _paradigm_reflection(self, state: Dict) -> Dict[str, float]:
        """Reflexión de nivel 5: reflexión paradigmática y filosófica"""
        outputs = {}
        
        for concept, concentration in state["content"].items():
            if concentration > 0.7:
                # Cuestionar paradigmas fundamentales
                outputs[f"paradigm_question_{concept}"] = concentration * 0.9
                
                # Explorar marcos alternativos
                outputs[f"alternative_framework_{concept}"] = concentration * 0.8
                
                # Examinar presupuestos filosóficos
                outputs[f"philosophical_assumptions_{concept}"] = concentration * 0.7
        
        return outputs

    def _generate_metacognitive_insights(self) -> Dict[str, float]:
        """Genera insights sobre el propio proceso de pensamiento"""
        metacognitive_insights = {}
        
        # Análisis de patrones de activación de reflexión
        if len(self.reflection_triggers) > 5:
            trigger_types = [t['trigger_type'] for t in self.reflection_triggers]
            most_common_trigger = max(set(trigger_types), key=trigger_types.count)
            
            trigger_frequency = trigger_types.count(most_common_trigger) / len(trigger_types)
            if trigger_frequency > 0.4:
                metacognitive_insights[f"frequent_trigger_{most_common_trigger}"] = trigger_frequency
        
        # Análisis de efectividad de niveles de reflexión
        active_levels = [name for name, state in self.reflection_states.items() if state["active"]]
        if len(active_levels) > 2:
            metacognitive_insights["multi_level_reflection_active"] = len(active_levels) / self.reflection_depth_levels
        
        # Análisis de duración de reflexiones
        avg_durations = {}
        for level_name, state in self.reflection_states.items():
            if "duration" in state and state["duration"] > 0:
                if level_name not in avg_durations:
                    avg_durations[level_name] = []
                avg_durations[level_name].append(state["duration"])
        
        for level, durations in avg_durations.items():
            if len(durations) > 1:
                avg_duration = sum(durations) / len(durations)
                if avg_duration > 300:  # Reflexiones largas (5+ minutos)
                    metacognitive_insights[f"deep_reflection_tendency_{level}"] = min(1.0, avg_duration / 600.0)
        
        return metacognitive_insights

    def _coordinate_reflection_transitions(self) -> Dict[str, float]:
        """Coordina transiciones entre niveles de reflexión"""
        transitions = {}
        
        # Detectar cuándo subir de nivel
        for i in range(self.reflection_depth_levels - 1):
            current_level = f"level_{i}"
            next_level = f"level_{i+1}"
            
            current_state = self.reflection_states[current_level]
            next_state = self.reflection_states[next_level]
            
            # Subir si el nivel actual está saturado y el siguiente inactivo
            if (current_state["active"] and not next_state["active"] and
                current_state.get("duration", 0) > 120):  # 2 minutos de reflexión
                
                avg_concentration = 0.0
                if current_state["content"]:
                    avg_concentration = sum(current_state["content"].values()) / len(current_state["content"])
                
                if avg_concentration > 0.6:
                    transitions[f"escalate_to_{next_level}"] = avg_concentration
        
        # Detectar cuándo bajar de nivel o terminar
        for i in range(self.reflection_depth_levels):
            level_name = f"level_{i}"
            if level_name in self.reflection_states:  # Verificar que el nivel existe
                state = self.reflection_states[level_name]
                
                if (state.get("active", False) and state.get("duration", 0) > 300):  # 5 minutos
                    # Evaluar si la reflexión está convergiendo
                    if state.get("content"):
                        content_stability = self._assess_content_stability(state["content"])
                        if content_stability > 0.8:
                            transitions[f"conclude_{level_name}"] = content_stability
        
        return transitions

    def _assess_content_stability(self, content: Dict[str, float]) -> float:
        """Evalúa si el contenido de reflexión se ha estabilizado"""
        if len(content) < 2:
            return 1.0
        
        # Calcular varianza de concentraciones
        concentrations = list(content.values())
        mean_conc = sum(concentrations) / len(concentrations)
        variance = sum((c - mean_conc) ** 2 for c in concentrations) / len(concentrations)
        
        # Estabilidad alta = baja varianza
        stability = 1.0 - min(1.0, variance * 2.0)
        return stability

    def _consolidate_deep_insights(self) -> Dict[str, float]:
        """Consolida insights profundos de múltiples niveles de reflexión"""
        consolidated = {}
        
        # Buscar conceptos que aparecen en múltiples niveles
        cross_level_concepts = defaultdict(list)
        
        for level_name, state in self.reflection_states.items():
            if state["active"] and state["content"]:
                level_num = int(level_name.split('_')[1])
                for concept, concentration in state["content"].items():
                    cross_level_concepts[concept].append((level_num, concentration))
        
        # Consolidar conceptos que aparecen en múltiples niveles
        for concept, level_data in cross_level_concepts.items():
            if len(level_data) > 1:  # Aparece en múltiples niveles
                # Calcular score de profundidad ponderado
                total_depth_score = 0.0
                total_weight = 0.0
                
                for level_num, concentration in level_data:
                    weight = level_num * concentration  # Niveles más altos pesan más
                    total_depth_score += weight
                    total_weight += level_num
                
                if total_weight > 0:
                    normalized_depth = total_depth_score / total_weight
                    consolidated[concept] = min(1.0, normalized_depth)
        
        return consolidated


class InterDomainMessenger(CognitiveMicelialNeuronBase):
    """Facilita comunicación conceptual entre dominios cognitivos especializados"""
    
    def __init__(self, neuron_id: str, specialized_domains: List[str]):
        super().__init__(neuron_id, max_synapses=250)
        self.specialized_domains = set(specialized_domains)
        self.domain_interfaces = {domain: {} for domain in specialized_domains}
        self.translation_protocols = {}
        self.message_routing_table = defaultdict(list)
        self.cross_domain_vocabulary = defaultdict(set)

    def receive_concept(self, concentration: float, concept_type: str, context: Dict = None) -> float:
        with self.lock:
            source_domain = context.get("source_domain", "general") if context else "general"
            target_domains = context.get("target_domains", []) if context else []
            message_type = context.get("message_type", "information") if context else "information"
            
            # Registrar concepto en interfaz del dominio fuente
            if source_domain in self.domain_interfaces:
                self.domain_interfaces[source_domain][concept_type] = concentration
            
            # Crear/actualizar vocabulario cross-domain
            self.cross_domain_vocabulary[concept_type].add(source_domain)
            
            # Procesar mensaje para dominios objetivo
            if target_domains:
                translation_success = self._translate_concept_for_domains(
                    concept_type, concentration, source_domain, target_domains, message_type)
                self.activation_level = concentration * translation_success
            else:
                # Sin dominios objetivo específicos - broadcast limitado
                broadcast_success = self._broadcast_to_compatible_domains(
                    concept_type, concentration, source_domain)
                self.activation_level = concentration * broadcast_success
            
            return self.activation_level

    def _translate_concept_for_domains(self, concept: str, concentration: float, 
                                     source_domain: str, target_domains: List[str], 
                                     message_type: str) -> float:
        """Traduce concepto para dominios objetivo específicos"""
        translation_successes = []
        
        for target_domain in target_domains:
            if target_domain in self.specialized_domains:
                # Crear protocolo de traducción si no existe
                protocol_key = f"{source_domain}_to_{target_domain}"
                if protocol_key not in self.translation_protocols:
                    self.translation_protocols[protocol_key] = {
                        "success_rate": 0.7,
                        "concept_mappings": {},
                        "usage_count": 0
                    }
                
                protocol = self.translation_protocols[protocol_key]
                
                # Intentar traducción
                translated_concept = self._perform_concept_translation(
                    concept, source_domain, target_domain, protocol)
                
                if translated_concept:
                    # Almacenar en tabla de ruteo
                    routing_entry = {
                        "original_concept": concept,
                        "translated_concept": translated_concept,
                        "source_domain": source_domain,
                        "target_domain": target_domain,
                        "concentration": concentration,
                        "message_type": message_type,
                        "timestamp": time.time()
                    }
                    
                    self.message_routing_table[target_domain].append(routing_entry)
                    
                    # Mantener solo mensajes recientes
                    if len(self.message_routing_table[target_domain]) > 20:
                        self.message_routing_table[target_domain].pop(0)
                    
                    # Actualizar protocolo
                    protocol["usage_count"] += 1
                    protocol["concept_mappings"][concept] = translated_concept
                    
                    translation_successes.append(protocol["success_rate"])
                else:
                    translation_successes.append(0.0)
                    # Reducir tasa de éxito del protocolo
                    protocol["success_rate"] = max(0.3, protocol["success_rate"] - 0.05)
        
        return sum(translation_successes) / len(translation_successes) if translation_successes else 0.0

    def _perform_concept_translation(self, concept: str, source_domain: str, 
                                   target_domain: str, protocol: Dict) -> Optional[str]:
        """Realiza traducción conceptual entre dominios"""
        # Usar mapeo existente si está disponible
        if concept in protocol["concept_mappings"]:
            return protocol["concept_mappings"][concept]
        
        # Traducción heurística basada en dominios
        translation_rules = {
            ("technical", "intuitive"): lambda c: c.replace("_", " ").replace("algorithm", "process"),
            ("abstract", "concrete"): lambda c: f"practical_{c}" if "theory" in c else c,
            ("logical", "emotional"): lambda c: c.replace("reasoning", "feeling").replace("analysis", "intuition"),
            ("quantitative", "qualitative"): lambda c: c.replace("measure", "quality").replace("metric", "aspect")
        }
        
        # Buscar regla aplicable
        for (src, tgt), rule in translation_rules.items():
            if source_domain == src and target_domain == tgt:
                try:
                    translated = rule(concept)
                    return translated if translated != concept else None
                except:
                    continue
        
        # Traducción genérica: añadir prefijo del dominio objetivo
        if len(concept.split('_')) < 3:  # Evitar conceptos ya muy complejos
            return f"{target_domain}_{concept}"
        
        return None

    def _broadcast_to_compatible_domains(self, concept: str, concentration: float, 
                                       source_domain: str) -> float:
        """Broadcast a dominios compatibles sin objetivo específico"""
        compatible_domains = []
        
        # Encontrar dominios que han usado conceptos similares
        for domain in self.specialized_domains:
            if domain != source_domain:
                domain_interface = self.domain_interfaces.get(domain, {})
                
                # Verificar si hay conceptos relacionados en este dominio
                related_concepts = [c for c in domain_interface.keys() 
                                  if self._concepts_semantically_related(concept, c)]
                
                if len(related_concepts) > 0:
                    compatibility = len(related_concepts) / max(len(domain_interface), 1)
                    compatible_domains.append((domain, compatibility))
        
        # Enviar a dominios más compatibles
        successful_broadcasts = 0
        for domain, compatibility in sorted(compatible_domains, key=lambda x: x[1], reverse=True)[:3]:
            if compatibility > 0.3:
                # Crear entrada de ruteo simplificada
                routing_entry = {
                    "original_concept": concept,
                    "translated_concept": f"{domain}_interpretation_{concept}",
                    "source_domain": source_domain,
                    "target_domain": domain,
                    "concentration": concentration * compatibility,
                    "message_type": "broadcast",
                    "timestamp": time.time()
                }
                
                self.message_routing_table[domain].append(routing_entry)
                successful_broadcasts += 1
        
        return successful_broadcasts / max(len(compatible_domains), 1) if compatible_domains else 0.0

    def _concepts_semantically_related(self, concept1: str, concept2: str) -> bool:
        """Verifica si dos conceptos están semánticamente relacionados"""
        # Heurística simple: palabras comunes, prefijos/sufijos similares
        words1 = set(concept1.lower().split('_'))
        words2 = set(concept2.lower().split('_'))
        
        # Palabras en común
        if len(words1 & words2) > 0:
            return True
        
        # Prefijos similares
        if len(concept1) > 3 and len(concept2) > 3:
            if concept1[:3] == concept2[:3]:
                return True
        
        # Sufijos similares
        if len(concept1) > 3 and len(concept2) > 3:
            if concept1[-3:] == concept2[-3:]:
                return True
        
        return False

    def process(self, context: Dict = None) -> Dict[str, float]:
        with self.lock:
            output_concepts = {}
            
            # Procesar mensajes pendientes en cada dominio
            for domain, messages in self.message_routing_table.items():
                if messages:
                    domain_output = self._process_domain_messages(domain, messages)
                    for output_type, strength in domain_output.items():
                        output_concepts[f"{domain}_{output_type}"] = strength
            
            # Optimizar protocolos de traducción
            protocol_optimizations = self._optimize_translation_protocols()
            for optimization, improvement in protocol_optimizations.items():
                output_concepts[f"optimize_{optimization}"] = improvement
            
            # Identificar gaps de comunicación
            communication_gaps = self._identify_communication_gaps()
            for gap_type, severity in communication_gaps.items():
                output_concepts[f"gap_{gap_type}"] = severity
            
            # Proponer nuevas rutas de comunicación
            new_routes = self._propose_new_communication_routes()
            for route_type, viability in new_routes.items():
                output_concepts[f"new_route_{route_type}"] = viability
            
            self.last_activation_time = time.time()
            return {k: v * self.cognitive_resilience for k, v in output_concepts.items()}

    def _process_domain_messages(self, domain: str, messages: List[Dict]) -> Dict[str, float]:
        """Procesa mensajes pendientes para un dominio específico"""
        domain_output = {}
        
        # Agrupar mensajes por tipo
        message_types = defaultdict(list)
        for msg in messages:
            message_types[msg["message_type"]].append(msg)
        
        # Procesar cada tipo de mensaje
        for msg_type, msg_list in message_types.items():
            if msg_type == "urgent":
                # Procesamiento inmediato
                total_urgency = sum(msg["concentration"] for msg in msg_list)
                domain_output[f"urgent_processing"] = min(1.0, total_urgency)
            
            elif msg_type == "information":
                # Integración gradual de información
                avg_info_strength = sum(msg["concentration"] for msg in msg_list) / len(msg_list)
                domain_output[f"information_integration"] = avg_info_strength * 0.8
            
            elif msg_type == "broadcast":
                # Procesamiento de broadcasts
                broadcast_diversity = len(set(msg["original_concept"] for msg in msg_list))
                domain_output[f"broadcast_diversity"] = min(1.0, broadcast_diversity / 5.0)
        
        # Señal de carga de procesamiento del dominio
        total_messages = len(messages)
        processing_load = min(1.0, total_messages / 15.0)
        domain_output["processing_load"] = processing_load
        
        return domain_output

    def _optimize_translation_protocols(self) -> Dict[str, float]:
        """Optimiza protocolos de traducción basado en uso histórico"""
        optimizations = {}
        
        for protocol_key, protocol in self.translation_protocols.items():
            usage = protocol["usage_count"]
            success_rate = protocol["success_rate"]
            
            # Protocolos muy usados con baja tasa de éxito necesitan optimización
            if usage > 10 and success_rate < 0.6:
                optimization_need = (usage / 20.0) * (1.0 - success_rate)
                optimizations[f"improve_{protocol_key}"] = min(1.0, optimization_need)
            
            # Protocolos exitosos pueden ser generalizados
            elif usage > 5 and success_rate > 0.8:
                generalization_potential = success_rate * min(1.0, usage / 10.0)
                optimizations[f"generalize_{protocol_key}"] = generalization_potential
        
        return optimizations

    def _identify_communication_gaps(self) -> Dict[str, float]:
        """Identifica gaps en la comunicación entre dominios"""
        gaps = {}
        
        # Analizar dominios con poca comunicación saliente
        for domain in self.specialized_domains:
            outgoing_messages = sum(1 for messages in self.message_routing_table.values()
                                  for msg in messages if msg["source_domain"] == domain)
            
            if outgoing_messages < 2:  # Dominio poco comunicativo
                isolation_level = 1.0 - (outgoing_messages / 5.0)
                gaps[f"isolated_domain_{domain}"] = isolation_level
        
        # Analizar pares de dominios sin comunicación directa
        domains = list(self.specialized_domains)
        for i, domain1 in enumerate(domains):
            for domain2 in domains[i+1:]:
                protocol_key = f"{domain1}_to_{domain2}"
                reverse_protocol_key = f"{domain2}_to_{domain1}"
                
                # Si no hay protocolos en ninguna dirección
                if (protocol_key not in self.translation_protocols and 
                    reverse_protocol_key not in self.translation_protocols):
                    
                    # Evaluar si sería útil conectar estos dominios
                    connection_utility = self._assess_domain_connection_utility(domain1, domain2)
                    if connection_utility > 0.4:
                        gaps[f"missing_connection_{domain1}_{domain2}"] = connection_utility
        
        return gaps

    def _assess_domain_connection_utility(self, domain1: str, domain2: str) -> float:
        """Evalúa utilidad de conectar dos dominios"""
        utility_factors = []
        
        # Factor 1: Actividad en ambos dominios
        activity1 = len(self.domain_interfaces.get(domain1, {}))
        activity2 = len(self.domain_interfaces.get(domain2, {}))
        combined_activity = min(1.0, (activity1 + activity2) / 10.0)
        utility_factors.append(combined_activity)
        
        # Factor 2: Conceptos potencialmente transferibles
        interface1 = self.domain_interfaces.get(domain1, {})
        interface2 = self.domain_interfaces.get(domain2, {})
        
        transferable_concepts = 0
        for concept1 in interface1:
            for concept2 in interface2:
                if self._concepts_semantically_related(concept1, concept2):
                    transferable_concepts += 1
        
        transferability = min(1.0, transferable_concepts / 5.0)
        utility_factors.append(transferability)
        
        # Factor 3: Demanda histórica (mensajes que podrían haber sido útiles)
        # (Simplificado - en implementación real se analizaría historial de solicitudes)
        historical_demand = 0.5  # Valor neutro por defecto
        utility_factors.append(historical_demand)
        
        return sum(utility_factors) / len(utility_factors)

    def _propose_new_communication_routes(self) -> Dict[str, float]:
        """Propone nuevas rutas de comunicación inter-dominio"""
        new_routes = {}
        
        # Analizar cadenas de traducción potenciales (A->B->C en lugar de A->C)
        domains = list(self.specialized_domains)
        
        for source in domains:
            for target in domains:
                if source != target:
                    direct_route = f"{source}_to_{target}"
                    
                    # Si no hay ruta directa, buscar rutas indirectas
                    if direct_route not in self.translation_protocols:
                        # Buscar dominios intermedios
                        for intermediate in domains:
                            if intermediate not in [source, target]:
                                route1 = f"{source}_to_{intermediate}"
                                route2 = f"{intermediate}_to_{target}"
                                
                                # Si ambas rutas existen
                                if (route1 in self.translation_protocols and 
                                    route2 in self.translation_protocols):
                                    
                                    # Calcular viabilidad de ruta indirecta
                                    success1 = self.translation_protocols[route1].get("success_rate", 0.0)
                                    success2 = self.translation_protocols[route2].get("success_rate", 0.0)
                                    combined_success = success1 * success2 * 0.8  # Penalización por indirección
                                    
                                    if combined_success > 0.5:
                                        new_routes[f"indirect_{source}_via_{intermediate}_to_{target}"] = combined_success
        
        # Asegurarse de devolver un diccionario, incluso si está vacío
        return new_routes
        
class CommunicatorNeuron(CognitiveMicelialNeuronBase):
    """
    Neurona especializada en la comunicación entre diferentes partes del sistema neuronal.
    Facilita la transferencia de información entre subsistemas neuronales.
    """
    
    def __init__(self, neuron_id: str, communication_bandwidth: int = 100):
        """
        Inicializa una nueva neurona comunicadora.
        
        Args:
            neuron_id: Identificador único para la neurona
            communication_bandwidth: Ancho de banda de comunicación (número de conexiones simultáneas)
        """
        super().__init__(neuron_id, max_synapses=communication_bandwidth * 2)  # Conexiones de entrada y salida
        self.communication_bandwidth = communication_bandwidth
        self.active_connections = 0
        self.message_queue = deque(maxlen=1000)  # Cola de mensajes pendientes
        self.communication_protocols = {}
        self.latency = 0.1  # Segundos de latencia de procesamiento
        self.throughput = 0.0  # Mensajes por segundo
        
        # Métricas de rendimiento
        self.messages_processed = 0
        self.total_latency = 0.0
        self.last_throughput_calculation = time.time()
        
    def receive_concept(self, concentration: float, concept_type: str, context: Dict = None):
        """
        Procesa un concepto recibido y lo encola para transmisión.
        
        Args:
            concentration: Intensidad de la señal/concepto
            concept_type: Tipo de concepto recibido
            context: Contexto adicional para el procesamiento
        """
        context = context or {}
        message = {
            'concept': concept_type,
            'concentration': concentration,
            'timestamp': time.time(),
            'source': context.get('source', 'unknown'),
            'destination': context.get('destination', 'broadcast'),
            'priority': context.get('priority', 1.0)
        }
        
        # Añadir a la cola de mensajes
        self.message_queue.append(message)
        
        # Actualizar métricas
        current_time = time.time()
        time_since_last = current_time - self.last_throughput_calculation
        if time_since_last > 1.0:  # Actualizar throughput cada segundo
            self.throughput = self.messages_processed / time_since_last if time_since_last > 0 else 0
            self.messages_processed = 0
            self.last_throughput_calculation = current_time
        
        return super().receive_concept(concentration, concept_type, context)
    
    def process(self, context: Dict = None):
        """
        Procesa los mensajes en cola según el ancho de banda disponible.
        """
        context = context or {}
        processed_messages = 0
        start_time = time.time()
        
        # Procesar mensajes mientras tengamos ancho de banda disponible
        while (self.message_queue and 
               self.active_connections < self.communication_bandwidth and
               processed_messages < self.communication_bandwidth):
            
            message = self.message_queue.popleft()
            self._process_message(message, context)
            self.messages_processed += 1
            processed_messages += 1
            
            # Pequeño retraso para simular procesamiento
            time.sleep(self.latency / 1000.0)  # Convertir a segundos
        
        # Actualizar métricas de latencia
        if processed_messages > 0:
            self.total_latency += (time.time() - start_time) / processed_messages
        
        # Lógica de procesamiento heredada
        return super().process(context)
    
    def _process_message(self, message: Dict, context: Dict):
        """
        Procesa un mensaje individual.
        
        Args:
            message: Mensaje a procesar
            context: Contexto de procesamiento
        """
        try:
            # Aplicar protocolo de comunicación si existe para este tipo de mensaje
            protocol = self.communication_protocols.get(message['concept'])
            if protocol:
                message = protocol(message, context)
            
            # Transmitir el mensaje a través de las sinapsis de salida
            self._transmit_message(message)
            
        except Exception as e:
            logging.error(f"Error procesando mensaje: {str(e)}")
    
    def _transmit_message(self, message: Dict):
        """
        Transmite un mensaje a través de las sinapsis de salida.
        
        Args:
            message: Mensaje a transmitir
        """
        # Implementar lógica de transmisión aquí
        # Esto sería similar a la lógica en otras neuronas para activar sinapsis
        pass
    
    def add_communication_protocol(self, concept_type: str, protocol_func: callable):
        """
        Añade un protocolo de comunicación para un tipo de concepto específico.
        
        Args:
            concept_type: Tipo de concepto al que aplicar el protocolo
            protocol_func: Función que procesa el mensaje (debe aceptar mensaje y contexto)
        """
        self.communication_protocols[concept_type] = protocol_func
    
    def get_performance_metrics(self) -> Dict:
        """
        Devuelve métricas de rendimiento de la neurona comunicadora.
        
        Returns:
            Diccionario con métricas de rendimiento
        """
        return {
            'throughput': self.throughput,
            'latency': self.total_latency / self.messages_processed if self.messages_processed > 0 else 0,
            'active_connections': self.active_connections,
            'queue_size': len(self.message_queue),
            'bandwidth_utilization': (self.active_connections / self.communication_bandwidth) * 100
        }


class ChemicalLearningNeuron(CognitiveMicelialNeuronBase):
    """
    Neurona especializada en aprendizaje basado en señales químicas.
    Implementa plasticidad dependiente de neurotransmisores y modulación sináptica.
    """
    
    def __init__(self, neuron_id: str, learning_rate: float = 0.01, plasticity_threshold: float = 0.5):
        """
        Inicializa una nueva neurona de aprendizaje químico.
        
        Args:
            neuron_id: Identificador único para la neurona
            learning_rate: Tasa de aprendizaje inicial
            plasticity_threshold: Umbral para la plasticidad sináptica
        """
        super().__init__(neuron_id)
        self.learning_rate = learning_rate
        self.plasticity_threshold = plasticity_threshold
        self.neurotransmitter_levels = {
            'dopamine': 0.0,
            'serotonin': 0.0,
            'acetylcholine': 0.0,
            'norepinephrine': 0.0,
            'gaba': 0.0
        }
        self.synaptic_plasticity = {}  # Mapeo de ID de sinapsis a nivel de plasticidad
        self.learning_history = []
        self.activity_history = []  # Historial de actividad reciente
        self.last_plasticity_update = time.time()
        
        # Inicializar atributos esperados por el sistema
        self.activation_level = 0.0
        self.last_activation = 0.0
        self.synapses = []  # Lista de sinapsis de salida
        self.inhibitory = False  # Por defecto, no es inhibitoria
        
    def receive_concept(self, concentration: float, concept_type: str, context: Dict = None) -> float:
        """
        Procesa un concepto recibido, actualizando el estado de la neurona según los niveles de neurotransmisores.
        
        Args:
            concentration: Intensidad del concepto recibido (0.0 a 1.0)
            concept_type: Tipo de concepto recibido
            context: Contexto adicional para el procesamiento
            
        Returns:
            float: Nivel de activación resultante después de procesar el concepto
        """
        try:
            # Asegurar que los parámetros tengan valores válidos
            if concentration is None:
                concentration = 0.0
            if not isinstance(concept_type, str):
                concept_type = str(concept_type) if concept_type is not None else "unknown"
            if context is None:
                context = {}
            
            # Registrar la actividad actual
            current_time = time.time()
            self.last_activation = current_time
            
            # Registrar el concepto en el historial de aprendizaje
            learning_entry = {
                'timestamp': current_time,
                'concept_type': concept_type,
                'concentration': concentration,
                'context': context
            }
            self.learning_history.append(learning_entry)
            
            # Mantener un registro de la actividad reciente
            self.activity_history.append({
                'time': current_time,
                'activation': concentration,
                'type': 'input'
            })
            
            # Limitar el tamaño del historial de actividad
            if len(self.activity_history) > 1000:  # Mantener solo las 1000 entradas más recientes
                self.activity_history = self.activity_history[-1000:]
            
            # Calcular modulación basada en neurotransmisores
            learning_modulation = self.calculate_learning_rate_modulation() if hasattr(self, 'calculate_learning_rate_modulation') else 1.0
            
            # Actualizar plasticidad sináptica basada en la actividad
            if current_time - self.last_plasticity_update > 1.0:  # Actualizar como máximo una vez por segundo
                if hasattr(self, '_update_plasticity_based_on_activity'):
                    self._update_plasticity_based_on_activity()
                self.last_plasticity_update = current_time
            
            # Calcular activación basada en la concentración y modulación
            activation = float(concentration) * float(learning_modulation)
            
            # Aplicar función de activación no lineal (sigmoide)
            try:
                activation = 1 / (1 + math.exp(-activation * 10 + 5))  # Escalado para mejor sensibilidad
            except (OverflowError, ValueError):
                activation = 1.0  # En caso de desbordamiento
            
            # Actualizar el nivel de activación de la neurona
            self.activation_level = activation
            self.last_activation_time = current_time
            
            # Actualizar neurotransmisores basados en la activación
            if hasattr(self, '_update_neurotransmitters'):
                self._update_neurotransmitters(activation)
            
            return activation
            
        except Exception as e:
            # Registrar el error pero no fallar
            print(f"Advertencia en receive_concept: {str(e)}")
            return 0.0
        
    def _update_neurotransmitters(self, activation: float):
        """Actualiza los niveles de neurotransmisores basados en la activación"""
        # La dopamina aumenta con la novedad y recompensa
        self.neurotransmitter_levels['dopamine'] = min(1.0, 
            self.neurotransmitter_levels['dopamine'] * 0.9 + activation * 0.1)
            
        # La serotonina se relaciona con el estado de ánimo y la confianza
        self.neurotransmitter_levels['serotonin'] = min(1.0,
            self.neurotransmitter_levels['serotonin'] * 0.95 + activation * 0.05)
            
        # La acetilcolina está relacionada con el aprendizaje y la atención
        self.neurotransmitter_levels['acetylcholine'] = min(1.0,
            self.neurotransmitter_levels['acetylcholine'] * 0.8 + activation * 0.2)
            
        # La noradrenalina aumenta con la alerta y el estrés
        self.neurotransmitter_levels['norepinephrine'] = min(1.0,
            self.neurotransmitter_levels['norepinephrine'] * 0.7 + activation * 0.3)
            
        # El GABA inhibe la activación excesiva
        self.neurotransmitter_levels['gaba'] = min(1.0,
            self.neurotransmitter_levels['gaba'] * 0.85 + (1 - activation) * 0.15)
        
    def update_neurotransmitter_levels(self, delta: Dict[str, float]):
        """
        Actualiza los niveles de neurotransmisores.
        
        Args:
            delta: Diccionario con los cambios en los niveles de neurotransmisores
        """
        for nt, value in delta.items():
            if nt in self.neurotransmitter_levels:
                self.neurotransmitter_levels[nt] = max(0.0, min(1.0, self.neurotransmitter_levels[nt] + value))
    
    def calculate_learning_rate_modulation(self) -> float:
        """
        Calcula la modulación de la tasa de aprendizaje basada en los niveles de neurotransmisores.
        
        Returns:
            Factor de modulación de la tasa de aprendizaje
        """
        mod = 1.0
        mod *= 1.0 + self.neurotransmitter_levels['dopamine'] * 0.5  # Aumenta aprendizaje
        mod *= 1.0 - self.neurotransmitter_levels['gaba'] * 0.3      # Disminuye aprendizaje
        return max(0.1, min(5.0, mod))  # Limitar el rango de modulación
    
    def update_synaptic_plasticity(self, synapse_id: str, activity: float):
        """
        Actualiza la plasticidad de una sinapsis específica.
        
        Args:
            synapse_id: ID de la sinapsis
            activity: Nivel de actividad reciente (0.0 a 1.0)
        """
        if synapse_id not in self.synaptic_plasticity:
            self.synaptic_plasticity[synapse_id] = 0.5  # Valor inicial de plasticidad
            
        # Aplicar regla de aprendizaje Hebbiano modificada
        current_plasticity = self.synaptic_plasticity[synapse_id]
        delta = (activity - 0.5) * self.learning_rate * self.calculate_learning_rate_modulation()
        
        # Aplicar límites a la plasticidad
        self.synaptic_plasticity[synapse_id] = max(0.0, min(1.0, current_plasticity + delta))
        
        # Registrar el cambio para análisis
        self.learning_history.append({
            'timestamp': time.time(),
            'synapse_id': synapse_id,
            'new_plasticity': self.synaptic_plasticity[synapse_id],
            'activity': activity,
            'neurotransmitters': self.neurotransmitter_levels.copy()
        })
        
        # Limitar el historial
        if len(self.learning_history) > 1000:
            self.learning_history = self.learning_history[-1000:]
    
    def process(self, context: Dict = None):
        """
        Procesa las entradas y actualiza el estado de la neurona.
        """
        context = context or {}
        current_time = time.time()
        
        # Actualizar plasticidad periódicamente
        if current_time - self.last_plasticity_update > 1.0:  # Cada segundo
            self._update_plasticity_based_on_activity()
            self.last_plasticity_update = current_time
        
        # Procesamiento estándar de la neurona
        return super().process(context)
    
    def _update_plasticity_based_on_activity(self):
        """
        Actualiza la plasticidad basada en la actividad reciente.
        """
        # Calcular actividad promedio reciente
        if self.activity_history:
            # Extraer los valores de activación del historial
            activation_values = [entry['activation'] for entry in self.activity_history]
            recent_activity = sum(activation_values) / len(activation_values)
        else:
            recent_activity = 0.0
        
        # Ajustar plasticidad basada en actividad global
        for synapse_id in list(self.synaptic_plasticity.keys()):
            current = self.synaptic_plasticity[synapse_id]
            # Si la actividad es alta, aumentar plasticidad; si es baja, disminuirla
            delta = (recent_activity - 0.5) * 0.01
            self.synaptic_plasticity[synapse_id] = max(0.0, min(1.0, current + delta))
    
    def get_learning_metrics(self) -> Dict:
        """
        Devuelve métricas de aprendizaje de la neurona.
        
        Returns:
            Diccionario con métricas de aprendizaje
        """
        avg_plasticity = sum(self.synaptic_plasticity.values()) / max(1, len(self.synaptic_plasticity))
        
        return {
            'avg_plasticity': avg_plasticity,
            'total_learning_events': len(self.learning_history),
            'neurotransmitter_levels': self.neurotransmitter_levels.copy(),
            'active_synapses': len([p for p in self.synaptic_plasticity.values() if p > 0.1])
        }


# Factory para crear diferentes tipos de neuronas miceliales cognitivas
def create_cognitive_micelial_neuron(neuron_type: str, neuron_id: str, **kwargs) -> CognitiveMicelialNeuronBase:
    """Factory para crear diferentes tipos de neuronas miceliales cognitivas"""
    
    neuron_classes = {
        'abstract_pattern_integrator': AbstractPatternIntegrator,
        'contextual_temporal_integrator': ContextualTemporalIntegrator,
        'knowledge_synthesizer': KnowledgeSynthesizer,
        'global_coherence_coordinator': GlobalCoherenceCoordinator,
        'conceptual_bridge_builder': ConceptualBridgeBuilder,
        'insight_propagator': InsightPropagator,
        'deep_reflection_orchestrator': DeepReflectionOrchestrator,
        'inter_domain_messenger': InterDomainMessenger,
        'communicator': CommunicatorNeuron,
        'chemical_learner': ChemicalLearningNeuron
    }
    
    if neuron_type not in neuron_classes:
        available_types = list(neuron_classes.keys())
        raise ValueError(f"Unknown cognitive micelial neuron type: {neuron_type}. Available types: {available_types}")
    
    return neuron_classes[neuron_type](neuron_id, **kwargs)


class CognitiveMicelialNetworkMaintenance:
    """Sistema de mantenimiento para la red micelial cognitiva de pensamiento profundo"""
    
    def __init__(self):
        self.neurons = []
        self.maintenance_interval = 120.0  # Mantenimiento cada 2 minutos
        self.last_maintenance = time.time()
        self.cognitive_health_threshold = 0.7
        self.network_coherence_score = 0.8
        
    def add_neuron(self, neuron: CognitiveMicelialNeuronBase):
        self.neurons.append(neuron)
    
    def run_maintenance_cycle(self):
        """Ejecuta ciclo de mantenimiento para toda la red cognitiva"""
        current_time = time.time()
        delta_time = current_time - self.last_maintenance
        
        for neuron in self.neurons:
            # Envejecimiento cognitivo gradual
            neuron.age_neuron(delta_time)
            
            # Mantenimiento de coherencia conceptual
            self._maintain_conceptual_coherence(neuron)
            
            # Optimización de conexiones cognitivas
            self._optimize_cognitive_connections(neuron)
            
            # Consolidación de insights
            self._consolidate_insights(neuron)
        
        # Mantenimiento global de coherencia de red
        self._maintain_global_cognitive_coherence()
        
        # Optimización de flujos de pensamiento
        self._optimize_thought_flows()
        
        self.last_maintenance = current_time
    
    def _maintain_conceptual_coherence(self, neuron: CognitiveMicelialNeuronBase):
        """Mantiene coherencia conceptual de una neurona"""
        # Verificar consistencia en concentraciones de conceptos
        if hasattr(neuron, 'concept_concentration'):
            total_concentration = sum(neuron.concept_concentration.values())
            
            # Normalizar si la concentración total es demasiado alta
            if total_concentration > 3.0:
                normalization_factor = 2.0 / total_concentration
                for concept_type in neuron.concept_concentration:
                    neuron.concept_concentration[concept_type] *= normalization_factor
        
        # Limpiar conceptos con concentración muy baja
        if hasattr(neuron, 'concept_concentration'):
            low_concentration_concepts = [c for c, conc in neuron.concept_concentration.items() 
                                        if conc < 0.01]
            for concept in low_concentration_concepts:
                del neuron.concept_concentration[concept]
    
    def _optimize_cognitive_connections(self, neuron: CognitiveMicelialNeuronBase):
        """Optimiza conexiones cognitivas de una neurona"""
        if not hasattr(neuron, 'synapses'):
            return
        
        # Fortalecer sinapsis cognitivamente productivas
        for synapse in neuron.synapses:
            if hasattr(synapse, 'cognitive_productivity'):
                if synapse.cognitive_productivity > 0.8:
                    # Aumentar peso de sinapsis productivas
                    if hasattr(synapse, 'weight'):
                        synapse.weight = min(2.0, synapse.weight + 0.05)
            
            # Marcar sinapsis poco productivas para poda
            elif hasattr(synapse, 'cognitive_productivity'):
                if synapse.cognitive_productivity < 0.2:
                    if hasattr(synapse, 'weight'):
                        synapse.weight = max(0.1, synapse.weight - 0.02)
        
        # Podar sinapsis con peso muy bajo
        if hasattr(neuron, 'synapses'):
            productive_synapses = [s for s in neuron.synapses 
                                 if not hasattr(s, 'weight') or s.weight > 0.15]
            neuron.synapses = productive_synapses
    
    def _consolidate_insights(self, neuron: CognitiveMicelialNeuronBase):
        """Consolida insights distribuidos en la neurona"""
        if hasattr(neuron, 'distributed_insights'):
            # Consolidar insights similares
            insight_groups = defaultdict(list)
            
            for insight_id, insight_data in neuron.distributed_insights.items():
                insight_type = insight_data.get('type', 'general')
                insight_groups[insight_type].append((insight_id, insight_data))
            
            # Mergear insights similares del mismo tipo
            for insight_type, insights in insight_groups.items():
                if len(insights) > 3:
                    # Mantener solo los 3 insights más fuertes de cada tipo
                    sorted_insights = sorted(insights, key=lambda x: x[1].get('strength', 0.0), reverse=True)
                    
                    # Conservar los top 3
                    keep_insights = sorted_insights[:3]
                    remove_insights = sorted_insights[3:]
                    
                    # Consolidar fuerza en los que se mantienen
                    total_removed_strength = sum(insight[1].get('strength', 0.0) for insight in remove_insights)
                    boost_per_kept = total_removed_strength / len(keep_insights)
                    
                    for insight_id, insight_data in keep_insights:
                        insight_data['strength'] = min(1.0, insight_data.get('strength', 0.0) + boost_per_kept)
                    
                    # Remover insights redundantes
                    for insight_id, _ in remove_insights:
                        if insight_id in neuron.distributed_insights:
                            del neuron.distributed_insights[insight_id]
    
    def _maintain_global_cognitive_coherence(self):
        """Mantiene coherencia cognitiva global de toda la red"""
        # Detectar inconsistencias entre neuronas
        global_concepts = defaultdict(list)
        
        for neuron in self.neurons:
            if hasattr(neuron, 'concept_concentration'):
                for concept, concentration in neuron.concept_concentration.items():
                    global_concepts[concept].append((neuron.neuron_id, concentration))
        
        # Identificar conceptos con concentraciones muy inconsistentes
        inconsistent_concepts = []
        for concept, neuron_data in global_concepts.items():
            if len(neuron_data) > 1:
                concentrations = [data[1] for data in neuron_data]
                variance = self._calculate_variance(concentrations)
                if variance > 0.3:  # Varianza alta indica inconsistencia
                    inconsistent_concepts.append((concept, variance))
        
        # Actualizar score de coherencia global
        if inconsistent_concepts:
            total_inconsistency = sum(variance for _, variance in inconsistent_concepts)
            self.network_coherence_score = max(0.0, 1.0 - total_inconsistency / 5.0)
        else:
            self.network_coherence_score = min(1.0, self.network_coherence_score + 0.01)
    
    def _calculate_variance(self, data: List[float]) -> float:
        """Calcula varianza de una lista de valores"""
        if len(data) < 2:
            return 0.0
        mean = sum(data) / len(data)
        return sum((x - mean) ** 2 for x in data) / len(data)
    
    def _optimize_thought_flows(self):
        """Optimiza flujos de pensamiento en toda la red"""
        # Identificar cuellos de botella cognitivos
        cognitive_bottlenecks = []
        
        for neuron in self.neurons:
            if hasattr(neuron, 'cognitive_interference'):
                if neuron.cognitive_interference > 0.7:
                    cognitive_bottlenecks.append(neuron)
        
        # Redistribuir carga cognitiva
        if cognitive_bottlenecks:
            for bottleneck_neuron in cognitive_bottlenecks:
                # Encontrar neuronas con menor carga
                low_load_neurons = [n for n in self.neurons 
                                  if (hasattr(n, 'cognitive_interference') and 
                                      n.cognitive_interference < 0.3 and 
                                      n != bottleneck_neuron)]
                
                if low_load_neurons and hasattr(bottleneck_neuron, 'concept_concentration'):
                    # Transferir algunos conceptos a neuronas con menos carga
                    concepts_to_transfer = [(c, conc) for c, conc in 
                                          bottleneck_neuron.concept_concentration.items() 
                                          if conc < 0.5]  # Transferir conceptos débiles
                    
                    if concepts_to_transfer and low_load_neurons:
                        target_neuron = low_load_neurons[0]  # Simplificado: usar la primera
                        
                        # Transferir hasta 2 conceptos
                        for concept, concentration in concepts_to_transfer[:2]:
                            if hasattr(target_neuron, 'concept_concentration'):
                                target_neuron.concept_concentration[concept] = concentration * 0.8
                                del bottleneck_neuron.concept_concentration[concept]
                                
                                # Reducir interferencia del cuello de botella
                                bottleneck_neuron.cognitive_interference *= 0.9
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de toda la red cognitiva"""
        stats = {
            "total_neurons": len(self.neurons),
            "network_coherence": self.network_coherence_score,
            "average_age": 0.0,
            "average_resilience": 0.0,
            "total_concepts": 0,
            "neuron_types": defaultdict(int)
        }
        
        if self.neurons:
            stats["average_age"] = sum(n.age for n in self.neurons) / len(self.neurons)
            stats["average_resilience"] = sum(n.cognitive_resilience for n in self.neurons) / len(self.neurons)
            
            for neuron in self.neurons:
                # Contar tipos de neuronas
                neuron_class = neuron.__class__.__name__
                stats["neuron_types"][neuron_class] += 1
                
                # Contar conceptos totales
                if hasattr(neuron, 'concept_concentration'):
                    stats["total_concepts"] += len(neuron.concept_concentration)
        
        return stats


# ============ SISTEMA DE INICIALIZACIÓN Y TESTING ============

def create_cognitive_micelial_network(config: Dict[str, Any]) -> List[CognitiveMicelialNeuronBase]:
    """Crea una red completa de neuronas miceliales cognitivas"""
    network = []
    
    # Configuración por defecto
    default_config = {
        "abstract_pattern_integrators": 2,
        "contextual_temporal_integrators": 2,
        "knowledge_synthesizers": 3,
        "global_coherence_coordinators": 1,
        "conceptual_bridge_builders": 2,
        "insight_propagators": 2,
        "deep_reflection_orchestrators": 1,
        "inter_domain_messengers": 3
    }
    
    # Mergear configuración
    final_config = {**default_config, **config}
    
    # Crear neuronas según configuración
    neuron_id_counter = 1
    
    for neuron_type, count in final_config.items():
        for i in range(count):
            neuron_id = f"{neuron_type}_{neuron_id_counter:03d}"
            
            # Parámetros específicos por tipo
            if neuron_type == "inter_domain_messengers":
                domains = ["logical", "creative", "analytical", "intuitive", "emotional"]
                selected_domains = domains[i*2:(i*2)+3]  # 3 dominios por messenger
                neuron = create_cognitive_micelial_neuron(
                    "inter_domain_messenger", neuron_id, 
                    specialized_domains=selected_domains
                )
            elif neuron_type == "knowledge_synthesizers":
                specializations = ["scientific", "philosophical", "practical", "creative", "analytical"]
                selected_specs = specializations[i*2:(i*2)+2]  # 2 especializaciones por synthesizer
                neuron = create_cognitive_micelial_neuron(
                    "knowledge_synthesizer", neuron_id,
                    domain_specializations=selected_specs
                )
            else:
                # Usar configuración por defecto para otros tipos
                clean_type = neuron_type.rstrip('s')  # Remover plural
                neuron = create_cognitive_micelial_neuron(clean_type, neuron_id)
            
            network.append(neuron)
            neuron_id_counter += 1
    
    return network


def demonstrate_cognitive_micelial_system():
    """Demostración del sistema de neuronas miceliales cognitivas"""
    print("=== Sistema de Neuronas Miceliales Cognitivas ===")
    print("Optimizado para pensamiento profundo y procesamiento conceptual\n")
    
    # Crear red de ejemplo
    config = {
        "abstract_pattern_integrators": 1,
        "contextual_temporal_integrators": 1,
        "knowledge_synthesizers": 1,
        "global_coherence_coordinators": 1,
        "conceptual_bridge_builders": 1,
        "insight_propagators": 1,
        "deep_reflection_orchestrators": 1,
        "inter_domain_messengers": 1
    }
    
    network = create_cognitive_micelial_network(config)
    print(f"Red creada con {len(network)} neuronas cognitivas")
    
    # Crear sistema de mantenimiento
    maintenance_system = CognitiveMicelialNetworkMaintenance()
    for neuron in network:
        maintenance_system.add_neuron(neuron)
    
    print("\nTipos de neuronas en la red:")
    neuron_types = {}
    for neuron in network:
        neuron_type = neuron.__class__.__name__
        neuron_types[neuron_type] = neuron_types.get(neuron_type, 0) + 1
    
    for neuron_type, count in neuron_types.items():
        print(f"  - {neuron_type}: {count}")
    
    # Simular procesamiento conceptual
    print("\n=== Simulación de Pensamiento Profundo ===")
    
    # Ejemplo 1: Integración de patrones abstractos
    pattern_integrator = network[0]  # AbstractPatternIntegrator
    print(f"\n1. {pattern_integrator.__class__.__name__} procesando conceptos abstractos...")
    
    # Conceptos de ejemplo con diferentes niveles de abstracción
    test_concepts = [
        ("consciousness", 0.8, {"abstraction_level": 4, "related_concepts": ["awareness", "experience"]}),
        ("emergence", 0.7, {"abstraction_level": 3, "related_concepts": ["complexity", "systems"]}),
        ("causality", 0.6, {"abstraction_level": 3, "related_concepts": ["determinism", "correlation"]})
    ]
    
    for concept, concentration, context in test_concepts:
        response = pattern_integrator.receive_concept(concentration, concept, context)
        print(f"  - Concepto '{concept}' (nivel {context['abstraction_level']}): respuesta {response:.3f}")
    
    output = pattern_integrator.process()
    print(f"  - Salida del integrador: {len(output)} señales conceptuales generadas")
    
    # Ejemplo 2: Coordinación de coherencia global
    coherence_coordinator = next(n for n in network if isinstance(n, GlobalCoherenceCoordinator))
    print(f"\n2. {coherence_coordinator.__class__.__name__} verificando coherencia...")
    
    # Simular razonamiento con potencial contradicción
    reasoning_steps = [
        ("premise_all_swans_white", 0.8, {"reasoning_thread": "swan_logic", "logical_role": "premise"}),
        ("premise_australian_discovery", 0.9, {"reasoning_thread": "swan_logic", "logical_role": "premise"}),
        ("conclusion_not_all_swans_white", 0.7, {"reasoning_thread": "swan_logic", "logical_role": "conclusion"})
    ]
    
    for concept, concentration, context in reasoning_steps:
        response = coherence_coordinator.receive_concept(concentration, concept, context)
        print(f"  - Paso lógico '{concept}': coherencia {response:.3f}")
    
    coherence_output = coherence_coordinator.process()
    print(f"  - Análisis de coherencia: {len(coherence_output)} señales de coordinación")
    
    # Ejemplo 3: Construcción de puentes conceptuales
    bridge_builder = next(n for n in network if isinstance(n, ConceptualBridgeBuilder))
    print(f"\n3. {bridge_builder.__class__.__name__} construyendo puentes...")
    
    bridge_concepts = [
        ("neural_networks", 0.8, {"domain": "computer_science", "semantic_features": ["networks", "learning", "adaptation"]}),
        ("mycelial_networks", 0.7, {"domain": "biology", "semantic_features": ["networks", "communication", "distributed"]}),
        ("social_networks", 0.6, {"domain": "sociology", "semantic_features": ["networks", "information", "influence"]})
    ]
    
    for concept, concentration, context in bridge_concepts:
        response = bridge_builder.receive_concept(concentration, concept, context)
        print(f"  - Concepto '{concept}' ({context['domain']}): potencial {response:.3f}")
    
    bridge_output = bridge_builder.process()
    print(f"  - Puentes propuestos: {len(bridge_output)} conexiones conceptuales")
    
    # Ejecutar mantenimiento
    print(f"\n4. Ejecutando mantenimiento de red...")
    maintenance_system.run_maintenance_cycle()
    stats = maintenance_system.get_network_stats()
    
    print(f"  - Coherencia de red: {stats['network_coherence']:.3f}")
    print(f"  - Conceptos totales: {stats['total_concepts']}")
    print(f"  - Resilience promedio: {stats['average_resilience']:.3f}")
    
    print(f"\n=== Sistema Cognitivo Micelial Listo ===")
    print("Optimizado para:")
    print("  ✓ Integración conceptual profunda")
    print("  ✓ Mantenimiento de coherencia lógica")
    print("  ✓ Construcción de puentes entre dominios")
    print("  ✓ Propagación de insights")
    print("  ✓ Reflexión metacognitiva")
    print("  ✓ Comunicación inter-dominio")
    print("  ✓ Longevidad de conocimiento")
    
    return network, maintenance_system


if __name__ == "__main__":
    # Ejecutar demostración
    network, maintenance = demonstrate_cognitive_micelial_system()
    
    print(f"\nSistema completo inicializado con {len(network)} neuronas cognitivas.")
    print("Listo para integración con neuronas animales para pensamiento híbrido.")