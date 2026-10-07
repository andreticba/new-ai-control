# evolution_gateway.py | AI-Control SDD v0.6.0 | 03-10-2026 00:15(GMT-04:00)
import os
import requests
from django.conf import settings
from core.models import AuditLog

class EvolutionGatewayService:
    def __init__(self):
        self.api_url = getattr(settings, 'WHATS_GT_API_URL', 'http://localhost:8081')
        self.api_key = getattr(settings, 'WHATS_GT_API_KEY', '')
        self.timeout = getattr(settings, 'WHATS_GT_TIMEOUT', 5)

    def _instance_name(self, org_slug):
        return f"ai_control_{org_slug}"

    def get_or_create_instance(self, org_slug, request=None):
        instance_name = self._instance_name(org_slug)
        url = f"{self.api_url}/instance/connectionState/{instance_name}"
        headers = {"apikey": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass

        # Passo 1: Criar Instância
        create_url = f"{self.api_url}/instance/create"
        create_payload = {
            "instanceName": instance_name,
            "integration": "WHATSAPP-BAILEYS",
            "qrcode": True
        }
        
        try:
            res = requests.post(create_url, json=create_payload, headers=headers, timeout=self.timeout)
            res.raise_for_status()
            created_data = res.json()
        except requests.RequestException as e:
            return {"error": f"Failed to create instance: {str(e)}"}
            
        # Passo 2: Configurar Webhook
        webhook_base = getattr(settings, 'WHATS_GT_WEBHOOK_BASE_URL', '')
        if not webhook_base and request:
            webhook_base = request.build_absolute_uri('/')[:-1]
            
        webhook_url = f"{webhook_base}/api/v1/webhook/whatsapp"
        webhook_set_url = f"{self.api_url}/webhook/set/{instance_name}"
        
        webhook_payload = {
            "webhook": {
                "enabled": True,
                "url": webhook_url,
                "byEvents": True,
                "events": [
                    "APPLICATION_STARTUP", 
                    "QRCODE_UPDATED", 
                    "MESSAGES_UPSERT", 
                    "MESSAGES_UPDATE", 
                    "MESSAGES_DELETE", 
                    "SEND_MESSAGE", 
                    "CONNECTION_UPDATE", 
                    "CALL", 
                    "PRESENCE_UPDATE"
                ]
            }
        }
        
        try:
            res_hook = requests.post(webhook_set_url, json=webhook_payload, headers=headers, timeout=self.timeout)
            res_hook.raise_for_status()
            return created_data
        except requests.RequestException as e:
            # Rollback: deletar a instância que ficou sem webhook
            self.delete_instance(instance_name)
            return {"error": f"Failed to set webhook: {str(e)}"}

    def get_qr_code(self, instance_name):
        url = f"{self.api_url}/instance/connect/{instance_name}"
        headers = {"apikey": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                
                base64 = data.get("base64")
                if not base64 and "qrcode" in data:
                    base64 = data["qrcode"].get("base64")

                if base64:
                    return {"base64": base64}

                state = data.get("instance", {}).get("state") or data.get("instance", {}).get("status")
                if state == "open":
                    return {"connected": True}
                    
                if state == "connecting" or data.get("qrcode", {}).get("count") == 0:
                    return {"error": "QR Code not ready yet", "retry": True}
                    
                return data
        except requests.RequestException:
            pass
        return {"error": "Failed to get QR code"}

    def get_connection_state(self, instance_name):
        url = f"{self.api_url}/instance/connectionState/{instance_name}"
        headers = {"apikey": self.api_key}
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                return response.json().get("instance", {}).get("state", "unknown")
        except requests.RequestException:
            pass
        return "unknown"

    def delete_instance(self, instance_name, actor=None):
        url = f"{self.api_url}/instance/delete/{instance_name}"
        headers = {"apikey": self.api_key}
        try:
            response = requests.delete(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            AuditLog.objects.create(
                action=AuditLog.ActionType.WHATSAPP_INSTANCE_DELETE,
                actor=actor,
                details={"instance_name": instance_name}
            )
            return True
        except requests.RequestException:
            return False

    def send_text_message(self, instance_name, jid, text):
        url = f"{self.api_url}/message/sendText/{instance_name}"
        headers = {"apikey": self.api_key}
        payload = {
            "number": jid,
            "options": {
                "delay": 1200,
                "presence": "composing"
            },
            "text": text
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def send_presence(self, instance_name, jid, state="composing"):
        url = f"{self.api_url}/chat/sendPresence/{instance_name}"
        headers = {"apikey": self.api_key}
        payload = {
            "number": jid,
            "presence": state,
            "delay": 10000
        }
        try:
            requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            return True
        except requests.RequestException:
            return False
