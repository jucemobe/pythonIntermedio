# archivo: sql_query_builder.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional, Sequence, Any


@dataclass(frozen=True)
class SQLCompilado:
    """
    Resultado final de la compilación de la consulta.
    """
    sql: str
    params: Tuple[Any, ...]  # parámetros posicionales para prepared statements

    def __str__(self) -> str:
        return self.sql


class SQLQuery:
    """
    Builder fluido para construir consultas SQL SELECT de forma segura y expresiva.

    Características:
    - select(*columnas): añade columnas a seleccionar (strings tal cual).
    - from_table(tabla): establece la tabla principal.
    - where(cond): añade una condición raw (tal cual). Útil para condiciones simples.
    - where_param(cond, *params): añade condición con parámetros posicionales (seguro).
      Ej: where_param("edad > ? AND matriculados = ?", 18, True)
    - order_by(*expresiones): ordenaciones arbitrarias (raw).
    - group_by(*expresiones): agrupaciones (raw).
    - having(cond): condición HAVING raw (si usas group_by).
    - limit(n): límite de filas (int).
    - offset(n): desplazamiento (int).
    - join(tipo, tabla, on): añade JOIN raw (ej. tipo="INNER", "LEFT", etc.)
    - inner_join/left_join/right_join/full_join(table, on): atajos de join comunes.

    Salida:
    - construir(): devuelve el SQL como string.
    - compilar(): devuelve SQLCompilado(sql, params) útil para drivers con parámetros.
    """

    __slots__ = (
        "_selects",
        "_from",
        "_wheres_raw",
        "_wheres_param",
        "_order_bys",
        "_group_bys",
        "_having_raw",
        "_having_params",
        "_joins",
        "_limit",
        "_offset",
    )

    def __init__(self) -> None:
        self._selects: List[str] = []
        self._from: Optional[str] = None
        self._wheres_raw: List[str] = []               # condiciones como texto plano
        self._wheres_param: List[Tuple[str, Tuple[Any, ...]]] = []  # (cond, params)
        self._order_bys: List[str] = []
        self._group_bys: List[str] = []
        self._having_raw: List[str] = []
        self._having_params: List[Tuple[str, Tuple[Any, ...]]] = []
        self._joins: List[Tuple[str, str, str]] = []   # (tipo, tabla, on)
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None

    # ---------------- API fluida ----------------

    def select(self, *columnas: str) -> "SQLQuery":
        """
        Añade columnas al SELECT. Acepta '*' o expresiones (p. ej. 'COUNT(*) as total').
        Llamadas sucesivas acumulan columnas.
        """
        if not columnas:
            raise ValueError("select requiere al menos una columna o '*'.")
        for c in columnas:
            if not isinstance(c, str) or not c.strip():
                raise ValueError("Cada columna debe ser str no vacío.")
            self._selects.append(c.strip())
        return self

    def from_table(self, tabla: str) -> "SQLQuery":
        """Establece la tabla principal del FROM."""
        if not isinstance(tabla, str) or not tabla.strip():
            raise ValueError("from_table requiere un nombre de tabla (str no vacío).")
        self._from = tabla.strip()
        return self

    def where(self, condicion_raw: str) -> "SQLQuery":
        """
        Añade una condición WHERE como texto literal (raw).
        Ejemplo: where("edad > 18")
        """
        if not isinstance(condicion_raw, str) or not condicion_raw.strip():
            raise ValueError("where requiere una condición (str no vacío).")
        self._wheres_raw.append(condicion_raw.strip())
        return self

    def where_param(self, condicion: str, *params: Any) -> "SQLQuery":
        """
        Añade condición WHERE con parámetros posicionales (para prepared statements).
        Usa '?' en la condición y pasa los valores como *params.
        Ej: where_param("edad > ? AND matriculados = ?", 18, True)
        """
        if not isinstance(condicion, str) or not condicion.strip():
            raise ValueError("where_param requiere una condición (str no vacío).")
        self._wheres_param.append((condicion.strip(), tuple(params)))
        return self

    def order_by(self, *expresiones: str) -> "SQLQuery":
        """
        Añade cláusulas ORDER BY (raw), p.ej. "id ASC", "nombre DESC".
        """
        if not expresiones:
            raise ValueError("order_by requiere al menos una expresión.")
        for e in expresiones:
            if not isinstance(e, str) or not e.strip():
                raise ValueError("Cada expresión de order_by debe ser str no vacío.")
            self._order_bys.append(e.strip())
        return self

    def group_by(self, *expresiones: str) -> "SQLQuery":
        """Añade columnas/expresiones a GROUP BY (raw)."""
        if not expresiones:
            raise ValueError("group_by requiere al menos una expresión.")
        for e in expresiones:
            if not isinstance(e, str) or not e.strip():
                raise ValueError("Cada expresión de group_by debe ser str no vacío.")
            self._group_bys.append(e.strip())
        return self

    def having(self, condicion_raw: str) -> "SQLQuery":
        """Añade condición HAVING (raw)."""
        if not isinstance(condicion_raw, str) or not condicion_raw.strip():
            raise ValueError("having requiere una condición (str no vacío).")
        self._having_raw.append(condicion_raw.strip())
        return self

    def having_param(self, condicion: str, *params: Any) -> "SQLQuery":
        """
        HAVING con parámetros posicionales.
        """
        if not isinstance(condicion, str) or not condicion.strip():
            raise ValueError("having_param requiere una condición (str no vacío).")
        self._having_params.append((condicion.strip(), tuple(params)))
        return self

    def join(self, tipo: str, tabla: str, on: str) -> "SQLQuery":
        """
        Añade un JOIN del tipo especificado (raw): INNER, LEFT, RIGHT, FULL, CROSS, etc.
        """
        for arg, name in ((tipo, "tipo"), (tabla, "tabla"), (on, "on")):
            if not isinstance(arg, str) or not arg.strip():
                raise ValueError(f"{name} de join debe ser str no vacío.")
        self._joins.append((tipo.strip().upper(), tabla.strip(), on.strip()))
        return self

    # Atajos comunes:
    def inner_join(self, tabla: str, on: str) -> "SQLQuery":
        return self.join("INNER", tabla, on)

    def left_join(self, tabla: str, on: str) -> "SQLQuery":
        return self.join("LEFT", tabla, on)

    def right_join(self, tabla: str, on: str) -> "SQLQuery":
        return self.join("RIGHT", tabla, on)

    def full_join(self, tabla: str, on: str) -> "SQLQuery":
        return self.join("FULL", tabla, on)

    def limit(self, n: int) -> "SQLQuery":
        if not isinstance(n, int) or n < 0:
            raise ValueError("limit requiere un entero >= 0.")
        self._limit = n
        return self

    def offset(self, n: int) -> "SQLQuery":
        if not isinstance(n, int) or n < 0:
            raise ValueError("offset requiere un entero >= 0.")
        self._offset = n
        return self

    # ---------------- Compilación ----------------

    def construir(self) -> str:
        """
        Compila y devuelve el SQL como string (con los valores inline si usaste where()).
        Nota: Si usaste where_param/having_param, el SQL contendrá placeholders '?'
        y deberías usar .compilar() para obtener también los parámetros.
        """
        return self.compilar().sql

    def compilar(self) -> SQLCompilado:
        """
        Compila y devuelve SQL + parámetros posicionales (para prepared statements).
        """
        if not self._from:
            raise ValueError("Falta FROM: llama a .from_table('mi_tabla').")

        select_sql = ", ".join(self._selects) if self._selects else "*"
        partes: List[str] = [f"SELECT {select_sql}", f"FROM {self._from}"]

        # JOINs
        for tipo, tabla, on in self._joins:
            partes.append(f"{tipo} JOIN {tabla} ON {on}")

        params: List[Any] = []

        # WHERE
        where_clauses: List[str] = []
        where_clauses.extend(self._wheres_raw)
        for cond, p in self._wheres_param:
            where_clauses.append(cond)
            params.extend(p)

        if where_clauses:
            partes.append("WHERE " + " AND ".join(where_clauses))

        # GROUP BY
        if self._group_bys:
            partes.append("GROUP BY " + ", ".join(self._group_bys))

        # HAVING
        having_clauses: List[str] = []
        having_clauses.extend(self._having_raw)
        for cond, p in self._having_params:
            having_clauses.append(cond)
            params.extend(p)
        if having_clauses:
            partes.append("HAVING " + " AND ".join(having_clauses))

        # ORDER BY
        if self._order_bys:
            partes.append("ORDER BY " + ", ".join(self._order_bys))

        # LIMIT / OFFSET
        if self._limit is not None:
            partes.append(f"LIMIT {self._limit}")
        if self._offset is not None:
            partes.append(f"OFFSET {self._offset}")

        sql = " ".join(partes)
        return SQLCompilado(sql=sql, params=tuple(params))


# --------------------- Ejemplos de uso ---------------------
if __name__ == "__main__":
    # Ejemplo del enunciado:
    # SQLQuery().select("id", "nombre").from_table("estudiantes").where("edad > 18").where("matriculados = true").order_by("id").construir()
    q1 = (
        SQLQuery()
        .select("id", "nombre")
        .from_table("estudiantes")
        .where("edad > 18")
        .where("matriculados = true")
        .order_by("id")
    )
    print("Consulta 1:")
    print(q1.construir())
    # -> SELECT id, nombre FROM estudiantes WHERE edad > 18 AND matriculados = true ORDER BY id

    # Ejemplo con parámetros (recomendado para seguridad/performance):
    q2 = (
        SQLQuery()
        .select("id", "nombre")
        .from_table("estudiantes")
        .where_param("edad > ?", 18)
        .where_param("matriculados = ?", True)
        .order_by("id DESC")
        .limit(10)
        .offset(20)
    )
    sql2 = q2.compilar()
    print("\nConsulta 2 (con parámetros):")
    print(sql2.sql)      # SELECT id, nombre FROM estudiantes WHERE edad > ? AND matriculados = ? ORDER BY id DESC LIMIT 10 OFFSET 20
    print(sql2.params)   # (18, True)

    # Ejemplo con JOIN y GROUP BY/HAVING:
    q3 = (
        SQLQuery()
        .select("e.id", "e.nombre", "COUNT(m.id) AS materias")
        .from_table("estudiantes e")
        .left_join("matriculas m", "m.estudiante_id = e.id")
        .group_by("e.id", "e.nombre")
        .having("COUNT(m.id) > 3")
        .order_by("materias DESC", "e.id ASC")
    )
    print("\nConsulta 3 (JOIN + GROUP BY/HAVING):")
    print(q3.construir())