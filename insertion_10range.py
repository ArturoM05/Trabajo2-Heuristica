"""
Búsqueda Local Insertion con rango 10 para NWJSSP
Estrategia: Insertar un trabajo en una posición diferente,
            con distancia máxima de 10 entre posición origen y destino
Mejora: First Improvement (acepta el primer vecino que mejore la solución actual)
"""

import time
from constructive import ConstructiveAlgorithm
from two_opt import evaluate_sequence


class InsertionRangeSearch:
    """
    Para cada posición i, extrae el trabajo e intenta insertarlo en j dentro de [i-10, i+10].
    First Improvement: acepta la primera inserción que mejore y reinicia el barrido.
    Repite hasta no haber mejora en un barrido completo. Nunca empeora la solución.
    """

    def __init__(self, n, m, operations, release_dates, max_range=10):
        self.n = n
        self.m = m
        self.operations = operations
        self.release_dates = release_dates
        self.max_range = max_range
        self._algo = ConstructiveAlgorithm(n, m, operations, release_dates)

    def _apply_insertion(self, sequence, i, j):
        """Extrae elemento en i e inserta en la posición j (antes del reajuste por extracción)."""
        new_seq = sequence[:]
        job = new_seq.pop(i)
        insert_at = j if j <= i else j - 1
        new_seq.insert(insert_at, job)
        return new_seq

    def solve(self, initial_solution=None, initial_flow_time=None):
        start_computation = time.time()

        if initial_solution is None:
            initial_solution, initial_flow_time, _ = self._algo.solve()

        job_sequence = sorted(range(self.n), key=lambda j: initial_solution[j])
        current_flow, current_starts = evaluate_sequence(job_sequence, self._algo)

        improved = True
        iterations = 0
        while improved and time.time() - start_computation < 3600 and iterations < 1000:  
            improved = False
            seq_len = len(job_sequence)

            for i in range(seq_len):
                if time.time() - start_computation >= 3600:
                    break
                j_min = max(0, i - self.max_range)
                j_max = min(seq_len - 1, i + self.max_range)

                for j in range(j_min, j_max + 1):
                    if time.time() - start_computation >= 3600:
                        break
                    if j == i:
                        continue

                    neighbor = self._apply_insertion(job_sequence, i, j)
                    neighbor_flow, neighbor_starts = evaluate_sequence(neighbor, self._algo)

                    # First improvement: aceptar la primera mejora
                    if neighbor_flow < current_flow:
                        job_sequence = neighbor
                        current_flow = neighbor_flow
                        current_starts = neighbor_starts
                        improved = True
                        iterations += 1
                        break

                if improved:
                    break

        end_computation = time.time()
        return current_starts, current_flow, (end_computation - start_computation) * 1000 #, iterations