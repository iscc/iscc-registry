from typing import Optional
from ninja import Schema, ModelSchema
from pydantic import Field, root_validator, validator
import iscc_core as ic
from bitarray import util
from datetime import datetime
from iscc_registry.models import IsccId
from eth_utils.address import to_checksum_address


API_VERSION = "0.1.0"


class API(Schema):
    openapi: str = Field("/api/v1/openapi.json")
    version: str = Field(API_VERSION)
    docs: str = Field("/api/v1/docs")


class Declaration(Schema):

    timestamp: datetime = Field(..., description="Unix timestamp of block")
    chain_id: int = Field(..., description="ID of source chain")
    block_height: int = Field(..., description="Block height")
    block_hash: str = Field(..., description="Block hash")
    tx_idx: int = Field(..., description="Index of TX within block")
    tx_hash: str = Field(..., description="Hash of transaction")
    declarer: str = Field(..., description="Wallet-Address of original declaring party")
    iscc_code: str = Field(
        ...,
        description="ISCC-CODE without URI prefix",
        example="KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY",
        max_length=73,
        min_length=15,
        regex="^[A-Z2-7:]{10,73}$",
    )
    message: Optional[str] = Field(None, description="Declaration processing message")
    meta_url: Optional[str] = Field(None, description="URL for ISCC Metadata")
    registrar: Optional[str] = Field(None, description="Wallet-Address of registrar")

    @property
    def did(self):
        """64-bit cross-chain, monotonic, and deterministic height"""
        ts = util.int2ba(int(self.timestamp.timestamp()), length=36, endian="big", signed=False)
        chain_id = util.int2ba(self.chain_id, length=14, endian="big", signed=False)
        tx_idx = util.int2ba(self.tx_idx, length=14, endian="big", signed=False)
        data = ts + chain_id + tx_idx
        return util.ba2int(data, signed=False)

    @property
    def freeze(self) -> bool:
        """Freeze declaration to disable updates"""
        return self.message == "frz:"

    @property
    def delete(self) -> bool:
        """Soft-Delete entry from registry"""
        return self.message == "del:"

    def get_iscc_id(self, uc=0) -> str:
        """Calculate ISCC-ID with counter `uc`"""
        return ic.gen_iscc_id_v0(
            iscc_code=self.iscc_code,
            chain_id=self.chain_id,
            wallet=self.declarer,
            uc=uc,
        )["iscc"].lstrip("ISCC:")

    @validator("declarer", "registrar", pre=True, allow_reuse=True)
    def address_checksum(cls, v):
        if v and v.startswith("0x"):
            return to_checksum_address(v)
        return v

    @validator("iscc_code", pre=True, allow_reuse=True)
    def clean_iscc(cls, v):
        return ic.iscc_clean(v)


class DeclarationResponse(ModelSchema):

    declarer: str
    chain: str
    registrar: Optional[str]

    class Config:
        model = IsccId
        model_fields = [
            "did",
            "iscc_id",
            "iscc_code",
            "declarer",
            "meta_url",
            "message",
            "chain",
            "block_height",
            "block_hash",
            "tx_idx",
            "tx_hash",
            "timestamp",
            "registrar",
        ]

    @validator("iscc_id", "iscc_code", pre=True, allow_reuse=True, check_fields=False)
    def iscc_normalize(cls, v):
        return ic.iscc_normalize(v)

    @staticmethod
    def resolve_declarer(obj):
        return obj.declarer.username if obj.declarer else ""

    @staticmethod
    def resolve_registrar(obj):
        return obj.registrar.username if obj.registrar else ""

    @staticmethod
    def resolve_chain(obj):
        return obj.chain.name if obj.chain else ""


class RegistrationResponse(Schema):

    did: int = Field(
        ...,
        description="Cross-Chain time-ordered unique Declaration-ID",
        example=330445058337719994,
    )

    iscc_id: str = Field(
        ...,
        description="Globally unique ISCC-ID",
        example="ISCC:MMAOHZYGQLBASTFM",
        max_length=73,
        min_length=15,
        regex="^ISCC:[A-Z2-7]{10,73}$",
    )


class Forecast(Schema):

    iscc_id: Optional[str] = Field(
        None,
        description="ISCC-ID",
        example="ISCC:MMAOHZYGQLBASTFM",
        max_length=73,
        min_length=15,
        regex="^ISCC:[A-Z2-7]{10,73}$",
        readOnly=True,
    )

    chain_id: Optional[int] = Field(
        None,
        description="ID of source chain",
        writeOnly=True,
    )
    wallet: Optional[str] = Field(
        None,
        description="Wallet-Address of original declaring party",
        example="0x1aD91ee08f21bE3dE0BA2ba6918E714dA6B45836",
        writeOnly=True,
    )
    iscc_code: Optional[str] = Field(
        None,
        description="ISCC-CODE",
        example="KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY",
        max_length=73,
        min_length=15,
        regex="^[A-Z2-7]{10,73}$",
        writeOnly=True,
    )

    @root_validator(pre=True)
    def normalize_addresses(cls, values):
        if values.get("chain_id") in (ic.ST_ID.ETHEREUM, ic.ST_ID.POLYGON):
            if values.get("wallet"):
                values["wallet"] = to_checksum_address(values["wallet"])
        return values


class Head(ModelSchema):
    class Config:
        model = IsccId
        model_fields = ["chain", "block_height", "block_hash", "tx_idx", "tx_hash", "timestamp"]


class Message(Schema):
    message: str


class Error(Schema):
    status_code: int


class Redirect(Schema):

    url: Optional[str] = Field(..., description="Redirection target for ISCC-ID")
