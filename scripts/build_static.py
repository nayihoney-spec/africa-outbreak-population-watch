"""Reproducible static build from tracked source; no network required."""
import pathlib, shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir()
for f in ['index.html','LICENSE']:shutil.copy2(ROOT/f,OUT/f)
for d in ['assets','pages','data']:shutil.copytree(ROOT/d,OUT/d,ignore=shutil.ignore_patterns('__pycache__'))
print('Built dist from source')
