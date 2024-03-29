-- This step should ahve occured first, prior to annotation
ALTER TABLE comments ADD COLUMN is_deleted bool;

UPDATE comments
SET is_deleted = 0;

UPDATE comments
SET is_deleted = 1
WHERE ROWID NOT IN (
-- preserve the first row
SELECT MIN(ROWID) AS rid FROM comments
GROUP BY comment_text
HAVING COUNT(1) > 1
-- set the rest to is_deleted
) AND comment_text IN (
SELECT comment_text FROM comments
GROUP BY comment_text
HAVING COUNT(1) > 1
)

-- Do this the clean way, up front... I made the mistake of doing it after doing some annotation...
-- SELECT comment_rowid FROM annotated
-- WHERE comment_rowid IN (
-- SELECT ROWID FROM comments WHERE comment_text IN (
-- SELECT comment_text FROM comments -- MIN(ROWID) AS min_rowid, COUNT(1) 
-- GROUP BY comment_text
-- HAVING COUNT(1) > 1
-- )
-- );

-- -- keep the row id from annotated dataset, 17 rows affected
-- UPDATE comments
-- SET is_deleted = 0
-- WHERE ROWID IN (
-- SELECT comment_rowid FROM annotated
-- WHERE comment_rowid IN (
-- SELECT ROWID FROM comments WHERE comment_text IN (
-- SELECT comment_text FROM comments -- MIN(ROWID) AS min_rowid, COUNT(1) 
-- GROUP BY comment_text
-- HAVING COUNT(1) > 1))

-- -- keep the min row id for dup comments, not already annotated
-- -- 14834 rows affected
-- UPDATE comments
-- SET is_deleted = 0
-- WHERE ROWID IN (
-- SELECT MIN(ROWID) AS c_rid
-- FROM comments 
-- GROUP BY comment_text
-- HAVING COUNT(1) > 1
-- ) AND ROWID NOT IN (
-- SELECT comment_rowid FROM annotated
-- WHERE comment_rowid IN (
-- SELECT ROWID FROM comments WHERE comment_text IN (
-- SELECT comment_text FROM comments
-- GROUP BY comment_text
-- HAVING COUNT(1) > 1
-- )))
