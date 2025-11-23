from fastapi import APIRouter, Depends, HTTPException
from lib.models.schemas import Params
from lib.llm.generator import Orchestrator
from src.db.api.db_endpoint import get_current_user_id

router = APIRouter()


class DialogueController:
    def __init__(self):
        self.generator_class = Orchestrator

    def generate(self, params: Params):
        generator = self.generator_class(params.dict())
        return generator.create_dialog()


dialogue_controller = DialogueController()


@router.post("/generate", tags=["Dialogue"])
def generate(params: Params, user_id: int = Depends(get_current_user_id)):
    try:
        return dialogue_controller.generate(params)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate dialogue: {exc}")
