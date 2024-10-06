from pydantic import BaseModel

class TranslateRequest(BaseModel):
    text: str
    source_lang: str = 'auto'
    target_lang: str = 'en'