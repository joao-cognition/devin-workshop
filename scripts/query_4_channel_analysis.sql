-- Average Transaction Amount by Channel
-- Shows average, min, max, and total amounts for each transaction channel

SELECT 
    channel,
    COUNT(*) AS transaction_count,
    ROUND(AVG(amount), 2) AS avg_amount,
    ROUND(MIN(amount), 2) AS min_amount,
    ROUND(MAX(amount), 2) AS max_amount,
    ROUND(SUM(amount), 2) AS total_amount
FROM transactions
GROUP BY channel
ORDER BY avg_amount DESC;
