UPDATE comments
SET to_classify = CASE WHEN ROWID IN (SELECT comment_rowid FROM annotated) THEN 1 ELSE NULL END