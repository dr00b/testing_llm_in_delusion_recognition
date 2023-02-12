SELECT 

	video_id, COUNT(1) AS cnt

	--min_len = MIN(LENGTH(comment_text), 

	--max_len = MAX(LENGTH(comment_text),

FROM comments

GROUP BY video_id

),



pct AS (

SELECT

	video_id,

	PERCENT_RANK()

    OVER (ORDER BY cnt ASC) AS pct,

	cnt

FROM grouped

ORDER BY cnt DESC

)

SELECT ROUND(pct, 1), pct, AVG(cnt) FROM pct

WHERE ROUND(pct, 1) IN (0, 0.2, 0.4, 0.6, 0.8, 1.0)

GROUP BY ROUND(pct, 1)
