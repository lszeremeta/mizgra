from __future__ import annotations

from abc import ABC, abstractmethod


# Abstract output class
class OutputFormat(ABC):

    @abstractmethod
    def print_node(self, node_name: str, label: str, attributes: dict[str, str] = {}) -> None:
        pass

    @abstractmethod
    def print_relation(self, source_node: str, relation_name: str, target_node: str,
                       attributes: dict[str, str] = {}) -> None:
        pass

    @abstractmethod
    def print_filename(self, filename: str) -> None:
        pass

    @abstractmethod
    def print_header(self) -> None:
        pass

    @abstractmethod
    def print_footer(self) -> None:
        pass
