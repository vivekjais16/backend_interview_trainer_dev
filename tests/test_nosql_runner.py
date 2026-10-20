from app.services.nosql_runner import run_nosql_query

def test_nosql_find_default():
    query = "db.orders.find({})"
    res = run_nosql_query(query)
    assert res["success"] is True
    assert res["document_count"] >= 3

def test_nosql_aggregate_match_group():
    query = """
    db.orders.aggregate([
      { "$match": { "status": "DELIVERED" } },
      { "$group": { "_id": "$customer.tier", "total_revenue": { "$sum": "$total_amount" } } }
    ])
    """
    res = run_nosql_query(query)
    assert res["success"] is True
    assert res["document_count"] > 0
    assert any(doc["_id"] == "VIP" for doc in res["documents"])
