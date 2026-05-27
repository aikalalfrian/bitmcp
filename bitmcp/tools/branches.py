"""Tools: branch & tag management."""

from typing import Optional

from bitmcp.server import mcp, api_get, api_post, get_workspace


# ---------------------------------------------------------------------------
# Branches
# ---------------------------------------------------------------------------

@mcp.tool()
def list_branches(
    repo_slug: str,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List semua branch di sebuah repository.

    Args:
        repo_slug: Slug repository
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/repositories/{ws}/{repo_slug}/refs/branches",
        params={"page": page, "pagelen": 25},
    )


@mcp.tool()
def create_branch(
    repo_slug: str,
    branch_name: str,
    source_branch: str = "main",
    workspace: Optional[str] = None,
) -> dict:
    """
    Buat branch baru dari branch sumber.

    Args:
        repo_slug: Slug repository
        branch_name: Nama branch baru (contoh: 'feature/login')
        source_branch: Branch asal (default: 'main')
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_post(
        f"/repositories/{ws}/{repo_slug}/refs/branches",
        {"name": branch_name, "target": {"hash": source_branch}},
    )


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

@mcp.tool()
def list_tags(
    repo_slug: str,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List semua tag di sebuah repository.

    Args:
        repo_slug: Slug repository
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/repositories/{ws}/{repo_slug}/refs/tags",
        params={"page": page, "pagelen": 25},
    )


@mcp.tool()
def create_tag(
    repo_slug: str,
    tag_name: str,
    target_commit: str,
    message: Optional[str] = None,
    workspace: Optional[str] = None,
) -> dict:
    """
    Buat tag baru.

    Args:
        repo_slug: Slug repository
        tag_name: Nama tag (contoh: 'v2.1.0')
        target_commit: Hash commit atau branch yang akan di-tag
        message: Pesan tag opsional
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    payload: dict = {"name": tag_name, "target": {"hash": target_commit}}
    if message:
        payload["message"] = message
    return api_post(f"/repositories/{ws}/{repo_slug}/refs/tags", payload)


# ---------------------------------------------------------------------------
# Branching Model
# ---------------------------------------------------------------------------

@mcp.tool()
def get_branching_model(
    repo_slug: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Ambil konfigurasi branching model repository (Gitflow, trunk-based, dll).

    Menampilkan informasi tentang branch development, production, dan aturan
    penamaan branch (feature/, bugfix/, hotfix/, release/).

    Args:
        repo_slug: Slug repository
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/branching-model")
