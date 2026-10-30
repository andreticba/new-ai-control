import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from core.middleware.sensitive_log_masking import SensitiveLogMaskingMiddleware, mask_sensitive_query_string


@pytest.fixture
def dummy_response():
    return HttpResponse("OK", status=200)


@pytest.fixture
def middleware(dummy_response):
    return SensitiveLogMaskingMiddleware(get_response=lambda req: dummy_response)


@pytest.fixture
def rf():
    return RequestFactory()


def test_mask_sensitive_query_string_unit():
    """Testa a função isolada de sanitização de query string."""
    qs = "page=2&apikey=supersecret123&user=john&token=jwt_abc_xyz&password=mypassword&secret=topsecret"
    masked = mask_sensitive_query_string(qs)
    
    assert "page=2" in masked
    assert "user=john" in masked
    assert "supersecret123" not in masked
    assert "jwt_abc_xyz" not in masked
    assert "mypassword" not in masked
    assert "topsecret" not in masked
    assert "apikey=%5BREDACTED%5D" in masked or "apikey=[REDACTED]" in masked
    assert "token=%5BREDACTED%5D" in masked or "token=[REDACTED]" in masked


def test_mask_sensitive_query_string_case_insensitive():
    """Garante que parâmetros em maiúsculas ou minúsculas sejam mascarados."""
    qs = "APIKEY=12345&Token=mytoken&PASSWORD=segredo_pessoal&client_secret=999"
    masked = mask_sensitive_query_string(qs)
    
    assert "12345" not in masked
    assert "mytoken" not in masked
    assert "segredo_pessoal" not in masked
    assert "999" not in masked


def test_mask_sensitive_query_string_without_sensitive_params():
    """Garante que query string sem dados sensíveis não seja alterada."""
    qs = "search=relatorio&status=open&page=1"
    masked = mask_sensitive_query_string(qs)
    assert "search=relatorio" in masked
    assert "status=open" in masked
    assert "page=1" in masked


def test_middleware_masks_query_string_in_request_meta(rf, middleware):
    """Garante que o middleware modifica request.META['QUERY_STRING']."""
    request = rf.get("/api/v1/gateway/webhook?apikey=segredo_mestre_123&event=messages.upsert")
    
    assert "segredo_mestre_123" in request.META["QUERY_STRING"]
    
    response = middleware(request)
    assert response.status_code == 200
    
    # O segredo não pode mais constar em QUERY_STRING
    assert "segredo_mestre_123" not in request.META["QUERY_STRING"]
    assert "[REDACTED]" in request.META["QUERY_STRING"] or "%5BREDACTED%5D" in request.META["QUERY_STRING"]


def test_middleware_preserves_apikey_in_headers_if_missing(rf, middleware):
    """
    Se a apikey for enviada na query string por compatibilidade legada,
    o middleware mascara a query string e injeta no cabeçalho HTTP_APIKEY
    para que as views autentiquem sem vazar o segredo nos logs do servidor.
    """
    request = rf.get("/api/v1/gateway/webhook?apikey=chave_legada_123")
    
    assert "HTTP_APIKEY" not in request.META
    
    middleware(request)
    
    assert request.META.get("HTTP_APIKEY") == "chave_legada_123"
    assert "chave_legada_123" not in request.META["QUERY_STRING"]


def test_middleware_does_not_overwrite_existing_http_apikey(rf, middleware):
    """Se o header HTTP_APIKEY já existir, ele é respeitado e preservado."""
    request = rf.get(
        "/api/v1/gateway/webhook?apikey=chave_ignorada",
        HTTP_APIKEY="chave_principal_header"
    )
    
    middleware(request)
    
    assert request.META.get("HTTP_APIKEY") == "chave_principal_header"
    assert "chave_ignorada" not in request.META["QUERY_STRING"]
