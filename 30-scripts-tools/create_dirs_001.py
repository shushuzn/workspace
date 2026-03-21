import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
from pathlib import Path
# Create directories
(Path('active_skills/agent-spectrum/references')).mkdir(parents=True, exist_ok=True)
(Path('active_skills/agent-spectrum/examples')).mkdir(parents=True, exist_ok=True)
print("Directories created")