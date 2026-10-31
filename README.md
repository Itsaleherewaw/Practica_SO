# Práctica 1 – Sistema de procesamiento de documentos con hilos

**Materia:** Sistemas Operativos · **Rama:** `Práctica1`

## Descripción

Cuatro trabajadores concurrentes (hilos de `threading.Thread`) procesan 24 documentos
que están en una cola compartida (`queue.Queue`). Cada documento tiene un
identificador y un tamaño simulado de 1 a 5. Cada documento se procesa exactamente
una vez, y un diccionario compartido protegido con `threading.Lock` cuenta cuántos
documentos completó cada trabajador.

**Cómo ejecutarlo:** `python practica.py`

## Trabajadores concurrentes

- Joel Corina
- Ernesto Colmena
- Camila Vargas
- Pablo Medina

## Contenido del repositorio

| Archivo | Descripción |
| --- | --- |
| `practica.py` | Código de la práctica |
| `asignacion.txt` | Asignación de los 24 documentos (documento, trabajador, tamaño) |
| `capturas/` | 4 capturas de la ejecución |
| `README.md` | Este documento |

## Interpretación de cada trabajador

Cada trabajador repite el mismo ciclo: intenta retirar un documento de la cola con
`get_nowait()`, simula el procesamiento con `time.sleep(tamaño × 0.1)` y actualiza el
resumen dentro de `with lock:`. Cuando la cola está vacía, captura `queue.Empty` y
termina.

El reparto es dinámico: quien termina primero toma el siguiente documento. Por eso
la cantidad de documentos por trabajador no es igual y cambia en cada ejecución.

| Trabajador | Documentos | Tamaño total | IDs asignados |
| --- | --- | --- | --- |
| Joel Corina | 6 | 21 | 1, 6, 15, 21, 22, 23 |
| Ernesto Colmena | 7 | 19 | 2, 8, 10, 13, 17, 19, 24 |
| Camila Vargas | 7 | 17 | 3, 5, 9, 12, 14, 16, 20 |
| Pablo Medina | 4 | 17 | 4, 7, 11, 18 |
| **Total** | **24** | | |

**Lectura de los resultados:**

- **Pablo Medina** procesó solo 4 documentos, pero con tamaño total 17: le tocaron
  documentos grandes, que tardan más, y por eso volvió menos veces a la cola.
- **Ernesto Colmena y Camila Vargas** procesaron 7 documentos cada uno con tamaños
  totales menores: en promedio sus documentos eran más pequeños, así que quedaban
  libres más rápido y tomaban más trabajo.
- **Joel Corina** quedó en un punto intermedio (6 documentos, tamaño 21).
- El tiempo de trabajo quedó parecido entre todos; lo que se equilibra es el tiempo
  ocupado, no la cantidad de documentos.

> **Importante:** estos números son de una ejecución de ejemplo. Los tamaños son
> aleatorios, así que antes de entregar reemplaza esta tabla y la lectura de arriba
> con los datos de **tu** ejecución (los mismos de tus capturas).

## Verificaciones

1. La suma de documentos por trabajador es 24. 
2. Cada ID aparece una sola vez (se comprueba con el registro detallado). 
3. Los cuatro hilos finalizan sin quedarse bloqueados. 

## Preguntas

### 1. ¿Por qué `queue.Queue` es apropiada para compartir trabajos?

Porque es segura para hilos (*thread-safe*): sus operaciones `put()` y `get()` ya
están sincronizadas internamente. Dos trabajadores no pueden sacar el mismo
documento ni se pierde ninguno, sin necesidad de agregar un lock para la cola.
También permite usar `get_nowait()` con `queue.Empty` para que cada hilo termine
de forma controlada, en lugar de `empty()`, que puede quedar desactualizado entre
la comprobación y la lectura.

### 2. ¿Qué protege `Lock` y qué pasaría si se actualizara el resumen sin él?

Protege la sección crítica: la actualización de los diccionarios compartidos
(`resultados`, `tamanos`) y del registro. Una instrucción como
`resultados[nombre] += 1` no es atómica: son tres pasos (leer, sumar y guardar).
Sin lock, dos hilos podrían leer el mismo valor y guardar el mismo resultado, y
una actualización se perdería. Sería una condición de carrera: el total saldría
menor a 24 aunque todos los documentos se hayan procesado, y el resultado
cambiaría de una ejecución a otra.

### 3. ¿Qué cambiarías si cada documento tuviera que guardarse en un archivo real?

- **Un archivo por documento** (por ejemplo `doc_07.txt`): cada hilo escribe en un
  archivo distinto, así que no se necesita lock para escribir.
- **Un solo archivo compartido:** la escritura debe ir dentro de un lock (o usar un
  único hilo escritor) para que las líneas no se mezclen.
- Manejar errores de entrada/salida con `try/except` y `with open(...)`, para no
  perder documentos si falla una escritura.

## Reto adicional

| Versión | Tiempo |
| --- | --- |
| Secuencial | 7.41 s |
| 4 hilos | 2.10 s |

> Reemplaza con los tiempos de tu ejecución.

La mejora es grande porque el trabajo simulado es `time.sleep()`: mientras un hilo
espera, los otros avanzan. En un caso real de cálculo intensivo en Python puro, el
GIL de CPython limitaría el paralelismo y la diferencia sería mucho menor. Además,
la rapidez no es el único criterio: también importan la exactitud (24 de 24 sin
repetidos) y la coordinación entre hilos.

El programa también acumula el tamaño total de documentos que procesó cada
trabajador (columna "Tamaño total").
