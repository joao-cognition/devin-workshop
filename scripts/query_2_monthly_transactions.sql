-- Monthly Transaction Volume by Category
-- Shows transaction count and total amount per category per month

SELECT 
    strftime('%Y-%m', transaction_date) AS month,
    category,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS avg_amount
FROM transactions
GROUP BY month, category
ORDER BY month DESC, total_amount DESC;
