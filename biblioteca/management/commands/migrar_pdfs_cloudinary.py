from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from pathlib import Path

from biblioteca.models import LibroLeido


class Command(BaseCommand):
    help = "Resube PDFs locales antiguos a Cloudinary y actualiza LibroLeido.pdf"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Solo muestra qué haría, sin subir nada."
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        media_root = Path(settings.MEDIA_ROOT)
        total = 0
        subidos = 0
        faltantes = 0

        # Busca libros con pdf asignado
        libros = LibroLeido.objects.exclude(pdf="").exclude(pdf=None)

        self.stdout.write(self.style.NOTICE(f"Libros con PDF en BD: {libros.count()}"))
        self.stdout.write(self.style.NOTICE(f"MEDIA_ROOT local: {media_root}"))

        for libro in libros:
            total += 1
            pdf_name = libro.pdf.name  # ej: "libros/archivo.pdf"

            # Ruta real en disco (LOCAL)
            local_path = media_root / pdf_name

            if not local_path.exists():
                faltantes += 1
                self.stdout.write(self.style.WARNING(
                    f"No existe en disco: {local_path} (Libro ID {libro.id})"
                ))
                continue

            self.stdout.write(f"Encontrado: {local_path} (Libro ID {libro.id})")

            if dry_run:
                continue

            # Abrir desde disco y reasignar para que Cloudinary lo suba
            with open(local_path, "rb") as f:
                libro.pdf.save(local_path.name, File(f), save=True)

            subidos += 1
            self.stdout.write(self.style.SUCCESS(
                f"Subido a Cloudinary y actualizado: Libro ID {libro.id}"
            ))

        self.stdout.write(self.style.NOTICE("\n--- RESUMEN ---"))
        self.stdout.write(self.style.NOTICE(f"Total revisados: {total}"))
        self.stdout.write(self.style.SUCCESS(f"Subidos: {subidos}"))
        self.stdout.write(self.style.WARNING(f"Faltantes en disco: {faltantes}"))

        if dry_run:
            self.stdout.write(self.style.WARNING("\n(dry-run) No se subió nada."))
