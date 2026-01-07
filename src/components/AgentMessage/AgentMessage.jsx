import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import styles from './AgentMessage.module.css';

const AgentMessage = ({ agentName, message, agentType, isTyping }) => {
  const getAgentIcon = (type) => {
    // Return LawAI logo for legal assistant
    return (
      <img 
        src="https://sspark.genspark.ai/cfimages?u1=qRqawqrDk00RQMP6wXEUHuxWslNIbEJeCgy3Kqs9GXjw0sIL8483WOde5qmLhtDY%2Fhw0V%2BGoiSSXpfCp3EeKCA2VGgjvltWHVtZrtmfw3iMJN6A6k3wj&u2=tJ5MdbAFRhq2FK3f&width=2560" 
        alt="LawAI" 
        style={{width: '100%', height: '100%', objectFit: 'contain'}}
      />
    );
  };

  return (
    <div className={styles['agent-message']}>
      <div className={`${styles['agent-avatar']} ${styles[agentType]}`}>
        {getAgentIcon(agentType)}
      </div>
      <div className={styles['agent-content']}>
        <p className={styles['agent-name']}>{agentName}</p>
        {isTyping ? (
          <p className={styles['agent-typing']}>is working on ideas...</p>
        ) : (
          <div className={styles['agent-text']}>
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                // eslint-disable-next-line jsx-a11y/heading-has-content
                h3: ({node, ...props}) => <h3 style={{fontSize: '1.1em', fontWeight: 'bold', marginTop: '16px', marginBottom: '8px'}} {...props} />,
                strong: ({node, ...props}) => <strong style={{fontWeight: '600', color: '#000'}} {...props} />,
                p: ({node, ...props}) => <p style={{marginBottom: '12px', lineHeight: '1.6'}} {...props} />,
                ul: ({node, ...props}) => <ul style={{marginLeft: '20px', marginBottom: '12px'}} {...props} />,
                ol: ({node, ...props}) => <ol style={{marginLeft: '20px', marginBottom: '12px'}} {...props} />,
                li: ({node, ...props}) => <li style={{marginBottom: '6px', lineHeight: '1.6'}} {...props} />
              }}
            >
              {message}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentMessage;
