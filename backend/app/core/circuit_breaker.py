import time
from enum import Enum
from app.db.redis_client import get_redis_client, is_redis_available

class CircuitState(Enum):
    CLOSED    = "closed"      # normal — calls go through
    OPEN      = "open"        # failing — calls blocked
    HALF_OPEN = "half_open"   # testing — one call allowed

# Redis keys
CB_FAILURE_COUNT  = "circuit_breaker:failures"
CB_STATE          = "circuit_breaker:state"
CB_LAST_FAILURE   = "circuit_breaker:last_failure"
CB_HALF_OPEN_TEST = "circuit_breaker:half_open_test"

# Config
FAILURE_THRESHOLD  = 5    # open after 5 failures
RECOVERY_TIMEOUT   = 30   # try recovery after 30 seconds
FAILURE_WINDOW     = 60   # count failures within 60 seconds

def get_state() -> CircuitState:
    """Get current circuit breaker state from Redis."""
    if not is_redis_available():
        return CircuitState.CLOSED  # fail open

    redis = get_redis_client()
    state = redis.get(CB_STATE)

    if state is None:
        return CircuitState.CLOSED

    state_str = state.decode() if isinstance(state, bytes) else state

    # if OPEN — check if recovery timeout has passed
    if state_str == CircuitState.OPEN.value:
        last_failure = redis.get(CB_LAST_FAILURE)
        if last_failure:
            last_failure_time = float(
                last_failure.decode() if isinstance(last_failure, bytes)
                else last_failure
            )
            if time.time() - last_failure_time >= RECOVERY_TIMEOUT:
                # move to half-open — allow one test call
                _set_state(CircuitState.HALF_OPEN)
                return CircuitState.HALF_OPEN

    return CircuitState(state_str)

def record_success() -> None:
    """Call succeeded — reset failure count, close circuit."""
    if not is_redis_available():
        return
    redis = get_redis_client()
    redis.delete(CB_FAILURE_COUNT)
    redis.delete(CB_HALF_OPEN_TEST)
    _set_state(CircuitState.CLOSED)
    print("Circuit breaker: CLOSED (success recorded)")

def record_failure() -> None:
    """Call failed — increment counter, open circuit if threshold reached."""
    if not is_redis_available():
        return
    redis = get_redis_client()

    # increment failure count with window expiry
    failures = redis.incr(CB_FAILURE_COUNT)
    redis.expire(CB_FAILURE_COUNT, FAILURE_WINDOW)

    # record time of latest failure
    redis.set(CB_LAST_FAILURE, str(time.time()))

    print(f"Circuit breaker: failure {failures}/{FAILURE_THRESHOLD}")

    if failures >= FAILURE_THRESHOLD:
        _set_state(CircuitState.OPEN)
        print(f"Circuit breaker: OPEN after {failures} failures")

def is_call_allowed() -> bool:
    """
    Returns True if LLM call should proceed.
    CLOSED    → always allowed
    OPEN      → never allowed
    HALF_OPEN → allowed once (test call)
    """
    state = get_state()

    if state == CircuitState.CLOSED:
        return True

    if state == CircuitState.OPEN:
        return False

    if state == CircuitState.HALF_OPEN:
        if not is_redis_available():
            return True
        redis = get_redis_client()
        # only allow one test call in half-open
        test_in_progress = redis.get(CB_HALF_OPEN_TEST)
        if test_in_progress:
            return False  # test already in progress
        redis.set(CB_HALF_OPEN_TEST, "1", ex=30)
        print("Circuit breaker: HALF_OPEN — allowing test call")
        return True

    return True

def _set_state(state: CircuitState) -> None:
    if not is_redis_available():
        return
    get_redis_client().set(CB_STATE, state.value)

def get_circuit_status() -> dict:
    """Returns circuit breaker status — used by admin dashboard."""
    if not is_redis_available():
        return {"state": "unknown", "failures": 0}

    redis = get_redis_client()
    state = get_state()
    failures = redis.get(CB_FAILURE_COUNT)
    last_failure = redis.get(CB_LAST_FAILURE)

    failures_count = int(
        failures.decode() if isinstance(failures, bytes) else failures
    ) if failures else 0

    last_failure_time = float(
        last_failure.decode() if isinstance(last_failure, bytes) else last_failure
    ) if last_failure else None

    return {
        "state": state.value,
        "failures": failures_count,
        "threshold": FAILURE_THRESHOLD,
        "recovery_timeout_seconds": RECOVERY_TIMEOUT,
        "last_failure_at": last_failure_time
    }