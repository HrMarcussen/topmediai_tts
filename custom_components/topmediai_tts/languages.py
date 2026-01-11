"""Language mapping for TopMediaAI."""

# Map API "Languagename" to HA ISO codes
LANGUAGE_MAP = {
    "English": "en-US",
    "Chinese": "zh-CN",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "Portuguese": "pt-PT",
    "German": "de-DE",
    "Indonesian": "id-ID",
    "Japanese": "ja-JP",
    "Russian": "ru-RU",
    "Korean": "ko-KR",
    "Italian": "it-IT",
    "Dutch": "nl-NL",
    "Turkish": "tr-TR",
    "Polish": "pl-PL",
    "Swedish": "sv-SE",
    "Bulgarian": "bg-BG",
    "Romanian": "ro-RO",
    "Arabic": "ar-SA",
    "Czech": "cs-CZ",
    "Greek": "el-GR",
    "Finnish": "fi-FI",
    "Croatian": "hr-HR",
    "Malay": "ms-MY",
    "Slovak": "sk-SK",
    "Danish": "da-DK",
    "Tamil": "ta-IN",
    "Ukrainian": "uk-UA",
    "Norwegian": "nb-NO",
    "Hindi": "hi-IN",
    "Thai": "th-TH",
    "Vietnamese": "vi-VN",
    "Filipino": "fil-PH",
    "Azerbaijani": "az-AZ",
    "Hungarian": "hu-HU",
    # Add more as discovered or needed
}

def get_iso_code(api_language_name):
    """Get the ISO code for a given API language name."""
    if not api_language_name:
        return "en-US"
    
    # Try direct match
    if api_language_name in LANGUAGE_MAP:
        return LANGUAGE_MAP[api_language_name]
        
    # Try fuzzy match? (e.g. "English (US)" -> "en-US")
    # For now, just return en-US fallback or the name itself if it looks like a code
    if "-" in api_language_name:
        return api_language_name
        
    return "en-US"
