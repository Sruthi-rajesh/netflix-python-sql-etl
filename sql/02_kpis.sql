-- 1) Total rows in each table
SELECT 'users' AS table_name, COUNT(*) AS rows FROM users
UNION ALL
SELECT 'titles', COUNT(*) FROM titles
UNION ALL
SELECT 'views', COUNT(*) FROM views;

-- 2) Completion rate overall
SELECT ROUND(AVG(completed) * 100, 2) AS completion_rate_pct
FROM views;

-- 3) Watch minutes by plan type
SELECT
  u.plan_type,
  SUM(v.watch_minutes) AS total_watch_minutes,
  ROUND(AVG(v.watch_minutes), 2) AS avg_watch_minutes
FROM views v
JOIN users u ON v.user_id = u.user_id
GROUP BY u.plan_type
ORDER BY total_watch_minutes DESC;

-- 4) Top genres by watch minutes
SELECT
  t.genre,
  SUM(v.watch_minutes) AS total_watch_minutes
FROM views v
JOIN titles t ON v.title_id = t.title_id
GROUP BY t.genre
ORDER BY total_watch_minutes DESC
LIMIT 10;

-- 5) Country-level engagement
SELECT
  u.country,
  COUNT(*) AS sessions,
  SUM(v.watch_minutes) AS total_watch_minutes,
  ROUND(AVG(v.watch_minutes), 2) AS avg_watch_minutes
FROM views v
JOIN users u ON v.user_id = u.user_id
GROUP BY u.country
ORDER BY total_watch_minutes DESC;

