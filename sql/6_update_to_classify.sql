-- Classify anything that has been annotated
UPDATE comments
SET to_classify = CASE WHEN ROWID IN (SELECT comment_rowid FROM annotated) THEN 1 ELSE NULL END

-- Flag 1500 random KI narratives as to_classify
UPDATE comments
SET to_classify = 1
WHERE ROWID IN (
SELECT ki.comment_rowid FROM knowledgeable_informant_narratives ki
INNER JOIN comments c
ON ki.comment_rowid = c.ROWID
AND c.is_deleted = 0
ORDER BY RANDOM()
LIMIT 1500
)