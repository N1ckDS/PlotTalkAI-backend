from fastapi import APIRouter, Depends, HTTPException, Header, HTTPException, status
router = APIRouter()
@router.head("/healthz", status_code=status.HTTP_200_OK)
def check_healthz():
    return {"status": "ok"}