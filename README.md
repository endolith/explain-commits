# Git Commit Analyzer with GPT-3

This script analyzes a specific git commit or the latest commit in a repository. It fetches the commit message and code diffs, writes them to a text file, and also sends the diffs to OpenAI's GPT-3 for a natural language explanation.

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

4. Add your OpenAI API key in the `.env` file.

## Usage

### Command Line Arguments

- `path`: Path to the git repository.
- `-c`, `--commit`: Specific commit hash. Defaults to the latest commit if not specified.
- `-i`, `--include`: Comma-separated list of file extensions to include. Defaults to `.c,.h`.

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

1. Open SmartGit and navigate to `Tools -> Open Tools`.
2. Add a new tool with the following settings:
    - Command: Path to Python executable
    - Arguments: `"F:\Language models\explain_commits\explain_commits.py" -c ${commit} ${repositoryRootPath}`
    - Title: "GPT analyze commit"

Run this tool from SmartGit to analyze a commit.
