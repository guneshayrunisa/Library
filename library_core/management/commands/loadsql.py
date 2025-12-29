from django.core.management.base import BaseCommand
from django.db import connection
import os

class Command(BaseCommand):
    help = "Run veritabani.sql on the current database"

    def handle(self, *args, **options):
        # Dosya yolu: manage.py'nin olduğu klasörden bir üst dizinde 'veritabani.sql' var
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sql_file_path = os.path.join(base_dir, '..', 'veritabani.sql')
        sql_file_path = os.path.normpath(sql_file_path)

        self.stdout.write(f"Reading SQL file from: {sql_file_path}")

        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql = f.read()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {sql_file_path}"))
            return

        with connection.cursor() as cursor:
            statements = sql.split(';')
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error executing statement: {e}"))
                    else:
                        self.stdout.write(self.style.SUCCESS("Executed statement"))
