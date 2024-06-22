from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint
from threading import Thread
from app.utils.whatsapp_utils import schedule_tasks  # Importieren Sie die Funktion
import schedule
import time

def create_app():
    app = Flask(__name__)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)

    # Aufgaben planen
    schedule_tasks(app)

    # Scheduler-Thread starten
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()

    return app
