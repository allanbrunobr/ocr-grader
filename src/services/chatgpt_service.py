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
            {"role": "system", "content": """Você é um professor experiente e vai analisar esta prova.
            
            Suas responsabilidades são:
            1. Identifique cada questão pelo seu cabeçalho/enunciado
            2. Para cada questão identificada:
               - Apresente o cabeçalho/enunciado original
               - Se não respondida: forneça a resposta correta com explicação
               - Se respondida: indique se está certa ou errada
               - Para questões erradas: explique o erro e forneça a resposta correta
            3. Atribua uma nota final considerando o desempenho geral
            
            Importante: Ao reproduzir qualquer texto, corrija erros óbvios de OCR para melhor legibilidade.
            
            Formato da sua resposta para cada questão:
            === QUESTÃO X (cabeçalho original) ===
            - Status: [Respondida/Não respondida]
            - Avaliação: [Correta/Incorreta/Resposta sugerida]
            - Explicação detalhada
            - Resposta correta (quando aplicável)
            
            Ao final:
            - Nota final
            - Feedback construtivo"""},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
