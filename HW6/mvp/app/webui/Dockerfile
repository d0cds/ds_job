FROM python:3.11-slim

WORKDIR /app/webui

COPY requirements.txt /app/webui/

RUN pip install --upgrade pip && pip install -r /app/webui/requirements.txt

COPY . /app/webui/

EXPOSE 8001

CMD ["streamlit", "run", "webui.py", "--server.port=8001", "--server.address=0.0.0.0"]