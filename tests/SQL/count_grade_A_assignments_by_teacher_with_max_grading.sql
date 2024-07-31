-- Write query to find the number of grade A's given by the teacher who has graded the most assignments
SELECT teacher_id, COUNT(*) as grade_A_count
FROM assignments
WHERE grade = 'A'
GROUP BY teacher_id
ORDER BY grade_A_count DESC
LIMIT 1;
