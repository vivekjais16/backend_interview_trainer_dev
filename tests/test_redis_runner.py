from app.services.redis_runner import run_redis_commands

def test_redis_basic_strings():
    script = """
    SET user:101 'Satya Nadella'
    GET user:101
    """
    res = run_redis_commands(script)
    assert res["success"] is True
    assert len(res["logs"]) == 2
    assert res["logs"][0]["output"] == "OK"
    assert res["logs"][1]["output"] == "Satya Nadella"

def test_redis_hashes():
    script = """
    HSET user:session:200 token 'jwt-token-xyz'
    HGET user:session:200 token
    """
    res = run_redis_commands(script)
    assert res["success"] is True
    assert res["logs"][1]["output"] == "jwt-token-xyz"

def test_redis_zset_rate_limiter():
    script = """
    ZADD rate:user:1 1000 'req-1'
    ZADD rate:user:1 1005 'req-2'
    ZCARD rate:user:1
    ZRANGEBYSCORE rate:user:1 1000 1010
    """
    res = run_redis_commands(script)
    assert res["success"] is True
    assert res["logs"][2]["output"] == 2
    assert res["logs"][3]["output"] == ["req-1", "req-2"]
