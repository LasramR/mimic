from os.path import isdir
from threading import Lock, Thread
from typing import Dict, List, Any

from .template import inject_variable
from ..utils.fs import ignore_glob
from ..utils.config import MimicPreview, MimicFileContentPreview, MimicVariable, MimicConfig

def _preview_file(source_file_path : str, variables : Dict[str, MimicVariable], variables_values : Dict[str, Any], mimic_template_preview : MimicPreview, mimic_template_preview_lock : Lock):
  try:
    changes : List[MimicFileContentPreview] = []
    with open(source_file_path, "r") as fd:
      lineno = 1
      for line in fd:
        striped_line = line.strip()
        parsed_line = inject_variable(striped_line, variables, variables_values).strip()
        if striped_line != parsed_line:
          changes.append(MimicFileContentPreview(striped_line, parsed_line, lineno))
        lineno += 1
  
    parsed_file_path = inject_variable(source_file_path, variables, variables_values)

    with mimic_template_preview_lock:
      mimic_template_preview.file_content_preview[source_file_path] = changes
      if source_file_path != parsed_file_path:
        mimic_template_preview.file_preview[source_file_path] = parsed_file_path
  except:
    pass

def preview_mimic_template(mimic_template_dir : str, mimic_config : MimicConfig, variables_values : Dict[str, Any]) -> MimicPreview:
  mimic_template_preview = MimicPreview()
  mimic_template_preview_lock = Lock()
  preview_file_threads = []

  for source_path in ignore_glob(mimic_config.template.ignorePatterns, root_dir=mimic_template_dir, include_hidden=True):
    if isdir(source_path):
      parsed_dir = inject_variable(source_path, mimic_config.template.variables, variables_values)
      if source_path != parsed_dir:
        mimic_template_preview.directory_preview[source_path] = parsed_dir
    else:
      source_file_preview_file_thread = Thread(
        target=_preview_file, 
        args=(source_path, mimic_config.template.variables, variables_values, mimic_template_preview, mimic_template_preview_lock)
      )
      preview_file_threads.append(source_file_preview_file_thread)
      source_file_preview_file_thread.start()

  for t in preview_file_threads:
    t.join()
  
  return mimic_template_preview