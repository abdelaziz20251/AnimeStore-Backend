"""
Django management command to reset the database.
WARNING: This will delete ALL data!
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection


class Command(BaseCommand):
    help = 'Reset the database by dropping all tables and running migrations fresh'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        if not options['noinput']:
            confirm = input(
                '⚠️  WARNING: This will DELETE ALL DATA in the database!\n'
                'Are you sure you want to continue? (yes/no): '
            )
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        self.stdout.write(self.style.WARNING('Resetting database...'))

        with connection.cursor() as cursor:
            # Get all table names
            cursor.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]

            # Drop all tables
            if tables:
                self.stdout.write(f'Dropping {len(tables)} tables...')
                for table in tables:
                    cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                    self.stdout.write(f'  Dropped: {table}')

            # Drop all sequences
            cursor.execute("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public'
            """)
            sequences = [row[0] for row in cursor.fetchall()]

            if sequences:
                self.stdout.write(f'Dropping {len(sequences)} sequences...')
                for seq in sequences:
                    cursor.execute(f'DROP SEQUENCE IF EXISTS "{seq}" CASCADE')
                    self.stdout.write(f'  Dropped: {seq}')

        self.stdout.write(self.style.SUCCESS('Database reset complete!'))
        self.stdout.write('Running migrations...')
        
        # Run migrations fresh
        call_command('migrate', verbosity=1)
        
        self.stdout.write(self.style.SUCCESS('Database reset and migrations completed!'))

