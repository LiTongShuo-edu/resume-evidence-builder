# Resume Evidence Builder

[![Validate Evidence Skill](https://github.com/LiTongShuo-edu/resume-evidence-builder/actions/workflows/validate.yml/badge.svg)](https://github.com/LiTongShuo-edu/resume-evidence-builder/actions/workflows/validate.yml)

`resume-evidence-builder` 是一个 Agent Skill，用于把项目资料、公开链接和验证记录整理为结构化的证据台账，并在撰写介绍材料前检查陈述是否有可追溯依据。它适用于作品集说明、项目总结、成果页面和简历等需要区分“已验证事实”与“待确认表述”的场景。

## 功能

- 使用 JSON 台账记录项目、需求映射、公开证据、验证方法和核验日期。
- 通过严格模式拒绝将未验证或明确排除的材料写成确定性成果。
- 可检查台账中引用的公开 HTTP(S) 链接是否可访问。
- 提供单项目与多项目的脱敏示例，便于复用数据结构和书写边界。
- 作为 Agent Skill 提供完整工作流说明，供自动化写作或人工整理时参考。

## 目录结构

| 路径 | 内容 |
| --- | --- |
| [`SKILL.md`](./SKILL.md) | Skill 使用说明、工作流与表述边界 |
| [`references/evidence-ledger.schema.json`](./references/evidence-ledger.schema.json) | 证据台账数据约定 |
| [`references/example-learningplusplus-ledger.json`](./references/example-learningplusplus-ledger.json) | 单项目示例台账 |
| [`references/example-public-portfolio-ledger.json`](./references/example-public-portfolio-ledger.json) | 多项目示例台账，包含未验证及排除材料的处理方式 |
| [`scripts/validate_evidence.py`](./scripts/validate_evidence.py) | 台账结构、声明状态和公开链接校验器 |
| [`tests/`](./tests/) | 校验规则的自动测试 |

## 快速开始

仓库中的脚本仅使用 Python 标准库。建议在虚拟环境中执行：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe scripts\validate_evidence.py references\example-learningplusplus-ledger.json --strict-resume
.\.venv\Scripts\python.exe scripts\validate_evidence.py references\example-public-portfolio-ledger.json --strict-resume --check-public-links
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 台账状态

| 状态 | 用途 |
| --- | --- |
| `verified` | 验证方法与结果完整，可在其已验证范围内直接引用 |
| `partially_verified` | 仅有部分覆盖，应限制表述范围 |
| `unverified` | 尚无验证依据，不作为确定性结论输出 |
| `excluded` | 因隐私、授权或公开边界原因明确排除 |

使用 `--strict-resume` 时，任何标记为可写入成稿、但状态不是 `verified` 的声明都会导致校验失败。使用 `--check-public-links` 时，脚本只检查链接可访问性，不判断链接内容是否足以支持具体陈述。

## 作为 Skill 使用

`SKILL.md` 定义了从资料盘点、台账整理、声明校验到最终文档复核的完整流程。安装为 Agent Skill 后，可在涉及资料核验和证据化写作的任务中调用该工作流。

## 测试与持续集成

GitHub Actions 会创建虚拟环境，验证仓库中的示例台账及其公开链接，并运行自动测试。测试覆盖多项目台账、未验证声明拒绝、排除材料限制和链接枚举检查。

## 公开数据说明

示例文件只保留用于说明数据结构与校验规则的公开或脱敏内容。实际使用时，应自行确认资料授权、隐私范围和陈述所依据的验证结果。
