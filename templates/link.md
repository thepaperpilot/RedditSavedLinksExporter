{% autoescape None %}{% if link["self"] == "True" %}
## [{{ link["link_title"] }}]({{ link["link_url"] }})
submitted by [{{ link["link_author"] }}](https://www.reddit.com/user/{{ link["link_author"] }}) in [{{ link["subreddit"] }}](https://www.reddit.com/r/{{ link["subreddit"] }}) with [{{ link["num_comments"] }} comments]({{ link["permalink"] }})
{{ link["body_md"] }}
>
> [{{ link["author"] }}](https://www.reddit.com/user/{{ link["author"] }}) [permalink]({{ link["comment_permalink"] }}){% else %}
## [{% if (link["thumbnail"] != None) & (link["thumbnail"] != "self") & (link["thumbnail"] != "default") & (link["thumbnail"] != "") %}![]({{ link["thumbnail"] }}) {% end %}{{ link["title"] }}]({{ link["url"] }})
submitted by [{{ link["author"] }}](https://www.reddit.com/user/{{ link["author"] }}) in [{{ link["subreddit"] }}](https://www.reddit.com/r/{{ link["subreddit"] }}) with [{{ link["num_comments"] }} comments]({{ link["permalink"] }}){% end %}
