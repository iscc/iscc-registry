from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect
from iscc_registry.models import IsccId
import iscc_core as ic


def index(request):
    return render(request, "index.html")


def resolver(request, iscc_id):
    """Resolve ISCC-ID"""
    # Validate ISCC string
    try:
        norm = ic.iscc_normalize(iscc_id)
        ic.iscc_validate(norm)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))

    # Fetch from database
    try:
        iscc_obj = IsccId.get_safe(iscc_id=norm.lstrip("ISCC:"))
    except IsccId.DoesNotExist:
        return HttpResponseNotFound(f"{iscc_id} not found.")

    # Resolve if we can
    if iscc_obj.metadata:
        url = iscc_obj.metadata.get("redirect")
        if url:
            return redirect(url, permanent=False)

    # Redirect to local entry
    return redirect(iscc_obj.get_registry_url(), permanent=False)
