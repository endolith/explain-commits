import argparse
import os

import git
import openai
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Fetch the API key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_diff_text(repo_path, commit_hash=None,
                  include_extensions=('.c', '.h', '.htm', '.py', '.BAT')):
    repo = git.Repo(repo_path)

    # Get the specified commit, or default to the latest commit
    commit = repo.commit(commit_hash) if commit_hash else repo.head.commit

    # Get the diff
    parent = commit.parents[0] if commit.parents else None
    diff = parent.diff(commit, create_patch=True) if parent else None

    diff_text = ""
    if diff:
        for d in diff:
            if d.a_path is None:  # File added
                diff_text += f"File added: {d.b_path}\n"
                diff_text += f"+ {d.b_blob.data_stream.read().decode('utf-8')}\n"
            elif d.b_path is None:  # File deleted
                diff_text += f"File deleted: {d.a_path}\n"
                diff_text += f"- {d.a_blob.data_stream.read().decode('utf-8')}\n"
            elif d.a_path.endswith(include_extensions):
                diff_text += d.__str__() + '\n\n'
            else:
                # Short summary of changes for binary files, etc. [:5] includes
                # "---Binary files … differ", "file deleted in rhs", etc.
                diff_text += "\n".join(d.__str__().splitlines()[:5])
                diff_text += '\n[…]\n\n'

    return commit.hexsha, commit.message, diff_text


def send_to_gpt_and_save(commit_hash, commit_message, diff_text, repo_path):
    with open(os.path.join(os.path.dirname(__file__),
                           'system_message.txt'), 'r') as file:
        system_message = file.read()

    user_message = "Commit Message:\n```\n" + commit_message + \
                   "```\n\nDiff:\n```diff\n" + diff_text + '\n```'

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    assistant_response = response.choices[0].message['content']

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
                        default=".c,.h,.htm,.py,.BAT")

    args = parser.parse_args()
    include_extensions = tuple(args.include.split(','))

    commit_hash, commit_message, diff_text = get_diff_text(
        args.path, args.commit, include_extensions)
    send_to_gpt_and_save(commit_hash, commit_message, diff_text, args.path)
