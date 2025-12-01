-- Top 10 Customers by Transaction Count
-- Shows customers with the most transactions, including their details

SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.city,
    c.customer_segment,
    c.balance AS account_balance,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_transaction_amount,
    ROUND(AVG(t.amount), 2) AS avg_transaction_amount
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, customer_name, c.city, c.customer_segment, c.balance
ORDER BY transaction_count DESC
LIMIT 10;
