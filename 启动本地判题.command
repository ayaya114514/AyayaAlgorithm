#!/bin/zsh
cd "${0:A:h}"
if [[ -f "$HOME/miniforge3/etc/profile.d/conda.sh" ]]; then
  source "$HOME/miniforge3/etc/profile.d/conda.sh"
else
  print "未找到 miniforge3。请先按 README 准备 conda 环境。"
  exit 1
fi
conda activate ai_env
python scripts/start.py "$@"
