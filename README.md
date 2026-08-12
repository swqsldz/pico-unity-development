# PICO Unity Development Skill

[中文](#中文) · [English](#english)

<a id="中文"></a>

## 中文

`pico-unity-development` 是面向 PICO XR 设备的 Unity 开发技能。它帮助 Codex
及其他兼容 Agent Skills 的编码代理，在有证据的前提下完成 PICO Unity Integration
SDK 或 Unity OpenXR Plugin 相关的开发、配置、审计、构建与故障排查。

覆盖范围包括项目与 SDK 配置、PXR Manager 和项目验证、Android Manifest 与权限、XR 场景、控制器/手部及身体、面部和眼动追踪、混合现实与空间感知、渲染和性能功能、Compositor Layer、平台服务、Android 构建、设备部署及 PICO 专属错误排查。

## 安装

先决条件：

- 使用 `npx skills` 安装：Node.js、npm/npx 和网络访问。
- 刷新本地官方文档语料：Python 3 和网络访问。
- 使用已安装且已刷新语料的 skill：不需要持续联网。

```bash
npx skills add swqsldz/pico-unity-development --skill pico-unity-development
```

可选的全局安装示例：

```bash
npx skills add swqsldz/pico-unity-development --skill pico-unity-development -g
```

首次使用时，skill 会在本地语料缺失时提示并运行刷新器。也可以进入安装后的 skill
目录手动刷新并校验：

```bash
python scripts/refresh_docs.py
python scripts/refresh_docs.py --check
```

使用示例：

```text
使用 $pico-unity-development 检查这个 Unity 项目的 PICO 手部追踪配置，并依据本地官方文档修复问题。
```

更新与卸载：

```bash
npx skills update pico-unity-development
npx skills remove pico-unity-development
```

更新后，在安装的 skill 目录运行刷新命令以获取最新官方文档。

## 仓库结构

```text
LICENSE
README.md
skills/
  pico-unity-development/
    SKILL.md
    agents/openai.yaml
    scripts/refresh_docs.py
    references/                 # 仅本地生成，未提交
```

技能说明见 [SKILL.md](skills/pico-unity-development/SKILL.md)，刷新器见 [refresh_docs.py](skills/pico-unity-development/scripts/refresh_docs.py)。生成的 `references/docs/`、`references/sources/`、`references/catalog.md` 和 `references/source-meta.json` 由 Git 忽略；仓库不分发约 410 篇 PICO 官方文档正文。

## 免责声明与来源

本项目不是 PICO 官方项目。PICO 官方文档不随本仓库分发，其内容及相关权利归各自权利人所有。刷新脚本会从 PICO 官方的[中文 Unity Integration 文档目录](https://developer-cn.picoxr.com/llmstxt/document/unity-integration/zh/llms.txt)和[英文 Unity Integration 文档目录](https://developer-cn.picoxr.com/llmstxt/document/unity-integration/en/llms.txt)下载本地副本；请遵守 PICO 的适用条款和政策。

仓库中的 MIT License 仅适用于本项目原创的 skill 指令、元数据、README 和刷新脚本，
不适用于下载到本地的 PICO 官方文档。

<a id="english"></a>

## English

`pico-unity-development` is a Unity development skill for PICO XR devices. It helps Codex and
other Agent Skills-compatible coding agents develop, configure, audit, build, and troubleshoot
projects that use the PICO Unity Integration SDK or the Unity OpenXR Plugin, using evidence from
a locally refreshed official corpus.

It covers project and SDK setup, PXR Manager and validation, Android manifests and permissions, XR scenes, controller/hand/body/face/eye tracking, mixed reality and spatial sensing, rendering and performance features, compositor layers, platform services, Android builds, device deployment, and PICO-specific Unity errors.

## Install

Prerequisites:

- Installing with `npx skills`: Node.js, npm/npx, and network access.
- Refreshing the local official corpus: Python 3 and network access.
- Using an installed skill with a refreshed corpus: no persistent network connection is required.

```bash
npx skills add swqsldz/pico-unity-development --skill pico-unity-development
```

Optional global-install example:

```bash
npx skills add swqsldz/pico-unity-development --skill pico-unity-development -g
```

On first use, the skill checks for a local corpus and prompts or runs the refresher when it is
missing. You can also refresh and verify it manually from the installed skill directory:

```bash
python scripts/refresh_docs.py
python scripts/refresh_docs.py --check
```

Example:

```text
Use $pico-unity-development to audit this Unity project's PICO hand-tracking setup and fix it against the local official documentation.
```

Update or remove the skill:

```bash
npx skills update pico-unity-development
npx skills remove pico-unity-development
```

After updating, refresh the corpus from the installed skill directory.

## Repository layout

```text
LICENSE
README.md
skills/
  pico-unity-development/
    SKILL.md
    agents/openai.yaml
    scripts/refresh_docs.py
    references/                 # generated locally only
```

See [SKILL.md](skills/pico-unity-development/SKILL.md) for the instructions and [refresh_docs.py](skills/pico-unity-development/scripts/refresh_docs.py) for the refresher. Generated `references/docs/`, `references/sources/`, `references/catalog.md`, and `references/source-meta.json` are ignored by Git; this repository does not distribute the roughly 410 PICO official document bodies.

## Disclaimer and sources

This is not an official PICO project. PICO official documentation is not distributed with this
repository; its content and related rights belong to their respective rightsholders. The refresh
script downloads local copies from PICO's official [Chinese Unity Integration documentation
directory](https://developer-cn.picoxr.com/llmstxt/document/unity-integration/zh/llms.txt) and
[English Unity Integration documentation
directory](https://developer-cn.picoxr.com/llmstxt/document/unity-integration/en/llms.txt).
Follow the applicable PICO terms and policies.

The repository's MIT License applies only to this project's original skill instructions,
metadata, README, and refresh script. It does not apply to PICO official documentation
downloaded locally.
