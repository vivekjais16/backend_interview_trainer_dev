from app.services.sql_runner import run_sql_query

def test_sql_runner_ecommerce():
    query = "SELECT name, price FROM products WHERE category = 'Electronics' ORDER BY price DESC;"
    res = run_sql_query(query, schema_name="ecommerce", include_explain=True)
    assert res["success"] is True
    assert len(res["rows"]) > 0
    assert "name" in res["columns"]
    assert "price" in res["columns"]
    assert res["query_plan"] is not None

def test_sql_runner_fintech():
    query = "SELECT user_name, balance FROM accounts WHERE balance > 10000;"
    res = run_sql_query(query, schema_name="fintech")
    assert res["success"] is True
    assert len(res["rows"]) >= 1

def test_sql_runner_hr():
    query = "SELECT name, salary FROM employees WHERE salary >= 200000;"
    res = run_sql_query(query, schema_name="hr_tech")
    assert res["success"] is True
    assert len(res["rows"]) >= 1

def test_sql_runner_forbidden_keyword():
    query = "PRAGMA table_info(products);"
    res = run_sql_query(query)
    assert res["success"] is False
    assert "forbidden" in res["error"]
