"""
Búsqueda Local Swap con rango 10 para NWJSSP
Estrategia: Intercambio de un trabajo con otro a distancia máxima 10 en la secuencia
Mejora: Best Improvement (evalúa todos los vecinos válidos y elige el mejor)
"""

import time
from constructive import ConstructiveAlgorithm
from two_opt import evaluate_sequence


class SwapRangeSearch:
    """
    Para cada posición i, evalúa intercambiar con cualquier j en [i+1, i+10].
    Best Improvement: aplica el swap con mayor reducción de flow time.
    Repite hasta no haber mejora. Nunca empeora la solución.
    """

    def __init__(self, n, m, operations, release_dates, max_range=10):
        self.n = n
        self.m = m
        self.operations = operations
        self.release_dates = release_dates
        self.max_range = max_range
        self._algo = ConstructiveAlgorithm(n, m, operations, release_dates)

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
            best_delta = 0
            best_i = -1
            best_j = -1
            seq_len = len(job_sequence)

            for i in range(seq_len - 1):
                if time.time() - start_computation >= 3600:
                    break
                j_max = min(i + self.max_range, seq_len - 1)
                for j in range(i + 1, j_max + 1):
                    if time.time() - start_computation >= 3600:
                        break

                    neighbor = job_sequence[:]
                    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                    neighbor_flow, _ = evaluate_sequence(neighbor, self._algo)
                    delta = current_flow - neighbor_flow
                    if delta > best_delta:
                        best_delta = delta
                        best_i = i
                        best_j = j

            if best_i >= 0:
                job_sequence[best_i], job_sequence[best_j] = (
                    job_sequence[best_j],
                    job_sequence[best_i],
                )
                current_flow, current_starts = evaluate_sequence(job_sequence, self._algo)
                improved = True
            iterations += 1 
        end_computation = time.time()
        return current_starts, current_flow, (end_computation - start_computation) * 1000 #, iterations