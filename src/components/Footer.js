import React from 'react';

import { rhythm } from '../utils/typography';
import config from '../../config';

const { githubUrl, juejin } = config;
class Footer extends React.Component {
  render() {
    return (
      <footer
        style={{
          marginTop: rhythm(2.5),
          paddingTop: rhythm(1),
        }}
      >
        <a href={githubUrl} target="_blank" rel="noopener noreferrer">
          github
        </a>{' '}
        {juejin && (
          <>
            &bull;{' '}
            <a href={juejin} target="_blank" rel="noopener noreferrer">
              掘金
            </a>
          </>
        )}
        &bull;{' '}
        <a
          href="https://github.com/sl1673495/sync-overreacted"
          target="_blank"
          rel="noopener noreferrer"
        >
          生成你的专属博客
        </a>
      </footer>
    );
  }
}

export default Footer;
