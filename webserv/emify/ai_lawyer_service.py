import os
import re
from typing import List, Optional, Dict, Tuple, Any, Union
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Access the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

class PlaceholderValues(BaseModel):
    values: List[Optional[str]]

def count_placeholders(template_text: str, regex_pattern: str) -> int:
    """
    Count placeholders in template text using the provided regex pattern.
    
    Args:
        template_text: The template text to search for placeholders
        regex_pattern: The regex pattern to use for matching placeholders
        
    Returns:
        The number of placeholders found in the template
    """
    # Clean up regex pattern for Python (remove JS-specific parts)
    clean_regex = regex_pattern.rstrip('g')
    if clean_regex.startswith('/'):
        clean_regex = clean_regex[1:]
    if clean_regex.endswith('/'):
        clean_regex = clean_regex[:-1]
        
    # Count matches if template is provided
    return len(re.findall(clean_regex, template_text)) if template_text else 0

def build_prompt(text: str, template_text: str, placeholder_regex: str, placeholder_count: int) -> Tuple[str, str]:
    """
    Build the prompt for the AI model.
    
    Args:
        text: The legal document text
        template_text: The template text
        placeholder_regex: The regex pattern for placeholders
        placeholder_count: The number of placeholders found
        
    Returns:
        Tuple of (user_prompt, system_prompt)
    """
    # Construct the system prompt
    system_prompt = (
        f"Du bist ein juristischer Assistent, der Platzhalter in einer Klageantwort basierend auf "
        f"einer Klageschrift ausfüllt. Dein Ziel ist es, starke Gegenargumente zu finden und eine "
        f"Verteidigung aufzubauen. Fülle mindestens 80% der Platzhalter mit sinnvollen Werten aus "
        f"und verwende null nur wenn absolut nötig. Liefere ein Array mit genau "
        f"{placeholder_count if placeholder_count > 0 else 45} Werten."
    )
    
    # Construct the user prompt
    user_prompt = f"""
#Aufgabe
Fülle das Template für Klageantwort aus. Gib mir ein json array mit allen ausgefüllten placeholder texten.

Dein Hauptziel ist es, starke Gegenargumente zur Klageschrift zu finden und möglichst viele Platzhalter sinnvoll auszufüllen. 
Versuche, mindestens 80% aller Platzhalter mit sinnvollen Werten zu füllen. Nur wenn absolut keine passende Information gefunden werden kann, darfst du null als Wert einsetzen.

Die Platzhalter im Template folgen diesem Regex-Muster: {placeholder_regex}
Suche nach allen Textstellen, die diesem Muster entsprechen, und fülle sie mit passenden Werten aus.
"""

    # Add information about placeholder count and null values
    if placeholder_count > 0:
        user_prompt += f"""
Im Template wurden genau {placeholder_count} Platzhalter gefunden. Dein Array MUSS exakt {placeholder_count} Einträge enthalten.
Versuche, mindestens {int(placeholder_count * 0.8)} Platzhalter auszufüllen. Verwende nur für maximal {int(placeholder_count * 0.2)} Platzhalter null-Werte.
Sei kreativ und entwickle starke juristische Gegenargumente, um die Position des Beklagten zu verteidigen.
"""

    user_prompt += f"""
#Klageschrift
{text}

#Template für Klageantwort
{template_text if template_text else ""}
"""
    
    return user_prompt, system_prompt

def get_placeholder_values(
    parsed_json_file: Dict[str, Any], 
    parsed_json_template_file: Optional[Dict[str, Any]] = None, 
    agreed_claims: Optional[List[str]] = None
) -> Tuple[List[Optional[str]], Dict[str, str]]:
    """
    Get placeholder values from OpenAI API based on the provided text.
    
    Args:
        parsed_json_file: Dictionary containing the 'text' field with legal document content
        parsed_json_template_file: Optional dictionary containing template text
        agreed_claims: Optional list of agreed claims
        
    Returns:
        Tuple of (placeholder_values, ai_prompt) where placeholder_values is a list of values 
        and ai_prompt is a dictionary containing the full prompts sent to the AI
    """
    # Extract text from inputs
    text = parsed_json_file.get('text', '')
    placeholder_regex = parsed_json_file.get('placeholder_regex', r'\[\s*•[^\]]*\]')
    template_text = parsed_json_template_file.get('text', '') if parsed_json_template_file else ''
    
    # Extract placeholders
    placeholder_count = count_placeholders(template_text, placeholder_regex)
    
    # Build prompt
    user_prompt, system_prompt = build_prompt(text, template_text, placeholder_regex, placeholder_count)
    
    # Prepare prompt information for return
    prompt_info = {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt
    }
    
    try:
        # Make request to OpenAI with structured outputs
        response = client.responses.parse(
            model="gpt-4o-2024-08-06",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            text_format=PlaceholderValues,
        )
        
        # Return the parsed values and the prompts
        return response.output_parsed.values, prompt_info
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Fall back to mock values if there's an error
        mock_values, _ = get_placeholder_mock_values(parsed_json_file, parsed_json_template_file, agreed_claims)
        prompt_info["error"] = str(e)
        return mock_values, prompt_info

def get_placeholder_mock_values(
    parsed_json_file: Dict[str, Any], 
    parsed_json_template_file: Optional[Dict[str, Any]] = None, 
    agreed_claims: Optional[List[str]] = None
) -> Tuple[List[str], None]:
    """
    Get mock placeholder values.
    
    Args:
        parsed_json_file: Dictionary containing the 'text' field with legal document content
        parsed_json_template_file: Optional dictionary containing template text
        agreed_claims: Optional list of agreed claims
        
    Returns:
        A tuple of (placeholder_values, None) where placeholder_values is a list of mock values
    """
    # Mock values for testing - these should represent typical responses
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