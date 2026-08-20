<!-- 建议标题：pysysmlv2 长期路线：从 SysML v2 textual AST 基础设施到语义模型、状态机发现与 stm-model-checker -->

# 背景与目标

`pysysmlv2` 的定位是开源、纯 Python、可随 wheel 发布的 SysML v2 textual language 基础设施，为后续精确发现状态机模型、建立结构检查能力并开发 `stm-model-checker` 提供稳定地基。本 issue 记录整个项目的目标、分层边界、官方证据、当前初始化交付、未完成工作和可验收的阶段计划；它不是把当前 parser 或 AST 冒充为完整 SysML 语义实现，也不是把结构诊断冒充为时序模型检查。

最终要求是：ANTLR 只负责语法前端，Python 侧必须能够取得结构完整、可定位、可比较、可 round-trip 的 source AST，并在其上建立 Python 原生 semantic model、workspace linking、symbol resolution 和状态机中间表示。任何状态机发现和检查结果都必须能够回溯到对应的 SysML 元素、文件和 source span；不能只返回脱离源代码的匿名 state 或 transition。

# 当前基线

截至 2026-08-21，初始化工作位于 `codex/foundation-ast-parser` 分支，当前提交以 PR #2 的最新 head 为准，PR 为 [#2](https://github.com/HansBug/pysysmlv2/pull/2)，主规划 issue 为 [#1](https://github.com/HansBug/pysysmlv2/issues/1)，grammar overlay 调查和更正记录在 [#3](https://github.com/HansBug/pysysmlv2/issues/3)。PR #2 当前为 OPEN、非 draft；旧提交的 workflow 结果不能代替当前提交的 CI 证据。

当前 pinned grammar submodule 是 `daltskin/sysml-v2-grammar` 的 `v2026.05.0`，commit 为 `7292dc39983a6d263d14f8f6689de0f3b35db5eb`；本项目使用 ANTLR 4.13.2 生成 Python lexer/parser，并把生成代码随 wheel 发布，因此安装运行时不需要 Java。`pysysmlv2/syntax/generated/` 是 generated-only 目录，grammar 只能通过 submodule、外层 overlay 和 `make antlr_update`/`make antlr_build` 变更。

# 范围边界

本仓库当前只承诺 SysML v2 textual language frontend；KerML 文档、KerML-only grammar extension 和 KerML 独立 frontend 不属于当前 parser contract，不能因为共享 OMG 语言基础就隐式加入。AST 是带 concrete-syntax 选择和 provenance 的 source AST，不等同于 OMG normative abstract semantic model；workspace、semantic model 和下游 checker 才负责 identity、namespace、membership、resolved reference、derived relationship 和诊断归属。

普通空白和 trivia-preserving formatting 不属于 AST 契约，但 SysML 模型本体中的 documentation、model-owned comment 和 textual representation 等元素不能丢失。`ASTNode` 只持有 `span`，可选 `source_path` 由 `SourceSpan` 承担；span 不参与 equality，grammar 必需字段必须是必需构造参数，只有语法真正可缺省的字段才能使用默认值或 `Optional`。每个公开 concrete node 必须显式声明可读的 snake_case 字段、实现自身的 `to_sysml()` 和 `__str__()`，表达式、语句、动作、控制节点、transition 和 state body 必须按 parser production 粒度拆解；不能把任意节点声明为裸 `ASTNode`，也不能以反射、动态字段表或自动 source-text scanning 代替 listener 组装。

# 官方证据与语法纪律

规范基线必须区分 OMG 正式 PDF、OMG Release 仓库的 informative KEBNF、官方 Pilot 参考实现、daltskin ANTLR grammar 和本地 compatibility overlay，不能把其中一个来源的版本或性质误写成另一个来源。主要证据包括 [OMG SysML 2.0 Language PDF](https://www.omg.org/spec/SysML/2.0/Language/PDF)、[OMG 2026-05 KEBNF](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/SysML-textual-bnf.kebnf)、[pinned daltskin parser grammar](https://github.com/daltskin/sysml-v2-grammar/blob/7292dc39983a6d263d14f8f6689de0f3b35db5eb/grammar/SysMLv2Parser.g4)、[official Pilot 2026-05](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.sysml.xtext/src/org/omg/sysml/xtext/SysML.xtext#L1866-L1882) 和 [official Intro textual notation PDF](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/doc/Intro%20to%20the%20SysML%20v2%20Language-Textual%20Notation.pdf)。PDF 例子必须由人工逐页核对后复制到本地 test fixture，测试时不能直接依赖网络、PDF 自动提取结果或 upstream checkout。

target transition 的规范结论已经收紧并固定：`TargetTransitionUsage` 只允许 trigger 后跟可选 guard，或者 guard-only；本项目已撤销错误添加的 target guard-before-trigger overlay、对应 provenance 和 listener/AST 分支。正式 OnOff5 是 `accept ... if ... then ...` 的 target shorthand；OnOff4 的 `transition ... if ... accept ... then ...` 是完整 `TransitionUsage`，完整 transition 的 `guard_before_trigger` 支持必须保留。该更正不影响其他独立调查项，例如完整 transition 的 guard-first、历史 effect semicolon 兼容和 terminate dispatch；这些项必须分别记录证据和版本状态，不能混为一个 target 规则。

# 已完成的初始化交付

- 使用 pinned grammar submodule、可重复的 ANTLR 生成链、provenance、上游许可证复制和生成漂移检查，生成产物随 package 发布。
- 提供结构化 lexer/parser diagnostics、`parse()`、`parse_as_ast_node()`、可指定 grammar entry 的局部解析、source-aware `SourceSpan`、手写 `SysMLAstListener`、显式 source AST 和 canonical `str(node)` round-trip。
- 提供 package、documentation、comment、state、state subaction、transition、expression、statement、action/control 节点的当前 AST slice，以及 workspace、semantic、formatter、query 和 Click CLI 的边界 placeholder。
- 建立严格源码镜像测试目录、英文 reStructuredText docstring、详细 module/init roadmap、双语 Sphinx、`rst_auto`、Makefile help、ANTLR/build/package smoke 和 `AGENTS.md -> CLAUDE.md` 真实 symlink。
- 本地保留 2026-03-02 人工复核的 OMG SysML 2.0 Language PDF inventory，共 275 个可执行 source entries 和 147 个明确排除记录；保留 Intro textual notation PDF 的 167 个 slide 资产及页面解说注释；复制 OMG 2026-05 Release 中 251 个 `.sysml` 官方模型到 `test/testfile`，测试不直接读取 upstream。
- Section 7.18 当前有 22 个提交的 parser-derived AST snapshot，其中 11 个状态/动作样例另有独立手写字段级 oracle；Section 8.4 的 8 个纳入样例具备独立字段级 AST/round-trip 回归，其他人工 ledger fixture 目前主要提供 source-preservation 与 fixed-point 回归。AST 和 listener 的专门 branch coverage 门禁要求 100%。这些数字代表当前已固化的本地资产，不代表完整 SysML 语义模型已经完成。
- 导出的 `RawElement` 语法兼容节点已登记在 `docs/research/raw_element_compatibility_ledger.json`，每条记录包含 production、listener callback、保留理由、回归测试和后续 typed-node 任务；它不是语义模型节点，核心 state/action/transition/expression/import/alias/filter/connection/interface 路径有专门回归，不能把该兼容桥接当成语义模型。

# 目标架构

1. Syntax frontend 层只负责 lexer、parser、parse tree、结构化语法诊断、错误位置和 entry-point 解析；生成的 ANTLR context/listener 不作为长期公共模型。
2. Source AST 层由手写 dataclass 和显式 listener 组成，负责 concrete syntax、模型本体中的文档/注释元素、source span、字段级 equality 和 canonical SysML export；AST 不负责跨文件 identity、解析引用或语义约束。
3. Workspace 层负责 request-local documents、URI/path canonicalization、import 资产、依赖图、重建边界和 AST 到语义对象的源映射。
4. Semantic model 层定义 Python 原生的 document、namespace、element identity、definition/usage、feature、membership、specialization、reference、import、alias、redefinition 和诊断对象，并实现 qualified/unqualified name resolution、missing/ambiguous reference 诊断和可序列化 snapshot。
5. State-machine extraction 层在 semantic model 之上发现任意 namespace 或 behavior 角落中的 state machine，定义 machine、region、state、pseudo-state、transition、trigger、guard、effect、hierarchy、concurrency 和 source mapping 的独立 IR。
6. `stm-model-checker` 层只依赖 semantic snapshot 和 state-machine IR，输出带 rule id、severity、message、元素 identity、source path/span、关联 SysML 元素和可选修复建议的稳定结果，不把 checker 逻辑倒灌进 parser/AST。

# 分阶段计划

## Phase 0：基础设施收敛

保持当前生成链、AST/listener、CLI、workspace/semantic placeholder、双语 docs、测试资产和跨平台 workflow 可重复运行；修正 target transition 后，所有 provenance、generated parser、AST golden、listener expectation、README、CLAUDE 和 architecture 文档保持一致。每次 grammar 或 ANTLR tool 更新都运行 `make antlr_update`、`make antlr_check`、全量 unit/doctest、官方 fixture、docs 和 package gates。

## Phase 1：完整 typed source AST 与 grammar conformance

为 pinned SysML v2 grammar 的每个需要进入公共模型的 parser production 建立明确 AST node、字段、listener callback、span 和 round-trip renderer；逐步清理 `RawElement`/lossless fallback，禁止下游依赖 opaque node。表达式必须拆到 literal、reference、operator、call、index、member access、constructor、metadata、cast、arrow、argument list 和 body expression 等最小语法粒度；Action/State/Transition 的不同 declaration、usage、effect 和 target 形式不得擅自合并。

把 OMG Language PDF、Intro PDF 和官方 2026-05 Release 中所有可形成完整语法上下文的例子登记为本地 fixture；每个 fixture 必须有人工来源记录、完整 AST golden 或手写 expected AST、逐字段 equality、span 排除规则、round-trip 再解析和 canonical fixed point 断言。上下文片段、图形说明、PDF 历史 typo、KerML-only 内容和当前 grammar 明确不适用的记录不得静默丢弃，必须保留 source text、排除原因和后续处理状态。251 个 release 文件不能只做 parse/no-diagnostic 或 fixed-point 断言，至少应建立按 production/语义类别可审计的字段级 oracle 覆盖矩阵。

## Phase 2：Workspace、semantic model 与 symbol resolution

先实现最小、稳定、可演进的 Python semantic metamodel，再逐步补充 OMG metaclass 映射、namespace、membership、import、alias、specialization、redefinition、feature typing、definition/usage 和 reference 关系。所有对象必须可以反查源 AST 节点和 `SourceSpan`，能够生成 JSON-like snapshot 供下游算法使用；AST 与 semantic model 的映射不能通过丢失 concrete source provenance 来换取便利。

## Phase 3：状态机发现与结构检查

盘点 state definition/usage、composite/parallel region、entry/exit/do/during action、transition、trigger、guard、effect、initial/final/junction/choice、exhibit、继承/重定义、跨文件 import 和嵌套 behavior 等实际形态，定义与 SysML 元素一一映射的 state-machine IR。首批 STM checks 只覆盖可证明的结构性质，例如 missing initial、unknown target、ambiguous reference、unreachable state、dead-end、非法 region/transition ownership 和不允许的 hierarchy/concurrency 组合；时序性质和完整 model checking 另立设计和验证范围。

## Phase 4：`stm-model-checker` 集成

冻结 checker input/output contract，要求每个 finding 带 rule id、severity、message、machine/state/transition identity、source path/span、相关 SysML AST/semantic 元素和可选修复建议。使用固定 corpus、AST/semantic goldens、diagnostic goldens、round-trip fixtures、grammar version compatibility tests 和跨平台 package smoke，防止 grammar 小版本更新导致状态机发现结果静默改变。

# 验收标准

- `make help` 完整列出安装、ANTLR、RST、docs、测试、doctest、format、lint、package 和 clean 工作流；`make test` 是 `make unittest` alias，`make unittest RANGE_DIR=...` 能对源码镜像目录执行局部测试并输出 `coverage.xml` 与 terminal `term-missing`。
- `make format_check`、`make lint`、`make unittest`、`make doctest`、`make test`、`make rst_auto_check`、`make docs_check`、`make antlr_check`、`make package_check` 全部通过；AST 和 listener 专门 branch coverage 为 100%，生成目录不进入 Ruff 和 coverage，但 ANTLR build 后生成 Python 文件必须经过 Ruff format。
- 所有公开 AST/listener/parser API 使用英文 pyfcstm 风格 reST docstring，module/init docstring 是详细 roadmap，文档生成不靠手写重复 API 页面；README 保持英文，规划 issue 使用中文且不做人为硬换行。
- Linux、Windows、macOS 上的 CPython 3.7-3.14 全矩阵继续运行 runtime/test；同时补充至少一个 Windows/macOS 的 wheel build/install/import smoke，使“跨平台支持”不只由纯 pytest 运行证明。ANTLR regeneration、docs 和 package check 可保留单独的维护者 Linux job，但必须明确其覆盖边界。
- wheel 安装后不需要 Java，generated parser/provenance/license/package data 完整；submodule revision、ANTLR version、grammar effective hash 和 overlay evidence 可由 `make antlr_check` 复核。
- 官方来源资产全部复制到 `test/testfile` 或明确的本地 research ledger，测试 collection 不访问网络、upstream checkout 或外部 PDF；每个排除项都有可复核原因，每个纳入项都有来源页/条款/fixture 映射。
- TargetTransitionUsage 严格保持 trigger-before-guard 或 guard-only；完整 TransitionUsage 的 guard-first 仍可解析和 round-trip；非规范 target guard-first 不被项目有意接受，相关测试和文档不得重新引入错误 provenance。
- 在 Phase 1 的 typed AST、Phase 2 的 semantic snapshot/symbol resolution、Phase 3 的 state-machine IR/structural checks 和 Phase 4 的 checker contract 均有实现、文档、测试、source mapping、round-trip 和 CI 证据之前，不关闭本总规划 issue；每一阶段拆成独立 issue/PR 并回链。

# 当前已知限制与风险

当前 `pysysmlv2/syntax/listener.py` 仍有面向未完成 production 的 `_raw_store`/`RawElement` 兼容路径；`RawElement` 虽从语法包导出以便调用方明确识别和拒绝，但不是语义模型 API。CLAUDE 中的“最终不得依赖 opaque fallback”是目标纪律，不应被当前 fixed-point round-trip 误解为已完成的全量 typed AST。当前官方 251 文件测试证明的是本地复制资产可被 parser 接受并达到 AST round-trip fixed point，不等价于每个文件都有独立的语义正确性 oracle；当前 275/147 manual inventory 也区分了可执行完整例子和上下文/图形/历史记录，不能把排除记录宣称为 parser 已支持。

当前 GitHub Actions 的 runtime/test matrix 是 3 个 host 乘 8 个 Python line，共 24 个跨平台 test job；quality/generated、docs、package smoke 和 Codecov upload 只在 Ubuntu 22.04/Python 3.12 执行，且 Codecov action 配置为 `fail_ci_if_error: true`。这证明现有 CI 已覆盖运行时兼容性和主流程，但尚不足以证明三个平台都能 build/install wheel、运行 docs 或重生成 ANTLR；后续验收必须保留这一事实边界。

SysML 2.0 PDF、2026-05 Beta 1 release、KEBNF、Pilot 和 daltskin grammar 可能存在版本差异或历史示例/grammar 矛盾；每次采用 overlay 都必须给出固定 commit、条款/行号、输入探针、规则差异、AST 影响和测试证据。不得把 informative KEBNF、历史 issue 或第三方实现单独升级为当前 normative standard；不得向 OMG 或 daltskin 重复提交已被核实为本地错误分类的 target guard-first 问题。

# 完成定义

当上述四个阶段的实现和证据链完整、全部适用官方例子拥有可审计的 AST/semantic 断言、状态机 IR 与 checker contract 已能稳定消费 Python 侧模型、所有文档和 workflow gates 持续通过，并且 PR review 和 CI 状态为可合并时，才认为 `pysysmlv2` 初始化及长期路线真正 ready；在此之前，本 issue 保持开放并作为阶段 issue 的总索引。
