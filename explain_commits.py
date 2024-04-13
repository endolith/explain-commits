import argparse
import os

import chardet
import git
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

# Fetch the API key from the .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_diff_text(repo_path, commit_hash=None,
                  include_extensions=('.c', '.h', '.htm', '.py', '.BAT')):
    repo = git.Repo(repo_path)

    # Get the specified commit, or default to the latest commit
    commit = repo.commit(commit_hash) if commit_hash else repo.head.commit

    # Get the diff
    parent = commit.parents[0] if commit.parents else None
    diffs = parent.diff(commit, create_patch=True) if parent else []

    diff_text = ""
    for d in diffs:
        # Determine the file path and its extension
        file_path = d.b_path or d.a_path
        _, file_extension = os.path.splitext(file_path)

        # Skip files not in include_extensions
        if file_extension not in include_extensions:
            continue

        try:
            # Attempt to read the diff text
            raw_diff_data = d.diff
            if raw_diff_data:  # Ensure that there is a diff to read
                # Use chardet to guess the encoding of the diff content
                encoding_guess = chardet.detect(raw_diff_data)
                encoding = encoding_guess['encoding']

                if encoding:  # If chardet was able to guess an encoding
                    diff_data = raw_diff_data.decode(encoding)
                    diff_text += f"Diff for {file_path}:\n\n{diff_data}\n\n"
                else:
                    raise UnicodeDecodeError(
                        "chardet unable to guess encoding", b"", 0, 1, "No encoding detected")
        except UnicodeDecodeError:
            # If there is a UnicodeDecodeError or chardet cannot guess the encoding,
            # note it and skip the file
            diff_text += f"Error decoding file: {file_path} (may contain non-text content or encoding is unknown)\n"

    return commit.hexsha, commit.message, diff_text


def send_to_gpt_and_save(commit_hash, commit_message, diff_text, repo_path):
    # Create a file path for the diff
    diff_file_path = os.path.join(repo_path, f"{commit_hash}.diff")

    # Save the diff to a text file
    with open(diff_file_path, 'w', encoding='utf-8') as f:
        f.write(diff_text)

    print(f"Diff saved to {diff_file_path}")

    with open(os.path.join(os.path.dirname(__file__),
                           'system_message.txt'), 'r') as file:
        system_message = file.read()

    user_message = "Commit Message:\n````\n" + commit_message + \
                   "````\n\nDiff:\n````diff\n" + diff_text + '\n````'

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    # Corrected line to access the assistant's response
    assistant_response = response.choices[0].message.content

    conversation = '## System Message\n\n' + system_message + \
                   '\n\n## User Message\n\n' + user_message + \
                   '\n\n## Assistant Response\n\n' + assistant_response

    output_file = os.path.join(repo_path, f"{commit_hash}.md")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(conversation)

    print(f"Conversation saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get commit diff and explain it.")
    parser.add_argument("path", help="Path to the git repository.")
    parser.add_argument("-c", "--commit",
                        help="Specific commit hash. If not specified, "
                             "defaults to the latest commit.")
    parser.add_argument("-i", "--include",
                        help="Comma-separated list of file extensions to "
                             "include. Defaults to .c,.h",
                        default=".c,.xc,.h,.htm,.txt,.py,.BAT")

    args = parser.parse_args()
    include_extensions = tuple(args.include.split(','))

    commit_hash, commit_message, diff_text = get_diff_text(
        args.path, args.commit, include_extensions)
    send_to_gpt_and_save(commit_hash, commit_message, diff_text, args.path)
