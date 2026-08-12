/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

// @ts-check

const {themes} = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
module.exports = {
  title: 'VizSeq',
  tagline: 'A Visual Analysis Toolkit for Text Generation (Translation, Captioning, Summarization, etc.)',
  url: 'https://facebookresearch.github.io',
  baseUrl: '/vizseq/',
  favicon: 'img/favicon.png',
  organizationName: 'facebookresearch',
  projectName: 'vizseq',
  onBrokenLinks: 'throw',
  onBrokenAnchors: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'throw',
    },
  },
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  themeConfig: {
    image: 'img/overview.png',
    colorMode: {
      defaultMode: 'light',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: '',
      logo: {
        alt: 'VizSeq',
        src: 'img/logo.png',
        srcDark: 'img/logo_dark.png',
      },
      items: [
        {to: '/#quickstartSection', label: 'Quickstart', position: 'right'},
        {to: '/docs/overview', label: 'Docs', position: 'right'},
        {
          href: 'https://github.com/facebookresearch/vizseq',
          label: 'VizSeq@GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: 'Overview', to: '/docs/overview'},
            {label: 'Installation', to: '/docs/getting_started/installation'},
            {label: 'Jupyter Notebook Example', to: '/docs/getting_started/ipynb_example'},
            {label: 'Web App Example', to: '/docs/getting_started/web_app_example'},
          ],
        },
        {
          title: 'More',
          items: [
            {label: 'VizSeq@GitHub', href: 'https://github.com/facebookresearch/vizseq'},
            {label: 'VizSeq@PyPI', href: 'https://pypi.org/project/vizseq/'},
            {label: 'Paper (EMNLP 2019)', href: 'https://arxiv.org/abs/1909.05424'},
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Meta Platforms, Inc. and affiliates.`,
    },
    prism: {
      theme: themes.github,
      darkTheme: themes.dracula,
      additionalLanguages: ['bash', 'python'],
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/facebookresearch/vizseq/edit/main/website/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
        // Replaces the retired UA-151434920-1 property; Universal Analytics
        // stopped collecting in July 2023 and Docusaurus 3 dropped its plugin.
        gtag: {
          trackingID: 'G-PN1X1ZJXPN',
          anonymizeIP: true,
        },
        sitemap: {
          changefreq: 'weekly',
          priority: 0.5,
        },
      }),
    ],
  ],
  // Docusaurus 3 ships no built-in search; this is an offline index built at
  // build time, so it needs no Algolia account or API key.
  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        indexBlog: false,
        docsRouteBasePath: '/docs',
      },
    ],
  ],
};
