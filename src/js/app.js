import React, { Component } from 'react';
import { render } from 'react-dom';

import '../css/style.css';

export default class App extends Component {
  constructor() {
    super();
    this.state = {
      searchTerm: '',
      results: [],
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

  renderSearchResults() {
    return this.state.results.map((item, i) => {
      return (
        <div key={i}>
          <h3>{item.title}</h3>
          <img src={item.albumart} />
          <p>{item.artist}</p>
        </div>
      );
    });
  }

  render() {
    return (
      <div>
        <form onSubmit={this.handleSearch}>
          <input type="text" name="search" onChange={this.handleSearchTermChange} value={this.state.searchTerm} />
          <button type="submit">search</button>
        </form>
        <div>
          {this.renderSearchResults()}
        </div>
      </div>
    );
  }
}

render(<App />, document.getElementById('app'));
