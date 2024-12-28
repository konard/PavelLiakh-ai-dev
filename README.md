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

## Agreements


**MVP выглядит так:**
- помещаем в контекст LLM список инструментов:
и1: список файлов проекта
и2: контент файла
и3: запись в файл
и4: поиск в гугле
и5: git commit 


1. мы вводим задачу
2. Начинается LLM business analys
3. Build plan by LLM -> список атомарных действий
4. research: использовать инструменты для поиска информации  
5. code writing.
- для каждой задачи
- пишется тест и записывается в подходящий файл
- пишется код в подходящий файл 
- выполняется QA
- если QA успешный - делается git commit
- переход к следующей задачи
6. qa 
- запускаются тесты
- если находится ошибка, то возвращаемся на этап написания кода. Максимум 3 раза

7. конец
