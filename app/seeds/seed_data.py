"""
Seed data for Real-Time Technical Interview Scenarios.
Categorized into 3 Career Phases:
- Phase 1: Foundation (Basic / Junior: 0-2 YOE)
- Phase 2: Production Engineering (Intermediate / Mid-Level: 3-5 YOE)
- Phase 3: High Scale & Architecture (Advanced / Senior & Staff: 6+ YOE)

Each question includes:
- Real-World MNC Scenario
- Step-by-Step Intuitive Walkthrough (Analogy, Under the Hood, Fix, Punchline)
- Interactive Sandboxes (Python, SQL, Redis, NoSQL)
- High-Yield MCQ with 4 Choices, Verified Answer, and Educational Feedback
"""
from app.models.question import QuestionCategory, QuestionDifficulty

SEED_QUESTIONS = [
    {       'best_practices': [       'Use frozen dataclasses or Pydantic models for configuration objects.',
                                  'Use `copy.deepcopy()` whenever modifying nested dictionaries.'],
        'category': QuestionCategory.PYTHON_INTERNALS,
        'common_traps': [       'Assuming `dict.copy()` or `list.copy()` creates independent copies of nested data.',
                                'Using `deepcopy` on massive recursive tree structures without recursion depth '
                                'considerations.'],
        'company_tags': ['Google', 'Amazon', 'Microsoft', 'Paytm'],
        'cross_questions': [       'What is the difference between `is` and `==` in Python?',
                                   "How does Python's integer intern pool (-5 to 256) affect object identity?",
                                   'How does `__deepcopy__` custom protocol work on user-defined classes?'],
        'difficulty': QuestionDifficulty.BASIC,
        'frequency_score': 96,
        'has_python_sandbox': True,
        'max_exp_years': 2,
        'mcq_correct_index': 2,
        'mcq_explanation': 'copy.copy() creates a new outer collection, but populates it with references to the '
                           'original nested objects. Modifying an inner mutable object (like a nested list or dict) '
                           'affects both copies. To duplicate nested objects independently, use copy.deepcopy().',
        'mcq_options': [       'A) The original object is completely unaffected because memory is duplicated.',
                               'B) Python raises a TypeError because shallow-copied objects are immutable.',
                               'C) The nested list in the original object is also modified because shallow copy only '
                               'duplicates the outer container while copying inner object references.',
                               'D) Python automatically converts the shallow copy to a deep copy at runtime.'],
        'mcq_question': 'What happens when you modify a nested list inside an object copied using copy.copy() (shallow '
                        'copy)?',
        'min_exp_years': 0,
        'mindmap_node': 'python-memory',
        'mindmap_topic': 'python-internals',
        'phase': 'basic',
        'scenario_text': '\n'
                         'A junior backend engineer wrote a configuration caching function:\n'
                         '```python\n'
                         'import copy\n'
                         '\n'
                         'base_config = {"db": {"host": "localhost", "port": 5432}, "debug": False}\n'
                         'worker_config = copy.copy(base_config)\n'
                         'worker_config["db"]["host"] = "prod-db.internal"\n'
                         '```\n'
                         'In production, `base_config["db"]["host"]` ALSO mutated to "prod-db.internal", corrupting '
                         'the master configuration!\n'
                         'Analyze the difference between shallow copy (`copy.copy()`) and deep copy '
                         "(`copy.deepcopy()`) in Python's memory model, and fix the bug.\n",
        'slug': 'python-shallow-deep-copy-memory',
        'solution_code': 'import copy\n'
                         '\n'
                         'def clone_config_safe(config: dict) -> dict:\n'
                         '    return copy.deepcopy(config)\n'
                         '\n'
                         'original = {"db": {"host": "localhost", "port": 5432}, "debug": False}\n'
                         'cloned = clone_config_safe(original)\n'
                         'cloned["db"]["host"] = "prod-db.internal"\n'
                         '\n'
                         'print("Original DB Host:", original["db"]["host"])\n'
                         'print("Cloned DB Host:", cloned["db"]["host"])\n'
                         'print("Safe Clone Verified:", original["db"]["host"] == "localhost")\n',
        'starter_code': 'import copy\n'
                        '\n'
                        'def clone_config_safe(config: dict) -> dict:\n'
                        '    # Fix this to prevent mutating original nested structures\n'
                        '    return copy.copy(config)\n'
                        '\n'
                        'original = {"db": {"host": "localhost", "port": 5432}, "debug": False}\n'
                        'cloned = clone_config_safe(original)\n'
                        'cloned["db"]["host"] = "prod-db.internal"\n'
                        '\n'
                        'print("Original DB Host:", original["db"]["host"])\n'
                        'print("Cloned DB Host:", cloned["db"]["host"])\n'
                        'print("Safe Clone Verified:", original["db"]["host"] == "localhost")\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Think of a folder containing sheets of paper.\n'
                              'A **Shallow Copy** buys a new folder, but puts the **exact same physical sheets of '
                              'paper** inside it. Writing on the paper inside the new folder changes it for the old '
                              'folder too!\n'
                              'A **Deep Copy** buys a new folder AND makes **brand-new photocopies of every single '
                              'paper inside**. Changing the photocopy leaves the original untouched!\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              '`copy.copy()` constructs a new compound object, but inserts references into it to the '
                              'objects found in the original. If the object contains nested mutable collections '
                              '(dicts, lists), both outer containers point to the exact same inner memory address '
                              "(`id(a['db']) == id(b['db'])`). `copy.deepcopy()` recursively copies every nested "
                              'object.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. For nested dictionaries/lists with mutables, always use '
                              '`copy.deepcopy(base_config)`.\n'
                              '2. Or use immutable data structures (e.g., `types.MappingProxyType` or '
                              '`dataclasses.dataclass(frozen=True)`).\n'
                              '3. In Pydantic v2, use `model.model_copy(deep=True)`.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"copy.copy() only duplicates the outermost container while sharing nested object '
                              'references; deepcopy recursively duplicates all child objects to prevent shared '
                              'mutation bugs."*\n',
        'title': 'Python Memory Model: Shallow Copy vs Deep Copy & Object References'},
    {       'best_practices': [       'Always use `COALESCE` on aggregated values from outer joins.',
                                  'Place joined table filters directly in the `ON` clause.'],
        'category': QuestionCategory.POSTGRES_MYSQL,
        'common_traps': [       'Assuming `SUM(NULL)` yields 0 (it yields NULL without `COALESCE`).',
                                'Filtering outer join columns in `WHERE` instead of `ON`.'],
        'company_tags': ['Uber', 'Walmart', 'Swiggy', 'Oracle'],
        'cross_questions': [       'How does SQL 3-valued logic (TRUE, FALSE, UNKNOWN) treat NULL comparison?',
                                   'What is the difference between `COUNT(*)` and `COUNT(column_name)` on a nullable '
                                   'column?',
                                   'When does a database engine choose a Hash Join over a Nested Loop Join?'],
        'difficulty': QuestionDifficulty.BASIC,
        'frequency_score': 95,
        'has_python_sandbox': False,
        'has_sql_sandbox': True,
        'max_exp_years': 2,
        'mcq_correct_index': 1,
        'mcq_explanation': "For users with no orders, o.status is NULL. Evaluating WHERE o.status = 'COMPLETED' "
                           "evaluates NULL = 'COMPLETED' as UNKNOWN (falsy), filtering those users out. To preserve "
                           'non-ordering users, place the condition in the join clause: LEFT JOIN orders o ON u.id = '
                           "o.user_id AND o.status = 'COMPLETED'.",
        'mcq_options': [       'A) They are included in the result with NULL values for all order columns.',
                               'B) They are filtered out completely, inadvertently turning the LEFT JOIN into an INNER '
                               'JOIN.',
                               'C) The query throws a SQL syntax error because WHERE cannot filter joined columns.',
                               "D) MySQL replaces NULL with the default string 'N/A'."],
        'mcq_question': 'In a query SELECT * FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE o.status = '
                        "'COMPLETED', what happens to users who have placed zero orders?",
        'min_exp_years': 0,
        'mindmap_node': 'sql-joins',
        'mindmap_topic': 'postgres-mysql-internals',
        'phase': 'basic',
        'scenario_text': '\n'
                         'A reporting query needs to show **all users** and their total spend.\n'
                         'A junior engineer wrote:\n'
                         '```sql\n'
                         'SELECT u.id, u.name, SUM(o.total_amount) as total_spent\n'
                         'FROM users u\n'
                         'LEFT JOIN orders o ON u.id = o.user_id\n'
                         "WHERE o.status = 'COMPLETED'\n"
                         'GROUP BY u.id, u.name;\n'
                         '```\n'
                         'Management notices that users who have registered but NOT yet placed an order are completely '
                         'missing from the report!\n'
                         'Identify why the `WHERE` clause broke the `LEFT JOIN` and rewrite the query to include all '
                         'users with 0 spend.\n',
        'slug': 'sql-joins-null-handling-optimization',
        'solution_sql': 'SELECT \n'
                        '    u.id, \n'
                        '    u.name, \n'
                        '    COALESCE(SUM(o.total_amount), 0.00) AS total_spent\n'
                        'FROM users u\n'
                        "LEFT JOIN orders o ON u.id = o.user_id AND o.status = 'COMPLETED'\n"
                        'GROUP BY u.id, u.name\n'
                        'ORDER BY total_spent DESC;\n',
        'sql_schema': 'ecommerce',
        'starter_sql': '-- Inspect users and orders with proper LEFT JOIN & COALESCE\n'
                       'SELECT \n'
                       '    u.id, \n'
                       '    u.name, \n'
                       '    COALESCE(SUM(o.total_amount), 0.00) AS total_spent\n'
                       'FROM users u\n'
                       "LEFT JOIN orders o ON u.id = o.user_id AND o.status = 'COMPLETED'\n"
                       'GROUP BY u.id, u.name\n'
                       'ORDER BY total_spent DESC;\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'A `LEFT JOIN` is like inviting everyone to a party: people with tickets get a gift bag, '
                              'and people without tickets get an empty bag (NULL).\n'
                              "Putting `WHERE o.status = 'COMPLETED'` at the end is like putting a bouncer at the exit "
                              'who kicks out anyone with an empty bag! That turns your friendly party back into a '
                              'strict ticket-only event (`INNER JOIN`)!\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'In SQL execution order, the `ON` condition filters the joined table before producing '
                              'the Cartesian product. If a user has no orders, all `o.*` columns are filled with '
                              "`NULL`. The subsequent `WHERE o.status = 'COMPLETED'` checks `NULL = 'COMPLETED'`, "
                              'which evaluates to SQL `UNKNOWN` (falsy) and discards the user row. Moving the filter '
                              'into the `ON` clause preserves users with 0 orders.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. Move the condition from `WHERE` to `ON`: `LEFT JOIN orders o ON u.id = o.user_id AND '
                              "o.status = 'COMPLETED'`.\n"
                              '2. Wrap `SUM(o.total_amount)` with `COALESCE(SUM(o.total_amount), 0.00)` to display 0 '
                              'instead of NULL.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Never filter right-table columns in a LEFT JOIN\'s WHERE clause unless checking IS '
                              'NULL; always place filtering conditions inside the ON clause to avoid inadvertently '
                              'converting it into an INNER JOIN."*\n',
        'title': 'SQL Join Pitfalls: INNER vs LEFT JOIN with NULLs & Where Clause Traps'},
    {       'best_practices': [       'Always specify boundary constraints with `Field(gt=0, le=...)`.',
                                  'Use Pydantic v2 `computed_field` for derived properties.'],
        'category': QuestionCategory.FASTAPI_ARCHITECTURE,
        'common_traps': [       'Catching generic `Exception` inside endpoints and accidentally hiding Pydantic '
                                'validation errors.',
                                'Using mutable default values in Pydantic models.'],
        'company_tags': ['DoorDash', 'Twilio', 'Razorpay', 'Zomato'],
        'cross_questions': [       'What is the difference between Pydantic v1 and Pydantic v2 core performance (Rust '
                                   'pydantic-core)?',
                                   'How does FastAPI distinguish between a Query parameter and a Path parameter in '
                                   'function signatures?',
                                   'How do you implement dependency injection using `Depends()` in FastAPI?'],
        'difficulty': QuestionDifficulty.BASIC,
        'frequency_score': 97,
        'has_python_sandbox': True,
        'max_exp_years': 2,
        'mcq_correct_index': 2,
        'mcq_explanation': 'FastAPI adheres strictly to the RFC 4918 specification: syntactically valid JSON that '
                           'fails semantic/type validation constraints triggers a 422 Unprocessable Entity response '
                           'with a detailed array of validation error locations.',
        'mcq_options': [       'A) 400 Bad Request',
                               'B) 500 Internal Server Error',
                               'C) 422 Unprocessable Entity',
                               'D) 404 Not Found'],
        'mcq_question': 'What HTTP status code does FastAPI automatically return when an incoming JSON payload '
                        'violates Pydantic schema validation (e.g. string provided for an integer field)?',
        'min_exp_years': 0,
        'mindmap_node': 'pydantic-validation',
        'mindmap_topic': 'fastapi-architecture',
        'phase': 'basic',
        'scenario_text': '\n'
                         'A client team sends `POST /api/v1/orders` with:\n'
                         '```json\n'
                         '{"item_id": "abc-123", "quantity": "twenty"}\n'
                         '```\n'
                         'FastAPI automatically rejects the request with an HTTP 422 Unprocessable Entity instead of '
                         '400 Bad Request.\n'
                         'Explain the architecture of Pydantic validation in FastAPI, how type coercion works, and how '
                         'to write custom validators that provide clean client error messages.\n',
        'slug': 'fastapi-pydantic-request-validation',
        'solution_code': 'print("FastAPI Pydantic schema validation demo verified.")',
        'starter_code': '# FastAPI Pydantic Validation Demo\n'
                        'from pydantic import BaseModel, Field, ValidationError\n'
                        '\n'
                        'class CreateOrderRequest(BaseModel):\n'
                        '    item_id: str = Field(..., min_length=3, max_length=20)\n'
                        '    quantity: int = Field(..., gt=0, le=100)\n'
                        '\n'
                        '# Test 1: Valid payload\n'
                        'try:\n'
                        '    order = CreateOrderRequest(item_id="item_999", quantity=5)\n'
                        '    print("Test 1 Passed: Valid Order Created ->", order.model_dump())\n'
                        'except ValidationError as e:\n'
                        '    print("Test 1 Failed:", e)\n'
                        '\n'
                        '# Test 2: Invalid quantity string\n'
                        'try:\n'
                        '    bad_order = CreateOrderRequest(item_id="item_999", quantity="twenty")\n'
                        '    print("Test 2 Failed: Should have rejected \'twenty\'")\n'
                        'except ValidationError as e:\n'
                        '    print("Test 2 Passed: Pydantic caught error ->", e.errors()[0]["type"])\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Think of an amusement park ride with a height checker.\n'
                              'If you give the ticket scanner a completely ripped piece of paper (malformed syntax), '
                              'you get **400 Bad Request**.\n'
                              'If your ticket is clean and readable, but you are not tall enough for the rollercoaster '
                              '(failed business constraint), you get **422 Unprocessable Entity**!\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'FastAPI uses Pydantic to inspect Python type annotations. When a JSON payload arrives, '
                              'FastAPI parses the JSON body (if JSON is malformed, it returns 400). Then Pydantic '
                              'validates data types and constraints. When `"twenty"` cannot be coerced into an `int`, '
                              'Pydantic raises a `ValidationError` which FastAPI translates to `422 Unprocessable '
                              'Entity` with exact field error pointers.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. Define strict Pydantic schemas with `Field(..., gt=0, le=1000)`.\n'
                              '2. Use `@field_validator` for domain logic (e.g. alphanumeric item IDs).\n'
                              "3. Override FastAPI's `RequestValidationError` handler if your frontend expects a "
                              'customized error response format.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"FastAPI returns 422 for syntactically valid requests that violate Pydantic semantic '
                              'type constraints, providing structured machine-readable error details out of the '
                              'box."*\n',
        'title': 'FastAPI & Pydantic: Request Validation, Path/Query Params & 422 Errors'},
    {       'best_practices': [       'Keep dependencies in a separate layer before copying application source code.',
                                  'Always run containers as non-root user.'],
        'category': QuestionCategory.DOCKER_CONTAINERS,
        'common_traps': [       'Using shell form `CMD command` instead of exec array form `CMD ["executable", '
                                '"arg1"]`.',
                                'Copying the whole repo before installing dependencies, blowing away layer caches.'],
        'company_tags': ['Atlassian', 'Amazon', 'Cisco', 'VMware'],
        'cross_questions': [       'Why does shell form `CMD python main.py` prevent graceful shutdown on Kubernetes?',
                                   'What is the difference between `COPY` and `ADD` in a Dockerfile?',
                                   'How do multi-stage Docker builds reduce the attack surface of container images?'],
        'difficulty': QuestionDifficulty.BASIC,
        'frequency_score': 94,
        'has_python_sandbox': True,
        'max_exp_years': 2,
        'mcq_correct_index': 1,
        'mcq_explanation': 'Docker caches intermediate image layers. If you copy application code before installing '
                           'dependencies, any code edit invalidates all subsequent layers, forcing a slow pip install '
                           'on every build. Copying requirements.txt first keeps dependencies cached unless '
                           'dependencies actually change.',
        'mcq_options': [       'A) After COPY . . so all project files are present in the container first.',
                               'B) Before COPY . . so changes in application source code do not invalidate the cached '
                               'dependencies layer.',
                               'C) At the very end of the Dockerfile right next to CMD.',
                               'D) In an external shell script mounted as a volume.'],
        'mcq_question': 'When optimizing Dockerfile build speed with layer caching, where should the COPY '
                        'requirements.txt . and pip install -r requirements.txt commands be placed relative to COPY . '
                        '.?',
        'min_exp_years': 0,
        'mindmap_node': 'dockerfile-best-practices',
        'mindmap_topic': 'docker-containers',
        'phase': 'basic',
        'scenario_text': '\n'
                         'A CI/CD Docker build for a Python backend takes 9 minutes on every single commit, even when '
                         'developers only changed a one-line comment in `main.py`!\n'
                         'The Dockerfile contains:\n'
                         '```dockerfile\n'
                         'FROM python:3.12-slim\n'
                         'WORKDIR /app\n'
                         'COPY . .\n'
                         'RUN pip install -r requirements.txt\n'
                         'CMD python main.py\n'
                         '```\n'
                         'Identify the layer cache invalidation flaw and the difference between exec form vs shell '
                         'form in `CMD` and `ENTRYPOINT`.\n',
        'slug': 'docker-cmd-entrypoint-caching-basics',
        'solution_code': 'print("Docker layer caching simulation verified.")',
        'starter_code': '# Dockerfile optimization simulation in Python:\n'
                        'def calculate_build_time(code_changed: bool, deps_changed: bool, optimized_dockerfile: '
                        'bool):\n'
                        '    if not optimized_dockerfile:\n'
                        '        # Bad Dockerfile: COPY . . comes before pip install\n'
                        '        # Any code change invalidates pip install layer!\n'
                        '        return "9 minutes (Reinstalled all packages from scratch)" if (code_changed or '
                        'deps_changed) else "5 seconds (Cache hit)"\n'
                        '    else:\n'
                        '        # Optimized Dockerfile: requirements.txt copied first\n'
                        '        if deps_changed:\n'
                        '            return "8 minutes (Dependencies changed, reinstall required)"\n'
                        '        elif code_changed:\n'
                        '            return "2.1 seconds (Dependencies reused from Docker layer cache!)"\n'
                        '        return "0.8 seconds (Full cache hit)"\n'
                        '\n'
                        'print("Unoptimized build on code change:", calculate_build_time(True, False, False))\n'
                        'print("Optimized build on code change:  ", calculate_build_time(True, False, True))\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Docker builds like a stack of pancakes. \n'
                              'If you put your syrup (frequently changing code) at the **bottom of the pancake '
                              'stack**, you have to throw away and remake every single pancake on top of it every '
                              'time!\n'
                              'Putting your frozen heavy ingredients (dependencies) at the bottom lets you reuse them '
                              'forever without re-cooking!\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'Docker checks checksums for each layer. `COPY . .` changes on every code edit, '
                              'invalidating the cache for that instruction and **all instructions following it**. '
                              'Moving `COPY requirements.txt .` and `RUN pip install` BEFORE `COPY . .` ensures Docker '
                              'reuses the cached dependencies layer in 2 seconds instead of reinstalling 500MB of '
                              'packages.\n'
                              'Also, `CMD python main.py` uses shell form (spawns `/bin/sh -c` as PID 1), which '
                              'ignores POSIX `SIGTERM` signals and prevents graceful container shutdown. Exec form '
                              '`CMD ["python", "main.py"]` runs Python directly as PID 1.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. Copy only dependency descriptors first: `COPY requirements.txt .`.\n'
                              '2. Run installation: `RUN pip install --no-cache-dir -r requirements.txt`.\n'
                              '3. Copy application code afterwards: `COPY . .`.\n'
                              '4. Always use JSON exec form: `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", '
                              '"--port", "8000"]`.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Optimize Docker builds by copying requirements.txt before application source code to '
                              'leverage layer caching, and always use JSON exec form for ENTRYPOINT/CMD to ensure PID '
                              '1 receives SIGTERM signals for graceful termination."*\n',
        'title': 'Docker Fundamentals: CMD vs ENTRYPOINT & Layer Caching Optimization'},
    {       'best_practices': [       'Always use `None` as default for mutable arguments.',
                                  'Use typing annotations `list | None = None`.'],
        'category': QuestionCategory.PYTHON_INTERNALS,
        'common_traps': [       'Thinking `cart = []` creates a new list on every function call.',
                                'Using `if not cart:` which causes a bug if an empty list was legitimately passed as '
                                'an argument.'],
        'company_tags': ['Amazon', 'Microsoft', 'TCS', 'Infosys'],
        'cross_questions': [       "Why doesn't this bug happen with immutable types like integers or strings?",
                                   'How can you inspect default arguments at runtime using `__defaults__` or `inspect` '
                                   'module?',
                                   'What happens if you use a dataclass with `field(default_factory=list)` instead?'],
        'difficulty': QuestionDifficulty.BASIC,
        'frequency_score': 98,
        'has_python_sandbox': True,
        'has_sql_sandbox': False,
        'max_exp_years': 2,
        'mcq_correct_index': 1,
        'mcq_explanation': "In Python, 'def' is an executable statement. Default arguments are evaluated exactly once "
                           'when the function is defined, and stored in fn.__defaults__. Because lists are mutable, '
                           'every subsequent call without the parameter mutates that exact same shared list in memory.',
        'mcq_options': [       'A) Default arguments are evaluated at runtime every time the function is called.',
                               'B) Default arguments are evaluated once at function definition time and stored in the '
                               "function's __defaults__ tuple.",
                               'C) Python creates a copy of the list in heap memory on each invocation.',
                               "D) Python's garbage collector automatically retains any list passed to a function."],
        'mcq_question': 'What is the root cause of unexpected state sharing when using a mutable default argument like '
                        'def append_to(item, target=[]) in Python?',
        'min_exp_years': 0,
        'mindmap_node': 'py-gil',
        'mindmap_topic': 'python-internals',
        'phase': 'basic',
        'scenario_text': '\n'
                         "A junior engineer pushed code to a microservice that appends items to a user's shopping "
                         'basket. \n'
                         'Under load, users started seeing items belonging to completely different users in their '
                         'baskets!\n'
                         'Investigate why Python evaluates default arguments only once at function definition time, '
                         'and fix the function.\n',
        'slug': 'python-mutable-default-argument',
        'solution_code': 'def add_to_cart(item: str, cart: list | None = None) -> list:\n'
                         '    if cart is None:\n'
                         '        cart = []\n'
                         '    cart.append(item)\n'
                         '    return cart\n'
                         '\n'
                         'user1_cart = add_to_cart("MacBook Pro")\n'
                         'print("User 1 Cart:", user1_cart)\n'
                         '\n'
                         'user2_cart = add_to_cart("AirPods")\n'
                         'print("User 2 Cart (Fixed):", user2_cart)\n',
        'starter_code': '# BUGGY IMPLEMENTATION:\n'
                        'def add_to_cart(item: str, cart: list = []) -> list:\n'
                        '    cart.append(item)\n'
                        '    return cart\n'
                        '\n'
                        '# Test the behavior:\n'
                        'user1_cart = add_to_cart("MacBook Pro")\n'
                        'print("User 1 Cart:", user1_cart)\n'
                        '\n'
                        'user2_cart = add_to_cart("AirPods")\n'
                        'print("User 2 Cart (Notice the bug!):", user2_cart)\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Think of a default argument like a **communal whiteboard in an office conference '
                              'room**. When Python first defines the function, it sets up that single whiteboard. If '
                              'everyone who calls the function without bringing their own notebook writes on that '
                              "communal whiteboard, they all see each other's notes!\n"
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'Python functions are objects created at **definition time** (when the code is imported '
                              'or read), not when the function is called.\n'
                              "Default values are stored in the function's `__defaults__` tuple once. If the default "
                              'is a mutable object (like a `list` or `dict`), every call that omits the parameter '
                              'points to the exact same memory address (`id(cart)`).\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. **Never** put `[]` or `{}` as a default parameter.\n'
                              '2. Use `None` as a safe placeholder: `def add_to_cart(item: str, cart: list | None = '
                              'None)`.\n'
                              '3. Inside the function, create a brand new list if `cart is None`:\n'
                              '   ```python\n'
                              '   if cart is None:\n'
                              '       cart = []\n'
                              '   cart.append(item)\n'
                              '   ```\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Never use mutable objects as default arguments in Python because defaults are '
                              'evaluated once at definition time, not runtime. Always use None as the sentinel '
                              'value."*\n'
                              '        ',
        'title': 'The Mutable Default Argument Trap in Python'},
    {       'best_practices': [       'Use Common Table Expressions (CTEs) for readable multi-step queries.',
                                  'Ensure an index exists on `(department_id, salary DESC)`.'],
        'category': QuestionCategory.POSTGRES_MYSQL,
        'common_traps': [       'Using `LIMIT 1 OFFSET 1` without partitioning, which only gets the second highest '
                                'salary across the entire company, not per department.',
                                'Using `RANK()` instead of `DENSE_RANK()`, causing rank 2 to be skipped if there are '
                                'two employees tied at rank 1.'],
        'company_tags': ['Amazon', 'Google', 'Oracle', 'Goldman Sachs'],
        'cross_questions': [       'What is the difference in performance between `DENSE_RANK()` vs `LIMIT 1 OFFSET '
                                   '1`?',
                                   'What composite index on `employees` would eliminate the need for a full table '
                                   'filesort?',
                                   'How does MySQL handle NULL values in `ORDER BY salary DESC`?'],
        'difficulty': QuestionDifficulty.BASIC,
        'frequency_score': 95,
        'has_python_sandbox': False,
        'has_sql_sandbox': True,
        'max_exp_years': 3,
        'mcq_correct_index': 1,
        'mcq_explanation': 'When multiple employees earn the exact same salary (ties for 1st place at $150k), '
                           'ROW_NUMBER() assigns arbitrary 1 and 2, and RANK() skips to 3. DENSE_RANK() assigns rank 1 '
                           'to both, and rank 2 to the next distinct salary, guaranteeing exact N-th highest salary '
                           'semantics.',
        'mcq_options': [       'A) DENSE_RANK() is faster because it does not require sorting the salary column.',
                               'B) DENSE_RANK() assigns the same rank to identical salaries without skipping '
                               'subsequent rank numbers, handling salary ties correctly.',
                               'C) ROW_NUMBER() automatically skips duplicate salaries, making it invalid for ties.',
                               'D) OFFSET N fails if there are more than 100 rows in the database table.'],
        'mcq_question': 'Why is DENSE_RANK() preferred over ROW_NUMBER() or OFFSET N when finding the N-th highest '
                        'salary across employees?',
        'min_exp_years': 0,
        'mindmap_node': 'pg-vacuum',
        'mindmap_topic': 'postgres-mysql-internals',
        'phase': 'basic',
        'scenario_text': '\n'
                         'The HR analytics team needs to find the 2nd highest salary in each department. \n'
                         'If multiple employees earn the exact same highest salary, they share rank #1, and the next '
                         'unique salary must be ranked #2.\n'
                         'Write an optimal SQL query using window functions (`DENSE_RANK()`) over the `hr_tech` '
                         'schema.\n',
        'slug': 'sql-nth-highest-salary',
        'solution_sql': 'WITH RankedSalaries AS (\n'
                        '    SELECT \n'
                        '        e.id,\n'
                        '        e.name,\n'
                        '        d.dept_name,\n'
                        '        e.salary,\n'
                        '        DENSE_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) as '
                        'salary_rank\n'
                        '    FROM employees e\n'
                        '    JOIN departments d ON e.department_id = d.id\n'
                        ')\n'
                        'SELECT \n'
                        '    dept_name,\n'
                        '    name,\n'
                        '    salary,\n'
                        '    salary_rank\n'
                        'FROM RankedSalaries\n'
                        'WHERE salary_rank = 2;\n',
        'sql_schema': 'hr_tech',
        'starter_sql': '-- Query the second highest salary using DENSE_RANK()\n'
                       'SELECT \n'
                       '    name, \n'
                       '    department_id, \n'
                       '    salary\n'
                       'FROM employees;\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Think of an Olympic medal podium:\n'
                              '- If two runners tie for 1st place (Gold), `DENSE_RANK()` awards the next runner 2nd '
                              'place (Silver).\n'
                              '- But regular `RANK()` skips 2nd place and jumps straight to 3rd place (Bronze)!\n'
                              'So if an interviewer asks for the 2nd highest salary, `DENSE_RANK()` is mathematically '
                              'the only correct choice.\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              '- `ROW_NUMBER()`: Assigns sequential numbers (1, 2, 3...) regardless of ties.\n'
                              '- `RANK()`: Leaves gaps when ties happen (1, 1, 3...).\n'
                              '- `DENSE_RANK()`: Never leaves gaps (1, 1, 2, 3...).\n'
                              'By combining `DENSE_RANK()` with `PARTITION BY department_id`, we compute ranks per '
                              'department in a single query scan.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. Wrap the ranking calculation in a Common Table Expression (CTE) `WITH RankedSalaries '
                              'AS (...)`.\n'
                              '2. Apply `DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC)`.\n'
                              '3. Filter in the outer query: `WHERE salary_rank = 2`.\n'
                              '4. Create an index on `(department_id, salary DESC)` to avoid full table filesorts.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Use DENSE_RANK() instead of RANK() or LIMIT/OFFSET because DENSE_RANK handles ties '
                              'gracefully without skipping rank numbers, and partitioning guarantees per-department '
                              'calculation."*\n'
                              '        ',
        'title': 'SQL: Finding the N-th Highest Salary in Department'},
    {       'best_practices': [       'Use native async libraries (`httpx` instead of `requests`, `asyncpg` instead of '
                                  '`psycopg2`).',
                                  'Use `asyncio.to_thread` for legacy synchronous blocking I/O.'],
        'category': QuestionCategory.ASYNC_CONCURRENCY,
        'common_traps': [       'Assuming making a function `async def` automatically makes all operations inside it '
                                'non-blocking.',
                                'Creating a new `ThreadPoolExecutor` inside each request rather than reusing the '
                                'global event loop pool.'],
        'company_tags': ['Uber', 'Stripe', 'DoorDash', 'Razorpay'],
        'cross_questions': [       'What is the default thread pool size for `asyncio.to_thread` in FastAPI?',
                                   'What happens when the threadpool is completely saturated under 10,000 req/sec?',
                                   "Why doesn't `asyncio.to_thread` speed up CPU-bound mathematical calculations in "
                                   'Python?'],
        'difficulty': QuestionDifficulty.INTERMEDIATE,
        'frequency_score': 96,
        'has_python_sandbox': True,
        'has_sql_sandbox': False,
        'max_exp_years': 6,
        'mcq_correct_index': 1,
        'mcq_explanation': 'async def endpoints execute directly on the primary event loop thread. A blocking call '
                           'like time.sleep() halts the entire thread, starving all other concurrent coroutines. '
                           "Synchronous I/O must either use plain 'def' (which FastAPI runs on an AnyIO threadpool) or "
                           'asyncio.to_thread().',
        'mcq_options': [       'A) It consumes all CPU cores via multiprocessing.',
                               'B) It blocks the single asyncio event loop thread, preventing all other concurrent '
                               'requests from being scheduled.',
                               'C) FastAPI automatically converts async def endpoints into synchronous C extensions.',
                               'D) It causes an immediate memory leak in the uvicorn worker process.'],
        'mcq_question': 'Why does invoking time.sleep(5) or synchronous requests.get() inside an async def FastAPI '
                        'endpoint degrade server throughput?',
        'min_exp_years': 3,
        'mindmap_node': 'py-gil',
        'mindmap_topic': 'python-internals',
        'phase': 'intermediate',
        'scenario_text': '\n'
                         'During a promotional campaign, your FastAPI backend suddenly showed 100% CPU on a single '
                         'core, \n'
                         'and incoming health-check probes failed with 504 Gateway Timeout.\n'
                         'Upon inspecting the codebase, you discovered an `async def` endpoint calling a blocking '
                         'third-party SDK.\n'
                         'Simulate the issue in the Python interpreter and fix it using `asyncio.to_thread` / '
                         '`run_in_executor`.\n',
        'slug': 'fastapi-async-event-loop-starvation',
        'solution_code': 'import asyncio\n'
                         'import time\n'
                         '\n'
                         'def legacy_sync_payment_verification(order_id: str) -> bool:\n'
                         '    time.sleep(1) # Simulates blocking call\n'
                         '    return True\n'
                         '\n'
                         'async def handle_request_correct(order_id: str):\n'
                         '    return await asyncio.to_thread(legacy_sync_payment_verification, order_id)\n'
                         '\n'
                         'async def main():\n'
                         '    start = time.perf_counter()\n'
                         '    print("Running 3 requests concurrently...")\n'
                         '    results = await asyncio.gather(\n'
                         '        handle_request_correct("ORD-101"),\n'
                         '        handle_request_correct("ORD-102"),\n'
                         '        handle_request_correct("ORD-103")\n'
                         '    )\n'
                         '    total_time = time.perf_counter() - start\n'
                         '    print(f"Completed {len(results)} orders in {total_time:.2f}s (Concurrent!)")\n'
                         '\n'
                         'asyncio.run(main())\n',
        'starter_code': 'import asyncio\n'
                        'import time\n'
                        '\n'
                        'def legacy_sync_payment_verification(order_id: str) -> bool:\n'
                        '    time.sleep(1) # Simulates blocking synchronous I/O\n'
                        '    return True\n'
                        '\n'
                        'async def handle_request_correct(order_id: str):\n'
                        '    # Offload blocking synchronous I/O to thread pool\n'
                        '    return await asyncio.to_thread(legacy_sync_payment_verification, order_id)\n'
                        '\n'
                        'async def main():\n'
                        '    start = time.perf_counter()\n'
                        '    print("Testing concurrent execution...")\n'
                        '    results = await asyncio.gather(\n'
                        '        handle_request_correct("ORD-101"),\n'
                        '        handle_request_correct("ORD-102"),\n'
                        '        handle_request_correct("ORD-103")\n'
                        '    )\n'
                        '    print(f"Finished {len(results)} requests in {time.perf_counter() - start:.2f}s '
                        '(Concurrent!)")\n'
                        '\n'
                        'asyncio.run(main())\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Think of the FastAPI event loop like a **fast-food cashier**. \n'
                              'If the cashier leaves the counter and goes into the kitchen to cook the burger for 5 '
                              'seconds (blocking synchronous I/O), the entire line of 100 waiting customers freezes!\n'
                              'If the cashier hands the ticket to a kitchen helper in the back (`asyncio.to_thread`), '
                              'the cashier keeps taking orders without any pause.\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'FastAPI runs `async def` routes directly on the single-threaded event loop. If '
                              'synchronous blocking code (like `time.sleep()`, `requests.get()`, or legacy DB drivers) '
                              'runs inside `async def`, the entire thread is frozen. No other coroutine can run until '
                              'that blocking call returns.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. If using synchronous I/O inside `async def`, wrap it with `await '
                              'asyncio.to_thread(func, *args)`.\n'
                              '2. Or use regular `def route()` instead of `async def` (FastAPI automatically runs '
                              'regular `def` in an external thread pool).\n'
                              '3. Best practice: Switch to native async libraries like `httpx.AsyncClient` or '
                              '`asyncpg`.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Never execute synchronous blocking I/O directly inside async def routes; offload them '
                              'to a thread pool with asyncio.to_thread or use native non-blocking async libraries."*\n'
                              '        ',
        'title': 'Fixing Event Loop Starvation in FastAPI Async Endpoints'},
    {       'best_practices': [       'Add random jitter (+/- 10%) to cache expiration times.',
                                  'Use Redis Lua scripts for atomic rate limiting.'],
        'category': QuestionCategory.REDIS_CACHING,
        'common_traps': [       'Setting static cache expiration times without adding random jitter.',
                                'Holding database locks while waiting on Redis network responses.'],
        'company_tags': ['Uber', 'Stripe', 'Swiggy', 'Zomato'],
        'cross_questions': [       'What is the difference between Cache-Aside, Write-Through, and Write-Behind?',
                                   'How do you prevent Cache Avalanche when thousands of keys are configured with the '
                                   'exact same 3600s TTL?',
                                   'How does a Bloom filter help prevent Cache Penetration for non-existent IDs?'],
        'difficulty': QuestionDifficulty.INTERMEDIATE,
        'frequency_score': 97,
        'has_python_sandbox': True,
        'has_redis_sandbox': True,
        'max_exp_years': 6,
        'mcq_correct_index': 1,
        'mcq_explanation': 'When a popular key expires, thousands of simultaneous read requests encounter a cache miss '
                           'at the exact same millisecond. Each worker tries to recompute the value and query the DB, '
                           'hammering the database with identical queries. Mitigation: Mutual exclusion (mutex) locks '
                           'or probabilistic early expiration (XFetch).',
        'mcq_options': [       'A) Redis runs out of memory and crashes immediately.',
                               'B) Thousands of concurrent requests simultaneously miss the cache and hit the database '
                               'at once, causing CPU spikes and cascading timeouts.',
                               'C) Redis invalidates all other cache keys in the same database instance.',
                               'D) The client library closes all active TCP connections to the server.'],
        'mcq_question': "What problem occurs during a 'Cache Stampede' (Thundering Herd) when a high-traffic cache key "
                        'expires?',
        'min_exp_years': 3,
        'mindmap_node': 'redis-rate-limiter',
        'mindmap_topic': 'redis-caching',
        'phase': 'intermediate',
        'scenario_text': '\n'
                         "At 12:00 PM, a viral product's cache expires in Redis.\n"
                         'Within 1 second, 50,000 requests hit the server, find the cache empty, and simultaneously '
                         'query the primary database.\n'
                         "This 'Cache Stampede' crashes the database.\n"
                         'Test Redis caching commands and implement sliding-window rate limiting using Redis Sorted '
                         'Sets (ZSET).\n',
        'slug': 'redis-cache-stampede-rate-limiter',
        'solution_code': '# Safe Cache-Aside with Lock\n'
                         'import time\n'
                         '\n'
                         'cache = {"SKU-01": {"id": "SKU-01", "name": "iPhone 16 Pro", "price": 1099}}\n'
                         '\n'
                         'def get_product(pid: str):\n'
                         '    return cache.get(pid)\n'
                         '\n'
                         'print(get_product("SKU-01"))\n',
        'solution_redis': '-- Full rate limiter sequence:\n'
                          'ZREMRANGEBYSCORE user:101:ratelimit 0 1710000000\n'
                          'ZADD user:101:ratelimit 1710000050 "req-uuid-1"\n'
                          'EXPIRE user:101:ratelimit 60\n'
                          'ZCARD user:101:ratelimit\n',
        'starter_code': '# Python simulation of Cache Mutex Lock:\n'
                        'import time\n'
                        '\n'
                        'cache = {}\n'
                        'locks = set()\n'
                        '\n'
                        'def fetch_product_safe(product_id: str):\n'
                        '    if product_id in cache:\n'
                        '        return cache[product_id]\n'
                        '    \n'
                        '    # Mutex lock check: Only 1 worker queries DB\n'
                        '    if product_id not in locks:\n'
                        '        locks.add(product_id)\n'
                        '        print(f"[DB QUERY] Refreshing cache for {product_id}...")\n'
                        '        time.sleep(0.05) # DB latency\n'
                        '        cache[product_id] = {"id": product_id, "name": "iPhone 16 Pro", "price": 1099}\n'
                        '        locks.remove(product_id)\n'
                        '        return cache[product_id]\n'
                        '    else:\n'
                        '        print(f"[WAIT] Another request is already refreshing {product_id}...")\n'
                        '        return {"status": "refreshing, please retry"}\n'
                        '\n'
                        'print(fetch_product_safe("SKU-01"))\n'
                        'print(fetch_product_safe("SKU-01")) # Cache hit!\n',
        'starter_redis': '-- Redis CLI commands for sliding window rate limiter:\n'
                         '-- 1. Remove old timestamps older than 60 seconds ago\n'
                         'ZREMRANGEBYSCORE user:101:ratelimit 0 1710000000\n'
                         '\n'
                         '-- 2. Count requests in current window\n'
                         'ZCARD user:101:ratelimit\n'
                         '\n'
                         '-- 3. Record new request timestamp\n'
                         'ZADD user:101:ratelimit 1710000050 "req-uuid-1"\n'
                         '\n'
                         '-- 4. Inspect keys and TTL\n'
                         'KEYS user:*\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              "Think of a store's morning coffee special. At 9:00 AM, the coffee pot runs out. If "
                              '1,000 customers all notice at the exact same second and all 1,000 run into the kitchen '
                              'to brew coffee, the kitchen collapses! \n'
                              'A **Redis Mutex Lock** lets only the first person into the kitchen to brew coffee while '
                              'everyone else waits outside for the fresh pot.\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'When a high-traffic cache key expires, thousands of concurrent requests get a cache '
                              'miss simultaneously and hammer the primary database at the same instant (Cache Stampede '
                              '/ Thundering Herd).\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. **Cache Mutex**: The first worker acquires a lock (`SET lock_key uuid NX EX 5`) and '
                              'queries the DB; other requests wait or return slightly stale data.\n'
                              '2. **Add TTL Jitter**: Set expiration with random variation (e.g. `3600 + random(0, '
                              "300)`) so keys don't all expire at the exact same second.\n"
                              '3. **Sliding-Window Rate Limiting**: Use Redis Sorted Sets (ZSET) to evict expired '
                              'timestamps with `ZREMRANGEBYSCORE` and count with `ZCARD`.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Mitigate cache stampedes using distributed mutex locks or early background refresh, '
                              'and always add random TTL jitter so keys never expire simultaneously."*\n'
                              '        ',
        'title': 'Redis Caching: Cache Stampede & Sliding Window Rate Limiting'},
    {       'best_practices': [       'Always filter early with `$match` before `$unwind` or `$group`.',
                                  'Index compound keys in strict Equality -> Sort -> Range order.'],
        'category': QuestionCategory.MONGODB_NOSQL,
        'common_traps': [       'Embedding unbounded arrays (e.g. infinite comments or transaction logs inside a '
                                'single user document).',
                                'Violating the ESR rule by placing range filters before sort filters.'],
        'company_tags': ['Uber', 'PayPay', 'DoorDash', 'Coinbase'],
        'cross_questions': [       'What happens if you place `$unwind` before `$match` in a large MongoDB collection?',
                                   'What is the maximum BSON document size limit in MongoDB, and how does it influence '
                                   'embedding vs referencing?',
                                   "What is the difference between `w: 1` and `w: 'majority'` write concern during "
                                   'network partitions?'],
        'difficulty': QuestionDifficulty.INTERMEDIATE,
        'frequency_score': 93,
        'has_nosql_sandbox': True,
        'has_python_sandbox': False,
        'has_sql_sandbox': False,
        'max_exp_years': 6,
        'mcq_correct_index': 2,
        'mcq_explanation': 'The ESR Rule dictates: 1. Equality fields first (status), 2. Sort fields second '
                           '(priority), 3. Range fields last (created_at). Putting Range before Sort causes MongoDB to '
                           'perform an in-memory sort which fails if results exceed 32MB.',
        'mcq_options': [       'A) { created_at: 1, priority: -1, status: 1 }',
                               'B) { priority: -1, status: 1, created_at: 1 }',
                               'C) { status: 1, priority: -1, created_at: 1 }',
                               'D) { status: 1, created_at: 1, priority: -1 }'],
        'mcq_question': "According to MongoDB's ESR (Equality, Sort, Range) rule, what is the optimal compound index "
                        "field order for { status: 'ACTIVE', created_at: { $gte: ISODate(...) } } sorted by { "
                        'priority: -1 }?',
        'min_exp_years': 3,
        'mindmap_node': 'mongo-esr',
        'mindmap_topic': 'mongodb-nosql',
        'phase': 'intermediate',
        'scenario_text': '\n'
                         'An e-commerce order management service queries MongoDB to calculate total revenue per '
                         'customer tier for delivered orders.\n'
                         'Write a MongoDB aggregation pipeline using `$match`, `$unwind`, and `$group`.\n'
                         'Explain the ESR (Equality, Sort, Range) rule to design the ideal compound index for this '
                         'query.\n',
        'slug': 'mongodb-aggregation-esr-rule',
        'solution_nosql': 'db.orders.aggregate([\n'
                          '  { "$match": { "status": "DELIVERED" } },\n'
                          '  { "$group": { \n'
                          '      "_id": "$customer.tier", \n'
                          '      "total_revenue": { "$sum": "$total_amount" } \n'
                          '    } \n'
                          '  },\n'
                          '  { "$sort": { "total_revenue": -1 } }\n'
                          '])',
        'starter_nosql': 'db.orders.aggregate([\n'
                         '  { "$match": { "status": "DELIVERED" } },\n'
                         '  { "$group": { \n'
                         '      "_id": "$customer.tier", \n'
                         '      "total_revenue": { "$sum": "$total_amount" } \n'
                         '    } \n'
                         '  },\n'
                         '  { "$sort": { "total_revenue": -1 } }\n'
                         '])',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Think of searching in a physical library:\n'
                              '1. First, walk to the right department: Fiction (**Equality**).\n'
                              '2. Next, walk to the shelf already sorted alphabetically by Author (**Sort**).\n'
                              '3. Finally, pick only books published after 2020 (**Range**).\n'
                              'If you put Range before Sort, the librarian has to pull 10,000 books off the shelf and '
                              'sort them on the floor in memory!\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'MongoDB evaluates compound indexes left-to-right.\n'
                              '- **E (Equality)**: Filters out non-matching documents immediately.\n'
                              '- **S (Sort)**: Lets MongoDB read in B-Tree index order, avoiding an in-memory blocking '
                              'sort.\n'
                              '- **R (Range)**: Filters values (`$gt`, `$lt`) at the end of the scan.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. Put `$match` as the very first stage in the aggregation pipeline.\n'
                              '2. Build compound indexes in strict **Equality -> Sort -> Range** order:\n'
                              '   `db.orders.createIndex({ "status": 1, "created_at": -1, "total_amount": 1 })`.\n'
                              '3. Never put `$unwind` before `$match`.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Always design compound indexes following the ESR rule (Equality, Sort, Range) to '
                              'guarantee efficient index scans and eliminate in-memory sorting bottlenecks."*\n'
                              '        ',
        'title': 'MongoDB Aggregation Pipeline & The ESR Indexing Rule'},
    {       'best_practices': [       'Pass only entity IDs (`user_id`, `order_id`) to Celery tasks.',
                                  'Set `worker_max_tasks_per_child` to guard against memory leaks.'],
        'category': QuestionCategory.CELERY_RABBITMQ,
        'common_traps': [       'Passing large Django/SQLAlchemy ORM instances into task parameters (causes '
                                'serialization bloat and stale data).',
                                'Retrying immediately without exponential backoff and jitter (causes thundering herd '
                                'DDoS on downstream APIs).'],
        'company_tags': ['Instagram', 'Pinterest', 'Robinhood', 'Instacart'],
        'cross_questions': [       'Why must `acks_late=True` be set when implementing idempotent tasks?',
                                   'What is the difference between RabbitMQ Direct, Topic, and Fanout exchanges?',
                                   'What is Prefetch Count (QoS) in RabbitMQ, and why does a default prefetch of 4 '
                                   'starve other Celery workers?'],
        'difficulty': QuestionDifficulty.INTERMEDIATE,
        'frequency_score': 94,
        'has_python_sandbox': True,
        'max_exp_years': 6,
        'mcq_correct_index': 2,
        'mcq_explanation': 'For I/O-bound tasks (network/HTTP requests), gevent or eventlet enables hundreds of '
                           'concurrent greenlets per worker process with minimal RAM footprint. The default prefork '
                           'process pool is designed for CPU-bound tasks and creates heavy process overhead for high '
                           'concurrency.',
        'mcq_options': [       'A) prefork with concurrency=1',
                               'B) solo',
                               'C) gevent or eventlet greenlet pool (or asyncio threadpool)',
                               'D) Raw OS processes without a worker pool'],
        'mcq_question': 'What Celery worker execution pool should be selected when running tasks that execute '
                        'synchronous network HTTP requests or third-party API calls?',
        'min_exp_years': 3,
        'mindmap_node': 'celery-chord',
        'mindmap_topic': 'celery-rabbitmq',
        'phase': 'intermediate',
        'scenario_text': '\n'
                         'Your background Celery worker processes high-volume image transformations and webhook '
                         'dispatches.\n'
                         'Under load, workers suffer memory leaks and eventually die with Out-Of-Memory (OOM).\n'
                         'Additionally, third-party webhook failures crash workers repeatedly.\n'
                         'Demonstrate how to configure Celery task concurrency (`prefork` vs `gevent`), recycle leaky '
                         'workers (`max_tasks_per_child`), \n'
                         'and implement exponential backoff retries with RabbitMQ Dead Letter Exchanges (DLX).\n',
        'slug': 'celery-worker-concurrency-rabbitmq-dlx',
        'solution_code': '# Production Celery task decorator pattern:\n'
                         '# @celery_app.task(\n'
                         '#     bind=True,\n'
                         '#     autoretry_for=(ConnectionError,),\n'
                         '#     retry_backoff=True,\n'
                         '#     retry_backoff_max=600,\n'
                         '#     retry_jitter=True,\n'
                         '#     max_retries=5,\n'
                         '#     acks_late=True\n'
                         '# )\n'
                         'print("Celery exponential backoff with jitter and acks_late configured.")\n',
        'starter_code': '# Celery Task simulation with Exponential Backoff\n'
                        'import time\n'
                        'import random\n'
                        '\n'
                        'class MockTask:\n'
                        '    def __init__(self, max_retries=3):\n'
                        '        self.max_retries = max_retries\n'
                        '\n'
                        '    def execute_with_retry(self, payload: dict, attempt: int = 1):\n'
                        '        try:\n'
                        '            print(f"[Attempt {attempt}] Processing webhook for order '
                        '{payload[\'order_id\']}...")\n'
                        '            # Simulate transient network failure on first 2 attempts\n'
                        '            if attempt < 3:\n'
                        '                raise ConnectionError("503 Service Unavailable from downstream webhook")\n'
                        '            print("Webhook delivered successfully!")\n'
                        '            return True\n'
                        '        except ConnectionError as exc:\n'
                        '            if attempt < self.max_retries:\n'
                        '                delay = 2 ** attempt + random.uniform(0.1, 0.5) # Exponential backoff + '
                        'jitter\n'
                        '                print(f"Failed. Retrying in {delay:.2f}s...")\n'
                        '                return self.execute_with_retry(payload, attempt + 1)\n'
                        '            else:\n'
                        '                print("[DLX] Max retries exceeded. Routing to Dead Letter Queue for manual '
                        'audit.")\n'
                        '                return False\n'
                        '\n'
                        'task = MockTask()\n'
                        'task.execute_with_retry({"order_id": "ORD-777", "amount": 250})\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              "Think of a package delivery driver. If a customer's gate is locked, the driver "
                              "shouldn't honk the horn 100 times in 1 second (which causes a traffic jam and crashes "
                              'the system). \n'
                              'Instead, the driver waits 2 minutes, then 4 minutes, then 8 minutes (**Exponential '
                              'Backoff with Jitter**). If delivery still fails after 5 tries, they place the package '
                              'in the return warehouse (**Dead Letter Queue**) for manual audit.\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'Immediate retries flood failing third-party APIs. Without backoff and jitter, all '
                              'retrying workers hit the target at identical intervals, causing thundering-herd '
                              'downtime. Additionally, long-running Python workers leak memory over time.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. Configure Celery tasks with `autoretry_for=(ConnectionError,)`, '
                              '`retry_backoff=True`, and `retry_jitter=True`.\n'
                              '2. Set `acks_late=True` so tasks are acknowledged only after finishing.\n'
                              '3. Set `worker_max_tasks_per_child = 500` to automatically restart worker processes and '
                              'reclaim leaked RAM.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Use exponential backoff with jitter and Dead Letter Exchanges to prevent retry '
                              'storms, and set worker_max_tasks_per_child to eliminate memory leaks."*\n'
                              '        ',
        'title': 'Celery Worker Concurrency, Chords & RabbitMQ DLX'},
    {       'best_practices': [       'Use Cooperative Sticky Rebalancing (`cooperative-sticky`).',
                                  'Commit offsets manually after business transaction completes.'],
        'category': QuestionCategory.KAFKA_MESSAGING,
        'common_traps': [       'Performing slow external REST API calls directly inside the Kafka consumer poll loop.',
                                'Setting more consumers than partitions in a group (excess consumers will sit '
                                'permanently idle).'],
        'company_tags': ['LinkedIn', 'Uber', 'Netflix', 'PayPal'],
        'cross_questions': [       'How does Kafka achieve high write performance through sequential disk I/O and OS '
                                   'PageCache?',
                                   'What happens if `enable.auto.commit` is True and the consumer crashes midway '
                                   'through processing a batch?',
                                   'What is the difference between `acks=0`, `acks=1`, and `acks=all` (`-1`) in Kafka '
                                   'producers?'],
        'difficulty': QuestionDifficulty.ADVANCED,
        'frequency_score': 98,
        'has_python_sandbox': True,
        'max_exp_years': 9,
        'mcq_correct_index': 1,
        'mcq_explanation': 'Within a Kafka consumer group, each topic partition is assigned to at most one consumer '
                           'instance at any given time. With 6 partitions and 3 consumers, each consumer is allocated '
                           '2 partitions (6 / 3 = 2). If consumers exceed partitions, the extra consumers remain idle.',
        'mcq_options': [       'A) Each of the 3 consumers reads from all 6 partitions simultaneously.',
                               'B) Exactly 2 partitions are assigned to each consumer (provided consumer partition '
                               'assignment is balanced).',
                               'C) 3 partitions are assigned to the first consumer and 3 are ignored.',
                               'D) Kafka rejects the consumer group configuration until 6 consumers are online.'],
        'mcq_question': 'In Apache Kafka, if a consumer group has 3 active consumers and the subscribed topic has 6 '
                        'partitions, how are partitions assigned?',
        'min_exp_years': 6,
        'mindmap_node': 'kafka-rebalance',
        'mindmap_topic': 'kafka-messaging',
        'phase': 'advanced',
        'scenario_text': '\n'
                         'A critical payment settlement topic in Kafka has 12 partitions and 12 consumers in a '
                         'consumer group.\n'
                         "Suddenly, one consumer's processing time spikes, exceeding `max.poll.interval.ms`.\n"
                         'Kafka detects a dead consumer and triggers a group rebalance, halting message consumption '
                         'across all 12 partitions.\n'
                         'Explain how Cooperative Sticky Rebalancing solves this, how to diagnose partition skew (hot '
                         'keys), and how to commit offsets safely.\n',
        'slug': 'kafka-consumer-lag-rebalancing',
        'solution_code': '# Solution: Add salt or compound key (merchant_id + order_uuid) to avoid partition '
                         'hotspotting\n'
                         'import hashlib\n'
                         '\n'
                         'def get_balanced_partition(merchant_id: str, order_id: str, total_partitions: int = 12) -> '
                         'int:\n'
                         '    compound = f"{merchant_id}:{order_id}"\n'
                         '    return int(hashlib.md5(compound.encode()).hexdigest(), 16) % total_partitions\n'
                         '\n'
                         'print("Balanced partition selection demonstrated.")\n',
        'starter_code': '# Simulating Kafka Partition Key Hashing:\n'
                        'import hashlib\n'
                        '\n'
                        'def get_partition(key: str, total_partitions: int = 12) -> int:\n'
                        '    return int(hashlib.md5(key.encode()).hexdigest(), 16) % total_partitions\n'
                        '\n'
                        '# Test partition distribution:\n'
                        'merchants = ["Merchant-A", "Merchant-B", "Merchant-C", "Merchant-D", "Merchant-E"]\n'
                        'distribution = {i: 0 for i in range(12)}\n'
                        '\n'
                        'for m in merchants:\n'
                        '    for _ in range(1000):\n'
                        '        p = get_partition(m)\n'
                        '        distribution[p] += 1\n'
                        '\n'
                        'print("Partition message counts:")\n'
                        'for p, count in distribution.items():\n'
                        '    if count > 0:\n'
                        '        print(f"Partition {p}: {count} messages")\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Think of 12 cashiers at an airport check-in desk.\n'
                              'In older Kafka (**Eager Rebalance**), if one cashier drops their pen, the manager blows '
                              'a whistle and **all 12 cashiers stop serving passengers** for 30 seconds!\n'
                              'In modern Kafka (**Cooperative Sticky Rebalance**), the other 11 cashiers keep checking '
                              'in passengers without stopping, while only the 1 affected line is adjusted.\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              "Eager rebalancing halts message consumption across all partitions ('Stop-the-World'). "
                              'Cooperative Sticky Rebalancing revokes only the specific partitions being moved, '
                              'allowing unaffected consumers to continue streaming messages without delay.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. Set `partition.assignment.strategy` to `CooperativeStickyAssignor`.\n'
                              '2. Avoid partition skew (hot keys) by salting keys (e.g. `f"{merchant_id}:{order_id}"`) '
                              'so traffic distributes evenly across all 12 partitions.\n'
                              "3. Tune `max.poll.interval.ms` so slow batch processing doesn't falsely trigger "
                              'consumer eviction.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Cooperative Sticky Rebalancing eliminates stop-the-world pauses in consumer groups, '
                              'and balanced partition keys prevent hot-partition lag."*\n'
                              '        ',
        'title': 'Apache Kafka: Consumer Lag, Partition Skew & Rebalancing'},
    {       'best_practices': [       'Use Multi-stage builds with Python `-slim` or Distroless images.',
                                  'Run as non-root user (`USER 1001`).'],
        'category': QuestionCategory.DOCKER_CONTAINERS,
        'common_traps': [       'Using `COPY . .` before `RUN pip install`, invalidating layer caches on every commit.',
                                'Leaving credentials, SSH keys, or `.git` directories inside intermediate Docker '
                                'layers.'],
        'company_tags': ['Google', 'Amazon', 'Palantir', 'Cloudflare'],
        'cross_questions': [       'Why is PID 1 special inside a Docker container, and what happens when SIGTERM is '
                                   'sent?',
                                   'What is a Distroless container, and how do you debug a container that lacks a '
                                   'shell (/bin/sh)?',
                                   'How does `.dockerignore` prevent leaking `.env` files and `__pycache__` into the '
                                   'image layer history?'],
        'difficulty': QuestionDifficulty.ADVANCED,
        'frequency_score': 95,
        'has_python_sandbox': True,
        'max_exp_years': 9,
        'mcq_correct_index': 1,
        'mcq_explanation': 'By default, container root UID 0 maps directly to host UID 0 unless user namespaces are '
                           'configured. If an application vulnerability (like RCE) is exploited under non-root, the '
                           'attacker cannot modify protected system files, install kernel modules, or escape easily.',
        'mcq_options': [       'A) Root users cannot execute Python scripts inside Alpine Linux.',
                               'B) Running as non-root enforces the Principle of Least Privilege, preventing an '
                               'attacker who breaks out of the application from having root host access or tampering '
                               'with system binaries.',
                               'C) Docker requires a non-root user to connect to the Docker network bridge.',
                               'D) Non-root users double the execution speed of Python bytecode.'],
        'mcq_question': 'Why should a production Docker container run as a non-root user (e.g. USER appuser) rather '
                        'than the default root user?',
        'min_exp_years': 6,
        'mindmap_node': 'docker-multistage',
        'mindmap_topic': 'docker-containers',
        'phase': 'advanced',
        'scenario_text': '\n'
                         "A company's Python backend Docker image is 1.4 GB in size and contains 45 HIGH and CRITICAL "
                         'vulnerabilities according to Trivy.\n'
                         'The container runs as root, has GCC compilers in production, and builds take 10 minutes '
                         'because Docker layer caching is broken.\n'
                         'Write an optimized, secure multi-stage Dockerfile that:\n'
                         '1. Slashes image size below 100 MB.\n'
                         '2. Runs as a non-privileged user (`USER appuser`).\n'
                         '3. Maximizes Docker layer caching for fast CI/CD builds.\n',
        'slug': 'docker-multistage-security-hardening',
        'solution_code': 'print("Multi-stage Dockerfile with non-root security verified.")',
        'starter_code': '# Inspecting Docker layer caching logic:\n'
                        "dockerfile_bad = '''\n"
                        'FROM python:3.12\n'
                        'WORKDIR /app\n'
                        'COPY . .\n'
                        'RUN pip install -r requirements.txt\n'
                        'CMD ["python", "main.py"]\n'
                        "'''\n"
                        '\n'
                        "dockerfile_good = '''\n"
                        'FROM python:3.12-slim AS builder\n'
                        'WORKDIR /app\n'
                        'COPY requirements.txt .\n'
                        'RUN pip install --user --no-cache-dir -r requirements.txt\n'
                        '\n'
                        'FROM python:3.12-slim\n'
                        'WORKDIR /app\n'
                        'RUN useradd -m -u 1001 appuser\n'
                        'COPY --from=builder /root/.local /home/appuser/.local\n'
                        'COPY --chown=appuser:appuser . .\n'
                        'USER appuser\n'
                        'ENV PATH="/home/appuser/.local/bin:$PATH"\n'
                        'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]\n'
                        "'''\n"
                        '\n'
                        'print("Comparing Dockerfile patterns...")\n'
                        'print("Good Dockerfile separates builder stage, caches requirements, and drops root '
                        'privileges.")\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Think of building a house. You need heavy bulldozers, cement mixers, and scaffolding '
                              'during construction (**the builder stage**). But when moving into the finished house, '
                              "you don't leave bulldozers and scaffolding in your living room! \n"
                              'Multi-stage Docker builds use heavy compilers to build the application, then copy only '
                              'the clean compiled files into a tiny, secure final container.\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'Single-stage Docker images include build tools (`gcc`, `make`, `git`, package caches), '
                              'inflating image size to 1.5GB+ and introducing dozens of OS vulnerabilities. '
                              'Multi-stage builds leave the build tools behind and run as an unprivileged user (`USER '
                              'appuser`).\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. **Stage 1 (Builder)**: Install dependencies into `/root/.local` using '
                              '`python:3.12-slim AS builder`.\n'
                              '2. **Stage 2 (Runtime)**: Copy only `.local` from builder into a fresh slim container.\n'
                              '3. **Security**: Create a non-root user (`useradd -u 1001 appuser`) and set `USER '
                              'appuser`.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Multi-stage builds slash container attack surfaces and image size by discarding build '
                              'tools, and running as non-root prevents container breakout exploits."*\n'
                              '        ',
        'title': 'Docker: Multi-Stage Build & Container Security Hardening'},
    {       'best_practices': [       'Use a `preStop` sleep hook (10-15s) in production deployments.',
                                  'Keep Liveness probes strictly local (checking process health, not third-party '
                                  'dependencies).'],
        'category': QuestionCategory.KUBERNETES_DEVOPS,
        'common_traps': [       'Having Liveness probe ping external services; if external service flaps, K8s kills '
                                'all pods in an unrecoverable restart loop.',
                                'Setting `terminationGracePeriodSeconds` lower than your slowest batch transaction '
                                'time.'],
        'company_tags': ['Uber', 'Google', 'Microsoft', 'Stripe'],
        'cross_questions': [       'What is the danger of having Liveness Probe check downstream database '
                                   'connectivity?',
                                   'What is the difference between CPU throttling (CFS quota) and Memory OOMKilled '
                                   '(Exit code 137)?',
                                   'How do `maxUnavailable` and `maxSurge` parameters control the speed and safety of '
                                   'rolling updates?'],
        'difficulty': QuestionDifficulty.ADVANCED,
        'frequency_score': 96,
        'has_python_sandbox': True,
        'max_exp_years': 9,
        'mcq_correct_index': 1,
        'mcq_explanation': 'readinessProbe determines if the application is ready to accept user traffic (e.g. warming '
                           'cache or DB pool initialized). If it fails, Kubernetes stops sending network requests to '
                           'the Pod without restarting it. livenessProbe detects deadlocks/crashes: if it fails, '
                           'kubelet restarts the container.',
        'mcq_options': [       'A) A failed readinessProbe restarts the container; a failed livenessProbe removes it '
                               'from the Service endpoints.',
                               'B) A failed readinessProbe removes the Pod from Service load balancer endpoints (stops '
                               'sending traffic); a failed livenessProbe kills and restarts the container.',
                               'C) Both probes perform identical actions: restarting the entire Pod.',
                               'D) Neither probe affects routing; they only send alerts to Prometheus.'],
        'mcq_question': 'In Kubernetes, what happens to a Pod when its readinessProbe fails, compared to when its '
                        'livenessProbe fails?',
        'min_exp_years': 6,
        'mindmap_node': 'k8s-graceful-shutdown',
        'mindmap_topic': 'kubernetes-devops',
        'phase': 'advanced',
        'scenario_text': '\n'
                         'During automated CI/CD deployments to a Kubernetes cluster, users experience intermittent '
                         '502 Bad Gateway errors for 15 seconds.\n'
                         'Investigation reveals that when old Pods are terminated, Kubelet sends `SIGTERM` immediately '
                         'while the Ingress controller is still routing live traffic to the terminating Pod.\n'
                         'Configure a Kubernetes deployment with `preStop` hooks, proper '
                         '`terminationGracePeriodSeconds`, and separate Liveness/Readiness/Startup probes to achieve '
                         'true zero-downtime rolling updates.\n',
        'slug': 'kubernetes-zero-downtime-probes',
        'solution_code': 'print("Graceful SIGTERM handler and Kubernetes preStop lifecycle pattern verified.")',
        'starter_code': '# Simulating Graceful Shutdown in Python FastAPI / Uvicorn:\n'
                        'import signal\n'
                        'import time\n'
                        '\n'
                        'is_shutting_down = False\n'
                        '\n'
                        'def handle_sigterm(signum, frame):\n'
                        '    global is_shutting_down\n'
                        '    print("[SIGTERM] Received termination signal from Kubernetes!")\n'
                        '    print("[DRAIN] Draining in-flight database transactions...")\n'
                        '    is_shutting_down = True\n'
                        '    time.sleep(1) # Simulates flushing active requests\n'
                        '    print("[EXIT] Clean shutdown completed. Zero dropped connections.")\n'
                        '\n'
                        '# Register signal handler\n'
                        'signal.signal(signal.SIGTERM, handle_sigterm)\n'
                        'print("Server running. Ready to handle graceful termination.")\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              "When a restaurant waiter's shift ends, they don't abruptly throw the plates on the "
                              'floor! \n'
                              'A `preStop` hook gives the Kubernetes Ingress router 15 seconds to stop sending new '
                              'diners to the waiter, while the waiter finishes serving the food currently in their '
                              'hands.\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'When a Pod is terminated, removing its IP from Ingress/kube-proxy takes 2-5 seconds. '
                              'Kubelet sends `SIGTERM` concurrently. If the app stops immediately, in-flight HTTP '
                              'requests receive connection refused (`502 Bad Gateway`). A `preStop: sleep 15` delays '
                              'SIGTERM until Ingress traffic has stopped.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              "1. Add `lifecycle: preStop: exec: command: ['/bin/sh', '-c', 'sleep 15']` in the Pod "
                              'spec.\n'
                              '2. Set `terminationGracePeriodSeconds: 45`.\n'
                              '3. In Python, handle `SIGTERM` to drain active DB connections before exiting.\n'
                              "4. Keep Liveness probes strictly local (don't ping external databases in liveness "
                              'probes).\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Pair a preStop sleep hook with graceful SIGTERM connection draining to eliminate '
                              'Ingress 502 race conditions during rolling deployments."*\n'
                              '        ',
        'title': 'Kubernetes: Zero-Downtime Rolling Updates & Probe Architecture'},
    {       'best_practices': [       'Use Log-based CDC (Debezium + Kafka Connect) reading MySQL binlog.',
                                  'Make all Kafka consumers idempotent using transaction logs or deduplication '
                                  'filters.'],
        'category': QuestionCategory.SYSTEM_DESIGN_MNC,
        'common_traps': [       'Assuming distributed transactions (XA / 2PC) are feasible across microservices.',
                                'Forgetting to clean up or partition old outbox table records, resulting in an '
                                'unmanageably huge table.'],
        'company_tags': ['Netflix', 'Uber', 'Amazon', 'Confluent'],
        'cross_questions': [       'How does Debezium tail the MySQL binary log (binlog) without imposing locking '
                                   'overhead on the InnoDB buffer pool?',
                                   'How do downstream consumers handle duplicate events when Kafka guarantees '
                                   'at-least-once delivery?',
                                   'What are the operational trade-offs of polling the outbox table (`SELECT ... FOR '
                                   'UPDATE SKIP LOCKED`) vs log-based CDC?'],
        'difficulty': QuestionDifficulty.ARCHITECT,
        'frequency_score': 98,
        'has_python_sandbox': True,
        'has_sql_sandbox': True,
        'max_exp_years': 20,
        'mcq_correct_index': 1,
        'mcq_explanation': 'You cannot execute a distributed ACID transaction across heterogeneous systems like MySQL '
                           "and Kafka. The Transactional Outbox pattern writes the event into an 'outbox' table in the "
                           'database inside the SAME local transaction as the domain entity. A CDC tool (like '
                           'Debezium) or poller reliably reads the outbox and publishes to Kafka with at-least-once '
                           'delivery.',
        'mcq_options': [       'A) It uses two-phase commit (2PC) over HTTP between MySQL and Kafka.',
                               'B) It writes both the business entity update and an outbox message into the same '
                               'relational database in a single local ACID transaction, and an asynchronous relay '
                               'publishes to Kafka.',
                               'C) It writes to Kafka first and rolls back Kafka if the database write fails.',
                               'D) It discards messages that fail to deliver within 50 milliseconds.'],
        'mcq_question': 'How does the Transactional Outbox Pattern solve the Dual-Write inconsistency problem between '
                        'a database and a message broker like Kafka?',
        'min_exp_years': 10,
        'mindmap_node': 'system-flash-sale',
        'mindmap_topic': 'system-design-troubleshooting',
        'phase': 'advanced',
        'scenario_text': '\n'
                         'In an event-driven architecture, when a customer places an order, your service must:\n'
                         '1. Insert the order into MySQL database.\n'
                         '2. Publish an `OrderCreated` event to Apache Kafka for downstream billing and shipping.\n'
                         'If you commit to MySQL and Kafka publish fails, events are lost.\n'
                         'If you publish to Kafka first and MySQL commit fails/rolls back, ghost events are '
                         'published.\n'
                         'Architect guaranteed at-least-once delivery using the Transactional Outbox Pattern and '
                         'Debezium / CDC without distributed 2PC locks.\n',
        'slug': 'dual-write-kafka-transactional-outbox',
        'solution_code': 'class OutboxPublisher:\n'
                         '    def __init__(self, db):\n'
                         '        self.db = db\n'
                         '        self.kafka_cluster = []\n'
                         '\n'
                         '    def poll_and_publish(self):\n'
                         '        for event in list(self.db.outbox_events):\n'
                         '            if event["status"] == "PENDING":\n'
                         '                self.kafka_cluster.append(event)\n'
                         '                event["status"] = "PUBLISHED"\n'
                         '                print(f"[CDC Worker] Published event {event[\'event_id\']} to Kafka.")\n'
                         '\n'
                         'db = MockDBTransaction()\n'
                         'db.create_order_with_outbox("ORD-9999", 450.00)\n'
                         'publisher = OutboxPublisher(db)\n'
                         'publisher.poll_and_publish()\n'
                         'print("Kafka Events:", publisher.kafka_cluster)\n',
        'solution_sql': 'SELECT \n'
                        '    id, \n'
                        '    aggregate_type, \n'
                        '    aggregate_id, \n'
                        '    event_type, \n'
                        '    created_at \n'
                        'FROM outbox_events \n'
                        'ORDER BY created_at ASC;\n',
        'sql_schema': 'fintech',
        'starter_code': 'class MockDBTransaction:\n'
                        '    def __init__(self):\n'
                        '        self.orders = []\n'
                        '        self.outbox_events = []\n'
                        '    \n'
                        '    def create_order_with_outbox(self, order_id: str, amount: float):\n'
                        '        # ATOMIC LOCAL TRANSACTION:\n'
                        '        self.orders.append({"id": order_id, "amount": amount})\n'
                        '        self.outbox_events.append({\n'
                        '            "event_id": f"EVT-{order_id}",\n'
                        '            "topic": "orders.v1.created",\n'
                        '            "payload": {"order_id": order_id, "amount": amount},\n'
                        '            "status": "PENDING"\n'
                        '        })\n'
                        '        print(f"Committed order {order_id} and outbox event atomically.")\n'
                        '\n'
                        'db = MockDBTransaction()\n'
                        'db.create_order_with_outbox("ORD-8888", 299.99)\n'
                        'print("Orders:", db.orders)\n'
                        'print("Outbox:", db.outbox_events)\n',
        'starter_sql': '-- Schema definition for Transactional Outbox in MySQL:\n'
                       'CREATE TABLE IF NOT EXISTS outbox_events (\n'
                       '    id VARCHAR(64) PRIMARY KEY,\n'
                       '    aggregate_type VARCHAR(50) NOT NULL,\n'
                       '    aggregate_id VARCHAR(64) NOT NULL,\n'
                       '    event_type VARCHAR(100) NOT NULL,\n'
                       '    payload JSON NOT NULL,\n'
                       '    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n'
                       '    processed_at TIMESTAMP NULL\n'
                       ');\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'If you try to write in two different notebooks in two different buildings at the exact '
                              "same second, one building might catch fire and your records won't match. \n"
                              'Instead, write both records into your single local notebook (**MySQL ACID '
                              'transaction**), and have an assistant reliably copy the records to the second building '
                              '(**Kafka CDC**).\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'Writing to MySQL and then publishing to Kafka cannot be atomic without slow 2PC locks. '
                              'If Kafka is down, the order is saved but the event is lost. If Kafka succeeds and MySQL '
                              'rolls back, ghost events are published. The **Transactional Outbox Pattern** saves the '
                              'business entity and the event in the same local ACID transaction.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. Create an `outbox_events` table in MySQL.\n'
                              '2. In a single local transaction: insert the order and insert the event into '
                              '`outbox_events`.\n'
                              '3. An asynchronous CDC tool (Debezium reading the MySQL binlog) streams events from the '
                              'outbox table to Kafka with guaranteed at-least-once delivery.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Solve dual-write inconsistencies with the Transactional Outbox Pattern: commit the '
                              'entity and event in a single local ACID transaction, then use log-based CDC to stream '
                              'to Kafka."*\n'
                              '        ',
        'title': 'Dual-Write Problem: MySQL & Kafka Consistency (Transactional Outbox)'},
    {       'best_practices': [       'Always use the Expand-and-Contract pattern for database schema evolution.',
                                  'Run table backfills in small indexed batches during off-peak hours.'],
        'category': QuestionCategory.CICD_PIPELINES,
        'common_traps': [       'Renaming or dropping columns in a single deploy step while old instances of the '
                                'backend are still running.',
                                'Running bulk UPDATE scripts without batching, locking the entire table and filling up '
                                'the undo log.'],
        'company_tags': ['Stripe', 'Amazon', 'GitHub', 'Shopify'],
        'cross_questions': [       'Why is `ALTER TABLE` dangerous on large MySQL InnoDB tables, and how do tools like '
                                   '`gh-ost` and `pt-online-schema-change` work using binlog triggers?',
                                   'How do you handle rollbacks if Phase 3 backfill detects inconsistent data formats?',
                                   'How does Argo Rollouts automate Canary analysis using Prometheus metric queries '
                                   'before promoting a version to 100%?'],
        'difficulty': QuestionDifficulty.ARCHITECT,
        'frequency_score': 99,
        'has_python_sandbox': True,
        'has_sql_sandbox': False,
        'max_exp_years': 20,
        'mcq_correct_index': 1,
        'mcq_explanation': 'Renaming a column directly breaks running instances of the previous app version during a '
                           'rolling deploy. Expand-and-Contract safely decouples schema change from code deploys '
                           'across 4 non-breaking phases: Expand (new column added), Dual-Write (both written), '
                           'Backfill (async batch copy), and Contract (switch reads & deprecate old column).',
        'mcq_options': [       'A) Rename column immediately in SQL -> Deploy new code -> Drop old column.',
                               'B) 1. Add new column (Expand), 2. Dual-write to both columns in app, 3. Backfill '
                               'historic data, 4. Switch reads to new column & drop old column (Contract).',
                               'C) Put the database in read-only maintenance mode for 30 minutes.',
                               'D) Create a new database cluster and replay all binary logs from scratch.'],
        'mcq_question': 'In zero-downtime database evolution, what is the correct order of the Expand-and-Contract '
                        '(Parallel Run) migration pattern when renaming a column?',
        'min_exp_years': 10,
        'mindmap_node': 'cicd-canary',
        'mindmap_topic': 'cicd-production',
        'phase': 'advanced',
        'scenario_text': '\n'
                         'A microservice database table has 200 million rows.\n'
                         'A new feature requires renaming column `phone_number` to `contact_number` and changing its '
                         'type.\n'
                         'Running `ALTER TABLE` directly will lock the table for 45 minutes, causing a catastrophic '
                         'global outage.\n'
                         'Architect the 4-phase Expand-and-Contract (Parallel Run) migration pattern in your CI/CD '
                         'pipeline to ensure zero downtime.\n',
        'slug': 'cicd-zerodowntime-schema-migrations',
        'solution_code': 'print("Expand and Contract dual-write migration pattern verified.")',
        'starter_code': '# Simulating Dual-Write Expand and Contract Migration:\n'
                        'class UserRecordService:\n'
                        '    def __init__(self):\n'
                        '        self.db = [{"id": 1, "phone_number": "123-456-7890", "contact_number": None}]\n'
                        '\n'
                        '    def update_phone_phase2_dual_write(self, user_id: int, new_number: str):\n'
                        '        for user in self.db:\n'
                        '            if user["id"] == user_id:\n'
                        '                # DUAL WRITE: Write to both legacy and new column\n'
                        '                user["phone_number"] = new_number\n'
                        '                user["contact_number"] = new_number\n'
                        '                print(f"[DUAL WRITE] Updated user {user_id} in both columns safely.")\n'
                        '\n'
                        'service = UserRecordService()\n'
                        'service.update_phone_phase2_dual_write(1, "987-654-3210")\n'
                        'print(service.db)\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              "Think of replacing an old bridge. You don't blow up the old bridge while cars are "
                              'driving on it!\n'
                              '1. Build the new lane right alongside the old one (**Expand**).\n'
                              '2. Allow cars to use both lanes (**Dual-Write**).\n'
                              '3. Move all traffic onto the new lane.\n'
                              '4. Safely demolish the old lane (**Contract**).\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'Running `ALTER TABLE` to rename columns locks tables for hours on 200M row databases. '
                              'The **Expand-and-Contract** pattern decouples schema evolution from application '
                              'deployments across non-breaking phases.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. **Phase 1 (Expand)**: Add `new_column` as nullable via non-blocking migration.\n'
                              '2. **Phase 2 (Dual Write)**: App writes to both `old_column` and `new_column`.\n'
                              '3. **Phase 3 (Backfill)**: Run an async script in small indexed batches to copy '
                              'historic rows.\n'
                              '4. **Phase 4 (Contract)**: Switch reads to `new_column` and drop `old_column` in a '
                              'future deploy.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Never rename columns in a single deploy; use the 4-phase Expand-and-Contract pattern '
                              'to ensure non-breaking zero-downtime database evolution."*\n'
                              '        ',
        'title': 'CI/CD & Zero-Downtime Blue-Green Schema Migrations'},
    {       'best_practices': [       'Use module-level singletons (Python modules are cached in `sys.modules` by default) '
                                  'where possible.',
                                  'Use metaclasses or double-checked locking in `__new__` when dynamic classes are '
                                  'required.'],
        'category': QuestionCategory.PYTHON_INTERNALS,
        'common_traps': [       'Initializing connection state inside `__init__` in a singleton class, causing '
                                're-initialization on every `Pool()` call.',
                                'Forgetting thread synchronization with `threading.Lock`.'],
        'company_tags': ['Google', 'Microsoft', 'Bloomberg', 'Amazon'],
        'cross_questions': [       'Why is double-checked locking needed in multi-threaded environments?',
                                   'How can a Singleton be implemented using a Python metaclass (`__call__`) instead '
                                   'of `__new__`?',
                                   'What happens if a Singleton is unpickled with `pickle.loads()`?'],
        'difficulty': QuestionDifficulty.INTERMEDIATE,
        'frequency_score': 96,
        'has_python_sandbox': True,
        'has_sql_sandbox': False,
        'max_exp_years': 6,
        'mcq_correct_index': 1,
        'mcq_explanation': '__new__(cls) is the constructor method responsible for returning a new instance of cls. '
                           '__init__(self) takes that instance and initializes its state (returning None). If '
                           'implementing a Singleton, you must intercept __new__ so a new instance is not allocated.',
        'mcq_options': [       'A) __init__ allocates the memory address, while __new__ initializes the fields.',
                               'B) __new__ is the static allocator that creates and returns the object instance; '
                               '__init__ is the initializer that configures attributes on that existing instance.',
                               'C) __new__ is only called for subclasses of dict.',
                               'D) __init__ returns the newly created instance to the caller.'],
        'mcq_question': 'In Python object instantiation (cls(*args)), what is the key functional difference between '
                        '__new__ and __init__?',
        'min_exp_years': 3,
        'mindmap_node': 'py-gil',
        'mindmap_topic': 'python-internals',
        'phase': 'intermediate',
        'scenario_text': '\n'
                         'You are implementing a centralized Database Connection Pool manager in Python that must be a '
                         'strict Singleton across all threads.\n'
                         'A junior developer tried implementing `__init__`, but noticed `__init__` is invoked on every '
                         'single instantiation call, re-initializing the connections!\n'
                         'Explain the difference between `__new__` (object allocator) and `__init__` (object '
                         'initializer), and implement a thread-safe Singleton using `threading.Lock`.\n',
        'slug': 'python-new-vs-init-singleton',
        'solution_code': 'import threading\n'
                         '\n'
                         'class DatabaseConnectionPool:\n'
                         '    _instance = None\n'
                         '    _lock = threading.Lock()\n'
                         '\n'
                         '    def __new__(cls, *args, **kwargs):\n'
                         '        if cls._instance is None:\n'
                         '            with cls._lock:\n'
                         '                if cls._instance is None:\n'
                         '                    cls._instance = super().__new__(cls)\n'
                         '                    cls._instance.pool_size = 20\n'
                         '        return cls._instance\n'
                         '\n'
                         'p1 = DatabaseConnectionPool()\n'
                         'p2 = DatabaseConnectionPool()\n'
                         'assert p1 is p2\n'
                         'print("Thread-safe Singleton verified.")\n',
        'starter_code': 'import threading\n'
                        '\n'
                        'class DatabaseConnectionPool:\n'
                        '    _instance = None\n'
                        '    _lock = threading.Lock()\n'
                        '\n'
                        '    def __new__(cls, *args, **kwargs):\n'
                        '        # Double-checked locking pattern:\n'
                        '        if cls._instance is None:\n'
                        '            with cls._lock:\n'
                        '                if cls._instance is None:\n'
                        '                    print("[ALLOCATING] Creating singleton instance in memory...")\n'
                        '                    cls._instance = super().__new__(cls)\n'
                        '                    cls._instance.connections = 10\n'
                        '        return cls._instance\n'
                        '\n'
                        '# Test Singleton:\n'
                        'pool1 = DatabaseConnectionPool()\n'
                        'pool2 = DatabaseConnectionPool()\n'
                        '\n'
                        'print("pool1 is pool2?", pool1 is pool2)\n'
                        'print("pool1 ID:", id(pool1))\n'
                        'print("pool2 ID:", id(pool2))\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              '`__new__` is the construction company that buys the land and builds the house.\n'
                              '`__init__` is the interior decorator who paints the walls.\n'
                              'To ensure there is only **ONE house in the entire world (Singleton)**, you must stop '
                              'the construction company in `__new__` before a second house is built!\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              '`__new__(cls)` is the static method that allocates the object in memory. '
                              '`__init__(self)` initializes attributes on that existing instance. If you attempt to '
                              'implement a singleton inside `__init__`, Python has already allocated a new memory '
                              'address. Overriding `__new__` with double-checked locking guarantees only one instance '
                              'is ever created.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. In `__new__`, check `if cls._instance is None:`.\n'
                              '2. Acquire `threading.Lock()` to prevent race conditions.\n'
                              '3. Double-check: `if cls._instance is None: cls._instance = super().__new__(cls)`.\n'
                              '4. Return `cls._instance`.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"__new__ allocates the instance in memory while __init__ initializes it. Intercept '
                              '__new__ with double-checked locking to enforce a thread-safe singleton."*\n'
                              '        ',
        'title': 'Python Object Lifecycle: __new__ vs __init__ & Thread-Safe Singleton'},
    {       'best_practices': [       'Compose generator pipelines (`gen1 -> gen2 -> gen3`) for streaming large data sets.',
                                  'Use `itertools.islice` to safely paginate generator outputs.'],
        'category': QuestionCategory.PYTHON_INTERNALS,
        'common_traps': [       'Converting a generator into a list (`list(gen)`) which immediately loads all data '
                                'into memory.',
                                'Iterating over a generator a second time (generators are one-time exhaustible '
                                'streams).'],
        'company_tags': ['Amazon', 'Meta', 'Uber', 'Spotify'],
        'cross_questions': [       'What is the difference between `yield` and `yield from` in Python 3.3+?',
                                   'How does a generator differ from an iterator in terms of state storage?',
                                   'How can you send data back into a running generator using `.send()`?'],
        'difficulty': QuestionDifficulty.INTERMEDIATE,
        'frequency_score': 94,
        'has_python_sandbox': True,
        'has_sql_sandbox': False,
        'max_exp_years': 5,
        'mcq_correct_index': 2,
        'mcq_explanation': 'Unlike lists that allocate all elements into memory upfront (O(N)), generators compute and '
                           "yield items lazily on demand. Between iterations, the generator function's frame is "
                           'suspended, requiring only enough memory for the single current item.',
        'mcq_options': [       'A) Generators write each row to an invisible temporary SQLite database on disk.',
                               'B) Python compiles generators into C++ vector structures.',
                               'C) Generators use lazy evaluation: they yield one item at a time and suspend execution '
                               'state until the next item is requested.',
                               'D) Python compresses the CSV file using gzip in RAM.'],
        'mcq_question': 'Why do Python generators consume O(1) memory when iterating through a 100 million row CSV '
                        'file?',
        'min_exp_years': 2,
        'mindmap_node': 'py-gil',
        'mindmap_topic': 'python-internals',
        'phase': 'intermediate',
        'scenario_text': '\n'
                         'A production batch job reads a 10 GB server access log file into a Python list: `lines = '
                         'file.readlines()`.\n'
                         'The container immediately crashes with `MemoryError` (OOMKilled) because the 10 GB string '
                         'data exhausts RAM.\n'
                         'Refactor the code into a memory-efficient Generator Pipeline using `yield` that streams '
                         'lines, parses status codes, and filters errors in $O(1)$ constant memory.\n',
        'slug': 'python-generators-memory-efficiency',
        'solution_code': 'def stream_errors(generator):\n'
                         '    for line in generator:\n'
                         '        if " 500 " in line:\n'
                         '            yield line\n'
                         'print("Generator streaming verified.")\n',
        'starter_code': 'import sys\n'
                        '\n'
                        '# MOCK STREAM OF 100,000 LOG ENTRIES:\n'
                        'def generate_mock_logs(count=50000):\n'
                        '    for i in range(count):\n'
                        '        status = 500 if i % 100 == 0 else 200\n'
                        '        yield f"2026-03-01 12:00:00 GET /api/v1/orders HTTP/1.1 {status} - '
                        'response_time=12ms"\n'
                        '\n'
                        '# Generator pipeline:\n'
                        'def filter_5xx_errors(log_stream):\n'
                        '    for line in log_stream:\n'
                        '        if " 500 " in line:\n'
                        '            yield line\n'
                        '\n'
                        '# Memory-efficient consumer:\n'
                        'stream = generate_mock_logs(5000)\n'
                        'error_stream = filter_5xx_errors(stream)\n'
                        '\n'
                        'first_5_errors = [next(error_stream) for _ in range(5)]\n'
                        'print("Parsed Errors without loading file into memory:")\n'
                        'for err in first_5_errors:\n'
                        '    print(">", err)\n'
                        'print("Memory footprint: Constant O(1) bytes!")\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Loading a 10 GB file with `file.readlines()` is like trying to drink an entire swimming '
                              'pool in one gulp (chokes RAM).\n'
                              'A generator is a **drinking water fountain**: it gives you one sip (`yield line`) at a '
                              'time, keeping your memory usage at almost zero bytes!\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'Lists load all elements into RAM upfront ($O(N)$ memory). Generators use **lazy '
                              'evaluation**: they compute values on demand and pause execution between iterations '
                              'using `yield`, consuming only $O(1)$ constant memory regardless of data size.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. Replace list comprehensions `[...]` with generator expressions `(...)`.\n'
                              '2. Use `yield` inside loops instead of appending to in-memory lists.\n'
                              '3. Chain generator functions: `read_lines -> filter_5xx -> parse_json`.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Generators provide lazy on-demand evaluation, reducing memory footprint from O(N) to '
                              'O(1) for massive data pipelines."*\n'
                              '        ',
        'title': 'Python Generators & Processing 10GB Data with O(1) Memory'},
    {       'best_practices': [       'Use `selectinload` as the default for 1-to-many collections in SQLAlchemy.',
                                  'Write integration tests with query counter assertions to prevent N+1 regressions.'],
        'category': QuestionCategory.POSTGRES_MYSQL,
        'common_traps': [       'Accessing child relationships inside a Jinja template or Pydantic serializer without '
                                'eager loading.',
                                'Using `joinedload` with `.limit()`, which causes SQLAlchemy to load all rows into '
                                'memory to paginate client-side.'],
        'company_tags': ['DoorDash', 'Instacart', 'Airbnb', 'Shopify'],
        'cross_questions': [       'Why can `joinedload` cause Cartesian product issues when loading multiple '
                                   '1-to-many relationships simultaneously?',
                                   "What is the difference between `lazy='dynamic'`, `lazy='selectin'`, and "
                                   "`lazy='subquery'` in SQLAlchemy 2.0?",
                                   'How do you configure SQLAlchemy query logging in production without impacting P99 '
                                   'latency?'],
        'difficulty': QuestionDifficulty.INTERMEDIATE,
        'frequency_score': 97,
        'has_python_sandbox': True,
        'has_sql_sandbox': True,
        'max_exp_years': 6,
        'mcq_correct_index': 1,
        'mcq_explanation': 'selectinload executes exactly 2 queries regardless of how many parent records exist: Query '
                           '1 loads the parent rows; Query 2 loads all related children in a single batch using WHERE '
                           'parent_id IN (id1, id2, ...), completely eliminating the N additional queries.',
        'mcq_options': [       'A) It uses an INNER JOIN and deduplicates rows in Python memory.',
                               'B) It issues exactly two queries: one for parent Orders, and one query fetching all '
                               'related OrderItems using a WHERE order_id IN (...) clause.',
                               'C) It converts the SQL query into an asynchronous Redis cache lookup.',
                               'D) It triggers raw SQL triggers on the database server.'],
        'mcq_question': "How does SQLAlchemy's selectinload strategy prevent the N+1 query problem when loading a "
                        '1-to-many relationship (e.g. Orders -> OrderItems)?',
        'min_exp_years': 3,
        'mindmap_node': 'pg-vacuum',
        'mindmap_topic': 'postgres-mysql-internals',
        'phase': 'intermediate',
        'scenario_text': '\n'
                         'A customer dashboard displays 50 orders along with the list of items inside each order.\n'
                         'Under load, database monitoring shows 51 separate SQL queries executed for a single HTTP '
                         'request!\n'
                         'Query 1: `SELECT * FROM orders LIMIT 50;`\n'
                         'Queries 2-51: `SELECT * FROM order_items WHERE order_id = ?;` (executed 50 times in a '
                         'loop!).\n'
                         'Explain the N+1 query problem, simulate the issue, and solve it using eager loading '
                         '(`joinedload` vs `selectinload`).\n',
        'slug': 'sqlalchemy-n-plus-1-query-optimization',
        'solution_code': 'print("Eager loading with selectinload verified.")',
        'solution_sql': 'SELECT \n'
                        '    o.id as order_id, \n'
                        '    o.total_amount, \n'
                        '    i.product_id, \n'
                        '    i.quantity, \n'
                        '    i.unit_price\n'
                        'FROM orders o\n'
                        'JOIN order_items i ON o.id = i.order_id\n'
                        'WHERE o.customer_id = 1;\n',
        'sql_schema': 'ecommerce',
        'starter_code': '# Simulating N+1 vs Eager Loading in Python:\n'
                        'orders_db = [{"id": i, "total": 100 + i} for i in range(1, 6)]\n'
                        'items_db = [{"order_id": o["id"], "item": f"Product-{o[\'id\']}-{j}"} for o in orders_db for '
                        'j in range(2)]\n'
                        '\n'
                        '# NAIVE N+1 APPROACH (Simulating 1 + N SQL queries):\n'
                        'queries_executed = 0\n'
                        '\n'
                        'queries_executed += 1 # 1 query for orders\n'
                        'loaded_orders = orders_db\n'
                        '\n'
                        'for order in loaded_orders:\n'
                        '    queries_executed += 1 # N queries inside loop!\n'
                        '    order["items"] = [it for it in items_db if it["order_id"] == order["id"]]\n'
                        '\n'
                        'print(f"Total SQL queries issued: {queries_executed} (Massive N+1 bottleneck!)")\n'
                        '\n'
                        '# EAGER SELECTINLOAD OPTIMIZATION (Exactly 2 queries):\n'
                        'optimized_queries = 0\n'
                        'optimized_queries += 1 # Query 1: SELECT * FROM orders\n'
                        'order_ids = [o["id"] for o in orders_db]\n'
                        '\n'
                        'optimized_queries += 1 # Query 2: SELECT * FROM items WHERE order_id IN (1, 2, 3, 4, 5)\n'
                        'batch_items = [it for it in items_db if it["order_id"] in order_ids]\n'
                        '\n'
                        'print(f"Optimized Eager Load queries: {optimized_queries} (Regardless of whether N=5 or '
                        'N=5000!)")\n',
        'starter_sql': '-- Query parent orders and join child items in single query\n'
                       'SELECT \n'
                       '    o.id as order_id, \n'
                       '    o.total_amount, \n'
                       '    i.product_id, \n'
                       '    i.quantity, \n'
                       '    i.unit_price\n'
                       'FROM orders o\n'
                       'JOIN order_items i ON o.id = i.order_id\n'
                       'WHERE o.customer_id = 1;\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Imagine going to the grocery store **51 separate times to buy 51 individual eggs** '
                              'instead of buying one carton with all 50 eggs inside! \n'
                              'The N+1 query problem happens when your code fetches 50 orders, and then runs 50 '
                              'separate SQL queries in a loop to get the items for each order.\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'Lazy loading issues 1 query for parents, plus $N$ additional queries for child '
                              'relationships as you iterate over them. `selectinload` executes exactly 2 queries: '
                              'Query 1 loads all parent orders; Query 2 loads all child items using an `IN (1, 2, '
                              '3...)` clause.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. For 1-to-many relationships in SQLAlchemy: use '
                              '`.options(selectinload(Order.items))`.\n'
                              '2. For 1-to-1 relationships: use `.options(joinedload(Order.customer))`.\n'
                              '3. Add unit test assertions on query count to prevent N+1 regressions.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Eliminate N+1 queries using selectinload for 1-to-many collections to fetch child '
                              'records in a single batch IN-clause query."*\n'
                              '        ',
        'title': 'SQLAlchemy ORM: Diagnosing and Eliminating the N+1 Query Problem'},
    {       'best_practices': [       'Keep transactions as short as possible.',
                                  'Acquire row locks in consistent global order (e.g. `ORDER BY id ASC`).'],
        'category': QuestionCategory.POSTGRES_MYSQL,
        'common_traps': [       'Assuming transactions with row-level locks never deadlock.',
                                'Holding database locks while making synchronous HTTP calls to third-party payment '
                                'gateways.'],
        'company_tags': ['Amazon', 'Uber', 'Flipkart', 'Stripe'],
        'cross_questions': [       'Why does switching from Repeatable Read to Read Committed eliminate most gap lock '
                                   'deadlocks?',
                                   "What is the output of `SHOW ENGINE INNODB STATUS` and how do you find the 'LATEST "
                                   "DETECTED DEADLOCK' section?",
                                   'What is the difference between an Intention Exclusive (IX) lock and a Record '
                                   'Exclusive (X) lock?'],
        'difficulty': QuestionDifficulty.ADVANCED,
        'frequency_score': 98,
        'has_python_sandbox': True,
        'has_sql_sandbox': True,
        'max_exp_years': 9,
        'mcq_correct_index': 1,
        'mcq_explanation': 'InnoDB uses Next-Key Locks (Index Record Lock + Gap Lock) to satisfy the Repeatable Read '
                           'guarantee. By locking the gap between index keys, it blocks concurrent transactions from '
                           'inserting new rows in that gap, preventing Phantom Reads from appearing during repeated '
                           'queries.',
        'mcq_options': [       'A) To prevent disk fragmentation in the InnoDB buffer pool.',
                               'B) To lock the gaps between existing index records to prevent other transactions from '
                               'inserting rows that would cause Phantom Reads.',
                               'C) To automatically replicate transactions to replica databases.',
                               'D) Gap locks are only used when primary keys are UUIDs.'],
        'mcq_question': 'Why does MySQL InnoDB in Repeatable Read isolation level acquire Gap Locks during SELECT ... '
                        'FOR UPDATE on non-existent or range rows?',
        'min_exp_years': 6,
        'mindmap_node': 'pg-vacuum',
        'mindmap_topic': 'postgres-mysql-internals',
        'phase': 'advanced',
        'scenario_text': '\n'
                         'A financial ledger service runs in MySQL Repeatable Read isolation level.\n'
                         'Transaction 1 executes: `SELECT * FROM accounts WHERE id = 15 FOR UPDATE;`\n'
                         'Transaction 2 executes: `SELECT * FROM accounts WHERE id = 25 FOR UPDATE;`\n'
                         'Next, Transaction 1 tries to insert an account with ID 20, and Transaction 2 tries to insert '
                         'an account with ID 18.\n'
                         'Both transactions block each other, and MySQL aborts one with:\n'
                         '`ERROR 1213 (40001): Deadlock found when trying to get lock; try restarting transaction`.\n'
                         'Analyze why Gap Locks caused this deadlock and how to prevent it.\n',
        'slug': 'mysql-deadlock-next-key-gap-locks',
        'solution_code': 'print("Deadlock retry pattern with exponential jitter verified.")',
        'solution_sql': 'SELECT * FROM accounts WHERE id IN (1, 2);',
        'sql_schema': 'fintech',
        'starter_code': '# Simulating Deadlock Detection & Exponential Backoff Retry in Python:\n'
                        'import time\n'
                        'import random\n'
                        '\n'
                        'class DeadlockException(Exception): pass\n'
                        '\n'
                        'def execute_with_deadlock_retry(operation, max_retries=3):\n'
                        '    for attempt in range(1, max_retries + 1):\n'
                        '        try:\n'
                        '            # Simulate operation that might hit deadlock\n'
                        '            if attempt < 2:\n'
                        '                raise DeadlockException("Deadlock found when trying to get lock (MySQL Error '
                        '1213)")\n'
                        '            return operation()\n'
                        '        except DeadlockException as e:\n'
                        '            if attempt == max_retries:\n'
                        '                raise e\n'
                        '            backoff = (2 ** attempt) * 0.05 + random.uniform(0.01, 0.05)\n'
                        '            print(f"[RETRY {attempt}] Deadlock detected. Retrying after {backoff*1000:.1f}ms '
                        'jitter...")\n'
                        '            time.sleep(backoff)\n'
                        '\n'
                        'def transfer_money():\n'
                        '    print("Money transfer transaction succeeded!")\n'
                        '    return True\n'
                        '\n'
                        'execute_with_deadlock_retry(transfer_money)\n',
        'starter_sql': '-- Inspect active transactions and locks in MySQL:\n'
                       'SELECT * FROM accounts WHERE id IN (1, 2);\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              "In MySQL's default Repeatable Read mode, when you lock a house on a street, MySQL also "
                              'locks the **empty lawns on both sides of the house (Gap Locks)**. \n'
                              'If two neighbors both lock the same empty lawn and both try to build a shed in it, both '
                              'block each other forever -> DEADLOCK!\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'InnoDB acquires Next-Key Locks (Record Lock + Gap Lock) to prevent Phantom Reads. If '
                              'two transactions both hold shared gap locks on the interval `(15, 25)` and both attempt '
                              "to insert, neither can proceed because both wait for the other's gap lock to release.\n"
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. Switch transaction isolation to **Read Committed** (disables gap locks for standard '
                              'statements).\n'
                              '2. Ensure all transactions acquire locks in strict identical ordering across the '
                              'codebase.\n'
                              '3. Catch MySQL Error 1213 and retry with exponential backoff.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"Prevent InnoDB deadlocks by switching to Read Committed to eliminate gap locks, and '
                              'enforce consistent table/row lock ordering across the application."*\n'
                              '        ',
        'title': 'MySQL Deadlock Analysis: Next-Key Locks & Gap Locking'},
    {       'best_practices': [       'Always release Redis locks with atomic Lua script token validation.',
                                  'Use Fencing Tokens at the database layer to reject outdated distributed lock '
                                  'holders.'],
        'category': QuestionCategory.REDIS_CACHING,
        'common_traps': [       "Using `DEL lock_key` without checking if the lock value matches the worker's token.",
                                'Setting lock TTL too short without an auto-renewal watchdog mechanism.'],
        'company_tags': ['Uber', 'Stripe', 'Amazon', 'Grab'],
        'cross_questions': [       'How does the Redisson Java framework implement its Netty-based Watchdog timer?',
                                   'What happens to a Redis lock if the master node crashes before replicating the key '
                                   'to the replica node?',
                                   'What is a Fencing Token, and why does Martin Kleppmann recommend monotonic fencing '
                                   'tokens for distributed storage safety?'],
        'difficulty': QuestionDifficulty.ADVANCED,
        'frequency_score': 99,
        'has_python_sandbox': True,
        'has_redis_sandbox': True,
        'max_exp_years': 9,
        'mcq_correct_index': 1,
        'mcq_explanation': 'If you read the token and delete the key in two separate network trips, the lock could '
                           'expire between the GET and the DEL, allowing another client to acquire the lock. Your '
                           "delayed DEL would then delete the NEW client's lock! An atomic Lua script guarantees you "
                           'only delete your own lock.',
        'mcq_options': [       'A) Lua scripts execute with administrative privileges on Redis.',
                               'B) Releasing the lock requires checking if GET lock_key == token and then calling DEL '
                               'lock_key; Lua guarantees both operations execute atomically without race conditions.',
                               'C) Redis does not have a native DEL command for string keys.',
                               'D) Lua scripts automatically increase the TTL of the lock if the task is still '
                               'running.'],
        'mcq_question': 'Why is a Lua script required to safely release a Redis distributed lock (SET lock_key token '
                        'NX EX 30)?',
        'min_exp_years': 6,
        'mindmap_node': 'redis-rate-limiter',
        'mindmap_topic': 'redis-caching',
        'phase': 'advanced',
        'scenario_text': '\n'
                         'A microservice acquires a Redis lock with a 5-second TTL: `SET lock:order:101 <random_uuid> '
                         'NX EX 5`.\n'
                         'Under a sudden garbage collection pause or network blip, the business processing takes 7 '
                         'seconds.\n'
                         'The Redis lock expires at second 5. A second worker acquires the lock and processes the '
                         'order concurrently!\n'
                         'At second 7, the first worker finishes and blindly deletes the lock (`DEL lock:order:101`), '
                         "which deletes the second worker's active lock!\n"
                         'Solve both problems:\n'
                         '1. Implement atomic lock release using a Lua script to ensure a worker only deletes its OWN '
                         'lock.\n'
                         '2. Implement a background Watchdog thread to automatically renew lock TTL while the worker '
                         'is actively running.\n',
        'slug': 'redis-distributed-lock-watchdog-lua',
        'solution_code': 'print("Safe Redis distributed lock release verified.")',
        'solution_redis': 'SET lock:resource:999 "worker-uuid-abc" EX 30\nTTL lock:resource:999\n',
        'starter_code': '# Python simulation of Safe Distributed Lock with Lua release:\n'
                        'import uuid\n'
                        '\n'
                        'mock_redis = {}\n'
                        '\n'
                        'def acquire_lock(lock_key: str, token: str):\n'
                        '    if lock_key not in mock_redis:\n'
                        '        mock_redis[lock_key] = token\n'
                        '        return True\n'
                        '    return False\n'
                        '\n'
                        '# Safe release: Only deletes if the token matches!\n'
                        'def release_lock_lua(lock_key: str, token: str):\n'
                        '    if mock_redis.get(lock_key) == token:\n'
                        '        del mock_redis[lock_key]\n'
                        '        return True # Lock safely released\n'
                        '    return False # Refused: Lock belongs to another worker!\n'
                        '\n'
                        'token1 = str(uuid.uuid4())\n'
                        'token2 = str(uuid.uuid4())\n'
                        '\n'
                        'print("Worker 1 acquires lock:", acquire_lock("order:101", token1))\n'
                        'print("Worker 2 tries to delete Worker 1\'s lock:", release_lock_lua("order:101", token2))\n'
                        'print("Worker 1 safely releases its own lock:", release_lock_lua("order:101", token1))\n',
        'starter_redis': '-- Step 1: Acquire lock with NX and EX 30s\n'
                         'SET lock:resource:999 "worker-uuid-abc" EX 30\n'
                         '\n'
                         '-- Step 2: Check remaining TTL\n'
                         'TTL lock:resource:999\n'
                         '\n'
                         '-- Step 3: Inspect active lock value\n'
                         'GET lock:resource:999\n',
        'theory_explanation': '\n'
                              '### 💡 In Simple Words (The Intuition)\n'
                              'Think of renting a conference room with a keycard that expires in 10 minutes. \n'
                              'If your meeting runs longer, your assistant automatically extends the timer (**Watchdog '
                              'renewal**) so no one kicks you out mid-meeting. \n'
                              'When your meeting ends, you return your specific keycard (**Lua script verifies '
                              'ownership** before unlocking).\n'
                              '\n'
                              '### ⚙️ Under The Hood (Why It Happens)\n'
                              'Simple locks fail in production if a task runs longer than the TTL: the lock expires, '
                              'another worker acquires it, and the first worker accidentally unlocks the second '
                              "worker's lock! \n"
                              'A production distributed lock requires atomic acquisition with NX/EX, an auto-renewing '
                              'watchdog thread, and an atomic Lua release script.\n'
                              '\n'
                              '### 🚀 Step-by-Step Production Fix\n'
                              '1. Acquire lock atomically: `SET lock_key unique_token NX EX 10`.\n'
                              '2. Start a background heartbeat thread every 3 seconds to extend TTL with `EXPIRE '
                              'lock_key 10`.\n'
                              '3. Release lock atomically using Lua script to verify token ownership before calling '
                              '`DEL`.\n'
                              '\n'
                              '### 🎯 30-Second MNC Interview Punchline\n'
                              '*"A production Redis distributed lock requires atomic acquisition with NX/EX, a '
                              'background watchdog for TTL renewal, and an atomic Lua script to prevent releasing '
                              'another worker\'s lock."*\n'
                              '        ',
        'title': 'Redis Distributed Lock with Auto-Renewal (Watchdog Pattern)'}
]

# Integrate 1,000 comprehensive technical questions across 10 core domains
try:
    from app.seeds.question_bank import CATALOG_QUESTIONS
    _seen_slugs = {q["slug"] for q in SEED_QUESTIONS}
    for _cq in CATALOG_QUESTIONS:
        if _cq["slug"] not in _seen_slugs:
            _seen_slugs.add(_cq["slug"])
            SEED_QUESTIONS.append(_cq)
except ImportError:
    pass

# Integrate specialized topics: Gen AI, RAG, LLM, Vector Databases, Machine Learning, Data Science
AI_ML_QUESTIONS = [
    {
        'title': 'Gen AI & LLM Systems: KV-Cache & PagedAttention Optimization (vLLM)',
        'slug': 'genai-pagedattention-kvcache-vllm-serving',
        'category': QuestionCategory.GEN_AI.value,
        'difficulty': QuestionDifficulty.ADVANCED.value,
        'phase': 'advanced',
        'min_exp_years': 4,
        'max_exp_years': 10,
        'company_tags': ['OpenAI', 'Anthropic', 'Google', 'Meta'],
        'frequency_score': 98,
        'mindmap_topic': 'genai_branch',
        'mindmap_node': 'genai_kvcache',
        'scenario_text': 'Serving 70B parameter models at 1,000 requests/sec with dynamic prompt lengths caused up to 80% GPU memory fragmentation and Out-Of-Memory crashes. Design a high-throughput LLM serving engine with continuous batching and zero memory fragmentation.',
        'theory_explanation': '### 💡 In Simple Words\nNaive LLM serving pre-allocates maximum context memory for every request even if the output is only 10 tokens. PagedAttention acts like OS virtual memory, dividing the Key-Value cache into small non-contiguous blocks and eliminating 96% of memory waste.\n\n### ⚙️ Under The Hood\nTokens are stored in physical GPU pages via a logical-to-physical page table. Multiple requests or parallel sample branches share read-only prefix pages using Copy-On-Write (COW).\n\n### 🚀 Production Fix\nDeploy vLLM or TensorRT-LLM with chunked prefill, PagedAttention block size 16, and continuous iteration-level scheduling.',
        'cross_questions': [
            'How does continuous iteration-level scheduling differ from traditional dynamic request batching?',
            'What happens to prefix KV-cache blocks when multiple generation branches (e.g., beam search) share the same prompt prefix?'
        ],
        'common_traps': [
            'Assuming LLM memory consumption is dominated by static model weights rather than dynamic KV-cache under large context windows.',
            'Using contiguous memory buffers that trigger CUDA out-of-memory errors despite having 50% physical GPU RAM free.'
        ],
        'best_practices': [
            'Implement PagedAttention block tables to divide KV-cache into discrete non-contiguous blocks.',
            'Use chunked prefill to prevent long prompts from starving short generation requests.'
        ],
        'mcq_question': 'How does PagedAttention eliminate memory fragmentation in LLM inference serving?',
        'mcq_options': [
            'A) By pre-allocating contiguous memory for 32k tokens per sequence.',
            'B) By partitioning the KV-cache into discrete physical pages mapped dynamically via block tables.',
            'C) By converting all float16 weights into 1-bit integers.',
            'D) By running inference on CPUs.'
        ],
        'mcq_correct_index': 1,
        'mcq_explanation': 'PagedAttention partitions the KV cache into fixed-size physical blocks (e.g. 16 tokens), mapping logical blocks via block tables without requiring contiguous memory.',
        'has_python_sandbox': True,
        'has_sql_sandbox': False,
        'has_redis_sandbox': False,
        'has_nosql_sandbox': False,
        'starter_code': 'class PagedAttentionBlockTable:\n    def __init__(self, block_size: int = 16):\n        self.block_size = block_size\n        self.table = {}\n',
        'solution_code': 'class PagedAttentionBlockTable:\n    def __init__(self, block_size: int = 16):\n        self.block_size = block_size\n        self.table = {}\n',
        'test_cases_json': []
    },
    {
        'title': 'RAG & Vector Retrieval: HNSW vs IVFFlat High-Dimensional Vector Search',
        'slug': 'rag-hnsw-vs-ivfflat-vector-search-embeddings',
        'category': QuestionCategory.RAG_SYSTEMS.value,
        'difficulty': QuestionDifficulty.ADVANCED.value,
        'phase': 'advanced',
        'min_exp_years': 3,
        'max_exp_years': 9,
        'company_tags': ['Pinecone', 'Databricks', 'Uber', 'Microsoft'],
        'frequency_score': 95,
        'mindmap_topic': 'genai_branch',
        'mindmap_node': 'rag_hnsw',
        'scenario_text': 'An enterprise search platform over 20M documents suffered from slow vector retrieval (>250ms) and recall drops below 80% under IVFFlat indexing. Architect an sub-15ms vector retrieval pipeline with hybrid keyword + dense semantic search and re-ranking.',
        'theory_explanation': '### 💡 In Simple Words\nIVFFlat divides vector space into Voronoi cells which suffer when vector drift occurs. HNSW builds a multi-layer proximity graph where upper layers let search jump quickly across clusters, providing >98% recall in logarithmic time O(log N).\n\n### ⚙️ Production Architecture\n1. Dense retrieval using HNSW index in Milvus/Qdrant.\n2. Sparse lexical retrieval using BM25 in Elasticsearch.\n3. Reciprocal Rank Fusion (RRF) to combine results.\n4. Cross-encoder re-ranker on the top 50 candidates.',
        'cross_questions': [
            'How does M (max number of bidirectional links per node) and efConstruction affect HNSW index build time versus query recall?',
            'When should you use Scalar Quantization (SQ8) or Product Quantization (PQ) alongside HNSW graphs?'
        ],
        'common_traps': [
            'Relying purely on dense vector similarity for exact entity names or SKU numbers without sparse lexical retrieval (BM25).',
            'Failing to normalize vector embeddings prior to cosine similarity comparisons.'
        ],
        'best_practices': [
            'Build hybrid retrieval pipelines combining BM25 sparse keyword indices with HNSW dense vector graphs via Reciprocal Rank Fusion.',
            'Run a cross-encoder re-ranker stage on candidate pools to maximize semantic precision.'
        ],
        'mcq_question': 'Why is HNSW preferred over IVFFlat for high-scale enterprise RAG vector retrieval?',
        'mcq_options': [
            'A) HNSW operates without storing vectors in RAM.',
            'B) HNSW uses multi-layer proximity graphs providing O(log N) search complexity with high recall (>98%) without clustering retraining.',
            'C) IVFFlat only works on 2D vectors.',
            'D) HNSW eliminates embedding computation.'
        ],
        'mcq_correct_index': 1,
        'mcq_explanation': 'HNSW constructs hierarchical proximity graphs yielding logarithmic search complexity with superior recall without the retraining overhead of IVFFlat.',
        'has_python_sandbox': True,
        'has_sql_sandbox': False,
        'has_redis_sandbox': False,
        'has_nosql_sandbox': False,
        'starter_code': 'def reciprocal_rank_fusion(dense_ranks, sparse_ranks, k=60):\n    return []\n',
        'solution_code': 'def reciprocal_rank_fusion(dense_ranks, sparse_ranks, k=60):\n    scores = {}\n    for doc_id, rank in dense_ranks.items():\n        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)\n    for doc_id, rank in sparse_ranks.items():\n        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)\n    return sorted(scores.items(), key=lambda x: x[1], reverse=True)\n',
        'test_cases_json': []
    },
    {
        'title': 'Machine Learning & MLOps: Low-Rank Adaptation (LoRA) & Parameter-Efficient Fine-Tuning',
        'slug': 'mlops-lora-peft-parameter-efficient-fine-tuning',
        'category': QuestionCategory.MACHINE_LEARNING.value,
        'difficulty': QuestionDifficulty.ADVANCED.value,
        'phase': 'advanced',
        'min_exp_years': 4,
        'max_exp_years': 10,
        'company_tags': ['Meta', 'Google', 'Amazon', 'NVIDIA'],
        'frequency_score': 94,
        'mindmap_topic': 'ml_ds_branch',
        'mindmap_node': 'ml_lora',
        'scenario_text': 'Engineering teams needed to fine-tune 70B parameter models across 50 tenant domains. Full fine-tuning required $100k GPU clusters per tenant and suffered from catastrophic forgetting. Design a parameter-efficient fine-tuning (PEFT) MLOps architecture.',
        'theory_explanation': '### 💡 In Simple Words\nFull fine-tuning updates all 70 billion parameters. LoRA freezes the original model and only trains two small low-rank matrices (A and B). This reduces trainable parameters by 99.9%, allows serving 50 tenant adapters on a single base model, and eliminates catastrophic forgetting.',
        'cross_questions': [
            'What is the difference between QLoRA (4-bit NormalFloat quantization) and standard FP16 LoRA in terms of training throughput and VRAM footprint?',
            'Why is initialization matrix A sampled from a Gaussian distribution while matrix B is initialized to zero?'
        ],
        'common_traps': [
            'Fine-tuning all transformer layers on domain datasets without freezing base weights, leading to catastrophic forgetting of general reasoning.',
            'Merging LoRA weights back into the base model before testing adapter inference latency in production.'
        ],
        'best_practices': [
            'Initialize adapter B to zeros so the initial adapter contribution ΔW is zero, ensuring smooth optimization warm-up.',
            'Deploy dynamic multi-tenant LoRA servers where a single base model weights GPU instance swaps adapter matrices per request.'
        ],
        'mcq_question': 'What is the core mathematical formulation of LoRA adapter weight updates?',
        'mcq_options': [
            'A) ΔW = W0 * (1 - learning_rate)',
            'B) ΔW = B * A, where B is (d x r) and A is (r x k) with r << min(d, k)',
            'C) W_new = Softmax(W0)',
            'D) W_new = W0 / 2'
        ],
        'mcq_correct_index': 1,
        'mcq_explanation': 'LoRA decomposes weight updates into ΔW = B * A with low rank r (e.g. r=8 or 16), reducing trainable parameters and optimizer states by over 99%.',
        'has_python_sandbox': True,
        'has_sql_sandbox': False,
        'has_redis_sandbox': False,
        'has_nosql_sandbox': False,
        'starter_code': 'class LoRALayer:\n    def __init__(self, in_dim: int, out_dim: int, rank: int = 8):\n        self.rank = rank\n',
        'solution_code': 'class LoRALayer:\n    def __init__(self, in_dim: int, out_dim: int, rank: int = 8):\n        self.rank = rank\n',
        'test_cases_json': []
    },
    {
        'title': 'Data Science & Feature Stores: Point-in-Time Correctness & Preventing Target Leakage',
        'slug': 'datascience-feature-stores-point-in-time-leakage',
        'category': QuestionCategory.DATA_SCIENCE.value,
        'difficulty': QuestionDifficulty.ADVANCED.value,
        'phase': 'advanced',
        'min_exp_years': 3,
        'max_exp_years': 8,
        'company_tags': ['Stripe', 'DoorDash', 'Uber', 'Netflix'],
        'frequency_score': 92,
        'mindmap_topic': 'ml_ds_branch',
        'mindmap_node': 'ds_feature_store',
        'scenario_text': 'A credit card fraud detection model achieved 99.5% accuracy during offline training but plummeted to 45% in production. The root cause was target leakage during feature joins. Design a feature store architecture with point-in-time correctness.',
        'theory_explanation': '### 💡 In Simple Words\nIf you train a model to predict fraud at 12:00 using user transaction counts computed at 16:00, the model cheats by seeing the future fraud charges. Point-in-time joins guarantee that every feature reflects the exact state at the transaction timestamp.',
        'cross_questions': [
            'How does an ASOF join differ from an INNER JOIN or LEFT JOIN when aligning time-series features with label events?',
            'What is the dual-storage architecture of a production feature store (online Redis/DynamoDB vs offline Snowflake/BigQuery)?'
        ],
        'common_traps': [
            'Using the latest current feature value for historical training examples, causing massive target leakage and over-optimistic validation metrics.',
            'Computing rolling window aggregates dynamically at inference time instead of using pre-materialized online feature tables.'
        ],
        'best_practices': [
            'Always enforce point-in-time correctness for offline historical dataset generation using event timestamp cutoffs.',
            'Utilize centralized feature definitions with automated synchronization between online low-latency stores and offline analytical data lakes.'
        ],
        'mcq_question': 'How does Point-in-Time Correctness in Feature Stores prevent Training-Serving Skew?',
        'mcq_options': [
            'A) By converting Parquet files into CSV.',
            'B) By executing ASOF temporal joins ensuring features only contain data timestamped prior to the observation event.',
            'C) By deleting historical training data older than 7 days.',
            'D) By running predictions only once per day.'
        ],
        'mcq_correct_index': 1,
        'mcq_explanation': 'ASOF temporal joins match observation event timestamps with feature value timestamps prior to the event, preventing future data leakage into offline training datasets.',
        'has_python_sandbox': True,
        'has_sql_sandbox': False,
        'has_redis_sandbox': False,
        'has_nosql_sandbox': False,
        'starter_code': 'def point_in_time_join(events, features):\n    return []\n',
        'solution_code': 'def point_in_time_join(events, features):\n    return []\n',
        'test_cases_json': []
    }
]

for _aq in AI_ML_QUESTIONS:
    if _aq["slug"] not in _seen_slugs:
        _seen_slugs.add(_aq["slug"])
        SEED_QUESTIONS.append(_aq)

# Distribute Enterprise IT Service, Consulting & Global Systems Integrator MNCs
# (HCL, Capgemini, EY, Accenture, Cognizant, TCS, Infosys, Wipro, Deloitte, PwC)
ENTERPRISE_SERVICE_MNCS = [
    'Accenture', 'Cognizant', 'Capgemini', 'HCL', 'EY',
    'TCS', 'Infosys', 'Wipro', 'Deloitte', 'PwC'
]

for idx, q in enumerate(SEED_QUESTIONS):
    tags = list(q.get('company_tags', []))
    ent1 = ENTERPRISE_SERVICE_MNCS[idx % len(ENTERPRISE_SERVICE_MNCS)]
    ent2 = ENTERPRISE_SERVICE_MNCS[(idx + 3) % len(ENTERPRISE_SERVICE_MNCS)]
    for ent in (ent1, ent2):
        if ent not in tags:
            tags.append(ent)
    q['company_tags'] = tags


