FROM python:3.6
EXPOSE 8888
RUN groupadd --gid 1000 user && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash user
RUN mkdir /home/user/app
ADD setup.py /home/user/app
ADD alpha.yaml /home/user/app
ADD app /home/user/app/app
ADD app/models ./models
RUN cd /home/user/app && \
    pip install --no-cache-dir .
RUN pip install -r /home/user/app/app/requirements.txt
RUN chown -R "1000:1000" /home/user
USER user
WORKDIR /home/user/app
ENV PYTHONPATH /home/user/app
CMD python3 /home/user/app/app/app.py