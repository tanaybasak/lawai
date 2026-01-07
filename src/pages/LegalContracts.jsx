import React, { useState } from 'react';
import styles from './LegalContracts.module.scss';

const LegalContracts = () => {
  const [activeTab, setActiveTab] = useState('nda');

  const tabs = [
    { id: 'nda', label: 'NDA' },
    { id: 'msa', label: 'MSA' },
    { id: 'employment', label: 'Employment' },
    { id: 'service', label: 'Service Agreement' },
    { id: 'all', label: 'All' },
  ];

  return (
    <div className={styles.page}>
      <div className={styles.pageHeader}>
        <h1>Legal Contracts</h1>
      </div>
      
      <div className={styles.tabs}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`${styles.tab} ${activeTab === tab.id ? styles.active : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className={styles.pageContent}>
        <div className={styles.contractsGrid}>
          {activeTab === 'nda' && (
            <div className={styles.contractCard}>
              <h3>Non-Disclosure Agreement</h3>
              <p>Protect confidential information with mutual or unilateral NDAs</p>
            </div>
          )}
          {activeTab === 'msa' && (
            <div className={styles.contractCard}>
              <h3>Master Service Agreement</h3>
              <p>Framework agreement for ongoing services</p>
            </div>
          )}
          {activeTab === 'employment' && (
            <div className={styles.contractCard}>
              <h3>Employment Agreement</h3>
              <p>Define terms of employment relationship</p>
            </div>
          )}
          {activeTab === 'service' && (
            <div className={styles.contractCard}>
              <h3>Service Agreement</h3>
              <p>Outline terms for specific services</p>
            </div>
          )}
          {activeTab === 'all' && (
            <>
              <div className={styles.contractCard}>
                <h3>Non-Disclosure Agreement</h3>
                <p>Protect confidential information</p>
              </div>
              <div className={styles.contractCard}>
                <h3>Master Service Agreement</h3>
                <p>Framework for ongoing services</p>
              </div>
              <div className={styles.contractCard}>
                <h3>Employment Agreement</h3>
                <p>Employment relationship terms</p>
              </div>
              <div className={styles.contractCard}>
                <h3>Service Agreement</h3>
                <p>Terms for specific services</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default LegalContracts;
