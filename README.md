## Story Of This Project
There are sometimes that we want to be first person that get notice about new post in a website. For example when you're looking for a job, you want to be first person that apply to the new jobs and by this way you want to increase your chance in the hiring process. Or you want to get new articles from your favorite websites daily. This framework is designed specifically for these purposes.

## Crawler Framework
This is a framework for crawling data from websites. You define a website, then the pages of that website and in the last step you define the structure of those pages so the crawler can retrieve data from them.  In this framework we have 3 main entities:
  - Agency
  - Page
  - Structure
### Agency
Agencies are the websites, like CNN and BBC. Before doing anything you should define agencies.

### Page
Pages, are different pages of an agency or website. For example CNN website has political, entertainment and etc pages in it. After defining your agencies you can specify pages of that website which you want crawl data.

### Structure
Structures define how crawler should gather data from a page. When you defining a page, you should specify its structure.
So you need define structure of a page, before creating the page. This model has three important fields that probably you need fill those.

First one is news_links_structure. This field specifies how we should get links of news or articles or anything that we want. At the below picture you can see an example. As you can see, we gather elements with tag **a** that has class attribute with value **c-jobListView__titleLink**
![image](https://user-images.githubusercontent.com/12118217/186157990-260c1c86-0ebf-4859-8d32-018d1551f028.png)

***

### Information
- Port: 8205
- Nginx log files:
    ```
    access: /var/log/nginx/api-crawler_access.log
    error:  /var/log/nginx/api-crawler_error.log
    ```
- Django Admin Panel:
    * [https://crawler.m-gh.com/secret-admin/](https://crawler.m-gh.com/secret-admin/)


## Guest User
Guest user have read-only access to some models, So using that, you can login into Django admin and 
see what potentials can have this project. By login into Django admin you can see I have defined a bunch
of websites that I get their new posts periodically. These are some examples that help you to create your
own crawler.

- Guest User Credential:
  * **Username**: guest
  * **Password**: RPxzsoen4O


## How To Setup?

You can setup the project by docker-compose utility.

```bash
  git clone git@github.com:ghorbani-mohammad/crawler-framework.git
  cd crawler-framework
  docker-compose up
```
    
