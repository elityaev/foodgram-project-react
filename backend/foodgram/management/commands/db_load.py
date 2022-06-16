import csv

from django.conf import settings
from django.core.management import BaseCommand


from foodgram.models import Ingredient, Tag

TABLES = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv',
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        for model, csv_f in TABLES.items():
            lines = 0
            file = open(f'{settings.BASE_DIR}/data/{csv_f}')
            for line in file:
                lines += 1
            with open(
                    f'{settings.BASE_DIR}/data/{csv_f}', 'r',
            ) as read_object, open(
                f'{settings.BASE_DIR}/data/temp.csv', 'w'
            ) as write_object:
                if csv_f == 'tags.csv':
                    write_object.write('id,name,color,slug\n')
                else:
                    write_object.write('id,name,measurement_unit\n')
                for idx, line in enumerate(read_object, start=1):
                    write_object.write(f'{idx},{line}')
            with open(
                f'{settings.BASE_DIR}/data/temp.csv',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                model.objects.bulk_create(
                    model(**data) for data in reader
                )
            self.stdout.write(
                self.style.SUCCESS(f'Все данные из файла {csv_f} загружены')
            )
