import openai

from app.utility.env import get_open_ai_key


def generate_sbar():
    client = openai.OpenAI(api_key=get_open_ai_key())

    model = "gpt-4o-mini"

    user_prompt = """"
    
    
    
    
    
    
    
    """

    class HandoffReport:
        pass

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
             "content": "You are a nurse preparing a handoff report for the incoming shift. Your task is to generate a structured SBAR report based on patient data."},
            {"role": "user", "content": f"{user_prompt}"}
        ],
        temperature=0,
        response_format=HandoffReport,
    )

    print("Generated text:\n", response.choices[0].message.content)

    return response.choices[0].message.content
