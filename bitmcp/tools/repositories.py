"""Tools: repository management."""

from typing import Optional

from bitmcp.server import mcp, api_get, api_post, api_put, get_workspace


@mcp.tool()
def list_repositories(workspace: Optional[str] = None, page: int = 1) -> dict:
    """
    List semua repository dalam workspace.

    Args:
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman (default 1, 10 repo per halaman).
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}", params={"page": page, "pagelen": 10})


@mcp.tool()
def get_repository(repo_slug: str, workspace: Optional[str] = None) -> dict:
    """
    Detail sebuah repository.

    Args:
        repo_slug: Slug repository (contoh: 'qontak-backend')
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}")


@mcp.tool()
def create_repository(
    repo_slug: str,
    name: str,
    is_private: bool = True,
    description: Optional[str] = None,
    workspace: Optional[str] = None,
) -> dict:
    """
    Buat repository baru.

    Args:
        repo_slug: Slug untuk repository baru
        name: Nama tampilan repository
        is_private: True = private, False = public (default True)
        description: Deskripsi opsional
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    payload = {
        "scm": "git",
        "name": name,
        "is_private": is_private,
    }
    if description:
        payload["description"] = description
    return api_post(f"/repositories/{ws}/{repo_slug}", payload)


@mcp.tool()
def update_repository(
    repo_slug: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_private: Optional[bool] = None,
    workspace: Optional[str] = None,
) -> dict:
    """
    Update pengaturan repository.

    Args:
        repo_slug: Slug repository yang akan diupdate
        name: Nama baru (opsional)
        description: Deskripsi baru (opsional)
        is_private: Ubah visibility (opsional)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    payload = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if is_private is not None:
        payload["is_private"] = is_private
    return api_put(f"/repositories/{ws}/{repo_slug}", payload)


@mcp.tool()
def fork_repository(
    repo_slug: str,
    fork_name: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Fork sebuah repository.

    Args:
        repo_slug: Slug repository sumber
        fork_name: Nama untuk fork baru
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_post(f"/repositories/{ws}/{repo_slug}/forks", {"name": fork_name})


@mcp.tool()
def list_repository_forks(
    repo_slug: str,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List semua fork dari sebuah repository.

    Args:
        repo_slug: Slug repository sumber
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/repositories/{ws}/{repo_slug}/forks",
        params={"page": page, "pagelen": 20},
    )
