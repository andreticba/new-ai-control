import os
import json
import redis
from cryptography.fernet import Fernet
from core.models import ConversationTurn

redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

def get_fernet():
    key = os.environ.get('CONTEXT_ENCRYPTION_KEY')
    if not key:
        # Default key for development only
        key = b'8U2mI4g2o0R6H7W2eM1aA5o3F4s9E0r6N7t2I4u8H1c='
    return Fernet(key)

def load_context(org_id: str, session_id: str) -> list[dict]:
    """
    Load context from Redis. If miss, load from DB and populate Redis.
    """
    cache_key = f"context:{org_id}:{session_id}"
    encrypted_data = redis_client.get(cache_key)
    
    if encrypted_data:
        f = get_fernet()
        data_json = f.decrypt(encrypted_data).decode('utf-8')
        return json.loads(data_json)
        
    # Fallback to DB
    turns = ConversationTurn.objects.filter(session_id=session_id).order_by('created_at')[:20]
    context = []
    for t in turns:
        context.append({
            'direction': t.direction,
            'text': t.message_text
        })
        
    if context:
        save_context(org_id, session_id, context)
        
    return context

def save_context(org_id: str, session_id: str, turns: list[dict]):
    """
    Save context to Redis encrypted.
    """
    cache_key = f"context:{org_id}:{session_id}"
    f = get_fernet()
    data_json = json.dumps(turns)
    encrypted_data = f.encrypt(data_json.encode('utf-8'))
    
    ttl = int(os.environ.get('SESSION_CONTEXT_TTL_SECONDS', 3600))
    redis_client.set(cache_key, encrypted_data, ex=ttl)
