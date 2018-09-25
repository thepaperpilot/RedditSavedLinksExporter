import React, { Component } from 'react'
import snoowrap from 'snoowrap'
import './auth.css'

class AuthButton extends Component {
    constructor(props) {
        super(props)

        this.authURL = snoowrap.getAuthUrl({
            clientId: process.env.REACT_APP_CLIENT_ID,
            scope: ['history', 'identity', 'read'],
            redirectUri: process.env.REACT_APP_REDIRECT_URI,
            permanent: false
        })
    }

    render() {
        return <div className="content">
            <div className="title">Reddit Saved Links Exporter</div>
            <a className="auth-button" href={this.authURL}>
                Authorize with Reddit
            </a>
        </div>
    }
}

export default AuthButton
