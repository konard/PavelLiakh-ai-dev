# AI Dev
AI-powered developer.

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
- `DEEPSEEK_API_KEY` - Deepseek API key. https://platform.deepseek.com/api-keys
- `GITHUB_API_KEY` - Do create here: https://github.com/settings/tokens

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