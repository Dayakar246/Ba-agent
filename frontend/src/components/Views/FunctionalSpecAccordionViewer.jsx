import React, { useState, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChevronDown, ChevronRight, Search, Maximize2, Minimize2, CheckCircle, FileText } from 'lucide-react';

export default function FunctionalSpecAccordionViewer({ content }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [openSections, setOpenSections] = useState({});
  const [allExpanded, setAllExpanded] = useState(true);

  const rawText = typeof content === 'string' ? content : (content ? JSON.stringify(content, null, 2) : '');

  // Parse markdown content into structured sections based on h2 / h3 headings
  const parsedSections = useMemo(() => {
    if (!rawText) return [];

    const lines = rawText.split('\n');
    const sections = [];
    let currentSection = {
      id: 'sec-0',
      title: '1. Executive Summary & Overview',
      contentLines: [],
      frCount: 0
    };

    lines.forEach((line) => {
      const isHeading = line.match(/^#{1,3}\s+(.+)/);
      if (isHeading) {
        if (currentSection.contentLines.length > 0 || currentSection.title) {
          sections.push(currentSection);
        }
        const titleText = isHeading[1].trim();
        currentSection = {
          id: `sec-${sections.length + 1}`,
          title: titleText,
          contentLines: [line],
          frCount: 0
        };
      } else {
        currentSection.contentLines.push(line);
      }
    });

    if (currentSection.contentLines.length > 0 || currentSection.title) {
      sections.push(currentSection);
    }

    // Count FR tags inside each section using a flexible regex pattern: FR-xxx, FR xxx, or [FR-xxx]
    return sections.map(sec => {
      const text = sec.contentLines.join('\n');
      const frMatches = text.match(/\[?FR[-\s]?\d+\]?/gi) || [];
      const uniqueFRs = new Set(frMatches.map(m => m.toUpperCase().replace(/[\[\]\s]/g, '').replace('FR', 'FR-')));
      return {
        ...sec,
        text,
        frCount: uniqueFRs.size
      };
    });
  }, [rawText]);

  // Filter sections by search term
  const filteredSections = useMemo(() => {
    if (!searchTerm.trim()) return parsedSections;
    const term = searchTerm.toLowerCase();
    return parsedSections.filter(sec => 
      sec.title.toLowerCase().includes(term) || sec.text.toLowerCase().includes(term)
    );
  }, [parsedSections, searchTerm]);

  const toggleSection = (id) => {
    setOpenSections(prev => ({
      ...prev,
      [id]: prev[id] === undefined ? false : !prev[id]
    }));
  };

  const handleToggleAll = () => {
    const nextState = !allExpanded;
    setAllExpanded(nextState);
    const newOpen = {};
    parsedSections.forEach(s => { newOpen[s.id] = nextState; });
    setOpenSections(newOpen);
  };

  const totalFRs = useMemo(() => {
    if (!rawText) return 0;
    const allMatches = rawText.match(/\[?FR[-\s]?\d+\]?/gi) || [];
    const globalUniqueFRs = new Set(allMatches.map(m => m.toUpperCase().replace(/[\[\]\s]/g, '').replace('FR', 'FR-')));
    return Math.max(globalUniqueFRs.size, parsedSections.reduce((acc, s) => acc + s.frCount, 0));
  }, [rawText, parsedSections]);

  return (
    <div className="functional-spec-accordion-container" style={{ color: '#1e293b', background: '#ffffff', padding: '16px', borderRadius: '12px' }}>
      {/* Top Toolbar with Search & Accordion Controls */}
      <div className="spec-toolbar" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 16px',
        marginBottom: '16px',
        background: '#f8fafc',
        borderRadius: '10px',
        border: '1px solid #e2e8f0',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
            <input
              type="text"
              placeholder="Search FR ID (e.g. FR-005) or keywords..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '7px 12px 7px 34px',
                borderRadius: '8px',
                border: '1px solid #cbd5e1',
                background: '#ffffff',
                color: '#0f172a',
                fontSize: '0.85rem'
              }}
            />
          </div>
          {totalFRs > 0 && (
            <span style={{
              fontSize: '0.8rem',
              padding: '4px 10px',
              borderRadius: '20px',
              background: '#eff6ff',
              color: '#1d4ed8',
              border: '1px solid #bfdbfe',
              fontWeight: '600'
            }}>
              {totalFRs} Mapped FRs
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            className="btn-secondary"
            onClick={handleToggleAll}
            style={{
              padding: '6px 12px',
              fontSize: '0.8rem',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: '#ffffff',
              color: '#0f172a',
              border: '1px solid #cbd5e1'
            }}
          >
            {allExpanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
            {allExpanded ? 'Collapse All' : 'Expand All'}
          </button>
        </div>
      </div>

      {/* Accordions List */}
      <div className="spec-accordions-list" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {filteredSections.length === 0 ? (
          <div style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>
            No matching requirements found for "{searchTerm}".
          </div>
        ) : (
          filteredSections.map((sec) => {
            const isOpen = openSections[sec.id] !== undefined ? openSections[sec.id] : allExpanded;
            return (
              <div
                key={sec.id}
                className="spec-accordion-item"
                style={{
                  borderRadius: '10px',
                  border: '1px solid #e2e8f0',
                  overflow: 'hidden',
                  background: '#ffffff',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                  transition: 'all 0.2s ease'
                }}
              >
                {/* Accordion Header */}
                <div
                  className="spec-accordion-header"
                  onClick={() => toggleSection(sec.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '14px 18px',
                    cursor: 'pointer',
                    background: isOpen ? '#f1f5f9' : '#f8fafc',
                    borderBottom: isOpen ? '1px solid #e2e8f0' : 'none',
                    userSelect: 'none'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {isOpen ? <ChevronDown size={18} color="#2563eb" /> : <ChevronRight size={18} color="#64748b" />}
                    <span style={{ fontWeight: '600', fontSize: '0.95rem', color: '#0f172a' }}>
                      {sec.title}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {sec.frCount > 0 && (
                      <span style={{
                        fontSize: '0.75rem',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        background: '#ecfdf5',
                        color: '#047857',
                        border: '1px solid #a7f3d0',
                        fontWeight: '600'
                      }}>
                        {sec.frCount} FRs
                      </span>
                    )}
                  </div>
                </div>

                {/* Accordion Content Body */}
                {isOpen && (
                  <div
                    className="spec-accordion-body"
                    style={{
                      padding: '18px 22px',
                      background: '#ffffff',
                      color: '#0f172a',
                      fontSize: '0.9rem',
                      lineHeight: '1.6'
                    }}
                  >
                    <article className="doc-content markdown-body" style={{ color: '#0f172a' }}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {sec.text}
                      </ReactMarkdown>
                    </article>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
