from datetime import datetime
from typing import Optional
from ninja import Schema
from pydantic import Field
import iscc_core as ic


API_VERSION = "0.1.0"


class API(Schema):
    openapi: str = Field("/api/openapi.json")
    version: str = Field(API_VERSION)
    docs: str = Field("/api/docs")


class Declaration(Schema):

    time: datetime = Field(..., description="Unix timestamp of block")
    chain_id: int = Field(..., description="ID of source chain")
    block_id: int = Field(..., description="Block height")
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
        regex="^[A-Z2-7]{10,73}$",
    )
    message: Optional[str] = Field(None, description="Declaration processing message")
    meta_url: Optional[str] = Field(None, description="URL for ISCC Metadata")
    registrar: Optional[str] = Field(None, description="Wallet-Address of registrar")

    def iscc_id(self, uc=0) -> str:
        return ic.gen_iscc_id_v0(
            iscc_code=self.iscc_code,
            chain_id=self.chain_id,
            wallet=self.declarer,
            uc=uc,
        )["iscc"].lstrip("ISCC:")

    @property
    def freeze(self) -> bool:
        return self.message == "frz:"

    @property
    def delete(self) -> bool:
        return self.message == "del:"


# class Declaration(Schema):
#     chain: str
#     declarer: str
#     iscc_code: str
#     block_height: int
#     block_hash: str
#     tx_hash: str
#     timestamp: float
#     tx_out_idx: int = 0
#     data: Optional[str] = None
#     meta_url: Optional[str] = None
#     registrar: Optional[str] = None
#
#     def get_id(self) -> int:
#         """Create monotonicaly increasing flake id from timestamp"""
#         return ic.Flake(ts=self.timestamp, bits=64).int
#
#     @property
#     def freeze(self) -> bool:
#         return self.data == b"\x01".hex()
#
#     @property
#     def delete(self) -> bool:
#         return self.data == b"\x02".hex()
#
#     @property
#     def chain_id(self):
#         chainmap = {
#             "BITCOIN": 1,
#             "ETHEREUM": 2,
#             "POLYGON": 3,
#         }
#         return chainmap[self.chain]
#
#     def iscc_id(self, uc=0) -> str:
#         return ic.gen_iscc_id_v0(
#             iscc_code=self.iscc_code,
#             chain_id=self.chain_id,
#             wallet=self.declarer,
#             uc=uc,
#         )["iscc"].lstrip("ISCC:")


class DeclarationResponse(Schema):
    iscc_id: str


class Error(Schema):
    status_code: int
