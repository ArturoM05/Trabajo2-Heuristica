"""
Búsqueda Local 2-opt para NWJSSP
Estrategia: Intercambio de 2 trabajos consecutivos en la secuencia
Mejora: Best Improvement (evalúa todos los vecinos y elige el mejor)

Evaluación de secuencias: usa la misma lógica del algoritmo constructivo
(find_earliest_start_time) para garantizar que cualquier movimiento aceptado
produce una solución estrictamente mejor que la actual.
"""

import time
from constructive import ConstructiveAlgorithm
from read_instances import calculate_flow_time


def evaluate_sequence(job_sequence, constructive_algo):
    """
    Evalúa el flow time de una secuencia usando la lógica del constructivo.
    Usa find_earliest_start_time para permitir overlap entre trabajos en
    máquinas distintas, igual que el constructivo original.

    Args:
        job_sequence: lista de job_ids en el orden a programar
        constructive_algo: instancia de ConstructiveAlgorithm

    Returns:
        flow_time: suma de tiempos de completación
        job_start_times: tiempos de inicio resultantes
    """
    job_start_times = [0] * constructive_algo.n
    machine_schedule = {}

    for job_id in job_sequence:
        start_time = constructive_algo.find_earliest_start_time(job_id, machine_schedule)
        job_start_times[job_id] = start_time
        current_time = start_time
        for machine, processing_time in constructive_algo.operations[job_id]:
            if machine not in machine_schedule:
                machine_schedule[machine] = []
            machine_schedule[machine].append(
                (current_time, current_time + processing_time, job_id)
            )
            current_time += processing_time

    flow_time, _ = calculate_flow_time(
        job_start_times, constructive_algo.operations, constructive_algo.release_dates
    )
    return flow_time, job_start_times


class TwoOptSearch:
    """
    Búsqueda local 2-opt: intercambio de trabajos consecutivos.
    Best Improvement: evalúa todos los pares (i, i+1) y aplica el mejor.
    Repite hasta no haber mejora. Nunca empeora la solución.
    """

    def __init__(self, n, m, operations, release_dates):
        self.n = n
        self.m = m
        self.operations = operations
        self.release_dates = release_dates
        self._algo = ConstructiveAlgorithm(n, m, operations, release_dates)

    def solve(self, initial_solution=None, initial_flow_time=None):
        start_computation = time.time()

        if initial_solution is None:
            initial_solution, initial_flow_time, _ = self._algo.solve()

        job_sequence = sorted(range(self.n), key=lambda j: initial_solution[j])
        current_flow, current_starts = evaluate_sequence(job_sequence, self._algo)

        improved = True
        iterations = 0
        max_iterations = 1000  # Límite adicional de iteraciones para evitar loops en instancias grandes
        while improved and time.time() - start_computation < 3600 and iterations < max_iterations:  
            improved = False
            best_delta = 0
            best_i = -1

            for i in range(len(job_sequence) - 1):
                if time.time() - start_computation >= 3600:
                    break
                neighbor = job_sequence[:]
                neighbor[i], neighbor[i + 1] = neighbor[i + 1], neighbor[i]
                neighbor_flow, _ = evaluate_sequence(neighbor, self._algo)
                delta = current_flow - neighbor_flow
                if delta > best_delta:
                    best_delta = delta
                    best_i = i

            if best_i >= 0:
                job_sequence[best_i], job_sequence[best_i + 1] = (
                    job_sequence[best_i + 1],
                    job_sequence[best_i],
                )
                current_flow, current_starts = evaluate_sequence(job_sequence, self._algo)
                improved = True
                iterations += 1

        end_computation = time.time()
        return current_starts, current_flow, (end_computation - start_computation) * 1000 #, iterations