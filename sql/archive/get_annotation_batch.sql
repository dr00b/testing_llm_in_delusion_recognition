-- does not exist an annotation for batch one
SELECT input_text_id FROM classifications c
WHERE NOT EXISTS (
SELECT 1 FROM annotated a 
WHERE a.comment_rowid = c.input_text_id
)
AND c.prompt_version = 5 