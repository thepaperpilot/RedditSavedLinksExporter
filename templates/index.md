# Saved Reddit Links by [{{ name }}](https://www.reddit.com{{ name }})
{% for link in links %}{% module Template("link.md", link=link) %}{% end %}
