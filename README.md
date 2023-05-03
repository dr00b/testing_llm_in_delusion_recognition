# Overview
This repo was created as part of an NLP class during my masters program. The goal was to classify "possible delusion" in a corpus of YouTube comments in which knowledgable informants (family, friends, caregivers) described an individual with dementia. For the full picture, read the paper which is in this repo as `final_report.pdf`.

# Installations
1. Initialize the conda environment using `environment.yml`
2. Install the spacy_experimental coreference model. Note, some of the steps below are already handled in step 1, but it won't hurt to rerun them...
```
pip install spacy_experimental
pip install chardet
pip install thinc[torch]
pip install https://github.com/explosion/spacy-experimental/releases/download/v0.6.1/en_coreference_web_trf-3.4.0a2-py3-none-any.whl
```

# Steps To Run
Note, this was an iterative research project. It's not possible to run start to finish simply via the cli. That said, an overview of steps is provided below:

1. Copy `.env_template` to `.env` and populate it with your own API key / parameters
2. Create a list of YouTube channels and videos to extract comments from and store them in `data`. The files were named, `channels_en.txt` and `vids_to_search.txt`. Note, channel id's have to be acquired via the YouTube data api. Can't just use the @username.
3. Run `youtube_extract.py`. This will create a SQLite database if it doesn't already exist.
4. Run sql scripts 1-2 using your favorite SQLite interface. Note, anything annotation related will fail as you haven't created that table yet.
5. Run through `notebooks/knowledgeable_informant_narratives.ipynb`
6. Run sql script 3.
7. Sql scripts 4-5. Get some data and start annotating! I kept it simple and did this in Excel, then loaded the data back into SQLite. The first batch of annotation informed the OpenAI prompting strategy and created a rubric for use in annotating a test set.
8. Sql script 6 controls which data to send to the OpenAI model.
9. Run `classify.py`
10. Run through `notebooks/compute_results.ipynb`

# Methods
See `final_report.pdf` for detailed overview of methods.

# Issues
### Open AI
- [500 Response Error 2/16/2023](https://community.openai.com/t/continuous-gpt3-api-500-error-the-server-had-an-error-while-processing-your-request-sorry-about-that/42239/14)
- [No text in response](https://community.openai.com/t/empty-text-in-the-response-from-the-api-after-few-calls/2067/11). I suspect this is due to predicting a stop sequence in the first character. In playground received: "The model predicted a completion that begins with a stop sequence, resulting in no output. Consider adjusting your prompt or stop sequences."

### Bias in YouTube Commments
- I relied on YouTube search to derive a corpus of dementia-related videos. People may have searched for the content, found a useful video, and begun internalizing vocabulary. Therefore not simulating an individual who has yet to find helpful content.
- Not clear why data is not present in API which is present via browser. May be result of anti-spam filters. In other cases, channel owners moderate comment content, stays in under review, but the comment count has already incremented in database. Complexity of managing a system with billions of videos, can't eventual consistency of aggregate stats. A [quora post to explain.](https://www.quora.com/Why-do-the-comments-number-on-Youtube-sometimes-not-match-the-actual-ones-shown)

| VideoID | Browser Count | API Count | API Coll Date |
| ------- | ---------| -------- | ------- |
| zx7gLoPMO-s | 105 | 64 | 2023-02-08 |
| zpth3xzvbjU | 40 | 40 | 2023-02-08 |
| -3V9eSYR6Cs | 51 | 49 | 2023-02-11 |
| 1EGhhZdQ_ts | 49 | 49 | 2023-02-11 |
| mJk02XI_sRA | 5245 | 3888 |  2023-02-11 |
| CWnILUjkgXg | 1824 | 1565 | 2023-02-08 |

# Resources
### Open AI on Classification
- https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api
- https://platform.openai.com/docs/api-reference/parameter-details
- https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset
- https://medium.com/@AlyssaSha/fine-tuning-gpt-3-using-python-for-keywords-classification-6c4970526c68

### Coreference resolution
#### Experimental Spacy Coreference (released Oct 2022):
- [Blog Post](https://explosion.ai/blog/coref)
- [API Docs](https://spacy.io/api/coref)
- [Github How To Issue](https://github.com/explosion/spaCy/discussions/11585)
- [Video Summary](https://www.youtube.com/watch?v=fio3BejnRsM)

#### Other Coreference Models
- https://medium.com/huggingface/state-of-the-art-neural-coreference-resolution-for-chatbots-3302365dcf30
- https://neurosys.com/blog/intro-to-coreference-resolution-in-nlp
