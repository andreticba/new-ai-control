<!-- api_contracts.md | Vitalia SDD v0.6.0 | 11-10-2026 20:45(GMT-04:00) -->
**api_contracts.md | AI-Control v0.0.1 | 11-10-2026 20:45(GMT-04:00)**

# Contratos de API: Frontend v1 & API Gateway Síncrono

Este documento formaliza as assinaturas, payloads, códigos HTTP e requisitos de segurança para os endpoints da Frente Síncrona da API.

---

## 1. `POST /api/v1/auth/token/`
Emissão inicial do par de tokens JWT (Access e Refresh) para autenticação do usuário.

- **Autenticação**: Nenhuma (`AllowAny`)
- **Headers**:
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "username": "prof.ana",
    "password": "demo1234"
  }
  ```
- **Response 200 OK**:
  ```json
  {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Erros**:
  - `401 Unauthorized`: `{"detail": "No active account found with the given credentials"}`

---

## 2. `POST /api/v1/auth/token/refresh/`
Renovação do token de acesso expirado utilizando o refresh token persistido.

- **Autenticação**: Nenhuma (`AllowAny`)
- **Headers**:
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Response 200 OK**:
  ```json
  {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Erros**:
  - `401 Unauthorized`: `{"detail": "Token is invalid or expired", "code": "token_not_valid"}`

---

## 3. `GET /api/v1/users/me/`
Recuperação dos dados de perfil e escopo do usuário autenticado (BFF agregado para inicialização da UI).

- **Autenticação**: `Bearer <token>` (`IsAuthenticated`)
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Response 200 OK**:
  ```json
  {
    "id": 1,
    "username": "prof.ana",
    "email": "prof.ana@example.org",
    "full_name": "Profa. Ana Santos",
    "primary_organization": {
      "id": "e8d648b2-5f6a-4d7a-8d1a-2895f32b85cf",
      "name": "Universidade Federal Demo",
      "slug": "ufdemo"
    },
    "platform_role": null,
    "memberships": {
      "organization": {
        "role": "org_member",
        "job_title": "Professor",
        "department": "DCOMP"
      },
      "projects": [
        {
          "project_id": "8a729e21-0a63-4c91-b3f2-1a4c85671bc4",
          "project_slug": "saude-digital",
          "project_name": "Saúde Digital na Comunidade",
          "role": "project_lead",
          "job_title": "Coordenador(a) do Projeto"
        },
        {
          "project_id": "5f1348c9-9b21-4f11-a832-7e19ca94210d",
          "project_slug": "ia-triagem",
          "project_name": "IA para Triagem Clínica",
          "role": "project_member",
          "job_title": "Pesquisador(a) Colaborador(a)"
        }
      ],
      "squads": [
        {
          "squad_id": "4b192837-7d61-4192-9a84-82a1736491bc",
          "squad_slug": "app-movel",
          "squad_name": "Squad App Móvel",
          "role": "squad_lead",
          "job_title": "Tech Lead"
        }
      ]
    }
  }
  ```
- **Erros**:
  - `401 Unauthorized`: Token ausente ou inválido.

---

## 4. `GET /api/v1/workspaces/`
Árvore completa dos 4 níveis hierárquicos acessíveis ao usuário para composição do dashboard, menus de contexto e navegação lateral.

- **Autenticação**: `Bearer <token>` (`IsAuthenticated`)
- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Response 200 OK**:
  ```json
  {
    "workspaces": [
      {
        "id": "e8d648b2-5f6a-4d7a-8d1a-2895f32b85cf",
        "name": "Universidade Federal Demo",
        "slug": "ufdemo",
        "org_type": "ACADEMIC",
        "role": "org_member",
        "job_title": "Professor",
        "departments": [
          {
            "id": "1a2b3c4d-...",
            "name": "Departamento de Computação",
            "slug": "dcomp",
            "code": "DCOMP"
          }
        ],
        "projects": [
          {
            "id": "8a729e21-0a63-4c91-b3f2-1a4c85671bc4",
            "name": "Saúde Digital na Comunidade",
            "slug": "saude-digital",
            "role": "project_lead",
            "job_title": "Coordenador(a) do Projeto",
            "squads": [
              {
                "id": "4b192837-7d61-4192-9a84-82a1736491bc",
                "name": "Squad App Móvel",
                "slug": "app-movel",
                "role": "squad_lead",
                "job_title": "Tech Lead"
              }
            ]
          }
        ]
      }
    ]
  }
  ```
- **Erros**:
  - `401 Unauthorized`: Token ausente ou inválido.

---

## 5. `GET /api/schema/`
Contrato OpenAPI 3.0 dinâmico gerado pelo `drf-spectacular` para extração de tipos do frontend.

- **Autenticação**:
  - Em desenvolvimento (`DEBUG=True`): Pública (`AllowAny`).
  - Em produção (`DEBUG=False`): Privada (`IsAdminUser` com `Authorization: Bearer <token_admin>`).
- **Response 200 OK**:
  - `Content-Type: application/vnd.oai.openapi+json` (ou `application/yaml` via format query).
  - Objeto OpenAPI 3.0 formal contendo components, securitySchemes e rotas documentadas.
- **Erros**:
  - Em produção sem token admin: `401 Unauthorized` ou `403 Forbidden`.
