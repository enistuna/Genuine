FROM python:3.10-slim

RUN useradd -m -u 1000 user
WORKDIR /home/user/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY requirements_core.txt requirements_ui.txt ./

RUN uv venv venv_core && \
    uv pip install --python venv_core --no-cache -r requirements_core.txt

RUN uv venv venv_ui && \
    uv pip install --python venv_ui --no-cache -r requirements_ui.txt

COPY --chown=user:user . .
RUN chown -R user:user /home/user/app

USER user

ENV HOME=/home/user \
    PATH=/home/user/app/venv_core/bin:$PATH \
    PYTHONPATH=/home/user/app

RUN chmod +x start.sh

EXPOSE 7860

CMD ["./start.sh"]
