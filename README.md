# Chat With RSS
A chat interface for interrogating uploaded files


## Install
```shell
# 1. Create your virtual env.  Many tools for this, choose what you like best

# 2. With the virtual env activated, Install Python modules
(.venv) pip install -r requirements.txt

# 3. Configure
(.venv) cp dist.env .env 
# add your openai key
```
## Initial ingest
This will ingest the most recent 100 items from the feed, create embeddings and persist into the Chroma vector db
```shell
# activate your python virtual env for this project
# run the ingest script.  
(.venv) python ingest.py
INFO:chat_with_rss.rss_reader:Found 100 entries in the feed.
...

```
This will take some time (2-3 mins) due to the fact it is downloading the content for (up to) 100 web pages.

You can run this repeatably and it will only download feed items not already processed

## Run the app
After the install and the initial ingest, you can run the app locally
```shell
(.venv) streamlit run app.py

You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```