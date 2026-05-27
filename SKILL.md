---
name: resume-evidence-builder
description: Build job-tailored resumes from verifiable evidence, with requirement mapping, claim auditing, public portfolio review, source disclosure, and safe wording boundaries. Use when Codex needs to draft or revise a Chinese or English resume/CV for a target role, validate project claims against repositories or artifacts, create an evidence ledger, prepare a public proof-oriented portfolio, or disclose AI-assisted development without overstating results.
---

# Resume Evidence Builder

将岗位定制简历视为一项可核验的交付工作：先收集证据，再筛选能够写入简历的陈述，最后生成和复核成稿。

**公开验证入口：** [校验脚本](scripts/validate_evidence.py) | [多项目示例台账](references/example-public-portfolio-ledger.json) | [持续检查](https://github.com/LiTongShuo-edu/resume-evidence-builder/actions)

快速核验公开作品组合：

```powershell
python scripts/validate_evidence.py references/example-public-portfolio-ledger.json --strict-resume --check-public-links
```

## 工作流

1. 提取岗位要求。
   - 将招聘描述拆为编号明确、可映射的要求，例如语言基础、调试验证、领域工具或协作方式。
   - 区分硬性要求、加分项和无法通过当前材料证明的要求。
2. 盘点候选证据。
   - 优先检查公开仓库、可运行代码、测试记录、成品文档和已公开链接。
   - 为每条证据记录来源、定位方式、验证动作、实际结果和核验日期。
   - 不把本地私有路径、联系方式、证件信息、第三方未授权资料写入公开案例。
3. 建立证据台账。
   - 读取 [references/evidence-ledger.schema.json](references/evidence-ledger.schema.json) 并据此生成 JSON 台账。
   - 需要单项目示例时读取 [references/example-learningplusplus-ledger.json](references/example-learningplusplus-ledger.json)；需要多个公开项目组成的简历证据组合时读取 [references/example-public-portfolio-ledger.json](references/example-public-portfolio-ledger.json)。仅复用结构和表述边界，不照搬候选人事实。
4. 核验简历声明。
   - 对每条拟写入简历的声明选择 `verified`、`partially_verified`、`unverified` 或 `excluded`。
   - 只有 `verified` 且具备证据、验证方法、验证结果、核验日期和来源披露的声明可以写成确定性成果。
   - 将未验证事实删除、降级为事实范围内的表述，或标注为待补充材料。
5. 生成岗位定制简历。
   - 优先展示能直接对应岗位要求的已核验项目，使用可复现的数字和公开链接。
   - 对 AI 协作内容明确人工责任、生成/复现范围与验证结果，不把生成代码伪称为历史原作。
   - 为投递版控制篇幅；完整证据矩阵可留在作品仓库或附页中。
6. 发布前复核。
   - 运行校验器，修正全部错误后再引用台账生成简历。
   - 发布仓库后检查公开链接是否可访问；链接可访问只证明发布状态，不代替内容核验。
   - 若输出为 DOCX/PDF，按对应文档工作流渲染并逐页检查版面与链接。

## 表述边界

| 台账状态 | 可用于简历的表述 |
| --- | --- |
| `verified` | 直接陈述已验证事实，并给出证据入口或可解释的核验依据。 |
| `partially_verified` | 仅陈述实际核验覆盖的范围，不推广到未测能力或性能。 |
| `unverified` | 不写入最终简历成果；列为待补材料或待验证事项。 |
| `excluded` | 明确不公开或不使用的材料，例如隐私数据或无授权第三方内容。 |

## 使用资源

- `references/evidence-ledger.schema.json`：创建台账时遵循的公开数据契约。
- `references/example-learningplusplus-ledger.json`：包含公开仓库证据的脱敏示例。
- `references/example-public-portfolio-ledger.json`：包含多个公开作品、未验证硬件结论和排除材料的组合示例。
- `scripts/validate_evidence.py`：在写简历前检查台账结构、映射和发布链接。

在项目虚拟环境中运行：

```powershell
python scripts/validate_evidence.py references/example-learningplusplus-ledger.json --strict-resume
python scripts/validate_evidence.py references/example-public-portfolio-ledger.json --strict-resume --check-public-links
```

`--strict-resume` 会拒绝任何标为可写入简历但状态不为 `verified` 的声明。`--check-public-links` 仅检查 HTTP(S) 链接能否访问，不为链接中的事实背书。

## 交付检查

- 台账中的岗位要求编号唯一，声明引用的要求编号均存在。
- 写入简历的每项数字、能力和验证结论均来自 `verified` 声明。
- 公开作品仅包含获准公开的材料，AI 协作和资料来源边界表述清楚。
- 简历中的公开链接在发布后可访问，最终文档经过版面检查。
