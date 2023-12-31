from abc import abstractmethod, abstractproperty
from enum import Enum
from typing import Protocol

import numpy as np
from qulacs import QuantumCircuit, QuantumGateMatrix
from qulacs.gate import DenseMatrix

from ..circuit import Noise
from ..hamiltonian import HamiltonianProtocol


class AnsatzType(Enum):
    DIRECT = 1
    INDIRECT_ISING = 2
    INDIRECT_XY = 3
    INDIRECT_HEISENBERG = 4
    CUSTOM = 5


class AnsatzProtocol(Protocol):
    n_qubits: int
    depth: int
    noise: Noise

    @abstractproperty
    def ansatz_type(self) -> AnsatzType:
        ...

    @abstractmethod
    def create_ansatz(self, params: list) -> QuantumCircuit:
        ...


class AnsatzWithTimeEvolutionGate(AnsatzProtocol):
    _hamiltonian: HamiltonianProtocol

    def create_time_evolution_gate(self, t_after, t_before) -> QuantumGateMatrix:
        diag, eigen_vecs = self._hamiltonian.eigh
        time_evol_op = np.dot(
            np.dot(eigen_vecs, np.diag(np.exp(-1j * (t_after - t_before) * diag))),
            eigen_vecs.T.conj(),
        )
        return DenseMatrix([i for i in range(self.n_qubits)], time_evol_op)
