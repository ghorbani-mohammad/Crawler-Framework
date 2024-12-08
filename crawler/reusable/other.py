import redis
import logging

REDIS_CLIENT = redis.Redis(host="crawler-redis", port=6379, db=5)


logger = logging.getLogger(__name__)


def only_one_concurrency(function=None, key="", timeout=None):
    def _dec(run_func):
        def _caller(*args, **kwargs):
            have_lock = False
            lock = REDIS_CLIENT.lock(key, timeout=timeout)
            try:
                have_lock = lock.acquire(blocking=False)
                if have_lock:
                    run_func(*args, **kwargs)
                else:
                    logger.info(f"Task skipped due to lock: {key}")
            finally:
                if have_lock:
                    try:
                        lock.release()
                    except redis.exceptions.LockError:
                        logger.warning(f"Failed to release lock: {key}")

        return _caller

    return _dec(function) if function is not None else _dec
