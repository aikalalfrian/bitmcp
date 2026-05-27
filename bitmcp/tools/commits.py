"""Tools: commits & file contents."""

from typing import Optional

from bitmcp.server import mcp, api_get, get_workspace


@mcp.tool()
def list_commits(
    repo_slug: str,
    branch: Optional[str] = None,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List commit dalam repository, opsional filter per branch.

    Args:
        repo_slug: Slug repository
        branch: Nama branch (opsional, default semua branch)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    params: dict = {"page": page, "pagelen": 20}
    if branch:
        params["include"] = branch
    return api_get(f"/repositories/{ws}/{repo_slug}/commits", params=params)


@mcp.tool()
def get_commit(
    repo_slug: str,
    commit_hash: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Detail sebuah commit.

    Args:
        repo_slug: Slug repository
        commit_hash: Hash commit (full atau 7-char short)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/commit/{commit_hash}")


@mcp.tool()
def get_commit_diff(
    repo_slug: str,
    spec: str,
    workspace: Optional[str] = None,
) -> str:
    """
    Tampilkan diff untuk satu commit atau range commit.

    Args:
        repo_slug: Slug repository
        spec: Hash commit atau range (contoh: 'abc123' atau 'abc123..def456')
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    import httpx
    from bitmcp.server import get_auth, BITBUCKET_API

    ws = get_workspace(workspace)
    auth = get_auth()
    url = f"{BITBUCKET_API}/repositories/{ws}/{repo_slug}/diff/{spec}"
    response = httpx.get(url, auth=auth, timeout=30)
    response.raise_for_status()
    return response.text


@mcp.tool()
def get_file_contents(
    repo_slug: str,
    file_path: str,
    branch: str = "main",
    workspace: Optional[str] = None,
) -> str:
    """
    Ambil isi file dari branch atau commit tertentu.

    Args:
        repo_slug: Slug repository
        file_path: Path file di repo (contoh: 'app/models/user.rb')
        branch: Branch atau commit hash (default: 'main')
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    import httpx
    from bitmcp.server import get_auth, BITBUCKET_API

    ws = get_workspace(workspace)
    auth = get_auth()
    url = f"{BITBUCKET_API}/repositories/{ws}/{repo_slug}/src/{branch}/{file_path}"
    response = httpx.get(url, auth=auth, timeout=30)
    response.raise_for_status()
    return response.text


@mcp.tool()
def get_commit_diffstat(
    repo_slug: str,
    spec: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Tampilkan ringkasan file yang berubah pada sebuah commit (diffstat).
    Lebih ringan dari diff karena hanya menampilkan nama file + status perubahan.

    Args:
        repo_slug: Slug repository
        spec: Hash commit atau range (contoh: 'abc123' atau 'abc123..def456')
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/diffstat/{spec}")


@mcp.tool()
def list_commit_statuses(
    repo_slug: str,
    commit_hash: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    List build statuses (CI/CD) yang terasosiasi dengan sebuah commit.
    Menampilkan status dari pipeline, Jenkins, atau sistem CI lain.

    Args:
        repo_slug: Slug repository
        commit_hash: Hash commit (full atau 7-char short)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/commit/{commit_hash}/statuses")


@mcp.tool()
def list_commit_comments(
    repo_slug: str,
    commit_hash: str,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List komentar pada sebuah commit.

    Args:
        repo_slug: Slug repository
        commit_hash: Hash commit
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/repositories/{ws}/{repo_slug}/commit/{commit_hash}/comments",
        params={"page": page, "pagelen": 50},
    )
