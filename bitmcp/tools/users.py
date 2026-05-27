"""Tools: user & account management."""

from typing import Optional

from bitmcp.server import mcp, api_get, get_workspace


@mcp.tool()
def get_current_user() -> dict:
    """
    Ambil profil akun Bitbucket yang sedang aktif (authenticated user).

    Berguna untuk mengecek apakah credentials sudah benar dan akun apa yang sedang login.
    """
    return api_get("/user")


@mcp.tool()
def get_user_profile(account_id: str) -> dict:
    """
    Ambil profil publik seorang user Bitbucket.

    Args:
        account_id: Account ID (UUID) atau username pengguna
                    (contoh: '{uuid}' atau 'johndoe')
    """
    return api_get(f"/users/{account_id}")


@mcp.tool()
def get_user_permissions(
    repo_slug: str,
    workspace: Optional[str] = None,
) -> dict:
    """
    Lihat permission user saat ini terhadap sebuah repository.

    Args:
        repo_slug: Slug repository yang ingin dicek permission-nya
        workspace: Workspace slug. Jika kosong, gunakan default dari config.
    """
    ws = get_workspace(workspace)
    return api_get(
        "/user/permissions/repositories",
        params={"q": f'repository.full_name="{ws}/{repo_slug}"'},
    )
