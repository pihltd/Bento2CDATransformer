#Provides a set of empty dictionaries for use in populating stuff
def init():
    global identifiers
    identifiers = {
        "system":None, "field_name":None, "value":None
    }

    global file 
    file = {
    "id": None,
    "identifiers": [],
    "label": None,
    "data_category": None,
    "data_type": None,
    "file_format": None,
    "drs_uri": None,
    "byte_size": None,
    "checksum": None,
    "data_modality": None,
    "imaging_modality": None,
    "dbgap_accession_number": None,
    "imaging_series": None,
    "associated_projects": [],
    "subjects": [],
    "research_subjects": [],
    "specimens": []
    }

    global diagnosis
    diagnosis = {
            "id": None,
            "identifiers": [],
            "primary_diagnosis":None,
            "age_at_diagnosis": None,
            "morphology": None,
            "stage": None,
            "grade": None,
            "method_of_diagnosis": None,
            "treatments": []
        }
    
    global treatment
    treatment = {
            "id": None,
            "identifiers": [],
            "treatment_type": None,
            "treatment_outcome": None,
            "days_to_treatment_start": None,
            "days_to_treatment_end": None,
            "therapeutic_agent": None,
            "treatment_effect": None,
            "treatment_end_reason": None,
            "number_of_cycles": None
        }

    global research_subject
    research_subject = {
            "id": None,
            "identifiers": [],
            "primary_diagnosis_condition": None,
            "primary_diagnosis_site": None,
            "member_of_research_project": None,
            "diagnoses": [],
            "treatments":[],
            "specimens": []
        }
    
    global subject
    subject = {
            "id": None,
            "identifiers": [],
            "species": None,
            "sex": None,
            "race": None,
            "ethnicity": None,
            "days_to_birth": None,
            "vital_status": None,
            "days_to_death": None,
            "cause_of_death": None,
            "subject_associated_projects": [],
            "research_subjects": []
        }
    
    global specimen
    specimen = {
            "id": None,
            "identifiers": [],
            "days_to_collection": None,
            "primary_disease_type": None,
            "anatomical_site": None,
            "source_material_type": None,
            "specimen_type": None,
            "associated_project": None,
            "derived_from_specimen": None,
            "derived_from_subject": None
        }