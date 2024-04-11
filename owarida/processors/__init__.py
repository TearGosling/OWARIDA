from .arc import ArcProcessor
from .base import BaseProcessor
from .winogrande import WinograndeProcessor

PROCESSOR_MAP: dict[str, BaseProcessor] = {
    'arc_challenge': ArcProcessor(split_name='challenge'),
    'arc_easy': ArcProcessor(split_name='easy'),
    'winogrande': WinograndeProcessor()
}
