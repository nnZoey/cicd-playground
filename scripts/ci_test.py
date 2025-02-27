import pytest
import sys
import os
import requests
import subprocess


def run_tests(test_path):
    """Run all test files and capture failed test cases."""
    try:
        result = subprocess.run(
            ["pytest", test_path, "--tb=short"], capture_output=True, text=True
        )
        stdout_output = result.stdout

        if result.returncode == 5:
            print("No tests were found. Exiting with status 0.")
            sys.exit(0)  # No tests found, exit successfully
        elif result.returncode != 0:
            print("Tests failed!")
            failed_tests, failed_summary = extract_failed_tests(stdout_output)
            return failed_tests, failed_summary
        return [], ""
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)


def extract_failed_tests(output):
    """Extract failed test cases from pytest output and format details."""
    failed_tests = []
    failed_summary = []

    capturing = False
    for line in output.split("\n"):
        if line.startswith("FAILED "):  # Pytest marks failed tests with "FAILED"
            failed_tests.append(line.strip())
            capturing = True  # Start capturing details
            failed_summary.append(f"**{line.strip()}**")
        elif capturing and line.strip():  # Capture assertion errors
            failed_summary.append(f"> {line.strip()}")
        else:
            capturing = False  # Stop capturing on blank lines

    return failed_tests, "\n".join(failed_summary)


def extract_pr_number():
    """Extract PR number from environment variables."""
    github_ref = os.getenv("GITHUB_REF", "")
    if "pull" in github_ref:
        parts = github_ref.split("/")
        if len(parts) >= 3:
            return parts[2]  # PR number
    return os.getenv("PR_ID")  # If PR_ID is manually set in env


def comment_on_pr(repo, pr_number, failed_tests, failed_summary):
    """Post a formatted comment to a GitHub PR with test failures."""
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("GITHUB_TOKEN not set. Skipping PR comment.")
        return
    if not pr_number:
        print("PR number could not be extracted. Skipping PR comment.")
        return

    api_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}

    comment_body = f"""
        ## 🔥 Test Failures Summary  
        - **✅ Passed:** _(count not implemented)_  
        - **❌ Failed:** {len(failed_tests)} tests  
        - **📄 Detailed Failures:**  
    """

    response = requests.post(api_url, headers=headers, json={"body": comment_body})
    if response.status_code == 201:
        print("Successfully posted comment to PR.")
    else:
        print(f"Error posting comment: {response.text}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ci_test.py <test_directory>")
        sys.exit(1)

    test_directory = sys.argv[1]
    failed_tests, failed_summary = run_tests(test_directory)

    if failed_tests:
        print("The following tests failed:")
        print(failed_summary)

        repo = os.getenv("GITHUB_REPOSITORY", "user/repo")  # Auto-detect repo from GitHub Actions
        pr_number = extract_pr_number()

        # comment_on_pr(repo, pr_number, failed_tests, failed_summary)
        sys.exit(1)
