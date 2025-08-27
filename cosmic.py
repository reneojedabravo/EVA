#cosmic.py
import random
import math
import time
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

class BosonType(Enum):
    PHOTON = "photon"
    W_BOSON = "w_boson"
    Z_BOSON = "z_boson"
    GLUON = "gluon"

class NodeState(Enum):
    STABLE = "stable"
    EXCITED = "excited"
    DEGRADED = "degraded"
    PRUNING = "pruning"
    TRANSMUTING = "transmuting"

class ElementCategory(Enum):
    ALKALI_METAL = "alkali_metal"
    ALKALINE_EARTH = "alkaline_earth"
    TRANSITION_METAL = "transition_metal"
    POST_TRANSITION = "post_transition"
    METALLOID = "metalloid"
    NONMETAL = "nonmetal"
    HALOGEN = "halogen"
    NOBLE_GAS = "noble_gas"
    LANTHANIDE = "lanthanide"
    ACTINIDE = "actinide"

@dataclass
class Element:
    """Representa un elemento de la tabla periódica"""
    atomic_number: int
    symbol: str
    name: str
    atomic_mass: float
    category: ElementCategory
    period: int
    group: int
    electronegativity: float
    ionization_energy: float
    electron_affinity: float
    metallic_radius: float
    stability_factor: float = 1.0
    
    def __post_init__(self):
        # Calcular factor de estabilidad basado en propiedades reales
        mass_stability = 1.0 - abs(self.atomic_mass - (self.atomic_number * 2)) / (self.atomic_number * 2)
        energy_stability = self.ionization_energy / 2500.0  # Normalizado
        
        # Gases nobles son más estables
        if self.category == ElementCategory.NOBLE_GAS:
            self.stability_factor = min(2.0, mass_stability + energy_stability + 0.5)
        else:
            self.stability_factor = max(0.1, mass_stability + energy_stability)

# Tabla periódica completa con los 118 elementos
PERIODIC_TABLE = {
    1: Element(1, "H", "Hidrógeno", 1.008, ElementCategory.NONMETAL, 1, 1, 2.20, 1312.0, 72.8, 25, 0.8),
    2: Element(2, "He", "Helio", 4.003, ElementCategory.NOBLE_GAS, 1, 18, 0.0, 2372.3, 0.0, 28, 2.0),
    3: Element(3, "Li", "Litio", 6.94, ElementCategory.ALKALI_METAL, 2, 1, 0.98, 520.2, 59.6, 145, 0.7),
    4: Element(4, "Be", "Berilio", 9.012, ElementCategory.ALKALINE_EARTH, 2, 2, 1.57, 899.5, 0.0, 105, 0.9),
    5: Element(5, "B", "Boro", 10.81, ElementCategory.METALLOID, 2, 13, 2.04, 800.6, 26.7, 85, 1.1),
    6: Element(6, "C", "Carbono", 12.011, ElementCategory.NONMETAL, 2, 14, 2.55, 1086.5, 153.9, 70, 1.5),
    7: Element(7, "N", "Nitrógeno", 14.007, ElementCategory.NONMETAL, 2, 15, 3.04, 1402.3, 7.0, 65, 1.3),
    8: Element(8, "O", "Oxígeno", 15.999, ElementCategory.NONMETAL, 2, 16, 3.44, 1313.9, 141.0, 60, 1.4),
    9: Element(9, "F", "Flúor", 18.998, ElementCategory.HALOGEN, 2, 17, 3.98, 1681.0, 328.0, 50, 1.2),
    10: Element(10, "Ne", "Neón", 20.180, ElementCategory.NOBLE_GAS, 2, 18, 0.0, 2080.7, 0.0, 38, 2.0),
    11: Element(11, "Na", "Sodio", 22.990, ElementCategory.ALKALI_METAL, 3, 1, 0.93, 495.8, 52.8, 180, 0.6),
    12: Element(12, "Mg", "Magnesio", 24.305, ElementCategory.ALKALINE_EARTH, 3, 2, 1.31, 737.7, 0.0, 150, 0.8),
    13: Element(13, "Al", "Aluminio", 26.982, ElementCategory.POST_TRANSITION, 3, 13, 1.61, 577.5, 42.5, 125, 1.0),
    14: Element(14, "Si", "Silicio", 28.085, ElementCategory.METALLOID, 3, 14, 1.90, 786.5, 133.6, 110, 1.2),
    15: Element(15, "P", "Fósforo", 30.974, ElementCategory.NONMETAL, 3, 15, 2.19, 1011.8, 72.0, 100, 1.1),
    16: Element(16, "S", "Azufre", 32.06, ElementCategory.NONMETAL, 3, 16, 2.58, 999.6, 200.4, 100, 1.0),
    17: Element(17, "Cl", "Cloro", 35.45, ElementCategory.HALOGEN, 3, 17, 3.16, 1251.2, 349.0, 100, 1.1),
    18: Element(18, "Ar", "Argón", 39.948, ElementCategory.NOBLE_GAS, 3, 18, 0.0, 1520.6, 0.0, 71, 2.0),
    19: Element(19, "K", "Potasio", 39.098, ElementCategory.ALKALI_METAL, 4, 1, 0.82, 418.8, 48.4, 220, 0.5),
    20: Element(20, "Ca", "Calcio", 40.078, ElementCategory.ALKALINE_EARTH, 4, 2, 1.00, 589.8, 2.37, 180, 0.7),
    # Metales de transición del período 4
    21: Element(21, "Sc", "Escandio", 44.956, ElementCategory.TRANSITION_METAL, 4, 3, 1.36, 633.1, 18.1, 160, 1.0),
    22: Element(22, "Ti", "Titanio", 47.867, ElementCategory.TRANSITION_METAL, 4, 4, 1.54, 658.8, 7.6, 140, 1.3),
    23: Element(23, "V", "Vanadio", 50.942, ElementCategory.TRANSITION_METAL, 4, 5, 1.63, 650.9, 50.6, 135, 1.2),
    24: Element(24, "Cr", "Cromo", 51.996, ElementCategory.TRANSITION_METAL, 4, 6, 1.66, 652.9, 64.3, 140, 1.4),
    25: Element(25, "Mn", "Manganeso", 54.938, ElementCategory.TRANSITION_METAL, 4, 7, 1.55, 717.3, 0.0, 140, 1.1),
    26: Element(26, "Fe", "Hierro", 55.845, ElementCategory.TRANSITION_METAL, 4, 8, 1.83, 762.5, 15.7, 140, 1.5),
    27: Element(27, "Co", "Cobalto", 58.933, ElementCategory.TRANSITION_METAL, 4, 9, 1.88, 760.4, 63.7, 135, 1.3),
    28: Element(28, "Ni", "Níquel", 58.693, ElementCategory.TRANSITION_METAL, 4, 10, 1.91, 737.1, 112.0, 135, 1.4),
    29: Element(29, "Cu", "Cobre", 63.546, ElementCategory.TRANSITION_METAL, 4, 11, 1.90, 745.5, 118.4, 135, 1.2),
    30: Element(30, "Zn", "Zinc", 65.38, ElementCategory.TRANSITION_METAL, 4, 12, 1.65, 906.4, 0.0, 135, 1.0),
    31: Element(31, "Ga", "Galio", 69.723, ElementCategory.POST_TRANSITION, 4, 13, 1.81, 578.8, 28.9, 130, 0.9),
    32: Element(32, "Ge", "Germanio", 72.630, ElementCategory.METALLOID, 4, 14, 2.01, 762.2, 119.0, 125, 1.1),
    33: Element(33, "As", "Arsénico", 74.922, ElementCategory.METALLOID, 4, 15, 2.18, 947.0, 78.0, 115, 1.0),
    34: Element(34, "Se", "Selenio", 78.971, ElementCategory.NONMETAL, 4, 16, 2.55, 941.0, 195.0, 115, 0.9),
    35: Element(35, "Br", "Bromo", 79.904, ElementCategory.HALOGEN, 4, 17, 2.96, 1139.9, 324.6, 115, 1.0),
    36: Element(36, "Kr", "Kriptón", 83.798, ElementCategory.NOBLE_GAS, 4, 18, 3.00, 1350.8, 0.0, 88, 1.8),
    # Período 5
    37: Element(37, "Rb", "Rubidio", 85.468, ElementCategory.ALKALI_METAL, 5, 1, 0.82, 403.0, 46.9, 235, 0.4),
    38: Element(38, "Sr", "Estroncio", 87.62, ElementCategory.ALKALINE_EARTH, 5, 2, 0.95, 549.5, 5.03, 200, 0.6),
    39: Element(39, "Y", "Itrio", 88.906, ElementCategory.TRANSITION_METAL, 5, 3, 1.22, 600.0, 29.6, 180, 1.0),
    40: Element(40, "Zr", "Circonio", 91.224, ElementCategory.TRANSITION_METAL, 5, 4, 1.33, 640.1, 41.1, 155, 1.3),
    41: Element(41, "Nb", "Niobio", 92.906, ElementCategory.TRANSITION_METAL, 5, 5, 1.6, 652.1, 86.1, 145, 1.2),
    42: Element(42, "Mo", "Molibdeno", 95.95, ElementCategory.TRANSITION_METAL, 5, 6, 2.16, 684.3, 71.9, 145, 1.4),
    43: Element(43, "Tc", "Tecnecio", 98.0, ElementCategory.TRANSITION_METAL, 5, 7, 1.9, 702.0, 53.0, 135, 0.8),
    44: Element(44, "Ru", "Rutenio", 101.07, ElementCategory.TRANSITION_METAL, 5, 8, 2.2, 710.2, 101.3, 130, 1.3),
    45: Element(45, "Rh", "Rodio", 102.91, ElementCategory.TRANSITION_METAL, 5, 9, 2.28, 719.7, 109.7, 135, 1.2),
    46: Element(46, "Pd", "Paladio", 106.42, ElementCategory.TRANSITION_METAL, 5, 10, 2.20, 804.4, 53.7, 140, 1.1),
    47: Element(47, "Ag", "Plata", 107.87, ElementCategory.TRANSITION_METAL, 5, 11, 1.93, 731.0, 125.6, 160, 1.0),
    48: Element(48, "Cd", "Cadmio", 112.41, ElementCategory.TRANSITION_METAL, 5, 12, 1.69, 867.8, 0.0, 155, 0.9),
    49: Element(49, "In", "Indio", 114.82, ElementCategory.POST_TRANSITION, 5, 13, 1.78, 558.3, 28.9, 155, 0.8),
    50: Element(50, "Sn", "Estaño", 118.71, ElementCategory.POST_TRANSITION, 5, 14, 1.96, 708.6, 107.3, 145, 1.0),
    51: Element(51, "Sb", "Antimonio", 121.76, ElementCategory.METALLOID, 5, 15, 2.05, 830.6, 103.2, 145, 0.9),
    52: Element(52, "Te", "Telurio", 127.60, ElementCategory.METALLOID, 5, 16, 2.1, 869.3, 190.2, 140, 0.8),
    53: Element(53, "I", "Yodo", 126.90, ElementCategory.HALOGEN, 5, 17, 2.66, 1008.4, 295.2, 140, 0.9),
    54: Element(54, "Xe", "Xenón", 131.29, ElementCategory.NOBLE_GAS, 5, 18, 2.60, 1170.4, 0.0, 108, 1.6),
    # Período 6
    55: Element(55, "Cs", "Cesio", 132.91, ElementCategory.ALKALI_METAL, 6, 1, 0.79, 375.7, 45.5, 260, 0.3),
    56: Element(56, "Ba", "Bario", 137.33, ElementCategory.ALKALINE_EARTH, 6, 2, 0.89, 502.9, 13.95, 215, 0.5),
    # Lantánidos
    57: Element(57, "La", "Lantano", 138.91, ElementCategory.LANTHANIDE, 6, 3, 1.10, 538.1, 53.0, 195, 1.0),
    58: Element(58, "Ce", "Cerio", 140.12, ElementCategory.LANTHANIDE, 6, 3, 1.12, 534.4, 50.0, 185, 1.0),
    59: Element(59, "Pr", "Praseodimio", 140.91, ElementCategory.LANTHANIDE, 6, 3, 1.13, 527.0, 50.0, 185, 1.0),
    60: Element(60, "Nd", "Neodimio", 144.24, ElementCategory.LANTHANIDE, 6, 3, 1.14, 533.1, 50.0, 185, 1.0),
    61: Element(61, "Pm", "Prometio", 145.0, ElementCategory.LANTHANIDE, 6, 3, 1.13, 540.0, 50.0, 185, 0.7),
    62: Element(62, "Sm", "Samario", 150.36, ElementCategory.LANTHANIDE, 6, 3, 1.17, 544.5, 50.0, 185, 1.0),
    63: Element(63, "Eu", "Europio", 151.96, ElementCategory.LANTHANIDE, 6, 3, 1.20, 547.1, 50.0, 185, 0.9),
    64: Element(64, "Gd", "Gadolinio", 157.25, ElementCategory.LANTHANIDE, 6, 3, 1.20, 593.4, 50.0, 180, 1.1),
    65: Element(65, "Tb", "Terbio", 158.93, ElementCategory.LANTHANIDE, 6, 3, 1.10, 565.8, 50.0, 175, 1.0),
    66: Element(66, "Dy", "Disprosio", 162.50, ElementCategory.LANTHANIDE, 6, 3, 1.22, 573.0, 50.0, 175, 1.0),
    67: Element(67, "Ho", "Holmio", 164.93, ElementCategory.LANTHANIDE, 6, 3, 1.23, 581.0, 50.0, 175, 1.0),
    68: Element(68, "Er", "Erbio", 167.26, ElementCategory.LANTHANIDE, 6, 3, 1.24, 589.3, 50.0, 175, 1.0),
    69: Element(69, "Tm", "Tulio", 168.93, ElementCategory.LANTHANIDE, 6, 3, 1.25, 596.7, 50.0, 175, 1.0),
    70: Element(70, "Yb", "Iterbio", 173.05, ElementCategory.LANTHANIDE, 6, 3, 1.10, 603.4, 50.0, 175, 0.9),
    71: Element(71, "Lu", "Lutecio", 174.97, ElementCategory.LANTHANIDE, 6, 3, 1.27, 523.5, 33.4, 175, 1.0),
    # Continuación período 6
    72: Element(72, "Hf", "Hafnio", 178.49, ElementCategory.TRANSITION_METAL, 6, 4, 1.3, 658.5, 0.0, 155, 1.3),
    73: Element(73, "Ta", "Tantalio", 180.95, ElementCategory.TRANSITION_METAL, 6, 5, 1.5, 761.0, 31.0, 145, 1.4),
    74: Element(74, "W", "Wolframio", 183.84, ElementCategory.TRANSITION_METAL, 6, 6, 2.36, 770.0, 78.6, 135, 1.5),
    75: Element(75, "Re", "Renio", 186.21, ElementCategory.TRANSITION_METAL, 6, 7, 1.9, 760.0, 14.5, 135, 1.3),
    76: Element(76, "Os", "Osmio", 190.23, ElementCategory.TRANSITION_METAL, 6, 8, 2.2, 840.0, 106.1, 130, 1.4),
    77: Element(77, "Ir", "Iridio", 192.22, ElementCategory.TRANSITION_METAL, 6, 9, 2.20, 880.0, 151.0, 135, 1.5),
    78: Element(78, "Pt", "Platino", 195.08, ElementCategory.TRANSITION_METAL, 6, 10, 2.28, 870.0, 205.3, 135, 1.3),
    79: Element(79, "Au", "Oro", 196.97, ElementCategory.TRANSITION_METAL, 6, 11, 2.54, 890.1, 222.8, 135, 1.2),
    80: Element(80, "Hg", "Mercurio", 200.59, ElementCategory.TRANSITION_METAL, 6, 12, 2.00, 1007.1, 0.0, 150, 0.8),
    81: Element(81, "Tl", "Talio", 204.38, ElementCategory.POST_TRANSITION, 6, 13, 1.62, 589.4, 19.2, 190, 0.7),
    82: Element(82, "Pb", "Plomo", 207.2, ElementCategory.POST_TRANSITION, 6, 14, 2.33, 715.6, 35.1, 180, 0.6),
    83: Element(83, "Bi", "Bismuto", 208.98, ElementCategory.POST_TRANSITION, 6, 15, 2.02, 703.0, 91.2, 160, 0.5),
    84: Element(84, "Po", "Polonio", 209.0, ElementCategory.POST_TRANSITION, 6, 16, 2.0, 812.1, 183.3, 190, 0.4),
    85: Element(85, "At", "Astato", 210.0, ElementCategory.HALOGEN, 6, 17, 2.2, 890.0, 270.1, 150, 0.3),
    86: Element(86, "Rn", "Radón", 222.0, ElementCategory.NOBLE_GAS, 6, 18, 2.2, 1037.0, 0.0, 120, 0.5),
    # Período 7
    87: Element(87, "Fr", "Francio", 223.0, ElementCategory.ALKALI_METAL, 7, 1, 0.7, 380.0, 46.9, 270, 0.2),
    88: Element(88, "Ra", "Radio", 226.0, ElementCategory.ALKALINE_EARTH, 7, 2, 0.9, 509.3, 9.6, 215, 0.3),
    # Actínidos
    89: Element(89, "Ac", "Actinio", 227.0, ElementCategory.ACTINIDE, 7, 3, 1.1, 499.0, 33.77, 195, 0.4),
    90: Element(90, "Th", "Torio", 232.04, ElementCategory.ACTINIDE, 7, 3, 1.3, 587.0, 112.72, 180, 0.6),
    91: Element(91, "Pa", "Protactinio", 231.04, ElementCategory.ACTINIDE, 7, 3, 1.5, 568.0, 53.0, 180, 0.3),
    92: Element(92, "U", "Uranio", 238.03, ElementCategory.ACTINIDE, 7, 3, 1.38, 597.6, 50.94, 175, 0.4),
    93: Element(93, "Np", "Neptunio", 237.0, ElementCategory.ACTINIDE, 7, 3, 1.36, 604.5, 45.85, 175, 0.2),
    94: Element(94, "Pu", "Plutonio", 244.0, ElementCategory.ACTINIDE, 7, 3, 1.28, 584.7, 48.4, 175, 0.1),
    95: Element(95, "Am", "Americio", 243.0, ElementCategory.ACTINIDE, 7, 3, 1.3, 578.0, 9.93, 175, 0.1),
    96: Element(96, "Cm", "Curio", 247.0, ElementCategory.ACTINIDE, 7, 3, 1.3, 581.0, 27.17, 176, 0.1),
    97: Element(97, "Bk", "Berkelio", 247.0, ElementCategory.ACTINIDE, 7, 3, 1.3, 601.0, 165.24, 176, 0.1),
    98: Element(98, "Cf", "Californio", 251.0, ElementCategory.ACTINIDE, 7, 3, 1.3, 608.0, 97.31, 176, 0.1),
    99: Element(99, "Es", "Einsteinio", 252.0, ElementCategory.ACTINIDE, 7, 3, 1.3, 619.0, 133.6, 176, 0.1),
    100: Element(100, "Fm", "Fermio", 257.0, ElementCategory.ACTINIDE, 7, 3, 1.3, 627.0, 33.96, 176, 0.1),
    101: Element(101, "Md", "Mendelevio", 258.0, ElementCategory.ACTINIDE, 7, 3, 1.3, 635.0, 93.91, 176, 0.1),
    102: Element(102, "No", "Nobelio", 259.0, ElementCategory.ACTINIDE, 7, 3, 1.3, 642.0, 223.22, 176, 0.1),
    103: Element(103, "Lr", "Lawrencio", 266.0, ElementCategory.ACTINIDE, 7, 3, 1.3, 470.0, 57.0, 176, 0.1),
    # Elementos superpesados
    104: Element(104, "Rf", "Rutherfordio", 267.0, ElementCategory.TRANSITION_METAL, 7, 4, 1.3, 580.0, 0.0, 150, 0.05),
    105: Element(105, "Db", "Dubnio", 270.0, ElementCategory.TRANSITION_METAL, 7, 5, 1.5, 665.0, 0.0, 139, 0.05),
    106: Element(106, "Sg", "Seaborgio", 271.0, ElementCategory.TRANSITION_METAL, 7, 6, 1.9, 757.0, 0.0, 132, 0.05),
    107: Element(107, "Bh", "Bohrio", 270.0, ElementCategory.TRANSITION_METAL, 7, 7, 2.2, 740.0, 0.0, 128, 0.05),
    108: Element(108, "Hs", "Hassio", 277.0, ElementCategory.TRANSITION_METAL, 7, 8, 2.3, 800.0, 0.0, 126, 0.05),
    109: Element(109, "Mt", "Meitnerio", 278.0, ElementCategory.TRANSITION_METAL, 7, 9, 2.4, 830.0, 0.0, 125, 0.05),
    110: Element(110, "Ds", "Darmstadtio", 281.0, ElementCategory.TRANSITION_METAL, 7, 10, 2.5, 850.0, 0.0, 124, 0.05),
    111: Element(111, "Rg", "Roentgenio", 282.0, ElementCategory.TRANSITION_METAL, 7, 11, 2.6, 870.0, 0.0, 121, 0.05),
    112: Element(112, "Cn", "Copernicio", 285.0, ElementCategory.TRANSITION_METAL, 7, 12, 2.6, 890.0, 0.0, 122, 0.05),
    113: Element(113, "Nh", "Nihonio", 286.0, ElementCategory.POST_TRANSITION, 7, 13, 2.1, 704.9, 66.6, 136, 0.05),
    114: Element(114, "Fl", "Flerovio", 289.0, ElementCategory.POST_TRANSITION, 7, 14, 2.0, 832.2, 106.0, 143, 0.05),
    115: Element(115, "Mc", "Moscovio", 290.0, ElementCategory.POST_TRANSITION, 7, 15, 1.9, 538.0, 35.3, 162, 0.05),
    116: Element(116, "Lv", "Livermorio", 293.0, ElementCategory.POST_TRANSITION, 7, 16, 1.8, 663.9, 74.9, 175, 0.05),
    117: Element(117, "Ts", "Tenesino", 294.0, ElementCategory.HALOGEN, 7, 17, 1.7, 742.9, 165.9, 165, 0.05),
    118: Element(118, "Og", "Oganesón", 294.0, ElementCategory.NOBLE_GAS, 7, 18, 1.6, 839.4, 5.40, 157, 0.1)
}

@dataclass
class Quark:
    """Representa un quark dentro del núcleo atómico"""
    type: str
    coherence: float = 1.0
    response_factor: float = 1.0
    color_charge: str = "red"  # red, green, blue
    
    def __post_init__(self):
        self.color_charge = random.choice(["red", "green", "blue"])
        
    def adjust_coherence(self, factor: float):
        self.coherence = max(0.1, min(2.0, self.coherence * factor))
        
    def adjust_response(self, factor: float):
        self.response_factor = max(0.1, min(2.0, self.response_factor * factor))

@dataclass
class Nucleus:
    """Núcleo atómico basado en elemento real de la tabla periódica"""
    element: Element
    quarks: List[Quark] = field(default_factory=list)
    gluon_strength: float = 1.0
    nuclear_binding_energy: float = 0.0
    
    def __post_init__(self):
        # Cada protón y neutrón tiene 3 quarks
        protons = self.element.atomic_number
        neutrons = int(self.element.atomic_mass - self.element.atomic_number)
        
        # Protones: 2 up quarks + 1 down quark cada uno
        for i in range(protons):
            self.quarks.extend([
                Quark("up"), Quark("up"), Quark("down")
            ])
        
        # Neutrones: 1 up quark + 2 down quarks cada uno  
        for i in range(neutrons):
            self.quarks.extend([
                Quark("up"), Quark("down"), Quark("down")
            ])
            
        # Energía de enlace nuclear basada en el elemento
        self.nuclear_binding_energy = self.calculate_binding_energy()
        self.gluon_strength = self.element.stability_factor
    
    def calculate_binding_energy(self) -> float:
        """Calcula la energía de enlace nuclear aproximada"""
        A = self.element.atomic_mass
        Z = self.element.atomic_number
        N = A - Z
        
        # Fórmula de Weizsäcker simplificada
        a_v = 15.75  # Término de volumen
        a_s = 17.8   # Término de superficie
        a_c = 0.711  # Término coulómbico
        a_a = 23.7   # Término de asimetría
        
        volume_term = a_v * A
        surface_term = -a_s * (A**(2/3))
        coulomb_term = -a_c * (Z**2) / (A**(1/3))
        asymmetry_term = -a_a * ((N - Z)**2) / A
        
        binding_energy = volume_term + surface_term + coulomb_term + asymmetry_term
        return max(0, binding_energy / 1000)  # Normalizado
    
    def get_stability(self) -> float:
        """Calcula estabilidad nuclear"""
        avg_coherence = sum(q.coherence for q in self.quarks) / len(self.quarks)
        stability = (avg_coherence * self.gluon_strength * 
                    self.nuclear_binding_energy * self.element.stability_factor)
        return min(2.0, stability)
    
    def reinforce_cohesion(self):
        """Refuerza la cohesión nuclear"""
        self.gluon_strength = min(2.0, self.gluon_strength * 1.05)
        for quark in self.quarks:
            quark.adjust_coherence(1.02)
    
    def can_transmute(self) -> bool:
        """Determina si el núcleo puede transmutarse a otro elemento"""
        if self.element.category == ElementCategory.ACTINIDE:
            return random.random() < 0.1  # Elementos radiactivos
        elif self.element.atomic_number > 103:
            return random.random() < 0.3  # Elementos superpesados
        else:
            return random.random() < 0.001  # Elementos estables

@dataclass
class ElectronShell:
    """Capa electrónica con configuración real"""
    shell_number: int
    subshells: Dict[str, int]  # s, p, d, f
    electrons: List['Electron'] = field(default_factory=list)
    
    def __post_init__(self):
        total_electrons = sum(self.subshells.values())
        for i in range(total_electrons):
            subshell_type = self.get_electron_subshell(i)
            self.electrons.append(Electron(self.shell_number, subshell_type))
    
    def get_electron_subshell(self, electron_index: int) -> str:
        """Determina en qué subcapa está el electrón"""
        count = 0
        for subshell, capacity in self.subshells.items():
            if count + capacity > electron_index:
                return subshell
            count += capacity
        return "s"

@dataclass
class Electron:
    """Electrón mejorado con propiedades cuánticas"""
    shell_level: int
    subshell: str = "s"
    spin: str = "up"
    information_capacity: float = 1.0
    flow_rate: float = 1.0
    quantum_state: str = "ground"
    
    def __post_init__(self):
        self.spin = random.choice(["up", "down"])
        # Capacidad de información basada en la capa y subcapa
        shell_factor = 1.0 / self.shell_level
        subshell_factor = {"s": 1.0, "p": 1.2, "d": 1.5, "f": 2.0}.get(self.subshell, 1.0)
        self.information_capacity = shell_factor * subshell_factor
        
    def excite(self):
        """Excita el electrón a un estado superior"""
        self.quantum_state = "excited"
        self.flow_rate *= 1.3
        
    def relax(self):
        """Relaja el electrón al estado fundamental"""
        self.quantum_state = "ground" 
        self.flow_rate *= 0.8
        
    def transfer_information(self, amount: float) -> float:
        """Transfiere información considerando el estado cuántico"""
        multiplier = 1.3 if self.quantum_state == "excited" else 1.0
        transferred = min(amount, self.information_capacity * self.flow_rate * multiplier)
        return transferred

@dataclass
class Molecule:
    """Molécula que actúa como 'idea' con química real"""
    formula: str
    bond_type: str  # ionic, covalent, metallic, van_der_waals
    strength: float = 1.0
    relevance: float = 1.0
    pattern_count: int = 0
    last_accessed: float = 0
    stability: float = 1.0
    
    def __post_init__(self):
        self.last_accessed = time.time()
        # Estabilidad basada en el tipo de enlace
        stability_map = {
            "ionic": 0.8,
            "covalent": 1.2, 
            "metallic": 1.0,
            "van_der_waals": 0.6,
            "hydrogen": 0.7
        }
        self.stability = stability_map.get(self.bond_type, 1.0)
        
    def reinforce(self):
        """Refuerza la idea-molécula"""
        self.strength = min(2.0, self.strength * (1.0 + 0.1 * self.stability))
        self.pattern_count += 1
        self.last_accessed = time.time()
        
    def decay(self):
        """Decaimiento natural de la molécula"""
        decay_rate = 0.99 if self.stability > 1.0 else 0.98
        self.strength *= decay_rate
        self.relevance *= (0.999 if self.stability > 1.0 else 0.995)
        
    def should_prune(self, current_time: float, threshold: float = 0.3) -> bool:
        """Determina si la molécula debe ser eliminada"""
        time_factor = 1.0 / (1.0 + (current_time - self.last_accessed) * 0.001)
        molecular_health = self.strength * self.relevance * self.stability * time_factor
        return molecular_health < threshold

class CosmicNode:
    """Nodo atómico basado en elemento real de la tabla periódica"""
    
    def __init__(self, node_id: str, atomic_number: int = None):
        self.id = node_id
        
        # Seleccionar elemento aleatorio o específico
        if atomic_number and atomic_number in PERIODIC_TABLE:
            self.element = PERIODIC_TABLE[atomic_number]
        else:
            # Probabilidad ponderada por estabilidad
            weights = [elem.stability_factor for elem in PERIODIC_TABLE.values()]
            self.element = random.choices(list(PERIODIC_TABLE.values()), weights=weights)[0]
        
        self.nucleus = Nucleus(self.element)
        self.electron_shells = self.create_electron_configuration()
        self.molecules: List[Molecule] = []
        self.state = NodeState.STABLE
        self.energy_level = 100.0 * self.element.stability_factor
        self.coherence = self.element.stability_factor
        self.connections: Dict[str, float] = {}
        
        # Bosones influenciados por propiedades del elemento
        self.bosons: Dict[BosonType, float] = {
            BosonType.PHOTON: self.element.electronegativity / 4.0,
            BosonType.W_BOSON: self.element.ionization_energy / 2000.0,
            BosonType.Z_BOSON: self.element.electron_affinity / 300.0,
            BosonType.GLUON: self.nucleus.gluon_strength
        }
        
        self.creation_time = time.time()
        self.last_transmutation = time.time()
        
    def create_electron_configuration(self) -> List[ElectronShell]:
        """Crea configuración electrónica real del elemento"""
        shells = []
        electrons_left = self.element.atomic_number
        
        # Orden de llenado: 1s, 2s, 2p, 3s, 3p, 4s, 3d, 4p, 5s, 4d, 5p, 6s, 4f, 5d, 6p, 7s, 5f, 6d, 7p
        filling_order = [
            (1, {"s": 2}),
            (2, {"s": 2, "p": 6}),
            (3, {"s": 2, "p": 6, "d": 10}),
            (4, {"s": 2, "p": 6, "d": 10, "f": 14}),
            (5, {"s": 2, "p": 6, "d": 10, "f": 14}),
            (6, {"s": 2, "p": 6, "d": 10, "f": 14}),
            (7, {"s": 2, "p": 6, "d": 10, "f": 14})
        ]
        
        for shell_num, max_subshells in filling_order:
            if electrons_left <= 0:
                break
                
            shell_config = {}
            for subshell, max_electrons in [("s", 2), ("p", 6), ("d", 10), ("f", 14)]:
                if subshell in max_subshells and electrons_left > 0:
                    electrons_in_subshell = min(electrons_left, max_subshells[subshell])
                    shell_config[subshell] = electrons_in_subshell
                    electrons_left -= electrons_in_subshell
                    
            if shell_config:
                shells.append(ElectronShell(shell_num, shell_config))
                
        return shells
        
    def add_molecule_idea(self, formula: str, bond_type: str = "covalent") -> Molecule:
        """Añade una nueva idea-molécula con química real"""
        molecule = Molecule(
            formula=formula,
            bond_type=bond_type,
            relevance=random.uniform(0.5, 1.0)
        )
        self.molecules.append(molecule)
        return molecule
        
    def reinforce_idea(self, formula: str):
        """Refuerza una idea específica"""
        for molecule in self.molecules:
            if molecule.formula == formula:
                molecule.reinforce()
                
    def prune_irrelevant_ideas(self):
        """Elimina ideas irrelevantes basado en química molecular"""
        current_time = time.time()
        self.molecules = [
            m for m in self.molecules 
            if not m.should_prune(current_time)
        ]
        
    def attempt_transmutation(self) -> bool:
        """Intenta transmutar a otro elemento"""
        if not self.nucleus.can_transmute():
            return False
            
        current_time = time.time()
        if current_time - self.last_transmutation < 60:  # Cooldown
            return False
            
        # Probabilidad de transmutación basada en categoría
        if self.element.category in [ElementCategory.ACTINIDE, ElementCategory.TRANSITION_METAL]:
            if random.random() < 0.1:
                # Transmutar a elemento cercano
                new_atomic_number = self.element.atomic_number
                
                if self.element.atomic_number > 92:  # Elementos transuránicos
                    new_atomic_number = random.randint(1, 92)  # Decaimiento
                else:
                    change = random.choice([-1, 1])
                    new_atomic_number = max(1, min(118, self.element.atomic_number + change))
                
                if new_atomic_number in PERIODIC_TABLE:
                    old_element = self.element.symbol
                    self.element = PERIODIC_TABLE[new_atomic_number]
                    self.nucleus = Nucleus(self.element)
                    self.electron_shells = self.create_electron_configuration()
                    self.state = NodeState.TRANSMUTING
                    self.last_transmutation = current_time
                    
                    print(f"⚛️  Transmutación: {old_element} → {self.element.symbol} en nodo {self.id}")
                    return True
                    
        return False
        
    def update_coherence(self):
        """Actualiza coherencia basada en propiedades elementales"""
        nuclear_stability = self.nucleus.get_stability()
        
        # Coherencia electrónica basada en configuración
        electron_coherence = 1.0
        total_electrons = sum(len(shell.electrons) for shell in self.electron_shells)
        if total_electrons > 0:
            excited_electrons = sum(
                1 for shell in self.electron_shells 
                for electron in shell.electrons 
                if electron.quantum_state == "excited"
            )
            electron_coherence = 1.0 - (excited_electrons / total_electrons) * 0.3
        
        # Coherencia molecular
        idea_coherence = 1.0
        if self.molecules:
            total_molecular_health = sum(
                m.strength * m.relevance * m.stability for m in self.molecules
            )
            idea_coherence = min(2.0, total_molecular_health / len(self.molecules))
        
        # Coherencia basada en categoría del elemento
        category_bonus = {
            ElementCategory.NOBLE_GAS: 0.3,
            ElementCategory.TRANSITION_METAL: 0.2,
            ElementCategory.METALLOID: 0.1,
            ElementCategory.HALOGEN: 0.15,
            ElementCategory.ALKALI_METAL: -0.1,
            ElementCategory.ACTINIDE: -0.2
        }.get(self.element.category, 0.0)
        
        self.coherence = max(0.1, (nuclear_stability + electron_coherence + 
                                  idea_coherence + category_bonus) / 3)
        
    def excite(self, intensity: float):
        """Excita el nodo y sus electrones"""
        self.energy_level = min(300.0, self.energy_level + intensity * self.element.stability_factor)
        
        if intensity > 20:
            self.state = NodeState.EXCITED
            # Excitar electrones de capa externa
            if self.electron_shells:
                outer_shell = self.electron_shells[-1]
                for electron in outer_shell.electrons[:min(3, len(outer_shell.electrons))]:
                    electron.excite()
        else:
            self.state = NodeState.STABLE
            
    def decay_energy(self):
        """Decaimiento natural de energía"""
        decay_rate = 0.999 if self.element.stability_factor > 1.0 else 0.997
        self.energy_level *= decay_rate
        
        if self.energy_level < 20 * self.element.stability_factor:
            self.state = NodeState.DEGRADED
            
        # Relajar electrones excitados
        for shell in self.electron_shells:
            for electron in shell.electrons:
                if electron.quantum_state == "excited" and random.random() < 0.3:
                    electron.relax()
                    
    def connect_to(self, other_node: 'CosmicNode', strength: float = None):
        """Establece conexión basada en compatibilidad química"""
        if strength is None:
            # Calcular afinidad basada en electronegatividades
            electronegativity_diff = abs(self.element.electronegativity - 
                                       other_node.element.electronegativity)
            
            # Elementos con electronegatividades similares se conectan mejor
            if electronegativity_diff < 0.5:
                strength = random.uniform(0.8, 1.0)
            elif electronegativity_diff < 1.0:
                strength = random.uniform(0.5, 0.8) 
            else:
                strength = random.uniform(0.2, 0.5)
                
            # Bonus por categorías compatibles
            compatible_categories = [
                (ElementCategory.ALKALI_METAL, ElementCategory.HALOGEN),
                (ElementCategory.TRANSITION_METAL, ElementCategory.NONMETAL),
                (ElementCategory.METALLOID, ElementCategory.METALLOID)
            ]
            
            for cat1, cat2 in compatible_categories:
                if ((self.element.category == cat1 and other_node.element.category == cat2) or
                    (self.element.category == cat2 and other_node.element.category == cat1)):
                    strength *= 1.3
                    
        self.connections[other_node.id] = min(2.0, strength)
        other_node.connections[self.id] = min(2.0, strength)
        
    def transmit_information(self, target_id: str, information: float) -> float:
        """Transmite información a través de electrones y bosones"""
        if target_id not in self.connections:
            return 0.0
            
        connection_strength = self.connections[target_id]
        
        # Capacidad de transmisión basada en electrones de capa externa
        transmission_capacity = 0.0
        if self.electron_shells:
            outer_shell = self.electron_shells[-1]
            for electron in outer_shell.electrons:
                transmission_capacity += electron.transfer_information(information * 0.1)
        
        # Modulación por bosones
        boson_efficiency = (self.bosons[BosonType.PHOTON] + 
                          self.bosons[BosonType.W_BOSON]) * 0.5
        
        transmitted = (transmission_capacity * connection_strength * 
                      boson_efficiency * self.element.stability_factor)
        
        return min(information, transmitted)
        
    def get_age_years(self) -> float:
        """Calcula la edad del nodo en años simulados"""
        return (time.time() - self.creation_time) * 1000
        
    def get_element_info(self) -> Dict:
        """Obtiene información detallada del elemento"""
        return {
            "símbolo": self.element.symbol,
            "nombre": self.element.name,
            "número_atómico": self.element.atomic_number,
            "masa_atómica": self.element.atomic_mass,
            "categoría": self.element.category.value,
            "período": self.element.period,
            "grupo": self.element.group,
            "electronegatividad": self.element.electronegativity,
            "factor_estabilidad": round(self.element.stability_factor, 3)
        }

class CosmicCluster:
    """Clúster de nodos que representa un concepto químico emergente"""
    
    def __init__(self, cluster_id: str, dominant_category: ElementCategory = None):
        self.id = cluster_id
        self.nodes: Dict[str, CosmicNode] = {}
        self.dominant_category = dominant_category
        self.concept_strength = 1.0
        self.chemical_stability = 1.0
        self.efficiency = 1.0
        self.last_optimization = time.time()
        self.reaction_products: List[str] = []
        
    def add_node(self, node: CosmicNode):
        """Añade un nodo al clúster con verificación química"""
        self.nodes[node.id] = node
        
        # Actualizar categoría dominante
        if not self.dominant_category:
            self.dominant_category = node.element.category
        
        # Simular reacciones químicas cuando se añaden nodos compatibles
        self.simulate_chemical_reactions(node)
        
    def simulate_chemical_reactions(self, new_node: CosmicNode):
        """Simula reacciones químicas entre elementos del clúster"""
        for existing_node in list(self.nodes.values())[:-1]:  # Excluir el nodo recién añadido
            # Probabilidad de reacción basada en electronegatividades
            electronegativity_diff = abs(new_node.element.electronegativity - 
                                       existing_node.element.electronegativity)
            
            reaction_probability = 0.0
            if electronegativity_diff > 1.5:  # Reacción iónica probable
                reaction_probability = 0.3
            elif 0.5 < electronegativity_diff < 1.5:  # Reacción covalente polar
                reaction_probability = 0.2
            elif electronegativity_diff < 0.5:  # Reacción covalente no polar
                reaction_probability = 0.1
                
            if random.random() < reaction_probability:
                # Crear "producto" molecular
                product_formula = f"{existing_node.element.symbol}{new_node.element.symbol}"
                
                if electronegativity_diff > 1.5:
                    bond_type = "ionic"
                elif electronegativity_diff > 0.5:
                    bond_type = "covalent"
                else:
                    bond_type = "metallic" if (existing_node.element.category == ElementCategory.TRANSITION_METAL) else "van_der_waals"
                
                # Añadir molécula-producto a ambos nodos
                existing_node.add_molecule_idea(product_formula, bond_type)
                new_node.add_molecule_idea(product_formula, bond_type)
                
                self.reaction_products.append(product_formula)
                
                print(f"🧪 Reacción química: {existing_node.element.symbol} + {new_node.element.symbol} → {product_formula} ({bond_type})")
        
    def remove_node(self, node_id: str):
        """Elimina un nodo del clúster"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            
    def calculate_concept_strength(self) -> float:
        """Calcula la fuerza del concepto basada en química"""
        if not self.nodes:
            return 0.0
            
        # Coherencia promedio ponderada por estabilidad elemental
        total_weighted_coherence = 0.0
        total_weight = 0.0
        
        for node in self.nodes.values():
            weight = node.element.stability_factor
            total_weighted_coherence += node.coherence * weight
            total_weight += weight
            
        avg_coherence = total_weighted_coherence / total_weight if total_weight > 0 else 0.0
        
        # Factor de conectividad química
        chemical_bonds = 0
        total_possible = len(self.nodes) * (len(self.nodes) - 1)
        
        if total_possible > 0:
            for node in self.nodes.values():
                chemical_bonds += sum(
                    strength for conn_id, strength in node.connections.items()
                    if conn_id in self.nodes and strength > 0.7  # Enlaces fuertes
                )
            connectivity = chemical_bonds / total_possible
        else:
            connectivity = 0
            
        # Bonus por diversidad elemental balanceada
        categories = [node.element.category for node in self.nodes.values()]
        diversity = len(set(categories)) / len(categories) if categories else 0
        
        self.concept_strength = avg_coherence * connectivity * (1 + diversity * 0.3)
        return self.concept_strength
        
    def calculate_chemical_stability(self) -> float:
        """Calcula estabilidad química del clúster"""
        if not self.nodes:
            return 0.0
            
        # Estabilidad basada en productos de reacción
        stable_products = sum(
            1 for product in self.reaction_products
            if any(molecule.formula == product and molecule.stability > 1.0
                   for node in self.nodes.values()
                   for molecule in node.molecules)
        )
        
        product_stability = stable_products / max(1, len(self.reaction_products))
        
        # Estabilidad elemental promedio
        element_stability = sum(node.element.stability_factor 
                              for node in self.nodes.values()) / len(self.nodes)
        
        self.chemical_stability = (product_stability + element_stability) * 0.5
        return self.chemical_stability
        
    def optimize_cluster(self):
        """Optimiza el clúster mediante poda química y refuerzo"""
        current_time = time.time()
        
        # Eliminar nodos con elementos muy inestables
        unstable_nodes = []
        for node_id, node in self.nodes.items():
            if (node.element.stability_factor < 0.2 or 
                node.state == NodeState.DEGRADED or 
                node.coherence < 0.2):
                unstable_nodes.append(node_id)
                
        for node_id in unstable_nodes:
            print(f"🗑️  Podando nodo inestable: {self.nodes[node_id].element.symbol}")
            self.remove_node(node_id)
            
        # Intentar transmutaciones en elementos muy pesados
        for node in self.nodes.values():
            if node.element.atomic_number > 100:
                node.attempt_transmutation()
                
        # Reforzar nodos con alta coherencia química
        for node in self.nodes.values():
            if node.coherence > 0.8:
                node.nucleus.reinforce_cohesion()
                node.excite(15)
                
                # Reforzar moléculas estables
                for molecule in node.molecules:
                    if molecule.stability > 1.0:
                        molecule.reinforce()
                        
        self.last_optimization = current_time
        
    def get_efficiency(self) -> float:
        """Calcula eficiencia energética considerando química"""
        if not self.nodes:
            return 0.0
            
        total_energy = sum(node.energy_level for node in self.nodes.values())
        chemical_output = self.concept_strength * self.chemical_stability * len(self.nodes)
        
        self.efficiency = chemical_output / (total_energy + 1)
        return self.efficiency
        
    def get_elemental_composition(self) -> Dict[str, int]:
        """Obtiene la composición elemental del clúster"""
        composition = {}
        for node in self.nodes.values():
            symbol = node.element.symbol
            composition[symbol] = composition.get(symbol, 0) + 1
        return composition

class CosmicBrain:
    """Cerebro cósmico con química real de 118 elementos"""
    
    def __init__(self, target_lifespan: int = 850):
        self.clusters: Dict[str, CosmicCluster] = {}
        self.global_nodes: Dict[str, CosmicNode] = {}
        self.target_lifespan = target_lifespan
        self.current_age = 0.0
        self.global_coherence = 1.0
        self.chemical_diversity = 0.0
        self.energy_efficiency = 1.0
        self.adaptation_rate = 0.01
        self.maintenance_cycles = 0
        self.transmutation_count = 0
        self.reaction_count = 0
        
    def create_cluster(self, cluster_id: str, concept_type: str, 
                      preferred_category: ElementCategory = None) -> CosmicCluster:
        """Crea clúster con elementos de categoría específica"""
        cluster = CosmicCluster(cluster_id, preferred_category)
        self.clusters[cluster_id] = cluster
        
        # Filtrar elementos por categoría si se especifica
        if preferred_category:
            available_elements = [
                num for num, elem in PERIODIC_TABLE.items()
                if elem.category == preferred_category and elem.stability_factor > 0.3
            ]
        else:
            available_elements = [
                num for num, elem in PERIODIC_TABLE.items()
                if elem.stability_factor > 0.1
            ]
        
        # Crear nodos con elementos de la categoría
        node_count = random.randint(4, 15)
        for i in range(node_count):
            atomic_number = random.choice(available_elements)
            node = CosmicNode(f"{cluster_id}_node_{i}", atomic_number)
            
            # Añadir moléculas conceptuales
            molecular_formulas = self.generate_concept_molecules(concept_type, node.element)
            for formula, bond_type in molecular_formulas:
                node.add_molecule_idea(formula, bond_type)
                
            cluster.add_node(node)
            self.global_nodes[node.id] = node
            
        return cluster
        
    def generate_concept_molecules(self, concept: str, element: Element) -> List[Tuple[str, str]]:
        """Genera moléculas relevantes para el concepto"""
        molecules = []
        
        concept_chemistry = {
            "memoria": [("C6H8O6", "covalent"), ("CaCO3", "ionic"), ("SiO2", "covalent")],
            "creatividad": [("C8H11NO2", "covalent"), ("Au", "metallic"), ("C60", "van_der_waals")],
            "percepción": [("NaCl", "ionic"), ("H2O", "hydrogen"), ("C2H5OH", "hydrogen")],
            "adaptación": [("DNA", "hydrogen"), ("RNA", "hydrogen"), ("ATP", "covalent")],
            "coherencia": [("He", "van_der_waals"), ("Ne", "van_der_waals"), ("Ar", "van_der_waals")],
            "flujo": [("Ag", "metallic"), ("Cu", "metallic"), ("Au", "metallic")]
        }
        
        base_molecules = concept_chemistry.get(concept, [("H2O", "hydrogen")])
        
        # Añadir moléculas específicas del elemento
        if element.category == ElementCategory.NOBLE_GAS:
            molecules.extend([(element.symbol, "van_der_waals")])
        elif element.category == ElementCategory.TRANSITION_METAL:
            molecules.extend([(f"{element.symbol}O", "ionic"), (f"{element.symbol}2O3", "ionic")])
        elif element.category == ElementCategory.HALOGEN:
            molecules.extend([(f"H{element.symbol}", "covalent"), (f"Na{element.symbol}", "ionic")])
        elif element.category == ElementCategory.ALKALI_METAL:
            molecules.extend([(f"{element.symbol}OH", "ionic"), (f"{element.symbol}Cl", "ionic")])
        
        molecules.extend(random.choices(base_molecules, k=random.randint(1, 3)))
        return molecules
        
    def interconnect_clusters(self):
        """Establece conexiones químicas entre clústeres"""
        cluster_list = list(self.clusters.values())
        
        for i, cluster_a in enumerate(cluster_list):
            for cluster_b in cluster_list[i+1:]:
                # Probabilidad basada en compatibilidad química
                compatibility = self.calculate_cluster_compatibility(cluster_a, cluster_b)
                
                if random.random() < compatibility:
                    # Conectar nodos químicamente compatibles
                    nodes_a = list(cluster_a.nodes.values())
                    nodes_b = list(cluster_b.nodes.values())
                    
                    connections = min(5, len(nodes_a), len(nodes_b))
                    
                    for _ in range(connections):
                        node_a = random.choice(nodes_a)
                        node_b = random.choice(nodes_b)
                        node_a.connect_to(node_b)  # Usa cálculo automático de afinidad
                        
    def calculate_cluster_compatibility(self, cluster_a: CosmicCluster, 
                                      cluster_b: CosmicCluster) -> float:
        """Calcula compatibilidad química entre clústeres"""
        if not cluster_a.nodes or not cluster_b.nodes:
            return 0.0
            
        # Compatibilidad basada en categorías químicas
        category_compatibility = {
            (ElementCategory.ALKALI_METAL, ElementCategory.HALOGEN): 0.9,
            (ElementCategory.TRANSITION_METAL, ElementCategory.NONMETAL): 0.7,
            (ElementCategory.ALKALINE_EARTH, ElementCategory.HALOGEN): 0.8,
            (ElementCategory.METALLOID, ElementCategory.METALLOID): 0.6,
            (ElementCategory.NOBLE_GAS, ElementCategory.NOBLE_GAS): 0.3,
            (ElementCategory.ACTINIDE, ElementCategory.ACTINIDE): 0.4
        }
        
        # Obtener categorías dominantes
        cat_a = cluster_a.dominant_category
        cat_b = cluster_b.dominant_category
        
        base_compatibility = category_compatibility.get((cat_a, cat_b), 
                           category_compatibility.get((cat_b, cat_a), 0.5))
        
        # Modificar por estabilidad de productos existentes
        stability_bonus = (cluster_a.chemical_stability + cluster_b.chemical_stability) * 0.1
        
        return min(0.95, base_compatibility + stability_bonus)
        
    def maintain_network(self):
        """Sistema de mantenimiento activo con química avanzada"""
        self.maintenance_cycles += 1
        
        # Optimizar cada clúster
        for cluster in self.clusters.values():
            cluster.optimize_cluster()
            
        # Mantenimiento de nodos individuales
        for node in self.global_nodes.values():
            node.update_coherence()
            node.decay_energy()
            node.prune_irrelevant_ideas()
            
            # Intentar transmutación en elementos inestables
            if node.attempt_transmutation():
                self.transmutation_count += 1
            
            # Reforzar nodos con baja coherencia
            if node.coherence < 0.4:
                node.nucleus.reinforce_cohesion()
                node.excite(20)
                
        # Eliminar clústeres químicamente inestables
        unstable_clusters = []
        for cluster_id, cluster in self.clusters.items():
            if (not cluster.nodes or 
                cluster.calculate_concept_strength() < 0.15 or
                cluster.chemical_stability < 0.2):
                unstable_clusters.append(cluster_id)
                
        for cluster_id in unstable_clusters:
            print(f"🧪 Eliminando clúster químicamente inestable: {cluster_id}")
            del self.clusters[cluster_id]
            
        # Crear nuevos clústeres si la diversidad es baja
        if len(self.clusters) < 3:
            self.create_emergency_cluster()
            
        self.update_global_metrics()
        
    def create_emergency_cluster(self):
        """Crea un clúster de emergencia con elementos estables"""
        emergency_concepts = ["estabilización", "recuperación", "homeostasis"]
        concept = random.choice(emergency_concepts)
        
        # Usar elementos muy estables (gases nobles y metales de transición)
        stable_categories = [ElementCategory.NOBLE_GAS, ElementCategory.TRANSITION_METAL]
        category = random.choice(stable_categories)
        
        cluster_id = f"emergency_{self.maintenance_cycles}"
        self.create_cluster(cluster_id, concept, category)
        print(f"🚨 Clúster de emergencia creado: {cluster_id} ({concept})")
        
    def update_global_metrics(self):
        """Actualiza métricas globales incluyendo diversidad química"""
        if not self.global_nodes:
            self.global_coherence = 0.0
            self.energy_efficiency = 0.0
            self.chemical_diversity = 0.0
            return
            
        # Coherencia global ponderada por estabilidad elemental
        total_weighted_coherence = 0.0
        total_weight = 0.0
        
        for node in self.global_nodes.values():
            weight = node.element.stability_factor
            total_weighted_coherence += node.coherence * weight
            total_weight += weight
            
        self.global_coherence = total_weighted_coherence / total_weight if total_weight > 0 else 0.0
        
        # Diversidad química (fracción de elementos únicos)
        unique_elements = set(node.element.atomic_number for node in self.global_nodes.values())
        self.chemical_diversity = len(unique_elements) / 118  # Normalizado por tabla periódica completa
        
        # Eficiencia energética con factor químico
        total_energy = sum(node.energy_level for node in self.global_nodes.values())
        chemical_output = sum(
            cluster.calculate_concept_strength() * cluster.chemical_stability
            for cluster in self.clusters.values()
        )
        
        if total_energy > 0:
            self.energy_efficiency = (chemical_output * len(self.clusters)) / total_energy
        else:
            self.energy_efficiency = 0.0
            
        # Actualizar edad promedio
        if self.global_nodes:
            self.current_age = sum(node.get_age_years() for node in self.global_nodes.values()) / len(self.global_nodes)
        
    def simulate_thinking_process(self, thought_concept: str, intensity: float = 1.0):
        """Simula proceso de pensamiento con reacciones químicas"""
        # Buscar clúster relevante o crear uno nuevo
        relevant_cluster = None
        for cluster in self.clusters.values():
            # Buscar por productos de reacción o moléculas conceptuales
            if any(thought_concept.lower() in product.lower() 
                   for product in cluster.reaction_products):
                relevant_cluster = cluster
                break
            
            # Buscar por moléculas en nodos
            if any(any(thought_concept.lower() in molecule.formula.lower()
                       for molecule in node.molecules)
                   for node in cluster.nodes.values()):
                relevant_cluster = cluster
                break
                
        if not relevant_cluster:
            # Crear clúster específico para el concepto
            concept_categories = {
                "memoria": ElementCategory.TRANSITION_METAL,
                "creatividad": ElementCategory.NOBLE_GAS,
                "percepción": ElementCategory.HALOGEN,
                "adaptación": ElementCategory.METALLOID,
                "aprendizaje": ElementCategory.ALKALI_METAL
            }
            
            preferred_category = concept_categories.get(thought_concept.lower())
            cluster_id = f"thought_{thought_concept}_{len(self.clusters)}"
            relevant_cluster = self.create_cluster(cluster_id, thought_concept, preferred_category)
            
        # Excitar nodos del clúster relevante
        excited_nodes = []
        for node in relevant_cluster.nodes.values():
            excitation_level = intensity * 25 * node.element.stability_factor
            node.excite(excitation_level)
            excited_nodes.append(node)
            
            # Reforzar ideas relevantes
            for molecule in node.molecules:
                if thought_concept.lower() in molecule.formula.lower():
                    molecule.reinforce()
                    
        # Propagar excitación a través de conexiones químicas
        propagation_count = 0
        for node in excited_nodes:
            for connected_id, strength in node.connections.items():
                if connected_id in self.global_nodes and strength > 0.6:
                    connected_node = self.global_nodes[connected_id]
                    information = intensity * strength * 15
                    transmitted = node.transmit_information(connected_id, information)
                    
                    if transmitted > 8:
                        connected_node.excite(transmitted * 0.6)
                        propagation_count += 1
                        
        print(f"🧠 Proceso de pensamiento '{thought_concept}': "
              f"{len(excited_nodes)} nodos excitados, {propagation_count} propagaciones")
              
    def simulate_chemical_learning(self, experience: str):
        """Simula aprendizaje mediante formación de nuevas conexiones químicas"""
        # Seleccionar nodos aleatorios para formar nuevas conexiones
        available_nodes = list(self.global_nodes.values())
        
        if len(available_nodes) >= 2:
            # Crear varias nuevas conexiones basadas en la experiencia
            connection_count = random.randint(2, min(8, len(available_nodes) // 2))
            
            for _ in range(connection_count):
                node_a, node_b = random.sample(available_nodes, 2)
                
                if node_b.id not in node_a.connections:
                    # Conectar con afinidad química mejorada por aprendizaje
                    node_a.connect_to(node_b)
                    
                    # Crear moléculas de "memoria" de la experiencia
                    memory_formula = f"Mem_{experience}_{random.randint(1, 100)}"
                    node_a.add_molecule_idea(memory_formula, "hydrogen")
                    node_b.add_molecule_idea(memory_formula, "hydrogen")
                    
            print(f"📚 Aprendizaje químico: {connection_count} nuevas conexiones para '{experience}'")
            
    def get_network_status(self) -> Dict:
        """Obtiene estado detallado de la red química"""
        # Composición elemental global
        elemental_composition = {}
        category_distribution = {}
        
        for node in self.global_nodes.values():
            symbol = node.element.symbol
            category = node.element.category.value
            
            elemental_composition[symbol] = elemental_composition.get(symbol, 0) + 1
            category_distribution[category] = category_distribution.get(category, 0) + 1
            
        # Top 10 elementos más abundantes
        top_elements = sorted(elemental_composition.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Productos químicos únicos
        all_products = set()
        for cluster in self.clusters.values():
            all_products.update(cluster.reaction_products)
            
        return {
            "edad_años": round(self.current_age, 2),
            "años_objetivo": self.target_lifespan,
            "coherencia_global": round(self.global_coherence, 3),
            "diversidad_química": round(self.chemical_diversity * 100, 1),
            "eficiencia_energética": round(self.energy_efficiency, 3),
            "total_clústeres": len(self.clusters),
            "total_nodos": len(self.global_nodes),
            "elementos_únicos": len(set(node.element.atomic_number for node in self.global_nodes.values())),
            "transmutaciones": self.transmutation_count,
            "productos_químicos": len(all_products),
            "ciclos_mantenimiento": self.maintenance_cycles,
            "elementos_principales": dict(top_elements),
            "distribución_categorías": category_distribution,
            "nodos_por_estado": {
                state.value: sum(1 for node in self.global_nodes.values() if node.state == state)
                for state in NodeState
            }
        }
        
    def get_detailed_chemistry_report(self) -> Dict:
        """Genera reporte detallado de química del cerebro"""
        report = {
            "resumen_químico": {
                "elementos_totales": len(set(node.element.atomic_number for node in self.global_nodes.values())),
                "reacciones_simuladas": sum(len(cluster.reaction_products) for cluster in self.clusters.values()),
                "estabilidad_promedio": round(sum(node.element.stability_factor for node in self.global_nodes.values()) / len(self.global_nodes), 3),
                "electronegatividad_promedio": round(sum(node.element.electronegativity for node in self.global_nodes.values()) / len(self.global_nodes), 3)
            },
            "clústeres_químicos": {},
            "elementos_críticos": [],
            "reacciones_destacadas": []
        }
        
        # Analizar cada clúster
        for cluster_id, cluster in self.clusters.items():
            cluster_info = {
                "composición": cluster.get_elemental_composition(),
                "estabilidad_química": round(cluster.chemical_stability, 3),
                "productos": cluster.reaction_products[:5],  # Top 5 productos
                "categoría_dominante": cluster.dominant_category.value if cluster.dominant_category else "mixta"
            }
            report["clústeres_químicos"][cluster_id] = cluster_info
            
        # Identificar elementos críticos (muy inestables o muy estables)
        for node in self.global_nodes.values():
            if node.element.stability_factor > 1.8:
                report["elementos_críticos"].append({
                    "elemento": f"{node.element.name} ({node.element.symbol})",
                    "tipo": "muy_estable",
                    "factor_estabilidad": node.element.stability_factor
                })
            elif node.element.stability_factor < 0.2:
                report["elementos_críticos"].append({
                    "elemento": f"{node.element.name} ({node.element.symbol})",
                    "tipo": "muy_inestable", 
                    "factor_estabilidad": node.element.stability_factor
                })
                
        return report
        
    def run_simulation_cycle(self):
        """Ejecuta un ciclo completo con procesos químicos"""
        # Mantenimiento de red
        self.maintain_network()
        
        # Simular procesos de pensamiento químico
        chemical_concepts = [
            "síntesis_proteica", "neurotransmisión", "metabolismo_energético",
            "homeostasis_iónica", "plasticidad_sináptica", "memoria_molecular"
        ]
        
        for _ in range(random.randint(1, 3)):
            concept = random.choice(chemical_concepts)
            intensity = random.uniform(0.8, 2.5)
            self.simulate_thinking_process(concept, intensity)
            
        # Simular aprendizaje químico ocasional
        if random.random() < 0.3:
            learning_experiences = [
                "patrón_sensorial", "asociación_temporal", "consolidación_memoria",
                "adaptación_ambiental", "respuesta_emocional"
            ]
            experience = random.choice(learning_experiences)
            self.simulate_chemical_learning(experience)

# Ejemplo de uso avanzado
if __name__ == "__main__":
    print("🧪 Inicializando Cerebro Cósmico con los 118 elementos...")
    cerebro = CosmicBrain(target_lifespan=875)
    
    # Crear clústeres especializados por categoría química
    cluster_configs = [
        ("metals_pensamiento", "procesamiento_neural", ElementCategory.TRANSITION_METAL),
        ("gases_memoria", "almacenamiento_información", ElementCategory.NOBLE_GAS),
        ("halogenos_percepcion", "detección_estímulos", ElementCategory.HALOGEN),
        ("alcalinos_acción", "respuesta_motora", ElementCategory.ALKALI_METAL),
        ("metaloides_integración", "síntesis_conceptual", ElementCategory.METALLOID),
        ("lantanidos_creatividad", "pensamiento_divergente", ElementCategory.LANTHANIDE)
    ]
    
    for cluster_id, concepto, categoria in cluster_configs:
        cerebro.create_cluster(cluster_id, concepto, categoria)
        print(f"✅ Clúster {categoria.value}: {cluster_id}")
    
    # Interconectar clústeres químicamente
    cerebro.interconnect_clusters()
    
    print("\n🚀 Iniciando simulación del cerebro cósmico...")
    print("="*80)
    
    # Ejecutar simulación extendida
    for ciclo in range(100):
        cerebro.run_simulation_cycle()
        
        if ciclo % 20 == 0:
            status = cerebro.get_network_status()
            print(f"\n--- CICLO {ciclo} ---")
            print(f"Coherencia Global: {status['coherencia_global']:.3f}")
            print(f"Diversidad Química: {status['diversidad_química']:.1f}%")
            print(f"Elementos Únicos: {status['elementos_únicos']}/118")
            print(f"Transmutaciones: {status['transmutaciones']}")
            print(f"Productos Químicos: {status['productos_químicos']}")
            print(f"Elementos Principales: {list(status['elementos_principales'].keys())[:5]}")
            
        # Simular el paso del tiempo
        time.sleep(0.005)
    
    print("\n" + "="*80)
    print("🧬 ESTADO FINAL DEL CEREBRO CÓSMICO QUÍMICO")
    print("="*80)
    
    final_status = cerebro.get_network_status()
    chemistry_report = cerebro.get_detailed_chemistry_report()
    
    print("\n📊 MÉTRICAS GLOBALES:")
    for key, value in final_status.items():
        if key not in ['elementos_principales', 'distribución_categorías', 'nodos_por_estado']:
            print(f"  {key.upper().replace('_', ' ')}: {value}")
    
    print(f"\n🧪 COMPOSICIÓN QUÍMICA:")
    print(f"  Elementos únicos activos: {final_status['elementos_únicos']}/118")
    print(f"  Diversidad química: {final_status['diversidad_química']:.1f}%")
    print(f"  Estabilidad promedio: {chemistry_report['resumen_químico']['estabilidad_promedio']}")
    print(f"  Electronegatividad promedio: {chemistry_report['resumen_químico']['electronegatividad_promedio']}")
    
    print(f"\n⚛️  ELEMENTOS MÁS ABUNDANTES:")
    for elemento, cantidad in list(final_status['elementos_principales'].items())[:8]:
        if elemento in [elem.symbol for elem in PERIODIC_TABLE.values()]:
            element_obj = next(elem for elem in PERIODIC_TABLE.values() if elem.symbol == elemento)
            print(f"  {elemento} ({element_obj.name}): {cantidad} nodos - {element_obj.category.value}")
    
    print(f"\n🏗️  DISTRIBUCIÓN POR CATEGORÍAS:")
    for categoria, cantidad in final_status['distribución_categorías'].items():
        print(f"  {categoria.replace('_', ' ').title()}: {cantidad} nodos")
    
    print(f"\n🔬 PROCESOS QUÍMICOS:")
    print(f"  Transmutaciones realizadas: {final_status['transmutaciones']}")
    print(f"  Productos químicos sintetizados: {final_status['productos_químicos']}")
    print(f"  Reacciones simuladas: {chemistry_report['resumen_químico']['reacciones_simuladas']}")
    
    # Evaluación final
    coherence_percent = final_status['coherencia_global'] * 100
    efficiency_percent = final_status['eficiencia_energética'] * 100
    diversity_percent = final_status['diversidad_química']
    
    print(f"\n📈 RENDIMIENTO FINAL:")
    print(f"  Coherencia global: {coherence_percent:.1f}%")
    print(f"  Eficiencia energética: {efficiency_percent:.1f}%") 
    print(f"  Diversidad química: {diversity_percent:.1f}%")
    
    if (coherence_percent > 60 and efficiency_percent > 30 and diversity_percent > 15):
        print(f"\n✅ El cerebro cósmico mantiene excelentes parámetros químicos")
        print(f"   para una vida prolongada de {cerebro.target_lifespan} años")
        print(f"   con {final_status['elementos_únicos']} elementos activos de la tabla periódica")
    elif (coherence_percent > 40 and efficiency_percent > 20):
        print(f"\n⚠️  El cerebro requiere optimización química adicional")
        print(f"   pero mantiene funcionalidad básica con diversidad elemental")
    else:
        print(f"\n❌ El cerebro necesita restructuración química crítica")
        print(f"   para alcanzar longevidad y estabilidad completas")
        
    print(f"\n🌟 Simulación completada: {final_status['ciclos_mantenimiento']} ciclos de mantenimiento")
    print(f"   Red química distribuida con {final_status['total_nodos']} nodos atómicos")
    print(f"   organizados en {final_status['total_clústeres']} clústeres conceptuales")
