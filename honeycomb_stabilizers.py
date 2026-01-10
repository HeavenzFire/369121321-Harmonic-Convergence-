"""
Honeycomb Stabilizer Operators for Kitaev Quantum Error Correction Code

This module implements the stabilizer operators for the Kitaev honeycomb lattice code:
- Plaquette stabilizers (Z-type): Product of σ^z over qubits around each plaquette
- Vertex stabilizers (X-type): Product of σ^x over qubits incident to each vertex
"""

import networkx as nx
import numpy as np
from typing import List, Dict, Tuple, Set


class HexagonalLattice:
    """Represents a hexagonal lattice for honeycomb code."""

    def __init__(self, n_nodes: int, freq: float = 915e6):
        """
        Initialize hexagonal lattice.

        Args:
            n_nodes: Number of nodes (approximate, will create hexagonal grid)
            freq: Frequency for LoRa communication (default 915MHz)
        """
        self.freq = freq
        self.graph = self._generate_hexagonal_lattice(n_nodes)
        self.plaquettes = self._identify_plaquettes()
        self.vertices = list(self.graph.nodes())

    def _generate_hexagonal_lattice(self, n_nodes: int) -> nx.Graph:
        """Generate a hexagonal lattice graph with approximately n_nodes."""
        # Create a hexagonal grid
        # For simplicity, create a grid and connect hexagonally
        rows = int(np.sqrt(n_nodes / 2)) + 1
        cols = rows

        G = nx.Graph()

        # Add nodes in hexagonal pattern
        for r in range(rows):
            for c in range(cols):
                if r % 2 == 0:
                    node_id = r * cols + c
                else:
                    node_id = r * cols + c + cols // 2
                if node_id < n_nodes:
                    G.add_node(node_id, pos=(c, r))

        # Add edges for hexagonal connectivity
        for node in G.nodes():
            r, c = divmod(node, cols)
            # Connect to neighbors
            neighbors = [
                (r, c-1), (r, c+1),  # left, right
                (r-1, c), (r+1, c),  # up, down
            ]
            if r % 2 == 1:
                neighbors.extend([(r-1, c+1), (r+1, c+1)])  # diagonal for odd rows
            else:
                neighbors.extend([(r-1, c-1), (r+1, c-1)])  # diagonal for even rows

            for nr, nc in neighbors:
                if 0 <= nr < rows and 0 <= nc < cols:
                    neighbor_id = nr * cols + nc if nr % 2 == 0 else nr * cols + nc + cols // 2
                    if neighbor_id < n_nodes and neighbor_id != node:
                        G.add_edge(node, neighbor_id)

        return G

    def _identify_plaquettes(self) -> List[List[int]]:
        """Identify plaquettes (faces) in the hexagonal lattice."""
        plaquettes = []
        # For hexagonal lattice, each plaquette is a hexagon
        # Find cycles of length 6
        for cycle in nx.cycle_basis(self.graph):
            if len(cycle) == 6:
                plaquettes.append(cycle)
        return plaquettes


class HoneycombStabilizers:
    """Implements stabilizer operators for honeycomb code."""

    def __init__(self, lattice: HexagonalLattice):
        self.lattice = lattice
        self.plaquette_stabilizers = self._compute_plaquette_stabilizers()
        self.vertex_stabilizers = self._compute_vertex_stabilizers()

    def _compute_plaquette_stabilizers(self) -> Dict[int, List[Tuple[int, str]]]:
        """
        Compute plaquette stabilizers (Z-type).

        Returns:
            Dict mapping plaquette index to list of (qubit_index, operator) tuples
        """
        stabilizers = {}
        for idx, plaquette in enumerate(self.lattice.plaquettes):
            # For honeycomb code, plaquette stabilizer is product of Z on edges around plaquette
            # In our graph, edges are between nodes, so qubits are on edges
            stabilizer_ops = []
            for i in range(len(plaquette)):
                edge = (plaquette[i], plaquette[(i+1) % len(plaquette)])
                # Assume qubit index is based on edge
                qubit_idx = self._edge_to_qubit(edge)
                stabilizer_ops.append((qubit_idx, 'Z'))
            stabilizers[idx] = stabilizer_ops
        return stabilizers

    def _compute_vertex_stabilizers(self) -> Dict[int, List[Tuple[int, str]]]:
        """
        Compute vertex stabilizers (X-type).

        Returns:
            Dict mapping vertex index to list of (qubit_index, operator) tuples
        """
        stabilizers = {}
        for vertex in self.lattice.vertices:
            # Vertex stabilizer is product of X on edges incident to vertex
            stabilizer_ops = []
            for neighbor in self.lattice.graph.neighbors(vertex):
                edge = (min(vertex, neighbor), max(vertex, neighbor))
                qubit_idx = self._edge_to_qubit(edge)
                stabilizer_ops.append((qubit_idx, 'X'))
            stabilizers[vertex] = stabilizer_ops
        return stabilizers

    def _edge_to_qubit(self, edge: Tuple[int, int]) -> int:
        """Convert edge to qubit index."""
        # Simple mapping: sort edge and use as index
        return hash(tuple(sorted(edge))) % 10000  # Arbitrary large number

    def get_stabilizer(self, node_id: int) -> List[Tuple[int, str]]:
        """
        Get stabilizer for a given node (plaquette or vertex).

        Args:
            node_id: Node identifier

        Returns:
            List of (qubit_index, operator) tuples
        """
        if node_id in self.plaquette_stabilizers:
            return self.plaquette_stabilizers[node_id]
        elif node_id in self.vertex_stabilizers:
            return self.vertex_stabilizers[node_id]
        else:
            raise ValueError(f"No stabilizer found for node {node_id}")


def honeycomb_stabilizers(lattice: HexagonalLattice) -> HoneycombStabilizers:
    """
    Factory function to create honeycomb stabilizers.

    Args:
        lattice: Hexagonal lattice instance

    Returns:
        HoneycombStabilizers instance
    """
    return HoneycombStabilizers(lattice)