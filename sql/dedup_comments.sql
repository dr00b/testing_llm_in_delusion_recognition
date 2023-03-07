DELETE FROM comments
WHERE rowid NOT IN (
  SELECT MIN(rowid) 
  FROM comments
  GROUP BY comment_id
)