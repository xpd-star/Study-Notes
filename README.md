# Study-Notes

学习笔记与技术沉淀，使用 Markdown 维护，直接在 GitHub 仓库中阅读。

## 目录结构

- [posts](./posts)：博客/笔记 Markdown（建议按 `YYYY-MM-DD-title.md` 命名）
- [images](./images)：图片资源（在 Markdown 中引用）
- [README.md](./README.md)：项目说明
- [LICENSE](./LICENSE)：许可证

## 写作规范（建议）

- 文件命名：`YYYY-MM-DD-title.md`（小写英文 + 连字符，避免空格，便于稳定链接与检索）
- 标题建议：文件首行使用 `# 标题`；或直接用文件名表达主题
- 目录组织：后续若文章增多，可以在 `posts/` 下按主题再分子目录（例如 `posts/python/`），但仍建议保留日期前缀

## 新增一篇笔记

1. 在 `posts/` 下新建文件，例如：`2026-04-19-my-first-note.md`
2. 直接使用 Markdown 编写内容
3. 引用图片（推荐相对路径）：

```md
![示例图片](../images/citeImage.png)
```

## 常用写法

### 图片引用

- 从 `posts/` 下的文章引用图片：

```md
![图示](../images/citeImage.png)
```

### 内部链接

- 文章之间互相引用（同目录）：

```md
[另一篇笔记](./2026-04-19-welcome.md)
```

## 阅读方式

- 进入 `posts/` 目录按文件列表阅读
- 或使用 GitHub 的搜索功能按关键字检索
