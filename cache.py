# cache_decorators.py
import time
import functools
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple

# ----------------------------------------
# Utilidad: convertir args/kwargs en clave hashable
# ----------------------------------------
def _make_key(args, kwargs):
    def freeze(obj):
        if isinstance(obj, dict):
            return tuple(sorted((k, freeze(v)) for k, v in obj.items()))
        if isinstance(obj, (list, tuple)):
            return tuple(freeze(x) for x in obj)
        if isinstance(obj, set):
            return frozenset(freeze(x) for x in obj)
        return obj  # suponemos hashable

    f_args = tuple(freeze(a) for a in args)
    f_kwargs = tuple(sorted((k, freeze(v)) for k, v in kwargs.items()))
    return (f_args, f_kwargs)

# ----------------------------------------
# Decorador: cache básico (memoización)
# ----------------------------------------
def cache(func):
    """
    Caché simple en memoria: guarda resultados por (args, kwargs).
    """
    _store: Dict[Tuple[Any, ...], Any] = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = _make_key(args, kwargs)
        if key in _store:
            return _store[key]
        result = func(*args, **kwargs)
        _store[key] = result
        return result

    # API auxiliar
    def cache_clear():
        _store.clear()

    def cache_info():
        return {"size": len(_store)}

    wrapper._cache = _store
    wrapper.cache_clear = cache_clear
    wrapper.cache_info = cache_info
    return wrapper

# ----------------------------------------
# Decorador: cache con TTL y LRU opcional
# ----------------------------------------
def cache_ttl(ttl: Optional[float] = None, maxsize: Optional[int] = None):
    """
    Caché con Time-To-Live (TTL) y tamaño máximo (LRU simple).
    - ttl: segundos; si None, no expira.
    - maxsize: si se supera, elimina el menos recientemente usado (LRU).
    """
    if ttl is not None and ttl <= 0:
        raise ValueError("ttl debe ser positivo o None")

    def decorator(func):
        store: "OrderedDict[Tuple[Any, ...], Tuple[float, Any]]" = OrderedDict()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = _make_key(args, kwargs)
            now = time.time()

            # HIT
            if key in store:
                ts, value = store[key]
                # ¿expiró?
                if ttl is not None and (now - ts) >= ttl:
                    # caducado → recalcular
                    result = func(*args, **kwargs)
                    store[key] = (now, result)
                else:
                    # válido → refrescar LRU
                    store.move_to_end(key)
                    return value

            # MISS o expirado → calcular y guardar
            result = func(*args, **kwargs)
            store[key] = (now, result)

            # Control de tamaño (LRU)
            if maxsize is not None and maxsize > 0:
                while len(store) > maxsize:
                    store.popitem(last=False)  # el más antiguo

            store.move_to_end(key)
            return store[key][1]

        # utilidades
        def cache_clear():
            store.clear()

        def cache_info():
            now = time.time()
            live = 0
            expired = 0
            for ts, _ in store.values():
                if ttl is not None and (now - ts) >= ttl:
                    expired += 1
                else:
                    live += 1
            return {
                "size": len(store),
                "live": live,
                "expired": expired,
                "ttl": ttl,
                "maxsize": maxsize,
            }

        def cache_invalidate(*a, **kw):
            key = _make_key(a, kw)
            store.pop(key, None)

        wrapper.cache_clear = cache_clear
        wrapper.cache_info = cache_info
        wrapper.cache_invalidate = cache_invalidate
        wrapper._cache_store = store
        return wrapper

    return decorator

# ----------------------------------------
# Demos rápidas
# Ejecuta este archivo para ver tiempos con/ sin caché
# ----------------------------------------
if __name__ == "__main__":
    print("== Demo cache básica ==")

    @cache
    def pesado(x, *, factor=1):
        time.sleep(1)  # simula cálculo costoso
        return (x * x) * factor

    t0 = time.time(); print("1ª:", pesado(10, factor=2), f"{time.time()-t0:.3f}s")
    t0 = time.time(); print("2ª (cache):", pesado(10, factor=2), f"{time.time()-t0:.3f}s")

    print("\n== Demo cache con TTL (2s) y LRU (128) ==")

    @cache_ttl(ttl=2.0, maxsize=128)
    def lento(n):
        time.sleep(1)  # simula cálculo costoso
        return n * 2

    t0 = time.time(); print("1ª:", lento(21), f"{time.time()-t0:.3f}s")
    t0 = time.time(); print("2ª (cache viva):", lento(21), f"{time.time()-t0:.3f}s")

    print("Esperando a que caduque (2.1s)...")
    time.sleep(2.1)

    t0 = time.time(); print("3ª (expirada):", lento(21), f"{time.time()-t0:.3f}s")
    print("cache_info:", lento.cache_info())

    # Invalidar manualmente una clave
    lento.cache_invalidate(21)
    print("Invalidada la clave (21). cache_info:", lento.cache_info())