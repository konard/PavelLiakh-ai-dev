# tg-assist
Telegram AI assistants generator and manager.

## Developer Instructions

### Onboarding
- check work rules in [Agreements](docs/agreements.md)
- be aware where to find more information:
  - [Aider](docs/aider.md) - Aider is a coding AI helper.
  - [Business Docs](docs/business.md) - Business logic of the app.
- download repo https://github.com/x-8-ai/tg-assist
- create two telegram bots. Go to https://t.me/BotFather
- setup environment variables.
- setup python 3.12
- install poetry
  - run `./install_poetry.sh`
    - add to path:
      - $HOME/.local/bin for Unix
      - %APPDATA%\Python\Scripts on Windows
      * see [poetry githun](https://github.com/python-poetry/install.python-poetry.org)
- build the app. Follow (Build)[#build] instructions.
- run the app. Follow (Run)[#run] instructions.

### Development process
SDLC or Development process is following:
- find a task to do. You can ask for it, you can find anything to improve, you can take a look into backlog.
- do implement the solution.
- do make pull request to `dev` branch. Do not merge it yourself.
  - make sure the `build` works.
- send pull request to review.
  - do fix comments if any. Or discuss.
  - once review finished, maintainer will merge.
- once changes are deployed to 'prod', the 'dev' will be merged into 'main'.
- do deploy prod once. Currently done by other maintainers only.
- pull-request checklist before merge:
  ```
  1 не должно быть конфликтов
  * Иначе не вмержится.
  * Ветка должна содержать все коммиты из target branch. Иначе после мержа результат билда может поменяться.
  
  2 должно быть осмысленое название ПРа
  Это поможет в будущем понять что происходило
  
  3 опционально, осмысленное название ветки
  Опционально, потому что помогает сориентироваться только в моменте.
  
  4 опциально, в комментах есть пруф рабостоспособности.
  Иногда я прикрепляю скриншот с образцом тестирования - это снимает обычно вопрос "как я это проверял" и "работает ли это (проверял ли я это)". Иногда на проектах писали типа "билд прошёл"
  ```

### Environment Variables
- `OPENAI_API_KEY` - OpenAI API key. https://platform.openai.com/api-keys
- `DEEPSEEK_API_KEY` - Deepseek API key. https://platform.deepseek.com/api-keys
- `MANAGER_BOT_TOKEN` - assistant creator (management) bot token
- `MANAGER_BOT_LINK` - assistant creator (management) bot name (e.g. my_bot)
- `EXAMPLE_BOT_TOKEN` - example bot token. Demonstration example bot for potential clients to try.
- `EXAMPLE_BOT_LINK` - example bot name (e.g. example_bot)
- `RNP_BOT_TOKEN` - RNP bot token. Фокус client bot token.
- `RNP_BOT_LINK` - RNP bot name (e.g. rnp_bot)
- `ADMIN_TELEGRAM_ID` - use your ID. Find here: https://t.me/RawDataBot -> message.from.id
- `GOOGLE_API_KEY` - Google Service Account API Key. See https://cloud.google.com/iam/docs/service-account-overview

### Build
1. Run
  ```
  ./build.sh
  ```

### Run
1. Run
    ```
    poetry run tg-assist
    ```

* once application run, you may see new folder `logs` and `storage`. You may mark them as ignored in IDE. It contains application runtime files.

### Production Build, Release and Run

#### Prerequisites
Do all of this once to prepare tools.

1. install `terraform`
- go to https://developer.hashicorp.com/terraform/install
- add `terraform` to PATH
- test with `terraform -v`

2. install AWS CLI
- go to https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- check with `aws --version`

3. configure AWS
3.0 Create access keys:
- go to https://us-east-1.console.aws.amazon.com/iam/home?region=us-west-2#/security_credentials
- create keys pair

3.1. do cli configuration
- Run and put values to:
```aws configure```
- Check with ```aws sts get-caller-identity```
- Do check no errors thrown when running ```aws s3 ls```

4. Generate SSH key
- do it just once
- add public key to your GitHub account
- private key will be added to system variables later

5. Setup environment variables for production instance.
Those variables will be used during terraform deployment to replace deployment placeholders with those secret variables.
Do add system variables:
- `TF_VAR_OPENAI_API_KEY` - OpenAI API Key
- `TF_VAR_DEEPSEEK_API_KEY` - Deepseek API Key
- `TF_VAR_MANAGER_BOT_TOKEN` - Manager bot token
- `TF_VAR_EXAMPLE_BOT_TOKEN` - Example bot token
- `TF_VAR_RNP_BOT_TOKEN` - RNP bot token
- `TF_VAR_GOOGLE_API_KEY` - Google Service Account API Key.
- `TF_VAR_SSH_KEY_1`, `TF_VAR_SSH_KEY_2` - GitHub private SSH key. The part between `---BEGIN---` and `---END---` collapsed into one-line. And then splitted into 2 parts with a similar length. Because of system variable length limitations.

6. Get AWS EC2 instance certificate (key)
- do get the certificate `terraform-entry-key-pem.pem` from the AWS account owner.
- put it to the `cicd` folder.

#### Release
- merge your changes to deploy to 'main' branch

#### Deploy
0. Do backup data
- go to `cicd` folder
- run ```./run_aws_backup.sh```
- go to [backup folder](https://github.com/x-8-ai/prod-backup/branches) and check that `data` and `logs` folders are updated.

1. Run
* currently, manual instance removal is required.
```
cicd/deploy.sh
```
- wait for a deployment process completion
* in some cases ```terraform init -reconfigure``` may help to fix terraform state.

2. Connect to EC2 to be sure it's launched
- run
```cicd/connect.sh```
- once connected, you can disconnect

3. Check logs are fine
- run
```cicd/logs.sh```
- once connected, you'll see installation logs.
- wait (or find) the label `Starting application...`
- check server started successfully

4. Do smoke E2E tests.
It's needed to be sure the app works.
- you may find use cases in `tests/e2e` folder.
- there are 2 prod bots to try:
  - [@x_8_ai_manager_bot](t.me/x_8_ai_manager_bot)
  - [@x_8_ai_example_bot](t.me/x_8_ai_example_bot)

#### Troubleshooting
You've created an EC2 instance and can't connect via SSH?
Do check security group Inbound rules. It should allow SSH port 22.
By default, it does not allow. So do add a new rule for SSH to allow access.


