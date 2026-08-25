from typing import Annotated

from app import models
from app.database.db import get_db
from app.dependencies.auth import get_current_user
from fastapi import Depends
from sqlalchemy.orm import Session

db_dependency = Annotated[Session, Depends(get_db)]

current_user_dependency = Annotated[models.User, Depends(get_current_user)]
