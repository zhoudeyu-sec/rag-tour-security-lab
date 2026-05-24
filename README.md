# RAG-Tour-Security-Lab

面向 **RAG 类 AI 应用** 的可复现安全评测靶场。在景区数字人导游场景下，验证 **知识库投毒** 与 **间接提示注入**，并对比 `baseline` 与 `hardened` 安全配置的攻击成功率（ASR）。

> 本项目由个人开发的「豆包 RAG 景区导游」升级而来，保留业务场景，新增安全模式开关、自动化评测与双轮实验归档。

---

## 实验结论（数据集 `all`，32 题 · 两轮复现）

| 轮次 | baseline ASR | hardened ASR | hardened 误杀率 |
|------|----------------|--------------|-----------------|
| **Run 1** | 85.0%（17/20） | 15.0%（3/20） | 0.0%（0/12） |
| **Run 2** | 85.0%（17/20） | 10.0%（2/20） | 8.3%（1/12） |

两轮 baseline ASR 一致（均为 85%），hardened 为 10% ~ 15%，攻击面在相同评测集上有所下降，但未降至零。Run 2 出现 1 例正常题被判定为过度拒绝（误杀率 8.3%），说明当前加固策略在可用性上仍有代价，详见 [EXPERIMENT.md](EXPERIMENT.md) 第 4.3 节。

**推荐阅读（与 README 同级）：**

- [EXPERIMENT.md](EXPERIMENT.md) — 双轮实验、误杀率思考、后期改进方向  
- [ARCHITECTURE.md](ARCHITECTURE.md) — 架构与威胁模型  

---

## 功能特性

- **三种安全模式**：`baseline` / `rag_poison_vuln` / `hardened`
- **32 条分层评测用例**：正常 12 + 间接注入 10 + RAG 投毒 10
- **Web Lab 控制台**：问答、检索预览、评测、统计
- **全量对话日志**：SQLite 持久化，支持导出
- **LLM**：火山引擎豆包 API

---

## 截图

### Run 1

![Lab 总览](images/image1.png)

![游客问答](images/image2.png)

![baseline 问答](images/image3.png)

![hardened 对比](images/image4.png)

![baseline 评测](images/image5.png)

![baseline ASR 结果](images/image6.png)

![hardened 评测](images/image7.png)

![hardened ASR 结果](images/image8.png)

![后台统计](images/image9.png)

![评测详情](images/image10.png)

### Run 2（清库复现）

![Run2 评测 baseline](images/run2/run2-01.png)

![Run2 评测结果](images/run2/run2-02.png)

![Run2 hardened 评测](images/run2/run2-03.png)

![Run2 hardened 结果](images/run2/run2-04.png)

---

## 快速开始

### 环境要求

- Python 3.10+
- 火山引擎豆包 API Key

### 安装与启动

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
python -m app.main
```

访问：**http://127.0.0.1:8000/** · Windows 可运行 [`scripts/start.bat`](scripts/start.bat)

### 运行评测

```bash
python ../eval/run_eval.py --mode baseline --dataset all
python ../eval/run_eval.py --mode hardened --dataset all
```

---

## 项目结构

```
rag-tour-security-lab/
├── README.md          # 项目概览
├── EXPERIMENT.md      # 实验报告（双轮结果、误杀率、改进方向）
├── ARCHITECTURE.md    # 架构与威胁模型
├── backend/           # FastAPI + RAG + 安全模式
├── eval/              # 评测集与 CLI
├── frontend/          # Lab Web 控制台
├── docs/              # 实验原始数据（结果、日志）
├── images/            # Run1 / Run2 截图
└── scripts/           # 启动脚本
```

---

## 文档与数据

| 文档 | 说明 |
|------|------|
| [EXPERIMENT.md](EXPERIMENT.md) | 双轮实验设计与分析 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 架构与威胁模型 |
| [docs/results/summary.json](docs/results/summary.json) | 结构化实验数据 |

---

## 合规声明

本项目仅供 **本地授权安全研究 / 教学演示**。请勿对未授权系统进行测试。仓库 **不包含** API 密钥。

---

## License

[MIT](LICENSE)
