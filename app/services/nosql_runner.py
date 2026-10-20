import time
import json
import re
from typing import Dict, Any, List

SAMPLE_ORDERS = [
    {
        "_id": "ORD-5001",
        "customer": {"name": "Alice Smith", "tier": "VIP", "country": "US"},
        "items": [
            {"sku": "SKU-M3-MAX", "category": "Electronics", "qty": 1, "price": 2499.00},
            {"sku": "SKU-AIRPODS", "category": "Audio", "qty": 2, "price": 249.00}
        ],
        "total_amount": 2997.00,
        "status": "DELIVERED",
        "tags": ["express", "fragile"],
        "created_at": "2026-03-01T10:15:00Z"
    },
    {
        "_id": "ORD-5002",
        "customer": {"name": "Bob Jones", "tier": "Standard", "country": "UK"},
        "items": [
            {"sku": "SKU-DELL-XPS", "category": "Electronics", "qty": 1, "price": 1799.00}
        ],
        "total_amount": 1799.00,
        "status": "PROCESSING",
        "tags": ["standard"],
        "created_at": "2026-03-02T14:20:00Z"
    },
    {
        "_id": "ORD-5003",
        "customer": {"name": "Charlie Brown", "tier": "VIP", "country": "US"},
        "items": [
            {"sku": "SKU-CHAIR-AERON", "category": "Furniture", "qty": 1, "price": 1250.00},
            {"sku": "SKU-MONITOR-4K", "category": "Electronics", "qty": 2, "price": 450.00}
        ],
        "total_amount": 2150.00,
        "status": "DELIVERED",
        "tags": ["heavy", "express"],
        "created_at": "2026-03-03T09:00:00Z"
    },
    {
        "_id": "ORD-5004",
        "customer": {"name": "Diana Prince", "tier": "VIP", "country": "CA"},
        "items": [
            {"sku": "SKU-SONY-XM5", "category": "Audio", "qty": 1, "price": 399.00}
        ],
        "total_amount": 399.00,
        "status": "DELIVERED",
        "tags": ["fragile"],
        "created_at": "2026-03-04T16:30:00Z"
    }
]

def run_nosql_query(query_str: str) -> Dict[str, Any]:
    """
    Executes a MongoDB-style query (e.g. db.orders.find(...) or db.orders.aggregate(...))
    against sample document collections.
    """
    start_time = time.perf_counter()
    clean = query_str.strip()

    try:
        # Check if aggregate or find
        if "aggregate" in clean:
            # Extract JSON array from db.orders.aggregate([...])
            match = re.search(r'aggregate\s*\(\s*(\[.*?\])\s*\)', clean, re.DOTALL)
            if not match:
                raise ValueError("Invalid aggregate syntax. Expected db.orders.aggregate([ { ... } ])")
            
            pipeline_json = match.group(1)
            # Replace single quotes with double quotes for JSON parsing if needed
            pipeline_json = re.sub(r"'([^']*)'", r'"\1"', pipeline_json)
            pipeline = json.loads(pipeline_json)

            data = list(SAMPLE_ORDERS)
            for stage in pipeline:
                if "$match" in stage:
                    match_criteria = stage["$match"]
                    filtered = []
                    for doc in data:
                        matches = True
                        for k, v in match_criteria.items():
                            if "." in k:
                                parts = k.split(".")
                                sub = doc
                                for p in parts:
                                    sub = sub.get(p, {}) if isinstance(sub, dict) else None
                                if sub != v:
                                    matches = False
                                    break
                            else:
                                if doc.get(k) != v:
                                    matches = False
                                    break
                        if matches:
                            filtered.append(doc)
                    data = filtered

                elif "$unwind" in stage:
                    path = stage["$unwind"].replace("$", "")
                    unwound = []
                    for doc in data:
                        items = doc.get(path, [])
                        if isinstance(items, list):
                            for it in items:
                                new_doc = dict(doc)
                                new_doc[path] = it
                                unwound.append(new_doc)
                    data = unwound

                elif "$group" in stage:
                    group_def = stage["$group"]
                    id_field = group_def.get("_id", "").replace("$", "")
                    groups: Dict[str, Any] = {}
                    for doc in data:
                        if "." in id_field:
                            parts = id_field.split(".")
                            gid = doc
                            for p in parts:
                                gid = gid.get(p, "") if isinstance(gid, dict) else ""
                        else:
                            gid = doc.get(id_field, "UNKNOWN")

                        gid_str = str(gid)
                        if gid_str not in groups:
                            groups[gid_str] = {"_id": gid, "total_revenue": 0.0, "count": 0}
                        
                        groups[gid_str]["count"] += 1
                        if "total_revenue" in group_def and "$sum" in group_def["total_revenue"]:
                            sum_field = group_def["total_revenue"]["$sum"].replace("$", "")
                            groups[gid_str]["total_revenue"] += float(doc.get(sum_field, 0.0))
                    data = list(groups.values())

                elif "$sort" in stage:
                    sort_def = stage["$sort"]
                    for sk, sv in sort_def.items():
                        reverse = (sv == -1)
                        data.sort(key=lambda x: x.get(sk, 0), reverse=reverse)

            res_docs = data
        else:
            # Default find()
            res_docs = SAMPLE_ORDERS

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        return {
            "success": True,
            "documents": res_docs,
            "document_count": len(res_docs),
            "execution_time_ms": duration_ms,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "documents": [],
            "document_count": 0,
            "execution_time_ms": 0.0,
            "error": str(e)
        }

from app.contracts.execution import DocumentExecutionContract

class NoSQLExecutionService(DocumentExecutionContract):
    """
    Decoupled NoSQL MongoDB Execution Microservice Adapter.
    Implements DocumentExecutionContract to run document queries and aggregation stages safely.
    """
    def execute(self, query_str: str) -> Dict[str, Any]:
        return run_nosql_query(query_str)

nosql_execution_service = NoSQLExecutionService()
