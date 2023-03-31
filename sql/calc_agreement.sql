SELECT a.possible_delusion, c.has_delu_keyword, COUNT(1) FROM annotated a
INNER JOIN comments c
ON a.comment_rowid = c.ROWID
GROUP BY a.possible_delusion, c.has_delu_keyword

SELECT a.possible_delusion, c1.is_possible_delusion, c.comment_text, a.excerpt FROM annotated a
INNER JOIN comments c
ON a.comment_rowid = c.ROWID
INNER JOIN classifications c1
ON a.comment_rowid = c1.input_text_id
WHERE a.possible_delusion = 1 OR c1.is_possible_delusion = 1
AND prompt_version = 3


SELECT a.comment_rowid, a.possible_delusion, c1.is_possible_delusion, c.comment_text, c1.excerpt, a.excerpt FROM annotated a
INNER JOIN comments c
ON a.comment_rowid = c.ROWID
INNER JOIN classifications c1
ON a.comment_rowid = c1.input_text_id
AND c1.prompt_version = 5
WHERE a.possible_delusion = 1 OR c1.is_possible_delusion = 1

-- confusion matrix
SELECT a.possible_delusion, c.is_possible_delusion, COUNT(1) FROM annotated a
INNER JOIN classifications c
ON a.comment_rowid = c.input_text_id
AND c.prompt_version = 5
GROUP BY a.possible_delusion, c.is_possible_delusion

SELECT a.possible_delusion, c.is_possible_delusion, COUNT(1) FROM annotated a
INNER JOIN classifications c
ON a.comment_rowid = c.input_text_id
AND c.prompt_version = 3
GROUP BY a.possible_delusion, c.is_possible_delusion