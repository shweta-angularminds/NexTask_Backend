from fastapi import APIRouter, HTTPException
from app.db.database import db
from app.schemas.user_schema import UserCreate, UserLogin
from app.core.security import hash_password,verify_password,create_access_token

router = APIRouter()

@router.post("/register")
async def register(user:UserCreate):
    existing =await db.users.find_one({"email":user.email})
    if existing:
        raise HTTPException(status_code=400,detail="Email already exists")

    hashed = hash_password(user.password)
    
    result = await db.users.insert_one({
        "name":user.name,
        "email":user.email,
        "password":hashed,
        "role":"member"
    })
    
    return {"message":"User created"}

@router.post("/login")
async def login(user:UserLogin):
    db_user = await db.users.find_one({"email":user.email})
    
    if not db_user:
        raise HTTPException(status_code=400,detail="Invalid credentials")
    
    if not verify_password(user.password,db_user["password"]):
        raise HTTPException(status_code=400,detail="Invalid credentials")
    
    token = create_access_token({"user_id":str(db_user["_id"])})
    
    return {"access_token":token}