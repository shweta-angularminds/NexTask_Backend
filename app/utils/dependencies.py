from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt,JWTError
from app.core.config import SECRET_KEY, ALGORITHM
from app.db.database import db

from bson import ObjectId

security = HTTPBearer()

async def get_current_user(token=Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")