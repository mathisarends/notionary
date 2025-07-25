from typing import Literal, Optional, Dict, Any, Union
from pydantic import BaseModel


class PersonUser(BaseModel):
    """Person user details"""
    email: Optional[str] = None


class BotOwner(BaseModel):
    """Bot owner information - simplified structure"""
    type: Literal["workspace", "user"]
    workspace: Optional[bool] = None


class WorkspaceLimits(BaseModel):
    """Workspace limits for bot users"""
    max_file_upload_size_in_bytes: int


class BotUser(BaseModel):
    """Bot user details"""
    owner: Optional[BotOwner] = None
    workspace_name: Optional[str] = None
    workspace_limits: Optional[WorkspaceLimits] = None


class NotionUserResponse(BaseModel):
    """
    Represents a Notion user object as returned by the Users API.
    Can represent both person and bot users.
    """
    object: Literal["user"]
    id: str
    type: Optional[Literal["person", "bot"]] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Person-specific fields
    person: Optional[PersonUser] = None
    
    # Bot-specific fields  
    bot: Optional[BotUser] = None


class NotionBotUserResponse(NotionUserResponse):
    """
    Specialized response for bot user (from /users/me endpoint)
    """
    # Bot users should have these fields, but they can still be None
    type: Literal["bot"]
    bot: Optional[BotUser] = None