import React, { Component } from 'react';
import { render } from 'react-dom';

import '../css/style.css';

export default class Hello extends Component {
  render() {
    return (
      <div>
        Fetch Music
      </div>
    );
  }
}

render(<Hello />, document.getElementById('app'));
