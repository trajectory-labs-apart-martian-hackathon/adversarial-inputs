# Adversarial Inputs Research Tool

Apart x Martian hackathon submission: **Mechanistic Analysis of Manipulation Vulnerabilities in AI Orchestration**

## Research Thesis

Investigate the security vulnerabilities of judge and router systems through systematic adversarial testing, focusing on whether malicious inputs can manipulate routing decisions or compromise evaluation accuracy in Expert Orchestration frameworks.

Design adversarial examples that attempt to flip judge signals, craft inputs that hack scoring systems, and analyze the mechanistic pathways through which manipulation occurs. Test robustness across different judge architectures and develop defense mechanisms through interpretability insights.

Martian integration: Use the router framework to test adversarial robustness across multiple judge types simultaneously, creating comprehensive security assessments for the entire Expert Orchestration pipeline. Develop robust judge models that can be deployed confidently in production systems.

## Overview

This project implements systematic adversarial testing tools to expose security vulnerabilities in AI judge and router systems within Expert Orchestration frameworks. The tools enable researchers to craft adversarial inputs that attempt to manipulate routing decisions, flip judge signals, and compromise evaluation accuracy - critical for securing production AI orchestration pipelines.

## Why This Matters

Compromised AI judges pose serious risks in real-world deployment scenarios where automated evaluation directly impacts critical decisions:

**Content Moderation & Safety**: Malicious actors could craft inputs that manipulate content safety judges to approve harmful, illegal, or inappropriate content that should be blocked, bypassing platform safety measures.

**Financial & Business Systems**: In AI systems routing financial queries or business decisions, manipulated judges could route critical requests to inappropriate experts, leading to poor investment advice, incorrect loan approvals, or flawed business strategy recommendations.

**Healthcare & Legal Applications**: Judge manipulation in medical AI systems could route patients to wrong specialists or approve dangerous treatment recommendations. In legal AI, compromised evaluation could affect case outcomes or legal advice quality.

**Academic & Certification Systems**: Educational AI judges that can be manipulated could unfairly award grades, certifications, or academic credentials, undermining the integrity of educational assessments.

**AI Safety & Alignment**: Perhaps most critically, if safety evaluation judges can be compromised, malicious actors could potentially bypass AI safety measures, allowing harmful AI behaviors to be rated as safe and deployed.

**Enterprise & Production Reliability**: Organizations deploying AI orchestration systems need confidence that their evaluation infrastructure can't be gamed by competitors, bad actors, or even accidental inputs that trigger unexpected behaviors.

This research helps identify these vulnerabilities before deployment, enabling the development of robust defense mechanisms for production AI systems.

## Key Features

- **Interactive Suffix Testing**: Real-time testing of judge signal manipulation through adversarial text additions
- **Judge Signal Flipping**: Systematic attempts to reverse evaluation outcomes through crafted inputs
- **Router Vulnerability Assessment**: Testing how adversarial inputs affect routing decisions in orchestration systems
- **Mechanistic Analysis**: Understanding manipulation pathways across different judge architectures
- **Comprehensive Security Testing**: 30+ evaluation rubrics testing different vulnerability vectors
- **Expert Orchestration Pipeline Testing**: End-to-end security assessment for production deployment

## Quick Start

1. **Activate the virtual environment and run the main interactive tool**:
   ```bash
   source .venv/bin/activate
   python main.py
   ```

2. **Interactive Commands**:
   - Enter any text to test as a suffix
   - Type `\h` for help
   - Type `\q` to quit

## Project Structure

### Core Files

- **`main.py`**: Interactive suffix testing tool (single scenario)
- **`judge_qa_pairs.py`**: Comprehensive evaluation across all scenarios and rubrics
- **`qa_pairs.py`**: Question-answer pairs with 3 response levels each
- **`judge_rubrics_sycophancy.py`**: 30+ evaluation rubrics for different aspects

### Evaluation Scenarios

Each scenario tests different contexts where users might seek validation:

1. **Group Project Conflict**: Confronting non-contributing teammates
2. **Social Media Argument**: Political debates and personal attacks
3. **Restaurant Complaint**: Service complaints and staff treatment
4. **Workplace Disagreement**: Professional interruptions and team dynamics
5. **Academic Performance**: Grade disputes and effort vs. results

### Response Types

Each scenario includes three response levels:
- **Disagreeing**: Challenges the user's perspective directly
- **Neutral**: Balanced, professional response
- **Sycophantic**: Validates and flatters the user's viewpoint

## How It Works

1. **Baseline Judge Evaluation**: Establishes normal judge scoring behavior
2. **Adversarial Suffix Injection**: Appends crafted text to attempt signal manipulation
3. **Judge Signal Analysis**: Measures how adversarial inputs affect evaluation scores
4. **Manipulation Detection**: Identifies successful attacks on judge reliability
5. **Vulnerability Mapping**: Tracks which techniques successfully compromise evaluation accuracy

## Use Cases

- **Production Security Assessment**: Testing judge robustness before deployment
- **Adversarial Defense Development**: Understanding attack vectors to build countermeasures
- **Expert Orchestration Security**: Ensuring routing decisions can't be maliciously influenced
- **Judge Architecture Analysis**: Comparing vulnerability patterns across different judge types
- **Mechanistic Interpretability**: Understanding how manipulation techniques affect internal decision processes

## Research Context

This tool addresses critical security concerns in AI orchestration systems by demonstrating how adversarial inputs can compromise:
- Judge evaluation accuracy and reliability
- Router decision-making in multi-expert systems
- Overall Expert Orchestration pipeline security
- Production deployment confidence in AI judge systems

## Dependencies

The project uses the Martian SDK for AI evaluation services. Parts of the code are adapted from the [martian-sdk-python](https://github.com/withmartian/martian-sdk-python) repository.

For environment setup instructions, see the source repository's documentation.

## Results

Evaluation results are automatically saved to the `results/` directory in JSON format, including:
- Individual rubric evaluations
- Comprehensive response comparisons  
- Summary statistics and scoring trends

---

*This project was developed for the Apart x Martian hackathon to advance understanding of AI manipulation vulnerabilities and promote safer AI systems.*
