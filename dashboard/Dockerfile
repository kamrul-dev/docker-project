# Dashboard image: serves the metrics dashboard via NGINX and reverse-proxies
# /api/* requests to the "collector-service" service over the Docker network.

# If you want to build the image from a pre-built own dashboard:1.0.0  image, uncomment the following line and comment out the next line.
# FROM dashboard:1.0.0 
FROM nginx:latest

RUN rm -f /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/app.conf
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
