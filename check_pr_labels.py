#!/usr/bin/env python3

import os
import sys
import re
from github import Github

def get_env_var(env_var_name, echo_value=False):
    value=os.environ.get(env_var_name)

    if value is None:
        raise ValueError(f'The environmental variable {env_var_name} is empty!')

    if echo_value:
        print(f"{env_var_name} = {value}")

    return value

# Check if the number of input arguments is correct
if len(sys.argv) != 4:
    raise ValueError('Invalid number of arguments!')

# Get the GitHub token
token=sys.argv[1]

# Get the list of valid labels
valid_labels=sys.argv[2]
print(f'Valid labels are: {valid_labels}')

# Get the PR number
pr_number_str=sys.argv[3]

# Get needed values from the environmental variables
repo_name=get_env_var('GITHUB_REPOSITORY')
github_ref=get_env_var('GITHUB_REF')
github_event_name=get_env_var('GITHUB_EVENT_NAME')

# Create a repository object, using the GitHub token
repo = Github(token).get_repo(repo_name)

# When this actions runs on a "pull_reques_target" event, the pull request number is not
# available in the environmental variables; in that case it must be defined as an input
# value. Otherwise, we will extract it from the 'GITHUB_REF' variable.
if github_event_name == 'pull_request_target':
    # Verify the passed pull request number
    try:
        pr_number=int(pr_number_str)
    except ValueError:
        print(f'A valid pull request number input must be defined when triggering on ' \
            f'"pull_request_target". The pull request number passed was "{pr_number_str}".')
        raise
else:
    # Try to extract the pull request number from the GitHub reference.
    try:
        pr_number=int(re.search('refs/pull/([0-9]+)/merge', github_ref).group(1))
    except AttributeError:
        print(f'The pull request number could not be extracted from the GITHUB_REF = ' \
            f'"{github_ref}"')
        raise

print(f'Pull request number: {pr_number}')
print(f'github_ref: {github_ref}')


# Create a pull request object
pr = repo.get_pull(pr_number)

# Check if the PR comes from a fork. If so, the trigger must be 'pull_request_target'.
# Otherwise raise an exception here.
if pr.head.repo.full_name != pr.base.repo.full_name:
    if github_event_name != 'pull_request_target':
        raise Exception('PRs from forks are only supported when trigger on "pull_request_target"')

# Get the pull request labels
pr_labels = pr.get_labels()

# Get the list of reviews
pr_reviews = pr.get_reviews()

# This is a list of valid label found in the pull request
pr_has_valid_label = None
# Check which of the label in the pull request, are in the
# list of valid labels
for label in pr_labels:
    if label.name in valid_labels:
        pr_has_valid_label = True

if pr_has_valid_label:
    # If there were valid labels, create a pull request review, approving it
    print(f'Success! This pull request contains the following valid labels: {valid_labels}')
    repo.get_commit(sha=pr.head.sha).create_status(
        state="success",
        target_url="https://www.application.com",
        description="Label check succeded",
        context="OCA Check")
else:
    # If there were not valid labels, then create a pull request review, requesting changes
    print(f'Error! This pull request does not contain any of the valid labels: {valid_labels}')
    repo.get_commit(sha=pr.head.sha).create_status(
        state="failure",
        target_url="https://www.application.com",
        description="Label check failed",
        context="OCA Check")


