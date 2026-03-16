from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Any, Tuple
from enum import Enum, unique
import json
import copy


@unique
class MetodoHTTP(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"


@dataclass(frozen=True)
class HttpRequest:
    """
    Representa una petición HTTP inmutable.

    Atributos:
        metodo: Método HTTP (Enum MetodoHTTP).
        url: Cadena con la URL (no se valida).
        headers: Diccionario de cabeceras (strings).
        body: JSON como dict (o None si no hay cuerpo).
    """
    metodo: MetodoHTTP
    url: str
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]] = None  # JSON (dict) o None

    def cuerpo_json_str(self, *, ensure_ascii: bool = False) -> Optional[str]:
        """Devuelve el cuerpo en JSON (str) si existe; en caso contrario None."""
        if self.body is None:
            return None
        return json.dumps(self.body, ensure_ascii=ensure_ascii)

    # ----- Helpers opcionales -----
    def to_requests_tuple(self) -> Tuple[str, str, Dict[str, str], Optional[str]]:
        """
        Devuelve (method, url, headers, data_str) listo para requests.
        data_str será una cadena JSON si hay body; si no, None.
        """
        data_str = self.cuerpo_json_str()
        return (self.metodo.value, self.url, self.headers, data_str)


class ConstructorHttpRequest:
    """
    Builder fluido para construir una HttpRequest respetando:
    - Body permitido solo en POST, PUT, PATCH (como JSON/dict).
    - URL se acepta tal cual (sin validación).
    - Headers por defecto y posibilidad de añadir clave/valor (strings).
    """

    _HEADERS_POR_DEFECTO: Dict[str, str] = {
        "User-Agent": "HttpRequestBuilder/1.0",
        "Accept": "application/json",
    }

    def __init__(self) -> None:
        # Estado interno mutable del builder
        self._metodo: Optional[MetodoHTTP] = None
        self._url: Optional[str] = None
        self._headers: Dict[str, str] = copy.deepcopy(self._HEADERS_POR_DEFECTO)
        self._body: Optional[Dict[str, Any]] = None

    # --------- API fluida (en español) ---------
    def metodo(self, metodo: str | MetodoHTTP) -> "ConstructorHttpRequest":
        """Establece el método HTTP. Acepta string o enum MetodoHTTP."""
        if isinstance(metodo, str):
            try:
                self._metodo = MetodoHTTP(metodo.upper())
            except ValueError:
                raise ValueError(
                    f"Método no soportado: {metodo}. "
                    f"Válidos: {', '.join(m.value for m in MetodoHTTP)}"
                )
        elif isinstance(metodo, MetodoHTTP):
            self._metodo = metodo
        else:
            raise TypeError("metodo debe ser str o MetodoHTTP")
        return self

    def url(self, url: str) -> "ConstructorHttpRequest":
        """Establece la URL (sin validación)."""
        if not isinstance(url, str):
            raise TypeError("url debe ser str")
        self._url = url
        return self

    def añadir_header(self, clave: str, valor: str) -> "ConstructorHttpRequest":
        """
        Añade o sobreescribe una cabecera.
        clave y valor deben ser strings.
        """
        if not isinstance(clave, str) or not isinstance(valor, str):
            raise TypeError("clave y valor del header deben ser str")
        self._headers[clave] = valor
        return self

    def body(self, json_body: Dict[str, Any]) -> "ConstructorHttpRequest":
        """
        Define el cuerpo como JSON (dict).
        Solo se permite para métodos POST, PUT y PATCH.
        """
        if not isinstance(json_body, dict):
            raise TypeError("El body debe ser un dict (JSON).")
        self._body = json_body
        return self

    def construir(self) -> HttpRequest:
        """Valida y construye la HttpRequest inmutable."""
        if self._metodo is None:
            raise ValueError("Falta definir el método HTTP mediante .metodo(...)")
        if self._url is None:
            raise ValueError("Falta definir la URL mediante .url(...)")

        # Validación de body vs método
        if self._body is not None and self._metodo not in {MetodoHTTP.POST, MetodoHTTP.PUT, MetodoHTTP.PATCH}:
            raise ValueError(
                f"El body solo está permitido en POST, PUT y PATCH (actual: {self._metodo.value})."
            )

        # Si hay body y no se especificó Content-Type, por defecto JSON
        headers_finales = copy.deepcopy(self._headers)
        if self._body is not None:
            headers_finales.setdefault("Content-Type", "application/json")

        # Construir objeto inmutable
        return HttpRequest(
            metodo=self._metodo,
            url=self._url,
            headers=headers_finales,
            body=copy.deepcopy(self._body) if self._body is not None else None,
        )


# --------------------- Ejemplos de uso ---------------------
if __name__ == "__main__":
    # --- Ejemplo 1: Tu caso (POST con body y Content-Type definido) ---
    peticion = (
        ConstructorHttpRequest()
        .metodo("POST")
        .url("/home")
        .añadir_header("Content-Type", "application/json")
        .body({"nombre": "Joaquin"})
        .construir()
    )

    print("Ejemplo 1 (tu caso):")
    print("método:", peticion.metodo)       # MetodoHTTP.POST
    print("url:", peticion.url)             # /home
    print("headers:", peticion.headers)     # {'User-Agent':..., 'Accept':..., 'Content-Type': 'application/json'}
    print("body:", peticion.body)           # {'nombre': 'Joaquin'}
    print("body JSON str:", peticion.cuerpo_json_str())  # {"nombre": "Joaquin"}
    print()

    # --- Ejemplo 2: PUT con body sin Content-Type (se añade por defecto) ---
    req_put = (
        ConstructorHttpRequest()
        .metodo("PUT")
        .url("https://api.ejemplo.com/usuarios/42")
        .body({"activo": True})
        .construir()
    )
    print("Ejemplo 2 (PUT con body y Content-Type automático):")
    print("headers:", req_put.headers)
    print()

    # --- Ejemplo 3: GET sin body y con header custom ---
    req_get = (
        ConstructorHttpRequest()
        .metodo(MetodoHTTP.GET)
        .url("https://api.ejemplo.com/usuarios")
        .añadir_header("X-Trace-Id", "abc-123")
        .construir()
    )
    print("Ejemplo 3 (GET sin body):")
    print("headers:", req_get.headers)
    print()

    # --- Ejemplo 4: Usar helper para requests ---
    method, url_, headers, data_str = peticion.to_requests_tuple()
    print("Ejemplo 4 (para requests):")
    print("method:", method)
    print("url:", url_)
    print("headers:", headers)
    print("data_str:", data_str)
    print()

    # Nota: si quisieras usar 'requests', sería algo así:
    # import requests
    # resp = requests.request(method, url_, headers=headers, data=data_str, timeout=10)
    # print(resp.status_code, resp.text)
