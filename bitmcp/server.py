"""
Bitbucket MCP Server — In-house implementation.

Credential management:
  Credentials disimpan di ~/.config/bitmcp/config.json (permission 600).
  Jalankan tool `setup_bitbucket` untuk konfigurasi awal.
  Env vars BITBUCKET_API_TOKEN, BITBUCKET_USERNAME, BITBUCKET_WORKSPACE
  dapat digunakan sebagai override (misalnya untuk CI/CD).
"""

import json
import os
from pathlib import Path
from typing import Optional

import httpx
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server instance — diimpor oleh semua tool modules
# ---------------------------------------------------------------------------
mcp = FastMCP("bitmcp")

# ---------------------------------------------------------------------------
# Config paths
# ---------------------------------------------------------------------------
CONFIG_DIR = Path.home() / ".config" / "bitmcp"
CONFIG_FILE = CONFIG_DIR / "config.json"

BITBUCKET_API = "https://api.bitbucket.org/2.0"


# ---------------------------------------------------------------------------
# Config helpers (dipakai oleh tools/)
# ---------------------------------------------------------------------------

def load_config() -> dict:
    """Membaca config dari file. Return {} jika belum dikonfigurasi."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(config: dict) -> None:
    """Menyimpan config ke file dengan permission 600 (owner-only)."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Gunakan os.open dengan mode 0o600 agar file langsung dibuat dengan
    # permission ketat — tidak ada jendela race condition di mana file
    # sempat terbaca oleh proses lain sebelum chmod dipanggil.
    fd = os.open(CONFIG_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(config, f, indent=2)


def get_auth(token: Optional[str] = None, username: Optional[str] = None) -> httpx.BasicAuth:
    """
    Bangun BasicAuth untuk Bitbucket API.
    Prioritas: parameter fungsi → env vars → config file.
    """
    config = load_config()
    resolved_token = (
        token
        or os.environ.get("BITBUCKET_API_TOKEN")
        or config.get("token")
    )
    resolved_username = (
        username
        or os.environ.get("BITBUCKET_USERNAME")
        or config.get("username")
    )
    if not resolved_token or not resolved_username:
        raise ValueError(
            "Credentials belum dikonfigurasi. "
            "Jalankan tool setup_bitbucket atau set env BITBUCKET_API_TOKEN & BITBUCKET_USERNAME."
        )
    return httpx.BasicAuth(resolved_username, resolved_token)


def get_workspace(workspace: Optional[str] = None) -> str:
    """
    Resolve workspace.
    Prioritas: parameter fungsi → env var → config file.
    """
    config = load_config()
    resolved = (
        workspace
        or os.environ.get("BITBUCKET_WORKSPACE")
        or config.get("workspace")
    )
    if not resolved:
        raise ValueError(
            "Workspace belum dikonfigurasi. "
            "Berikan parameter workspace atau jalankan setup_bitbucket."
        )
    return resolved


def api_get(path: str, params: Optional[dict] = None) -> dict:
    """Helper: GET request ke Bitbucket API."""
    auth = get_auth()
    url = f"{BITBUCKET_API}{path}"
    response = httpx.get(url, auth=auth, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: Optional[dict] = None) -> dict:
    """Helper: POST request ke Bitbucket API."""
    auth = get_auth()
    url = f"{BITBUCKET_API}{path}"
    response = httpx.post(url, auth=auth, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def api_put(path: str, payload: Optional[dict] = None) -> dict:
    """Helper: PUT request ke Bitbucket API."""
    auth = get_auth()
    url = f"{BITBUCKET_API}{path}"
    response = httpx.put(url, auth=auth, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def api_delete(path: str) -> dict:
    """Helper: DELETE request ke Bitbucket API. Return dict kosong jika 204."""
    auth = get_auth()
    url = f"{BITBUCKET_API}{path}"
    response = httpx.delete(url, auth=auth, timeout=30)
    if response.status_code == 204:
        return {"status": "deleted"}
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Import semua tool modules (registrasi ke mcp terjadi di sini)
# ---------------------------------------------------------------------------
import bitmcp.tools  # noqa: E402, F401


def main() -> None:
    """Entry point untuk MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
