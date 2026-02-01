from app.ui.main_window import MainWindow
from app.utils.logger import setup_logger
import logging

if __name__ == "__main__":
    logger = setup_logger()
    
    try:
        logger.info("Inicando SmartCredit App...")
        app = MainWindow()
        app.mainloop()
        logger.info("App closed normally.")
    except Exception as e:
        logger.exception(f"Critical Error: {e}")
        # Optionally show a native popup here if tkinter is still alive
        print(f"CRITICAL ERROR: {e}")
