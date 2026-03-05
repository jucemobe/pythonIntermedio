class Usuario:
    """
    Clase Usuario con:
      - nombre
      - contraseña (debe tener más de 20 caracteres)
    """

    def __init__(self, nombre: str, contraseña: str):
        self.nombre = nombre
        self.contraseña = None  # se asigna mediante el setter
        self.set_contraseña(contraseña)

    def set_contraseña(self, nueva_contraseña: str):
        """
        Establece la contraseña validando longitud.
        """
        if not isinstance(nueva_contraseña, str):
            raise TypeError("La contraseña debe ser una cadena de texto.")
        
        if len(nueva_contraseña) <= 20:
            raise ValueError("La contraseña debe tener más de 20 caracteres.")
        
        self.contraseña = nueva_contraseña
        print("[INFO] Contraseña establecida correctamente.")

    def __str__(self):
        return f"Usuario(nombre='{self.nombre}')"

    def __repr__(self):
        return f"Usuario(nombre={self.nombre!r}, contraseña='***oculta***')"

# ============================
# Ejemplo de uso
# ============================
if __name__ == "__main__":
    try:
        u = Usuario("Carlos", "estaesunacontraseñamuyseguraylarga123")
        print(u)
    except Exception as e:
        print("[ERROR]", e)