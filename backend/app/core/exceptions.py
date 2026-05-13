class AgentWorkflowError(Exception):
    """Base exception for workflow failures."""


class LLMConfigurationError(AgentWorkflowError):
    """Raised when the OpenAI-compatible LLM configuration is incomplete."""


class RunbookNotFoundError(AgentWorkflowError):
    """Raised when no runbook can be matched for an error code."""

