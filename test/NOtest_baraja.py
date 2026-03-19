# import unittest
# from codigo_pruebas import Baraja  # asumiendo que tu clase está en baraja.py

# class TestBaraja(unittest.TestCase):

#     def test_barajar_y_repartir(self):
#         b = Baraja()
#         original = b.cartas().copy()

#         # Barajar
#         b.barajar()
#         barajada = b.cartas()

#         # Comprobamos que la baraja cambia al barajar
#         self.assertNotEqual(original, barajada, "La baraja debería cambiar al barajar")

#         # Repartimos 5 cartas
#         mano = b.repartir(5)

#         # La mano tiene 5 cartas
#         self.assertEqual(len(mano), 5, "Deben repartirse exactamente 5 cartas")

#         # La baraja ahora tiene N-5 cartas
#         self.assertEqual(len(b.cartas()), len(original) - 5, "La baraja debe reducirse tras repartir")

#         # Ninguna carta de la mano sigue en la baraja
#         for carta in mano:
#             self.assertNotIn(carta, b.cartas(), "Las cartas repartidas no deben seguir en la baraja")


# if __name__ == "__main__":
#     unittest.main()
# -*- coding: utf-8 -*-
# import unittest
# from codigo_pruebas import Baraja  # Asegúrate de que la clase esté en baraja.py

# class TestGestionCartasBaraja(unittest.TestCase):

#     def setUp(self):
#         # Nueva baraja para cada test (aislamiento)
#         self.b = Baraja()
#         self.inicial = self.b.cartas()
#         self.n0 = len(self.inicial)

#     # ---------------------------
#     #         AÑADIR
#     # ---------------------------
#     def test_añadir_sin_posicion_agrega_al_final(self):
#         carta_nueva = ("♦", "X")  # carta "no estándar" para evitar duplicados
#         ok = self.b.gestionar_carta("añadir", carta=carta_nueva)

#         self.assertTrue(ok, "La operación de añadir debería devolver True")
#         cartas = self.b.cartas()
#         self.assertEqual(len(cartas), self.n0 + 1, "La baraja debe aumentar en 1 carta")
#         self.assertEqual(cartas[-1], carta_nueva, "Sin posición, la carta debería ir al final")
#         self.assertIn(carta_nueva, cartas, "La carta añadida debe estar en la baraja")

#     def test_añadir_en_posicion_cero(self):
#         carta_nueva = ("♣", "X")
#         ok = self.b.gestionar_carta("añadir", carta=carta_nueva, posicion=0)

#         self.assertTrue(ok, "Añadir en posición específica debe devolver True")
#         cartas = self.b.cartas()
#         self.assertEqual(len(cartas), self.n0 + 1, "La baraja debe aumentar en 1 carta")
#         self.assertEqual(cartas[0], carta_nueva, "La carta debe insertarse en la posición 0")

#     # ---------------------------
#     #        ELIMINAR
#     # ---------------------------
#     def test_eliminar_existente_retorna_true_y_reduce_tamaño(self):
#         carta_existente = self.inicial[10]  # una carta que sabemos que existe
#         ok = self.b.gestionar_carta("eliminar", carta=carta_existente)

#         self.assertTrue(ok, "Eliminar una carta existente debe devolver True")
#         cartas = self.b.cartas()
#         self.assertEqual(len(cartas), self.n0 - 1, "La baraja debe reducirse en 1 al eliminar")
#         self.assertNotIn(carta_existente, cartas, "La carta eliminada no debe permanecer en la baraja")

#     def test_eliminar_inexistente_retorna_false_y_no_cambia_tamaño(self):
#         carta_inexistente = ("♠", "ZZ")  # No forma parte de la baraja estándar
#         ok = self.b.gestionar_carta("eliminar", carta=carta_inexistente)

#         self.assertFalse(ok, "Eliminar una carta inexistente debe devolver False")
#         self.assertEqual(len(self.b.cartas()), self.n0, "La baraja no debe cambiar de tamaño")

#     # ---------------------------
#     #        MODIFICAR
#     # ---------------------------
#     def test_modificar_en_misma_posicion(self):
#         carta_original = self.inicial[5]
#         pos_original = 5
#         carta_nueva = ("♥", "X")

#         ok = self.b.gestionar_carta("modificar", carta=carta_original, nueva_carta=carta_nueva)

#         self.assertTrue(ok, "Modificar una carta existente debe devolver True")
#         cartas = self.b.cartas()
#         self.assertEqual(len(cartas), self.n0, "Modificar no debe cambiar el tamaño total de la baraja")
#         self.assertNotIn(carta_original, cartas, "La carta original no debe permanecer tras modificar")
#         self.assertIn(carta_nueva, cartas, "La nueva carta debe estar en la baraja")
#         self.assertEqual(
#             cartas.index(carta_nueva), pos_original,
#             "Sin posición explícita, la carta modificada debe mantenerse en su índice original"
#         )

#     def test_modificar_moviendo_a_otra_posicion(self):
#         carta_original = self.inicial[7]
#         carta_nueva = ("♠", "X")
#         nueva_posicion = 3

#         ok = self.b.gestionar_carta("modificar", carta=carta_original, nueva_carta=carta_nueva, posicion=nueva_posicion)

#         self.assertTrue(ok, "Modificar y mover debe devolver True")
#         cartas = self.b.cartas()
#         self.assertEqual(len(cartas), self.n0, "Modificar no cambia el tamaño total")
#         self.assertNotIn(carta_original, cartas, "La carta original no debe permanecer en la baraja")
#         self.assertIn(carta_nueva, cartas, "La carta nueva debe estar en la baraja")
#         self.assertEqual(
#             cartas.index(carta_nueva), nueva_posicion,
#             "La carta nueva debe quedar exactamente en la posición indicada"
#         )

# if __name__ == "__main__":
#     unittest.main(verbosity=4)
from codigo_pruebas import Baraja, CARTAS
from pytest import fixture

@fixture
def baraja():
    baraja = Baraja()
    return baraja

@fixture
def baraja_mezclada():
    baraja = Baraja()
    ~baraja
    return baraja
    
def test_bajara(baraja):
    assert CARTAS == abs(baraja)
    ~baraja
    assert CARTAS != abs(baraja)
    assert len(baraja) == 54
    
def test_primera_y_ultima_cartas(baraja):
    baraja_cartas = abs(baraja)
    primera_carta = baraja_cartas[0]
    ultima_carta = baraja_cartas[-1]
    assert primera_carta == CARTAS[0]
    assert ultima_carta == CARTAS[-1]
    
def test_elegir_carta(baraja):
    indice_elegido = 12
    carta_elegida = CARTAS[indice_elegido]
    assert carta_elegida == baraja[indice_elegido]

def test_cambiar_carta(baraja):
    indice_elegido = 20
    carta_a_introducir = CARTAS[0]
    baraja[indice_elegido] = carta_a_introducir
    assert baraja[indice_elegido] == carta_a_introducir
    
def test_eliminar_carta(baraja_mezclada):
    indice_elegido = 4
    carta_eliminada = baraja_mezclada[indice_elegido]
    del baraja_mezclada[indice_elegido]
    mi_baraja = abs(baraja_mezclada)
    assert carta_eliminada not in mi_baraja
    
def test_repartir_cartas(baraja_mezclada):
    mano = baraja_mezclada[:6]
    assert len(mano) == 6
    assert len(baraja_mezclada) == 54
 