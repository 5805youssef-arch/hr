from fastapi import APIRouter

from ..penalties import MATRIX_DATA, PENALTY_MAP

router = APIRouter(prefix="/matrix", tags=["matrix"])


@router.get("")
def get_matrix():
    return {"matrix": MATRIX_DATA, "penalties": PENALTY_MAP}
