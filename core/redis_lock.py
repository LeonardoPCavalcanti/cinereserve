import redis
from django.conf import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)

SEAT_LOCK_TTL = 600  # 10 minutes


def acquire_seat_lock(session_id: str, seat_id: str, user_id: str) -> bool:
    """
    Acquire a distributed lock for a seat.
    Returns True if acquired, False if already locked.
    Uses SET NX EX (atomic SET if Not eXists with EXpiry).
    """
    lock_key = f"seat_lock:{session_id}:{seat_id}"
    result = redis_client.set(lock_key, str(user_id), nx=True, ex=SEAT_LOCK_TTL)
    return result is not None


def release_seat_lock(session_id: str, seat_id: str, user_id: str) -> bool:
    """
    Release the lock only if it belongs to the user.
    Uses a Lua script for atomic check-and-delete.
    """
    lock_key = f"seat_lock:{session_id}:{seat_id}"
    lua_script = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """
    result = redis_client.eval(lua_script, 1, lock_key, str(user_id))
    return result == 1


def get_lock_ttl(session_id: str, seat_id: str) -> int:
    """Returns the remaining TTL of the lock in seconds."""
    lock_key = f"seat_lock:{session_id}:{seat_id}"
    return redis_client.ttl(lock_key)


def check_seat_lock(session_id: str, seat_id: str) -> str | None:
    """Returns the user_id holding the lock, or None."""
    lock_key = f"seat_lock:{session_id}:{seat_id}"
    value = redis_client.get(lock_key)
    return value.decode() if value else None
