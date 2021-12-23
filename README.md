### Information

- Server: **DigitalOcean**
- Port: 8205
- Server path: `/var/www/crawler/`
- Nginx log files:
    ```
    access: /var/log/nginx/api-crawler_access.log
    error:  /var/log/nginx/api-crawler_error.log
    ```
- Django Admin Panel:
    * [crawler.m-gh.com](https://crawler.m-gh.com/secret-admin/)



# Crawler Framework

This is a Framework for crawling websites and social networks and send data to Telegram channel.


## How it works?

You can setup the project by docker-compose utility.

```bash
  git clone git@github.com:ghorbani-mohammad/crawler-framework.git
  cd crawler-framework
  docker-compose up
```
    
