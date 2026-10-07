# debug_views.py | Atualizado em: 02-10-2026 13:35:45(GMT-04:00)
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods

@staff_member_required
@require_http_methods(["GET"])
def whatsgt_debug_view(request):
    """
    Renderiza o template de debug no Django Admin.
    """
    return render(request, "admin/whatsgt_debug.html", {
        "title": "Debug: Pareamento QR Code & Mensagens"
    })
