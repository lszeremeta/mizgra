from __future__ import annotations

from .output_format import OutputFormat


# GraphML output format
class GraphML(OutputFormat):
    NODE_KEYS = ('MMLId', 'absoluteconstrMMLId', 'absoluteorigconstrMMLId', 'absoluteorigpatternMMLId', 'absolutenr',
                 'absolutepatternMMLId', 'amount', 'antonymic', 'arity', 'articleext', 'articleid', 'bracketed',
                 'constr', 'constrnr', 'description', 'endposition', 'formatdes', 'formatnr', 'freevarnr', 'href',
                 'idnr', 'inscription', 'kind', 'labelnr', 'labels', 'leftargsbracketed', 'leftargscount', 'nonocc',
                 'notation', 'nr', 'number', 'occurs', 'origconstrnr', 'originalnr', 'origin', 'originnr',
                 'origpatternnr', 'patternnr', 'position', 'property', 'rightargsbracketed', 'serialnr', 'shape',
                 'sort', 'spelling', 'superfluous', 'uuid', 'value', 'varidkind', 'varintro', 'varnr', 'xmlid')

    EDGE_KEYS = ('lang', 'label')

    def print_node(self, node_name: str, label: str, attributes: dict[str, str] = {}) -> None:
        attribute_str: str = "".join(
            [f'<data key="{key}"><![CDATA[{value}]]></data>\n' for key, value in attributes.items()])
        print(f'<node id="{node_name}" labels=":{label}">\n<data key="labels">:{label}</data>\n{attribute_str}</node>')

    def print_relation(self, source_node: str, relation_name: str, target_node: str,
                       attributes: dict[str, str] = {}) -> None:
        attribute_str: str = "".join(
            [f'<data key="{key}"><![CDATA[{value}]]></data>\n' for key, value in attributes.items()])
        print(f'''<edge source="{source_node}" target="{target_node}" label="{relation_name}">
<data key="label">{relation_name}</data>\n{attribute_str}</edge>''')

    def print_filename(self, filename: str) -> None:
        print(f"<!-- START OF {filename} -->")

    def print_header(self) -> None:
        node_keys = "\n".join(
            f'<key id="{node_key}" for="node" attr.name="{node_key}"/>' for node_key in self.NODE_KEYS)
        edge_keys = "\n".join(
            f'<key id="{edge_key}" for="edge" attr.name="{edge_key}"/>' for edge_key in self.EDGE_KEYS)

        print(f'''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
{node_keys}
{edge_keys}
<graph id="G" edgedefault="directed">''')

    def print_footer(self) -> None:
        print('</graph>\n</graphml>')
