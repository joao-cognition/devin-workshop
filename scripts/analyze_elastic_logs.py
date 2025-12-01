#!/usr/bin/env python3
"""
Comprehensive Elastic Log Performance Analysis Script.

This script analyzes Elastic log data to identify performance anomalies,
resource utilization patterns, database performance issues, and provides
capacity planning insights.
"""

import json
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


def load_logs(file_path: str) -> list[dict[str, Any]]:
    """Load log entries from JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO format timestamp."""
    return datetime.strptime(ts.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f")


def calculate_percentile(data: list[float], percentile: float) -> float:
    """Calculate the given percentile of a list of values."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = (len(sorted_data) - 1) * percentile / 100
    lower = int(index)
    upper = lower + 1
    if upper >= len(sorted_data):
        return sorted_data[-1]
    weight = index - lower
    return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


def analyze_response_times(logs: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze HTTP response times per endpoint."""
    http_logs = [log for log in logs if log.get("log_type") == "http"]

    endpoint_times: dict[str, list[int]] = defaultdict(list)
    endpoint_status_codes: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    hourly_response_times: dict[int, list[int]] = defaultdict(list)
    response_time_spikes: list[dict[str, Any]] = []

    for log in http_logs:
        endpoint = log["http"]["request"]["path"]
        duration_ns = log["event"]["duration"]
        response_time_ms = duration_ns / 1_000_000
        status_code = log["http"]["response"]["status_code"]
        timestamp = parse_timestamp(log["@timestamp"])

        endpoint_times[endpoint].append(response_time_ms)
        endpoint_status_codes[endpoint][status_code] += 1
        hourly_response_times[timestamp.hour].append(response_time_ms)

        # Detect spikes (response time > 1000ms)
        if response_time_ms > 1000:
            response_time_spikes.append({
                "timestamp": log["@timestamp"],
                "endpoint": endpoint,
                "response_time_ms": response_time_ms,
                "status_code": status_code,
            })

    # Calculate metrics per endpoint
    endpoint_metrics: dict[str, dict[str, Any]] = {}
    for endpoint, times in endpoint_times.items():
        endpoint_metrics[endpoint] = {
            "count": len(times),
            "avg_ms": round(statistics.mean(times), 2),
            "median_ms": round(statistics.median(times), 2),
            "p95_ms": round(calculate_percentile(times, 95), 2),
            "p99_ms": round(calculate_percentile(times, 99), 2),
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2),
            "std_dev_ms": round(statistics.stdev(times), 2) if len(times) > 1 else 0,
            "status_codes": dict(endpoint_status_codes[endpoint]),
        }

    # Identify slow endpoints (p95 > 500ms)
    slow_endpoints = [
        {"endpoint": ep, "p95_ms": metrics["p95_ms"], "avg_ms": metrics["avg_ms"]}
        for ep, metrics in endpoint_metrics.items()
        if metrics["p95_ms"] > 500
    ]

    # Hourly patterns
    hourly_metrics = {
        hour: {
            "avg_ms": round(statistics.mean(times), 2),
            "p95_ms": round(calculate_percentile(times, 95), 2),
            "request_count": len(times),
        }
        for hour, times in sorted(hourly_response_times.items())
    }

    return {
        "total_requests": len(http_logs),
        "endpoint_metrics": endpoint_metrics,
        "slow_endpoints": sorted(slow_endpoints, key=lambda x: x["p95_ms"], reverse=True),
        "response_time_spikes": response_time_spikes[:20],  # Top 20 spikes
        "hourly_patterns": hourly_metrics,
    }


def analyze_resource_utilization(logs: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze resource utilization metrics."""
    metric_logs = [log for log in logs if log.get("log_type") == "metrics"]

    host_metrics: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    hourly_cpu: dict[int, list[float]] = defaultdict(list)
    hourly_memory: dict[int, list[float]] = defaultdict(list)
    connection_pool_utilization: list[float] = []
    high_cpu_events: list[dict[str, Any]] = []
    high_memory_events: list[dict[str, Any]] = []
    connection_pool_warnings: list[dict[str, Any]] = []

    for log in metric_logs:
        host = log["host"]["name"]
        timestamp = parse_timestamp(log["@timestamp"])
        hour = timestamp.hour

        cpu_pct = log["system"]["cpu"]["total"]["pct"] * 100
        memory_pct = log["system"]["memory"]["actual"]["used"]["pct"] * 100
        disk_read = log["system"]["diskio"]["read"]["bytes_per_sec"] / (1024 * 1024)
        disk_write = log["system"]["diskio"]["write"]["bytes_per_sec"] / (1024 * 1024)
        pool_util = log["connection_pool"]["utilization_pct"]

        host_metrics[host]["cpu"].append(cpu_pct)
        host_metrics[host]["memory"].append(memory_pct)
        host_metrics[host]["disk_read_mbps"].append(disk_read)
        host_metrics[host]["disk_write_mbps"].append(disk_write)

        hourly_cpu[hour].append(cpu_pct)
        hourly_memory[hour].append(memory_pct)
        connection_pool_utilization.append(pool_util)

        # Detect high CPU (>80%)
        if cpu_pct > 80:
            high_cpu_events.append({
                "timestamp": log["@timestamp"],
                "host": host,
                "cpu_pct": round(cpu_pct, 2),
            })

        # Detect high memory (>85%)
        if memory_pct > 85:
            high_memory_events.append({
                "timestamp": log["@timestamp"],
                "host": host,
                "memory_pct": round(memory_pct, 2),
            })

        # Detect connection pool near exhaustion (>80%)
        if pool_util > 80:
            connection_pool_warnings.append({
                "timestamp": log["@timestamp"],
                "host": host,
                "utilization_pct": round(pool_util, 2),
            })

    # Calculate per-host metrics
    host_summary: dict[str, dict[str, Any]] = {}
    for host, metrics in host_metrics.items():
        host_summary[host] = {
            "cpu": {
                "avg_pct": round(statistics.mean(metrics["cpu"]), 2),
                "max_pct": round(max(metrics["cpu"]), 2),
                "p95_pct": round(calculate_percentile(metrics["cpu"], 95), 2),
            },
            "memory": {
                "avg_pct": round(statistics.mean(metrics["memory"]), 2),
                "max_pct": round(max(metrics["memory"]), 2),
                "p95_pct": round(calculate_percentile(metrics["memory"], 95), 2),
            },
            "disk_io": {
                "avg_read_mbps": round(statistics.mean(metrics["disk_read_mbps"]), 2),
                "avg_write_mbps": round(statistics.mean(metrics["disk_write_mbps"]), 2),
                "max_read_mbps": round(max(metrics["disk_read_mbps"]), 2),
                "max_write_mbps": round(max(metrics["disk_write_mbps"]), 2),
            },
        }

    # Hourly patterns
    hourly_resource_patterns = {
        hour: {
            "avg_cpu_pct": round(statistics.mean(hourly_cpu[hour]), 2),
            "avg_memory_pct": round(statistics.mean(hourly_memory[hour]), 2),
        }
        for hour in sorted(hourly_cpu.keys())
    }

    # Memory leak detection (check for consistent memory growth)
    memory_trend = []
    for log in sorted(metric_logs, key=lambda x: x["@timestamp"]):
        memory_trend.append(log["system"]["memory"]["actual"]["used"]["pct"] * 100)

    # Simple trend analysis: compare first quarter avg to last quarter avg
    quarter_size = len(memory_trend) // 4
    if quarter_size > 0:
        first_quarter_avg = statistics.mean(memory_trend[:quarter_size])
        last_quarter_avg = statistics.mean(memory_trend[-quarter_size:])
        memory_growth_pct = ((last_quarter_avg - first_quarter_avg) / first_quarter_avg) * 100
    else:
        memory_growth_pct = 0

    return {
        "total_metric_samples": len(metric_logs),
        "host_summary": host_summary,
        "hourly_patterns": hourly_resource_patterns,
        "connection_pool": {
            "avg_utilization_pct": round(statistics.mean(connection_pool_utilization), 2),
            "max_utilization_pct": round(max(connection_pool_utilization), 2),
            "p95_utilization_pct": round(calculate_percentile(connection_pool_utilization, 95), 2),
        },
        "high_cpu_events": high_cpu_events[:10],
        "high_memory_events": high_memory_events[:10],
        "connection_pool_warnings": connection_pool_warnings[:10],
        "memory_leak_analysis": {
            "memory_growth_pct": round(memory_growth_pct, 2),
            "potential_leak": memory_growth_pct > 10,
        },
    }


def analyze_database_performance(logs: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze database query performance."""
    db_logs = [log for log in logs if log.get("log_type") == "database"]

    query_times: dict[str, list[int]] = defaultdict(list)
    table_times: dict[str, list[int]] = defaultdict(list)
    slow_queries: list[dict[str, Any]] = []
    hourly_query_times: dict[int, list[int]] = defaultdict(list)
    connection_usage: dict[int, int] = defaultdict(int)

    for log in db_logs:
        query_type = log["database"]["query"]["type"]
        table = log["database"]["query"]["table"]
        exec_time = log["database"]["query"]["execution_time_ms"]
        is_slow = log["database"]["query"]["slow_query"]
        conn_id = log["database"]["connection"]["id"]
        timestamp = parse_timestamp(log["@timestamp"])

        query_times[query_type].append(exec_time)
        table_times[table].append(exec_time)
        hourly_query_times[timestamp.hour].append(exec_time)
        connection_usage[conn_id] += 1

        if is_slow:
            slow_queries.append({
                "timestamp": log["@timestamp"],
                "query_type": query_type,
                "table": table,
                "execution_time_ms": exec_time,
            })

    # Query type metrics
    query_type_metrics = {
        qtype: {
            "count": len(times),
            "avg_ms": round(statistics.mean(times), 2),
            "p95_ms": round(calculate_percentile(times, 95), 2),
            "p99_ms": round(calculate_percentile(times, 99), 2),
            "max_ms": max(times),
        }
        for qtype, times in query_times.items()
    }

    # Table metrics
    table_metrics = {
        table: {
            "count": len(times),
            "avg_ms": round(statistics.mean(times), 2),
            "p95_ms": round(calculate_percentile(times, 95), 2),
            "max_ms": max(times),
        }
        for table, times in table_times.items()
    }

    # Hourly patterns
    hourly_db_patterns = {
        hour: {
            "query_count": len(times),
            "avg_ms": round(statistics.mean(times), 2),
            "p95_ms": round(calculate_percentile(times, 95), 2),
        }
        for hour, times in sorted(hourly_query_times.items())
    }

    # Connection pool analysis
    active_connections = len(connection_usage)
    queries_per_connection = list(connection_usage.values())

    return {
        "total_queries": len(db_logs),
        "slow_query_count": len(slow_queries),
        "slow_query_percentage": round((len(slow_queries) / len(db_logs)) * 100, 2) if db_logs else 0,
        "query_type_metrics": query_type_metrics,
        "table_metrics": table_metrics,
        "hourly_patterns": hourly_db_patterns,
        "slow_queries": sorted(slow_queries, key=lambda x: x["execution_time_ms"], reverse=True)[:20],
        "connection_pool_analysis": {
            "unique_connections_used": active_connections,
            "avg_queries_per_connection": round(statistics.mean(queries_per_connection), 2),
            "max_queries_per_connection": max(queries_per_connection),
        },
    }


def analyze_service_health(logs: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze service health and availability."""
    health_logs = [log for log in logs if log.get("log_type") == "service_health"]
    error_logs = [log for log in logs if log.get("log_type") == "error"]

    service_status: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    service_error_rates: dict[str, list[float]] = defaultdict(list)
    circuit_breaker_events: list[dict[str, Any]] = []
    degraded_events: list[dict[str, Any]] = []

    for log in health_logs:
        service = log["service"]["name"]
        status = log["service"]["status"]
        cb_state = log["service"]["circuit_breaker"]["state"]
        error_rate = log["service"]["metrics"]["error_rate_pct"]

        service_status[service][status] += 1
        service_error_rates[service].append(error_rate)

        if cb_state != "closed":
            circuit_breaker_events.append({
                "timestamp": log["@timestamp"],
                "service": service,
                "state": cb_state,
                "failure_count": log["service"]["circuit_breaker"]["failure_count"],
            })

        if status == "degraded":
            degraded_events.append({
                "timestamp": log["@timestamp"],
                "service": service,
                "error_rate_pct": error_rate,
            })

    # Calculate service availability
    service_availability: dict[str, dict[str, Any]] = {}
    for service, statuses in service_status.items():
        total = sum(statuses.values())
        healthy = statuses.get("healthy", 0)
        availability = (healthy / total) * 100 if total > 0 else 0
        service_availability[service] = {
            "availability_pct": round(availability, 2),
            "healthy_checks": healthy,
            "degraded_checks": statuses.get("degraded", 0),
            "total_checks": total,
            "avg_error_rate_pct": round(statistics.mean(service_error_rates[service]), 2),
            "max_error_rate_pct": round(max(service_error_rates[service]), 2),
        }

    # Error analysis
    error_by_type: dict[str, int] = defaultdict(int)
    error_by_service: dict[str, int] = defaultdict(int)
    for log in error_logs:
        error_type = log["error"]["type"]
        service = log["service"]["name"]
        error_by_type[error_type] += 1
        error_by_service[service] += 1

    return {
        "total_health_checks": len(health_logs),
        "total_errors": len(error_logs),
        "service_availability": service_availability,
        "circuit_breaker_events": circuit_breaker_events,
        "degraded_events": degraded_events,
        "error_distribution": {
            "by_type": dict(error_by_type),
            "by_service": dict(error_by_service),
        },
    }


def analyze_capacity_planning(
    logs: list[dict[str, Any]],
    response_analysis: dict[str, Any],
    resource_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Provide capacity planning insights."""
    http_logs = [log for log in logs if log.get("log_type") == "http"]

    # Identify peak load times
    hourly_requests: dict[int, int] = defaultdict(int)
    for log in http_logs:
        timestamp = parse_timestamp(log["@timestamp"])
        hourly_requests[timestamp.hour] += 1

    peak_hour = max(hourly_requests, key=hourly_requests.get) if hourly_requests else 0
    peak_requests = hourly_requests.get(peak_hour, 0)
    avg_requests = statistics.mean(hourly_requests.values()) if hourly_requests else 0

    # Resource headroom analysis
    host_summary = resource_analysis.get("host_summary", {})
    cpu_headroom = []
    memory_headroom = []
    for host, metrics in host_summary.items():
        cpu_headroom.append(100 - metrics["cpu"]["p95_pct"])
        memory_headroom.append(100 - metrics["memory"]["p95_pct"])

    avg_cpu_headroom = statistics.mean(cpu_headroom) if cpu_headroom else 0
    avg_memory_headroom = statistics.mean(memory_headroom) if memory_headroom else 0

    # Connection pool headroom
    pool_metrics = resource_analysis.get("connection_pool", {})
    pool_headroom = 100 - pool_metrics.get("p95_utilization_pct", 0)

    # Scaling recommendations
    scaling_recommendations = []

    if avg_cpu_headroom < 20:
        scaling_recommendations.append({
            "resource": "CPU",
            "current_headroom_pct": round(avg_cpu_headroom, 2),
            "recommendation": "Consider horizontal scaling or CPU upgrade",
            "priority": "high",
        })
    elif avg_cpu_headroom < 40:
        scaling_recommendations.append({
            "resource": "CPU",
            "current_headroom_pct": round(avg_cpu_headroom, 2),
            "recommendation": "Monitor CPU usage closely, plan for scaling",
            "priority": "medium",
        })

    if avg_memory_headroom < 15:
        scaling_recommendations.append({
            "resource": "Memory",
            "current_headroom_pct": round(avg_memory_headroom, 2),
            "recommendation": "Increase memory allocation or add instances",
            "priority": "high",
        })
    elif avg_memory_headroom < 30:
        scaling_recommendations.append({
            "resource": "Memory",
            "current_headroom_pct": round(avg_memory_headroom, 2),
            "recommendation": "Monitor memory usage, consider optimization",
            "priority": "medium",
        })

    if pool_headroom < 20:
        scaling_recommendations.append({
            "resource": "Connection Pool",
            "current_headroom_pct": round(pool_headroom, 2),
            "recommendation": "Increase connection pool size",
            "priority": "high",
        })

    # Traffic growth projection
    traffic_capacity = {
        "current_peak_rps": round(peak_requests / 60, 2),  # requests per second
        "estimated_max_rps": round((peak_requests / 60) * (1 + avg_cpu_headroom / 100), 2),
        "growth_capacity_pct": round(avg_cpu_headroom, 2),
    }

    return {
        "peak_load_analysis": {
            "peak_hour": peak_hour,
            "peak_requests_per_hour": peak_requests,
            "avg_requests_per_hour": round(avg_requests, 2),
            "peak_to_avg_ratio": round(peak_requests / avg_requests, 2) if avg_requests > 0 else 0,
        },
        "resource_headroom": {
            "cpu_headroom_pct": round(avg_cpu_headroom, 2),
            "memory_headroom_pct": round(avg_memory_headroom, 2),
            "connection_pool_headroom_pct": round(pool_headroom, 2),
        },
        "traffic_capacity": traffic_capacity,
        "scaling_recommendations": scaling_recommendations,
    }


def analyze_performance_trends(
    logs: list[dict[str, Any]],
    response_analysis: dict[str, Any],
    resource_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Identify performance trends and correlations."""
    http_logs = [log for log in logs if log.get("log_type") == "http"]
    metric_logs = [log for log in logs if log.get("log_type") == "metrics"]

    # Time-based response time trends
    hourly_response_times: dict[int, list[float]] = defaultdict(list)
    for log in http_logs:
        timestamp = parse_timestamp(log["@timestamp"])
        response_time_ms = log["event"]["duration"] / 1_000_000
        hourly_response_times[timestamp.hour].append(response_time_ms)

    # Calculate hourly averages
    hourly_avg_response: dict[int, float] = {
        hour: statistics.mean(times)
        for hour, times in hourly_response_times.items()
    }

    # Identify degradation patterns
    degradation_hours = []
    baseline_avg = statistics.mean(hourly_avg_response.values()) if hourly_avg_response else 0
    for hour, avg in hourly_avg_response.items():
        if avg > baseline_avg * 1.5:  # 50% above baseline
            degradation_hours.append({
                "hour": hour,
                "avg_response_ms": round(avg, 2),
                "baseline_ms": round(baseline_avg, 2),
                "degradation_pct": round(((avg - baseline_avg) / baseline_avg) * 100, 2),
            })

    # CPU-Response time correlation
    hourly_cpu: dict[int, list[float]] = defaultdict(list)
    for log in metric_logs:
        timestamp = parse_timestamp(log["@timestamp"])
        cpu_pct = log["system"]["cpu"]["total"]["pct"] * 100
        hourly_cpu[timestamp.hour].append(cpu_pct)

    hourly_avg_cpu = {
        hour: statistics.mean(values)
        for hour, values in hourly_cpu.items()
    }

    # Simple correlation analysis
    correlation_data = []
    for hour in sorted(set(hourly_avg_response.keys()) & set(hourly_avg_cpu.keys())):
        correlation_data.append({
            "hour": hour,
            "avg_response_ms": round(hourly_avg_response[hour], 2),
            "avg_cpu_pct": round(hourly_avg_cpu[hour], 2),
        })

    # Seasonal patterns (business hours vs off-hours)
    business_hours = [h for h in range(9, 18)]
    off_hours = [h for h in range(24) if h not in business_hours]

    business_hour_response = [
        hourly_avg_response[h] for h in business_hours if h in hourly_avg_response
    ]
    off_hour_response = [
        hourly_avg_response[h] for h in off_hours if h in hourly_avg_response
    ]

    seasonal_patterns = {
        "business_hours_avg_ms": round(statistics.mean(business_hour_response), 2) if business_hour_response else 0,
        "off_hours_avg_ms": round(statistics.mean(off_hour_response), 2) if off_hour_response else 0,
        "business_hours_impact_pct": 0,
    }

    if off_hour_response and business_hour_response:
        off_avg = statistics.mean(off_hour_response)
        bus_avg = statistics.mean(business_hour_response)
        if off_avg > 0:
            seasonal_patterns["business_hours_impact_pct"] = round(
                ((bus_avg - off_avg) / off_avg) * 100, 2
            )

    return {
        "hourly_response_trend": {
            hour: round(avg, 2) for hour, avg in sorted(hourly_avg_response.items())
        },
        "degradation_patterns": degradation_hours,
        "cpu_response_correlation": correlation_data,
        "seasonal_patterns": seasonal_patterns,
        "baseline_metrics": {
            "avg_response_ms": round(baseline_avg, 2),
            "response_std_dev_ms": round(
                statistics.stdev(list(hourly_avg_response.values())), 2
            ) if len(hourly_avg_response) > 1 else 0,
        },
    }


def generate_alerting_thresholds(
    response_analysis: dict[str, Any],
    resource_analysis: dict[str, Any],
    db_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Generate recommended alerting thresholds based on analysis."""
    # Response time thresholds
    all_p95 = [
        metrics["p95_ms"]
        for metrics in response_analysis.get("endpoint_metrics", {}).values()
    ]
    avg_p95 = statistics.mean(all_p95) if all_p95 else 500

    # Resource thresholds
    host_summary = resource_analysis.get("host_summary", {})
    cpu_p95_values = [h["cpu"]["p95_pct"] for h in host_summary.values()]
    memory_p95_values = [h["memory"]["p95_pct"] for h in host_summary.values()]

    avg_cpu_p95 = statistics.mean(cpu_p95_values) if cpu_p95_values else 70
    avg_memory_p95 = statistics.mean(memory_p95_values) if memory_p95_values else 75

    # Database thresholds
    db_metrics = db_analysis.get("query_type_metrics", {})
    db_p95_values = [m["p95_ms"] for m in db_metrics.values()]
    avg_db_p95 = statistics.mean(db_p95_values) if db_p95_values else 100

    return {
        "response_time": {
            "warning_ms": round(avg_p95 * 1.5, 0),
            "critical_ms": round(avg_p95 * 2.5, 0),
            "baseline_p95_ms": round(avg_p95, 2),
        },
        "cpu_utilization": {
            "warning_pct": min(round(avg_cpu_p95 + 15, 0), 85),
            "critical_pct": min(round(avg_cpu_p95 + 25, 0), 95),
            "baseline_p95_pct": round(avg_cpu_p95, 2),
        },
        "memory_utilization": {
            "warning_pct": min(round(avg_memory_p95 + 10, 0), 85),
            "critical_pct": min(round(avg_memory_p95 + 15, 0), 95),
            "baseline_p95_pct": round(avg_memory_p95, 2),
        },
        "database_query_time": {
            "warning_ms": round(avg_db_p95 * 3, 0),
            "critical_ms": round(avg_db_p95 * 10, 0),
            "baseline_p95_ms": round(avg_db_p95, 2),
        },
        "error_rate": {
            "warning_pct": 2.0,
            "critical_pct": 5.0,
        },
        "connection_pool": {
            "warning_pct": 75,
            "critical_pct": 90,
        },
    }


def generate_executive_summary(
    response_analysis: dict[str, Any],
    resource_analysis: dict[str, Any],
    db_analysis: dict[str, Any],
    health_analysis: dict[str, Any],
    capacity_analysis: dict[str, Any],
    trends_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Generate executive summary of system performance."""
    # Overall health score (0-100)
    health_factors = []

    # Response time health (based on p95)
    slow_endpoints = response_analysis.get("slow_endpoints", [])
    response_health = max(0, 100 - len(slow_endpoints) * 10)
    health_factors.append(response_health)

    # Resource health
    resource_headroom = capacity_analysis.get("resource_headroom", {})
    cpu_headroom = resource_headroom.get("cpu_headroom_pct", 50)
    memory_headroom = resource_headroom.get("memory_headroom_pct", 50)
    resource_health = min(100, (cpu_headroom + memory_headroom))
    health_factors.append(resource_health)

    # Database health
    slow_query_pct = db_analysis.get("slow_query_percentage", 0)
    db_health = max(0, 100 - slow_query_pct * 10)
    health_factors.append(db_health)

    # Service health
    service_availability = health_analysis.get("service_availability", {})
    avg_availability = statistics.mean(
        [s["availability_pct"] for s in service_availability.values()]
    ) if service_availability else 100
    service_health = avg_availability
    health_factors.append(service_health)

    overall_health = statistics.mean(health_factors)

    # Key findings
    key_findings = []

    if slow_endpoints:
        key_findings.append(
            f"{len(slow_endpoints)} endpoint(s) have p95 response times exceeding 500ms"
        )

    if resource_analysis.get("memory_leak_analysis", {}).get("potential_leak"):
        key_findings.append("Potential memory leak detected - memory usage trending upward")

    if db_analysis.get("slow_query_percentage", 0) > 5:
        key_findings.append(
            f"High slow query rate: {db_analysis['slow_query_percentage']}% of queries are slow"
        )

    if health_analysis.get("circuit_breaker_events"):
        key_findings.append(
            f"{len(health_analysis['circuit_breaker_events'])} circuit breaker events detected"
        )

    if not key_findings:
        key_findings.append("System is operating within healthy parameters")

    # Performance grade
    if overall_health >= 90:
        grade = "A"
        status = "Excellent"
    elif overall_health >= 80:
        grade = "B"
        status = "Good"
    elif overall_health >= 70:
        grade = "C"
        status = "Fair"
    elif overall_health >= 60:
        grade = "D"
        status = "Needs Attention"
    else:
        grade = "F"
        status = "Critical"

    return {
        "overall_health_score": round(overall_health, 1),
        "performance_grade": grade,
        "status": status,
        "component_scores": {
            "response_time": round(response_health, 1),
            "resource_utilization": round(resource_health, 1),
            "database_performance": round(db_health, 1),
            "service_availability": round(service_health, 1),
        },
        "key_findings": key_findings,
        "total_requests_analyzed": response_analysis.get("total_requests", 0),
        "analysis_period": "24 hours",
    }


def generate_optimization_recommendations(
    response_analysis: dict[str, Any],
    resource_analysis: dict[str, Any],
    db_analysis: dict[str, Any],
    capacity_analysis: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate prioritized optimization recommendations."""
    recommendations = []

    # Response time optimizations
    slow_endpoints = response_analysis.get("slow_endpoints", [])
    for endpoint in slow_endpoints[:3]:  # Top 3 slow endpoints
        recommendations.append({
            "category": "Response Time",
            "priority": "high" if endpoint["p95_ms"] > 1000 else "medium",
            "issue": f"Endpoint {endpoint['endpoint']} has high p95 latency ({endpoint['p95_ms']}ms)",
            "recommendation": "Profile endpoint, optimize database queries, consider caching",
            "expected_impact": "Reduce response time by 30-50%",
        })

    # Database optimizations
    slow_query_pct = db_analysis.get("slow_query_percentage", 0)
    if slow_query_pct > 3:
        recommendations.append({
            "category": "Database",
            "priority": "high",
            "issue": f"{slow_query_pct}% of queries are slow",
            "recommendation": "Add indexes, optimize query patterns, consider query caching",
            "expected_impact": "Reduce slow query rate to <1%",
        })

    # Slow tables
    table_metrics = db_analysis.get("table_metrics", {})
    for table, metrics in table_metrics.items():
        if metrics["p95_ms"] > 100:
            recommendations.append({
                "category": "Database",
                "priority": "medium",
                "issue": f"Table '{table}' has high query latency (p95: {metrics['p95_ms']}ms)",
                "recommendation": f"Review indexes on {table}, consider partitioning if large",
                "expected_impact": "Reduce query time by 40-60%",
            })

    # Resource optimizations
    memory_leak = resource_analysis.get("memory_leak_analysis", {})
    if memory_leak.get("potential_leak"):
        recommendations.append({
            "category": "Memory",
            "priority": "high",
            "issue": f"Memory usage growing by {memory_leak['memory_growth_pct']}% over analysis period",
            "recommendation": "Profile memory usage, check for object leaks, review caching strategy",
            "expected_impact": "Stabilize memory usage, prevent OOM errors",
        })

    # Connection pool
    pool_metrics = resource_analysis.get("connection_pool", {})
    if pool_metrics.get("p95_utilization_pct", 0) > 70:
        recommendations.append({
            "category": "Connection Pool",
            "priority": "medium",
            "issue": f"Connection pool utilization at {pool_metrics['p95_utilization_pct']}% (p95)",
            "recommendation": "Increase pool size, optimize connection usage, implement connection recycling",
            "expected_impact": "Reduce connection wait times, prevent pool exhaustion",
        })

    # Capacity recommendations
    scaling_recs = capacity_analysis.get("scaling_recommendations", [])
    for rec in scaling_recs:
        recommendations.append({
            "category": "Capacity",
            "priority": rec["priority"],
            "issue": f"{rec['resource']} headroom at {rec['current_headroom_pct']}%",
            "recommendation": rec["recommendation"],
            "expected_impact": "Ensure system can handle traffic growth",
        })

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 2))

    return recommendations


def format_report(analysis_results: dict[str, Any]) -> str:
    """Format the analysis results into a readable report."""
    report_lines = []

    report_lines.append("=" * 80)
    report_lines.append("ELASTIC LOG PERFORMANCE ANALYSIS REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report_lines.append(f"Log File: logs/sample_20_healthy_system.json")
    report_lines.append("")

    # Executive Summary
    summary = analysis_results["executive_summary"]
    report_lines.append("-" * 80)
    report_lines.append("EXECUTIVE SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append(f"Overall Health Score: {summary['overall_health_score']}/100 ({summary['performance_grade']} - {summary['status']})")
    report_lines.append(f"Analysis Period: {summary['analysis_period']}")
    report_lines.append(f"Total Requests Analyzed: {summary['total_requests_analyzed']:,}")
    report_lines.append("")
    report_lines.append("Component Scores:")
    for component, score in summary["component_scores"].items():
        report_lines.append(f"  - {component.replace('_', ' ').title()}: {score}/100")
    report_lines.append("")
    report_lines.append("Key Findings:")
    for finding in summary["key_findings"]:
        report_lines.append(f"  * {finding}")
    report_lines.append("")

    # Response Time Analysis
    response = analysis_results["response_time_analysis"]
    report_lines.append("-" * 80)
    report_lines.append("1. RESPONSE TIME ANALYSIS")
    report_lines.append("-" * 80)
    report_lines.append(f"Total HTTP Requests: {response['total_requests']:,}")
    report_lines.append("")
    report_lines.append("Endpoint Performance Metrics:")
    report_lines.append(f"{'Endpoint':<40} {'Count':>8} {'Avg(ms)':>10} {'P95(ms)':>10} {'P99(ms)':>10}")
    report_lines.append("-" * 80)
    for endpoint, metrics in sorted(response["endpoint_metrics"].items(), key=lambda x: x[1]["p95_ms"], reverse=True):
        report_lines.append(f"{endpoint:<40} {metrics['count']:>8} {metrics['avg_ms']:>10.1f} {metrics['p95_ms']:>10.1f} {metrics['p99_ms']:>10.1f}")
    report_lines.append("")

    if response["slow_endpoints"]:
        report_lines.append("Slow Endpoints (p95 > 500ms):")
        for ep in response["slow_endpoints"]:
            report_lines.append(f"  - {ep['endpoint']}: p95={ep['p95_ms']}ms, avg={ep['avg_ms']}ms")
    report_lines.append("")

    if response["response_time_spikes"]:
        report_lines.append(f"Response Time Spikes Detected: {len(response['response_time_spikes'])}")
        report_lines.append("Top 5 Spikes:")
        for spike in sorted(response["response_time_spikes"], key=lambda x: x["response_time_ms"], reverse=True)[:5]:
            report_lines.append(f"  - {spike['timestamp']}: {spike['endpoint']} - {spike['response_time_ms']}ms")
    report_lines.append("")

    # Resource Utilization
    resource = analysis_results["resource_utilization_analysis"]
    report_lines.append("-" * 80)
    report_lines.append("2. RESOURCE UTILIZATION ANALYSIS")
    report_lines.append("-" * 80)
    report_lines.append(f"Total Metric Samples: {resource['total_metric_samples']:,}")
    report_lines.append("")
    report_lines.append("Host Resource Summary:")
    for host, metrics in resource["host_summary"].items():
        report_lines.append(f"  {host}:")
        report_lines.append(f"    CPU: avg={metrics['cpu']['avg_pct']:.1f}%, p95={metrics['cpu']['p95_pct']:.1f}%, max={metrics['cpu']['max_pct']:.1f}%")
        report_lines.append(f"    Memory: avg={metrics['memory']['avg_pct']:.1f}%, p95={metrics['memory']['p95_pct']:.1f}%, max={metrics['memory']['max_pct']:.1f}%")
        report_lines.append(f"    Disk I/O: read={metrics['disk_io']['avg_read_mbps']:.1f}MB/s, write={metrics['disk_io']['avg_write_mbps']:.1f}MB/s")
    report_lines.append("")

    pool = resource["connection_pool"]
    report_lines.append(f"Connection Pool: avg={pool['avg_utilization_pct']:.1f}%, p95={pool['p95_utilization_pct']:.1f}%, max={pool['max_utilization_pct']:.1f}%")
    report_lines.append("")

    memory_leak = resource["memory_leak_analysis"]
    report_lines.append(f"Memory Trend: {memory_leak['memory_growth_pct']:.1f}% growth over period")
    report_lines.append(f"Potential Memory Leak: {'Yes - INVESTIGATE' if memory_leak['potential_leak'] else 'No'}")
    report_lines.append("")

    if resource["high_cpu_events"]:
        report_lines.append(f"High CPU Events (>80%): {len(resource['high_cpu_events'])}")
    if resource["high_memory_events"]:
        report_lines.append(f"High Memory Events (>85%): {len(resource['high_memory_events'])}")
    if resource["connection_pool_warnings"]:
        report_lines.append(f"Connection Pool Warnings (>80%): {len(resource['connection_pool_warnings'])}")
    report_lines.append("")

    # Database Performance
    db = analysis_results["database_performance_analysis"]
    report_lines.append("-" * 80)
    report_lines.append("3. DATABASE PERFORMANCE ANALYSIS")
    report_lines.append("-" * 80)
    report_lines.append(f"Total Queries: {db['total_queries']:,}")
    report_lines.append(f"Slow Queries: {db['slow_query_count']} ({db['slow_query_percentage']:.2f}%)")
    report_lines.append("")
    report_lines.append("Query Type Performance:")
    report_lines.append(f"{'Type':<12} {'Count':>10} {'Avg(ms)':>10} {'P95(ms)':>10} {'P99(ms)':>10}")
    report_lines.append("-" * 55)
    for qtype, metrics in db["query_type_metrics"].items():
        report_lines.append(f"{qtype:<12} {metrics['count']:>10} {metrics['avg_ms']:>10.1f} {metrics['p95_ms']:>10.1f} {metrics['p99_ms']:>10.1f}")
    report_lines.append("")

    report_lines.append("Table Performance:")
    report_lines.append(f"{'Table':<15} {'Count':>10} {'Avg(ms)':>10} {'P95(ms)':>10}")
    report_lines.append("-" * 50)
    for table, metrics in sorted(db["table_metrics"].items(), key=lambda x: x[1]["p95_ms"], reverse=True):
        report_lines.append(f"{table:<15} {metrics['count']:>10} {metrics['avg_ms']:>10.1f} {metrics['p95_ms']:>10.1f}")
    report_lines.append("")

    conn_pool = db["connection_pool_analysis"]
    report_lines.append(f"Connection Pool: {conn_pool['unique_connections_used']} unique connections, avg {conn_pool['avg_queries_per_connection']:.1f} queries/connection")
    report_lines.append("")

    # Service Health
    health = analysis_results["service_health_analysis"]
    report_lines.append("-" * 80)
    report_lines.append("4. SERVICE HEALTH ANALYSIS")
    report_lines.append("-" * 80)
    report_lines.append(f"Total Health Checks: {health['total_health_checks']:,}")
    report_lines.append(f"Total Errors: {health['total_errors']}")
    report_lines.append("")
    report_lines.append("Service Availability:")
    report_lines.append(f"{'Service':<25} {'Availability':>12} {'Healthy':>10} {'Degraded':>10} {'Avg Error%':>12}")
    report_lines.append("-" * 75)
    for service, metrics in health["service_availability"].items():
        report_lines.append(f"{service:<25} {metrics['availability_pct']:>11.2f}% {metrics['healthy_checks']:>10} {metrics['degraded_checks']:>10} {metrics['avg_error_rate_pct']:>11.2f}%")
    report_lines.append("")

    if health["circuit_breaker_events"]:
        report_lines.append(f"Circuit Breaker Events: {len(health['circuit_breaker_events'])}")
        for event in health["circuit_breaker_events"][:5]:
            report_lines.append(f"  - {event['timestamp']}: {event['service']} - {event['state']}")
    report_lines.append("")

    if health["error_distribution"]["by_type"]:
        report_lines.append("Error Distribution by Type:")
        for error_type, count in health["error_distribution"]["by_type"].items():
            report_lines.append(f"  - {error_type}: {count}")
    report_lines.append("")

    # Capacity Planning
    capacity = analysis_results["capacity_planning_insights"]
    report_lines.append("-" * 80)
    report_lines.append("5. CAPACITY PLANNING INSIGHTS")
    report_lines.append("-" * 80)
    peak = capacity["peak_load_analysis"]
    report_lines.append(f"Peak Hour: {peak['peak_hour']}:00 ({peak['peak_requests_per_hour']:,} requests)")
    report_lines.append(f"Average Requests/Hour: {peak['avg_requests_per_hour']:,.0f}")
    report_lines.append(f"Peak-to-Average Ratio: {peak['peak_to_avg_ratio']:.2f}x")
    report_lines.append("")

    headroom = capacity["resource_headroom"]
    report_lines.append("Resource Headroom:")
    report_lines.append(f"  - CPU: {headroom['cpu_headroom_pct']:.1f}%")
    report_lines.append(f"  - Memory: {headroom['memory_headroom_pct']:.1f}%")
    report_lines.append(f"  - Connection Pool: {headroom['connection_pool_headroom_pct']:.1f}%")
    report_lines.append("")

    traffic = capacity["traffic_capacity"]
    report_lines.append("Traffic Capacity:")
    report_lines.append(f"  - Current Peak: {traffic['current_peak_rps']:.1f} req/sec")
    report_lines.append(f"  - Estimated Max: {traffic['estimated_max_rps']:.1f} req/sec")
    report_lines.append(f"  - Growth Capacity: {traffic['growth_capacity_pct']:.1f}%")
    report_lines.append("")

    if capacity["scaling_recommendations"]:
        report_lines.append("Scaling Recommendations:")
        for rec in capacity["scaling_recommendations"]:
            report_lines.append(f"  [{rec['priority'].upper()}] {rec['resource']}: {rec['recommendation']}")
    report_lines.append("")

    # Performance Trends
    trends = analysis_results["performance_trends_analysis"]
    report_lines.append("-" * 80)
    report_lines.append("6. PERFORMANCE TRENDS ANALYSIS")
    report_lines.append("-" * 80)
    baseline = trends["baseline_metrics"]
    report_lines.append(f"Baseline Response Time: {baseline['avg_response_ms']:.1f}ms (std dev: {baseline['response_std_dev_ms']:.1f}ms)")
    report_lines.append("")

    seasonal = trends["seasonal_patterns"]
    report_lines.append("Seasonal Patterns:")
    report_lines.append(f"  - Business Hours (9-18): {seasonal['business_hours_avg_ms']:.1f}ms avg")
    report_lines.append(f"  - Off Hours: {seasonal['off_hours_avg_ms']:.1f}ms avg")
    report_lines.append(f"  - Business Hours Impact: {seasonal['business_hours_impact_pct']:.1f}% increase")
    report_lines.append("")

    if trends["degradation_patterns"]:
        report_lines.append("Degradation Patterns Detected:")
        for pattern in trends["degradation_patterns"]:
            report_lines.append(f"  - Hour {pattern['hour']}: {pattern['degradation_pct']:.1f}% above baseline ({pattern['avg_response_ms']:.1f}ms)")
    report_lines.append("")

    # Alerting Thresholds
    thresholds = analysis_results["alerting_thresholds"]
    report_lines.append("-" * 80)
    report_lines.append("7. RECOMMENDED ALERTING THRESHOLDS")
    report_lines.append("-" * 80)
    report_lines.append(f"{'Metric':<25} {'Warning':>15} {'Critical':>15} {'Baseline':>15}")
    report_lines.append("-" * 75)

    rt = thresholds["response_time"]
    report_lines.append(f"{'Response Time (ms)':<25} {rt['warning_ms']:>15.0f} {rt['critical_ms']:>15.0f} {rt['baseline_p95_ms']:>15.1f}")

    cpu = thresholds["cpu_utilization"]
    report_lines.append(f"{'CPU Utilization (%)':<25} {cpu['warning_pct']:>15.0f} {cpu['critical_pct']:>15.0f} {cpu['baseline_p95_pct']:>15.1f}")

    mem = thresholds["memory_utilization"]
    report_lines.append(f"{'Memory Utilization (%)':<25} {mem['warning_pct']:>15.0f} {mem['critical_pct']:>15.0f} {mem['baseline_p95_pct']:>15.1f}")

    dbq = thresholds["database_query_time"]
    report_lines.append(f"{'DB Query Time (ms)':<25} {dbq['warning_ms']:>15.0f} {dbq['critical_ms']:>15.0f} {dbq['baseline_p95_ms']:>15.1f}")

    err = thresholds["error_rate"]
    report_lines.append(f"{'Error Rate (%)':<25} {err['warning_pct']:>15.1f} {err['critical_pct']:>15.1f} {'N/A':>15}")

    pool = thresholds["connection_pool"]
    report_lines.append(f"{'Connection Pool (%)':<25} {pool['warning_pct']:>15.0f} {pool['critical_pct']:>15.0f} {'N/A':>15}")
    report_lines.append("")

    # Optimization Recommendations
    recommendations = analysis_results["optimization_recommendations"]
    report_lines.append("-" * 80)
    report_lines.append("8. PRIORITIZED OPTIMIZATION RECOMMENDATIONS")
    report_lines.append("-" * 80)
    for i, rec in enumerate(recommendations, 1):
        report_lines.append(f"{i}. [{rec['priority'].upper()}] {rec['category']}")
        report_lines.append(f"   Issue: {rec['issue']}")
        report_lines.append(f"   Recommendation: {rec['recommendation']}")
        report_lines.append(f"   Expected Impact: {rec['expected_impact']}")
        report_lines.append("")

    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)

    return "\n".join(report_lines)


def main() -> None:
    """Main function to run the analysis."""
    log_file = "/home/ubuntu/repos/devin-workshop/logs/sample_20_healthy_system.json"
    output_dir = Path("/home/ubuntu/repos/devin-workshop/analysis")
    output_dir.mkdir(exist_ok=True)

    print("Loading log data...")
    logs = load_logs(log_file)
    print(f"Loaded {len(logs):,} log entries")

    print("\nPerforming Response Time Analysis...")
    response_analysis = analyze_response_times(logs)

    print("Performing Resource Utilization Analysis...")
    resource_analysis = analyze_resource_utilization(logs)

    print("Performing Database Performance Analysis...")
    db_analysis = analyze_database_performance(logs)

    print("Performing Service Health Analysis...")
    health_analysis = analyze_service_health(logs)

    print("Performing Capacity Planning Analysis...")
    capacity_analysis = analyze_capacity_planning(logs, response_analysis, resource_analysis)

    print("Performing Performance Trends Analysis...")
    trends_analysis = analyze_performance_trends(logs, response_analysis, resource_analysis)

    print("Generating Alerting Thresholds...")
    alerting_thresholds = generate_alerting_thresholds(
        response_analysis, resource_analysis, db_analysis
    )

    print("Generating Executive Summary...")
    executive_summary = generate_executive_summary(
        response_analysis, resource_analysis, db_analysis,
        health_analysis, capacity_analysis, trends_analysis
    )

    print("Generating Optimization Recommendations...")
    optimization_recommendations = generate_optimization_recommendations(
        response_analysis, resource_analysis, db_analysis, capacity_analysis
    )

    # Compile all results
    analysis_results = {
        "executive_summary": executive_summary,
        "response_time_analysis": response_analysis,
        "resource_utilization_analysis": resource_analysis,
        "database_performance_analysis": db_analysis,
        "service_health_analysis": health_analysis,
        "capacity_planning_insights": capacity_analysis,
        "performance_trends_analysis": trends_analysis,
        "alerting_thresholds": alerting_thresholds,
        "optimization_recommendations": optimization_recommendations,
    }

    # Save JSON results
    json_output = output_dir / "performance_analysis_results.json"
    with open(json_output, "w") as f:
        json.dump(analysis_results, f, indent=2)
    print(f"\nJSON results saved to: {json_output}")

    # Generate and save text report
    report = format_report(analysis_results)
    report_output = output_dir / "performance_analysis_report.txt"
    with open(report_output, "w") as f:
        f.write(report)
    print(f"Text report saved to: {report_output}")

    # Print summary
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Overall Health Score: {executive_summary['overall_health_score']}/100")
    print(f"Performance Grade: {executive_summary['performance_grade']} ({executive_summary['status']})")
    print(f"\nKey Findings:")
    for finding in executive_summary["key_findings"]:
        print(f"  - {finding}")


if __name__ == "__main__":
    main()
