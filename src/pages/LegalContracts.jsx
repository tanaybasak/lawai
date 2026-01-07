import React, { useState } from 'react';
import styles from './LegalContracts.module.scss';

const LegalContracts = () => {
  const [activeTab, setActiveTab] = useState('nda');
  const [activeLanguage, setActiveLanguage] = useState('english');
  const [inputText, setInputText] = useState('');

  const tabs = [
    { id: 'nda', label: 'NDA' },
    { id: 'msa', label: 'MSA' },
    { id: 'employment', label: 'Employment' },
    { id: 'service', label: 'Service Agreement' },
    { id: 'all', label: 'All' },
  ];

  const languages = [
    { id: 'english', label: 'English (US)' },
    { id: 'french', label: 'French' },
    { id: 'spanish', label: 'Spanish' },
    { id: 'german', label: 'German' },
    { id: 'all', label: 'All' },
  ];

  const modes = [
    'Standard', 'Fluency', 'Humanize', 'Formal', 'Academic', 
    'Simple', 'Creative', 'Expand', 'Shorten', 'Custom'
  ];

  const [activeMode, setActiveMode] = useState('Standard');

  return (
    <div className={styles.page}>
      <div className={styles.pageHeader}>
        <h1>Legal Contracts</h1>
        <p className={styles.subtitle}>Draft and customize legal documents with AI assistance</p>
      </div>
      
      <div className={styles.languageTabs}>
        {languages.map((lang) => (
          <button
            key={lang.id}
            className={`${styles.languageTab} ${activeLanguage === lang.id ? styles.active : ''}`}
            onClick={() => setActiveLanguage(lang.id)}
          >
            {lang.label}
          </button>
        ))}
      </div>

      <div className={styles.modesSection}>
        <span className={styles.modesLabel}>Modes:</span>
        <div className={styles.modes}>
          {modes.map((mode) => (
            <button
              key={mode}
              className={`${styles.modeBtn} ${activeMode === mode ? styles.active : ''}`}
              onClick={() => setActiveMode(mode)}
            >
              {mode}
            </button>
          ))}
        </div>
        <div className={styles.synonymControl}>
          <span>Synonyms:</span>
          <input type="range" min="0" max="100" defaultValue="50" className={styles.slider} />
        </div>
      </div>

      <div className={styles.pageContent}>
        <div className={styles.inputSection}>
          <textarea
            className={styles.textInput}
            placeholder="To draft a contract, describe your requirements here and press 'Generate'."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
          />
          
          <div className={styles.actions}>
            <button className={styles.uploadBtn}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Upload Doc
            </button>
            <button className={styles.generateBtn}>
              Generate Contract
            </button>
          </div>
        </div>

        <div className={styles.contractTypes}>
          <h3>Quick Contract Templates</h3>
          <div className={styles.contractsGrid}>
            {activeTab === 'nda' && (
              <div className={styles.contractCard}>
                <h4>Non-Disclosure Agreement</h4>
                <p>Protect confidential information with mutual or unilateral NDAs</p>
              </div>
            )}
            {activeTab === 'msa' && (
              <div className={styles.contractCard}>
                <h4>Master Service Agreement</h4>
                <p>Framework agreement for ongoing services</p>
              </div>
            )}
            {activeTab === 'employment' && (
              <div className={styles.contractCard}>
                <h4>Employment Agreement</h4>
                <p>Define terms of employment relationship</p>
              </div>
            )}
            {activeTab === 'service' && (
              <div className={styles.contractCard}>
                <h4>Service Agreement</h4>
                <p>Outline terms for specific services</p>
              </div>
            )}
            {activeTab === 'all' && (
              <>
                <div className={styles.contractCard}>
                  <h4>Non-Disclosure Agreement</h4>
                  <p>Protect confidential information</p>
                </div>
                <div className={styles.contractCard}>
                  <h4>Master Service Agreement</h4>
                  <p>Framework for ongoing services</p>
                </div>
                <div className={styles.contractCard}>
                  <h4>Employment Agreement</h4>
                  <p>Employment relationship terms</p>
                </div>
                <div className={styles.contractCard}>
                  <h4>Service Agreement</h4>
                  <p>Terms for specific services</p>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LegalContracts;
