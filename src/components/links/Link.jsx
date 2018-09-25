import React, { Component } from 'react'
import TransientImage from './../ui/TransientImage'

class Link extends Component {
    constructor(props) {
        super(props)

        this.state = {
            showBody: false
        }

        this.toggleBody = this.toggleBody.bind(this)
    }

    toggleBody() {
        this.setState({
            showBody: !this.state.showBody
        })
    }

    render() {
        const {
            url,
            title,
            author,
            subreddit,
            permalink,
            num_comments,
            selftext_html,
            body_html,
            thumbnail,
            link_url,
            link_author,
            link_title,
            link_permalink
        } = this.props.link

        return <div className="link">
            <div className="link-header">
                {thumbnail && <a className={`thumbnail ${thumbnail}`} href={url}>
                    <TransientImage src={thumbnail} />
                </a>}
                <div className="link-info">
                    <a className="link-title" href={url}>{title}</a>
                    {body_html ?
                        <p className="tagline">
                            <a href={link_url}>{link_title}</a> by <a className="reddit"
                                href={`https://www.reddit.com/user/${link_author}`}>
                                {link_author}
                            </a> in <a className="reddit"
                                href={`https://www.reddit.com/r/${subreddit}`}>
                                {subreddit}
                            </a> with <a className="reddit"
                                href={`https://www.reddit.com${link_permalink}`}>
                                {num_comments} comments
                            </a>
                        </p> :
                        <p className="tagline">
                            {selftext_html && <button className="bodyToggle"
                                onClick={this.toggleBody}>☰</button>}
                            submitted by <a className="reddit"
                                href={`https://www.reddit.com/user/${author}`}>
                                {author}
                            </a> to <a className="reddit"
                                href={`https://www.reddit.com/r/${subreddit}`}>
                                {subreddit}
                            </a> with <a className="reddit"
                                href={`https://www.reddit.com${permalink}`}>
                                {num_comments} comments
                            </a>
                        </p>}
                </div>
            </div>
            {this.state.showBody &&
                <div className="body"
                    dangerouslySetInnerHTML={{ __html: selftext_html }} />}
            {body_html && <div className="comment">
                A <a className="reddit"
                    href={`https://www.reddit.com${permalink}`}>
                    comment
                </a> by <a className="reddit"
                    href={`https://www.reddit.com/user/${author}`}>
                    {author}
                </a>
                <div className="body"
                    dangerouslySetInnerHTML={{ __html: body_html }} />
            </div>}
        </div>
    }
}

export default Link
