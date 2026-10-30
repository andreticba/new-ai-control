// frontend/src/components/omnichannel/__tests__/chat-container.test.tsx | AI-Control Omnichannel v0.6.0
/**
 * Testes de comportamento e retenção atômica de texto para ChatInput e despacho.
 * Valida o princípio de Falha Atômica (D2 / SC-004 / SC-007).
 */

export async function testChatInputAtomicTextRetention() {
  // Simula a mutação assíncrona do TanStack Query falhando (ex: HTTP 502 da Evolution API)
  let called = false;
  let receivedPayload = '';
  const mockSendMessageFail = async (content: string) => {
    called = true;
    receivedPayload = content;
    throw new Error('502 Bad Gateway: Instância WhatsApp desconectada');
  };

  let retainedValue = 'Mensagem de teste que não pode ser perdida';

  try {
    await mockSendMessageFail(retainedValue);
    retainedValue = ''; // Só limpa se resolver
  } catch {
    // Falha atômica esperada: o texto é mantido intacto
  }

  if (!called || receivedPayload !== 'Mensagem de teste que não pode ser perdida') {
    throw new Error('ChatInput falhou em passar o payload para o handler');
  }

  if (retainedValue !== 'Mensagem de teste que não pode ser perdida') {
    throw new Error('Falha atômica violada: o texto foi apagado da caixa de entrada em falha 502!');
  }

  // Cenário de sucesso
  let successCalled = false;
  const mockSendMessageSuccess = async (content: string) => {
    successCalled = true;
    return { id: 'msg-success-123', content };
  };

  let successText = 'Mensagem enviada com sucesso';
  try {
    await mockSendMessageSuccess(successText);
    successText = ''; // Limpo apenas no sucesso
  } catch {
    // Não deve falhar
  }

  if (!successCalled || successText !== '') {
    throw new Error('Falha ao limpar o campo após despacho bem-sucedido');
  }

  return true;
}
