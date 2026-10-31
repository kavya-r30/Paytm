"""Settings and secrets from the environment, plus validated YAML config: policies, providers, calendar.

An invalid config file stops the app at boot with the file name in the error. API keys are read only here,
as SecretStr, from backend/.env; they never reach the web app, logs, spans or prompts (spec Part G0).
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from arth.core.clock import IST
from arth.core.paths import BACKEND_DIR, CONFIG_DIR, DATA_DIR, PACKS_DIR
from arth.core.yamlconf import ConfigError, Strict, validate

Tier = Literal["R0", "R1", "R2", "R3", "R4"]
Mode = Literal["dev", "test", "demo", "prod"]
HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
TOKEN_ENVS = {
    "ARTH_DIRECTOR_TOKEN": "director_token",
    "ARTH_DEVICE_TOKEN": "device_token",
    "ARTH_CONSOLE_TOKEN": "console_token",
}
KEY_ENVS = (
    "AZURE_OPENAI_API_KEY",
    "MISTRAL_API_KEY",
    "GROQ_API_KEY",
    "SARVAM_API_KEY",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
)


# ---- settings and secrets ------------------------------------------------------------------


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ARTH_", env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    mode: Mode = "dev"
    data_dir: Path = DATA_DIR
    config_dir: Path = CONFIG_DIR
    packs_dir: Path = PACKS_DIR
    clock_start: datetime = datetime(2026, 10, 29, 7, 45, tzinfo=IST)
    director_token: SecretStr = SecretStr("dev-director")
    device_token: SecretStr = SecretStr("dev-device")
    console_token: SecretStr = SecretStr("dev-console")
    session_signing_key: SecretStr | None = None
    cors_origins: list[str] = ["http://localhost:3000"]
    tick_interval_s: float = 1.0
    # Normal (dev/prod) mode: the shop's clock runs at real time, so undo windows elapse, hourly intel and the
    # nightly agents fire; test/demo keep it frozen for deterministic runs. The Director can freeze/run it.
    clock_running: bool | None = None

    @property
    def clock_runs(self) -> bool:
        return self.clock_running if self.clock_running is not None else self.mode in {"dev", "prod"}

    azure_openai_api_key: SecretStr | None = Field(default=None, validation_alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str | None = Field(default=None, validation_alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version: str = Field(
        default="2025-04-01-preview", validation_alias="AZURE_OPENAI_API_VERSION"
    )
    mistral_api_key: SecretStr | None = Field(default=None, validation_alias="MISTRAL_API_KEY")
    groq_api_key: SecretStr | None = Field(default=None, validation_alias="GROQ_API_KEY")
    sarvam_api_key: SecretStr | None = Field(default=None, validation_alias="SARVAM_API_KEY")
    langfuse_public_key: SecretStr | None = Field(default=None, validation_alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: SecretStr | None = Field(default=None, validation_alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(default="https://cloud.langfuse.com", validation_alias="LANGFUSE_HOST")

    @field_validator(
        "azure_openai_api_key",
        "azure_openai_endpoint",
        "mistral_api_key",
        "groq_api_key",
        "sarvam_api_key",
        "langfuse_public_key",
        "langfuse_secret_key",
        mode="before",
    )
    @classmethod
    def _blank_is_unset(cls, value: object) -> object:
        return None if isinstance(value, str) and not value.strip() else value

    @property
    def db_path(self) -> Path:
        return self.data_dir / "arth.db"

    def secret(self, env_name: str) -> SecretStr | None:
        secrets = {
            "AZURE_OPENAI_API_KEY": self.azure_openai_api_key if self.azure_openai_endpoint else None,
            "MISTRAL_API_KEY": self.mistral_api_key,
            "GROQ_API_KEY": self.groq_api_key,
            "SARVAM_API_KEY": self.sarvam_api_key,
            "LANGFUSE_PUBLIC_KEY": self.langfuse_public_key,
            "LANGFUSE_SECRET_KEY": self.langfuse_secret_key,
        }
        if env_name not in secrets:
            raise ConfigError(f"unknown secret {env_name!r}")
        return secrets[env_name]


def check_auth_tokens(settings: Settings) -> None:
    """In prod the dev-* default surface tokens are refused. Messages name env vars, never values."""
    weak = sorted(
        env
        for env, attr in TOKEN_ENVS.items()
        if getattr(settings, attr).get_secret_value().startswith("dev-")
    )
    if weak and settings.mode == "prod":
        raise ConfigError(f"prod refuses the default dev-* auth tokens; set {', '.join(weak)}")


# ---- policies.yaml -------------------------------------------------------------------------


class Role(Strict):
    max_tier: Tier
    approve: list[Tier] = []
    allow: list[str] = []


class QuietHours(Strict):
    start: str
    end: str

    @field_validator("start", "end")
    @classmethod
    def _hhmm(cls, value: str) -> str:
        if not HHMM.match(value):
            raise ValueError(f"time {value!r} must be HH:MM, 24-hour (e.g. '21:30')")
        return value


class ContactCaps(Strict):
    marketing_per_patron_per_week: int = Field(ge=0)


class Reminders(Strict):
    per_patron_per_week: int = Field(ge=0)
    cadence_days: list[int]


class Growth(Strict):
    holdout_share: float = Field(ge=0, le=1)
    holdout_min: int = Field(ge=0)
    margin_floor: float = Field(ge=0, le=1)
    monthly_incentive_budget_paise: int = Field(ge=0)


class DiscreetMode(Strict):
    busy_hours: list[str]


class Attention(Strict):
    proactive_per_day: int = Field(ge=0)
    urgent_interrupts_per_day: int = Field(ge=0)


class Policies(Strict):
    tiers: dict[str, Tier]
    roles: dict[str, Role]
    quiet_hours: QuietHours
    contact_caps: ContactCaps
    reminders: Reminders
    growth: Growth
    expiry_alert_days: dict[str, int]
    discreet_mode: DiscreetMode
    attention: Attention
    forbid_offers_on_flags: list[str] = []

    @model_validator(mode="after")
    def _owner_is_top(self) -> Policies:
        owner = self.roles.get("owner")
        if owner is None or owner.max_tier != "R4":
            raise ValueError("an 'owner' role with max_tier R4 is required")
        return self


# ---- providers.yaml ------------------------------------------------------------------------

DataTag = Literal["merchant_ok_if_paid_plan", "synthetic_only", "synthetic_only_on_free_tier"]
REQUIRED_ROLES = {"llm.fast", "llm.large", "vision", "ocr", "stt", "tts", "translate", "guard", "persona"}


class Hop(Strict):
    provider: str
    model: str | None = None
    timeout_ms: int | None = Field(default=None, gt=0)
    json_mode: bool = Field(default=False, alias="json")
    langs: list[str] | None = None
    speaker: str | None = None  # TTS voice for this model (speaker sets differ per Bulbul version)


class RoleChain(Strict):
    chain: list[Hop] = Field(min_length=1)


class Provider(Strict):
    api_key_env: str
    data_tag: DataTag
    rate: dict[str, int] = {}

    @field_validator("api_key_env")
    @classmethod
    def _known_env(cls, value: str) -> str:
        if value not in KEY_ENVS:
            raise ValueError(f"api_key_env {value!r} is not one of {', '.join(KEY_ENVS)}")
        return value


class Providers(Strict):
    roles: dict[str, RoleChain]
    providers: dict[str, Provider]

    @model_validator(mode="after")
    def _chains_are_resolvable(self) -> Providers:
        missing = REQUIRED_ROLES - self.roles.keys()
        if missing:
            raise ValueError(f"missing roles: {sorted(missing)}")
        for role, chain in self.roles.items():
            for hop in chain.chain:
                if hop.provider != "cassette" and hop.provider not in self.providers:
                    raise ValueError(f"role {role!r} uses unknown provider {hop.provider!r}")
                if hop.provider != "cassette" and not hop.model:
                    raise ValueError(f"role {role!r}: provider {hop.provider!r} needs a model id")
        return self

    def used(self) -> set[str]:
        return {
            hop.provider for chain in self.roles.values() for hop in chain.chain if hop.provider != "cassette"
        }


def provider_status(settings: Settings, providers: Providers) -> dict[str, bool]:
    """Which providers have a key configured. Values are booleans only, never the key."""
    return {
        name: settings.secret(p.api_key_env) is not None for name, p in sorted(providers.providers.items())
    }


def check_provider_keys(settings: Settings, providers: Providers) -> None:
    missing = sorted(
        providers.providers[name].api_key_env
        for name in providers.used()
        if settings.secret(providers.providers[name].api_key_env) is None
    )
    if missing and settings.mode == "prod":
        raise ConfigError(f"missing API keys in .env for prod: {', '.join(missing)}")


# ---- loaders -------------------------------------------------------------------------------


def load_policies(path: Path) -> Policies:
    return validate(Policies, path)


def load_providers(path: Path) -> Providers:
    return validate(Providers, path)
