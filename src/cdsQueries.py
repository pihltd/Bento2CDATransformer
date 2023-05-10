def init():
    global testquery
    testquery = """
    {
        program{
            program_acronym
        }
    }
    """
    
    global file_info
    file_info ="""
    {
        file{
            file_id
            file_name
            file_type
            file_size
            md5sum
        }
    }"""

    global file_samples
    file_samples = """
    {
        file{
            file_id
            samples{
                sample_id
            }
        }
    }"""
    global file_participants
    file_participants = """
    {
        file{
            file_id
            samples{
            participant{
                participant_id
            }
            }
        }
    }"""
    global diagnosis_info
    diagnosis_info = """
    {
        diagnosis{
            diagnosis_id
            primary_diagnosis
            age_at_diagnosis
            morphology
            tumor_stage_clinical_m
            tumor_stage_clinical_n
            tumor_stage_clinical_t
            tumor_grade
        }
    }"""

    global treatment_info
    treatment_info = """
    {
        treatment{
            treatment_id
            treatment_type
            treatment_outcome
            days_to_treatment
            therapeutic_agents
        }
    }"""

    global sample_info
    sample_info = """
    {
        sample{
            sample_id
            sample_age_at_collection
            sample_anatomic_site
            sample_type
            derived_from_specimen
        }
    }"""

    global basic_subject_info
    basic_subject_info = """
    {
        participant{
            participant_id
            gender
            race
            ethnicity
        }
    }
    """

    global test_subject_info
    test_subject_info = """
    {
        participant{
            participant_id
            gender
            race
            ethnicity
            study{
                organism_species
                study_acronym
            }
            diagnoses{
                vital_status
            }
        }
    }
    """

global research_subject_info
research_subject_info = """
    {
    participant{
        participant_id
        diagnoses{
        primary_diagnosis
                primary_site
        }
        samples{
        sample_id
        }
    }
    }
"""