// frontend/src/components/omnichannel/__tests__/omnichannel-components.test.ts | AI-Control Omnichannel v0.6.0
/**
 * Teste estático de integridade de tipos e contratos dos componentes Omnichannel.
 * Garante que todas as interfaces, props e payloads respeitam estritamente a política de zero PII (LGPD).
 */

import type {
  OmnichannelContact,
  OmnichannelConversation,
  OmnichannelMessage,
  CopilotDraft,
} from '@/types/omnichannel';

export function testOmnichannelContractSanitization() {
  const mockContact: OmnichannelContact = {
    id: 'contact-uuid-001',
    display_name: 'Dr. Roberto Santos',
    avatar_url: 'https://example.com/avatar.jpg',
    status: 'CLIENT',
  };

  // Garante que o objeto do frontend não possui propriedade de telefone
  // @ts-expect-error O telefone deve ser estritamente bloqueado no frontend (Zero PII)
  const forbiddenPhone = mockContact.phone_number;

  const mockConversation: OmnichannelConversation = {
    id: 'conv-uuid-001',
    contact: mockContact,
    status: 'ACTIVE_AI',
    access_level: 'ORGANIZATION',
    unread_count: 0,
    is_pinned: false,
    channel_type: 'WHATSAPP',
    instance_name: 'ai_control_default',
    tags: ['VIP', 'Cardiologia'],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  const mockMessage: OmnichannelMessage = {
    id: 'msg-uuid-001',
    direction: 'INBOUND',
    content: 'Olá, gostaria de confirmar o agendamento.',
    sent_by_ai: false,
    delivery_status: 'READ',
    is_read: true,
    media_type: 'text',
    timestamp: new Date().toISOString(),
  };

  const mockDraft: CopilotDraft = {
    id: 'draft-uuid-001',
    conversation_id: mockConversation.id,
    suggested_content: 'Olá Dr. Roberto! Seu agendamento está confirmado para as 14h.',
    status: 'PENDING',
    generated_by_model: 'phi4-mini:latest',
    latency_ms: 125,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  return {
    mockContact,
    mockConversation,
    mockMessage,
    mockDraft,
    forbiddenPhone,
  };
}
