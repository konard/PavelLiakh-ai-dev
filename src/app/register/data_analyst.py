from pathlib import Path
from typing import Any
import traceback

from src.ioc import user_file_service
from src.app.service.entities import User
from src.app.register.entities import PostProcessorResponse
from src.app.register.metadata import get_metadata
from src.app.register.postprocessor import postprocess_answer
from src.app.register.planner import plan_data_retrieve
from src.app.register.preprocessor import preprocess_question
from src.app.register.rag import retrieve_data
from src.config import config
from src.infrastructure.db.debug_storage import store_debug_info
from src.ioc import log
from src.app.register.postprocessor import is_good_answer


def analyze_task(user_question: str, user: User = None) -> PostProcessorResponse:
    if config.is_test():
        return PostProcessorResponse.model_construct(
            explanations_and_details="Mocked business analyst response"
        )

    debug_data = []
    try:
        result, debug_data = do_analyze_task(user_question, user)
        debug_data.append({"app_version": config.version})
        answer_is_good = is_good_answer(user_question, result.model_dump().__str__())
        debug_data.append({"answer_is_good": answer_is_good})
        log.info(f"Answer is good enough: {answer_is_good}, {result}")
        if not answer_is_good:
            log.warning(f"Answer is not good enough: %s", result.model_dump().__str__())
            result, debug_data_2 = do_analyze_task(user_question, user)
            debug_data.append(debug_data_2)

        store_debug_info(debug_data)
        return result
    except Exception as e:
        log.error(f"Failed to analyze user question: %s", e)
        traceback.print_exc()
        debug_data.append({"error": str(e), "traceback": traceback.format_exc()})
        store_debug_info(debug_data)
        return PostProcessorResponse.model_construct(explanations_and_details="Failed to answer")


def do_analyze_task(user_question: str, user: User) -> tuple[PostProcessorResponse, Any]:
    debug_data = []
    data_file: Path = user_file_service.get_current_file_path(user)
    debug_data.append({"data_file": str(data_file)})
    debug_data.append({"metadata": get_metadata()})
    debug_data.append({"user_question": user_question})

    user_request = preprocess_question(user_question)
    debug_data.append({"preprocess": user_request.model_dump()})

    data_retrieve_plan = plan_data_retrieve(user_request)
    debug_data.append({"data_retrieve_plan": data_retrieve_plan.model_dump()})

    if data_retrieve_plan.enough_data:
        user_data, retrieve_debug_data = retrieve_data(
            file_path=str(data_file),
            metadata=get_metadata(),
            user_request=user_request,
            data_criteria=data_retrieve_plan,
        )
        debug_data.append({"user_data": user_data, "user_data_debug": retrieve_debug_data})
    else:
        user_data = f"(No data retrieved. Reason: {data_retrieve_plan.retrieve_plan})"
        log.info(f"Not enough data to answer the question.")

    postprocessed_answer = postprocess_answer(
        user_data, user_request, data_retrieve_plan.retrieve_plan
    )
    debug_data.append({"postprocessed_answer": postprocessed_answer.model_dump()})
    log.info(f"Postprocessed answer: %s", postprocessed_answer)

    log.info(f"Task analysis completed.")
    log.info(f"Debug data: %s", debug_data)

    return postprocessed_answer, debug_data


if __name__ == "__main__":
    result = analyze_task("Топ-5 продающихся товаров")

    print(f"Analysis Results:\n{result}")
