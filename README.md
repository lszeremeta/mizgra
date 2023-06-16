# mizgra

[![PyPI](https://img.shields.io/pypi/v/mizgra)](https://pypi.org/project/mizgra/) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mizgra) [![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/lszeremeta/mizgra?label=Docker%20image%20size)](https://hub.docker.com/r/lszeremeta/mizgra)

Converts Mizar ESX MML mathematical data to property graph formats - GraphML, YARS-PG. Produce files ready to import to various graph databases, including Neo4j. Supports external RDF data in various formats.

To save output to file, add `> /path/to/output.graphml` to the end of the command, e.g.:

```shell
mizgra /path/to/esx_mml /path/to/mml.lar -m /path/to/metadata.xml -c /path/to/CSVs -cv > mmlkg.graphml
```

Read more about the MMLKG project at the [MMLKG website](https://mmlkg.uwb.edu.pl).

## Run mizgra

There are several ways to run mizgra. You can install it from PyPI, run it using Docker, or run it from the source.
Choose the most convenient way for you.

### PyPI

1. Install mizgra:

```shell
pip install mizgra
```

2. Run mizgra:

```shell
mizgra [ESXMML] [MMLLAR]
```

### Docker from Docker Hub

1. Pull Docker image from Docker Hub:

```shell
docker pull lszeremeta/mizgra
```

2. Run Docker container:

```shell
docker run --rm -v /path/to/esx/and/mml.lar:/app/input lszeremeta/mizgra /app/input/esx_mml /app/input/mml.lar
```

### Docker from source

1. Build Docker image:

```shell
docker build -t mizgra .
```

2. Run Docker container:

```shell
docker run --rm -v /path/to/esx/and/mml.lar:/app/input mizgra /app/input/esx_mml /app/input/mml.lar
```

### Python from source

1. Clone this repository and go to its directory:

```shell
git clone git@github.com:lszeremeta/mizgra.git
cd mizgra
```

2. Install requirements:

```shell
pip install -r requirements.txt
```

3. Run mizgra:

```shell
python -m mizgra [ESXMML] [MMLLAR]
```

## Recommended usage

Mizgra requires two arguments:

- `ESXMML`: Path to the ESX MML files directory. You can [download](https://github.com/arturkornilowicz/esx_files/archive/refs/heads/main.zip) it from [esx_files](https://github.com/arturkornilowicz/esx_files/) repository.
- `MMLLAR`: Path to the mml.lar file. You can [download](https://github.com/arturkornilowicz/esx_files/archive/refs/heads/main.zip) it from [esx_files](https://github.com/arturkornilowicz/esx_files/) repository.

Metadata and CSV relations are recommended. To include them, use `-m` and `-c` arguments.
You can generate metadata with statistics using [metadata_gen](https://github.com/domel/metadata_gen)
and CSV relations using [csvrelgen](https://github.com/arturkornilowicz/csvrelgen).

To save the output to a file, add `> /path/to/output.graphml` to the end of the command.

Example:

```shell
mizgra /path/to/esx_mml /path/to/mml.lar -m /path/to/metadata.xml -c /path/to/CSVs -cv > mmlkg.graphml
```

See [Usage](#usage) for more details.

## Usage

```shell
usage: mizgra [-h] [-v] [-o OUTPUT]
              [-s {filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} [{filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} ...]]
              [-d {filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} [{filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} ...]]
              [-m METADATA] [-c CSV [CSV ...]] [-cv] [-r RDF] [-rf {json-ld,hext,n3,nquads,nt,trix,turtle,xml}]
              ESXMML MMLLAR
```

To see all options in your version use `-h` or `--help`:

```shell
mizgra -h
```

### Informative arguments

- `-h`, `--help`: Show help message and exit.
- `-v`, `--version`: Show program version and exit.

### Required arguments

- `ESXMML`: Path to the ESX MML files directory. You can [download](https://github.com/arturkornilowicz/esx_files/archive/refs/heads/main.zip) it from [esx_files](https://github.com/arturkornilowicz/esx_files/) repository.
- `MMLLAR`: Path to the mml.lar file. You can [download](https://github.com/arturkornilowicz/esx_files/archive/refs/heads/main.zip) it from [esx_files](https://github.com/arturkornilowicz/esx_files/) repository.

### Output preference arguments

- `-o OUTPUT`, `--output OUTPUT`: Output format (`graphml`, `yarspg`; default: `graphml`).
- `-s {filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} [{filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} ...], --show {filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} [{filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} ...]`:
  Show only selected outputs; by default, all possible results are shown, excluding those that are disabled by default (
  local-ref-relations, usages-relations, and broader-relations; handled by CSV relations). To show disabled
  outputs, specify them directly with -s/--show option. It's recommended to use CSV relations.
- `-d {filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} [{filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} ...], --disable {filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} [{filenames,nodes,metadata,member-relations,local-ref-relations,usages-relations,broader-relations,csv-relations,rdf-relations} ...]`:
  Disable selected outputs (local-ref-relations, usages-relations, and broader-relations are disabled by default; handled
  by CSV relations).

### External data arguments

- `-m METADATA`, `--metadata METADATA`: Path to the metadata file. If not specified, metadata without dataset statistics will
  be included. You can generate a full metadata file using: https://github.com/domel/metadata_gen
- `-c CSV`, `--csv CSV`: Paths to the CSV files/directories with relations. You can generate it using: https://github.com/arturkornilowicz/csvrelgen
- `-cv`, `--csv-validate`: Validates CSV files by several checks before reading to minimize the possibility of CSV errors;
  turned off by default.
- `-r RDF`, `--rdf RDF`: Path to the RDF data file; for URLs or files with not standard extensions may be needed to
  specify format using `-rf`.
- `-rf {json-ld,hext,n3,nquads,nt,trix,turtle,xml}`, `--rdf-format {json-ld,hext,n3,nquads,nt,trix,turtle,xml}`: RDF
  data file format, specify if not detected automatically

## Examples

Convert ESX MML data to GraphML format:

```shell
mizgra /path/to/esx_mml /path/to/mml.lar > graph.graphml
```

Convert ESX MML data to YARS-PG format:

```shell
mizgra /path/to/esx_mml /path/to/mml.lar -o yarspg > graph.yarspg
```

Convert ESX MML data to GraphML format, showing only metadata and member-relations:

```shell
mizgra /path/to/esx_mml /path/to/mml.lar -s metadata member-relations > graph.graphml
```

Convert ESX MML data to GraphML format and include external metadata:

```shell
mizgra /path/to/esx_mml /path/to/mml.lar -m /path/to/metadata.xml > graph.graphml
```

Convert ESX MML data to GraphML format and include RDF data in Turtle format:

```shell
mizgra /path/to/esx_mml /path/to/mml.lar -r /path/to/external.ttl -rf turtle > graph.graphml
```

Convert ESX MML data to GraphML format, include CSV data from selected directory, validate CSV files:

```shell
mizgra /path/to/esx_mml /path/to/mml.lar -c /path/to/external -cv > graph.graphml
```

Convert ESX MML data to GraphML format and include CSV data:

```shell
mizgra /path/to/esx_mml /path/to/mml.lar -c /path/to/external.csv > graph.graphml
```

Convert ESX MML data to GraphML format and include CSV data from multiple files and directories:

```shell
mizgra /path/to/esx_mml /path/to/mml.lar -c /path/to/external1.csv /path/to/external2 /path/to/external3.csv > graph.graphml
```

## Contribution

Would you like to improve this project? Great! We are waiting for your help and suggestions. If you are new to open
source contributions, read [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/).

## License

Distributed under [MIT License](https://github.com/lszeremeta/mizgra/blob/main/LICENSE).

This project contains a sample external RDF data file ([rdf_data.nt](https://github.com/lszeremeta/mizgra/blob/main/mizgra/resources/rdf_data.nt)), prepared by Dominik Tomaszuk ([@domel](https://github.com/domel)) and available under the [CC-BY 4.0 License](https://creativecommons.org/licenses/by/4.0/). The base for the query was developed using [Wikidata](https://www.wikidata.org/), which is available under the [Creative Commons CC0 License](https://creativecommons.org/publicdomain/zero/1.0/). While it also includes references to [DBpedia](https://wiki.dbpedia.org/) and [YAGO](https://yago-knowledge.org/) (whose data are on [Creative Commons Attribution-ShareAlike 3.0 License](https://creativecommons.org/licenses/by-sa/3.0/)), Dominik Tomaszuk only retrieved non-data links from these sources. The structure of this file is entirely different than the above datasets.