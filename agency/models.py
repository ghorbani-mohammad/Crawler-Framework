from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Agency(BaseModel):
    name = models.CharField(max_length=20, null=False, unique=True)
    country = models.CharField(max_length=20, default="NA")
    website = models.CharField(max_length=100, null=False, unique=True)
    alexa_global_rank = models.IntegerField(default=0, null=True)
    crawl_headers = models.JSONField(null=True, blank=True, default=dict)
    status = models.BooleanField(default=1)
    link_keep_days = models.PositiveIntegerField(
        default=1,
        null=True,
        blank=True,
        help_text="how many days to keep the links of crawled page in redis",
    )

    class Meta:
        verbose_name_plural = "agencies"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.pages.all().update(status=self.status)

    def __str__(self):
        return self.name


class Structure(models.Model):
    name = models.CharField(max_length=20, null=True)
    news_links_structure = models.JSONField()
    news_links_code = models.TextField(
        null=True,
        blank=True,
        help_text='like: for el in elements: try: links.append(el["href"]) except: continue',
    )
    news_meta_structure = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name if self.name is not None else "None"


class Cookie(BaseModel):
    key_values = models.JSONField()


class Page(models.Model):
    agency = models.ForeignKey(Agency, related_name="pages", on_delete=models.CASCADE)
    url = models.CharField(max_length=2000, null=False, unique=True)
    crawl_interval = models.PositiveIntegerField(default=60, help_text="minute")
    load_sleep = models.PositiveIntegerField(
        default=4, blank=True, help_text="each link sleep"
    )
    links_sleep = models.PositiveIntegerField(
        default=1, blank=True, help_text="all links sleep"
    )
    last_crawl = models.DateTimeField(null=True)
    last_crawl_count = models.PositiveIntegerField(null=True, blank=True)
    status = models.BooleanField(default=1)
    fetch_content = models.BooleanField(default=1)
    structure = models.ForeignKey(
        Structure, on_delete=models.SET_NULL, null=True, blank=True
    )
    telegram_channel = models.CharField(
        max_length=100, null=True, blank=True, help_text="like: @jobinja"
    )
    iv_code = models.CharField(max_length=100, null=True, blank=True)
    message_code = models.TextField(
        default=None,
        null=True,
        blank=True,
        help_text='message=data["link"] or data["iv_link"]',
    )
    take_picture = models.BooleanField(default=False)
    cookie = models.ForeignKey(
        Cookie, related_name="pages", on_delete=models.CASCADE, null=True
    )
    lock = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.url

    @property
    def days_to_keep(self):
        return self.agency.link_keep_days


class Report(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="report")
    status = models.CharField(max_length=300, null=True)
    fetched_links = models.IntegerField(default=0)
    new_links = models.IntegerField(default=0)
    picture = models.ImageField(
        upload_to=".static/crawler/static", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    log = models.TextField(blank=True)

    def __str__(self):
        return self.page.url


class Log(BaseModel):
    page = models.ForeignKey(
        Page, on_delete=models.CASCADE, related_name="logs", null=True
    )
    url = models.CharField(max_length=2000, null=True)
    description = models.TextField(default="")
    error = models.TextField(null=True)

    CRAWLING = "cra"
    SENDING = "sen"

    PHASE_CHOICES = (
        (CRAWLING, "کرال"),
        (SENDING, "ارسال به تلگرام"),
    )
    phase = models.CharField(choices=PHASE_CHOICES, null=True, blank=True, max_length=3)

    def __str__(self):
        return "{} {}".format(self.id, self.page)


class Option(models.Model):
    key = models.CharField(max_length=70)
    value = models.CharField(max_length=70)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
