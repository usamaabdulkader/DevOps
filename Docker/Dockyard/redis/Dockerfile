FROM redis:7-alpine
VOLUME /data
CMD ["redis-server", "--appendonly", "yes", "--save", "60", "1"]