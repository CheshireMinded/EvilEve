#!/bin/bash

echo "Creating EvilEVE modular project structure..."

# Base directories
mkdir -p evilEVE/{core,data,logs,attackers}

# Core Python modules
touch evilEVE/simulation.py
touch evilEVE/core/profile_manager.py
touch evilEVE/core/psychology.py
touch evilEVE/core/mitre_engine.py
touch evilEVE/core/reward_system.py
touch evilEVE/core/tool_executor.py
touch evilEVE/core/memory_graph.py
touch evilEVE/core/logger.py

# Data files
echo '{}' > evilEVE/data/cve_map.json

# Logs
LOG_FILE="evilEVE/logs/attack_log.csv"
if [ ! -f "$LOG_FILE" ]; then
  echo "timestamp,attacker_id,name,tool,target_ip,phase,success,suspicion,confidence,frustration,self_doubt,exit_code" > "$LOG_FILE"
  echo "📝 Created logs/attack_log.csv"
fi

# Sample attacker profile for demonstration
echo '{}' > evilEVE/attackers/sample_attacker.json

# Init __init__.py files for import structure (optional)
touch evilEVE/__init__.py
touch evilEVE/core/__init__.py

# Permissions
chmod -R 755 evilEVE

echo "EvilEVE modular project scaffolding complete!"
