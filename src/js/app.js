import React, { Component } from 'react';
import { render } from 'react-dom';
import { saveAs } from 'file-saver';

import { API_HOST } from './vars'

import '../css/style.css';

export default class App extends Component {
  constructor() {
    super();
    this.state = {
      searchTerm: '',
      results: [],
      selectedItem: null,
    };

    console.log(process.env);

    this.handleSearchTermChange = this.handleSearchTermChange.bind(this);
    this.handleSearch = this.handleSearch.bind(this);
  }

  handleSearch(event) {
    event.preventDefault();
    const { searchTerm } = this.state;
    fetch(`http://${API_HOST}/api/search?q=${searchTerm}`)
    .then((response) => response.json()
    .then((data) => {
      console.log(data);
      this.setState({
        results: data.results,
      });
    }));
  }

  handleSearchTermChange(event) {
    this.setState({
      searchTerm: event.target.value,
    });
  }

  handleSongSelection(item) {
    const { url } = item;
    this.setState({
      selectedItem: item,
    });

    fetch(`http://${API_HOST}/api/song?id=${url}`)
    .then((response) => response.blob()
    )
    .then((blob) => {
      saveAs(blob, this.state.selectedItem.title);
    });
  }

  handleDownload() {
    // TODO
  }

  renderSearchResults() {
    if (this.state.results.length === 0) return <div>no results</div>;
    return this.state.results.map((item, i) => {
      return (
        <div key={i} style={{ display: 'flex', margin: 10, backgroundColor: '#fff' }}>
          <div style={{ background: `url(${item.albumart})`, width: 120, height: 120 }} />
          <div style={{ padding: 10 }}>
            <h3 onClick={() => this.handleSongSelection(item)}><a href="#">{item.title}</a></h3>
            <p>{item.artist}</p>
            <p>{item.link}</p>
          </div>
        </div>
      );
    });
  }
  // BQBGMapv0oYtZrr9Ogtv6x3BQERsCv3alIOZuWw8d5PMXXXyTIW5bp1SYX0TOmR3C9BX6XIGJOro2LMIBDC_G17M22dvq1yky0vdtAYEYmhT
  render() {
    return (
      <div style={{ width: '80%', margin: '0 auto' }}>
        <form onSubmit={this.handleSearch}>
          <input type="text" name="search" onChange={this.handleSearchTermChange} value={this.state.searchTerm} />
          <button type="submit">search</button>
        </form>
        <div style={{ margin: 10, textAlign: 'center' }}>
          {this.renderSearchResults()}
        </div>
      </div>
    );
  }
}

render(<App />, document.getElementById('app'));
