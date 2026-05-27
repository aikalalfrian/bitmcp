"""Tools: konfigurasi credentials Bitbucket."""

from typing import Optional

from bitmcp.server import mcp, save_config, load_config, CONFIG_FILE


@mcp.tool()
def setup_bitbucket(workspace: str, username: Optional[str], api_token: str, auth_method: str = "basic") -> str:
    """
    Simpan credentials Bitbucket ke config file lokal.

    Args:
        workspace: Bitbucket workspace slug (contoh: 'miraeasset-tech')
        username: Email akun Atlassian Anda (contoh: 'john@company.com'). Untuk
                  API token tanpa username (Bearer), masukkan kosong atau None
                  dan set `auth_method='bearer'`.
        api_token: Token API. Untuk Bitbucket Cloud saat ini gunakan API tokens
                   yang dibuat di Bitbucket -> Personal settings -> API tokens
                   (atau App passwords jika masih tersedia). Pastikan token
                   memiliki scope yang diperlukan: `Account: Read`,
                   `Repositories: Read`, `Pull requests: Read` (tambahkan Write bila perlu).
        auth_method: 'basic' (default) atau 'bearer' untuk Authorization: Bearer <token>.
    """
    config = {
        "workspace": workspace,
        "username": username,
        "token": api_token,
        "auth_method": auth_method,
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
        f"  auth_method: {config.get('auth_method', 'basic')}\n"
        f"  token     : {token_preview}\n"
        f"  config    : {CONFIG_FILE}"
    )
