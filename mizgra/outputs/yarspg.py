from __future__ import annotations

from .output_format import OutputFormat


# YARS-PG output format
class YARSPG(OutputFormat):
    def print_node(self, node_name: str, label: str, attributes: dict[str] = {}) -> None:
        # (hiddenL2 {"Text-Proper"}["articleid": "HIDDEN", "articleext": ".miz", "position": "17\5", "notation": "m.1.2", "uuid": "cac5245f-1eb1-566d-a3c2-001ac90a9d83"])

        if not attributes:
            print(f"({node_name} {{\"{label}\"}})")
        else:
            # Replace \ with \\ and " with \" in attribute values using chr().
            attribute_str: str = ", ".join(
                [f'"{key}": "{value.replace(chr(92), chr(92) * 2).replace(chr(34), chr(92) + chr(34))}"' for key, value
                 in attributes.items()])
            print(f"({node_name} {{\"{label}\"}}[{attribute_str}])")

    def print_relation(self, source_node: str, relation_name: str, target_node: str,
                       attributes: dict[str, str] = {}) -> None:
        # (xboole1L9566)-({"RELATION"})->(xboole1L9556)

        if not attributes:
            print(f"({source_node})-({{\"{relation_name}\"}})->({target_node})")
        else:
            attribute_str: str = ", ".join([f'"{key}": "{value}"' for key, value in attributes.items()])
            print(f"({source_node})-({{\"{relation_name}\"}}[{attribute_str}])->({target_node})")

    def print_filename(self, filename: str) -> None:
        print(f"# START OF {filename}")

    def print_header(self) -> None:
        print("# begin file")

    def print_footer(self) -> None:
        print("# end file")
