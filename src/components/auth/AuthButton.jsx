import React, { Component } from 'react'
import { connect } from 'react-redux'
import snoowrap from 'snoowrap'
import './auth.css'

class AuthButton extends Component {
    constructor(props) {
        super(props)

        this.id = AuthButton.id++

        this.authURL = snoowrap.getAuthUrl({
            clientId: process.env.REACT_APP_CLIENT_ID,
            scope: ['history', 'identity', 'read'],
            redirectUri: process.env.REACT_APP_REDIRECT_URI,
            permanent: false
        })

        this.load = this.load.bind(this)
    }

    load(e) {
        if (window.FileReader) {
            const file = e.target.files[0]
            const reader = new FileReader()
            const dispatch = this.props.dispatch

            reader.onload = r => {
                dispatch({
                    type: 'LOAD',
                    username: file.name.slice(0, -5),
                    links: JSON.parse(r.target.result)
                })
            }

            reader.readAsText(file)
        }
    }

    render() {
        return <div className="content">
            <div className="title">Reddit Saved Links Exporter</div>
            <a className="auth-button" href={this.authURL}>
                Authorize with Reddit
            </a>
            <p className="auth-button">or</p>
            <input id={`auth-button-${this.id}`}
                type="file"
                className="auth-load"
                onChange={this.load}
                value={null}
                accept=".json" />
            <label htmlFor={`auth-button-${this.id}`}>
                Load local JSON
            </label>
        </div>
    }
}

AuthButton.id = 0

export default connect()(AuthButton)
