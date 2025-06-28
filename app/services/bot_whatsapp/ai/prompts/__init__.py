from pathlib import Path
import yaml
from pydantic import BaseModel

class BasePrompt(BaseModel):
    system: str


class Prompts(BaseModel):
    chat_principal: BasePrompt


def load_prompts() -> Prompts:
    prompts_path = Path(__file__).parent / "prompts.yaml"

    return Prompts.model_validate(
        yaml.safe_load(prompts_path.read_text(encoding="utf-8"))
    )


node_prompts = load_prompts()