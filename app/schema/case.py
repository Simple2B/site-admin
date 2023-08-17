from pydantic import BaseModel


class CaseScreenshot(BaseModel):
    id: int
    url: str

    class Config:
        orm_mode = True


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
    screenshots: list[CaseScreenshot]

    main_image_url: str
    preview_image_url: str

    class Config:
        orm_mode = True
