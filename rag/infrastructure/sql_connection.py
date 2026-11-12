
import os

from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal


def create_sql_connection():
    workspace_host = os.getenv("DATABRICKS_HOST")
    client_id = os.getenv("DATABRICKS_CLIENT_ID")
    client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

    required_values = {
        "DATABRICKS_HOST": workspace_host,
        "DATABRICKS_CLIENT_ID": client_id,
        "DATABRICKS_CLIENT_SECRET": client_secret,
        "DATABRICKS_WAREHOUSE_ID": warehouse_id
    }

    missing = [
        name for name, value in required_values.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            f"Missing Databricks configuration: {', '.join(missing)}"
        )

    server_hostname = (
        workspace_host
        .removeprefix("https://")
        .removeprefix("http://")
        .rstrip("/")
    )

    def credential_provider():
        config = Config(
            host=f"https://{server_hostname}",
            client_id=client_id,
            client_secret=client_secret
        )

        return oauth_service_principal(config)

    return sql.connect(
        server_hostname=server_hostname,
        http_path=f"/sql/1.0/warehouses/{warehouse_id}",
        credentials_provider=credential_provider
    )
