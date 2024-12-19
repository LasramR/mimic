from os import sep, walk
from os.path import join
from threading import Lock, Thread
from typing import Dict, List, Any

from .template import inject_variable
from ..utils.fs import get_file_without_extension, is_file_of_extension
from ..utils.config import MimicPreview, MimicFileContentPreview

def _preview_file(source_file_path : str, variables : Dict[str, Any], mimic_template_preview : MimicPreview, mimic_template_preview_lock : Lock):
  try:
    changes : List[MimicFileContentPreview] = []
    with open(source_file_path, "r") as fd:
      lineno = 1
      for line in fd:
        striped_line = line.strip()
        parsed_line = inject_variable(striped_line, variables).strip()
        if striped_line != parsed_line:
          changes.append(MimicFileContentPreview(striped_line, parsed_line, lineno))
        lineno += 1
  
    parsed_file_path = sep.join(map(lambda d : get_file_without_extension(d), inject_variable(source_file_path, variables).split(sep)))

    with mimic_template_preview_lock:
      mimic_template_preview.file_content_preview[source_file_path] = changes
      if source_file_path != parsed_file_path:
        mimic_template_preview.file_preview[source_file_path] = parsed_file_path
  except:
    pass

def preview_mimic_template(mimic_template_dir : str, variables : Dict[str, Any]) -> MimicPreview:
  mimic_template_preview = MimicPreview()
  mimic_template_preview_lock = Lock()
  preview_file_threads = []

  for root, dirnames, filenames in walk(mimic_template_dir):
    for dirname in dirnames:
      if is_file_of_extension(dirname):
        source_dir = join(root, dirname)
        parsed_dir = get_file_without_extension(inject_variable(source_dir, variables))
        
        if source_dir != parsed_dir:
          mimic_template_preview.directory_preview[source_dir] = parsed_dir

    for filename in filenames:
      if is_file_of_extension(filename):
        source_file_path = join(root, filename)
        source_file_preview_file_thread = Thread(
          target=_preview_file, 
          args=(source_file_path, variables, mimic_template_preview, mimic_template_preview_lock)
        )
        preview_file_threads.append(source_file_preview_file_thread)
        source_file_preview_file_thread.start()

  for t in preview_file_threads:
    t.join()
  
  return mimic_template_preview