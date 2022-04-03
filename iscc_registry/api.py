"""
## Public features:

- resolve ISCC-IDs to their redirection target
- retrieve declaration metadata for an ISCC-ID
- find ISCC-IDs for a given ISCC-CODE

## Administrative features:
- Allow chain observers to sync ISCC declarations to the registry.
"""
from django.shortcuts import redirect
from ninja import NinjaAPI
from ninja.errors import HttpError

from iscc_registry import schema as s
import iscc_core as ic

api = NinjaAPI(
    title="ISCC - Registry API",
    version=s.API_VERSION,
    description=__doc__,
)


@api.get("", tags=["public"], response=s.API)
def index(request):
    """Returns current API information."""
    return {}


@api.get("/resolve/{iscc}", tags=["public"])
def resolve(request, iscc: str):
    try:
        ic.iscc_validate(ic.iscc_normalize(iscc), strict=True)
    except ValueError as e:
        raise HttpError(400, str(e))

    return redirect("https://example.com", permanent=False)


@api.post("/register", tags=["observer"], response=s.DeclarationResponse)
def register(request, declartion: s.Declaration):
    """Register an on-chain ISCC-Declaration for ISCC-ID minting."""
    pass
