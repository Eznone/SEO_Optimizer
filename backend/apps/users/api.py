from django.contrib.auth import logout
from ninja import Router, Schema
from typing import Optional
from .models import UserProfile

router = Router()

class ProfileResponse(Schema):
    username: str
    email: str
    has_groq_key: bool

class ApiKeyUpdate(Schema):
    groq_api_key: str

@router.get("/me", response=ProfileResponse)
def get_my_profile(request):
    return {
        "username": request.auth.username,
        "email": request.auth.email,
        "has_groq_key": bool(request.auth.profile.groq_api_key)
    }

@router.post("/update-key")
def update_api_key(request, data: ApiKeyUpdate):
    profile = request.auth.profile
    profile.groq_api_key = data.groq_api_key
    profile.save()
    return {"message": "API key updated successfully"}

@router.post("/logout")
def user_logout(request):
    logout(request)
    return {"message": "Logged out successfully"}
