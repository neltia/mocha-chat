from pydantic import BaseModel


# 표준 응답 모델들
class SQLInput(BaseModel):
    query: str
    database_type: str = "MariaDB"
    context: str = ""


class TextInput(BaseModel):
    description: str
    database_type: str = "MariaDB"
    context: str = ""


class ScenarioInput(BaseModel):
    scenario: str
    database_type: str = "MariaDB"
    expected_scale: str = "medium"
    performance_requirements: str = "standard"
