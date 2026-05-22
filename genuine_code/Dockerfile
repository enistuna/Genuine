FROM python:3.10-slim

RUN useradd -m -u 1000 user

WORKDIR /home/user/app

COPY requirements_core.txt requirements_ui.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_core.txt -r requirements_ui.txt

COPY --chown=user:user . .

RUN chown -R user:user /home/user/app

USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/home/user/app

RUN chmod +x start.sh

EXPOSE 7860

CMD ["./start.sh"]
