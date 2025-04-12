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