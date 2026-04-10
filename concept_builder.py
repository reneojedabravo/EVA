import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Set, Optional, Tuple
import numpy as np

class ConceptBuilder:
    def __init__(self, brain):
        self.brain = brain
        self.concepts = {}  # Almacena conceptos construidos
        self.threshold = 5  # Frecuencia mínima de co-ocurrencia
        
        # Patrones universales aprendibles (sin idioma específico)
        self.learned_patterns = {
            'property_indicators': {},  # Palabras que típicamente indican propiedades
            'category_markers': {},     # Palabras que marcan categorías
            'relationship_words': {},   # Palabras que indican relaciones
            'negation_words': set(),    # Palabras de negación aprendidas
            'intensity_modifiers': {}   # Modificadores de intensidad
        }
        
    def detect_candidate_clusters(self) -> List[Dict]:
        """Encuentra grupos de palabras que co-ocurren frecuentemente con métricas mejoradas."""
        clusters = []
        
        # Obtener clusters del subconsciente
        for pattern in self.brain.tripartite_mind.subconscious.pattern_buffer:
            if pattern["type"] == "semantic_cluster" and len(pattern["words"]) >= 3:
                # Calcular cohesión del cluster
                cohesion_score = self._calculate_cluster_cohesion(pattern["words"])
                
                cluster_data = {
                    "words": pattern["words"],
                    "cohesion": cohesion_score,
                    "frequency": pattern.get("frequency", 1),
                    "contexts": pattern.get("contexts", [])
                }
                clusters.append(cluster_data)
        
        # Ordenar por cohesión y frecuencia
        clusters.sort(key=lambda x: (x["cohesion"], x["frequency"]), reverse=True)
        return clusters
    
    def _calculate_cluster_cohesion(self, words: List[str]) -> float:
        """Calcula qué tan cohesionado está un cluster basado en co-ocurrencias."""
        if len(words) < 2:
            return 0.0
            
        total_pairs = len(words) * (len(words) - 1) / 2
        strong_assocs = self.brain.learning_system.get_strong_associations()
        
        connected_pairs = 0
        for i, word1 in enumerate(words):
            for word2 in words[i+1:]:
                if word1 in strong_assocs and word2 in strong_assocs.get(word1, {}):
                    connected_pairs += 1
        
        return connected_pairs / total_pairs if total_pairs > 0 else 0.0
    
    def _extract_properties_universal(self, words: List[str], contexts: List[str] = None) -> Dict[str, Set[str]]:
        """Extrae propiedades usando patrones aprendidos sin idioma específico."""
        properties = defaultdict(set)
        
        # Obtener todos los textos relevantes
        all_texts = []
        
        # Textos de memoria a corto plazo
        for entry in self.brain.memory.short_term:
            if isinstance(entry, dict) and entry.get("data"):
                all_texts.append(entry["data"])
        
        # Contextos específicos del cluster
        if contexts:
            all_texts.extend(contexts)
        
        # Buscar propiedades para cada palabra del cluster
        for word in words:
            for text in all_texts:
                if self._word_appears_in_text(word, text):
                    self._extract_properties_from_context(text, word, properties)
        
        # Extracción basada en asociaciones aprendidas
        self._extract_properties_from_associations(words, properties)
        
        # Inferencia basada en patrones universales aprendidos
        self._infer_properties_from_patterns(words, properties)
        
        return {k: list(v) for k, v in properties.items()}
    
    def _word_appears_in_text(self, word: str, text: str) -> bool:
        """Determina si una palabra aparece en el texto (insensible a mayúsculas)."""
        return word.lower() in text.lower()
    
    def _extract_properties_from_context(self, text: str, target_word: str, properties: Dict[str, Set[str]]):
        """Extrae propiedades basándose en el contexto inmediato de la palabra."""
        words_in_text = text.split()
        target_positions = []
        
        # Encontrar todas las posiciones donde aparece la palabra objetivo
        for i, word in enumerate(words_in_text):
            if target_word.lower() in word.lower():
                target_positions.append(i)
        
        # Para cada aparición, analizar el contexto circundante
        for pos in target_positions:
            context_window = 3  # Ventana de contexto (palabras antes y después)
            start = max(0, pos - context_window)
            end = min(len(words_in_text), pos + context_window + 1)
            
            context_words = words_in_text[start:end]
            self._analyze_context_window(context_words, target_word, properties)
    
    def _analyze_context_window(self, context_words: List[str], target_word: str, properties: Dict[str, Set[str]]):
        """Analiza una ventana de contexto para extraer propiedades."""
        context_text = " ".join(context_words).lower()
        
        # Buscar indicadores de propiedades aprendidos
        for category, indicators in self.learned_patterns['property_indicators'].items():
            for indicator in indicators:
                if indicator in context_text:
                    # Determinar la propiedad específica del contexto
                    property_value = self._extract_property_value(context_words, indicator, target_word)
                    if property_value:
                        properties[category].add(property_value)
        
        # Detectar patrones de descripción universales
        self._detect_universal_description_patterns(context_words, target_word, properties)
    
    def _extract_property_value(self, context_words: List[str], indicator: str, target_word: str) -> Optional[str]:
        """Extrae el valor específico de una propiedad del contexto."""
        # Encontrar palabras cercanas al indicador que podrían ser valores
        context_text = " ".join(context_words).lower()
        
        if indicator in context_text:
            # Buscar palabras adyacentes al indicador
            words = context_text.split()
            try:
                indicator_pos = words.index(indicator)
                
                # Buscar en posiciones adyacentes
                for offset in [-1, 1, -2, 2]:
                    pos = indicator_pos + offset
                    if 0 <= pos < len(words):
                        candidate = words[pos]
                        if candidate != target_word.lower() and len(candidate) > 2:
                            return candidate
            except ValueError:
                pass
        
        return None
    
    def _detect_universal_description_patterns(self, context_words: List[str], target_word: str, properties: Dict[str, Set[str]]):
        """Detecta patrones universales de descripción en cualquier idioma."""
        context_text = " ".join(context_words).lower()
        target_lower = target_word.lower()
        
        # Patrón: [target] [es/is/está] [propiedad]
        # Buscar palabras que podrían ser conectores universales
        potential_connectors = self._find_potential_connectors(context_words, target_word)
        
        for connector_pos in potential_connectors:
            # Buscar propiedades después del conector
            if connector_pos + 1 < len(context_words):
                property_candidate = context_words[connector_pos + 1].lower()
                if len(property_candidate) > 2:
                    properties['descriptive'].add(property_candidate)
    
    def _find_potential_connectors(self, context_words: List[str], target_word: str) -> List[int]:
        """Encuentra posiciones de posibles palabras conectoras (es, is, está, etc.)."""
        connectors = []
        target_lower = target_word.lower()
        
        for i, word in enumerate(context_words):
            word_lower = word.lower()
            
            # Buscar palabras cortas que podrían ser conectores
            if (len(word_lower) <= 4 and 
                word_lower != target_lower and
                i > 0 and context_words[i-1].lower() == target_lower):
                connectors.append(i)
        
        return connectors
    
    def _extract_properties_from_associations(self, words: List[str], properties: Dict[str, Set[str]]):
        """Extrae propiedades basadas en asociaciones fuertes aprendidas."""
        strong_assocs = self.brain.learning_system.get_strong_associations()
        
        for word in words:
            if word in strong_assocs:
                for associated_word, strength in strong_assocs[word].items():
                    if strength > 0.7:  # Asociación muy fuerte
                        # Categorizar la asociación basándose en patrones aprendidos
                        category = self._categorize_association(word, associated_word)
                        if category:
                            properties[category].add(associated_word)
    
    def _categorize_association(self, word1: str, word2: str) -> Optional[str]:
        """Categoriza una asociación basándose en patrones aprendidos."""
        # Buscar en categorías aprendidas
        for category, markers in self.learned_patterns['category_markers'].items():
            if word2 in markers:
                return category
        
        # Si no hay categoría específica, usar asociación genérica
        return 'associated'
    
    def _infer_properties_from_patterns(self, words: List[str], properties: Dict[str, Set[str]]):
        """Infiere propiedades basándose en patrones universales aprendidos."""
        # Analizar la estructura de las palabras (morfología básica)
        for word in words:
            morphological_features = self._analyze_word_morphology(word)
            for feature, value in morphological_features.items():
                if value:
                    properties[f'morphology_{feature}'].add(value)
    
    def _analyze_word_morphology(self, word: str) -> Dict[str, Optional[str]]:
        """Analiza características morfológicas básicas de una palabra."""
        features = {}
        
        # Longitud de palabra
        if len(word) <= 3:
            features['length'] = 'short'
        elif len(word) >= 8:
            features['length'] = 'long'
        else:
            features['length'] = 'medium'
        
        # Patrones de repetición
        if len(set(word)) < len(word) * 0.6:  # Muchas letras repetidas
            features['repetition'] = 'high'
        
        # Estructura básica (vocales/consonantes)
        vowels = sum(1 for char in word.lower() if char in 'aeiouáéíóúàèìòùäëïöü')
        consonants = len(word) - vowels
        
        if vowels > consonants:
            features['phonetic_structure'] = 'vowel_heavy'
        elif consonants > vowels * 2:
            features['phonetic_structure'] = 'consonant_heavy'
        else:
            features['phonetic_structure'] = 'balanced'
        
        return features
    
    def _generate_concept_name(self, words: List[str], properties: Dict[str, List[str]]) -> str:
        """Genera un nombre inteligente para el concepto basado en patrones aprendidos."""
        # 1. Buscar en categorías aprendidas
        for category_name, category_words in self.learned_patterns['category_markers'].items():
            if any(word in category_words for word in words):
                return category_name.title()
        
        # 2. Usar la palabra más central del cluster
        strong_assocs = self.brain.learning_system.get_strong_associations()
        word_scores = {}
        
        for word in words:
            score = 0
            # Puntuación por frecuencia de asociaciones
            if word in strong_assocs:
                score += len(strong_assocs[word])
            
            # Puntuación por centralidad en el cluster
            connections = 0
            for other_word in words:
                if other_word != word and word in strong_assocs:
                    if other_word in strong_assocs[word]:
                        connections += 1
            score += connections * 2
            
            word_scores[word] = score
        
        if word_scores:
            best_word = max(word_scores.keys(), key=lambda x: word_scores[x])
            return best_word.title()
        
        # 3. Nombre por defecto usando el primer elemento
        if words:
            return f"{words[0].title()}_Concept"
        
        return f"Concept_{len(self.concepts) + 1}"
    
    def build_concept_from_cluster(self, cluster_data: Dict) -> Dict:
        """Construye un concepto a partir de datos de cluster mejorados."""
        words = cluster_data["words"]
        contexts = cluster_data.get("contexts", [])
        
        # Extraer propiedades usando métodos universales
        properties = self._extract_properties_universal(words, contexts)
        
        # Generar nombre basado en patrones aprendidos
        concept_name = self._generate_concept_name(words, properties)
        
        # Calcular métricas de calidad
        quality_metrics = {
            "cohesion": cluster_data["cohesion"],
            "frequency": cluster_data["frequency"],
            "property_richness": sum(len(props) for props in properties.values()),
            "semantic_diversity": len(set(words)),
            "context_coverage": len(contexts)
        }
        
        # Crear concepto
        concept = {
            "name": concept_name,
            "members": words,
            "properties": properties,
            "quality_metrics": quality_metrics,
            "creation_time": datetime.datetime.now().isoformat(),
            "accesses": 1,
            "last_activation": datetime.datetime.now().isoformat(),
            "activation_strength": 1.0,
            "relationships": {},  # Para conexiones con otros conceptos
            "learned_contexts": contexts[:10]  # Guardar contextos más relevantes
        }
        
        return concept
    
    def learn_language_patterns(self, text: str, context_info: Dict = None):
        """Aprende patrones específicos del idioma a partir del texto de entrada."""
        words = text.split()
        
        # Aprender indicadores de propiedades
        self._learn_property_indicators(words, context_info)
        
        # Aprender marcadores de categorías
        self._learn_category_markers(words, context_info)
        
        # Aprender palabras de relación
        self._learn_relationship_words(words, context_info)
        
        # Aprender negaciones
        self._learn_negation_patterns(words, context_info)
        
        # Aprender modificadores de intensidad
        self._learn_intensity_modifiers(words, context_info)
    
    def _learn_property_indicators(self, words: List[str], context_info: Dict):
        """Aprende palabras que típicamente indican propiedades."""
        # Buscar patrones como "X es Y" donde Y podría ser una propiedad
        for i in range(len(words) - 2):
            word1, connector, word2 = words[i], words[i+1], words[i+2]
            
            # Si el conector es corto (posible "es", "is", etc.)
            if len(connector) <= 4:
                # Registrar el conector como posible indicador
                if 'descriptive' not in self.learned_patterns['property_indicators']:
                    self.learned_patterns['property_indicators']['descriptive'] = set()
                
                self.learned_patterns['property_indicators']['descriptive'].add(connector.lower())
    
    def _learn_category_markers(self, words: List[str], context_info: Dict):
        """Aprende palabras que marcan categorías específicas."""
        if context_info and 'category' in context_info:
            category = context_info['category']
            
            if category not in self.learned_patterns['category_markers']:
                self.learned_patterns['category_markers'][category] = set()
            
            # Agregar palabras del contexto a esta categoría
            for word in words:
                if len(word) > 2:  # Filtrar palabras muy cortas
                    self.learned_patterns['category_markers'][category].add(word.lower())
    
    def _learn_relationship_words(self, words: List[str], context_info: Dict):
        """Aprende palabras que indican relaciones entre conceptos."""
        # Buscar preposiciones y conectores
        potential_connectors = []
        for word in words:
            if len(word) <= 5 and word.lower() not in ['the', 'a', 'an']:  # Evitar artículos comunes en inglés
                potential_connectors.append(word.lower())
        
        for connector in potential_connectors:
            if connector not in self.learned_patterns['relationship_words']:
                self.learned_patterns['relationship_words'][connector] = 0
            self.learned_patterns['relationship_words'][connector] += 1
    
    def _learn_negation_patterns(self, words: List[str], context_info: Dict):
        """Aprende patrones de negación del idioma."""
        # Buscar palabras que aparezcan frecuentemente en contextos negativos
        if context_info and context_info.get('sentiment') == 'negative':
            for word in words:
                if len(word) <= 6:  # Las negaciones suelen ser cortas
                    self.learned_patterns['negation_words'].add(word.lower())
    
    def _learn_intensity_modifiers(self, words: List[str], context_info: Dict):
        """Aprende modificadores de intensidad (muy, mucho, poco, etc.)."""
        # Buscar adverbios que modifiquen adjetivos
        for i in range(len(words) - 1):
            word1, word2 = words[i], words[i+1]
            
            # Si la primera palabra es corta, podría ser un modificador
            if len(word1) <= 6:
                intensity_level = self._guess_intensity_level(word1, context_info)
                if intensity_level:
                    if intensity_level not in self.learned_patterns['intensity_modifiers']:
                        self.learned_patterns['intensity_modifiers'][intensity_level] = set()
                    self.learned_patterns['intensity_modifiers'][intensity_level].add(word1.lower())
    
    def _guess_intensity_level(self, word: str, context_info: Dict) -> Optional[str]:
        """Intenta adivinar el nivel de intensidad de una palabra."""
        # Usar información contextual si está disponible
        if context_info and 'intensity' in context_info:
            return context_info['intensity']
        
        # Análisis básico por longitud y estructura
        if len(word) <= 3:
            return 'high'  # Palabras muy cortas suelen ser intensificadores
        elif len(word) <= 5:
            return 'medium'
        
        return None
    
    def _establish_concept_relationships(self, new_concept: Dict):
        """Establece relaciones entre el nuevo concepto y los existentes."""
        concept_name = new_concept["name"]
        
        for existing_name, existing_concept in self.concepts.items():
            if existing_name == concept_name:
                continue
                
            # Calcular similitud
            similarity = self._calculate_concept_similarity(new_concept, existing_concept)
            
            if similarity > 0.3:  # Umbral de relación
                relationship_type = self._determine_relationship_type(
                    new_concept, existing_concept, similarity
                )
                
                # Establecer relación bidireccional
                new_concept["relationships"][existing_name] = {
                    "type": relationship_type,
                    "strength": similarity
                }
                existing_concept["relationships"][concept_name] = {
                    "type": relationship_type,
                    "strength": similarity
                }
    
    def _calculate_concept_similarity(self, concept1: Dict, concept2: Dict) -> float:
        """Calcula similitud entre dos conceptos."""
        # Similitud por miembros compartidos
        members1 = set(concept1["members"])
        members2 = set(concept2["members"])
        member_overlap = len(members1.intersection(members2))
        member_union = len(members1.union(members2))
        member_similarity = member_overlap / member_union if member_union > 0 else 0
        
        # Similitud por propiedades compartidas
        props1 = set()
        props2 = set()
        
        for prop_list in concept1["properties"].values():
            props1.update(prop_list)
        for prop_list in concept2["properties"].values():
            props2.update(prop_list)
        
        prop_overlap = len(props1.intersection(props2))
        prop_union = len(props1.union(props2))
        prop_similarity = prop_overlap / prop_union if prop_union > 0 else 0
        
        # Promedio ponderado
        return 0.6 * member_similarity + 0.4 * prop_similarity
    
    def _determine_relationship_type(self, concept1: Dict, concept2: Dict, similarity: float) -> str:
        """Determina el tipo de relación entre conceptos."""
        if similarity > 0.8:
            return "similar"
        elif similarity > 0.6:
            return "related"
        elif any(member in concept2["members"] for member in concept1["members"]):
            return "overlapping"
        else:
            return "associated"
    
    def run_cycle(self) -> List[Dict]:
        """Ciclo mejorado de construcción de conceptos."""
        clusters = self.detect_candidate_clusters()
        new_concepts = []
        
        for cluster_data in clusters:
            # Filtrar clusters de baja calidad
            if cluster_data["cohesion"] < 0.3:
                continue
                
            cluster_words = cluster_data["words"]
            
            # Verificar si ya existe un concepto similar
            if not self._concept_exists(cluster_words):
                concept = self.build_concept_from_cluster(cluster_data)
                
                # Establecer relaciones con conceptos existentes
                self._establish_concept_relationships(concept)
                
                # Almacenar concepto
                self.concepts[concept["name"]] = concept
                new_concepts.append(concept)
                
                # Almacenar en memoria como conocimiento consolidado
                self.brain.memory.store(
                    data=f"Concept: {concept['name']} = {concept['members']} | Properties: {concept['properties']}",
                    importance=4,  # Mayor importancia para conceptos
                    context={
                        "type": "concept",
                        "name": concept["name"],
                        "quality": concept["quality_metrics"]
                    }
                )
        
        return new_concepts
    
    def _concept_exists(self, members: List[str]) -> bool:
        """Verifica si ya existe un concepto con miembros similares."""
        members_set = set(members)
        
        for concept in self.concepts.values():
            existing_members = set(concept["members"])
            
            # Si hay más del 70% de solapamiento, considerarlo existente
            overlap = len(members_set.intersection(existing_members))
            union = len(members_set.union(existing_members))
            
            if overlap / union > 0.7:
                return True
        
        return False
    
    def activate_concept(self, concept_name: str, activation_strength: float = 1.0):
        """Activa un concepto y actualiza sus métricas."""
        if concept_name in self.concepts:
            concept = self.concepts[concept_name]
            concept["accesses"] += 1
            concept["last_activation"] = datetime.datetime.now().isoformat()
            concept["activation_strength"] = min(concept["activation_strength"] + activation_strength, 5.0)
            
            # Activar conceptos relacionados (propagación)
            for related_name, relationship in concept["relationships"].items():
                if related_name in self.concepts:
                    propagation_strength = activation_strength * relationship["strength"] * 0.5
                    if propagation_strength > 0.1:
                        self.activate_concept(related_name, propagation_strength)
    
    def get_active_concepts(self, threshold: float = 0.5) -> List[Dict]:
        """Obtiene conceptos actualmente activados."""
        active = []
        for concept in self.concepts.values():
            if concept["activation_strength"] >= threshold:
                active.append(concept)
        
        # Ordenar por fuerza de activación
        return sorted(active, key=lambda x: x["activation_strength"], reverse=True)
    
    def decay_activations(self, decay_rate: float = 0.1):
        """Aplica decaimiento a las activaciones de conceptos."""
        for concept in self.concepts.values():
            concept["activation_strength"] = max(
                concept["activation_strength"] - decay_rate, 
                0.0
            )
    
    def get_concept_network(self) -> Dict:
        """Retorna la red de conceptos para visualización o análisis."""
        network = {
            "nodes": [],
            "edges": []
        }
        
        # Nodos
        for name, concept in self.concepts.items():
            network["nodes"].append({
                "id": name,
                "label": name,
                "size": concept["activation_strength"],
                "properties": concept["properties"],
                "members": concept["members"]
            })
        
        # Aristas
        for name, concept in self.concepts.items():
            for related_name, relationship in concept["relationships"].items():
                network["edges"].append({
                    "source": name,
                    "target": related_name,
                    "weight": relationship["strength"],
                    "type": relationship["type"]
                })
        
        return network
    
    def get_learned_patterns(self) -> Dict:
        """Retorna los patrones aprendidos para inspección o persistencia."""
        return {
            "property_indicators": {k: list(v) if isinstance(v, set) else v 
                                   for k, v in self.learned_patterns['property_indicators'].items()},
            "category_markers": {k: list(v) if isinstance(v, set) else v 
                                for k, v in self.learned_patterns['category_markers'].items()},
            "relationship_words": dict(self.learned_patterns['relationship_words']),
            "negation_words": list(self.learned_patterns['negation_words']),
            "intensity_modifiers": {k: list(v) if isinstance(v, set) else v 
                                   for k, v in self.learned_patterns['intensity_modifiers'].items()}
        }
    
    def load_learned_patterns(self, patterns: Dict):
        """Carga patrones previamente aprendidos."""
        if 'property_indicators' in patterns:
            self.learned_patterns['property_indicators'] = {
                k: set(v) if isinstance(v, list) else v 
                for k, v in patterns['property_indicators'].items()
            }
        if 'category_markers' in patterns:
            self.learned_patterns['category_markers'] = {
                k: set(v) if isinstance(v, list) else v 
                for k, v in patterns['category_markers'].items()
            }
        if 'relationship_words' in patterns:
            self.learned_patterns['relationship_words'] = patterns['relationship_words']
        if 'negation_words' in patterns:
            self.learned_patterns['negation_words'] = set(patterns['negation_words'])
        if 'intensity_modifiers' in patterns:
            self.learned_patterns['intensity_modifiers'] = {
                k: set(v) if isinstance(v, list) else v 
                for k, v in patterns['intensity_modifiers'].items()
            }