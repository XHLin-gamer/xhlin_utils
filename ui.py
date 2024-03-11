from contextlib import contextmanager
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import Progress
from rich.spinner import Spinner
from rich import box
import threading
import time



class my_table:
    def __init__(self, box_style=box.SIMPLE_HEAD) -> None:

        self.box_style = box_style
        self.columns = []
        self.rows = []
        self.title = ""
        self.table = self.generated_table()

    def add_column(self, name):
        self.columns.append(name)

    def add_row(self, *row_context):
        self.rows.append(row_context)

    def remove_column(self, name):
        self.columns.remove(name)

    def remove_row(self, *row_context):
        self.rows.remove(row_context)

    def set_title(self, title):
        self.title = title

    def generated_table(self):
        self.table = Table(
            title=self.title, box=self.box_style, title_justify='center')
        [self.table.add_column(c, justify="center") for c in self.columns]
        [self.table.add_row(*r) for r in self.rows]
        return self.table


class _UI:
    def __init__(self, live_zone_name="PROCESSING") -> None:
        self.console = Console(record=True)
        self.task_list = []
        self.live_table = my_table()
        self.live_table.add_column(live_zone_name)
        self.is_live = False
        self.is_progress = False

    def status(self, context):
        return self.console.status(context, spinner="aesthetic")

    def _add_task(self, task):
        self.task_list.append(task)

    def _remove_task(self, task):
        self.task_list.remove(task)

    @contextmanager
    def add_progress_to_live(self, context):
        if not self.is_progress:
            self.is_progress = True
            self.progress = Progress(
                transient=True, refresh_per_second=4, auto_refresh=False)
            self.progress.__enter__()
            self.live_table.add_row(self.progress)

        task = self.progress.add_task(context, start=False)
        self._add_task(task)
        yield task
        if self.progress.finished:
            self.progress.__exit__((None) ^ 3)
            self.is_progress = False
            self.live_table.remove_row(self.progress)
        self._remove_task(task)

    @contextmanager
    def add_status_to_live(self, context, spinner="aesthetic"):
        renderable_spinner = Spinner(name=spinner, text=context)
        self.live_table.add_row(renderable_spinner)
        self._add_task(renderable_spinner)
        if not self.is_live:
            self.live_thread = threading.Thread(target=self._start_live)
            self.live_thread.start()
        try:
            yield renderable_spinner
        except Exception as e:
            self.log(f"[red]UI ERROR when rendering the status -> {context}")
            # self.console.print_exception(show_locals=True)
        self.live_table.remove_row(renderable_spinner)
        self._remove_task(renderable_spinner)

    def _start_live(self):
        self.is_live = True
        with Live(self.live_table.generated_table(), console=self.console, refresh_per_second=4, transient=True) as live:
            while len(self.task_list) > 0:
                live.update(renderable=self.live_table.generated_table())
                time.sleep(0.25)

        self.is_live = False

    
    def log(self, context):
        return self.console.log(context)

    def save(self, path):
        self.console.save_html(path=path)


UI = _UI()

if __name__ == "__main__":
    
    ui = UI

    def task_1():
        with ui.add_status_to_live("程序启动") as status:
            ui.log("[green]all plugins mounted successfully")
            # time.sleep(1)
            # status.update(text="")
            for i in range(100):
                status.update(text=f"{i} files discovered")
                time.sleep(0.01)
            ui.log("[green]99 files discovered")

    def task_2():
        with ui.add_status_to_live("[blue]Computing the vague value", "dots") as status:
            time.sleep(1)
            ui.log("Start solution")
        with ui.add_progress_to_live("Downloading...") as progress:

            time.sleep(2)
    
    t = threading.Thread(target=task_1)
    t.start()
    time.sleep(0.5)
    t2 = threading.Thread(target=task_2)
    t2.start()

    t.join()
    t2.join()
