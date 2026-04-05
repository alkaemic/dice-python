from dice.rng.base import RNG
from dice.rng.default import DefaultRNG

_default_rng = DefaultRNG()


def roll_die(sides: int, rng: RNG | None = None) -> int:
    """Roll a single die with the given number of sides.

    This is the single point of randomness for the entire library.
    All die-rolling code should delegate to this function.

    :param sides: Number of sides on the die.
    :param rng: Optional RNG instance. Uses DefaultRNG if not provided.
    :return: A random integer between 1 and sides (inclusive).
    :raises DiceValidationError: If sides < 1.
    """
    if sides < 1:
        from dice.errors import DiceValidationError

        raise DiceValidationError(
            code="INVALID_DIE_SIDES",
            message=f"Die must have at least 1 side, got {sides}",
        )
    if rng is None:
        rng = _default_rng
    return rng.randint(1, sides)
