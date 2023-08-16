from pydantic import BaseModel


class CaseOut(BaseModel):
    id: int
    title: str
    sub_title: str
    description: str
    is_active: bool
    is_main: bool
    project_link: str
    role: str

    stacks_names: list[str]
    screenshots: list[str]

    main_image: str
    preview_image: str

    class Config:
        orm_mode = True
