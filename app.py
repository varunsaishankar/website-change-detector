from flask import Flask, render_template, request, redirect,send_from_directory, abort
import difflib
import database
import checker
import scheduler

app = Flask(__name__)
database.init_db()


@app.route("/")
def home():
    pages = database.get_all_pages()
    return render_template("index.html", pages=pages)


@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    url = request.form["url"]
    interval = int(request.form["interval"])
    interval = max(15, min(interval, 1440))   # keep between 15 min and 24 h
    sensitivity = request.form.get("sensitivity", "medium")
    database.add_page(name, url, interval, sensitivity)
    return redirect("/")


@app.route("/check/<int:page_id>", methods=["POST"])
def check(page_id):
    pages = database.get_all_pages()
    for p in pages:
        if p["id"] == page_id:
            try:
                checker.check_page(page_id, p["url"])
            except Exception:
                database.update_status(page_id, "error")
            break
    return redirect("/")

@app.route("/history/<int:page_id>")
def history(page_id):
    page = database.get_page(page_id)
    if page is None:
        abort(404)
    snapshots = database.get_snapshots(page_id)
    return render_template("history.html", page=page, snapshots=snapshots)


@app.route("/diff")
def diff():
    old = database.get_snapshot(request.args.get("old", type=int))
    new = database.get_snapshot(request.args.get("new", type=int))
    if old is None or new is None:
        abort(404)

    differ = difflib.HtmlDiff(wrapcolumn=70)
    table = differ.make_table(
        old["text"].splitlines(),
        new["text"].splitlines(),
        fromdesc=f"Version {old['id']} ({old['created_at']})",
        todesc=f"Version {new['id']} ({new['created_at']})",
        context=True,
        numlines=2,
    )
    return render_template("diff.html", table=table, old=old, new=new)

@app.route("/screenshots/<path:filename>")
def screenshot(filename):
    return send_from_directory("screenshots", filename)

if __name__ == "__main__":
    scheduler.start_scheduler()
    app.run(debug=True, use_reloader=False)