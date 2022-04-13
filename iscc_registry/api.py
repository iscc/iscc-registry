"""
## Public features:

- resolve ISCC-IDs to their redirection target
- retrieve declaration metadata for an ISCC-ID
- find ISCC-IDs for a given ISCC-CODE

## Administrative features:
- Allow chain observers to sync ISCC declarations to the registry.
"""
from typing import Optional, Any
from django.http import HttpRequest
from django.shortcuts import redirect
from django_simple_task import defer
from ninja import NinjaAPI
from ninja.errors import HttpError

from iscc_registry import settings
from iscc_registry.exceptions import RegistrationError
from iscc_registry import schema as s
from iscc_registry.models import IsccIdModel
from iscc_registry.schema import Head, Message, RegistrationResponse, Declaration
from iscc_registry.transactions import rollback, register
from ninja.security import HttpBearer
import iscc_core as ic

from iscc_registry.tasks import fetch_metadata


class ObserverAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[Any]:
        if token == settings.OBSERVER_TOKEN:
            return token


api = NinjaAPI(
    title="ISCC - Registry API", version=s.API_VERSION, description=__doc__, auth=ObserverAuth()
)


####################################################################################################
# Public endpoints                                                                                 #
####################################################################################################


@api.get("", tags=["public"], response=s.API, auth=None)
def index(request):
    """Returns current API information."""
    return {}


@api.get("/resolve/{iscc}", tags=["public"], auth=None)
def resolve(request, iscc: str):
    try:
        ic.iscc_validate(ic.iscc_normalize(iscc), strict=True)
    except ValueError as e:
        raise HttpError(400, str(e))

    return redirect("https://example.com", permanent=False)


####################################################################################################
# Private observer endpoints                                                                       #
####################################################################################################


@api.get("/head/{chain_id}", tags=["observer"], response={200: Head, 404: Message})
def head(request, chain_id: int):
    """Return block header of the latest registration event for given chain."""
    obj = IsccIdModel.objects.filter(chain_id=chain_id).order_by("did").last()
    if not obj:
        return 404, Message(message="No registrations found for chain")
    return 200, obj


@api.post("/register", tags=["observer"], response={201: RegistrationResponse, 422: Message})
def register_(request, declartion: Declaration):
    """Register an on-chain ISCC-Declaration for ISCC-ID minting."""
    try:
        iid_obj = register(declartion)
        defer(fetch_metadata, arguments={"args": [iid_obj.did]})
        return 201, iid_obj
    except RegistrationError as e:
        return 422, Message(message=str(e))


@api.post("/rollback/{block_hash}", tags=["observer"], response={200: Head, 404: Message})
def rollback_(request, block_hash: str):
    """Rollback events to state before `block_hash`"""
    return rollback(block_hash)
