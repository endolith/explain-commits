import argparse
import os

import git
import openai
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Fetch the API key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")


def commit_to_file(repo_path, commit_hash=None,
                   include_extensions=('.c', '.h')):
    repo = git.Repo(repo_path)

    # Get the specified commit, or default to the latest commit
    commit = repo.commit(commit_hash) if commit_hash else repo.head.commit

    # Get the diff
    parent = commit.parents[0] if commit.parents else None
    diff = parent.diff(commit, create_patch=True) if parent else None

    diff_text = ""
    if diff:
        for d in diff:
            if d.a_path.endswith(include_extensions):
                diff_text += d.__str__()
            else:
                # Short summary of changes for binary files, etc. [:5] includes
                # "---Binary files … differ", "file deleted in rhs", etc.
                diff_text += "\n".join(d.__str__().splitlines()[:5])
                diff_text += '\n[…]\n\n'  # […] is a single token ;)

    # Define output file name
    output_file = os.path.join(repo_path, f"{commit.hexsha}.txt")

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Commit Message:\n" + commit.message + "\n")
        if diff_text:
            f.write("Diff:\n" + diff_text)

    print(f"Commit information written to {output_file}")

    # Send the diff to GPT API
    send_to_gpt(diff_text)


def send_to_gpt(diff_text):
    system_message = "You are a skilled software engineer with expertise in automated code harmonization. You can understand the differences between files and apply similar changes to different files. Your task is to explain code diffs in plain English, elaborating on what they do and why they were made, to the best of your ability. Be prepared to answer follow-up questions about your explanations. Don't just summarize or paraphrase the changes in a list. Respond using Markdown."
    user_message = '```\n' + diff_text + '\n```'

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    # Print the assistant's response
    print(response.choices[0].message['content'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Write commit info to a file.")
    parser.add_argument("path", help="Path to the git repository.")
    parser.add_argument("-c", "--commit",
                        help="Specific commit hash. If not specified, "
                        "defaults to the latest commit.")
    parser.add_argument("-i", "--include",
                        help="Comma-separated list of file extensions to "
                        "include. Defaults to .c,.h",
                        default=".c,.h")

    args = parser.parse_args()
    include_extensions = tuple(args.include.split(','))

    commit_to_file(args.path, args.commit, include_extensions)
