#!/usr/bin/env python3
"""
Generate realistic Elastic log data for performance analysis.

This script creates a sample_20_healthy_system.json file with realistic
log entries that simulate a healthy system with various performance patterns.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Any


def generate_timestamp(base_time: datetime, offset_minutes: int) -> str:
    """Generate ISO format timestamp."""
    ts = base_time + timedelta(minutes=offset_minutes)
    return ts.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def generate_http_log(
    timestamp: str,
    endpoint: str,
    method: str,
    response_time_ms: int,
    status_code: int,
    client_ip: str,
    user_agent: str,
) -> dict[str, Any]:
    """Generate an HTTP request/response log entry."""
    return {
        "@timestamp": timestamp,
        "log_type": "http",
        "http": {
            "request": {
                "method": method,
                "path": endpoint,
                "headers": {"User-Agent": user_agent},
            },
            "response": {
                "status_code": status_code,
                "body_bytes": random.randint(100, 50000),
            },
        },
        "client": {"ip": client_ip},
        "event": {
            "duration": response_time_ms * 1000000,  # nanoseconds
            "outcome": "success" if status_code < 400 else "failure",
        },
        "service": {"name": "api-gateway", "version": "2.1.0"},
        "host": {"name": f"api-server-{random.randint(1, 3)}"},
    }


def generate_resource_log(
    timestamp: str,
    cpu_percent: float,
    memory_percent: float,
    memory_used_gb: float,
    disk_io_read_mbps: float,
    disk_io_write_mbps: float,
    network_in_mbps: float,
    network_out_mbps: float,
    connection_pool_active: int,
    connection_pool_max: int,
    host_name: str,
) -> dict[str, Any]:
    """Generate a resource utilization log entry."""
    return {
        "@timestamp": timestamp,
        "log_type": "metrics",
        "system": {
            "cpu": {"total": {"pct": cpu_percent / 100}},
            "memory": {
                "total": 32.0,
                "used": {"bytes": int(memory_used_gb * 1024 * 1024 * 1024)},
                "actual": {"used": {"pct": memory_percent / 100}},
            },
            "diskio": {
                "read": {"bytes_per_sec": int(disk_io_read_mbps * 1024 * 1024)},
                "write": {"bytes_per_sec": int(disk_io_write_mbps * 1024 * 1024)},
            },
            "network": {
                "in": {"bytes_per_sec": int(network_in_mbps * 1024 * 1024)},
                "out": {"bytes_per_sec": int(network_out_mbps * 1024 * 1024)},
            },
        },
        "connection_pool": {
            "active": connection_pool_active,
            "max": connection_pool_max,
            "available": connection_pool_max - connection_pool_active,
            "utilization_pct": (connection_pool_active / connection_pool_max) * 100,
        },
        "host": {"name": host_name},
        "service": {"name": "application-server"},
    }


def generate_database_log(
    timestamp: str,
    query_type: str,
    table_name: str,
    execution_time_ms: int,
    rows_affected: int,
    connection_id: int,
    is_slow: bool,
) -> dict[str, Any]:
    """Generate a database query log entry."""
    return {
        "@timestamp": timestamp,
        "log_type": "database",
        "database": {
            "type": "postgresql",
            "name": "production_db",
            "query": {
                "type": query_type,
                "table": table_name,
                "execution_time_ms": execution_time_ms,
                "rows_affected": rows_affected,
                "slow_query": is_slow,
            },
            "connection": {
                "id": connection_id,
                "pool_name": "main_pool",
            },
        },
        "event": {
            "duration": execution_time_ms * 1000000,
            "outcome": "success",
        },
        "host": {"name": "db-primary-1"},
    }


def generate_service_health_log(
    timestamp: str,
    service_name: str,
    status: str,
    health_check_duration_ms: int,
    circuit_breaker_state: str,
    error_rate_pct: float,
    request_rate: int,
) -> dict[str, Any]:
    """Generate a service health log entry."""
    return {
        "@timestamp": timestamp,
        "log_type": "service_health",
        "service": {
            "name": service_name,
            "status": status,
            "health_check": {
                "duration_ms": health_check_duration_ms,
                "passed": status == "healthy",
            },
            "circuit_breaker": {
                "state": circuit_breaker_state,
                "failure_count": 0 if circuit_breaker_state == "closed" else random.randint(1, 10),
            },
            "metrics": {
                "error_rate_pct": error_rate_pct,
                "request_rate_per_sec": request_rate,
                "success_rate_pct": 100 - error_rate_pct,
            },
        },
        "host": {"name": f"{service_name}-server-1"},
    }


def generate_error_log(
    timestamp: str,
    error_type: str,
    message: str,
    service_name: str,
    stack_trace: str | None = None,
) -> dict[str, Any]:
    """Generate an error log entry."""
    log_entry = {
        "@timestamp": timestamp,
        "log_type": "error",
        "log": {
            "level": "error",
            "logger": f"{service_name}.error_handler",
        },
        "error": {
            "type": error_type,
            "message": message,
        },
        "service": {"name": service_name},
        "host": {"name": f"{service_name}-server-1"},
    }
    if stack_trace:
        log_entry["error"]["stack_trace"] = stack_trace
    return log_entry


def generate_logs() -> list[dict[str, Any]]:
    """Generate a comprehensive set of log entries for a healthy system."""
    logs: list[dict[str, Any]] = []
    base_time = datetime(2024, 11, 20, 0, 0, 0)

    # Configuration for realistic patterns
    endpoints = [
        ("/api/v1/users", "GET", 50, 150),
        ("/api/v1/users/{id}", "GET", 30, 100),
        ("/api/v1/orders", "GET", 100, 300),
        ("/api/v1/orders", "POST", 150, 400),
        ("/api/v1/products", "GET", 40, 120),
        ("/api/v1/products/search", "GET", 200, 500),
        ("/api/v1/auth/login", "POST", 80, 200),
        ("/api/v1/auth/refresh", "POST", 20, 60),
        ("/api/v1/payments", "POST", 300, 800),
        ("/api/v1/reports/generate", "POST", 500, 2000),
        ("/api/v1/health", "GET", 5, 20),
        ("/api/v1/metrics", "GET", 10, 30),
    ]

    tables = ["users", "orders", "products", "payments", "sessions", "audit_logs"]
    services = [
        "user-service",
        "order-service",
        "payment-service",
        "notification-service",
        "auth-service",
    ]
    hosts = ["api-server-1", "api-server-2", "api-server-3"]
    client_ips = [f"192.168.1.{i}" for i in range(1, 50)]
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) Mobile/15E148",
        "PostmanRuntime/7.32.3",
        "python-requests/2.31.0",
    ]

    # Generate logs over 24 hours with realistic patterns
    for minute in range(0, 1440, 1):  # Every minute for 24 hours
        timestamp = generate_timestamp(base_time, minute)
        hour = minute // 60

        # Traffic pattern: lower at night, peak during business hours
        if 2 <= hour < 6:
            traffic_multiplier = 0.2
        elif 6 <= hour < 9:
            traffic_multiplier = 0.6
        elif 9 <= hour < 12:
            traffic_multiplier = 1.0
        elif 12 <= hour < 14:
            traffic_multiplier = 0.8
        elif 14 <= hour < 18:
            traffic_multiplier = 1.0
        elif 18 <= hour < 22:
            traffic_multiplier = 0.5
        else:
            traffic_multiplier = 0.3

        # Generate HTTP logs
        num_requests = int(random.randint(5, 20) * traffic_multiplier)
        for _ in range(num_requests):
            endpoint, method, base_time_ms, max_time_ms = random.choice(endpoints)

            # Response time with occasional spikes
            if random.random() < 0.02:  # 2% chance of spike
                response_time = random.randint(max_time_ms, max_time_ms * 3)
            else:
                response_time = random.randint(base_time_ms, max_time_ms)

            # Status codes: mostly 200, occasional 4xx/5xx
            rand_val = random.random()
            if rand_val < 0.95:
                status_code = 200
            elif rand_val < 0.98:
                status_code = random.choice([400, 401, 403, 404])
            else:
                status_code = random.choice([500, 502, 503])

            logs.append(
                generate_http_log(
                    timestamp=timestamp,
                    endpoint=endpoint,
                    method=method,
                    response_time_ms=response_time,
                    status_code=status_code,
                    client_ip=random.choice(client_ips),
                    user_agent=random.choice(user_agents),
                )
            )

        # Generate resource metrics every 5 minutes
        if minute % 5 == 0:
            for host in hosts:
                # CPU and memory patterns based on traffic
                base_cpu = 20 + (traffic_multiplier * 30)
                base_memory = 45 + (traffic_multiplier * 20)

                logs.append(
                    generate_resource_log(
                        timestamp=timestamp,
                        cpu_percent=base_cpu + random.uniform(-5, 10),
                        memory_percent=base_memory + random.uniform(-3, 5),
                        memory_used_gb=(base_memory / 100) * 32,
                        disk_io_read_mbps=random.uniform(10, 50) * traffic_multiplier,
                        disk_io_write_mbps=random.uniform(5, 30) * traffic_multiplier,
                        network_in_mbps=random.uniform(20, 100) * traffic_multiplier,
                        network_out_mbps=random.uniform(30, 150) * traffic_multiplier,
                        connection_pool_active=int(50 * traffic_multiplier) + random.randint(0, 20),
                        connection_pool_max=100,
                        host_name=host,
                    )
                )

        # Generate database logs
        num_queries = int(random.randint(3, 10) * traffic_multiplier)
        for _ in range(num_queries):
            query_type = random.choice(["SELECT", "INSERT", "UPDATE", "DELETE"])
            table = random.choice(tables)

            # Execution time based on query type
            if query_type == "SELECT":
                base_exec_time = random.randint(5, 50)
            elif query_type == "INSERT":
                base_exec_time = random.randint(10, 30)
            elif query_type == "UPDATE":
                base_exec_time = random.randint(15, 60)
            else:
                base_exec_time = random.randint(10, 40)

            # Occasional slow queries
            is_slow = random.random() < 0.03
            if is_slow:
                exec_time = base_exec_time * random.randint(5, 20)
            else:
                exec_time = base_exec_time

            logs.append(
                generate_database_log(
                    timestamp=timestamp,
                    query_type=query_type,
                    table_name=table,
                    execution_time_ms=exec_time,
                    rows_affected=random.randint(1, 1000),
                    connection_id=random.randint(1, 50),
                    is_slow=is_slow,
                )
            )

        # Generate service health logs every 10 minutes
        if minute % 10 == 0:
            for service in services:
                # Healthy system: mostly healthy status
                if random.random() < 0.98:
                    status = "healthy"
                    circuit_state = "closed"
                    error_rate = random.uniform(0, 2)
                else:
                    status = "degraded"
                    circuit_state = random.choice(["closed", "half-open"])
                    error_rate = random.uniform(2, 5)

                logs.append(
                    generate_service_health_log(
                        timestamp=timestamp,
                        service_name=service,
                        status=status,
                        health_check_duration_ms=random.randint(5, 50),
                        circuit_breaker_state=circuit_state,
                        error_rate_pct=error_rate,
                        request_rate=int(100 * traffic_multiplier) + random.randint(-20, 20),
                    )
                )

        # Generate occasional error logs
        if random.random() < 0.01:  # 1% chance per minute
            error_types = [
                ("ConnectionTimeout", "Connection to upstream service timed out"),
                ("ValidationError", "Invalid request payload"),
                ("RateLimitExceeded", "Rate limit exceeded for client"),
                ("DatabaseError", "Deadlock detected in transaction"),
                ("CacheError", "Cache miss for frequently accessed key"),
            ]
            error_type, message = random.choice(error_types)
            logs.append(
                generate_error_log(
                    timestamp=timestamp,
                    error_type=error_type,
                    message=message,
                    service_name=random.choice(services),
                )
            )

    return logs


def main() -> None:
    """Generate and save the log file."""
    print("Generating Elastic log data...")
    logs = generate_logs()

    # Sort by timestamp
    logs.sort(key=lambda x: x["@timestamp"])

    output_path = "/home/ubuntu/repos/devin-workshop/logs/sample_20_healthy_system.json"
    with open(output_path, "w") as f:
        json.dump(logs, f, indent=2)

    print(f"Generated {len(logs)} log entries")
    print(f"Saved to: {output_path}")

    # Print summary
    log_types = {}
    for log in logs:
        log_type = log.get("log_type", "unknown")
        log_types[log_type] = log_types.get(log_type, 0) + 1

    print("\nLog type distribution:")
    for log_type, count in sorted(log_types.items()):
        print(f"  {log_type}: {count}")


if __name__ == "__main__":
    main()
