"""Pygent configuration models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProviderConfig(BaseModel):
    """Default provider settings."""

    provider: str = "ollama"
    model: str = "qwen2.5-coder:3b"


class SyntaxConfig(BaseModel):
    """Configuration for conversational syntax."""

    enabled: bool = True
    prefixes: dict[str, str] = Field(
        default_factory=lambda: {
            "mention": "@",
            "command": "/",
        }
    )


class ChatConfig(BaseModel):
    """Interactive chat configuration."""

    syntax: SyntaxConfig = Field(default_factory=SyntaxConfig)


class UserConfig(BaseModel):
    """User identity configuration."""

    username: str | None = None


class Config(BaseModel):
    """Pygent user configuration."""

    model_config = ConfigDict(extra="ignore")

    user: UserConfig = Field(default_factory=UserConfig)
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    chat: ChatConfig = Field(default_factory=ChatConfig)
