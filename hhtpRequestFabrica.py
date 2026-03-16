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
        response = requests.request(
            method=self.method,
            url=self.url,
            headers=self.headers,
            params=self.params,
            data=self.data,
            json=self.json
        )
        return response
 
 
class HttpRequestBuilder:
    def __init__(self):
        self.method = "GET"
        self.url = None
        self.headers = {}
        self.params = {}
        self.data = None
        self.json = None
 
    def set_method(self, method):
        self.method = method.upper()
        return self
 
    def set_url(self, url):
        self.url = url
        return self
 
    def add_header(self, key, value):
        self.headers[key] = value
        return self
 
    def add_param(self, key, value):
        self.params[key] = value
        return self
 
    def set_json(self, json_body):
        self.json = json_body
        return self
 
    def set_data(self, data_body):
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
 
builder = HttpRequestFactory.create_builder()
 
request = (
    builder
    .set_method("GET")
    .set_url("https://api.example.com/users")
    .add_param("page", 2)
    .add_header("Accept", "application/json")
    .build()
)
 
response = request.send()
print(response.status_code, response.text)

builder = HttpRequestFactory.create_builder()
 
request = (
    builder
    .set_method("POST")
    .set_url("https://api.example.com/login")
    .add_header("Content-Type", "application/json")
    .set_json({"username": "admin", "password": "1234"})
    .build()
)
 
response = request.send()
print(response.status_code, response.json())