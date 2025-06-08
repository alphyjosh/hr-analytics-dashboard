import os
import os
import openai
import json

def extract_fields_with_gpt(ocr_text):
    print("[DEBUG] Called extract_fields_with_gpt")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not set in environment variables.")
        raise ValueError("OPENAI_API_KEY not set in environment variables.")
    client = openai.OpenAI(api_key=api_key)
    prompt = f"""
Extract the following fields from this certificate text:
- Employee Name
- Employee ID
- Department
- Designation
- Company Name
- Employment Period
- Date of Issuance
- Signatory

Certificate Text:
{ocr_text}

Respond in JSON format with keys: employee_name, id_no, department, designation, company_name, employment_period, date_of_issuance, signatory.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        content = response.choices[0].message.content
        print("GPT-4o raw response:", content)  # Debug print
        # Extract JSON from the response
        start = content.find('{')
        end = content.rfind('}') + 1
        json_str = content[start:end]
        fields = json.loads(json_str)
        return fields
    except Exception as e:
        import traceback
        print("[ERROR] LLM extraction failed:", e)
        traceback.print_exc()
        return None
