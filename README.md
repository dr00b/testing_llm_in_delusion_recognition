# nlp_final
Test - Beep boop

# Issues
### Youtube
- Search function does not actually order by views despite parameter. Receiving very low view count videos alongside "stars".
- Discrepancy in API comments count per vid and browser count.

| VideoID | Browser Count | API Count | API Coll Date |
| ------- | ---------| -------- | ------- |
| zx7gLoPMO-s | 105 | 64 | 2023-02-08 |
| zpth3xzvbjU | 40 | 40 | 2023-02-08 |
| -3V9eSYR6Cs | 51 | 49 | 2023-02-11 |
| 1EGhhZdQ_ts | 49 | 49 | 2023-02-11 |
| mJk02XI_sRA | 5245 | 3888 |  2023-02-11 |
| CWnILUjkgXg | 1824 | 1565 | 2023-02-08 |

### Open AI
- [500 Response Error 2/16/2023](https://community.openai.com/t/continuous-gpt3-api-500-error-the-server-had-an-error-while-processing-your-request-sorry-about-that/42239/14)


# Bias in Data
- Topic is affected by video content. People may have searched for the content, internalized vocabulary. Therefore not simulating someone who has yet to find helpful content.
- Not clear why data is not present in API which is present via browser. May be result of anti-spam filters. In other cases, channel owners moderate comment content, stays in under review, but the comment count has already incremented in database. Complexity of managing a system with billions of videos, can't eventual consistency of aggregate stats. A [quora post to explain.](https://www.quora.com/Why-do-the-comments-number-on-Youtube-sometimes-not-match-the-actual-ones-shown)

# Methods
- Use classic NLP techniques to identify patient testimonials in text. (length, narrative text cues, must be multiple langugages)
- Use classic NLP techniques to remove useless excerpts (thank you to the poster)
- Send as many results as possible to da-vinci model (justifiable given qualitative coding case)
- Choice of presence / frequency penalty and temperature to enhance consistency.
- Manually code responses, highlighting evidence (can I get annotators for this?)
- Compute concordance, ability to cite evidence from text

# TODO
- load some spanish comments
- create requirements.txt
- Estimate cost before hands, what is the average tokens?
- deidentify the comments, and the channel?
- spiff it up, fork it, post on linkedin...
https://www.biorxiv.org/content/10.1101/2022.12.23.521610v1
https://www.nature.com/articles/d41586-023-00056-7


# Resources
### Open AI on Classification
https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset
https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api
https://medium.com/@AlyssaSha/fine-tuning-gpt-3-using-python-for-keywords-classification-6c4970526c68
https://platform.openai.com/docs/api-reference/parameter-details