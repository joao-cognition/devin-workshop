-- Customer Demographics by Segment
-- Shows count, average age, and average balance for each customer segment

SELECT 
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(age), 1) AS avg_age,
    ROUND(AVG(balance), 2) AS avg_balance,
    ROUND(MIN(balance), 2) AS min_balance,
    ROUND(MAX(balance), 2) AS max_balance
FROM customers
GROUP BY customer_segment
ORDER BY customer_count DESC;
