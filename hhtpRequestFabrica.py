import requests

class HttpRequest:
    def __init__(self, method, url, headers=None, params=None, data=None, json=None):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.params = params or {}
        self.data = data
        self.json = json

    def send(self):
        try:
            response = requests.request(
                method=self.method,
                url=self.url,
                headers=self.headers,
                params=self.params,
                data=self.data,
                json=self.json,
                timeout=10  # ✅ Evita que la petición se quede colgada
            )
            response.raise_for_status()  # ✅ Lanza excepción si el status es 4xx o 5xx
            return response

        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"No se pudo conectar a: {self.url}")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"La petición a {self.url} superó el tiempo límite")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Error HTTP: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error inesperado en la petición: {e}")


class HttpRequestBuilder:
    VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}

    def __init__(self):
        self.method = "GET"
        self.url = None
        self.headers = {}
        self.params = {}
        self.data = None
        self.json = None

    def set_method(self, method):
        method = method.upper()
        if method not in self.VALID_METHODS:  # ✅ Valida que el método HTTP sea válido
            raise ValueError(f"Método HTTP no válido: '{method}'. Permitidos: {self.VALID_METHODS}")
        self.method = method
        return self

    def set_url(self, url):
        if not url or not url.startswith(("http://", "https://")):  # ✅ Valida formato de URL
            raise ValueError(f"URL no válida: '{url}'. Debe comenzar con http:// o https://")
        self.url = url
        return self

    def add_header(self, key, value):
        if not isinstance(key, str) or not isinstance(value, str):  # ✅ Valida tipos de cabecera
            raise TypeError("La clave y el valor del header deben ser strings")
        self.headers[key] = value
        return self

    def add_param(self, key, value):
        self.params[key] = value
        return self

    def set_json(self, json_body):
        if self.data is not None:  # ✅ Evita conflicto entre json y data
            raise ValueError("No se puede usar 'json' y 'data' al mismo tiempo")
        self.json = json_body
        return self

    def set_data(self, data_body):
        if self.json is not None:  # ✅ Evita conflicto entre data y json
            raise ValueError("No se puede usar 'data' y 'json' al mismo tiempo")
        self.data = data_body
        return self

    def build(self):
        if not self.url:
            raise ValueError("La URL es obligatoria para construir la petición")
        return HttpRequest(
            method=self.method,
            url=self.url,
            headers=self.headers,
            params=self.params,
            data=self.data,
            json=self.json
        )


class HttpRequestFactory:
    @staticmethod
    def create_builder():
        return HttpRequestBuilder()


# ✅ URLs públicas reales para pruebas (reemplaza api.example.com)

# Ejemplo GET
builder = HttpRequestFactory.create_builder()
request = (
    builder
    .set_method("GET")
    .set_url("https://jsonplaceholder.typicode.com/users")
    .add_param("_page", 2)
    .add_header("Accept", "application/json")
    .build()
)
response = request.send()
print(response.status_code, response.text[:100])  # Muestra los primeros 100 caracteres

# Ejemplo POST
builder = HttpRequestFactory.create_builder()
request = (
    builder
    .set_method("POST")
    .set_url("https://jsonplaceholder.typicode.com/posts")
    .add_header("Content-Type", "application/json")
    .set_json({"username": "admin", "password": "1234"})
    .build()
)
response = request.send()
print(response.status_code, response.json())