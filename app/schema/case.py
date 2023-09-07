from pydantic import BaseModel, Field

from app.common import models as m


class CaseScreenshot(BaseModel):
    id: int
    url: str

    class Config:
        orm_mode = True


class CaseOut(BaseModel):
    id: int
    title: str
    sub_title: str = Field(alias="subTitle")
    description: str
    is_active: bool = Field(alias="isActive")
    is_main: bool = Field(alias="isMain")
    project_link: str = Field(alias="projectLink")
    role: str

    stacks_names: list[str] = Field(alias="stacksNames")
    screenshots: list[CaseScreenshot]

    main_image_url: str = Field(alias="mainImageUrl")
    preview_image_url: str = Field(alias="previewImageUrl")
    language: m.Languages

    class Config:
        orm_mode = True
        use_enum_values = True
        allow_population_by_field_name = True
