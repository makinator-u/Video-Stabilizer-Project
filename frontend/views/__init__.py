"""Frontend window views strictly for the actual core functions of the project."""

from .home_view import render_home_portal
from .studio_view import render_studio_window
from .flow_view import render_flow_window
from .trajectory_view import render_trajectory_window
from .benchmark_view import render_benchmark_window

__all__ = [
    "render_home_portal",
    "render_studio_window",
    "render_flow_window",
    "render_trajectory_window",
    "render_benchmark_window",
]
