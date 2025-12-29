import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify

class Command(BaseCommand):
    help = "DB'ye toplu örnek kitap ekler (internetsiz)."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=300, help="Kaç kitap eklensin?")
        parser.add_argument("--dry-run", action="store_true", help="DB'ye yazmadan simüle et")

    def handle(self, *args, **options):
        count = options["count"]
        dry_run = options["dry_run"]

        # Modeli yakala (Book veya Kitap)
        BookModel = None
        try:
            from library_core.models import Book as BookModel  # type: ignore
        except Exception:
            try:
                from library_core.models import Kitap as BookModel  # type: ignore
            except Exception:
                self.stderr.write(self.style.ERROR(
                    "library_core.models içinde 'Book' veya 'Kitap' modeli bulamadım. "
                    "models.py'deki kitap modelinin adını kontrol et."
                ))
                return

        authors = [
            "Orhan Pamuk", "Elif Şafak", "Ahmet Hamdi Tanpınar", "Sabahattin Ali",
            "Yaşar Kemal", "Oğuz Atay", "Fyodor Dostoyevski", "Victor Hugo",
            "George Orwell", "Jane Austen", "J.K. Rowling", "Haruki Murakami",
            "Albert Camus", "Gabriel García Márquez", "Franz Kafka",
        ]

        categories = [
            "Roman", "Klasik", "Bilim Kurgu", "Fantastik", "Polisiye",
            "Tarih", "Felsefe", "Psikoloji", "Biyografi", "Edebiyat",
        ]

        publishers = [
            "İş Bankası Kültür", "Can Yayınları", "Yapı Kredi", "Everest",
            "Penguin", "Vintage", "HarperCollins", "Oxford Press",
        ]

        title_prefix = [
            "Gizemli", "Kayıp", "Son", "Sessiz", "Karanlık", "Beyaz", "Kırmızı",
            "Rüzgarlı", "Uzak", "Yakın", "Derin", "Küçük", "Büyük"
        ]

        title_suffix = [
            "Yolculuk", "Şehir", "Ada", "Geceler", "Rüya", "Sırlar", "Mektuplar",
            "Defter", "Zaman", "Kule", "Kapı", "Orman", "Deniz"
        ]

        def fake_isbn13():
            # Gerçek doğrulama şart değil; düzgün görünen 13 haneli sayı üretir
            return "".join(str(random.randint(0, 9)) for _ in range(13))

        # Model alanlarını oku
        field_names = {f.name for f in BookModel._meta.get_fields() if hasattr(f, "name")}

        # Olası alan isimleri (projeye göre değişebilir)
        title_field = "title" if "title" in field_names else ("name" if "name" in field_names else ("kitap_adi" if "kitap_adi" in field_names else None))
        author_field = "author" if "author" in field_names else ("yazar" if "yazar" in field_names else None)
        isbn_field = "isbn" if "isbn" in field_names else ("isbn_no" if "isbn_no" in field_names else None)
        category_field = "category" if "category" in field_names else ("kategori" if "kategori" in field_names else None)
        publisher_field = "publisher" if "publisher" in field_names else ("yayinevi" if "yayinevi" in field_names else None)
        year_field = "year" if "year" in field_names else ("publish_year" if "publish_year" in field_names else ("basim_yili" if "basim_yili" in field_names else None))
        copies_field = "copies" if "copies" in field_names else ("adet" if "adet" in field_names else ("quantity" if "quantity" in field_names else None))
        available_field = "available" if "available" in field_names else ("mevcut" if "mevcut" in field_names else None)

        if not title_field:
            self.stderr.write(self.style.ERROR(
                f"Kitap modelinde başlık alanını bulamadım. Alanlar: {sorted(field_names)}\n"
                "models.py'deki kitap modelini atarsan alanlara göre uyarlayayım."
            ))
            return

        created = 0
        skipped = 0

        for i in range(count):
            title = f"{random.choice(title_prefix)} {random.choice(title_suffix)} {i+1}"
            author = random.choice(authors)
            category = random.choice(categories)
            publisher = random.choice(publishers)
            year = random.randint(1950, 2024)
            copies = random.randint(1, 10)
            isbn = fake_isbn13()

            data = {}
            data[title_field] = title

            if author_field:
                data[author_field] = author
            if isbn_field:
                data[isbn_field] = isbn
            if publisher_field:
                data[publisher_field] = publisher
            if year_field:
                data[year_field] = year
            if copies_field:
                data[copies_field] = copies
            if available_field:
                # available boolean ise True yapalım
                data[available_field] = True

            # category FK mi, CharField mı? Bilemiyoruz.
            # CharField ise direkt string basar. FK ise patlar, o durumda o alanı atlarız.
            if category_field:
                data[category_field] = category

            if dry_run:
                created += 1
                continue

            try:
                # Aynı başlık+author varsa tekrar eklememeye çalış
                lookup = {title_field: title}
                if author_field:
                    lookup[author_field] = author

                obj, is_created = BookModel.objects.get_or_create(defaults=data, **lookup)
                if is_created:
                    created += 1
                else:
                    skipped += 1
            except Exception:
                # category FK olabilir vs. O zaman category'yi çıkarıp tekrar dene
                if category_field and category_field in data:
                    data.pop(category_field, None)
                try:
                    lookup = {title_field: title}
                    if author_field:
                        lookup[author_field] = author
                    obj, is_created = BookModel.objects.get_or_create(defaults=data, **lookup)
                    if is_created:
                        created += 1
                    else:
                        skipped += 1
                except Exception as e2:
                    skipped += 1
                    self.stderr.write(self.style.WARNING(f"Atlandı ({title}): {e2}"))

        self.stdout.write(self.style.SUCCESS(f"Bitti. Oluşturulan: {created}, Zaten vardı/atlandı: {skipped}"))
