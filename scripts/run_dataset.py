from label import label
from download import download
from show_samples import show
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s', )

#download(start_again=True, auto_resize=False)
label()
show()