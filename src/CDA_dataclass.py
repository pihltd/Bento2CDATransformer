from dataclasses import dataclass
from typing import List

@dataclass
class cdaidentifier:
    system: str
    field_name: str
    value: str

@dataclass
class File:
    id: str
    identifiers: cdaidentifier
    label: str
    data_category: str
    data_type: str
    file_format: str
    drs_uri: str
    byte_size: int
    checksum: str
    data_modality: str
    imaging_modality: str
    dbgap_accession_number: str
    imaging_series: str
    associated_projects: list
    subjects: list
    research_subjects: list
    specimens: list

@dataclass
class Files:
    file: List[File]