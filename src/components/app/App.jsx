import React, { Component } from 'react'
import { connect } from 'react-redux'
import { BrowserRouter, Route,Switch } from 'react-router-dom'
import Authenticator from './../auth/Authenticator'
import AuthButton from './../auth/AuthButton'
import Links from './../links/Links'
import Loader from './../ui/Loader'
import './app.css'

class App extends Component {
    render() {
        const { loggedIn, linksLoaded } = this.props
        return (
            <BrowserRouter>
                <Switch>
                    <Route path="/auth" component={Authenticator} />
                    <Route path="/" component={loggedIn ?
                        linksLoaded ? Links : Loader :
                        AuthButton} />
                </Switch>
            </BrowserRouter>
        )
    }
}

function mapStateToProps(state) {
    return {
        loggedIn: state.loggedIn,
        linksLoaded: state.links.length
    }
}

export default connect(mapStateToProps)(App)
