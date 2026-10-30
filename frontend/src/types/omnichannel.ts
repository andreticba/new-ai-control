// frontend/src/types/omnichannel.ts | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:53:00(GMT-04:00)

export type ContactStatus = 'PLATFORM_LEAD' | 'CUSTOMER_LEAD' | 'PROSPECT' | 'CLIENT' | 'ARCHIVED';

export type ConversationStatus = 'ACTIVE_AI' | 'ACTIVE_HUMAN' | 'CLOSED';

export type DeliveryStatus = 'PENDING' | 'SENT' | 'DELIVERED' | 'READ' | 'FAILED';

export type MessageDirection = 'INBOUND' | 'OUTBOUND';

export type MediaType = 'text' | 'image' | 'audio' | 'video' | 'document' | 'sticker';

export type CopilotDraftStatus = 'PENDING' | 'APPROVED' | 'DISCARDED';

export type ConversationFilterTab = 'all' | 'unread' | 'ai' | 'mine' | 'pinned';

/**
 * Contato com blindagem total de PII (LGPD Art. 13 e 46).
 * Telefones são expressamente omitidos para o operador.
 */
export interface OmnichannelContact {
  id: string;
  display_name: string;
  avatar_url: string | null;
  status: ContactStatus;
}

export interface QuotedMessageSummary {
  id: string;
  content: string;
  media_type?: MediaType;
  timestamp?: string;
}

export interface OmnichannelMessage {
  id: string;
  external_id?: string | null;
  direction: MessageDirection;
  content: string;
  sent_by_ai: boolean;
  delivery_status: DeliveryStatus;
  is_read: boolean;
  read_at?: string | null;
  media_type: MediaType;
  media_url?: string | null;
  media_mimetype?: string | null;
  media_duration?: number | null;
  sender_user_id?: string | null;
  sender_name?: string | null;
  quoted_message?: QuotedMessageSummary | null;
  timestamp: string;
  created_at?: string;
}

export interface LastMessagePreview {
  id?: string | null;
  content: string;
  direction: MessageDirection;
  timestamp: string | null;
  delivery_status?: DeliveryStatus;
  media_type?: MediaType;
}

export interface OmnichannelConversation {
  id: string;
  contact: OmnichannelContact;
  status: ConversationStatus;
  access_level: string;
  unread_count: number;
  is_pinned: boolean;
  channel_type: string;
  instance_name?: string | null;
  last_message?: LastMessagePreview | null;
  tags: string[];
  assigned_user_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CopilotDraft {
  id: string;
  conversation_id: string;
  trigger_message_id?: string | null;
  suggested_content: string;
  final_sent_content?: string | null;
  status: CopilotDraftStatus;
  generated_by_model: string;
  latency_ms: number;
  created_at: string;
  updated_at: string;
}

export interface OmnichannelWebSocketMessage {
  event: 'conversation.message.new' | 'conversation.message.status_updated' | 'copilot.draft.generated' | 'conversation.status.updated' | 'pong';
  data?: any;
}
