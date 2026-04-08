import sys
from threading import Event

from PySide6.QtWidgets import QApplication

from src.pattern_tracking.logic.BackgroundComputation import BackgroundComputation
from src.pattern_tracking.logic.tracker.TrackerManager import TrackerManager
from src.pattern_tracking.logic.video.DummyVideoFeed import DummyVideoFeed
from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.qt_gui.AppMainWindow import AppMainWindow


class Main:
    """
    Launches all separate operations on their own thread,
    the main thread will launch Qt's user interface.
    """

    def __init__(self):
        self._app = QApplication(sys.argv)
        self._global_halt = Event()
        self._tracker_manager = TrackerManager()
        self._live_feed_wrapper: LiveFeedWrapper = LiveFeedWrapper(DummyVideoFeed(self._global_halt))
        self._main_window = AppMainWindow(self._tracker_manager, self._live_feed_wrapper)
        self._app.aboutToQuit.connect(self._stop_children_operations)

        self._background_computation_worker = BackgroundComputation(
            self._tracker_manager,
            self._live_feed_wrapper,
            self._main_window.get_frame_display_widget(),
            self._global_halt,
            self._main_window
        )

        # Connect cross-thread signal: plot update runs on main thread via Qt event queue
        self._background_computation_worker.plot_update_requested.connect(
            self._main_window.get_plot_container_widget().update_plots
        )

    def run(self):
        self._live_feed_wrapper.start()
        self._background_computation_worker.start()
        self._main_window.show()
        self._app.exec()

    def _stop_children_operations(self):
        self._global_halt.set()


def main():
    worker = Main()
    worker.run()


if __name__ == '__main__':
    main()
