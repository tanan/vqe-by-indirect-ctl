import datetime
import sys
import time

import yaml
from qulacs import QuantumCircuit, QuantumState
from scipy.optimize import minimize

from constraints import create_time_constraints
from core.ansatz import XYAnsatz
from core.database.bigquery import BigQueryClient, insert_job_result
from core.database.schema import Job, JobFactory
from core.database.sqlite import DBClient, insert_job
from core.hamiltonian import XYHamiltonian
from hamiltonian import create_ising_hamiltonian
from params import create_init_params

iteration = 0
param_history = []
cost_history = []
iter_history = []

def reset():
    global param_history
    global cost_history
    global iter_history
    global iteration
    param_history = []
    cost_history = []
    iter_history = []
    iteration = 0

def record(x):
    global param_history
    global cost_history
    global iter_history
    param_history.append(x)
    cost_history.append(cost(x))
    iter_history.append(iteration)

def record_database(job: Job, is_bq_import: bool, gcp_project_id: str) -> None:
    client = DBClient("data/job_results.sqlite3")
    insert_job(client, job)
    if is_bq_import:
        bqClient = BigQueryClient(gcp_project_id)
        insert_job_result(bqClient, job)
 
def init_ansatz(n_qubits: int, depth: int, gate_type: str, noise: dict):
    if gate_type == "direct":
        ...
        # ansatz = HardwareEfficientAnsatz(n_qubits, depth, noise)
    elif gate_type == "indirect_xy":
        coef = ([0.5] * n_qubits, [1.0] * n_qubits)
        hamiltonian = XYHamiltonian(n_qubits, coef, gamma=0)
        ansatz = XYAnsatz(n_qubits, depth, noise, hamiltonian)
    return ansatz

def cost(n_qubits, ansatz, observable, params):
    global iteration
    iteration += 1
    state = QuantumState(n_qubits)
    circuit = QuantumCircuit(n_qubits)
    circuit = ansatz.create_ansatz(params)
    circuit.update_quantum_state(state)
    return observable.get_expectation_value(state)

def run(config):
    ## performance measurement
    start_time = time.perf_counter()
    now = datetime.datetime.now()

    n_qubits = config["n_qubits"]
    ## init qulacs hamiltonian
    observable = create_ising_hamiltonian(n_qubits)

    ## init ansatz instance
    ansatz = init_ansatz(n_qubits, config["depth"], config["gate"]["type"], config["gate"]["noise"])

    ## randomize and create constraints
    init_params, _ = create_init_params(n_qubits, config)
    record(init_params)

    def cost_fn(params):
        return cost(n_qubits, ansatz, observable, params)

    ## calculation
    options = {"maxiter": 1000}
    opt = minimize(
        cost_fn, init_params, method=config["optimizer"]["method"], options=options, callback=record
    )

    end_time = time.perf_counter()

    print(cost_history)
    # record to database
    job = JobFactory(config).create(
        now, start_time, end_time, cost_history, param_history, iter_history
    )
    record_database(job, config["gcp"]["bigquery"]["import"], config["gcp"]["project"]["id"])

if __name__ == "__main__":
    args = sys.argv
    path = args[1]
    with open(path, "r") as f:
        config = yaml.safe_load(f)
        for k in range(config["iter"]):
            run(config)
            reset()