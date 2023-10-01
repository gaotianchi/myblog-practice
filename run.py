from myblog import app
from myblog.models import Watcher, Schedule


if __name__ == "__main__":
    watcher = Watcher(app)
    scheduler = Schedule(app)
    scheduler.run()
    watcher.run()
    app.run(debug=True)
