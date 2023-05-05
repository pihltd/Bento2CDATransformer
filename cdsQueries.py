def init():
    global file_info
    file_info ="""
{
file{
    file_id
    file_name
    file_type
    file_url_in_cds
    file_size
    md5sum
    study{
      phs_accession
      study_name
      study_acronym
    }
    samples{
        sample_id
        participant{
            participant_id
      }
    }
}
}"""
