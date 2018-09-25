import React, { Component } from 'react'

const transparent = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='

class TransientImage extends Component {
    constructor(props) {
        super(props)

        this.state = {
            error: false
        }

        this.onError = this.onError.bind(this)
    }

    onError() {
        this.setState({
            error: true
        })
    }

    render() {
        const {src, ...props} = this.props
        return <img {...props}
            onError={this.onError}
            src={this.state.error ? transparent : src} />
    }
}

export default TransientImage
