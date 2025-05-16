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

def build_prompt(text: str, template_text: str, placeholder_regex: str, placeholder_count: int) -> str:
    system_prompt = (
        "Du bist ein erfahrener Rechtsanwalt in der Schweiz. Basierend auf dem folgenden Klageschrift, "
        "erstelle eine detaillierte juristische Gegenargmentation in deutscher Sprache.\n\n"
        "Strukturiere deine Antwort in drei Hauptteile:\n\n"
        "1. Allgemeine Gegenargumente (counter):\n"
        "- Zentrale Schwachstellen der Klage identifizieren\n" 
        "- Hauptargumente der Gegenseite widerlegen\n"
        "- Strategische Verteidigungsposition aufbauen\n\n"
        "2. Formelle Aspekte (formelles):\n"
        "- Zuständigkeit des Gerichts prüfen\n"
        "- Prozessvoraussetzungen analysieren\n" 
        "- Formelle Mängel der Klage aufzeigen\n"
        "- Fristen und Verfahrensabläufe prüfen\n\n"
        "3. Materielle Aspekte (materielles):\n"
        "- Detaillierte rechtliche Würdigung der Ansprüche\n"
        "- Beweislast und Beweismittel analysieren\n"
        "- Materielle Einwendungen und Einreden\n"
        "- Rechtliche Grundlagen und Präzedenzfälle\n\n"
        "Formatiere die Antwort als JSON-Objekt mit exakt dieser Struktur:\n"
        '{\n  "counter": "Allgemeine Gegenargumente hier",\n'
        '  "formelles": "Formelle Aspekte hier",\n'
        '  "materielles": "Materielle Aspekte hier"\n}\n\n'
        "Wichtige Hinweise:\n"
        "- Verwende präzise juristische Fachsprache\n"
        "- Zitiere relevante Gesetzesartikel\n"
        "- Beziehe dich spezifisch auf den Sachverhalt\n"
        "- Fokussiere auf eine starke Verteidigungsposition\n"
        "- Argumentiere sachlich und professionell\n\n"
        "#Klageschrift:\n"
    )

    system_prompt += f"{text}\n\n"
    return system_prompt

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