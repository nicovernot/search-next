"""
Property-based tests for rate limiting configuration parsing.
"""
import json
import os
import pytest
from hypothesis import given, strategies as st, assume
from unittest.mock import patch

from app.models.rate_limit_models import RateLimit, RateLimitConfig
from app.settings import Settings


class TestRateLimitConfigurationParsing:
    """Property-based tests for rate limit configuration parsing."""

    @given(
        enabled=st.booleans(),
        default_requests=st.integers(min_value=1, max_value=10000),
        default_window=st.integers(min_value=1, max_value=3600),
        burst_multiplier=st.floats(min_value=1.0, max_value=10.0),
        authenticated_multiplier=st.floats(min_value=1.0, max_value=10.0),
        backend=st.sampled_from(['redis', 'memory']),
        log_violations=st.booleans(),
        metrics_enabled=st.booleans(),
    )
    def test_configuration_via_environment_variables(
        self,
        enabled,
        default_requests,
        default_window,
        burst_multiplier,
        authenticated_multiplier,
        backend,
        log_violations,
        metrics_enabled,
    ):
        """
        **Feature: rate-limiting, Property 6: Configuration via environment variables**
        
        For any valid rate limit configuration provided via environment variables,
        the system should apply those limits without requiring code changes.
        **Validates: Requirements 3.2**
        """
        # Create environment variables
        env_vars = {
            'RATE_LIMIT_ENABLED': str(enabled).lower(),
            'RATE_LIMIT_DEFAULT_REQUESTS': str(default_requests),
            'RATE_LIMIT_DEFAULT_WINDOW': str(default_window),
            'RATE_LIMIT_BURST_MULTIPLIER': str(burst_multiplier),
            'RATE_LIMIT_AUTHENTICATED_MULTIPLIER': str(authenticated_multiplier),
            'RATE_LIMIT_BACKEND': backend,
            'RATE_LIMIT_LOG_VIOLATIONS': str(log_violations).lower(),
            'RATE_LIMIT_METRICS_ENABLED': str(metrics_enabled).lower(),
        }
        
        # Mock environment variables
        with patch.dict(os.environ, env_vars, clear=False):
            # Create settings instance
            settings = Settings()
            
            # Get rate limit configuration
            rate_limit_config = settings.get_rate_limit_config()
            
            # Verify configuration matches environment variables
            assert rate_limit_config.enabled == enabled
            assert rate_limit_config.default_requests == default_requests
            assert rate_limit_config.default_window == default_window
            assert abs(rate_limit_config.burst_multiplier - burst_multiplier) < 0.001
            assert abs(rate_limit_config.authenticated_multiplier - authenticated_multiplier) < 0.001
            assert rate_limit_config.backend == backend
            assert rate_limit_config.log_violations == log_violations
            assert rate_limit_config.metrics_enabled == metrics_enabled

    @given(
        endpoints_data=st.dictionaries(
            keys=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
            values=st.fixed_dictionaries({
                'requests': st.integers(min_value=1, max_value=10000),
                'window': st.integers(min_value=1, max_value=3600),
                'burst_multiplier': st.floats(min_value=1.0, max_value=10.0).filter(lambda x: not (x != x))  # Filter NaN
            }),
            min_size=0,
            max_size=5
        )
    )
    def test_endpoint_specific_configuration_parsing(self, endpoints_data):
        """
        **Feature: rate-limiting, Property 6: Configuration via environment variables**
        
        For any valid endpoint-specific configuration provided via environment variables,
        the system should parse and apply those endpoint-specific limits.
        **Validates: Requirements 3.2**
        """
        # Convert to JSON string
        endpoints_json = json.dumps(endpoints_data)
        
        env_vars = {
            'RATE_LIMIT_ENDPOINTS': endpoints_json,
        }
        
        # Mock environment variables
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            rate_limit_config = settings.get_rate_limit_config()
            
            # Verify each endpoint configuration
            for endpoint_name, expected_config in endpoints_data.items():
                actual_limit = rate_limit_config.get_rate_limit_for_endpoint(endpoint_name)
                
                assert actual_limit.requests == expected_config['requests']
                assert actual_limit.window_seconds == expected_config['window']
                assert abs(actual_limit.burst_multiplier - expected_config['burst_multiplier']) < 0.001

    @given(
        ip_list=st.lists(
            st.builds(
                lambda a, b, c, d: f"{a}.{b}.{c}.{d}",
                st.integers(min_value=0, max_value=255),
                st.integers(min_value=0, max_value=255),
                st.integers(min_value=0, max_value=255),
                st.integers(min_value=0, max_value=255)
            ),
            min_size=0,
            max_size=10
        )
    )
    def test_ip_whitelist_configuration_parsing(self, ip_list):
        """
        **Feature: rate-limiting, Property 6: Configuration via environment variables**
        
        For any valid IP whitelist configuration provided via environment variables,
        the system should parse and apply the IP whitelist correctly.
        **Validates: Requirements 3.2**
        """
        # Create comma-separated IP list
        ip_whitelist_str = ','.join(ip_list)
        
        env_vars = {
            'RATE_LIMIT_IP_WHITELIST': ip_whitelist_str,
        }
        
        # Mock environment variables
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            rate_limit_config = settings.get_rate_limit_config()
            
            # Verify IP whitelist
            for ip in ip_list:
                assert rate_limit_config.is_ip_whitelisted(ip)
            
            # Verify non-whitelisted IPs are not allowed
            if ip_list:  # Only test if we have IPs in the list
                assert not rate_limit_config.is_ip_whitelisted('192.168.1.999')

    @given(
        environment=st.sampled_from(['development', 'production', 'test', 'staging'])
    )
    def test_environment_specific_defaults(self, environment):
        """
        **Feature: rate-limiting, Property 6: Configuration via environment variables**
        
        For any valid environment setting, the system should apply appropriate
        environment-specific defaults for rate limiting configuration.
        **Validates: Requirements 3.2**
        """
        env_vars = {
            'ENVIRONMENT': environment,
        }
        
        # Mock environment variables
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            
            # Verify environment-specific defaults are applied
            if environment == 'test':
                assert settings.rate_limit_default_requests == 10
            elif environment == 'production':
                assert settings.rate_limit_default_requests == 100
            elif environment == 'development':
                assert settings.rate_limit_default_requests == 1000
            elif environment == 'staging':
                assert settings.rate_limit_default_requests == 200
            
            # Verify endpoint-specific defaults are set
            assert settings.rate_limit_endpoints != ""
            
            # Parse and verify endpoint defaults
            endpoints_data = json.loads(settings.rate_limit_endpoints)
            assert 'search' in endpoints_data
            assert 'suggest' in endpoints_data
            
            # Verify environment-appropriate limits
            if environment == 'test':
                assert endpoints_data['search']['requests'] == 5
                assert endpoints_data['suggest']['requests'] == 20
            elif environment == 'production':
                assert endpoints_data['search']['requests'] == 50
                assert endpoints_data['suggest']['requests'] == 200

    def test_invalid_configuration_handling(self):
        """
        Test that invalid configuration values are properly rejected.
        **Validates: Requirements 3.2**
        """
        # Test invalid backend
        with pytest.raises(ValueError, match="rate_limit_backend must be"):
            with patch.dict(os.environ, {'RATE_LIMIT_BACKEND': 'invalid'}, clear=False):
                Settings()
        
        # Test invalid positive values
        with pytest.raises(ValueError, match="Rate limit values must be positive"):
            with patch.dict(os.environ, {'RATE_LIMIT_DEFAULT_REQUESTS': '0'}, clear=False):
                Settings()
        
        # Test invalid multipliers
        with pytest.raises(ValueError, match="Rate limit multipliers must be"):
            with patch.dict(os.environ, {'RATE_LIMIT_BURST_MULTIPLIER': '0.5'}, clear=False):
                Settings()

    def test_malformed_json_endpoints_configuration(self):
        """
        Test that malformed JSON in endpoints configuration is handled gracefully.
        **Validates: Requirements 3.2**
        """
        env_vars = {
            'RATE_LIMIT_ENDPOINTS': '{"invalid": json}',
        }
        
        # Should not raise exception, but should log warning and use empty endpoints
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings()
            rate_limit_config = settings.get_rate_limit_config()
            
            # Should fall back to empty endpoints configuration
            assert len(rate_limit_config.endpoints) == 0