"""Validated private runtime configuration, separate from the public interface."""
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, SecretStr, field_validator


class Settings(BaseModel):
    switch_url: str
    room_id: str = Field(min_length=1)
    operator_ids: list[str] = Field(min_length=1)
    repo_root: Path
    verifier_id: str
    verifier_key: SecretStr = Field(repr=False)
    fixer_id: str
    fixer_key: SecretStr = Field(repr=False)

    @field_validator('switch_url')
    @classmethod
    def valid_url(cls, value):
        url = urlsplit(value)
        if url.scheme not in {'http', 'https'} or not url.hostname or url.username or url.password:
            raise ValueError('Use a server URL without embedded credentials')
        return value.rstrip('/')

    @field_validator('repo_root')
    @classmethod
    def valid_repository_directory(cls, value):
        resolved = value.resolve()
        if not resolved.is_dir():
            raise ValueError('The allowlisted repository directory must exist')
        return resolved
