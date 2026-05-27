"""Tools: konfigurasi credentials Bitbucket."""

from bitmcp.server import mcp, save_config, load_config, CONFIG_FILE


@mcp.tool()
def setup_bitbucket(workspace: str, username: str, api_token: str) -> str:
    """
    Simpan credentials Bitbucket ke config file lokal.

    Args:
        workspace: Bitbucket workspace slug (contoh: 'miraeasset-tech')
        username: Email akun Atlassian Anda (contoh: 'john@company.com')
        api_token: API token dari https://id.atlassian.com/manage-profile/security/api-tokens
    """
    config = {
        "workspace": workspace,
        "username": username,
        "token": api_token,
    }
    save_config(config)
    # JANGAN return token di output — cukup konfirmasi
    return (
        f"Credentials berhasil disimpan di {CONFIG_FILE}\n"
        f"  workspace : {workspace}\n"
        f"  username  : {username}\n"
        f"  token     : {'*' * 8} (tersimpan aman, permission 600)"
    )


@mcp.tool()
def get_config_status() -> str:
    """Cek status konfigurasi Bitbucket saat ini."""
    config = load_config()
    if not config:
        return f"Belum dikonfigurasi. Jalankan setup_bitbucket terlebih dahulu.\nConfig path: {CONFIG_FILE}"

    token_preview = ("*" * 8 + config["token"][-4:]) if config.get("token") else "TIDAK ADA"
    return (
        f"Konfigurasi aktif:\n"
        f"  workspace : {config.get('workspace', 'TIDAK ADA')}\n"
        f"  username  : {config.get('username', 'TIDAK ADA')}\n"
        f"  token     : {token_preview}\n"
        f"  config    : {CONFIG_FILE}"
    )
