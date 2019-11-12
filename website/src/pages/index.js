/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from 'react';
import classnames from 'classnames';
import Layout from '@theme/Layout';
import CodeBlock from '@theme/CodeBlock';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './styles.module.css';

const features = [
  {
    title: <>Multi-Modal</>,
    description: (
        <>
            Covering a wide range of {"{text, image, audio, video}"}-to-text generation tasks. Supporting multiple sources and references.
        </>
    ),
  },
  {
    title: <>Usable</>,
    description: (
        <>
            Built with a full collection of common metrics. Analyzing data in various formats. Providing visualization in both Jupyter Notebook and web App interfaces.
        </>
    ),
  },
  {
    title: <>Productive</>,
    description: (
      <>
        Highly-integrated UI with samples and statistics in one place. Interactive data filtering with keyword searching, example sorting and grouping. One-click export of tables and figures to slides, papers     or spreadsheets.

      </>
    ),
  },
  {
    title: <>Scalable</>,
    description: (
      <>
        Multi-process acceleration of metrics and statistics computation. Auto-sampling and caching mechanism for performance on large-scale datasets.
      </>
    ),
  },
];

const ipynbDataInputCode = `from glob import glob
root = 'examples/data/translation_wmt14_en_de_test'
src, ref, hypo = glob(f'{root}/src_*.txt'), glob(f'{root}/ref_*.txt'), glob(f'{root}/pred_*.txt')
`;

const ipynbViewingCode = `import vizseq
vizseq.view_stats(src, ref)
vizseq.view_n_grams(src)
vizseq.view_scores(ref, hypo, ['bleu', 'meteor'])
vizseq.view_examples(src, ref, hypo, ['bleu', 'meteor'], query='book', page_sz=10, page_no=1)
`;

function Feature({imageUrl, title, description}) {
  const imgUrl = useBaseUrl(imageUrl);
  return (
    <div className={classnames('col col-3', styles.feature)}>
      {imgUrl && (
        <div className="text--center">
          <img className={styles.featureImage} src={imgUrl} alt={title} />
        </div>
      )}
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function Home() {
  const context = useDocusaurusContext();
  const {siteConfig = {}} = context;
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="ViSeq: A Visual Analysis Toolkit for Text Generation Tasks.">
      <header className={classnames('hero hero--primary', styles.heroBanner)}>
        <div className="container">
          <h1 className="hero__title">{siteConfig.title}</h1>
          <p className="hero__subtitle">{siteConfig.tagline}</p>
          <div className={styles.buttons}>
            <Link
              className={classnames(
                'button button--success button--lg',
                styles.getStarted,
              )}
              to="#quickstartSection">
              Get Started
            </Link>
            &emsp;
            <Link
              className={classnames(
                'button button--secondary button--lg',
                styles.getStarted,
              )}
              to="docs/overview">
              Learn More
            </Link>
          </div>
        </div>
      </header>
      <main>
        {features && features.length && (
          <section className={styles.features}>
            <div className="container">
              <div className="row">
                {features.map((props, idx) => (
                  <Feature key={idx} {...props} />
                ))}
              </div>
            </div>
          </section>
        )}
        <section id="quickstartSection" className={classnames('hero', styles.quickstart)}>
            <div className="container">
                <h1 className="text--center">Quickstart</h1>
                <h4>Install VizSeq:</h4>
                <CodeBlock className="bash">$ pip install vizseq</CodeBlock>
                <br/>
                <h4>Use VizSeq in Jupyter notebook:</h4>
                <h9>First, set up data inputs:</h9>
                <CodeBlock className="python">{ipynbDataInputCode}</CodeBlock>
                <br/>
                <h9>Then use the <Link to={useBaseUrl('docs/features/ipynb_api')}>APIs</Link> to view samples, scores and statistics:</h9>
                <CodeBlock className="python">{ipynbViewingCode}</CodeBlock>
                <br/>
                <h4>Or use VizSeq web App:</h4>
                <CodeBlock className="bash">$ python -m vizseq.server --port 9001 --data-root examples/data</CodeBlock>
                <br/>
                <h9>In your web browser, navigate to:</h9>
                <CodeBlock className="bash">http://localhost:9001</CodeBlock>
                <br/>
                <h4>For more details, please check out the <Link to={useBaseUrl('docs/overview')}>Docs</Link>.</h4>
            </div>
        </section>
      </main>
    </Layout>
  );
}

export default Home;
