# The image is already built, please use the following command to run the container:
# docker start frontend-profiler
# To stop the container, use:
# docker stop frontend-profiler
#
# if you want to rebuild the image, use the following command:
# docker build -t frontend-image .
# To run the container with the new image, use:
# docker run -d --name frontend-profiler -p 8080:8080 frontend-profiler

FROM nginx:alpine
WORKDIR /Dashboard-Placed

COPY . /Dashboard-Placed

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
