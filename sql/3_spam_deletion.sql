-- Spam Deletion, applied 3/17/2023
-- 5348 comments
SELECT ROWID FROM comments WHERE comment_text LIKE '%@gmail%' OR comment_text LIKE '%@%.com%'OR comment_text LIKE '%ojuko%' OR comment_text LIKE '%whatsapp%' OR comment_text LIKE '%http%'

-- 954 rows deleted
DELETE FROM comments_coref
WHERE comment_rowid IN (
SELECT ROWID FROM comments WHERE comment_text LIKE '%@gmail%' OR comment_text LIKE '%@%.com%'OR comment_text LIKE '%ojuko%' OR comment_text LIKE '%whatsapp%' OR comment_text LIKE '%http%'
)


-- 246 rows deleted
DELETE FROM knowledgeable_informant_narratives
WHERE comment_rowid IN (
SELECT ROWID FROM comments WHERE comment_text LIKE '%@gmail%' OR comment_text LIKE '%@%.com%'OR comment_text LIKE '%ojuko%' OR comment_text LIKE '%whatsapp%' OR comment_text LIKE '%http%'
)