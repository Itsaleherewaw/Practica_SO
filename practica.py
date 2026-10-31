import threading
import queue
import time
import random

NOMBRES = ["Joel Corina", "Ernesto Colmena", "Camila Vargas", "Pablo Medina"]
TOTAL_DOCUMENTOS = 24

trabajos = queue.Queue()
resultados = {n: 0 for n in NOMBRES}   # documentos procesados por trabajador
tamanos = {n: 0 for n in NOMBRES}      # tamaño total procesado por trabajador
registro = []                          # (id_documento, trabajador, tamaño)
lock = threading.Lock()

# ---------- esto es solo para los 24 documentos ----------
documentos = [(doc_id, random.randint(1, 5))
              for doc_id in range(1, TOTAL_DOCUMENTOS + 1)]
for doc in documentos:
    trabajos.put(doc)


def trabajador(nombre):
    """Retira documentos de la cola hasta que esté vacía."""
    while True:
        try:
            # get_nowait() no se queda esperando; si no hay nada lanza Empty.
            # No se usa empty() porque la cola puede cambiar entre la
            # comprobación y la lectura.
            doc_id, tamano = trabajos.get_nowait()
        except queue.Empty:
            break  # salida controlada del hilo

        time.sleep(tamano * 0.1)  # simula el procesamiento (fuera del lock)

        with lock:  # sección crítica: datos compartidos
            resultados[nombre] += 1
            tamanos[nombre] += tamano
            registro.append((doc_id, nombre, tamano))
            print(f"{nombre} procesó el documento {doc_id:02d} "
                  f"(tamaño {tamano})")


def procesar_secuencial():
    """Reto: mismo trabajo sin hilos, solo para comparar tiempos."""
    inicio = time.time()
    for _, tamano in documentos:
        time.sleep(tamano * 0.1)
    return time.time() - inicio


# ---------- Ejecución con 4 hilos ----------
print("=== Procesamiento con 4 hilos ===")
inicio = time.time()
hilos = [threading.Thread(target=trabajador, args=(n,)) for n in NOMBRES]
for h in hilos:
    h.start()
for h in hilos:
    h.join()
tiempo_hilos = time.time() - inicio

# ---------- Resumen por trabajador ----------
print("\n=== Resumen por trabajador ===")
for n in NOMBRES:
    print(f"{n}: {resultados[n]} documentos, tamaño total {tamanos[n]}")
total = sum(resultados.values())
print(f"\nTotal procesado: {total} de {TOTAL_DOCUMENTOS} documentos")

# ---------- Asignación de los 24 documentos ----------
print("\n=== Asignación de documentos ===")
with open("asignacion.txt", "w", encoding="utf-8") as archivo:
    archivo.write("documento,trabajador,tamano\n")
    for doc_id, nombre, tamano in sorted(registro):
        archivo.write(f"{doc_id},{nombre},{tamano}\n")
for n in NOMBRES:
    ids = sorted(d for d, t, _ in registro if t == n)
    print(f"{n}: {ids}")
print("(detalle guardado en asignacion.txt)")

# ---------- Verificaciones ----------
ids_procesados = [d for d, _, _ in registro]
print("\n=== Verificaciones ===")
print("1. Suma de documentos = 24:",
      "OK" if total == TOTAL_DOCUMENTOS else "FALLO")
print("2. Cada ID aparece una sola vez:",
      "OK" if len(set(ids_procesados)) == len(ids_procesados) == TOTAL_DOCUMENTOS
      else "FALLO")
print("3. Los 4 hilos terminaron:",
      "OK" if not any(h.is_alive() for h in hilos) else "FALLO")

tiempo_sec = procesar_secuencial()
print("\n=== Reto: comparación de tiempos ===")
print(f"Versión secuencial: {tiempo_sec:.2f} s")
print(f"Versión con 4 hilos: {tiempo_hilos:.2f} s")