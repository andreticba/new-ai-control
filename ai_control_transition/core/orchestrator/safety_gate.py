import os

def classify_response(text: str) -> bool:
    """
    Returns True if the response is clinical (requires HITL/Draft), False if general.
    """
    clinical_keywords = os.environ.get('CLINICAL_KEYWORDS', 'sintoma,dor,remédio,tratamento,diagnóstico,paracetamol,médico').split(',')
    
    text_lower = text.lower()
    for kw in clinical_keywords:
        if kw.strip() and kw.strip() in text_lower:
            return True
            
    return False
