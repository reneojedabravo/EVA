# monitoring.py

"""Módulo de monitoreo para el sistema de neuronas cognitivas.
Proporciona logging estructurado, registro de activaciones y errores.
Compatible con neuronas animales y miceliales.
"""

import time
import sys
from collections import deque
from threading import RLock
from typing import Any, Dict, Optional

# ─── Niveles de log ──────────────────────────────────────────────────────────
LOG_LEVELS = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
CURRENT_LOG_LEVEL = "INFO"   # Cambia a "DEBUG" para máximo detalle

# ─── Colores ANSI (se desactivan automáticamente si no hay terminal) ─────────
_USE_COLOR = sys.stdout.isatty()
_COLORS = {
    "DEBUG":    "\033[90m",   # gris
    "INFO":     "\033[0m",    # normal
    "WARNING":  "\033[93m",   # amarillo
    "ERROR":    "\033[91m",   # rojo
    "CRITICAL": "\033[1;91m", # rojo negrita
    "RESET":    "\033[0m",
    "CYAN":     "\033[96m",
    "GREEN":    "\033[92m",
    "MAGENTA":  "\033[95m",
}

def _color(text: str, level: str) -> str:
    if not _USE_COLOR:
        return text
    c = _COLORS.get(level, "")
    r = _COLORS["RESET"]
    return f"{c}{text}{r}"

# ─── Almacenamiento en memoria (ring buffer) ─────────────────────────────────
_MAX_LOG_ENTRIES       = 5000
_MAX_ACTIVATION_ENTRIES = 2000
_MAX_ERROR_ENTRIES     = 500

_log_buffer:        deque = deque(maxlen=_MAX_LOG_ENTRIES)
_activation_buffer: deque = deque(maxlen=_MAX_ACTIVATION_ENTRIES)
_error_buffer:      deque = deque(maxlen=_MAX_ERROR_ENTRIES)
_lock = RLock()

# ─── Estadísticas globales ───────────────────────────────────────────────────
_stats: Dict[str, Any] = {
    "total_events":      0,
    "total_activations": 0,
    "total_errors":      0,
    "total_warnings":    0,
    "neurons_seen":      set(),
    "start_time":        time.time(),
}


# ════════════════════════════════════════════════════════════════════════════════
#  FUNCIONES PRINCIPALES
# ════════════════════════════════════════════════════════════════════════════════

def log_event(message: str, level: str = "INFO", neuron_id: str = "") -> None:
    """Registra un evento genérico del sistema.

    Args:
        message:   Texto del evento.
        level:     Nivel de severidad (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        neuron_id: ID opcional de la neurona que genera el evento.
    """
    if LOG_LEVELS.get(level, 0) < LOG_LEVELS.get(CURRENT_LOG_LEVEL, 1):
        return

    entry = {
        "ts":        time.time(),
        "level":     level,
        "neuron_id": neuron_id,
        "message":   message,
    }

    with _lock:
        _log_buffer.append(entry)
        _stats["total_events"] += 1
        if level == "WARNING":
            _stats["total_warnings"] += 1

    ts_str     = _fmt_ts(entry["ts"])
    prefix     = f"[{level:<8}]"
    nid_str    = f" ({neuron_id})" if neuron_id else ""
    line       = f"{ts_str} {prefix}{nid_str} {message}"
    print(_color(line, level))


def log_neuron_activation(
    neuron_id: str,
    activation_level: float,
    plasticity: float = 0.0,
    impact: float = 0.0,
    efficiency: float = 0.0,
) -> None:
    """Registra una activación neuronal con sus métricas asociadas.

    Args:
        neuron_id:        Identificador de la neurona.
        activation_level: Nivel de activación (0.0–1.0).
        plasticity:       Score de plasticidad actual.
        impact:           Score de impacto actual.
        efficiency:       Score de eficiencia actual.
    """
    entry = {
        "ts":               time.time(),
        "neuron_id":        neuron_id,
        "activation_level": activation_level,
        "plasticity":       plasticity,
        "impact":           impact,
        "efficiency":       efficiency,
    }

    with _lock:
        _activation_buffer.append(entry)
        _stats["total_activations"] += 1
        _stats["neurons_seen"].add(neuron_id)

    if LOG_LEVELS.get(CURRENT_LOG_LEVEL, 1) <= LOG_LEVELS["DEBUG"]:
        ts_str = _fmt_ts(entry["ts"])
        bar    = _activation_bar(activation_level)
        line   = (
            f"{ts_str} [ACTIVATION] ({neuron_id}) "
            f"act={activation_level:.3f} {bar} "
            f"plas={plasticity:.3f} imp={impact:.3f} eff={efficiency:.3f}"
        )
        print(_color(line, "DEBUG"))


def log_neuron_error(neuron_id: str, error_message: str) -> None:
    """Registra un error en una neurona específica.

    Args:
        neuron_id:     Identificador de la neurona.
        error_message: Descripción del error (puede incluir traceback).
    """
    entry = {
        "ts":        time.time(),
        "neuron_id": neuron_id,
        "message":   error_message,
    }

    with _lock:
        _error_buffer.append(entry)
        _stats["total_errors"] += 1

    ts_str = _fmt_ts(entry["ts"])
    # Truncar mensajes muy largos en consola
    short_msg = error_message.split("\n")[0][:200]
    line = f"{ts_str} [ERROR   ] ({neuron_id}) {short_msg}"
    print(_color(line, "ERROR"))


def log_neuron_warning(neuron_id: str, warning_message: str) -> None:
    """Registra una advertencia en una neurona específica.

    Args:
        neuron_id:       Identificador de la neurona.
        warning_message: Descripción de la advertencia.
    """
    log_event(warning_message, level="WARNING", neuron_id=neuron_id)


# ════════════════════════════════════════════════════════════════════════════════
#  CONSULTAS Y ESTADÍSTICAS
# ════════════════════════════════════════════════════════════════════════════════

def get_stats() -> Dict[str, Any]:
    """Retorna estadísticas globales del sistema de monitoreo."""
    with _lock:
        uptime = time.time() - _stats["start_time"]
        return {
            "uptime_s":          round(uptime, 2),
            "total_events":      _stats["total_events"],
            "total_activations": _stats["total_activations"],
            "total_errors":      _stats["total_errors"],
            "total_warnings":    _stats["total_warnings"],
            "unique_neurons":    len(_stats["neurons_seen"]),
            "log_buffer_size":   len(_log_buffer),
            "error_buffer_size": len(_error_buffer),
        }


def get_recent_errors(n: int = 10) -> list:
    """Retorna los últimos n errores registrados."""
    with _lock:
        return list(_error_buffer)[-n:]


def get_recent_activations(neuron_id: str = "", n: int = 20) -> list:
    """Retorna las últimas n activaciones, opcionalmente filtradas por neurona."""
    with _lock:
        entries = list(_activation_buffer)
        if neuron_id:
            entries = [e for e in entries if e["neuron_id"] == neuron_id]
        return entries[-n:]


def get_recent_events(level: str = "", n: int = 20) -> list:
    """Retorna los últimos n eventos, opcionalmente filtrados por nivel."""
    with _lock:
        entries = list(_log_buffer)
        if level:
            entries = [e for e in entries if e["level"] == level]
        return entries[-n:]


def reset() -> None:
    """Limpia todos los buffers y reinicia estadísticas."""
    with _lock:
        _log_buffer.clear()
        _activation_buffer.clear()
        _error_buffer.clear()
        _stats["total_events"]      = 0
        _stats["total_activations"] = 0
        _stats["total_errors"]      = 0
        _stats["total_warnings"]    = 0
        _stats["neurons_seen"]      = set()
        _stats["start_time"]        = time.time()


def set_log_level(level: str) -> None:
    """Cambia el nivel mínimo de log en tiempo de ejecución.

    Args:
        level: Uno de DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """
    global CURRENT_LOG_LEVEL
    if level not in LOG_LEVELS:
        raise ValueError(f"Nivel inválido '{level}'. Opciones: {list(LOG_LEVELS.keys())}")
    CURRENT_LOG_LEVEL = level


def print_summary() -> None:
    """Imprime un resumen del estado del sistema de monitoreo."""
    s = get_stats()
    sep = "─" * 50
    print(f"\n{sep}")
    print("  RESUMEN DE MONITOREO")
    print(sep)
    print(f"  Uptime:             {s['uptime_s']} s")
    print(f"  Eventos totales:    {s['total_events']}")
    print(f"  Activaciones:       {s['total_activations']}")
    print(f"  Errores:            {s['total_errors']}")
    print(f"  Advertencias:       {s['total_warnings']}")
    print(f"  Neuronas vistas:    {s['unique_neurons']}")
    print(f"  Nivel de log:       {CURRENT_LOG_LEVEL}")
    print(sep)

    if s["total_errors"] > 0:
        print("\n  Últimos errores:")
        for e in get_recent_errors(3):
            short = e["message"].split("\n")[0][:80]
            print(f"    [{e['neuron_id']}] {short}")
    print()


# ════════════════════════════════════════════════════════════════════════════════
#  UTILIDADES INTERNAS
# ════════════════════════════════════════════════════════════════════════════════

def _fmt_ts(ts: float) -> str:
    """Formatea timestamp como HH:MM:SS.mmm"""
    t = time.localtime(ts)
    ms = int((ts % 1) * 1000)
    return f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}.{ms:03d}"


def _activation_bar(level: float, width: int = 10) -> str:
    """Barra visual ASCII para nivel de activación."""
    filled = int(round(level * width))
    return f"[{'█' * filled}{'░' * (width - filled)}]"


# ════════════════════════════════════════════════════════════════════════════════
#  AUTO-TEST
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Ejecutando auto-test de monitoring.py...\n")

    set_log_level("DEBUG")

    log_event("Sistema de monitoreo iniciado", "INFO")
    log_event("Parámetro de prueba fuera de rango", "WARNING", "test_neuron_01")
    log_neuron_activation("test_neuron_01", 0.82, plasticity=0.6, impact=0.4, efficiency=0.75)
    log_neuron_activation("test_neuron_02", 0.45, plasticity=0.5, impact=0.3, efficiency=0.60)
    log_neuron_error("test_neuron_03", "ValueError: señal nula recibida en receive_signal")
    log_event("Ciclo de mantenimiento completado", "INFO")

    print_summary()

    s = get_stats()
    assert s["total_activations"] == 2, "Conteo de activaciones incorrecto"
    assert s["total_errors"]      == 1, "Conteo de errores incorrecto"
    assert s["unique_neurons"]    == 2, "Conteo de neuronas únicas incorrecto"

    print("✓ Todos los assertions pasaron.")
