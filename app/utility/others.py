import json


def construct_sbar_report(situation,
                          background,
                          assessment,
                          recommendation,
                          reported_by) -> json:
    report_dict = {
        "sbar_report": {
            "patient": {
                "name": situation.patient_name,
                "mrn": situation.mrn,
                "age": situation.age,
                "gender": situation.gender,
                "room_number": situation.room_number,
                "admission_date": situation.admission_date,
            },
            "situation": {
                "feedback": situation.list_situations_feedback
            },
            "background": background.list_backgrounds,
            "assessment": assessment.list_assessments,
            "recommendation": recommendation.list_recommendations,
            "reported_by": {
                "nurse": reported_by.nurse,
                "license_number": reported_by.license_number
            }
        }
    }

    return json.dumps(report_dict)
