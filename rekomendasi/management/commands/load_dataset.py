
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import pandas as pd
from rekomendasi.models import TrainingRecord
from rekomendasi.ml import _normalize_dataframe

class Command(BaseCommand):
    help = "Load dataset Excel (2 sheet) menjadi TrainingRecord"

    def add_arguments(self, parser):
        parser.add_argument("excel_path", type=str, help="Path file Excel")

    def handle(self, *args, **opts):
        path = Path(opts["excel_path"])
        if not path.exists():
            raise CommandError(f"File tidak ditemukan: {path}")

        xls = pd.ExcelFile(path)
        total = 0
        for sn in xls.sheet_names[:2]:
            df = pd.read_excel(path, sheet_name=sn)
            df = _normalize_dataframe(df)
            for _, row in df.iterrows():
                TrainingRecord.objects.update_or_create(
                    name=row["name"],
                    defaults=dict(
                        nilai_mtk=row["nilai_mtk"],
                        nilai_bindo=row["nilai_bindo"],
                        nilai_bing=row["nilai_bing"],
                        nilai_ipa=row["nilai_ipa"],
                        minat=row["minat"],
                        jurusan=row["jurusan"],
                    )
                )
                total += 1
        self.stdout.write(self.style.SUCCESS(f"Sukses memuat {total} baris."))
