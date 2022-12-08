'use strict';

const e = React.createElement;

class LikeButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = { liked: false };
  }
  
  button_press = () => {
      this.setState( {liked: true} )
  }
  
  whatever = () => {
    return (
      <div>Hello</div>

    )
  }


  render() {
    if (this.state.liked) {
      return 'You liked this.';
    }
    
    return (
      <div>
      <div class="button" onClick={ () => {this.button_press() } }
        className="btn btn-primary">Like</div>
      </div>
    );

  }
}

const domContainer = document.querySelector('#react_container');
ReactDOM.render(e(LikeButton), domContainer);
