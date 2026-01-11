"""Language mapping for TopMediaAI."""

# Map API "Languagename" to HA ISO codes
LANGUAGE_MAP = {
    # Common Languages
    "Arabic": "ar-SA",
    "Arabic (Gulf)": "ar-AE",
    "Chinese": "zh-CN",
    "Chinese(Cantonese)": "zh-HK",
    "Chinese(Mandarin, Taiwan)": "zh-TW", 
    "Chinese(Wu, Shanghainese)": "wuu-CN",
    "Czech": "cs-CZ",
    "Danish": "da-DK",
    "Dutch": "nl-NL",
    "Dutch(Belgium)": "nl-BE",
    "English": "en-US",
    "English(Australia)": "en-AU",
    "English(Canada)": "en-CA",
    "English(India)": "en-IN",
    "English(Ireland)": "en-IE",
    "English(New Zealand)": "en-NZ",
    "English(Philippines)": "en-PH",
    "English(South Africa)": "en-ZA",
    "English(UK)": "en-GB",
    "English(US)": "en-US",
    "Filipino": "fil-PH",
    "Finnish": "fi-FI",
    "French": "fr-FR",
    "French(Belgium)": "fr-BE",
    "French(Canada)": "fr-CA",
    "French(Switzerland)": "fr-CH",
    "German": "de-DE",
    "German(Austria)": "de-AT",
    "German(Switzerland)": "de-CH",
    "Greek": "el-GR",
    "Hebrew": "he-IL",
    "Hindi": "hi-IN",
    "Hungarian": "hu-HU",
    "Indonesian": "id-ID",
    "Italian": "it-IT",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Malay": "ms-MY",
    "Norwegian": "nb-NO",
    "Polish": "pl-PL",
    "Portuguese": "pt-PT",
    "Portuguese(Brazil)": "pt-BR",
    "Romanian": "ro-RO",
    "Russian": "ru-RU",
    "Slovak": "sk-SK",
    "Spanish": "es-ES",
    "Spanish(Mexico)": "es-MX",
    "Spanish(US)": "es-US",
    "Swedish": "sv-SE",
    "Thai": "th-TH",
    "Turkish": "tr-TR",
    "Ukrainian": "uk-UA",
    "Vietnamese": "vi-VN",
    
    # Other Languages found in API
    "Afrikaans": "af-ZA",
    "Albanian": "sq-AL",
    "Amharic": "am-ET",
    "Armenian": "hy-AM",
    "Azerbaijani": "az-AZ",
    "Bengali": "bn-IN",
    "Bosnian": "bs-BA",
    "Bulgarian": "bg-BG",
    "Burmese": "my-MM",
    "Catalan": "ca-ES",
    "Croatian": "hr-HR",
    "Estonian": "et-EE",
    "Galician": "gl-ES",
    "Georgian": "ka-GE",
    "Gujarati": "gu-IN",
    "Icelandic": "is-IS",
    "Irish": "ga-IE",
    "Javanese": "jv-ID",
    "Kannada": "kn-IN",
    "Kazakh": "kk-KZ",
    "Khmer": "km-KH",
    "Lao": "lo-LA",
    "Latvian": "lv-LV",
    "Lithuanian": "lt-LT",
    "Macedonian": "mk-MK",
    "Malayalam": "ml-IN",
    "Maltese": "mt-MT",
    "Marathi": "mr-IN",
    "Mongolian": "mn-MN",
    "Nepali": "ne-NP",
    "Pashto": "ps-AF",
    "Persian": "fa-IR",
    "Punjabi": "pa-IN",
    "Serbian": "sr-RS",
    "Sinhala": "si-LK",
    "Slovenian": "sl-SI",
    "Somali": "so-SO",
    "Sundanese": "su-ID",
    "Swahili": "sw-KE",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Urdu": "ur-PK",
    "Uzbek": "uz-UZ",
    "Welsh": "cy-GB",
    "Zulu": "zu-ZA",
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
