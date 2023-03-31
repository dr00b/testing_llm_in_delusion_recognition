-- Flag batch 1 for annotation
UPDATE comments
SET to_classify = CASE WHEN ROWID IN (SELECT comment_rowid FROM annotated) THEN 1 ELSE NULL END

-- Flag batch 2 for davinci classification
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