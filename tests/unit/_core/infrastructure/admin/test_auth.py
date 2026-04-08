import hmac
import os
from unittest.mock import MagicMock, patch


def _authenticate(
    username: str, password: str, admin_id: str, admin_password: str
) -> bool:
    """Replicate AdminAuthProvider.authenticate logic for isolated testing."""
    return hmac.compare_digest(username, admin_id) and hmac.compare_digest(
        password, admin_password
    )


class TestAdminAuthenticate:
    def test_valid_credentials(self):
        assert _authenticate("admin", "secret", "admin", "secret") is True

    def test_wrong_username(self):
        assert _authenticate("wrong", "secret", "admin", "secret") is False

    def test_wrong_password(self):
        assert _authenticate("admin", "wrong", "admin", "secret") is False

    def test_both_wrong(self):
        assert _authenticate("wrong", "wrong", "admin", "secret") is False

    def test_empty_credentials(self):
        assert _authenticate("", "", "admin", "secret") is False

    def test_similar_but_different(self):
        assert _authenticate("admin", "secre", "admin", "secret") is False
        assert _authenticate("admi", "secret", "admin", "secret") is False


class TestAdminAuthProviderImport:
    """Test AdminAuthProvider.authenticate with required env vars set."""

    @patch.dict(
        os.environ,
        {
            "ADMIN_ID": "admin",
            "ADMIN_PASSWORD": "admin",
            "ADMIN_STORAGE_SECRET": "test-secret",
            "DATABASE_ENGINE": "postgresql",
            "DATABASE_USER": "postgres",
            "DATABASE_PASSWORD": "postgres",
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "5432",
            "DATABASE_NAME": "postgres",
            "AWS_SQS_ACCESS_KEY": "test",
            "AWS_SQS_SECRET_KEY": "test",
            "AWS_SQS_URL": "http://localhost",
        },
    )
    def test_authenticate_integration(self):
        # Reload settings with test env vars
        with patch("src._core.infrastructure.admin.auth.settings") as mock_settings:
            mock_settings.admin_id = "testadmin"
            mock_settings.admin_password = "testpass"

            from src._core.infrastructure.admin.auth import AdminAuthProvider

            assert AdminAuthProvider.authenticate("testadmin", "testpass") is True
            assert AdminAuthProvider.authenticate("wrong", "testpass") is False
