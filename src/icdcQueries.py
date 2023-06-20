def init():
    global ming_query
    ming_qure = """{
  file {
    uuid
    file_name
    file_type
    file_size
    file_format
    md5sum
    file_location
    study {
      clinical_study_designation
    }
    case{
      case_id
      canine_individual {
        canine_individual_id
      }
    }
    diagnosis {
      diagnosis_id
      case {
        case_id
      }
    }
    sample {
      sample_id
      case {
          case_id
      }
    }
  }
}"""
    
