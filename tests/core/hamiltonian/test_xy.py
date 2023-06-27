import numpy as np
from core.hamiltonian import XYHamiltonian, HamiltonianModel

class TestXYHamiltonian:
    def test_create_hamiltonian(self) -> None:
        n_qubits = 3
        coef = ([1.0] * n_qubits, [1.0] * n_qubits)
        hamiltonian = XYHamiltonian(n_qubits, coef)
        ope = hamiltonian.create_hamiltonian()

    def test_type(self) -> None:
        n_qubits = 3
        coef = ([1.0] * n_qubits, [1.0] * n_qubits)
        hamiltonian = XYHamiltonian(n_qubits, coef)
        assert(hamiltonian.type == HamiltonianModel.XY)