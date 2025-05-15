import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
import re

# Load environment variables from .env file
load_dotenv()

# Access the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

class PlaceholderValues(BaseModel):
    values: List[Optional[str]]

def get_placeholder_values(parsed_json_file, parsed_json_template_file=None, agreed_claims=None):
    """Get placeholder values from OpenAI API based on the provided text.
    
    Args:
        parsed_json_file: Dictionary containing the 'text' field with legal document content
        parsed_json_template_file: Optional dictionary containing template text
        agreed_claims: Optional list of agreed claims
        
    Returns:
        Tuple of (placeholder_values, ai_prompt) where placeholder_values is a list of values and ai_prompt is the full prompt sent to the AI
    """
    # Extract text from parsed_json_file
    text = parsed_json_file.get('text', '')
    
    # Extract placeholder regex if provided, otherwise use default
    placeholder_regex = parsed_json_file.get('placeholder_regex', r'\[\s*•[^\]]*\]')
    
    # Extract template text if provided
    template_text = ""
    if parsed_json_template_file and 'text' in parsed_json_template_file:
        template_text = parsed_json_template_file.get('text', '')
    
    # Count placeholders if template is provided
    placeholder_count = 0
    if template_text:
        # Remove 'g' flag for Python regex
        search_regex = placeholder_regex.rstrip('g')
        if search_regex.startswith('/'):
            search_regex = search_regex[1:]
        if search_regex.endswith('/'):
            search_regex = search_regex[:-1]
            
        # Count matches
        placeholder_count = len(re.findall(search_regex, template_text))
    
    # Construct the prompt for OpenAI
    prompt = """
#Aufgabe
Fülle das Template für Klageantwort aus. Gib mir ein json array mit allen ausgefüllten placeholder texten.

Dein Hauptziel ist es, starke Gegenargumente zur Klageschrift zu finden und möglichst viele Platzhalter sinnvoll auszufüllen. 
Versuche, mindestens 80% aller Platzhalter mit sinnvollen Werten zu füllen. Nur wenn absolut keine passende Information gefunden werden kann, darfst du null als Wert einsetzen.
"""

    # Add regex information
    prompt += f"""
Die Platzhalter im Template folgen diesem Regex-Muster: {placeholder_regex}
Suche nach allen Textstellen, die diesem Muster entsprechen, und fülle sie mit passenden Werten aus.
"""

    # Add information about placeholder count and null values
    if placeholder_count > 0:
        prompt += f"""
Im Template wurden genau {placeholder_count} Platzhalter gefunden. Dein Array MUSS exakt {placeholder_count} Einträge enthalten.
Versuche, mindestens {int(placeholder_count * 0.8)} Platzhalter auszufüllen. Verwende nur für maximal {int(placeholder_count * 0.2)} Platzhalter null-Werte.
Sei kreativ und entwickle starke juristische Gegenargumente, um die Position des Beklagten zu verteidigen.
"""

    prompt += """
#Klageschrift
"""

    prompt += text

    prompt += """

#Template für Klageantwort
"""

    # Add template information if available
    if template_text:
        prompt += template_text
    
    # Store system prompt for returning
    system_prompt = f"Du bist ein juristischer Assistent, der Platzhalter in einer Klageantwort basierend auf einer Klageschrift ausfüllt. Dein Ziel ist es, starke Gegenargumente zu finden und eine Verteidigung aufzubauen. Fülle mindestens 80% der Platzhalter mit sinnvollen Werten aus und verwende null nur wenn absolut nötig. Liefere ein Array mit genau {placeholder_count if placeholder_count > 0 else 45} Werten."
    
    try:
        # Make request to OpenAI with structured outputs
        response = client.responses.parse(
            model="gpt-4o-2024-08-06",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            text_format=PlaceholderValues,
        )
        
        # Return the parsed values and the prompts
        return response.output_parsed.values, {
            "system_prompt": system_prompt,
            "user_prompt": prompt
        }
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Fall back to mock values if there's an error
        mock_values = get_placeholder_mock_values(parsed_json_file, parsed_json_template_file, agreed_claims)
        return mock_values, {
            "system_prompt": system_prompt,
            "user_prompt": prompt,
            "error": str(e)
        }

def get_placeholder_mock_values(parsed_json_file, parsed_json_template_file=None, agreed_claims=None):
    """Get mock placeholder values.
    
    Args:
        parsed_json_file: Dictionary containing the 'text' field with legal document content
        parsed_json_template_file: Optional dictionary containing template text
        agreed_claims: Optional list of agreed claims
        
    Returns:
        A tuple of (placeholder_values, None) where placeholder_values is a list of mock values
    """
    # get the placeholder values from the parsed json file
    text = parsed_json_file['text']

    mock_placeholder_values = [
        "Die Klage sei abzuweisen;",
        "der Klägerin",
        "24. Oktober 2012",
        "Die Schlichtungsverhandlung fand am (…) statt. Da zwischen den Parteien keine Einigung zustande kam, wurde der Klägerin am (…) die Klagebewilligung erteilt.",
        "Zivilgericht Basel-Stadt",
        "nicht anwendbar",
        "nicht anwendbar",
        "nicht anwendbar",
        "Das angerufene Gericht ist örtlich und sachlich zuständig (Art. 31 ZPO), da der Wohnsitz des Beklagten in Basel liegt.",
        "Der Streitwert beträgt CHF 12'000.– (Art. 221 Abs. 1 lit. c ZPO).",
        "Die Aktiv- und Passivlegitimation sind unbestritten gegeben.",
        "Der Beklagte",
        "Die Sachverhaltsdarstellung, Ausführungen und Behauptungen der Klägerin werden gesamthaft und in allen Einzelheiten bestritten, soweit diese nicht ausdrücklich anerkannt werden.",
        "Der Beklagte offeriert für sämtliche bestrittenen Sachverhaltsdarstellungen der Klägerin den rechtsgenügenden Beweis insgesamt und in jedem einzelnen Punkt, sofern und soweit ihn die Beweislast trifft.",
        "Einleitung zur materiellen Begründung",
        "Die Klägerin behauptet eine Forderung aus einem Kaufvertrag.",
        "Der Kaufvertrag ist bestritten.",
        "Der Beklagte bestreitet, dass ein wirksamer Vertrag zustande kam.",
        "Der Beklagte hat das Fahrzeug nicht vorbehaltlos übernommen, sondern Mängel gerügt.",
        "Es bestehen erhebliche Zweifel an der Mangelfreiheit des Fahrzeuges.",
        "Der Ausschluss der Gewährleistung ist unwirksam, da eine grobe Täuschung durch die Klägerin vorliegt.",
        "Beweis: Zeuge A, Fahrer der Klägerin",
        "Beweis: Schriftwechsel zwischen den Parteien (Mahnschreiben vom 5. und 30. April 2012)",
        "Beweis: Fahrzeugunterlagen (Brief/Schein) vorhanden",
        "Es liegt ein Verzug nicht vor, da keine wirksame Forderung besteht.",
        "Verzugszinsen sind somit unbegründet.",
        "Die Klägerin hat sich nicht an Treu und Glauben gehalten.",
        "Die Forderung ist rechtsmissbräuchlich geltend gemacht.",
        "Das Verhalten der Klägerin verletzt die Aufklärungspflicht im Vertragsrecht.",
        "Zusammenfassung der rechtlichen Argumentation",
        "Die Klage ist unbegründet und abzuweisen.",
        "Sehr geehrter Herr Präsident",
        "Entscheid Zivilgericht Basel-Stadt",
        "24. Oktober 2012",
        "kläg.act. 0 bis 5",
        "bekl.act. 1 bis 3 retour",
        "Rechtsanwalt Dr. Mark Sacher",
        "Beilagen: Entscheid Zivilgericht Basel-Stadt",
        "Beilagen: Vollmacht vom 24. Oktober 2012",
        "Beilagen: kläg.act. 0 bis 5",
        "Beilagen: bekl.act. 1 bis 3 retour",
        "Klientschaft",
        "Sacher Rechtsanwälte, Basel",
        "5% Zins ab 28. Mai 2012 wird bestritten"
    ] 
    return mock_placeholder_values, None