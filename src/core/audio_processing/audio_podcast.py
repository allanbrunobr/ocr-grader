import os
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

ELEVENLABS_API_KEY = "sk_5a8b597b9cca599c6dc7048f0868ef8f244deba7da4e0324"
#os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY not found in environment variables")

client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

def generate_audio_elevenlabs(text, voice_id, output_path, is_professor):
    """
    Generates super enthusiastic educational podcast audio
    """
    print(f"Generating {voice_id} enthusiastic podcast audio for text: {text}")

    if is_professor:
        # Professor: Super enthusiastic and engaging!
        voice_settings = VoiceSettings(
            stability=0.15,  # Very expressive and dynamic
            similarity_boost=0.45,  # Allow lots of variation
            style=1.0,  # Maximum style for super dynamic delivery
            use_speaker_boost=True,
        )
        text = add_super_excited_professor(text)
    else:
        # Student: Energetic teenager
        voice_settings = VoiceSettings(
            stability=0.25,  # More variation for teenage energy
            similarity_boost=0.65,  # Keep some youth characteristics
            style=1.0,  # Very stylized for teenage enthusiasm
            use_speaker_boost=True,
        )
        text = add_teenage_student_style(text)

    try:
        response = client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_turbo_v2_5",
            voice_settings=voice_settings,
        )

        with open(output_path, "wb") as audio_file:
            for chunk in response:
                if chunk:
                    audio_file.write(chunk)

        return output_path

    except Exception as e:
        print(f"Error generating podcast audio: {e}")
        raise

def add_super_excited_professor(text):
    """
    Makes the professor super enthusiastic and interactive
    """
    # Start with overall energetic tone
    text = f"<prosody pitch='+12%' rate='108%'>{text}</prosody>"

    # Add extra enthusiasm to greetings and introductions
    intro_phrases = [
        "bom dia", "olá", "bem-vindo", "vamos", "hoje",
        "agora", "certo", "beleza"
    ]
    for phrase in intro_phrases:
        text = text.replace(
            f" {phrase} ",
            f" <prosody pitch='+25%' rate='115%'>{phrase}!</prosody> "
        )

    # Make statements more engaging by adding questions
    text = text.replace(
        "Vamos falar sobre",
        "Você está pronto para descobrir algo incrível sobre"
    )
    text = text.replace(
        "Vamos aprender",
        "Quer conhecer algo fascinante sobre"
    )

    # Add extra enthusiasm to positive feedback
    excitement_words = [
        "excelente", "perfeito", "incrível", "fantástico",
        "sensacional", "brilhante", "maravilhoso", "exatamente",
        "absolutamente", "muito bem", "isso mesmo"
    ]
    for word in excitement_words:
        text = text.replace(
            f" {word} ",
            f" <prosody pitch='+30%' rate='120%'>{word}! That's fantastic!</prosody> "
        )

    # Add engaging questions and interactions
    text = text.replace(
        "For example,",
        "Here's something mind-blowing - can you guess"
    )
    text = text.replace(
        "This means",
        "And you know what this means? It means"
    )

    # Add dramatic pauses and emphasis
    text = text.replace(".", "! <break time='300ms'/>")
    text = text.replace("?", "? <break time='400ms'/>")

    # Make educational terms exciting
    edu_terms = [
        "ciência", "matemática", "história", "pesquisa",
        "descoberta", "experimento", "teoria", "conceito"
    ]

    # Substitui frases de introdução
    text = text.replace(
        "Vamos falar sobre",
        "Você está pronto para descobrir algo incrível sobre"
    )
    text = text.replace(
        "Vamos aprender",
        "Quer conhecer algo fascinante sobre"
    )
    for term in edu_terms:
        text = text.replace(
            f" {term} ",
            f" <prosody pitch='+20%' rate='110%'><emphasis level='strong'>{term}</emphasis></prosody> "
        )

    return text

def add_teenage_student_style(text):
    """
    Faz o aluno soar como um adolescente entusiasmado
    """
    text = f"<prosody pitch='+20%' rate='115%'>{text}</prosody>"

    teen_phrases = {
        "Eu acho": "Nossa, eu acho",
        "Talvez": "Caramba, talvez",
        "Será": "Meu Deus, será",
        "Pode ser": "Uau! Pode ser",
        "Certo": "Isso, isso mesmo!",
        "Entendi": "Ahhh, agora sim entendi!",
        "Sim": "Nossa, sim! Com certeza!",
        "Por que": "Nossa, por que",
        "Como assim": "Caramba, como assim",
        "Interessante": "Que máximo! Super interessante"
    }

    for old, new in teen_phrases.items():
        text = text.replace(
            f" {old} ",
            f" <prosody pitch='+20%' rate='110%'>{new}</prosody> "
        )

    # Add teenage enthusiasm to questions
    if "?" in text:
        text = f"<prosody pitch='+25%' rate='120%'>{text}</prosody>"

    # Add excitement to realizations
    if "!" in text:
        text = f"<prosody pitch='+30%' rate='125%'>{text}</prosody>"

    text = text.replace("!", "! <break time='200ms'/> ")
    text = text.replace("?", "? <break time='300ms'/> ")

    return text

def generate_conversation_audios(conversation, person1_voice_id, person2_voice_id, output_dir, person1, person2):
    lines = conversation.split('\n')
    audio_files = []

    # Suggested voices for more enthusiasm:
    # Professor - Try "Josh" or "Sam" for more energy
    # Student - Try "Rachel" or "Grace" with higher pitch settings

    for i, line in enumerate(lines):
        line = line.replace('*', '').strip()

        if not line:
            continue

        if f"{person1}:" in line:
            voice_id = person1_voice_id
            text = line.split(f"{person1}:", 1)[1].strip()
            is_professor = True
        elif f"{person2}:" in line:
            voice_id = person2_voice_id
            text = line.split(f"{person2}:", 1)[1].strip()
            is_professor = False
        else:
            continue

        if not text:
            continue

        output_filename = f"audio_{i:03d}_{voice_id[-6:]}.mp3"
        output_path = os.path.join(output_dir, output_filename)

        try:
            generate_audio_elevenlabs(text, voice_id, output_path, is_professor)
            audio_files.append((i,output_path))

        except Exception as e:
            print(f"Error generating audio {i+1}: {e}")
            continue

    audio_files.sort(key=lambda x: x[0])
    return [path for _, path in audio_files]

def combine_audio_files(audio_files, output_dir):
    """
    Combines audio files with dynamic podcast effects
    """
    try:
        combined = AudioSegment.empty()

        # Add energetic transition
        transition = AudioSegment.silent(duration=500).fade_in(150).fade_out(150)
        combined += transition

        for i, audio_file in enumerate(sorted(audio_files)):
            audio = AudioSegment.from_mp3(audio_file)

            # Enhance volume and normalize
            audio = audio.normalize()

            # Dynamic silence based on context
            silence_duration = 300 if i % 2 == 0 else 400
            combined += AudioSegment.silent(duration=silence_duration)

            # Add slight fade for smooth transitions
            audio = audio.fade_in(100).fade_out(100)
            combined += audio

        output_path = os.path.join(output_dir, "energetic_podcast.mp3")

        combined.export(
            output_path,
            format="mp3",
            bitrate="192k",
            parameters=["-ac", "2", "-ar", "44100"]
        )

        return output_path

    except Exception as e:
        print(f"Error combining podcast audios: {e}")
        return None