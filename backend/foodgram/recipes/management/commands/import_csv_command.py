import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу из файла csv.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path', type=str, help='Путь к CSV-файлу с ингредиентами'
        )

    def handle(self, *args, **options):
        file_path = options['path']
        if not file_path:
            raise ValueError(
                'Укажите путь к CSV-файлу с ингредиентами '
                'через аргумент --path'
            )

        with open(file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            ingredients = []
            for row in csv_reader:
                try:
                    ingredient = Ingredient(
                        name=row[0],
                        measurement_unit=row[1],
                    )
                    ingredients.append(ingredient)
                except ValueError:
                    print('Ошибка при импорте ингредиента:', row)
            Ingredient.objects.bulk_create(ingredients)
            self.stdout.write(self.style.SUCCESS(
                'Ингредиенты успешно импортированы.')
            )
