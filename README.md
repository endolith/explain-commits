# GPT Explain Commits

This script analyzes a specific git commit or the latest commit in a repository. It fetches the commit message and code diffs, and sends them to OpenAI's ChatGPT for a natural language explanation.

## Installation

1. Clone the repository to your local machine.
2. Install the required Python packages:

    ```shell
    pip install gitpython openai python-dotenv
    ```

3. Create a `.env` file using the `.env.template` as a reference:

    ```shell
    cp .env.template .env
    ```

4. Add your [OpenAI API key](https://platform.openai.com/account/api-keys) in the `.env` file.

## Usage

### Command Line Arguments

- `path`: Path to the git repository.
- `-c`, `--commit`: Specific commit hash. Defaults to the latest commit if not specified.
- `-i`, `--include`: Comma-separated whitelist of file extensions to include. Defaults to `.c,.h,.py,.htm`.

### Example

To analyze a specific commit:

```bash
python explain_commits.py -c [commit_hash] [repository_path]
```

To analyze the latest commit in the repository:

```bash
python explain_commits.py [repository_path]
```

### SmartGit Integration

1. Open SmartGit and navigate to **Edit** → **Preferences** → **Tools**.
2. Add a new tool with the following settings:
    - **Menu Item Name**: "GPT explain commit"
    - **Command**: Path to Python executable
    - **Arguments**: `"[…]\explain_commits.py" -c ${commit} ${repositoryRootPath}`

Then this tool is available on the context menu for commits, which will output a `.md` file to the repo folder.
