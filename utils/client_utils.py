"""Client classification utilities."""


def is_generic_client(client: str) -> bool:
    """Check if client is a generic/placeholder value.

    Returns True for:
    - Empty or whitespace-only strings
    - Values ending with 'clients' (e.g., "Multiple Clients", "Fortune 500 Clients")
    - Values ending with 'project' (e.g., "Independent Project")

    Args:
        client: Client name to check

    Returns:
        True if client is generic, False if it's a named client
    """
    if not client or not client.strip():
        return True
    lower = client.lower().strip()
    return lower.endswith("clients") or lower.endswith("project")
