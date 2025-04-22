FROM python:3.12-slim
WORKDIR /app

# define environment variables
ENV PORT=8501
ENV BASE_URL_PATH="verden-pa-norsk"

COPY app/requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app /app/

CMD streamlit run Hjem.py --server.port $PORT --server.baseUrlPath $BASE_URL_PATH --browser.gatherUsageStats False
