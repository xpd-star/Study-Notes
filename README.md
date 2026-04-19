# Study-Notes（Jekyll + GitHub Pages）

本仓库用于通过 Markdown 编写文章，并通过 GitHub Pages 发布到：

`https://<username>.github.io/Study-Notes/`

## 目录结构

- `_posts/`：文章（文件名必须为 `YYYY-MM-DD-title.md`）
- `_layouts/`：布局（`default.html` / `post.html` / `archive.html`）
- `_includes/`：复用片段
- `assets/`：静态资源（CSS/JS/图片）
- `.github/workflows/jekyll.yml`：Actions 自动构建与部署

## 写作规范

文章示例：

```yaml
---
layout: post
title: "标题"
date: 2026-04-19 10:00:00 +0800
tags: [tag1, tag2]
description: "摘要（可选）"
---
```

## 本地预览

建议使用 Ruby 3.1（与 GitHub Pages/Jekyll 工作流保持一致）。

```bash
bundle install
bundle exec jekyll serve
```

本地访问：`http://127.0.0.1:4000/Study-Notes/`

## GitHub Pages 部署

1. 仓库 Settings → Pages → Build and deployment 选择 `GitHub Actions`
2. 推送到 `main` 分支后会自动构建并部署
