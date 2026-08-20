# Dashboard image: serves the metrics dashboard via NGINX and reverse-proxies
# /api/* requests to the "collector-service" service over the Docker network.
FROM nginx:latest

RUN rm -f /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/app.conf
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
