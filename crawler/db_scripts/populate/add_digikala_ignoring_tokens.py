import os
import sys
import django


def initial():
    sys.path.append("../..")
    os.environ["DJANGO_SETTINGS_MODULE"] = "crawler.settings"
    django.setup()


initial()

from notification.models import FilteringTag, FilteringToken


ignore_tokens = [
    "فوم اصلاح",
    "کرم مرطوب‌کننده",
    "شورت",
    "سشوار",
    "اپیلاتور",
    "کرم دور چشم",
    "ادو پرفیوم",
    "ادوپرفیوم",
    "بادی نوزادی",
    "کاغذ A4",
    "چراغ قوه",
    "چمدان",
    "اسپری بدن",
    "سرم پوست",
    "اسپری ضد تعریق",
    "عطر جیبی",
    "بالم لب",
    "کیسه زباله",
    "نوار بهداشتی",
    "ست تی شرت",
    "کفش طبی",
    "کفش مخصوص",
    "تاپ زنانه",
    "عینک آفتابی",
    "هندزفری",
    "پیراهن آستین",
    "کرم ترک پا",
    "لوسیون",
    "دستمال",
    "نوشابه",
    "دستبند طلا",
    "گردنبند طلا",
    "اسباب بازی",
    "عسل",
    "کالسکه",
    "گوش پاک کن",
    "کرم کنترل کننده چربی",
    "فوم شستشو",
    "تونر پاک کننده",
    "کیسه فریزر",
    "کرم موبر",
    "بی بی چک",
    "سرویس خواب",
    "چسب مو",
    "کفش",
    "شانه مو",
    "رول ضد تعریق",
    "شارژر فندکی",
    "ساعت مچی عقربه",
    "کرم ضد لک",
    "فریم عینک",
    "هات چاکلت",
    "کرم احیای",
    "رژ لب",
    "کافی میکس",
    "برس حرارتی",
    "سرویس ملحفه",
    "ست بادی",
    "کت چرم",
    "تیپ ناخن",
    "شمش طلا",
    "پافر",
    "ست شیرآلات",
    "پنل سقفی",
    "محلول پاک کننده آرایش",
    "پنیر پیتزا",
    "استیک ضد تعریق",
    "لباس نوزادی",
    "دوچرخه ثابت",
    "کرم مرطوب کننده",
    "روروک",
    "سوتین زنانه",
    "نرم کننده مو",
    "کرم روشن کننده",
    "کرم سفت کننده",
    "کرم رفع بوی",
    "ماسک مو",
    "انگشتر طلا",
    "صابون",
    "النگو",
    "شامپو",
    "اسکاچ",
    "پد بهداشتی",
    "مردانه",
    "زنانه",
    "پسرانه",
    "دخترانه",
    "بانوان",
]

tag_id = 2
tag = FilteringTag.objects.get(id=tag_id)

created_count = 0
skipped_count = 0

for token in ignore_tokens:
    token = token.strip()
    if not token:
        continue  # Skip empty tokens

    obj, created = FilteringToken.objects.get_or_create(
        token=token, defaults={"tag": tag}
    )
    if created:
        created_count += 1
    else:
        skipped_count += 1

print(f"Created {created_count} tokens, skipped {skipped_count} tokens.")
