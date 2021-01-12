const _ = require('lodash');
const Promise = require('bluebird');
const path = require('path');
const { createFilePath } = require('gatsby-source-filesystem');
const { supportedLanguages } = require('./i18n');

exports.createPages = ({ graphql, actions }) => {
  const { createPage, createRedirect } = actions;

  // Oops
  createRedirect({
    fromPath: '/zh_TW/things-i-dont-know-as-of-2018/',
    toPath: '/zh-hant/things-i-dont-know-as-of-2018/',
    isPermanent: true,
    redirectInBrowser: true,
  });
  // Oops 2
  createRedirect({
    fromPath: '/not-everything-should-be-a-hook/',
    toPath: '/why-isnt-x-a-hook/',
    isPermanent: true,
    redirectInBrowser: true,
  });
  // Oops 3
  createRedirect({
    fromPath: '/making-setinterval-play-well-with-react-hooks/',
    toPath: '/making-setinterval-declarative-with-react-hooks/',
    isPermanent: true,
    redirectInBrowser: true,
  });

  return new Promise((resolve, reject) => {
    const blogPost = path.resolve('./src/templates/blog-post.js');

    // Create index pages for all supported languages
    Object.keys(supportedLanguages).forEach(langKey => {
      createPage({
        path: langKey === 'en' ? '/' : `/${langKey}/`,
        component: path.resolve('./src/templates/blog-index.js'),
        context: {
          langKey,
        },
      });
    });

    resolve(
      graphql(
        `
          {
            allMarkdownRemark(
              sort: { fields: [frontmatter___date], order: DESC }
              limit: 1000
            ) {
              edges {
                node {
                  fields {
                    slug
                    langKey
                    directoryName
                  }
                  frontmatter {
                    title
                  }
                }
              }
            }
          }
        `
      ).then(result => {
        if (result.errors) {
          console.log(result.errors);
          reject(result.errors);
          return;
        }

        // Create blog posts pages.
        const posts = result.data.allMarkdownRemark.edges;
        const allSlugs = _.reduce(
          posts,
          (result, post) => {
            result.add(post.node.fields.slug);
            return result;
          },
          new Set()
        );

        const translationsByDirectory = _.reduce(
          posts,
          (result, post) => {
            const directoryName = _.get(post, 'node.fields.directoryName');
            const langKey = _.get(post, 'node.fields.langKey');

            if (directoryName && langKey && langKey !== 'en') {
              (result[directoryName] || (result[directoryName] = [])).push(
                langKey
              );
            }

            return result;
          },
          {}
        );

        const defaultLangPosts = posts.filter(
          ({ node }) => node.fields.langKey === 'en'
        );
        _.each(defaultLangPosts, (post, index) => {
          const previous =
            index === defaultLangPosts.length - 1
              ? null
              : defaultLangPosts[index + 1].node;
          const next = index === 0 ? null : defaultLangPosts[index - 1].node;

          const translations =
            translationsByDirectory[_.get(post, 'node.fields.directoryName')] ||
            [];

          createPage({
            path: post.node.fields.slug,
            component: blogPost,
            context: {
              slug: post.node.fields.slug,
              previous,
              next,
              translations,
              translatedLinks: [],
            },
          });

          const otherLangPosts = posts.filter(
            ({ node }) => node.fields.langKey !== 'en'
          );
          _.each(otherLangPosts, post => {
            const translations =
              translationsByDirectory[_.get(post, 'node.fields.directoryName')];

            // Record which links to internal posts have translated versions
            // into this language. We'll replace them before rendering HTML.
            let translatedLinks = [];
            const { langKey } = post.node.fields;

            createPage({
              path: post.node.fields.slug,
              component: blogPost,
              context: {
                slug: post.node.fields.slug,
                translations,
                translatedLinks,
              },
            });
          });
        });
      })
    );
  });
};

exports.onCreateNode = ({ node, actions }) => {
  const { createNodeField } = actions;

  if (_.get(node, 'internal.type') === `MarkdownRemark`) {
    createNodeField({
      node,
      name: 'directoryName',
      value: path.basename(path.dirname(_.get(node, 'fileAbsolutePath'))),
    });
  }
};
