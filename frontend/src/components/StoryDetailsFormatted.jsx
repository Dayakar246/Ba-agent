import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export const StoryDetailsFormatted = ({ story }) => {
  if (!story) return null;

  let rawDesc = story.description || '';
  const rawAC = story.acceptance_criteria;

  // Replace "User Story Statement" header with "Description" to mirror Azure DevOps standards
  rawDesc = rawDesc.replace(/\*\*\s*User Story Statement\s*\*\*:?/gi, '**Description:**');

  // Ensure newlines before bold section headers if smushed together
  rawDesc = rawDesc.replace(/([^\n])\s*(\*\*(?:Description|User Story Statement|Business Context|Workflow Impact|Functional Rules|Acceptance Criteria)[^*]*:\*\*)/gi, '$1\n\n$2');

  let mainDesc = rawDesc;
  let extractedACText = '';

  // Deduplicate if title statement is repeated at the start of description
  const storyTitleClean = (story.title || '').replace(/^\[[^\]]+\]\s*/, '').trim();
  if (storyTitleClean && storyTitleClean.length > 10) {
    const escapedTitle = storyTitleClean.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    mainDesc = mainDesc.replace(new RegExp(`^(?:\\*\\*Description:\\*\\*\\s*)?${escapedTitle}\\.?\\s*`, 'i'), '**Description:**\n');
  }

  // Separate Acceptance Criteria if embedded inside description
  const acMatch = rawDesc.match(/\*\*\s*Acceptance Criteria[^*]*\*\*:?/i) || rawDesc.match(/Acceptance Criteria\s*\([^)]*\):?/i);
  if (acMatch) {
    const splitIdx = rawDesc.indexOf(acMatch[0]);
    mainDesc = mainDesc.substring(0, splitIdx).trim();
    extractedACText = rawDesc.substring(splitIdx + acMatch[0].length).trim();
  }

  // Parse extracted AC text into structured blocks/scenarios
  let extractedACItems = [];
  if (extractedACText) {
    // Split by Scenario or double newline
    extractedACItems = extractedACText
      .split(/(?=\bScenario\s*\d+:|\*\*Scenario\s*\d+:|\n\n)/i)
      .map(s => s.trim())
      .filter(Boolean);
  }

  // Normalize explicit acceptance_criteria property
  let explicitACItems = [];
  if (Array.isArray(rawAC) && rawAC.length > 0) {
    explicitACItems = rawAC.map(item => typeof item === 'string' ? item.trim() : JSON.stringify(item)).filter(Boolean);
  } else if (typeof rawAC === 'string' && rawAC.trim()) {
    explicitACItems = rawAC.split('\n').map(s => s.trim()).filter(Boolean);
  }

  // Combine all AC items
  const allACItems = [...explicitACItems, ...extractedACItems];

  // Helper to format Gherkin text with keyword badges
  const renderGherkinText = (text) => {
    // Clean up asterisks if any
    const cleaned = text.replace(/\*\*/g, '');
    const lines = cleaned.split('\n').filter(Boolean);

    return lines.map((line, lIdx) => {
      const trimmed = line.trim();
      const match = trimmed.match(/^(Given|When|Then|And|Scenario\s*\d+:?)(.*)/i);

      if (match) {
        const keyword = match[1].trim();
        const rest = match[2];
        const lowerKw = keyword.toLowerCase();

        if (lowerKw.startsWith('scenario')) {
          return (
            <div key={lIdx} className="ac-scenario-header">
              📌 <strong>{keyword}{rest}</strong>
            </div>
          );
        }

        let kwClass = 'and';
        if (lowerKw === 'given') kwClass = 'given';
        else if (lowerKw === 'when') kwClass = 'when';
        else if (lowerKw === 'then') kwClass = 'then';

        return (
          <div key={lIdx} className="ac-gherkin-line">
            <span className={`ac-kw ${kwClass}`}>{keyword.toUpperCase()}</span>
            <span>{rest}</span>
          </div>
        );
      }

      return (
        <div key={lIdx} className="ac-plain-line">
          {line}
        </div>
      );
    });
  };

  return (
    <div className="story-details-container">
      {mainDesc && (
        <div className="story-desc-markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{mainDesc}</ReactMarkdown>
        </div>
      )}

      {allACItems.length > 0 && (
        <div className="ac-section">
          <div className="ac-section-header">
            <span className="ac-icon">📋</span>
            <h6>Acceptance Criteria</h6>
          </div>
          <div className="ac-list-container">
            {allACItems.map((acItem, idx) => (
              <div key={idx} className="ac-item-card">
                {renderGherkinText(acItem)}
              </div>
            ))}
          </div>
        </div>
      )}

      {story.tasks && story.tasks.length > 0 && (
        <div className="story-tasks-section">
          <div className="tasks-header">
            <span>⚙️ Development Tasks</span>
          </div>
          <div className="tasks-list">
            {story.tasks.map((task, tIdx) => (
              <div key={tIdx} className="node task">
                <div className="node-head">
                  <span className="node-tag">TASK</span>
                  <span className="node-title">{typeof task === 'string' ? task : (task.title || JSON.stringify(task))}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StoryDetailsFormatted;
