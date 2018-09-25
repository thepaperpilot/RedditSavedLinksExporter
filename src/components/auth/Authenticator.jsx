import React, { Component } from 'react'
import { connect } from 'react-redux'
import qs from 'query-string'
import axios from 'axios'
import Loader from './../ui/Loader'

class Authenticator extends Component {
    componentDidMount() {
        const { code } = qs.parse(this.props.location.search, {
            ignoreQueryPrefix: true
        })
        
        this.props.history.push('/')
        this.props.dispatch({ type: 'LOG_IN' })
        
        axios.post('/auth', { code })
            .then(response => {
                this.props.dispatch({
                    type: 'LOAD',
                    ...response.data
                })
            })
            .catch(() => {
                this.props.dispatch({ type: 'LOG_OUT' })
            })
    }

    render() {
        return <Loader label="Authenticating" />
    }
}

export default connect()(Authenticator)
