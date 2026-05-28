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
import logging
from fastmcp import FastMCP
from urllib.parse import urlparse

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


def get_auth(token: Optional[str] = None, username: Optional[str] = None) -> tuple[Optional[httpx.Auth], dict]:
    """
    Build auth for Bitbucket API.
    Returns a tuple `(auth, headers)` where `auth` is an `httpx.Auth` instance
    for Basic auth (or `None`) and `headers` is a dict of headers to include
    (e.g. Authorization: Bearer ...).

    Priority: function params -> env vars -> config file.
    """
    config = load_config()
    # Ambil token/username dari parameter -> env -> config.
    raw_token = (
        token
        or os.environ.get("BITBUCKET_API_TOKEN")
        or config.get("token")
        or ""
    )
    raw_username = (
        username
        or os.environ.get("BITBUCKET_USERNAME")
        or config.get("username")
        or ""
    )

    # Deteksi karakter whitespace yang tidak diinginkan sebelum strip.
    token_has_surrounding_ws = raw_token != raw_token.strip()
    username_has_surrounding_ws = raw_username != raw_username.strip()

    resolved_token = raw_token.strip()
    resolved_username = raw_username.strip()

    # Determine auth method: env/config override OR infer from presence of username
    config_method = load_config().get("auth_method")
    env_method = os.environ.get("BITBUCKET_AUTH_METHOD")
    method = (env_method or config_method or ("basic" if resolved_username else "bearer")).lower()

    # Log non-sensitive details
    logger = logging.getLogger("bitmcp.server.auth")
    try:
        cfg_mode = oct(CONFIG_FILE.stat().st_mode & 0o777)
    except Exception:
        cfg_mode = "missing"
    logger.info(
        "get_auth: method=%s username_present=%s username_repr=%s token_len=%d token_ws=%s cfg_mode=%s",
        method,
        bool(resolved_username),
        repr(resolved_username),
        len(resolved_token),
        token_has_surrounding_ws,
        cfg_mode,
    )

    if not resolved_token:
        raise ValueError(
            "Credentials belum dikonfigurasi. "
            "Jalankan tool setup_bitbucket atau set env BITBUCKET_API_TOKEN."
        )

    if method in ("bearer", "token", "api_token"):
        # Use Authorization: Bearer <token>
        return None, {"Authorization": f"Bearer {resolved_token}"}

    # Default to basic auth
    if not resolved_username:
        raise ValueError(
            "Username diperlukan untuk Basic auth. "
            "Atau set BITBUCKET_AUTH_METHOD=bearer untuk menggunakan API token tanpa username."
        )
    return httpx.BasicAuth(resolved_username, resolved_token), {}


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
    # Normalisasi input workspace: terima slug, "bitbucket.org/<slug>", atau full URL
    try:
        # Jika user memasukkan URL lengkap (dengan scheme), ambil segmen path pertama
        parsed = urlparse(resolved)
        if parsed.scheme:
            path = parsed.path.strip('/')
            if path:
                resolved = path.split('/')[0]
        elif 'bitbucket.org' in resolved:
            # Jika string mengandung 'bitbucket.org', ambil apa yang ada setelahnya
            after = resolved.split('bitbucket.org', 1)[1].lstrip('/')
            if after:
                resolved = after.split('/')[0]
    except Exception:
        # Jika parsing gagal, kembalikan nilai apa adanya
        pass

    return resolved


def api_get(path: str, params: Optional[dict] = None) -> dict:
    """Helper: GET request ke Bitbucket API."""
    auth, headers = get_auth()
    url = f"{BITBUCKET_API}{path}"
    kwargs = {"params": params, "timeout": 30}
    if auth is not None:
        kwargs["auth"] = auth
    if headers:
        kwargs.setdefault("headers", {}).update(headers)
    try:
        response = httpx.get(url, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        resp = e.response
        body = (resp.text or "").strip()
        if resp.status_code == 401:
            raise RuntimeError(
                "Bitbucket authentication failed (401 Unauthorized). "
                "Verify your BITBUCKET_API_TOKEN and BITBUCKET_USERNAME, or run the 'setup_bitbucket' tool. "
                f"Response: {body}"
            )
        if resp.status_code == 403:
            raise RuntimeError(
                "Bitbucket API permission denied (403 Forbidden). "
                "The app password may be missing required scopes (e.g., repository/pullrequest). "
                f"Response: {body}"
            )
        if resp.status_code == 404:
            raise RuntimeError(
                "Bitbucket resource not found (404). "
                "Check that the workspace and repository slugs are correct (use slug, not full URL). "
                f"Response: {body}"
            )
        # Re-raise for other status codes to preserve original details
        raise


def api_post(path: str, payload: Optional[dict] = None) -> dict:
    """Helper: POST request ke Bitbucket API."""
    auth, headers = get_auth()
    url = f"{BITBUCKET_API}{path}"
    kwargs = {"json": payload, "timeout": 30}
    if auth is not None:
        kwargs["auth"] = auth
    if headers:
        kwargs.setdefault("headers", {}).update(headers)
    try:
        response = httpx.post(url, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        resp = e.response
        body = (resp.text or "").strip()
        if resp.status_code == 401:
            raise RuntimeError(
                "Bitbucket authentication failed (401 Unauthorized). "
                "Verify your BITBUCKET_API_TOKEN and BITBUCKET_USERNAME, or run the 'setup_bitbucket' tool. "
                f"Response: {body}"
            )
        if resp.status_code == 403:
            raise RuntimeError(
                "Bitbucket API permission denied (403 Forbidden). "
                "The app password may be missing required scopes. "
                f"Response: {body}"
            )
        raise


def api_put(path: str, payload: Optional[dict] = None) -> dict:
    """Helper: PUT request ke Bitbucket API."""
    auth, headers = get_auth()
    url = f"{BITBUCKET_API}{path}"
    kwargs = {"json": payload, "timeout": 30}
    if auth is not None:
        kwargs["auth"] = auth
    if headers:
        kwargs.setdefault("headers", {}).update(headers)
    try:
        response = httpx.put(url, **kwargs)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        resp = e.response
        body = (resp.text or "").strip()
        if resp.status_code == 401:
            raise RuntimeError(
                "Bitbucket authentication failed (401 Unauthorized). "
                "Verify your BITBUCKET_API_TOKEN and BITBUCKET_USERNAME, or run the 'setup_bitbucket' tool. "
                f"Response: {body}"
            )
        if resp.status_code == 403:
            raise RuntimeError(
                "Bitbucket API permission denied (403 Forbidden). "
                "The app password may be missing required scopes. "
                f"Response: {body}"
            )
        raise


def api_delete(path: str) -> dict:
    """Helper: DELETE request ke Bitbucket API. Return dict kosong jika 204."""
    auth, headers = get_auth()
    url = f"{BITBUCKET_API}{path}"
    kwargs = {"timeout": 30}
    if auth is not None:
        kwargs["auth"] = auth
    if headers:
        kwargs.setdefault("headers", {}).update(headers)
    try:
        response = httpx.delete(url, **kwargs)
        if response.status_code == 204:
            return {"status": "deleted"}
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        resp = e.response
        body = (resp.text or "").strip()
        if resp.status_code == 401:
            raise RuntimeError(
                "Bitbucket authentication failed (401 Unauthorized). "
                "Verify your BITBUCKET_API_TOKEN and BITBUCKET_USERNAME, or run the 'setup_bitbucket' tool. "
                f"Response: {body}"
            )
        if resp.status_code == 403:
            raise RuntimeError(
                "Bitbucket API permission denied (403 Forbidden). "
                "The app password may be missing required scopes. "
                f"Response: {body}"
            )
        raise


# ---------------------------------------------------------------------------
# Import semua tool modules (registrasi ke mcp terjadi di sini)
# ---------------------------------------------------------------------------
import bitmcp.tools  # noqa: E402, F401


def main() -> None:
    """Entry point untuk MCP server."""
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger = logging.getLogger("bitmcp.server")
        logger.info("Shutting down (KeyboardInterrupt)")
        return


if __name__ == "__main__":
    main()
