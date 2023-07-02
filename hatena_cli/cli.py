from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)


class Spinner(Progress):
    def __init__(self):
        super().__init__(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        )


class ProgressBar(Progress):
    def __init__(self):
        super().__init__(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(elapsed_when_finished=True),
        )
