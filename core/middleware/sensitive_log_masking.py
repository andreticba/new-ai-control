import urllib.parse
from typing import Callable
from django.http import HttpRequest, HttpResponse


SENSITIVE_PARAM_NAMES = {
    'apikey',
    'api_key',
    'token',
    'access_token',
    'refresh_token',
    'secret',
    'client_secret',
    'password',
    'pass',
    'authorization',
}


def mask_sensitive_query_string(query_string: str) -> str:
    """
    Substitui o valor de parâmetros sensíveis por [REDACTED] em uma query string,
    preservando parâmetros não sensíveis.
    """
    if not query_string:
        return query_string

    parsed_pairs = urllib.parse.parse_qsl(query_string, keep_blank_values=True)
    sanitized_pairs = []

    for key, val in parsed_pairs:
        if key.lower() in SENSITIVE_PARAM_NAMES:
            sanitized_pairs.append((key, '[REDACTED]'))
        else:
            sanitized_pairs.append((key, val))

    return urllib.parse.urlencode(sanitized_pairs)


class SensitiveLogMaskingMiddleware:
    """
    Middleware no topo do pipeline HTTP para higienização e prevenção de vazamento
    de credenciais em logs de servidores de aplicação (Daphne/Django).
    
    1. Intercepta parâmetros sensíveis em query strings (ex: ?apikey=...).
    2. Como fallback para compatibilidade legada, se 'apikey' estiver na query string
       e não houver cabeçalho HTTP_APIKEY, injeta o valor original em request.META['HTTP_APIKEY'].
    3. Mascara request.META['QUERY_STRING'] com '[REDACTED]' antes que qualquer log ou
       processamento subsequente ocorra.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        raw_query = request.META.get('QUERY_STRING', '')

        if raw_query:
            # Fallback seguro para headers nativos: se apikey estiver na query e não no header,
            # garante injeção no cabeçalho antes de sanitizar a query string
            parsed_pairs = urllib.parse.parse_qsl(raw_query, keep_blank_values=True)
            for k, v in parsed_pairs:
                if k.lower() == 'apikey' and v and 'HTTP_APIKEY' not in request.META:
                    request.META['HTTP_APIKEY'] = v

            # Higieniza request.META['QUERY_STRING']
            request.META['QUERY_STRING'] = mask_sensitive_query_string(raw_query)

        return self.get_response(request)
