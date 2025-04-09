import time
from typing import Dict, Any, Callable, Optional
from functools import wraps
import logging
from contextlib import contextmanager

# Opcionalmente, integrar com libs como prometheus_client
try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Logger para métricas
logger = logging.getLogger(__name__)

# Métricas em memória como fallback
_in_memory_metrics = {
    "counters": {},
    "histograms": {},
    "gauges": {}
}


def increment_counter(name: str, value: int = 1, labels: Optional[Dict[str, str]] = None) -> None:
    """
    Incrementa um contador.
    
    Args:
        name: Nome do contador
        value: Valor a incrementar
        labels: Rótulos adicionais
    """
    labels = labels or {}
    
    if PROMETHEUS_AVAILABLE:
        try:
            # Usar Prometheus se disponível
            counter_key = f"counter_{name}"
            
            if counter_key not in globals():
                globals()[counter_key] = Counter(name, f"Contador para {name}", list(labels.keys()))
            
            if labels:
                globals()[counter_key].labels(**labels).inc(value)
            else:
                globals()[counter_key].inc(value)
        except Exception as e:
            logger.warning(f"Erro ao incrementar contador Prometheus: {e}")
            _fallback_increment_counter(name, value, labels)
    else:
        _fallback_increment_counter(name, value, labels)


def _fallback_increment_counter(name: str, value: int = 1, labels: Optional[Dict[str, str]] = None) -> None:
    """Fallback para contador em memória."""
    labels_key = "_".join([f"{k}:{v}" for k, v in (labels or {}).items()])
    key = f"{name}_{labels_key}" if labels_key else name
    
    if key not in _in_memory_metrics["counters"]:
        _in_memory_metrics["counters"][key] = 0
    
    _in_memory_metrics["counters"][key] += value


def observe_histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """
    Observa um valor para um histograma.
    
    Args:
        name: Nome do histograma
        value: Valor a observar
        labels: Rótulos adicionais
    """
    labels = labels or {}
    
    if PROMETHEUS_AVAILABLE:
        try:
            # Usar Prometheus se disponível
            histogram_key = f"histogram_{name}"
            
            if histogram_key not in globals():
                globals()[histogram_key] = Histogram(
                    name, f"Histograma para {name}", list(labels.keys())
                )
            
            if labels:
                globals()[histogram_key].labels(**labels).observe(value)
            else:
                globals()[histogram_key].observe(value)
        except Exception as e:
            logger.warning(f"Erro ao observar histograma Prometheus: {e}")
            _fallback_observe_histogram(name, value, labels)
    else:
        _fallback_observe_histogram(name, value, labels)


def _fallback_observe_histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """Fallback para histograma em memória."""
    labels_key = "_".join([f"{k}:{v}" for k, v in (labels or {}).items()])
    key = f"{name}_{labels_key}" if labels_key else name
    
    if key not in _in_memory_metrics["histograms"]:
        _in_memory_metrics["histograms"][key] = []
    
    _in_memory_metrics["histograms"][key].append(value)


def set_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """
    Define um valor para um gauge.
    
    Args:
        name: Nome do gauge
        value: Valor a definir
        labels: Rótulos adicionais
    """
    labels = labels or {}
    
    if PROMETHEUS_AVAILABLE:
        try:
            # Usar Prometheus se disponível
            gauge_key = f"gauge_{name}"
            
            if gauge_key not in globals():
                globals()[gauge_key] = Gauge(name, f"Gauge para {name}", list(labels.keys()))
            
            if labels:
                globals()[gauge_key].labels(**labels).set(value)
            else:
                globals()[gauge_key].set(value)
        except Exception as e:
            logger.warning(f"Erro ao definir gauge Prometheus: {e}")
            _fallback_set_gauge(name, value, labels)
    else:
        _fallback_set_gauge(name, value, labels)


def _fallback_set_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """Fallback para gauge em memória."""
    labels_key = "_".join([f"{k}:{v}" for k, v in (labels or {}).items()])
    key = f"{name}_{labels_key}" if labels_key else name
    
    _in_memory_metrics["gauges"][key] = value


@contextmanager
def measure_time(name: str, labels: Optional[Dict[str, str]] = None):
    """
    Contexto para medir tempo de execução.
    
    Args:
        name: Nome da métrica
        labels: Rótulos adicionais
    
    Yields:
        None
    """
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        observe_histogram(f"{name}_seconds", elapsed_time, labels)


def timed(name: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
    """
    Decorador para medir tempo de execução de uma função.
    
    Args:
        name: Nome da métrica (default é nome da função)
        labels: Rótulos adicionais
    
    Returns:
        Decorador
    """
    def decorator(func: Callable):
        metric_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with measure_time(metric_name, labels):
                return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def get_metrics() -> Dict[str, Any]:
    """
    Obtém todas as métricas em memória.
    
    Returns:
        Dicionário com métricas
    """
    return _in_memory_metrics
