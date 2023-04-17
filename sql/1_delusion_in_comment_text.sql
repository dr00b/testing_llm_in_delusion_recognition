ALTER TABLE comments ADD COLUMN has_delu_keyword bool;

UPDATE comments
SET has_delu_keyword = 0;

UPDATE comments
SET has_delu_keyword = 1
WHERE comment_text LIKE '%delus%';