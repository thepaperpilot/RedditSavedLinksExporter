import React, { Component } from 'react'
import { connect } from 'react-redux'
import download from 'downloadjs'
import './header.css'

class Exporter extends Component {
    constructor(props) {
        super(props)

        this.exportJSON = this.exportJSON.bind(this)
    }

    exportJSON() {
        const json = JSON.stringify(this.props.links)
            .replace(/[\u007F-\uFFFF]/g, function(chr) {
                return `\\u${`0000${chr.charCodeAt(0).toString(16)}`.substr(-4)}`
            })

        download(
            json,
            `${this.props.username}.json`,
            'text/json')
    }

    render() {
        return <div className="header">
            <p>Viewing saved links for: {this.props.username}</p>
            <button onClick={this.exportJSON}>Export JSON</button>
        </div>
    }
}

function mapStateToProps(state) {
    return {
        links: state.links,
        username: state.username
    }
}

export default connect(mapStateToProps)(Exporter)
