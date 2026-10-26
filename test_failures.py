
import io
from contextlib import redirect_stderr
from unittest.mock import Mock, patch

import requests
import extract_customers


def check_failure(label, expected_message, api_url, mocked_get=None):
    error_output = io.StringIO()

    with patch("extract_customers.API_URL", api_url):
        with redirect_stderr(error_output):
            if mocked_get is None:
                try:
                    extract_customers.main()
                except SystemExit as exc:
                    assert exc.code == 1, f"{label}: wrong exit code"
                else:
                    raise AssertionError(f"{label}: expected exit code 1")
            else:
                with patch("extract_customers.requests.get", mocked_get):
                    try:
                        extract_customers.main()
                    except SystemExit as exc:
                        assert exc.code == 1, f"{label}: wrong exit code"
                    else:
                        raise AssertionError(
                            f"{label}: expected exit code 1"
                        )

    message = error_output.getvalue()
    assert expected_message in message, (
        f"{label}: expected {expected_message!r}, got {message!r}"
    )

    print(f"PASS: {label} (exit code 1, clear error message)")


# 1. Wrong URL: requests rejects this invalid URL.
check_failure(
    "Wrong URL",
    "API request failed:",
    "not-a-valid-url",
)

# 2. Timeout.
check_failure(
    "Timeout",
    "API request timed out",
    "https://example.com/users",
    Mock(side_effect=requests.Timeout("simulated timeout")),
)

# 3. Non-200 HTTP response.
http_error_response = Mock()
http_error_response.status_code = 503

check_failure(
    "Non-200 response",
    "API returned HTTP 503",
    "https://example.com/users",
    Mock(return_value=http_error_response),
)

# 4. Invalid JSON body.
invalid_json_response = Mock()
invalid_json_response.status_code = 200
invalid_json_response.json.side_effect = ValueError("invalid JSON")

check_failure(
    "Invalid JSON",
    "API response body is not valid JSON",
    "https://example.com/users",
    Mock(return_value=invalid_json_response),
)

print("\nAll four failure tests passed.")
