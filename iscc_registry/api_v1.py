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
from ninja import NinjaAPI
from ninja.errors import HttpError
from iscc_registry import settings
from iscc_registry.exceptions import RegistrationError
from iscc_registry import schema as s
from iscc_registry.models import IsccId
from iscc_registry.schema import Head, Message, RegistrationResponse, Declaration
from iscc_registry.transactions import rollback, register, mint
from iscc_registry.tasks import fetch_metadata
from ninja.security import HttpBearer
import iscc_core as ic
import iscc_schema as ics


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


@api.get(
    "/declaration/{iscc_id}",
    tags=["public"],
    response=s.DeclarationResponse,
    auth=None,
)
def declaration(request, iscc_id: str):
    """Get declaration for ISCC-ID"""
    try:
        ic.iscc_validate(ic.iscc_normalize(iscc_id), strict=True)
    except ValueError as e:
        raise HttpError(400, str(e))
    return IsccId.get_safe(iscc_id=ic.Code(iscc_id).code)


@api.get(
    "/metadata/{iscc_id}",
    tags=["public"],
    response=ics.IsccMeta,
    auth=None,
    exclude_none=True,
    by_alias=True,
)
def metadata(request, iscc_id: str):
    """Get metadata for ISCC-ID"""
    try:
        ic.iscc_validate(ic.iscc_normalize(iscc_id), strict=True)
    except ValueError as e:
        raise HttpError(400, str(e))
    return IsccId.get_safe(iscc_id=ic.Code(iscc_id).code).metadata


@api.get("/resolve/{iscc_id}", tags=["public"], auth=None, response={200: s.Redirect, 404: Message})
def resolve(request, iscc_id: str):
    try:
        norm = ic.iscc_normalize(iscc_id)
        ic.iscc_validate(norm)
    except ValueError as e:
        return 404, Message(message=str(e))

    # Fetch from database
    try:
        iscc_obj = IsccId.get_safe(iscc_id=norm.lstrip("ISCC:"))
    except IsccId.DoesNotExist:
        return 404, Message(message=f"{iscc_id} does not exist")

    # Resolve if we can
    if iscc_obj.metadata:
        url = iscc_obj.metadata.get("redirect")
        if url:
            return 200, {"url": url}

    # Redirect to local entry
    return {"url": iscc_obj.get_registry_url()}


@api.post("/forecast", tags=["public"], response=s.Forecast, auth=None, exclude_none=True)
def forecast(request, data: s.Forecast):
    """Create ISCC-ID forecast from declaration data."""
    iscc_id = mint(**data.dict(exclude_none=True))
    return s.Forecast(iscc_id=f"ISCC:{iscc_id}")


####################################################################################################
# Private observer endpoints                                                                       #
####################################################################################################


@api.get("/head/{chain_id}", tags=["observer"], response={200: Head, 422: Message})
def head(request, chain_id: int, offset: int = 0):
    """Return block header of the latest registration event for given chain."""
    qs = IsccId.objects.filter(chain_id=chain_id).order_by("-did")
    if not qs.exists():
        return 422, Message(message="No registrations found for chain")
    try:
        obj = qs[offset]
    except IndexError:
        return 422, Message(message=f"No registration at offset {offset}")
    return 200, obj


@api.post("/register", tags=["observer"], response={201: RegistrationResponse, 422: Message})
def register_(request, declartion: Declaration):
    """Register an on-chain ISCC-Declaration for ISCC-ID minting."""
    try:
        iid_obj = register(declartion)
        # enqueue task to fetch metadata
        fetch_metadata(iid_obj.did)
        return 201, dict(did=iid_obj.did, iscc_id=f"ISCC:{iid_obj.iscc_id}")
    except RegistrationError as e:
        return 422, Message(message=str(e))


@api.post("/rollback/{block_hash}", tags=["observer"], response={200: Head, 404: Message})
def rollback_(request, block_hash: str):
    """Rollback events to state before `block_hash`"""
    return rollback(block_hash)
