import React from 'react'
import './loader.css'

export default props => <div className="loader-wrapper">
    <div className="loader">
        <div style={{
            marginLeft: '-100%',
            marginRight: '-100%',
            textAlign: 'center'
        }}>
            {props.label || 'Loading...'}
        </div>
    </div>
</div>
