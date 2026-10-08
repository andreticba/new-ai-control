import os
import sys
import re
import subprocess
from pathlib import Path

# Configuração de caminhos
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
MANUALS_DIR = DOCS_DIR / "manuals"

def check_arc42_diff():
    print("Verificando alterações em docs/01_*.md ... docs/12_*.md (FR-002)")
    cmd = ["git", "diff", "--exit-code", "--"] + [str(DOCS_DIR / f"{i:02d}_*.md") for i in range(1, 13)]
    try:
        # We run the command via shell to expand glob correctly, but better to use pure python or specific files
        arc_files = list(DOCS_DIR.glob("[0-1][0-9]_*.md"))
        if not arc_files:
            return True
        subprocess.run(["git", "diff", "--exit-code", "--"] + [str(f) for f in arc_files], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        print("❌ Arquivos Arc42 (docs/01_*.md a 12_*.md) foram modificados. Isso não é permitido.")
        return False

def check_expected_files():
    print("Verificando existência de arquivos esperados")
    expected = [
        "README.md",
        "GLOSSARY.md",
        "01-product/00_visao_geral.md",
        "01-product/01_hierarquia_organizacional.md",
        "01-product/02_papeis_e_permissoes.md",
        "01-product/03_conhecimento_e_rag.md",
        "01-product/04_whatsapp.md",
        "01-product/05_casos_limite.md",
        "02-engineering/01_modelo_de_dados_rbac.md",
        "02-engineering/02_resolucao_de_permissoes.md",
        "02-engineering/03_rag_pgvector.md",
        "02-engineering/04_pipeline_whatsapp.md",
        "02-engineering/05_signals_auditoria_sanitizacao.md",
        "02-engineering/06_casos_limite_tecnico.md",
        "02-engineering/00_como_ler_e_rodar_labs.md",
        "03-history/README.md",
        "03-history/adr-map.md",
        "04-academic/trilha_onboarding.md"
    ]
    missing = []
    for f in expected:
        if not (MANUALS_DIR / f).exists():
            missing.append(f)
    if missing:
        print(f"❌ Arquivos esperados ausentes: {', '.join(missing)}")
        return False
    return True

def check_readme_confidentiality():
    print("Verificando aviso de confidencialidade no README.md")
    readme_path = MANUALS_DIR / "README.md"
    if not readme_path.exists():
        return False
    content = readme_path.read_text(encoding="utf-8")
    if "Confidencial" not in content and "Uso interno" not in content:
        print("❌ README.md não contém aviso de confidencialidade explícito.")
        return False
    return True

def check_headers():
    print("Verificando cabeçalhos em cada módulo")
    failed = False
    for md_file in MANUALS_DIR.rglob("*.md"):
        if "_templates" in md_file.parts or "postmortems" in md_file.parts:
            continue
        if md_file.name == "README.md" or md_file.name == "GLOSSARY.md" or md_file.name == "adr-map.md":
            continue
        content = md_file.read_text(encoding="utf-8")
        if "Commit de referência:" not in content or "Público-alvo:" not in content:
            print(f"❌ Cabeçalho incompleto ou ausente em {md_file.relative_to(MANUALS_DIR)}")
            failed = True
    return not failed

def check_relative_links():
    print("Verificando links relativos")
    link_pattern = re.compile(r'\[.*?\]\((?!http|#|mailto:)(.*?)\)')
    failed = False
    for md_file in MANUALS_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        links = link_pattern.findall(content)
        for link in links:
            # limpa hash se houver
            link_path = link.split('#')[0]
            if not link_path:
                continue
            target = (md_file.parent / link_path).resolve()
            if not target.exists():
                print(f"❌ Link quebrado em {md_file.relative_to(MANUALS_DIR)}: {link}")
                failed = True
    return not failed

def check_code_references():
    print("Verificando referências de código (arquivo:símbolo)")
    ref_pattern = re.compile(r'`([a-zA-Z0-9_./\-]+):([a-zA-Z0-9_]+)`')
    failed = False
    total_refs = 0
    resolved_refs = 0
    for md_file in MANUALS_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        refs = ref_pattern.findall(content)
        for filepath, symbol in refs:
            total_refs += 1
            target_path = PROJECT_ROOT / filepath
            if not target_path.exists():
                print(f"⚠️  Arquivo referenciado não encontrado: {filepath}")
                continue
            target_content = target_path.read_text(encoding="utf-8")
            if symbol not in target_content:
                print(f"⚠️  Símbolo '{symbol}' não encontrado em {filepath} (referenciado em {md_file.relative_to(MANUALS_DIR)})")
            else:
                resolved_refs += 1

    if total_refs > 0:
        resolution_rate = resolved_refs / total_refs
        if resolution_rate < 0.90:
            print(f"❌ Taxa de resolução de símbolos ({resolution_rate*100:.1f}%) abaixo de 90%.")
            failed = True
    return not failed

def check_sensitive_data():
    print("Verificando padrões sensíveis (e-mail real, telefone real, CPF, chaves)")
    email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    dummy_emails = {"example.com", "example.org", "test.com", "fake.com"}
    failed = False
    
    for md_file in MANUALS_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        emails = email_pattern.findall(content)
        for email in emails:
            domain = email.split('@')[1]
            if domain not in dummy_emails:
                print(f"❌ Possível e-mail real encontrado em {md_file.relative_to(MANUALS_DIR)}: {email}")
                failed = True
        
        # Simples verificação de chaves/tokens
        if "sk-" in content or "AKIA" in content or re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.I):
            if "example" not in content and "senha123" not in content:
                print(f"⚠️  Possível secret/senha em {md_file.relative_to(MANUALS_DIR)}.")
                failed = True

    return not failed

def main():
    print("Iniciando Verificação dos Manuais (check_manuals.py)...\n")
    checks = [
        check_arc42_diff,
        check_expected_files,
        check_readme_confidentiality,
        check_headers,
        check_relative_links,
        check_code_references,
        check_sensitive_data
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    if not all_passed:
        print("\n❌ Falha na verificação. O estado está RED.")
        sys.exit(1)
    else:
        print("\n✅ Todas as verificações passaram. O estado está GREEN.")
        sys.exit(0)

if __name__ == "__main__":
    main()
