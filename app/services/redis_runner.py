import time
import re
from typing import Dict, Any, List

class InMemoryRedis:
    def __init__(self):
        self.strings: Dict[str, str] = {}
        self.hashes: Dict[str, Dict[str, str]] = {}
        self.lists: Dict[str, List[str]] = {}
        self.zsets: Dict[str, List[tuple]] = {} # [(score, member)]
        self.expirations: Dict[str, float] = {}

    def _is_expired(self, key: str) -> bool:
        if key in self.expirations:
            if time.time() > self.expirations[key]:
                self._delete_key(key)
                return True
        return False

    def _delete_key(self, key: str):
        self.strings.pop(key, None)
        self.hashes.pop(key, None)
        self.lists.pop(key, None)
        self.zsets.pop(key, None)
        self.expirations.pop(key, None)

    def execute_command_line(self, line: str) -> Any:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            return None

        # Split preserving quotes
        parts = re.findall(r'[^\s"\']+|"[^"]*"|\'[^\']*\'', line)
        if not parts:
            return None
        parts = [p.strip('"\'') for p in parts]
        cmd = parts[0].upper()
        args = parts[1:]

        # STRING COMMANDS
        if cmd == "SET":
            if len(args) < 2:
                return "ERR wrong number of arguments for 'set' command"
            key, val = args[0], args[1]
            self._delete_key(key)
            self.strings[key] = val
            # Handle EX seconds
            if len(args) >= 4 and args[2].upper() == "EX":
                ttl = float(args[3])
                self.expirations[key] = time.time() + ttl
            return "OK"

        elif cmd == "GET":
            if len(args) != 1:
                return "ERR wrong number of arguments for 'get' command"
            key = args[0]
            if self._is_expired(key) or key not in self.strings:
                return None
            return self.strings[key]

        elif cmd == "INCR":
            key = args[0]
            val = int(self.strings.get(key, 0)) + 1
            self.strings[key] = str(val)
            return val

        elif cmd == "DECR":
            key = args[0]
            val = int(self.strings.get(key, 0)) - 1
            self.strings[key] = str(val)
            return val

        elif cmd == "DEL":
            count = 0
            for k in args:
                if k in self.strings or k in self.hashes or k in self.lists or k in self.zsets:
                    self._delete_key(k)
                    count += 1
            return count

        # HASH COMMANDS
        elif cmd == "HSET":
            if len(args) < 3:
                return "ERR wrong number of arguments for 'hset' command"
            key, field, val = args[0], args[1], args[2]
            if key not in self.hashes:
                self.hashes[key] = {}
            self.hashes[key][field] = val
            return 1

        elif cmd == "HGET":
            key, field = args[0], args[1]
            if self._is_expired(key) or key not in self.hashes:
                return None
            return self.hashes[key].get(field)

        elif cmd == "HGETALL":
            key = args[0]
            if self._is_expired(key) or key not in self.hashes:
                return {}
            return self.hashes[key]

        # LIST COMMANDS
        elif cmd == "LPUSH":
            key = args[0]
            if key not in self.lists:
                self.lists[key] = []
            for v in args[1:]:
                self.lists[key].insert(0, v)
            return len(self.lists[key])

        elif cmd == "RPUSH":
            key = args[0]
            if key not in self.lists:
                self.lists[key] = []
            for v in args[1:]:
                self.lists[key].append(v)
            return len(self.lists[key])

        elif cmd == "LRANGE":
            key = args[0]
            start = int(args[1]) if len(args) > 1 else 0
            stop = int(args[2]) if len(args) > 2 else -1
            lst = self.lists.get(key, [])
            if stop == -1 or stop >= len(lst):
                return lst[start:]
            return lst[start:stop+1]

        # SORTED SET (ZSET) COMMANDS
        elif cmd == "ZADD":
            if len(args) < 3:
                return "ERR wrong number of arguments for 'zadd' command"
            key = args[0]
            score = float(args[1])
            member = args[2]
            if key not in self.zsets:
                self.zsets[key] = []
            # Remove existing member if any
            self.zsets[key] = [item for item in self.zsets[key] if item[1] != member]
            self.zsets[key].append((score, member))
            self.zsets[key].sort(key=lambda x: x[0])
            return 1

        elif cmd == "ZRANGEBYSCORE":
            key = args[0]
            min_score = float(args[1]) if args[1] != "-inf" else -float("inf")
            max_score = float(args[2]) if args[2] != "+inf" else float("inf")
            z = self.zsets.get(key, [])
            return [item[1] for item in z if min_score <= item[0] <= max_score]

        elif cmd == "ZCARD":
            key = args[0]
            return len(self.zsets.get(key, []))

        elif cmd == "KEYS":
            all_keys = list(set(list(self.strings.keys()) + list(self.hashes.keys()) + list(self.lists.keys()) + list(self.zsets.keys())))
            return all_keys

        elif cmd == "TTL":
            key = args[0]
            if key in self.expirations:
                remaining = int(self.expirations[key] - time.time())
                return max(remaining, -2)
            return -1 if (key in self.strings or key in self.hashes or key in self.lists or key in self.zsets) else -2

        return f"ERR unknown command '{cmd}'"

def run_redis_commands(script: str) -> Dict[str, Any]:
    """
    Executes a script of Redis CLI commands sequentially in an isolated sandbox.
    """
    start_time = time.perf_counter()
    r = InMemoryRedis()
    logs = []
    
    # Preload seed data for MNC scenario
    r.execute_command_line("HSET user:session:101 username alexander")
    r.execute_command_line("HSET user:session:101 tier enterprise")
    r.execute_command_line("SET product:lock:SKU-LAP-01 locked EX 30")
    
    lines = script.strip().split("\n")
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("//"):
            logs.append({"command": line, "type": "comment", "output": None})
            continue

        res = r.execute_command_line(line)
        logs.append({
            "command": line,
            "type": "result",
            "output": res
        })

    duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    return {
        "success": True,
        "logs": logs,
        "execution_time_ms": duration_ms
    }
