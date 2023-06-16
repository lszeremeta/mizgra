"""Mizgra - Mizar to graph converter."""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import sys
import uuid
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse

import importlib_resources
from lxml import etree
from rdflib import Graph
from rdflib.term import Literal

import mizgra.config as config
from mizgra import __version__
from mizgra.outputs import GraphML, YARSPG
from . import resources


class Mizgra:
    """Mizgra class."""

    def __init__(self, cli_args):
        """Initializes Mizgra object.

        Args:
            cli_args (argparse.Namespace): Parsed CLI arguments.
        """
        self.output = self._get_output_format(cli_args.output)
        self.ESXMML = cli_args.ESXMML
        self.MMLLAR = cli_args.MMLLAR
        self.MMLLAR_filenames = self._read_filenames_from_mml_lar()
        self.show: set = set(cli_args.show)
        self.disable: set = set(cli_args.disable)

        self.__disabled_selected_to_show__ = self.disable - self.show

        if self.__disabled_selected_to_show__:
            # Remove it from disable
            self.disable = self.__disabled_selected_to_show__ - self.disable

        self.selected_outputs: list = sorted(self.show - self.disable)
        if cli_args.metadata is None:
            self.metadata = self._get_resource_filepath('metadata.xml')
        else:
            self.metadata = cli_args.metadata

        self.csv_validate = cli_args.csv_validate

        self.csv_data = self._load_csv_files(cli_args.csv)

        if cli_args.rdf is None:
            self.rdf = self._get_resource_filepath('rdf_data.nt')
        else:
            self.rdf = cli_args.rdf

        self.rdf_format = cli_args.rdf_format
        self.rdf_graph = Graph().parse(self.rdf, format=self.rdf_format)
        self.usages_rel_cache = {}
        self.broader_rel_cache = {}
        self.current_filename = ""
        self.current_doc = None
        self.current_node = ""
        self.local_references: dict[str] = {}

    @staticmethod
    def _create_node_name(filename: str, id: str) -> str:
        """Creates a node name based on the given filename and identifier.

        Args:
            filename (str): The filename.
            id (str): Xmlid attribute value or line number.

        Returns:
            str: The created node name.
        """
        return f"{filename}N{id}"

    @staticmethod
    def _create_filename_from_mmlid(mmlid: str) -> str:
        """Creates a filename from the given MML ID.

        Args:
            mmlid (str): The MML ID.

        Returns:
            str: The created filename.
        """
        return mmlid.split(':', 1)[0].lower()

    @staticmethod
    def parse_arguments():
        """Parses command-line arguments for the Mizgra.

        Returns:
            argparse.Namespace: The parsed arguments.
        """
        parser = argparse.ArgumentParser(
            description="""Converts Mizar ESX MML mathematical data to property graph formats - GraphML, YARS-PG.
                        Produce files ready to import to various graph databases, including Neo4j.
                        Supports external RDF data in various formats.
                        To save output to file, add `> /path/to/output.graphml` to the end of the command, e.g.:
                        mizgra /path/to/esx_mml /path/to/mml.lar -m /path/to/metadata.xml -c /path/to/CSVs -cv > mmlkg.graphml
                        Read more about the MMLKG project at https://mmlkg.uwb.edu.pl.""",
            add_help=False, prog='mizgra')
        informative = parser.add_argument_group('Informative arguments')
        informative.add_argument("-h", "--help", help='show this help message and exit', action="help")
        informative.add_argument("-v", "--version", help='show program version and exit', action="version",
                                 version=__version__)
        required = parser.add_argument_group('Required arguments')
        required.add_argument('ESXMML', type=str,
                              help='Path to the ESX MML files directory. You can download it from: https://github.com/arturkornilowicz/esx_files/archive/refs/heads/main.zip')
        required.add_argument('MMLLAR', type=str,
                              help='Path to the mml.lar file. You can download it from: https://github.com/arturkornilowicz/esx_files/archive/refs/heads/main.zip')
        output_preference = parser.add_argument_group('Output preference arguments')
        output_preference.add_argument('-o', '--output', type=str, default='graphml',
                                       help='Output format (graphml, yarspg); default: graphml')
        output_preference.add_argument('-s', '--show', type=str, nargs='+', choices=config.outputs_choices,
                                       default=config.outputs_choices - config.disabled_outputs,
                                       help='''Show only selected outputs; by default, all possible results are shown, excluding those that are disabled by default (local-ref-relations, usages-relations, and broader-relations; handled by CSV relations). To show disabled outputs, specify them directly with -s/--show option. It's recommended to use CSV relations.''')
        output_preference.add_argument('-d', '--disable', type=str, nargs='+', choices=config.outputs_choices,
                                       default=config.disabled_outputs,
                                       help='Disable selected outputs (local-ref-relations, usages-relations, and broader-relations are disabled by default; handled by CSV relations)')
        external = parser.add_argument_group('External data arguments')
        external.add_argument('-m', '--metadata', type=str,
                              help='Path to the metadata file. If not specified, metadata without dataset statistics will be included. You can generate a full metadata file using: https://github.com/domel/metadata_gen')
        external.add_argument('-c', '--csv', type=str, nargs='+',
                              help='Paths to the CSV files/directories with relations. You can generate it using: https://github.com/arturkornilowicz/csvrelgen')
        external.add_argument('-cv', '--csv-validate', action='store_true',
                              help='Validates CSV files by several checks before reading to minimize the possibility of CSV errors; turned off by default')
        external.add_argument('-r', '--rdf', type=str,
                              help='Path to the RDF data file; for URLs or files with not standard '
                                   'extensions may be needed to specify format using -rf')
        external.add_argument('-rf', '--rdf-format', type=str, choices=config.rdf_format_choices,
                              help='RDF data file format, specify if not detected automatically')
        return parser.parse_args()

    @staticmethod
    def _get_output_format(output_format: str):
        """Gets the output format object based on the given output format string.

        Args:
            output_format (str): The output format string (graphml, yarspg).

        Returns:
            object: The output format object.
        """
        if output_format == 'graphml':
            return GraphML()
        elif output_format == 'yarspg':
            return YARSPG()

    def _read_filenames_from_mml_lar(self) -> list[str]:
        """Reads filenames from the mml.lar file.

        Returns:
            list[str]: The list of filenames.
        """
        with open(self.MMLLAR, 'r') as f:
            return f.read().splitlines()

    @staticmethod
    def _get_resource_filepath(resource: str) -> str:
        """Gets the filepath of the given resource.

        Args:
            resource (str): The resource to get the filepath for.

        Returns:
            str: The filepath of the given resource.
        """
        return importlib_resources.files(resources).joinpath(resource)

    def _process_metadata_file(self, filepath: str):
        """Processes the metadata file.

        Args:
            filepath (str): The path to the metadata file.
        """
        metadata_doc = etree.parse(filepath)
        root = metadata_doc.getroot()

        # Get filename without extension
        metadata_file_name = os.path.basename(filepath).split('.')[0]

        # Print main metadata node
        self.output.print_node(metadata_file_name, "GraphMetadata")

        # Parse everything excluding the root element
        for element in root.iterchildren():
            # Replace CURRENT_DATE with current date when default metadata file is used
            if element.tag == '{http://purl.org/dc/terms/}date' and element.text == 'CURRENT_DATE':
                element.text = datetime.now().strftime('%Y-%m-%d')

            current_node_name = self._create_node_name(metadata_file_name, element.sourceline)
            # Get the element name without namespace
            current_element_name = etree.QName(element.tag).localname
            self.output.print_node(current_node_name, current_element_name, {'value': element.text})
            self.output.print_relation(metadata_file_name, "HAS", current_node_name)

    def _load_csv_files(self, csv_paths: list[str]) -> defaultdict(set):
        """Loads csv files from the given list of paths or directories. Only unique relations will be loaded. If a path is a directory, all .csv files within that directory will be loaded.

        Args:
            csv_paths (list[str]): The list of paths or directories to load csv files from.

        Returns:
            defaultdict(set): Data from csv files.
        """
        csv_data = defaultdict(set)

        if csv_paths:
            for path in csv_paths:
                # if the path is to a directory, find all the .csv files in the directory
                if os.path.isdir(path):
                    for filename in os.listdir(path):
                        if filename.endswith('.csv'):
                            file_path = os.path.join(path, filename)
                            self._read_csv_file(file_path, csv_data)
                # if the path is to a file, load the file
                elif os.path.isfile(path):
                    self._read_csv_file(path, csv_data)

            print(f"Loaded {len(csv_data)} relations from CSV files\033[K", file=sys.stderr)
        return csv_data

    def _read_csv_file(self, file_path: str, csv_data: defaultdict(set)):
        """Reads a single csv file and updates csv_data. CSV file format: source_file, source_xmlid, target_file, target_xmlid, relation.

        Args:
            file_path (str): The path to the csv file.
            csv_data (defaultdict(set)): Data from csv files to update.

        Raises:
            IOError: If an error occurs when opening the file.
            ValueError: If an error occurs when parsing the file.
        """
        try:
            with open(file_path, 'r') as csv_file:
                print(
                    f"{'Reading and validating' if self.csv_validate else 'Reading'}: {file_path}\033[K", end='\r',
                    file=sys.stderr)
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    source_file, source_xmlid, target_file, target_xmlid, relation = row

                    if self.csv_validate:
                        self._validate_csv_row(row)

                    source_node = self._create_node_name(source_file, source_xmlid)
                    target_node = self._create_node_name(target_file, target_xmlid)
                    csv_data[source_node].add((target_node, relation))

        except IOError as e:
            print(f"Error opening CSV file {file_path}: {e}\033[K", file=sys.stderr)
        except ValueError as e:
            print(f"Error parsing CSV file {file_path} at row {row}:\n{e}\033[K", file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            print("Interrupted by user. Exiting...\033[K", file=sys.stderr)
            sys.exit()
        except Exception as e:
            self.output.print_footer()
            print(f"Error while reading CSV files: {e}\033[K", file=sys.stderr)
            sys.exit(1)

    def _validate_csv_row(self, row: list[str]) -> bool:
        """Validates a row from a CSV file.

        Args:
            row (list[str]): The row to validate.

        Returns:
            bool: True if the row is valid, False otherwise.

        Raises:
            ValueError: If the row is invalid.
        """
        source_file, source_xmlid, target_file, target_xmlid, relation = row

        errors = []
        # check if all values are not empty or None
        if not all([source_file, source_xmlid, target_file, target_xmlid, relation]):
            errors.append("Empty value")

        # check if source_file is in MMLLAR
        if source_file not in self.MMLLAR_filenames:
            errors.append(f"Source file (\"{source_file}\") not in MMLLAR")

        # check if target_file is in MMLLAR
        if target_file not in self.MMLLAR_filenames:
            errors.append(f"Target file (\"{target_file}\") not in MMLLAR")

        # check if source_xmlid and target_xmlid are in format x letter, then number (e.g. x307)
        if not all([source_xmlid[0] == 'x', target_xmlid[0] == 'x', source_xmlid[1:].isdigit(),
                    target_xmlid[1:].isdigit()]):
            errors.append(
                f"Source_xmlid (\"{source_xmlid}\") or target_xmlid (\"{target_xmlid}\") is not in format x letter "
                f"then number (e.g. \"x307\")")

        # check if source_file is not before target_file based on MMLLAR order
        if self.MMLLAR_filenames.index(source_file) < self.MMLLAR_filenames.index(target_file):
            errors.append(
                f"Source file (\"{source_file}\") shouldn't be before target file (\"{target_file}\") based on MMLLAR order")

        # check if source_file xmlid is not before target_file xmlid
        if source_file == target_file and int(source_xmlid[1:]) < int(target_xmlid[1:]):
            errors.append(f"Source xmlid (\"{source_xmlid}\") shouldn't be before target xmlid (\"{target_xmlid}\")")

        if errors:
            error_messages = "\n".join(f"* {error}" for error in errors)
            raise ValueError(error_messages)

        return True

    def process_files(self, filenames: list[str]):
        """Processes a list of filenames, generating the MMLKG.

        Args:
            filenames (list[str]): The list of filenames to process.
        """
        for file_id, filename in enumerate(filenames):
            print(f"Processing ESX MML file: {filename} ({file_id + 1}/{len(filenames)})\033[K", end='\r',
                  file=sys.stderr)
            self.current_filename = filename

            filepath: str = os.path.join(self.ESXMML, f'{filename}.esx')

            if 'filenames' in self.selected_outputs:
                self.output.print_filename(filename)

            self.current_doc = etree.parse(filepath)
            self._process_elements(file_id)
            self.local_references.clear()

    def _process_elements(self, file_id):
        """Processes the elements of the current document.

        Args:
            file_id (int): The file order index.
        """
        for element in self.current_doc.iter():
            current_xmlid = element.get("xmlid")
            self.current_node = self._create_node_name(self.current_filename, current_xmlid)

            node_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"http://mizar.uwb.edu.pl/.well-known/mmlkg/{self.current_node}")
            element.attrib.update({"notation": f"m.{file_id + 1}.{element.sourceline}", "uuid": f"{node_uuid}"})

            if 'nodes' in self.selected_outputs:
                self.output.print_node(self.current_node, element.tag, element.attrib)

            self._process_relations(element)

    def _process_relations(self, element):
        """Processes relations of the given element.

        Args:
            element (lxml.etree.Element): The element to process relations for.
        """
        if 'member-relations' in self.selected_outputs:
            self._process_member_relation(element)

        if 'local-ref-relations' in self.selected_outputs:
            self._process_local_reference_relation(element)

        if 'usages-relations' in self.selected_outputs:
            self._process_usages_relations(element)

        if 'broader-relations' in self.selected_outputs:
            self._process_broader_relations(element)

        if 'csv-relations' in self.selected_outputs:
            self._process_csv_relations()

        if 'rdf-relations' in self.selected_outputs:
            self._process_rdf_relations(element)

    def _process_member_relation(self, element):
        """Processes the MEMBER relation of the given element.

        Args:
            element (lxml.etree.Element): The element to process the member relation for.
        """
        if element.getparent() is not None:
            parent_node: str = self._create_node_name(self.current_filename, element.getparent().get("xmlid"))
            self.output.print_relation(self.current_node, "MEMBER", parent_node)

    def _process_local_reference_relation(self, element):
        """Processes the Local-Reference of the given element. Local-Reference is a reference to a Label element in the same file. Both should have the same serialnr attribute.

        Args:
            element (lxml.etree.Element): The element to process the local reference for.
        """
        if element.tag == "Label":
            serialnr = element.get("serialnr")
            if serialnr not in self.local_references:
                self.local_references[serialnr] = self.current_node

        if element.tag == "Local-Reference":
            serialnr = element.get("serialnr")
            related_node = self.local_references.get(serialnr)
            if related_node is not None:
                self.output.print_relation(self.current_node, "RELATED", related_node)

    def _process_usages_relations(self, element):
        """Processes usages relations of the given element.

        Details on usages relations can be found in the config.py file.
        source -> target with the same attribute value
        Attribute value contains info about target element's filename

        Args:
            element (lxml.etree.Element): The element to process the usages reference for.
        """
        for ref in config.usages_relations:
            if element.tag == ref[0]:
                attribute_value = element.get(ref[1])
                ref_filename = self._create_filename_from_mmlid(attribute_value)
                ref_file_doc = self._get_reference_file_doc(ref_filename)

                target_elements = ref_file_doc.findall(f".//{ref[2]}[@{ref[1]}='{attribute_value}']")

                for target_element in target_elements:
                    if target_element is not None:
                        related_node = self._create_node_name(ref_filename, target_element.get("xmlid"))
                        self.output.print_relation(self.current_node, "RELATED", related_node)

    def _process_broader_relations(self, element):
        """Processes BROADER relations of the given element. Details on relations can be found in the config.py file.

        Args:
            element (lxml.etree.Element): The element to process the broader reference for.
        """
        for ref_id, ref in enumerate(config.broader_relations):
            parent_el, el = self._parse_reference_path(ref[0])

            if element.tag == el and (parent_el is None or element.getparent().tag == parent_el):
                # save ref[0] element's ref[1] attribute's value to attribute_value
                attribute_value = element.get(ref[1])

                # save current node name to cache, key is {ref_id}_{attribute_value}
                self.broader_rel_cache[f"{ref_id}_{attribute_value}"] = self.current_node

                # Print relations for all ref[2] elements
                for ref2 in element.findall(f"..//{ref[2]}"):
                    if ref2 is not None:
                        self.output.print_relation(self.current_node, "BROADER",
                                                   self.broader_rel_cache[f"{ref_id}_{ref2.get(ref[1])}"])

    def _process_csv_relations(self) -> None:
        """Processes CSV file relation of current node."""
        # check if current node is in csv_data
        if self.current_node in self.csv_data:

            # print all relations from current node
            for target_node, relation in self.csv_data[self.current_node]:
                self.output.print_relation(self.current_node, relation, target_node)

            # delete current node from csv_data
            del self.csv_data[self.current_node]

    def _process_rdf_relations(self, element: etree.Element) -> None:
        """Processes RDF file relation of given element.

        Args:
            element (lxml.etree.Element): The element to process the rdf relation for.
        """
        if element.tag == "Notion-Name":
            # lowercase and remove all chars except letters and numbers
            inscription: str = re.sub(r'[^a-z0-9]', '', element.get("inscription").lower())

            for subj, pred, obj in self.rdf_graph:
                # encode/decode to remove weird chars
                subj = subj.encode('utf-8', 'ignore').decode('utf-8')
                pred = pred.encode('utf-8', 'ignore').decode('utf-8')
                # get last part of url (after last / excluding params and fragments)
                # lowercase and remove all chars except letters and numbers
                subj = re.sub(r'[^a-z0-9]', '', urlparse(subj).path.split('/')[-1].lower())
                # replace _ with space
                pred = urlparse(pred).path.split('/')[-1].replace('_', ' ')

                if inscription == subj:
                    hash_object = hashlib.md5(obj.encode('utf-8', 'ignore').decode('utf-8').encode())
                    target_node = f"rdf{hash_object.hexdigest()}"
                    obj_clean = obj.encode('utf-8', 'ignore').decode('utf-8')

                    self.output.print_node(target_node, "rdfResource", {"value": obj_clean})

                    if isinstance(obj, Literal) and obj.language is not None:
                        self.output.print_relation(self.current_node, pred, target_node, {"lang": obj.language})
                    else:
                        self.output.print_relation(self.current_node, pred, target_node)

    @staticmethod
    def _parse_reference_path(path: str):
        """Parses a reference path. Only one slash is allowed.

        Args:
            path (str): The reference path to parse. Format: parent_element/element

        Returns:
            tuple: The parsed reference path (parent_element, element).
        """
        if '/' in path:
            path_splitted = path.split('/')
            return path_splitted[0], path_splitted[1]
        else:
            return None, path

    def _get_reference_file_doc(self, ref_filename: str):
        """Gets the reference file document for the given reference filename.

        Args:
            ref_filename (str): The reference filename.

        Returns:
            lxml.etree.ElementTree: The reference file document.
        """
        if ref_filename == self.current_filename:
            return self.current_doc
        elif ref_filename in self.usages_rel_cache:
            return self.usages_rel_cache[ref_filename]
        else:
            ref_file_doc = etree.parse(os.path.join(self.ESXMML, f"{ref_filename}.esx"))
            self.usages_rel_cache[ref_filename] = ref_file_doc
            return ref_file_doc

    def run(self):
        """Runs the Mizgra with the given output format."""
        # Check if there is anything to do
        if not self.selected_outputs:
            print("Nothing to do. Exiting...\033[K", file=sys.stderr)
            sys.exit()

        try:
            print(f"Selected outputs: {self.selected_outputs}\033[K", file=sys.stderr)
            self.output.print_header()

            if 'metadata' in self.selected_outputs:
                self._process_metadata_file(self.metadata)
                if self.selected_outputs == ['metadata']:
                    self.output.print_footer()
                    print("Converted metadata. Exiting...\033[K", file=sys.stderr)
                    sys.exit()
            self.process_files(self.MMLLAR_filenames)
            self.output.print_footer()
            print("Converted all files. Exiting...\033[K", file=sys.stderr)
        except KeyboardInterrupt:
            self.output.print_footer()
            print("Interrupted by user. Exiting...\033[K", file=sys.stderr)
            sys.exit()
        except Exception as e:
            self.output.print_footer()
            print(f"Error: {e}\033[K", file=sys.stderr)
            sys.exit(1)


def main():
    """Main function."""
    args = Mizgra.parse_arguments()
    mizgra = Mizgra(args)
    mizgra.run()


if __name__ == '__main__':
    main()
