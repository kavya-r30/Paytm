from pathlib import Path

import pytest

from arth.core.config import (
    ConfigError,
    Settings,
    check_auth_tokens,
    check_provider_keys,
    load_policies,
    load_providers,
    provider_status,
)
from arth.core.paths import CONFIG_DIR, DATA_DIR

CONFIG = CONFIG_DIR
KEY_VARS = (
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "MISTRAL_API_KEY",
    "GROQ_API_KEY",
    "SARVAM_API_KEY",
)
TOKEN_VARS = ("ARTH_DIRECTOR_TOKEN", "ARTH_DEVICE_TOKEN", "ARTH_CONSOLE_TOKEN")


@pytest.fixture
def no_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (*KEY_VARS, *TOKEN_VARS, "ARTH_MODE"):
        monkeypatch.delenv(name, raising=False)


def write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_repo_policies_load() -> None:
    policies = load_policies(CONFIG / "policies.yaml")
    assert policies.roles["owner"].max_tier == "R4"
    assert policies.tiers, "every action has a tier"
    assert 0 <= policies.growth.margin_floor <= 1


def test_bad_tier_fails_with_file_name(tmp_path: Path) -> None:
    text = (
        (CONFIG / "policies.yaml")
        .read_text(encoding="utf-8")
        .replace("ledger.add_entry: R2", "ledger.add_entry: R9")
    )
    with pytest.raises(ConfigError, match="policies.yaml"):
        load_policies(write(tmp_path, "policies.yaml", text))


def test_policies_require_owner_role(tmp_path: Path) -> None:
    text = (CONFIG / "policies.yaml").read_text(encoding="utf-8").replace("  owner:", "  boss:")
    with pytest.raises(ConfigError, match="owner"):
        load_policies(write(tmp_path, "policies.yaml", text))


@pytest.mark.parametrize("bad", ["9:5", "25:00", "21:60", "abc", "21.30", "2130"])
def test_quiet_hours_must_be_hh_mm(tmp_path: Path, bad: str) -> None:
    text = (CONFIG / "policies.yaml").read_text(encoding="utf-8").replace("start: '21:30'", f"start: '{bad}'")
    with pytest.raises(ConfigError, match="HH:MM"):
        load_policies(write(tmp_path, "policies.yaml", text))


def test_repo_providers_structure() -> None:
    providers = load_providers(CONFIG / "providers.yaml")
    assert providers.used() <= providers.providers.keys()
    for env in (p.api_key_env for p in providers.providers.values()):
        assert env.endswith("_API_KEY")


def test_repo_providers_use_the_decided_stack() -> None:
    # Team decisions, pinned on purpose: Azure OpenAI primary LLM (user, 31 Oct 2026: the Mistral key is
    # rate-limited), Groq backup, Mistral OCR, Sarvam STT/TTS models.
    providers = load_providers(CONFIG / "providers.yaml")
    assert providers.roles["llm.fast"].chain[0].provider == "azure"
    assert providers.roles["llm.fast"].chain[0].model == "renaiscent-gpt-5.4-mini"
    assert providers.roles["ocr"].chain[0].provider == "mistral"
    assert providers.roles["llm.fast"].chain[1].provider == "groq"
    assert providers.roles["stt"].chain[0].model == "saaras:v4"
    assert providers.roles["tts"].chain[0].model == "bulbul:v4-flash"
    assert providers.providers["sarvam"].api_key_env == "SARVAM_API_KEY"


def test_unknown_provider_in_chain_fails(tmp_path: Path) -> None:
    text = (
        (CONFIG / "providers.yaml")
        .read_text(encoding="utf-8")
        .replace(
            "provider: groq, model: openai/gpt-oss-20b, timeout_ms: 3000",
            "provider: openx, model: x, timeout_ms: 3000",
        )
    )
    with pytest.raises(ConfigError, match="openx"):
        load_providers(write(tmp_path, "providers.yaml", text))


def test_unknown_key_env_fails(tmp_path: Path) -> None:
    text = (
        (CONFIG / "providers.yaml")
        .read_text(encoding="utf-8")
        .replace("api_key_env: GROQ_API_KEY", "api_key_env: GROQ_KEY")
    )
    with pytest.raises(ConfigError, match="GROQ_KEY"):
        load_providers(write(tmp_path, "providers.yaml", text))


def test_settings_defaults_point_inside_repo(no_key_env: None) -> None:
    settings = Settings(_env_file=None)
    assert settings.mode == "dev"
    assert settings.db_path == DATA_DIR / "arth.db"
    assert settings.clock_start.isoformat() == "2026-10-29T07:45:00+05:30"
    assert settings.mistral_api_key is None


def test_keys_come_from_the_env_file_as_secrets(tmp_path: Path, no_key_env: None) -> None:
    env = write(tmp_path, ".env", "MISTRAL_API_KEY=sk-test-123\nGROQ_API_KEY=\nARTH_MODE=demo\n")
    settings = Settings(_env_file=env)
    assert settings.mode == "demo"
    assert settings.mistral_api_key is not None
    assert settings.mistral_api_key.get_secret_value() == "sk-test-123"
    assert settings.groq_api_key is None, "a blank value means 'not set'"
    assert "sk-test-123" not in repr(settings)
    assert "sk-test-123" not in settings.model_dump_json()


def test_auth_tokens_are_secrets(tmp_path: Path, no_key_env: None) -> None:
    env = write(tmp_path, ".env", "ARTH_DIRECTOR_TOKEN=tok-director-xyz\nARTH_DEVICE_TOKEN=tok-device-xyz\n")
    settings = Settings(_env_file=env)
    assert settings.director_token.get_secret_value() == "tok-director-xyz"
    dumped = repr(settings) + settings.model_dump_json()
    for text in ("tok-director-xyz", "tok-device-xyz", "dev-console"):
        assert text not in dumped


def test_prod_refuses_default_dev_tokens(no_key_env: None) -> None:
    with pytest.raises(ConfigError) as err:
        check_auth_tokens(Settings(_env_file=None, mode="prod"))
    message = str(err.value)
    for env in TOKEN_VARS:
        assert env in message
    assert "dev-director" not in message


def test_prod_accepts_real_tokens_and_dev_accepts_defaults(tmp_path: Path, no_key_env: None) -> None:
    check_auth_tokens(Settings(_env_file=None, mode="dev"))
    env = write(
        tmp_path,
        ".env",
        "ARTH_MODE=prod\nARTH_DIRECTOR_TOKEN=a-long-random-1\nARTH_DEVICE_TOKEN=a-long-random-2\n"
        "ARTH_CONSOLE_TOKEN=a-long-random-3\n",
    )
    check_auth_tokens(Settings(_env_file=env))


def test_prod_refuses_to_boot_without_keys(no_key_env: None) -> None:
    providers = load_providers(CONFIG / "providers.yaml")
    with pytest.raises(ConfigError, match="AZURE_OPENAI_API_KEY.*MISTRAL_API_KEY.*SARVAM_API_KEY"):
        check_provider_keys(Settings(_env_file=None, mode="prod"), providers)


def test_prod_boots_when_all_keys_are_present(tmp_path: Path, no_key_env: None) -> None:
    providers = load_providers(CONFIG / "providers.yaml")
    env = write(
        tmp_path,
        ".env",
        "ARTH_MODE=prod\nMISTRAL_API_KEY=fake-m\nGROQ_API_KEY=fake-g\nSARVAM_API_KEY=fake-s\n"
        "AZURE_OPENAI_API_KEY=fake-a\nAZURE_OPENAI_ENDPOINT=https://x.example.azure.com/\n",
    )
    settings = Settings(_env_file=env)
    check_provider_keys(settings, providers)
    assert provider_status(settings, providers) == {
        "azure": True,
        "mistral": True,
        "groq": True,
        "sarvam": True,
    }


def test_config_errors_never_contain_key_text(tmp_path: Path, no_key_env: None) -> None:
    providers = load_providers(CONFIG / "providers.yaml")
    env = write(
        tmp_path, ".env", "ARTH_MODE=prod\nMISTRAL_API_KEY=sk-secret-aaa\nGROQ_API_KEY=sk-secret-bbb\n"
    )
    with pytest.raises(ConfigError) as err:
        check_provider_keys(Settings(_env_file=env), providers)
    assert "SARVAM_API_KEY" in str(err.value)
    assert "sk-secret" not in str(err.value)


def test_dev_boots_without_keys_and_reports_status(no_key_env: None) -> None:
    providers = load_providers(CONFIG / "providers.yaml")
    settings = Settings(_env_file=None, mode="dev")
    check_provider_keys(settings, providers)
    status = provider_status(settings, providers)
    assert set(status) == set(providers.providers)
    assert not any(status.values())
