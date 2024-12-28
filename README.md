# AI Developer

## About
- this repository is for AI software developer. Simply put - automated SDLC process.
  

## Technostack
- python 3
- autogen
- AWS
- Docker
- terraform
- bash shell


## How it works in more details
1. This repository contains main code of the automated tool.
2. The tool itself may be laucnhed locally and used for a 


## SDLC process / CI/CD
0. There is a logic of the application described.
1. Take task from the [board](https://github.com/orgs/x-8-ai/projects/1/views/1?layout=board)
2. Create branch for your task in github repository. Must not repeat any existing branch name. 
3. Decompose, if needed, to number of subtasks.
3.1 build a list of actions that need to be completed one by one.
3.2 the appplication must be always working.
4. For each subtask do each step:
4.1 Optional. Write new test or modify existing. If needed. 
4.2 Optional. Write new code or modify existing new code. If needed.
4.3 Create commit.
4.4 Check that application can build and run. If something failed move to the step 5 with a failure details.
4.5 Push.
5. Create PR to the `develop` branch.
6. Assign @PavelLiakh as reviewer.


## Agreements
- `main` branch is `production` version. Contains only the same what already in production.
- `dev` branch is `development` version. Must always work.
