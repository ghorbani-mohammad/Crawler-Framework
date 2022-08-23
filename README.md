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
  - Agency
  - Page
  - Structure
### Agency
Agencies are the websites, like CNN and BBC. Before doing anything you should define agencies.

### Page
Pages, are different pages of an agency or website. For example CNN website has political, entertainment ... pages in it. After defining your agencies you can specify pages of that website which you want crawl data.

### Structure
Structures define how app should gather data from a page. When you defining a page, you should specify its structure.
So you need define structure of a page, before creating the page.


## How it works?

You can setup the project by docker-compose utility.

```bash
  git clone git@github.com:ghorbani-mohammad/crawler-framework.git
  cd crawler-framework
  docker-compose up
```
    
