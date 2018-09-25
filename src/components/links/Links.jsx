import React, { Component } from 'react'
import { connect } from 'react-redux'
import Link from './Link'
import Exporter from './Exporter'
import './links.css'

class Links extends Component {
    render() {
        return <div className="links">
            <Exporter />
            {this.props.links.map((link, i) => <Link link={link} key={i} />)}
        </div>
    }
}

function mapStateToProps(state) {
    return {
        links: state.links
    }
}

export default connect(mapStateToProps)(Links)
