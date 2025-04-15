# EvilEVE: Cognitively-Modeled Adversary Simulation Framework

_EvilEVE_ (Evolving Intrusion Logic via Empirical Vulnerability Exploitation) is a research-grade attacker simulation framework designed to evaluate the effectiveness of deception-based cybersecurity defenses—specifically, 
honeypots exploiting cognitive biases.

This simulator mimics human-like attacker behavior based on psychological profiles, decision modeling, and the MITRE ATT&CK framework. It enables reproducible, high-fidelity experiments 
comparing static and adaptive deception environments.

---

## Purpose

To evaluate the hypothesis:

> “Do adaptive honeypots leveraging cognitive bias exploitation result in greater attacker engagement, confusion, and behavioral observability than traditional static honeypots?”

---

##  Key Concepts & Decision Variables

| Variable               | Source                             | Impact                                                                 |
|------------------------|-------------------------------------|------------------------------------------------------------------------|
| **Deception Present**  | Experimental condition              | Increases attacker confusion and time waste                           |
| **Informed or Not**    | Experimental manipulation           | Affects attacker suspicion and confidence                             |
| **Confidence**         | CTQ (Cyber Task Questionnaire)      | Predicts decisiveness or hesitancy                                    |
| **Confusion/Frustration** | CTQ + logs + physiology         | Signals cognitive overload, changes strategy                          |
| **Belief in Deception**| Self-report / prompt-driven         | Drives strategic deviation                                             |
| **Touch/Probe/Scan**   | Decoy interaction logs              | Inferred attacker intent & engagement with deception                  |

---

##  Experimental Architecture

### Honeypot Setups (Testbed)

1. **Baseline T-Pot Deployment**
   - Static honeypots (Cowrie, Dionaea, Elasticpot)
   - No dynamic behavior or psychological tactics

2. **Adaptive Cognitive Bias Honeypot**
   - Dynamically adapts based on attacker behavior
   - Exploits Anchoring, Confirmation, and Overconfidence biases
   - Modifies honeypot exposure based on attacker psychological state

### Attacker Simulator: EvilEVE VM

- Completely isolated (no internet or production access)
- Receives **no prior knowledge** of target systems
- Simulates human attacker profiles and decision-making under uncertainty
- Executes against both honeypot configurations under identical conditions

---

## EvilEVE Configuration

### Psychological Profiling

Each attacker is initialized with:
- Confidence
- Frustration
- Self-Doubt
- Suspicion

These evolve dynamically across attack phases.

### Skill Level Unlocking

| Skill | Tools Available                              |
|-------|-----------------------------------------------|
| 0     | None                                          |
| 1     | `curl`, `wget`                                |
| 2     | Adds `httpie`                                 |
| 3     | Adds `nmap`, `sqlmap`                         |
| 4     | Adds `hydra`                                  |
| 5     | Full toolkit: `metasploit`, `ghidra`, etc.    |

### MITRE ATT&CK Phases

1. Reconnaissance  
2. Initial Access  
3. Execution  
4. Persistence  
5. Privilege Escalation  
6. Lateral Movement  
7. Collection  
8. Exfiltration  
9. Impact

### Execution Modes

- `--dry`: Logic only (no actual execution)
- `--real`: CLI tools executed in isolation
- `--bias`: Targeted bias-driven simulation (`anchoring`, `confirmation`, `overconfidence`)

---

## Getting Started

### Requirements

- Python 3.8+
- Isolated Linux VM
- Access to internal honeypot environment (via `--ip` argument)

### Launch a Simulation

```bash
python3 simulation.py --name bob --ip 192.168.X.X --seed 42 --phases 5 --bias anchoring

### METRICS COLLECTED:

Category | Examples
Deception Impact | Time in honeypots, tool failures, triggered decoys
Cognitive Influence | Trait drift (confidence, suspicion, etc.), hesitation events
Behavioral Drift | Tool switching, fallback attempts, repeated failed exploits
Engagement Outcomes | Exploit, Confusion, or Withdrawal classifications

### OUTPUTS:
Field | Description
Honeypot Setup Type | Baseline or Adaptive
Attacker Name | Simulation profile
Bias Mode | Anchoring / Confirmation / Overconfidence / None
Tools Used | CLI tools invoked
Time Wasted (sec) | Duration attacker spent in honeypots
Honeypot Services Hit | Count of decoy containers triggered
Psychological Drift | Change in core traits over time
Final Outcome | Exploit / Confusion / Withdrawal


All experiments are conducted in fully sandboxed environments using fictional attacker profiles and
no real-world targets. EvilEVE is a research-only simulator not intended for offensive use.

