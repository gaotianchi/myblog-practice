import os


from myblog import app
from myblog.models import Watcher, Schedule


if __name__ == "__main__":
    watcher_path = os.path.join(app.config["WORKSPACE"], "posts")
    if not os.path.exists(watcher_path):
        os.makedirs(watcher_path)

    watcher = Watcher(watcher_path, app)
    scheduler = Schedule(app)
    scheduler.run()
    watcher.run()
    app.run(debug=True)
