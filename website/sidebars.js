/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
module.exports = {
  docs: [
    'overview',
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting_started/installation',
        'getting_started/ipynb_example',
        'getting_started/web_app_example',
        'getting_started/scorer_example',
        'getting_started/fairseq_example',
      ],
    },
    {
      type: 'category',
      label: 'Features',
      collapsed: false,
      items: [
        'features/data',
        'features/metrics',
        'features/tags',
        'features/ipynb_api',
        'features/scorer_api',
        'features/fairseq_api',
        'features/g_translate',
      ],
    },
    {
      type: 'category',
      label: 'Extending VizSeq',
      collapsed: false,
      items: ['new_metric'],
    },
  ],
};
