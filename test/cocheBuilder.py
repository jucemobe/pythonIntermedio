from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ============================
# MODELOS (Producto y piezas)
# ============================

class TipoMotor(Enum):
    DIESEL = "diesel"
    GASOLINA = "gasolina"
    ELECTRICO = "electrico"


@dataclass(frozen=True)
class Rueda:
    marca: str
    pulgadas: int = 16


@dataclass(frozen=True)
class Motor:
    tipo: TipoMotor
    marca: str
    caballos: int
    cilindrada_cc: int = 0  # 0 si es eléctrico o si no aplica


@dataclass
class Coche:
    color: str
    asientos: int
    motor: Motor
    ruedas: List[Rueda] = field(default_factory=list)
    extras: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Validaciones mínimas (puedes ampliarlas)
        if not (2 <= self.asientos <= 7):
            raise ValueError("El coche debe tener entre 2 y 7 asientos.")
        if len(self.ruedas) != 4:
            raise ValueError("El coche debe tener exactamente 4 ruedas.")
        if self.motor.tipo == TipoMotor.ELECTRICO and self.motor.cilindrada_cc != 0:
            raise ValueError("En motor eléctrico, la cilindrada_cc debería ser 0.")
        if self.motor.caballos <= 0:
            raise ValueError("Los caballos deben ser > 0.")


# ============================
# BUILDER
# ============================

class CocheBuilder:
    """
    Builder con interfaz fluida para construir un Coche paso a paso.
    """

    def __init__(self):
        self._reset()

    def _reset(self):
        self._color: str = "blanco"
        self._asientos: int = 5
        self._motor: Optional[Motor] = None
        self._ruedas: List[Rueda] = []
        self._extras: List[str] = []

    # ---- setters fluídos ----
    def color(self, color: str) -> CocheBuilder:
        self._color = color
        return self

    def asientos(self, n: int) -> CocheBuilder:
        self._asientos = n
        return self

    def motor(self, tipo: TipoMotor, marca: str, caballos: int, cilindrada_cc: int = 0) -> CocheBuilder:
        self._motor = Motor(tipo=tipo, marca=marca, caballos=caballos, cilindrada_cc=cilindrada_cc)
        return self

    def rueda(self, marca: str, pulgadas: int = 16) -> CocheBuilder:
        """
        Añade UNA rueda. Puedes mezclar marcas (ruedas de varias marcas).
        Debes añadir 4 en total (se valida al construir).
        """
        self._ruedas.append(Rueda(marca=marca, pulgadas=pulgadas))
        return self

    def ruedas(self, marcas: List[str], pulgadas: int = 16) -> CocheBuilder:
        """
        Añade ruedas a partir de una lista de marcas.
        Ej: ["Michelin","Michelin","Pirelli","Pirelli"]
        """
        for m in marcas:
            self._ruedas.append(Rueda(marca=m, pulgadas=pulgadas))
        return self

    def extra(self, nombre: str) -> CocheBuilder:
        self._extras.append(nombre)
        return self

    def extras(self, nombres: List[str]) -> CocheBuilder:
        self._extras.extend(nombres)
        return self

    # ---- build ----
    def build(self) -> Coche:
        if self._motor is None:
            raise ValueError("Falta configurar el motor (motor(...)).")
        coche = Coche(
            color=self._color,
            asientos=self._asientos,
            motor=self._motor,
            ruedas=list(self._ruedas),
            extras=list(self._extras),
        )
        # opcional: reset para reutilizar el builder sin arrastre
        self._reset()
        return coche


# ============================
# DIRECTOR (opcional, útil en ejercicios)
# ============================

class DirectorCoches:
    """
    Crea configuraciones predefinidas usando el builder.
    """

    def __init__(self, builder: CocheBuilder):
        self.builder = builder

    def construir_suv_familiar(self) -> Coche:
        return (
            self.builder
            .color("gris")
            .asientos(7)
            .motor(TipoMotor.DIESEL, marca="Toyota", caballos=150, cilindrada_cc=2200)
            .ruedas(["Michelin", "Michelin", "Michelin", "Michelin"], pulgadas=18)
            .extras(["camara_360", "sensores_aparcamiento", "porton_electrico"])
            .build()
        )

    def construir_coupe_deportivo(self) -> Coche:
        return (
            self.builder
            .color("rojo")
            .asientos(2)
            .motor(TipoMotor.GASOLINA, marca="BMW", caballos=320, cilindrada_cc=3000)
            # mezcla de marcas (ejemplo)
            .ruedas(["Pirelli", "Pirelli", "Michelin", "Michelin"], pulgadas=19)
            .extras(["modo_sport", "asientos_bucket", "escape_deportivo"])
            .build()
        )

    def construir_electrico_urbano(self) -> Coche:
        return (
            self.builder
            .color("azul")
            .asientos(5)
            .motor(TipoMotor.ELECTRICO, marca="Tesla", caballos=250, cilindrada_cc=0)
            .ruedas(["Continental", "Continental", "Continental", "Continental"], pulgadas=17)
            .extras(["autopilot", "carga_rapida"])
            .build()
        )


# ============================
# EJEMPLOS DE USO (rápidos)
# ============================
if __name__ == "__main__":
    builder = CocheBuilder()

    # 1) Construcción manual (fluida)
    coche_personalizado = (
        builder
        .color("negro")
        .asientos(5)
        .motor(TipoMotor.GASOLINA, marca="SEAT", caballos=110, cilindrada_cc=1400)
        .rueda("Michelin", 16).rueda("Michelin", 16).rueda("Pirelli", 16).rueda("Pirelli", 16)
        .extras(["gps", "sensores_lluvia", "climatizador"])
        .build()
    )
    print("Coche personalizado:", coche_personalizado)

    # 2) Con Director (configuraciones predefinidas)
    director = DirectorCoches(CocheBuilder())

    suv = director.construir_suv_familiar()
    coupe = director.construir_coupe_deportivo()
    electrico = director.construir_electrico_urbano()

    print("SUV familiar:", suv)
    print("Coupé deportivo:", coupe)
    print("Eléctrico urbano:", electrico)