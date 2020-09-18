from threading import Timer, Lock

class TareaPeriodica():
    """
    Clase wrapper para ejecutar periódicamente una tarea haciendo uso de threading.Timers
    """
    def __init__(self, interval, function, *args, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.detener_timer = False
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._stopped = True
        if kwargs.pop('autostart', True):
            self.start()

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            if(not(self.detener_timer)):
                self._timer = Timer(self.interval, self._run)
                self._timer.start()
            else: self._timer.cancel()
        self._lock.release()

    def _run(self):
        try:
            self.function(*self.args, **self.kwargs)
        except Exception as e:
            print(f"Error ocurrido al ejecutar el scrapeo: {e}")
        finally:
            self.start(from_run=True)

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self.detener_timer = True
        self._lock.release()

