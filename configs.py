LANGUAGES = {
    'en': 'English',
    'ru': 'Russian',
    'uz': 'Uzbek',
    'ko': 'Korean',
    'ja': 'Japanese',
    'zh-cn': 'Chinese',
    'tr': 'Turkish',
    'de': 'Deutsch',
    'ar': 'Arabic',
    'fr': 'French',
    'it': 'Italian',
    'es': 'Spanish'
}

def get_key(value):
    for k, v in LANGUAGES.items():
        if v == value:
            return k

