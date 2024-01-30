from typing import Union

from utils import ErrorMsg, get_suggested_answer_validation_res

from promptflow import tool
from promptflow.connections import AzureOpenAIConnection, OpenAIConnection


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def validate_suggested_answer(
    connection: Union[OpenAIConnection, AzureOpenAIConnection],
    model: str,
    suggested_answer: str,
    validate_suggested_answer_prompt: str,
):
    """
    1. Validates the given ground truth.

    Returns:
        dict: The generated ground truth and its validation result.
    """
    if not suggested_answer:
        return {"suggested_answer": "", "validation_res": None}

    validation_res = get_suggested_answer_validation_res(connection, model,
                                                         validate_suggested_answer_prompt, suggested_answer)
    is_valid_gt = validation_res.pass_validation
    failed_reason = ""
    if not is_valid_gt:
        failed_reason = ErrorMsg.INVALID_ANSWER.format(suggested_answer)
        print(failed_reason)
        suggested_answer = ""

    return {"suggested_answer": suggested_answer, "validation_res": validation_res}
