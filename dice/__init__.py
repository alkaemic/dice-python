"""dice — a Python library for rolling dice with Roll20-compatible notation."""

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from dice.api import roll  # noqa: E402
from dice.constants import SYNTAX_VERSION  # noqa: E402
from dice.errors import DiceError, DiceExecutionError, DiceParseError  # noqa: E402
from dice.evaluation import (  # noqa: E402
    DefaultEvaluator,
    Evaluator,
    evaluate,
    register_evaluator,
)
from dice.execution import ExecutionConfig, ExecutionResult, execute  # noqa: E402
from dice.grammar import ParseResult, parse, validate  # noqa: E402
from dice.rng import RNG, DefaultRNG, SeededRNG  # noqa: E402
from dice.roll_result import RollResult  # noqa: E402
from dice.terms import (  # noqa: E402
    FATE_FACE_VALUES,
    DiceTerm,
    DieResult,
    FunctionTerm,
    GroupTerm,
    GroupingTerm,
    NumericTerm,
    OperatorTerm,
    ParentheticalTerm,
    RollExpression,
    RollTerm,
)

__all__ = [
    # Core API
    "roll",
    "parse",
    "validate",
    "execute",
    "evaluate",
    "register_evaluator",
    # Result types
    "ParseResult",
    "ExecutionResult",
    "ExecutionConfig",
    "RollResult",
    # Evaluator
    "Evaluator",
    "DefaultEvaluator",
    # RNG
    "RNG",
    "DefaultRNG",
    "SeededRNG",
    # Errors
    "DiceError",
    "DiceParseError",
    "DiceExecutionError",
    # Terms
    "RollTerm",
    "RollExpression",
    "DiceTerm",
    "FATE_FACE_VALUES",
    "NumericTerm",
    "OperatorTerm",
    "ParentheticalTerm",
    "GroupTerm",
    "GroupingTerm",
    "FunctionTerm",
    "DieResult",
    # Constants
    "SYNTAX_VERSION",
]
