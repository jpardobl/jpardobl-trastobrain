FROM ubuntu:20.04
RUN apt-get update && apt-get install \
  -y --no-install-recommends python3 python3-virtualenv

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies:
RUN pip install -r requirements.txt

# Install module:
RUN pip install .

# Run the application:
CMD ["/bin/bash", "scripts/start.sh"]
