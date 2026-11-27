"""Materiały kursu i API labów pod wspólnym adresem."""
from importlib import import_module
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from flask import Blueprint, Response, abort, jsonify, request, send_file, send_from_directory

ROOT = Path(__file__).resolve().parent
materials = Blueprint("materials", __name__)
DOWNLOADS = {".csv", ".py", ".md", ".txt", ".yaml"}


@materials.get("/kurs.zip")
def course_archive():
    files = [ROOT / name for name in ("app.py", "course.py", "requirements.txt", "verify_labs.py", "test_code.js",
             "pagerank.py", "index.html", "projekty.html", "w-produkcji.html", "sylabus.pdf", ".gitignore")]
    for folder in ("assets", *(f"lab{i}" for i in range(1, 11))):
        files.extend(path for path in (ROOT / folder).iterdir()
                     if path.is_file() and not path.is_symlink() and not path.name.startswith(".")
                     and path.suffix in DOWNLOADS | {".html", ".css", ".js", ".svg"})
    archive = BytesIO()
    with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
        for path in sorted(files):
            bundle.write(path, path.relative_to(ROOT).as_posix())
    archive.seek(0)
    return send_file(archive, mimetype="application/zip", as_attachment=True, download_name="isi-kurs.zip")


@materials.get("/")
@materials.get("/index.html")
@materials.get("/projekty.html")
@materials.get("/w-produkcji.html")
@materials.get("/sylabus.pdf")
@materials.get("/requirements.txt")
@materials.get("/pagerank.py")
@materials.get("/verify_labs.py")
@materials.get("/lab<int:number>/")
@materials.get("/lab<int:number>/<path:name>")
def page(number=None, name=None):
    if number is None:
        path = ROOT / (request.path.lstrip("/") or "index.html")
    else:
        if not 1 <= number <= 10:
            abort(404)
        if name and "/" in name:
            abort(404)
        path = ROOT / f"lab{number}" / (name or "index.html")
        if name == "articles.csv" and number in (5, 6):
            path = ROOT / "lab4" / name
    path = path.resolve()
    if not path.is_relative_to(ROOT) or path.suffix not in DOWNLOADS | {".html", ".svg", ".pdf"}:
        abort(404)
    return send_from_directory(path.parent, path.name, as_attachment=path.suffix in DOWNLOADS)


@materials.route("/lab<int:number>/api/<path:endpoint>", methods=["GET", "POST"])
def api(number, endpoint):
    if not 1 <= number <= 10:
        abort(404)
    try:
        lab = import_module(f"lab{number}.app").app
    except ModuleNotFoundError as error:
        return jsonify(error=f"Brakuje pakietu {error.name}. Zainstaluj zależności zgodnie z instrukcją Lab {number}."), 503
    environ = request.environ.copy()
    environ["SCRIPT_NAME"] = environ.get("SCRIPT_NAME", "") + f"/lab{number}"
    environ["PATH_INFO"] = "/api/" + endpoint
    return Response.from_app(lab.wsgi_app, environ)
