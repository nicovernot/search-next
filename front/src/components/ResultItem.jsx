import React from 'react';
import './ResultItem.css';

function ResultItem({ doc }) {
  // Les données Solr sont plates, pas besoin de _source
  const title = doc.titre || doc.title || doc.naked_titre || 'Sans titre';
  const description = doc.naked_resume || doc.naked_texte || doc.description || '';
  const url = doc.url || '#';
  const platform = doc.site_title || doc.platformID || 'OpenEdition';
  const type = doc.type || '';
  const authors = doc.contributeurFacet_auteur || doc.contributeurFacetR_auteur || [];
  
  // Formater les auteurs (peut être un tableau ou une chaîne)
  const authorsList = Array.isArray(authors) ? authors : (authors ? [authors] : []);

  return (
    <article className="result-item">
      <div className="result-header">
        {platform && <span className="result-platform">{platform}</span>}
        {type && <span className="result-type">{type}</span>}
      </div>
      
      <h2 className="result-title">
        <a href={url} target="_blank" rel="noopener noreferrer">
          {title}
        </a>
      </h2>
      
      {authorsList.length > 0 && (
        <p className="result-authors">
          {authorsList.slice(0, 3).join(', ')}
          {authorsList.length > 3 && ' et al.'}
        </p>
      )}
      
      {description && (
        <p className="result-description">
          {description.length > 300 
            ? `${description.substring(0, 300)}...` 
            : description}
        </p>
      )}
      
      <a 
        href={url} 
        className="result-link" 
        target="_blank" 
        rel="noopener noreferrer"
      >
        Voir le document →
      </a>
    </article>
  );
}

export default ResultItem;
