import React, { Component } from 'react';
import { render } from 'react-dom';
import { saveAs } from 'file-saver';

import '../css/style.css';

export default class App extends Component {
  constructor() {
    super();
    this.state = {
      searchTerm: '',
      results: [],
      selectedItem: null,
    };

    this.handleSearchTermChange = this.handleSearchTermChange.bind(this);
    this.handleSearch = this.handleSearch.bind(this);
  }

  handleSearch(event) {
    event.preventDefault();
    const { searchTerm } = this.state;
    fetch(`http://localhost:5001/api/search?q=${searchTerm}`)
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

    fetch(`http://localhost:5001/api/song?id=${url}`)
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
    return this.state.results.map((item, i) => {
      return (
        <div key={i} onClick={() => this.handleSongSelection(item)}>
          <h3>{item.title}</h3>
          <img src={item.albumart} />
          <p>{item.artist}</p>
          <p>{item.link}</p>
        </div>
      );
    });
  }

  renderSongDetails() {
    if (this.state.song) {
      const { title, url, artist, albumart } = this.state.song;
      return (
        <div>
          <h3>{title}</h3>
          <img src={albumart} />
          <p>{artist}</p>
          <button onClick={() => this.handleDownload()}>download</button>
        </div>
      );
    }
    return <div></div>;
  }
  // BQBGMapv0oYtZrr9Ogtv6x3BQERsCv3alIOZuWw8d5PMXXXyTIW5bp1SYX0TOmR3C9BX6XIGJOro2LMIBDC_G17M22dvq1yky0vdtAYEYmhT
  render() {
    return (
      <div>
        <form onSubmit={this.handleSearch}>
          <input type="text" name="search" onChange={this.handleSearchTermChange} value={this.state.searchTerm} />
          <button type="submit">search</button>
        </form>
        <div>{this.renderSongDetails()}</div>
        <div>
          {this.renderSearchResults()}
        </div>
      </div>
    );
  }
}

render(<App />, document.getElementById('app'));
