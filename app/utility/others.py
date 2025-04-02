import json

from app.utility.logger import get_logger

logger = get_logger()


def construct_sbar_report(situation,
                          background,
                          assessment,
                          recommendation,
                          reported_by,
                          prompt_tokens,
                          completion_tokens,
                          total_tokens,
                          cost_estimate) -> json:
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
        },
        "token_usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        },
        "cost_estimate": cost_estimate
    }

    return json.dumps(report_dict)


def construct_question_answer(answer: str) -> json:
    report_dict = {
        "answer": answer
    }

    return json.dumps(report_dict)


def get_database_configuration(environment, url, path):
    try:
        with open(path, 'r') as config_file:
            config = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading database configuration: {e}")
        raise SystemExit(1)
    return config[environment][url]
