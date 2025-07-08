# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, Mock, patch

import pytest

from cpk_lib_python_aws.aws_sso_auditor.auditor import AWSSSOAuditor, NullOutputSink
from cpk_lib_python_aws.aws_sso_auditor.config import Config
from cpk_lib_python_aws.aws_sso_auditor.exceptions import AWSSSOAuditorError


class TestNullOutputSink:
    """Test the NullOutputSink class."""

    def test_null_output_sink_methods(self):
        """Test that all NullOutputSink methods can be called without error."""
        sink = NullOutputSink()

        # All methods should return None and not raise exceptions
        assert sink.progress("test message") is None
        assert sink.debug_info("test message") is None
        assert sink.warning("test message") is None
        assert sink.info("test message") is None
        assert sink.error("test message") is None

    """Test the AWSSSOAuditor class."""

    @patch("cpk_lib_python_aws.aws_sso_auditor.auditor.AWSClientManager")
    def test_auditor_initialization_with_default_config(self, mock_aws_manager):
        """Test auditor initialization with default configuration."""
        # Mock the AWS client manager
        mock_manager_instance = Mock()
        mock_manager_instance.sso_admin_client = Mock()
        mock_manager_instance.identitystore_client = Mock()
        mock_manager_instance.organizations_client = Mock()
        mock_manager_instance.identity_store_id = "d-123456789"
        mock_manager_instance.instance_arn = "arn:aws:sso:::instance/ssoins-123456789"
        mock_manager_instance.get_client_info.return_value = {"region": "us-east-1"}
        mock_aws_manager.return_value = mock_manager_instance

        auditor = AWSSSOAuditor()

        # Verify initialization
        assert auditor.config is not None
        assert isinstance(auditor.output_sink, NullOutputSink)
        assert auditor.identity_store_id == "d-123456789"
        assert auditor.instance_arn == "arn:aws:sso:::instance/ssoins-123456789"

    @patch("cpk_lib_python_aws.aws_sso_auditor.auditor.AWSClientManager")
    def test_auditor_initialization_with_custom_config(self, mock_aws_manager):
        """Test auditor initialization with custom configuration."""
        mock_manager_instance = Mock()
        mock_manager_instance.sso_admin_client = Mock()
        mock_manager_instance.identitystore_client = Mock()
        mock_manager_instance.organizations_client = Mock()
        mock_manager_instance.identity_store_id = "d-123456789"
        mock_manager_instance.instance_arn = "arn:aws:sso:::instance/ssoins-123456789"
        mock_manager_instance.get_client_info.return_value = {"region": "us-west-2"}
        mock_aws_manager.return_value = mock_manager_instance

        config = Config(aws_region="us-west-2", debug=True)
        output_sink = Mock()

        auditor = AWSSSOAuditor(config, output_sink)

        assert auditor.config.aws_region == "us-west-2"
        assert auditor.config.debug is True
        assert auditor.output_sink == output_sink

    @patch("cpk_lib_python_aws.aws_sso_auditor.auditor.AWSClientManager")
    def test_get_permission_sets_for_account_success(self, mock_aws_manager):
        """Test successful retrieval of permission sets for account."""
        # Setup mocks
        mock_manager_instance = Mock()
        mock_sso_client = Mock()
        mock_paginator = Mock()

        mock_sso_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [
            {
                "PermissionSets": [
                    "arn:aws:sso:::permissionSet/ps-123",
                    "arn:aws:sso:::permissionSet/ps-456",
                ]
            }
        ]

        mock_manager_instance.sso_admin_client = mock_sso_client
        mock_manager_instance.identitystore_client = Mock()
        mock_manager_instance.organizations_client = Mock()
        mock_manager_instance.identity_store_id = "d-123456789"
        mock_manager_instance.instance_arn = "arn:aws:sso:::instance/ssoins-123456789"
        mock_manager_instance.get_client_info.return_value = {"region": "us-east-1"}
        mock_aws_manager.return_value = mock_manager_instance

        auditor = AWSSSOAuditor()
        result = auditor.get_permission_sets_for_account("123456789012")

        assert len(result) == 2
        assert "arn:aws:sso:::permissionSet/ps-123" in result
        assert "arn:aws:sso:::permissionSet/ps-456" in result

    @patch("cpk_lib_python_aws.aws_sso_auditor.auditor.AWSClientManager")
    def test_get_permission_sets_for_account_failure(self, mock_aws_manager):
        """Test handling of errors when retrieving permission sets."""
        # Setup mocks to raise exception
        mock_manager_instance = Mock()
        mock_sso_client = Mock()
        mock_sso_client.get_paginator.side_effect = Exception("AWS API Error")

        mock_manager_instance.sso_admin_client = mock_sso_client
        mock_manager_instance.identitystore_client = Mock()
        mock_manager_instance.organizations_client = Mock()
        mock_manager_instance.identity_store_id = "d-123456789"
        mock_manager_instance.instance_arn = "arn:aws:sso:::instance/ssoins-123456789"
        mock_manager_instance.get_client_info.return_value = {"region": "us-east-1"}
        mock_aws_manager.return_value = mock_manager_instance

        auditor = AWSSSOAuditor()
        result = auditor.get_permission_sets_for_account("123456789012")

        # Should return empty list on error
        assert result == []

    @patch("cpk_lib_python_aws.aws_sso_auditor.auditor.AWSClientManager")
    def test_get_group_details_success(self, mock_aws_manager):
        """Test successful retrieval of group details."""
        mock_manager_instance = Mock()
        mock_identity_client = Mock()

        mock_identity_client.describe_group.return_value = {
            "GroupId": "group-123",
            "DisplayName": "Test Group",
            "Description": "A test group",
        }

        mock_manager_instance.sso_admin_client = Mock()
        mock_manager_instance.identitystore_client = mock_identity_client
        mock_manager_instance.organizations_client = Mock()
        mock_manager_instance.identity_store_id = "d-123456789"
        mock_manager_instance.instance_arn = "arn:aws:sso:::instance/ssoins-123456789"
        mock_manager_instance.get_client_info.return_value = {"region": "us-east-1"}
        mock_aws_manager.return_value = mock_manager_instance

        auditor = AWSSSOAuditor()
        result = auditor.get_group_details("group-123")

        assert result["GroupId"] == "group-123"
        assert result["DisplayName"] == "Test Group"
        assert result["Description"] == "A test group"

    @patch("cpk_lib_python_aws.aws_sso_auditor.auditor.AWSClientManager")
    def test_get_group_details_failure(self, mock_aws_manager):
        """Test handling of errors when retrieving group details."""
        mock_manager_instance = Mock()
        mock_identity_client = Mock()
        mock_identity_client.describe_group.side_effect = Exception("Group not found")

        mock_manager_instance.sso_admin_client = Mock()
        mock_manager_instance.identitystore_client = mock_identity_client
        mock_manager_instance.organizations_client = Mock()
        mock_manager_instance.identity_store_id = "d-123456789"
        mock_manager_instance.instance_arn = "arn:aws:sso:::instance/ssoins-123456789"
        mock_manager_instance.get_client_info.return_value = {"region": "us-east-1"}
        mock_aws_manager.return_value = mock_manager_instance

        auditor = AWSSSOAuditor()
        result = auditor.get_group_details("group-123")

        # Should return default values on error
        assert result["GroupId"] == "group-123"
        assert result["DisplayName"] == "Unknown"
        assert result["Description"] == ""

    @patch("cpk_lib_python_aws.aws_sso_auditor.auditor.AWSClientManager")
    def test_audit_account_basic_flow(self, mock_aws_manager):
        """Test basic audit_account flow with minimal data."""
        mock_manager_instance = Mock()
        mock_sso_client = Mock()
        mock_identity_client = Mock()

        # Mock get_all_account_assignments to return empty list
        mock_manager_instance.sso_admin_client = mock_sso_client
        mock_manager_instance.identitystore_client = mock_identity_client
        mock_manager_instance.organizations_client = Mock()
        mock_manager_instance.identity_store_id = "d-123456789"
        mock_manager_instance.instance_arn = "arn:aws:sso:::instance/ssoins-123456789"
        mock_manager_instance.get_client_info.return_value = {"region": "us-east-1"}
        mock_aws_manager.return_value = mock_manager_instance

        auditor = AWSSSOAuditor()

        # Mock the get_permission_sets_for_account to return empty list
        auditor.get_permission_sets_for_account = Mock(return_value=[])

        result = auditor.audit_account("123456789012")

        # Verify basic structure
        assert "metadata" in result
        assert "sso_groups" in result
        assert "permission_sets" in result
        assert "summary" in result
        assert result["metadata"]["account_id"] == "123456789012"
        assert result["summary"]["total_groups"] == 0
        assert result["summary"]["total_permission_sets"] == 0
        assert result["summary"]["total_assignments"] == 0
