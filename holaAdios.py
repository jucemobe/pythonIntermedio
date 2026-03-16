from multiprocessing import Process, Pipe
import time
 
def proceso_a(conn):
    print("[A] Enviando: hola")
    conn.send("hola")
 
    respuesta = conn.recv()
    print(f"[A] Recibido: {respuesta}")
 
    conn.close()
 
 
def proceso_b(conn):
    mensaje = conn.recv()
    print(f"[B] Recibido: {mensaje}")
 
    if mensaje == "hola":
        print("[B] Enviando: adios")
        conn.send("adios")
 
    conn.close()
 
 
if __name__ == "__main__":
    # Creamos un Pipe con dos extremos
    conn_a, conn_b = Pipe()
 
    # Creamos los procesos
    p1 = Process(target=proceso_a, args=(conn_a,))
    p2 = Process(target=proceso_b, args=(conn_b,))
 
    # Iniciamos los procesos
    p1.start()
    p2.start()
 
    # Esperamos a que terminen
    p1.join()
    p2.join()
 
    print("Comunicación finalizada correctamente.")
 