---
layout: default
title: "首页"
permalink: /
---

<section class="hero">
  <div class="hero__inner">
    <p class="hero__kicker">学习笔记与技术沉淀</p>
    <h2 class="hero__title">{{ site.title }}</h2>
    <p class="hero__desc">持续整理：工具使用、踩坑记录、读书与实践总结。</p>
    <div class="hero__actions">
      <label class="search" aria-label="Search">
        <span class="search__icon" aria-hidden="true">⌕</span>
        <input class="search__input" data-search="input" type="search" placeholder="搜索标题 / 标签 / 摘要…" autocomplete="off" />
      </label>
      <a class="button" href="{{ '/archive/' | relative_url }}">查看归档</a>
    </div>
  </div>
</section>

<h2 class="section-title">最新文章</h2>

{% assign posts = site.posts %}
{% if posts.size == 0 %}
<div class="empty">
  <p>暂无文章。请在 <code>_posts/</code> 下创建 <code>YYYY-MM-DD-title.md</code>。</p>
</div>
{% else %}
<div class="post-list">
  {% for post in posts limit: 20 %}
    {% assign tag_text = post.tags | join: ' ' %}
    {% assign desc_text = post.description | default: '' %}
    {% capture search_text %}{{ post.title }} {{ tag_text }} {{ desc_text }}{% endcapture %}
    <article class="post-card" data-search="item" data-search-text="{{ search_text | escape }}">
      <div class="post-card__meta">
        <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%Y-%m-%d" }}</time>
        {% if post.tags and post.tags.size > 0 %}
          <span class="post-card__dots" aria-hidden="true">·</span>
          <div class="post-card__tags">
            {% for tag in post.tags limit: 3 %}
              <span class="tag">{{ tag }}</span>
            {% endfor %}
            {% if post.tags.size > 3 %}
              <span class="tag tag--muted">+{{ post.tags.size | minus: 3 }}</span>
            {% endif %}
          </div>
        {% endif %}
      </div>
      <h3 class="post-card__title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
      {% if post.description %}
        <p class="post-card__excerpt">{{ post.description }}</p>
      {% else %}
        <p class="post-card__excerpt">{{ post.excerpt | strip_html | strip_newlines | truncate: 140 }}</p>
      {% endif %}
      <div class="post-card__cta">
        <a class="link" href="{{ post.url | relative_url }}">阅读 →</a>
      </div>
    </article>
  {% endfor %}
</div>
{% endif %}
