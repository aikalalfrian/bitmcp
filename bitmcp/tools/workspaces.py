"""Tools: workspace & project management."""

from typing import Optional

from bitmcp.server import mcp, api_get, api_post, get_workspace


@mcp.tool()
def list_workspaces(page: int = 1) -> dict:
    """
    List semua workspace Bitbucket yang bisa diakses oleh akun saat ini.

    Args:
        page: Nomor halaman (default 1, 25 workspace per halaman)
    """
    return api_get("/workspaces", params={"page": page, "pagelen": 25})


@mcp.tool()
def get_workspace_details(workspace: Optional[str] = None) -> dict:
    """
    Ambil detail sebuah workspace.

    Args:
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/workspaces/{ws}")


@mcp.tool()
def list_workspace_members(
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List semua anggota workspace beserta role mereka.

    Args:
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/workspaces/{ws}/members",
        params={"page": page, "pagelen": 50},
    )


@mcp.tool()
def list_workspace_permissions(
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List permission seluruh member di workspace (owner, collaborator, dll).

    Args:
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/workspaces/{ws}/permissions",
        params={"page": page, "pagelen": 50},
    )


@mcp.tool()
def list_projects(
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    List semua project di dalam workspace.

    Args:
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/workspaces/{ws}/projects",
        params={"page": page, "pagelen": 25},
    )


@mcp.tool()
def get_project(
    project_key: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Ambil detail sebuah project.

    Args:
        project_key: Key unik project (huruf kapital, contoh: 'BACKEND', 'FRONTEND')
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/workspaces/{ws}/projects/{project_key}")


@mcp.tool()
def create_project(
    name: str,
    key: str,
    description: Optional[str] = None,
    is_private: bool = True,
    workspace: Optional[str] = None,
) -> dict:
    """
    Buat project baru di workspace.

    Args:
        name: Nama tampilan project (contoh: 'Backend Services')
        key: Key unik project — huruf kapital tanpa spasi (contoh: 'BACKEND')
        description: Deskripsi opsional
        is_private: Private atau public (default True — direkomendasikan untuk project internal)
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    payload: dict = {"name": name, "key": key, "is_private": is_private}
    if description:
        payload["description"] = description
    return api_post(f"/workspaces/{ws}/projects", payload)


@mcp.tool()
def get_default_reviewers(
    repo_slug: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Lihat daftar default reviewer sebuah repository.
    Berguna untuk mengetahui siapa yang otomatis di-assign sebagai reviewer saat PR dibuat.

    Args:
        repo_slug: Slug repository
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(f"/repositories/{ws}/{repo_slug}/default-reviewers")


@mcp.tool()
def search_code(
    query: str,
    workspace: Optional[str] = None,
    page: int = 1,
) -> dict:
    """
    Cari kode di seluruh repository dalam workspace.

    Args:
        query: Query pencarian (contoh: 'TODO', 'class UserService', 'def calculate_tax')
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
        page: Nomor halaman (10 hasil per halaman)
    """
    ws = get_workspace(workspace)
    return api_get(
        f"/workspaces/{ws}/search/code",
        params={"search_query": query, "page": page, "pagelen": 10},
    )
