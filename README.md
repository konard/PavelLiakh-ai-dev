# AI Dev
AI-powered developer that automatically processes GitHub issues and implements solutions.

## Table of Contents
- [Usage Instructions](#usage-instructions)
  - [Setup](#setup)
  - [Target Repository Requirements](#target-repository-requirements)
  - [How to Use](#how-to-use)
  - [Troubleshooting](#troubleshooting)
- [Developers Instructions](#developers-instructions)

## Usage Instructions

### Setup

#### Prerequisites
- Python 3.12
- Poetry (Python package manager)
- GitHub account with API access
- OpenAI API key
- Git

#### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/PavelLiakh/ai-dev.git
   cd ai-dev
   ```

2. Install Poetry if you don't have it:
   - See [Poetry installation guide](https://github.com/python-poetry/install.python-poetry.org)

3. Create a `.env` file in the project root with the following variables:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   DEEPSEEK_API_KEY=your_deepseek_key_here
   GITHUB_API_KEY=your_github_personal_access_token
   GITHUB_REPO_NAME=YourUsername/your-target-repo
   ```

   Where to get API keys:
   - `OPENAI_API_KEY`: Create at https://platform.openai.com/api-keys
   - `DEEPSEEK_API_KEY`: Create at https://platform.deepseek.com/api-keys (can be mocked with any value for now as DeepSeek is not yet used)
   - `GITHUB_API_KEY`: Create at https://github.com/settings/tokens (requires `repo` scope for full access)
   - `GITHUB_REPO_NAME`: Your target repository in format `owner/repository-name`

4. Build the application:
   ```bash
   ./build.sh
   ```
   This script will:
   - Configure Poetry virtual environment
   - Initialize git submodules
   - Install dependencies
   - Build grammar parsers
   - Run tests
   - Format code
   - Run static analysis

5. Run the application:
   ```bash
   poetry run ai-dev
   ```

### Target Repository Requirements

Your target repository (specified in `GITHUB_REPO_NAME`) must meet the following requirements:

1. **GitHub Issues**: The repository must have open GitHub issues that need to be resolved
2. **Access Permissions**: Your GitHub API token must have appropriate permissions:
   - Read access to issues
   - Write access to create branches and pull requests
   - Access to repository contents
3. **Git Repository**: Must be a valid Git repository accessible via GitHub
4. **No Specific Code Requirements**: The AI-powered developer can work with any programming language or project structure

### How to Use

1. **Ensure your target repository has open issues**: The AI Dev tool monitors GitHub issues in the repository specified in your `.env` file.

2. **Run the AI Dev workflow**:
   ```bash
   poetry run ai-dev
   ```

3. **What happens automatically**:
   - The tool fetches all open issues from your target repository
   - For each new issue, it creates a development story
   - It analyzes the issue requirements
   - Creates an implementation plan
   - Generates code to solve the issue
   - Creates a new branch and commits changes
   - The results are tracked in the local database

4. **Monitor progress**: Check the console output for logs about:
   - Issues being processed
   - Stories being planned
   - Code being implemented
   - Build and test results

### Troubleshooting

#### Common Issues

**Problem**: `poetry: command not found`
- **Solution**: Install Poetry following the [official installation guide](https://python-poetry.org/docs/#installation)

**Problem**: Build fails with git submodule errors
- **Solution**: Ensure git is installed and run `git submodule update --init --recursive` manually

**Problem**: API authentication errors
- **Solution**:
  - Verify your API keys are correct in the `.env` file
  - Check that your GitHub token has the required `repo` scope
  - Ensure the `.env` file is in the project root directory

**Problem**: `GITHUB_REPO_NAME` repository not found
- **Solution**:
  - Verify the repository name format is correct: `owner/repo-name`
  - Ensure your GitHub token has access to this repository
  - Check if the repository exists and is not private (or your token has private repo access)

**Problem**: Tests fail during build
- **Solution**:
  - Check the `report.html` file for detailed test results
  - Ensure Python 3.12 is being used
  - Try running `poetry install` again to ensure all dependencies are installed

**Problem**: Permission denied errors
- **Solution**: Ensure `build.sh` has execute permissions: `chmod +x build.sh`

#### Getting Help

If you encounter issues not covered here:
1. Check existing issues at https://github.com/PavelLiakh/ai-dev/issues
2. Create a new issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - Error messages or logs
   - Your environment (OS, Python version, etc.)
3. Include relevant logs from the console output

## Developers Instructions

### Onboarding
- setup environment variables.
- setup python 3.12
- install poetry
    * see [poetry githun](https://github.com/python-poetry/install.python-poetry.org)
- build the app. Follow (Build)[#build] instructions.
- run the app. Follow (Run)[#run] instructions.
- check out [docs/sdlc.md](docs/sdlc.md) to learn more about development process.


### Environment Variables
- `OPENAI_API_KEY` - OpenAI API key. https://platform.openai.com/api-keys
- `DEEPSEEK_API_KEY` - Deepseek API key. https://platform.deepseek.com/api-keys. For now can be mocked with any value as deepseek not yet used.
- `GITHUB_API_KEY` - Do create here: https://github.com/settings/tokens
- `GITHUB_REPO_NAME` - Repository for testing github name. E.g `PavelLiakh/rut`

### Build
1. Run cli:
  ```
  ./build.sh
  ```

### Run
1. Run cli:
  ```
  poetry run ai-dev
  ```

## Debug Mode

FYI There is a UI for testing `Planner` logic.

In order to use it do run `src/poc/runner.py` and open `localhost` in browser.