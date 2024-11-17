from os import path

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from selenium.webdriver.firefox.options import Options as FirefoxOptions

CODE = """
{0}
"""

IMAGE_FILE_TYPES = ["jpeg", "jpg", "png", "bmp"]

DEFAULT_HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.11 (KHTML, like Gecko) "
    "Chrome/23.0.1271.64 Safari/537.11",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "none",
    "Accept-Language": "en-US,en;q=0.8",
    "Connection": "keep-alive",
}


def is_image(ext):
    if ext.lower() not in IMAGE_FILE_TYPES:
        raise ValidationError("unknown file format")
    return True


def report_image_path(_instance, filename):
    ext = filename.split(".")[-1].lower()
    if is_image(ext):
        return path.join(
            ".",
            "report",
            "images",
            f"{int(timezone.now().timestamp())}.{ext}",
        )
    return None


def get_browser_options(use_proxy: bool =False):
    options = FirefoxOptions()
    options.set_capability("pageLoadStrategy", "eager")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-automation")
    options.add_argument("--no-sandbox")

    if use_proxy:
        # Set up the HTTP and HTTPS proxy for Firefox
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.http", settings.PROXY_HOST)
        options.set_preference("network.proxy.http_port", settings.PROXY_PORT)
        options.set_preference("network.proxy.ssl", settings.PROXY_HOST)
        options.set_preference("network.proxy.ssl_port", settings.PROXY_PORT)

        proxy_host = settings.PROXY_HOST
        proxy_port = settings.PROXY_PORT
        proxy_username = settings.PROXY_USER
        proxy_password = settings.PROXY_PASS
        proxy_with_credentials = f"{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"

        options.set_preference("network.proxy.http", proxy_host)
        options.set_preference("network.proxy.http_port", int(proxy_port))
        options.set_preference("network.proxy.ssl", proxy_host)
        options.set_preference("network.proxy.ssl_port", int(proxy_port))
        options.set_preference("network.proxy.type", 1)  # Enable manual proxy configuration
        options.set_preference("network.proxy.http", proxy_with_credentials)

        # Optional: Disable proxy for HTTPS and other protocols
        options.set_preference("network.proxy.ssl", "")  # No HTTPS proxy
        options.set_preference("network.proxy.ftp", "")  # No FTP proxy
        options.set_preference("network.proxy.socks", "")  # No SOCKS proxy

    # Disable images
    options.set_preference("permissions.default.image", 2)

    return options
