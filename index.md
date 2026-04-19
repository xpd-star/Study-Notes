---
layout: default
title: "首页"
permalink: /
---

## 最新文章

{% assign posts = site.posts %}
{% if posts.size == 0 %}
暂无文章。请在 `_posts/` 下创建 `YYYY-MM-DD-title.md`。
{% else %}
<div class="post-list">
  {% for post in posts limit: 20 %}
    <article class="post-card">
      <div class="post-card__meta">
        <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%Y-%m-%d" }}</time>
      </div>
      <h3 class="post-card__title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
      {% if post.description %}
        <p class="post-card__excerpt">{{ post.description }}</p>
      {% else %}
        <p class="post-card__excerpt">{{ post.excerpt | strip_html | strip_newlines | truncate: 140 }}</p>
      {% endif %}
      {% if post.tags and post.tags.size > 0 %}
        <div class="post-card__tags">
          {% for tag in post.tags %}
            <span class="tag">{{ tag }}</span>
          {% endfor %}
        </div>
      {% endif %}
    </article>
  {% endfor %}
</div>
{% endif %}

