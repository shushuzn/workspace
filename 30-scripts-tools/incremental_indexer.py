#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Incremental Indexer - Dynamic index updates with delta computation
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
INDEX_DIR = WORKSPACE / 'data' / 'incremental_index'
INDEX_DIR.mkdir(parents=True, exist_ok=True)

class Document:
    """Represents a document for indexing"""
    
    def __init__(self, doc_id: str, content: str, metadata: Dict = None):
        self.doc_id = doc_id
        self.content = content
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.content_hash = hashlib.md5(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            'doc_id': self.doc_id,
            'content': self.content,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'content_hash': self.content_hash,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Document':
        doc = cls(
            doc_id=data['doc_id'],
            content=data['content'],
            metadata=data.get('metadata', {})
        )
        doc.created_at = datetime.fromisoformat(data['created_at'])
        doc.updated_at = datetime.fromisoformat(data['updated_at'])
        doc.content_hash = data['content_hash']
        return doc


class InvertedIndex:
    """Memory-efficient inverted index with incremental updates"""
    
    def __init__(self):
        # term -> {doc_id: frequency}
        self.postings: Dict[str, Dict[str, int]] = defaultdict(dict)
        
        # doc_id -> Document
        self.documents: Dict[str, Document] = {}
        
        # Statistics
        self.total_terms = 0
        self.total_postings = 0
        
        # Change tracking
        self.added_docs: Set[str] = set()
        self.updated_docs: Set[str] = set()
        self.deleted_docs: Set[str] = set()
    
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization (can be enhanced with stemming, etc.)"""
        import re
        # Convert to lowercase, extract words
        tokens = re.findall(r'\b[a-zA-Z\u4e00-\u9fff]+\b', text.lower())
        return tokens
    
    def add_document(self, doc: Document, force: bool = False):
        """Add or update a document in the index"""
        doc_id = doc.doc_id
        
        # Check if document exists and hasn't changed
        if doc_id in self.documents and not force:
            existing = self.documents[doc_id]
            if existing.content_hash == doc.content_hash:
                return  # No change, skip
        
        # Remove old version if exists
        if doc_id in self.documents:
            self._remove_document_from_index(doc_id)
            self.updated_docs.add(doc_id)
        else:
            self.added_docs.add(doc_id)
        
        # Tokenize and index
        tokens = self.tokenize(doc.content)
        term_freq = defaultdict(int)
        
        for token in tokens:
            term_freq[token] += 1
        
        # Update postings
        for term, freq in term_freq.items():
            self.postings[term][doc_id] = freq
            self.total_postings += 1
        
        self.total_terms = len(self.postings)
        
        # Store document
        self.documents[doc_id] = doc
    
    def _remove_document_from_index(self, doc_id: str):
        """Remove document from index (but keep in tracking)"""
        if doc_id not in self.documents:
            return
        
        doc = self.documents[doc_id]
        tokens = self.tokenize(doc.content)
        
        # Remove from postings
        for token in set(tokens):
            if token in self.postings and doc_id in self.postings[token]:
                del self.postings[token][doc_id]
                self.total_postings -= 1
                
                # Remove empty terms
                if not self.postings[token]:
                    del self.postings[token]
        
        self.total_terms = len(self.postings)
    
    def delete_document(self, doc_id: str):
        """Mark document for deletion"""
        if doc_id in self.documents:
            self._remove_document_from_index(doc_id)
            del self.documents[doc_id]
            self.deleted_docs.add(doc_id)
    
    def search(self, query: str) -> List[Tuple[str, float]]:
        """Search for documents matching query"""
        tokens = self.tokenize(query)
        
        if not tokens:
            return []
        
        # Simple scoring: sum of term frequencies
        scores = defaultdict(float)
        
        for token in tokens:
            if token in self.postings:
                for doc_id, freq in self.postings[token].items():
                    scores[doc_id] += freq
        
        # Sort by score
        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return results
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        return {
            'total_documents': len(self.documents),
            'total_terms': self.total_terms,
            'total_postings': self.total_postings,
            'added_docs': len(self.added_docs),
            'updated_docs': len(self.updated_docs),
            'deleted_docs': len(self.deleted_docs),
            'avg_terms_per_doc': self.total_terms / len(self.documents) if self.documents else 0,
            'avg_postings_per_doc': self.total_postings / len(self.documents) if self.documents else 0,
        }
    
    def get_delta(self) -> Dict:
        """Get changes since last commit"""
        return {
            'added': list(self.added_docs),
            'updated': list(self.updated_docs),
            'deleted': list(self.deleted_docs),
            'total_changes': len(self.added_docs) + len(self.updated_docs) + len(self.deleted_docs),
        }
    
    def reset_delta(self):
        """Reset change tracking"""
        self.added_docs.clear()
        self.updated_docs.clear()
        self.deleted_docs.clear()
    
    def save(self, index_file: Path = None) -> Path:
        """Save index to disk"""
        if index_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            index_file = INDEX_DIR / f'inverted_index_{timestamp}.json'
        
        data = {
            'postings': dict(self.postings),
            'documents': {doc_id: doc.to_dict() for doc_id, doc in self.documents.items()},
            'stats': {
                'total_terms': self.total_terms,
                'total_postings': self.total_postings,
            },
            'created_at': datetime.now().isoformat(),
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Index saved to: {index_file}")
        return index_file
    
    @classmethod
    def load(cls, index_file: Path) -> 'InvertedIndex':
        """Load index from disk"""
        with open(index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        index = cls()
        index.postings = defaultdict(dict, data['postings'])
        index.documents = {
            doc_id: Document.from_dict(doc_data)
            for doc_id, doc_data in data['documents'].items()
        }
        index.total_terms = data['stats']['total_terms']
        index.total_postings = data['stats']['total_postings']
        
        print(f"✅ Index loaded from: {index_file}")
        return index


class IncrementalIndexer:
    """
    Incremental Indexer with delta computation
    
    Features:
    - Incremental updates (only index changed documents)
    - Delta computation (added/updated/deleted)
    - Efficient storage (only save changes)
    - Batch processing
    - Automatic index merging
    """
    
    def __init__(self, auto_save: bool = True,
                 save_interval: int = 100):
        self.auto_save = auto_save
        self.save_interval = save_interval
        
        # Current index
        self.index = InvertedIndex()
        
        # Change log
        self.change_log: List[Dict] = []
        
        # Last save time
        self.last_save_time = None
        
        # Load existing index
        self._load_latest_index()
    
    def _load_latest_index(self):
        """Load latest index from disk"""
        index_files = sorted(INDEX_DIR.glob('inverted_index_*.json'))
        
        if index_files:
            latest = index_files[-1]
            self.index = InvertedIndex.load(latest)
            self.last_save_time = datetime.now()
    
    def add_documents(self, documents: List[Document], batch_size: int = 50):
        """Add multiple documents in batches"""
        total = len(documents)
        
        for i in range(0, total, batch_size):
            batch = documents[i:i + batch_size]
            
            for doc in batch:
                self.index.add_document(doc)
            
            # Auto-save if needed
            if self.auto_save and len(self.index.added_docs) >= self.save_interval:
                self.save_index()
        
        print(f"✅ Added {total} documents")
    
    def update_document(self, doc: Document):
        """Update a single document"""
        self.index.add_document(doc, force=True)
        
        if self.auto_save:
            self.save_index()
    
    def delete_document(self, doc_id: str):
        """Delete a document"""
        self.index.delete_document(doc_id)
        
        if self.auto_save:
            self.save_index()
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float, Document]]:
        """Search with document retrieval"""
        results = self.index.search(query)
        
        # Get top-k results with documents
        enriched_results = []
        for doc_id, score in results[:top_k]:
            if doc_id in self.index.documents:
                doc = self.index.documents[doc_id]
                enriched_results.append((doc_id, score, doc))
        
        return enriched_results
    
    def get_delta(self) -> Dict:
        """Get changes since last save"""
        return self.index.get_delta()
    
    def save_index(self, index_file: Path = None) -> Path:
        """Save index and log changes"""
        # Get delta before saving
        delta = self.get_delta()
        
        if delta['total_changes'] > 0:
            # Save index
            saved_file = self.index.save(index_file)
            
            # Log changes
            self.change_log.append({
                'timestamp': datetime.now().isoformat(),
                'delta': delta,
                'index_file': str(saved_file),
            })
            
            # Reset delta tracking
            self.index.reset_delta()
            
            self.last_save_time = datetime.now()
            
            print(f"✅ Index saved (changes: {delta['total_changes']})")
            return saved_file
        else:
            print("ℹ️  No changes to save")
            return None
    
    def get_stats(self) -> Dict:
        """Get indexer statistics"""
        return {
            'index_stats': self.index.get_stats(),
            'change_log_entries': len(self.change_log),
            'last_save_time': self.last_save_time.isoformat() if self.last_save_time else None,
            'pending_changes': self.index.get_delta()['total_changes'],
        }
    
    def export_delta_report(self, output_file: Path = None) -> Path:
        """Export delta report to JSON"""
        if output_file is None:
            output_file = INDEX_DIR / 'delta_report.json'
        
        report = {
            'delta': self.get_delta(),
            'stats': self.get_stats(),
            'recent_changes': self.change_log[-10:],  # Last 10 changes
            'timestamp': datetime.now().isoformat(),
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Delta report exported to: {output_file}")
        return output_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Incremental Indexer")
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    parser.add_argument('--save', action='store_true', help='Save index')
    args = parser.parse_args()
    
    indexer = IncrementalIndexer(auto_save=False)
    
    if args.demo:
        print("\n📚 Incremental Indexer Demo")
        print("=" * 80)
        
        # Create sample documents
        print("\n📄 Creating sample documents...\n")
        
        documents = [
            Document("doc1", "Memory optimization techniques for fast retrieval", 
                    {'category': 'performance', 'author': 'Alice'}),
            Document("doc2", "Security best practices for cloud infrastructure",
                    {'category': 'security', 'author': 'Bob'}),
            Document("doc3", "Workflow automation with AI agents",
                    {'category': 'automation', 'author': 'Charlie'}),
            Document("doc4", "Neural embedding for semantic search",
                    {'category': 'ml', 'author': 'Diana'}),
            Document("doc5", "Cache tier management and optimization",
                    {'category': 'performance', 'author': 'Eve'}),
        ]
        
        # Add documents
        indexer.add_documents(documents)
        
        # Show delta
        print("\n📊 Delta (changes):")
        delta = indexer.get_delta()
        print(f"   Added: {delta['added']}")
        print(f"   Updated: {delta['updated']}")
        print(f"   Deleted: {delta['deleted']}")
        
        # Search
        print("\n🔍 Search examples:")
        
        queries = ["memory optimization", "security", "neural"]
        
        for query in queries:
            results = indexer.search(query, top_k=3)
            print(f"\n   Query: '{query}'")
            for doc_id, score, doc in results:
                print(f"      {doc_id}: {score:.2f} - {doc.metadata.get('category', 'N/A')}")
        
        # Update a document
        print("\n✏️  Updating document...")
        doc1_updated = Document("doc1", "Advanced memory optimization techniques with caching",
                               {'category': 'performance', 'author': 'Alice'})
        indexer.update_document(doc1_updated)
        
        # Show updated delta
        print("\n📊 Updated delta:")
        delta = indexer.get_delta()
        print(f"   Added: {delta['added']}")
        print(f"   Updated: {delta['updated']}")
        print(f"   Deleted: {delta['deleted']}")
        
        # Show stats
        print("\n📈 Index Statistics:")
        stats = indexer.get_stats()
        print(f"   Total documents: {stats['index_stats']['total_documents']}")
        print(f"   Total terms: {stats['index_stats']['total_terms']}")
        print(f"   Total postings: {stats['index_stats']['total_postings']}")
        print(f"   Pending changes: {stats['pending_changes']}")
        
        # Save index
        if args.save:
            indexer.save_index()
        
        print("\n✅ Demo complete!")
    
    elif args.stats:
        stats = indexer.get_stats()
        print("\n📈 Incremental Indexer Statistics")
        print("=" * 80)
        print(f"Total documents: {stats['index_stats']['total_documents']}")
        print(f"Total terms: {stats['index_stats']['total_terms']}")
        print(f"Total postings: {stats['index_stats']['total_postings']}")
        print(f"Pending changes: {stats['pending_changes']}")
        print(f"Last save: {stats['last_save_time']}")
    
    elif args.save:
        indexer.save_index()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
