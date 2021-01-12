import React from 'react';
import avatar from '../assets/avatar.jpeg';
import { rhythm } from '../utils/typography';
import config from '../../config';

const { username, githubUrl } = config;

class Bio extends React.Component {
  render() {
    return (
      <div
        style={{
          display: 'flex',
          marginBottom: rhythm(2),
        }}
      >
        {avatar && (
          <img
            src={avatar}
            alt={username}
            style={{
              marginRight: rhythm(1 / 2),
              marginBottom: 0,
              width: rhythm(2),
              height: rhythm(2),
              borderRadius: '50%',
            }}
          />
        )}

        <p style={{ maxWidth: 310 }}>
          Personal blog by <a href={githubUrl}>{username}</a>. I&nbsp;explain
          with words and code.
        </p>
      </div>
    );
  }
}

export default Bio;
