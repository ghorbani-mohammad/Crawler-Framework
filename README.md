### Information

- Server: **DigitalOcean**
- Port: 8205
- Server path: `/var/www/cra/`
- Nginx log files:
    ```
    access: /var/log/nginx/api-crawler_access.log
    error:  /var/log/nginx/api-crawler_error.log
    ```
- Django Admin Panel:
    * [https://crawler.m-gh.com/secret-admin/](https://crawler.m-gh.com/secret-admin/)

- Guest User Credential:
  ```
  username: guest
  password: RPxzsoen4O
  ```


## Guest User
Guest user have read-only access to some models, So using that, you can login into Django admin and 
see what potential can have this project. By login into Django admin you can see I have defined a bunch
of websites that I get their new posts periodically. These are some examples that help you to create your
own crawler.


## Crawler Framework
In this framework we have 3 main entities:
  Agency
  Page
  Structure
This is a Framework for crawling websites and social networks and send data to Telegram channel. First You should create agency. Agency means website or social network. For example you create CNN agency. Then you should create pages that you want must be crawled. For example you just want politics section of CNN. So you create CNN politics page. Each page has structure.


## What is structure?
By using structure we define how we can get data within a page.


## How it works?

You can setup the project by docker-compose utility.

```bash
  git clone git@github.com:ghorbani-mohammad/crawler-framework.git
  cd crawler-framework
  docker-compose up
```
    
