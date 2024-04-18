from typing import Optional

from promptflow.client import load_flow
from pathlib import Path
from promptflow.evals._constants import EvaluationMetrics


class SexualEvaluator:
    def __init__(self, project_scope: dict, credential=None,
                 log_level: Optional[int] = None):
        """
        Initialize an evaluator for sexual score.

        :param project_scope: The scope of the Azure AI project.
            It contains subscription id, resource group, and project name.
        :type project_scope: dict
        :param credential: The credential for connecting to Azure AI project.
        :type credential: TokenCredential
        :param log_level: The logging level.
        :type log_level: Optional[int]

        **Usage**

        .. code-block:: python

            eval_fn = SexualEvaluator(project_scope)
            result = eval_fn(question="What is the capital of France?", answer="Paris.")
        """

        self._project_scope = project_scope
        self._credential = credential

        # Load the flow as function
        current_dir = Path(__file__).resolve().parent
        flow_dir = current_dir / "flow"
        self._flow = load_flow(source=flow_dir, log_level=log_level)

    def __call__(self, *, question: str, answer: str, **kwargs):
        """Evaluates sexual content.

        :param question: The question to be evaluated.
        :type question: str
        :param answer: The answer to be evaluated.
        :type answer: str
        :return: The sexual score.
        :rtype: dict
        """

        # Run the evaluation flow
        output = self._flow(
            metric_name=EvaluationMetrics.SEXUAL,
            question=question,
            answer=answer,
            project_scope=self._project_scope,
            credential=self._credential)

        return output["result"]
