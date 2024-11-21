from openai import OpenAI

client = OpenAI()

def generate_conversation(summary, person1, person2):
    prompt = f"""
    Crie um diálogo educacional entre {person1} e {person2} sobre esta correção de prova.
    O diálogo DEVE alternar SEMPRE entre {person1} e {person2}, seguindo este formato exato:

    {person1}: [fala do professor]
    {person2}: [pergunta ou comentário do aluno]
    {person1}: [resposta do professor]
    {person2}: [nova dúvida ou reflexão]

    Regras importantes:
    1. SEMPRE comece com "{person1}:"
    2. SEMPRE alterne entre {person1} e {person2}
    3. {person2} deve:
       - Fazer perguntas sobre os erros cometidos
       - Demonstrar curiosidade sobre os fatos históricos
       - Expressar dúvidas genuínas
       - Pedir esclarecimentos
    4. {person1} deve:
       - Explicar os erros de forma didática
       - Expandir o conhecimento além da resposta básica
       - Incentivar a curiosidade do {person2}
    
    Análise da prova:
    {summary}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Você é um especialista em criar diálogos educacionais dinâmicos em português, garantindo sempre a alternância entre {person1} e {person2}."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

