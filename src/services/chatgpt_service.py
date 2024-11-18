from typing import List, Dict
from openai import OpenAI

client = OpenAI()

def send_to_chatgpt(text_results: List[Dict]) -> str:
    prompt = "Aqui está o conteúdo da prova extraído via OCR:\n\n"
    for result in text_results:
        if 'page' in result:
            prompt += f"Documento: {result['filename']}\n"
            prompt += f"Página {result['page']}:\n{result['text_data']}\n\n"
        else:
            prompt += f"Documento: {result['filename']}\n{result['text_data']}\n\n"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """Você é um professor experiente..."""},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
