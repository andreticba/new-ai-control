from _lab_base import run_lab, load_mock_personas
from core.models import Document, DocumentChunk, UserProfile
from django.contrib.auth.models import User
from pgvector.django import CosineDistance

def lab_rag():
    org_uf, _ = load_mock_personas()
    prof, _ = User.objects.get_or_create(username="prof.ana.lab3", defaults={"email": "prof.ana3@example.org"})
    UserProfile.objects.get_or_create(user=prof)
    
    # Fake embedding 768d
    fake_embedding_1 = [0.1] * 768
    fake_embedding_2 = [0.2] * 768

    doc1, _ = Document.objects.get_or_create(
        organization=org_uf,
        uploaded_by_user=prof,
        file_name="Orcamento_Publico.pdf",
        defaults={
            "visibility": Document.Visibility.ORGANIZATION,
            "ai_accessible": True
        }
    )
    
    DocumentChunk.objects.get_or_create(
        document=doc1,
        organization=org_uf,
        content="Dados do orçamento da organização",
        defaults={"embedding": fake_embedding_1}
    )

    doc2, _ = Document.objects.get_or_create(
        organization=org_uf,
        uploaded_by_user=prof,
        file_name="Notas_Pessoais_Sigilosas.pdf",
        defaults={
            "visibility": Document.Visibility.SQUAD,
            "ai_accessible": False
        }
    )
    
    DocumentChunk.objects.get_or_create(
        document=doc2,
        organization=org_uf,
        content="Documento não acessível à IA",
        defaults={"embedding": fake_embedding_2}
    )

    print("--- Busca Vetorial ORM (Design de Referência) ---")
    query_vector = [0.15] * 768
    
    # Filtro rígido onde o isolamento acontece
    # O documento precisa ter ai_accessible=True
    chunks = DocumentChunk.objects.filter(
        organization=org_uf,
        document__ai_accessible=True,
        document__visibility__in=[Document.Visibility.ORGANIZATION]
    ).order_by(CosineDistance('embedding', query_vector))[:5]
    
    for c in chunks:
        print(f"Match: {c.document.file_name} | Content: {c.content}")

if __name__ == '__main__':
    run_lab(lab_rag)
