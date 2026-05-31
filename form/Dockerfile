# The image is already built, please use the following command to run the container:
# docker start fastapi-container
# To stop the container, use:
# docker stop fastapi-container
#
# if you want to rebuild the image, use the following command:
# docker build -t fastapi-image .
# To run the container with the new image, use:
# docker run -d --name fastapi-container -p 8001:8001 my-fastapi-app

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /Dashboard-Placed

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /Dashboard-Placed/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /Dashboard-Placed

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "form:app", "--host", "0.0.0.0", "--port", "8001"]

