from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Cdaidentifier:
    system: str = None
    field_name: str = None
    value: str = None

@dataclass
class File:
    id: str = None
    identifiers: Cdaidentifier = None
    label: str = None
    data_category: str = None
    data_type: str = None
    file_format: str = None
    drs_uri: str = None
    byte_size: int = None
    checksum: str = None
    data_modality: str = None
    imaging_modality: str = None
    dbgap_accession_number: str = None
    imaging_series: str = None
    associated_projects: list = None
    subjects: list = None
    research_subjects: list = None
    specimens: list = None

@dataclass
class Files:
    file: List[File]