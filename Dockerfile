# The image is already built, please use the following command to run the container:
# docker start dashboard-container
# To stop the container, use:
# docker stop dashboard-container
#
# if you want to rebuild the image, use the following command:
# docker build -t dashboard-image .
# To run the container with the new image, use:
# docker run -e SUPABASE_URL="supabse_url" -e SUPABASE_KEY="supabase_key" -d --name dashboard-container -p 5500:5500 my-dashboard-app

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /Dashboard-Placed

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /Dashboard-Placed/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /Dashboard-Placed

EXPOSE 5500

CMD ["streamlit", "run", "app.py", "--server.port=5500", "--server.address=0.0.0.0"]